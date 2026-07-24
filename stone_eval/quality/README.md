# 长篇叙事质量评测

本模块保存 NovelCritique 风格的评价标准，以及 LongStoryEval 摘要和评价适配代码。

当前只完成了：

- `critique.py` 中的评价维度和 prompt 数据结构；
- `stone_eval.longstory` 中的摘要、评价与 OpenAI-compatible 调用封装；
- `resources/corpora/hongloumeng/prepared/longstoryeval/` 输入格式准备。

尚未发现正式 LongStoryEval 运行结果，因此不建立空置结果或实验目录。后续结果
默认写入 `stone_eval/quality/results/longstoryeval/`。
