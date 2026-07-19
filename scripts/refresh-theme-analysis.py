#!/usr/bin/env python3
"""Refresh fixed theme memberships and aggregates after Review coding changes."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_DIR = ROOT / "data-pilot" / "B0CR1R7FKP" / "analysis" / "2026-07-18"
SOURCE_DIR = ROOT / "data-pilot" / "B0CR1R7FKP" / "source-exports" / "2026-07-18"
DEFAULT_04 = SOURCE_DIR / "04_merged-reviews.jsonl"
DEFAULT_08 = ANALYSIS_DIR / "08_full-review-coding.jsonl"
DEFAULT_12 = ANALYSIS_DIR / "12_full-theme-analysis.json"
DEFAULT_ASSIGNMENTS = Path.home() / "AppData" / "Local" / "Temp" / "amz-review-insight-full-audit"

UNKNOWN = "unknown"
SCENE_FIELDS = ["实际场景", "计划场景", "用户估计", "转述证据"]
UT_LIST_FIELDS = [
    "消费者",
    "用户任务",
    "购买动机",
    "期望结果",
    "实际结果",
    "满意点",
    "价值链",
    "未满足的需求",
    "决策结果",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_04)
    parser.add_argument("--coding", type=Path, default=DEFAULT_08)
    parser.add_argument("--template", type=Path, default=DEFAULT_12)
    parser.add_argument("--assignments", type=Path, default=DEFAULT_ASSIGNMENTS)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def load_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def known(value) -> bool:
    if value is None or value == UNKNOWN:
        return False
    if isinstance(value, list):
        return any(known(item) for item in value)
    if isinstance(value, dict):
        return any(known(item) for item in value.values())
    return True


def flatten(value):
    if isinstance(value, list):
        for item in value:
            yield from flatten(item)
    elif known(value):
        yield value


def unique_top(values, limit: int = 30) -> list:
    items = list(values)
    if not items:
        return []
    serialised = [json.dumps(item, ensure_ascii=False, sort_keys=True) for item in items]
    counts = Counter(serialised)
    first = {value: index for index, value in enumerate(serialised)}
    ordered = sorted(counts, key=lambda value: (-counts[value], first[value]))
    return [json.loads(value) for value in ordered[:limit]]


def distribution(values, preferred: list[str]) -> dict[str, int]:
    counts = Counter(str(value) for value in values)
    result = {key: counts.pop(key, 0) for key in preferred}
    result.update({key: counts[key] for key in sorted(counts)})
    return result


def read_assignments(directory: Path, prefix: str) -> list[dict]:
    rows = []
    for batch in range(1, 9):
        path = directory / f"{prefix}-{batch:02d}.jsonl"
        if not path.is_file():
            raise ValueError(f"缺少归类文件：{path}")
        rows.extend(load_jsonl(path))
    return rows


def validate_assignments(coding: list[dict], pt_rows: list[dict], ut_rows: list[dict], themes: dict) -> None:
    expected_units = [unit["unit_id"] for review in coding for unit in review["反馈点"]]
    actual_units = [row["unit_id"] for row in pt_rows]
    if len(actual_units) != len(set(actual_units)) or set(actual_units) != set(expected_units):
        missing = sorted(set(expected_units) - set(actual_units))
        extra = sorted(set(actual_units) - set(expected_units))
        raise ValueError(f"产品主题覆盖失败：missing={missing[:5]} extra={extra[:5]}")
    legal_pt = {item["主题ID"] for item in themes["产品体验主题"]}
    if any(row.get("theme_id") not in legal_pt for row in pt_rows):
        raise ValueError("产品主题归类含非法 theme_id")

    actual_review_rows = [row["row"] for row in ut_rows]
    if sorted(actual_review_rows) != list(range(1, len(coding) + 1)):
        raise ValueError("用户主题归类未恰好覆盖全部 Review")
    legal_ut = {item["主题ID"] for item in themes["用户主题"]}
    if any(not set(row.get("theme_ids", [])).issubset(legal_ut) for row in ut_rows):
        raise ValueError("用户主题归类含非法 theme_id")


def aggregate_review_fields(rows: list[int], coding_by_row: dict[int, dict]) -> dict:
    layers = [coding_by_row[row]["Review层编码"] for row in rows]
    result = {}
    for field in UT_LIST_FIELDS:
        result[field] = unique_top(
            item
            for layer in layers
            for item in flatten(layer[field])
        )
    result["使用场景"] = {
        state: unique_top(
            item
            for layer in layers
            for item in flatten(layer["使用场景"][state])
        )
        for state in SCENE_FIELDS
    }
    return result


def review_distributions(rows: list[int], coding_by_row: dict[int, dict], source_by_row: dict[int, dict]) -> dict:
    return {
        "星级分布": distribution((source_by_row[row]["评星"] for row in rows), ["1", "2", "3", "4", "5"]),
        "年份分布": distribution((source_by_row[row]["评论日期"][:4] for row in rows), []),
        "总体极性分布": distribution(
            (coding_by_row[row]["Review层编码"]["总体极性"] for row in rows),
            ["正向", "正向为主", "正负混合", "负向", "负向为主"],
        ),
        "证据强度分布": distribution(
            (coding_by_row[row]["Review层编码"]["证据强度"]["等级"] for row in rows),
            ["高", "中", "低"],
        ),
    }


def refresh_user_themes(themes: dict, ut_rows: list[dict], coding_by_row: dict[int, dict], source_by_row: dict[int, dict]) -> None:
    members = {item["主题ID"]: [] for item in themes["用户主题"]}
    for row in ut_rows:
        for theme_id in row["theme_ids"]:
            members[theme_id].append(row["row"])
    for theme in themes["用户主题"]:
        rows = sorted(members[theme["主题ID"]])
        fields = aggregate_review_fields(rows, coding_by_row)
        theme.update({
            "涉及Review数": len(rows),
            "Review编码序号": rows,
            "数据行": rows,
            **fields,
            **review_distributions(rows, coding_by_row, source_by_row),
        })
    covered = set().union(*(set(rows) for rows in members.values()))
    themes["未进入用户主题的Review编码序号"] = sorted(set(coding_by_row) - covered)


def select_representative_units(units: list[dict], limit: int = 8) -> list[dict]:
    polarity_order = ["负向", "正向", "正负混合", "中性"]
    selected = []
    for polarity in polarity_order:
        match = next((unit for unit in units if unit["极性"] == polarity and unit not in selected), None)
        if match:
            selected.append(match)
    selected.extend(unit for unit in units if unit not in selected)
    return selected[:limit]


def refresh_product_themes(themes: dict, pt_rows: list[dict], coding_by_row: dict[int, dict], source_by_row: dict[int, dict]) -> dict[str, str]:
    unit_index = {
        unit["unit_id"]: (row, unit)
        for row, review in coding_by_row.items()
        for unit in review["反馈点"]
    }
    members = {item["主题ID"]: [] for item in themes["产品体验主题"]}
    unit_to_theme = {}
    for assignment in pt_rows:
        members[assignment["theme_id"]].append(assignment["unit_id"])
        unit_to_theme[assignment["unit_id"]] = assignment["theme_id"]
    for theme in themes["产品体验主题"]:
        unit_ids = members[theme["主题ID"]]
        pairs = [unit_index[unit_id] for unit_id in unit_ids]
        rows = sorted({row for row, _ in pairs})
        units = [unit for _, unit in pairs]
        representatives = select_representative_units(units)
        theme.update({
            "涉及Review数": len(rows),
            "反馈点数": len(unit_ids),
            "Review编码序号": rows,
            "数据行": rows,
            "unit_id": unit_ids,
            "星级分布": distribution((source_by_row[row]["评星"] for row in rows), ["1", "2", "3", "4", "5"]),
            "年份分布": distribution((source_by_row[row]["评论日期"][:4] for row in rows), []),
            "反馈点极性分布": distribution((unit["极性"] for unit in units), ["中性", "正向", "正负混合", "负向"]),
            "主要满意点": unique_top(item for unit in units for item in flatten(unit["满意点"])),
            "主要问题": unique_top(item for unit in units for item in flatten(unit["问题"])),
            "主要未满足需求": unique_top(item for unit in units for item in flatten(unit["未满足的需求"])),
            "代表性证据": [
                {
                    "编码序号": unit_index[unit["unit_id"]][0],
                    "数据行": unit_index[unit["unit_id"]][0],
                    "unit_id": unit["unit_id"],
                    "极性": unit["极性"],
                    "证据原文": unit["证据原文"],
                    "事实判断": unit["事实判断"],
                }
                for unit in representatives
            ],
        })
    return unit_to_theme


def refresh_opportunity_chains(themes: dict, coding_by_row: dict[int, dict], unit_to_theme: dict[str, str]) -> None:
    user_by_id = {item["主题ID"]: item for item in themes["用户主题"]}
    pt_id_by_name = {item["主题名称"]: item["主题ID"] for item in themes["产品体验主题"]}
    for chain in themes["用户机会链"]:
        source_theme = user_by_id[chain["来源用户主题ID"]]
        rows = source_theme["Review编码序号"]
        allowed_pt = {pt_id_by_name[name] for name in chain["关键产品体验主题"]}
        related_units = [
            unit["unit_id"]
            for row in rows
            for unit in coding_by_row[row]["反馈点"]
            if unit_to_theme[unit["unit_id"]] in allowed_pt
        ]
        related_unit_ids = set(related_units)
        related = [
            unit
            for row in rows
            for unit in coding_by_row[row]["反馈点"]
            if unit["unit_id"] in related_unit_ids
        ]
        layers = [coding_by_row[row]["Review层编码"] for row in rows]
        outcomes_and_values = [
            item
            for layer in layers
            for field in ["实际结果", "满意点"]
            for item in flatten(layer[field])
        ]
        outcomes_and_values.extend(
            item
            for layer in layers
            for value_chain in flatten(layer["价值链"])
            if isinstance(value_chain, dict)
            for field in ["用户任务结果", "情绪关系社会价值"]
            for item in flatten(value_chain.get(field, []))
        )
        chain.update({
            "涉及Review数": len(rows),
            "Review编码序号": rows,
            "数据行": rows,
            "消费者与关系": source_theme["消费者"],
            "场景": {state: source_theme["使用场景"][state] for state in ["实际场景", "计划场景"]},
            "用户任务": source_theme["用户任务"],
            "期望结果": source_theme["期望结果"],
            "实际结果与价值": unique_top(outcomes_and_values),
            "主要阻碍": unique_top(item for unit in related for item in flatten(unit["问题"])),
            "未满足需求": unique_top(item for unit in related for item in flatten(unit["未满足的需求"])),
            "关联unit_id": related_units,
        })


def validate_output(themes: dict, coding: list[dict]) -> None:
    expected_units = [unit["unit_id"] for review in coding for unit in review["反馈点"]]
    actual_units = [unit_id for theme in themes["产品体验主题"] for unit_id in theme["unit_id"]]
    if len(actual_units) != len(expected_units) or len(actual_units) != len(set(actual_units)) or set(actual_units) != set(expected_units):
        raise ValueError("候选 12 的产品主题反馈点覆盖失败")
    review_rows = set(range(1, len(coding) + 1))
    covered = {row for theme in themes["用户主题"] for row in theme["Review编码序号"]}
    unthemed = set(themes["未进入用户主题的Review编码序号"])
    if covered | unthemed != review_rows or covered & unthemed:
        raise ValueError("候选 12 的用户主题覆盖失败")
    for chain in themes["用户机会链"]:
        rows = set(chain["Review编码序号"])
        for unit_id in chain["关联unit_id"]:
            row = int(unit_id[1:4])
            if row not in rows or unit_id not in set(expected_units):
                raise ValueError(f"机会链关联无效：{chain['机会链ID']} {unit_id}")


def main() -> int:
    args = parse_args()
    source = load_jsonl(args.source)
    coding = load_jsonl(args.coding)
    themes = json.loads(args.template.read_text(encoding="utf-8"))
    if len(source) != 559 or len(coding) != 559:
        raise ValueError("04 与 08 必须各有 559 条")
    source_by_row = {index: review for index, review in enumerate(source, 1)}
    coding_by_row = {review["编码序号"]: review for review in coding}
    pt_rows = read_assignments(args.assignments, "theme-classification")
    ut_rows = read_assignments(args.assignments, "user-theme-classification")
    validate_assignments(coding, pt_rows, ut_rows, themes)

    refresh_user_themes(themes, ut_rows, coding_by_row, source_by_row)
    unit_to_theme = refresh_product_themes(themes, pt_rows, coding_by_row, source_by_row)
    refresh_opportunity_chains(themes, coding_by_row, unit_to_theme)

    feedback_count = sum(len(review["反馈点"]) for review in coding)
    themes["输入"]["正式编码文件SHA256"] = sha256(args.coding)
    themes["输入"]["Review数"] = len(coding)
    themes["输入"]["反馈点数"] = feedback_count
    themes["全量校验"] = {
        "Review总数": len(coding),
        "反馈点总数": feedback_count,
        "已分配主产品主题反馈点数": feedback_count,
        "产品主题unit_id唯一数": feedback_count,
        "用户主题覆盖Review数": len(coding) - len(themes["未进入用户主题的Review编码序号"]),
        "未进入用户主题Review数": len(themes["未进入用户主题的Review编码序号"]),
        "实际场景与计划场景分开保存": True,
        "用户估计与转述证据未并入实际场景": True,
        "质量复核状态": "全量语义复核、固定主题重映射与机械全检通过",
    }
    validate_output(themes, coding)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(themes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(args.output),
        "reviews": len(coding),
        "feedback_units": feedback_count,
        "unthemed_reviews": len(themes["未进入用户主题的Review编码序号"]),
        "coding_sha256": themes["输入"]["正式编码文件SHA256"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
