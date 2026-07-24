"""Shared data and metric utilities for the short-story CFPG reproduction.

The paper operates on sentences from BookSum summaries.  Our source stories are
already paragraph-addressable, so this module adds stable sentence IDs while
retaining the original paragraph IDs for evidence auditing.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable


PARAGRAPH_RE = re.compile(r"^\[(P\d{4})\]\s+(.*)$", re.S)
SPAN_RE = re.compile(r"P(\d{4})")
ZH_RE = re.compile(r"[\u3400-\u9fff]")
ZH_SENTENCE_RE = re.compile(r".*?(?:[。！？!?]+[”’」』]?|$)", re.S)
EN_BOUNDARY_RE = re.compile(r"(?<=[.!?])\s+(?=[\"'“‘A-Z0-9])")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def parse_story(path: Path) -> tuple[str, list[dict[str, str]]]:
    title = path.stem
    paragraphs: list[dict[str, str]] = []
    for block in path.read_text(encoding="utf-8").split("\n\n"):
        block = block.strip()
        if not block:
            continue
        if block.startswith("# "):
            title = block[2:].strip() or title
            continue
        match = PARAGRAPH_RE.match(block)
        if match:
            paragraphs.append({"paragraph_id": match.group(1), "text": match.group(2).strip()})
    return title, paragraphs


def split_sentences(text: str) -> list[str]:
    """Conservatively split English/Chinese prose without external models."""
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    if len(ZH_RE.findall(text)) >= max(2, len(text) // 12):
        parts = [match.group(0).strip() for match in ZH_SENTENCE_RE.finditer(text)]
    else:
        parts = [part.strip() for part in EN_BOUNDARY_RE.split(text)]
    return [part for part in parts if part]


def segment_story(path: Path) -> tuple[str, list[dict[str, Any]]]:
    title, paragraphs = parse_story(path)
    segments: list[dict[str, Any]] = []
    for paragraph in paragraphs:
        sentences = split_sentences(paragraph["text"]) or [paragraph["text"]]
        for sentence_number, sentence in enumerate(sentences, start=1):
            segments.append(
                {
                    "segment_id": f"{paragraph['paragraph_id']}S{sentence_number:03d}",
                    "segment_index": len(segments),
                    "paragraph_id": paragraph["paragraph_id"],
                    "text": sentence,
                }
            )
    return title, segments


def paragraph_bounds(span: str) -> tuple[int, int]:
    values = [int(value) for value in SPAN_RE.findall(span or "")]
    if not values:
        raise ValueError(f"span has no paragraph ID: {span!r}")
    return values[0], values[-1]


def _features(text: str) -> set[str]:
    lowered = text.lower()
    words = set(re.findall(r"[a-z0-9]+", lowered))
    chinese = "".join(ZH_RE.findall(lowered))
    if chinese:
        words.update(chinese[index : index + 2] for index in range(max(1, len(chinese) - 1)))
    return words


def lexical_similarity(left: str, right: str) -> float:
    left_features = _features(left)
    right_features = _features(right)
    if not left_features or not right_features:
        return 0.0
    return len(left_features & right_features) / len(left_features | right_features)


def best_segment_in_span(
    segments: list[dict[str, Any]], span: str, description: str
) -> dict[str, Any]:
    start, end = paragraph_bounds(span)
    candidates = [
        row
        for row in segments
        if start <= int(row["paragraph_id"][1:]) <= end
    ]
    if not candidates:
        raise ValueError(f"no source segment found for {span}")
    return max(candidates, key=lambda row: lexical_similarity(row["text"], description))


def last_segment_index_in_span(segments: list[dict[str, Any]], span: str) -> int:
    start, end = paragraph_bounds(span)
    candidates = [
        row["segment_index"]
        for row in segments
        if start <= int(row["paragraph_id"][1:]) <= end
    ]
    if not candidates:
        raise ValueError(f"no source segment found for {span}")
    return max(candidates)


def build_cases(
    triples_path: Path,
    normalized_dir: Path,
    story_ids: set[str] | None = None,
    taxonomy: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Convert accepted paragraph-level triples to sentence-level experiment cases."""
    cache: dict[str, tuple[str, list[dict[str, Any]]]] = {}
    cases: list[dict[str, Any]] = []
    for item in read_jsonl(triples_path):
        candidate = item.get("candidate", item)
        verdict = item.get("verdict", {})
        story_id = candidate["story_id"]
        if story_ids and story_id not in story_ids:
            continue
        if verdict and verdict.get("accepted") is not True:
            continue
        if story_id not in cache:
            cache[story_id] = segment_story(normalized_dir / f"{story_id}.txt")
        title, segments = cache[story_id]
        f_description = verdict.get("foreshadow_description") or candidate.get("foreshadow_summary", "")
        p_description = verdict.get("payoff_description") or candidate.get("payoff_summary", "")
        f_anchor = best_segment_in_span(segments, candidate["foreshadow_span"], f_description)
        p_anchor = best_segment_in_span(segments, candidate["payoff_span"], p_description)
        if p_anchor["segment_index"] <= f_anchor["segment_index"]:
            continue
        trigger = verdict.get("final_trigger") or candidate.get("proposed_trigger", {})
        normalized = (taxonomy or {}).get("cases", {}).get(candidate["candidate_id"], {})
        cases.append(
            {
                "case_id": candidate["candidate_id"],
                "story_id": story_id,
                "story_title": title,
                "foreshadow": {
                    "description": f_description,
                    "description_zh": normalized.get("foreshadow_zh", ""),
                    "span": candidate["foreshadow_span"],
                    "anchor_segment_id": f_anchor["segment_id"],
                    "anchor_index": f_anchor["segment_index"],
                    "span_end_index": last_segment_index_in_span(
                        segments, candidate["foreshadow_span"]
                    ),
                    "text": candidate.get("foreshadow_text", ""),
                    "primary_type": normalized.get("primary_type")
                    or candidate.get("primary_type")
                    or candidate.get("foreshadow_type", "unknown"),
                    "narrative_function": normalized.get("narrative_function")
                    or candidate.get("narrative_function", "unknown"),
                    "legacy_type": candidate.get("foreshadow_type"),
                },
                "trigger": trigger,
                "trigger_zh": normalized.get("trigger_zh", ""),
                "payoff": {
                    "description": p_description,
                    "description_zh": normalized.get("payoff_zh", ""),
                    "span": candidate["payoff_span"],
                    "anchor_segment_id": p_anchor["segment_id"],
                    "anchor_index": p_anchor["segment_index"],
                    "text": p_anchor["text"],
                    "full_span_text": candidate.get("payoff_text", ""),
                    "type": candidate.get("payoff_type", "unknown"),
                },
                "relation_description": candidate.get("relation_description", ""),
                "segments": segments,
                "source_text_path": str(normalized_dir / f"{story_id}.txt"),
                "source_triple_path": str(triples_path),
            }
        )
    return cases


def select_refresh_context(
    prefix: list[dict[str, Any]],
    foreshadow_text: str,
    top_k: int = 5,
    recent_k: int = 8,
) -> list[dict[str, Any]]:
    """FSCR approximation: retrieve old sentences by lexical Jaccard similarity."""
    recent = prefix[-recent_k:]
    recent_ids = {row["segment_id"] for row in recent}
    older = [row for row in prefix[:-recent_k] if row["segment_id"] not in recent_ids]
    retrieved = sorted(
        older,
        key=lambda row: lexical_similarity(row["text"], foreshadow_text),
        reverse=True,
    )[:top_k]
    return sorted([*retrieved, *recent], key=lambda row: row["segment_index"])


def summarize_tracking(rows: list[dict[str, Any]], tolerance: int = 3) -> dict[str, Any]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault((row["model"], row["method"]), []).append(row)
    output: dict[str, Any] = {}
    for (model, method), items in grouped.items():
        offsets = [item["predicted_index"] - item["gold_index"] for item in items if item.get("predicted_index") is not None]
        correct = [offset for offset in offsets if abs(offset) <= tolerance]
        fidelity = [
            float(item["continuation_judgment"]["score"])
            for item in items
            if item.get("predicted_index") is not None
            and abs(item["predicted_index"] - item["gold_index"]) <= tolerance
            and item.get("continuation_judgment", {}).get("score") is not None
        ]
        key = f"{model}/{method}"
        output[key] = {
            "cases": len(items),
            "correct_detection_rate": len(correct) / len(items) if items else 0.0,
            "early_triggers": sum(offset < -tolerance for offset in offsets),
            "late_triggers": sum(offset > tolerance for offset in offsets),
            "missed_triggers": sum(item.get("predicted_index") is None for item in items),
            "localization_error": sum(abs(offset) for offset in offsets) / len(offsets) if offsets else None,
            "continuation_fidelity": sum(fidelity) / len(fidelity) if fidelity else None,
        }
    return output


def summarize_oracle(rows: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault((row["model"], row["method"]), []).append(row)
    output: dict[str, Any] = {}
    for (model, method), items in grouped.items():
        scores = [float(item["judgment"]["score"]) for item in items]
        activations = [
            bool(item["should_payoff"])
            for item in items
            if isinstance(item.get("should_payoff"), bool)
        ]
        output[f"{model}/{method}"] = {
            "cases": len(items),
            "should_payoff_rate": (
                sum(activations) / len(activations) if activations else None
            ),
            "average_score": sum(scores) / len(scores) if scores else None,
        }
    return output
