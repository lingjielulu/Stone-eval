# Evaluation Workflow

Current stage uses two literature-backed evaluators:

1. ConStory-Bench / ConStory-Checker for chapter-level consistency issues.
2. LongStoryEval / NovelCritique-style inputs for book-level narrative quality.

Original text and continuations are evaluated as separate corpora.

## Prepare Data

```bash
stone-eval prepare-corpus \
  --original 红楼梦.txt \
  --continuations 红楼梦续作文本 \
  --output-dir data/processed \
  --original-chapters 80
```

Outputs:

- `data/processed/constory/original_chapters.parquet`
- `data/processed/constory/continuation_chapters.parquet`
- `data/processed/longstoryeval/original/books_json/`
- `data/processed/longstoryeval/continuations/books_json/`
- `data/processed/manifest.json`

## Run ConStory-Checker

Original chapters:

```bash
stone-eval constory-judge \
  --input data/processed/constory/original_chapters.parquet \
  --model-name original_80 \
  --output-dir outputs/constory/original
```

Continuation chapters:

```bash
stone-eval constory-judge \
  --input data/processed/constory/continuation_chapters.parquet \
  --model-name continuations \
  --output-dir outputs/constory/continuations
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

The upstream LongStoryEval API scripts currently hard-code empty API key and URL
fields, so the next integration step is to wrap or patch those scripts to read
the same `.env` variables used by `stone-eval constory-judge`.
