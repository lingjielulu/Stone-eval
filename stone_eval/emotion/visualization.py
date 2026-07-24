"""Plot a smoothed NTUSD emotional arc with chapter-level annotations."""

from __future__ import annotations

import argparse
import bisect
import csv
import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-stone-eval")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/stone-eval-cache")

import matplotlib

matplotlib.use("Agg")

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

from stone_eval.emotion.hedonometer import TEXT_CLEAN_RE


COMMON_CJK_FONTS = [
    "WenQuanYi Zen Hei",
    "Noto Sans CJK SC",
    "Noto Sans CJK JP",
    "Source Han Sans SC",
    "SimHei",
    "Microsoft YaHei",
]


def configure_font() -> None:
    available = {font.name for font in fm.fontManager.ttflist}
    for name in COMMON_CJK_FONTS:
        if name in available:
            plt.rcParams["font.sans-serif"] = [name, "DejaVu Sans"]
            break
    plt.rcParams["axes.unicode_minus"] = False


def tokenize(text: str) -> list[str]:
    try:
        import jieba

        return [token.strip() for token in jieba.lcut(text) if token.strip()]
    except ImportError:
        return [char for char in TEXT_CLEAN_RE.sub("", text) if char.strip()]


def chapter_token_offsets(book_json: Path) -> tuple[list[int], list[str]]:
    payload = json.loads(book_json.read_text(encoding="utf-8"))
    ends: list[int] = []
    titles: list[str] = []
    total = 0
    for chapter_index, chapter in enumerate(payload.get("chaps", []), start=1):
        title = chapter.get("title") or f"第{chapter_index}回"
        text = "\n".join(chapter.get("content", []))
        total += len(tokenize(text))
        ends.append(total)
        titles.append(title)
    return ends, titles


def moving_average(values: list[float], width: int) -> list[float]:
    width = max(1, width)
    radius = width // 2
    smoothed: list[float] = []
    for index in range(len(values)):
        start = max(0, index - radius)
        end = min(len(values), index + radius + 1)
        smoothed.append(sum(values[start:end]) / (end - start))
    return smoothed


def point_chapter_label(point: dict, chapter_ends: list[int], chapter_titles: list[str]) -> tuple[int, str]:
    center = (point["start_token"] + point["end_token"]) / 2
    chapter_index = min(bisect.bisect_left(chapter_ends, center) + 1, len(chapter_titles))
    return chapter_index, chapter_titles[chapter_index - 1]


def local_extrema(values: list[float], kind: str, radius: int = 5) -> list[int]:
    extrema: list[int] = []
    for index in range(radius, len(values) - radius):
        window = values[index - radius : index + radius + 1]
        current = values[index]
        if kind == "peak" and current == max(window) and current > values[index - 1] and current >= values[index + 1]:
            extrema.append(index)
        if kind == "valley" and current == min(window) and current < values[index - 1] and current <= values[index + 1]:
            extrema.append(index)
    return extrema


def select_extrema(
    candidates: list[int],
    values: list[float],
    *,
    kind: str,
    count: int = 4,
    min_gap: int = 18,
) -> list[int]:
    reverse = kind == "peak"
    ordered = sorted(candidates, key=lambda index: values[index], reverse=reverse)
    selected: list[int] = []
    for index in ordered:
        if all(abs(index - existing) >= min_gap for existing in selected):
            selected.append(index)
        if len(selected) == count:
            break
    return sorted(selected)


def write_extrema_files(rows: list[dict], output_json: Path, output_csv: Path) -> None:
    output_json.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    with output_csv.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = (
            list(rows[0].keys())
            if rows
            else [
                "label",
                "kind",
                "point_index",
                "percent",
                "chapter_index",
                "chapter_title",
                "raw_happiness_score",
                "smoothed_happiness_score",
                "start_token",
                "end_token",
                "matched_terms",
            ]
        )
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def score_axis_metadata(arc_payload: dict) -> tuple[str, str, str, str]:
    """Return method-specific title, axis label, scale note, and pipeline text."""
    scheme = arc_payload.get("scheme", "lexicon_score")
    if scheme == "model_score":
        scorer_name = arc_payload.get("model") or arc_payload.get("scorer_type", "model")
        title_method = f"DeepSeek/LLM叙事情绪正向性评分：{scorer_name}"
        ylabel = "模型情绪正向性评分（1=极负向，5=中性/混合，9=极正向）"
        scale_note = (
            "DeepSeek分数含义：模型综合叙事情境、人物情绪、事件走向和气氛给出1-9分；"
            "1=悲痛/恐惧/压抑等极负向，5=中性或正负混合，9=欢乐/温情/圆满等极正向。"
        )
        pipeline_method = (
            f"{arc_payload.get('scorer_type', 'model')}模型按prompt逐窗口输出1-9分"
        )
    else:
        scorer_name = arc_payload.get("lexicon", "NTUSD")
        title_method = f"{scorer_name} Hedonometer式幸福度"
        ylabel = "词典幸福度 / 情绪正向性（1=低幸福/负向，9=高幸福/正向）"
        scale_note = (
            "词典分数含义：Hedonometer式happiness score，不是单独的sadness强度；"
            "高分表示命中词更偏快乐/正向，低分表示更偏悲伤/压抑/负向，5约为中性。"
        )
        pipeline_method = "NTUSD正负词典按论文公式做频率加权平均"
    return title_method, ylabel, scale_note, pipeline_method


def plot_arc(
    arc_payload: dict,
    book_json: Path,
    output_png: Path,
    output_json: Path,
    output_csv: Path,
    smooth_width: int,
) -> None:
    configure_font()
    arc = arc_payload["arc"]
    title_method, ylabel, scale_note, pipeline_method = score_axis_metadata(arc_payload)
    raw = [float(point["happiness_score"]) for point in arc]
    smooth = moving_average(raw, smooth_width)
    mean_raw = sum(raw) / len(raw)
    chapter_ends, chapter_titles = chapter_token_offsets(book_json)

    peak_indices = select_extrema(local_extrema(smooth, "peak"), smooth, kind="peak")
    valley_indices = select_extrema(local_extrema(smooth, "valley"), smooth, kind="valley")

    extrema_rows: list[dict] = []
    for label_prefix, indices in [("P", peak_indices), ("V", valley_indices)]:
        kind = "peak" if label_prefix == "P" else "valley"
        for order, index in enumerate(indices, start=1):
            chapter_index, title = point_chapter_label(arc[index], chapter_ends, chapter_titles)
            extrema_rows.append(
                {
                    "label": f"{label_prefix}{order}",
                    "kind": kind,
                    "point_index": index,
                    "percent": arc[index]["percent"],
                    "chapter_index": chapter_index,
                    "chapter_title": title,
                    "raw_happiness_score": round(raw[index], 4),
                    "smoothed_happiness_score": round(smooth[index], 4),
                    "start_token": arc[index]["start_token"],
                    "end_token": arc[index]["end_token"],
                    "matched_terms": arc[index].get("matched_terms", ""),
                }
            )
    extrema_rows.sort(key=lambda row: row["point_index"])
    write_extrema_files(extrema_rows, output_json, output_csv)

    x = [point["percent"] for point in arc]
    fig = plt.figure(figsize=(16, 9.8), dpi=180)
    grid = fig.add_gridspec(3, 4, height_ratios=[4.5, 0.1, 1.45], width_ratios=[1, 1, 1, 1.08])
    ax = fig.add_subplot(grid[0, :3])
    table_ax = fig.add_subplot(grid[0, 3])
    note_ax = fig.add_subplot(grid[2, :])

    ax.plot(x, raw, color="#9ca3af", linewidth=0.8, alpha=0.45, label="原始窗口得分")
    ax.plot(x, smooth, color="#2563eb", linewidth=2.4, label=f"{smooth_width}点滚动平均")
    ax.axhline(mean_raw, color="#b91c1c", linestyle="--", linewidth=1.1, alpha=0.75, label=f"原始均值 {mean_raw:.3f}")

    for chapter in range(10, 81, 10):
        ax.axvline((chapter - 0.5) / 80 * 100, color="#e5e7eb", linewidth=0.7, zorder=0)
        ax.text((chapter - 0.5) / 80 * 100, min(smooth) - 0.08, f"{chapter}", ha="center", va="top", fontsize=8, color="#6b7280")

    marker_styles = {"peak": ("#16a34a", "^"), "valley": ("#dc2626", "v")}
    for row in extrema_rows:
        color, marker = marker_styles[row["kind"]]
        index = row["point_index"]
        ax.scatter(x[index], smooth[index], s=52, color=color, marker=marker, zorder=5)
        offset = 0.11 if row["kind"] == "peak" else -0.13
        va = "bottom" if row["kind"] == "peak" else "top"
        ax.text(
            x[index],
            smooth[index] + offset,
            f"{row['label']} 第{row['chapter_index']}回",
            ha="center",
            va=va,
            fontsize=8.5,
            color=color,
            fontweight="bold",
        )

    y_pad = 0.22
    y_min = max(1.0, min(smooth + raw) - y_pad)
    y_max = min(9.0, max(smooth + raw) + y_pad)
    ax.set_ylim(y_min, y_max)
    ax.set_xlim(0, 100)
    ax.set_title(f"《红楼梦》前80回情感弧线：{title_method}", fontsize=15, fontweight="bold", pad=14)
    ax.set_xlabel("文本进度（0-100%，底部数字为约略章回位置）")
    ax.set_ylabel(ylabel)
    ax.text(
        99,
        y_max - 0.02 * (y_max - y_min),
        "高分：快乐 / 温情 / 正向",
        ha="right",
        va="top",
        fontsize=8.8,
        color="#166534",
        bbox={"boxstyle": "round,pad=0.25", "facecolor": "#f0fdf4", "edgecolor": "#bbf7d0"},
    )
    ax.text(
        99,
        y_min + 0.02 * (y_max - y_min),
        "低分：悲伤 / 压抑 / 负向",
        ha="right",
        va="bottom",
        fontsize=8.8,
        color="#991b1b",
        bbox={"boxstyle": "round,pad=0.25", "facecolor": "#fef2f2", "edgecolor": "#fecaca"},
    )
    ax.grid(axis="y", color="#e5e7eb", linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(loc="upper left", frameon=False)

    table_ax.axis("off")
    table_ax.set_title("平滑后主要峰谷", fontsize=12, fontweight="bold", loc="left")
    table_lines = []
    for row in extrema_rows:
        short_title = row["chapter_title"]
        if len(short_title) > 24:
            short_title = short_title[:24] + "..."
        score = row["smoothed_happiness_score"]
        table_lines.append(f"{row['label']}  第{row['chapter_index']}回  {score:.3f}\n{short_title}")
    table_ax.text(0, 0.98, "\n\n".join(table_lines), ha="left", va="top", fontsize=8.8, linespacing=1.35)

    note_ax.axis("off")
    note_text = (
        "处理流程：红楼梦.txt前80回 -> 清理为LongStoryEval book_json -> jieba分词 -> "
        f"{pipeline_method} -> {arc_payload.get('window_size')} token滑动窗口、"
        f"{arc_payload.get('points')}个采样点 -> "
        f"{smooth_width}点滚动平均用于主图和峰谷标注。\n"
        f"{scale_note} 图中纵轴显示该1-9量表的局部放大区间，以便观察趋势。\n"
        "读图说明：浅灰线是未平滑窗口得分，蓝线是更稳定的整体情感弧线；峰谷表示相邻数回范围内的局部高/低点，"
        "不等同于单个情节的人工情绪判断。论文中的SVD用于多本书曲线矩阵的形状分解/聚类；这里只展示单部原作的平滑时间序列。"
    )
    note_ax.text(
        0.01,
        0.94,
        note_text,
        ha="left",
        va="top",
        fontsize=9.5,
        bbox={"boxstyle": "round,pad=0.45", "facecolor": "#f8fafc", "edgecolor": "#d1d5db"},
        wrap=True,
    )

    output_png.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_png, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--arc-json",
        default=(
            "stone_eval/emotion/results/hongloumeng_baselines_202606/"
            "original_80_emotion_arc_ntusd_recommended.json"
        ),
    )
    parser.add_argument(
        "--book-json",
        default=(
            "resources/corpora/hongloumeng/prepared/longstoryeval/"
            "original/books_json/红楼梦前80回.json"
        ),
    )
    parser.add_argument(
        "--output-png",
        default=(
            "stone_eval/emotion/results/current/"
            "original_80_ntusd_emotion_arc_smoothed.png"
        ),
    )
    parser.add_argument(
        "--output-json",
        default=(
            "stone_eval/emotion/results/current/"
            "original_80_ntusd_smoothed_peaks_valleys.json"
        ),
    )
    parser.add_argument(
        "--output-csv",
        default=(
            "stone_eval/emotion/results/current/"
            "original_80_ntusd_smoothed_peaks_valleys.csv"
        ),
    )
    parser.add_argument("--smooth-width", type=int, default=7)
    args = parser.parse_args()

    arc_payload = json.loads(Path(args.arc_json).read_text(encoding="utf-8"))
    plot_arc(
        arc_payload=arc_payload,
        book_json=Path(args.book_json),
        output_png=Path(args.output_png),
        output_json=Path(args.output_json),
        output_csv=Path(args.output_csv),
        smooth_width=args.smooth_width,
    )
    print(f"written {args.output_png}")
    print(f"written {args.output_json}")
    print(f"written {args.output_csv}")


if __name__ == "__main__":
    main()
