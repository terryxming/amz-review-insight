import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const projectDir = dirname(dirname(fileURLToPath(import.meta.url)));
const pilotDir = join(dirname(projectDir), "data-pilot", "B0CR1R7FKP");

function readJsonLines(relativePath) {
  return readFileSync(join(pilotDir, relativePath), "utf8")
    .split(/\r?\n/)
    .filter(Boolean)
    .map(line => JSON.parse(line));
}

function requireById(map, reviewId, sourceName) {
  const value = map.get(reviewId);
  if (!value) throw new Error(`${sourceName} 缺少评论 ${reviewId}`);
  return value;
}

const evidenceMapCache = new Map();

function readEvidenceMap(relativePath) {
  if (!evidenceMapCache.has(relativePath)) {
    evidenceMapCache.set(relativePath, new Map(
      readJsonLines(relativePath).map(row => [row.review_id, row]),
    ));
  }
  return evidenceMapCache.get(relativePath);
}

function resolveTranslation(row, sourceName, trail = []) {
  if (row.title_zh && row.body_zh) return row;
  if (!row.translation_ref) throw new Error(`${sourceName} 的 ${row.review_id} 缺少译文引用`);

  const [relativePath, reviewId] = row.translation_ref.split("#");
  const key = `${relativePath}#${reviewId}`;
  if (trail.includes(key)) throw new Error(`${sourceName} 的译文引用形成循环：${[...trail, key].join(" -> ")}`);
  const target = requireById(readEvidenceMap(relativePath), reviewId, `${sourceName} 的译文引用`);
  const resolved = resolveTranslation(target, sourceName, [...trail, key]);
  return { ...row, title_zh: resolved.title_zh, body_zh: resolved.body_zh };
}

function resolvedEvidenceMap(relativePath, sourceName) {
  return new Map(
    [...readEvidenceMap(relativePath)].map(([reviewId, row]) => [reviewId, resolveTranslation(row, sourceName)]),
  );
}

const masterById = new Map(
  readJsonLines(join("normalized", "reviews-master.jsonl"))
    .map(row => [row.review_id, row]),
);
const issueCoding = readJsonLines(join("qa", "mic-theme-candidate-review.jsonl"));
const issueTranslationById = new Map(
  readJsonLines(join("analysis", "mic-reliability-evidence.jsonl"))
    .map(row => [row.review_id, row]),
);
const sellingCoding = readJsonLines(join("qa", "mic-shared-singing-candidate-review.jsonl"));
const sellingTranslationById = new Map(
  readJsonLines(join("analysis", "mic-selling-point-evidence.jsonl"))
    .map(row => [row.review_id, row]),
);
const giftCoding = readJsonLines(join("qa", "gift-theme-candidate-review.jsonl"));
const giftTranslationById = new Map(
  readJsonLines(join("analysis", "gift-theme-evidence.jsonl"))
    .map(row => [row.review_id, row]),
);
const partyCoding = readJsonLines(join("qa", "party-quick-start-candidate-review.jsonl"));
const partyTranslationById = new Map(
  readJsonLines(join("analysis", "party-quick-start-evidence.jsonl"))
    .map(row => [row.review_id, row]),
);
const partyFailureCoding = readJsonLines(join("qa", "party-failure-candidate-review.jsonl"));
const partyFailureTranslationById = new Map(
  readJsonLines(join("analysis", "party-failure-evidence.jsonl"))
    .map(row => [row.review_id, row]),
);
const purchaseCoding = readJsonLines(join("qa", "purchase-motivation-candidate-review.jsonl"));
const purchaseTranslationById = resolvedEvidenceMap("analysis/purchase-motivation-evidence.jsonl", "购买动机译文");
const roleSceneCoding = readJsonLines(join("qa", "role-scene-candidate-review.jsonl"));
const roleSceneTranslationById = resolvedEvidenceMap("analysis/role-scene-evidence.jsonl", "关系场景译文");
const taskOutcomeTranslationById = resolvedEvidenceMap("analysis/task-outcome-evidence.jsonl", "任务结果译文");
const unmetNeedTranslationById = resolvedEvidenceMap("analysis/unmet-needs-evidence.jsonl", "未满足需求译文");

const commerceOutcomes = new Set(["return", "replacement_mic", "replacement_machine"]);
const micEvidence = issueCoding
  .filter(row => row.is_valid_issue)
  .map(coding => {
    const master = requireById(masterById, coding.review_id, "评论主表");
    const translation = requireById(issueTranslationById, coding.review_id, "问题译文");
    return {
      reviewId: coding.review_id,
      expression: translation.consumer_expression,
      result: translation.result,
      original: `${master.title_original}\n${master.body_original}`,
      translation: `${translation.title_zh}\n${translation.body_zh}`,
      rating: master.rating,
      date: master.review_date,
      source: master.source_primary,
      object: `${master.asin}（自有ASIN）`,
      version: "未知",
      representative: coding.evidence_selected,
      blocking: coding.task_impact === "task_blocking_or_recovery",
      commerce: commerceOutcomes.has(coding.observed_outcome),
      outcomeType: coding.observed_outcome,
      sentiment: "negative",
    };
  });

const micMetrics = {
  all: { numerator: micEvidence.length, denominator: masterById.size },
  blocking: {
    numerator: micEvidence.filter(row => row.blocking).length,
    denominator: micEvidence.length,
  },
  commerce: {
    numerator: micEvidence.filter(row => row.commerce).length,
    denominator: micEvidence.length,
  },
};

const sellingEvidence = sellingCoding
  .filter(row => row.evidence_selected)
  .map(coding => {
    const master = requireById(masterById, coding.review_id, "评论主表");
    const translation = requireById(sellingTranslationById, coding.review_id, "卖点译文");
    return {
      reviewId: coding.review_id,
      expression: translation.consumer_expression,
      result: translation.task_value,
      original: `${master.title_original}\n${master.body_original}`,
      translation: `${translation.title_zh}\n${translation.body_zh}`,
      rating: master.rating,
      date: master.review_date,
      source: master.source_primary,
      object: `${master.asin}（自有ASIN）`,
      version: "未知",
      sentiment: "positive",
    };
  });

const micSellingPoint = {
  validated: sellingCoding.filter(row => row.is_valid_shared_singing).length,
  denominator: masterById.size,
  headline: "Two Mics. One Shared Moment.",
  body: "Invite a duet instead of waiting for turns. Two rechargeable wireless microphones store neatly inside the X2, making family nights and parties easier to start and easier to share.",
  evidence: sellingEvidence,
};

const giftEvidence = giftCoding
  .filter(row => row.review_status === "valid")
  .map(coding => {
    const master = requireById(masterById, coding.review_id, "评论主表");
    const translation = requireById(giftTranslationById, coding.review_id, "礼物主题译文");
    return {
      reviewId: coding.review_id,
      expression: translation.consumer_expression,
      result: translation.task_value,
      original: `${master.title_original}\n${master.body_original}`,
      translation: `${translation.title_zh}\n${translation.body_zh}`,
      rating: master.rating,
      date: master.review_date,
      source: master.source_primary,
      object: `${master.asin}（自有ASIN）`,
      version: "未知",
      representative: coding.evidence_selected,
      giftContextType: coding.gift_context_type,
      recipientRole: coding.recipient_role,
      occasion: coding.occasion,
      sharedOutcome: coding.shared_outcome,
      sentiment: coding.shared_outcome === "negative_failure" ? "negative" : "positive",
    };
  });

const giftMetrics = {
  all: { numerator: giftEvidence.length, denominator: masterById.size },
  buyerToRecipient: {
    numerator: giftEvidence.filter(row => row.giftContextType === "buyer_to_recipient").length,
    denominator: giftEvidence.length,
  },
  sharedOutcome: {
    numerator: giftEvidence.filter(row => row.sharedOutcome === "explicit").length,
    denominator: giftEvidence.length,
  },
  failure: {
    numerator: giftEvidence.filter(row => row.sharedOutcome === "negative_failure").length,
    denominator: giftEvidence.length,
  },
};

const partyEvidence = partyCoding
  .filter(row => row.review_status === "valid")
  .map(coding => {
    const master = requireById(masterById, coding.review_id, "评论主表");
    const translation = requireById(partyTranslationById, coding.review_id, "聚会快速启动译文");
    return {
      reviewId: coding.review_id,
      expression: translation.consumer_expression,
      result: translation.task_value,
      original: `${master.title_original}\n${master.body_original}`,
      translation: `${translation.title_zh}\n${translation.body_zh}`,
      rating: master.rating,
      date: master.review_date,
      source: master.source_primary,
      object: `${master.asin}（自有ASIN）`,
      version: "未知",
      representative: coding.evidence_selected,
      partySceneType: coding.party_scene_type,
      organizerSignal: coding.organizer_signal,
      quickStartSignal: coding.quick_start_signal,
      participationOutcome: coding.participation_outcome,
      sentiment: coding.participation_outcome === "requires_subscription_or_youtube_workaround" ? "negative" : "positive",
    };
  });

const partyFailureEvidence = partyFailureCoding
  .filter(row => row.review_status === "valid")
  .map(coding => {
    const master = requireById(masterById, coding.review_id, "评论主表");
    const translation = requireById(partyFailureTranslationById, coding.review_id, "聚会失败译文");
    return {
      reviewId: coding.review_id,
      expression: translation.consumer_expression,
      result: translation.task_impact,
      original: `${master.title_original}\n${master.body_original}`,
      translation: `${translation.title_zh}\n${translation.body_zh}`,
      rating: master.rating,
      date: master.review_date,
      source: master.source_primary,
      object: `${master.asin}（自有ASIN）`,
      version: "未知",
      representative: coding.evidence_selected,
      failureType: coding.failure_type,
      sentiment: "negative",
    };
  });

const lowFrictionExceptions = new Set(["easy_after_learning", "easy_initial_setup_but_content_friction"]);
const nonParticipationOutcomes = new Set(["not_observed_yet", "requires_subscription_or_youtube_workaround"]);
const partyMetrics = {
  all: { numerator: partyEvidence.length, denominator: masterById.size },
  lowFriction: {
    numerator: partyEvidence.filter(row => !lowFrictionExceptions.has(row.quickStartSignal)).length,
    denominator: partyEvidence.length,
  },
  participation: {
    numerator: partyEvidence.filter(row => !nonParticipationOutcomes.has(row.participationOutcome)).length,
    denominator: partyEvidence.length,
  },
  failure: { numerator: partyFailureEvidence.length, denominator: masterById.size },
};

function toWorkbenchEvidence(reviewId, translation, expression, result, extra = {}) {
  const master = requireById(masterById, reviewId, "评论主表");
  return {
    reviewId,
    expression,
    result,
    original: `${master.title_original}\n${master.body_original}`,
    translation: `${translation.title_zh}\n${translation.body_zh}`,
    rating: master.rating,
    date: master.review_date,
    source: master.source_primary,
    object: `${master.asin}（自有ASIN）`,
    version: "未知",
    ...extra,
  };
}

const mobileSceneEvidence = roleSceneCoding
  .filter(row => row.review_status === "valid" && row.candidate_label === "travel_or_outdoor")
  .map(coding => {
    const translation = requireById(roleSceneTranslationById, coding.review_id, "关系场景译文");
    return toWorkbenchEvidence(
      coding.review_id,
      translation,
      translation.consumer_expression,
      translation.task_value,
      { sentiment: "positive" },
    );
  });

const mobileTaskEvidence = [...taskOutcomeTranslationById.values()]
  .filter(row => row.valid_labels.includes("portable_entertainment"))
  .map(translation => toWorkbenchEvidence(
    translation.review_id,
    translation,
    translation.consumer_expression,
    translation.task_value,
    { sentiment: "positive" },
  ));

const mobileMotivationIds = new Set(["RFIC0EJKONNK9", "R3FDLBNE51G1SR", "RLR59GUY3LLRR"]);
const mobileMotivationEvidence = purchaseCoding
  .filter(row => row.review_status === "valid" && mobileMotivationIds.has(row.review_id))
  .map(coding => {
    const translation = requireById(purchaseTranslationById, coding.review_id, "购买动机译文");
    return toWorkbenchEvidence(
      coding.review_id,
      translation,
      translation.consumer_expression,
      translation.motivation_value,
      { sentiment: "positive" },
    );
  });

const mobileUnmetIds = new Set(["R1MMMISQGTFKLA", "RD73IFZUY4PZR"]);
const mobileUnmetEvidence = [...unmetNeedTranslationById.values()]
  .filter(row => mobileUnmetIds.has(row.review_id))
  .map(translation => toWorkbenchEvidence(
    translation.review_id,
    translation,
    translation.consumer_expression,
    translation.task_impact,
    { sentiment: "negative" },
  ));

const upgradeEvidence = purchaseCoding
  .filter(row => row.review_status === "valid" && row.candidate_label === "replace_or_upgrade")
  .map(coding => {
    const translation = requireById(purchaseTranslationById, coding.review_id, "购买动机译文");
    return toWorkbenchEvidence(
      coding.review_id,
      translation,
      translation.consumer_expression,
      translation.motivation_value,
      { sentiment: "positive" },
    );
  });

const upgradeUnmetEvidence = [...unmetNeedTranslationById.values()]
  .map(translation => toWorkbenchEvidence(
    translation.review_id,
    translation,
    translation.consumer_expression,
    translation.task_impact,
    { sentiment: "negative" },
  ));

const partyOrganizerSignals = new Set([
  "purchaser_host",
  "mobile_host",
  "event_organizer",
  "prospective_host",
  "event_owner",
  "host",
  "birthday_hosts",
  "family_host",
  "explicit_host",
]);
const partyMotivationIds = new Set([
  "R1DLJE8HUPR4S6",
  "R1YJ73B69KGA2Z",
  "R2594FZUED2YER",
  "R2EEB5UBTF3EDG",
  "R2FAGGRYHPK4GM",
  "R3PSW1ZFQMVE9I",
  "RCMY1YY8POJWM",
  "RLR59GUY3LLRR",
  "RO2U4OHN81V2V",
]);
const partyEvidenceByKey = {
  role: partyEvidence.filter(row => partyOrganizerSignals.has(row.organizerSignal)),
  scene: partyEvidence,
  job: partyEvidence,
  motivation: partyEvidence.filter(row => partyMotivationIds.has(row.reviewId)),
  outcome: partyEvidence.filter(row => !nonParticipationOutcomes.has(row.participationOutcome)),
  "unmet-need": partyFailureEvidence,
};

const unknownRecipientRoles = new Set(["unknown", "unspecified_person"]);
const giftEvidenceByKey = {
  role: giftEvidence.filter(row => !unknownRecipientRoles.has(row.recipientRole)),
  scene: giftEvidence.filter(row => row.occasion !== "generic_gift"),
  job: giftEvidence.filter(row => row.sharedOutcome === "explicit"),
  motivation: giftEvidence.filter(row => ["buyer_to_recipient", "gift_given_unspecified"].includes(row.giftContextType)),
  outcome: giftEvidence.filter(row => row.sharedOutcome === "explicit"),
  "unmet-need": giftEvidence.filter(row => row.sharedOutcome === "negative_failure"),
};

const consumerEvidenceIds = {
  role: new Set(["R1LIPX69A9427F", "R3VEYXGAY4W3UU", "R23L5VYM81JQW0"]),
  scene: new Set(sellingEvidence.map(row => row.reviewId)),
  job: new Set(sellingEvidence.map(row => row.reviewId)),
  motivation: new Set(["R1LIPX69A9427F", "R2P8RMF66PCBXT"]),
  outcome: new Set(sellingEvidence.map(row => row.reviewId)),
};
const consumerEvidenceByKey = {
  role: sellingEvidence.filter(row => consumerEvidenceIds.role.has(row.reviewId)),
  scene: sellingEvidence.filter(row => consumerEvidenceIds.scene.has(row.reviewId)),
  job: sellingEvidence.filter(row => consumerEvidenceIds.job.has(row.reviewId)),
  motivation: sellingEvidence.filter(row => consumerEvidenceIds.motivation.has(row.reviewId)),
  outcome: sellingEvidence.filter(row => consumerEvidenceIds.outcome.has(row.reviewId)),
  "unmet-need": micEvidence,
};
const consumerTaskChain = {
  id: "family-shared-entertainment",
  title: "家庭共同娱乐",
  validated: micSellingPoint.validated,
  denominator: masterById.size,
  summary: "在家庭或朋友相聚时，购买者希望用一体化双麦让多人直接共同演唱，从而制造共同参与和欢乐；双麦可靠性是这条任务链的体验底线。",
  scopeNote: "任务链由11条已确认共同娱乐评论建立；节点下钻使用5条已翻译代表证据，未满足需求使用16条已确认问题证据。节点证据数不是消费者占比。",
  heroStats: [
    { value: micSellingPoint.validated, label: "条共同娱乐主题\n人工确认" },
    { value: micSellingPoint.evidence.length, label: "条已翻译\n代表证据" },
    { value: micMetrics.all.numerator, label: "条未满足需求\n确认问题" },
  ],
  bridge: {
    valueTitle: "让家人与朋友直接共同参与",
    valueBody: "双麦的核心价值不是“多一个配件”，而是减少轮流等待，形成共享娱乐时刻。",
    valueEvidence: `${micSellingPoint.validated} / ${masterById.size}条共同娱乐主题证据`,
    diagnosisTitle: "单支失效也会破坏多人任务",
    diagnosisBody: "当连接、充电或稳定性出问题，即使主机仍能工作，这次共同娱乐也可能失败。",
    diagnosisAction: "查看麦克风诊断",
    actionTitle: "卖共同参与，也要修可靠性底线",
    actionBody: "Listing放大“双麦共同参与”，同时管理连接预期；产品端建立双麦可靠性回归门槛。",
  },
  cannotAnswer: "完整消费者分群、各场景真实占比、自有与竞品差异、A版与D版差异，仍需后续全量编码与竞品数据验证。",
  canAnswer: "家庭共同娱乐任务真实存在，双麦是部分用户明确购买理由，共同参与是核心价值，麦克风可靠性是任务底线。",
  nodes: [
    {
      id: "role",
      label: "关系角色",
      claim: "跨代家庭成员、聚会组织者与送礼者共同出现",
      evidenceMode: "显性关系 / 场景归纳",
      evidenceLabel: `${consumerEvidenceByKey.role.length}条代表证据`,
      boundary: "只描述评论中出现的关系与购买角色，不推断年龄、收入或完整人口画像。",
    },
    {
      id: "scene",
      label: "使用场景",
      claim: "家庭互动、家庭聚会与生日场合",
      evidenceMode: "显性证据",
      evidenceLabel: `${consumerEvidenceByKey.scene.length}条代表证据`,
      boundary: "当前只证明这些场景真实出现，不代表完整场景分布。",
    },
    {
      id: "job",
      label: "用户任务",
      claim: "让两人或多人共同演唱，减少轮流等待",
      evidenceMode: "显性证据",
      evidenceLabel: `${consumerEvidenceByKey.job.length}条代表证据`,
      boundary: "共同演唱有直接原声支持；减少等待是对双麦价值的保守表达。",
    },
    {
      id: "motivation",
      label: "购买动机",
      claim: "双麦是部分用户明确说出的选择理由",
      evidenceMode: "显性选择理由",
      evidenceLabel: `${consumerEvidenceByKey.motivation.length}条明确表达`,
      boundary: "只把明确说出 glad/happy chose/got two microphones 的评论计为购买动机。",
    },
    {
      id: "outcome",
      label: "期望结果",
      claim: "共同参与、欢乐互动与聚会气氛",
      evidenceMode: "分析归纳",
      evidenceLabel: `${consumerEvidenceByKey.outcome.length}条代表证据`,
      boundary: "由 sing along、family had a blast、laughing、fun and joy 等结果表达归纳。",
    },
    {
      id: "unmet-need",
      label: "未满足需求",
      claim: "两支麦克风在整场活动中都应稳定可用",
      evidenceMode: "问题证据反推",
      evidenceLabel: `${consumerEvidenceByKey["unmet-need"].length} / ${masterById.size}条确认问题`,
      boundary: "这是由连接、充电或失效问题反推的需求，不等于用户逐字说出的愿望。",
    },
  ],
};

const giftTaskChain = {
  id: "gift-to-shared-entertainment",
  title: "礼物转化为共享娱乐",
  validated: giftMetrics.all.numerator,
  denominator: masterById.size,
  summary: "购买者把产品送给某个关系对象，但产品价值往往由整个家庭或朋友网络共同实现；易启动的共享娱乐是送礼成功条件，核心部件失效则会让礼物在开箱时彻底失败。",
  scopeNote: "36条规则候选经逐条复核，确认24条送礼语境；24条是显性证据的保守下界，不代表送礼订单占比。节点下钻均来自这24条已翻译证据。",
  heroStats: [
    { value: giftMetrics.all.numerator, label: "条送礼语境\n人工确认" },
    { value: giftMetrics.buyerToRecipient.numerator, label: "条购买者到收礼者\n关系明确" },
    { value: giftMetrics.sharedOutcome.numerator, label: "条共享或正向\n关系结果" },
  ],
  bridge: {
    valueTitle: "送给一个人，也让周围人加入",
    valueBody: "礼物的价值不止是收礼者喜欢，还会扩展为家庭、朋友与跨代成员共同参与的娱乐活动。",
    valueEvidence: `${giftMetrics.sharedOutcome.numerator} / ${giftMetrics.all.numerator}条确认送礼证据出现共享或正向结果`,
    diagnosisTitle: "开箱可靠性决定送礼是否成功",
    diagnosisBody: "一条明确失败证据显示，麦克风无法充电和工作会让礼物完全无法使用，关系场合也随之落空。",
    diagnosisAction: "查看失败证据",
    actionTitle: "把“个人礼物”表达成“共享时刻”",
    actionBody: "Listing可面向生日、节日与家庭关系表达共享价值；产品端优先保障开箱即用、双麦可靠和设置可理解。",
  },
  cannotAnswer: "送礼订单真实占比、不同收礼关系的转化率、节日销量增量、A版与D版的送礼体验差异，仍需订单与版本数据验证。",
  canAnswer: "送礼是已确认购买语境，购买者与使用者经常分离，个人惊喜会扩展为共享活动，开箱可靠性是送礼任务底线。",
  nodes: [
    {
      id: "role",
      label: "关系角色",
      claim: "购买者与使用者经常分离，关系横跨家庭、配偶、孩子、长辈与朋友",
      evidenceMode: "显性关系证据",
      evidenceLabel: `${giftEvidenceByKey.role.length}条关系明确`,
      boundary: "只统计评论明确写出的收礼关系；unknown与未指明对象不纳入该节点。",
    },
    {
      id: "scene",
      label: "使用场景",
      claim: "生日、圣诞、婚礼与乔迁等关系场合",
      evidenceMode: "显性场合证据",
      evidenceLabel: `${giftEvidenceByKey.scene.length}条场合明确`,
      boundary: "通用礼物语境不计入场合节点；场合提及数不是场景占比。",
    },
    {
      id: "job",
      label: "用户任务",
      claim: "选择一份收礼者喜欢、周围人也能加入的娱乐礼物",
      evidenceMode: "关系结果归纳",
      evidenceLabel: `${giftEvidenceByKey.job.length}条共享结果`,
      boundary: "任务由明确送礼语境与共同使用结果归纳，不等于用户逐字表达。",
    },
    {
      id: "motivation",
      label: "购买动机",
      claim: "依据唱歌兴趣、家庭共享或关系表达选择礼物",
      evidenceMode: "显性送礼动机",
      evidenceLabel: `${giftEvidenceByKey.motivation.length}条明确送礼`,
      boundary: "只计入明确购买送人或明确称为已送礼物的评论；泛化推荐不计入。",
    },
    {
      id: "outcome",
      label: "期望结果",
      claim: "个人惊喜扩展为家庭与朋友共同活动",
      evidenceMode: "显性结果 / 分析归纳",
      evidenceLabel: `${giftEvidenceByKey.outcome.length}条正向或共享结果`,
      boundary: "共享结果包括全家喜欢、聚会持续使用、邀请朋友与跨代共同参与。",
    },
    {
      id: "unmet-need",
      label: "未满足需求",
      claim: "礼物必须在开箱与关系场合中可靠可用",
      evidenceMode: "失败证据反推",
      evidenceLabel: `${giftEvidenceByKey["unmet-need"].length}条明确任务失败`,
      boundary: "当前只有一条明确送礼失败证据，因此用于识别严重性，不用于估算发生率。",
    },
  ],
};

const partyTaskChain = {
  id: "party-quick-start",
  title: "聚会快速启动与现场参与",
  validated: partyMetrics.all.numerator,
  denominator: masterById.size,
  summary: "聚会组织者购买的不是单一唱歌功能，而是一套能被带到现场、快速完成设置并让不同年龄来宾加入的活动工具；网络、电源、内容、续航和麦克风任一环节失效，都可能把组织者重新拖回现场排障。",
  scopeNote: "94条聚会宽候选中，先取25条同时命中快速启动的交集并逐条复核，确认19条、6条保持不确定；另确认7条聚会现场失败。19条是该具体任务链的保守证据下界，不代表聚会订单占比。",
  heroStats: [
    { value: partyMetrics.all.numerator, label: "条聚会快速启动\n人工确认" },
    { value: partyMetrics.participation.numerator, label: "条多人参与或\n正向现场结果" },
    { value: partyMetrics.failure.numerator, label: "条现场失败\n确认问题" },
  ],
  bridge: {
    valueTitle: "从设备准备快速进入多人参与",
    valueBody: "一体化屏幕、双麦、便携与较少接线的价值，是让组织者减少设备管理，把现场注意力留给来宾。",
    valueEvidence: `${partyMetrics.participation.numerator} / ${partyMetrics.all.numerator}条确认任务证据出现多人参与或正向现场结果`,
    diagnosisTitle: "现场可靠性是一条串联系统",
    diagnosisBody: "网络、电源、内容服务、电池、麦克风和说明支持任一断点，都可能迫使组织者临时改方案或让活动失败。",
    diagnosisAction: "查看7条现场失败",
    actionTitle: "卖更少准备，也要交代现场前提",
    actionBody: "Listing应把一体化与多人参与连接起来，同时明确内容订阅、网络、电源和续航边界；产品端按真实活动链路做回归测试。",
  },
  cannotAnswer: "全部聚会评论占比、不同人数规模的性能上限、所有场地网络兼容性、A版与D版现场表现差异，仍需全量复核与实测。",
  canAnswer: "聚会快速启动任务真实存在，组织者看重较少准备和便携，多人参与是主要结果，现场可靠性必须按完整活动链而非单一功能管理。",
  nodes: [
    {
      id: "role",
      label: "关系角色",
      claim: "活动组织者、主持人或设备负责人承担现场成功压力",
      evidenceMode: "显性组织角色",
      evidenceLabel: `${partyEvidenceByKey.role.length}条角色明确`,
      boundary: "只计入明确主持、组织、为活动购买或负责活动设备的评论，不把所有参与者都称为组织者。",
    },
    {
      id: "scene",
      label: "使用场景",
      claim: "家庭、生日、办公室、户外与中小型聚会中的现场使用",
      evidenceMode: "显性场景证据",
      evidenceLabel: `${partyEvidenceByKey.scene.length}条确认场景`,
      boundary: "只使用25条快速启动交集中的19条有效评论；其余泛化party表达不进入该节点。",
    },
    {
      id: "job",
      label: "用户任务",
      claim: "用更少设备与设置，把一群人快速带入卡拉OK活动",
      evidenceMode: "跨评论任务归纳",
      evidenceLabel: `${partyEvidenceByKey.job.length}条任务证据`,
      boundary: "由聚会场景与设置表达共同归纳，不等于每位用户逐字说出同一句任务。",
    },
    {
      id: "motivation",
      label: "购买动机",
      claim: "为便携、一体化、减少外接设备或特定活动而购买",
      evidenceMode: "显性购买 / 选择理由",
      evidenceLabel: `${partyEvidenceByKey.motivation.length}条明确理由`,
      boundary: "只计入明确说出活动目的、替换旧设备、减少手机依赖或便携需求的评论。",
    },
    {
      id: "outcome",
      label: "期望结果",
      claim: "不同年龄来宾迅速参与，活动形成共同欢乐与记忆",
      evidenceMode: "显性现场结果",
      evidenceLabel: `${partyEvidenceByKey.outcome.length}条参与结果`,
      boundary: "排除尚未实际使用以及只描述订阅摩擦、没有现场参与结果的评论。",
    },
    {
      id: "unmet-need",
      label: "未满足需求",
      claim: "网络、电源、内容、电池与麦克风必须在真实场地连续可靠",
      evidenceMode: "现场失败反推",
      evidenceLabel: `${partyEvidenceByKey["unmet-need"].length}条确认失败`,
      boundary: "7条是人工确认的严重现场失败下界，用于识别断点，不用于估算产品故障率。",
    },
  ],
};

const mobileTaskChain = {
  id: "complete-entertainment-on-the-move",
  title: "完整娱乐随场所移动",
  validated: mobileTaskEvidence.length,
  denominator: masterById.size,
  summary: "消费者要移动的不是一只音箱，而是屏幕、双麦、声音、电池与内容组成的完整娱乐能力；它需要从房间移动到朋友家、旅行、户外或活动现场后仍能继续工作。",
  scopeNote: "移动娱乐20条候选经逐条复核，确认16条、排除2条、保留2条不确定；旅行／户外19条候选确认11条。不同证据集存在评论重叠，不能相加为27条独立评论。",
  heroStats: [
    { value: mobileTaskEvidence.length, label: "条移动娱乐任务\n人工确认" },
    { value: mobileSceneEvidence.length, label: "条旅行或户外\n场景确认" },
    { value: mobileUnmetEvidence.length, label: "条移动任务\n明确失败" },
  ],
  bridge: {
    valueTitle: "把整套体验带到人群所在地",
    valueBody: "屏幕、双麦、声音与电池一起移动，才能减少到场后的重新搭建，让家庭、朋友和活动来宾继续参与。",
    valueEvidence: `${mobileTaskEvidence.length} / ${masterById.size}条移动娱乐任务证据`,
    diagnosisTitle: "物理可移动不等于任务可移动",
    diagnosisBody: "电池失效或现场内容、网络不可用时，设备即使被带到现场，完整娱乐任务仍会中断。",
    diagnosisAction: "查看移动失败证据",
    actionTitle: "卖完整迁移，不做绝对轻量承诺",
    actionBody: "Listing展示屏幕、双麦和声音如何一起随场景移动；产品端用运输、到场、联网、启动、收纳的完整链路验证便携。",
  },
  cannotAnswer: "不同场地的真实订单占比、覆盖人数与声压边界、所有网络条件兼容性、A版与D版的便携差异仍无法回答。",
  canAnswer: "完整娱乐随场所移动是真实任务；便携价值来自少带、少接、到场仍可用，而不是单纯重量更轻。",
  nodes: [
    {
      id: "role",
      label: "关系角色",
      claim: "设备携带者、活动组织者与家庭朋友参与者共同构成使用链",
      evidenceMode: "显性角色 / 场景证据",
      evidenceLabel: `${mobileSceneEvidence.length}条场景证据`,
      boundary: "只描述评论明确出现的携带、组织和参与关系，不推断固定人群画像。",
    },
    {
      id: "scene",
      label: "使用场景",
      claim: "朋友家、旅行、后院、泳池、生日、婚礼与户外活动",
      evidenceMode: "显性实际场景",
      evidenceLabel: `${mobileSceneEvidence.length}条确认场景`,
      boundary: "计划去海滩、露营或笼统写适合户外但没有实际事件的评论不计入。",
    },
    {
      id: "job",
      label: "用户任务",
      claim: "让完整卡拉OK能力随人和活动移动，而不重新拼装设备",
      evidenceMode: "显性任务 / 跨评论归纳",
      evidenceLabel: `${mobileTaskEvidence.length}条任务证据`,
      boundary: "候选必须明确出现移动、跨地点或实际外带任务；只说compact不成立。",
    },
    {
      id: "motivation",
      label: "购买动机",
      claim: "替换笨重旧设备、满足小型活动，或在推荐后选择更易移动的一体机",
      evidenceMode: "显性购买 / 替换理由",
      evidenceLabel: `${mobileMotivationEvidence.length}条明确理由`,
      boundary: "只纳入明确说明为何购买或替换的评论，不把使用后喜欢倒推为购买前动机。",
    },
    {
      id: "outcome",
      label: "期望结果",
      claim: "到场后仍保留声音、双麦和参与体验，让娱乐进入更多关系场合",
      evidenceMode: "显性结果 / 分析归纳",
      evidenceLabel: `${mobileTaskEvidence.length}条任务结果`,
      boundary: "只证明这些评论中的任务结果，不代表所有购买者都会跨场景使用。",
    },
    {
      id: "unmet-need",
      label: "未满足需求",
      claim: "电池、现场网络与内容必须让移动后的任务继续成立",
      evidenceMode: "现场问题反推",
      evidenceLabel: `${mobileUnmetEvidence.length}条明确失败`,
      boundary: "当前只使用一条电池到货失效和一条现场内容／网络失败，不估算整体发生率。",
    },
  ],
};

const upgradeTaskChain = {
  id: "all-in-one-upgrade",
  title: "从旧设备升级到一体机",
  validated: upgradeEvidence.length,
  denominator: masterById.size,
  summary: "中高价购买不是为了堆叠参数，而是替换廉价、功能有限或笨重的旧方案，把声音、屏幕、双麦、充电收纳和内容入口集中起来，减少整套娱乐任务的管理成本。",
  scopeNote: "替换／升级11条候选经逐条复核，确认5条、排除6条；5条是明确升级动机的保守下界。另有17条未满足需求证明，一体化价值会被内容、软件、电视连接、电池和支持断点削弱。",
  heroStats: [
    { value: upgradeEvidence.length, label: "条旧机升级动机\n人工确认" },
    { value: upgradeUnmetEvidence.length, label: "条一体化承诺\n确认缺口" },
    { value: masterById.size, label: "条严格子ASIN\n历史评论分母" },
  ],
  bridge: {
    valueTitle: "消费者为减少整套任务摩擦付费",
    valueBody: "高价合理性来自少拼装、少充电、少搬运，同时获得明显更好的声音、内容和多人活动能力。",
    valueEvidence: `${upgradeEvidence.length} / ${masterById.size}条明确旧机升级动机`,
    diagnosisTitle: "一体化是一份端到端体验合同",
    diagnosisBody: "订阅预期、平板性能、HDMI音频、主电池或支持任一断点，都会重新引入手机、电脑、线材或排障成本。",
    diagnosisAction: "查看17条一体化缺口",
    actionTitle: "用任务差异解释溢价，也要收紧承诺",
    actionBody: "Listing用旧方案与一体机的任务步骤对比解释价格；产品端优先修复会重新引入外部设备的系统断点。",
  },
  cannotAnswer: "全部中高价购买者的动机占比、与低价竞品的真实转化差异、硬件规格对溢价的单独贡献、A版与D版差异仍无法回答。",
  canAnswer: "存在明确的旧机升级人群；他们购买的是更完整、可持续使用的系统，而内容与软件断点会直接破坏高价价值判断。",
  nodes: [
    {
      id: "role",
      label: "关系角色",
      claim: "已有廉价、笨重或功能受限设备的升级者",
      evidenceMode: "显性既有设备证据",
      evidenceLabel: `${upgradeEvidence.length}条升级者证据`,
      boundary: "只纳入明确比较旧机、低价机或既有系统的评论。",
    },
    {
      id: "scene",
      label: "使用场景",
      claim: "家庭唱歌夜、家庭与办公室派对、个人练习和小型活动",
      evidenceMode: "显性使用语境",
      evidenceLabel: `${upgradeEvidence.length}条升级语境`,
      boundary: "场景来自同一组明确升级评论，不推断为全部升级者的场景分布。",
    },
    {
      id: "job",
      label: "用户任务",
      claim: "用一台完整系统替换廉价、分散或搬运困难的旧方案",
      evidenceMode: "跨评论任务归纳",
      evidenceLabel: `${upgradeEvidence.length}条替换任务`,
      boundary: "任务由明确旧方案、升级语言与新价值共同归纳。",
    },
    {
      id: "motivation",
      label: "购买动机",
      claim: "减少外接手机、独立充电、换电池、设备拼装和搬运",
      evidenceMode: "显性比较 / 选择理由",
      evidenceLabel: `${upgradeEvidence.length}条明确动机`,
      boundary: "只计入明确说出替换、升级或与低价方案比较的评论。",
    },
    {
      id: "outcome",
      label: "期望结果",
      claim: "以更少管理获得更好的声音、连续点歌和多人活动能力",
      evidenceMode: "显性结果 / 分析归纳",
      evidenceLabel: `${upgradeEvidence.length}条升级结果`,
      boundary: "结果只用于解释这5条升级证据中的价值，不外推为整体满意率。",
    },
    {
      id: "unmet-need",
      label: "未满足需求",
      claim: "内容、软件、电视连接、电池与支持必须共同兑现一体化",
      evidenceMode: "问题证据反推",
      evidenceLabel: `${upgradeUnmetEvidence.length}条确认缺口`,
      boundary: "17条来自五类人工确认问题主题，可识别系统断点，不能计算故障率。",
    },
  ],
};

const consumerTaskChains = [consumerTaskChain, giftTaskChain, partyTaskChain, mobileTaskChain, upgradeTaskChain];

const output = `// 此文件由 scripts/generate-mic-analysis-data.mjs 生成，请勿手工修改。\n\n`
  + `export const micEvidence = ${JSON.stringify(micEvidence, null, 2)};\n\n`
  + `export const micMetrics = ${JSON.stringify(micMetrics, null, 2)};\n\n`
  + `export const micSellingPoint = ${JSON.stringify(micSellingPoint, null, 2)};\n\n`
  + `export const giftEvidence = ${JSON.stringify(giftEvidence, null, 2)};\n\n`
  + `export const giftMetrics = ${JSON.stringify(giftMetrics, null, 2)};\n\n`
  + `export const partyEvidence = ${JSON.stringify(partyEvidence, null, 2)};\n\n`
  + `export const partyFailureEvidence = ${JSON.stringify(partyFailureEvidence, null, 2)};\n\n`
  + `export const partyMetrics = ${JSON.stringify(partyMetrics, null, 2)};\n\n`
  + `const mobileSceneEvidence = ${JSON.stringify(mobileSceneEvidence, null, 2)};\n\n`
  + `const mobileTaskEvidence = ${JSON.stringify(mobileTaskEvidence, null, 2)};\n\n`
  + `const mobileMotivationEvidence = ${JSON.stringify(mobileMotivationEvidence, null, 2)};\n\n`
  + `const mobileUnmetEvidence = ${JSON.stringify(mobileUnmetEvidence, null, 2)};\n\n`
  + `const upgradeEvidence = ${JSON.stringify(upgradeEvidence, null, 2)};\n\n`
  + `const upgradeUnmetEvidence = ${JSON.stringify(upgradeUnmetEvidence, null, 2)};\n\n`
  + `export const consumerTaskChain = ${JSON.stringify(consumerTaskChain, null, 2)};\n\n`
  + `export const giftTaskChain = ${JSON.stringify(giftTaskChain, null, 2)};\n\n`
  + `export const partyTaskChain = ${JSON.stringify(partyTaskChain, null, 2)};\n\n`
  + `export const mobileTaskChain = ${JSON.stringify(mobileTaskChain, null, 2)};\n\n`
  + `export const upgradeTaskChain = ${JSON.stringify(upgradeTaskChain, null, 2)};\n\n`
  + `export const consumerTaskChains = [consumerTaskChain, giftTaskChain, partyTaskChain, mobileTaskChain, upgradeTaskChain];\n\n`
  + `const consumerEvidenceIds = ${JSON.stringify(Object.fromEntries(Object.entries(consumerEvidenceIds).map(([key, ids]) => [key, [...ids]])), null, 2)};\n\n`
  + `export function selectConsumerEvidence(key) {\n`
  + `  if (key === "unmet-need") return micEvidence;\n`
  + `  const ids = consumerEvidenceIds[key];\n`
  + `  return ids ? micSellingPoint.evidence.filter(row => ids.includes(row.reviewId)) : [];\n`
  + `}\n\n`
  + `const giftEvidenceFilters = {\n`
  + `  role: row => !["unknown", "unspecified_person"].includes(row.recipientRole),\n`
  + `  scene: row => row.occasion !== "generic_gift",\n`
  + `  job: row => row.sharedOutcome === "explicit",\n`
  + `  motivation: row => ["buyer_to_recipient", "gift_given_unspecified"].includes(row.giftContextType),\n`
  + `  outcome: row => row.sharedOutcome === "explicit",\n`
  + `  "unmet-need": row => row.sharedOutcome === "negative_failure",\n`
  + `};\n\n`
  + `export function selectGiftEvidence(key) {\n`
  + `  const filter = giftEvidenceFilters[key];\n`
  + `  return filter ? giftEvidence.filter(filter) : [];\n`
  + `}\n\n`
  + `const partyEvidenceIds = ${JSON.stringify(Object.fromEntries(Object.entries(partyEvidenceByKey).filter(([key]) => key !== "unmet-need").map(([key, rows]) => [key, rows.map(row => row.reviewId)])), null, 2)};\n\n`
  + `export function selectPartyEvidence(key) {\n`
  + `  if (key === "unmet-need") return partyFailureEvidence;\n`
  + `  const ids = partyEvidenceIds[key];\n`
  + `  return ids ? partyEvidence.filter(row => ids.includes(row.reviewId)) : [];\n`
  + `}\n\n`
  + `export function selectMobileEvidence(key) {\n`
  + `  if (["role", "scene"].includes(key)) return mobileSceneEvidence;\n`
  + `  if (["job", "outcome"].includes(key)) return mobileTaskEvidence;\n`
  + `  if (key === "motivation") return mobileMotivationEvidence;\n`
  + `  if (key === "unmet-need") return mobileUnmetEvidence;\n`
  + `  return [];\n`
  + `}\n\n`
  + `export function selectUpgradeEvidence(key) {\n`
  + `  if (["role", "scene", "job", "motivation", "outcome"].includes(key)) return upgradeEvidence;\n`
  + `  if (key === "unmet-need") return upgradeUnmetEvidence;\n`
  + `  return [];\n`
  + `}\n\n`
  + `export function selectTaskChainEvidence(chainId, key) {\n`
  + `  if (chainId === upgradeTaskChain.id) return selectUpgradeEvidence(key);\n`
  + `  if (chainId === mobileTaskChain.id) return selectMobileEvidence(key);\n`
  + `  if (chainId === partyTaskChain.id) return selectPartyEvidence(key);\n`
  + `  if (chainId === giftTaskChain.id) return selectGiftEvidence(key);\n`
  + `  if (chainId === consumerTaskChain.id) return selectConsumerEvidence(key);\n`
  + `  return [];\n`
  + `}\n\n`
  + `const evidenceFilters = {\n`
  + `  all: () => true,\n`
  + `  blocking: row => row.blocking,\n`
  + `  commerce: row => row.commerce,\n`
  + `};\n\n`
  + `export function selectMicEvidence(key) {\n`
  + `  const filter = evidenceFilters[key];\n`
  + `  return filter ? micEvidence.filter(filter) : [];\n`
  + `}\n`;

writeFileSync(join(projectDir, "src", "mic-analysis-data.js"), output, "utf8");
