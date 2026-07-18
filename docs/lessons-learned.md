# 踩坑与经验


## 2026-07-18 评论分析校准

- **先冻结契约再扩量**：4 条和 40 条阶段允许发现结构问题，559 条阶段不应边编码边改字段。已固化到：[`07_analysis-method-and-standards.md`](../data-pilot/B0CR1R7FKP/analysis/2026-07-18/07_analysis-method-and-standards.md#全量编码契约)。
- **语义判断与机械工作分离**：Agent 负责理解评论，主流程负责定位、编号、合并和校验。已固化到：[`07_analysis-method-and-standards.md`](../data-pilot/B0CR1R7FKP/analysis/2026-07-18/07_analysis-method-and-standards.md#全量提速方案)。
- **证据必须逐字可回查**：省略号、改写和空格变化都会破坏证据校验。已固化到：[`07_analysis-method-and-standards.md`](../data-pilot/B0CR1R7FKP/analysis/2026-07-18/07_analysis-method-and-standards.md#质量门禁)。
- **并行需要受控工作池**：最大化 Agent 数会增加漂移和返工，固定 Agent、小批次和批后校验更有效。已固化到：[`07_analysis-method-and-standards.md`](../data-pilot/B0CR1R7FKP/analysis/2026-07-18/07_analysis-method-and-standards.md#推荐执行方式)。
- **受控标签与固定类型是全量统计前提**：自由极性文本和字符串/数组混用在 40 条阶段已经暴露聚合问题。已固化到：[`07_analysis-method-and-standards.md`](../data-pilot/B0CR1R7FKP/analysis/2026-07-18/07_analysis-method-and-standards.md#全量编码契约)。
