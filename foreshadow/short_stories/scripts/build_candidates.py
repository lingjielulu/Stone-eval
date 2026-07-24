"""Generate weak candidate annotations for manual correction.

The output is not gold data. It provides paragraph-level candidates for an
annotator to accept, split, merge, or delete before validation.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


EVENT_MARKERS = re.compile(
    r"\b(killed|died|found|saw|heard|said|told|asked|decided|went|came|lost|"
    r"bought|sold|opened|struck|built|fell|returned|confessed|revealed)\b",
    re.IGNORECASE,
)
FORESHADOW_MARKERS = re.compile(
    r"\b(strange|curious|peculiar|mysterious|warning|danger|cold|fire|"
    r"necklace|jewel|ventilator|bell-rope|safe|milk|snake|watch|hair)\b",
    re.IGNORECASE,
)
CAUSAL_MARKERS = re.compile(r"\b(because|therefore|so that|so|as a result|in order to|for this reason)\b", re.IGNORECASE)

ZH_EVENT_MARKERS = re.compile(r"(死|殺|買|賣|喫|吃|走|問|說|聞|見|得|失|投井|進|獻|醒|化|咳|治|葬|祭)")
ZH_FORESHADOW_MARKERS = re.compile(r"(藥|饅頭|人血|花環|烏鴉|促織|蟋蟀|巫|畫|宮中|征|井|魂|斗|雞)")
ZH_CAUSAL_MARKERS = re.compile(r"(因|遂|乃|故|以|使|致|為|由是|所以|于是|於是)")


def iter_paragraphs(path: Path):
    for block in path.read_text(encoding="utf-8").split("\n\n"):
        block = block.strip()
        if not block or block.startswith("# "):
            continue
        match = re.match(r"^\[(P\d+)\]\s+(.*)$", block, re.DOTALL)
        if match:
            yield match.group(1), match.group(2).strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("story_id")
    parser.add_argument("--normalized-dir", default="foreshadow/short_stories/dataset/normalized_texts")
    parser.add_argument("--out-dir", default="foreshadow/short_stories/dataset/annotations/candidates")
    args = parser.parse_args()

    story_path = Path(args.normalized_dir) / f"{args.story_id}.txt"
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    events = []
    foreshadowing = []
    causal_hints = []
    for para_id, text in iter_paragraphs(story_path):
        if EVENT_MARKERS.search(text) or ZH_EVENT_MARKERS.search(text):
            events.append({"paragraph_id": para_id, "candidate_summary": text[:220]})
        if FORESHADOW_MARKERS.search(text) or ZH_FORESHADOW_MARKERS.search(text):
            foreshadowing.append({"paragraph_id": para_id, "candidate_signal": text[:220]})
        if CAUSAL_MARKERS.search(text) or ZH_CAUSAL_MARKERS.search(text):
            causal_hints.append({"paragraph_id": para_id, "candidate_evidence": text[:220]})

    output = {
        "story_id": args.story_id,
        "note": "Weak candidates only; human annotators should correct before gold use.",
        "candidate_events": events,
        "candidate_foreshadowing": foreshadowing,
        "candidate_causal_hints": causal_hints,
    }
    target = out_dir / f"{args.story_id}_candidates.json"
    target.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {target}")


if __name__ == "__main__":
    main()
