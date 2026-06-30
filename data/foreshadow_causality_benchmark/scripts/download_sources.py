"""Download public-domain source texts for the foreshadowing/causality benchmark."""

from __future__ import annotations

import argparse
import urllib.request
from pathlib import Path


SOURCES = {
    "gutenberg_1661_adventures_of_sherlock_holmes.txt": "https://www.gutenberg.org/cache/epub/1661/pg1661.txt",
    "gutenberg_3090_maupassant_original_short_stories.txt": "https://gutenberg.pglaf.org/3/0/9/3090/3090-0.txt",
    "gutenberg_2429_lost_face.txt": "https://gutenberg.pglaf.org/2/4/2/2429/2429-0.txt",
    "wikisource_luxun_yao_parse.json": "https://zh.wikisource.org/w/api.php?action=parse&page=%E8%97%A5&prop=text&format=json&formatversion=2",
    "wikisource_liaozhai_vol04_api.json": "https://zh.wikisource.org/w/api.php?action=query&prop=revisions&rvprop=content&rvslots=main&format=json&titles=%E8%81%8A%E9%BD%8B%E5%BF%97%E7%95%B0/%E7%AC%AC04%E5%8D%B7",
}


def download(url: str, target: Path, force: bool = False) -> None:
    if target.exists() and not force:
        print(f"skip existing {target}")
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "StoneEvalDataset/0.1"})
    print(f"download {url}")
    with urllib.request.urlopen(req, timeout=180) as response, target.open("wb") as out:
        while True:
            chunk = response.read(65536)
            if not chunk:
                break
            out.write(chunk)
    print(f"wrote {target} ({target.stat().st_size} bytes)")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", default="data/foreshadow_causality_benchmark/raw_texts")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    raw_dir = Path(args.raw_dir)
    for filename, url in SOURCES.items():
        download(url, raw_dir / filename, force=args.force)


if __name__ == "__main__":
    main()
