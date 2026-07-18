import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const root = new URL("../", import.meta.url);

function readJsonLines(relativePath) {
  return readFileSync(new URL(relativePath, root), "utf8")
    .split(/\r?\n/)
    .filter(Boolean)
    .map(line => JSON.parse(line));
}

const labels = [
  "content_service_transparency",
  "software_performance",
  "tv_connection_expectation",
  "battery_reliability",
  "setup_and_support",
];
const candidates = readJsonLines("qa/consumer-theme-candidates.jsonl")
  .filter(row => labels.includes(row.candidate_label));

test("五类未满足需求候选口径保持评论与标签粒度", () => {
  assert.equal(candidates.length, 32);
  assert.deepEqual(
    Object.fromEntries(labels.map(label => [label, candidates.filter(row => row.candidate_label === label).length])),
    {
      content_service_transparency: 16,
      software_performance: 7,
      tv_connection_expectation: 4,
      battery_reliability: 3,
      setup_and_support: 2,
    },
  );
});

test("32条候选标签全部人工复核且不把重复评论重复算作唯一证据", () => {
  const qa = readJsonLines("qa/unmet-needs-candidate-review.jsonl");

  assert.equal(qa.length, 32);
  assert.equal(new Set(qa.map(row => `${row.review_id}:${row.candidate_label}`)).size, 32);
  assert.deepEqual(
    Object.fromEntries(["valid", "invalid", "uncertain"].map(status => [status, qa.filter(row => row.review_status === status).length])),
    { valid: 20, invalid: 12, uncertain: 0 },
  );
  assert.deepEqual(
    Object.fromEntries(labels.map(label => [label, qa.filter(row => row.candidate_label === label && row.review_status === "valid").length])),
    {
      content_service_transparency: 7,
      software_performance: 7,
      tv_connection_expectation: 3,
      battery_reliability: 1,
      setup_and_support: 2,
    },
  );
  assert.deepEqual(
    new Set(qa.map(row => `${row.review_id}:${row.candidate_label}`)),
    new Set(candidates.map(row => `${row.review_id}:${row.candidate_label}`)),
  );
  assert.equal(new Set(qa.filter(row => row.evidence_selected).map(row => row.review_id)).size, 10);
});

test("17条唯一有效问题评论都有可解析的中文译文与洞察字段", () => {
  const qa = readJsonLines("qa/unmet-needs-candidate-review.jsonl");
  const evidence = readJsonLines("analysis/unmet-needs-evidence.jsonl");
  const validIds = new Set(qa.filter(row => row.review_status === "valid").map(row => row.review_id));

  assert.equal(validIds.size, 17);
  assert.equal(evidence.length, 17);
  assert.deepEqual(new Set(evidence.map(row => row.review_id)), validIds);

  const referencedTranslations = new Map(
    readJsonLines("analysis/party-failure-evidence.jsonl")
      .concat(readJsonLines("analysis/party-quick-start-evidence.jsonl"))
      .map(row => [row.review_id, row]),
  );
  for (const row of evidence) {
    for (const field of ["review_id", "issue_types", "consumer_expression", "failure_point", "task_impact"]) {
      assert.ok(row[field]?.length, `${row.review_id || "未知评论"} 缺少 ${field}`);
    }
    if (row.translation_ref) {
      const referenced = referencedTranslations.get(row.review_id);
      assert.ok(referenced?.title_zh && referenced?.body_zh, `${row.review_id} 的译文引用无法解析`);
    } else {
      assert.ok(row.title_zh && row.body_zh, `${row.review_id} 缺少内联译文`);
    }
  }
});
