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

const candidates = readJsonLines("qa/consumer-theme-candidates.jsonl");
const partyIds = new Set(
  candidates
    .filter(row => row.dimension === "scene" && row.candidate_label === "party_or_gathering")
    .map(row => row.review_id),
);
const quickStartIds = new Set(
  candidates
    .filter(row => row.dimension === "job" && row.candidate_label === "quick_start")
    .map(row => row.review_id),
);
const intersectionIds = new Set([...partyIds].filter(reviewId => quickStartIds.has(reviewId)));

test("聚会快速启动候选只取聚会场景与快速启动的交集", () => {
  assert.equal(partyIds.size, 94);
  assert.equal(intersectionIds.size, 25);
});

test("聚会快速启动主题完整复核25条交集候选", () => {
  const qa = readJsonLines("qa/party-quick-start-candidate-review.jsonl");

  assert.equal(qa.length, 25);
  assert.equal(new Set(qa.map(row => row.review_id)).size, 25);
  assert.deepEqual(new Set(qa.map(row => row.review_id)), intersectionIds);
  assert.deepEqual(
    Object.fromEntries(["valid", "invalid", "uncertain"].map(status => [status, qa.filter(row => row.review_status === status).length])),
    { valid: 19, invalid: 0, uncertain: 6 },
  );
  assert.equal(qa.filter(row => row.evidence_selected).length, 10);
});

test("全部有效聚会快速启动证据都具备完整中文翻译与洞察字段", () => {
  const qa = readJsonLines("qa/party-quick-start-candidate-review.jsonl");
  const evidence = readJsonLines("analysis/party-quick-start-evidence.jsonl");
  const validIds = new Set(qa.filter(row => row.review_status === "valid").map(row => row.review_id));

  assert.equal(evidence.length, validIds.size);
  assert.deepEqual(new Set(evidence.map(row => row.review_id)), validIds);
  for (const row of evidence) {
    for (const field of ["review_id", "title_zh", "body_zh", "consumer_expression", "party_context", "task_value"]) {
      assert.ok(row[field], `${row.review_id || "未知评论"} 缺少 ${field}`);
    }
  }
});

test("聚会现场失败证据完整复核并翻译", () => {
  const qa = readJsonLines("qa/party-failure-candidate-review.jsonl");
  const evidence = readJsonLines("analysis/party-failure-evidence.jsonl");

  assert.equal(qa.length, 7);
  assert.equal(qa.filter(row => row.review_status === "valid").length, 7);
  assert.equal(qa.filter(row => row.evidence_selected).length, 7);
  assert.deepEqual(new Set(evidence.map(row => row.review_id)), new Set(qa.map(row => row.review_id)));
  for (const row of evidence) {
    for (const field of ["review_id", "title_zh", "body_zh", "consumer_expression", "failure_point", "task_impact"]) {
      assert.ok(row[field], `${row.review_id || "未知评论"} 缺少 ${field}`);
    }
  }
});
