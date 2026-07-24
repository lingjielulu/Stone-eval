#!/usr/bin/env python3
"""Local server for bilingual F–T–P annotation.

The server intentionally uses only Python's standard library.  It serves the
browser application and stores human annotations separately from the seed YAML
and CFPG experiment outputs.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse


APP_ROOT = Path(__file__).resolve().parent
SHORT_STORY_ROOT = APP_ROOT.parent
DATASET_ROOT = SHORT_STORY_ROOT / "dataset"
TEXT_ROOT = DATASET_ROOT / "normalized_texts"
ZH_TEXT_ROOT = DATASET_ROOT / "normalized_texts_zh"
MANUAL_ROOT = DATASET_ROOT / "annotations" / "manual"
CFPG_CASES = SHORT_STORY_ROOT / "cfpg" / "data" / "cfpg_cases.jsonl"
TAXONOMY_PATH = SHORT_STORY_ROOT / "cfpg" / "data" / "cfpg_taxonomy_v2.json"
STATIC_ROOT = APP_ROOT / "static"

ID_RE = re.compile(r"^[a-z0-9_]+$")
PARAGRAPH_RE = re.compile(r"^\[(P\d{4})\]\s*(.*)$")
SPAN_RE = re.compile(r"^P\d{4}(?:-P\d{4})?$")

STORY_META = {
    "cask_of_amontillado": ("The Cask of Amontillado", "一桶白葡萄酒", "Edgar Allan Poe"),
    "cricket": ("Cricket", "促织", "蒲松龄"),
    "gift_of_the_magi": ("The Gift of the Magi", "麦琪的礼物", "O. Henry"),
    "last_leaf": ("The Last Leaf", "最后一片叶子", "O. Henry"),
    "medicine": ("Medicine", "药", "鲁迅"),
    "necklace": ("The Necklace", "项链", "Guy de Maupassant"),
    "rashomon": ("Rashōmon", "罗生门", "芥川龙之介"),
    "red_headed_league": ("The Red-Headed League", "红发会", "Arthur Conan Doyle"),
    "shiji_hongmenyan": ("The Feast at Hong Gate", "鸿门宴", "司马迁"),
    "shiji_jingke": ("Jing Ke's Attempt on Qin", "荆轲刺秦王", "司马迁"),
    "shiji_wanbi_guizhao": ("Returning the Jade Intact", "完璧归赵", "司马迁"),
    "speckled_band": ("The Speckled Band", "斑点带子案", "Arthur Conan Doyle"),
    "tell_tale_heart": ("The Tell-Tale Heart", "泄密的心", "Edgar Allan Poe"),
    "to_build_a_fire": ("To Build a Fire", "生火", "Jack London"),
}

TAXONOMY = {
    "primary_types": {
        "object": "物件",
        "event": "事件",
        "dialogue": "对话",
        "rule": "规则",
        "environment_description": "环境描写",
        "character_state": "人物状态",
        "narrator_commentary": "叙述者评论",
    },
    "narrative_functions": {
        "direct_setup": "直接铺垫",
        "anomaly": "反常线索",
        "misdirection": "误导",
        "warning": "警告",
        "retrospective_reinterpretation": "回溯重释",
        "ironic_contrast": "反讽对照",
        "symbolic_reframing": "象征重构",
    },
    "payoff_types": {
        "literal": "直接兑现",
        "ironic": "反讽兑现",
        "symbolic": "象征兑现",
        "negative": "否定兑现",
        "misdirection": "误导揭示",
        "delayed_revelation": "延迟揭示",
    },
    "confidence": {"high": "高", "medium": "中", "low": "低"},
    "status": {"draft": "草稿", "reviewed": "已复核", "adjudicated": "已裁定"},
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def valid_story_id(story_id: str) -> bool:
    return bool(ID_RE.fullmatch(story_id)) and (TEXT_ROOT / f"{story_id}.txt").is_file()


def parse_text(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    heading = ""
    paragraphs: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("# ") and not heading:
            heading = line[2:].strip()
            continue
        match = PARAGRAPH_RE.match(line)
        if match:
            current = {"id": match.group(1), "text": match.group(2).strip()}
            paragraphs.append(current)
        elif current:
            current["text"] += "\n" + line
        elif not heading:
            heading = line
    return {"heading": heading, "paragraphs": paragraphs}


def load_saved(story_id: str) -> dict[str, Any]:
    path = MANUAL_ROOT / f"{story_id}.json"
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return {
        "schema_version": "ftp_manual_annotation_v1",
        "story_id": story_id,
        "annotations": [],
        "updated_at": None,
    }


def list_stories() -> list[dict[str, Any]]:
    stories = []
    for path in sorted(TEXT_ROOT.glob("*.txt")):
        story_id = path.stem
        en_title, zh_title, author = STORY_META.get(
            story_id, (story_id.replace("_", " ").title(), story_id, "")
        )
        source_language = (
            "zh" if story_id.startswith("shiji_") or story_id in {"medicine", "cricket"}
            else "ja" if story_id == "rashomon"
            else "en"
        )
        saved = load_saved(story_id)
        stories.append(
            {
                "story_id": story_id,
                "title_en": en_title,
                "title_zh": zh_title,
                "author": author,
                "source_language": source_language,
                "has_en": source_language == "en",
                "has_zh": source_language == "zh" or (ZH_TEXT_ROOT / path.name).is_file(),
                "has_parallel_zh": (ZH_TEXT_ROOT / path.name).is_file(),
                "annotation_count": len(saved.get("annotations", [])),
                "reviewed_count": sum(
                    item.get("status") in {"reviewed", "adjudicated"}
                    for item in saved.get("annotations", [])
                ),
            }
        )
    return stories


def story_payload(story_id: str) -> dict[str, Any]:
    source = parse_text(TEXT_ROOT / f"{story_id}.txt")
    translated = parse_text(ZH_TEXT_ROOT / f"{story_id}.txt")
    meta = next(item for item in list_stories() if item["story_id"] == story_id)
    if meta["source_language"] == "en":
        texts = {"en": source, "zh": translated}
    elif meta["source_language"] == "zh":
        texts = {"en": None, "zh": source}
    else:
        texts = {"en": source, "zh": translated}
    return {"story": meta, "texts": texts}


def load_seeds(story_id: str) -> list[dict[str, Any]]:
    if not CFPG_CASES.is_file():
        return []
    seeds = []
    with CFPG_CASES.open(encoding="utf-8") as stream:
        for line in stream:
            if not line.strip():
                continue
            case = json.loads(line)
            if case.get("story_id") != story_id:
                continue
            foreshadow = case.get("foreshadow") or {}
            trigger = case.get("trigger") or {}
            payoff = case.get("payoff") or {}
            def inferred_span(value: Any) -> str:
                paragraph_ids = sorted(
                    set(re.findall(r"P\d{4}", json.dumps(value, ensure_ascii=False))),
                    key=lambda paragraph_id: int(paragraph_id[1:]),
                )
                if not paragraph_ids:
                    return ""
                if len(paragraph_ids) == 1:
                    return paragraph_ids[0]
                return f"{paragraph_ids[0]}-{paragraph_ids[-1]}"

            seeds.append(
                {
                    "seed_id": case.get("case_id"),
                    "accepted": bool(case.get("accepted", True)),
                    "primary_type": foreshadow.get("primary_type", ""),
                    "narrative_function": foreshadow.get("narrative_function", ""),
                    "payoff_type": payoff.get("type", ""),
                    "rationale": case.get("relation_description", ""),
                    "f": {
                        "span": foreshadow.get("span", ""),
                        "summary_en": foreshadow.get("description", ""),
                        "summary_zh": foreshadow.get("description_zh", ""),
                    },
                    "t": {
                        "span": trigger.get("span", "") or inferred_span(trigger),
                        "summary_en": trigger.get("description", ""),
                        "summary_zh": case.get("trigger_zh", ""),
                    },
                    "p": {
                        "span": payoff.get("span", ""),
                        "summary_en": payoff.get("description", ""),
                        "summary_zh": payoff.get("description_zh", ""),
                    },
                }
            )
    return seeds


def validate_annotations(payload: Any, story_id: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["请求正文必须是 JSON 对象"]
    if payload.get("story_id") != story_id:
        errors.append("story_id 与 URL 不一致")
    annotations = payload.get("annotations")
    if not isinstance(annotations, list):
        return errors + ["annotations 必须是数组"]
    seen: set[str] = set()
    for index, item in enumerate(annotations):
        prefix = f"第 {index + 1} 条"
        if not isinstance(item, dict):
            errors.append(f"{prefix}不是对象")
            continue
        annotation_id = item.get("annotation_id", "")
        if not isinstance(annotation_id, str) or not annotation_id:
            errors.append(f"{prefix}缺少 annotation_id")
        elif annotation_id in seen:
            errors.append(f"{prefix} annotation_id 重复")
        seen.add(annotation_id)
        story = story_payload(story_id)
        text_by_language = {
            language: {
                paragraph["id"]: paragraph["text"]
                for paragraph in (text_data or {}).get("paragraphs", [])
            }
            for language, text_data in story["texts"].items()
        }
        for key in ("f", "t", "p"):
            part = item.get(key)
            if not isinstance(part, dict):
                errors.append(f"{prefix}缺少 {key.upper()} 对象")
                continue
            for span_key in ("span", "span_en", "span_zh"):
                span = part.get(span_key, "")
                if span and not SPAN_RE.fullmatch(span):
                    errors.append(f"{prefix} {key.upper()} 的 {span_key} 格式无效")
            for language in ("en", "zh"):
                selection = part.get(f"selection_{language}")
                if selection is None:
                    continue
                if not isinstance(selection, dict):
                    errors.append(f"{prefix} {key.upper()} 的 selection_{language} 必须是对象")
                    continue
                required = (
                    "start_paragraph", "start_offset",
                    "end_paragraph", "end_offset", "text",
                )
                if any(field not in selection for field in required):
                    errors.append(f"{prefix} {key.upper()} 的 selection_{language} 字段不完整")
                    continue
                start_id = selection["start_paragraph"]
                end_id = selection["end_paragraph"]
                paragraphs = text_by_language[language]
                if start_id not in paragraphs or end_id not in paragraphs:
                    errors.append(f"{prefix} {key.upper()} 的 {language} 段落锚点不存在")
                    continue
                start_offset = selection["start_offset"]
                end_offset = selection["end_offset"]
                if (
                    not isinstance(start_offset, int)
                    or not isinstance(end_offset, int)
                    or start_offset < 0
                    or end_offset < 0
                    or start_offset > len(paragraphs[start_id])
                    or end_offset > len(paragraphs[end_id])
                ):
                    errors.append(f"{prefix} {key.upper()} 的 {language} 字符位置越界")
                if int(start_id[1:]) > int(end_id[1:]) or (
                    start_id == end_id and start_offset >= end_offset
                ):
                    errors.append(f"{prefix} {key.upper()} 的 {language} 选择范围顺序无效")
        status = item.get("status", "draft")
        if status not in TAXONOMY["status"]:
            errors.append(f"{prefix}状态无效")
        primary_type = item.get("primary_type", "")
        if primary_type and primary_type not in TAXONOMY["primary_types"]:
            errors.append(f"{prefix}伏笔类型无效")
        function = item.get("narrative_function", "")
        if function and function not in TAXONOMY["narrative_functions"]:
            errors.append(f"{prefix}叙事功能无效")
        if status in {"reviewed", "adjudicated"}:
            for field, label in (
                ("primary_type", "伏笔类型"),
                ("narrative_function", "叙事功能"),
                ("rationale", "原因解释"),
            ):
                if not item.get(field):
                    errors.append(f"{prefix}标为已复核前必须填写{label}")
            for key in ("f", "t", "p"):
                part = item.get(key, {})
                if not any(part.get(name) for name in ("span", "span_en", "span_zh")):
                    errors.append(f"{prefix}标为已复核前必须填写 {key.upper()} 范围")
    return errors


def save_annotations(story_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    MANUAL_ROOT.mkdir(parents=True, exist_ok=True)
    previous = load_saved(story_id)
    created_by_id = {
        item.get("annotation_id"): item.get("created_at")
        for item in previous.get("annotations", [])
    }
    now = utc_now()
    clean_items = []
    for item in payload["annotations"]:
        clean = dict(item)
        clean["story_id"] = story_id
        clean["created_at"] = created_by_id.get(clean["annotation_id"]) or clean.get("created_at") or now
        clean["updated_at"] = now
        clean_items.append(clean)
    document = {
        "schema_version": "ftp_manual_annotation_v1",
        "story_id": story_id,
        "annotations": clean_items,
        "updated_at": now,
    }
    destination = MANUAL_ROOT / f"{story_id}.json"
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{story_id}.", suffix=".tmp", dir=MANUAL_ROOT
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(document, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temporary_name, destination)
    finally:
        if os.path.exists(temporary_name):
            os.unlink(temporary_name)
    return document


class AnnotationHandler(SimpleHTTPRequestHandler):
    server_version = "FTPAnnotation/1.0"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(STATIC_ROOT), **kwargs)

    def send_json(self, value: Any, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        if path == "/api/stories":
            self.send_json({"stories": list_stories()})
            return
        if path == "/api/taxonomy":
            taxonomy = dict(TAXONOMY)
            if TAXONOMY_PATH.is_file():
                taxonomy["source_version"] = json.loads(
                    TAXONOMY_PATH.read_text(encoding="utf-8")
                ).get("version")
            self.send_json(taxonomy)
            return
        for prefix, loader in (
            ("/api/story/", story_payload),
            ("/api/annotations/", load_saved),
            ("/api/seeds/", lambda story_id: {"seeds": load_seeds(story_id)}),
        ):
            if path.startswith(prefix):
                story_id = path[len(prefix) :]
                if not valid_story_id(story_id):
                    self.send_json({"error": "小说不存在"}, HTTPStatus.NOT_FOUND)
                    return
                self.send_json(loader(story_id))
                return
        if path in {"/", "/index.html"}:
            self.path = "/index.html"
        super().do_GET()

    def do_PUT(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        prefix = "/api/annotations/"
        if not parsed.path.startswith(prefix):
            self.send_json({"error": "接口不存在"}, HTTPStatus.NOT_FOUND)
            return
        story_id = unquote(parsed.path[len(prefix) :])
        if not valid_story_id(story_id):
            self.send_json({"error": "小说不存在"}, HTTPStatus.NOT_FOUND)
            return
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length > 5_000_000:
                raise ValueError("请求过大")
            payload = json.loads(self.rfile.read(content_length))
        except (ValueError, json.JSONDecodeError) as exc:
            self.send_json({"error": f"无法读取 JSON：{exc}"}, HTTPStatus.BAD_REQUEST)
            return
        errors = validate_annotations(payload, story_id)
        if errors:
            self.send_json({"error": "校验失败", "details": errors}, HTTPStatus.BAD_REQUEST)
            return
        self.send_json(save_annotations(story_id, payload))

    def log_message(self, format: str, *args: Any) -> None:
        print(f"[annotation] {self.address_string()} - {format % args}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), AnnotationHandler)
    print(f"F–T–P annotation app: http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
