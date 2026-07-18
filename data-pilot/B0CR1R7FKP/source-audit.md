# B0CR1R7FKP 数据源审计

## 审计范围

- 目标：香港奥卡美国站的子 ASIN `B0CR1R7FKP`。
- 店铺：`香港奥卡-US`，Lingxing `sid=7481`，国家字段为“美国”。
- Listing 上架时间：2024-01-04。
- 查询截止：2026-07-18。
- 本阶段只验证数据来源、归属、覆盖和可追溯性，不翻译、不做评论洞察。


## 结论

评论主数据源应采用 Lingxing，Sorftime 只作为交叉校验和变体池补充，不能把两个来源的行数直接相加。

- Lingxing 美国店全量商品评论共 1735 条，本次已完整取回 1735 条。
- 其中 `ASIN=B0CR1R7FKP` 为 558 条，`review_id` 唯一数也是 558，没有 review_id 重复。
- 目标评论日期覆盖 2024-01-23 至 2026-07-08；最早评论晚于 Listing 上架日19天，不能把“最早评论日”等同于“上架日”。
- 星级分布：1星 55，2星 19，3星 28，4星 42，5星 414。
- Sorftime 返回100行、近一年、最多100条；其中 4 行为完全重复。
- 经过日期、星级、标题和正文的规范化匹配，Sorftime 有 70 行命中 Lingxing 的 66 条目标评论，只能作为交叉验证。
- Sorftime 有 30 条去重后未命中目标子 ASIN，且包含 X1、Shell S1、带支架版本等属性。因为 Sorftime 不返回评论对应的真实子 ASIN，这些评论进入“变体池待归属”，不进入目标子 ASIN 的558条主分母。


## Sorftime 未归属变体池

- Size=Break X1：8 条。
- Size=Break X2 with Mic Stand：7 条。
- Size=Break X1 with Wireless Microphones：6 条。
- Size=Break X2 with Wireless Microphones and Mic Stand：4 条。
- Size=Shell S1：3 条。
- Size=Break X2 with Wireless Microphones：1 条。
- Size=Break X2：1 条。

即使属性名包含 Break X2，也不能据此认定为 `B0CR1R7FKP`；Amazon 变体评论池会跨子 ASIN 展示，而当前 Sorftime 结果缺少 review_id、评论链接和真实评论对象。


## 版本与评论归属

已确认同一子 ASIN 在 Lingxing 中存在两个 MSKU：

- A版：`A00X220232`，业务提供为64GB；Lingxing内部品名含“1030A”。
- D版：`IK-US-Break X2-103001BLK00`，业务提供为32GB；Lingxing内部品名含“1030D”，当前 Listing 标题也为32GB。

但是 Lingxing 的558条评论明细统一显示 `MSKU=A00X220232`。这更像当前评价管理的商品映射，不足以证明每条历史评论的购买版本。因此第一版主表中全部 `version_judgement=unknown`，不能按评论日期自动切成A版或D版。


## 买家之声与退货

Lingxing VOC 当前快照返回该 ASIN 两个 MSKU：

- D版：1,029个订单、45个不满意订单、不满意率4.37%，主要原因 `ui_performance_or_quality_not_adequate`，满意度“良好”，更新于2026-07-17。
- A版：6个订单、0个不满意订单；主要原因字段仍返回 `ui_defective_item`，但在0个不满意订单的条件下不能把它当成当前高频问题。

退货分析按 MSKU 与退货时间分段：

- 2024：A版销量9,390、退货量0；D版销量25、退货量0。该结果与销售规模不相称，必须标记为“历史退货数据疑似不完整”，不能解释成零退货。
- 2025：A版714/9,072，退货率7.87%；D版471/10,495，退货率4.49%。
- 2026-01-01至2026-07-18：A版6/23，退货率26.09%，但分母很小；D版1,194/7,036，退货率16.97%。

这些值是Lingxing透传的不同年度切片，只能用于发现异常与决定后续核查，不能直接推断某一评论主题导致了退货率变化。


## 当前缺口

- 当前可调用的 Lingxing MCP 没有逐条退货留言接口，只有退货量、退货率、NCX和Top退货原因等聚合字段。
- Sorftime只能返回近一年最多100条，无法单独满足“从上架日起全部历史评论”。
- Sorftime缺少真实评论对象，无法可靠扩大严格子 ASIN 分母。
- 评论明细缺少购买时版本，A/D归属目前无法逐条确认。
- 2024退货量为0存在明显完整性疑点。
- Listing当前显示评论数1,095，而Lingxing严格子ASIN为558条；二者口径可能分别是变体组展示数与子ASIN明细数，后续必须分开呈现，不能声称558条覆盖全部页面可见评论。


## 第一版数据契约

- 严格子 ASIN 评论分母：558条Lingxing明细，以 `review_id` 去重。
- Sorftime命中项：只增加 `sorftime_validated=true`，不增加评论行。
- Sorftime未命中项：保存在变体池，`analysis_eligible=false`。
- 评论对象无法确认时不得写目标 ASIN。
- 版本无法确认时统一写 `unknown`。
- 所有指标必须能回到原始文件与 review_id；无逐条证据的数据只能作为聚合背景，不得伪造成评论证据。
