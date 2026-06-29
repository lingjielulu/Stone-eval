#!/usr/bin/env python3
"""Preprocess Project Gutenberg #57333 Chekhov compilation.

The source file is a compilation: Gutenberg metadata, table-of-contents
sections, then story bodies. This script builds a reproducible story-level
corpus and keeps enough provenance to audit every split boundary.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from statistics import mean, median
from typing import Iterable


ALIAS_TITLES = {
    "GOUSSIEV": "GUSEV",
}

NON_STORY_TITLES = {
    "CONTENTS OF EACH BOOK",
    "IN ALPHABETICAL ORDER",
    "INTRODUCTION",
}

RUN_IN_HEADING_PATTERNS = (
    ("THE LADY WITH THE TOY\nDOG\n", "THE LADY WITH THE TOY DOG\n"),
    (
        "With The Mezzanine THE HOUSE WITH THE MEZZANINE\n",
        "With The Mezzanine\n\nTHE HOUSE WITH THE MEZZANINE\n",
    ),
    (" only just beginning. GOUSSIEV\n", " only just beginning.\n\nGOUSSIEV\n"),
    ("human language. MY LIFE\n", "human language.\n\nMY LIFE\n"),
    (" human language. MY LIFE\n", " human language.\n\nMY LIFE\n"),
    (
        "Then he tossed his head and began packing.\nMY LIFE THE STORY OF A PROVINCIAL I\n",
        "Then he tossed his head and began packing.\n\nMY LIFE THE STORY OF A PROVINCIAL I\n",
    ),
)

WORD_RE = re.compile(r"[A-Za-z]+(?:['-][A-Za-z]+)*")
ROMAN_RE = re.compile(r"^(?:[IVXLCDM]+)$")


@dataclass
class Heading:
    title: str
    canonical_title: str
    heading_line: str
    line_index: int


@dataclass
class StoryRecord:
    story_id: str
    source_order: int
    occurrence: int
    title: str
    canonical_title: str
    heading_line: str
    source_start_line: int
    source_end_line: int
    word_count: int
    paragraph_count: int
    chapter_count: int
    char_count: int
    sha256_12: str
    quality_flags: list[str]
    text: str


def normalize_newlines(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return "\n".join(line.rstrip() for line in text.split("\n"))


def normalize_title(title: str) -> str:
    title = title.strip()
    title = re.sub(r"\s+\[[A-Z]\]$", "", title)
    title = re.sub(r"\s+", " ", title)
    title = title.strip(" .")
    return ALIAS_TITLES.get(title, title)


def clean_catalog_title(title: str) -> str:
    title = title.strip()
    title = re.sub(r"\s+\[[A-Z]\]$", "", title)
    title = re.sub(r"\s+", " ", title)
    return title.strip(" .")


def extract_ordered_titles(lines: list[str]) -> list[str]:
    start = lines.index("CONTENTS OF EACH BOOK") + 1
    end = lines.index("IN ALPHABETICAL ORDER")
    titles: list[str] = []
    seen: set[str] = set()
    for raw in lines[start:end]:
        line = raw.strip()
        if not line:
            continue
        # Example: "AN ACTOR'S END The Schoolmaster and Other Stories".
        line = re.sub(r"\s+The\s+.+$", "", line)
        mixed_case_pos = next((i for i, ch in enumerate(line) if ch.islower()), None)
        if mixed_case_pos is not None:
            line = line[:mixed_case_pos].rstrip()
        title = clean_catalog_title(line)
        if not title or title in NON_STORY_TITLES:
            continue
        if title not in seen:
            titles.append(title)
            seen.add(title)
    return titles


def body_start_line(lines: list[str]) -> int:
    matches = [i for i, line in enumerate(lines) if line.strip() == "THE HORSE-STEALERS"]
    if not matches:
        raise ValueError("Could not locate THE HORSE-STEALERS body heading")
    return matches[-1]


def repair_run_in_headings(text: str, titles: list[str]) -> str:
    for old, new in RUN_IN_HEADING_PATTERNS:
        text = text.replace(old, new)
    for title in sorted(titles, key=len, reverse=True):
        escaped = re.escape(title)
        suffix = r"(?:\s+\([A-Za-z0-9 '\-.,]+\))?(?:\s+[IVXLCDM]+)?"
        pattern = re.compile(rf"(?P<end>[.!?][\"']?) (?P<head>{escaped}{suffix})\n")
        text = pattern.sub(r"\g<end>\n\n\g<head>\n", text)
    repaired_lines: list[str] = []
    sorted_titles = sorted(titles, key=len, reverse=True)
    original_lines = text.split("\n")
    for idx, line in enumerate(original_lines):
        previous_blank = idx == 0 or not original_lines[idx - 1].strip()
        if previous_blank:
            split_done = False
            for title in sorted_titles:
                prefix = f"{title} "
                if not line.startswith(prefix):
                    continue
                rest = line[len(prefix) :].strip()
                if rest and not allowed_heading_suffix(title, rest):
                    repaired_lines.extend([title, rest])
                    split_done = True
                break
            if split_done:
                continue
        repaired_lines.append(line)
    return "\n".join(repaired_lines)


def allowed_heading_suffix(title: str, suffix: str) -> bool:
    if not suffix:
        return True
    if ROMAN_RE.match(suffix):
        return True
    if title == "THE STEPPE" and re.match(r"^The Story of a Journey(?:\s+[IVXLCDM]+)?$", suffix):
        return True
    if title == "MY LIFE" and re.match(r"^(?:THE STORY OF A PROVINCIAL)(?:\s+[IVXLCDM]+)?$", suffix):
        return True
    if title == "TERROR" and suffix == "My Friend's Story":
        return True
    if title == "UPROOTED" and suffix == "An Incident of My Travels":
        return True
    if title == "A DREARY STORY" and suffix == "FROM THE NOTEBOOK OF AN OLD MAN":
        return True
    if re.match(r"^\([A-Za-z0-9 '\-.,]+\)(?:\s+[IVXLCDM]+)?$", suffix):
        return True
    return False


def find_heading(line: str, title_candidates: list[str]) -> tuple[str, str] | None:
    stripped = line.strip()
    if not stripped or len(stripped) > 120:
        return None
    if stripped in NON_STORY_TITLES or ROMAN_RE.match(stripped):
        return None
    for title in title_candidates:
        if stripped == title:
            return title, normalize_title(title)
        prefix = f"{title} "
        if stripped.startswith(prefix):
            suffix = stripped[len(prefix) :].strip()
            if allowed_heading_suffix(title, suffix):
                return title, normalize_title(title)
    return None


def find_body_headings(lines: list[str], titles: list[str]) -> list[Heading]:
    title_candidates = sorted(titles, key=len, reverse=True)
    headings: list[Heading] = []
    for idx, line in enumerate(lines):
        found = find_heading(line, title_candidates)
        if found is None:
            continue
        title, canonical = found
        headings.append(
            Heading(
                title=title,
                canonical_title=canonical,
                heading_line=line.strip(),
                line_index=idx,
            )
        )
    return headings


def normalize_story_text(lines: Iterable[str]) -> str:
    raw = "\n".join(lines).strip()
    raw = re.sub(r"(\w)-\n(\w)", r"\1\2", raw)
    paragraphs = re.split(r"\n\s*\n", raw)
    clean_paragraphs: list[str] = []
    for paragraph in paragraphs:
        pieces = [piece.strip() for piece in paragraph.splitlines() if piece.strip()]
        if pieces:
            clean_paragraphs.append(re.sub(r"\s+", " ", " ".join(pieces)))
    return "\n\n".join(clean_paragraphs)


def count_chapters(lines: Iterable[str]) -> int:
    return sum(1 for line in lines if ROMAN_RE.match(line.strip()))


def make_story_id(canonical_title: str, occurrence: int) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", canonical_title.lower()).strip("_")
    return f"chekhov_{slug}_{occurrence:02d}"


def build_records(body_lines: list[str], headings: list[Heading]) -> list[StoryRecord]:
    records: list[StoryRecord] = []
    occurrence_counts: Counter[str] = Counter()
    for order, heading in enumerate(headings, start=1):
        next_line = headings[order].line_index if order < len(headings) else len(body_lines)
        story_lines = body_lines[heading.line_index + 1 : next_line]
        clean_text = normalize_story_text(story_lines)
        words = WORD_RE.findall(clean_text)
        occurrence_counts[heading.canonical_title] += 1
        occurrence = occurrence_counts[heading.canonical_title]
        quality_flags: list[str] = []
        if heading.title != heading.canonical_title:
            quality_flags.append("title_alias_normalized")
        if occurrence > 1:
            quality_flags.append("duplicate_canonical_title")
        if heading.title in {"MY LIFE", "GUSEV", "GOUSSIEV"}:
            quality_flags.append("known_layout_sensitive_title")
        if len(words) < 500:
            quality_flags.append("short_segment_under_500_words")
        sha = hashlib.sha256(clean_text.encode("utf-8")).hexdigest()[:12]
        records.append(
            StoryRecord(
                story_id=make_story_id(heading.canonical_title, occurrence),
                source_order=order,
                occurrence=occurrence,
                title=heading.title,
                canonical_title=heading.canonical_title,
                heading_line=heading.heading_line,
                source_start_line=heading.line_index + 1,
                source_end_line=next_line,
                word_count=len(words),
                paragraph_count=len([p for p in clean_text.split("\n\n") if p.strip()]),
                chapter_count=count_chapters(story_lines),
                char_count=len(clean_text),
                sha256_12=sha,
                quality_flags=quality_flags,
                text=clean_text,
            )
        )
    return records


def canonical_records(records: list[StoryRecord]) -> list[StoryRecord]:
    selected: dict[str, StoryRecord] = {}
    for record in records:
        current = selected.get(record.canonical_title)
        if current is None or record.word_count > current.word_count:
            selected[record.canonical_title] = record
    return sorted(selected.values(), key=lambda item: item.source_order)


def bucket_lengths(records: list[StoryRecord]) -> list[dict[str, int | str]]:
    buckets = [
        ("<500", 0, 499),
        ("500-1K", 500, 999),
        ("1K-2K", 1000, 1999),
        ("2K-5K", 2000, 4999),
        ("5K-10K", 5000, 9999),
        ("10K-20K", 10000, 19999),
        ("20K+", 20000, 10**9),
    ]
    rows = []
    for label, lo, hi in buckets:
        rows.append(
            {
                "bucket": label,
                "story_count": sum(1 for record in records if lo <= record.word_count <= hi),
            }
        )
    return rows


def stats(
    records_all: list[StoryRecord],
    records_canonical: list[StoryRecord],
    titles: list[str],
) -> dict:
    word_counts = [record.word_count for record in records_canonical]
    duplicate_titles = {
        title: count
        for title, count in Counter(record.canonical_title for record in records_all).items()
        if count > 1
    }
    detected_titles = {record.canonical_title for record in records_all}
    unmatched_titles = [
        title for title in titles if normalize_title(title) not in detected_titles and title not in NON_STORY_TITLES
    ]
    quality_flag_counts = Counter(flag for record in records_all for flag in record.quality_flags)
    return {
        "source_title_count_from_contents": len(titles),
        "detected_story_segments_all": len(records_all),
        "canonical_story_count": len(records_canonical),
        "unmatched_catalog_title_count": len(unmatched_titles),
        "unmatched_catalog_titles": unmatched_titles,
        "duplicate_canonical_title_count": len(duplicate_titles),
        "duplicate_canonical_titles": duplicate_titles,
        "quality_flag_counts": dict(sorted(quality_flag_counts.items())),
        "total_words_canonical": sum(word_counts),
        "mean_words_canonical": round(mean(word_counts), 2) if word_counts else 0,
        "median_words_canonical": median(word_counts) if word_counts else 0,
        "min_words_canonical": min(word_counts) if word_counts else 0,
        "max_words_canonical": max(word_counts) if word_counts else 0,
        "length_buckets_canonical": bucket_lengths(records_canonical),
        "longest_20": [
            {
                "canonical_title": record.canonical_title,
                "word_count": record.word_count,
                "story_id": record.story_id,
            }
            for record in sorted(records_canonical, key=lambda item: item.word_count, reverse=True)[:20]
        ],
        "shortest_20": [
            {
                "canonical_title": record.canonical_title,
                "word_count": record.word_count,
                "story_id": record.story_id,
            }
            for record in sorted(records_canonical, key=lambda item: item.word_count)[:20]
        ],
    }


def write_jsonl(path: Path, records: Iterable[StoryRecord]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")


def write_csv(path: Path, records: Iterable[StoryRecord]) -> None:
    fieldnames = [
        "story_id",
        "source_order",
        "occurrence",
        "title",
        "canonical_title",
        "heading_line",
        "source_start_line",
        "source_end_line",
        "word_count",
        "paragraph_count",
        "chapter_count",
        "char_count",
        "sha256_12",
        "quality_flags",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            row = asdict(record)
            row["quality_flags"] = ";".join(record.quality_flags)
            row.pop("text")
            writer.writerow(row)


def write_title_index(path: Path, records_all: list[StoryRecord]) -> None:
    grouped: dict[str, list[StoryRecord]] = defaultdict(list)
    for record in records_all:
        grouped[record.canonical_title].append(record)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "canonical_title",
                "occurrences",
                "selected_story_id",
                "all_story_ids",
                "word_counts",
            ],
        )
        writer.writeheader()
        for title in sorted(grouped):
            group = grouped[title]
            selected = max(group, key=lambda item: item.word_count)
            writer.writerow(
                {
                    "canonical_title": title,
                    "occurrences": len(group),
                    "selected_story_id": selected.story_id,
                    "all_story_ids": ";".join(record.story_id for record in group),
                    "word_counts": ";".join(str(record.word_count) for record in group),
                }
            )


def markdown_table(rows: list[dict], columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row[col]) for col in columns) + " |")
    return "\n".join(lines)


def write_report(path: Path, stats_data: dict) -> None:
    bucket_rows = stats_data["length_buckets_canonical"]
    long_rows = stats_data["longest_20"]
    short_rows = stats_data["shortest_20"]
    duplicate_rows = [
        {"canonical_title": title, "occurrences": count}
        for title, count in sorted(stats_data["duplicate_canonical_titles"].items())
    ]
    report = f"""# Chekhov Normalized Corpus Statistics

Source: `data/chekhov/raw/chekhov_short_stories.txt`

## Summary

| Metric | Value |
|---|---:|
| Titles parsed from contents | {stats_data["source_title_count_from_contents"]} |
| Detected body story segments | {stats_data["detected_story_segments_all"]} |
| Canonical story records | {stats_data["canonical_story_count"]} |
| Catalog titles not matched to body boundary | {stats_data["unmatched_catalog_title_count"]} |
| Duplicate canonical titles | {stats_data["duplicate_canonical_title_count"]} |
| Total words, canonical corpus | {stats_data["total_words_canonical"]:,} |
| Mean words, canonical corpus | {stats_data["mean_words_canonical"]:,} |
| Median words, canonical corpus | {stats_data["median_words_canonical"]:,} |
| Min words | {stats_data["min_words_canonical"]:,} |
| Max words | {stats_data["max_words_canonical"]:,} |

## Length Buckets

{markdown_table(bucket_rows, ["bucket", "story_count"])}

## Longest 20

{markdown_table(long_rows, ["canonical_title", "word_count", "story_id"])}

## Shortest 20

{markdown_table(short_rows, ["canonical_title", "word_count", "story_id"])}

## Duplicate Canonical Titles

{markdown_table(duplicate_rows, ["canonical_title", "occurrences"]) if duplicate_rows else "No duplicate canonical titles detected."}

## Unmatched Catalog Titles

These titles appear in the parsed contents but were not emitted as standalone canonical story records. Most are duplicate translation titles, alternate anthology labels, or entries whose body heading is absent in this Gutenberg compilation.

{", ".join(stats_data["unmatched_catalog_titles"]) if stats_data["unmatched_catalog_titles"] else "None."}
"""
    path.write_text(report, encoding="utf-8")


def write_manifest(path: Path, stats_data: dict) -> None:
    manifest = {
        "source": "Project Gutenberg #57333, local file data/chekhov/raw/chekhov_short_stories.txt",
        "preprocessing_script": "data/chekhov/scripts/preprocess_chekhov.py",
        "outputs": {
            "all_segments_jsonl": "data/chekhov/processed/stories_all.jsonl",
            "all_segments_csv": "data/chekhov/processed/stories_all.csv",
            "canonical_jsonl": "data/chekhov/processed/stories_canonical.jsonl",
            "canonical_csv": "data/chekhov/processed/stories_canonical.csv",
            "title_index_csv": "data/chekhov/processed/title_index.csv",
            "stats_json": "data/chekhov/processed/stats.json",
            "stats_report": "data/chekhov/reports/chekhov_normalized_stats.md",
        },
        "policy": {
            "body_start": "last THE HORSE-STEALERS heading after contents/index",
            "title_source": "CONTENTS OF EACH BOOK section before IN ALPHABETICAL ORDER",
            "split_boundary": "catalog title at line start, with support for roman numerals/subtitles",
            "run_in_heading_repair": "sentence-final catalog titles glued to previous paragraph are separated before splitting",
            "canonical_selection": "for duplicate canonical titles, keep the longest detected segment",
        },
        "statistics": stats_data,
    }
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def preprocess(raw_path: Path, output_dir: Path) -> dict:
    text = normalize_newlines(raw_path.read_text(encoding="utf-8"))
    source_lines = text.split("\n")
    titles = extract_ordered_titles(source_lines)
    start = body_start_line(source_lines)
    body_text = repair_run_in_headings("\n".join(source_lines[start:]), titles)
    body_lines = body_text.split("\n")
    headings = find_body_headings(body_lines, titles)
    if not headings:
        raise ValueError("No story headings detected")
    records_all = build_records(body_lines, headings)
    records_canonical = canonical_records(records_all)
    stats_data = stats(records_all, records_canonical, titles)

    output_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(output_dir / "stories_all.jsonl", records_all)
    write_jsonl(output_dir / "stories_canonical.jsonl", records_canonical)
    write_csv(output_dir / "stories_all.csv", records_all)
    write_csv(output_dir / "stories_canonical.csv", records_canonical)
    write_title_index(output_dir / "title_index.csv", records_all)
    (output_dir / "stats.json").write_text(
        json.dumps(stats_data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_manifest(output_dir / "manifest.json", stats_data)
    write_report(output_dir.parent / "reports" / "chekhov_normalized_stats.md", stats_data)
    return stats_data


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--raw",
        type=Path,
        default=Path("data/chekhov/raw/chekhov_short_stories.txt"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/chekhov/processed"),
    )
    args = parser.parse_args()
    stats_data = preprocess(args.raw, args.output_dir)
    print(
        json.dumps(
            {
                "detected_story_segments_all": stats_data["detected_story_segments_all"],
                "canonical_story_count": stats_data["canonical_story_count"],
                "total_words_canonical": stats_data["total_words_canonical"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
