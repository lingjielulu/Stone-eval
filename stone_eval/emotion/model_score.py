"""Model-based emotional arc scoring.

This module is intentionally separate from ``hedonometer.py``.  The latter is
scheme 1: deterministic dictionary scoring.  This module is scheme 2: model
scoring, either via an OpenAI-compatible LLM endpoint or a local model baseline.
"""

from __future__ import annotations

import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from openai import OpenAI
from tqdm import tqdm

from .hedonometer import book_tokens


PROMPT_VERSION = "model_score_zh_literary_v1"


@dataclass(frozen=True)
class LLMEmotionConfig:
    model: str
    api_key: str
    api_base: str | None = None
    max_retries: int = 3
    retry_delay: float = 3.0
    temperature: float = 0.0
    max_window_chars: int = 12000


def _build_client(config: LLMEmotionConfig) -> OpenAI:
    kwargs: dict[str, Any] = {"api_key": config.api_key}
    if config.api_base:
        kwargs["base_url"] = config.api_base.rstrip("/")
    return OpenAI(**kwargs)


def _fixed_windows(book_json: Path, points: int, window_size: int) -> tuple[list[str], list[dict]]:
    tokens = book_tokens(book_json)
    if not tokens:
        raise ValueError(f"No tokens found in {book_json}")
    if len(tokens) <= window_size:
        window_size = max(1, len(tokens) // 2)
    points = max(1, points)
    max_start = max(0, len(tokens) - window_size)
    starts = [
        round(i * max_start / (points - 1)) if points > 1 else 0
        for i in range(points)
    ]
    windows = []
    for index, start in enumerate(starts):
        end = min(len(tokens), start + window_size)
        windows.append(
            {
                "index": index,
                "start_token": start,
                "end_token": end,
                "percent": round(index / (points - 1) * 100, 4) if points > 1 else 0.0,
                "text": "".join(tokens[start:end]),
            }
        )
    return tokens, windows


def _limit_text(text: str, max_chars: int) -> tuple[str, str]:
    if max_chars <= 0 or len(text) <= max_chars:
        return text, "none"
    half = max_chars // 2
    return (
        text[:half] + "\n...[中间略去，保留窗口首尾以控制模型调用长度]...\n" + text[-half:],
        "head_tail",
    )


def _score_prompt(text: str) -> list[dict[str, str]]:
    system = (
        "你是中文文学情感弧线打分器。你的任务是给文本窗口的整体情绪正向性打分，"
        "分数范围为1到9：1=极端负向/悲痛/恐惧/压抑，5=中性或正负混合，"
        "9=极端正向/欢乐/圆满/轻快。只输出JSON，不要输出解释性前后缀。"
    )
    user = f"""请评估下面这段《红楼梦》文本窗口的整体情绪正向性。

要求：
1. 结合叙事情境、人物情绪、事件走向和气氛判断，不要只数情绪词。
2. 古典小说中“笑”“喜”“恼”“羞”等词要按上下文理解。
3. 输出必须是一个合法JSON对象，字段为：
   - happiness_score: 1到9之间的浮点数
   - confidence: 0到1之间的浮点数
   - valence_label: "negative" | "mixed_negative" | "neutral" | "mixed_positive" | "positive"
   - rationale_short: 不超过40个汉字的极简理由

文本：
<<<
{text}
>>>"""
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def _extract_json_object(content: str) -> dict:
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?", "", content).strip()
        content = re.sub(r"```$", "", content).strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", content, flags=re.S)
        if not match:
            raise
        return json.loads(match.group(0))


def _normalize_score(raw: dict) -> dict:
    score = float(raw.get("happiness_score", 5.0))
    confidence = float(raw.get("confidence", 0.0))
    score = min(9.0, max(1.0, score))
    confidence = min(1.0, max(0.0, confidence))
    label = str(raw.get("valence_label", "neutral"))
    if label not in {
        "negative",
        "mixed_negative",
        "neutral",
        "mixed_positive",
        "positive",
    }:
        label = "neutral"
    rationale = str(raw.get("rationale_short", ""))[:40]
    return {
        "happiness_score": round(score, 4),
        "confidence": round(confidence, 4),
        "valence_label": label,
        "rationale_short": rationale,
    }


def score_text_with_llm(text: str, config: LLMEmotionConfig) -> dict:
    client = _build_client(config)
    last_error: Exception | None = None
    for attempt in range(config.max_retries):
        try:
            messages = _score_prompt(text)
            try:
                response = client.chat.completions.create(
                    model=config.model,
                    messages=messages,
                    temperature=config.temperature,
                    response_format={"type": "json_object"},
                )
            except Exception:
                response = client.chat.completions.create(
                    model=config.model,
                    messages=messages,
                    temperature=config.temperature,
                )
            content = response.choices[0].message.content or "{}"
            return _normalize_score(_extract_json_object(content))
        except Exception as exc:  # pragma: no cover - network/API dependent
            last_error = exc
            if attempt < config.max_retries - 1:
                time.sleep(config.retry_delay * (attempt + 1))
    raise RuntimeError(f"LLM emotion scoring failed: {last_error}") from last_error


def _partial_payload(
    book_json: Path,
    config: LLMEmotionConfig,
    points: int,
    window_size: int,
    tokens: int,
    arc: list[dict],
) -> dict:
    completed = [point for point in arc if not point.get("error")]
    mean = (
        sum(point["happiness_score"] for point in completed) / len(completed)
        if completed
        else None
    )
    return {
        "scheme": "model_score",
        "scorer_type": "llm",
        "method": "OpenAI-compatible LLM sliding-window literary emotion scoring",
        "prompt_version": PROMPT_VERSION,
        "book_json": str(book_json),
        "model": config.model,
        "api_base": config.api_base,
        "tokens": tokens,
        "points": points,
        "window_size": window_size,
        "max_window_chars": config.max_window_chars,
        "completed_points": len(completed),
        "mean_happiness": round(mean, 4) if mean is not None else None,
        "arc": sorted(arc, key=lambda point: point["index"]),
    }


def write_llm_window_arc(
    book_json: Path,
    output: Path,
    config: LLMEmotionConfig,
    points: int = 80,
    window_size: int = 5000,
    concurrent: int = 1,
    resume: bool = True,
    dry_run: bool = False,
) -> dict:
    tokens, windows = _fixed_windows(book_json, points=points, window_size=window_size)
    existing_by_index: dict[int, dict] = {}
    if resume and output.exists():
        existing = json.loads(output.read_text(encoding="utf-8"))
        for point in existing.get("arc", []):
            if "index" in point and not point.get("error"):
                existing_by_index[int(point["index"])] = point

    arc: list[dict] = [existing_by_index[index] for index in sorted(existing_by_index)]
    pending = [window for window in windows if window["index"] not in existing_by_index]
    output.parent.mkdir(parents=True, exist_ok=True)

    def score_window(window: dict) -> dict:
        text, truncation = _limit_text(window["text"], config.max_window_chars)
        base = {
            "index": window["index"],
            "start_token": window["start_token"],
            "end_token": window["end_token"],
            "percent": window["percent"],
            "input_chars": len(window["text"]),
            "scored_chars": len(text),
            "truncation": truncation,
        }
        if dry_run:
            return {
                **base,
                "happiness_score": 5.0,
                "confidence": 0.0,
                "valence_label": "neutral",
                "rationale_short": "dry-run未调用模型",
            }
        try:
            return {**base, **score_text_with_llm(text, config)}
        except Exception as exc:  # pragma: no cover - network/API dependent
            return {**base, "error": str(exc)}

    if concurrent <= 1:
        for window in tqdm(pending, desc=f"LLM emotion scoring ({config.model})"):
            point = score_window(window)
            arc = [item for item in arc if item["index"] != point["index"]]
            arc.append(point)
            output.write_text(
                json.dumps(
                    _partial_payload(
                        book_json, config, points, window_size, len(tokens), arc
                    ),
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
    else:
        with ThreadPoolExecutor(max_workers=concurrent) as executor:
            future_map = {executor.submit(score_window, window): window for window in pending}
            for future in tqdm(
                as_completed(future_map),
                total=len(future_map),
                desc=f"LLM emotion scoring ({config.model})",
            ):
                point = future.result()
                arc = [item for item in arc if item["index"] != point["index"]]
                arc.append(point)
                output.write_text(
                    json.dumps(
                        _partial_payload(
                            book_json, config, points, window_size, len(tokens), arc
                        ),
                        ensure_ascii=False,
                        indent=2,
                    ),
                    encoding="utf-8",
                )

    payload = _partial_payload(book_json, config, points, window_size, len(tokens), arc)
    completed = [point for point in payload["arc"] if not point.get("error")]
    if completed:
        mean = sum(point["happiness_score"] for point in completed) / len(completed)
        for point in payload["arc"]:
            if not point.get("error"):
                point["centered_happiness"] = round(point["happiness_score"] - mean, 4)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def write_snownlp_model_arc(
    book_json: Path,
    output: Path,
    points: int = 100,
    window_size: int = 10000,
) -> dict:
    from .hedonometer import snownlp_window_arc

    payload = snownlp_window_arc(book_json, points=points, window_size=window_size)
    payload.update(
        {
            "scheme": "model_score",
            "scorer_type": "local_model",
            "method": "SnowNLP local sliding-window sentiment scoring",
        }
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload
