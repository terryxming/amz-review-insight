from __future__ import annotations

import hashlib
import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_DIR = ROOT / "data-pilot" / "B0CR1R7FKP" / "analysis" / "2026-07-18"
REPORT_DIR = ROOT / "data-pilot" / "B0CR1R7FKP" / "reports" / "2026-07-18"
SOURCE_DIR = ROOT / "data-pilot" / "B0CR1R7FKP" / "source-exports" / "2026-07-18"
PILOT_PATH = ANALYSIS_DIR / "06_stratified-pilot-coding.jsonl"
CODING_PATH = ANALYSIS_DIR / "08_full-review-coding.jsonl"
THEME_PATH = ANALYSIS_DIR / "12_full-theme-analysis.json"
ACTION_PATH = ANALYSIS_DIR / "13_business-recommendations.md"
OVERVIEW_PATH = REPORT_DIR / "14_overview-pilot.md"
DATA_PATH = REPORT_DIR / "15_overview-report-pilot.json"
HTML_PATH = REPORT_DIR / "16_overview-report-pilot.html"
REVIEWS_PATH = SOURCE_DIR / "04_merged-reviews.jsonl"

REVIEW_FIELDS = [
    "消费者",
    "使用场景",
    "用户任务",
    "购买动机",
    "期望结果",
    "实际结果",
    "满意点",
    "价值链",
    "未满足的需求",
    "证据强度",
    "总体极性",
    "决策结果",
]

SECTION_IDS = {
    "核心结论": "core",
    "消费者与需求背景": "audience",
    "使用场景与用户任务": "contexts",
    "为什么购买": "motivation",
    "购买前期待什么，实际得到什么": "expectations",
    "价值在哪里形成": "value-formation",
    "价值在哪里中断": "value-interruption",
    "未满足需求与决策后果": "unmet-and-decisions",
    "从看到的现象推导应该做什么": "actions-source",
    "证据边界": "methodology-source",
}

SUBSECTION_EVIDENCE = {
    ("contexts", "家庭日常娱乐"): [183, 226, 234, 457, 485, 526],
    ("contexts", "生日、送礼和首次使用"): [167, 169, 277, 457, 526],
    ("contexts", "聚会、办公室和户外活动"): [20, 116, 187, 206, 207, 226, 350, 542],
    ("contexts", "个人练习与家庭影音整合"): [109, 157, 304, 359, 445, 470, 548],
    ("contexts", "用户任务不是功能清单"): [109, 167, 183, 187, 206, 207, 226, 234, 359, 457, 526],
}

ACTION_TITLES = {
    "L-01": "把无限歌曲改为可验证的内容入口说明",
    "L-02": "把续航条件和充电要求放在同一主张中",
    "L-03": "增加电视与外接设备的能力边界",
    "L-04": "把一体化、容易开始改写为具体步骤",
    "V-01": "先回答谁在用、在什么场景使用",
    "V-02": "展示从开箱到开唱的完整路径",
    "V-03": "讲清歌曲从哪里来、成本在哪里",
    "V-04": "讲清便携和连接边界",
    "V-05": "把声音优势转成演唱结果",
    "P-01": "验证供电、充电和地区包装",
    "P-02": "验证平板、应用、歌词和网络的完整唱歌时段",
    "P-03": "验证麦克风返声延迟和自动同步",
    "P-04": "验证 HDMI 与外接音响能力",
    "P-05": "保持声音与便携优势",
}

ACTION_CONTEXTS = {
    "L-01": {
        "current_state": "当前页面把 YouTube、KaraFun、Spotify 与大量歌曲放在同一卖点中，但第三方账号、订阅、地区、网络和曲库边界不够显著。",
        "voc_facts": [
            "样本同时出现“联网后基本能找到歌曲”的正向体验，以及 Spotify 不可用、免费歌曲少、订阅权益与描述不一致等负向体验。",
            "内容入口存在不等于歌曲免费、完整或持续可用；软件更新后可用权益也可能发生变化。",
        ],
        "unknowns": ["当前美国站固件中的实际应用清单", "各服务在美国站的免费、付费和地区边界"],
        "business_impact": "内容预期落差会把第三方服务问题转化为整机信任、价格价值和退货问题。",
        "acceptance_criteria": ["页面逐项说明内容入口、账号、订阅、网络和地区条件", "所有权益与当前美国站实机流程一致", "不再使用无法验证的无限或全免费承诺"],
        "evidence_refs": [(187, "R187-U02", "正向边界"), (209, "R209-U01", "购买前预期"), (209, "R209-U02", "主张冲突"), (209, "R209-U03", "额外成本"), (222, "R222-U08", "权益落差"), (292, "R292-U01", "免费内容缺口"), (350, "R350-U06", "权益缺失"), (528, "R528-U03", "更新后成本")],
    },
    "L-02": {
        "current_state": "五点描述强调 8 小时续航，FAQ 才补充音量与充电条件；充电器、线材和美国站包装条件没有在同一主张中说明。",
        "voc_facts": ["样本中既有续航长的正向反馈，也有充电慢、只能使用几小时和包装缺少合适适配器的反馈。", "评论能证明问题出现过，但不能据此估算总体故障率。"],
        "unknowns": ["8 小时续航的完整测试条件", "当前美国站 BOM 与包装一致性", "问题是否集中于特定批次或充电配件"],
        "business_impact": "续航和充电主张不完整会影响派对任务、首次使用和高客单价产品的可信度。",
        "acceptance_criteria": ["续航数字与音量、屏幕、灯光、联网状态及测试方法同屏呈现", "页面、说明书、BOM 和实物包装一致", "量产机可在声明条件下复现结果"],
        "evidence_refs": [(20, "R020-U01", "问题证据"), (20, "R020-U02", "问题证据"), (161, "R161-U02", "正向边界"), (169, "R169-U01", "包装问题"), (169, "R169-U04", "任务阻断"), (169, "R169-U06", "包装问题"), (194, "R194-U04", "正向边界"), (445, "R445-U03", "正向边界")],
    },
    "L-03": {
        "current_state": "页面广泛列出 HDMI、TV、投影和外接音响能力，但没有清楚区分画面、歌词、音频路径及随附线材。",
        "voc_facts": ["样本中有投影、电视显示歌词的成功路径，也有 HDMI 只出画面、不出音频以及无法连接条形音箱的失败路径。", "不同外接设备的成功经验不能自动外推到所有组合。"],
        "unknowns": ["当前固件支持的音视频输出矩阵", "常见电视、投影、soundbar 与转换器的兼容范围"],
        "business_impact": "连接边界不清会造成高价预期落差、额外试错和退货。",
        "acceptance_criteria": ["页面分别说明画面、歌词和音频去向", "列清随附与需自备的线材", "所有展示组合均通过美国站量产机实测"],
        "evidence_refs": [(157, "R157-U05", "正向路径"), (206, "R206-U01", "正向路径"), (206, "R206-U02", "正向路径"), (359, "R359-U05", "正向路径"), (470, "R470-U02", "兼容失败"), (548, "R548-U05", "能力边界")],
    },
    "L-04": {
        "current_state": "页面使用 no setup hassle、ultra-sensitive 等绝对化表达，但首次充电、联网、账号、应用入口和异常恢复仍可能需要用户判断。",
        "voc_facts": ["样本中有快速开机、联网和容易设置的正向证据。", "也有缺少说明、应用入口难找、必须重置或重启才能恢复等问题。"],
        "unknowns": ["新用户完成首次开唱的真实步骤与耗时", "异常恢复入口在当前固件中的可发现性"],
        "business_impact": "绝对化易用承诺与首次体验不一致，会放大礼物失败、价格不值和退货风险。",
        "acceptance_criteria": ["页面用真实步骤替代绝对化词语", "首次开唱路径经新用户可用性测试", "异常恢复入口和说明可被用户找到"],
        "evidence_refs": [(109, "R109-U01", "正向路径"), (109, "R109-U02", "正向路径"), (167, "R167-U01", "说明缺口"), (205, "R205-U02", "说明缺口"), (225, "R225-U02", "操作障碍"), (330, "R330-U02", "恢复成本"), (350, "R350-U11", "说明缺口"), (359, "R359-U14", "正向路径")],
    },
    "V-01": {
        "current_state": "当前功能表达容易把双麦、便携和大音量拆开呈现，未充分说明它们如何支持家庭、朋友和活动参与。",
        "voc_facts": ["家庭共同娱乐、朋友聚会、户外活动和礼物场景在样本中均有实际使用证据。", "双麦的业务价值是让两个人更容易同时参与，而不只是包装内多一支麦克风。"],
        "unknowns": ["不同场景在 559 条总体中的相对规模", "主图和 A+ 当前素材对真实关系与场景的覆盖程度"],
        "business_impact": "只讲规格会削弱购买者对家庭关系、聚会组织和共同娱乐价值的理解。",
        "acceptance_criteria": ["副图或 A+ 首屏明确出现人物关系、场景和用户任务", "双麦与共同参与结果同屏表达", "素材不暗示评论无法证明的人群属性"],
        "evidence_refs": [(183, "R183-U01", "家庭价值"), (183, "R183-U02", "双麦价值"), (187, "R187-U04", "户外活动"), (226, "R226-U01", "朋友聚会"), (485, "R485-U04", "共同娱乐"), (526, "R526-U04", "家庭任务失败")],
    },
    "V-02": {
        "current_state": "页面强调一体化和容易开始，但没有把配件、充电、开机、联网、内容入口和取麦连成一条完整首次使用路径。",
        "voc_facts": ["样本中存在开机选应用即可开始、麦克风自动连接的顺畅路径。", "也存在适配器缺失、应用入口难找、麦克风需恢复或充电后仍无法启动的阻断。"],
        "unknowns": ["美国站当前包装与首次启动界面", "各异常在当前固件中的恢复步骤"],
        "business_impact": "任何一环失败都可能让礼物或聚会在首次使用时直接中断。",
        "acceptance_criteria": ["流程图与美国站量产包装和当前固件一致", "账号、订阅和异常恢复入口在同一区域可见", "新用户可按图完成首次开唱"],
        "evidence_refs": [(109, "R109-U02", "正向路径"), (169, "R169-U01", "配件阻断"), (169, "R169-U04", "任务阻断"), (225, "R225-U02", "操作障碍"), (330, "R330-U02", "恢复成本"), (359, "R359-U14", "正向路径"), (457, "R457-U03", "正向路径"), (486, "R486-U02", "麦克风阻断")],
    },
    "V-03": {
        "current_state": "页面把多个内容服务并列展示，但用户难以一眼区分内置入口、第三方账号、订阅、网络依赖和离线能力。",
        "voc_facts": ["用户可通过 YouTube、KaraFun 等路径找到歌曲，但免费范围、完整歌曲和持续成本存在差异。", "部分用户把第三方权益理解成硬件自带内容，产生明显落差。"],
        "unknowns": ["当前固件中每个入口的真实可用状态", "各服务在美国站的权益和地区限制"],
        "business_impact": "内容来源和成本不透明会直接损伤价值感、信任和推荐意愿。",
        "acceptance_criteria": ["内容入口图明确区分服务、账号、订阅、网络和离线条件", "第三方权益不包装为硬件永久权益", "所有图标和说明与当前实机一致"],
        "evidence_refs": [(109, "R109-U03", "正向路径"), (109, "R109-U05", "订阅边界"), (209, "R209-U02", "入口缺失"), (222, "R222-U08", "权益落差"), (292, "R292-U03", "付费边界"), (304, "R304-U04", "多入口价值"), (528, "R528-U03", "更新后成本")],
    },
    "V-04": {
        "current_state": "便携、收纳、尺寸和多设备连接分散在不同页面区域，用户难以判断实际移动方式与连接边界。",
        "voc_facts": ["样本支持紧凑、便携、屏幕可收纳以及跨电视和投影移动的正向价值。", "也出现设备尺寸与预期不同、支架孔未展示、外接音响和 HDMI 音频边界不清。"],
        "unknowns": ["美国站当前随附物与实机尺寸展示是否一致", "全部外接组合的实测结果"],
        "business_impact": "尺寸、随附物或连接理解错误会增加购买前疑虑和购买后试错。",
        "acceptance_criteria": ["图片以实机比例展示尺寸、重量、肩带和收纳", "连接矩阵分别说明画面与声音路径", "主图随附物与美国站包装一致"],
        "evidence_refs": [(206, "R206-U02", "移动连接"), (207, "R207-U01", "便携场景"), (207, "R207-U07", "收纳价值"), (222, "R222-U07", "尺寸预期"), (483, "R483-U03", "信息缺口"), (542, "R542-U01", "便携价值"), (548, "R548-U05", "连接边界")],
    },
    "V-05": {
        "current_state": "声音、双麦、回声与 EQ 多以功能或参数出现，未稳定连接到两人合唱、室内外演唱和整场娱乐结果。",
        "voc_facts": ["样本中声音、音量、麦克风和共同演唱有多条正向证据。", "同时存在拾音距离、延迟和大型场地覆盖的边界，不能使用零延迟或无条件专业级承诺。"],
        "unknowns": ["不同音量与场地下的覆盖边界", "麦克风延迟、拾音和 EQ 的量产一致性"],
        "business_impact": "把功能转成可感知结果有助于转化，但夸大容量或专业性会制造反向信任风险。",
        "acceptance_criteria": ["图片展示真实演唱关系与控制方式", "所有人数、场地和延迟表述有实测依据", "正向声音资产与使用边界同时可见"],
        "evidence_refs": [(116, "R116-U02", "使用边界"), (187, "R187-U03", "户外声音价值"), (187, "R187-U04", "活动结果"), (234, "R234-U04", "正向资产"), (427, "R427-U02", "延迟边界"), (457, "R457-U05", "正向资产"), (457, "R457-U06", "容量边界"), (485, "R485-U04", "共同演唱结果")],
    },
    "P-01": {
        "current_state": "页面宣称 8 小时续航，FAQ 另列约 4 小时充电和可边充边用；适配器规格、线材与美国站包装条件尚未集中对齐。",
        "voc_facts": ["样本中出现充电慢、续航只有几小时、包装缺少合适适配器、麦克风无法保持电量或充电后仍无法启动。", "也有用户认可长续航和麦克风机内自充电的便利，说明价值成立但依赖可靠工作。", "这些证据证明问题存在，不代表市场故障率。"],
        "unknowns": ["当前美国站 BOM 和包装是否跨批次一致", "问题真实发生率与根因", "8 小时续航在声明条件下是否可复现"],
        "business_impact": "供电失败会阻断首次使用、礼物和聚会任务，并触发退货、不推荐与高价信任损失。",
        "acceptance_criteria": ["BOM、实物包装、说明书和页面一致", "随附配件可为主机和两支麦克风正常充电", "续航与充电声明在明确条件下通过量产机测试", "失败结果可分流到页面、包装或产品修复"],
        "evidence_refs": [(20, "R020-U01", "充电问题"), (20, "R020-U02", "续航问题"), (161, "R161-U02", "正向边界"), (169, "R169-U01", "包装问题"), (169, "R169-U04", "任务阻断"), (277, "R277-U01", "麦克风充电"), (457, "R457-U02", "正向价值"), (486, "R486-U02", "麦克风充电")],
    },
    "P-02": {
        "current_state": "内置平板、应用、歌词和联网共同承担完整唱歌时段，但页面没有区分硬件、系统、网络和第三方应用的责任边界。",
        "voc_facts": ["样本中有联网、应用和歌曲访问顺畅的正向路径。", "也有平板迟缓、触控延迟、缓冲、应用不可用、歌词过小和系统重启等问题。"],
        "unknowns": ["问题在硬件性能、固件、网络或第三方应用间的归因", "长时运行和弱网下的复现率"],
        "business_impact": "启动、搜索、播放或歌词任何一环失败，都会让完整唱歌任务中断并削弱一体化价值。",
        "acceptance_criteria": ["建立网络、应用、歌词和长时运行测试矩阵", "问题可归因并分流到固件、硬件、第三方或页面说明", "关键唱歌路径在量产机上连续通过"],
        "evidence_refs": [(161, "R161-U05", "性能问题"), (161, "R161-U06", "触控问题"), (304, "R304-U05", "入口性能"), (350, "R350-U04", "场地网络"), (350, "R350-U09", "应用不可用"), (359, "R359-U15", "长时性能"), (445, "R445-U06", "歌词可读性"), (548, "R548-U04", "流媒体中断")],
    },
    "P-03": {
        "current_state": "页面强调麦克风自动连接和演唱体验，但延迟、配对、重启恢复与两支麦克风一致性尚未形成明确质量边界。",
        "voc_facts": ["样本中既有自动连接和声音良好的正向证据，也有延迟、不同步、无法连接及必须重启或重置的反馈。", "延迟样本规模不等于发生率，但对演唱任务的严重度较高。"],
        "unknowns": ["延迟与音效、音量、无线环境和使用时长的关系", "配对失败是否集中于固件或批次"],
        "business_impact": "延迟或失配直接破坏自然演唱，并可能使高价一体机失去核心用途。",
        "acceptance_criteria": ["建立端到端延迟阈值和测量方法", "两支麦克风在开机、休眠、长时运行后稳定连接", "失配后可自动恢复或提供明确恢复入口"],
        "evidence_refs": [(195, "R195-U01", "连接失败"), (221, "R221-U01", "延迟问题"), (330, "R330-U01", "开机失配"), (427, "R427-U02", "延迟问题"), (457, "R457-U03", "正向边界"), (480, "R480-U02", "轻微延迟"), (483, "R483-U08", "同步问题"), (483, "R483-U09", "延迟问题")],
    },
    "P-04": {
        "current_state": "HDMI、电视、投影和外接音响被作为连接能力展示，但音频与视频输出路径及设备兼容范围未形成可执行测试矩阵。",
        "voc_facts": ["样本中存在投影和电视显示歌词的成功案例。", "也存在 HDMI 仅输出视频、无法连接 soundbar 和外接屏幕后性能下降的案例。"],
        "unknowns": ["各接口在当前固件下的能力边界", "常见电视、投影、soundbar 与转换链路的兼容性"],
        "business_impact": "连接失败会破坏家庭影音整合和大屏歌词任务，并带来绕行、客服和退货。",
        "acceptance_criteria": ["建立画面、歌词、音频分项通过矩阵", "明确修固件、改接口或仅澄清页面的判断规则", "页面只展示通过测试的组合"],
        "evidence_refs": [(157, "R157-U05", "正向路径"), (206, "R206-U01", "正向路径"), (359, "R359-U05", "正向路径"), (359, "R359-U06", "性能边界"), (470, "R470-U02", "兼容失败"), (548, "R548-U05", "能力边界")],
    },
    "P-05": {
        "current_state": "声音、音量、便携和机内麦克风收纳已有较强正向证据，是后续改动时需要保护的体验基线。",
        "voc_facts": ["样本跨家庭、派对、户外和日常场景反复肯定声音、音量、便携与收纳。", "少量反馈指出拾音、音质偏好和场地覆盖边界，说明应保持优势同时监测条件性缺口。"],
        "unknowns": ["优势在量产批次间的一致性", "远程音量、EQ、保护袋等增量需求的优先级"],
        "business_impact": "若为解决其他问题而牺牲声音或便携，会损伤已被验证的核心购买价值。",
        "acceptance_criteria": ["后续版本不低于当前声音、音量和便携基线", "新增控制或配件需求先验证使用频率与影响", "回归测试覆盖家庭、户外和移动场景"],
        "evidence_refs": [(116, "R116-U01", "负向边界"), (187, "R187-U03", "户外声音"), (206, "R206-U02", "便携价值"), (206, "R206-U05", "声音价值"), (207, "R207-U01", "移动价值"), (234, "R234-U04", "声音价值"), (457, "R457-U05", "声音价值"), (542, "R542-U01", "便携价值")],
    },
}


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def clean_markdown(value: str) -> str:
    return value.replace("`", "").replace("**", "").strip()


def parse_markdown_table(markdown: str, heading: str) -> list[list[str]]:
    section = markdown.split(heading, 1)[1].split("\n\n## ", 1)[0]
    lines = [line.strip() for line in section.splitlines() if line.strip().startswith("|")]
    return [[cell.strip() for cell in line.strip("|").split("|")] for line in lines[2:]]


def parse_actions() -> list[dict]:
    markdown = ACTION_PATH.read_text(encoding="utf-8")
    sections = [
        ("## Listing 建议", "listing", ["id", "priority", "recommendation", "release_gate"]),
        (
            "## 主副图与 A+ 建议",
            "visual",
            ["id", "priority", "information_job", "recommendation", "evidence_refs"],
        ),
        (
            "## 产品验证与迭代建议",
            "product",
            ["id", "priority", "question", "minimum_validation", "decision_basis"],
        ),
    ]
    actions: list[dict] = []
    for heading, category, keys in sections:
        for cells in parse_markdown_table(markdown, heading):
            if len(cells) != len(keys):
                raise ValueError(f"Unexpected action table row under {heading}: {cells}")
            action = {key: clean_markdown(value) for key, value in zip(keys, cells)}
            action["category"] = category
            action["title"] = ACTION_TITLES[action["id"]]
            actions.append(action)
    return actions


def rows_from_text(text: str) -> list[int]:
    rows: set[int] = set()
    for match in re.finditer(r"数据行\s*`([^`]+)`", text):
        rows.update(int(value) for value in re.findall(r"\d+", match.group(1)))
    return sorted(rows)


def parse_blocks(lines: list[str]) -> list[dict]:
    blocks: list[dict] = []
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue
        if line.startswith("- "):
            items: list[str] = []
            while index < len(lines) and lines[index].strip().startswith("- "):
                items.append(lines[index].strip()[2:].strip())
                index += 1
            text = "\n".join(items)
            blocks.append({"type": "list", "items": items, "review_rows": rows_from_text(text)})
            continue
        if line.startswith("> "):
            quote_lines: list[str] = []
            while index < len(lines) and lines[index].strip().startswith("> "):
                quote_lines.append(lines[index].strip()[2:].strip())
                index += 1
            text = " ".join(quote_lines)
            blocks.append({"type": "quote", "text": text, "review_rows": rows_from_text(text)})
            continue
        paragraph: list[str] = []
        while index < len(lines):
            candidate = lines[index].strip()
            if not candidate or candidate.startswith("- ") or candidate.startswith("> "):
                break
            paragraph.append(candidate)
            index += 1
        text = " ".join(paragraph)
        blocks.append({"type": "paragraph", "text": text, "review_rows": rows_from_text(text)})
    return blocks


def rows_from_blocks(blocks: list[dict]) -> list[int]:
    return sorted({row for block in blocks for row in block["review_rows"]})


def parse_overview() -> dict:
    lines = OVERVIEW_PATH.read_text(encoding="utf-8").splitlines()
    first_section = next(index for index, line in enumerate(lines) if line.startswith("## "))
    intro = parse_blocks([line for line in lines[1:first_section] if line.strip()])
    section_starts = [index for index, line in enumerate(lines) if line.startswith("## ")]
    sections: list[dict] = []
    for position, start in enumerate(section_starts):
        end = section_starts[position + 1] if position + 1 < len(section_starts) else len(lines)
        title = lines[start][3:].strip()
        if title not in SECTION_IDS:
            raise ValueError(f"Unknown overview section: {title}")
        content = lines[start + 1 : end]
        subsection_starts = [index for index, line in enumerate(content) if line.startswith("### ")]
        lead_end = subsection_starts[0] if subsection_starts else len(content)
        lead_blocks = parse_blocks(content[:lead_end])
        subsections: list[dict] = []
        for subsection_position, subsection_start in enumerate(subsection_starts):
            subsection_end = (
                subsection_starts[subsection_position + 1]
                if subsection_position + 1 < len(subsection_starts)
                else len(content)
            )
            blocks = parse_blocks(content[subsection_start + 1 : subsection_end])
            subsection_title = content[subsection_start][4:].strip()
            review_rows = rows_from_blocks(blocks)
            if not review_rows:
                review_rows = SUBSECTION_EVIDENCE.get((SECTION_IDS[title], subsection_title), [])
            subsections.append(
                {
                    "title": subsection_title,
                    "blocks": blocks,
                    "review_rows": review_rows,
                }
            )
        sections.append(
            {
                "id": SECTION_IDS[title],
                "title": title,
                "lead_blocks": lead_blocks,
                "subsections": subsections,
                "review_rows": sorted(
                    set(rows_from_blocks(lead_blocks))
                    | {row for subsection in subsections for row in subsection["review_rows"]}
                ),
            }
        )
    return {"intro": intro, "sections": sections}


def evidence_by_state(actual=None, planned=None, estimated=None, reported=None) -> dict:
    return {
        "actual": sorted(actual or []),
        "planned": sorted(planned or []),
        "estimated": sorted(estimated or []),
        "reported": sorted(reported or []),
    }


def evidence_rows(states: dict) -> list[int]:
    return sorted({row for rows in states.values() for row in rows})


BRIDGES = [
    {
        "id": "F-01",
        "finding": "消费者购买的是共同参与，不是双麦规格本身",
        "meaning": "家庭、伴侣和朋友真正需要的是让更多人容易加入并持续获得乐趣。",
        "evidence_by_state": evidence_by_state(
            actual=[183, 226, 234, 457, 485, 526], planned=[526], reported=[457]
        ),
        "business_impact": "页面若只展示两支麦克风，会遗漏家庭共同参与这一购买理由。",
        "action_ids": ["V-01", "V-05"],
    },
    {
        "id": "F-02",
        "finding": "第一次使用是否成功取决于完整启动链路",
        "meaning": "配件、充电、开机、联网、账号、内容入口和取麦任何一环都能阻断开唱。",
        "evidence_by_state": evidence_by_state(actual=[167, 169, 194, 207, 225, 304, 457, 486]),
        "business_impact": "首次失败会直接损伤礼物体验、价格合理性和退货风险。",
        "action_ids": ["L-04", "V-02"],
    },
    {
        "id": "F-03",
        "finding": "歌曲可得性包含账号、订阅和持续成本",
        "meaning": "应用入口存在，不等于歌曲免费、完整或持续可用。",
        "evidence_by_state": evidence_by_state(
            actual=[109, 157, 205, 206, 209, 234, 483, 485, 526, 528], estimated=[109]
        ),
        "business_impact": "购买前预期不准确，会让内容问题上升为整机价值和信任问题。",
        "action_ids": ["L-01", "V-03", "P-02"],
    },
    {
        "id": "F-04",
        "finding": "活动价值要求设备在整个时段持续可靠",
        "meaning": "供电、网络、内容、声音、麦克风和显示链路需要共同成立。",
        "evidence_by_state": evidence_by_state(
            actual=[20, 23, 116, 187, 206, 207, 221, 226, 330, 350, 526, 542],
            planned=[457],
            estimated=[20, 457],
            reported=[206],
        ),
        "business_impact": "可靠性失败不是单项扣分，而会让活动任务整体归零。",
        "action_ids": ["L-02", "P-01", "P-03"],
    },
    {
        "id": "F-05",
        "finding": "外接屏幕和影音设备属于部分用户的真实工作流",
        "meaning": "HDMI、电视、投影和外接音响的画面、歌词与声音路径并不等价。",
        "evidence_by_state": evidence_by_state(
            actual=[157, 206, 304, 359, 445, 470, 548], planned=[548], estimated=[359, 548]
        ),
        "business_impact": "连接边界不清会带来高价落差、绕行和退货。",
        "action_ids": ["L-03", "V-04", "P-04"],
    },
    {
        "id": "F-06",
        "finding": "声音与便携是应被保护的已验证优势",
        "meaning": "这些优势跨家庭、派对和户外场景帮助共同参与与活动成立。",
        "evidence_by_state": evidence_by_state(actual=[116, 187, 207, 234, 445, 457, 485]),
        "business_impact": "优化内容、连接和可靠性时，不应牺牲声音、双麦便利或移动性。",
        "action_ids": ["P-05"],
    },
]


def is_known(value) -> bool:
    if isinstance(value, list):
        return bool(value) and value != ["unknown"]
    if isinstance(value, dict):
        return any(is_known(item) for item in value.values())
    return value not in (None, "", "unknown")


def build_evidence_reviews() -> list[dict]:
    pilots = load_jsonl(PILOT_PATH)
    coding_rows = load_jsonl(CODING_PATH)
    raw_reviews = load_jsonl(REVIEWS_PATH)
    coding_by_row = {row["来源定位"]["数据行"]: row for row in coding_rows}
    evidence: list[dict] = []
    for pilot in pilots:
        data_row = pilot["来源定位"]["数据行"]
        coding = coding_by_row[data_row]
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


def build_coverage(evidence_reviews: list[dict]) -> list[dict]:
    key_map = {
        "消费者": "consumer",
        "使用场景": "scenes",
        "用户任务": "tasks",
        "购买动机": "motivations",
        "期望结果": "expectations",
        "实际结果": "outcomes",
        "满意点": "satisfiers",
        "价值链": "value_chains",
        "未满足的需求": "unmet_needs",
        "证据强度": "evidence_strength",
        "总体极性": "sentiment",
        "决策结果": "decision",
    }
    return [
        {
            "field": field,
            "known": sum(is_known(review[key_map[field]]) for review in evidence_reviews),
            "denominator": len(evidence_reviews),
        }
        for field in REVIEW_FIELDS
    ]


def build_taxonomy() -> dict:
    themes = json.loads(THEME_PATH.read_text(encoding="utf-8"))
    return {
        "labels": {
            item[id_key]: item[name_key]
            for group, id_key, name_key in [
                (themes["用户主题"], "主题ID", "主题名称"),
                (themes["产品体验主题"], "主题ID", "主题名称"),
                (themes["用户机会链"], "机会链ID", "机会链名称"),
            ]
            for item in group
        },
        "user_themes": {
            item["主题ID"]: set(item["数据行"]) for item in themes["用户主题"]
        },
        "product_themes": {
            item["主题ID"]: set(item["unit_id"]) for item in themes["产品体验主题"]
        },
        "opportunity_chains": {
            item["机会链ID"]: set(item["数据行"]) for item in themes["用户机会链"]
        },
    }


def decision_signals(value: str) -> list[str]:
    signals: list[str] = []
    if "退货" in value or "退回" in value:
        signals.append("退货")
    if "不推荐" in value or "不要购买" in value or "不要买" in value:
        signals.append("不推荐")
    elif "推荐" in value:
        signals.append("推荐")
    if any(token in value for token in ["保留", "继续使用", "持续使用", "另购", "仍喜欢"]):
        signals.append("继续使用")
    if any(token in value for token in ["绕行", "改用", "替代"]):
        signals.append("绕行")
    return signals or ["未明确"]


def enrich_actions(actions: list[dict], bridges: list[dict]) -> None:
    targets = {
        "listing": ["五点描述", "文案"],
        "visual": ["副图", "A+"],
        "product": ["产品迭代"],
    }
    for action in actions:
        if action["category"] == "visual":
            action["theme_evidence_refs"] = action.pop("evidence_refs")
        context = ACTION_CONTEXTS[action["id"]]
        action.update({key: value for key, value in context.items() if key != "evidence_refs"})
        action["evidence_refs"] = [
            {"review_row": row, "unit_id": unit_id, "role": role}
            for row, unit_id, role in context["evidence_refs"]
        ]
        linked = [bridge for bridge in bridges if action["id"] in bridge["action_ids"]]
        action["source_finding_ids"] = [bridge["id"] for bridge in linked]
        action["source_review_rows"] = sorted(
            {reference["review_row"] for reference in action["evidence_refs"]}
        )
        action["target_surfaces"] = targets[action["category"]]
        action["workflow_status"] = "保持并监测" if action["id"] == "P-05" else "待验证"


def enrich_evidence_reviews(
    evidence_reviews: list[dict], actions: list[dict], bridges: list[dict], taxonomy: dict
) -> None:
    for review in evidence_reviews:
        row = review["data_row"]
        unit_ids = {unit["unit_id"] for unit in review["units"]}
        action_ids = [
            action["id"]
            for action in actions
            if any(reference["review_row"] == row for reference in action["evidence_refs"])
        ]
        action_categories = sorted(
            {action["category"] for action in actions if action["id"] in action_ids}
        )
        review["facets"] = {
            "user_theme_ids": sorted(
                theme_id
                for theme_id, rows in taxonomy["user_themes"].items()
                if row in rows
            ),
            "product_theme_ids": sorted(
                theme_id
                for theme_id, theme_units in taxonomy["product_themes"].items()
                if unit_ids & theme_units
            ),
            "opportunity_chain_ids": sorted(
                chain_id
                for chain_id, rows in taxonomy["opportunity_chains"].items()
                if row in rows
            ),
            "finding_ids": [bridge["id"] for bridge in bridges if row in bridge["review_rows"]],
            "action_ids": action_ids,
            "business_surfaces": action_categories,
            "scene_states": [
                state
                for state, source_key in [
                    ("actual", "实际场景"),
                    ("planned", "计划场景"),
                    ("estimated", "用户估计"),
                    ("reported", "转述证据"),
                ]
                if is_known(review["scenes"][source_key])
            ],
            "decision_signals": decision_signals(review["decision"]),
            "dimensions": sorted(
                {dimension for unit in review["units"] for dimension in unit["dimensions"]}
            ),
            "unit_polarities": sorted({unit["polarity"] for unit in review["units"]}),
        }


def build_data() -> dict:
    narrative = parse_overview()
    evidence_reviews = build_evidence_reviews()
    actions = parse_actions()
    bridges = [{**bridge, "review_rows": evidence_rows(bridge["evidence_by_state"])} for bridge in BRIDGES]
    taxonomy = build_taxonomy()
    enrich_actions(actions, bridges)
    enrich_evidence_reviews(evidence_reviews, actions, bridges, taxonomy)
    coverage = build_coverage(evidence_reviews)
    coverage_by_field = {item["field"]: item["known"] for item in coverage}
    both_satisfied_and_unmet = sum(
        is_known(review["satisfiers"]) and is_known(review["unmet_needs"])
        for review in evidence_reviews
    )
    scene_states = {
        "actual": sum(is_known(review["scenes"]["实际场景"]) for review in evidence_reviews),
        "planned": sum(is_known(review["scenes"]["计划场景"]) for review in evidence_reviews),
        "estimated": sum(is_known(review["scenes"]["用户估计"]) for review in evidence_reviews),
        "reported": sum(is_known(review["scenes"]["转述证据"]) for review in evidence_reviews),
    }
    return {
        "contract": {
            "schema_version": "0.4-decision-evidence-workbench-pilot",
            "artifact_role": "40 条 VOC 叙事报告的结构化消费契约",
            "source_roles": {
                "04": "评论原文与译文事实源",
                "08": "Review 层与反馈点编码事实源",
                "12": "主题边界校验源",
                "13": "业务动作事实源",
                "14": "经用户确认的 VOC 叙事内容源",
            },
            "display_rules": [
                "主阅读路径先回答消费者、场景、任务、期待、实际结果、价值与缺口，再进入动作。",
                "十二个 Review 层字段共同支持一条体验叙事，不拆成十二张数据目录。",
                "实际场景、计划场景、用户估计和转述证据在下钻时保持分开。",
                "unknown 只表示该字段无证据，不使整条 Review 失效。",
                "所有动作同时显示 ID、名称和完整含义。",
                "动作证据按动作独立选择，不继承宽泛发现的全部 Review。",
                "动作证据精确到数据行与 unit_id，并标明其在决策中的角色。",
                "证据下钻保留英文原文、中文译文、数据行、编码序号和 unit_id。",
            ],
            "required_sections": [
                "narrative",
                "finding_to_action",
                "actions",
                "evidence_reviews",
                "methodology",
            ],
        },
        "report": {
            "asin": "B0CR1R7FKP",
            "title": "Ikarao X2 评论洞察",
            "subtitle": "谁在使用、如何使用、想完成什么，以及体验如何导向业务行动",
            "scope_label": "40 条分层样本，用于校准报告结构，不代表 559 条总体比例",
            "generated_on": "2026-07-19",
        },
        "summary": {
            "thesis": "消费者购买的并不只是一台可以唱歌的音响，而是一套降低准备负担、组织多人参与并维持整场娱乐活动的一体式工具。",
            "task_chain": ["准备设备", "找到歌曲", "邀请他人参与", "持续演唱", "活动不中断"],
            "mixed_experience_count": both_satisfied_and_unmet,
            "metrics": [
                {"label": "消费者有明确证据", "value": coverage_by_field["消费者"], "denominator": 40},
                {"label": "实际场景有明确证据", "value": scene_states["actual"], "denominator": 40},
                {"label": "购买动机有明确证据", "value": coverage_by_field["购买动机"], "denominator": 40},
                {"label": "决策结果有明确证据", "value": coverage_by_field["决策结果"], "denominator": 40},
            ],
        },
        "narrative": narrative,
        "finding_to_action": bridges,
        "actions": actions,
        "evidence_reviews": evidence_reviews,
        "taxonomy": {"labels": taxonomy["labels"]},
        "methodology": {
            "sample": "40 条样本按 1 至 5 星各抽取 8 条，用于校准结构，不代表 559 条总体分布。",
            "quantification_rule": "计数只说明这 40 条分层样本中有多少条提供了相应字段或主题证据，不可解释为消费者占比、场景占比或问题发生率。",
            "scene_states": scene_states,
            "field_coverage": coverage,
            "boundaries": [
                "评论不能可靠推断年龄、收入、职业、销量占比或技术根因。",
                "消费者未知的 Review 仍可证明充电、联网、声音或退货结果。",
                "购买动机未知时不能从星级、实际结果或决策结果倒推原因。",
                "同一 Review 可以同时满意和不满，也可以属于多个情境与任务主题。",
            ],
        },
    }


def validate_data(data: dict) -> None:
    sample_rows = {review["data_row"] for review in data["evidence_reviews"]}
    if len(data["evidence_reviews"]) != 40 or len(sample_rows) != 40:
        raise ValueError("Evidence library must contain 40 unique pilot reviews")
    if [section["id"] for section in data["narrative"]["sections"]] != list(SECTION_IDS.values()):
        raise ValueError("Narrative sections drifted from the approved 14 structure")
    narrative_rows = {
        row for section in data["narrative"]["sections"] for row in section["review_rows"]
    }
    bridge_rows = {row for bridge in data["finding_to_action"] for row in bridge["review_rows"]}
    if not narrative_rows | bridge_rows <= sample_rows:
        raise ValueError("Narrative or bridge cites rows outside the 40-review pilot")
    action_ids = {action["id"] for action in data["actions"]}
    linked_action_ids = {
        action_id for bridge in data["finding_to_action"] for action_id in bridge["action_ids"]
    }
    if action_ids != set(ACTION_TITLES) or action_ids != linked_action_ids:
        raise ValueError("Actions must be complete and each action must link to a finding")
    if any(not action["source_review_rows"] for action in data["actions"]):
        raise ValueError("Each action needs pilot evidence rows")
    review_units = {
        review["data_row"]: {unit["unit_id"] for unit in review["units"]}
        for review in data["evidence_reviews"]
    }
    required_action_keys = {
        "current_state",
        "voc_facts",
        "unknowns",
        "business_impact",
        "acceptance_criteria",
        "evidence_refs",
        "target_surfaces",
        "workflow_status",
    }
    for action in data["actions"]:
        if not required_action_keys <= action.keys():
            raise ValueError(f"Action {action['id']} does not expose the complete decision chain")
        if not all(
            reference["review_row"] in review_units
            and reference["unit_id"] in review_units[reference["review_row"]]
            and reference["role"]
            for reference in action["evidence_refs"]
        ):
            raise ValueError(f"Action {action['id']} contains an invalid row or unit_id reference")
        if action["source_review_rows"] != sorted(
            {reference["review_row"] for reference in action["evidence_refs"]}
        ):
            raise ValueError(f"Action {action['id']} rows must come only from exact action evidence")
    required_review_keys = {
        "consumer",
        "scenes",
        "tasks",
        "motivations",
        "expectations",
        "outcomes",
        "satisfiers",
        "value_chains",
        "unmet_needs",
        "evidence_strength",
        "sentiment",
        "decision",
    }
    for review in data["evidence_reviews"]:
        if not required_review_keys <= review.keys():
            raise ValueError(f"Review {review['data_row']} does not expose all 12 review-layer fields")
        if "facets" not in review or not {
            "user_theme_ids",
            "product_theme_ids",
            "opportunity_chain_ids",
            "finding_ids",
            "action_ids",
            "business_surfaces",
            "scene_states",
            "decision_signals",
            "dimensions",
            "unit_polarities",
        } <= review["facets"].keys():
            raise ValueError(f"Review {review['data_row']} is missing evidence workbench facets")
    p01 = next(action for action in data["actions"] if action["id"] == "P-01")
    if p01["source_review_rows"] != [20, 161, 169, 277, 457, 486]:
        raise ValueError("P-01 evidence drifted from the calibrated charging and packaging evidence")
    if data["summary"]["mixed_experience_count"] != 25:
        raise ValueError("Expected 25 reviews with both satisfaction and unmet needs")
    coverage = {item["field"]: item["known"] for item in data["methodology"]["field_coverage"]}
    if coverage["决策结果"] != 33 or coverage["购买动机"] != 16:
        raise ValueError("Pilot coverage counts drifted from the approved narrative")


def render_html(data: dict, json_sha256: str) -> str:
    embedded = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    template = HTML_TEMPLATE.replace("__TITLE__", html.escape(data["report"]["title"]))
    template = template.replace("__DATA__", embedded)
    return template.replace("__JSON_SHA256__", json_sha256)


def main() -> None:
    data = build_data()
    validate_data(data)
    data_text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    DATA_PATH.write_text(data_text, encoding="utf-8", newline="\n")
    digest = hashlib.sha256(data_text.encode("utf-8")).hexdigest()
    HTML_PATH.write_text(render_html(data, digest), encoding="utf-8", newline="\n")
    print(f"wrote {DATA_PATH.relative_to(ROOT)}")
    print(f"wrote {HTML_PATH.relative_to(ROOT)}")
    print(f"data_sha256={digest}")


HTML_TEMPLATE = r'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light">
  <meta name="report-data-sha256" content="__JSON_SHA256__">
  <title>__TITLE__</title>
  <style>
    :root {
      --ink: #202124;
      --muted: #656a73;
      --line: #dfe2e6;
      --soft: #f5f6f7;
      --paper: #ffffff;
      --nav: #25282d;
      --coral: #c94f3d;
      --teal: #147b70;
      --blue: #326ba4;
      --amber: #a77518;
      --danger: #a53d3d;
      --radius: 6px;
      --shadow: 0 14px 34px rgba(20, 22, 25, .14);
    }
    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body {
      margin: 0;
      color: var(--ink);
      background: var(--paper);
      font-family: Inter, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
      font-size: 15px;
      line-height: 1.72;
      letter-spacing: 0;
    }
    button, input, select { font: inherit; letter-spacing: 0; }
    button { cursor: pointer; }
    code { padding: 1px 4px; background: var(--soft); border-radius: 3px; }
    .sidebar {
      position: fixed;
      inset: 0 auto 0 0;
      width: 236px;
      padding: 26px 16px;
      color: #fff;
      background: var(--nav);
      overflow-y: auto;
      z-index: 20;
    }
    .brand { padding: 0 10px 20px; border-bottom: 1px solid rgba(255,255,255,.16); }
    .brand strong { display: block; font-size: 17px; }
    .brand span { color: #bcc1c8; font-size: 12px; }
    .nav { display: grid; gap: 3px; margin-top: 16px; }
    .nav a {
      min-height: 40px;
      padding: 8px 10px;
      color: #cfd3d8;
      border-left: 3px solid transparent;
      text-decoration: none;
    }
    .nav a:hover, .nav a.active { color: #fff; border-left-color: var(--coral); background: rgba(255,255,255,.06); }
    .nav-num { display: inline-block; width: 28px; color: #8f969f; font-size: 11px; }
    .side-note { margin: 24px 10px 0; color: #9ea5ae; font-size: 12px; }
    main { margin-left: 236px; }
    .report-head { padding: 48px clamp(24px, 6vw, 84px) 40px; border-bottom: 1px solid var(--line); background: #f7f4f1; }
    .head-inner, .content, .footer > div { width: min(1080px, 100%); margin: 0 auto; }
    .eyebrow { color: var(--coral); font-size: 12px; font-weight: 800; text-transform: uppercase; }
    h1, h2, h3 { margin: 0; line-height: 1.25; letter-spacing: 0; }
    h1 { max-width: 760px; margin-top: 8px; font-size: 42px; }
    h2 { font-size: 28px; }
    h3 { font-size: 18px; }
    .report-head .subtitle { max-width: 760px; margin: 14px 0 0; color: #4f555d; font-size: 18px; }
    .scope { display: inline-block; margin-top: 18px; padding: 5px 8px; color: #5c5148; border: 1px solid #d8cec5; background: #fff; border-radius: 4px; font-size: 12px; }
    .content { padding: 0 clamp(20px, 5vw, 70px); }
    section { padding: 64px 0; border-bottom: 1px solid var(--line); scroll-margin-top: 20px; }
    .section-head { display: grid; grid-template-columns: minmax(260px, .85fr) minmax(320px, 1.15fr); gap: 36px; align-items: end; margin-bottom: 30px; }
    .kicker { margin: 0 0 7px; color: var(--coral); font-size: 12px; font-weight: 800; }
    .section-answer { margin: 0; color: var(--muted); }
    .thesis { max-width: 900px; margin: 0; font-size: 23px; line-height: 1.5; font-weight: 720; }
    .task-chain { display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; margin: 28px 0; }
    .task-step { position: relative; padding: 14px 12px; border-top: 3px solid var(--teal); background: var(--soft); text-align: center; font-weight: 700; }
    .task-step:not(:last-child)::after { content: "→"; position: absolute; right: -8px; top: 12px; color: var(--coral); z-index: 2; }
    .metrics { display: grid; grid-template-columns: repeat(4, 1fr); margin-top: 28px; border: 1px solid var(--line); }
    .metric { min-height: 112px; padding: 18px; border-right: 1px solid var(--line); }
    .metric:last-child { border-right: 0; }
    .metric strong { display: block; font-size: 29px; line-height: 1; }
    .metric span { color: var(--muted); font-size: 12px; }
    .mixed-note { margin: 18px 0 0; padding: 13px 16px; border-left: 4px solid var(--amber); background: #fbf7ec; }
    .story-section + .story-section { margin-top: 48px; }
    .story-title { margin-bottom: 16px; }
    .prose { max-width: 880px; }
    .prose p { margin: 0 0 14px; }
    .prose ul { margin: 0 0 16px; padding-left: 22px; }
    .prose blockquote { margin: 18px 0; padding: 12px 18px; color: #38424d; border-left: 4px solid var(--blue); background: var(--soft); }
    .subsection { display: grid; grid-template-columns: minmax(220px, .58fr) minmax(0, 1.42fr); gap: 34px; padding: 27px 0; border-top: 1px solid var(--line); }
    .subsection:first-of-type { margin-top: 20px; }
    .subsection h3 { position: sticky; top: 20px; align-self: start; }
    .evidence-coverage { margin: 2px 0 8px; color: var(--muted); font-size: 12px; }
    .evidence-coverage strong { color: var(--ink); }
    .evidence-link { padding: 0; color: var(--blue); background: transparent; border: 0; font-weight: 700; text-align: left; }
    .evidence-link:hover { text-decoration: underline; }
    .states { display: flex; flex-wrap: wrap; gap: 6px; margin: 8px 0; }
    .state { padding: 2px 6px; border: 1px solid var(--line); border-radius: 3px; font-size: 11px; }
    .state.actual { color: var(--teal); }
    .state.planned { color: var(--blue); }
    .state.estimated { color: var(--amber); }
    .state.reported { color: #74538c; }
    .bridge-list { display: grid; }
    .bridge {
      display: grid;
      grid-template-columns: minmax(210px, .9fr) minmax(220px, 1fr) minmax(250px, 1.15fr);
      gap: 28px;
      padding: 24px 0;
      border-top: 1px solid var(--line);
    }
    .bridge:first-child { border-top: 0; }
    .bridge-id { color: var(--coral); font-size: 12px; font-weight: 850; }
    .bridge h3 { margin-top: 4px; }
    .bridge p { margin: 0; color: var(--muted); }
    .bridge p + p { margin-top: 10px; }
    .action-pills { display: flex; flex-wrap: wrap; gap: 7px; align-content: start; }
    .action-pill { padding: 7px 9px; color: var(--ink); border: 1px solid var(--line); background: var(--soft); border-radius: 4px; text-align: left; }
    .action-pill b { color: var(--coral); }
    .toolbar { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 12px; margin-bottom: 20px; }
    .segmented { display: inline-flex; border: 1px solid var(--line); border-radius: 4px; overflow: hidden; }
    .segmented button { min-height: 38px; padding: 7px 12px; color: var(--muted); background: #fff; border: 0; border-right: 1px solid var(--line); }
    .segmented button:last-child { border-right: 0; }
    .segmented button.active { color: #fff; background: var(--nav); }
    .action-list { display: grid; }
    .action-card { padding: 20px 0; border-top: 1px solid var(--line); }
    .action-card:first-child { border-top: 0; }
    .action-head { display: grid; grid-template-columns: 62px minmax(0, 1fr) auto; gap: 12px; align-items: start; }
    .action-id { color: var(--coral); font-weight: 850; }
    .priority { padding: 2px 6px; color: #fff; background: var(--nav); border-radius: 3px; font-size: 11px; }
    .action-card details { margin-top: 10px; }
    summary { color: var(--blue); cursor: pointer; font-weight: 700; }
    .action-state { max-width: 840px; margin: 9px 0; color: var(--ink); }
    .action-meta, .reverse-links { display: flex; flex-wrap: wrap; gap: 6px; margin: 9px 0; }
    .meta-chip, .reverse-link { padding: 3px 7px; color: var(--muted); background: var(--soft); border: 1px solid var(--line); border-radius: 3px; font-size: 11px; }
    button.reverse-link { cursor: pointer; }
    .action-detail { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; margin-top: 14px; color: var(--muted); }
    .decision-block { padding: 14px; border-left: 3px solid var(--line); background: var(--soft); }
    .decision-block.current { border-left-color: var(--amber); }
    .decision-block.evidence { border-left-color: var(--blue); }
    .decision-block.action { border-left-color: var(--coral); }
    .decision-block.wide { grid-column: 1 / -1; }
    .decision-block p, .decision-block ul { margin: 5px 0 0; }
    .decision-block b { display: block; color: var(--ink); font-size: 12px; }
    .exact-ref { display: inline-flex; gap: 5px; margin: 4px 5px 0 0; padding: 4px 7px; color: var(--ink); background: #fff; border: 1px solid var(--line); border-radius: 3px; font-size: 11px; }
    .investigation-entry { padding: 22px 0; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); }
    .investigation-entry label { display: block; margin-bottom: 5px; font-size: 12px; font-weight: 800; }
    .investigation-entry select { width: 100%; min-height: 44px; padding: 8px 10px; border: 1px solid var(--line); border-radius: 4px; background: #fff; }
    .investigation-overview { padding: 26px 0 30px; border-bottom: 1px solid var(--line); }
    .investigation-overview h3 { margin-top: 4px; font-size: 22px; }
    .investigation-description { max-width: 860px; margin: 9px 0 0; color: #434951; }
    .investigation-metrics { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); margin: 22px 0 18px; border: 1px solid var(--line); }
    .investigation-metric { min-height: 84px; padding: 14px 16px; border-right: 1px solid var(--line); }
    .investigation-metric:last-child { border-right: 0; }
    .investigation-metric strong { display: block; font-size: 24px; line-height: 1.2; }
    .investigation-metric span { color: var(--muted); font-size: 12px; }
    .phenomenon-row { display: flex; flex-wrap: wrap; gap: 7px; align-items: center; }
    .phenomenon-row b { margin-right: 5px; font-size: 12px; }
    .phenomenon-chip { padding: 4px 7px; color: var(--ink); background: var(--soft); border: 1px solid var(--line); border-radius: 3px; font-size: 12px; cursor: pointer; }
    .phenomenon-chip:hover { border-color: var(--blue); }
    .phenomenon-chip[aria-pressed="true"] { color: #fff; background: var(--blue); border-color: var(--blue); }
    .phenomenon-chip:focus-visible { outline: 2px solid var(--blue); outline-offset: 2px; }
    .evidence-boundary { margin: 13px 0 0; color: var(--muted); font-size: 12px; }
    .evidence-refine { margin-top: 26px; }
    .evidence-toolbar { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 9px; margin-bottom: 10px; }
    .evidence-toolbar select { min-width: 0; min-height: 40px; padding: 7px 9px; border: 1px solid var(--line); border-radius: 4px; background: #fff; }
    .filter-summary { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 10px; margin-bottom: 18px; }
    .active-filters { display: flex; flex-wrap: wrap; gap: 6px; }
    .filter-chip { padding: 4px 7px; color: var(--blue); background: var(--soft); border-radius: 3px; font-size: 11px; }
    .clear-filters { padding: 5px 8px; color: var(--muted); background: #fff; border: 1px solid var(--line); border-radius: 4px; }
    .evidence-count { margin-left: 10px; color: var(--muted); text-align: right; }
    .evidence-list { display: grid; gap: 8px; }
    .evidence-card { padding: 16px 0 18px; border-top: 1px solid var(--line); }
    .evidence-card:first-child { border-top: 0; }
    .evidence-summary { display: grid; grid-template-columns: 60px minmax(0, 1fr) auto; gap: 12px; align-items: start; }
    .stars { color: var(--amber); font-weight: 800; white-space: nowrap; }
    .evidence-title strong, .evidence-title span { display: block; }
    .evidence-title span { color: var(--muted); font-size: 12px; }
    .sentiment { padding: 2px 6px; color: var(--muted); background: var(--soft); border-radius: 3px; font-size: 11px; }
    .evidence-excerpt { margin: 10px 0 0 72px; }
    .evidence-excerpt p { margin: 0 0 8px; }
    .evidence-excerpt blockquote { margin: 8px 0; padding: 9px 13px; color: #434951; border-left: 3px solid var(--blue); background: var(--soft); }
    .evidence-card-actions { display: flex; flex-wrap: wrap; gap: 12px; margin: 10px 0 0 72px; }
    .pagination { display: flex; justify-content: space-between; align-items: center; gap: 12px; margin-top: 20px; padding-top: 14px; border-top: 1px solid var(--line); }
    .pagination button { min-height: 36px; padding: 6px 10px; color: var(--blue); background: #fff; border: 1px solid var(--line); border-radius: 4px; }
    .pagination button:disabled { color: #a4a8ae; cursor: default; }
    .quote-pair { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; padding: 16px; border-left: 4px solid var(--blue); background: var(--soft); }
    .quote-pair p { margin: 0; }
    .quote-pair .source-body { margin-top: 12px; }
    .review-fields { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0 24px; margin-top: 18px; }
    .field { padding: 11px 0; border-top: 1px solid var(--line); }
    .field b { display: block; font-size: 12px; }
    .field p { margin: 3px 0 0; }
    .scene-field-group { grid-column: 1 / -1; padding: 13px 0 15px; border-top: 1px solid var(--line); }
    .scene-field-title { display: block; margin-bottom: 8px; font-size: 12px; }
    .scene-fields { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0 24px; padding-left: 14px; border-left: 3px solid var(--blue); }
    .scene-fields .field { padding: 8px 0; border-top: 0; }
    .scene-fields .field:nth-child(n + 3) { border-top: 1px solid var(--line); }
    .field-missing { color: var(--muted); }
    .field-inference { margin-top: 8px; padding: 9px 11px; border-left: 3px solid #b7791f; background: #fff8e8; }
    .field .field-inference b { display: inline; color: #8a570d; }
    .field-inference p { margin-top: 5px; }
    .field-inference-meta { color: var(--muted); font-size: 11px; }
    .value-chain-field { grid-column: 1 / -1; }
    .value-chain-list { display: grid; gap: 10px; margin-top: 8px; }
    .value-chain-item { padding: 10px 12px; border-left: 3px solid var(--blue); background: var(--soft); }
    .value-chain-item > b { color: var(--blue); }
    .value-chain-item .value-chain-meta { margin-top: 7px; color: var(--muted); font-size: 12px; }
    .value-chain-item .value-chain-meta b { display: inline; }
    .units { margin-top: 16px; }
    .unit { padding: 10px 0; border-top: 1px solid var(--line); }
    .unit-id { color: var(--coral); font-weight: 800; }
    .unit p { margin: 4px 0 0; }
    .unit.evidence-match { margin-inline: -10px; padding-inline: 10px; border-left: 4px solid var(--coral); background: #fff7f2; }
    .evidence-role { margin-left: 6px; padding: 2px 5px; color: #fff; background: var(--coral); border-radius: 3px; font-size: 10px; }
    .method-grid { display: grid; grid-template-columns: minmax(240px, .8fr) minmax(0, 1.2fr); gap: 34px; }
    .coverage { width: 100%; border-collapse: collapse; }
    .coverage th, .coverage td { padding: 8px 9px; border-bottom: 1px solid var(--line); text-align: left; }
    .coverage th { color: var(--muted); background: var(--soft); font-size: 12px; }
    .footer { padding: 26px clamp(20px, 5vw, 70px); color: #c5c9ce; background: var(--nav); }
    .drawer-backdrop { position: fixed; inset: 0; display: none; place-items: center; padding: 24px; background: rgba(25,27,31,.42); z-index: 40; }
    .drawer-backdrop.open { display: grid; }
    .drawer { position: relative; width: min(900px, 100%); max-height: min(88vh, 900px); padding: 26px; background: #fff; border-radius: var(--radius); box-shadow: var(--shadow); overflow-y: auto; }
    .drawer-close { position: sticky; top: 0; float: right; width: 38px; height: 38px; color: var(--ink); background: var(--soft); border: 1px solid var(--line); border-radius: 4px; font-size: 23px; z-index: 1; }
    .modal-back { min-height: 34px; margin: 0 0 14px; padding: 5px 9px; color: var(--blue); background: #fff; border: 1px solid var(--line); border-radius: 4px; }
    .modal-lead { margin: 8px 52px 20px 0; color: var(--muted); }
    .drawer-review { padding: 14px 0; border-top: 1px solid var(--line); }
    .drawer-review p { margin: 5px 0; color: var(--muted); }
    .modal-review-meta { margin: 5px 0 16px; color: var(--muted); }
    .modal-action-state { padding: 14px 16px; border-left: 4px solid var(--coral); background: #fff7f2; }
    .modal-action-state p { margin: 5px 0 0; }
    .modal-unit-list { margin-top: 16px; }
    .empty { padding: 30px; color: var(--muted); background: var(--soft); text-align: center; }
    @media (max-width: 960px) {
      .sidebar { position: sticky; top: 0; width: 100%; height: auto; padding: 7px 12px; overflow-x: auto; }
      .brand, .side-note { display: none; }
      .nav { display: flex; width: max-content; margin: 0; }
      .nav a { border-left: 0; border-bottom: 3px solid transparent; white-space: nowrap; }
      .nav a:hover, .nav a.active { border-left-color: transparent; border-bottom-color: var(--coral); }
      main { margin-left: 0; }
      .section-head, .subsection, .bridge { grid-template-columns: 1fr; gap: 13px; }
      .subsection h3 { position: static; }
      .metrics { grid-template-columns: repeat(2, 1fr); }
      .metric:nth-child(2) { border-right: 0; }
      .metric:nth-child(-n+2) { border-bottom: 1px solid var(--line); }
    }
    @media (max-width: 650px) {
      body { font-size: 14px; }
      .report-head { padding: 34px 20px 30px; }
      h1 { font-size: 34px; }
      h2 { font-size: 25px; }
      section { padding: 50px 0; }
      .content { padding-inline: 18px; }
      .task-chain, .metrics, .quote-pair, .review-fields, .method-grid, .action-detail, .investigation-entry, .investigation-metrics { grid-template-columns: 1fr; }
      .task-step:not(:last-child)::after { content: "↓"; right: 50%; top: auto; bottom: -17px; }
      .metric { border-right: 0; border-bottom: 1px solid var(--line); }
      .metric:last-child { border-bottom: 0; }
      .investigation-metric { border-right: 0; border-bottom: 1px solid var(--line); }
      .investigation-metric:last-child { border-bottom: 0; }
      .evidence-toolbar { grid-template-columns: 1fr; }
      .evidence-count { text-align: left; }
      .evidence-summary { grid-template-columns: 50px minmax(0, 1fr); }
      .evidence-summary .sentiment { grid-column: 2; width: fit-content; }
      .evidence-excerpt, .evidence-card-actions { margin-left: 0; }
      .action-head { grid-template-columns: 55px minmax(0, 1fr); }
      .priority { grid-column: 2; width: fit-content; }
      .drawer-backdrop { padding: 10px; }
      .drawer { max-height: calc(100vh - 20px); padding: 18px; }
    }
    @media print {
      .sidebar, .investigation-entry, .evidence-refine, .filter-summary, .pagination, .drawer-backdrop { display: none !important; }
      main { margin: 0; }
      section { break-inside: avoid; }
    }
  </style>
</head>
<body>
  <aside class="sidebar">
    <div class="brand"><strong>Review Insight</strong><span id="sideAsin"></span></div>
    <nav class="nav" aria-label="报告章节">
      <a href="#core"><span class="nav-num">01</span>核心结论</a>
      <a href="#people"><span class="nav-num">02</span>消费者与场景</a>
      <a href="#expectations"><span class="nav-num">03</span>动机、期待与实际</a>
      <a href="#value"><span class="nav-num">04</span>价值与缺口</a>
      <a href="#bridge"><span class="nav-num">05</span>发现到行动</a>
      <a href="#actions"><span class="nav-num">06</span>业务动作</a>
      <a href="#evidence"><span class="nav-num">07</span>证据工作台</a>
      <a href="#method"><span class="nav-num">08</span>方法边界</a>
    </nav>
    <p class="side-note">先读结论，再按需下钻证据。试点计数不是市场比例。</p>
  </aside>
  <main>
    <header class="report-head">
      <div class="head-inner">
        <span class="eyebrow" id="reportMeta"></span>
        <h1 id="reportTitle"></h1>
        <p class="subtitle" id="reportSubtitle"></p>
        <span class="scope" id="scopeLabel"></span>
      </div>
    </header>
    <div class="content">
      <section id="core">
        <div class="section-head">
          <div><p class="kicker">01 · 先回答最重要的问题</p><h2>这不是一台孤立的唱歌设备</h2></div>
          <p class="section-answer">核心价值来自一条连续任务链，任何关键环节中断都会改变消费者对整机的判断。</p>
        </div>
        <p class="thesis" id="thesis"></p>
        <div class="task-chain" id="taskChain"></div>
        <div class="prose" id="coreNarrative"></div>
        <div class="metrics" id="metrics"></div>
        <p class="mixed-note" id="mixedNote"></p>
      </section>

      <section id="people">
        <div class="section-head">
          <div><p class="kicker">02 · 谁在使用，如何使用</p><h2>消费者、使用情境与用户任务</h2></div>
          <p class="section-answer">不把“消费者”“场景”“任务”拆成三份孤立目录，而是放回同一段生活和活动组织过程。</p>
        </div>
        <div id="peopleNarrative"></div>
      </section>

      <section id="expectations">
        <div class="section-head">
          <div><p class="kicker">03 · 为什么买，期待什么</p><h2>购买动机、期望结果与实际结果</h2></div>
          <p class="section-answer">同一个功能表现会因购买动机不同而产生完全不同的价值后果。</p>
        </div>
        <div id="expectationNarrative"></div>
      </section>

      <section id="value">
        <div class="section-head">
          <div><p class="kicker">04 · 体验如何改变判断</p><h2>价值形成、价值中断与未满足需求</h2></div>
          <p class="section-answer">消费者可以同时喜欢声音和一体式设计，又因内容、供电或可靠性降低评价甚至退货。</p>
        </div>
        <div id="valueNarrative"></div>
      </section>

      <section id="bridge">
        <div class="section-head">
          <div><p class="kicker">05 · 从看到什么到应该做什么</p><h2>发现如何导向业务行动</h2></div>
          <p class="section-answer">每项发现先说明业务含义，再列出动作 ID 与完整名称，避免用户回头查表。</p>
        </div>
        <div class="bridge-list" id="bridgeList"></div>
      </section>

      <section id="actions">
        <div class="section-head">
          <div><p class="kicker">06 · 应该做什么</p><h2>Listing、图片/A+ 与产品动作</h2></div>
          <p class="section-answer">每项动作先交代当前状况与 VOC 事实，再说明业务影响、未知项、执行内容和验证门槛；证据精确到反馈点。</p>
        </div>
        <div class="toolbar">
          <div class="segmented" role="tablist" aria-label="动作类型">
            <button class="active" data-action-category="all">全部</button>
            <button data-action-category="listing">Listing</button>
            <button data-action-category="visual">图片与 A+</button>
            <button data-action-category="product">产品</button>
          </div>
          <span id="actionCount"></span>
        </div>
        <div class="action-list" id="actionList"></div>
      </section>

      <section id="evidence">
        <div class="section-head">
          <div><p class="kicker">07 · 用证据完成工作</p><h2>证据工作台</h2></div>
          <p class="section-answer">先选择要调查的洞察、业务动作或主题，直接看发生了什么、有多少证据以及用户原话；筛选只用于继续缩小范围。</p>
        </div>
        <div class="investigation-entry">
          <div>
            <label for="investigationContext">我现在要调查</label>
            <select id="investigationContext" aria-label="选择调查对象"></select>
          </div>
        </div>
        <div class="investigation-overview" aria-live="polite">
          <p class="kicker" id="investigationType">全部试点证据</p>
          <h3 id="investigationTitle"></h3>
          <p class="investigation-description" id="investigationDescription"></p>
          <div class="investigation-metrics" id="investigationMetrics"></div>
          <div class="phenomenon-row" id="phenomenonRow"></div>
          <p class="evidence-boundary">计数只描述当前 40 条分层试点中的证据覆盖，不代表市场发生率或订单占比。</p>
        </div>
        <div class="evidence-refine">
          <div class="evidence-toolbar">
            <select id="starFilter" aria-label="按星级筛选"><option value="all">星级：全部</option><option value="5">5 星</option><option value="4">4 星</option><option value="3">3 星</option><option value="2">2 星</option><option value="1">1 星</option></select>
            <select id="unitPolarityFilter" aria-label="按反馈点倾向筛选"><option value="all">反馈点倾向：全部</option><option value="正向">反馈点：正向</option><option value="负向">反馈点：负向</option><option value="正负混合">反馈点：正负混合</option><option value="中性">反馈点：中性</option></select>
          </div>
        </div>
        <div class="filter-summary"><div class="active-filters" id="activeFilters"></div><div><button class="clear-filters" id="clearFilters">清除收窄条件</button><span class="evidence-count" id="evidenceCount"></span></div></div>
        <div class="evidence-list" id="evidenceList"></div>
        <div class="pagination" id="evidencePagination"></div>
      </section>

      <section id="method">
        <div class="section-head">
          <div><p class="kicker">08 · 需要时再看</p><h2>方法与证据边界</h2></div>
          <p class="section-answer">这些说明不打断主阅读路径，但保留样本口径、字段覆盖和证据状态供审计。</p>
        </div>
        <div class="method-grid">
          <div class="prose" id="methodText"></div>
          <table class="coverage"><thead><tr><th>Review 层字段</th><th>有明确证据</th></tr></thead><tbody id="coverageBody"></tbody></table>
        </div>
      </section>
    </div>
    <footer class="footer"><div id="footerText"></div></footer>
  </main>
  <div class="drawer-backdrop" id="drawerBackdrop" role="dialog" aria-modal="true" aria-labelledby="drawerTitle" aria-hidden="true">
    <div class="drawer"><button class="drawer-close" id="drawerClose" aria-label="关闭">&times;</button><div id="drawerContent"></div></div>
  </div>
  <script id="report-data" type="application/json">__DATA__</script>
  <script>
    const data = JSON.parse(document.getElementById('report-data').textContent);
    const byId = (id) => document.getElementById(id);
    const escapeHtml = (value) => String(value ?? '').replace(/[&<>'"]/g, (char) => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));
    const inlineMarkup = (value) => escapeHtml(value).replace(/`([^`]+)`/g, '<code>$1</code>').replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    const reviewMap = new Map(data.evidence_reviews.map((review) => [review.data_row, review]));
    const actionMap = new Map(data.actions.map((action) => [action.id, action]));
    const findingMap = new Map(data.finding_to_action.map((finding) => [finding.id, finding]));
    const sectionMap = new Map(data.narrative.sections.map((section) => [section.id, section]));
    const taxonomyLabels = data.taxonomy.labels;
    const stateLabels = {actual:'实际场景', planned:'计划场景', estimated:'用户估计', reported:'转述证据'};
    const sceneKeys = {actual:'实际场景', planned:'计划场景', estimated:'用户估计', reported:'转述证据'};
    const evidenceFilterIds = ['starFilter','unitPolarityFilter'];
    const evidencePageSize = 8;
    let evidencePage = 1;
    let evidenceDimension = 'all';

    function renderBlocks(blocks) {
      return blocks.map((block) => {
        if (block.type === 'list') return `<ul>${block.items.map((item) => `<li>${inlineMarkup(item)}</li>`).join('')}</ul>`;
        if (block.type === 'quote') return `<blockquote>${inlineMarkup(block.text)}</blockquote>`;
        return `<p>${inlineMarkup(block.text)}</p>`;
      }).join('');
    }

    function renderStorySection(section) {
      return `<article class="story-section"><h2 class="story-title">${escapeHtml(section.title)}</h2><div class="prose">${renderBlocks(section.lead_blocks)}</div>${section.subsections.map((subsection) => {
        const coverage = subsection.coverage || {matched_reviews:subsection.review_rows.length, total_reviews:data.evidence_reviews.length, percentage:Math.round(subsection.review_rows.length / data.evidence_reviews.length * 100)};
        return `<div class="subsection"><h3>${escapeHtml(subsection.title)}</h3><div class="prose">${renderBlocks(subsection.blocks)}${subsection.review_rows.length ? `<div class="evidence-coverage">评论证据覆盖 <strong>${coverage.matched_reviews}/${coverage.total_reviews}（${coverage.percentage}%）</strong></div><button class="evidence-link" data-open-rows="${subsection.review_rows.join(',')}">查看 ${subsection.review_rows.length} 条关联评论证据</button>` : ''}</div></div>`;
      }).join('')}</article>`;
    }

    function renderNarrative(target, sectionIds) {
      byId(target).innerHTML = sectionIds.map((id) => renderStorySection(sectionMap.get(id))).join('');
    }

    function renderStates(states) {
      return `<div class="states">${Object.entries(states).filter(([, rows]) => rows.length).map(([state, rows]) => `<span class="state ${state}">${stateLabels[state]} ${rows.length}</span>`).join('')}</div>`;
    }

    function listText(value) {
      if (Array.isArray(value)) return value.join('；');
      if (value && typeof value === 'object') return JSON.stringify(value);
      return String(value ?? 'unknown');
    }

    function isUnknownValue(value) {
      if (value === null || value === undefined || value === '' || value === 'unknown') return true;
      return Array.isArray(value) && (!value.length || value.every((item) => item === 'unknown'));
    }

    function knownItems(value) {
      return (Array.isArray(value) ? value : [value]).filter((item) => item && item !== 'unknown');
    }

    function unknownFieldText(label) {
      const labels = {
        '消费者':'原文未提供可识别的消费者角色',
        '计划场景':'原文未提及未来使用计划',
        '用户估计':'原文未提及尚未实测的个人判断',
        '转述证据':'原文未引用他人或外部信息',
        '购买动机':'原文未明确说明购买动机',
        '期望结果':'原文未明确说明购买前期待',
        '未满足的需求':'原文未提供明确缺口证据',
        '决策结果':'原文未提及退货、换货、保留、推荐或复购等决定'
      };
      return labels[label] || '原文未明确提及';
    }

    function persistedInference(review, label, value) {
      if (!isUnknownValue(value)) return null;
      const inference = review.inferences?.[label];
      if (!inference || inference['处理结果'] !== '可谨慎推测') return null;
      const possible = knownItems(inference['可能推测']);
      const basis = knownItems(inference['依据']);
      if (!possible.length || !basis.length) return null;
      return {
        text: possible.join('；'),
        basis: basis.join('；'),
        boundary: inference['事实边界'] || '原文未明确说明'
      };
    }

    function renderReviewField(review, label, value, className = '') {
      const unknown = isUnknownValue(value);
      const inference = persistedInference(review, label, value);
      const inferenceMarkup = inference ? `<div class="field-inference"><b>谨慎推测 · 非事实</b><p>${escapeHtml(inference.text)}</p><p class="field-inference-meta"><b>依据：</b>${escapeHtml(inference.basis)}</p><p class="field-inference-meta"><b>事实边界：</b>${escapeHtml(inference.boundary)} 该推测不参与证据计数或主题统计。</p></div>` : '';
      return `<div class="field${className ? ` ${className}` : ''}"><b>${escapeHtml(label)}</b><p class="${unknown ? 'field-missing' : ''}">${escapeHtml(unknown ? unknownFieldText(label) : listText(value))}</p>${inferenceMarkup}</div>`;
    }

    function renderValueChains(valueChains) {
      if (!Array.isArray(valueChains) || !valueChains.length) return '<p class="field-missing">原文未提供可形成价值链的证据</p>';
      const display = (value) => isUnknownValue(value) ? '原文未明确提及' : value;
      return `<div class="value-chain-list">${valueChains.map((chain, index) => `<div class="value-chain-item"><b>链路 ${index + 1}</b><p>${escapeHtml(display(chain.产品特征或体验))} <span aria-hidden="true">→</span> ${escapeHtml(display(chain.用户任务结果))} <span aria-hidden="true">→</span> ${escapeHtml(display(chain.情绪关系社会价值))}</p><p class="value-chain-meta"><b>事实边界：</b>${escapeHtml(display(chain.事实边界))} · <b>证据强度：</b>${escapeHtml(display(chain.证据强度))}</p></div>`).join('')}</div>`;
    }

    function renderSummary() {
      byId('sideAsin').textContent = data.report.asin;
      byId('reportMeta').textContent = `${data.report.asin} · VOC 洞察结构试点`;
      byId('reportTitle').textContent = data.report.title;
      byId('reportSubtitle').textContent = data.report.subtitle;
      byId('scopeLabel').textContent = data.report.scope_label;
      byId('thesis').textContent = data.summary.thesis;
      byId('taskChain').innerHTML = data.summary.task_chain.map((step) => `<div class="task-step">${escapeHtml(step)}</div>`).join('');
      const coreBlocks = sectionMap.get('core').lead_blocks;
      byId('coreNarrative').innerHTML = renderBlocks([coreBlocks[1], coreBlocks[3]]);
      byId('metrics').innerHTML = data.summary.metrics.map((metric) => `<div class="metric"><strong>${metric.value}/${metric.denominator}</strong><span>${escapeHtml(metric.label)}</span></div>`).join('');
      byId('mixedNote').textContent = `${data.summary.mixed_experience_count}/40 条评论同时包含明确满意点和未满足需求。因此，报告不能把消费者机械拆成好评与差评两组。`;
      byId('footerText').textContent = `${data.report.asin} · 数据契约 ${data.contract.schema_version} · 生成日期 ${data.report.generated_on}`;
    }

    function renderBridge() {
      byId('bridgeList').innerHTML = data.finding_to_action.map((bridge) => `<article class="bridge"><div><span class="bridge-id">${bridge.id}</span><h3>${escapeHtml(bridge.finding)}</h3>${renderStates(bridge.evidence_by_state)}<button class="evidence-link" data-open-rows="${bridge.review_rows.join(',')}">查看 ${bridge.review_rows.length} 条关联证据</button></div><div><p><b>这意味着什么</b><br>${escapeHtml(bridge.meaning)}</p><p><b>业务影响</b><br>${escapeHtml(bridge.business_impact)}</p></div><div class="action-pills">${bridge.action_ids.map((actionId) => { const action = actionMap.get(actionId); return `<button class="action-pill" data-open-action-details="${actionId}" aria-haspopup="dialog"><b>${actionId}</b> ${escapeHtml(action.title)}</button>`; }).join('')}</div></article>`).join('');
    }

    function renderList(items) {
      return `<ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul>`;
    }

    function categoryActionDetails(action) {
      if (action.category === 'listing') return `<div class="decision-block action"><b>具体动作</b><p>${escapeHtml(action.recommendation)}</p></div><div class="decision-block"><b>上线前核验</b><p>${escapeHtml(action.release_gate)}</p></div>`;
      if (action.category === 'visual') return `<div class="decision-block action"><b>画面要完成的信息任务</b><p>${escapeHtml(action.information_job)}</p></div><div class="decision-block"><b>建议呈现</b><p>${escapeHtml(action.recommendation)}</p></div>`;
      return `<div class="decision-block action"><b>待验证问题</b><p>${escapeHtml(action.question)}</p></div><div class="decision-block"><b>最小验证方案</b><p>${escapeHtml(action.minimum_validation)}</p></div><div class="decision-block"><b>立项判断</b><p>${escapeHtml(action.decision_basis)}</p></div>`;
    }

    function actionDetails(action) {
      const refs = action.evidence_refs.map((ref) => `<button class="exact-ref" data-open-unit="${action.id}|${ref.review_row}|${escapeHtml(ref.unit_id)}">${escapeHtml(ref.unit_id)} · ${escapeHtml(ref.role)}</button>`).join('');
      return `<div class="decision-block current"><b>当前产品或页面状况</b><p>${escapeHtml(action.current_state)}</p></div><div class="decision-block evidence"><b>评论已经告诉我们的事实</b>${renderList(action.voc_facts)}</div><div class="decision-block"><b>仍然不知道什么</b>${renderList(action.unknowns)}</div><div class="decision-block"><b>为什么影响业务</b><p>${escapeHtml(action.business_impact)}</p></div>${categoryActionDetails(action)}<div class="decision-block wide"><b>验收标准</b>${renderList(action.acceptance_criteria)}</div><div class="decision-block wide evidence"><b>动作级精确证据</b><div>${refs}</div></div>`;
    }

    function renderActions(category = 'all') {
      document.querySelectorAll('[data-action-category]').forEach((button) => button.classList.toggle('active', button.dataset.actionCategory === category));
      const actions = category === 'all' ? data.actions : data.actions.filter((action) => action.category === category);
      byId('actionCount').textContent = `${actions.length} 项动作`;
      byId('actionList').innerHTML = actions.map((action) => `<article class="action-card" id="action-${action.id}"><div class="action-head"><span class="action-id">${action.id}</span><h3>${escapeHtml(action.title)}</h3><span class="priority">${escapeHtml(action.priority)}</span></div><div class="action-meta">${action.target_surfaces.map((surface) => `<span class="meta-chip">${escapeHtml(surface)}</span>`).join('')}<span class="meta-chip">${escapeHtml(action.workflow_status)}</span><span class="meta-chip">来自 ${action.source_finding_ids.join('、')}</span></div><p class="action-state"><b>当前状况：</b>${escapeHtml(action.current_state)}</p><button class="evidence-link" data-open-action-evidence="${action.id}">查看 ${action.source_review_rows.length} 条动作证据（精确到反馈点）</button><details><summary>查看完整决策链</summary><div class="action-detail">${actionDetails(action)}</div></details></article>`).join('');
    }

    function sceneField(review) {
      const fields = Object.entries(sceneKeys).map(([, key]) => renderReviewField(review, key, review.scenes[key])).join('');
      return `<div class="scene-field-group"><b class="scene-field-title">使用场景</b><div class="scene-fields">${fields}</div></div>`;
    }

    function facetHas(review, key, value) {
      return value === 'all' || review.facets[key].includes(value);
    }

    function investigationContext() {
      const value = byId('investigationContext').value || 'all';
      if (value === 'all') return {kind:'all', id:'all', type:'全部试点证据', title:'这 40 条评论整体在说什么', description:'先从全部试点证据浏览，也可以从上方选择一条洞察、业务动作或主题，直接进入对应证据集合。'};
      const [kind, id] = value.split(':');
      if (kind === 'action') {
        const action = actionMap.get(id);
        return {kind, id, type:`业务动作 ${id}`, title:action.title, description:action.current_state, action};
      }
      if (kind === 'finding') {
        const finding = findingMap.get(id);
        return {kind, id, type:`洞察 ${id}`, title:finding.finding, description:finding.meaning, finding};
      }
      return {kind, id, type:kind === 'user-theme' ? '消费者与场景主题' : '产品体验主题', title:taxonomyLabels[id], description:`当前试点中，以下 Review 被编码到“${taxonomyLabels[id]}”主题。数量说明证据覆盖，不等于市场占比。`};
    }

    function matchesInvestigation(review, context) {
      if (context.kind === 'all') return true;
      if (context.kind === 'action') return review.facets.action_ids.includes(context.id);
      if (context.kind === 'finding') return review.facets.finding_ids.includes(context.id);
      if (context.kind === 'user-theme') return review.facets.user_theme_ids.includes(context.id);
      return review.facets.product_theme_ids.includes(context.id);
    }

    function investigationUnits(review, context) {
      if (context.kind !== 'action') return review.units.map((unit) => ({unit, role:null}));
      return context.action.evidence_refs.filter((ref) => ref.review_row === review.data_row).map((ref) => ({unit:review.units.find((unit) => unit.unit_id === ref.unit_id), role:ref.role})).filter((item) => item.unit);
    }

    function filteredInvestigationUnits(review, context) {
      const units = investigationUnits(review, context);
      return evidenceDimension === 'all' ? units : units.filter(({unit}) => unit.dimensions.includes(evidenceDimension));
    }

    function renderActiveFilters() {
      const chips = evidenceFilterIds.filter((id) => byId(id).value !== 'all').map((id) => `<span class="filter-chip">${escapeHtml(byId(id).selectedOptions[0].textContent)}</span>`);
      if (evidenceDimension !== 'all') chips.push(`<span class="filter-chip">具体问题：${escapeHtml(evidenceDimension)}</span>`);
      byId('activeFilters').innerHTML = chips.length ? chips.join('') : '<span class="evidence-count">未增加收窄条件</span>';
    }

    function renderInvestigationOverview(reviews, context, contextReviews) {
      const dimensionRows = new Map();
      let unitCount = 0;
      reviews.forEach((review) => filteredInvestigationUnits(review, context).forEach(() => { unitCount += 1; }));
      contextReviews.forEach((review) => investigationUnits(review, context).forEach(({unit}) => {
        unit.dimensions.forEach((dimension) => {
          if (!dimensionRows.has(dimension)) dimensionRows.set(dimension, new Set());
          dimensionRows.get(dimension).add(review.data_row);
        });
      }));
      const dimensions = [...dimensionRows.entries()].sort((a, b) => b[1].size - a[1].size || a[0].localeCompare(b[0])).slice(0, 6);
      const metrics = [
        [reviews.length, '匹配的独立 Review'],
        [unitCount, context.kind === 'action' ? '动作级精确反馈点' : '这些 Review 内的反馈点'],
        [reviews.filter((review) => review.stars <= 2).length, '1–2 星 Review'],
        [reviews.filter((review) => review.evidence_strength.等级 === '高').length, '高强度证据 Review'],
      ];
      byId('investigationType').textContent = context.type;
      byId('investigationTitle').textContent = context.title;
      byId('investigationDescription').textContent = context.description;
      byId('investigationMetrics').innerHTML = metrics.map(([value, label]) => `<div class="investigation-metric"><strong>${value}</strong><span>${label}</span></div>`).join('');
      byId('phenomenonRow').innerHTML = dimensions.length ? `<b>证据涉及的具体问题</b>${dimensions.map(([dimension, rows]) => `<button class="phenomenon-chip" type="button" data-evidence-dimension="${escapeHtml(dimension)}" aria-pressed="${evidenceDimension === dimension}">${escapeHtml(dimension)} · ${rows.size} 条</button>`).join('')}` : '<span class="evidence-count">当前范围内没有可汇总的反馈点。</span>';
    }

    function renderEvidenceCard(review, context) {
      const relevantUnits = filteredInvestigationUnits(review, context);
      const excerpts = relevantUnits.slice(0, 2);
      const quoteHtml = excerpts.length ? excerpts.map(({unit, role}) => `<div><p><b>${role ? `${escapeHtml(role)}：` : ''}${escapeHtml(unit.fact_zh)}</b></p><blockquote lang="en">“${escapeHtml(unit.quote_en)}”</blockquote></div>`).join('') : `<blockquote lang="en">“${escapeHtml(review.review_en || '原文为空')}”</blockquote>`;
      return `<article class="evidence-card" data-review-row="${review.data_row}"><div class="evidence-summary"><span class="stars">${review.stars} 星</span><span class="evidence-title"><strong>${escapeHtml(review.title_zh || review.title_en)}</strong><span>数据行 ${review.data_row} · ${escapeHtml(review.date)} · ${escapeHtml(review.consumer)}</span></span><span class="sentiment">${escapeHtml(review.sentiment)}</span></div><div class="evidence-excerpt">${quoteHtml}</div><div class="evidence-card-actions"><button class="evidence-link" data-open-review-detail="${review.data_row}" aria-haspopup="dialog">查看完整评论与编码</button>${relevantUnits.length > 2 ? `<span class="evidence-count">另有 ${relevantUnits.length - 2} 个相关反馈点</span>` : ''}</div></article>`;
    }

    function renderPagination(totalPages) {
      byId('evidencePagination').innerHTML = totalPages > 1 ? `<button data-evidence-page="${evidencePage - 1}" ${evidencePage === 1 ? 'disabled' : ''}>上一页</button><span>第 ${evidencePage} / ${totalPages} 页</span><button data-evidence-page="${evidencePage + 1}" ${evidencePage === totalPages ? 'disabled' : ''}>下一页</button>` : '';
    }

    function renderEvidence(resetPage = false) {
      if (resetPage) evidencePage = 1;
      const context = investigationContext();
      const stars = byId('starFilter').value;
      const unitPolarity = byId('unitPolarityFilter').value;
      const contextReviews = data.evidence_reviews.filter((review) => matchesInvestigation(review, context));
      const reviews = contextReviews.filter((review) => (stars === 'all' || String(review.stars) === stars) && facetHas(review, 'unit_polarities', unitPolarity) && (evidenceDimension === 'all' || investigationUnits(review, context).some(({unit}) => unit.dimensions.includes(evidenceDimension))));
      const totalPages = Math.max(1, Math.ceil(reviews.length / evidencePageSize));
      evidencePage = Math.min(evidencePage, totalPages);
      const visibleReviews = reviews.slice((evidencePage - 1) * evidencePageSize, evidencePage * evidencePageSize);
      byId('evidenceCount').textContent = `${reviews.length} 条 Review${reviews.length > evidencePageSize ? ` · 当前第 ${evidencePage} 页` : ''}`;
      renderActiveFilters();
      renderInvestigationOverview(reviews, context, contextReviews);
      byId('evidenceList').innerHTML = visibleReviews.length ? visibleReviews.map((review) => renderEvidenceCard(review, context)).join('') : '<div class="empty">当前调查范围内没有符合这些收窄条件的证据。</div>';
      renderPagination(totalPages);
    }

    function renderMethod() {
      const source = sectionMap.get('methodology-source');
      byId('methodText').innerHTML = `<p><b>样本口径：</b>${escapeHtml(data.methodology.sample)}</p><p><b>计数解释：</b>${escapeHtml(data.methodology.quantification_rule)}</p>${renderBlocks(source.lead_blocks)}<h3>事实边界</h3><ul>${data.methodology.boundaries.map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul>`;
      byId('coverageBody').innerHTML = data.methodology.field_coverage.map((item) => `<tr><td>${escapeHtml(item.field)}</td><td>${item.known}/${item.denominator}</td></tr>`).join('');
    }

    let modalContext = null;
    let modalTrigger = null;

    function showModal(markup) {
      const backdrop = byId('drawerBackdrop');
      if (!backdrop.classList.contains('open')) modalTrigger = document.activeElement;
      byId('drawerContent').innerHTML = markup;
      backdrop.classList.add('open');
      backdrop.setAttribute('aria-hidden', 'false');
      backdrop.querySelector('.drawer').scrollTop = 0;
      document.body.style.overflow = 'hidden';
      byId('drawerClose').focus();
    }

    function closeDrawer() {
      const backdrop = byId('drawerBackdrop');
      if (!backdrop.classList.contains('open')) return;
      backdrop.classList.remove('open');
      backdrop.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
      if (modalTrigger && typeof modalTrigger.focus === 'function') modalTrigger.focus();
      modalTrigger = null;
      modalContext = null;
    }

    function modalBackButton() {
      return modalContext ? '<button class="modal-back" data-modal-back>返回上一级证据</button>' : '';
    }

    function modalReviewFields(review) {
      return `<div class="review-fields">${renderReviewField(review, '消费者', review.consumer)}${sceneField(review)}${renderReviewField(review, '用户任务', review.tasks)}${renderReviewField(review, '购买动机', review.motivations)}${renderReviewField(review, '期望结果', review.expectations)}${renderReviewField(review, '实际结果', review.outcomes)}${renderReviewField(review, '满意点', review.satisfiers)}<div class="field value-chain-field"><b>价值链</b>${renderValueChains(review.value_chains)}</div>${renderReviewField(review, '未满足的需求', review.unmet_needs)}<div class="field"><b>证据强度</b><p>${escapeHtml(review.evidence_strength.等级)} · ${escapeHtml(review.evidence_strength.说明)}</p></div>${renderReviewField(review, '总体极性', review.sentiment)}${renderReviewField(review, '决策结果', review.decision)}</div>`;
    }

    function modalUnit(review, unit, ref = null) {
      return `<div class="unit${ref ? ' evidence-match' : ''}" data-modal-unit-id="${escapeHtml(unit.unit_id)}"><span class="unit-id">${escapeHtml(unit.unit_id)}</span>${ref ? `<span class="evidence-role">${escapeHtml(ref.role)}</span>` : ''} · ${escapeHtml(unit.polarity)} · ${escapeHtml(unit.dimensions.join(' / '))}<p>${escapeHtml(unit.quote_en)}</p><p><b>事实判断：</b>${escapeHtml(unit.fact_zh)}</p></div>`;
    }

    function openReviewListModal(rows, title = '关联评论证据') {
      modalContext = {kind:'reviews', rows:rows.map(Number), title};
      renderReviewListModal();
    }

    function renderReviewListModal() {
      const reviews = modalContext.rows.map((row) => reviewMap.get(row)).filter(Boolean);
      showModal(`<h2 id="drawerTitle">${escapeHtml(modalContext.title)}</h2><p class="modal-lead">这里只列出当前 40 条试点中的关联 Review；计数不代表市场发生率。</p>${reviews.length ? reviews.map((review) => `<article class="drawer-review"><strong>${review.stars} 星 · 数据行 ${review.data_row} · ${escapeHtml(review.title_zh || review.title_en)}</strong><p>${escapeHtml(review.review_zh || review.review_en || '原文为空')}</p><button class="evidence-link" data-open-review-detail="${review.data_row}">查看完整编码</button></article>`).join('') : '<div class="empty">没有属于当前试点的关联 Review。</div>'}`);
    }

    function actionRefsForReview(reviewRow) {
      if (!modalContext || !modalContext.actionId) return [];
      return actionMap.get(modalContext.actionId).evidence_refs.filter((ref) => ref.review_row === reviewRow);
    }

    function openReviewDetail(row) {
      const review = reviewMap.get(Number(row));
      if (!review) return;
      const refs = actionRefsForReview(review.data_row);
      const refMap = new Map(refs.map((ref) => [ref.unit_id, ref]));
      showModal(`${modalBackButton()}<h2 id="drawerTitle">Review 完整编码</h2><p class="modal-review-meta">${review.stars} 星 · 数据行 ${review.data_row} · ${escapeHtml(review.date)}</p><div class="quote-pair"><div><p><b>中文标题</b><br>${escapeHtml(review.title_zh || '原文为空')}</p><p class="source-body"><b>中文正文</b><br>${escapeHtml(review.review_zh || '原文为空')}</p></div><div><p><b>英文标题</b><br>${escapeHtml(review.title_en || '原文为空')}</p><p class="source-body"><b>英文正文</b><br>${escapeHtml(review.review_en || '原文为空')}</p></div></div>${modalReviewFields(review)}<div class="units"><h3>${review.units.length} 个反馈点</h3>${review.units.map((unit) => modalUnit(review, unit, refMap.get(unit.unit_id))).join('')}</div>`);
    }

    function openActionEvidence(actionId) {
      modalContext = {kind:'action', actionId};
      renderActionEvidenceModal();
    }

    function openActionDetails(actionId) {
      modalContext = {kind:'action-details', actionId};
      renderActionDetailsModal();
    }

    function renderActionDetailsModal() {
      const action = actionMap.get(modalContext.actionId);
      showModal(`<h2 id="drawerTitle">${action.id} · ${escapeHtml(action.title)}</h2><div class="action-meta">${action.target_surfaces.map((surface) => `<span class="meta-chip">${escapeHtml(surface)}</span>`).join('')}<span class="meta-chip">${escapeHtml(action.priority)}</span><span class="meta-chip">${escapeHtml(action.workflow_status)}</span></div><p class="modal-lead">这是当前发现关联的完整业务动作。你可以继续查看决策链或下钻到精确反馈点。</p><div class="action-detail">${actionDetails(action)}</div><button class="evidence-link" data-open-action-evidence="${action.id}">查看 ${action.source_review_rows.length} 条动作证据（精确到反馈点）</button>`);
    }

    function renderActionEvidenceModal() {
      const action = actionMap.get(modalContext.actionId);
      const refsByReview = new Map();
      action.evidence_refs.forEach((ref) => {
        if (!refsByReview.has(ref.review_row)) refsByReview.set(ref.review_row, []);
        refsByReview.get(ref.review_row).push(ref);
      });
      const reviews = [...refsByReview.entries()].map(([row, refs]) => ({review:reviewMap.get(row), refs})).filter((item) => item.review);
      showModal(`<h2 id="drawerTitle">${action.id} · ${escapeHtml(action.title)}</h2><p class="modal-lead">${reviews.length} 条 Review · ${action.evidence_refs.length} 个精确反馈点</p><div class="modal-action-state"><b>当前状况</b><p>${escapeHtml(action.current_state)}</p></div><div class="modal-unit-list">${reviews.map(({review, refs}) => `<article class="drawer-review"><strong>${review.stars} 星 · 数据行 ${review.data_row} · ${escapeHtml(review.title_zh || review.title_en)}</strong><p>${escapeHtml(review.review_zh || review.review_en || '原文为空')}</p>${refs.map((ref) => { const unit = review.units.find((item) => item.unit_id === ref.unit_id); return unit ? modalUnit(review, unit, ref) : ''; }).join('')}<button class="evidence-link" data-open-review-detail="${review.data_row}">查看该 Review 完整编码</button></article>`).join('')}</div>`);
    }

    function openUnitEvidence(value) {
      const [actionId, row, unitId] = value.split('|');
      const action = actionMap.get(actionId);
      const review = reviewMap.get(Number(row));
      const ref = action && action.evidence_refs.find((item) => item.review_row === Number(row) && item.unit_id === unitId);
      const unit = review && review.units.find((item) => item.unit_id === unitId);
      if (!action || !review || !ref || !unit) return;
      if (!modalContext || modalContext.kind !== 'action-details' || modalContext.actionId !== actionId) modalContext = {kind:'action', actionId};
      showModal(`${modalBackButton()}<h2 id="drawerTitle">${action.id} · 精确反馈点</h2><p class="modal-review-meta">${review.stars} 星 · 数据行 ${review.data_row} · ${escapeHtml(review.title_zh || review.title_en)}</p><div class="modal-action-state"><b>支持的动作</b><p>${escapeHtml(action.title)}</p><p>${escapeHtml(action.current_state)}</p></div><div class="modal-unit-list">${modalUnit(review, unit, ref)}</div><button class="evidence-link" data-open-review-detail="${review.data_row}">查看该 Review 完整编码</button>`);
    }

    function returnToModalContext() {
      if (modalContext.kind === 'reviews') renderReviewListModal();
      if (modalContext.kind === 'action') renderActionEvidenceModal();
      if (modalContext.kind === 'action-details') renderActionDetailsModal();
    }

    function clearEvidenceFilters(shouldRender = true) {
      evidenceFilterIds.forEach((id) => { byId(id).value = 'all'; });
      evidenceDimension = 'all';
      if (shouldRender) renderEvidence(true);
    }

    function wireEvents() {
      document.addEventListener('click', (event) => {
        const rowsButton = event.target.closest('[data-open-rows]');
        if (rowsButton) openReviewListModal(rowsButton.dataset.openRows.split(',').filter(Boolean));
        const actionEvidenceButton = event.target.closest('[data-open-action-evidence]');
        if (actionEvidenceButton) openActionEvidence(actionEvidenceButton.dataset.openActionEvidence);
        const actionDetailsButton = event.target.closest('[data-open-action-details]');
        if (actionDetailsButton) openActionDetails(actionDetailsButton.dataset.openActionDetails);
        const reviewDetailButton = event.target.closest('[data-open-review-detail]');
        if (reviewDetailButton) openReviewDetail(reviewDetailButton.dataset.openReviewDetail);
        const modalBack = event.target.closest('[data-modal-back]');
        if (modalBack) returnToModalContext();
        const unitButton = event.target.closest('[data-open-unit]');
        if (unitButton) openUnitEvidence(unitButton.dataset.openUnit);
        const dimensionButton = event.target.closest('[data-evidence-dimension]');
        if (dimensionButton) {
          evidenceDimension = evidenceDimension === dimensionButton.dataset.evidenceDimension ? 'all' : dimensionButton.dataset.evidenceDimension;
          renderEvidence(true);
        }
        const pageButton = event.target.closest('[data-evidence-page]');
        if (pageButton && !pageButton.disabled) {
          evidencePage = Number(pageButton.dataset.evidencePage);
          renderEvidence();
          byId('evidenceList').scrollIntoView({behavior:'smooth', block:'start'});
        }
      });
      document.querySelectorAll('[data-action-category]').forEach((button) => button.addEventListener('click', () => renderActions(button.dataset.actionCategory)));
      byId('investigationContext').addEventListener('change', () => { clearEvidenceFilters(false); renderEvidence(true); });
      evidenceFilterIds.forEach((id) => byId(id).addEventListener('change', () => renderEvidence(true)));
      byId('clearFilters').addEventListener('click', () => clearEvidenceFilters());
      byId('drawerClose').addEventListener('click', closeDrawer);
      byId('drawerBackdrop').addEventListener('click', (event) => { if (event.target === byId('drawerBackdrop')) closeDrawer(); });
      document.addEventListener('keydown', (event) => { if (event.key === 'Escape') closeDrawer(); });
      const observer = new IntersectionObserver((entries) => entries.forEach((entry) => { if (entry.isIntersecting) document.querySelectorAll('.nav a').forEach((link) => link.classList.toggle('active', link.hash === `#${entry.target.id}`)); }), {rootMargin:'-35% 0px -55% 0px'});
      document.querySelectorAll('main section').forEach((section) => observer.observe(section));
    }

    function renderInvestigationOptions() {
      const findings = data.finding_to_action.map((finding) => `<option value="finding:${finding.id}">${finding.id} · ${escapeHtml(finding.finding)}</option>`).join('');
      const actions = data.actions.map((action) => `<option value="action:${action.id}">${action.id} · ${escapeHtml(action.title)}</option>`).join('');
      const userThemes = Object.entries(taxonomyLabels).filter(([id]) => id.startsWith('UT-')).map(([id, label]) => `<option value="user-theme:${id}">${id} · ${escapeHtml(label)}</option>`).join('');
      const productThemes = Object.entries(taxonomyLabels).filter(([id]) => id.startsWith('PT-')).map(([id, label]) => `<option value="product-theme:${id}">${id} · ${escapeHtml(label)}</option>`).join('');
      byId('investigationContext').innerHTML = `<option value="all">全部试点证据</option><optgroup label="验证一条洞察">${findings}</optgroup><optgroup label="追溯一项业务动作">${actions}</optgroup><optgroup label="探索消费者、场景与任务">${userThemes}</optgroup><optgroup label="探索产品体验问题">${productThemes}</optgroup>`;
      byId('investigationContext').value = 'action:P-01';
    }

    function init() {
      renderSummary();
      renderNarrative('peopleNarrative', ['audience', 'contexts']);
      renderNarrative('expectationNarrative', ['motivation', 'expectations']);
      renderNarrative('valueNarrative', ['value-formation', 'value-interruption', 'unmet-and-decisions']);
      renderBridge();
      renderActions();
      renderInvestigationOptions();
      renderEvidence();
      renderMethod();
      wireEvents();
    }
    init();
  </script>
</body>
</html>
'''


if __name__ == "__main__":
    main()
