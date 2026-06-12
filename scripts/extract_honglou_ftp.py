"""Extract and verify Foreshadow-Trigger-Payoff triples from summaries."""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from pathlib import Path
from typing import Any

from openai import OpenAI

from cfpg_prompt_utils import PromptTemplate, load_prompt_templates, render_messages

DEFAULT_PROMPT_FILE = Path("prompts/cfpg/honglou_prompts.md")
EXTRACTION_PROMPT_KEY = "candidate_extraction"
VERIFICATION_PROMPT_KEY = "candidate_verification"


def load_dotenv(path: Path = Path(".env")) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def parse_json_object(content: str) -> dict[str, Any]:
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?", "", content).strip()
        content = re.sub(r"```$", "", content).strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", content, flags=re.S)
        if not match:
            raise
        return json.loads(match.group(0))


def chat_json(
    client: OpenAI,
    model: str,
    messages: list[dict[str, str]],
    max_retries: int = 3,
) -> dict[str, Any]:
    last_error: Exception | None = None
    for attempt in range(max_retries):
        try:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0,
                    response_format={"type": "json_object"},
                )
            except Exception:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0,
                )
            return parse_json_object(response.choices[0].message.content or "{}")
        except Exception as exc:
            last_error = exc
            if attempt < max_retries - 1:
                time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"LLM JSON call failed: {last_error}") from last_error


def load_summaries(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def build_timeline(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    timeline: list[dict[str, Any]] = []
    for item in items:
        for sentence in item.get("summary_sentences", []):
            timeline.append(
                {
                    "global_sentence_index": len(timeline),
                    "chapter_index": item["chapter_index"],
                    "chapter_sentence_index": sentence["sentence_index"],
                    "book_id": item["book_id"],
                    "text": sentence["text"],
                    "source_summary_id": item["id"],
                    "source_text_path": item["source_text_path"],
                }
            )
    return timeline


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def render_timeline(timeline: list[dict[str, Any]]) -> str:
    return "\n".join(
        f"[{row['global_sentence_index']:03d}] 第{row['chapter_index']:03d}回."
        f"{row['chapter_sentence_index']}: {row['text']}"
        for row in timeline
    )


def render_notes(items: list[dict[str, Any]]) -> str:
    blocks: list[str] = []
    for item in items:
        lines = [f"第{item['chapter_index']:03d}回 {item['chapter_title']}"]
        for key, label in [
            ("unresolved_setups", "unresolved"),
            ("foreshadow_notes", "foreshadow"),
            ("poem_dream_prophecy_objects", "poem/dream/object"),
        ]:
            values = item.get(key, [])
            for value in values[:8]:
                if not isinstance(value, dict):
                    continue
                text = (
                    value.get("setup")
                    or value.get("note")
                    or value.get("item")
                    or value.get("literal_content")
                    or ""
                )
                evidence = value.get("evidence_quote", "")
                lines.append(f"- {label}: {text} | evidence: {evidence}")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def extraction_messages(
    timeline: list[dict[str, Any]],
    items: list[dict[str, Any]],
    max_candidates: int,
    prompt_template: PromptTemplate,
) -> list[dict[str, str]]:
    return render_messages(
        prompt_template,
        {
            "max_candidates": max_candidates,
            "summary_timeline": render_timeline(timeline),
            "chapter_notes": render_notes(items),
        },
    )


def normalize_candidates(
    payload: dict[str, Any],
    timeline: list[dict[str, Any]],
    summary_source: str,
    extraction_prompt_version: str,
) -> list[dict[str, Any]]:
    by_index = {row["global_sentence_index"]: row for row in timeline}
    rows: list[dict[str, Any]] = []
    for raw in payload.get("candidates", []):
        try:
            f_idx = int(raw["foreshadow_sentence_index"])
            p_idx = int(raw["payoff_sentence_index"])
        except Exception:
            continue
        if f_idx not in by_index or p_idx not in by_index or p_idx <= f_idx:
            continue
        f_row = by_index[f_idx]
        p_row = by_index[p_idx]
        rows.append(
            {
                "candidate_id": f"honglou:original_80:candidate:{len(rows) + 1:06d}",
                "book_id": "红楼梦前80回",
                "summary_source": summary_source,
                "foreshadow_sentence_index": f_idx,
                "payoff_sentence_index": p_idx,
                "foreshadow_chapter_index": f_row["chapter_index"],
                "payoff_chapter_index": p_row["chapter_index"],
                "foreshadow_text": f_row["text"],
                "payoff_text": p_row["text"],
                "proposed_trigger": raw.get("proposed_trigger", {}),
                "relation_description": raw.get("relation_description", ""),
                "foreshadow_type": raw.get("foreshadow_type", "event"),
                "distance_sentences": p_idx - f_idx,
                "distance_chapters": p_row["chapter_index"] - f_row["chapter_index"],
                "stage1_confidence": raw.get("stage1_confidence", 0.0),
                "stage1_rationale": raw.get("stage1_rationale", ""),
                "extraction_prompt_version": extraction_prompt_version,
            }
        )
    return rows


def context_window(timeline: list[dict[str, Any]], center: int, radius: int = 2) -> list[dict[str, Any]]:
    return [
        row
        for row in timeline
        if center - radius <= row["global_sentence_index"] <= center + radius
    ]


def render_window(rows: list[dict[str, Any]]) -> str:
    return "\n".join(
        f"[{row['global_sentence_index']:03d}] 第{row['chapter_index']:03d}回."
        f"{row['chapter_sentence_index']}: {row['text']}"
        for row in rows
    )


def verification_messages(
    candidate: dict[str, Any],
    timeline: list[dict[str, Any]],
    prompt_template: PromptTemplate,
) -> list[dict[str, str]]:
    setup = context_window(timeline, int(candidate["foreshadow_sentence_index"]))
    payoff = context_window(timeline, int(candidate["payoff_sentence_index"]))
    return render_messages(
        prompt_template,
        {
            "candidate_id": candidate["candidate_id"],
            "foreshadow_sentence_index": candidate["foreshadow_sentence_index"],
            "foreshadow_text": candidate["foreshadow_text"],
            "payoff_sentence_index": candidate["payoff_sentence_index"],
            "payoff_text": candidate["payoff_text"],
            "proposed_trigger_json": json.dumps(
                candidate.get("proposed_trigger", {}),
                ensure_ascii=False,
            ),
            "relation_description": candidate.get("relation_description", ""),
            "setup_window": render_window(setup),
            "payoff_window": render_window(payoff),
        },
    )


def verified_triple(
    candidate: dict[str, Any],
    verdict: dict[str, Any],
    verification_prompt_version: str,
) -> dict[str, Any]:
    return {
        "id": candidate["candidate_id"].replace("candidate", "ftp"),
        "dataset": "honglou",
        "book_id": candidate["book_id"],
        "book_title": candidate["book_id"],
        "source": "llm_booksum_style_summary",
        "summary_path": candidate["summary_source"],
        "summary_text": "",
        "foreshadow": {
            "global_sentence_index": candidate["foreshadow_sentence_index"],
            "chapter_index": candidate["foreshadow_chapter_index"],
            "text": candidate["foreshadow_text"],
            "description": verdict.get("foreshadow_description", ""),
            "type": candidate.get("foreshadow_type", "event"),
        },
        "trigger": verdict.get("final_trigger") or candidate.get("proposed_trigger", {}),
        "payoff": {
            "global_sentence_index": candidate["payoff_sentence_index"],
            "chapter_index": candidate["payoff_chapter_index"],
            "text": candidate["payoff_text"],
            "description": verdict.get("payoff_description", ""),
        },
        "distance_sentences": candidate["distance_sentences"],
        "distance_chapters": candidate["distance_chapters"],
        "confidence": candidate.get("stage1_confidence", 0.0),
        "verifier": {
            "setup_validity": bool(verdict.get("setup_validity")),
            "payoff_validity": bool(verdict.get("payoff_validity")),
            "temporal_separation": bool(verdict.get("temporal_separation")),
            "foreshadow_justification": bool(verdict.get("foreshadow_justification")),
            "trigger_validity": bool(verdict.get("trigger_validity")),
            "connection_validity": bool(verdict.get("connection_validity")),
            "rationale": verdict.get("rationale", ""),
            "evidence_sentence_indices": verdict.get("evidence_sentence_indices", []),
            "verification_prompt_version": verification_prompt_version,
        },
    }


def render_review(triples: list[dict[str, Any]], rejected: list[dict[str, Any]], path: Path) -> None:
    lines = ["# HongLou CFPG F-T-P Review", ""]
    lines.extend(["## Accepted Triples", ""])
    if not triples:
        lines.append("- None")
    for triple in triples:
        lines.extend(
            [
                f"### {triple['id']}",
                "",
                f"- Type: `{triple['foreshadow']['type']}`",
                f"- Distance: {triple['distance_sentences']} sentences, {triple['distance_chapters']} chapters",
                f"- F[{triple['foreshadow']['global_sentence_index']}] 第{triple['foreshadow']['chapter_index']:03d}回: {triple['foreshadow']['text']}",
                f"- T: {triple.get('trigger', {}).get('description', '')}",
                f"- P[{triple['payoff']['global_sentence_index']}] 第{triple['payoff']['chapter_index']:03d}回: {triple['payoff']['text']}",
                f"- Rationale: {triple['verifier']['rationale']}",
                "",
            ]
        )
    lines.extend(["## Rejected Candidates", ""])
    if not rejected:
        lines.append("- None")
    for item in rejected:
        candidate = item["candidate"]
        verdict = item["verdict"]
        lines.extend(
            [
                f"### {candidate['candidate_id']}",
                "",
                f"- F[{candidate['foreshadow_sentence_index']}]: {candidate['foreshadow_text']}",
                f"- P[{candidate['payoff_sentence_index']}]: {candidate['payoff_text']}",
                f"- Reason: {verdict.get('rejection_reason') or verdict.get('rationale', '')}",
                "",
            ]
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--summary",
        default="data/processed/cfpg/honglou_booksum/original_80_chapter_summaries.jsonl",
    )
    parser.add_argument("--run-id", default="20260611_deepseek_honglou_original80")
    parser.add_argument("--model", default=None)
    parser.add_argument("--api-base", default=None)
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--max-candidates", type=int, default=12)
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument("--prompt-file", type=Path, default=DEFAULT_PROMPT_FILE)
    args = parser.parse_args()

    load_dotenv()
    model = args.model or os.environ.get("CFPG_EXTRACT_MODEL") or os.environ.get(
        "JUDGE_MODEL", "deepseek-v4-pro"
    )
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    api_base = args.api_base or os.environ.get("OPENAI_BASE_URL")
    if not api_key:
        raise SystemExit("Missing OPENAI_API_KEY or --api-key")

    kwargs: dict[str, Any] = {"api_key": api_key}
    if api_base:
        kwargs["base_url"] = api_base.rstrip("/")
    client = OpenAI(**kwargs)
    prompt_templates = load_prompt_templates(args.prompt_file)
    extraction_prompt = prompt_templates[EXTRACTION_PROMPT_KEY]
    verification_prompt = prompt_templates[VERIFICATION_PROMPT_KEY]

    summary_path = Path(args.summary)
    items = load_summaries(summary_path)
    timeline = build_timeline(items)

    timeline_path = Path(
        "data/processed/cfpg/summary_alignments/"
        f"original_80_summary_sentence_timeline_{args.run_id}.jsonl"
    )
    candidates_path = Path(
        f"data/processed/cfpg/candidates/honglou_candidates_{args.run_id}.jsonl"
    )
    verified_path = Path(
        f"data/processed/cfpg/verified/honglou_ftp_triples_{args.run_id}.jsonl"
    )
    rejected_path = Path(
        "data/processed/cfpg/verified/"
        f"honglou_rejected_candidates_{args.run_id}.jsonl"
    )
    review_path = Path(
        f"data/processed/cfpg/verified/honglou_ftp_triples_{args.run_id}.review.md"
    )
    output_dir = Path("outputs/cfpg") / args.run_id
    output_dir.mkdir(parents=True, exist_ok=True)

    write_jsonl(timeline_path, timeline)
    print(f"wrote {timeline_path}", flush=True)

    print("extracting candidates", flush=True)
    raw_candidates = chat_json(
        client,
        model,
        extraction_messages(timeline, items, args.max_candidates, extraction_prompt),
        max_retries=args.max_retries,
    )
    candidates = normalize_candidates(
        raw_candidates,
        timeline,
        str(summary_path),
        extraction_prompt.version,
    )
    write_jsonl(candidates_path, candidates)
    (output_dir / "candidate_extraction_report.json").write_text(
        json.dumps(
            {
                "run_id": args.run_id,
                "model": model,
                "api_base": api_base,
                "prompt_file": str(args.prompt_file),
                "prompt_key": EXTRACTION_PROMPT_KEY,
                "prompt_version": extraction_prompt.version,
                "summary": str(summary_path),
                "timeline": str(timeline_path),
                "candidate_count": len(candidates),
                "raw": raw_candidates,
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"wrote {candidates_path}", flush=True)

    verified: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    verdicts: list[dict[str, Any]] = []
    for candidate in candidates:
        print(f"verifying {candidate['candidate_id']}", flush=True)
        verdict = chat_json(
            client,
            model,
            verification_messages(candidate, timeline, verification_prompt),
            max_retries=args.max_retries,
        )
        verdicts.append({"candidate_id": candidate["candidate_id"], **verdict})
        if verdict.get("accepted"):
            verified.append(verified_triple(candidate, verdict, verification_prompt.version))
        else:
            rejected.append({"candidate": candidate, "verdict": verdict})

    write_jsonl(verified_path, verified)
    write_jsonl(rejected_path, rejected)
    render_review(verified, rejected, review_path)
    (output_dir / "verification_report.json").write_text(
        json.dumps(
            {
                "run_id": args.run_id,
                "model": model,
                "api_base": api_base,
                "prompt_file": str(args.prompt_file),
                "prompt_key": VERIFICATION_PROMPT_KEY,
                "prompt_version": verification_prompt.version,
                "candidate_count": len(candidates),
                "verified_count": len(verified),
                "rejected_count": len(rejected),
                "verified": str(verified_path),
                "rejected": str(rejected_path),
                "review": str(review_path),
                "verdicts": verdicts,
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"wrote {verified_path}", flush=True)
    print(f"wrote {rejected_path}", flush=True)
    print(f"wrote {review_path}", flush=True)


if __name__ == "__main__":
    main()
