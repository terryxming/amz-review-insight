import assert from "node:assert/strict";
import test from "node:test";
import {
  consumerTaskChains,
  consumerTaskChain,
  giftEvidence,
  giftMetrics,
  giftTaskChain,
  micEvidence,
  micMetrics,
  micSellingPoint,
  partyEvidence,
  partyFailureEvidence,
  partyMetrics,
  partyTaskChain,
  mobileTaskChain,
  upgradeTaskChain,
  selectConsumerEvidence,
  selectGiftEvidence,
  selectMicEvidence,
  selectPartyEvidence,
  selectTaskChainEvidence,
} from "./mic-analysis-data.js";

test("麦克风KPI使用严格子ASIN分母与人工确认分子", () => {
  assert.deepEqual(micMetrics, {
    all: { numerator: 16, denominator: 558 },
    blocking: { numerator: 9, denominator: 16 },
    commerce: { numerator: 5, denominator: 16 },
  });
});

test("点击三个KPI分别返回全部问题、任务阻断、退换货证据", () => {
  assert.equal(selectMicEvidence("all").length, 16);
  assert.equal(selectMicEvidence("blocking").length, 9);
  assert.equal(selectMicEvidence("commerce").length, 5);
});

test("默认下钻保留10条代表证据且每条具备完整展示字段", () => {
  const representativeRows = micEvidence.filter(row => row.representative);
  assert.equal(representativeRows.length, 10);

  for (const row of micEvidence) {
    for (const field of ["reviewId", "expression", "result", "original", "translation", "rating", "date", "source", "object", "version"]) {
      assert.ok(row[field], `${row.reviewId || "未知评论"} 缺少 ${field}`);
    }
  }
});

test("共同娱乐卖点保留人工确认口径与代表证据", () => {
  assert.equal(micSellingPoint.validated, 11);
  assert.equal(micSellingPoint.denominator, 558);
  assert.equal(micSellingPoint.evidence.length, 5);
  assert.equal(micSellingPoint.headline, "Two Mics. One Shared Moment.");
});

test("消费者任务链覆盖六个理解维度并区分证据与推断", () => {
  assert.equal(consumerTaskChain.validated, 11);
  assert.equal(consumerTaskChain.denominator, 558);
  assert.deepEqual(
    consumerTaskChain.nodes.map(node => node.id),
    ["role", "scene", "job", "motivation", "outcome", "unmet-need"],
  );
  assert.deepEqual(
    consumerTaskChain.nodes.map(node => node.evidenceMode),
    ["显性关系 / 场景归纳", "显性证据", "显性证据", "显性选择理由", "分析归纳", "问题证据反推"],
  );
});

test("消费者任务链每个节点都能下钻到完整评论证据", () => {
  const expectedCounts = {
    role: 3,
    scene: 5,
    job: 5,
    motivation: 2,
    outcome: 5,
    "unmet-need": 16,
  };

  for (const [key, count] of Object.entries(expectedCounts)) {
    const rows = selectConsumerEvidence(key);
    assert.equal(rows.length, count, `${key} 证据数不正确`);
    for (const row of rows) {
      for (const field of ["reviewId", "expression", "result", "original", "translation", "rating", "date", "source", "object", "version"]) {
        assert.ok(row[field], `${key} 的 ${row.reviewId || "未知评论"} 缺少 ${field}`);
      }
    }
  }
});

test("礼物任务链使用人工确认口径并保留10条代表证据", () => {
  assert.deepEqual(giftMetrics, {
    all: { numerator: 24, denominator: 558 },
    buyerToRecipient: { numerator: 17, denominator: 24 },
    sharedOutcome: { numerator: 21, denominator: 24 },
    failure: { numerator: 1, denominator: 24 },
  });
  assert.equal(giftEvidence.filter(row => row.representative).length, 10);

  for (const row of giftEvidence) {
    for (const field of ["reviewId", "expression", "result", "original", "translation", "rating", "date", "source", "object", "version"]) {
      assert.ok(row[field], `${row.reviewId || "未知评论"} 缺少 ${field}`);
    }
  }
});

test("礼物任务链覆盖六个理解维度并能下钻到完整证据", () => {
  assert.equal(giftTaskChain.validated, 24);
  assert.equal(giftTaskChain.denominator, 558);
  assert.deepEqual(
    giftTaskChain.nodes.map(node => node.id),
    ["role", "scene", "job", "motivation", "outcome", "unmet-need"],
  );

  const expectedCounts = {
    role: 17,
    scene: 13,
    job: 21,
    motivation: 21,
    outcome: 21,
    "unmet-need": 1,
  };

  for (const [key, count] of Object.entries(expectedCounts)) {
    const rows = selectGiftEvidence(key);
    assert.equal(rows.length, count, `${key} 证据数不正确`);
  }
});

test("任务链通用选择器兼容五条真实任务链", () => {
  assert.deepEqual(consumerTaskChains.map(chain => chain.id), [
    "family-shared-entertainment",
    "gift-to-shared-entertainment",
    "party-quick-start",
    "complete-entertainment-on-the-move",
    "all-in-one-upgrade",
  ]);
  assert.equal(selectTaskChainEvidence("family-shared-entertainment", "motivation").length, 2);
  assert.equal(selectTaskChainEvidence("gift-to-shared-entertainment", "motivation").length, 21);
  assert.equal(selectTaskChainEvidence("party-quick-start", "motivation").length, 9);
  assert.equal(selectTaskChainEvidence("complete-entertainment-on-the-move", "scene").length, 11);
  assert.equal(selectTaskChainEvidence("complete-entertainment-on-the-move", "job").length, 16);
  assert.equal(selectTaskChainEvidence("complete-entertainment-on-the-move", "motivation").length, 3);
  assert.equal(selectTaskChainEvidence("complete-entertainment-on-the-move", "unmet-need").length, 2);
  assert.equal(selectTaskChainEvidence("all-in-one-upgrade", "motivation").length, 5);
  assert.equal(selectTaskChainEvidence("all-in-one-upgrade", "unmet-need").length, 17);
  assert.deepEqual(selectTaskChainEvidence("unknown", "motivation"), []);
});

test("新增移动与升级任务链使用人工确认口径并保留完整证据字段", () => {
  assert.equal(mobileTaskChain.validated, 16);
  assert.equal(mobileTaskChain.denominator, 558);
  assert.equal(upgradeTaskChain.validated, 5);
  assert.equal(upgradeTaskChain.denominator, 558);

  for (const chain of [mobileTaskChain, upgradeTaskChain]) {
    assert.deepEqual(chain.nodes.map(node => node.id), ["role", "scene", "job", "motivation", "outcome", "unmet-need"]);
    for (const node of chain.nodes) {
      const rows = selectTaskChainEvidence(chain.id, node.id);
      assert.ok(rows.length > 0, `${chain.id}:${node.id} 没有下钻证据`);
      for (const row of rows) {
        for (const field of ["reviewId", "expression", "result", "original", "translation", "rating", "date", "source", "object", "version"]) {
          assert.ok(row[field], `${chain.id}:${node.id} 的 ${row.reviewId || "未知评论"} 缺少 ${field}`);
        }
      }
    }
  }
});

test("聚会快速启动任务链保留人工确认口径与现场失败证据", () => {
  assert.deepEqual(partyMetrics, {
    all: { numerator: 19, denominator: 558 },
    lowFriction: { numerator: 17, denominator: 19 },
    participation: { numerator: 17, denominator: 19 },
    failure: { numerator: 7, denominator: 558 },
  });
  assert.equal(partyEvidence.filter(row => row.representative).length, 10);
  assert.equal(partyFailureEvidence.length, 7);
});

test("聚会快速启动六维节点均能下钻到完整证据", () => {
  assert.equal(partyTaskChain.validated, 19);
  assert.equal(partyTaskChain.denominator, 558);
  const expectedCounts = {
    role: 10,
    scene: 19,
    job: 19,
    motivation: 9,
    outcome: 17,
    "unmet-need": 7,
  };

  for (const [key, count] of Object.entries(expectedCounts)) {
    const rows = selectPartyEvidence(key);
    assert.equal(rows.length, count, `${key} 证据数不正确`);
    for (const row of rows) {
      for (const field of ["reviewId", "expression", "result", "original", "translation", "rating", "date", "source", "object", "version"]) {
        assert.ok(row[field], `${key} 的 ${row.reviewId || "未知评论"} 缺少 ${field}`);
      }
    }
  }
});
