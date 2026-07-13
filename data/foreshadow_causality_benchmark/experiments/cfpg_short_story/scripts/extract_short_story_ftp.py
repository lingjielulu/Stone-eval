"""Initial CFPG-style F-T-P extraction for short stories.

Prompts live in the experiment's ``prompts/short_story_prompts.md``. This script only
loads templates and fills the explicit placeholders.
"""

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


REPO_ROOT = Path(__file__).resolve().parents[5]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from cfpg_prompt_utils import PromptTemplate, load_prompt_templates, render_messages  # noqa: E402


EXPERIMENT_ROOT = Path(
    "data/foreshadow_causality_benchmark/experiments/cfpg_short_story"
)
DEFAULT_PROMPT_FILE = EXPERIMENT_ROOT / "prompts/short_story_prompts.md"
EXTRACTION_PROMPT_KEY = "short_story_candidate_extraction"
VERIFICATION_PROMPT_KEY = "short_story_candidate_verification"
PARAGRAPH_RE = re.compile(r"^\[(P\d{4})\]\s+(.*)$", re.S)
SPAN_RE = re.compile(r"P(\d{4})")


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
    max_retries: int,
    timeout: float,
    max_tokens: int,
) -> dict[str, Any]:
    last_error: Exception | None = None
    request_kwargs: dict[str, Any] = {"timeout": timeout}
    if max_tokens > 0:
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


def extract_payload_with_candidates(
    client: OpenAI,
    model: str,
    messages: list[dict[str, str]],
    max_retries: int,
    timeout: float,
    max_tokens: int,
) -> dict[str, Any]:
    last_payload: dict[str, Any] = {}
    repair_suffix = (
        "上一次输出缺少顶层 candidates 数组。请严格重做，只输出一个 JSON object，"
        "格式必须是 {\"candidates\": [...]}；如果没有候选，也必须输出 {\"candidates\": []}。"
    )
    for attempt in range(max_retries):
        active_messages = messages
        if attempt > 0:
            active_messages = [
                *messages,
                {"role": "assistant", "content": json.dumps(last_payload, ensure_ascii=False)},
                {"role": "user", "content": repair_suffix},
            ]
        last_payload = chat_json(
            client,
            model,
            active_messages,
            max_retries=1,
            timeout=timeout,
            max_tokens=max_tokens,
        )
        if isinstance(last_payload.get("candidates"), list):
            return last_payload
        time.sleep(1)
    raise RuntimeError(
        "extractor did not return a valid `candidates` array: "
        f"{json.dumps(last_payload, ensure_ascii=False)[:500]}"
    )


def verify_candidate_with_valid_verdict(
    client: OpenAI,
    model: str,
    messages: list[dict[str, str]],
    max_retries: int,
    timeout: float,
    max_tokens: int,
) -> dict[str, Any]:
    last_verdict: dict[str, Any] = {}
    repair_suffix = (
        "上一次输出缺少 boolean accepted 字段。请严格重做，只输出一个 JSON object，"
        "其中 accepted 必须是 true 或 false。"
    )
    for attempt in range(max_retries):
        active_messages = messages
        if attempt > 0:
            active_messages = [
                *messages,
                {"role": "assistant", "content": json.dumps(last_verdict, ensure_ascii=False)},
                {"role": "user", "content": repair_suffix},
            ]
        last_verdict = chat_json(
            client,
            model,
            active_messages,
            max_retries=1,
            timeout=timeout,
            max_tokens=max_tokens,
        )
        if isinstance(last_verdict.get("accepted"), bool):
            return last_verdict
        time.sleep(1)
    raise RuntimeError(
        "verifier did not return a valid boolean `accepted` field: "
        f"{json.dumps(last_verdict, ensure_ascii=False)[:500]}"
    )


def parse_normalized_text(path: Path) -> tuple[str, list[dict[str, Any]]]:
    title = path.stem
    paragraphs: list[dict[str, Any]] = []
    for block in path.read_text(encoding="utf-8").split("\n\n"):
        block = block.strip()
        if not block:
            continue
        if block.startswith("# "):
            title = block[2:].strip() or title
            continue
        match = PARAGRAPH_RE.match(block)
        if not match:
            continue
        paragraph_id = match.group(1)
        paragraphs.append(
            {
                "paragraph_id": paragraph_id,
                "paragraph_index": int(paragraph_id[1:]),
                "text": match.group(2).strip(),
            }
        )
    return title, paragraphs


def select_paragraphs(
    paragraphs: list[dict[str, Any]],
    start: int,
    end: int,
    max_paragraphs: int,
) -> list[dict[str, Any]]:
    selected = paragraphs
    if start > 0:
        selected = [row for row in selected if row["paragraph_index"] >= start]
    if end > 0:
        selected = [row for row in selected if row["paragraph_index"] <= end]
    if max_paragraphs > 0:
        selected = selected[:max_paragraphs]
    return selected


def render_paragraph_timeline(paragraphs: list[dict[str, Any]], max_chars: int = 0) -> str:
    lines: list[str] = []
    for row in paragraphs:
        text = row["text"]
        if max_chars > 0 and len(text) > max_chars:
            text = text[:max_chars].rstrip() + "..."
        lines.append(f"[{row['paragraph_id']}] {text}")
    return "\n\n".join(lines)


def read_annotation_context(path: Path, max_chars: int) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    if max_chars <= 0 or len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "\n..."


def span_start(span: str) -> int | None:
    match = SPAN_RE.search(span or "")
    if not match:
        return None
    return int(match.group(1))


def span_text(span: str, by_id: dict[str, dict[str, Any]]) -> str:
    ids = SPAN_RE.findall(span or "")
    if not ids:
        return ""
    start = int(ids[0])
    end = int(ids[-1])
    rows = [by_id[f"P{index:04d}"]["text"] for index in range(start, end + 1) if f"P{index:04d}" in by_id]
    return "\n\n".join(rows)


def context_window(
    paragraphs: list[dict[str, Any]],
    span: str,
    radius: int,
) -> list[dict[str, Any]]:
    start = span_start(span)
    if start is None:
        return []
    return [
        row
        for row in paragraphs
        if start - radius <= row["paragraph_index"] <= start + radius
    ]


def extraction_messages(
    story_id: str,
    title: str,
    language: str,
    paragraphs: list[dict[str, Any]],
    zh_paragraphs: list[dict[str, Any]],
    annotation_context: str,
    max_candidates: int,
    prompt_template: PromptTemplate,
    max_paragraph_chars: int,
) -> list[dict[str, str]]:
    return render_messages(
        prompt_template,
        {
            "story_id": story_id,
            "story_title": title,
            "language": language,
            "max_candidates": max_candidates,
            "paragraph_timeline": render_paragraph_timeline(paragraphs, max_paragraph_chars),
            "zh_paragraph_timeline": render_paragraph_timeline(zh_paragraphs, max_paragraph_chars) if zh_paragraphs else "(none)",
            "annotation_context": annotation_context or "(none)",
        },
    )


def normalize_candidates(
    payload: dict[str, Any],
    story_id: str,
    paragraphs: list[dict[str, Any]],
    prompt_version: str,
    source_text_path: Path,
) -> list[dict[str, Any]]:
    by_id = {row["paragraph_id"]: row for row in paragraphs}
    rows: list[dict[str, Any]] = []
    for raw in payload.get("candidates", []):
        f_span = str(raw.get("foreshadow_span", "")).strip()
        p_span = str(raw.get("payoff_span", "")).strip()
        f_start = span_start(f_span)
        p_start = span_start(p_span)
        if f_start is None or p_start is None or p_start <= f_start:
            continue
        row = {
            "candidate_id": f"{story_id}:ftp_candidate:{len(rows) + 1:06d}",
            "story_id": story_id,
            "source_text_path": str(source_text_path),
            "foreshadow_span": f_span,
            "payoff_span": p_span,
            "foreshadow_text": span_text(f_span, by_id),
            "payoff_text": span_text(p_span, by_id),
            "foreshadow_summary": raw.get("foreshadow_summary", ""),
            "payoff_summary": raw.get("payoff_summary", ""),
            "proposed_trigger": raw.get("proposed_trigger", {}),
            "relation_description": raw.get("relation_description", ""),
            "primary_type": raw.get("primary_type") or raw.get("foreshadow_type", "event"),
            "narrative_function": raw.get("narrative_function", "direct_setup"),
            "legacy_foreshadow_type": raw.get("foreshadow_type"),
            "payoff_type": raw.get("payoff_type", "literal"),
            "distance_paragraphs": p_start - f_start,
            "stage1_confidence": raw.get("stage1_confidence", "low"),
            "stage1_rationale": raw.get("stage1_rationale", ""),
            "extraction_prompt_version": prompt_version,
        }
        rows.append(row)
    return rows


def verification_messages(
    story_id: str,
    title: str,
    paragraphs: list[dict[str, Any]],
    candidate: dict[str, Any],
    prompt_template: PromptTemplate,
) -> list[dict[str, str]]:
    return render_messages(
        prompt_template,
        {
            "candidate_id": candidate["candidate_id"],
            "story_id": story_id,
            "story_title": title,
            "foreshadow_span": candidate["foreshadow_span"],
            "foreshadow_text": candidate.get("foreshadow_text", ""),
            "payoff_span": candidate["payoff_span"],
            "payoff_text": candidate.get("payoff_text", ""),
            "proposed_trigger_json": json.dumps(candidate.get("proposed_trigger", {}), ensure_ascii=False),
            "relation_description": candidate.get("relation_description", ""),
            "setup_window": render_paragraph_timeline(context_window(paragraphs, candidate["foreshadow_span"], 2)),
            "payoff_window": render_paragraph_timeline(context_window(paragraphs, candidate["payoff_span"], 2)),
        },
    )


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def render_prompt_preview(path: Path, messages: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Short Story CFPG Prompt Preview", ""]
    for message in messages:
        lines.extend([f"## {message['role']}", "", "```text", message["content"], "```", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def render_review(path: Path, candidates: list[dict[str, Any]], verified: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Short Story CFPG Candidate Review", ""]
    lines.extend(["## Candidates", ""])
    if not candidates:
        lines.append("- None")
    for candidate in candidates:
        lines.extend(
            [
                f"### {candidate['candidate_id']}",
                "",
                f"- Type: `{candidate['primary_type']}` / function "
                f"`{candidate['narrative_function']}` / payoff `{candidate['payoff_type']}`",
                f"- Distance: {candidate['distance_paragraphs']} paragraphs",
                f"- F {candidate['foreshadow_span']}: {candidate['foreshadow_summary']}",
                f"- T: {candidate.get('proposed_trigger', {}).get('description', '')}",
                f"- P {candidate['payoff_span']}: {candidate['payoff_summary']}",
                f"- Rationale: {candidate.get('stage1_rationale', '')}",
                "",
            ]
        )
    if verified:
        lines.extend(["## Verification", ""])
        for item in verified:
            verdict = item["verdict"]
            lines.extend(
                [
                    f"### {item['candidate']['candidate_id']}",
                    "",
                    f"- accepted: `{verdict.get('accepted')}`",
                    f"- rationale: {verdict.get('rationale', '')}",
                    f"- rejection: {verdict.get('rejection_reason', '')}",
                    "",
                ]
            )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract short-story F-T-P candidates")
    parser.add_argument("story_id")
    parser.add_argument("--normalized-dir", default="data/foreshadow_causality_benchmark/novels/normalized_texts")
    parser.add_argument("--zh-dir", default="data/foreshadow_causality_benchmark/novels/normalized_texts_zh")
    parser.add_argument("--annotations-dir", default="data/foreshadow_causality_benchmark/novels/annotations")
    parser.add_argument("--out-dir", default=str(EXPERIMENT_ROOT / "results/extraction"))
    parser.add_argument("--prompt-file", type=Path, default=DEFAULT_PROMPT_FILE)
    parser.add_argument("--model", default=None)
    parser.add_argument("--api-base", default=None)
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--language", default="auto")
    parser.add_argument("--max-candidates", type=int, default=8)
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--max-output-tokens", type=int, default=2048)
    parser.add_argument("--max-paragraphs", type=int, default=0)
    parser.add_argument("--start-paragraph", type=int, default=0)
    parser.add_argument("--end-paragraph", type=int, default=0)
    parser.add_argument("--max-paragraph-chars", type=int, default=0)
    parser.add_argument("--include-zh", action="store_true")
    parser.add_argument("--include-existing-annotations", action="store_true")
    parser.add_argument("--annotation-context-chars", type=int, default=6000)
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    load_dotenv()
    run_id = args.run_id or time.strftime("%Y%m%d_short_story_cfpg")
    story_path = Path(args.normalized_dir) / f"{args.story_id}.txt"
    if not story_path.exists():
        raise SystemExit(f"missing story text: {story_path}")
    title, all_paragraphs = parse_normalized_text(story_path)
    paragraphs = select_paragraphs(
        all_paragraphs,
        args.start_paragraph,
        args.end_paragraph,
        args.max_paragraphs,
    )
    if not paragraphs:
        raise SystemExit("no paragraphs selected")

    zh_paragraphs: list[dict[str, Any]] = []
    zh_path = Path(args.zh_dir) / f"{args.story_id}.txt"
    if args.include_zh and zh_path.exists():
        _, parsed_zh = parse_normalized_text(zh_path)
        zh_by_index = {row["paragraph_index"]: row for row in parsed_zh}
        zh_paragraphs = [
            zh_by_index[row["paragraph_index"]]
            for row in paragraphs
            if row["paragraph_index"] in zh_by_index
        ]

    annotation_context = ""
    if args.include_existing_annotations:
        annotation_context = read_annotation_context(
            Path(args.annotations_dir) / f"{args.story_id}.yaml",
            args.annotation_context_chars,
        )

    prompt_templates = load_prompt_templates(args.prompt_file)
    extraction_prompt = prompt_templates[EXTRACTION_PROMPT_KEY]
    verification_prompt = prompt_templates[VERIFICATION_PROMPT_KEY]
    language = args.language
    if language == "auto":
        language = "zh" if args.story_id in {"medicine", "cricket", "rashomon"} else "en"

    messages = extraction_messages(
        story_id=args.story_id,
        title=title,
        language=language,
        paragraphs=paragraphs,
        zh_paragraphs=zh_paragraphs,
        annotation_context=annotation_context,
        max_candidates=args.max_candidates,
        prompt_template=extraction_prompt,
        max_paragraph_chars=args.max_paragraph_chars,
    )

    out_dir = Path(args.out_dir)
    preview_path = out_dir / "reviews" / f"{args.story_id}_prompt_preview_{run_id}.md"
    render_prompt_preview(preview_path, messages)
    print(f"wrote {preview_path}")
    if args.dry_run:
        return

    model = args.model or os.environ.get("CFPG_EXTRACT_MODEL") or os.environ.get("JUDGE_MODEL", "deepseek-v4-pro")
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    api_base = args.api_base or os.environ.get("OPENAI_BASE_URL")
    if not api_key:
        raise SystemExit("Missing OPENAI_API_KEY or --api-key")

    kwargs: dict[str, Any] = {"api_key": api_key, "timeout": args.timeout}
    if api_base:
        kwargs["base_url"] = api_base.rstrip("/")
    client = OpenAI(**kwargs)

    payload = extract_payload_with_candidates(
        client,
        model,
        messages,
        max_retries=args.max_retries,
        timeout=args.timeout,
        max_tokens=args.max_output_tokens,
    )
    raw_path = out_dir / "candidates" / f"{args.story_id}_ftp_raw_{run_id}.json"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {raw_path}")

    candidates = normalize_candidates(payload, args.story_id, paragraphs, extraction_prompt.version, story_path)
    candidates_path = out_dir / "candidates" / f"{args.story_id}_ftp_candidates_{run_id}.jsonl"
    write_jsonl(candidates_path, candidates)
    print(f"wrote {candidates_path}")

    verified: list[dict[str, Any]] = []
    if args.verify:
        for candidate in candidates:
            verdict = verify_candidate_with_valid_verdict(
                client,
                model,
                verification_messages(args.story_id, title, paragraphs, candidate, verification_prompt),
                max_retries=args.max_retries,
                timeout=args.timeout,
                max_tokens=args.max_output_tokens,
            )
            verified.append(
                {
                    "candidate": candidate,
                    "verdict": verdict,
                    "verification_prompt_version": verification_prompt.version,
                }
            )
        verified_path = out_dir / "verified" / f"{args.story_id}_ftp_verified_{run_id}.jsonl"
        write_jsonl(verified_path, verified)
        print(f"wrote {verified_path}")

    review_path = out_dir / "reviews" / f"{args.story_id}_ftp_review_{run_id}.md"
    render_review(review_path, candidates, verified)
    print(f"wrote {review_path}")


if __name__ == "__main__":
    main()
