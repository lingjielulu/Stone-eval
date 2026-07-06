"""Normalize downloaded story collections into one UTF-8 text file per story.

This is intentionally conservative: it extracts known public-domain chapters by
heading boundaries, removes Gutenberg boilerplate, and writes paragraph-numbered
plain text for stable annotation references.
"""

from __future__ import annotations

import argparse
import html
import json
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
    source_format: str = "plain"
    ensure_title_heading: bool = False


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
    StorySpec(
        story_id="medicine",
        raw_file="wikisource_luxun_yao_parse.json",
        start_pattern=r"^一\[编辑\]\s*$",
        end_pattern=r"^1996年1月1日",
        title="藥",
        source_format="wikisource_parse_html",
        ensure_title_heading=True,
    ),
    StorySpec(
        story_id="cricket",
        raw_file="wikisource_liaozhai_vol04_api.json",
        start_pattern=r"^==促織==\s*$",
        end_pattern=r"^==柳秀才==\s*$",
        title="促織",
        source_format="wikisource_revisions_wikitext",
    ),
    StorySpec(
        story_id="red_headed_league",
        raw_file="gutenberg_1661_adventures_of_sherlock_holmes.txt",
        start_pattern=r"^II\. THE RED-HEADED LEAGUE\s*$",
        end_pattern=r"^III\. A CASE OF IDENTITY\s*$",
        title="THE RED-HEADED LEAGUE",
        min_line=1000,
    ),
    StorySpec(
        story_id="gift_of_the_magi",
        raw_file="gutenberg_7256_gift_of_the_magi.txt",
        start_pattern=r"^The Gift of the Magi\s*$",
        end_pattern=r"^\*\*\* END OF THE PROJECT GUTENBERG",
        title="THE GIFT OF THE MAGI",
    ),
    StorySpec(
        story_id="last_leaf",
        raw_file="gutenberg_3707_trimmed_lamp.txt",
        start_pattern=r"^THE LAST LEAF\.?\s*$",
        end_pattern=r"^THE COUNT AND THE WEDDING GUEST\.?\s*$",
        title="THE LAST LEAF",
        min_line=5000,
    ),
    StorySpec(
        story_id="tell_tale_heart",
        raw_file="gutenberg_2148_poe_vol2.txt",
        start_pattern=r"^THE TELL-TALE HEART\.?\s*$",
        end_pattern=r"^BERENICE\.?\s*$",
        title="THE TELL-TALE HEART",
        min_line=5000,
        ensure_title_heading=True,
    ),
    StorySpec(
        story_id="cask_of_amontillado",
        raw_file="gutenberg_2148_poe_vol2.txt",
        start_pattern=r"^THE CASK OF AMONTILLADO\.?\s*$",
        end_pattern=r"^THE IMP OF THE PERVERSE\.?\s*$",
        title="THE CASK OF AMONTILLADO",
        min_line=100,
        ensure_title_heading=True,
    ),
    StorySpec(
        story_id="rashomon",
        raw_file="aozora_rashomon.txt",
        start_pattern=r"^羅生門\s*$",
        end_pattern=r"^底本：",
        title="羅生門",
        source_format="aozora_plain",
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


def strip_html_to_text(markup: str) -> str:
    markup = re.sub(r"<style.*?</style>", "", markup, flags=re.DOTALL | re.IGNORECASE)
    markup = re.sub(r"<script.*?</script>", "", markup, flags=re.DOTALL | re.IGNORECASE)
    markup = re.sub(r"<h[1-6][^>]*>", "\n\n", markup, flags=re.IGNORECASE)
    markup = re.sub(r"</p>|</div>|<br\s*/?>", "\n\n", markup, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", markup)
    text = html.unescape(text)
    text = text.replace("\u200b", "")
    return re.sub(r"\n{3,}", "\n\n", text)


def read_source(path: Path, source_format: str) -> str:
    raw_text = read_text(path)
    if source_format == "plain" or source_format == "aozora_plain":
        return raw_text

    data = json.loads(raw_text)
    if source_format == "wikisource_parse_html":
        return strip_html_to_text(data["parse"]["text"])
    if source_format == "wikisource_revisions_wikitext":
        page = next(iter(data["query"]["pages"].values()))
        return page["revisions"][0]["slots"]["main"]["*"]

    raise ValueError(f"unknown source_format: {source_format}")


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


def normalize(text: str, title: str, ensure_title_heading: bool = False) -> str:
    text = text.replace("\t", " ")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \u00a0]+", " ", text)
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

    cleaned = []
    for para in paragraphs:
        lines = [line.strip() for line in para.split("\n") if line.strip()]
        merged = " ".join(lines)
        if (merged.upper().rstrip(".") == title.upper().rstrip(".")
                or merged.upper() == title.upper()):
            cleaned.append(f"# {title.title()}")
        elif re.fullmatch(r"\d+", merged):
            continue
        elif re.fullmatch(r"[一二三四五六七八九十]+(\[编辑\])?", merged):
            cleaned.append(f"## {merged.replace('[编辑]', '')}")
        elif re.fullmatch(r"==[^=]+==", merged):
            heading = merged.strip("=").strip()
            cleaned.append(f"# {heading}")
        else:
            cleaned.append(merged)

    if ensure_title_heading and cleaned and not cleaned[0].startswith("# "):
        cleaned.insert(0, f"# {title.title()}")

    numbered = []
    para_index = 0
    for para in cleaned:
        if para.startswith("#"):
            numbered.append(para)
            continue
        para_index += 1
        numbered.append(f"[P{para_index:04d}] {para}")
    return "\n\n".join(numbered).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", default="data/foreshadow_causality_benchmark/novels/raw_texts")
    parser.add_argument("--out-dir", default="data/foreshadow_causality_benchmark/novels/normalized_texts")
    args = parser.parse_args()

    raw_dir = Path(args.raw_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for spec in STORIES:
        raw_text = read_source(raw_dir / spec.raw_file, spec.source_format)
        story_text = extract_between(raw_text, spec.start_pattern, spec.end_pattern, spec.min_line)
        normalized = normalize(story_text, spec.title, spec.ensure_title_heading)
        output = out_dir / f"{spec.story_id}.txt"
        output.write_text(normalized, encoding="utf-8", newline="\n")
        print(f"wrote {output}")


if __name__ == "__main__":
    main()
