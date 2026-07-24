"""Local Chinese happiness scoring similar to a lightweight Hedonometer.

The scorer is intentionally deterministic and offline.  It is not a substitute
for a calibrated sentiment model, but it produces a stable 1-9 positivity curve
that is useful for comparing long-form narrative segments.
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Iterable


POSITIVE_WEIGHTS = {
    "大喜": 2.2,
    "欢喜": 2.0,
    "喜欢": 1.8,
    "高兴": 2.0,
    "快活": 1.8,
    "快乐": 2.0,
    "喜悦": 2.1,
    "欢悦": 2.1,
    "欢笑": 1.9,
    "笑": 0.9,
    "喜": 1.0,
    "乐": 0.8,
    "爱": 0.8,
    "怜爱": 1.0,
    "可爱": 1.1,
    "称赞": 1.1,
    "赞": 0.7,
    "妙": 1.0,
    "佳": 0.8,
    "好": 0.7,
    "美": 0.9,
    "俊": 0.7,
    "雅": 0.6,
    "清": 0.4,
    "明": 0.4,
    "香": 0.5,
    "甜": 0.8,
    "荣": 0.6,
    "贵": 0.5,
    "富贵": 1.0,
    "兴旺": 1.3,
    "热闹": 1.2,
    "团圆": 1.8,
    "平安": 1.5,
    "安稳": 1.2,
    "自在": 1.0,
    "有趣": 1.0,
    "得意": 1.0,
    "赏": 0.6,
    "福": 1.2,
    "寿": 0.8,
    "吉": 1.0,
    "善": 0.8,
    "贤": 0.7,
    "仁": 0.6,
    "义": 0.5,
    "情": 0.2,
}

NEGATIVE_WEIGHTS = {
    "大哭": -2.3,
    "痛哭": -2.5,
    "哭": -1.2,
    "泪": -1.1,
    "悲": -1.5,
    "哀": -1.4,
    "伤心": -2.0,
    "伤": -1.0,
    "愁": -1.5,
    "忧": -1.2,
    "恨": -1.4,
    "怒": -1.2,
    "恼": -1.0,
    "骂": -1.1,
    "打": -0.9,
    "杀": -2.3,
    "死": -2.1,
    "亡": -1.9,
    "丧": -1.8,
    "病": -1.3,
    "疼": -1.2,
    "痛": -1.3,
    "苦": -1.4,
    "可怜": -1.4,
    "凄": -1.5,
    "冷": -0.6,
    "怕": -1.0,
    "惧": -1.3,
    "惊": -0.9,
    "慌": -1.1,
    "烦": -0.9,
    "闷": -0.9,
    "叹": -0.8,
    "悔": -1.0,
    "惭": -0.9,
    "羞": -0.6,
    "罪": -1.4,
    "祸": -1.8,
    "灾": -1.8,
    "冤": -1.5,
    "辱": -1.4,
    "欺": -1.2,
    "毒": -1.8,
    "恶": -1.2,
    "败": -1.4,
    "失": -0.9,
    "离": -0.8,
    "别": -0.6,
    "孤": -1.0,
    "穷": -1.0,
    "衰": -1.4,
    "愧": -1.0,
    "无奈": -1.2,
    "不得": -0.4,
}

PHRASE_OVERRIDES = {
    "冷笑": -1.1,
    "苦笑": -1.2,
    "赔笑": -0.1,
    "笑道": 0.25,
    "不觉": 0.0,
}

NEGATIONS = ("不", "无", "没", "未", "莫", "休", "非")
INTENSIFIERS = {
    "极": 1.35,
    "甚": 1.25,
    "很": 1.2,
    "最": 1.35,
    "大": 1.25,
    "万分": 1.5,
    "十分": 1.35,
    "越发": 1.2,
}
TEXT_CLEAN_RE = re.compile(r"\s+")


def term_happiness_scores() -> dict[str, float]:
    """Map local sentiment terms onto the 1-9 happiness scale."""
    scores: dict[str, float] = {}
    for term, weight in POSITIVE_WEIGHTS.items():
        scores[term] = min(9.0, max(1.0, 5.0 + weight * 1.2))
    for term, weight in NEGATIVE_WEIGHTS.items():
        scores[term] = min(9.0, max(1.0, 5.0 + weight * 1.2))
    for term, weight in PHRASE_OVERRIDES.items():
        scores[term] = min(9.0, max(1.0, 5.0 + weight * 1.2))
    return scores


def load_polarity_lexicon(
    positive_path: Path | None = None,
    negative_path: Path | None = None,
    positive_score: float = 7.0,
    negative_score: float = 3.0,
) -> dict[str, float]:
    """Load newline-delimited positive/negative lexicons as happiness scores."""
    scores: dict[str, float] = {}
    if positive_path is not None:
        for line in positive_path.read_text(encoding="utf-8").splitlines():
            term = line.strip()
            if term:
                scores[term] = positive_score
    if negative_path is not None:
        for line in negative_path.read_text(encoding="utf-8").splitlines():
            term = line.strip()
            if term:
                scores[term] = negative_score
    return scores


def resolve_lexicon(
    name: str = "builtin",
    positive_path: Path | None = None,
    negative_path: Path | None = None,
) -> tuple[str, dict[str, float]]:
    """Resolve a named or explicit lexicon into term happiness scores."""
    if positive_path is not None or negative_path is not None:
        lexicon = load_polarity_lexicon(positive_path, negative_path)
        return "custom_polarity", lexicon
    if name == "builtin":
        return "builtin_weighted_terms", term_happiness_scores()
    if name == "ntusd":
        root = Path("resources/lexicons/ntusd")
        lexicon = load_polarity_lexicon(root / "positive_utf8.txt", root / "negative_utf8.txt")
        return "ntusd_polarity", lexicon
    raise ValueError(f"Unknown lexicon: {name}")


def _weighted_occurrences(text: str, lexicon: dict[str, float]) -> float:
    total = 0.0
    for word, weight in lexicon.items():
        start = 0
        while True:
            pos = text.find(word, start)
            if pos < 0:
                break
            local_weight = weight
            prefix = text[max(0, pos - 4) : pos]
            if any(prefix.endswith(negation) for negation in NEGATIONS):
                local_weight *= -0.7
            for intensifier, factor in INTENSIFIERS.items():
                if prefix.endswith(intensifier):
                    local_weight *= factor
                    break
            total += local_weight
            start = pos + max(len(word), 1)
    return total


def score_happiness(text: str) -> float:
    """Return a Hedonometer-like happiness score in the 1-9 range."""
    compact = TEXT_CLEAN_RE.sub("", text)
    if not compact:
        return 5.0

    raw = 0.0
    raw += _weighted_occurrences(compact, POSITIVE_WEIGHTS)
    raw += _weighted_occurrences(compact, NEGATIVE_WEIGHTS)
    raw += _weighted_occurrences(compact, PHRASE_OVERRIDES)

    exclamations = compact.count("！") + compact.count("!")
    if exclamations:
        raw *= 1.0 + min(exclamations, 3) * 0.08

    normalizer = math.sqrt(max(len(compact), 12) / 18)
    score = 5.0 + 3.2 * math.tanh(raw / (2.8 * normalizer))
    return round(min(9.0, max(1.0, score)), 2)


def hedonometer_average(text: str, lexicon: dict[str, float] | None = None) -> tuple[float, int]:
    """Frequency-weighted average happiness following the paper's equation C1."""
    compact = TEXT_CLEAN_RE.sub("", text)
    if not compact:
        return 5.0, 0
    lexicon = lexicon or term_happiness_scores()
    weighted_sum = 0.0
    count = 0
    for term, happiness in lexicon.items():
        occurrences = compact.count(term)
        if occurrences:
            weighted_sum += happiness * occurrences
            count += occurrences
    if not count:
        return 5.0, 0
    return round(weighted_sum / count, 4), count


def book_tokens(book_json: Path) -> list[str]:
    """Tokenize a LongStoryEval book JSON for sliding-window emotion arcs."""
    segments = [text for _, _, text in segments_from_book_json(book_json)]
    text = "\n".join(segments)
    try:
        import jieba

        tokens = [token.strip() for token in jieba.lcut(text) if token.strip()]
    except ImportError:
        tokens = [char for char in TEXT_CLEAN_RE.sub("", text) if char.strip()]
    return tokens


def sliding_window_arc(
    book_json: Path,
    points: int = 100,
    window_size: int = 10000,
    lexicon_name: str = "builtin",
    positive_path: Path | None = None,
    negative_path: Path | None = None,
) -> dict:
    """Generate a paper-style fixed-length sliding-window happiness arc."""
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

    resolved_name, lexicon = resolve_lexicon(lexicon_name, positive_path, negative_path)
    values = []
    for index, start in enumerate(starts):
        end = min(len(tokens), start + window_size)
        text = "".join(tokens[start:end])
        happiness_score, matched_terms = hedonometer_average(text, lexicon)
        values.append(
            {
                "index": index,
                "start_token": start,
                "end_token": end,
                "percent": round(index / (points - 1) * 100, 4) if points > 1 else 0.0,
                "happiness_score": happiness_score,
                "matched_terms": matched_terms,
                "matched_terms_per_1000_tokens": round(matched_terms / max(end - start, 1) * 1000, 4),
            }
        )

    mean_happiness = sum(point["happiness_score"] for point in values) / len(values)
    for point in values:
        point["centered_happiness"] = round(point["happiness_score"] - mean_happiness, 4)

    return {
        "book_json": str(book_json),
        "method": "Reagan et al. 2016 inspired sliding-window emotional arc",
        "lexicon": resolved_name,
        "lexicon_terms": len(lexicon),
        "tokenizer": "jieba" if len(tokens) > len(TEXT_CLEAN_RE.sub('', ''.join(tokens))) / 2 else "char",
        "tokens": len(tokens),
        "points": len(values),
        "window_size": window_size,
        "mean_happiness": round(mean_happiness, 4),
        "mean_matched_terms": round(
            sum(point["matched_terms"] for point in values) / len(values),
            4,
        ),
        "arc": values,
    }


def write_sliding_window_arc(
    book_json: Path,
    output: Path,
    points: int = 100,
    window_size: int = 10000,
    lexicon_name: str = "builtin",
    positive_path: Path | None = None,
    negative_path: Path | None = None,
) -> dict:
    payload = sliding_window_arc(
        book_json,
        points=points,
        window_size=window_size,
        lexicon_name=lexicon_name,
        positive_path=positive_path,
        negative_path=negative_path,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def snownlp_window_arc(
    book_json: Path,
    points: int = 100,
    window_size: int = 10000,
) -> dict:
    """Generate a sliding-window arc using SnowNLP sentence sentiment."""
    from snownlp import SnowNLP

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

    values = []
    for index, start in enumerate(starts):
        end = min(len(tokens), start + window_size)
        text = "".join(tokens[start:end])
        chunks = [
            text[offset : offset + 1000]
            for offset in range(0, len(text), 1000)
            if text[offset : offset + 1000].strip()
        ]
        if not chunks:
            chunks = [text]
        probs = [SnowNLP(chunk).sentiments for chunk in chunks]
        sentiment_prob = sum(probs) / len(probs)
        values.append(
            {
                "index": index,
                "start_token": start,
                "end_token": end,
                "percent": round(index / (points - 1) * 100, 4) if points > 1 else 0.0,
                "sentiment_probability": round(sentiment_prob, 4),
                "happiness_score": round(1.0 + 8.0 * sentiment_prob, 4),
                "chunks_scored": len(probs),
            }
        )

    mean_happiness = sum(point["happiness_score"] for point in values) / len(values)
    for point in values:
        point["centered_happiness"] = round(point["happiness_score"] - mean_happiness, 4)

    return {
        "book_json": str(book_json),
        "method": "SnowNLP sliding-window sentiment arc",
        "model": "snownlp-0.12.3",
        "tokens": len(tokens),
        "points": len(values),
        "window_size": window_size,
        "mean_happiness": round(mean_happiness, 4),
        "arc": values,
    }


def write_snownlp_window_arc(
    book_json: Path,
    output: Path,
    points: int = 100,
    window_size: int = 10000,
) -> dict:
    payload = snownlp_window_arc(book_json, points=points, window_size=window_size)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def segments_from_book_json(book_json: Path) -> list[tuple[int, str, str]]:
    """Flatten a LongStoryEval book JSON into non-empty paragraph segments."""
    payload = json.loads(book_json.read_text(encoding="utf-8"))
    segments: list[tuple[int, str, str]] = []
    for chapter_offset, chapter in enumerate(payload.get("chaps", []), start=1):
        chapter_title = chapter.get("title") or f"第{chapter_offset}回"
        for paragraph in chapter.get("content", []):
            text = paragraph.strip()
            if text:
                segments.append((chapter_offset, chapter_title, text))
    return segments


def score_segments(segments: Iterable[str]) -> list[dict]:
    rows = []
    for index, text in enumerate(segments):
        rows.append(
            {
                "index": index,
                "text": text,
                "happiness_score": score_happiness(text),
            }
        )
    return rows


def write_happiness_json(book_json: Path, output: Path, summary_output: Path | None = None) -> dict:
    """Score a book JSON and write the required JSON array output."""
    segment_records = segments_from_book_json(book_json)
    rows = score_segments(text for _, _, text in segment_records)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    summary = {
        "book_json": str(book_json),
        "output": str(output),
        "segments": len(rows),
        "mean_happiness": round(
            sum(row["happiness_score"] for row in rows) / len(rows), 4
        )
        if rows
        else 0.0,
        "chapter_curve": [],
    }
    chapter_scores: dict[int, list[float]] = {}
    chapter_titles: dict[int, str] = {}
    for (chapter_index, chapter_title, _), row in zip(segment_records, rows, strict=True):
        chapter_scores.setdefault(chapter_index, []).append(row["happiness_score"])
        chapter_titles[chapter_index] = chapter_title
    for chapter_index in sorted(chapter_scores):
        scores = chapter_scores[chapter_index]
        summary["chapter_curve"].append(
            {
                "chapter_index": chapter_index,
                "chapter_title": chapter_titles[chapter_index],
                "segments": len(scores),
                "mean_happiness": round(sum(scores) / len(scores), 4),
            }
        )

    if summary_output is not None:
        summary_output.parent.mkdir(parents=True, exist_ok=True)
        summary_output.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    return summary
