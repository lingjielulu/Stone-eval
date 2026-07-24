"""Render human-readable CFPG layer views from existing outputs."""

from __future__ import annotations

import argparse
import json
from collections import OrderedDict
from pathlib import Path
from typing import Any


DEFAULT_SUMMARIES = Path(
    "foreshadow/honglou/results/cfpg/honglou_booksum/original_80_chapter_summaries.jsonl"
)
DEFAULT_CANDIDATES = Path(
    "foreshadow/honglou/results/cfpg/candidates/"
    "honglou_candidates_20260611_deepseek_honglou_original80.jsonl"
)
DEFAULT_VERIFIED = Path(
    "foreshadow/honglou/results/cfpg/verified/"
    "honglou_ftp_triples_20260611_deepseek_honglou_original80.jsonl"
)
DEFAULT_VERIFIED_UNIQUE = Path(
    "foreshadow/honglou/results/cfpg/verified/"
    "honglou_ftp_triples_20260611_deepseek_honglou_original80.unique.jsonl"
)
DEFAULT_REJECTED = Path(
    "foreshadow/honglou/results/cfpg/verified/"
    "honglou_rejected_candidates_20260611_deepseek_honglou_original80.jsonl"
)
DEFAULT_RUN_ID = "20260611_deepseek_honglou_original80"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + ("\n" if rows else ""),
        encoding="utf-8",
    )


def source_text(value: dict[str, Any]) -> str:
    return (
        value.get("setup")
        or value.get("note")
        or value.get("item")
        or value.get("literal_content")
        or ""
    )


def build_foreshadow_rows(summaries: list[dict[str, Any]], candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for chapter in summaries:
        chapter_index = chapter["chapter_index"]
        chapter_title = chapter["chapter_title"]
        for field, layer, label in [
            ("unresolved_setups", "summary_unresolved_setup", "unresolved"),
            ("foreshadow_notes", "summary_foreshadow_note", "foreshadow"),
            ("poem_dream_prophecy_objects", "summary_poem_dream_prophecy_object", "poem/dream/object"),
        ]:
            for item in chapter.get(field, []):
                if not isinstance(item, dict):
                    continue
                text = source_text(item)
                if not text:
                    continue
                rows.append(
                    {
                        "foreshadow_id": f"honglou:original_80:foreshadow:{len(rows) + 1:06d}",
                        "source_layer": layer,
                        "label": label,
                        "book_id": chapter["book_id"],
                        "chapter_index": chapter_index,
                        "chapter_title": chapter_title,
                        "text": text,
                        "type": item.get("type") or item.get("category") or "",
                        "status": item.get("status", "candidate"),
                        "why_it_matters": item.get("why_it_matters_without_future_spoilers", ""),
                        "evidence_quote": item.get("evidence_quote", ""),
                    }
                )

    seen: OrderedDict[tuple[int, str], dict[str, Any]] = OrderedDict()
    for candidate in candidates:
        key = (candidate["foreshadow_sentence_index"], candidate["foreshadow_text"])
        if key not in seen:
            seen[key] = {
                "foreshadow_id": f"honglou:original_80:extracted_foreshadow:{len(seen) + 1:06d}",
                "source_layer": "candidate_extraction",
                "label": "candidate_foreshadow",
                "book_id": candidate["book_id"],
                "chapter_index": candidate["foreshadow_chapter_index"],
                "chapter_title": "",
                "global_sentence_index": candidate["foreshadow_sentence_index"],
                "text": candidate["foreshadow_text"],
                "type": candidate.get("foreshadow_type", ""),
                "status": "candidate",
                "why_it_matters": candidate.get("stage1_rationale", ""),
                "evidence_quote": candidate["foreshadow_text"],
            }
    rows.extend(seen.values())
    return rows


def rejected_by_candidate_id(rejected: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        row.get("candidate", {}).get("candidate_id"): row.get("verdict", {})
        for row in rejected
        if row.get("candidate", {}).get("candidate_id")
    }


def verified_by_candidate_id(verified: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        row["id"].replace(":ftp:", ":candidate:"): row
        for row in verified
        if row.get("id")
    }


def build_ft_rows(
    candidates: list[dict[str, Any]],
    verified: list[dict[str, Any]],
    rejected: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    accepted = verified_by_candidate_id(verified)
    rejected_map = rejected_by_candidate_id(rejected)
    rows: list[dict[str, Any]] = []
    for candidate in candidates:
        candidate_id = candidate["candidate_id"]
        verdict = "review"
        reason = ""
        if candidate_id in accepted:
            verdict = "accepted"
            reason = accepted[candidate_id].get("verifier", {}).get("rationale", "")
        elif candidate_id in rejected_map:
            verdict = "rejected"
            reason = rejected_map[candidate_id].get("rejection_reason", "")
        rows.append(
            {
                "foreshadow_trigger_id": candidate_id.replace(":candidate:", ":foreshadow_trigger:"),
                "candidate_id": candidate_id,
                "book_id": candidate["book_id"],
                "status": verdict,
                "foreshadow": {
                    "global_sentence_index": candidate["foreshadow_sentence_index"],
                    "chapter_index": candidate["foreshadow_chapter_index"],
                    "text": candidate["foreshadow_text"],
                    "type": candidate.get("foreshadow_type", ""),
                },
                "trigger": candidate.get("proposed_trigger", {}),
                "linked_payoff_hint": {
                    "global_sentence_index": candidate["payoff_sentence_index"],
                    "chapter_index": candidate["payoff_chapter_index"],
                    "text": candidate["payoff_text"],
                },
                "distance_sentences": candidate["distance_sentences"],
                "distance_chapters": candidate["distance_chapters"],
                "confidence": candidate.get("stage1_confidence", 0.0),
                "rationale": candidate.get("stage1_rationale", ""),
                "verification_note": reason,
                "prompt_version": candidate.get("extraction_prompt_version", ""),
            }
        )
    return rows


def render_foreshadows(path: Path, rows: list[dict[str, Any]]) -> None:
    lines = ["# HongLou CFPG Foreshadows", ""]
    lines.append(f"Total rows: {len(rows)}")
    lines.append("")
    for row in rows:
        idx = row.get("global_sentence_index")
        idx_text = f" | S[{idx}]" if idx is not None else ""
        lines.extend(
            [
                f"## {row['foreshadow_id']}",
                f"- Source: {row['source_layer']} / {row['label']}",
                f"- Location: 第{row['chapter_index']:03d}回{idx_text}",
                f"- Type: {row.get('type', '')}",
                f"- Status: {row.get('status', '')}",
                f"- Text: {row['text']}",
            ]
        )
        if row.get("why_it_matters"):
            lines.append(f"- Why: {row['why_it_matters']}")
        if row.get("evidence_quote"):
            lines.append(f"- Evidence: {row['evidence_quote']}")
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def render_foreshadow_triggers(path: Path, rows: list[dict[str, Any]]) -> None:
    lines = ["# HongLou CFPG Foreshadow-Trigger Candidates", ""]
    lines.append(f"Total rows: {len(rows)}")
    lines.append("")
    for row in rows:
        f = row["foreshadow"]
        p = row["linked_payoff_hint"]
        t = row["trigger"]
        lines.extend(
            [
                f"## {row['foreshadow_trigger_id']} [{row['status']}]",
                f"- Candidate: {row['candidate_id']}",
                f"- F[{f['global_sentence_index']}] 第{f['chapter_index']:03d}回: {f['text']}",
                f"- T: {t.get('description', '')}",
            ]
        )
        for condition in t.get("observable_conditions", []):
            lines.append(f"  - condition: {condition}")
        lines.extend(
            [
                f"- Linked payoff hint P[{p['global_sentence_index']}] 第{p['chapter_index']:03d}回: {p['text']}",
                f"- Confidence: {row['confidence']}",
                f"- Stage1 rationale: {row['rationale']}",
            ]
        )
        if row.get("verification_note"):
            lines.append(f"- Verification note: {row['verification_note']}")
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def render_overview(
    path: Path,
    summaries_path: Path,
    timeline_path: Path,
    candidates_path: Path,
    verified_path: Path,
    foreshadows_path: Path,
    ft_path: Path,
    counts: dict[str, int],
) -> None:
    lines = [
        "# HongLou CFPG Layer Overview",
        "",
        "当前有四层数据：",
        "",
        f"1. 摘要层: `{summaries_path}`",
        f"   - 人类可读: `{summaries_path.with_suffix('.review.md')}`",
        f"   - chapters: {counts['summaries']}",
        f"2. 摘要句时间线层: `{timeline_path}`",
        f"   - summary sentences: {counts['timeline']}",
        f"3. 伏笔层: `{foreshadows_path}`",
        f"   - 人类可读: `{foreshadows_path.with_suffix('.review.md')}`",
        f"   - rows: {counts['foreshadows']}",
        f"4. 伏笔+trigger 候选层: `{ft_path}`",
        f"   - 人类可读: `{ft_path.with_suffix('.review.md')}`",
        f"   - rows: {counts['foreshadow_triggers']}",
        f"5. 伏笔-trigger-payoff verified 层: `{verified_path}`",
        f"   - 人类可读: `{verified_path.with_suffix('.review.md')}`",
        f"   - unique triples: {counts['verified']}",
        "",
        "说明：伏笔层包含摘要阶段保留下来的 unresolved/foreshadow/poem-dream-object 条目，另附候选抽取阶段实际用作 F 的摘要句。伏笔+trigger 层来自 candidate extraction，包含 accepted/rejected/review 状态；verified 层只保留通过 verifier 的 F-T-P。",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summaries", type=Path, default=DEFAULT_SUMMARIES)
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--verified", type=Path, default=DEFAULT_VERIFIED)
    parser.add_argument("--verified-unique", type=Path, default=DEFAULT_VERIFIED_UNIQUE)
    parser.add_argument("--rejected", type=Path, default=DEFAULT_REJECTED)
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    args = parser.parse_args()

    summaries = read_jsonl(args.summaries)
    candidates = read_jsonl(args.candidates)
    verified = read_jsonl(args.verified)
    verified_unique = read_jsonl(args.verified_unique)
    rejected = read_jsonl(args.rejected)

    foreshadows = build_foreshadow_rows(summaries, candidates)
    fts = build_ft_rows(candidates, verified, rejected)

    foreshadows_path = Path("foreshadow/honglou/results/cfpg/foreshadows") / (
        f"honglou_foreshadows_{args.run_id}.jsonl"
    )
    ft_path = Path("foreshadow/honglou/results/cfpg/foreshadow_triggers") / (
        f"honglou_foreshadow_triggers_{args.run_id}.jsonl"
    )
    timeline_path = Path(
        "foreshadow/honglou/results/cfpg/summary_alignments/"
        f"original_80_summary_sentence_timeline_{args.run_id}.jsonl"
    )
    overview_path = Path("foreshadow/honglou/results/cfpg/layers") / (
        f"honglou_cfpg_layers_{args.run_id}.review.md"
    )

    write_jsonl(foreshadows_path, foreshadows)
    write_jsonl(ft_path, fts)
    render_foreshadows(foreshadows_path.with_suffix(".review.md"), foreshadows)
    render_foreshadow_triggers(ft_path.with_suffix(".review.md"), fts)
    render_overview(
        overview_path,
        args.summaries,
        timeline_path,
        args.candidates,
        args.verified_unique,
        foreshadows_path,
        ft_path,
        {
            "summaries": len(summaries),
            "timeline": len(read_jsonl(timeline_path)),
            "foreshadows": len(foreshadows),
            "foreshadow_triggers": len(fts),
            "verified": len(verified_unique),
        },
    )

    print(f"foreshadows={len(foreshadows)} -> {foreshadows_path}")
    print(f"foreshadow_triggers={len(fts)} -> {ft_path}")
    print(f"verified_raw={len(verified)} -> {args.verified}")
    print(f"verified_unique={len(verified_unique)} -> {args.verified_unique}")
    print(f"overview -> {overview_path}")


if __name__ == "__main__":
    main()
