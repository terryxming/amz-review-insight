# Amazon 评论洞察 Skill 交接

本文件只记录当前可续工状态。评论、编码、主题、建议与全量报告数据的正式事实源分别是 `04_merged-reviews.jsonl`、`08_full-review-coding.jsonl`、`12_full-theme-analysis.json`、`13_business-recommendations.md` 与 `17_full-overview-report.json`；产物编号与状态以 `artifact-index.md` 为准。


## 当前状态

- 当前试点对象为 Amazon 美国站 ASIN `B0CR1R7FKP`。
- `04_merged-reviews.jsonl` 是唯一评论事实源，共 559 条、每条固定 13 个字段；SHA-256 为 `6dd60229bdcfbb35165e521bfeceb3511488b99a908f209bb11ff55a120e820a`。
- `08_full-review-coding.jsonl` 已完成 559 条 Review 层编码与 2,546 个反馈点编码，并完成机械全检和全量语义复核。
- `12_full-theme-analysis.json` 已完成全量主题归并：10 个消费者与场景主题、16 个产品体验主题、8 条机会链；515 条 Review 进入消费者与场景主题，44 条因证据不足未强行归类。
- `13_business-recommendations.md` 已基于全部 559 条 Review 形成 14 条业务建议；Listing 页面事实已于 2026-07-19 核对。
- `14_overview-pilot.md`、`15_overview-report-pilot.json` 与 `16_overview-report-pilot.html` 是已确认并冻结的 40 条报告校准快照，不承担全量数据角色，也不随之后的 `08` 语义修正回写。
- `17_full-overview-report.json` 与 `18_full-overview-report.html` 已完成。它们直接消费 `08 + 12 + 13` 并复用 `14–16` 的内容结构、数据契约与界面交互，没有重新执行 559 条语义分析。
- 全量报告包含 559 条 Review、2,546 个反馈点、6 条发现到行动链和 14 条业务动作；动作卡区分主题覆盖范围、完整精确动作证据和最多 8 条代表证据，所有证据弹窗按 8 条一页渲染。
- 仓库产物已按 `source-exports`、`analysis`、`reports` 与 `supporting-data` 归位；`.playwright-cli`、`outputs` 与 Python 字节码缓存不进入仓库。
- 14 项动作共引用 476 条唯一 Review，其中 437 条不在 40 条分层试点中；单项动作覆盖 14–321 条 Review、15–603 个精确反馈点，不再出现所有动作都显示 8 条的假全量现象。


## 下一步

1. 按 `docs/amazon-review-insight-skill-v1-planning.md` 开始固化 Skill `v1.0.0`。
2. 先解决数据清洗不可重复和 40 条校准快照缺少输入版本绑定的问题，再封装编码、主题、建议与报告流程。
3. 使用非卡拉 OK 品类做前向测试，验证 schema、主题归并与业务建议不会过拟合当前样本。
4. 实施 Listing、副图、A+、五点或产品迭代前，重新核对在线 Listing，并为动作补充后台指标或实验数据。


## 未决问题

- 评论证据能支持消费者、场景、任务、结果与问题洞察，但不能单独证明转化率、退货率、利润或改版增量；这些仍需后台与实验数据验证。
- `13` 中的 Listing 页面事实核对日期为 2026-07-19。真正实施页面修改前，应重新核对在线 Listing，避免把页面变化误当成评论洞察。
- `17` 中动作的 `source_review_rows` 表示关联主题覆盖范围，`evidence_refs` 表示由 `12` 的产品主题 `unit_id` 与机会链 `关联unit_id` 重建的完整精确动作证据，`representative_evidence_refs` 只是最多 8 条的展示子集；三种口径不能混用。
- `14–16` 是历史校准快照；当前 `scripts/build-overview-report-pilot.py` 读取已经刷新过的 `08`，其购买动机与决策结果覆盖数已不同，不能原样复现快照。不要为让脚本通过而静默改写已确认产物，后续应显式绑定校准输入版本。


## 环境备忘

- 仓库路径：`D:\amz-review-insight`；当前分支：`main`。
- 本轮分析、报告、脚本与目录治理成果已纳入仓库版本管理；跨设备续工前先拉取 `origin/main`。
- 正式报告路径：`data-pilot/B0CR1R7FKP/reports/2026-07-18/18_full-overview-report.html`。
- 40 条试点生成脚本为 `scripts/build-overview-report-pilot.py`；全量报告生成脚本为 `scripts/build-full-overview-report.py`。
- 用户根目录下旧的亚马逊评论 Skill 已由用户删除。仓库内文档与正式产物是当前工作依据。
- JSONL 始终是评论与编码数据的唯一事实源；不要同时生成 Excel、CSV 或无意义中间文件。


## 上次会话摘要

- 完成 `17_full-overview-report.json` 与 `18_full-overview-report.html`，全量组装复用了已确认的报告结构，没有重做编码、主题发现或业务建议。
- 修正全量报告证据组装：总览和发现使用完整主题 Review 集合；动作 `evidence_refs` 从 `12` 的完整主题单元重建，代表证据与每页 8 条展示单独处理，没有重做 `08`、`12`、`13`。
- 强化机械门禁：逐项校验动作预期与实际 `unit_id` 集合相等、引用来源可追溯、无重复、数量分布未被 8 条上限截断，并确认 437 条精确证据 Review 位于 40 条试点之外。
- 浏览器验收通过：发现 F-01 显示 154 条关联证据并分页为 20 页；动作 V-02 显示 308 条 Review、603 个精确反馈点并分页为 39 页；翻页正常，控制台 0 错误、0 警告。
- 完成仓库归位：`14–18` 移入 `reports`，辅助业务数据移入 `supporting-data`，删除并忽略三类运行缓存，同时更新根 README、产物索引、路径引用和目录布局决策。
