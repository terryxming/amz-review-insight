import argparse
import copy
import hashlib
import json
import re
from pathlib import Path


SOURCE_SHA256 = "6dd60229bdcfbb35165e521bfeceb3511488b99a908f209bb11ff55a120e820a"
SOURCE_FIELDS = [
    "评论日期",
    "评星",
    "标题",
    "评论",
    "标题_中文",
    "评论_中文",
    "sorftime_评论产品的属性",
    "lingxing_review_id",
    "lingxing_VP",
    "lingxing_Vine",
    "lingxing_来源",
    "lingxing_MSKU",
    "lingxing_ASIN",
]
TOP_LEVEL_FIELDS = ["编码序号", "来源定位", "Review层编码", "Review层推测", "反馈点"]
SOURCE_LOCATOR_FIELDS = ["数据行", "review_id", "评论日期", "评星", "标题"]
SCENE_FIELDS = ["实际场景", "计划场景", "用户估计", "转述证据"]
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
VALUE_CHAIN_FIELDS = [
    "产品特征或体验",
    "用户任务结果",
    "情绪关系社会价值",
    "事实边界",
    "证据强度",
]
REVIEW_EVIDENCE_FIELDS = ["等级", "说明"]
INFERENCE_FIELDS = ["购买动机", "期望结果"]
INFERENCE_DETAIL_FIELDS = ["处理结果", "可能推测", "依据", "事实边界"]
FEEDBACK_FIELDS = [
    "unit_id",
    "证据原文",
    "事实判断",
    "极性",
    "维度",
    "满意点",
    "问题",
    "未满足的需求",
    "未知项",
    "解释假设",
    "候选业务动作",
]
ACTION_FIELDS = ["Listing", "图片与A+", "产品"]
REVIEW_POLARITIES = {"正向", "正向为主", "正负混合", "负向为主", "负向"}
FEEDBACK_POLARITIES = {"正向", "中性", "负向", "正负混合"}
EVIDENCE_LEVELS = {"高", "中", "低", "unknown"}
INFERENCE_STATUSES = {"已有直接证据", "可谨慎推测", "证据不足"}


def read_jsonl(path):
    records = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                raise ValueError(f"{path} 第 {line_number} 行为空")
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise ValueError(f"{path} 第 {line_number} 行不是合法 JSON: {error}") from error
    return records


def write_jsonl(path, records):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")))
            handle.write("\n")


def validate_source_contract(path):
    path = Path(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != SOURCE_SHA256:
        raise ValueError(f"04 SHA-256 已变化: {digest}")

    sources = read_jsonl(path)
    if len(sources) != 559:
        raise ValueError(f"04 应为 559 行，实际为 {len(sources)} 行")
    for index, source in enumerate(sources, start=1):
        _expect_keys(source, SOURCE_FIELDS, f"04 第 {index} 行")
    return sources


def prepare_batches(sources, output_dir, batch_size=10):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for offset in range(0, len(sources), batch_size):
        batch_number = offset // batch_size + 1
        path = output_dir / f"batch-{batch_number:03d}.jsonl"
        records = []
        for source_index, source in enumerate(sources[offset:offset + batch_size], start=offset + 1):
            records.append({"编码序号": source_index, **source})
        write_jsonl(path, records)
        paths.append(path)
    return paths


def merge_records(sources, semantic_records):
    by_sequence = {}
    for record in semantic_records:
        sequence = record.get("编码序号")
        if not isinstance(sequence, int):
            raise ValueError("语义记录的编码序号必须是整数")
        if sequence in by_sequence:
            raise ValueError(f"编码序号 {sequence} 重复")
        _expect_keys(
            record,
            ["编码序号", "Review层编码", "Review层推测", "反馈点"],
            f"语义记录 {sequence}",
        )
        by_sequence[sequence] = record

    expected = set(range(1, len(sources) + 1))
    actual = set(by_sequence)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise ValueError(f"语义记录覆盖不完整，缺失={missing}，越界={extra}")

    merged = []
    for sequence, source in enumerate(sources, start=1):
        semantic = by_sequence[sequence]
        feedback = []
        for unit_number, unit in enumerate(semantic["反馈点"], start=1):
            normalized = {"unit_id": f"R{sequence:03d}-U{unit_number:02d}"}
            normalized.update({key: copy.deepcopy(value) for key, value in unit.items() if key != "unit_id"})
            feedback.append(normalized)
        merged.append({
            "编码序号": sequence,
            "来源定位": {
                "数据行": sequence,
                "review_id": source["lingxing_review_id"],
                "评论日期": source["评论日期"],
                "评星": source["评星"],
                "标题": source["标题"],
            },
            "Review层编码": copy.deepcopy(semantic["Review层编码"]),
            "Review层推测": copy.deepcopy(semantic["Review层推测"]),
            "反馈点": feedback,
        })
    return merged


def validate_semantic_batch(source_batch, semantic_records):
    sources = {}
    for record in source_batch:
        _expect_keys(record, ["编码序号", *SOURCE_FIELDS], "批次输入")
        sequence = record["编码序号"]
        if not isinstance(sequence, int) or sequence in sources:
            raise ValueError("批次输入的编码序号必须是唯一整数")
        sources[sequence] = {field: record[field] for field in SOURCE_FIELDS}

    semantics = {}
    for record in semantic_records:
        sequence = record.get("编码序号")
        _expect_keys(
            record,
            ["编码序号", "Review层编码", "Review层推测", "反馈点"],
            f"语义记录 {sequence}",
        )
        if not isinstance(sequence, int) or sequence in semantics:
            raise ValueError("语义记录的编码序号必须是唯一整数")
        semantics[sequence] = record

    if set(sources) != set(semantics):
        raise ValueError(
            f"批次覆盖不一致，缺失={sorted(set(sources) - set(semantics))}，"
            f"越界={sorted(set(semantics) - set(sources))}"
        )

    feedback_count = 0
    for sequence in sorted(sources):
        semantic = semantics[sequence]
        location = f"编码序号 {sequence}"
        _validate_review(semantic["Review层编码"], location)
        _validate_inference(
            semantic["Review层推测"],
            semantic["Review层编码"],
            location,
        )
        feedback = semantic["反馈点"]
        if not isinstance(feedback, list) or not feedback:
            raise ValueError(f"{location}.反馈点必须是非空数组")
        for unit_number, unit in enumerate(feedback, start=1):
            normalized = {"unit_id": f"R{sequence:03d}-U{unit_number:02d}"}
            normalized.update({key: value for key, value in unit.items() if key != "unit_id"})
            _validate_feedback(
                normalized,
                sources[sequence],
                f"{location}.反馈点[{unit_number}]",
            )
            feedback_count += 1
    return {"评论数": len(semantics), "反馈点数": feedback_count}


def validate_records(sources, records):
    if len(records) != len(sources):
        raise ValueError(f"正式编码行数应为 {len(sources)}，实际为 {len(records)}")

    unit_ids = set()
    for sequence, (source, record) in enumerate(zip(sources, records), start=1):
        location = f"编码序号 {sequence}"
        _expect_keys(record, TOP_LEVEL_FIELDS, location)
        if record["编码序号"] != sequence:
            raise ValueError(f"{location} 的编码序号或排序错误")

        expected_locator = {
            "数据行": sequence,
            "review_id": source["lingxing_review_id"],
            "评论日期": source["评论日期"],
            "评星": source["评星"],
            "标题": source["标题"],
        }
        _expect_keys(record["来源定位"], SOURCE_LOCATOR_FIELDS, f"{location}.来源定位")
        if record["来源定位"] != expected_locator:
            raise ValueError(f"{location}.来源定位与 04 不一致")

        _validate_review(record["Review层编码"], location)
        _validate_inference(
            record["Review层推测"],
            record["Review层编码"],
            location,
        )
        feedback = record["反馈点"]
        if not isinstance(feedback, list) or not feedback:
            raise ValueError(f"{location}.反馈点必须是非空数组")
        for unit_number, unit in enumerate(feedback, start=1):
            unit_location = f"{location}.反馈点[{unit_number}]"
            _validate_feedback(unit, source, unit_location)
            expected_unit_id = f"R{sequence:03d}-U{unit_number:02d}"
            if unit["unit_id"] != expected_unit_id:
                raise ValueError(f"{unit_location}.unit_id 应为 {expected_unit_id}")
            if unit["unit_id"] in unit_ids:
                raise ValueError(f"unit_id 重复: {unit['unit_id']}")
            unit_ids.add(unit["unit_id"])
    return {"评论数": len(records), "反馈点数": len(unit_ids)}


def _validate_review(review, location):
    _expect_keys(review, REVIEW_FIELDS, f"{location}.Review层编码")
    _expect_string(review["消费者"], f"{location}.消费者")
    _expect_keys(review["使用场景"], SCENE_FIELDS, f"{location}.使用场景")
    for field in SCENE_FIELDS:
        _expect_string_array(review["使用场景"][field], f"{location}.使用场景.{field}")
    for field in ["用户任务", "购买动机", "期望结果", "实际结果", "满意点", "未满足的需求"]:
        _expect_string_array(review[field], f"{location}.{field}")

    chains = review["价值链"]
    if not isinstance(chains, list) or not chains:
        raise ValueError(f"{location}.价值链必须是非空数组")
    for index, chain in enumerate(chains, start=1):
        chain_location = f"{location}.价值链[{index}]"
        _expect_keys(chain, VALUE_CHAIN_FIELDS, chain_location)
        for field in VALUE_CHAIN_FIELDS[:-1]:
            _expect_string(chain[field], f"{chain_location}.{field}")
        if chain["证据强度"] not in EVIDENCE_LEVELS:
            raise ValueError(f"{chain_location}.证据强度不在受控词表")

    _expect_keys(review["证据强度"], REVIEW_EVIDENCE_FIELDS, f"{location}.证据强度")
    if review["证据强度"]["等级"] not in EVIDENCE_LEVELS:
        raise ValueError(f"{location}.证据强度.等级不在受控词表")
    _expect_string(review["证据强度"]["说明"], f"{location}.证据强度.说明")
    if review["总体极性"] not in REVIEW_POLARITIES:
        raise ValueError(f"{location}.总体极性不在受控词表")
    _expect_string(review["决策结果"], f"{location}.决策结果")


def _validate_feedback(unit, source, location):
    _expect_keys(unit, FEEDBACK_FIELDS, location)
    _expect_string(unit["unit_id"], f"{location}.unit_id")
    evidence = unit["证据原文"]
    _expect_string(evidence, f"{location}.证据原文")
    if evidence not in source["标题"] and evidence not in source["评论"]:
        raise ValueError(f"{location}.证据原文不是英文标题或正文的逐字连续子串")
    _expect_string(unit["事实判断"], f"{location}.事实判断")
    if unit["极性"] not in FEEDBACK_POLARITIES:
        raise ValueError(f"{location}.极性不在受控词表")
    for field in ["维度", "满意点", "问题", "未满足的需求", "未知项"]:
        _expect_string_array(unit[field], f"{location}.{field}")
    _expect_string(unit["解释假设"], f"{location}.解释假设")
    _expect_keys(unit["候选业务动作"], ACTION_FIELDS, f"{location}.候选业务动作")
    for field in ACTION_FIELDS:
        _expect_string(unit["候选业务动作"][field], f"{location}.候选业务动作.{field}")


def _validate_inference(inference, review, location):
    inference_location = f"{location}.Review层推测"
    _expect_keys(inference, INFERENCE_FIELDS, inference_location)
    for field in INFERENCE_FIELDS:
        item_location = f"{inference_location}.{field}"
        item = inference[field]
        _expect_keys(item, INFERENCE_DETAIL_FIELDS, item_location)
        status = item["处理结果"]
        if status not in INFERENCE_STATUSES:
            raise ValueError(f"{item_location}.处理结果不在受控词表")
        _expect_string_array(item["可能推测"], f"{item_location}.可能推测")
        _expect_string_array(item["依据"], f"{item_location}.依据")
        _expect_string(item["事实边界"], f"{item_location}.事实边界")

        has_direct_evidence = review[field] != ["unknown"]
        has_inference = item["可能推测"] != ["unknown"] and item["依据"] != ["unknown"]
        if status == "已有直接证据" and (not has_direct_evidence or has_inference):
            raise ValueError(f"{item_location} 与 Review 层直接证据不一致")
        if status == "证据不足" and (has_direct_evidence or has_inference):
            raise ValueError(f"{item_location} 的证据不足状态与内容不一致")
        if status == "可谨慎推测" and (has_direct_evidence or not has_inference):
            raise ValueError(f"{item_location} 的谨慎推测不得写入事实层，且必须有推测与依据")


def _expect_keys(value, expected, location):
    if not isinstance(value, dict):
        raise ValueError(f"{location} 必须是对象")
    if list(value) != expected:
        raise ValueError(f"{location} 字段应为 {expected}，实际为 {list(value)}")


def _expect_string(value, location):
    if not isinstance(value, str) or not value:
        raise ValueError(f"{location} 必须是非空字符串")


def _expect_string_array(value, location):
    if not isinstance(value, list) or not value or any(not isinstance(item, str) or not item for item in value):
        raise ValueError(f"{location} 必须是非空字符串数组")
    if "unknown" in value and value != ["unknown"]:
        raise ValueError(f"{location} 不得把 unknown 与其他值混用")


def _load_semantic_directory(path):
    paths = sorted(Path(path).glob("batch-*-coded.jsonl"))
    if not paths:
        raise ValueError(f"{path} 中没有 batch-*-coded.jsonl")
    records = []
    for batch_path in paths:
        records.extend(read_jsonl(batch_path))
    return records


def main():
    parser = argparse.ArgumentParser(description="准备、合并并校验全量评论编码")
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare")
    prepare.add_argument("source", type=Path)
    prepare.add_argument("output_dir", type=Path)

    merge = subparsers.add_parser("merge")
    merge.add_argument("source", type=Path)
    merge.add_argument("semantic_dir", type=Path)
    merge.add_argument("output", type=Path)

    validate = subparsers.add_parser("validate")
    validate.add_argument("source", type=Path)
    validate.add_argument("output", type=Path)

    validate_batch = subparsers.add_parser("validate-batch")
    validate_batch.add_argument("source_batch", type=Path)
    validate_batch.add_argument("coded_batch", type=Path)

    args = parser.parse_args()

    if args.command == "validate-batch":
        summary = validate_semantic_batch(
            read_jsonl(args.source_batch),
            read_jsonl(args.coded_batch),
        )
        print(json.dumps(summary, ensure_ascii=False))
        return

    sources = validate_source_contract(args.source)

    if args.command == "prepare":
        paths = prepare_batches(sources, args.output_dir)
        print(json.dumps({"批次数": len(paths), "评论数": len(sources)}, ensure_ascii=False))
        return

    if args.command == "merge":
        semantics = _load_semantic_directory(args.semantic_dir)
        records = merge_records(sources, semantics)
        summary = validate_records(sources, records)
        write_jsonl(args.output, records)
        print(json.dumps(summary, ensure_ascii=False))
        return

    records = read_jsonl(args.output)
    summary = validate_records(sources, records)
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
