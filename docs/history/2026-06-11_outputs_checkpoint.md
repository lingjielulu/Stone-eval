# Output Archive Marker

Archived on `2026-06-11` before starting the ConStory-Bench ACL-2026
reproduction stage.

Previous-stage outputs:

- Corpus validation: `resources/corpora/hongloumeng/prepared/reports/corpus_validation.json`
- ConStory smoke run:
  - `stone_eval/consistency/results/hongloumeng_original80_smoke_20260608/original/judge_original_80_0_end_20260608_100032.csv`
  - `stone_eval/consistency/results/hongloumeng_original80_smoke_20260608/original/judge_original_80_partial16_deepseek-v4-pro_20260608_100032.csv`
- Emotion arc baseline:
  - `stone_eval/emotion/results/hongloumeng_baselines_202606/original_80_emotion_arc_ntusd_recommended.json`
  - `stone_eval/emotion/results/hongloumeng_baselines_202606/original_80_ntusd_emotion_arc_smoothed.png`
  - `stone_eval/emotion/results/hongloumeng_baselines_202606/original_80_ntusd_smoothed_peaks_valleys.csv`
  - `stone_eval/emotion/results/hongloumeng_baselines_202606/original_80_ntusd_smoothed_peaks_valleys.json`
- Model-scored emotion arc:
  - `stone_eval/emotion/results/hongloumeng_baselines_202606/model_score/original_80_deepseek_arc.json`
  - `stone_eval/emotion/results/hongloumeng_baselines_202606/model_score/original_80_deepseek_arc_smoothed.png`
  - `stone_eval/emotion/results/hongloumeng_baselines_202606/model_score/original_80_deepseek_peaks_valleys.csv`
  - `stone_eval/emotion/results/hongloumeng_baselines_202606/model_score/original_80_deepseek_peaks_valleys.json`

Use these as previous-stage references only.  New ConStory-Bench reproduction
outputs should go under a new run-specific directory, for example
`stone_eval/consistency/results/<run_id>/`.
