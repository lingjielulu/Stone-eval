"""
Unified CLI for Stone-eval: consistency, quality, social, emotion evaluation.

Usage:
    stone-eval consistency --source chapter_080.txt --continuation chapter_081.txt
    stone-eval critique --summary summary.md
    stone-eval social --text chapter_081.txt --character-list characters.json
    stone-eval emotion --text chapter_081.txt --reference original_arc.json
    stone-eval all --source-dir chapters/ --continuation-dir continuations/
"""

import click

from stone_eval import __version__


@click.group()
@click.version_option(__version__)
def main():
    """Stone-eval: HongLou Meng continuation evaluation suite."""


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
