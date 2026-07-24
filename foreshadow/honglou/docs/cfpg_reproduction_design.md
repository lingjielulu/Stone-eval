# CFPG 伏笔-回收论文复现设计

## 目标

本阶段复现 `Codified Foreshadowing-Payoff Text Generation`，但数据路线不是直接复用
BookSum 英文样本，而是模仿 BookSum 的层级摘要组织方式，先为《红楼梦》构造
BookSum-style 摘要数据，再在摘要层上应用 CFPG 的伏笔-回收抽取方法。

核心目标：

1. 按 BookSum 思路为《红楼梦》前 80 回和续作生成 chapter-level / book-level 摘要。
2. 在摘要句子层面抽取 Foreshadow-Trigger-Payoff 三元组。
3. 将三元组编码为可跟踪的 narrative commitment state。
4. 在原文和续作的增量阅读场景下判断 payoff 是否应当触发、是否过早、是否遗漏。
5. 最终形成《红楼梦》续作的伏笔兑现评价维度。

本设计基于本地材料：

- 论文 PDF：`documentations/Codified Foreshadowing-Payoff Text Generation.pdf`
- BookSum PDF：`documentations/BOOKSUM.pdf`
- 本地 BookSum 项目：`../booksum`，用于参考数据组织和 alignment 设计
- 当前 Stone-eval 已处理语料：
  - `resources/corpora/hongloumeng/prepared/longstoryeval/original/books_json/红楼梦前80回.json`
  - `resources/corpora/hongloumeng/prepared/longstoryeval/continuations/books_json/*.json`

## 论文要点

CFPG 将长叙事一致性中的“伏笔兑现”形式化为显式因果承诺，而不是依赖模型隐式记忆。

核心对象是 F-T-P 三元组：

- Foreshadow: 早期设置、异常、对象、承诺或规则，形成尚未解决的叙事债务。
- Trigger: 使伏笔进入可兑现状态的叙事条件。
- Payoff: 具体、可观察的事件、解释或揭示，用来清偿 Foreshadow 引入的承诺。

核心循环是：

1. 维护未兑现伏笔池 `C = {(F, T, P)}`。
2. 对当前上下文 `X_t` 检查每个 `T` 是否满足。
3. 只把触发条件满足的 payoff 注入生成或判断过程。
4. 生成/阅读新文本后，更新伏笔池：移除已兑现项，加入新伏笔。

论文数据构造基于 BookSum 的人写摘要，先抽取候选句对，再做 payoff 对齐验证和 rubric 过滤。最终数据规模为 148 本书、629 个 validated foreshadow-payoff pairs。论文的关键评估包含：

- Oracle timing 下的 payoff activation。
- 增量上下文下的 grounded payoff tracking。
- 错误类型归因：过早触发、主题混淆、延迟触发、状态丢失、间接链接失败等。

## BookSum 在本地的作用

`../booksum` 在本阶段不是主要实验语料，而是格式和流程参照。需要借鉴的是它如何把长篇文学作品组织成可摘要、可对齐的数据：

- 章节级 summary alignment：
  - `../booksum/alignments/chapter-level-summary-alignments/*.jsonl`
- 书级 summary alignment：
  - `../booksum/alignments/book-level-summary-alignments/*.jsonl`
- 章节文本和摘要文件：
  - `../booksum/all_chapterized_books/*`
  - `../booksum/finished_summaries/*`

BookSum 本身不是伏笔标注数据集。对本项目更关键的是：

1. 使用 BookSum 的 chapter-level / book-level 摘要粒度，避免直接在完整长文本上抽伏笔。
2. 为《红楼梦》建立类似 `source_text -> human/LLM summary -> sentence-level alignment` 的中间层。
3. 在这个中间层上运行 CFPG 的候选抽取、验证和 tracking。

因此第一阶段产物应是《红楼梦》的 BookSum-style 摘要数据，而不是 BookSum 英文样本的 smoke 结果。

## 仓库位置规划

### 代码

新增包：

```text
stone_eval/foreshadow/
├── __init__.py
├── schema.py        # F/T/P、候选句对、验证结果、tracking decision 数据结构
├── booksum_ref.py   # 读取 ../booksum 样例，作为格式参照和调试样本
├── honglou.py       # 读取红楼梦原文、续作和已处理 book JSON
├── summarize.py     # 生成 BookSum-style chapter/book summaries
├── segment.py       # summary/chapter sentence segmentation
├── extraction.py    # Stage 1: LLM 候选 Foreshadow-Payoff 抽取
├── verifier.py      # Stage 2/3: alignment verification + rubric filtering
├── tracker.py       # Foreshadow pool、trigger gate、state update
├── metrics.py       # detection rate、early/late、localization error、continuation score
└── prompts.py       # 所有 LLM prompt 模板集中管理
```

CLI 放在 `stone_eval/cli.py`，命令前缀统一为 `cfpg-*`：

```text
stone-eval cfpg-build-honglou-summary-inputs
stone-eval cfpg-summarize-honglou
stone-eval cfpg-align-summary
stone-eval cfpg-extract-candidates
stone-eval cfpg-verify-candidates
stone-eval cfpg-track
stone-eval cfpg-evaluate
```

批处理脚本：

```text
scripts/run_cfpg_honglou_summary.sh
scripts/run_cfpg_honglou.sh
```

### 数据

BookSum 原仓库保持只读，不纳入本仓库版本管理。Stone-eval 保存《红楼梦》的摘要输入、摘要结果、中间三元组和实验输出。

```text
foreshadow/honglou/results/cfpg/
├── honglou_booksum/
│   ├── original_80_chapter_inputs.jsonl
│   ├── original_80_chapter_summaries.jsonl
│   ├── original_80_book_summary.json
│   ├── continuation_chapter_inputs.jsonl
│   ├── continuation_chapter_summaries.jsonl
│   ├── continuation_book_summaries.jsonl
│   └── manifest.json
├── summary_alignments/
│   ├── original_80_summary_sentence_alignment.jsonl
│   └── continuation_summary_sentence_alignment.jsonl
├── candidates/
│   └── honglou_candidates_<run_id>.jsonl
├── verified/
│   └── honglou_ftp_triples_<run_id>.jsonl
└── honglou/
    ├── original_80_ftp_triples_<run_id>.jsonl
    └── continuation_payoff_checks_<run_id>.jsonl
```

### 输出

所有新复现实验输出放在：

```text
foreshadow/honglou/results/cfpg_reports/<run_id>/
├── config.json
├── extraction_report.json
├── verification_report.json
├── tracking_metrics.json
├── tracking_decisions.jsonl
├── error_taxonomy.json
└── samples/
```

其中 `<run_id>` 建议使用 `YYYYMMDD_model_dataset_stage`，例如：

```text
foreshadow/honglou/results/cfpg_reports/20260611_deepseek_honglou_summary/
foreshadow/honglou/results/cfpg_reports/20260611_deepseek_honglou_original80/
```

### 文档

```text
foreshadow/honglou/docs/cfpg_reproduction_design.md       # 本文件
documentations/cfpg_experiment_log.md            # 后续记录每次 run 的结论
documentations/cfpg_honglou_summary_protocol.md  # 后续记录红楼梦摘要规范
```

### Prompt 模板

实际被代码读取的 prompt 模板独立放在：

```text
foreshadow/honglou/prompts/honglou_prompts.md
```

脚本通过 `--prompt-file` 按需读取，默认使用这个文件。修改 prompt 时只改模板文件，并同步更新其中的 `version`，避免同一 run 中混用不可追踪的 prompt。

## 数据结构

### BookSum-style chapter summary

```json
{
  "id": "honglou:original_80:chapter_001",
  "dataset": "honglou",
  "book_id": "红楼梦前80回",
  "book_kind": "original",
  "chapter_index": 1,
  "chapter_title": "...",
  "source_text_path": "resources/corpora/hongloumeng/prepared/chapters/original/chapter_001.txt",
  "source_text": "...",
  "summary": "...",
  "summary_sentences": [
    {
      "sentence_index": 0,
      "text": "...",
      "source_span_hint": "chapter_001"
    }
  ],
  "model": "deepseek-v4-pro",
  "prompt_version": "honglou_booksum_chapter_v1"
}
```

### Summary sentence timeline

CFPG 论文的数据构造单位是摘要句子：先从句子序列 `X = (s1, ..., sT)` 中找出早期 setup 句 `s_tf` 和后续 payoff 句 `s_tp`。因此《红楼梦》摘要不能只按“第几回”粗粒度处理，需要先把各回摘要展平成全书级句子时间线：

```json
{
  "global_sentence_index": 42,
  "chapter_index": 5,
  "chapter_sentence_index": 3,
  "book_id": "红楼梦前80回",
  "text": "...",
  "source_summary_id": "honglou:original_80:chapter_005",
  "source_text_path": "resources/corpora/hongloumeng/prepared/chapters/original/chapter_005.txt"
}
```

后续候选抽取和验证统一使用 `global_sentence_index`，回号和回内句号用于人工审查。

### Candidate Foreshadow-Payoff pair

论文 Stage 1 是高召回候选识别，不直接等同最终 F-T-P。我们先保存候选 F-P 句对，同时让模型给一个 provisional trigger，后续通过 verifier 固化：

```json
{
  "candidate_id": "honglou:original_80:candidate:000001",
  "book_id": "红楼梦前80回",
  "summary_source": "original_80_chapter_summaries.jsonl",
  "foreshadow_sentence_index": 1,
  "payoff_sentence_index": 14,
  "foreshadow_text": "...",
  "payoff_text": "...",
  "proposed_trigger": {
    "description": "...",
    "observable_conditions": ["..."]
  },
  "relation_description": "...",
  "foreshadow_type": "object|event|speech_act|rule|symbol|dream|poem|identity",
  "distance_sentences": 13,
  "distance_chapters": 4,
  "stage1_confidence": 0.0,
  "stage1_rationale": "..."
}
```

### F-T-P triple

```json
{
  "id": "honglou:original_80:<local_id>",
  "dataset": "honglou",
  "book_id": "红楼梦前80回",
  "book_title": "红楼梦前80回",
  "source": "llm_booksum_style_summary",
  "summary_path": "foreshadow/honglou/results/cfpg/honglou_booksum/original_80_chapter_summaries.jsonl",
  "summary_text": "...",
  "foreshadow": {
    "global_sentence_index": 12,
    "chapter_index": 1,
    "chapter_sentence_index": 4,
    "text": "...",
    "description": "...",
    "type": "object|event|speech_act|rule|symbol|dream|poem|identity"
  },
  "trigger": {
    "description": "...",
    "observable_conditions": ["..."]
  },
  "payoff": {
    "global_sentence_index": 34,
    "chapter_index": 5,
    "chapter_sentence_index": 2,
    "text": "...",
    "description": "..."
  },
  "distance_sentences": 22,
  "confidence": 0.0,
  "verifier": {
    "setup_validity": true,
    "payoff_validity": true,
    "temporal_separation": true,
    "foreshadow_justification": true,
    "trigger_validity": true,
    "connection_validity": true,
    "rationale": "...",
    "evidence": [
      {"sentence_index": 12, "text": "..."},
      {"sentence_index": 34, "text": "..."}
    ]
  }
}
```

### Incremental tracking decision

```json
{
  "triple_id": "...",
  "step_sentence_index": 31,
  "gold_payoff_index": 34,
  "decision": "pending|should_payoff|resolved|violated",
  "confidence": 0.0,
  "trigger_satisfied": false,
  "evidence": ["..."],
  "predicted_payoff": "...",
  "error_type": null
}
```

## 复现阶段

### Phase 1: 《红楼梦》BookSum-style 摘要层

目的：模仿 BookSum，为《红楼梦》生成稳定、可复查、可逐句定位的摘要层。CFPG 不直接在完整章回文本上抽取，而是在这个摘要层上抽取长程叙事依赖。

输入：

- 原文前 80 回：
  - `resources/corpora/hongloumeng/prepared/longstoryeval/original/books_json/红楼梦前80回.json`
  - `resources/corpora/hongloumeng/prepared/chapters/original/*.txt`
- 续作：
  - `resources/corpora/hongloumeng/prepared/longstoryeval/continuations/books_json/*.json`
  - `resources/corpora/hongloumeng/prepared/chapters/continuations/*/*.txt`

摘要层级：

- chapter-level summary：每回一个摘要，保留关键人物、事件、未解释异常、承诺、梦境/诗词/判词。
- book-level summary：将 chapter summaries 汇总成全书情节轨迹。
- optional section-level summary：按 5 或 10 回聚合，用于减少跨章节 tracking 成本。

产物：

- `foreshadow/honglou/results/cfpg/honglou_booksum/original_80_chapter_inputs.jsonl`
- `foreshadow/honglou/results/cfpg/honglou_booksum/original_80_chapter_summaries.jsonl`
- `foreshadow/honglou/results/cfpg/honglou_booksum/original_80_book_summary.json`
- `foreshadow/honglou/results/cfpg/honglou_booksum/continuation_chapter_summaries.jsonl`
- `foreshadow/honglou/results/cfpg/honglou_booksum/continuation_book_summaries.jsonl`

验收：

- 每条 summary 有稳定 `id`、章节索引、模型信息和 prompt version。
- summary 被切成句子并保留 `sentence_index`。
- 摘要显式保留可能的伏笔材料，而不是只写主线剧情。
- 前 6 回调试已完成；当前扩展到原文前 80 回，人工检查摘要是否适合抽 F-T-P。

### Phase 2: 从《红楼梦》摘要层抽取 F-T-P 三元组

目的：在 HongLou BookSum-style 摘要上复现论文的数据构造方法。

论文方法对应关系：

- 论文输入：BookSum human-written hierarchical abstractive summaries。
- 本项目输入：LLM 生成但人工可审查的 HongLou BookSum-style chapter/book summaries。
- 论文目标：从摘要句子序列中恢复 `(s_tf, s_tp)`，其中 `s_tf` 引入具体叙事条件，`s_tp` 后续解决该条件。
- 本项目目标：先恢复 F-P 句对，再补全可观察 Trigger，形成正式 F-T-P。

#### Step 0: 构造摘要句子时间线

输入 `original_80_chapter_summaries*.jsonl`，把每回 `summary_sentences` 展平成全书句子表：

```text
foreshadow/honglou/results/cfpg/summary_alignments/original_80_summary_sentence_timeline_<run_id>.jsonl
```

每句保留 `global_sentence_index`、`chapter_index`、`chapter_sentence_index`、`text`、`source_summary_id` 和 `source_text_path`。

#### Stage 1: Sentence-Level Candidate Identification

目标：高召回抽取候选 Foreshadow-Payoff 句对。论文明确这一阶段优先 recall，允许 weak/noisy candidates，后续再过滤。

输入：

- 摘要句子时间线。
- 每回摘要中的 `unresolved_setups`、`foreshadow_notes`、`poem_dream_prophecy_objects` 作为候选提示，但不直接当 gold。

候选规则：

- F 必须是早于 P 的摘要句：`payoff_sentence_index > foreshadow_sentence_index`。
- F/P 距离至少 2 个 summary sentences；同句或相邻句的普通即时因果先排除。
- F 类型优先：object、event、speech_act、rule、identity、dream、poem。
- symbol 类型允许输出，但默认低置信，后续需严格验证。
- 模型必须给 `proposed_trigger`：说明什么可观察条件使 payoff 在该位置变得合理。若无法描述 trigger，候选降权或拒绝。

窗口策略：

- 前 80 回：按 10 回滑动窗口处理，重叠 2 回；窗口之间 carry pending setups，避免跨窗口伏笔丢失。

输出：

```text
foreshadow/honglou/results/cfpg/candidates/honglou_candidates_<run_id>.jsonl
foreshadow/honglou/results/cfpg_reports/<run_id>/candidate_extraction_report.json
```

#### Stage 2: Payoff Alignment Verification

目标：过滤主题呼应、意象重复、人物再次出现等非因果关联。论文做法是检查 payoff 句附近窗口是否真正构成 setup 句附近窗口的 causal/narrative resolution。

对每个 candidate 构造两个 context window：

- setup window：`tf - 2` 到 `tf + 2`。
- payoff window：`tp - 2` 到 `tp + 2`。

验证问题：

1. payoff 是否提供新的叙事信息？
2. payoff 是否解决、履行、解释或回顾性重释 setup？
3. 二者是否只是主题相似、词语重复、同一人物再次出现？
4. proposed trigger 是否能解释为什么 payoff 应在此处发生，而不是更早发生？

输出：

```json
{
  "candidate_id": "...",
  "accepted_stage2": true,
  "connection_validity": true,
  "is_thematic_echo_only": false,
  "is_unsupported_by_evidence": false,
  "trigger_supported": true,
  "rationale": "...",
  "evidence_sentence_indices": [12, 13, 34]
}
```

#### Stage 3: Rubric-Based Filtering

目标：按论文四项 rubric 做严格过滤。论文要求两个独立 verifier 都接受才保留；本项目分调试和正式两档。

调试：

- DeepSeek 抽取。
- DeepSeek verifier 过滤。
- 人工抽查 Markdown review。

正式：

- DeepSeek 或同类中文强模型抽取。
- 另一个强模型或第二 verifier prompt 做交叉验证。
- 两个 verifier 均通过才写入 verified triples。

论文四项 rubric：

1. Setup Validity：F 引入具体叙事元素，如物件、行动、规则、决定、身份线索；且在引入时未完全解释或解决。
2. Payoff Validity：P 提供新的叙事信息，能履行、解决或重释 F；不是简单重复。
3. Temporal Separation：F 与 P 在不同句子，且有非平凡间隔；排除即时因果。
4. Foreshadow Justification：读到 P 后，F 能被合理回看为伏笔；读到 F 当下仍是欠解释或待履行的 setup。

本项目额外加一项：

5. Trigger Validity：T 是可观察叙事条件，不是抽象主题词；它能解释 payoff 的时机，避免 premature payoff。

#### Stage 4: 输出 verified triples 和 review

accepted candidates 转成正式 F-T-P triple；rejected candidates 保留 rejection reason 便于调 prompt。

产物：

- `foreshadow/honglou/results/cfpg/candidates/honglou_candidates_<run_id>.jsonl`
- `foreshadow/honglou/results/cfpg/verified/honglou_ftp_triples_<run_id>.jsonl`
- `foreshadow/honglou/results/cfpg/verified/honglou_rejected_candidates_<run_id>.jsonl`
- `foreshadow/honglou/results/cfpg/verified/honglou_ftp_triples_<run_id>.review.md`
- `foreshadow/honglou/results/cfpg_reports/<run_id>/extraction_report.json`
- `foreshadow/honglou/results/cfpg_reports/<run_id>/verification_report.json`

验收：

- 每个候选必须绑定摘要句子索引。
- 每个 verified triple 必须有 F/T/P 三部分，不能只有 F-P。
- Trigger 必须是可观察条件，例如“身份被确认”“物件用途被揭示”“承诺被要求履行”，不能只是“命运展开”“气氛变化”。
- verifier 必须给证据句，不允许只给文学评论。
- verified triple 必须通过论文四项 rubric；正式 run 还要通过 Trigger Validity。
- 第一版优先保守抽取 object/event/rule/speech-act 类型，symbol 类型单独标记为低置信。

### Phase 3: 复现论文核心评估

目的：在《红楼梦》摘要层上复现论文的两个核心实验小规模版本。

实验 A：Oracle timing payoff activation

- 在 gold payoff 前截断 summary。
- baseline prompt 只给上下文。
- CFPG prompt 给 F-T-P state 和已满足 trigger。
- 用 entailment judge 判断生成是否兑现 gold payoff。

实验 B：Grounded payoff tracking

- 逐句喂入 summary prefix。
- 每一步判断 trigger 是否满足、是否应当 payoff。
- 与 gold payoff sentence index 比较。

指标：

- Correct Detection Rate，容忍窗口先使用论文的 `±3 sentences`。
- Early Triggers。
- Late Triggers。
- Localization Error。
- Continuation Score：生成内容与 gold payoff 的 narrative entailment 分数。

### Phase 4: 错误类型归因

目的：复现论文的错误 taxonomy，并为《红楼梦》续作评价做准备。

错误类型先采用论文 taxonomy：

- premature_trigger: 过早触发。
- thematic_confusion: 主题/事件相似但不是目标 payoff。
- deferred_not_yet_observable: 长间隔中误以为已经解决。
- state_failure: 忘记或错误更新叙事状态。
- conservative_late: 触发过晚。
- indirect_link_failure: 间接或回顾式兑现没有被链接。

输出：

- `foreshadow/honglou/results/cfpg_reports/<run_id>/error_taxonomy.json`
- `foreshadow/honglou/results/cfpg_reports/<run_id>/samples/*.json`

### Phase 5: 续作伏笔兑现评价

目的：用前 80 回抽出的 pending / extendable F-T-P pool，评价各续作如何兑现、误兑现或遗漏伏笔。

输入：

- 原文摘要三元组：`foreshadow/honglou/results/cfpg/verified/honglou_ftp_triples_<run_id>.jsonl`
- 续作 BookSum-style summaries：`foreshadow/honglou/results/cfpg/honglou_booksum/continuation_*`

评价类别：

- resolved: 续作给出合理 payoff。
- unresolved: 伏笔延续但未兑现。
- missing: 伏笔被忽略。
- premature: 未满足 trigger 就强行兑现。
- contradictory: payoff 与原伏笔或原著状态矛盾。
- alternative_payoff: 续作给出另一种可辩护兑现。

中文化注意点：

- 伏笔可能来自判词、诗词、灯谜、梦境、物件、人物话语、制度规则。
- Trigger 不一定是显性事件，可能是人物命运转折或家族状态变化。
- Payoff 需要区分“命运谶语解释”和“可观察情节兑现”，第一版只保守处理可观察情节兑现。

## Prompt 设计边界

第一版所有 LLM prompt 必须输出 JSON，且强制包含证据句索引，避免只给文学评论式解释。

Prompt 不能依赖“你是某论文的数据构造员/verifier”这类角色设定，因为模型未必知道该论文，且即使知道也可能混入外部记忆。所有抽取和验证 prompt 必须自包含定义：

- F/T/P 三个术语的操作化含义。
- 当前步骤是“候选抽取”还是“严格验证”。
- 输入材料的边界：只能使用 summary sentence timeline 和 notes。
- notes 的用途：可作为辅助证据，但 F/P 的索引必须锚定到摘要句。
- 判词、诗词、梦境可以作为伏笔来源；如果给定范围内没有后续 payoff，只能保留为 pending setup，不能硬凑 verified triple。
- reject 条件：主题呼应、意象重复、人物再次出现、外部知识补全、摘要窗口中缺少具体 payoff 证据。

摘要 prompt 必须保留伏笔候选：

- 不只写主线剧情。
- 显式列出未解释的异常、承诺、梦境、诗词、判词、物件、人物话语。
- 不提前解释后文信息；每回摘要只能基于当前回内容。

抽取 prompt 只做高召回：

- 输入 summary sentence timeline + 每回 notes。
- 输出多个候选 F-P pair，同时给 provisional trigger。
- 每个 pair 必须有 `foreshadow_sentence_index` 和 `payoff_sentence_index`。
- 不要求此阶段高精度；宁可多抽，后面 verifier 过滤。

验证 prompt 做高精度：

- 判断 setup validity、payoff validity、temporal separation、foreshadow justification。
- 额外判断 trigger validity。
- 任一项失败则 reject。
- 要求引用原句索引作为 evidence。
- 必须区分“主题呼应/意象重复”和“真实因果回收”。

tracking prompt 做二分类/四分类：

- 当前 prefix 下，trigger 是否满足。
- payoff 是否应该现在发生。
- 当前句是否已经 resolved。
- 不允许根据未来内容推断。

## 与现有模块的关系

- `stone_eval.consistency` 负责 ConStory-Bench 一致性错误分类。
- `stone_eval.quality` 负责 NovelCritique/LongStoryEval 风格整体质量。
- `stone_eval.emotion` 负责情感曲线。
- 新增 `stone_eval.foreshadow` 专注两件事：BookSum-style 摘要层生成，以及伏笔-回收结构抽取/评价。

不要把 CFPG 逻辑塞进 `stone_eval.longstory.py`。LongStoryEval/BookSum 是数据来源和辅助摘要格式，CFPG 是独立评价维度。

## 风险和取舍

- 论文代码链接指向 `https://github.com/LongfeiYun17/CFPG`，当前本地还没有该项目。第一版根据论文和本地 BookSum 复现机制，后续如果需要可再拉取原仓库对齐实现细节。
- 论文使用 GPT-4.1 做候选抽取，本地复现可先使用 `.env` 中 OpenAI-compatible judge model，记录 model/base URL。
- BookSum 是格式参照，不是主数据。不要把英文 BookSum smoke 当成本阶段主线。
- 摘要质量决定 F-T-P 抽取上限。摘要 prompt 必须专门保留伏笔候选，否则普通剧情摘要会把伏笔信息压缩掉。
- 伏笔抽取成本高，必须支持 resume、run_id 和逐条 JSONL 输出。
- 自动抽取会漏掉象征性/隐喻性伏笔。第一版优先保守处理 object/event/rule/speech-act 类型。

## 下一步执行清单

1. 新建 `stone_eval/foreshadow/` 包和 schema。
2. 实现《红楼梦》chapter input builder，生成 `foreshadow/honglou/results/cfpg/honglou_booksum/*inputs.jsonl`。
3. 写 BookSum-style chapter summary prompt；前 6 回 smoke 已完成并删除产物。
4. 人工检查摘要是否保留伏笔候选，必要时调整 prompt。
5. 生成前 80 回 BookSum-style 摘要层和人类可读 review。
6. 写 Stage 1 candidate extraction prompt 和 JSONL writer。
7. 写 Stage 2/3 verifier prompt，产出 validated triples。
8. 写 incremental tracker 和 metrics。
9. 记录并维护 prompts 到 `foreshadow/honglou/prompts/honglou_prompts.md`。
10. 再扩展到 15 部续作。
