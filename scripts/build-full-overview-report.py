from __future__ import annotations

import hashlib
import importlib.util
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "data-pilot" / "B0CR1R7FKP"
SOURCE_DIR = DATA_ROOT / "source-exports" / "2026-07-18"
ANALYSIS_DIR = DATA_ROOT / "analysis" / "2026-07-18"
REPORT_DIR = DATA_ROOT / "reports" / "2026-07-18"
REVIEWS_PATH = SOURCE_DIR / "04_merged-reviews.jsonl"
CODING_PATH = ANALYSIS_DIR / "08_full-review-coding.jsonl"
PILOT_CODING_PATH = ANALYSIS_DIR / "06_stratified-pilot-coding.jsonl"
THEME_PATH = ANALYSIS_DIR / "12_full-theme-analysis.json"
ACTION_PATH = ANALYSIS_DIR / "13_business-recommendations.md"
DATA_PATH = REPORT_DIR / "17_full-overview-report.json"
HTML_PATH = REPORT_DIR / "18_full-overview-report.html"
PILOT_BUILDER_PATH = ROOT / "scripts" / "build-overview-report-pilot.py"
FULL_REVIEW_COUNT = 559

SECTION_IDS = [
    "core",
    "audience",
    "contexts",
    "motivation",
    "expectations",
    "value-formation",
    "value-interruption",
    "unmet-and-decisions",
    "actions-source",
    "methodology-source",
]

ACTION_THEME_IDS = {
    "L-01": ["UT-05", "PT-06"],
    "L-02": ["PT-01"],
    "L-03": ["PT-07"],
    "L-04": ["UT-06", "PT-05", "PT-08", "PT-09"],
    "V-01": ["UT-01", "UT-02", "UT-03", "OC-01", "OC-02", "OC-03"],
    "V-02": ["UT-06", "PT-01", "PT-06", "PT-09", "OC-06"],
    "V-03": ["UT-05", "PT-04", "PT-06", "OC-05"],
    "V-04": ["UT-03", "PT-07", "PT-11", "PT-13"],
    "V-05": ["UT-07", "PT-02", "PT-03", "PT-10", "OC-07"],
    "P-01": ["PT-01", "PT-13", "PT-14"],
    "P-02": ["PT-04", "PT-05", "PT-06", "PT-08"],
    "P-03": ["PT-02"],
    "P-04": ["PT-07"],
    "P-05": ["PT-10", "PT-11"],
}


def load_pilot_builder():
    spec = importlib.util.spec_from_file_location("overview_pilot_builder", PILOT_BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load the approved pilot report builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


pilot = load_pilot_builder()


def paragraph(text: str) -> dict:
    return {"type": "paragraph", "text": text, "review_rows": []}


def bullet_list(items: list[str]) -> dict:
    return {"type": "list", "items": items, "review_rows": []}


def section(section_id: str, title: str, lead: list[dict], subsections: list[dict]) -> dict:
    rows = sorted({row for item in subsections for row in item["review_rows"]})
    return {
        "id": section_id,
        "title": title,
        "lead_blocks": lead,
        "subsections": subsections,
        "review_rows": rows,
    }


def subsection(title: str, blocks: list[dict], rows: list[int]) -> dict:
    review_rows = sorted(set(rows))
    matched_reviews = len(review_rows)
    return {
        "title": title,
        "blocks": blocks,
        "review_rows": review_rows,
        "coverage": {
            "matched_reviews": matched_reviews,
            "total_reviews": FULL_REVIEW_COUNT,
            "percentage": round(matched_reviews / FULL_REVIEW_COUNT * 100),
        },
    }


def build_evidence_reviews() -> list[dict]:
    coding_rows = pilot.load_jsonl(CODING_PATH)
    raw_reviews = pilot.load_jsonl(REVIEWS_PATH)
    evidence = []
    for coding in coding_rows:
        data_row = coding["来源定位"]["数据行"]
        raw = raw_reviews[data_row - 1]
        review_layer = coding["Review层编码"]
        evidence.append(
            {
                "data_row": data_row,
                "coding_index": coding["编码序号"],
                "review_id": coding["来源定位"]["review_id"],
                "date": raw["评论日期"],
                "stars": raw["评星"],
                "title_en": raw["标题"],
                "review_en": raw["评论"],
                "title_zh": raw["标题_中文"],
                "review_zh": raw["评论_中文"],
                "consumer": review_layer["消费者"],
                "scenes": review_layer["使用场景"],
                "tasks": review_layer["用户任务"],
                "motivations": review_layer["购买动机"],
                "expectations": review_layer["期望结果"],
                "inferences": coding["Review层推测"],
                "outcomes": review_layer["实际结果"],
                "satisfiers": review_layer["满意点"],
                "value_chains": review_layer["价值链"],
                "unmet_needs": review_layer["未满足的需求"],
                "evidence_strength": review_layer["证据强度"],
                "sentiment": review_layer["总体极性"],
                "decision": review_layer["决策结果"],
                "units": [
                    {
                        "unit_id": unit["unit_id"],
                        "quote_en": unit["证据原文"],
                        "fact_zh": unit["事实判断"],
                        "polarity": unit["极性"],
                        "dimensions": unit["维度"],
                    }
                    for unit in coding["反馈点"]
                ],
            }
        )
    return evidence


def theme_index(themes: dict) -> dict[str, dict]:
    return {
        item[id_key]: item
        for group, id_key in [
            (themes["用户主题"], "主题ID"),
            (themes["产品体验主题"], "主题ID"),
            (themes["用户机会链"], "机会链ID"),
        ]
        for item in group
    }


def rows_for(theme_ids: list[str], index: dict[str, dict]) -> list[int]:
    return sorted({row for theme_id in theme_ids for row in index[theme_id]["数据行"]})


def exact_unit_ids(theme_ids: list[str], index: dict[str, dict]) -> set[str]:
    unit_ids: set[str] = set()
    for theme_id in theme_ids:
        if theme_id.startswith("PT-"):
            unit_ids.update(index[theme_id]["unit_id"])
        elif theme_id.startswith("OC-"):
            unit_ids.update(index[theme_id]["关联unit_id"])
    return unit_ids


def evidence_role(action: dict, polarity: str) -> str:
    if action["id"] == "P-05":
        return {
            "正向": "已验证优势",
            "负向": "体验边界",
            "正负混合": "条件边界",
            "中性": "背景证据",
        }[polarity]
    if action["category"] == "visual":
        return {
            "正向": "价值证据",
            "负向": "失败边界",
            "正负混合": "条件边界",
            "中性": "背景证据",
        }[polarity]
    return {
        "正向": "正向边界",
        "负向": "问题证据",
        "正负混合": "条件冲突",
        "中性": "背景证据",
    }[polarity]


def build_action_evidence(
    action: dict,
    theme_ids: list[str],
    index: dict[str, dict],
    evidence_by_row: dict[int, dict],
) -> list[dict]:
    exact_theme_ids = [
        theme_id for theme_id in theme_ids if theme_id.startswith(("PT-", "OC-"))
    ]
    theme_units = {
        theme_id: exact_unit_ids([theme_id], index) for theme_id in exact_theme_ids
    }
    unit_lookup = {
        unit["unit_id"]: (review, unit)
        for review in evidence_by_row.values()
        for unit in review["units"]
    }
    references = []
    for unit_id in sorted(exact_unit_ids(theme_ids, index)):
        review, unit = unit_lookup[unit_id]
        references.append(
            {
                "review_row": review["data_row"],
                "unit_id": unit_id,
                "role": evidence_role(action, unit["polarity"]),
                "source_theme_ids": [
                    theme_id for theme_id in exact_theme_ids if unit_id in theme_units[theme_id]
                ],
            }
        )
    return references


def representative_evidence_refs(
    references: list[dict], evidence_by_row: dict[int, dict], limit: int = 8
) -> list[dict]:
    strength_rank = {"高": 0, "中": 1, "低": 2}
    polarity_order = {"负向": 0, "正负混合": 1, "正向": 2, "中性": 3}
    unit_by_id = {
        unit["unit_id"]: unit
        for review in evidence_by_row.values()
        for unit in review["units"]
    }

    def rank(reference: dict) -> tuple:
        review = evidence_by_row[reference["review_row"]]
        level = review["evidence_strength"]["等级"]
        strength = next((value for key, value in strength_rank.items() if key in level), 3)
        polarity = unit_by_id[reference["unit_id"]]["polarity"]
        star_rank = review["stars"] if polarity in {"负向", "正负混合"} else -review["stars"]
        return strength, star_rank, review["data_row"], reference["unit_id"]

    buckets: dict[tuple[str, str], list[dict]] = {}
    for reference in references:
        polarity = unit_by_id[reference["unit_id"]]["polarity"]
        key = (reference["source_theme_ids"][0], polarity)
        buckets.setdefault(key, []).append(reference)
    ordered_keys = sorted(
        buckets,
        key=lambda key: (key[0], polarity_order[key[1]]),
    )
    for bucket in buckets.values():
        bucket.sort(key=rank)

    selected = []
    while len(selected) < limit and any(buckets[key] for key in ordered_keys):
        for key in ordered_keys:
            if buckets[key] and len(selected) < limit:
                selected.append(buckets[key].pop(0))
    return selected


def representative_rows(rows: list[int], evidence_by_row: dict[int, dict], limit: int = 8) -> list[int]:
    candidates = [evidence_by_row[row] for row in rows]
    strength_rank = {"高": 0, "中": 1, "低": 2}

    def rank(review: dict) -> tuple:
        strength = str(review["evidence_strength"])
        strength_value = next((value for key, value in strength_rank.items() if key in strength), 3)
        return strength_value, review["data_row"]

    buckets = [
        sorted((item for item in candidates if item["stars"] <= 2), key=rank),
        sorted((item for item in candidates if item["stars"] == 3), key=rank),
        sorted((item for item in candidates if item["stars"] >= 4), key=rank),
    ]
    selected = []
    while len(selected) < limit and any(buckets):
        for bucket in buckets:
            if bucket and len(selected) < limit:
                selected.append(bucket.pop(0)["data_row"])
    return sorted(selected)


def theme_rows(theme_ids: list[str], index: dict[str, dict]) -> list[int]:
    return rows_for(theme_ids, index)


def build_narrative(index: dict[str, dict], evidence_by_row: dict[int, dict], mixed: int) -> dict:
    count = lambda theme_id: index[theme_id]["涉及Review数"]
    pt_count = lambda theme_id: index[theme_id]["反馈点数"]
    pt_polarity = lambda theme_id, polarity: index[theme_id]["反馈点极性分布"].get(polarity, 0)
    sections = [
        section(
            "core",
            "核心结论",
            [
                paragraph("从 559 条唯一评论看，消费者购买的并不只是一台可以唱歌的音响，而是一套能够**降低准备负担、组织多人参与并维持整场娱乐活动**的一体式工具。"),
                paragraph("价值沿着一条连续任务链形成：**准备设备 -> 找到歌曲 -> 邀请他人参与 -> 持续演唱 -> 活动不中断**。双麦、屏幕、音箱、应用和便携性只有放进这条链路里，才具有真实业务含义。"),
                paragraph("声音、双麦、屏幕和便携让参与更容易发生；歌曲、供电、系统、同步或连接任一关键环节失效，则可能让整场任务一起中断。"),
                paragraph(f"全量编码中有 {mixed} 条评论同时提供明确满意点和未满足需求。用户可能认可声音、便携或双麦，同时因歌曲成本、供电、系统性能或连接问题降低评价、绕行甚至退货，因此不能把 VOC 机械拆成好评与差评两组。"),
            ],
            [],
        ),
        section(
            "audience",
            "消费者与需求背景",
            [paragraph("评论能识别购买者和使用关系，却不能可靠推断年龄、收入或职业。以下人群是评论中反复出现的业务角色，主题之间允许重叠。")],
            [
                subsection("家庭娱乐的发起者", [paragraph(f"`UT-01` 涉及 {count('UT-01')} 条 Review。购买者常以家长、伴侣或家庭成员身份组织共同娱乐；双麦的价值是让伴侣、孩子、长辈和朋友更容易同时参与，而不是单纯增加配件数量。")], theme_rows(["UT-01"], index)),
                subsection("派对与活动的组织者", [paragraph(f"`UT-02` 涉及 {count('UT-02')} 条 Review。这类用户承担让生日、办公室活动、亲友聚会或其他现场开始并持续运转的责任，关注的是整场活动的可控性。")], theme_rows(["UT-02"], index)),
                subsection("户外与跨场地使用者", [paragraph(f"`UT-03` 涉及 {count('UT-03')} 条 Review。他们需要在家庭、营地、户外或不同场地之间移动设备，因此重量、肩带、麦克风收纳、续航和网络替代路径会共同影响价值。")], theme_rows(["UT-03"], index)),
                subsection("礼物购买者与日常练习者", [paragraph(f"礼物关系主题 `UT-04` 涉及 {count('UT-04')} 条 Review，个人练习与家庭日常主题 `UT-08` 涉及 {count('UT-08')} 条。前者要求收礼后尽快成功，后者更看重低摩擦、高频使用。")], theme_rows(["UT-04", "UT-08"], index)),
            ],
        ),
        section(
            "contexts",
            "使用场景与用户任务",
            [paragraph("评论里的场景不是背景标签，而是产品必须完成的任务环境。实际场景、计划场景、用户估计与转述证据在证据下钻中保持分开。")],
            [
                subsection("家庭共同参与", [paragraph("任务是让不同年龄、熟练度和兴趣的人快速加入，完成合唱、轮唱和共同娱乐；组织者不应先成为设备管理员。")], theme_rows(["OC-01"], index)),
                subsection("派对和活动持续运转", [paragraph("任务是完成搬运、供电、联网、点歌、显示和多人轮换，并确保声音、麦克风、应用与电池在活动期间不中断。")], theme_rows(["OC-02"], index)),
                subsection("户外与跨场地娱乐", [paragraph("任务是轻松运输、快速重新布置，并在电源或网络条件变化时仍能继续使用。")], theme_rows(["OC-03"], index)),
                subsection("礼物开箱即成功", [paragraph("任务是让收礼者无需复杂学习就能完成充电、开机、联网、打开内容和取麦演唱；首次失败会直接破坏礼物关系体验。")], theme_rows(["OC-04"], index)),
                subsection("个人练习与家庭日常", [paragraph("任务是随时开始、重复使用，并在独唱、练习和小范围家庭娱乐之间切换，不需要每次重建复杂连接。")], theme_rows(["UT-08"], index)),
            ],
        ),
        section(
            "motivation",
            "为什么购买",
            [paragraph("购买动机的共同方向是减少拼装和准备成本，同时获得足够好的演唱结果。动机未知时不从星级或结果反推。")],
            [
                subsection("一体化降低准备负担", [paragraph(f"低学习成本主题 `UT-06` 涉及 {count('UT-06')} 条 Review。屏幕、音箱、双麦和内容入口集成在同一设备中，是用户愿意选择它的重要原因。")], theme_rows(["UT-06"], index)),
                subsection("声音与演唱体验", [paragraph(f"声音敏感主题 `UT-07` 涉及 {count('UT-07')} 条 Review。用户购买的不只是大音量，还包括清晰、可调、适合多人参与且不会被延迟打断的演唱体验。")], theme_rows(["UT-07"], index)),
                subsection("歌曲可得与持续成本", [paragraph(f"歌曲与成本主题 `UT-05` 涉及 {count('UT-05')} 条 Review。用户希望快速找到想唱的歌，但应用入口、第三方账号、订阅、网络和地区边界共同决定实际可得性。")], theme_rows(["UT-05"], index)),
                subsection("价格价值与购买信心", [paragraph(f"价格价值主题 `UT-10` 涉及 {count('UT-10')} 条 Review。声音、便携、易用和内容链路共同支撑价格合理性；任何关键断点都会让用户重新比较替代品。")], theme_rows(["UT-10"], index)),
            ],
        ),
        section(
            "expectations",
            "购买前期待什么，实际得到什么",
            [paragraph("用户期待的是一条完整结果链，而不是若干孤立功能：拿到设备后能快速开始、找到歌曲、获得好声音，并在需要时可靠使用。")],
            [
                subsection("被兑现的期待", [paragraph(f"声音主题 `PT-10` 有 {pt_count('PT-10')} 个反馈点，其中 {pt_polarity('PT-10', '正向')} 个正向；便携主题 `PT-11` 有 {pt_count('PT-11')} 个反馈点，其中 {pt_polarity('PT-11', '正向')} 个正向；设置易用性 `PT-09` 也以正向反馈为主。这些是当前体验最稳定的价值支柱。")], theme_rows(["PT-10", "PT-11", "PT-09"], index)),
                subsection("部分兑现的期待", [paragraph("大屏、应用入口、双麦和电池能够支持任务，但它们都存在条件边界。用户往往先获得部分价值，再在订阅、歌词、充电、系统性能或异常恢复处遇到阻力。")], theme_rows(["PT-01", "PT-03", "PT-05", "PT-06"], index)),
                subsection("完全中断的期待", [paragraph(f"基础可靠可用主题 `UT-09` 涉及 {count('UT-09')} 条 Review。当供电、整机、麦克风、系统或连接链路失效时，结果不是单项功能扣分，而是原定演唱和活动任务无法完成。")], theme_rows(["UT-09"], index)),
            ],
        ),
        section(
            "value-formation",
            "价值在哪里形成",
            [],
            [
                subsection("声音把设备能力转成现场结果", [paragraph("清晰度、音量、麦克风控制与效果调节让家庭、派对和户外场景真正成立。声音是最强的正向体验资产，应继续被保护。")], theme_rows(["PT-10", "PT-03"], index)),
                subsection("便携与收纳降低场地切换成本", [paragraph("机身、肩带和麦克风收纳让设备能被带走、快速部署并减少配件管理，便携不是外观卖点，而是跨场地任务的一部分。")], theme_rows(["PT-11"], index)),
                subsection("低学习成本扩大共同参与", [paragraph("较顺畅的开机、设置和操作会让儿童、长辈、非技术用户与临时参与者更容易加入，直接放大家庭与活动价值。")], theme_rows(["PT-09", "OC-06"], index)),
            ],
        ),
        section(
            "value-interruption",
            "价值在哪里中断",
            [paragraph("以下问题不应按功能列表阅读。它们分别阻断开始、持续演唱、跨设备使用或购买信任。")],
            [
                subsection("歌曲、应用与订阅边界", [paragraph(f"`PT-06` 有 {pt_count('PT-06')} 个反馈点，其中负向 {pt_polarity('PT-06', '负向')}、正负混合 {pt_polarity('PT-06', '正负混合')}。应用入口存在不等于歌曲免费、完整或持续可用，内容落差会被用户解释为整机价值问题。")], theme_rows(["PT-06"], index)),
                subsection("供电与可靠性", [paragraph(f"`PT-01` 有 {pt_count('PT-01')} 个反馈点，其中负向 {pt_polarity('PT-01', '负向')}；`PT-14` 有 {pt_count('PT-14')} 个反馈点，其中负向 {pt_polarity('PT-14', '负向')}。充电、续航、边充边用、休眠唤醒和整机稳定性会决定活动能否持续。")], theme_rows(["PT-01", "PT-14"], index)),
                subsection("屏幕、系统与同步", [paragraph("触控、歌词可读、系统卡顿和麦克风返声延迟会直接干扰点歌与演唱节奏。同步问题规模较小，但严重度高，不能仅以数量排序。")], theme_rows(["PT-02", "PT-05", "PT-08"], index)),
                subsection("外接设备能力边界", [paragraph("电视、投影、外接音响与 HDMI 的画面、歌词和声音路径并不等价。页面若不区分路径、线材与已验证设备，用户只能通过绕行或退货自行完成边界确认。")], theme_rows(["PT-07"], index)),
            ],
        ),
        section(
            "unmet-and-decisions",
            "未满足需求与决策后果",
            [],
            [
                subsection("需要更清楚的承诺边界", [paragraph("用户需要在购买前知道歌曲从哪里来、是否需要订阅、续航在什么条件下成立、电视与音响如何连接，以及包装中实际包含什么。")], theme_rows(["PT-01", "PT-06", "PT-07", "PT-13"], index)),
                subsection("需要更可靠的完整使用链", [paragraph("未满足需求集中在首次成功、长时稳定、异常恢复和跨设备连接。内容说明可以减少预期落差，但不能代替对供电、同步、系统和整机问题的产品验证。")], theme_rows(["PT-02", "PT-04", "PT-08", "PT-14"], index)),
                subsection("决策后果不是只有退货", [paragraph("评论中的后果还包括推荐、继续使用、降低评分、改用外部设备、另购配件和不推荐。证据工作台保留完整 Review 编码，便于区分问题严重度与用户最终选择。")], theme_rows(["UT-09", "UT-10"], index)),
            ],
        ),
        section(
            "actions-source",
            "从看到的现象推导应该做什么",
            [paragraph("动作按三条路径展开：先修正 Listing 的事实与承诺边界，再用副图和 A+ 讲清消费者任务链，同时把不能由内容解决的问题送入产品验证。")],
            [subsection("行动原则", [bullet_list(["页面动作必须说明当前状况、VOC 事实和上线门槛。", "图片与 A+ 先讲谁在用、在哪里用、如何开始，再讲规格。", "产品动作必须给出最小验证方案，不能用文案掩盖故障。", "每项动作保留完整名称，并可下钻到精确反馈点。"]),], theme_rows(["UT-01", "UT-05", "UT-09"], index))],
        ),
        section(
            "methodology-source",
            "证据边界",
            [],
            [subsection("如何阅读这些数量", [paragraph("主题 Review 数只表示 559 条评论中被编码到该主题的证据覆盖，不代表订单占比、市场人群占比或故障率。用户主题允许重叠，产品反馈点主题互斥。")], []), subsection("unknown 如何处理", [paragraph("`unknown` 只表示相应字段没有证据，不使整条 Review 失效；消费者未知的评论仍可证明充电、联网、声音或退货结果。")], [])],
        ),
    ]
    return {"intro": [], "sections": sections}


def bridge_evidence_by_state(rows: list[int], evidence_by_row: dict[int, dict]) -> dict:
    field_by_state = {
        "actual": "实际场景",
        "planned": "计划场景",
        "estimated": "用户估计",
        "reported": "转述证据",
    }
    return {
        state: [
            row
            for row in rows
            if pilot.is_known(evidence_by_row[row]["scenes"][field])
        ]
        for state, field in field_by_state.items()
    }


def build_bridges(index: dict[str, dict], evidence_by_row: dict[int, dict]) -> list[dict]:
    definitions = [
        ("F-01", "消费者购买的是共同参与，不是双麦规格本身", "家庭、伴侣和朋友需要的是让更多人容易加入并持续获得乐趣。", "页面若只展示两支麦克风，会遗漏家庭共同参与这一购买理由。", ["UT-01"], ["V-01", "V-05"]),
        ("F-02", "第一次使用是否成功取决于完整启动链路", "配件、充电、开机、联网、账号、内容入口和取麦任何一环都能阻断开唱。", "首次失败会直接损伤礼物体验、价格合理性和退货风险。", ["UT-06"], ["L-04", "V-02"]),
        ("F-03", "歌曲可得性包含账号、订阅和持续成本", "应用入口存在，不等于歌曲免费、完整或持续可用。", "购买前预期不准确，会让内容问题上升为整机价值和信任问题。", ["UT-05"], ["L-01", "V-03", "P-02"]),
        ("F-04", "活动价值要求设备在整个时段持续可靠", "供电、网络、内容、声音、麦克风和显示链路需要共同成立。", "可靠性失败不是单项扣分，而会让活动任务整体归零。", ["UT-02", "UT-09"], ["L-02", "P-01", "P-03"]),
        ("F-05", "外接屏幕和影音设备属于部分用户的真实工作流", "HDMI、电视、投影和外接音响的画面、歌词与声音路径并不等价。", "连接边界不清会带来高价落差、绕行和退货。", ["PT-07"], ["L-03", "V-04", "P-04"]),
        ("F-06", "声音与便携是应被保护的已验证优势", "这些优势跨家庭、派对和户外场景帮助共同参与与活动成立。", "优化内容、连接和可靠性时，不应牺牲声音、双麦便利或移动性。", ["PT-10", "PT-11"], ["P-05"]),
    ]
    bridges = []
    for bridge_id, finding, meaning, impact, theme_ids, action_ids in definitions:
        rows = rows_for(theme_ids, index)
        bridges.append(
            {
                "id": bridge_id,
                "finding": finding,
                "meaning": meaning,
                "evidence_by_state": bridge_evidence_by_state(rows, evidence_by_row),
                "business_impact": impact,
                "action_ids": action_ids,
                "review_rows": rows,
                "representative_review_rows": representative_rows(rows, evidence_by_row),
            }
        )
    return bridges


def theme_metric(theme_id: str, item: dict) -> str:
    if theme_id.startswith("UT-"):
        return f"{theme_id} {item['主题名称']}涉及 {item['涉及Review数']} 条 Review。"
    if theme_id.startswith("OC-"):
        return f"{theme_id} {item['机会链名称']}连接 {item['涉及Review数']} 条 Review。"
    polarity = item["反馈点极性分布"]
    return f"{theme_id} {item['主题名称']}涉及 {item['涉及Review数']} 条 Review、{item['反馈点数']} 个反馈点，其中负向 {polarity.get('负向', 0)}、正负混合 {polarity.get('正负混合', 0)}。"


def clean_trial_language(value):
    if isinstance(value, str):
        return value.replace("当前试点中", "全量评论中").replace("样本同时出现", "全量评论同时出现").replace("样本中", "评论中")
    if isinstance(value, list):
        return [clean_trial_language(item) for item in value]
    if isinstance(value, dict):
        return {key: clean_trial_language(item) for key, item in value.items()}
    return value


def build_actions(
    bridges: list[dict], index: dict[str, dict], evidence_by_row: dict[int, dict]
) -> list[dict]:
    pilot.ACTION_PATH = ACTION_PATH
    actions = pilot.parse_actions()
    pilot.enrich_actions(actions, bridges)
    for action in actions:
        theme_ids = ACTION_THEME_IDS[action["id"]]
        context = clean_trial_language({
            key: action[key]
            for key in ["current_state", "voc_facts", "unknowns", "business_impact", "acceptance_criteria"]
        })
        action.update(context)
        action.pop("theme_evidence_refs", None)
        action["voc_facts"] = [theme_metric(theme_id, index[theme_id]) for theme_id in theme_ids] + action["voc_facts"]
        action["source_review_rows"] = rows_for(theme_ids, index)
        action["evidence_basis_theme_ids"] = [
            theme_id for theme_id in theme_ids if theme_id.startswith(("PT-", "OC-"))
        ]
        action["evidence_refs"] = build_action_evidence(
            action, theme_ids, index, evidence_by_row
        )
        action["representative_evidence_refs"] = representative_evidence_refs(
            action["evidence_refs"], evidence_by_row
        )
        action["source_finding_ids"] = [bridge["id"] for bridge in bridges if action["id"] in bridge["action_ids"]]
    return actions


def build_data() -> dict:
    themes = json.loads(THEME_PATH.read_text(encoding="utf-8"))
    index = theme_index(themes)
    evidence_reviews = build_evidence_reviews()
    evidence_by_row = {review["data_row"]: review for review in evidence_reviews}
    coverage = pilot.build_coverage(evidence_reviews)
    coverage_by_field = {item["field"]: item["known"] for item in coverage}
    mixed = sum(pilot.is_known(review["satisfiers"]) and pilot.is_known(review["unmet_needs"]) for review in evidence_reviews)
    scene_states = {
        "actual": sum(pilot.is_known(review["scenes"]["实际场景"]) for review in evidence_reviews),
        "planned": sum(pilot.is_known(review["scenes"]["计划场景"]) for review in evidence_reviews),
        "estimated": sum(pilot.is_known(review["scenes"]["用户估计"]) for review in evidence_reviews),
        "reported": sum(pilot.is_known(review["scenes"]["转述证据"]) for review in evidence_reviews),
    }
    bridges = build_bridges(index, evidence_by_row)
    actions = build_actions(bridges, index, evidence_by_row)
    taxonomy = pilot.build_taxonomy()
    pilot.enrich_evidence_reviews(evidence_reviews, actions, bridges, taxonomy)
    return {
        "contract": {
            "schema_version": "1.1-full-decision-evidence-workbench",
            "artifact_role": "559 条 VOC 叙事、业务动作与证据下钻的正式数据契约",
            "source_roles": {
                "04": "评论原文与译文事实源",
                "08": "Review 层与反馈点编码事实源",
                "12": "用户主题、产品体验主题与机会链事实源",
                "13": "业务动作事实源",
                "14-16": "经用户确认的内容结构、数据契约与界面交互校准源",
            },
            "display_rules": [
                "主阅读路径先回答消费者、场景、任务、期待、实际结果、价值与缺口，再进入动作。",
                "十二个 Review 层字段共同支持一条体验叙事，不拆成十二张数据目录。",
                "实际场景、计划场景、用户估计和转述证据在下钻时保持分开。",
                "unknown 只表示该字段无证据，不使整条 Review 失效。",
                "主题数量表示评论证据覆盖，不解释为市场占比或故障率。",
                "动作证据精确到数据行与 unit_id，并标明其在决策中的角色。",
                "动作的完整精确证据取自 12 中关联产品主题的 unit_id 与关联机会链的关联unit_id；最多 8 条代表证据只用于首屏展示。",
            ],
            "required_sections": ["narrative", "finding_to_action", "actions", "evidence_reviews", "methodology"],
        },
        "report": {
            "asin": "B0CR1R7FKP",
            "title": "Ikarao X2 评论洞察",
            "subtitle": "谁在使用、如何使用、想完成什么，以及体验如何导向业务行动",
            "scope_label": "559 条唯一评论的全量编码与主题分析；主题数量表示证据覆盖，不代表市场占比",
            "generated_on": "2026-07-19",
        },
        "summary": {
            "thesis": "消费者购买的并不只是一台可以唱歌的音响，而是一套降低准备负担、组织多人参与并维持整场娱乐活动的一体式工具。",
            "task_chain": ["准备设备", "找到歌曲", "邀请他人参与", "持续演唱", "活动不中断"],
            "mixed_experience_count": mixed,
            "metrics": [
                {"label": "消费者有明确证据", "value": coverage_by_field["消费者"], "denominator": 559},
                {"label": "实际场景有明确证据", "value": scene_states["actual"], "denominator": 559},
                {"label": "购买动机有明确证据", "value": coverage_by_field["购买动机"], "denominator": 559},
                {"label": "决策结果有明确证据", "value": coverage_by_field["决策结果"], "denominator": 559},
            ],
        },
        "narrative": build_narrative(index, evidence_by_row, mixed),
        "finding_to_action": bridges,
        "actions": actions,
        "evidence_reviews": evidence_reviews,
        "taxonomy": {"labels": taxonomy["labels"]},
        "methodology": {
            "sample": "559 条合并去重后的唯一评论均已进入 Review 层与反馈点编码。",
            "quantification_rule": "主题 Review 数只说明全量评论中的证据覆盖；用户主题允许重叠，产品反馈点主题互斥，均不可直接解释为订单占比、市场占比或故障率。",
            "scene_states": scene_states,
            "field_coverage": coverage,
            "boundaries": [
                "评论不能可靠推断年龄、收入、职业、销量占比或技术根因。",
                "消费者未知的 Review 仍可证明充电、联网、声音或退货结果。",
                "购买动机未知时不能从星级、实际结果或决策结果倒推原因。",
                "同一 Review 可以同时满意和不满，也可以属于多个情境与任务主题。",
                "产品问题的发生率与技术根因需要订单、退货、售后和质量数据另行验证。",
            ],
        },
    }


def validate_data(data: dict) -> None:
    reviews = data["evidence_reviews"]
    if len(reviews) != FULL_REVIEW_COUNT or len({review["data_row"] for review in reviews}) != FULL_REVIEW_COUNT:
        raise ValueError("The full evidence library must contain 559 unique reviews")
    feedback_count = sum(len(review["units"]) for review in reviews)
    themes = json.loads(THEME_PATH.read_text(encoding="utf-8"))
    index = theme_index(themes)
    theme_feedback_count = sum(item["反馈点数"] for item in themes["产品体验主题"])
    if feedback_count != theme_feedback_count:
        raise ValueError(
            f"Evidence and product-theme feedback counts disagree: {feedback_count} != {theme_feedback_count}"
        )
    for field in ["购买动机", "期望结果"]:
        actual_counts = Counter(review["inferences"][field]["处理结果"] for review in reviews)
        if sum(actual_counts.values()) != FULL_REVIEW_COUNT or not set(actual_counts) <= {
            "已有直接证据", "可谨慎推测", "证据不足"
        }:
            raise ValueError(f"Invalid persisted inference counts for {field}: {dict(actual_counts)}")
        for review in reviews:
            inference = review["inferences"][field]
            strict_value = review["motivations"] if field == "购买动机" else review["expectations"]
            status = inference["处理结果"]
            if (status == "已有直接证据") != (strict_value != ["unknown"]):
                raise ValueError(f"Strict evidence and inference status disagree: row {review['data_row']} / {field}")
            if status == "可谨慎推测" and (
                inference["可能推测"] == ["unknown"] or inference["依据"] == ["unknown"]
            ):
                raise ValueError(f"Cautious inference is missing its basis: row {review['data_row']} / {field}")
    if [item["id"] for item in data["narrative"]["sections"]] != SECTION_IDS:
        raise ValueError("Narrative sections drifted from the approved report structure")
    narrative_counts = [
        len(subsection["review_rows"])
        for section in data["narrative"]["sections"]
        for subsection in section["subsections"]
        if subsection["review_rows"]
    ]
    if len(set(narrative_counts)) == 1 or max(narrative_counts) <= 8:
        raise ValueError("Narrative evidence is still capped at the pilot display limit")
    valid_rows = {review["data_row"] for review in reviews}
    for section in data["narrative"]["sections"]:
        for subsection in section["subsections"]:
            rows = subsection["review_rows"]
            if rows != sorted(set(rows)) or not set(rows) <= valid_rows:
                raise ValueError(f"Invalid narrative evidence rows: {section['id']} / {subsection['title']}")
            expected_coverage = {
                "matched_reviews": len(rows),
                "total_reviews": len(reviews),
                "percentage": round(len(rows) / len(reviews) * 100),
            }
            if subsection.get("coverage") != expected_coverage:
                raise ValueError(f"Invalid narrative coverage: {section['id']} / {subsection['title']}")
    audience = next(section for section in data["narrative"]["sections"] if section["id"] == "audience")
    family_starter = next(item for item in audience["subsections"] if item["title"] == "家庭娱乐的发起者")
    if family_starter["review_rows"] != rows_for(["UT-01"], index):
        raise ValueError("The family-starter narrative no longer matches the complete UT-01 review set")
    if len(data["finding_to_action"]) != 6 or len(data["actions"]) != 14:
        raise ValueError("The report must contain 6 finding bridges and 14 business actions")
    for bridge in data["finding_to_action"]:
        bridge_rows = set(bridge["review_rows"])
        for state, rows in bridge["evidence_by_state"].items():
            if rows != sorted(set(rows)) or not set(rows) <= bridge_rows:
                raise ValueError(f"Invalid finding evidence state: {bridge['id']} / {state}")
    action_ids = {action["id"] for action in data["actions"]}
    linked_ids = {action_id for bridge in data["finding_to_action"] for action_id in bridge["action_ids"]}
    if action_ids != linked_ids:
        raise ValueError("Every business action must link to at least one finding")
    units_by_row = {review["data_row"]: {unit["unit_id"] for unit in review["units"]} for review in reviews}
    unit_to_row = {
        unit["unit_id"]: review["data_row"]
        for review in reviews
        for unit in review["units"]
    }
    evidence_counts = []
    action_evidence_rows = set()
    for action in data["actions"]:
        if not action["source_review_rows"] or not action["evidence_refs"]:
            raise ValueError(f"{action['id']} is missing full theme rows or exact evidence")
        expected_unit_ids = exact_unit_ids(ACTION_THEME_IDS[action["id"]], index)
        actual_unit_ids = {reference["unit_id"] for reference in action["evidence_refs"]}
        if len(actual_unit_ids) != len(action["evidence_refs"]):
            raise ValueError(f"{action['id']} contains duplicate exact evidence")
        if actual_unit_ids != expected_unit_ids:
            missing = sorted(expected_unit_ids - actual_unit_ids)[:5]
            extra = sorted(actual_unit_ids - expected_unit_ids)[:5]
            raise ValueError(
                f"{action['id']} exact evidence is incomplete; missing={missing}, extra={extra}"
            )
        evidence_counts.append(len(actual_unit_ids))
        action_evidence_rows.update(reference["review_row"] for reference in action["evidence_refs"])
        for reference in action["evidence_refs"]:
            if reference["unit_id"] not in units_by_row.get(reference["review_row"], set()):
                raise ValueError(f"Invalid exact evidence reference: {reference}")
            expected_sources = [
                theme_id
                for theme_id in action["evidence_basis_theme_ids"]
                if reference["unit_id"] in exact_unit_ids([theme_id], index)
            ]
            if reference["source_theme_ids"] != expected_sources:
                raise ValueError(f"Invalid theme provenance: {reference}")
            if unit_to_row[reference["unit_id"]] != reference["review_row"]:
                raise ValueError(f"Invalid review provenance: {reference}")
        representative_ids = {
            reference["unit_id"] for reference in action["representative_evidence_refs"]
        }
        if len(representative_ids) > 8 or not representative_ids <= actual_unit_ids:
            raise ValueError(f"{action['id']} has invalid representative evidence")
    if len(set(evidence_counts)) == 1:
        raise ValueError("All actions have the same exact evidence count; likely a display cap leak")
    pilot_rows = {
        item["来源定位"]["数据行"] for item in pilot.load_jsonl(PILOT_CODING_PATH)
    }
    if not action_evidence_rows - pilot_rows:
        raise ValueError("Action evidence is still confined to the 40-review pilot")
    serialized = json.dumps(data, ensure_ascii=False)
    if re.search(r"(?<!\d)40 条", serialized) or "试点" in serialized:
        raise ValueError("Pilot language leaked into the full report data")


def render_html(data: dict, digest: str) -> str:
    template = pilot.HTML_TEMPLATE
    replacements = {
        "全部试点证据": "全部评论证据",
        "VOC 洞察结构试点": "VOC 洞察报告",
        "先读结论，再按需下钻证据。试点计数不是市场比例。": "先读结论，再按需下钻证据。主题计数不是市场比例。",
        "这 40 条评论整体在说什么": "这 559 条评论整体在说什么",
        "当前试点中，以下 Review": "全量评论中，以下 Review",
        "样本口径、字段覆盖": "数据口径、字段覆盖",
        "样本口径：": "数据口径：",
        "当前 40 条分层试点中的证据覆盖": "当前 559 条全量编码中的证据覆盖",
        "这里只列出当前 40 条试点中的关联 Review": "这里只列出当前 559 条全量评论中的代表性关联 Review",
        "没有属于当前试点的关联 Review": "没有属于当前主题的关联 Review",
        "`${data.summary.mixed_experience_count}/40 条评论": "`${data.summary.mixed_experience_count}/${data.evidence_reviews.length} 条评论",
        "查看 ${action.source_review_rows.length} 条动作证据（精确到反馈点）": "查看 ${new Set(action.evidence_refs.map((ref) => ref.review_row)).size} 条动作证据（${action.evidence_refs.length} 个精确反馈点）",
    }
    for source, target in replacements.items():
        template = template.replace(source, target)
    template = template.replace(
        "      const refs = action.evidence_refs.map((ref) =>",
        "      const representativeRefs = action.representative_evidence_refs || action.evidence_refs;\n      const refs = representativeRefs.map((ref) =>",
    )
    template = template.replace(
        "<b>动作级精确证据</b><div>${refs}</div>",
        "<b>动作级精确证据</b><p>完整关联 ${action.evidence_refs.length} 个反馈点；以下展示 ${representativeRefs.length} 个代表反馈点。</p><div>${refs}</div>",
    )
    template = template.replace(
        """    function openReviewListModal(rows, title = '关联评论证据') {
      modalContext = {kind:'reviews', rows:rows.map(Number), title};
      renderReviewListModal();
    }

    function renderReviewListModal() {
      const reviews = modalContext.rows.map((row) => reviewMap.get(row)).filter(Boolean);
      showModal(`<h2 id="drawerTitle">${escapeHtml(modalContext.title)}</h2><p class="modal-lead">这里只列出当前 559 条全量评论中的代表性关联 Review；计数不代表市场发生率。</p>${reviews.length ? reviews.map((review) => `<article class="drawer-review"><strong>${review.stars} 星 · 数据行 ${review.data_row} · ${escapeHtml(review.title_zh || review.title_en)}</strong><p>${escapeHtml(review.review_zh || review.review_en || '原文为空')}</p><button class="evidence-link" data-open-review-detail="${review.data_row}">查看完整编码</button></article>`).join('') : '<div class="empty">没有属于当前主题的关联 Review。</div>'}`);
    }
""",
        """    function modalPager(page, totalPages) {
      if (totalPages <= 1) return '';
      return `<div class="pagination"><button data-modal-page="${page - 1}" ${page === 1 ? 'disabled' : ''}>上一页</button><span>第 ${page} / ${totalPages} 页</span><button data-modal-page="${page + 1}" ${page === totalPages ? 'disabled' : ''}>下一页</button></div>`;
    }

    function openReviewListModal(rows, title = '关联评论证据') {
      modalContext = {kind:'reviews', rows:rows.map(Number), title, page:1};
      renderReviewListModal();
    }

    function renderReviewListModal() {
      const reviews = modalContext.rows.map((row) => reviewMap.get(row)).filter(Boolean);
      const pageSize = 8;
      const totalPages = Math.max(1, Math.ceil(reviews.length / pageSize));
      modalContext.page = Math.min(Math.max(modalContext.page || 1, 1), totalPages);
      const start = (modalContext.page - 1) * pageSize;
      const visible = reviews.slice(start, start + pageSize);
      showModal(`<h2 id="drawerTitle">${escapeHtml(modalContext.title)}</h2><p class="modal-lead">共 ${reviews.length} 条关联 Review，当前显示 ${visible.length} 条；计数表示证据覆盖，不代表市场发生率。</p>${visible.length ? visible.map((review) => `<article class="drawer-review"><strong>${review.stars} 星 · 数据行 ${review.data_row} · ${escapeHtml(review.title_zh || review.title_en)}</strong><p>${escapeHtml(review.review_zh || review.review_en || '原文为空')}</p><button class="evidence-link" data-open-review-detail="${review.data_row}">查看完整编码</button></article>`).join('') : '<div class="empty">没有属于当前主题的关联 Review。</div>'}${modalPager(modalContext.page, totalPages)}`);
    }
""",
    )
    template = template.replace(
        """    function openActionEvidence(actionId) {
      modalContext = {kind:'action', actionId};
      renderActionEvidenceModal();
    }
""",
        """    function openActionEvidence(actionId) {
      modalContext = {kind:'action', actionId, page:1};
      renderActionEvidenceModal();
    }
""",
    )
    template = template.replace(
        """    function renderActionEvidenceModal() {
      const action = actionMap.get(modalContext.actionId);
      const refsByReview = new Map();
      action.evidence_refs.forEach((ref) => {
        if (!refsByReview.has(ref.review_row)) refsByReview.set(ref.review_row, []);
        refsByReview.get(ref.review_row).push(ref);
      });
      const reviews = [...refsByReview.entries()].map(([row, refs]) => ({review:reviewMap.get(row), refs})).filter((item) => item.review);
      showModal(`<h2 id="drawerTitle">${action.id} · ${escapeHtml(action.title)}</h2><p class="modal-lead">${reviews.length} 条 Review · ${action.evidence_refs.length} 个精确反馈点</p><div class="modal-action-state"><b>当前状况</b><p>${escapeHtml(action.current_state)}</p></div><div class="modal-unit-list">${reviews.map(({review, refs}) => `<article class="drawer-review"><strong>${review.stars} 星 · 数据行 ${review.data_row} · ${escapeHtml(review.title_zh || review.title_en)}</strong><p>${escapeHtml(review.review_zh || review.review_en || '原文为空')}</p>${refs.map((ref) => { const unit = review.units.find((item) => item.unit_id === ref.unit_id); return unit ? modalUnit(review, unit, ref) : ''; }).join('')}<button class="evidence-link" data-open-review-detail="${review.data_row}">查看该 Review 完整编码</button></article>`).join('')}</div>`);
    }
""",
        """    function renderActionEvidenceModal() {
      const action = actionMap.get(modalContext.actionId);
      const refsByReview = new Map();
      action.evidence_refs.forEach((ref) => {
        if (!refsByReview.has(ref.review_row)) refsByReview.set(ref.review_row, []);
        refsByReview.get(ref.review_row).push(ref);
      });
      const reviews = [...refsByReview.entries()].sort((left, right) => left[0] - right[0]).map(([row, refs]) => ({review:reviewMap.get(row), refs})).filter((item) => item.review);
      const pageSize = 8;
      const totalPages = Math.max(1, Math.ceil(reviews.length / pageSize));
      modalContext.page = Math.min(Math.max(modalContext.page || 1, 1), totalPages);
      const start = (modalContext.page - 1) * pageSize;
      const visible = reviews.slice(start, start + pageSize);
      showModal(`<h2 id="drawerTitle">${action.id} · ${escapeHtml(action.title)}</h2><p class="modal-lead">完整关联 ${reviews.length} 条 Review · ${action.evidence_refs.length} 个精确反馈点；当前显示 ${visible.length} 条 Review</p><div class="modal-action-state"><b>当前状况</b><p>${escapeHtml(action.current_state)}</p></div><div class="modal-unit-list">${visible.map(({review, refs}) => `<article class="drawer-review"><strong>${review.stars} 星 · 数据行 ${review.data_row} · ${escapeHtml(review.title_zh || review.title_en)}</strong><p>${escapeHtml(review.review_zh || review.review_en || '原文为空')}</p>${refs.map((ref) => { const unit = review.units.find((item) => item.unit_id === ref.unit_id); return unit ? modalUnit(review, unit, ref) : ''; }).join('')}<button class="evidence-link" data-open-review-detail="${review.data_row}">查看该 Review 完整编码</button></article>`).join('')}</div>${modalPager(modalContext.page, totalPages)}`);
    }
""",
    )
    template = template.replace(
        """        const pageButton = event.target.closest('[data-evidence-page]');
        if (pageButton && !pageButton.disabled) {
""",
        """        const modalPageButton = event.target.closest('[data-modal-page]');
        if (modalPageButton && !modalPageButton.disabled && modalContext) {
          modalContext.page = Number(modalPageButton.dataset.modalPage);
          returnToModalContext();
        }
        const pageButton = event.target.closest('[data-evidence-page]');
        if (pageButton && !pageButton.disabled) {
""",
    )
    template = template.replace("<title>__TITLE__</title>", "<title>Ikarao X2 评论洞察</title><link rel=\"icon\" href=\"data:,\">")
    if "40 条" in template or "试点" in template:
        raise ValueError("Pilot language leaked into the full report template")
    for required_fragment in [
        "function modalPager",
        "data-modal-page",
        "representative_evidence_refs",
        "完整关联 ${reviews.length} 条 Review",
        "function renderValueChains",
        "renderValueChains(review.value_chains)",
        "data-evidence-dimension",
        "filteredInvestigationUnits",
        "aria-pressed=\"${evidenceDimension === dimension}\"",
        "function persistedInference",
        "谨慎推测 · 非事实",
        "该推测不参与证据计数或主题统计",
        "scene-field-group",
        "评论证据覆盖",
        "subsection.coverage",
        "中文标题",
        "中文正文",
        "英文标题",
        "英文正文",
    ]:
        if required_fragment not in template:
            raise ValueError(f"Full-report interaction patch is missing: {required_fragment}")
    if "function fieldInference" in template:
        raise ValueError("Runtime inference must not remain in the full report")
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return template.replace("__DATA__", payload).replace("__DIGEST__", digest)


def main() -> None:
    data = build_data()
    validate_data(data)
    pretty = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    digest = hashlib.sha256(pretty.encode("utf-8")).hexdigest()
    DATA_PATH.write_text(pretty, encoding="utf-8")
    HTML_PATH.write_text(render_html(data, digest), encoding="utf-8")
    print(json.dumps({"reviews": len(data["evidence_reviews"]), "units": sum(len(item["units"]) for item in data["evidence_reviews"]), "actions": len(data["actions"]), "json_sha256": digest, "json": str(DATA_PATH), "html": str(HTML_PATH)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
