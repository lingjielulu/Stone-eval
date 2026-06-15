# HongLou CFPG Layer Overview

当前有四层数据：

1. 摘要层: `data/processed/cfpg/honglou_booksum/original_80_chapter_summaries.jsonl`
   - 人类可读: `data/processed/cfpg/honglou_booksum/original_80_chapter_summaries.review.md`
   - chapters: 80
2. 摘要句时间线层: `data/processed/cfpg/summary_alignments/original_80_summary_sentence_timeline_20260611_deepseek_honglou_original80.jsonl`
   - summary sentences: 504
3. 伏笔层: `data/processed/cfpg/foreshadows/honglou_foreshadows_20260611_deepseek_honglou_original80.jsonl`
   - 人类可读: `data/processed/cfpg/foreshadows/honglou_foreshadows_20260611_deepseek_honglou_original80.review.md`
   - rows: 1057
4. 伏笔+trigger 候选层: `data/processed/cfpg/foreshadow_triggers/honglou_foreshadow_triggers_20260611_deepseek_honglou_original80.jsonl`
   - 人类可读: `data/processed/cfpg/foreshadow_triggers/honglou_foreshadow_triggers_20260611_deepseek_honglou_original80.review.md`
   - rows: 38
5. 伏笔-trigger-payoff verified 层: `data/processed/cfpg/verified/honglou_ftp_triples_20260611_deepseek_honglou_original80.unique.jsonl`
   - 人类可读: `data/processed/cfpg/verified/honglou_ftp_triples_20260611_deepseek_honglou_original80.unique.review.md`
   - unique triples: 30

说明：伏笔层包含摘要阶段保留下来的 unresolved/foreshadow/poem-dream-object 条目，另附候选抽取阶段实际用作 F 的摘要句。伏笔+trigger 层来自 candidate extraction，包含 accepted/rejected/review 状态；verified 层只保留通过 verifier 的 F-T-P。
