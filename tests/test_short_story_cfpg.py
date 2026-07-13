from __future__ import annotations

import json
import sys
from pathlib import Path


SCRIPT_DIR = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "foreshadow_causality_benchmark"
    / "experiments"
    / "cfpg_short_story"
    / "scripts"
)
sys.path.insert(0, str(SCRIPT_DIR))

from cfpg_short_story import (  # noqa: E402
    lexical_similarity,
    select_refresh_context,
    split_sentences,
    summarize_oracle,
    summarize_tracking,
)


def test_sentence_splitter_handles_english_and_chinese() -> None:
    assert split_sentences("One clue appeared. Later it mattered!") == [
        "One clue appeared.",
        "Later it mattered!",
    ]
    assert split_sentences("先有異象。後來真相大白！") == ["先有異象。", "後來真相大白！"]


def test_refresh_context_keeps_recent_and_retrieves_related_old_sentence() -> None:
    prefix = [
        {"segment_id": "P0001S001", "segment_index": 0, "text": "A silver key was hidden."},
        {"segment_id": "P0002S001", "segment_index": 1, "text": "They ate dinner."},
        {"segment_id": "P0003S001", "segment_index": 2, "text": "Night fell."},
    ]
    selected = select_refresh_context(prefix, "the hidden silver key", top_k=1, recent_k=1)
    assert [row["segment_id"] for row in selected] == ["P0001S001", "P0003S001"]
    assert lexical_similarity(prefix[0]["text"], "silver key") > 0


def test_paper_metric_summaries() -> None:
    tracking = summarize_tracking(
        [
            {
                "model": "m",
                "method": "cfpg",
                "gold_index": 10,
                "predicted_index": 12,
                "continuation_judgment": {"score": 1.0},
            },
            {
                "model": "m",
                "method": "cfpg",
                "gold_index": 20,
                "predicted_index": 15,
                "continuation_judgment": {"score": 0.0},
            },
            {
                "model": "m",
                "method": "cfpg",
                "gold_index": 30,
                "predicted_index": None,
                "continuation_judgment": None,
            },
        ]
    )["m/cfpg"]
    assert tracking["correct_detection_rate"] == 1 / 3
    assert tracking["early_triggers"] == 1
    assert tracking["missed_triggers"] == 1
    assert tracking["localization_error"] == 3.5
    assert tracking["continuation_fidelity"] == 1.0

    oracle = summarize_oracle(
        [
            {"model": "m", "method": "cfpg", "should_payoff": True, "judgment": {"score": 1.0, "payoff_realized": True}},
            {"model": "m", "method": "cfpg", "should_payoff": False, "judgment": {"score": 0.5, "payoff_realized": False}},
        ]
    )["m/cfpg"]
    assert oracle["should_payoff_rate"] == 0.5
    assert oracle["average_score"] == 0.75


def test_taxonomy_v2_separates_carrier_from_narrative_function() -> None:
    root = Path(__file__).resolve().parents[1]
    taxonomy = json.loads(
        (
            root
            / "data"
            / "foreshadow_causality_benchmark"
            / "experiments"
            / "cfpg_short_story"
            / "data"
            / "cfpg_taxonomy_v2.json"
        ).read_text(encoding="utf-8")
    )
    allowed_primary = set(taxonomy["primary_types"])
    allowed_functions = set(taxonomy["narrative_functions"])
    assert len(taxonomy["cases"]) == 30
    assert "red_herring" not in allowed_primary
    assert "misdirection" in allowed_functions
    for case in taxonomy["cases"].values():
        assert case["primary_type"] in allowed_primary
        assert case["narrative_function"] in allowed_functions
        assert case["foreshadow_zh"] and case["trigger_zh"] and case["payoff_zh"]
