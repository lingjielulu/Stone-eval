# 2026-06-11 Previous Experiment Archive

## Purpose

This checkpoint marks the end of the current exploratory stage before starting
the next reproduction target:

- Paper target: ConStory-Bench ACL-2026
- Repository: https://github.com/Picrew/ConStory-Bench
- Next focus: LLM long-narrative consistency error classification

The previous stage is archived as a Stone-eval corpus preparation and baseline
evaluation checkpoint for HongLou continuation evaluation.

## Repository State

- Branch: `master`
- Base commit before local experiment changes: `f7fee17 Add ConStory-Bench and LongStoryEval as submodules`
- Local modified tracked files:
  - `pyproject.toml`
  - `requirements.txt`
  - `stone_eval/cli.py`
  - `stone_eval/emotion/__init__.py`
  - `stone_eval/quality/__init__.py`
  - `third_party/ConStory-Bench/constory/judge.py`
- Local new experiment files:
  - `stone_eval/corpus.py`
  - `stone_eval/longstory.py`
  - `stone_eval/emotion/hedonometer.py`
  - `stone_eval/emotion/model_score.py`
  - `scripts/plot_smoothed_emotion_arc.py`
  - `environment-emotion.yml`
  - `documentations/*`
  - `resources/corpora/hongloumeng/prepared/*`
  - `resources/lexicons/ntusd/*`
  - `outputs/*`
  - `logs/*`

## Completed Work

### Corpus preparation

Prepared `红楼梦` original and continuation corpora for both ConStory-Bench and
LongStoryEval-style pipelines.

Primary command:

```bash
stone-eval prepare-corpus \
  --original 红楼梦.txt \
  --continuations 红楼梦续作文本 \
  --output-dir resources/corpora/hongloumeng/prepared \
  --original-chapters 80
```

Validation output:

- `resources/corpora/hongloumeng/prepared/reports/corpus_validation.json`
- Errors: `0`
- Warnings: `0`
- ConStory original rows: `80`
- ConStory continuation rows: `552`
- Continuation books: `15`

Canonical prepared inputs:

- `resources/corpora/hongloumeng/prepared/manifest.json`
- `resources/corpora/hongloumeng/prepared/constory/original_chapters.parquet`
- `resources/corpora/hongloumeng/prepared/constory/continuation_chapters.parquet`
- `resources/corpora/hongloumeng/prepared/longstoryeval/original/books_json/红楼梦前80回.json`
- `resources/corpora/hongloumeng/prepared/longstoryeval/continuations/books_json/*.json`

### ConStory judge smoke run

Ran the vendored ConStory judge on the original 80 chapters as a baseline smoke
test.  This is not yet the full ConStory-Bench reproduction.

Outputs:

- `experiments/hongloumeng_constory_smoke/runs/20260608_original80_smoke/original/judge_original_80_0_end_20260608_100032.csv`
- `experiments/hongloumeng_constory_smoke/runs/20260608_original80_smoke/original/judge_original_80_partial16_deepseek-v4-pro_20260608_100032.csv`
- `logs/judge_20260608_100032.log`

Observed log boundary:

- Start: `2026-06-08 10:00:32`
- Loaded stories: `80`
- Criteria templates loaded: `5`

Local ConStory-Bench adapter change:

- Added `--output-file` to `third_party/ConStory-Bench/constory/judge.py`
- Purpose: resume or write into a deterministic CSV path from `stone-eval constory-judge`

### Emotion arc baseline

Implemented and ran two emotion-arc baselines for `红楼梦前80回`.

Dictionary/NTUSD baseline:

- Output: `experiments/hongloumeng_emotion_arc/runs/baselines_202606/original_80_emotion_arc_ntusd_recommended.json`
- Figure: `experiments/hongloumeng_emotion_arc/runs/baselines_202606/original_80_ntusd_emotion_arc_smoothed.png`
- Peaks/valleys:
  - `experiments/hongloumeng_emotion_arc/runs/baselines_202606/original_80_ntusd_smoothed_peaks_valleys.csv`
  - `experiments/hongloumeng_emotion_arc/runs/baselines_202606/original_80_ntusd_smoothed_peaks_valleys.json`
- Tokens: `396323`
- Points: `240`
- Window size: `5000`
- Mean happiness: `4.5801`

LLM model-scored baseline:

- Output: `experiments/hongloumeng_emotion_arc/runs/baselines_202606/model_score/original_80_deepseek_arc.json`
- Figure: `experiments/hongloumeng_emotion_arc/runs/baselines_202606/model_score/original_80_deepseek_arc_smoothed.png`
- Peaks/valleys:
  - `experiments/hongloumeng_emotion_arc/runs/baselines_202606/model_score/original_80_deepseek_peaks_valleys.csv`
  - `experiments/hongloumeng_emotion_arc/runs/baselines_202606/model_score/original_80_deepseek_peaks_valleys.json`
- Model: `deepseek-v4-pro`
- API base: `https://api.deepseek.com`
- Tokens: `396323`
- Points: `80`
- Window size: `5000`
- Completed points: `80`
- Mean happiness: `4.6338`

## Current CLI Surface

Useful commands added or extended in this stage:

```bash
stone-eval prepare-corpus
stone-eval validate-corpus
stone-eval constory-judge
stone-eval longstory-summarize
stone-eval longstory-evaluate
stone-eval emotion-happiness
stone-eval emotion-arc
stone-eval emotion-arc-model
```

## Known Limitations

- `consistency`, `critique`, `social`, and `all` CLI commands still contain
  placeholder implementations.
- The ConStory judge run is only a baseline/smoke run on the original 80
  chapters.  It has not yet been converted into a full long-narrative
  consistency error classification reproduction protocol.
- LongStoryEval summarization/evaluation helpers are present, but no completed
  LongStoryEval output files were found under `outputs/longstoryeval`.
- The ConStory-Bench submodule has a local adapter patch.  Treat the submodule
  as locally modified until that patch is either committed upstream in the
  superproject workflow or re-applied after reset.
- Raw text files and generated corpora may be large and are experiment assets,
  not hand-curated source code.

## Boundary for Next Stage

Start the next stage from this boundary:

1. Keep `resources/corpora/hongloumeng/prepared/constory/*.parquet` as the prepared Stone-eval input
   unless the ConStory-Bench reproduction requires a different schema.
2. Treat `experiments/hongloumeng_constory_smoke/runs/20260608_original80_smoke/original/*20260608_100032.csv` as previous-stage
   smoke output only.
3. Build the next experiment around ConStory-Bench's error taxonomy, annotation
   format, and evaluation protocol instead of extending the emotion arc outputs.

