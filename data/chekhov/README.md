# Chekhov Corpus Workspace

This directory contains the reproducible Chekhov preprocessing workspace.

## Layout

| Path | Purpose |
|---|---|
| `../../chekhov/chekhov_short_stories.txt` | Tracked Project Gutenberg #57333 source text. |
| `scripts/preprocess_chekhov.py` | Rule-based preprocessing and story splitting script. |
| `processed/stories_all.jsonl` | All detected story segments, including duplicate translations. |
| `processed/stories_canonical.jsonl` | One selected record per canonical title, used for default statistics. |
| `processed/stories_all.csv` | Metadata-only CSV for all segments. |
| `processed/stories_canonical.csv` | Metadata-only CSV for canonical stories. |
| `processed/title_index.csv` | Duplicate-title index and selected canonical record. |
| `processed/stats.json` | Machine-readable corpus statistics. |
| `processed/manifest.json` | Preprocessing policy, output registry, and audit summary. |
| `reports/chekhov_normalized_stats.md` | Human-readable corpus statistics report. |
| `../../chekhov/chekhov_analysis.md` | Downstream visual analysis generated from normalized results. |
| `reports/chekhov_analysis_legacy.md` | Previous visualization report kept locally for comparison. |
| `docs/chekhov_preprocessing_and_foreshadowing_design.md` | Design notes and future foreshadowing-analysis plan. |

## Rebuild

Run from the repository root:

```bash
python data/chekhov/scripts/preprocess_chekhov.py
```

Current normalized output:

- 213 detected story segments.
- 201 canonical story records.
- 845,027 words in the canonical corpus.
- 16 unmatched catalog titles, all from non-Chekhov or absent-body entries in the Gutenberg compilation.
