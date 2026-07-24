"""Extract and verify Foreshadow-Trigger-Payoff triples from summaries."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

from openai import OpenAI

COMMON_DIR = Path(__file__).resolve().parents[2] / "common"
if str(COMMON_DIR) not in sys.path:
    sys.path.insert(0, str(COMMON_DIR))

from cfpg_prompt_utils import PromptTemplate, load_prompt_templates, render_messages

DEFAULT_PROMPT_FILE = Path("foreshadow/honglou/prompts/honglou_prompts.md")
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
    timeout: float | None = None,
    max_tokens: int | None = None,
) -> dict[str, Any]:
    last_error: Exception | None = None
    request_kwargs: dict[str, Any] = {}
    if timeout is not None:
        request_kwargs["timeout"] = timeout
    if max_tokens is not None and max_tokens > 0:
        request_kwargs["max_tokens"] = max_tokens
    for attempt in range(max_retries):
        try:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0,
                    response_format={"type": "json_object"},
                    **request_kwargs,
                )
            except Exception:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0,
                    **request_kwargs,
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


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


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


def timeline_windows(
    timeline: list[dict[str, Any]],
    window_size: int,
    stride: int,
) -> list[list[dict[str, Any]]]:
    if not timeline:
        return []
    if window_size <= 0 or window_size >= len(timeline):
        return [timeline]
    stride = max(1, stride)
    windows: list[list[dict[str, Any]]] = []
    start = 0
    while start < len(timeline):
        end = min(start + window_size, len(timeline))
        windows.append(timeline[start:end])
        if end == len(timeline):
            break
        start += stride
    return windows


def items_for_window(
    items: list[dict[str, Any]],
    window: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    chapters = {row["chapter_index"] for row in window}
    return [item for item in items if item["chapter_index"] in chapters]


def normalize_candidates(
    payload: dict[str, Any],
    timeline: list[dict[str, Any]],
    summary_source: str,
    extraction_prompt_version: str,
    extraction_window: dict[str, Any] | None = None,
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
                "extraction_window": extraction_window or {},
            }
        )
    return rows


def reassign_candidate_ids(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, candidate in enumerate(candidates, start=1):
        row = dict(candidate)
        row["candidate_id"] = f"honglou:original_80:candidate:{index:06d}"
        rows.append(row)
    return rows


def dedupe_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[int, int]] = set()
    rows: list[dict[str, Any]] = []
    for candidate in sorted(
        candidates,
        key=lambda row: (
            row["foreshadow_sentence_index"],
            row["payoff_sentence_index"],
            -float(row.get("stage1_confidence") or 0.0),
        ),
    ):
        key = (
            int(candidate["foreshadow_sentence_index"]),
            int(candidate["payoff_sentence_index"]),
        )
        if key in seen:
            continue
        seen.add(key)
        rows.append(candidate)
    return reassign_candidate_ids(rows)


def summarize_candidate_windows(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_window: dict[int, dict[str, Any]] = {}
    for candidate in candidates:
        window = candidate.get("extraction_window") or {}
        window_index = window.get("window_index")
        if not isinstance(window_index, int):
            continue
        row = by_window.setdefault(
            window_index,
            {
                "window_index": window_index,
                "window_count": window.get("window_count"),
                "start_sentence_index": window.get("start_sentence_index"),
                "end_sentence_index": window.get("end_sentence_index"),
                "chapter_indices": window.get("chapter_indices", []),
                "deduped_candidate_count": 0,
            },
        )
        row["deduped_candidate_count"] += 1
    return [by_window[key] for key in sorted(by_window)]


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


def dedupe_triples(triples: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[int, int]] = set()
    rows: list[dict[str, Any]] = []
    for triple in triples:
        key = (
            int(triple["foreshadow"]["global_sentence_index"]),
            int(triple["payoff"]["global_sentence_index"]),
        )
        if key in seen:
            continue
        seen.add(key)
        rows.append(triple)
    return rows


def candidate_id_from_triple(triple: dict[str, Any]) -> str:
    return str(triple.get("id", "")).replace(":ftp:", ":candidate:")


def has_valid_rejection(row: dict[str, Any]) -> bool:
    return row.get("verdict", {}).get("accepted") is False


def verify_candidate_with_valid_verdict(
    client: OpenAI,
    model: str,
    candidate: dict[str, Any],
    timeline: list[dict[str, Any]],
    verification_prompt: PromptTemplate,
    max_retries: int,
    timeout: float,
    max_output_tokens: int,
) -> dict[str, Any]:
    last_verdict: dict[str, Any] = {}
    last_error: Exception | None = None
    for _ in range(max_retries):
        try:
            verdict = chat_json(
                client,
                model,
                verification_messages(candidate, timeline, verification_prompt),
                max_retries=1,
                timeout=timeout,
                max_tokens=max_output_tokens,
            )
        except Exception as exc:
            last_error = exc
            time.sleep(1)
            continue
        last_verdict = verdict
        if isinstance(verdict.get("accepted"), bool):
            return verdict
        last_error = ValueError(
            "verifier did not return a valid boolean `accepted` field: "
            f"{json.dumps(last_verdict, ensure_ascii=False)[:500]}"
        )
        time.sleep(1)
    raise RuntimeError(f"verifier failed after retries: {last_error}") from last_error


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--summary",
        default="foreshadow/honglou/results/cfpg/honglou_booksum/original_80_chapter_summaries.jsonl",
    )
    parser.add_argument("--run-id", default="20260611_deepseek_honglou_original80")
    parser.add_argument("--model", default=None)
    parser.add_argument("--api-base", default=None)
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--max-candidates", type=int, default=12)
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument("--window-size", type=int, default=80)
    parser.add_argument("--window-stride", type=int, default=40)
    parser.add_argument("--max-windows", type=int, default=0)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--max-output-tokens", type=int, default=2048)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--skip-verification", action="store_true")
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
    kwargs["timeout"] = args.timeout
    client = OpenAI(**kwargs)
    prompt_templates = load_prompt_templates(args.prompt_file)
    extraction_prompt = prompt_templates[EXTRACTION_PROMPT_KEY]
    verification_prompt = prompt_templates[VERIFICATION_PROMPT_KEY]

    summary_path = Path(args.summary)
    items = load_summaries(summary_path)
    timeline = build_timeline(items)

    timeline_path = Path(
        "foreshadow/honglou/results/cfpg/summary_alignments/"
        f"original_80_summary_sentence_timeline_{args.run_id}.jsonl"
    )
    candidates_path = Path(
        f"foreshadow/honglou/results/cfpg/candidates/honglou_candidates_{args.run_id}.jsonl"
    )
    verified_path = Path(
        f"foreshadow/honglou/results/cfpg/verified/honglou_ftp_triples_{args.run_id}.jsonl"
    )
    verified_unique_path = Path(
        "foreshadow/honglou/results/cfpg/verified/"
        f"honglou_ftp_triples_{args.run_id}.unique.jsonl"
    )
    rejected_path = Path(
        "foreshadow/honglou/results/cfpg/verified/"
        f"honglou_rejected_candidates_{args.run_id}.jsonl"
    )
    review_path = Path(
        f"foreshadow/honglou/results/cfpg/verified/honglou_ftp_triples_{args.run_id}.review.md"
    )
    unique_review_path = Path(
        "foreshadow/honglou/results/cfpg/verified/"
        f"honglou_ftp_triples_{args.run_id}.unique.review.md"
    )
    output_dir = Path("foreshadow/honglou/results/cfpg_reports") / args.run_id
    output_dir.mkdir(parents=True, exist_ok=True)

    write_jsonl(timeline_path, timeline)
    print(f"wrote {timeline_path}", flush=True)

    window_reports: list[dict[str, Any]] = []
    candidate_report_source = "model_extraction"
    if candidates_path.exists() and not args.force:
        candidates = read_jsonl(candidates_path)
        window_reports = summarize_candidate_windows(candidates)
        candidate_report_source = "existing_candidates"
        print(f"using existing {candidates_path} ({len(candidates)} candidates)", flush=True)
    else:
        print("extracting candidates", flush=True)
        all_candidates: list[dict[str, Any]] = []
        windows = timeline_windows(timeline, args.window_size, args.window_stride)
        if args.max_windows > 0:
            windows = windows[: args.max_windows]
        for window_index, window in enumerate(windows, start=1):
            first = window[0]["global_sentence_index"]
            last = window[-1]["global_sentence_index"]
            print(
                f"extracting window {window_index}/{len(windows)} "
                f"S[{first}-{last}]",
                flush=True,
            )
            raw_candidates = chat_json(
                client,
                model,
                extraction_messages(
                    window,
                    items_for_window(items, window),
                    args.max_candidates,
                    extraction_prompt,
                ),
                max_retries=args.max_retries,
                timeout=args.timeout,
                max_tokens=args.max_output_tokens,
            )
            extraction_window = {
                "window_index": window_index,
                "window_count": len(windows),
                "start_sentence_index": first,
                "end_sentence_index": last,
                "chapter_indices": sorted({row["chapter_index"] for row in window}),
            }
            rows = normalize_candidates(
                raw_candidates,
                timeline,
                str(summary_path),
                extraction_prompt.version,
                extraction_window=extraction_window,
            )
            all_candidates.extend(rows)
            candidates = dedupe_candidates(all_candidates)
            write_jsonl(candidates_path, candidates)
            window_reports.append(
                {
                    **extraction_window,
                    "raw_candidate_count": len(raw_candidates.get("candidates", [])),
                    "normalized_candidate_count": len(rows),
                    "deduped_candidate_count_so_far": len(candidates),
                    "raw": raw_candidates,
                }
            )
        candidates = dedupe_candidates(all_candidates)
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
                "window_size": args.window_size,
                "window_stride": args.window_stride,
                "report_source": candidate_report_source,
                "windows": window_reports,
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"wrote {candidates_path}", flush=True)

    if args.skip_verification:
        print("skipping verification", flush=True)
        return

    verified: list[dict[str, Any]] = [] if args.force else read_jsonl(verified_path)
    existing_rejected = [] if args.force else read_jsonl(rejected_path)
    rejected: list[dict[str, Any]] = [
        row for row in existing_rejected if has_valid_rejection(row)
    ]
    undecided_existing_count = len(existing_rejected) - len(rejected)
    completed = {candidate_id_from_triple(row) for row in verified}
    completed.update(
        row.get("candidate", {}).get("candidate_id", "")
        for row in rejected
        if row.get("candidate", {}).get("candidate_id")
    )
    skipped_existing_count = 0
    verdicts: list[dict[str, Any]] = []
    for candidate in candidates:
        if candidate["candidate_id"] in completed:
            print(f"skipping verified {candidate['candidate_id']}", flush=True)
            skipped_existing_count += 1
            continue
        print(f"verifying {candidate['candidate_id']}", flush=True)
        verdict = verify_candidate_with_valid_verdict(
            client,
            model,
            candidate,
            timeline,
            verification_prompt,
            args.max_retries,
            args.timeout,
            args.max_output_tokens,
        )
        verdicts.append({"candidate_id": candidate["candidate_id"], **verdict})
        if verdict.get("accepted"):
            verified.append(verified_triple(candidate, verdict, verification_prompt.version))
        else:
            rejected.append({"candidate": candidate, "verdict": verdict})
        write_jsonl(verified_path, verified)
        write_jsonl(rejected_path, rejected)
        unique = dedupe_triples(verified)
        write_jsonl(verified_unique_path, unique)
        render_review(verified, rejected, review_path)
        render_review(unique, rejected, unique_review_path)

    write_jsonl(verified_path, verified)
    write_jsonl(rejected_path, rejected)
    unique = dedupe_triples(verified)
    write_jsonl(verified_unique_path, unique)
    render_review(verified, rejected, review_path)
    render_review(unique, rejected, unique_review_path)
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
                "verified_unique_count": len(unique),
                "rejected_count": len(rejected),
                "processed_this_run": len(verdicts),
                "skipped_existing_candidates": skipped_existing_count,
                "undecided_existing_candidates_reprocessed": undecided_existing_count,
                "verified": str(verified_path),
                "verified_unique": str(verified_unique_path),
                "rejected": str(rejected_path),
                "review": str(review_path),
                "unique_review": str(unique_review_path),
                "verdicts": verdicts,
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"wrote {verified_path}", flush=True)
    print(f"wrote {verified_unique_path}", flush=True)
    print(f"wrote {rejected_path}", flush=True)
    print(f"wrote {review_path}", flush=True)


if __name__ == "__main__":
    main()
