import assert from "node:assert/strict";
import test from "node:test";
import {
  discoverConsumerCandidates,
  loadMasterReviews,
} from "./discover-consumer-theme-candidates.mjs";

const masterPath = new URL("../normalized/reviews-master.jsonl", import.meta.url);
const reviews = loadMasterReviews(masterPath);
const byId = new Map(reviews.map(row => [row.review_id, row]));

test("严格主表包含558条唯一评论", () => {
  assert.equal(reviews.length, 558);
  assert.equal(byId.size, 558);
});

test("已知消费者表达能进入对应六维候选", () => {
  const sampleIds = [
    "R1LIPX69A9427F",
    "R109D7LUYY25LQ",
    "R3JJNQQQOBH21C",
    "R1MMMISQGTFKLA",
  ];
  const candidates = discoverConsumerCandidates(sampleIds.map(id => byId.get(id)));
  const keys = new Set(candidates.map(row => `${row.review_id}|${row.dimension}|${row.candidate_label}`));

  assert.ok(keys.has("R1LIPX69A9427F|role|cross_generation_family"));
  assert.ok(keys.has("R1LIPX69A9427F|job|shared_singing"));
  assert.ok(keys.has("R1LIPX69A9427F|motivation|explicit_two_mic_choice"));
  assert.ok(keys.has("R109D7LUYY25LQ|scene|gift_occasion"));
  assert.ok(keys.has("R109D7LUYY25LQ|job|bring_karaoke_home"));
  assert.ok(keys.has("R3JJNQQQOBH21C|unmet_need|software_performance"));
  assert.ok(keys.has("R1MMMISQGTFKLA|unmet_need|battery_reliability"));
});

test("候选记录保持待复核，不携带最终KPI字段", () => {
  const candidates = discoverConsumerCandidates(reviews.slice(0, 40));
  assert.ok(candidates.length > 0);

  for (const row of candidates) {
    assert.equal(row.review_status, "pending");
    assert.equal(row.evidence_type, "unknown");
    assert.equal(row.decision_basis, null);
    assert.ok(row.review_id);
    assert.ok(row.dimension);
    assert.ok(row.candidate_label);
    assert.ok(Array.isArray(row.rule_ids) && row.rule_ids.length > 0);
    assert.ok(row.matched_text);
    for (const forbidden of ["validated_count", "rate", "share", "consumer_share"]) {
      assert.equal(Object.hasOwn(row, forbidden), false, `${row.review_id} 不应包含 ${forbidden}`);
    }
  }
});

test("同一评论同一维度同一标签只生成一条候选并合并规则", () => {
  const candidates = discoverConsumerCandidates([byId.get("R1LIPX69A9427F")]);
  const sharedSinging = candidates.filter(row => row.dimension === "job" && row.candidate_label === "shared_singing");

  assert.equal(sharedSinging.length, 1);
  assert.ok(sharedSinging[0].rule_ids.length >= 2);
});
