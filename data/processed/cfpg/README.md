# CFPG 复现说明

本 README 是 `data/processed/cfpg/` 的入口说明，记录《红楼梦》CFPG 复现链路的数据准备结果、prompt 位置、人类可读结果位置和生成脚本。

## 项目设计文档

整体设计和项目控制文档：

[documentations/cfpg_reproduction_design.md](../../../documentations/cfpg_reproduction_design.md)

这份文档记录复现目标、论文方法拆解、BookSum-style 摘要路线、数据层级、prompt 规范、目录规划和后续阶段。

## 当前状态

- 已删除：前 6 回 smoke test 产物。
- 已完成：前 80 回 BookSum-style 摘要层、摘要句时间线、宽口径伏笔层。
- 待完成：分段/滑窗 F-P 候选抽取、Trigger 固化、F-T-P 验证层。

## Prompt 文件

当前 CFPG 主链路的可编辑 prompt 文件：

[prompts/cfpg/honglou_prompts.md](../../../prompts/cfpg/honglou_prompts.md)

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

[outputs/cfpg/honglou_summary_original80/report.json](../../../outputs/cfpg/honglou_summary_original80/report.json)

### 2. 摘要句时间线

机器可读：

[summary_alignments/original_80_summary_sentence_timeline_20260611_deepseek_honglou_original80.jsonl](summary_alignments/original_80_summary_sentence_timeline_20260611_deepseek_honglou_original80.jsonl)

### 3. 伏笔层

机器可读：

[foreshadows/honglou_foreshadows_20260611_deepseek_honglou_original80.jsonl](foreshadows/honglou_foreshadows_20260611_deepseek_honglou_original80.jsonl)

人类可读：

[foreshadows/honglou_foreshadows_20260611_deepseek_honglou_original80.review.md](foreshadows/honglou_foreshadows_20260611_deepseek_honglou_original80.review.md)

### 4. 伏笔 + Trigger 候选层

当前尚未正式抽取。现有占位文件为空：

[foreshadow_triggers/honglou_foreshadow_triggers_20260611_deepseek_honglou_original80.jsonl](foreshadow_triggers/honglou_foreshadow_triggers_20260611_deepseek_honglou_original80.jsonl)

[foreshadow_triggers/honglou_foreshadow_triggers_20260611_deepseek_honglou_original80.review.md](foreshadow_triggers/honglou_foreshadow_triggers_20260611_deepseek_honglou_original80.review.md)

### 5. 已验证 Foreshadow-Trigger-Payoff 层

尚未生成。需要先完成分段/滑窗候选抽取和验证。

## 生成脚本

- [scripts/summarize_honglou_booksum.py](../../../scripts/summarize_honglou_booksum.py)
- [scripts/build_cfpg_summary_timeline.py](../../../scripts/build_cfpg_summary_timeline.py)
- [scripts/extract_honglou_ftp.py](../../../scripts/extract_honglou_ftp.py)
- [scripts/render_honglou_summary_review.py](../../../scripts/render_honglou_summary_review.py)
- [scripts/render_cfpg_layers_review.py](../../../scripts/render_cfpg_layers_review.py)

摘要层生成：

```bash
python scripts/summarize_honglou_booksum.py --force
python scripts/render_honglou_summary_review.py
python scripts/build_cfpg_summary_timeline.py
python scripts/render_cfpg_layers_review.py
```

两个 LLM 脚本都支持：

```text
--prompt-file prompts/cfpg/honglou_prompts.md
```
