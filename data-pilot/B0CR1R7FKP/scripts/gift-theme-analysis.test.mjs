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

const candidates = readJsonLines("qa/consumer-theme-candidates.jsonl")
  .filter(row => row.dimension === "scene" && row.candidate_label === "gift_occasion");
const qa = readJsonLines("qa/gift-theme-candidate-review.jsonl");

test("礼物主题完整复核36条候选且状态互斥", () => {
  assert.equal(candidates.length, 36);
  assert.equal(qa.length, 36);
  assert.equal(new Set(qa.map(row => row.review_id)).size, 36);
  assert.deepEqual(
    Object.fromEntries(["valid", "invalid", "uncertain"].map(status => [status, qa.filter(row => row.review_status === status).length])),
    { valid: 24, invalid: 9, uncertain: 3 },
  );
  assert.equal(qa.filter(row => row.evidence_selected).length, 10);
  assert.deepEqual(
    new Set(qa.map(row => row.review_id)),
    new Set(candidates.map(row => row.review_id)),
  );
});

test("全部有效礼物证据都具备完整中文翻译与洞察字段", () => {
  const evidence = readJsonLines("analysis/gift-theme-evidence.jsonl");
  const validIds = new Set(qa.filter(row => row.review_status === "valid").map(row => row.review_id));

  assert.equal(evidence.length, validIds.size);
  assert.deepEqual(new Set(evidence.map(row => row.review_id)), validIds);
  for (const row of evidence) {
    for (const field of ["review_id", "title_zh", "body_zh", "consumer_expression", "purchase_context", "task_value"]) {
      assert.ok(row[field], `${row.review_id || "未知评论"} 缺少 ${field}`);
    }
  }
});
