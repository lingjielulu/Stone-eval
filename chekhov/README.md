# Chekhov Workspace

This directory is the human-facing entry point for the Chekhov corpus work.

## Layout

| Path | Purpose |
|---|---|
| `chekhov_short_stories.txt` | Tracked Project Gutenberg #57333 source text used by preprocessing. |
| `chekhov_analysis.md` | Downstream visual analysis generated from the normalized preprocessing output. |

## Related Data Pipeline

The reproducible preprocessing pipeline lives under `data/chekhov/`:

- `data/chekhov/scripts/preprocess_chekhov.py`
- `data/chekhov/processed/stats.json`
- `data/chekhov/processed/manifest.json`
- `data/chekhov/reports/chekhov_normalized_stats.md`
- `data/chekhov/docs/chekhov_preprocessing_and_foreshadowing_design.md`

Rebuild from the repository root:

```bash
python data/chekhov/scripts/preprocess_chekhov.py
```
