"""Unified CLI for Stone-eval."""

import json
import os
from pathlib import Path
import re
import subprocess
import sys

import click

from stone_eval import __version__
from stone_eval.corpus import prepare_stone_corpora
from stone_eval.emotion import (
    LLMEmotionConfig,
    write_happiness_json,
    write_llm_window_arc,
    write_snownlp_model_arc,
    write_sliding_window_arc,
)
from stone_eval.longstory import (
    LongStoryConfig,
    env_config,
    evaluate_book_summaries,
    summarize_books,
)


@click.group()
@click.version_option(__version__)
def main():
    """Stone-eval: HongLou Meng continuation evaluation suite."""


def _load_dotenv(path: Path = Path(".env")) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


@main.command("prepare-corpus")
@click.option("--original", default="红楼梦.txt", show_default=True, help="Original text file")
@click.option(
    "--continuations",
    default="红楼梦续作文本",
    show_default=True,
    help="Directory containing continuation .txt files",
)
@click.option(
    "--output-dir",
    default="data/processed",
    show_default=True,
    help="Directory for prepared evaluation inputs",
)
@click.option(
    "--original-chapters",
    default=80,
    show_default=True,
    type=int,
    help="Number of original chapters to evaluate",
)
def prepare_corpus(original, continuations, output_dir, original_chapters):
    """Prepare separated original/continuation inputs for current evaluators."""
    result = prepare_stone_corpora(
        original_path=Path(original),
        continuation_dir=Path(continuations),
        output_dir=Path(output_dir),
        original_chapters=original_chapters,
    )
    click.echo("Prepared Stone evaluation corpora:")
    click.echo(f"  manifest: {result['manifest']}")
    click.echo(f"  original chapters: {result['original_chapters']}")
    click.echo(f"  continuation books: {result['continuation_books']}")
    click.echo(f"  continuation chapters: {result['continuation_chapters']}")
    click.echo("")
    click.echo("ConStory-Bench inputs:")
    click.echo(f"  original: {result['constory_original']}")
    click.echo(f"  continuations: {result['constory_continuations']}")
    click.echo("")
    click.echo("LongStoryEval inputs:")
    click.echo(f"  {Path(output_dir) / 'longstoryeval' / 'original' / 'books_json'}")
    click.echo(f"  {Path(output_dir) / 'longstoryeval' / 'continuations' / 'books_json'}")


@main.command("validate-corpus")
@click.option(
    "--processed-dir",
    default="data/processed",
    show_default=True,
    help="Prepared corpus directory",
)
@click.option("--output", default="outputs/corpus_validation.json", show_default=True)
def validate_corpus(processed_dir, output):
    """Validate prepared ConStory and LongStoryEval inputs."""
    import pandas as pd

    root = Path(processed_dir)
    manifest_path = root / "manifest.json"
    if not manifest_path.exists():
        raise click.ClickException(f"Missing manifest: {manifest_path}")

    report = {
        "manifest": str(manifest_path),
        "errors": [],
        "warnings": [],
        "constory": {},
        "longstoryeval": {},
    }

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for label, parquet in {
        "original": root / "constory" / "original_chapters.parquet",
        "continuations": root / "constory" / "continuation_chapters.parquet",
    }.items():
        if not parquet.exists():
            report["errors"].append(f"Missing ConStory parquet: {parquet}")
            continue
        df = pd.read_parquet(parquet)
        missing_cols = {"id", "book", "chapter_index", "story_text"} - set(df.columns)
        if missing_cols:
            report["errors"].append(f"{parquet} missing columns: {sorted(missing_cols)}")
        report["constory"][label] = {
            "path": str(parquet),
            "rows": len(df),
            "books": int(df["book"].nunique()) if "book" in df else 0,
        }
        if "story_text" in df and df["story_text"].str.strip().eq("").any():
            report["errors"].append(f"{parquet} contains empty story_text rows")

    expected_books = [manifest["original"]["name"]]
    expected_books.extend(item["name"] for item in manifest["continuations"])
    book_roots = [
        root / "longstoryeval" / "original" / "books_json",
        root / "longstoryeval" / "continuations" / "books_json",
    ]
    for book_root in book_roots:
        if not book_root.exists():
            report["errors"].append(f"Missing LongStoryEval directory: {book_root}")
            continue
        for book_path in sorted(book_root.glob("*.json")):
            payload = json.loads(book_path.read_text(encoding="utf-8"))
            chapters = payload.get("chaps", [])
            indices = []
            empty = 0
            for chapter in chapters:
                title = chapter.get("title", "")
                match = re.search(r"第(\d+)回", title)
                if match:
                    indices.append(int(match.group(1)))
                if not "\n".join(chapter.get("content", [])).strip():
                    empty += 1
            missing = []
            if indices:
                missing = sorted(set(range(min(indices), max(indices) + 1)) - set(indices))
            if missing:
                report["warnings"].append(f"{book_path.stem} missing chapter indices: {missing}")
            if empty:
                report["errors"].append(f"{book_path.stem} has {empty} empty chapters")
            report["longstoryeval"][book_path.stem] = {
                "path": str(book_path),
                "chapters": len(chapters),
                "missing_chapter_indices": missing,
                "empty_chapters": empty,
            }

    actual_books = set(report["longstoryeval"])
    for book in expected_books:
        if book not in actual_books:
            report["errors"].append(f"Missing LongStoryEval book JSON: {book}")

    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    click.echo(f"Corpus validation written to {output_path}")
    click.echo(f"  errors: {len(report['errors'])}")
    click.echo(f"  warnings: {len(report['warnings'])}")
    if report["warnings"]:
        for warning in report["warnings"][:5]:
            click.echo(f"  warning: {warning}")
    if report["errors"]:
        raise click.ClickException("Corpus validation found errors.")


@main.command("longstory-summarize")
@click.option(
    "--book-dir",
    "book_dirs",
    multiple=True,
    required=True,
    type=click.Path(path_type=Path),
)
@click.option("--output-dir", default="outputs/longstoryeval/summaries", show_default=True)
@click.option("--model", default=None, help="Default: $JUDGE_MODEL or gpt-4o")
@click.option("--api-base", default=None, help="Default: $OPENAI_BASE_URL")
@click.option("--api-key", default=None, help="Default: $OPENAI_API_KEY")
@click.option("--concurrent", default=1, show_default=True, type=int)
@click.option("--max-chars", default=12000, show_default=True, type=int)
@click.option("--dry-run", is_flag=True)
def longstory_summarize(
    book_dirs,
    output_dir,
    model,
    api_base,
    api_key,
    concurrent,
    max_chars,
    dry_run,
):
    """Generate LongStoryEval chapter-progressive summaries for book JSON files."""
    _load_dotenv()
    config = (
        LongStoryConfig(
            model=model or os.environ.get("JUDGE_MODEL") or "gpt-4o",
            api_key="dry-run",
        )
        if dry_run
        else env_config(model, api_base, api_key)
    )
    results = summarize_books(
        book_dirs,
        Path(output_dir),
        config,
        max_chars=max_chars,
        concurrent=concurrent,
        dry_run=dry_run,
    )
    click.echo(f"LongStoryEval summaries: {len(results)} books")
    click.echo(f"  output: {output_dir}")
    if dry_run:
        for item in results:
            click.echo(f"  dry-run: {item['book']} chunks={item['chunks']}")


@main.command("longstory-evaluate")
@click.option(
    "--book-dir",
    "book_dirs",
    multiple=True,
    required=True,
    type=click.Path(path_type=Path),
)
@click.option("--summary-dir", required=True, type=click.Path(path_type=Path))
@click.option(
    "--book-info",
    "book_infos",
    multiple=True,
    required=True,
    type=click.Path(path_type=Path),
)
@click.option("--output-dir", default="outputs/longstoryeval/evaluations", show_default=True)
@click.option("--model", default=None, help="Default: $JUDGE_MODEL or gpt-4o")
@click.option("--api-base", default=None, help="Default: $OPENAI_BASE_URL")
@click.option("--api-key", default=None, help="Default: $OPENAI_API_KEY")
@click.option("--concurrent", default=1, show_default=True, type=int)
@click.option("--dry-run", is_flag=True)
def longstory_evaluate(
    book_dirs,
    summary_dir,
    book_infos,
    output_dir,
    model,
    api_base,
    api_key,
    concurrent,
    dry_run,
):
    """Run LongStoryEval summary-based quality evaluation."""
    _load_dotenv()
    config = (
        LongStoryConfig(
            model=model or os.environ.get("JUDGE_MODEL") or "gpt-4o",
            api_key="dry-run",
        )
        if dry_run
        else env_config(model, api_base, api_key)
    )
    results = evaluate_book_summaries(
        book_dirs,
        Path(summary_dir),
        book_infos,
        Path(output_dir),
        config,
        concurrent=concurrent,
        dry_run=dry_run,
    )
    summary_path = Path(output_dir) / "summary.json"
    if not dry_run:
        summary_path.write_text(
            json.dumps(results, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    click.echo(f"LongStoryEval evaluations: {len(results)} books")
    click.echo(f"  output: {output_dir}")
    if dry_run:
        for item in results:
            click.echo(f"  dry-run: {item['book']}")


@main.command("constory-judge")
@click.option("--input", "input_path", required=True, help="Prepared ConStory parquet path")
@click.option("--model-name", required=True, help="Name used in ConStory output filename")
@click.option("--output-dir", default="outputs/constory", show_default=True)
@click.option(
    "--output-file",
    default=None,
    type=click.Path(path_type=Path),
    help="Exact CSV output path. Use this to resume into an existing result file.",
)
@click.option("--judge-model", default=None, help="Default: $JUDGE_MODEL or o4-mini")
@click.option("--api-base", default=None, help="Default: $OPENAI_BASE_URL or OpenAI")
@click.option("--api-key", default=None, help="Default: $OPENAI_API_KEY")
@click.option("--concurrent", default=3, show_default=True, type=int)
@click.option("--start", default=0, show_default=True, type=int)
@click.option("--end", default=None, type=int)
@click.option("--no-resume", is_flag=True)
def constory_judge(
    input_path,
    model_name,
    output_dir,
    output_file,
    judge_model,
    api_base,
    api_key,
    concurrent,
    start,
    end,
    no_resume,
):
    """Run vendored ConStory-Checker on a prepared corpus."""
    _load_dotenv()
    judge_model = judge_model or os.environ.get("JUDGE_MODEL") or "o4-mini"
    api_base = api_base or os.environ.get("OPENAI_BASE_URL") or "https://api.openai.com/v1"
    api_key = api_key or os.environ.get("OPENAI_API_KEY") or ""
    if not api_key:
        raise click.ClickException("Missing API key. Set OPENAI_API_KEY or pass --api-key.")

    repo_root = Path(__file__).resolve().parent.parent
    constory_root = repo_root / "lib" / "ConStory-Bench"
    prompts_dir = constory_root / "prompts"
    env = os.environ.copy()
    env["PYTHONPATH"] = (
        str(constory_root)
        if not env.get("PYTHONPATH")
        else f"{constory_root}{os.pathsep}{env['PYTHONPATH']}"
    )

    cmd = [
        sys.executable,
        "-m",
        "constory.judge",
        "--input",
        input_path,
        "--story-column",
        "story_text",
        "--model-name",
        model_name,
        "--output-dir",
        output_dir,
        "--judge-model",
        judge_model,
        "--api-base",
        api_base,
        "--api-key",
        api_key,
        "--prompts-dir",
        str(prompts_dir),
        "--concurrent",
        str(concurrent),
        "--start",
        str(start),
    ]
    if output_file is not None:
        cmd.extend(["--output-file", str(output_file)])
    if end is not None:
        cmd.extend(["--end", str(end)])
    if no_resume:
        cmd.append("--no-resume")

    click.echo(f"Running ConStory-Checker on {input_path}")
    subprocess.run(cmd, check=True, env=env)


@main.command()
@click.option("--source", required=True, help="Path to source chapter text")
@click.option("--continuation", required=True, help="Path to continuation chapter text")
@click.option("--model", default=None, help="Judge model (default from .env)")
@click.option("--output", default=None, help="Output JSON path")
def consistency(source, continuation, model, output):
    """Run consistency error detection on a continuation chapter."""
    click.echo(f"Consistency check: source={source}, continuation={continuation}")
    click.echo("(judge calls via LLM — implementation pending)")


@main.command()
@click.option("--summary", required=True, help="Path to chapter summary")
@click.option("--model", default=None, help="Judge model (default from .env)")
@click.option("--output", default=None, help="Output JSON path")
def critique(summary, model, output):
    """Run 8-dimensional quality critique on a chapter summary."""
    click.echo(f"Quality critique: summary={summary}")
    click.echo("(judge calls via LLM — implementation pending)")


@main.command()
@click.option("--text", required=True, help="Path to chapter text")
@click.option("--character-list", default=None, help="Path to character list JSON")
@click.option("--output", default=None, help="Output JSON path")
def social(text, character_list, output):
    """Build character social network and compute metrics."""
    click.echo(f"Social network analysis: text={text}")
    click.echo("(networkx-based analysis — implementation pending)")


@main.command()
@click.option("--text", required=True, help="Path to chapter text")
@click.option("--reference", default=None, help="Path to reference arc JSON for correlation")
@click.option("--output", default=None, help="Output JSON path")
def emotion(text, reference, output):
    """Compute emotional arc of a chapter and compare with reference."""
    click.echo(f"Emotion arc analysis: text={text}")
    click.echo("(sentiment segmentation + clustering — implementation pending)")


@main.command("emotion-happiness")
@click.option(
    "--book-json",
    default="data/processed/longstoryeval/original/books_json/红楼梦前80回.json",
    show_default=True,
    type=click.Path(path_type=Path),
    help="LongStoryEval book JSON to score",
)
@click.option(
    "--output",
    default="outputs/emotion/original_80_happiness.json",
    show_default=True,
    type=click.Path(path_type=Path),
    help="JSON array output path",
)
@click.option(
    "--summary-output",
    default="outputs/emotion/original_80_happiness_summary.json",
    show_default=True,
    type=click.Path(path_type=Path),
    help="Companion summary with chapter-level curve",
)
def emotion_happiness(book_json, output, summary_output):
    """Score paragraph-level happiness with an offline Hedonometer-like heuristic."""
    summary = write_happiness_json(book_json, output, summary_output)
    click.echo("Happiness scoring completed:")
    click.echo(f"  book: {book_json}")
    click.echo(f"  output: {output}")
    click.echo(f"  segments: {summary['segments']}")
    click.echo(f"  mean happiness: {summary['mean_happiness']}")
    click.echo(f"  summary: {summary_output}")


@main.command("emotion-arc")
@click.option(
    "--book-json",
    default="data/processed/longstoryeval/original/books_json/红楼梦前80回.json",
    show_default=True,
    type=click.Path(path_type=Path),
    help="LongStoryEval book JSON to score",
)
@click.option(
    "--output",
    default="outputs/emotion/original_80_emotion_arc.json",
    show_default=True,
    type=click.Path(path_type=Path),
)
@click.option("--points", default=100, show_default=True, type=int)
@click.option("--window-size", default=10000, show_default=True, type=int)
@click.option(
    "--lexicon",
    default="builtin",
    show_default=True,
    help="Lexicon to use: builtin or ntusd",
)
@click.option("--positive-lexicon", default=None, type=click.Path(path_type=Path))
@click.option("--negative-lexicon", default=None, type=click.Path(path_type=Path))
def emotion_arc(book_json, output, points, window_size, lexicon, positive_lexicon, negative_lexicon):
    """Generate a Reagan et al. inspired sliding-window emotional arc."""
    payload = write_sliding_window_arc(
        book_json,
        output,
        points=points,
        window_size=window_size,
        lexicon_name=lexicon,
        positive_path=positive_lexicon,
        negative_path=negative_lexicon,
    )
    click.echo("Emotion arc completed:")
    click.echo(f"  book: {book_json}")
    click.echo(f"  output: {output}")
    click.echo(f"  lexicon: {payload['lexicon']} ({payload['lexicon_terms']} terms)")
    click.echo(f"  tokens: {payload['tokens']}")
    click.echo(f"  points: {payload['points']}")
    click.echo(f"  window size: {payload['window_size']}")
    click.echo(f"  mean happiness: {payload['mean_happiness']}")
    click.echo(f"  mean matched terms/window: {payload['mean_matched_terms']}")


@main.command("emotion-arc-model")
@click.option(
    "--book-json",
    default="data/processed/longstoryeval/original/books_json/红楼梦前80回.json",
    show_default=True,
    type=click.Path(path_type=Path),
    help="LongStoryEval book JSON to score",
)
@click.option(
    "--output",
    default="outputs/emotion/model_score/original_80_llm_arc.json",
    show_default=True,
    type=click.Path(path_type=Path),
)
@click.option(
    "--model-backend",
    default="llm",
    show_default=True,
    type=click.Choice(["llm", "snownlp"]),
    help="Model scoring backend. llm uses .env OpenAI-compatible settings.",
)
@click.option("--points", default=80, show_default=True, type=int)
@click.option("--window-size", default=5000, show_default=True, type=int)
@click.option("--model", default=None, help="LLM model. Default: $EMOTION_MODEL, $JUDGE_MODEL, or deepseek-chat")
@click.option("--api-base", default=None, help="Default: $OPENAI_BASE_URL")
@click.option("--api-key", default=None, help="Default: $OPENAI_API_KEY")
@click.option("--concurrent", default=1, show_default=True, type=int)
@click.option("--max-window-chars", default=12000, show_default=True, type=int)
@click.option("--no-resume", is_flag=True, help="Disable resume from existing output")
@click.option("--dry-run", is_flag=True, help="Write placeholder output without calling an API")
def emotion_arc_model(
    book_json,
    output,
    model_backend,
    points,
    window_size,
    model,
    api_base,
    api_key,
    concurrent,
    max_window_chars,
    no_resume,
    dry_run,
):
    """Generate scheme-2 model-scored sliding-window emotional arc."""
    _load_dotenv()
    if model_backend == "snownlp":
        payload = write_snownlp_model_arc(
            book_json,
            output,
            points=points,
            window_size=window_size,
        )
    else:
        resolved_model = (
            model
            or os.environ.get("EMOTION_MODEL")
            or os.environ.get("JUDGE_MODEL")
            or "deepseek-chat"
        )
        resolved_base = api_base or os.environ.get("OPENAI_BASE_URL")
        resolved_key = api_key or os.environ.get("OPENAI_API_KEY") or ""
        if not resolved_key and not dry_run:
            raise click.ClickException("Missing API key. Set OPENAI_API_KEY or pass --api-key.")
        config = LLMEmotionConfig(
            model=resolved_model,
            api_key=resolved_key or "dry-run",
            api_base=resolved_base,
            max_window_chars=max_window_chars,
        )
        payload = write_llm_window_arc(
            book_json,
            output,
            config=config,
            points=points,
            window_size=window_size,
            concurrent=concurrent,
            resume=not no_resume,
            dry_run=dry_run,
        )
    click.echo("Model emotion arc completed:")
    click.echo(f"  book: {book_json}")
    click.echo(f"  output: {output}")
    click.echo(f"  scheme: {payload['scheme']}")
    click.echo(f"  scorer type: {payload['scorer_type']}")
    click.echo(f"  model: {payload['model']}")
    click.echo(f"  tokens: {payload['tokens']}")
    click.echo(f"  points: {payload['points']}")
    click.echo(f"  window size: {payload['window_size']}")
    if "completed_points" in payload:
        click.echo(f"  completed points: {payload['completed_points']}")
    click.echo(f"  mean happiness: {payload['mean_happiness']}")


@main.command()
@click.option("--source-dir", required=True, help="Directory of source chapters")
@click.option("--continuation-dir", required=True, help="Directory of continuation chapters")
@click.option("--model", default=None, help="Judge model (default from .env)")
@click.option("--output-dir", default=None, help="Output directory")
@click.option("--categories", default="all", help="Comma-separated: consistency,critique,social,emotion")
def all(source_dir, continuation_dir, model, output_dir, categories):
    """Run all enabled evaluation methods on all chapters."""
    click.echo(f"Full evaluation: source={source_dir}, continuation={continuation_dir}")
    click.echo(f"Enabled: {categories}")
    click.echo("(batch evaluation pipeline — implementation pending)")


if __name__ == "__main__":
    main()
