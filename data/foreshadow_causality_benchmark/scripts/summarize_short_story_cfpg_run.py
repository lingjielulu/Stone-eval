"""Summarize a short-story CFPG experiment run."""

from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter
from pathlib import Path
from typing import Any


CORE_STORIES = [
    "speckled_band",
    "red_headed_league",
    "necklace",
    "gift_of_the_magi",
    "last_leaf",
    "tell_tale_heart",
    "cask_of_amontillado",
    "to_build_a_fire",
    "medicine",
    "cricket",
]

DISPLAY_TITLES = {
    "speckled_band": "The Adventure of the Speckled Band / 斑点带子案",
    "red_headed_league": "The Red-Headed League / 红发会",
    "necklace": "The Diamond Necklace / 项链",
    "gift_of_the_magi": "The Gift of the Magi / 麦琪的礼物",
    "last_leaf": "The Last Leaf / 最后一片叶子",
    "tell_tale_heart": "The Tell-Tale Heart / 泄密的心",
    "cask_of_amontillado": "The Cask of Amontillado / 一桶白葡萄酒",
    "to_build_a_fire": "To Build a Fire / 生火",
    "medicine": "藥",
    "cricket": "促織",
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def pct(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return "0.00%"
    return f"{numerator / denominator * 100:.2f}%"


def distance_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    values = [
        row["candidate"].get("distance_paragraphs")
        for row in rows
        if isinstance(row.get("candidate", {}).get("distance_paragraphs"), int)
    ]
    if not values:
        return {"count": 0}
    return {
        "count": len(values),
        "min": min(values),
        "max": max(values),
        "mean": round(statistics.mean(values), 2),
        "median": statistics.median(values),
    }


def md_link(label: str, path: Path, run_dir: Path) -> str:
    return f"[{label}]({path.relative_to(run_dir)})"


def build_report(
    run_dir: Path,
    run_id: str,
    story_rows: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
    accepted: list[dict[str, Any]],
    rejected: list[dict[str, Any]],
    summary: dict[str, Any],
) -> str:
    candidates_by_type = Counter(row.get("foreshadow_type", "unknown") for row in candidates)
    accepted_by_type = Counter(row["candidate"].get("foreshadow_type", "unknown") for row in accepted)
    accepted_by_payoff = Counter(row["candidate"].get("payoff_type", "unknown") for row in accepted)

    lines: list[str] = [
        "# 短篇小说 CFPG 伏笔实验报告",
        "",
        "## 概览",
        "",
        (
            "本报告记录 `foreshadow_causality_benchmark` 核心 10 篇短篇小说的 "
            "Foreshadow-Trigger-Payoff 候选抽取与 verifier 实验。"
            "本轮不经过摘要层，直接使用 `normalized_texts` 的段落时间线；"
            "英文作品同步插入 `normalized_texts_zh` 的中文辅助译文，已有 seed YAML 的作品插入人工标注上下文作为参考。"
        ),
        "",
        "当前结论：",
        "",
        f"- 有效 run：`{run_id}`。",
        f"- 结果集中保存于：`{run_dir}`。",
        "- Prompt 集中维护于：`prompts/cfpg/short_story_prompts.md`。",
        "- 抽取脚本：`data/foreshadow_causality_benchmark/scripts/extract_short_story_ftp.py`。",
        f"- 覆盖核心作品：{summary['story_count']} 篇。",
        f"- Candidate extraction 产出：{summary['candidate_count']} 条候选。",
        f"- Verifier 接受：{summary['accepted_count']} 条 verified F-T-P。",
        f"- Verifier 拒绝：{summary['rejected_count']} 条。",
        f"- Verifier 接受率：{pct(summary['accepted_count'], summary['verified_count'])}。",
        "",
        "## 方法",
        "",
        "本轮实验沿用 CFPG 的三元组定义，但针对短篇做两点调整：",
        "",
        "- 不做 BookSum-style 摘要，直接在全文段落 ID 上定位 evidence。",
        "- 每篇最多抽取 3 个高召回候选，再逐条运行 verifier；这是为了避免长 prompt 下 JSON 输出被截断，同时贴近红楼梦报告中“每窗最多 3 个候选”的口径。",
        "",
        "运行配置：",
        "",
        "| 参数 | 值 |",
        "| --- | --- |",
        f"| run_id | `{run_id}` |",
        "| model | `deepseek-v4-pro` |",
        "| max_candidates | 3 / story |",
        "| max_output_tokens | 8192 |",
        "| input text | full paragraph timeline |",
        "| bilingual aid | English stories include Chinese translation when available |",
        "| verification | enabled |",
        "",
        "## 输出目录",
        "",
        "| 输出 | 路径 |",
        "| --- | --- |",
        f"| prompt previews | `{run_dir / 'reviews'}` |",
        f"| raw extraction JSON | `{run_dir / 'candidates'}` |",
        f"| normalized candidates | `{run_dir / 'candidates'}` |",
        f"| verifier JSONL | `{run_dir / 'verified'}` |",
        f"| accepted aggregate | `{run_dir / f'accepted_triples_{run_id}.jsonl'}` |",
        f"| rejected aggregate | `{run_dir / f'rejected_candidates_{run_id}.jsonl'}` |",
        f"| summary JSON | `{run_dir / 'summary.json'}` |",
        "",
        "## 过滤结果统计",
        "",
        "| 阶段 | 输入 | 输出/保留 | 保留率 | 备注 |",
        "| --- | ---: | ---: | ---: | --- |",
        f"| 核心作品 | {summary['story_count']} 篇 | {summary['story_count']} 篇 | 100.00% | 核心 10 篇，不含 `rashomon` 扩展样本 |",
        f"| Candidate extraction | {summary['story_count']} 篇全文 | {summary['candidate_count']} 条候选 | - | 每篇最多 3 条 |",
        f"| F-T-P verification | {summary['candidate_count']} 条候选 | {summary['accepted_count']} 条 accepted | {pct(summary['accepted_count'], summary['candidate_count'])} | {summary['rejected_count']} 条 rejected |",
        "",
        "## 分作品结果",
        "",
        "| story_id | 作品 | candidates | accepted | rejected | review |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]

    for row in story_rows:
        review_path = run_dir / "reviews" / f"{row['story_id']}_ftp_review_{run_id}.md"
        lines.append(
            "| "
            f"`{row['story_id']}` | {DISPLAY_TITLES.get(row['story_id'], row['story_id'])} | "
            f"{row['candidate_count']} | {row['accepted_count']} | {row['rejected_count']} | "
            f"{md_link('review', review_path, run_dir)} |"
        )

    lines.extend(
        [
            "",
            "## 类型分布",
            "",
            "| foreshadow_type | candidates | accepted |",
            "| --- | ---: | ---: |",
        ]
    )
    for key in sorted(set(candidates_by_type) | set(accepted_by_type)):
        lines.append(f"| `{key}` | {candidates_by_type[key]} | {accepted_by_type[key]} |")

    lines.extend(
        [
            "",
            "| payoff_type | accepted |",
            "| --- | ---: |",
        ]
    )
    for key, count in sorted(accepted_by_payoff.items()):
        lines.append(f"| `{key}` | {count} |")

    stats = summary["accepted_distance_paragraphs"]
    lines.extend(
        [
            "",
            "## Payoff 距离",
            "",
            "| 指标 | 段落数 |",
            "| --- | ---: |",
            f"| count | {stats.get('count', 0)} |",
            f"| min | {stats.get('min', '-')} |",
            f"| median | {stats.get('median', '-')} |",
            f"| mean | {stats.get('mean', '-')} |",
            f"| max | {stats.get('max', '-')} |",
            "",
            "## Accepted 样例",
            "",
        ]
    )

    for item in accepted[:5]:
        candidate = item["candidate"]
        verdict = item.get("verdict", {})
        lines.extend(
            [
                f"### {candidate['candidate_id']}",
                "",
                f"- F: `{candidate['foreshadow_span']}` {candidate.get('foreshadow_summary', '')}",
                f"- T: {candidate.get('proposed_trigger', {}).get('description', '')}",
                f"- P: `{candidate['payoff_span']}` {candidate.get('payoff_summary', '')}",
                f"- verifier rationale: {verdict.get('rationale', '')}",
                "",
            ]
        )

    lines.extend(["## Rejected 样例", ""])
    for item in rejected[:5]:
        candidate = item["candidate"]
        verdict = item.get("verdict", {})
        lines.extend(
            [
                f"### {candidate['candidate_id']}",
                "",
                f"- F: `{candidate['foreshadow_span']}` {candidate.get('foreshadow_summary', '')}",
                f"- P: `{candidate['payoff_span']}` {candidate.get('payoff_summary', '')}",
                f"- rejection: {verdict.get('rejection_reason') or verdict.get('rationale', '')}",
                "",
            ]
        )

    lines.extend(
        [
            "## 运行问题记录",
            "",
            "本轮正式统计采用 `v3_verified`。此前两个诊断 run 不计入统计：",
            "",
            "- `20260701_short_story_cfpg_v1`: `max_candidates=8`, `max_output_tokens=2048`，模型返回 `{}`，normalized candidates 为 0。",
            "- `20260701_short_story_cfpg_v2`: 增加 schema 校验后确认 `{}` 为无效输出；提高 token 后出现截断 JSON。",
            "- `20260701_short_story_cfpg_v3_verified`: 将每篇候选数降为 3，并使用 `max_output_tokens=8192`，完整跑通 extraction + verification。",
            "",
            "## 后续处理",
            "",
            "- 25 条 accepted 仍是 LLM verifier 结果，不等同 gold；进入 `annotations/*.yaml` 前需要人工复核。",
            "- 5 条 rejected 可用于调 prompt 边界，尤其是主题呼应、普通因果和 span 粒度问题。",
            "- 下一步可以把 accepted 聚合结果映射到现有 schema 的 `foreshadowing_units` 草稿层，再人工审查 trigger/payoff event 绑定。",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--stories", nargs="*", default=CORE_STORIES)
    args = parser.parse_args()

    run_dir = args.run_dir
    all_candidates: list[dict[str, Any]] = []
    all_verified: list[dict[str, Any]] = []
    story_rows: list[dict[str, Any]] = []

    for story_id in args.stories:
        candidates_path = run_dir / "candidates" / f"{story_id}_ftp_candidates_{args.run_id}.jsonl"
        verified_path = run_dir / "verified" / f"{story_id}_ftp_verified_{args.run_id}.jsonl"
        candidates = read_jsonl(candidates_path)
        verified = read_jsonl(verified_path)
        accepted = [row for row in verified if row.get("verdict", {}).get("accepted") is True]
        rejected = [row for row in verified if row.get("verdict", {}).get("accepted") is False]
        story_rows.append(
            {
                "story_id": story_id,
                "candidate_count": len(candidates),
                "verified_count": len(verified),
                "accepted_count": len(accepted),
                "rejected_count": len(rejected),
            }
        )
        all_candidates.extend(candidates)
        all_verified.extend(verified)

    accepted_all = [row for row in all_verified if row.get("verdict", {}).get("accepted") is True]
    rejected_all = [row for row in all_verified if row.get("verdict", {}).get("accepted") is False]
    summary = {
        "run_id": args.run_id,
        "story_count": len(args.stories),
        "candidate_count": len(all_candidates),
        "verified_count": len(all_verified),
        "accepted_count": len(accepted_all),
        "rejected_count": len(rejected_all),
        "acceptance_rate": pct(len(accepted_all), len(all_verified)),
        "stories": story_rows,
        "candidate_foreshadow_type_counts": Counter(
            row.get("foreshadow_type", "unknown") for row in all_candidates
        ),
        "accepted_foreshadow_type_counts": Counter(
            row["candidate"].get("foreshadow_type", "unknown") for row in accepted_all
        ),
        "accepted_payoff_type_counts": Counter(
            row["candidate"].get("payoff_type", "unknown") for row in accepted_all
        ),
        "accepted_distance_paragraphs": distance_stats(accepted_all),
    }

    write_jsonl(run_dir / f"accepted_triples_{args.run_id}.jsonl", accepted_all)
    write_jsonl(run_dir / f"rejected_candidates_{args.run_id}.jsonl", rejected_all)
    (run_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    report = build_report(
        run_dir,
        args.run_id,
        story_rows,
        all_candidates,
        accepted_all,
        rejected_all,
        summary,
    )
    report_path = run_dir / "short_story_cfpg_report.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"wrote {run_dir / 'summary.json'}")
    print(f"wrote {run_dir / f'accepted_triples_{args.run_id}.jsonl'}")
    print(f"wrote {run_dir / f'rejected_candidates_{args.run_id}.jsonl'}")
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
