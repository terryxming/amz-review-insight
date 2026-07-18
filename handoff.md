# Amazon评论洞察Skill交接

本文件记录 `D:\amz-review-insight` 的当前可续工状态。事实口径以数据文件和自动测试为准；本文件只负责说明为什么这样做、目前做到哪里以及下一步如何继续。


## 当前状态

### 目标与范围

- 目标：把亚马逊评论分析从人工下载、翻译和粗略归纳，升级为可重复执行的Skill，服务Listing优化、设计表达和产品优化。
- 当前站点：美国站。
- 当前自有子ASIN：`B0CR1R7FKP`。
- 当前严格评论分母：558条Lingxing历史评论，`review_id`唯一。
- Sorftime当前用于跨源补充与校验，不能与Lingxing简单相加；已确认66条目标评论匹配。
- 分析对象必须是具体子ASIN。评论无法可靠判断购买时属于A版64GB还是D版32GB，版本保持未知。

### 已完成的数据基础

- 评论事实主表：`data-pilot/B0CR1R7FKP/normalized/reviews-master.jsonl`。
- 六维编码契约：`data-pilot/B0CR1R7FKP/analysis/consumer-insight-coding-schema.md`。
- 消费者主题候选池：837条候选记录，覆盖332条唯一评论；候选只负责召回，不是最终KPI。
- 候选生成脚本：`data-pilot/B0CR1R7FKP/scripts/discover-consumer-theme-candidates.mjs`。
- Lingxing买家之声、退货、Sorftime评论和Listing快照均已保存在 `data-pilot/B0CR1R7FKP/raw/`，但尚未全部进入消费者洞察闭环。

### 已验证的五条消费者任务链

1. **家庭共同娱乐**

   - 11条人工确认显性主题证据，分母558。
   - 5条已翻译代表证据。
   - 双麦是部分用户明确选择理由，共同参与是核心价值。
   - 麦克风未满足需求另有16条人工确认问题证据。

2. **礼物转化为共享娱乐**

   - 36条候选逐条复核：24条有效、9条无效、3条不确定。
   - 17 / 24条明确购买者到收礼者关系。
   - 21 / 24条出现共享或正向结果。
   - 1条明确送礼任务失败。
   - 24条是显性证据保守下界，不代表礼物订单占比。

3. **聚会快速启动与现场参与**

   - 94条party宽候选没有直接进入KPI。
   - 取聚会与快速启动的25条交集逐条复核：19条有效、6条不确定。
   - 17 / 19条出现低准备摩擦或多人参与结果。
   - 另确认7条聚会现场失败，覆盖网络、电源、内容、续航、麦克风和说明支持。
   - 19条是具体任务链的保守下界，不代表聚会订单占比。

4. **完整娱乐随场所移动**

   - 移动娱乐20条候选逐条复核：16条有效、2条无效、2条不确定。
   - 旅行／户外19条候选逐条复核：11条有效、2条无效、6条不确定。
   - 3条评论明确说明移动相关购买或替换理由。
   - 2条明确移动任务失败，分别涉及主电池失效和现场内容／网络不可用。
   - 不同证据集存在评论重叠，不能相加为27条独立评论。

5. **从旧设备升级到一体机**

   - 替换／升级11条候选逐条复核：5条有效、6条无效。
   - 消费者用中高价一体机替换廉价、功能有限或笨重的旧方案，购买的是更少拼装、充电和搬运，同时保留声音、内容与多人活动能力。
   - 17条唯一未满足需求证据覆盖内容服务透明度、软件性能、电视连接、电池可靠性和设置支持。
   - 5条是明确升级动机的保守下界；17条只用于识别系统断点，不代表故障率。

### 当前原型

- 目录：`desktop-overview-prototype/`。
- 本地预览：`http://127.0.0.1:4173/`。
- 信息架构：消费者洞察 → 体验诊断 → 决策行动。
- 消费者总览支持五条真实任务链同页切换。
- 六维节点均可下钻消费者表达、结果、评论原文、评论译文、星级、日期、来源、评论对象和版本判断。
- 只做桌面端，不承担手机端适配。

### 最近验证结果

- 数据层测试：23项通过。
- 原型数据与选择器测试：12项通过。
- `npm run build`通过。
- 1440像素桌面浏览器中五个任务链标签无换行或横向溢出。
- 新增任务链下钻数量已核对：移动链为11、11、16、3、16、2；升级链为5、5、5、5、5、17。
- 浏览器控制台无错误。
- Lighthouse桌面可访问性100分、最佳实践100分；本地原型未处理SEO、`robots.txt`与`llms.txt`。


## 下一步

### 当前优先级：补齐评论以外的数据源

自有ASIN的评论层六维复核和任务链组装已完成。下一步不是继续扩充评论主题，而是把另外两类事实源纳入同一分析流程：

1. **Lingxing买家之声**

   - 建立独立主表、分母、翻译和主题映射。
   - 与评论主题交叉验证，但不与558条评论直接相加。
   - 标记它支持、补充或反驳了哪条任务链。

2. **Lingxing退货留言**

   - 先确认MSKU到具体子ASIN的归属关系。
   - 建立独立退货分母与原因编码，不能用评论分母计算退货比例。
   - 将明确的错误预期、产品故障和操作困难映射到体验诊断与产品行动。

3. **冻结自有ASIN标签体系V1**

   - 固定五条任务链、六维节点定义、证据等级和未知处理。
   - 新数据只能补充证据或提出变更申请，不能静默改变既有口径。

### 后续顺序

1. 标准化、翻译并交叉验证Lingxing买家之声和退货留言。
2. 冻结自有ASIN标签体系V1及变更规则。
3. 使用同一标签体系处理竞品子ASIN：`B0FQCFZCS8`、`B0FRM2C79J`、`B0GCND2552`。
4. 完成自有与竞品的共同任务、差异、短板和市场空白比较。
5. 完善Excel、HTML、代理编排和正式Skill输入输出契约。


## 未决问题

- `B0CR1R7FKP` 的评论无法可靠按A版和D版归因；时间只能作为评论日期，不能替代版本字段。
- Sorftime与Lingxing评论覆盖范围不同，严格分母仍以具体子ASIN、可确认归属的Lingxing评论为准，除非后续对账证明可扩大。
- 买家之声与退货留言尚未形成与评论一致的标准化主表；三类数据必须保留各自分母。
- 消费者总览的五条任务链均为真实复核数据；风险与机会总览仍含结构示意主题，必须继续明确标注。
- “跨代关系”和“跨地点迁移”也可作为现有任务链的筛选层，但当前没有单独复制为同义任务链。
- 当前目录不是Git仓库，无法按项目规则执行pull、commit和push，也无法支持跨设备同步；需要用户明确授权后再初始化或连接远程仓库。


## 环境备忘

- 工作目录：`D:\amz-review-insight`。
- 系统：Windows PowerShell。
- Node.js与npm可用。
- 原型开发服务器端口：`4173`。
- 原型使用React、Vite和Phosphor Icons。
- 不新增移动端适配。
- 不要手工修改 `desktop-overview-prototype/src/mic-analysis-data.js`，它由 `scripts/generate-mic-analysis-data.mjs`生成。
- 新增主题时遵循：先失败测试 → 人工复核文件 → 全部有效证据译文 → 洞察文档 → 生成数据契约 → 原型接入 → 浏览器验收。

### 验证命令

```powershell
node --test 'D:\amz-review-insight\data-pilot\B0CR1R7FKP\scripts\discover-consumer-theme-candidates.test.mjs' 'D:\amz-review-insight\data-pilot\B0CR1R7FKP\scripts\gift-theme-analysis.test.mjs' 'D:\amz-review-insight\data-pilot\B0CR1R7FKP\scripts\party-theme-analysis.test.mjs' 'D:\amz-review-insight\data-pilot\B0CR1R7FKP\scripts\purchase-motivation-analysis.test.mjs' 'D:\amz-review-insight\data-pilot\B0CR1R7FKP\scripts\role-scene-analysis.test.mjs' 'D:\amz-review-insight\data-pilot\B0CR1R7FKP\scripts\task-outcome-analysis.test.mjs' 'D:\amz-review-insight\data-pilot\B0CR1R7FKP\scripts\unmet-needs-analysis.test.mjs'
```

```powershell
Set-Location 'D:\amz-review-insight\desktop-overview-prototype'
npm test
npm run build
```


## 上次会话摘要

- 明确消费者洞察不能退化成差评分析，必须覆盖关系角色、使用场景、用户任务、购买动机、期望结果和未满足需求。
- 建立六维编码契约，规则只负责候选召回，最终KPI必须逐条人工复核。
- 委派三个子代理并行完成购买动机、关系场景、用户任务与期望结果复核；主代理完成未满足需求复核与统一审计。
- 新增“完整娱乐随场所移动”和“从旧设备升级到一体机”，消费者总览现有五条真实任务链。
- 对重复评论译文建立 `translation_ref`，同一条评论只维护一份权威中文译文。
- 五条任务链所有节点均支持完整双语证据下钻。
- 明确评论证据数是保守下界，不是消费者占比、订单占比或故障率。
- 下一步补齐买家之声与退货留言，再冻结自有ASIN标签体系V1并进入竞品分析。
