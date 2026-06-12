"""Corpus preparation utilities for Stone-eval.

The evaluation stage treats the Cao Xueqin/Gao E text and later continuations as
separate corpora.  ConStory-Bench receives chapter-level rows, while
LongStoryEval receives book-level JSON files with chapter lists.
"""

from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


CHINESE_DIGITS = {
    "零": 0,
    "〇": 0,
    "一": 1,
    "二": 2,
    "两": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
}

ORIGINAL_HEADING_RE = re.compile(
    r"^\s*第(?P<num>\d+)章\s*(?P<title>.+?)\s*$",
    re.MULTILINE,
)
CONTINUATION_HEADING_RE = re.compile(
    r"^[\s　●○◇]*第(?P<num>[一二三四五六七八九十百零〇两\d]+)"
    r"(?:(?P<marker>[回章])\s*(?P<title>.*?)|\s+(?P<title_no_marker>.*?))\s*$"
)
CONTINUATION_ID_RE = re.compile(r"^C(?P<num>\d{3})_(?P<title>.+)$")


@dataclass(frozen=True)
class Chapter:
    index: int
    title: str
    text: str


@dataclass(frozen=True)
class PreparedCorpus:
    name: str
    kind: str
    chapters: list[Chapter]
    title: str | None = None
    source_file: str | None = None


def parse_chinese_number(value: str) -> int:
    """Parse simple Chinese chapter numerals up to 199."""
    value = value.strip()
    if value.isdigit():
        return int(value)
    if not value:
        raise ValueError("empty chapter number")

    total = 0
    current = 0
    for char in value:
        if char == "百":
            total += (current or 1) * 100
            current = 0
        elif char == "十":
            total += (current or 1) * 10
            current = 0
        elif char in CHINESE_DIGITS:
            current = CHINESE_DIGITS[char]
        else:
            raise ValueError(f"unsupported Chinese numeral: {value}")
    return total + current


def slugify_name(name: str) -> str:
    stem = Path(name).stem
    stem = re.sub(r"\s+", "_", stem.strip())
    stem = re.sub(r"[^\w\u4e00-\u9fff.-]+", "_", stem)
    return stem.strip("_") or "untitled"


def numbered_continuation_name(index: int, name: str) -> str:
    return f"C{index:03d}_{slugify_name(name)}"


def continuation_entries(continuation_dir: Path) -> list[tuple[int, Path, str, str]]:
    """Assign stable Cxxx IDs, preserving explicit Cxxx_ filename prefixes."""
    explicit: list[tuple[int, Path, str, str]] = []
    unnumbered: list[Path] = []
    used_ids: set[int] = set()

    for path in sorted(continuation_dir.glob("*.txt")):
        stem = slugify_name(path.name)
        match = CONTINUATION_ID_RE.match(stem)
        if match:
            index = int(match.group("num"))
            if index in used_ids:
                raise ValueError(f"Duplicate explicit continuation id C{index:03d}: {path}")
            title = match.group("title")
            explicit.append((index, path, stem, title))
            used_ids.add(index)
        else:
            unnumbered.append(path)

    entries = explicit[:]
    next_id = 1
    for path in unnumbered:
        while next_id in used_ids:
            next_id += 1
        title = slugify_name(path.name)
        entries.append((next_id, path, numbered_continuation_name(next_id, path.name), title))
        used_ids.add(next_id)
        next_id += 1

    seen_names: set[str] = set()
    for _, path, name, _ in entries:
        if name in seen_names:
            raise ValueError(f"Duplicate continuation id/name after numbering: {name} ({path})")
        seen_names.add(name)

    return sorted(entries, key=lambda item: item[0])


def split_original_text(path: Path, max_chapter: int = 80) -> list[Chapter]:
    text = path.read_text(encoding="utf-8")
    matches = list(ORIGINAL_HEADING_RE.finditer(text))
    if not matches:
        raise ValueError(f"No numeric chapter headings found in {path}")

    chapters: list[Chapter] = []
    for i, match in enumerate(matches):
        index = int(match.group("num"))
        if index > max_chapter:
            continue
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        chapters.append(Chapter(index=index, title=match.group("title").strip(), text=body))
    return chapters


def split_continuation_text(path: Path) -> list[Chapter]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    headings: list[tuple[int, int, str]] = []
    for line_no, line in enumerate(lines):
        match = CONTINUATION_HEADING_RE.match(line)
        if not match:
            continue
        try:
            number = parse_chinese_number(match.group("num"))
        except ValueError:
            continue
        if not match.group("marker") and number < 10:
            continue
        title = (match.group("title") or match.group("title_no_marker") or "").strip()
        headings.append((line_no, number, title))

    if not headings:
        body = text.strip()
        if not body:
            raise ValueError(f"No chapter headings found in empty file {path}")
        return [Chapter(index=1, title=Path(path).stem, text=body)]

    # Many continuation files start with a table of contents and then repeat
    # "第一回" for the real body.  If chapter 1 appears more than once, start at
    # its second occurrence and ignore the front matter TOC.
    first_chapter_positions = [i for i, (_, number, _) in enumerate(headings) if number == 1]
    start_heading_idx = first_chapter_positions[1] if len(first_chapter_positions) > 1 else 0
    toc_titles = {
        number: title
        for _, number, title in headings[:start_heading_idx]
        if title
    }
    body_headings = headings[start_heading_idx:]

    chapters: list[Chapter] = []
    for i, (line_no, number, title) in enumerate(body_headings):
        next_line = body_headings[i + 1][0] if i + 1 < len(body_headings) else len(lines)
        body_prefix = ""
        toc_title = toc_titles.get(number)
        if toc_title and title.startswith(toc_title) and len(title) > len(toc_title):
            body_prefix = title[len(toc_title) :].strip()
            title = toc_title
        body = "\n".join(lines[line_no + 1 : next_line]).strip()
        if body_prefix:
            body = f"{body_prefix}\n{body}".strip()
        if not body and title:
            body = title
        chapters.append(Chapter(index=number, title=title, text=body))
    return chapters


def write_chapter_files(chapters: Iterable[Chapter], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for chapter in chapters:
        title = f"第{chapter.index:03d}回 {chapter.title}".strip()
        content = f"{title}\n\n{chapter.text}\n"
        (output_dir / f"chapter_{chapter.index:03d}.txt").write_text(content, encoding="utf-8")


def build_constory_rows(corpora: Iterable[PreparedCorpus]) -> list[dict]:
    rows: list[dict] = []
    for corpus in corpora:
        for chapter in corpus.chapters:
            title = f"第{chapter.index}回 {chapter.title}".strip()
            story_text = f"{title}\n\n{chapter.text}".strip()
            rows.append(
                {
                    "id": f"{corpus.kind}:{corpus.name}:chapter_{chapter.index:03d}",
                    "corpus": corpus.kind,
                    "book": corpus.name,
                    "book_title": corpus.title or corpus.name,
                    "source_file": corpus.source_file or "",
                    "chapter_index": chapter.index,
                    "chapter_title": chapter.title,
                    "story_text": story_text,
                }
            )
    return rows


def write_constory_parquet(rows: list[dict], output_path: Path) -> None:
    import pandas as pd

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_parquet(output_path, index=False)


def write_longstory_book(corpus: PreparedCorpus, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "id": corpus.name,
        "title": corpus.title or corpus.name,
        "kind": corpus.kind,
        "source_file": corpus.source_file or "",
        "chaps": [
            {
                "title": f"第{chapter.index}回 {chapter.title}".strip(),
                "content": chapter.text.splitlines(),
            }
            for chapter in corpus.chapters
        ],
    }
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_book_info(corpora: Iterable[PreparedCorpus], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {}
    for corpus in corpora:
        payload[corpus.name] = {
            "title": corpus.title or corpus.name,
            "basic": "《红楼梦》原文前80回" if corpus.kind == "original" else "《红楼梦》续作",
            "premise": "评估《红楼梦》原文或续作的叙事质量与一致性。",
            "genres": ["Chinese classical novel", "HongLouMeng"],
            "score": 0,
            "kind": corpus.kind,
            "chapters": len(corpus.chapters),
            "source_file": corpus.source_file or "",
        }
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def prepare_stone_corpora(
    original_path: Path,
    continuation_dir: Path,
    output_dir: Path,
    original_chapters: int = 80,
) -> dict[str, Path | int]:
    for generated_dir in ("chapters", "constory", "longstoryeval"):
        path = output_dir / generated_dir
        if path.exists():
            shutil.rmtree(path)

    original = PreparedCorpus(
        name=f"红楼梦前{original_chapters}回",
        kind="original",
        chapters=split_original_text(original_path, max_chapter=original_chapters),
        title=f"红楼梦前{original_chapters}回",
        source_file=str(original_path),
    )

    continuation_corpora: list[PreparedCorpus] = []
    for _, path, name, title in continuation_entries(continuation_dir):
        chapters = split_continuation_text(path)
        continuation_corpora.append(
            PreparedCorpus(
                name=name,
                kind="continuation",
                chapters=chapters,
                title=title,
                source_file=str(path),
            )
        )

    original_chapter_dir = output_dir / "chapters" / "original"
    write_chapter_files(original.chapters, original_chapter_dir)

    continuation_chapter_root = output_dir / "chapters" / "continuations"
    for corpus in continuation_corpora:
        write_chapter_files(corpus.chapters, continuation_chapter_root / corpus.name)

    constory_original = output_dir / "constory" / "original_chapters.parquet"
    constory_continuations = output_dir / "constory" / "continuation_chapters.parquet"
    write_constory_parquet(build_constory_rows([original]), constory_original)
    write_constory_parquet(build_constory_rows(continuation_corpora), constory_continuations)

    longstory_original_dir = output_dir / "longstoryeval" / "original" / "books_json"
    longstory_continuation_dir = output_dir / "longstoryeval" / "continuations" / "books_json"
    write_longstory_book(original, longstory_original_dir / f"{original.name}.json")
    for corpus in continuation_corpora:
        write_longstory_book(corpus, longstory_continuation_dir / f"{corpus.name}.json")

    write_book_info([original], output_dir / "longstoryeval" / "original" / "book_info.json")
    write_book_info(
        continuation_corpora,
        output_dir / "longstoryeval" / "continuations" / "book_info.json",
    )

    manifest = {
        "original": {
            "name": original.name,
            "chapters": len(original.chapters),
            "chapter_dir": str(original_chapter_dir),
            "constory_parquet": str(constory_original),
            "longstory_books_json": str(longstory_original_dir),
        },
        "continuations": [
            {
                "name": corpus.name,
                "title": corpus.title or corpus.name,
                "source_file": corpus.source_file or "",
                "chapters": len(corpus.chapters),
                "chapter_dir": str(continuation_chapter_root / corpus.name),
            }
            for corpus in continuation_corpora
        ],
        "continuation_constory_parquet": str(constory_continuations),
        "continuation_longstory_books_json": str(longstory_continuation_dir),
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "manifest": manifest_path,
        "original_chapters": len(original.chapters),
        "continuation_books": len(continuation_corpora),
        "continuation_chapters": sum(len(corpus.chapters) for corpus in continuation_corpora),
        "constory_original": constory_original,
        "constory_continuations": constory_continuations,
    }
