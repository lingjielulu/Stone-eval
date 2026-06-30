# 数据目录

混合保存已提交的研究产物与仅本地保留的较大生成数据。

## 目录结构

| 路径 | 状态 | 说明 |
|---|---|---|
| `chekhov/` | 选择性提交 | 契诃夫短篇语料预处理流水线。原始文本、脚本、文档、统计报告；较大的 JSONL/CSV 产物仅本地保留。 |
| `foreshadow_causality_benchmark/` | 已提交 | 短篇小说伏笔-因果-回收评测基准。含 3 篇 MVP 种子小说（The Speckled Band、The Diamond Necklace、To Build a Fire）的归一化文本、人工标注、候选集和校验脚本。 |
| `lexicons/ntusd/` | 选择性提交 | NTUSD 正负面情感词表。`*_utf8.txt` 已提交（`stone_eval.emotion.hedonometer` 使用），`*_traditional.txt` 仅本地（非 UTF-8 编码）。 |
| `prompts/` | 仅本地 | 提示词模板目录（预留）。 |
| `processed/ARCHIVE.md` | 已提交 | 处理产物归档说明。 |
| `processed/manifest.json` | 仅本地 | 处理产物清单。 |
| `processed/cfpg/` | 选择性提交 | 红楼梦伏笔-触发-回收图（CFPG）流水线产物，`.gitignore` 中列出精选提交。 |
| `processed/chapters/` | 仅本地 | 展开的章节文本（80 回原文 + 15 个续写版本共 552 章），可由源语料重新生成。 |
| `processed/constory/` | 仅本地 | ConStory parquet 输入。 |
| `processed/longstoryeval/` | 仅本地 | LongStoryEval JSON 输入（原文 + 15 个续写版本）。 |

## 备注

看起来像乱码的文件主要是 NTUSD 的 `*_traditional.txt` 源文件。运行时使用 `positive_utf8.txt` 和 `negative_utf8.txt`，正常运行不依赖这些非 UTF-8 原始文件。
