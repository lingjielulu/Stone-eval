# Output Archive Marker

Archived on `2026-06-11` before starting the ConStory-Bench ACL-2026
reproduction stage.

Previous-stage outputs:

- Corpus validation: `resources/corpora/hongloumeng/prepared/reports/corpus_validation.json`
- ConStory smoke run:
  - `experiments/hongloumeng_constory_smoke/runs/20260608_original80_smoke/original/judge_original_80_0_end_20260608_100032.csv`
  - `experiments/hongloumeng_constory_smoke/runs/20260608_original80_smoke/original/judge_original_80_partial16_deepseek-v4-pro_20260608_100032.csv`
- Emotion arc baseline:
  - `experiments/hongloumeng_emotion_arc/runs/baselines_202606/original_80_emotion_arc_ntusd_recommended.json`
  - `experiments/hongloumeng_emotion_arc/runs/baselines_202606/original_80_ntusd_emotion_arc_smoothed.png`
  - `experiments/hongloumeng_emotion_arc/runs/baselines_202606/original_80_ntusd_smoothed_peaks_valleys.csv`
  - `experiments/hongloumeng_emotion_arc/runs/baselines_202606/original_80_ntusd_smoothed_peaks_valleys.json`
- Model-scored emotion arc:
  - `experiments/hongloumeng_emotion_arc/runs/baselines_202606/model_score/original_80_deepseek_arc.json`
  - `experiments/hongloumeng_emotion_arc/runs/baselines_202606/model_score/original_80_deepseek_arc_smoothed.png`
  - `experiments/hongloumeng_emotion_arc/runs/baselines_202606/model_score/original_80_deepseek_peaks_valleys.csv`
  - `experiments/hongloumeng_emotion_arc/runs/baselines_202606/model_score/original_80_deepseek_peaks_valleys.json`

Use these as previous-stage references only.  New ConStory-Bench reproduction
outputs should go under a new run-specific directory, for example
`experiments/hongloumeng_constory_smoke/runs/<run_id>/`.
