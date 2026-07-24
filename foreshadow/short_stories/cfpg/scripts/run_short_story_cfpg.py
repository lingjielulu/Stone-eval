"""Run the paper's oracle-timing and grounded-tracking experiments on short stories."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

from openai import OpenAI

from cfpg_short_story import (
    read_jsonl,
    select_refresh_context,
    split_sentences,
    summarize_oracle,
    summarize_tracking,
)


REPO_ROOT = Path(__file__).resolve().parents[4]
SCRIPTS_DIR = REPO_ROOT / "foreshadow" / "common"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from cfpg_prompt_utils import load_prompt_templates, render_messages  # noqa: E402


EXPERIMENT_ROOT = Path(
    "foreshadow/short_stories/cfpg"
)
PROMPT_FILE = EXPERIMENT_ROOT / "prompts/short_story_prompts.md"
ORACLE_METHODS = ("prompt", "cfpg")
TRACKING_METHODS = ("fap", "fscr", "cfpg")


def load_dotenv(path: Path = Path(".env")) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("\"'").strip())


def parse_json_object(content: str) -> dict[str, Any]:
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?", "", content).strip()
        content = re.sub(r"```$", "", content).strip()
    try:
        value = json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", content, re.S)
        if not match:
            raise
        value = json.loads(match.group(0))
    if not isinstance(value, dict):
        raise ValueError("expected a JSON object")
    return value


def call_text(
    client: OpenAI,
    model: str,
    messages: list[dict[str, str]],
    timeout: float,
    max_tokens: int,
    retries: int,
    json_mode: bool = False,
) -> str:
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            kwargs: dict[str, Any] = {
                "model": model,
                "messages": messages,
                "temperature": 0,
                "timeout": timeout,
                "max_tokens": max_tokens,
            }
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}
            try:
                response = client.chat.completions.create(**kwargs)
            except Exception:
                kwargs.pop("response_format", None)
                response = client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content or ""
            if not content.strip():
                raise ValueError(
                    "model returned empty content (the completion budget may have been consumed by reasoning)"
                )
            return content
        except Exception as exc:
            last_error = exc
            if attempt + 1 < retries:
                time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"LLM call failed after {retries} attempts: {last_error}") from last_error


def call_json(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return parse_json_object(call_text(*args, **kwargs, json_mode=True))


def format_context(rows: list[dict[str, Any]], max_chars: int) -> str:
    rendered = [f"[{row['segment_id']}] {row['text']}" for row in rows]
    selected: list[str] = []
    used = 0
    for line in reversed(rendered):
        if selected and used + len(line) + 2 > max_chars:
            break
        selected.append(line)
        used += len(line) + 2
    return "\n\n".join(reversed(selected))


def triple_payload(case: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": case["case_id"],
        "status": "unresolved",
        "foreshadow": case["foreshadow"]["description"],
        "trigger": case["trigger"],
        "payoff": case["payoff"]["description"],
    }


def decision_messages(
    templates: dict[str, Any],
    case: dict[str, Any],
    method: str,
    prefix: list[dict[str, Any]],
    max_context_chars: int,
    refresh_top_k: int,
    recent_k: int,
) -> list[dict[str, str]]:
    context_rows = prefix
    if method == "fscr":
        context_rows = select_refresh_context(
            prefix,
            case["foreshadow"]["text"] or case["foreshadow"]["description"],
            top_k=refresh_top_k,
            recent_k=recent_k,
        )
    common = {
        "story_id": case["story_id"],
        "story_title": case["story_title"],
        "current_context": format_context(context_rows, max_context_chars),
    }
    if method == "cfpg":
        return render_messages(
            templates["short_story_cfpg_decision"],
            {**common, "triple_json": json.dumps(triple_payload(case), ensure_ascii=False, indent=2)},
        )
    return render_messages(
        templates["short_story_fap_decision"],
        {**common, "foreshadow_description": case["foreshadow"]["description"]},
    )


def continuation_messages(
    templates: dict[str, Any],
    case: dict[str, Any],
    method: str,
    prefix: list[dict[str, Any]],
    max_context_chars: int,
    oracle: bool,
) -> list[dict[str, str]]:
    if method == "cfpg":
        guidance = (
            "CFPG gate 已激活。下一句必须自然实现以下结构化 payoff：\n"
            + json.dumps(triple_payload(case), ensure_ascii=False, indent=2)
        )
    elif oracle and method == "prompt":
        guidance = "没有额外控制条件；根据当前文本自然续写。"
    else:
        guidance = (
            "你已判断现在应回收这个未解决的伏笔，请自然续写："
            + case["foreshadow"]["description"]
        )
    return render_messages(
        templates["short_story_continuation"],
        {
            "story_id": case["story_id"],
            "story_title": case["story_title"],
            "current_context": format_context(prefix, max_context_chars),
            "guidance": guidance,
        },
    )


def judge_messages(
    templates: dict[str, Any],
    case: dict[str, Any],
    gold: str,
    generated: str,
) -> list[dict[str, str]]:
    return render_messages(
        templates["short_story_continuation_judge"],
        {
            "story_id": case["story_id"],
            "story_title": case["story_title"],
            "foreshadow_description": case["foreshadow"]["description"],
            "payoff_description": case["payoff"]["description"],
            "gold_continuation": gold,
            "generated_continuation": generated,
        },
    )


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def normalized_judgment(raw: dict[str, Any]) -> dict[str, Any]:
    score = raw.get("score", 0.5)
    try:
        score = float(score)
    except (TypeError, ValueError):
        score = 0.5
    score = min((0.0, 0.5, 1.0), key=lambda allowed: abs(allowed - score))
    return {
        **raw,
        "score": score,
        "payoff_realized": raw.get("payoff_realized") is True,
    }


def one_sentence(raw: str) -> str:
    sentences = split_sentences(raw)
    return sentences[0] if sentences else raw.strip()


def run_oracle(
    client: OpenAI,
    cases: list[dict[str, Any]],
    methods: list[str],
    templates: dict[str, Any],
    args: argparse.Namespace,
    output_path: Path,
) -> list[dict[str, Any]]:
    existing = read_jsonl(output_path) if output_path.exists() else []
    done = {(row["case_id"], row["model"], row["method"]) for row in existing}
    for case in cases:
        gold_index = case["payoff"]["anchor_index"]
        prefix = case["segments"][:gold_index]
        for method in methods:
            key = (case["case_id"], args.model, method)
            if key in done:
                continue
            activation: dict[str, Any] | None = None
            if method == "cfpg":
                activation = call_json(
                    client,
                    args.model,
                    decision_messages(
                        templates,
                        case,
                        "cfpg",
                        prefix,
                        args.max_context_chars,
                        args.refresh_top_k,
                        args.recent_k,
                    ),
                    args.timeout,
                    args.decision_tokens,
                    args.retries,
                )
            raw_generated = call_text(
                client,
                args.model,
                continuation_messages(
                    templates, case, method, prefix, args.max_context_chars, oracle=True
                ),
                args.timeout,
                args.generation_tokens,
                args.retries,
            ).strip()
            generated = one_sentence(raw_generated)
            judgment = normalized_judgment(
                call_json(
                    client,
                    args.judge_model,
                    judge_messages(templates, case, case["payoff"]["text"], generated),
                    args.timeout,
                    args.judge_tokens,
                    args.retries,
                )
            )
            row = {
                "experiment": "oracle",
                "case_id": case["case_id"],
                "story_id": case["story_id"],
                "model": args.model,
                "judge_model": args.judge_model,
                "method": method,
                "gold_index": gold_index,
                "gold_segment_id": case["payoff"]["anchor_segment_id"],
                "should_payoff": (
                    activation.get("should_payoff") is True if activation is not None else None
                ),
                "activation_decision": activation,
                "raw_generated_continuation": raw_generated,
                "generated_continuation": generated,
                "judgment": judgment,
            }
            append_jsonl(output_path, row)
            existing.append(row)
            print(f"oracle {case['case_id']} {method}: {judgment['score']}")
    return existing


def run_tracking(
    client: OpenAI,
    cases: list[dict[str, Any]],
    methods: list[str],
    templates: dict[str, Any],
    args: argparse.Namespace,
    output_path: Path,
) -> list[dict[str, Any]]:
    existing = read_jsonl(output_path) if output_path.exists() else []
    done = {(row["case_id"], row["model"], row["method"]) for row in existing}
    for case in cases:
        gold_index = case["payoff"]["anchor_index"]
        start = case["foreshadow"].get(
            "span_end_index", case["foreshadow"]["anchor_index"]
        ) + 1
        stop = min(len(case["segments"]), gold_index + args.post_payoff_steps + 1)
        positions = list(range(start, stop, args.stride))
        if gold_index not in positions and start <= gold_index < stop:
            positions.append(gold_index)
            positions.sort()
        for method in methods:
            key = (case["case_id"], args.model, method)
            if key in done:
                continue
            predicted_index: int | None = None
            predicted_decision: dict[str, Any] | None = None
            trace: list[dict[str, Any]] = []
            for position in positions:
                prefix = case["segments"][:position]
                decision = call_json(
                    client,
                    args.model,
                    decision_messages(
                        templates,
                        case,
                        method,
                        prefix,
                        args.max_context_chars,
                        args.refresh_top_k,
                        args.recent_k,
                    ),
                    args.timeout,
                    args.decision_tokens,
                    args.retries,
                )
                should_payoff = decision.get("should_payoff") is True
                trace.append(
                    {
                        "position": position,
                        "next_segment_id": case["segments"][position]["segment_id"],
                        "should_payoff": should_payoff,
                        "confidence": decision.get("confidence"),
                        "rationale": decision.get("rationale", ""),
                    }
                )
                if should_payoff:
                    predicted_index = position
                    predicted_decision = decision
                    break

            generated: str | None = None
            judgment: dict[str, Any] | None = None
            if predicted_index is not None:
                prefix = case["segments"][:predicted_index]
                raw_generated = call_text(
                    client,
                    args.model,
                    continuation_messages(
                        templates, case, method, prefix, args.max_context_chars, oracle=False
                    ),
                    args.timeout,
                    args.generation_tokens,
                    args.retries,
                ).strip()
                generated = one_sentence(raw_generated)
                gold_continuation = case["segments"][predicted_index]["text"]
                judgment = normalized_judgment(
                    call_json(
                        client,
                        args.judge_model,
                        judge_messages(templates, case, gold_continuation, generated),
                        args.timeout,
                        args.judge_tokens,
                        args.retries,
                    )
                )
            row = {
                "experiment": "tracking",
                "case_id": case["case_id"],
                "story_id": case["story_id"],
                "model": args.model,
                "judge_model": args.judge_model,
                "method": method,
                "gold_index": gold_index,
                "gold_segment_id": case["payoff"]["anchor_segment_id"],
                "predicted_index": predicted_index,
                "predicted_segment_id": (
                    case["segments"][predicted_index]["segment_id"]
                    if predicted_index is not None
                    else None
                ),
                "decision": predicted_decision,
                "decision_trace": trace,
                "generated_continuation": generated,
                "continuation_judgment": judgment,
            }
            append_jsonl(output_path, row)
            existing.append(row)
            offset = None if predicted_index is None else predicted_index - gold_index
            print(f"tracking {case['case_id']} {method}: offset={offset}")
    return existing


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cases",
        type=Path,
        default=EXPERIMENT_ROOT / "data/cfpg_cases.jsonl",
    )
    parser.add_argument("--output-dir", type=Path, default=EXPERIMENT_ROOT / "results/generation")
    parser.add_argument("--run-id", default=time.strftime("%Y%m%d_%H%M%S"))
    parser.add_argument("--experiment", choices=("oracle", "tracking", "all"), default="all")
    parser.add_argument("--method", action="append", default=[])
    parser.add_argument("--story-id", action="append", default=[])
    parser.add_argument("--max-cases", type=int, default=0)
    parser.add_argument("--model", default=None)
    parser.add_argument("--judge-model", default=None)
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--api-base", default=None)
    parser.add_argument("--prompt-file", type=Path, default=PROMPT_FILE)
    parser.add_argument("--max-context-chars", type=int, default=30000)
    parser.add_argument("--stride", type=int, default=1)
    parser.add_argument("--post-payoff-steps", type=int, default=3)
    parser.add_argument("--refresh-top-k", type=int, default=5)
    parser.add_argument("--recent-k", type=int, default=8)
    parser.add_argument("--decision-tokens", type=int, default=1024)
    parser.add_argument("--generation-tokens", type=int, default=2048)
    parser.add_argument("--judge-tokens", type=int, default=1024)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.stride < 1:
        parser.error("--stride must be at least 1")
    load_dotenv()
    args.model = args.model or os.environ.get("CFPG_GENERATION_MODEL") or os.environ.get("JUDGE_MODEL")
    args.judge_model = args.judge_model or os.environ.get("CFPG_JUDGE_MODEL") or os.environ.get("JUDGE_MODEL")
    if not args.model or not args.judge_model:
        parser.error("set --model/--judge-model or JUDGE_MODEL")

    cases = read_jsonl(args.cases)
    if args.story_id:
        cases = [case for case in cases if case["story_id"] in set(args.story_id)]
    if args.max_cases > 0:
        cases = cases[: args.max_cases]
    templates = load_prompt_templates(args.prompt_file)

    oracle_methods = list(args.method or ORACLE_METHODS)
    tracking_methods = list(args.method or TRACKING_METHODS)
    if args.experiment in {"oracle", "all"}:
        invalid = sorted(set(oracle_methods) - set(ORACLE_METHODS))
        if invalid:
            parser.error(f"invalid oracle methods: {', '.join(invalid)}")
    if args.experiment in {"tracking", "all"}:
        invalid = sorted(set(tracking_methods) - set(TRACKING_METHODS))
        if invalid:
            parser.error(f"invalid tracking methods: {', '.join(invalid)}")

    if args.dry_run:
        oracle_calls = 0
        if args.experiment in {"oracle", "all"}:
            oracle_calls = len(cases) * (
                len(oracle_methods) * 2 + int("cfpg" in oracle_methods)
            )
        tracking_decisions = 0
        if args.experiment in {"tracking", "all"}:
            for case in cases:
                steps = max(
                    0,
                    min(len(case["segments"]), case["payoff"]["anchor_index"] + args.post_payoff_steps + 1)
                    - case["foreshadow"].get(
                        "span_end_index", case["foreshadow"]["anchor_index"]
                    )
                    - 1,
                )
                tracking_decisions += (steps + args.stride - 1) // args.stride
            tracking_decisions *= len(tracking_methods)
        print(
            json.dumps(
                {
                    "cases": len(cases),
                    "oracle_methods": oracle_methods,
                    "tracking_methods": tracking_methods,
                    "estimated_oracle_calls": oracle_calls,
                    "maximum_tracking_decision_calls": tracking_decisions,
                    "note": "each triggered tracking case adds generation + judge calls",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        parser.error("set --api-key or OPENAI_API_KEY")
    client_kwargs: dict[str, Any] = {"api_key": api_key, "timeout": args.timeout}
    api_base = args.api_base or os.environ.get("OPENAI_BASE_URL")
    if api_base:
        client_kwargs["base_url"] = api_base.rstrip("/")
    client = OpenAI(**client_kwargs)

    run_dir = args.output_dir / args.run_id
    summary: dict[str, Any] = {"run_id": args.run_id, "model": args.model, "judge_model": args.judge_model}
    if args.experiment in {"oracle", "all"}:
        oracle_rows = run_oracle(
            client, cases, oracle_methods, templates, args, run_dir / "oracle.jsonl"
        )
        summary["oracle"] = summarize_oracle(oracle_rows)
    if args.experiment in {"tracking", "all"}:
        tracking_rows = run_tracking(
            client, cases, tracking_methods, templates, args, run_dir / "tracking.jsonl"
        )
        summary["tracking"] = summarize_tracking(tracking_rows)
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"wrote {run_dir / 'summary.json'}")


if __name__ == "__main__":
    main()
