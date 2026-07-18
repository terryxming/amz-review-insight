# 踩坑与经验


## 2026-07-18 评论分析校准

- **先冻结契约再扩量**：4 条和 40 条阶段允许发现结构问题，559 条阶段不应边编码边改字段。已固化到：[`07_analysis-method-and-standards.md`](../data-pilot/B0CR1R7FKP/analysis/2026-07-18/07_analysis-method-and-standards.md#全量编码契约)。
- **语义判断与机械工作分离**：Agent 负责理解评论，主流程负责定位、编号、合并和校验。已固化到：[`07_analysis-method-and-standards.md`](../data-pilot/B0CR1R7FKP/analysis/2026-07-18/07_analysis-method-and-standards.md#全量提速方案)。
- **证据必须逐字可回查**：省略号、改写和空格变化都会破坏证据校验。已固化到：[`07_analysis-method-and-standards.md`](../data-pilot/B0CR1R7FKP/analysis/2026-07-18/07_analysis-method-and-standards.md#质量门禁)。
- **并行需要受控工作池**：最大化 Agent 数会增加漂移和返工，固定 Agent、小批次和批后校验更有效。已固化到：[`07_analysis-method-and-standards.md`](../data-pilot/B0CR1R7FKP/analysis/2026-07-18/07_analysis-method-and-standards.md#推荐执行方式)。
- **受控标签与固定类型是全量统计前提**：自由极性文本和字符串/数组混用在 40 条阶段已经暴露聚合问题。已固化到：[`07_analysis-method-and-standards.md`](../data-pilot/B0CR1R7FKP/analysis/2026-07-18/07_analysis-method-and-standards.md#全量编码契约)。


## 2026-07-19 全量编码与风险复核

- **计划并发不等于运行时容量**：用户确认的 8-Agent 工作池在实际环境中受 6-Agent 上限约束，应记录执行偏差，但不能倒写用户决策。已固化到：[`0001-full-review-coding-contract.md`](decisions/0001-full-review-coding-contract.md#执行偏差记录)。
- **风险筛选需要精确命中复核目标**：过宽关键词会把一般硬件体验误判成“硬件改动建议”，增加无效复核；本轮收窄后覆盖 161 条唯一 Review。已固化到：[`07_analysis-method-and-standards.md`](../data-pilot/B0CR1R7FKP/analysis/2026-07-18/07_analysis-method-and-standards.md#语义复核)。
- **语义修正不能直接批量覆盖**：风险 Agent 的建议仍可能改变事实边界，必须由主流程逐条对照中英文原文后决定是否采纳；本轮 56 条建议全部经主流程裁决。已固化到：[`07_analysis-method-and-standards.md`](../data-pilot/B0CR1R7FKP/analysis/2026-07-18/07_analysis-method-and-standards.md#实际执行记录)。
- **全量编码完成不等于业务建议完成**：主题同义归一、产物结构和当前 Listing 页面证据尚未确认，不能直接从逐条候选动作生成最终建议。已固化到：[`07_analysis-method-and-standards.md`](../data-pilot/B0CR1R7FKP/analysis/2026-07-18/07_analysis-method-and-standards.md#主题汇总与业务动作标准)。
