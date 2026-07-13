# CFPG 短篇原文复现

本目录复现 *Codified Foreshadowing-Payoff Text Generation*（Yun et al., 2026）的两项核心实验，数据源改为 `novels/normalized_texts` 中的短篇小说原文，不经过 BookSum 或任何摘要模型。

## 目录结构

```text
cfpg_short_story/
├── prompts/   # 全流程 Prompt 模板
├── scripts/   # 抽取、案例准备、实验运行与报告生成
├── data/      # 句级案例和修订后的伏笔分类
├── results/   # 抽取结果、Oracle smoke test 与后续生成结果
└── reports/   # Markdown 报告、渲染 HTML 和可视化前端
```

阅读入口：[可视化前端](reports/dashboard.html) · [渲染实验报告](reports/experiment_report.html) · [Markdown 报告](reports/experiment_report.md)。以下命令均从仓库根目录执行。

## 复现范围

论文方法被映射为以下流程：

1. 从短篇全文抽取并验证 Foreshadow–Trigger–Payoff（F–T–P）三元组。
2. 将带段落 ID 的原文切为稳定的 `P####S###` 句级时间线；原段落 ID 始终保留。
3. Oracle timing：在 gold payoff 句之前截断，比较无控制 `prompt` 与显式 F–T–P 控制 `cfpg` 的一句续写。
4. Grounded tracking：只向模型逐句暴露前缀，比较：
   - `fap`：自然语言 Foreshadow-Aware Prompt；
   - `fscr`：按词汇 Jaccard 相似度取回旧句，再拼接最近窗口；
   - `cfpg`：显式 F–T–P 谓词和 trigger gate。
5. LLM judge 按 entailment / neutral / contradiction 记为 1.0 / 0.5 / 0.0，并汇总论文附录 B 的指标。

论文指标与实现字段对应如下：

| 论文指标 | `summary.json` 字段 |
| --- | --- |
| Should-Payoff Rate | `oracle.*.should_payoff_rate` |
| Avg. Score | `oracle.*.average_score` |
| Correct Detection Rate (±3 句) | `tracking.*.correct_detection_rate` |
| Early / Late Triggers | `tracking.*.early_triggers` / `late_triggers` |
| Localization Error | `tracking.*.localization_error` |
| Continuation Fidelity | `tracking.*.continuation_fidelity` |

Oracle 的 `prompt.should_payoff_rate` 为 `null`，与论文表 1 的 “—” 一致；只有带 codify gate 的 CFPG 方法产生 activation decision。

## 数据准备

当前仓库已有一次 10 篇核心短篇的候选抽取与验证结果。将其中 25 个 accepted triples 转为句级实验案例：

```bash
python data/foreshadow_causality_benchmark/experiments/cfpg_short_story/scripts/prepare_short_story_cfpg.py
```

默认输出：

```text
data/foreshadow_causality_benchmark/experiments/cfpg_short_story/data/cfpg_cases.jsonl
```

每个案例同时保存 F/T/P、句级 gold anchor、完整句级时间线和源文件路径。Payoff anchor 在候选 payoff 段落范围内，以 payoff 描述和原句的词汇重合度确定；因此它是可重复的弱对齐，不是人工句级 gold。

现有 30 条候选的修订分类和中文 F/T/P 说明位于 `data/cfpg_taxonomy_v2.json`。新版把伏笔的文本承载形式记录为 `primary_type`，把误导、警告、反讽和回顾性重释记录为独立的 `narrative_function`；`red_herring` 不再是主类型。

如需从原文重新抽取，必须避免 gold 泄漏：不要传 `--include-existing-annotations`，也不要把中文译文作为原文证据。例如：

```bash
python data/foreshadow_causality_benchmark/experiments/cfpg_short_story/scripts/extract_short_story_ftp.py medicine \
  --verify \
  --max-candidates 8 \
  --out-dir data/foreshadow_causality_benchmark/experiments/cfpg_short_story/results/extraction \
  --run-id clean_source_v1
```

## 运行实验

先查看调用规模，不请求 API：

```bash
python data/foreshadow_causality_benchmark/experiments/cfpg_short_story/scripts/run_short_story_cfpg.py \
  --dry-run
```

最小 smoke test：

```bash
python data/foreshadow_causality_benchmark/experiments/cfpg_short_story/scripts/run_short_story_cfpg.py \
  --experiment oracle \
  --story-id cricket \
  --max-cases 1 \
  --run-id oracle_smoke
```

完整论文口径（在线阶段逐句扫描，调用量很大）：

```bash
python data/foreshadow_causality_benchmark/experiments/cfpg_short_story/scripts/run_short_story_cfpg.py \
  --experiment all \
  --stride 1 \
  --run-id full_sentence_level
```

低成本调试可使用 `--stride 5`、`--max-cases` 或重复的 `--story-id`。`--stride 1` 才是论文的逐句在线设定。脚本按 `case_id + model + method` 自动跳过已有结果，可使用同一 `run-id` 断点续跑。

模型和 API 默认从 `.env` 的 `JUDGE_MODEL`、`OPENAI_API_KEY`、`OPENAI_BASE_URL` 读取，也可使用 `--model`、`--judge-model`、`--api-key`、`--api-base` 覆盖。

## 与论文的已知差异

- 输入从 BookSum 长篇摘要改为短篇原文，这是本复现的目标改动。原文含对话、描写和局部事件，噪声显著高于摘要。
- 原数据的 gold 是句级；本数据最初以段落 span 抽取，再做确定性句级弱对齐，建议最终由人工复核 `anchor_segment_id`。
- 论文没有公开完整 prompts、随机种子、verifier 型号和 FSCR 检索细节；论文中给出的 GitHub 地址在 2026-07-13 检查时返回 404。本实现把所有 prompts 固定在 `prompts/short_story_prompts.md`，并将 FSCR 明确定义为 Jaccard 检索，便于审计。
- 仓库现有的 `20260701_short_story_cfpg_v3_verified` 抽取曾使用中文辅助译文，且部分作品插入 seed annotation context；它适合打通流程，但不是无泄漏的最终论文结果。正式报告应使用上面的 clean-source 重跑结果替换它。
- 论文的 attention saliency 分析依赖开源模型内部注意力，本 API 复现不覆盖该机制分析。
- 当前作品大多是经典公版小说，模型可能记忆原文；oracle 续写结果会同时受到训练数据污染影响。正式比较应报告逐作品结果，并另建未公开短篇或改写版测试集做抗记忆验证。
- 默认生成模型与 judge 可能相同，适合流程验证但可能产生 self-judge 偏差。正式实验应通过 `--judge-model` 使用独立模型，并对随机样本做人评。

因此，当前实现属于“论文方法和指标复现”，不宣称对原作者未公开代码进行逐行或数值复现。
