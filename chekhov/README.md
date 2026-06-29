# 契诃夫语料工作区

这个目录是契诃夫短篇语料项目的人类可读入口。

## 目录结构

| 路径 | 用途 |
|---|---|
| `chekhov_short_stories.txt` | 已纳入版本控制的 Project Gutenberg #57333 原始文本，是预处理脚本的默认输入。 |
| `chekhov_analysis.md` | 下游可视化分析报告，由规范化清洗结果生成。 |

## 相关数据流水线

可复现的数据预处理流水线位于 `data/chekhov/`：

- `data/chekhov/scripts/preprocess_chekhov.py`
- `data/chekhov/processed/stats.json`
- `data/chekhov/processed/manifest.json`
- `data/chekhov/reports/chekhov_normalized_stats.md`
- `data/chekhov/docs/chekhov_preprocessing_and_foreshadowing_design.md`

从仓库根目录重新生成：

```bash
python data/chekhov/scripts/preprocess_chekhov.py
```

## 报告分工

目前保留两类报告：

| 报告 | 定位 |
|---|---|
| `chekhov/chekhov_analysis.md` | 面向阅读和展示的下游分析报告，包含可视化表格、主题词密度和伏笔统计的后续字段建议。 |
| `data/chekhov/reports/chekhov_normalized_stats.md` | 面向数据审计的清洗统计报告，只记录切分数量、篇幅桶、最长/最短篇、重复标题和未匹配目录项。 |
