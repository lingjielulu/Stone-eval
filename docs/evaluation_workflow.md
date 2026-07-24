# Evaluation Workflow

Current stage uses two literature-backed evaluators:

1. ConStory-Bench / ConStory-Checker for chapter-level consistency issues.
2. LongStoryEval / NovelCritique-style inputs for book-level narrative quality.

Original text and continuations are evaluated as separate corpora.

## Prepare Data

```bash
stone-eval prepare-corpus \
  --original resources/corpora/hongloumeng/红楼梦.txt \
  --continuations resources/corpora/hongloumeng/continuations \
  --output-dir resources/corpora/hongloumeng/prepared \
  --original-chapters 80
```

Outputs:

- `resources/corpora/hongloumeng/prepared/constory/original_chapters.parquet`
- `resources/corpora/hongloumeng/prepared/constory/continuation_chapters.parquet`
- `resources/corpora/hongloumeng/prepared/longstoryeval/original/books_json/`
- `resources/corpora/hongloumeng/prepared/longstoryeval/continuations/books_json/`
- `resources/corpora/hongloumeng/prepared/manifest.json`

## Run ConStory-Checker

Original chapters:

```bash
stone-eval constory-judge \
  --input resources/corpora/hongloumeng/prepared/constory/original_chapters.parquet \
  --model-name original_80 \
  --output-dir stone_eval/consistency/results/hongloumeng_original80_smoke_20260608/original
```

Continuation chapters:

```bash
stone-eval constory-judge \
  --input resources/corpora/hongloumeng/prepared/constory/continuation_chapters.parquet \
  --model-name continuations \
  --output-dir stone_eval/consistency/results/continuations
```

The command reads `OPENAI_API_KEY`, `OPENAI_BASE_URL`, and `JUDGE_MODEL` from
`.env` when present.  It uses the vendored ConStory-Bench prompts and writes
separate CSV outputs for original and continuation corpora.

## LongStoryEval Inputs

The prepared `books_json` folders follow LongStoryEval's expected shape:

```json
{
  "id": "book id",
  "title": "book title",
  "kind": "original | continuation",
  "chaps": [
    {
      "title": "chapter title",
      "content": ["line 1", "line 2"]
    }
  ]
}
```

`stone_eval.longstory` wraps the upstream prompt files and reads the same
OpenAI-compatible environment variables used by `stone-eval constory-judge`.
No completed formal LongStoryEval evaluation run is currently archived.
