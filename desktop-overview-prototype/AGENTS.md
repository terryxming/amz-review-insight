# Prototype Instructions

Run the local server yourself and open the preview in the browser available to this environment. Do not give the user server-start instructions when you can run it.

Before making substantial visual changes, use the Product Design plugin's `get-context` skill when the visual source is unclear or no longer matches the current goal. When the user gives durable prototype-specific design feedback, preferences, or decisions, record them in `AGENTS.md`.

When implementing from a selected generated mock, treat that image as the source of truth for layout, component anatomy, density, spacing, color, typography, visible content, and hierarchy.

## Durable product decisions

- 只设计和验证桌面端，不承担手机端适配。
- 工作台采用“消费者洞察／体验诊断／决策行动”三层信息架构，默认入口为消费者洞察；原双轨总览归入决策行动。
- 消费者洞察以“关系角色／使用场景／用户任务／购买动机／期望结果／未满足需求”六维任务链组织，节点必须区分显性证据、分析归纳与问题证据反推。
- 评论提及数不得表述为消费者占比；没有显性证据时，不推断年龄、收入等人口属性。
- 决策行动以“风险修正／卖点强化”双轨为主骨架，角色视图只负责重排与突出，不复制洞察。
- 每条洞察必须显示优先级、精确证据分子／分母、消费者结果或价值、证据强度与接收角色。
- 点击麦克风洞察进入已确认的证据详情；详情保留原文、译文、星级、日期、来源、评论对象和版本判断。
- 家庭共同娱乐、礼物转化为共享娱乐、聚会快速启动与现场参与三条任务链已接入 `B0CR1R7FKP` 真实试点数据，并在消费者总览同页切换；麦克风风险与家庭双人合唱主题也使用真实复核数据，其他主题仍为结构示意，界面必须明确区分。
- 礼物任务链使用24条人工确认显性证据作为保守下界：17条明确购买者到收礼者关系，21条出现共享或正向结果，1条明确送礼任务失败；这些数字不得解释为订单占比或转化率。
- 聚会快速启动任务链使用19条人工确认交集证据作为保守下界：17条出现低准备摩擦或多人参与结果，另有7条确认现场失败；94条party宽候选不得直接进入工作台KPI。
- 完整娱乐随场所移动任务链使用16条人工确认移动任务、11条确认旅行／户外场景、3条明确移动购买动机与2条明确移动失败证据；不同集合存在重叠，不得相加为独立评论数。
- 从旧设备升级到一体机任务链使用5条明确替换／升级动机作为保守下界，17条一体化体验缺口只用于识别系统断点，不得解释为故障率。
