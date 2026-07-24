"""Tests for the local F–T–P annotation server data layer."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


SERVER_PATH = (
    Path(__file__).resolve().parents[1] / "annotation_app" / "server.py"
)
SPEC = importlib.util.spec_from_file_location("ftp_annotation_server", SERVER_PATH)
assert SPEC and SPEC.loader
server = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(server)


def test_story_inventory_exposes_parallel_and_source_only_texts() -> None:
    stories = {item["story_id"]: item for item in server.list_stories()}
    assert stories["speckled_band"]["has_en"] is True
    assert stories["speckled_band"]["has_zh"] is True
    assert stories["medicine"]["source_language"] == "zh"
    assert stories["medicine"]["has_en"] is False


def test_story_payload_preserves_paragraph_ids_in_both_languages() -> None:
    payload = server.story_payload("speckled_band")
    assert payload["texts"]["en"]["paragraphs"][0]["id"] == "P0001"
    assert payload["texts"]["zh"]["paragraphs"][0]["id"] == "P0001"
    assert payload["texts"]["en"]["paragraphs"][0]["text"]
    assert payload["texts"]["zh"]["paragraphs"][0]["text"]


def test_reviewed_annotation_requires_complete_triple_and_explanation() -> None:
    payload = {
        "story_id": "speckled_band",
        "annotations": [
            {
                "annotation_id": "sb_001",
                "status": "reviewed",
                "f": {"span_en": "P0001"},
                "t": {"span_en": ""},
                "p": {"span_en": "P0003"},
                "primary_type": "object",
                "narrative_function": "",
                "rationale": "",
            }
        ],
    }
    errors = server.validate_annotations(payload, "speckled_band")
    assert any("T 范围" in error for error in errors)
    assert any("叙事功能" in error for error in errors)
    assert any("原因解释" in error for error in errors)


def test_bilingual_spans_can_be_independent() -> None:
    payload = {
        "story_id": "speckled_band",
        "annotations": [
            {
                "annotation_id": "sb_001",
                "status": "reviewed",
                "f": {"span_en": "P0143-P0158", "span_zh": "P0150-P0162"},
                "t": {"span_en": "P0166-P0171", "span_zh": "P0170-P0178"},
                "p": {"span_en": "P0237-P0238", "span_zh": "P0240-P0241"},
                "primary_type": "object",
                "narrative_function": "anomaly",
                "payoff_type": "literal",
                "rationale": "The anomalous fixtures become the delivery mechanism.",
            }
        ],
    }
    assert server.validate_annotations(payload, "speckled_band") == []


def test_character_level_selection_is_validated_against_source_text() -> None:
    payload = {
        "story_id": "speckled_band",
        "annotations": [
            {
                "annotation_id": "sb_exact_001",
                "status": "draft",
                "f": {
                    "span_en": "P0001",
                    "selection_en": {
                        "start_paragraph": "P0001",
                        "start_offset": 6,
                        "end_paragraph": "P0001",
                        "end_offset": 15,
                        "text": "THE ADVEN",
                    },
                },
                "t": {},
                "p": {},
            }
        ],
    }
    assert server.validate_annotations(payload, "speckled_band") == []
    payload["annotations"][0]["f"]["selection_en"]["end_offset"] = 1000
    errors = server.validate_annotations(payload, "speckled_band")
    assert any("字符位置越界" in error for error in errors)


def test_character_level_selection_can_cross_paragraphs() -> None:
    payload = {
        "story_id": "medicine",
        "annotations": [
            {
                "annotation_id": "medicine_exact_001",
                "status": "draft",
                "f": {
                    "span_zh": "P0012-P0014",
                    "selection_zh": {
                        "start_paragraph": "P0012",
                        "start_offset": 2,
                        "end_paragraph": "P0014",
                        "end_offset": 8,
                        "text": "跨段精确摘录由前端保存",
                    },
                },
                "t": {},
                "p": {},
            }
        ],
    }
    assert server.validate_annotations(payload, "medicine") == []


def test_save_is_separate_and_round_trips(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(server, "MANUAL_ROOT", tmp_path)
    payload = {
        "story_id": "medicine",
        "annotations": [
            {
                "annotation_id": "medicine_ftp_001",
                "status": "draft",
                "f": {"span_zh": "P0012"},
                "t": {"span_zh": ""},
                "p": {"span_zh": ""},
            }
        ],
    }
    saved = server.save_annotations("medicine", payload)
    loaded = server.load_saved("medicine")
    assert loaded == saved
    assert loaded["schema_version"] == "ftp_manual_annotation_v1"
    on_disk = json.loads((tmp_path / "medicine.json").read_text(encoding="utf-8"))
    assert on_disk["annotations"][0]["story_id"] == "medicine"


def test_cfpg_seed_is_available_without_becoming_manual_gold() -> None:
    seeds = server.load_seeds("speckled_band")
    assert seeds
    assert seeds[0]["seed_id"].startswith("speckled_band:")
    assert seeds[0]["f"]["span"]
    assert seeds[0]["t"]["span"]
    assert seeds[0]["p"]["span"]
    assert server.load_saved("speckled_band")["annotations"] == []
