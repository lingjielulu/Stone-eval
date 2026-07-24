"""Render HongLou BookSum-style summary JSONL into a human-readable review file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def bullet_items(items: list[dict[str, Any]], fields: list[str]) -> list[str]:
    lines: list[str] = []
    for item in items:
        parts = []
        for field in fields:
            value = item.get(field)
            if value in (None, "", []):
                continue
            parts.append(f"{field}: {value}")
        if parts:
            lines.append(f"- {'; '.join(parts)}")
    return lines or ["- None"]


def render_item(item: dict[str, Any]) -> str:
    lines = [
        f"## Chapter {item['chapter_index']:03d}: {item.get('chapter_title', '')}",
        "",
        f"- ID: `{item.get('id', '')}`",
        f"- Model: `{item.get('model', '')}`",
        f"- Prompt: `{item.get('prompt_version', '')}`",
        f"- Source: `{item.get('source_text_path', '')}`",
        "",
        "### Summary",
        "",
        item.get("summary", "").strip() or "None",
        "",
        "### Summary Sentences",
        "",
    ]
    for sentence in item.get("summary_sentences", []):
        lines.append(f"{sentence.get('sentence_index')}. {sentence.get('text', '')}")

    sections = [
        (
            "Key Events",
            "key_events",
            ["event", "evidence_quote"],
        ),
        (
            "Character State Changes",
            "character_state_changes",
            ["character", "state_change", "evidence_quote"],
        ),
        (
            "Unresolved Setups",
            "unresolved_setups",
            ["setup", "type", "status", "evidence_quote"],
        ),
        (
            "Foreshadow Notes",
            "foreshadow_notes",
            ["note", "type", "why_it_matters_without_future_spoilers", "evidence_quote"],
        ),
        (
            "Poem Dream Prophecy Objects",
            "poem_dream_prophecy_objects",
            ["item", "category", "literal_content", "evidence_quote"],
        ),
        (
            "Warnings",
            "warnings",
            ["warning"],
        ),
    ]
    for title, key, fields in sections:
        lines.extend(["", f"### {title}", ""])
        values = item.get(key, [])
        if isinstance(values, list) and values and isinstance(values[0], dict):
            lines.extend(bullet_items(values, fields))
        elif isinstance(values, list) and values:
            lines.extend(f"- {value}" for value in values)
        else:
            lines.append("- None")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="foreshadow/honglou/results/cfpg/honglou_booksum/original_80_chapter_summaries.jsonl",
    )
    parser.add_argument(
        "--output",
        default="foreshadow/honglou/results/cfpg/honglou_booksum/original_80_chapter_summaries.review.md",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    items = [
        json.loads(line)
        for line in input_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    lines = [
        "# HongLou BookSum-Style Summary Review",
        "",
        f"- Source JSONL: `{input_path}`",
        f"- Chapters: {len(items)}",
        "",
    ]
    for item in items:
        lines.append(render_item(item))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {output_path}")


if __name__ == "__main__":
    main()
