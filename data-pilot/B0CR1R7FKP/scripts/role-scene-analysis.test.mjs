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

function resolveTranslation(row) {
  if (row.title_zh && row.body_zh) return row;
  assert.ok(row.translation_ref, `${row.review_id} 缺少译文或 translation_ref`);
  const [relativePath, reviewId] = row.translation_ref.split("#");
  const source = readJsonLines(relativePath.replace(/^analysis\//, "analysis/"))
    .find(item => item.review_id === reviewId);
  assert.ok(source?.title_zh && source?.body_zh, `${row.review_id} 的译文引用不可解析`);
  return { ...row, title_zh: source.title_zh, body_zh: source.body_zh };
}

const targetLabels = new Set(["cross_generation_family", "home_karaoke", "travel_or_outdoor"]);
const candidates = readJsonLines("qa/consumer-theme-candidates.jsonl")
  .filter(row => targetLabels.has(row.candidate_label));
const qa = readJsonLines("qa/role-scene-candidate-review.jsonl");
const primaryQa = qa.filter(row => row.candidate_origin === "target_candidate");
const supportQa = qa.filter(row => row.candidate_origin === "cross_support");

test("关系角色与场景完整复核37条窄主题候选", () => {
  assert.equal(candidates.length, 37);
  assert.equal(primaryQa.length, 37);
  assert.equal(new Set(primaryQa.map(row => `${row.review_id}:${row.candidate_label}`)).size, 37);
  assert.deepEqual(
    new Set(primaryQa.map(row => `${row.review_id}:${row.candidate_label}`)),
    new Set(candidates.map(row => `${row.review_id}:${row.candidate_label}`)),
  );
  for (const row of primaryQa) {
    assert.ok(["valid", "invalid", "uncertain"].includes(row.review_status));
    assert.ok(row.decision_basis);
  }
});

test("每个窄主题都保留候选与确认状态的独立口径", () => {
  const summary = Object.fromEntries([...targetLabels].map(label => {
    const rows = primaryQa.filter(row => row.candidate_label === label);
    return [label, {
      candidates: rows.length,
      valid: rows.filter(row => row.review_status === "valid").length,
      invalid: rows.filter(row => row.review_status === "invalid").length,
      uncertain: rows.filter(row => row.review_status === "uncertain").length,
    }];
  }));

  assert.deepEqual(summary, {
    cross_generation_family: { candidates: 2, valid: 2, invalid: 0, uncertain: 0 },
    home_karaoke: { candidates: 16, valid: 7, invalid: 5, uncertain: 4 },
    travel_or_outdoor: { candidates: 19, valid: 11, invalid: 2, uncertain: 6 },
  });
});

test("宽泛家庭候选只补充一条明确跨代关系证据", () => {
  assert.equal(supportQa.length, 1);
  assert.deepEqual(supportQa[0], {
    review_id: "R3UL2QNZHC2RG8",
    candidate_label: "cross_generation_family",
    source_candidate_label: "family_members",
    candidate_origin: "cross_support",
    review_status: "valid",
    evidence_type: "explicit",
    decision_basis: "评论明确说孩子到祖父母都加入家庭聚会，补充了规则未召回的跨代共同参与证据。",
    evidence_selected: true,
  });
});

test("全部有效证据都有完整中文翻译与关系场景洞察字段", () => {
  const evidence = readJsonLines("analysis/role-scene-evidence.jsonl");
  const validIds = new Set(qa.filter(row => row.review_status === "valid").map(row => row.review_id));

  assert.equal(evidence.length, validIds.size);
  assert.deepEqual(new Set(evidence.map(row => row.review_id)), validIds);
  assert.ok(evidence.filter(row => row.evidence_selected).length <= 10);
  for (const sourceRow of evidence) {
    const row = resolveTranslation(sourceRow);
    for (const field of [
      "review_id",
      "title_zh",
      "body_zh",
      "consumer_expression",
      "relationship_context",
      "scene_context",
      "task_value",
    ]) {
      assert.ok(row[field], `${row.review_id || "未知评论"} 缺少 ${field}`);
    }
  }
});
