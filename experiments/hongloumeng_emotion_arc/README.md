# 《红楼梦》情感弧线实验

对《红楼梦》前 80 回进行滑动窗口情感评分，并比较词典与模型评分方案。

## 内容

- `resources/lexicons/ntusd/`：项目级公共 NTUSD 词表。
- `scripts/plot_smoothed_emotion_arc.py`：平滑、峰谷提取和绘图。
- `runs/baselines_202606/`：2026 年 6 月完成的 NTUSD 与 DeepSeek 基线。
- `emotion_scoring_schemes.md`：两种评分方案及运行参数。
- `references/`：Emotion Arcs 论文，本地保留。

默认输入是共享语料中的
`resources/corpora/hongloumeng/prepared/longstoryeval/original/books_json/红楼梦前80回.json`。

新运行写入 `runs/current/`；历史基线不应被覆盖。
