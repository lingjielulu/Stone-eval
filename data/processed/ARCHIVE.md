# Processed Data Archive Marker

Archived on `2026-06-11` before starting the ConStory-Bench ACL-2026
reproduction stage.

This directory currently stores prepared HongLou continuation corpora generated
by `stone-eval prepare-corpus`.

Key files:

- `manifest.json`
- `constory/original_chapters.parquet`
- `constory/continuation_chapters.parquet`
- `longstoryeval/original/books_json/红楼梦前80回.json`
- `longstoryeval/continuations/books_json/*.json`
- `chapters/original/*.txt`
- `chapters/continuations/*/*.txt`

Validation checkpoint:

- Report: `outputs/corpus_validation.json`
- Errors: `0`
- Warnings: `0`
- Original chapters: `80`
- Continuation chapters: `552`
- Continuation books: `15`

Do not overwrite this directory during the next reproduction stage without first
creating a new archive marker.

