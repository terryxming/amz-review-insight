import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const root = new URL("../", import.meta.url);
const targetLabels = new Set([
  "bring_karaoke_home",
  "portable_entertainment",
  "shared_singing",
  "sound_and_atmosphere",
  "shared_fun_and_connection",
]);

function readJsonLines(relativePath) {
  return readFileSync(new URL(relativePath, root), "utf8")
    .split(/\r?\n/)
    .filter(Boolean)
    .map(line => JSON.parse(line));
}

function resolveTranslation(row) {
  if (row.title_zh && row.body_zh) return row;
  assert.ok(row.translation_ref, `${row.review_id} 缺少译文或 translation_ref`);
  const [relativePath, reviewId] = row.translation_ref.split("#");
  const source = readJsonLines(relativePath).find(item => item.review_id === reviewId);
  assert.ok(source?.title_zh && source?.body_zh, `${row.review_id} 的译文引用不可解析`);
  return { ...row, title_zh: source.title_zh, body_zh: source.body_zh };
}

function candidateKey(row) {
  return `${row.review_id}:${row.dimension}:${row.candidate_label}`;
}

const master = readJsonLines("normalized/reviews-master.jsonl");
const candidates = readJsonLines("qa/consumer-theme-candidates.jsonl")
  .filter(row => targetLabels.has(row.candidate_label));
const qa = readJsonLines("qa/task-outcome-candidate-review.jsonl");

test("用户任务与期望结果完整复核五类候选且不把宽候选直接纳入", () => {
  assert.equal(master.length, 558);
  assert.equal(candidates.length, 122);
  assert.equal(new Set(candidates.map(row => row.review_id)).size, 106);
  assert.equal(qa.length, 122);
  assert.equal(new Set(qa.map(candidateKey)).size, 122);
  assert.deepEqual(new Set(qa.map(candidateKey)), new Set(candidates.map(candidateKey)));

  const allowedStatuses = new Set(["valid", "invalid", "uncertain"]);
  const allowedEvidenceTypes = new Set(["explicit", "synthesized", "unknown"]);
  for (const row of qa) {
    assert.ok(allowedStatuses.has(row.review_status), `${candidateKey(row)} 状态无效`);
    assert.ok(allowedEvidenceTypes.has(row.evidence_type), `${candidateKey(row)} 证据性质无效`);
    assert.ok(row.decision_basis, `${candidateKey(row)} 缺少 decision_basis`);
    assert.equal("quick_start" in row, false, `${candidateKey(row)} 不应把宽候选写成字段`);
    assert.equal("low_setup_effort" in row, false, `${candidateKey(row)} 不应把宽候选写成字段`);
  }

  assert.ok(qa.filter(row => row.evidence_selected).length <= 10);
  assert.equal(new Set(qa.filter(row => row.evidence_selected).map(row => row.review_id)).size, qa.filter(row => row.evidence_selected).length);
});

test("全部有效任务结果评论都有完整中文翻译与洞察字段", () => {
  const evidence = readJsonLines("analysis/task-outcome-evidence.jsonl");
  const validIds = new Set(qa.filter(row => row.review_status === "valid").map(row => row.review_id));
  const masterIds = new Set(master.map(row => row.review_id));

  assert.equal(evidence.length, validIds.size);
  assert.deepEqual(new Set(evidence.map(row => row.review_id)), validIds);
  for (const sourceRow of evidence) {
    const row = resolveTranslation(sourceRow);
    assert.ok(masterIds.has(row.review_id), `${row.review_id} 不在评论主表`);
    for (const field of ["review_id", "title_zh", "body_zh", "consumer_expression", "task_context", "outcome_context", "task_value"]) {
      assert.ok(row[field], `${row.review_id || "未知评论"} 缺少 ${field}`);
    }
  }
});

test("有效证据只来自人工确认标签且代表证据最多十条", () => {
  const evidence = readJsonLines("analysis/task-outcome-evidence.jsonl");
  const validLabelsByReview = new Map();

  for (const row of qa.filter(row => row.review_status === "valid")) {
    const labels = validLabelsByReview.get(row.review_id) ?? [];
    labels.push(row.candidate_label);
    validLabelsByReview.set(row.review_id, labels);
  }

  for (const row of evidence) {
    assert.deepEqual(new Set(row.valid_labels), new Set(validLabelsByReview.get(row.review_id)));
  }
  assert.ok(evidence.filter(row => row.evidence_selected).length <= 10);
});
