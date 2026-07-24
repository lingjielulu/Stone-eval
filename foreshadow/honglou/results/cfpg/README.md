# CFPG 复现说明

本 README 是 `foreshadow/honglou/results/cfpg/` 的入口说明，记录《红楼梦》CFPG 复现链路的数据准备结果、prompt 位置、人类可读结果位置和生成脚本。

## 实验报告

前 80 回实验报告：

[original80_report.md](original80_report.md)

报告包含方法、结果统计、例子、数据量与质量分析、问题和结果链接。README 保持为入口索引，报告负责记录本轮实验分析。

## 项目设计文档

整体设计和项目控制文档：

[foreshadow/honglou/docs/cfpg_reproduction_design.md](../../docs/cfpg_reproduction_design.md)

这份文档记录复现目标、论文方法拆解、BookSum-style 摘要路线、数据层级、prompt 规范、目录规划和后续阶段。

## 当前状态

- 已删除：前 6 回 smoke test 产物。
- 已完成：前 80 回 BookSum-style 摘要层、摘要句时间线、宽口径伏笔层、分窗 F-P 候选抽取、Trigger 候选和 F-T-P 验证层。
- 当前结果：38 个 F+Trigger 候选，30 个 verified F-T-P，8 个 rejected candidates。
- 待完成：人工抽样审查、schema 清洗、续作伏笔兑现评价。

## Prompt 文件

当前 CFPG 主链路的可编辑 prompt 文件：

[foreshadow/honglou/prompts/honglou_prompts.md](../../prompts/honglou_prompts.md)

该文件包含三个 prompt block：

- `booksum_chapter_summary`: 生成 BookSum-style 每回摘要。
- `candidate_extraction`: 从摘要句时间线抽取候选 Foreshadow-Payoff，并生成 provisional Trigger。
- `candidate_verification`: 验证候选是否形成 Foreshadow-Trigger-Payoff 三元组。

## 已生成结果

优先从总览文件开始看：

[layers/honglou_cfpg_layers_20260611_deepseek_honglou_original80.review.md](layers/honglou_cfpg_layers_20260611_deepseek_honglou_original80.review.md)

### 1. BookSum-style 摘要层

机器可读：

[honglou_booksum/original_80_chapter_summaries.jsonl](honglou_booksum/original_80_chapter_summaries.jsonl)

人类可读：

[honglou_booksum/original_80_chapter_summaries.review.md](honglou_booksum/original_80_chapter_summaries.review.md)

报告：

[foreshadow/honglou/results/cfpg_reports/honglou_summary_original80/report.json](../cfpg_reports/honglou_summary_original80/report.json)

### 2. 摘要句时间线

机器可读：

[summary_alignments/original_80_summary_sentence_timeline_20260611_deepseek_honglou_original80.jsonl](summary_alignments/original_80_summary_sentence_timeline_20260611_deepseek_honglou_original80.jsonl)

### 3. 伏笔层

机器可读：

[foreshadows/honglou_foreshadows_20260611_deepseek_honglou_original80.jsonl](foreshadows/honglou_foreshadows_20260611_deepseek_honglou_original80.jsonl)

人类可读：

[foreshadows/honglou_foreshadows_20260611_deepseek_honglou_original80.review.md](foreshadows/honglou_foreshadows_20260611_deepseek_honglou_original80.review.md)

### 4. 伏笔 + Trigger 候选层

[foreshadow_triggers/honglou_foreshadow_triggers_20260611_deepseek_honglou_original80.jsonl](foreshadow_triggers/honglou_foreshadow_triggers_20260611_deepseek_honglou_original80.jsonl)

[foreshadow_triggers/honglou_foreshadow_triggers_20260611_deepseek_honglou_original80.review.md](foreshadow_triggers/honglou_foreshadow_triggers_20260611_deepseek_honglou_original80.review.md)

候选源文件：

[candidates/honglou_candidates_20260611_deepseek_honglou_original80.jsonl](candidates/honglou_candidates_20260611_deepseek_honglou_original80.jsonl)

### 5. 已验证 Foreshadow-Trigger-Payoff 层

机器可读：

[verified/honglou_ftp_triples_20260611_deepseek_honglou_original80.unique.jsonl](verified/honglou_ftp_triples_20260611_deepseek_honglou_original80.unique.jsonl)

人类可读：

[verified/honglou_ftp_triples_20260611_deepseek_honglou_original80.unique.review.md](verified/honglou_ftp_triples_20260611_deepseek_honglou_original80.unique.review.md)

Rejected candidates：

[verified/honglou_rejected_candidates_20260611_deepseek_honglou_original80.jsonl](verified/honglou_rejected_candidates_20260611_deepseek_honglou_original80.jsonl)

## 生成脚本

- [foreshadow/honglou/scripts/summarize_honglou_booksum.py](../../scripts/summarize_honglou_booksum.py)
- [foreshadow/honglou/scripts/build_cfpg_summary_timeline.py](../../scripts/build_cfpg_summary_timeline.py)
- [foreshadow/honglou/scripts/extract_honglou_ftp.py](../../scripts/extract_honglou_ftp.py)
- [foreshadow/honglou/scripts/render_honglou_summary_review.py](../../scripts/render_honglou_summary_review.py)
- [foreshadow/honglou/scripts/render_cfpg_layers_review.py](../../scripts/render_cfpg_layers_review.py)

摘要层生成：

```bash
python foreshadow/honglou/scripts/summarize_honglou_booksum.py --force
python foreshadow/honglou/scripts/render_honglou_summary_review.py
python foreshadow/honglou/scripts/build_cfpg_summary_timeline.py
python foreshadow/honglou/scripts/render_cfpg_layers_review.py
```

两个 LLM 脚本都支持：

```text
--prompt-file foreshadow/honglou/prompts/honglou_prompts.md
```
