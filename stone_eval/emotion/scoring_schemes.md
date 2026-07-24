# 情感弧线打分方案

## 方案一：词典 / Hedonometer

- CLI：`python -m stone_eval.cli emotion-arc`
- 输出标识：`method = Reagan et al. 2016 inspired sliding-window emotional arc`
- 当前主词典：NTUSD，也可使用内置小词典或自定义正负词典。
- 计算方式：滑动窗口内情绪词命中后按词频加权平均，输出 1-9 分。
- 优点：快、可复现、成本低、适合全量和多续作批量比较。
- 限制：依赖词典命中，古典文本语义、反讽、上下文会被弱化。

## 方案二：模型打分

- CLI：`python -m stone_eval.cli emotion-arc-model`
- 输出标识：`scheme = model_score`
- LLM 后端：`scorer_type = llm`
- 本地模型后端：`scorer_type = local_model`
- 默认 LLM 配置来源：`.env` 中的 `OPENAI_API_KEY`、`OPENAI_BASE_URL`、`EMOTION_MODEL` 或 `JUDGE_MODEL`。
- 计算方式：对每个滑动窗口调用模型，要求模型结合叙事情境、人物情绪、事件走向和气氛输出 1-9 分。
- 优点：能利用上下文，不只依赖情绪词。
- 限制：慢、有 API 成本、结果受模型和 prompt 影响；需要记录 prompt 版本和模型名。

推荐快速命令：

```bash
python -m stone_eval.cli emotion-arc-model \
  --model-backend llm \
  --points 80 \
  --window-size 5000 \
  --output stone_eval/emotion/results/hongloumeng_baselines_202606/model_score/original_80_deepseek_arc.json \
  --concurrent 1
```

推荐更细命令：

```bash
python -m stone_eval.cli emotion-arc-model \
  --model-backend llm \
  --points 160 \
  --window-size 5000 \
  --output stone_eval/emotion/results/hongloumeng_baselines_202606/model_score/original_80_deepseek_arc_160p.json \
  --concurrent 1
```

本地快速基线：

```bash
python -m stone_eval.cli emotion-arc-model \
  --model-backend snownlp \
  --points 100 \
  --window-size 10000 \
  --output stone_eval/emotion/results/hongloumeng_baselines_202606/model_score/original_80_snownlp_arc.json
```

## 开源替代方案定位

- `cnsenti`：中文情感分析库，默认使用知网正负情感词典和大连理工七类情绪词典；项目已停止维护，功能合并到 `cntext`。它属于词典/规则方案，不作为方案二主实现。
- `cntext`：中文社会科学文本分析库，包含词频、情感分析、语义投影、词向量和 LLM/Ollama 工具。适合作为后续本地词典/嵌入扩展，但如果使用其传统情感模块，应归到方案一或“词典扩展”，不要混入模型打分。
- `SnowNLP`：本地模型/朴素贝叶斯风格情感工具，速度快、无需 API；当前作为方案二的 `local_model` 基线，但在《红楼梦》上有整体偏高和波动偏大的风险。

## 隔离原则

- 词典方案输出保留在 `stone_eval/emotion/results/hongloumeng_baselines_202606/` 或 `stone_eval/emotion/results/hongloumeng_baselines_202606/lexicon/`。
- 模型方案输出保留在 `stone_eval/emotion/results/hongloumeng_baselines_202606/model_score/`。
- 每个输出必须记录 `scheme`、`scorer_type`、`model` 或 `lexicon`、`points`、`window_size`、`prompt_version`。
- 不把 NTUSD、SnowNLP、DeepSeek 的分数直接混合平均；只能并列画图或做相关性/稳健性比较。
