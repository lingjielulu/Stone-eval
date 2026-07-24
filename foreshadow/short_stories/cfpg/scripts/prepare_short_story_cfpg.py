"""Build sentence-level CFPG cases from verified short-story triples."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from cfpg_short_story import build_cases, write_jsonl


EXPERIMENT_ROOT = Path(
    "foreshadow/short_stories/cfpg"
)
DEFAULT_TRIPLES = Path(
    "foreshadow/short_stories/cfpg/results/extraction/runs/"
    "20260701_short_story_cfpg_v3_verified/"
    "accepted_triples_20260701_short_story_cfpg_v3_verified.jsonl"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--triples", type=Path, default=DEFAULT_TRIPLES)
    parser.add_argument(
        "--normalized-dir",
        type=Path,
        default=Path("foreshadow/short_stories/dataset/normalized_texts"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=EXPERIMENT_ROOT / "data/cfpg_cases.jsonl",
    )
    parser.add_argument("--story-id", action="append", default=[])
    parser.add_argument(
        "--taxonomy",
        type=Path,
        default=EXPERIMENT_ROOT / "data/cfpg_taxonomy_v2.json",
    )
    args = parser.parse_args()

    taxonomy = json.loads(args.taxonomy.read_text(encoding="utf-8")) if args.taxonomy else None
    cases = build_cases(
        args.triples, args.normalized_dir, set(args.story_id) or None, taxonomy=taxonomy
    )
    write_jsonl(args.output, cases)
    print(f"wrote {len(cases)} cases to {args.output}")


if __name__ == "__main__":
    main()
