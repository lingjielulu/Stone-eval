"""Normalize downloaded story collections into one UTF-8 text file per story.

This is intentionally conservative: it extracts known public-domain chapters by
heading boundaries, removes Gutenberg boilerplate, and writes paragraph-numbered
plain text for stable annotation references.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class StorySpec:
    story_id: str
    raw_file: str
    start_pattern: str
    end_pattern: str
    title: str
    min_line: int = 0


STORIES = [
    StorySpec(
        story_id="speckled_band",
        raw_file="gutenberg_1661_adventures_of_sherlock_holmes.txt",
        start_pattern=r"^VIII\. THE ADVENTURE OF THE SPECKLED BAND\s*$",
        end_pattern=r"^IX\. THE ADVENTURE OF THE ENGINEER",
        title="THE ADVENTURE OF THE SPECKLED BAND",
        min_line=1000,
    ),
    StorySpec(
        story_id="necklace",
        raw_file="gutenberg_3090_maupassant_original_short_stories_mirror.txt",
        start_pattern=r"^THE DIAMOND NECKLACE\s*$",
        end_pattern=r"^THE MARQUIS DE FUMEROL\s*$",
        title="THE DIAMOND NECKLACE",
        min_line=18000,
    ),
    StorySpec(
        story_id="to_build_a_fire",
        raw_file="gutenberg_2429_lost_face_mirror.txt",
        start_pattern=r"^TO BUILD A FIRE\s*$",
        end_pattern=r"^THAT SPOT\s*$",
        title="TO BUILD A FIRE",
        min_line=100,
    ),
]


def read_text(path: Path) -> str:
    data = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def extract_between(text: str, start_pattern: str, end_pattern: str, min_line: int = 0) -> str:
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    start_re = re.compile(start_pattern, re.IGNORECASE)
    end_re = re.compile(end_pattern, re.IGNORECASE)

    start_idx = None
    for idx, line in enumerate(lines):
        if idx >= min_line and start_re.match(line.strip()):
            start_idx = idx
            break
    if start_idx is None:
        raise ValueError(f"start heading not found: {start_pattern}")

    end_idx = len(lines)
    for idx in range(start_idx + 1, len(lines)):
        if end_re.match(lines[idx].strip()):
            end_idx = idx
            break

    return "\n".join(lines[start_idx:end_idx]).strip()


def normalize(text: str, title: str) -> str:
    text = text.replace("\t", " ")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \u00a0]+", " ", text)
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

    cleaned = []
    for para in paragraphs:
        lines = [line.strip() for line in para.split("\n") if line.strip()]
        merged = " ".join(lines)
        if merged.upper() == title:
            cleaned.append(f"# {title.title()}")
        elif re.fullmatch(r"\d+", merged):
            continue
        else:
            cleaned.append(merged)

    numbered = []
    para_index = 0
    for para in cleaned:
        if para.startswith("# "):
            numbered.append(para)
            continue
        para_index += 1
        numbered.append(f"[P{para_index:04d}] {para}")
    return "\n\n".join(numbered).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", default="data/foreshadow_causality_benchmark/raw_texts")
    parser.add_argument("--out-dir", default="data/foreshadow_causality_benchmark/normalized_texts")
    args = parser.parse_args()

    raw_dir = Path(args.raw_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for spec in STORIES:
        raw_text = read_text(raw_dir / spec.raw_file)
        story_text = extract_between(raw_text, spec.start_pattern, spec.end_pattern, spec.min_line)
        normalized = normalize(story_text, spec.title)
        output = out_dir / f"{spec.story_id}.txt"
        output.write_text(normalized, encoding="utf-8", newline="\n")
        print(f"wrote {output}")


if __name__ == "__main__":
    main()
