"""LongStoryEval-style summary and evaluation helpers."""

from __future__ import annotations

import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from openai import OpenAI


DEFAULT_PROMPT_ROOT = Path("lib/LongStoryEval")
DEFAULT_SUMMARY_PROMPTS = DEFAULT_PROMPT_ROOT / "summarize_book" / "prompts"
DEFAULT_EVAL_PROMPT = (
    DEFAULT_PROMPT_ROOT / "evaluation_codes" / "prompt_template" / "no_criteria.txt"
)


@dataclass(frozen=True)
class LongStoryConfig:
    model: str
    api_key: str
    api_base: str | None = None
    max_retries: int = 3
    retry_delay: float = 3.0


def build_client(config: LongStoryConfig) -> OpenAI:
    kwargs: dict[str, Any] = {"api_key": config.api_key}
    if config.api_base:
        kwargs["base_url"] = config.api_base.rstrip("/")
    return OpenAI(**kwargs)


def chat_completion(client: OpenAI, config: LongStoryConfig, prompt: str) -> str:
    last_error: Exception | None = None
    for attempt in range(config.max_retries):
        try:
            response = client.chat.completions.create(
                model=config.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
            )
            content = response.choices[0].message.content
            return content or ""
        except Exception as exc:  # pragma: no cover - network/API dependent
            last_error = exc
            if attempt < config.max_retries - 1:
                time.sleep(config.retry_delay * (attempt + 1))
    raise RuntimeError(f"LongStoryEval API call failed: {last_error}") from last_error


def process_summary_response(response: str) -> tuple[str, str, str, str]:
    cur_summ, overall_sum, cur_char, all_char = "", "", "", ""
    try:
        if "\n\n### Characters:" in response:
            summ, char = response.split("\n\n### Characters:", 1)
            char = "\n".join(char.split("\n")[1:])
        else:
            summ = response
            char = ""

        summ = summ.replace("### Updated Plot Summary", "### Overall Plot Summary")
        if "\n\n### Overall Plot Summary" in summ:
            cur_summ, overall_sum = summ.split("\n\n### Overall Plot Summary", 1)
            overall_sum = "\n".join(overall_sum.split("\n")[1:])
            if "### Summary of Current Segment" in cur_summ:
                cur_summ = "\n".join(cur_summ.split("\n")[1:])
        else:
            overall_sum = "\n".join(summ.split("\n")[1:]) if "### Plot Summary" in summ else summ
            cur_summ = overall_sum

        if "\n- **Current Experience" in char:
            chars = char.split("\n- **Current Experience")
            all_char = chars[0]
            cur_char = char
            for tchar in chars[1:20]:
                all_char += "\n"
                all_char += "\n".join(tchar.split("\n")[1:])
        else:
            all_char = char
            cur_char = all_char
    except Exception:
        pass

    return (
        cur_summ.replace("\n\n", "\n").replace("\n---", ""),
        overall_sum.replace("\n\n", "\n").replace("\n---", ""),
        cur_char,
        all_char,
    )


def process_characters(char_sum: str) -> str:
    chars = char_sum.split("\n\n")
    rights = []
    for char in chars:
        lower = char.lower()
        if "not mentioned" in lower or "---" in char:
            continue
        if "Overall Experience" not in char and "Profile" not in char:
            if "**New Character" not in char:
                continue
        rights.append(char)
    return "\n\n".join(rights[:8])


def book_chunks(book: dict[str, Any], max_chars: int = 12000) -> list[str]:
    chunks: list[str] = []
    current = ""
    for chapter in book.get("chaps", []):
        title = chapter.get("title", "")
        content = "\n".join(chapter.get("content", []))
        chapter_text = f"### {title}\n\n{content}" if title else content
        if current and len(current) + len(chapter_text) > max_chars:
            chunks.append(current)
            current = ""
        current = f"{current}\n\n\n{chapter_text}".strip() if current else chapter_text
    if current:
        chunks.append(current)
    return chunks


def summarize_book(
    book_path: Path,
    output_path: Path,
    config: LongStoryConfig,
    prompt_dir: Path = DEFAULT_SUMMARY_PROMPTS,
    max_chars: int = 12000,
    dry_run: bool = False,
) -> dict[str, Any]:
    book = json.loads(book_path.read_text(encoding="utf-8"))
    chunks = book_chunks(book, max_chars=max_chars)
    if not chunks:
        raise ValueError(f"No chapter content found in {book_path}")

    result = {
        "book": book_path.stem,
        "chunks": len(chunks),
        "output": str(output_path),
        "dry_run": dry_run,
    }
    if dry_run:
        return result

    prompt_start = (prompt_dir / "beginning.txt").read_text(encoding="utf-8")
    prompt_update = (prompt_dir / "update.txt").read_text(encoding="utf-8")
    client = build_client(config)

    response = chat_completion(client, config, prompt_start.replace("{Beginning}", chunks[0]))
    cur_summ, overall_sum, cur_char, overall_char = process_summary_response(response)
    summaries = [
        {
            "response": response,
            "cur_sum": cur_summ,
            "overall_sum": overall_sum,
            "cur_char": cur_char,
            "overall_char": overall_char,
        }
    ]

    for idx, chunk in enumerate(chunks[1:], start=1):
        prompt = prompt_update.replace("{Beginning}", chunk)
        prompt = prompt.replace("{Chars}", overall_char).replace("{Sum}", overall_sum)
        if idx == len(chunks) - 1 and "epilogue" not in prompt.lower():
            prompt = "### Epilogue\n\n" + prompt
        response = chat_completion(client, config, prompt)
        cur_summ, next_sum, cur_char, next_char = process_summary_response(response)
        if next_sum and len(next_sum) >= 20:
            overall_sum = next_sum
        if next_char and len(next_char) >= 20:
            overall_char = next_char
        summaries.append(
            {
                "response": response,
                "cur_sum": cur_summ,
                "overall_sum": overall_sum,
                "cur_char": cur_char,
                "overall_char": overall_char,
            }
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summaries, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def get_excerpt(content: list[str], max_chars: int = 1200) -> str:
    lines: list[str] = []
    size = 0
    for line in content:
        if "chapter " in line.lower():
            continue
        cleaned = line.replace("\n", " ").strip()
        if not cleaned:
            continue
        if size + len(cleaned) > max_chars:
            break
        lines.append(cleaned)
        size += len(cleaned)
    return "\n".join(lines)


def extract_scores(text: str) -> dict[str, float]:
    scores: dict[str, float] = {}
    current_aspect = ""
    aspect_re = re.compile(r"^###\s*\d+\.\s*(.+?):?\s*$")
    score_re = re.compile(r"(?:Overall\s+)?Score:\s*([0-9]+(?:\.[0-9]+)?)", re.I)
    for raw_line in text.splitlines():
        line = raw_line.strip().strip("-* ")
        aspect_match = aspect_re.match(line)
        if aspect_match:
            current_aspect = aspect_match.group(1).strip()
            continue
        score_match = score_re.search(line)
        if score_match:
            key = current_aspect or "Overall"
            if "Overall Assessment" in raw_line or "Overall Score" in raw_line:
                key = "Overall"
            scores[key] = float(score_match.group(1))
    return scores


def evaluate_book_summary(
    book_path: Path,
    summary_path: Path,
    book_info: dict[str, Any],
    output_path: Path,
    config: LongStoryConfig,
    prompt_path: Path = DEFAULT_EVAL_PROMPT,
    dry_run: bool = False,
) -> dict[str, Any]:
    book = json.loads(book_path.read_text(encoding="utf-8"))
    summaries = json.loads(summary_path.read_text(encoding="utf-8"))
    if not summaries:
        raise ValueError(f"Empty summary file: {summary_path}")

    meta = book_info[book_path.stem]
    genres = ", ".join(meta.get("genres", [])[:3])
    premise = str(meta.get("premise") or meta.get("basic") or "")
    final_summary = summaries[-1]
    event_summary = final_summary.get("overall_sum", "").replace("In this segment, ", "Later, ")
    char_summary = process_characters(final_summary.get("overall_char", ""))
    first_content = next((chap.get("content", []) for chap in book.get("chaps", []) if chap), [])
    excerpt = get_excerpt(first_content)

    result = {
        "book": book_path.stem,
        "summary": str(summary_path),
        "output": str(output_path),
        "dry_run": dry_run,
    }
    if dry_run:
        return result

    template = prompt_path.read_text(encoding="utf-8")
    prompt = (
        template.replace("{Title}", meta.get("title", book_path.stem))
        .replace("{Genre}", genres)
        .replace("{Premise}", premise)
        .replace("{Plot_Summary}", event_summary)
        .replace("{Character_Summary}", char_summary)
        .replace("{Excerpt}", excerpt)
    )
    client = build_client(config)
    response = chat_completion(client, config, prompt)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(response, encoding="utf-8")
    result["scores"] = extract_scores(response)
    return result


def iter_book_files(book_dirs: Iterable[Path]) -> list[Path]:
    files: list[Path] = []
    for book_dir in book_dirs:
        files.extend(sorted(book_dir.glob("*.json")))
    return files


def summarize_books(
    book_dirs: Iterable[Path],
    output_dir: Path,
    config: LongStoryConfig,
    prompt_dir: Path = DEFAULT_SUMMARY_PROMPTS,
    max_chars: int = 12000,
    concurrent: int = 1,
    dry_run: bool = False,
) -> list[dict[str, Any]]:
    books = iter_book_files(book_dirs)
    output_dir.mkdir(parents=True, exist_ok=True)

    def _one(path: Path) -> dict[str, Any]:
        return summarize_book(
            path,
            output_dir / path.name,
            config,
            prompt_dir=prompt_dir,
            max_chars=max_chars,
            dry_run=dry_run,
        )

    return run_parallel(books, _one, concurrent=concurrent)


def evaluate_book_summaries(
    book_dirs: Iterable[Path],
    summary_dir: Path,
    book_info_paths: Iterable[Path],
    output_dir: Path,
    config: LongStoryConfig,
    prompt_path: Path = DEFAULT_EVAL_PROMPT,
    concurrent: int = 1,
    dry_run: bool = False,
) -> list[dict[str, Any]]:
    book_info: dict[str, Any] = {}
    for path in book_info_paths:
        book_info.update(json.loads(path.read_text(encoding="utf-8")))

    books = iter_book_files(book_dirs)
    output_dir.mkdir(parents=True, exist_ok=True)

    def _one(path: Path) -> dict[str, Any]:
        summary_path = summary_dir / path.name
        if not summary_path.exists():
            raise FileNotFoundError(f"Missing summary for {path.stem}: {summary_path}")
        if path.stem not in book_info:
            raise KeyError(f"Missing book_info entry: {path.stem}")
        return evaluate_book_summary(
            path,
            summary_path,
            book_info,
            output_dir / f"{path.stem}.txt",
            config,
            prompt_path=prompt_path,
            dry_run=dry_run,
        )

    return run_parallel(books, _one, concurrent=concurrent)


def run_parallel(items: list[Path], fn, concurrent: int) -> list[dict[str, Any]]:
    if concurrent <= 1:
        return [fn(item) for item in items]

    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=concurrent) as pool:
        futures = {pool.submit(fn, item): item for item in items}
        for future in as_completed(futures):
            results.append(future.result())
    return results


def env_config(model: str | None, api_base: str | None, api_key: str | None) -> LongStoryConfig:
    resolved_key = api_key or os.environ.get("OPENAI_API_KEY") or ""
    if not resolved_key:
        raise ValueError("Missing API key. Set OPENAI_API_KEY or pass --api-key.")
    return LongStoryConfig(
        model=model or os.environ.get("JUDGE_MODEL") or "gpt-4o",
        api_base=api_base or os.environ.get("OPENAI_BASE_URL"),
        api_key=resolved_key,
    )

