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


## 2026-07-19 报告试点与状态维护

- **区分历史试点与当前状态文档**：试编码、主题试点和报告试点中的“4 条”“40 条”是当时真实的执行范围，不能为了显示最新进度而回写成全量；当前状态以 [`artifact-index.md`](../data-pilot/B0CR1R7FKP/artifact-index.md) 与 [`handoff.md`](../handoff.md) 为主事实入口，方法文档顶部只保留链接式摘要。
- **分开全量分析与全量报告组装**：`08`、`12`、`13` 已经完成全量编码、主题归并和业务建议，`14–16` 只负责校准报告结构。正式全量报告直接消费 `08 + 12 + 13`，不得因报告尚未全量化而重复执行 559 条语义分析。已固化到：[`07_analysis-method-and-standards.md`](../data-pilot/B0CR1R7FKP/analysis/2026-07-18/07_analysis-method-and-standards.md) 与 [`handoff.md`](../handoff.md)。


## 2026-07-19 全量报告组装与验收

- **全量化是组装，不是重做语义分析**：正式报告直接消费已经完成的 `04`、`08`、`12`、`13`，复用已确认的 `14–16` 报告契约，避免同一批评论产生第二套编码或主题事实。已固化到：[`build-full-overview-report.py`](../scripts/build-full-overview-report.py) 与 [`artifact-index.md`](../data-pilot/B0CR1R7FKP/artifact-index.md)。
- **关联主题覆盖与精确动作证据必须分开**：`source_review_rows` 表示动作关联主题覆盖的 Review 范围，`evidence_refs` 表示能直接支撑该动作的反馈点；界面只能用后者标注“动作证据”数量。已固化到：[`17_full-overview-report.json`](../data-pilot/B0CR1R7FKP/reports/2026-07-18/17_full-overview-report.json) 与 [`build-full-overview-report.py`](../scripts/build-full-overview-report.py)。
- **全量证据工作台必须分页渲染**：主题可能关联数百条 Review，不能一次把全部证据卡插入页面；当前固定每页 8 条，并保留星级和反馈点倾向两个有业务意义的筛选条件。已固化到：[`18_full-overview-report.html`](../data-pilot/B0CR1R7FKP/reports/2026-07-18/18_full-overview-report.html)。
- **数据契约校验不能替代浏览器验收**：JSON 数量、引用和字段校验通过后，仍需在真实浏览器检查弹窗、主题切换、分页、筛选和控制台；模板运行时契约错误只有这一层能可靠暴露。已固化到：[`build-full-overview-report.py`](../scripts/build-full-overview-report.py) 与 [`handoff.md`](../handoff.md)。
- **展示上限绝不能进入统计口径**：8 条只负责代表证据和分页渲染；总览、发现和动作按钮必须展示完整 Review 与反馈点总量。已固化到：[`07_analysis-method-and-standards.md`](../data-pilot/B0CR1R7FKP/analysis/2026-07-18/07_analysis-method-and-standards.md#全量报告组装与验收) 与 [`build-full-overview-report.py`](../scripts/build-full-overview-report.py)。
- **全量覆盖与精确引用必须一起刷新**：此前只扩展动作的 `source_review_rows`，却保留了 40 条试点的静态 `evidence_refs`；现在精确引用从 `12` 的主题 `unit_id` 重新建立，并校验实际集合与预期集合完全相等。已固化到：[`build-full-overview-report.py`](../scripts/build-full-overview-report.py)。
- **非空校验发现不了假全量**：必须额外检查各模块数量不是同一个展示上限、动作证据覆盖试点外 Review，并在浏览器核对按钮总数、弹窗总数和分页。已固化到：[`07_analysis-method-and-standards.md`](../data-pilot/B0CR1R7FKP/analysis/2026-07-18/07_analysis-method-and-standards.md#全量报告组装与验收)。
- **模板替换需要最终片段断言**：字符串模板按顺序替换时，新增代码可能引用尚未注入的函数，或目标片段未命中却静默继续；构建后必须断言最终 HTML 含所需函数与文案，再做浏览器验收。已固化到：[`build-full-overview-report.py`](../scripts/build-full-overview-report.py)。
