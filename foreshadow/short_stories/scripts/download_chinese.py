"""Audit and download Chinese translations for non-Chinese benchmark stories.

Configured sources carry explicit license notes. Public-domain/open-license
sources are preferred; copyright-unclear web reposts may be downloaded for
internal comparison only and are flagged in the audit output.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import time
import urllib.parse
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


WIKISOURCE_OPENSEARCH = "https://zh.wikisource.org/w/api.php?action=opensearch"


@dataclass(frozen=True)
class ChineseSource:
    source_id: str
    url: str
    source_format: str
    license_note: str
    source_note: str = ""


@dataclass(frozen=True)
class TranslationSpec:
    story_id: str
    zh_title: str
    original_title: str
    author: str
    original_language: str
    search_terms: tuple[str, ...]
    configured_sources: tuple[ChineseSource, ...] = field(default_factory=tuple)


TRANSLATIONS = [
    TranslationSpec(
        story_id="speckled_band",
        zh_title="斑点带子案",
        original_title="The Adventure of the Speckled Band",
        author="Arthur Conan Doyle",
        original_language="en",
        search_terms=("斑點帶子案", "斑点带子案", "帶斑點的帶子", "带斑点的带子"),
        configured_sources=(
            ChineseSource(
                source_id="mingzhuxiaoshuo_7100",
                url="https://www.mingzhuxiaoshuo.com/waiguo/79/7100.Html",
                source_format="mingzhuxiaoshuo_content_html",
                license_note="web_repost; translator/license not stated; use for internal comparison only",
                source_note="Avoid jingdianbook mirror because several characters are rendered as images.",
            ),
        ),
    ),
    TranslationSpec(
        story_id="red_headed_league",
        zh_title="红发会",
        original_title="The Red-Headed League",
        author="Arthur Conan Doyle",
        original_language="en",
        search_terms=("紅髮會", "红发会", "紅髮俱樂部", "红发案"),
        configured_sources=(
            ChineseSource(
                source_id="mingzhuxiaoshuo_7094",
                url="https://www.mingzhuxiaoshuo.com/waiguo/79/7094.Html",
                source_format="mingzhuxiaoshuo_content_html",
                license_note="web_repost; translator/license not stated; use for internal comparison only",
            ),
        ),
    ),
    TranslationSpec(
        story_id="necklace",
        zh_title="项链",
        original_title="The Diamond Necklace",
        author="Guy de Maupassant",
        original_language="fr",
        search_terms=("項鏈 莫泊桑", "项链 莫泊桑", "首飾 莫泊桑", "La Parure 中文"),
        configured_sources=(
            ChineseSource(
                source_id="kepub_41498",
                url="https://www.kepub.net/book/41498",
                source_format="kepub_reader_html",
                license_note="web_repost; translator/license not stated; use for internal comparison only",
            ),
        ),
    ),
    TranslationSpec(
        story_id="gift_of_the_magi",
        zh_title="麦琪的礼物",
        original_title="The Gift of the Magi",
        author="O. Henry",
        original_language="en",
        search_terms=("麥琪的禮物", "麦琪的礼物", "聖賢的禮物", "贤者的礼物"),
        configured_sources=(
            ChineseSource(
                source_id="kepub_40005",
                url="https://www.kepub.net/book/40005",
                source_format="kepub_reader_html",
                license_note="web_repost; translator/license not stated; use for internal comparison only",
            ),
        ),
    ),
    TranslationSpec(
        story_id="last_leaf",
        zh_title="最后一片叶子",
        original_title="The Last Leaf",
        author="O. Henry",
        original_language="en",
        search_terms=("最後一片葉子", "最后一片叶子", "最後一片常春藤葉", "最后一片常春藤叶"),
        configured_sources=(
            ChineseSource(
                source_id="diancangwang_bb22af752244",
                url="https://www.diancangwang.cn/waiguomingzhu/e0fe524f6df0/bb22af752244.html",
                source_format="diancang_pageview_html",
                license_note="web_repost; translator/license not stated; use for internal comparison only",
            ),
        ),
    ),
    TranslationSpec(
        story_id="tell_tale_heart",
        zh_title="泄密的心",
        original_title="The Tell-Tale Heart",
        author="Edgar Allan Poe",
        original_language="en",
        search_terms=("洩密的心", "泄密的心", "告密的心", "泄密心"),
        configured_sources=(
            ChineseSource(
                source_id="chinesebooks_212791",
                url="https://chinesebooks.github.io/xiandai/jingdianxiaoxiaoshuo/212791.html",
                source_format="chinesebooks_article_html",
                license_note="web_repost; translator/license not stated; use for internal comparison only",
            ),
        ),
    ),
    TranslationSpec(
        story_id="cask_of_amontillado",
        zh_title="一桶白葡萄酒",
        original_title="The Cask of Amontillado",
        author="Edgar Allan Poe",
        original_language="en",
        search_terms=("一桶白葡萄酒", "一桶阿蒙蒂亚度酒", "阿蒙蒂亚度酒桶", "The Cask of Amontillado 中文"),
        configured_sources=(
            ChineseSource(
                source_id="sohu_238138336",
                url="https://www.sohu.com/a/238138336_304015",
                source_format="sohu_article_html",
                license_note="web_repost; translator/license not stated; use for internal comparison only",
            ),
        ),
    ),
    TranslationSpec(
        story_id="to_build_a_fire",
        zh_title="生火",
        original_title="To Build a Fire",
        author="Jack London",
        original_language="en",
        search_terms=("生火 杰克伦敦", "生火 傑克倫敦", "起火 杰克伦敦", "To Build a Fire 中文"),
        configured_sources=(
            ChineseSource(
                source_id="jianshu_ba38e428bcd7",
                url="https://www.jianshu.com/p/ba38e428bcd7",
                source_format="jianshu_next_data_html",
                license_note="web_repost; translator/license not stated; use for internal comparison only",
            ),
        ),
    ),
]


def fetch_json(url: str) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": "StoneEvalDataset/0.1"})
    with urllib.request.urlopen(req, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_bytes(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "StoneEvalDataset/0.1"})
    with urllib.request.urlopen(req, timeout=120) as response:
        return response.read()


def fetch_text(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 StoneEvalDataset/0.1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=120) as response:
        return decode_response(response.read())


def decode_response(data: bytes) -> str:
    for encoding in ("utf-8-sig", "gb18030"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8-sig", errors="replace")


def strip_html_to_text(markup: str) -> str:
    markup = re.sub(r"<span[^>]+display\s*:\s*none[^>]*>.*?</span>", "", markup, flags=re.DOTALL | re.IGNORECASE)
    markup = re.sub(r"<style.*?</style>", "", markup, flags=re.DOTALL | re.IGNORECASE)
    markup = re.sub(r"<script.*?</script>", "", markup, flags=re.DOTALL | re.IGNORECASE)
    markup = re.sub(r"</p>|</div>|<br\s*/?>", "\n\n", markup, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", markup)
    text = html.unescape(text)
    text = text.replace("\u200b", "")
    return re.sub(r"\n{3,}", "\n\n", text)


def extract_between(markup: str, start_pattern: str, source_format: str) -> str:
    start = re.search(start_pattern, markup, flags=re.IGNORECASE)
    if not start:
        raise ValueError(f"could not find content start for {source_format}")
    remainder = markup[start.end() :]
    end = re.search(r"</div>", remainder, flags=re.IGNORECASE)
    if not end:
        raise ValueError(f"could not find content end for {source_format}")
    return remainder[: end.start()]


def extract_by_regex(markup: str, pattern: str, source_format: str) -> str:
    match = re.search(pattern, markup, flags=re.DOTALL | re.IGNORECASE)
    if not match:
        raise ValueError(f"could not extract content for {source_format}")
    return match.group(1)


def extract_after_marker(text: str, marker: str) -> str:
    if marker not in text:
        return text
    return text.split(marker, 1)[1].strip()


def iter_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        strings: list[str] = []
        for child in value.values():
            strings.extend(iter_strings(child))
        return strings
    if isinstance(value, list):
        strings = []
        for child in value:
            strings.extend(iter_strings(child))
        return strings
    return []


def extract_jianshu_article(markup: str) -> str:
    match = re.search(
        r'<script\s+id="__NEXT_DATA__"\s+type="application/json">(.*?)</script>',
        markup,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if not match:
        raise ValueError("could not find Jianshu __NEXT_DATA__")
    data = json.loads(html.unescape(match.group(1)))
    candidates = [
        value
        for value in iter_strings(data)
        if "<p" in value and ("生火" in value or "寒冷" in value or "育空" in value)
    ]
    if not candidates:
        raise ValueError("could not find Jianshu article body")
    text = strip_html_to_text(max(candidates, key=len))
    for marker in ("六朔　译", "六朔 译", "生火To Build a Fire"):
        if marker in text:
            return text.split(marker, 1)[1].strip()
    return text


def normalize_chinese(text: str, title: str) -> str:
    text = re.sub(r"\r\n?", "\n", text)
    text = text.replace("草AE� 1上", "草坪上")
    text = text.replace("几翧E银丝", "几缕银丝")
    text = re.sub(r"[ \t\u00a0]+", " ", text)
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

    cleaned = [f"# {title}"]
    para_index = 0
    for para in paragraphs:
        para = re.sub(r"\n+", "", para)
        if not para or para == title:
            continue
        if re.fullmatch(r"[一二三四五六七八九十]+", para):
            cleaned.append(f"## {para}")
            continue
        para_index += 1
        cleaned.append(f"[P{para_index:04d}] {para}")
    return "\n\n".join(cleaned).strip() + "\n"


def search_wikisource(term: str) -> dict[str, Any]:
    query = urllib.parse.urlencode(
        {
            "search": term,
            "limit": "10",
            "namespace": "0",
            "format": "json",
        }
    )
    url = f"{WIKISOURCE_OPENSEARCH}&{query}"
    try:
        data = fetch_json(url)
    except urllib.error.HTTPError as exc:
        if exc.code == 429:
            time.sleep(8)
            try:
                data = fetch_json(url)
            except urllib.error.HTTPError as retry_exc:
                return {"term": term, "error": f"HTTP {retry_exc.code}", "matches": []}
            except urllib.error.URLError as retry_exc:
                return {"term": term, "error": str(retry_exc.reason), "matches": []}
        else:
            return {"term": term, "error": f"HTTP {exc.code}", "matches": []}
    except urllib.error.URLError as exc:
        return {"term": term, "error": str(exc.reason), "matches": []}
    titles = data[1] if len(data) > 1 else []
    urls = data[3] if len(data) > 3 else []
    return {"term": term, "matches": [{"title": title, "url": url} for title, url in zip(titles, urls)]}


def audit_sources(output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "policy": (
            "Chinese translation sources are recorded with source-level license notes. "
            "Public-domain/open-license sources are preferred; web reposts without clear "
            "translator/license metadata are flagged for internal comparison only."
        ),
        "stories": [],
    }
    for spec in TRANSLATIONS:
        report["stories"].append(
            {
                "story_id": spec.story_id,
                "zh_title": spec.zh_title,
                "original_title": spec.original_title,
                "author": spec.author,
                "original_language": spec.original_language,
                "configured_sources": [
                    {
                        "source_id": source.source_id,
                        "url": source.url,
                        "source_format": source.source_format,
                        "license_note": source.license_note,
                        "source_note": source.source_note,
                    }
                    for source in spec.configured_sources
                ],
                "wikisource_search": [],
                "status": "downloadable_web_translation" if spec.configured_sources else "needs_translation_source",
            }
        )
        for term in spec.search_terms:
            report["stories"][-1]["wikisource_search"].append(search_wikisource(term))
            time.sleep(2)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {output_path}")


def read_source(source: ChineseSource) -> str:
    text = fetch_text(source.url)
    if source.source_format == "plain":
        return text
    if source.source_format == "wikisource_parse_html":
        parsed = json.loads(text)
        return strip_html_to_text(parsed["parse"]["text"])
    if source.source_format == "kepub_reader_html":
        return strip_html_to_text(extract_between(text, r'<div\s+id="content"[^>]*>', source.source_format))
    if source.source_format == "diancang_pageview_html":
        extracted = strip_html_to_text(extract_between(text, r'<div\s+id="pageview"[^>]*>', source.source_format))
        return extract_after_marker(extracted, "全文：")
    if source.source_format == "chinesebooks_article_html":
        return strip_html_to_text(
            extract_between(text, r'<div\s+class="articleContent"\s+id="articleContent"[^>]*>', source.source_format)
        )
    if source.source_format == "mingzhuxiaoshuo_content_html":
        return strip_html_to_text(
            extract_by_regex(text, r'<div\s+id="content"[^>]*>(.*?)</div>\s*</div>\s*</center>', source.source_format)
        )
    if source.source_format == "sohu_article_html":
        extracted = strip_html_to_text(
            extract_by_regex(
                text,
                r'<article\s+class="article"\s+id="mp-editor"[^>]*>(.*?)</article>',
                source.source_format,
            )
        )
        return extracted.split("▌赏析", 1)[0].strip()
    if source.source_format == "jianshu_next_data_html":
        return extract_jianshu_article(text)
    raise ValueError(f"unknown source_format: {source.source_format}")


def download_configured(raw_dir: Path, out_dir: Path, force: bool = False) -> None:
    raw_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for spec in TRANSLATIONS:
        for source in spec.configured_sources:
            raw_path = raw_dir / f"{spec.story_id}_{source.source_id}.txt"
            out_path = out_dir / f"{spec.story_id}.txt"
            if raw_path.exists() and out_path.exists() and not force:
                print(f"skip existing {out_path}")
                count += 1
                continue
            raw_text = read_source(source)
            raw_path.write_text(raw_text, encoding="utf-8", newline="\n")
            out_path.write_text(normalize_chinese(raw_text, spec.zh_title), encoding="utf-8", newline="\n")
            print(f"wrote {raw_path}")
            print(f"wrote {out_path}")
            count += 1
    if count == 0:
        print("no configured Chinese translation sources to download")


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit/download Chinese translations")
    parser.add_argument("--audit", action="store_true", help="Write Wikisource search audit JSON")
    parser.add_argument("--download", action="store_true", help="Download configured Chinese sources")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--raw-dir", default="foreshadow/short_stories/dataset/raw_texts_zh")
    parser.add_argument("--out-dir", default="foreshadow/short_stories/dataset/normalized_texts_zh")
    parser.add_argument(
        "--audit-output",
        default="foreshadow/short_stories/dataset/docs/chinese_translation_audit.json",
    )
    args = parser.parse_args()

    if args.audit or not args.download:
        audit_sources(Path(args.audit_output))
    if args.download:
        download_configured(Path(args.raw_dir), Path(args.out_dir), force=args.force)


if __name__ == "__main__":
    main()
