# 短篇小说伏笔系统设计

本文档说明如何把 `Codified Foreshadowing-Payoff Text Generation` 的 CFPG 思路用于 `short-story foreshadow dataset` 中的短篇/中篇小说。设计参考：

- `documentations/Codified Foreshadowing-Payoff Text Generation.pdf`
- `foreshadow/honglou/docs/cfpg_reproduction_design.md`
- `foreshadow/honglou/results/cfpg/`

核心差异是：论文和红楼梦项目主要在 BookSum-style 摘要句时间线上抽取伏笔，因为长篇原文太长；本 benchmark 的文本是短篇/中篇，已经有稳定段落编号，因此第一版应直接在全文段落层处理，不强制先摘要。

## 目标

为当前短篇小说建立一套可复用的伏笔系统，用于三类任务：

1. 从全文中抽取 Foreshadow-Trigger-Payoff 三元组。
2. 将三元组写入现有 `annotations/*.yaml`，作为人工可校验的 gold 或 silver 数据。
3. 支持增量阅读/生成评测：判断伏笔何时仍 pending、何时 trigger 已满足、何时 payoff 应发生或已发生。

输出不是文学赏析，而是可验证的叙事承诺状态：

```text
Foreshadow: 早期 setup，引入未解决叙事债务
Trigger: 使该债务进入可兑现状态的可观察条件
Payoff: 后文具体兑现、解释、反转、否定或主题性回收
```

## 为什么短篇不默认摘要

红楼梦 CFPG 复现链路是：

```text
长篇原文 -> BookSum-style 摘要 -> 摘要句时间线 -> F-P 候选 -> Trigger -> F-T-P 验证
```

这适合章回长篇，因为直接在原文上抽取会遇到窗口过长、引用定位困难、成本过高的问题。

短篇小说的情况不同：

- 每篇通常在几十到数百段之间，全文可以被 LLM 分窗读取。
- 当前 `normalized_texts/*.txt` 已有稳定 `[P0001]` 段落 ID。
- 伏笔往往落在具体词句、物件、声音、空间细节或叙述语气中；摘要会丢失这些信号。
- 现有 `annotations/*.yaml` 已用段落跨度作为 evidence，直接连接全文更容易审查。

因此第一版采用：

```text
normalized full text -> paragraph/event timeline -> F-T-P candidate extraction -> verification -> annotation/update/tracking
```

摘要只作为可选层：

- 对 novella 或长中篇做分段压缩。
- 给人工 review 生成摘要说明。
- 做跨语言对齐时辅助定位，但不作为 gold evidence。

## 输入数据

主要输入：

```text
foreshadow/short_stories/dataset/
  normalized_texts/{story_id}.txt
  normalized_texts_zh/{story_id}.txt
  annotations/{story_id}.yaml
  annotations/candidates/{story_id}_candidates.json
  schemas/story_schema.json
```

文本单位：

- `paragraph_id`: `[P0001]` 等稳定段落编号。
- `event_id`: YAML 中人工事件节点，如 `SB_E03`。
- `span`: 段落范围，如 `P0143-P0158`。

语言策略：

- Gold 标注以原文为主，中文译文可作人工理解和中文模型抽取辅助。
- 若使用中文译文抽取，必须把候选映射回原文段落 ID，不能只保留中文证据。
- 译文来源授权未确认时，仅用于内部标注参考，不作为公开发布正文依据。

## 输出层级

### 1. 全文段落时间线

从 `normalized_texts/{story_id}.txt` 生成机器可读段落表：

```json
{
  "story_id": "speckled_band",
  "paragraph_id": "P0143",
  "paragraph_index": 143,
  "text": "...",
  "section_hint": "inspection",
  "language": "en"
}
```

可选加入中文对齐：

```json
{
  "story_id": "speckled_band",
  "paragraph_id": "P0143",
  "source_text": "...",
  "zh_text": "...",
  "alignment_status": "paragraph_index_matched"
}
```

### 2. 高召回候选层

候选层允许噪声，目标是不要漏掉重要伏笔：

```json
{
  "candidate_id": "speckled_band:ftp_candidate:000001",
  "story_id": "speckled_band",
  "foreshadow_span": "P0143-P0158",
  "payoff_span": "P0243-P0247",
  "foreshadow_text": "...",
  "payoff_text": "...",
  "proposed_trigger": {
    "description": "Holmes waits in the room at night and the signal causes the snake to appear.",
    "observable_conditions": [
      "Holmes and Watson occupy the target room",
      "the whistle/signal is heard",
      "movement at the bell-rope is observed"
    ]
  },
  "foreshadow_type": "spatial",
  "payoff_type": "literal",
  "distance_paragraphs": 85,
  "stage1_confidence": "medium",
  "stage1_rationale": "The ventilator and bell-rope are anomalous household details later used as the delivery path."
}
```

### 3. 验证后的 F-T-P 层

验证层要能直接转写到 `annotations/{story_id}.yaml`：

```json
{
  "id": "SB_F01",
  "story_id": "speckled_band",
  "foreshadow": {
    "text_span": "P0143-P0158",
    "summary": "The bell-rope and ventilator do not serve their apparent functions.",
    "type": "spatial"
  },
  "trigger": {
    "event_id": "SB_E06",
    "description": "Holmes hears the signal, observes the delivery path, and strikes at the bell-pull.",
    "observable_conditions": ["signal heard", "night watch in target room", "creature enters path"]
  },
  "payoff": {
    "event_id": "SB_E07",
    "text_span": "P0243-P0247",
    "summary": "The swamp adder reveals the mechanism."
  },
  "verifier": {
    "setup_validity": true,
    "payoff_validity": true,
    "temporal_separation": true,
    "foreshadow_justification": true,
    "trigger_validity": true,
    "connection_validity": true,
    "rationale": "The room details are unresolved anomalies until the snake mechanism is revealed.",
    "evidence_spans": ["P0143-P0158", "P0237-P0239", "P0243-P0247"]
  }
}
```

### 4. Pending pool / tracking 层

CFPG 的核心不是“找到伏笔”而是维护未兑现承诺池：

```json
{
  "step_paragraph_id": "P0200",
  "active_pool": [
    {
      "triple_id": "SB_F01",
      "status": "pending",
      "trigger_satisfied": false,
      "expected_payoff": "The anomalous room arrangement should be explained by a concrete mechanism."
    }
  ],
  "decision": "hold",
  "rationale": "The night watch has not happened yet."
}
```

用于生成或评测时，每一步只激活 trigger 已满足的 payoff，避免模型过早兑现。

## 处理流程

### Stage 0: 段落和事件准备

输入：

- `normalized_texts/{story_id}.txt`
- 若已有 gold：`annotations/{story_id}.yaml`

步骤：

1. 解析 `[Pxxxx]` 段落。
2. 读取现有 `events`、`causal_edges`、`foreshadowing_units`。
3. 若没有 annotation，先运行弱候选：

```bash
python foreshadow/short_stories/scripts/build_candidates.py {story_id}
```

4. 对没有事件节点的作品，先生成 `event_candidates`，由人工合并成稳定事件。

验收：

- 每段有稳定 ID。
- 每个候选伏笔和 payoff 都能回指段落。
- 如果绑定 `trigger_event_id`/`payoff_event_id`，对应事件必须存在。

### Stage 1: 高召回候选抽取

目标：从全文段落层抽取候选 F-P pair，并要求模型给 provisional trigger。

窗口策略：

- `short`: 全文一次输入。
- `novelette/novella`: 滑动窗口，例如 30 段窗口、10 段重叠。
- 每个窗口携带上一窗口 pending setup 摘要，但 evidence 仍必须来自段落。

候选要求：

- `foreshadow_span` 必须早于 `payoff_span`。
- F 不能是已经即时解决的普通因果。
- P 必须提供新叙事信息，不能只是重复 F。
- 必须输出 proposed trigger；不能描述 trigger 的候选降权。

优先类型：

- `object`: 项链、怀表、发梳、牛奶盘、保险柜。
- `rule`: 极寒环境规则、自然法则、社会仪式。
- `psychological`: 幻听、过度辩解、执念。
- `spatial`: 通风口、地下墓穴、锁链、房间布局。
- `social`: 人血馒头、官僚摊派、阶层压力。
- `symbolic`: 最后一片叶子、花环等。
- `red_herring`: 吉卜赛人、错误解释、伪线索。
- `retrospective`: 结尾反转后才被确认的 setup。

### Stage 2: Payoff alignment verification

目标：过滤主题相似、意象重复、人物再次出现等假连接。

每个候选检查：

1. F 是否引入具体叙事元素或未解决异常。
2. P 是否解决、履行、解释、反转或否定 F。
3. F 和 P 是否有非平凡时间间隔。
4. P 出现后，F 是否能被合理回看为伏笔。
5. T 是否是可观察条件，能解释为什么 payoff 此时发生而不是更早发生。
6. 证据是否足够落在当前文本中，不能依赖外部读者知识硬补。

拒绝条件：

- 只是主题呼应，没有具体兑现。
- 只是同一物件/人物再次出现，没有状态变化。
- 只是普通因果，不形成 delayed commitment。
- Trigger 是抽象词，如“命运展开”“气氛成熟”。
- P 需要未来文本或外部改写才能成立。

### Stage 3: 写入 YAML 标注

已验证候选映射到现有 schema：

```text
foreshadowing_units[].foreshadowing_text_span <- foreshadow_span
foreshadowing_units[].foreshadowing_type      <- foreshadow_type
foreshadowing_units[].trigger_event_id        <- trigger.event_id
foreshadowing_units[].payoff_event_id         <- payoff.event_id
foreshadowing_units[].payoff_text_span        <- payoff_span
foreshadowing_units[].payoff_type             <- payoff_type
```

如果候选只有段落但没有事件：

1. 先创建或复用 `events`。
2. 再绑定 trigger/payoff event。
3. 不允许在 gold YAML 里只写自然语言 trigger 而没有事件 ID。

### Stage 4: 增量 tracking

对每个故事按段落或事件递增扫描：

```text
for paragraph/event step:
  add newly introduced foreshadows to pool
  check trigger conditions for pending triples
  mark selected payoffs as active when trigger is satisfied
  mark resolved if payoff evidence appears
  keep pending if no trigger
  mark violated only when text contradicts or bypasses required payoff
```

状态枚举：

- `not_introduced`: F 尚未出现。
- `pending`: F 已出现，但 T 未满足。
- `triggered`: T 满足，P 应进入可兑现状态。
- `resolved`: P 已发生。
- `violated`: 文本与 F/T/P 约束矛盾。
- `abandoned_or_unresolved`: 文本结束仍未兑现。

## 与当前 10 篇的适配重点

| story_id | 首选抽取模式 | 重点 |
| --- | --- | --- |
| `speckled_band` | 全文/事件辅助 | 物理线索、红鲱鱼、机关回收 |
| `red_headed_league` | 全文/事件辅助 | 荒诞任务作为犯罪计划的功能性 setup |
| `necklace` | 全文 | 物件误认、阶层欲望、长延迟反转 |
| `gift_of_the_magi` | 全文 | 双线牺牲、互相失效的 payoff |
| `last_leaf` | 全文 | 象征物、信念因果、牺牲揭示 |
| `tell_tale_heart` | 全文 | 心理症状、声音意象、罪感触发 |
| `cask_of_amontillado` | 全文 | 空间不可逆、欺骗链、讽刺话语 |
| `to_build_a_fire` | 全文/规则辅助 | 环境规则、物理因果、失败型 payoff |
| `medicine` | 全文/中文原文 | 社会误解、象征回收、负向 payoff |
| `cricket` | 全文/中文原文 | 制度压力、奇幻触发、命运反转 |

## 推荐目录

建议新增：

```text
foreshadow/short_stories/dataset/
  cfpg/
    paragraph_timelines/
    candidates/
    verified/
    tracking/
    reviews/
```

文件命名：

```text
cfpg/paragraph_timelines/{story_id}_paragraphs.jsonl
cfpg/candidates/{story_id}_ftp_candidates_{run_id}.jsonl
cfpg/verified/{story_id}_ftp_verified_{run_id}.jsonl
cfpg/tracking/{story_id}_tracking_{run_id}.jsonl
cfpg/reviews/{story_id}_ftp_review_{run_id}.md
```

`run_id` 建议包含日期、模型和语言，例如：

```text
20260701_deepseek_fulltext_en
20260701_deepseek_fulltext_zh_assisted
```

## 初始实现入口

第一版先把所有短篇 CFPG prompt 放在单独文件：

```text
foreshadow/short_stories/cfpg/prompts/short_story_prompts.md
```

脚本只负责在固定槽位插入故事元信息、段落时间线、中文辅助译文和已有标注上下文：

```text
foreshadow/short_stories/cfpg/scripts/extract_short_story_ftp.py
```

查看 prompt 拼接效果：

```bash
python foreshadow/short_stories/cfpg/scripts/extract_short_story_ftp.py last_leaf \
  --dry-run \
  --max-paragraphs 12 \
  --include-zh \
  --run-id smoke
```

该命令不调用模型，只输出渲染后的 prompt 预览：

```text
foreshadow/short_stories/cfpg/results/extraction/reviews/last_leaf_prompt_preview_smoke.md
```

实际抽取时去掉 `--dry-run`，可按需加入 `--verify` 做候选验证：

```bash
python foreshadow/short_stories/cfpg/scripts/extract_short_story_ftp.py last_leaf \
  --include-zh \
  --run-id 20260701_fulltext_zh_assisted \
  --verify
```

## Prompt 约束

所有 LLM prompt 必须自包含定义，不依赖模型知道论文。

抽取 prompt 必须要求：

- 只使用输入文本。
- 输出 JSON。
- 每条候选必须有段落 span。
- 每条候选必须有 proposed trigger。
- 允许多抽，但必须标 confidence 和 rationale。

验证 prompt 必须要求：

- 逐项判断 setup/payoff/temporal/justification/trigger/connection。
- 给 evidence spans。
- 任一关键项失败就 reject。
- 明确区分真实回收和主题呼应。

tracking prompt 必须要求：

- 只能基于当前 prefix 判断。
- 不允许使用未来 payoff 段落。
- 输出 `pending|triggered|resolved|violated`。

## 评测指标

抽取质量：

- `candidate_recall`: gold F-T-P 中有多少被候选覆盖。
- `verification_precision`: verified candidates 中人工接受比例。
- `span_accuracy`: F/T/P span 是否落在正确段落范围。
- `trigger_validity_rate`: trigger 是否可观察且解释 payoff 时机。

Tracking 质量：

- `correct_detection_rate`: 在 payoff 附近窗口内正确触发。
- `early_trigger_count`: trigger 未满足时提前要求 payoff。
- `late_trigger_count`: payoff 已可见后仍未触发。
- `localization_error`: 预测触发点与 gold payoff/trigger 的距离。
- `unresolved_detection`: 文本结束时能否正确保持未兑现状态。

生成/续写质量：

- `payoff_realization`: 给定 active payoff 后是否生成合理兑现。
- `premature_payoff_suppression`: pending 状态下是否避免提前兑现。
- `constraint_consistency`: 生成 payoff 是否违反原文事实。

## 错误类型

沿用论文和红楼梦复现中的错误 taxonomy，并针对短篇做细化：

- `premature_trigger`: 根据表面词提前触发。
- `thematic_confusion`: 把主题/意象重复误判为 payoff。
- `ordinary_causality`: 普通局部因果被误当伏笔。
- `missed_trigger`: trigger 已满足但系统仍 pending。
- `late_resolution`: payoff 已出现但系统未识别。
- `span_drift`: 找到关系但段落定位偏移。
- `translation_drift`: 中文译文辅助抽取后无法映射回原文。
- `symbolic_overreach`: 把开放隐喻强行验证为具体回收。
- `red_herring_misread`: 没区分误导线索和真实 payoff。

## 实施顺序

### Phase 1: 复用现有 gold 做基线

目标作品：

- `speckled_band`
- `necklace`
- `to_build_a_fire`
- `medicine`
- `cricket`

任务：

1. 从现有 YAML 导出 verified F-T-P JSONL。
2. 写 paragraph timeline builder。
3. 写 tracking evaluator，在 gold 上跑增量状态。
4. 生成 review markdown，人工检查状态转移是否合理。

### Phase 2: 自动抽取补齐未标注 5 篇

目标作品：

- `red_headed_league`
- `gift_of_the_magi`
- `last_leaf`
- `tell_tale_heart`
- `cask_of_amontillado`

任务：

1. 全文段落层抽候选。
2. verifier 过滤。
3. 人工审查后写入 YAML。
4. 运行 `validate_dataset.py`。

### Phase 3: 双语辅助

任务：

1. 使用 `normalized_texts_zh/` 做中文抽取。
2. 将中文候选映射回原文段落。
3. 比较英文/中文抽取差异。
4. 只把有原文 evidence 的候选写入 gold。

### Phase 4: 生成/续写实验

任务：

1. 给定故事前缀和 pending pool，让模型继续写 1-3 段。
2. 在 pending 状态下检查是否过早兑现。
3. 在 triggered 状态下检查是否兑现 active payoff。
4. 对比 baseline prompt、foreshadow-aware prompt、CFPG trigger-gated prompt。

## 关键取舍

- 第一版不要为短篇强制摘要化；摘要会损失伏笔证据。
- 第一版优先 concrete 伏笔：物件、规则、空间、话语、心理异常。
- 象征性伏笔可以保留，但验证标准要更严格。
- Gold YAML 里必须绑定 `trigger_event_id` 和 `payoff_event_id`，这比论文摘要句 pair 更适合当前 benchmark。
- 中文译文可提升人工理解和中文模型召回，但不能替代原文 evidence。
- 自动抽取只生成 silver；进入 benchmark gold 前必须人工复核。
