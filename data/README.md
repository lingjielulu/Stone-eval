# Data Directory

This directory mixes small committed research artifacts with larger local
corpora and generated datasets.

## Commit Policy

| Area | Status | Notes |
|---|---|---|
| `data/processed/cfpg/` | committed selectively | Curated Honglou CFPG artifacts listed in `.gitignore`. |
| `chekhov/` | committed | Tracked Chekhov source text and downstream visual analysis. |
| `data/chekhov/` | committed selectively | Scripts, docs, manifest, and stats are committed; large JSONL/CSV outputs stay local. |
| `data/lexicons/ntusd/*_utf8.txt` | committed | UTF-8 lexicons used by `stone_eval.emotion.hedonometer`. |
| `data/lexicons/ntusd/*_traditional.txt` | local only | Original non-UTF-8 lexicon files; they may appear as mojibake in UTF-8 terminals. |
| `data/processed/chapters/` | local only | Expanded chapter text, regenerated from source corpora. |
| `data/processed/constory/` | local only | Generated parquet inputs. |
| `data/processed/longstoryeval/` | local only | Generated LongStoryEval JSON inputs. |

## Notes

The apparent garbled files are the NTUSD `*_traditional.txt` sources. The
runtime path uses `positive_utf8.txt` and `negative_utf8.txt`, so the
non-UTF-8 originals should not be required for normal runs.
