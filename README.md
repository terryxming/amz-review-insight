# Amazon Review Insight

本仓库用于把 Amazon 评论证据整理为可追溯、可下钻、可行动的 VOC 洞察，服务 Listing 文案、主副图与 A+ 优化，以及产品迭代决策。当前完整试点对象为美国站 ASIN `B0CR1R7FKP`。


## 仓库结构

- `data-pilot/B0CR1R7FKP/source-exports/`：评论源导出、字段盘点与合并评论事实源。
- `data-pilot/B0CR1R7FKP/analysis/`：校准编码、正式编码、主题分析与业务建议。
- `data-pilot/B0CR1R7FKP/reports/`：报告试点、结构化报告数据与单文件 HTML 交付。
- `data-pilot/B0CR1R7FKP/supporting-data/`：退货等辅助数据，不属于评论分析正式产物序列。
- `scripts/`：编码校验、主题刷新与报告构建脚本。
- `docs/`：决策记录、踩坑记录与 Skill v1.0.0 规划材料。


## 事实源

- 评论事实源：`04_merged-reviews.jsonl`。
- 逐条编码事实源：`08_full-review-coding.jsonl`。
- 主题事实源：`12_full-theme-analysis.json`。
- 业务建议事实源：`13_business-recommendations.md`。
- 报告消费数据：`17_full-overview-report.json`。

完整编号、路径与状态以 [`artifact-index.md`](data-pilot/B0CR1R7FKP/artifact-index.md) 为准；当前续工状态以 [`handoff.md`](handoff.md) 为准。
