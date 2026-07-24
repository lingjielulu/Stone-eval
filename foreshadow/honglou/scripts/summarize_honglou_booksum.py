"""Generate BookSum-style HongLou chapter summaries."""

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
PROMPT_KEY = "booksum_chapter_summary"


def load_dotenv(path: Path = Path(".env")) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def chapter_title_and_body(text: str) -> tuple[str, str]:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip():
            return line.strip(), "\n".join(lines[index + 1 :]).strip()
    return "", text.strip()


def split_sentences(text: str) -> list[dict[str, Any]]:
    pieces = re.split(r"(?<=[。！？；])\s*", text.strip())
    sentences = [piece.strip() for piece in pieces if piece.strip()]
    return [
        {
            "sentence_index": index,
            "text": sentence,
            "source_span_hint": "",
        }
        for index, sentence in enumerate(sentences)
    ]


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


def summarize_chapter(
    client: OpenAI,
    model: str,
    chapter_path: Path,
    chapter_index: int,
    max_retries: int,
    prompt_template: PromptTemplate,
) -> dict[str, Any]:
    raw = chapter_path.read_text(encoding="utf-8")
    title, body = chapter_title_and_body(raw)
    messages = render_messages(
        prompt_template,
        {
            "chapter_title": title,
            "chapter_text": body,
        },
    )
    last_error: Exception | None = None
    for attempt in range(max_retries):
        try:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.2,
                    response_format={"type": "json_object"},
                )
            except Exception:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.2,
                )
            content = response.choices[0].message.content or "{}"
            payload = parse_json_object(content)
            summary = str(payload.get("chapter_summary", "")).strip()
            return {
                "id": f"honglou:original_80:chapter_{chapter_index:03d}",
                "dataset": "honglou",
                "book_id": "红楼梦前80回",
                "book_kind": "original",
                "chapter_index": chapter_index,
                "chapter_title": title,
                "source_text_path": str(chapter_path),
                "summary": summary,
                "summary_sentences": split_sentences(summary),
                "key_events": payload.get("key_events", []),
                "character_state_changes": payload.get("character_state_changes", []),
                "unresolved_setups": payload.get("unresolved_setups", []),
                "foreshadow_notes": payload.get("foreshadow_notes", []),
                "poem_dream_prophecy_objects": payload.get(
                    "poem_dream_prophecy_objects", []
                ),
                "warnings": payload.get("warnings", []),
                "model": model,
                "prompt_version": prompt_template.version,
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            }
        except Exception as exc:
            last_error = exc
            if attempt < max_retries - 1:
                time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"Failed to summarize {chapter_path}: {last_error}") from last_error


def load_existing_ids(output_path: Path) -> set[str]:
    if not output_path.exists():
        return set()
    ids: set[str] = set()
    for line in output_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            ids.add(json.loads(line)["id"])
        except Exception:
            continue
    return ids


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--chapters-dir",
        default="resources/corpora/hongloumeng/prepared/chapters/original",
    )
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=80)
    parser.add_argument(
        "--output",
        default=(
            "foreshadow/honglou/results/cfpg/honglou_booksum/"
            "original_80_chapter_summaries.jsonl"
        ),
    )
    parser.add_argument(
        "--report",
        default="foreshadow/honglou/results/cfpg_reports/honglou_summary_original80/report.json",
    )
    parser.add_argument("--model", default=None)
    parser.add_argument("--api-base", default=None)
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument("--prompt-file", type=Path, default=DEFAULT_PROMPT_FILE)
    args = parser.parse_args()

    load_dotenv()
    model = args.model or os.environ.get("CFPG_SUMMARY_MODEL") or os.environ.get(
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
    prompt_template = prompt_templates[PROMPT_KEY]

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    existing_ids = set() if args.force else load_existing_ids(output_path)

    completed: list[dict[str, Any]] = []
    with output_path.open("a" if not args.force else "w", encoding="utf-8") as out:
        for chapter_index in range(args.start, args.end + 1):
            chapter_id = f"honglou:original_80:chapter_{chapter_index:03d}"
            if chapter_id in existing_ids:
                completed.append({"id": chapter_id, "status": "skipped_existing"})
                print(f"skip existing {chapter_id}", flush=True)
                continue
            chapter_path = Path(args.chapters_dir) / f"chapter_{chapter_index:03d}.txt"
            if not chapter_path.exists():
                raise FileNotFoundError(chapter_path)
            print(f"summarizing {chapter_id} with {model}", flush=True)
            item = summarize_chapter(
                client=client,
                model=model,
                chapter_path=chapter_path,
                chapter_index=chapter_index,
                max_retries=args.max_retries,
                prompt_template=prompt_template,
            )
            out.write(json.dumps(item, ensure_ascii=False) + "\n")
            out.flush()
            completed.append(
                {
                    "id": item["id"],
                    "status": "completed",
                    "summary_sentences": len(item["summary_sentences"]),
                    "unresolved_setups": len(item["unresolved_setups"]),
                    "foreshadow_notes": len(item["foreshadow_notes"]),
                }
            )

    report = {
        "task": "honglou_booksum_style_summary_original80",
        "prompt_file": str(args.prompt_file),
        "prompt_key": PROMPT_KEY,
        "prompt_version": prompt_template.version,
        "model": model,
        "api_base": api_base,
        "start": args.start,
        "end": args.end,
        "output": str(output_path),
        "completed": completed,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {output_path}", flush=True)
    print(f"wrote {report_path}", flush=True)


if __name__ == "__main__":
    main()
