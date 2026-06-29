# 数据目录

这个目录混合保存少量已提交的研究产物，以及较大的本地语料和生成数据。

## 提交策略

| 区域 | 状态 | 说明 |
|---|---|---|
| `data/processed/cfpg/` | 选择性提交 | `.gitignore` 中列出的红楼梦 CFPG 精选产物。 |
| `chekhov/` | 已提交 | 契诃夫原始文本和下游可视化分析报告。 |
| `data/chekhov/` | 选择性提交 | 提交脚本、文档、manifest 和统计；较大的 JSONL/CSV 产物保留在本地。 |
| `data/lexicons/ntusd/*_utf8.txt` | 已提交 | `stone_eval.emotion.hedonometer` 使用的 UTF-8 词表。 |
| `data/lexicons/ntusd/*_traditional.txt` | 仅本地 | 原始非 UTF-8 词表文件，在 UTF-8 终端中可能显示为乱码。 |
| `data/processed/chapters/` | 仅本地 | 展开的章节文本，可由源语料重新生成。 |
| `data/processed/constory/` | 仅本地 | 生成的 parquet 输入。 |
| `data/processed/longstoryeval/` | 仅本地 | 生成的 LongStoryEval JSON 输入。 |

## 备注

看起来像乱码的文件主要是 NTUSD 的 `*_traditional.txt` 源文件。运行时使用
`positive_utf8.txt` 和 `negative_utf8.txt`，正常运行不依赖这些非 UTF-8 原始文件。
