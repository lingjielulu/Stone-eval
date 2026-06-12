"""Build a summary sentence timeline from HongLou BookSum-style summaries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--summary",
        type=Path,
        default=Path("data/processed/cfpg/honglou_booksum/original_80_chapter_summaries.jsonl"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "data/processed/cfpg/summary_alignments/"
            "original_80_summary_sentence_timeline_20260611_deepseek_honglou_original80.jsonl"
        ),
    )
    args = parser.parse_args()

    timeline = build_timeline(read_jsonl(args.summary))
    write_jsonl(args.output, timeline)
    print(f"wrote {args.output}")
    print(f"summary_sentences={len(timeline)}")


if __name__ == "__main__":
    main()
