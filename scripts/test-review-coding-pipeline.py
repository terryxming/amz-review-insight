import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("review-coding-pipeline.py")
SPEC = importlib.util.spec_from_file_location("review_coding_pipeline", SCRIPT)
pipeline = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pipeline)


def source_record(review_id="R1"):
    return {
        "评论日期": "2026-01-01",
        "评星": 4,
        "标题": "Great sound",
        "评论": "Great sound, but the app is slow.",
        "标题_中文": "声音很好",
        "评论_中文": "声音很好，但应用很慢。",
        "sorftime_评论产品的属性": "",
        "lingxing_review_id": review_id,
        "lingxing_VP": "是",
        "lingxing_Vine": "否",
        "lingxing_来源": "review",
        "lingxing_MSKU": "MSKU",
        "lingxing_ASIN": "ASIN",
    }


def semantic_record(sequence=1, evidence="Great sound"):
    return {
        "编码序号": sequence,
        "Review层编码": {
            "消费者": "unknown",
            "使用场景": {
                "实际场景": ["使用卡拉OK机"],
                "计划场景": ["unknown"],
                "用户估计": ["unknown"],
                "转述证据": ["unknown"],
            },
            "用户任务": ["唱歌娱乐"],
            "购买动机": ["unknown"],
            "期望结果": ["unknown"],
            "实际结果": ["声音好"],
            "满意点": ["声音好"],
            "价值链": [{
                "产品特征或体验": "声音好",
                "用户任务结果": "获得良好听感",
                "情绪关系社会价值": "unknown",
                "事实边界": "前两层为直接体验",
                "证据强度": "高",
            }],
            "未满足的需求": ["unknown"],
            "证据强度": {"等级": "高", "说明": "直接体验"},
            "总体极性": "正向为主",
            "决策结果": "unknown",
        },
        "Review层推测": {
            "购买动机": {
                "处理结果": "证据不足",
                "可能推测": ["unknown"],
                "依据": ["unknown"],
                "事实边界": "原文未明确说明购买动机",
            },
            "期望结果": {
                "处理结果": "证据不足",
                "可能推测": ["unknown"],
                "依据": ["unknown"],
                "事实边界": "原文未明确说明购买前期待",
            },
        },
        "反馈点": [{
            "证据原文": evidence,
            "事实判断": "用户认为声音好。",
            "极性": "正向",
            "维度": ["音质"],
            "满意点": ["声音好"],
            "问题": ["unknown"],
            "未满足的需求": ["unknown"],
            "未知项": ["unknown"],
            "解释假设": "unknown",
            "候选业务动作": {
                "Listing": "unknown",
                "图片与A+": "unknown",
                "产品": "unknown",
            },
        }],
    }


class ReviewCodingPipelineTests(unittest.TestCase):
    def test_merge_injects_source_locator_and_unit_ids(self):
        merged = pipeline.merge_records([source_record()], [semantic_record()])

        self.assertEqual(merged[0]["来源定位"]["review_id"], "R1")
        self.assertEqual(merged[0]["反馈点"][0]["unit_id"], "R001-U01")
        self.assertEqual(
            list(merged[0]),
            ["编码序号", "来源定位", "Review层编码", "Review层推测", "反馈点"],
        )

    def test_validation_rejects_non_verbatim_evidence(self):
        merged = pipeline.merge_records(
            [source_record()],
            [semantic_record(evidence="Great audio")],
        )

        with self.assertRaisesRegex(ValueError, "证据原文"):
            pipeline.validate_records([source_record()], merged)

    def test_validation_rejects_uncontrolled_polarity(self):
        semantic = semantic_record()
        semantic["Review层编码"]["总体极性"] = "强正向"
        merged = pipeline.merge_records([source_record()], [semantic])

        with self.assertRaisesRegex(ValueError, "总体极性"):
            pipeline.validate_records([source_record()], merged)

    def test_validation_rejects_inference_promoted_to_fact_layer(self):
        semantic = semantic_record()
        semantic["Review层推测"]["购买动机"] = {
            "处理结果": "可谨慎推测",
            "可能推测": ["可能为家庭娱乐购买"],
            "依据": ["评论提到唱歌"],
            "事实边界": "只是推测",
        }
        semantic["Review层编码"]["购买动机"] = ["为家庭娱乐购买"]
        merged = pipeline.merge_records([source_record()], [semantic])

        with self.assertRaisesRegex(ValueError, "谨慎推测不得写入事实层"):
            pipeline.validate_records([source_record()], merged)

    def test_prepare_writes_ten_record_batches(self):
        sources = [source_record(f"R{index}") for index in range(1, 24)]

        with tempfile.TemporaryDirectory() as directory:
            paths = pipeline.prepare_batches(sources, Path(directory), batch_size=10)
            counts = [len(path.read_text(encoding="utf-8").splitlines()) for path in paths]

        self.assertEqual(counts, [10, 10, 3])

    def test_batch_validation_accepts_global_sequence_numbers(self):
        source_batch = [
            {"编码序号": 21, **source_record("R21")},
            {"编码序号": 22, **source_record("R22")},
        ]
        semantics = [semantic_record(21), semantic_record(22)]

        summary = pipeline.validate_semantic_batch(source_batch, semantics)

        self.assertEqual(summary, {"评论数": 2, "反馈点数": 2})

    def test_jsonl_round_trip_keeps_unicode(self):
        records = [source_record()]

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "records.jsonl"
            pipeline.write_jsonl(path, records)
            loaded = pipeline.read_jsonl(path)

        self.assertEqual(loaded, records)
        self.assertIn("声音", path.read_text(encoding="utf-8") if path.exists() else "声音")


if __name__ == "__main__":
    unittest.main()
