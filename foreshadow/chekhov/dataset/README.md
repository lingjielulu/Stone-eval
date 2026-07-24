# 契诃夫语料预处理工作区

这个目录保存契诃夫短篇原始语料和规范化数据产物。预处理代码、设计文档与分析报告
统一放在 `foreshadow/`。

## 目录结构

| 路径 | 用途 |
|---|---|
| `chekhov_short_stories.txt` | 已纳入版本控制的 Project Gutenberg #57333 原始文本。 |
| `processed/stories_all.jsonl` | 所有检测到的故事段，包括重复译本或重复标题。 |
| `processed/stories_canonical.jsonl` | 每个 canonical 标题保留一条记录，默认用于统计。 |
| `processed/stories_all.csv` | 所有故事段的元数据 CSV，不含正文。 |
| `processed/stories_canonical.csv` | canonical 故事的元数据 CSV，不含正文。 |
| `processed/story_catalog.csv` | 201 篇 canonical 小说的中英文标题、类型、主题、摘要和伏笔候选表。 |
| `processed/title_index.csv` | 重复标题索引，以及每个 canonical 标题选中的记录。 |
| `processed/stats.json` | 机器可读的语料统计。 |
| `processed/manifest.json` | 预处理策略、输出清单和审计摘要。 |
| `../scripts/preprocess_chekhov.py` | 基于规则的文本清洗和故事切分脚本。 |
| `../results/` | 数据审计与下游分析报告。 |
| `../docs/chekhov_preprocessing_and_foreshadowing_design.md` | 预处理设计说明和后续伏笔统计方案。 |

## 重新生成

从仓库根目录运行：

```bash
python foreshadow/chekhov/scripts/preprocess_chekhov.py
```

当前规范化输出：

- 检测到 213 个正文故事段。
- 生成 201 条 canonical 故事记录。
- canonical 语料总词数为 845,027。
- 有 16 个目录标题未匹配到正文边界，主要是 Gutenberg 合集中非契诃夫或无独立正文标题的条目。

## 报告分工

| 报告 | 是否提交 | 用途 |
|---|---|---|
| `../results/chekhov_analysis.md` | 是 | 下游分析报告，给人阅读，展示清洗后的篇幅分布、主题词密度和后续伏笔统计入口。 |
| `../results/chekhov_normalized_stats.md` | 是 | 清洗审计报告，给数据处理流程检查，集中记录切分数量、重复标题、未匹配标题和 Top 榜单。 |
