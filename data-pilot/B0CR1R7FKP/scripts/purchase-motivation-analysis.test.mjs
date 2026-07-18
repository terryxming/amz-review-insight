import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const root = new URL("../", import.meta.url);
const motivationLabels = new Set([
  "replace_or_upgrade",
  "recommendation_trigger",
  "explicit_two_mic_choice",
  "replace_external_venue",
]);

function readJsonLines(relativePath) {
  return readFileSync(new URL(relativePath, root), "utf8")
    .split(/\r?\n/)
    .filter(Boolean)
    .map(line => JSON.parse(line));
}

const candidates = readJsonLines("qa/consumer-theme-candidates.jsonl")
  .filter(row => row.dimension === "motivation" && motivationLabels.has(row.candidate_label));
const qa = readJsonLines("qa/purchase-motivation-candidate-review.jsonl");

test("购买动机完整复核四类31条候选且不把召回量当KPI", () => {
  assert.equal(candidates.length, 31);
  assert.equal(qa.length, 31);
  assert.equal(new Set(qa.map(row => row.review_id)).size, 31);
  assert.deepEqual(
    new Set(qa.map(row => `${row.review_id}:${row.candidate_label}`)),
    new Set(candidates.map(row => `${row.review_id}:${row.candidate_label}`)),
  );
  assert.deepEqual(
    Object.fromEntries(["valid", "invalid", "uncertain"].map(status => [status, qa.filter(row => row.review_status === status).length])),
    { valid: 10, invalid: 21, uncertain: 0 },
  );
  assert.equal(qa.filter(row => row.evidence_selected).length, 10);
});

test("各类购买动机只计入原文支持的购买前原因", () => {
  const counts = Object.fromEntries(
    [...motivationLabels].map(label => [
      label,
      {
        candidate: qa.filter(row => row.candidate_label === label).length,
        valid: qa.filter(row => row.candidate_label === label && row.review_status === "valid").length,
      },
    ]),
  );

  assert.deepEqual(counts, {
    replace_or_upgrade: { candidate: 11, valid: 5 },
    recommendation_trigger: { candidate: 17, valid: 2 },
    explicit_two_mic_choice: { candidate: 2, valid: 2 },
    replace_external_venue: { candidate: 1, valid: 1 },
  });
  for (const row of qa) {
    assert.ok(row.decision_basis, `${row.review_id} 缺少 decision_basis`);
    assert.ok(["explicit", "unknown"].includes(row.evidence_type), `${row.review_id} evidence_type 非法`);
    assert.equal(row.review_status === "valid", row.evidence_type === "explicit");
  }
});

test("全部有效购买动机证据都具备完整中文翻译与洞察字段", () => {
  const evidence = readJsonLines("analysis/purchase-motivation-evidence.jsonl");
  const validIds = new Set(qa.filter(row => row.review_status === "valid").map(row => row.review_id));
  const referencedTranslations = new Map(
    readJsonLines("analysis/mic-selling-point-evidence.jsonl")
      .concat(readJsonLines("analysis/gift-theme-evidence.jsonl"))
      .concat(readJsonLines("analysis/party-quick-start-evidence.jsonl"))
      .map(row => [row.review_id, row]),
  );

  assert.equal(evidence.length, validIds.size);
  assert.deepEqual(new Set(evidence.map(row => row.review_id)), validIds);
  for (const row of evidence) {
    for (const field of ["review_id", "consumer_expression", "purchase_context", "motivation_value"]) {
      assert.ok(row[field], `${row.review_id || "未知评论"} 缺少 ${field}`);
    }
    if (row.translation_ref) {
      const referenced = referencedTranslations.get(row.review_id);
      assert.ok(referenced?.title_zh && referenced?.body_zh, `${row.review_id} 的译文引用无法解析`);
    } else {
      assert.ok(row.title_zh && row.body_zh, `${row.review_id} 缺少内联译文`);
    }
  }
});
