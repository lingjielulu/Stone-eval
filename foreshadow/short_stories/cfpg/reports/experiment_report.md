# CFPG 短篇小说原文复现实验报告

## 1. 实验概览

本实验在 `foreshadow/short_stories/dataset` 的短篇小说数据上复现 *Codified Foreshadowing-Payoff Text Generation*（CFPG）。与论文使用 BookSum 长篇小说摘要不同，本实验不生成摘要，直接以带段落编号的短篇原文作为输入。

截至 2026-07-13，已完成：

1. 核心 10 篇短篇的 F–T–P 候选抽取与单模型 verifier；
2. 25 条 accepted triples 的句级实验数据转换；
3. Oracle Timing 的单案例 API smoke test；
4. 完整 Oracle Timing 与 Grounded Tracking 实验代码、prompt 和指标实现。

尚未完成全量 25 案例的生成实验和逐句在线追踪，因此本报告不会将 smoke test 外推为完整性能结论。

> **复现状态结论：尚未完全复现论文。** 当前已经复现数据结构、候选抽取、单 verifier、句级适配、Oracle/Tracking 代码和论文指标；只实际运行了全量抽取与 1 个 Oracle 案例。双独立 verifier、全量 Oracle、全量逐句 Tracking、人工评测和 attention saliency 尚未完成。

可视化浏览入口：[打开 CFPG 实验前端](dashboard.html)。

网页渲染版：[阅读排版后的 HTML 报告](experiment_report.html)；源文件：[查看原始 Markdown](experiment_report.md)。

## 2. 结果存储位置

| 内容 | 路径 |
| --- | --- |
| 抽取汇总 | [summary.json](../results/extraction/runs/20260701_short_story_cfpg_v3_verified/summary.json) |
| Accepted triples | [accepted triples JSONL](../results/extraction/runs/20260701_short_story_cfpg_v3_verified/accepted_triples_20260701_short_story_cfpg_v3_verified.jsonl) |
| Rejected candidates | [rejected candidates JSONL](../results/extraction/runs/20260701_short_story_cfpg_v3_verified/rejected_candidates_20260701_short_story_cfpg_v3_verified.jsonl) |
| 原抽取报告 | [short_story_cfpg_report.md](../results/extraction/runs/20260701_short_story_cfpg_v3_verified/short_story_cfpg_report.md) |
| 句级复现实验集 | [cfpg_cases.jsonl](../data/cfpg_cases.jsonl) |
| Oracle smoke 原始结果 | [oracle.jsonl](../results/oracle_smoke_20260713/oracle.jsonl) |
| Oracle smoke 汇总 | [summary.json](../results/oracle_smoke_20260713/summary.json) |
| 权威 Prompt 文件 | [short_story_prompts.md](../prompts/short_story_prompts.md) |
| 新分类与中文说明 | [cfpg_taxonomy_v2.json](../data/cfpg_taxonomy_v2.json) |
| 可视化前端 | [dashboard.html](dashboard.html) |
| Markdown 渲染页 | [experiment_report.html](experiment_report.html) |
| 前端生成脚本 | [render_cfpg_report_frontend.py](../scripts/render_cfpg_report_frontend.py) |

## 3. 数据与方法

### 3.1 数据

实验覆盖以下 10 篇核心作品：

| story_id | 作品 | 原文 | 结果审阅 |
| --- | --- | --- | --- |
| `speckled_band` | The Adventure of the Speckled Band / 斑点带子案 | [source](../../dataset/normalized_texts/speckled_band.txt) | [review](../results/extraction/runs/20260701_short_story_cfpg_v3_verified/reviews/speckled_band_ftp_review_20260701_short_story_cfpg_v3_verified.md) |
| `red_headed_league` | The Red-Headed League / 红发会 | [source](../../dataset/normalized_texts/red_headed_league.txt) | [review](../results/extraction/runs/20260701_short_story_cfpg_v3_verified/reviews/red_headed_league_ftp_review_20260701_short_story_cfpg_v3_verified.md) |
| `necklace` | The Diamond Necklace / 项链 | [source](../../dataset/normalized_texts/necklace.txt) | [review](../results/extraction/runs/20260701_short_story_cfpg_v3_verified/reviews/necklace_ftp_review_20260701_short_story_cfpg_v3_verified.md) |
| `gift_of_the_magi` | The Gift of the Magi / 麦琪的礼物 | [source](../../dataset/normalized_texts/gift_of_the_magi.txt) | [review](../results/extraction/runs/20260701_short_story_cfpg_v3_verified/reviews/gift_of_the_magi_ftp_review_20260701_short_story_cfpg_v3_verified.md) |
| `last_leaf` | The Last Leaf / 最后一片叶子 | [source](../../dataset/normalized_texts/last_leaf.txt) | [review](../results/extraction/runs/20260701_short_story_cfpg_v3_verified/reviews/last_leaf_ftp_review_20260701_short_story_cfpg_v3_verified.md) |
| `tell_tale_heart` | The Tell-Tale Heart / 泄密的心 | [source](../../dataset/normalized_texts/tell_tale_heart.txt) | [review](../results/extraction/runs/20260701_short_story_cfpg_v3_verified/reviews/tell_tale_heart_ftp_review_20260701_short_story_cfpg_v3_verified.md) |
| `cask_of_amontillado` | The Cask of Amontillado / 一桶白葡萄酒 | [source](../../dataset/normalized_texts/cask_of_amontillado.txt) | [review](../results/extraction/runs/20260701_short_story_cfpg_v3_verified/reviews/cask_of_amontillado_ftp_review_20260701_short_story_cfpg_v3_verified.md) |
| `to_build_a_fire` | To Build a Fire / 生火 | [source](../../dataset/normalized_texts/to_build_a_fire.txt) | [review](../results/extraction/runs/20260701_short_story_cfpg_v3_verified/reviews/to_build_a_fire_ftp_review_20260701_short_story_cfpg_v3_verified.md) |
| `medicine` | 鲁迅《药》 | [source](../../dataset/normalized_texts/medicine.txt) | [review](../results/extraction/runs/20260701_short_story_cfpg_v3_verified/reviews/medicine_ftp_review_20260701_short_story_cfpg_v3_verified.md) |
| `cricket` | 蒲松龄《促织》 | [source](../../dataset/normalized_texts/cricket.txt) | [review](../results/extraction/runs/20260701_short_story_cfpg_v3_verified/reviews/cricket_ftp_review_20260701_short_story_cfpg_v3_verified.md) |

输入使用 `dataset/normalized_texts/*.txt`。每个原文段落具有 `P####` ID；句级转换进一步生成 `P####S###` ID，既满足论文的逐句实验设定，也保留回溯原文证据的能力。

中文覆盖已经核对完毕：8 篇英译中文本位于 `dataset/normalized_texts_zh`，《药》和《促织》本身使用中文原文，因此核心 10 篇均有中文版本。历史抽取 JSON 保留原始语言，`cfpg_taxonomy_v2.json` 为全部 30 条候选提供中文 F/T/P 说明；本报告和前端的统计、分类和案例说明以中文层为准。

### 3.2 F–T–P 定义

- Foreshadow（F）：较早出现、当时尚未完全解释或解决的具体叙事元素。
- Trigger（T）：使伏笔进入可回收状态的可观察条件。
- Payoff（P）：在后文履行、解释、反转或重新解释 F 的具体事件。

### 3.3 生成实验

Oracle Timing 在 gold payoff 句之前截断原文：

- `prompt`：不加入显式因果控制，直接续写一句；
- `cfpg`：先运行 codify gate 判断 trigger，再将结构化 F–T–P 作为控制条件续写一句。

Grounded Tracking 逐句暴露原文前缀：

- `fap`：提供自然语言形式的未解决伏笔；
- `fscr`：检索与伏笔词汇相似的旧句，并与最近上下文拼接；
- `cfpg`：维护显式 F–T–P 状态，通过 trigger gate 决定何时回收。

### 3.4 指标

- Should-Payoff Rate：Oracle 位置上 CFPG gate 的激活率；普通 Prompt 不适用。
- Average Score：生成句相对真实轨迹的 narrative entailment 得分，取值为 1.0、0.5 或 0.0。
- Correct Detection Rate：在线预测位置位于 gold payoff 的 ±3 句内的比例。
- Early/Late Triggers：早于或晚于容忍窗口的触发数量。
- Localization Error：预测位置与 gold payoff 位置的平均绝对句距。
- Continuation Fidelity：正确触发后，生成续写与真实叙事轨迹的一致性。

### 3.5 实际流程、提示词和各阶段产物

| 流程 | Prompt key / version | 给模型的核心要求 | 当前结果 |
| --- | --- | --- | --- |
| Stage 1 候选抽取 | 历史结果：`short_story_ftp_extraction_v2`；当前模板：`short_story_ftp_extraction_v3` | 阅读全文段落时间线；输出 F/P span、可观察 Trigger、互斥主类型、独立叙事功能、置信度和理由；只输出 JSON | 历史 run 为 10 篇各 3 条，共 30 条；已用 taxonomy v2 重新归类 |
| Stage 2/3 严格验证 | `short_story_candidate_verification` / `short_story_ftp_verification_v1` | 按 setup、payoff、时间间隔、伏笔合理性、trigger、连接有效性六项 rubric 判断；任一关键项失败即拒绝 | 接受 25，拒绝 5 |
| 句级适配 | 无 Prompt | 确定性切句为 `P####S###`，在 F/P 段落范围内用词汇重合选择 anchor | 25 条句级案例 |
| FAP 在线决策 | `short_story_fap_decision` / `short_story_fap_decision_v1` | 只给自然语言未解决伏笔和当前前缀，判断下一句是否应 payoff | 代码完成，全量未运行 |
| FSCR 在线决策 | 同 FAP prompt | 先以 Jaccard 相似度检索旧句，再加最近窗口；不提供显式 T/P | 代码完成，全量未运行 |
| CFPG Gate | `short_story_cfpg_decision` / `short_story_cfpg_decision_v1` | 输入结构化 F/T/P，逐项检查可观察 trigger 条件，输出 `should_payoff` | 1 个 Oracle 案例已运行并正确触发 |
| 条件续写 | `short_story_continuation` / `short_story_continuation_v1` | 维持原文语言、时态、视角，只续写一句；CFPG 激活时必须自然实现 payoff | Prompt 与 CFPG 各生成 1 条 |
| 轨迹评判 | `short_story_continuation_judge` / `short_story_continuation_judge_v1` | 将生成句和 gold 下一句判为 entailment / neutral / contradiction，对应 1/0.5/0 | 两条 smoke 续写均为 1.0 |

实际 Prompt 全文可在 [short_story_prompts.md](../prompts/short_story_prompts.md) 或[可视化前端的“提示词”区域](dashboard.html)展开查看。核心差异如下：

```text
FAP:  未解决的伏笔 + 当前前缀 → “下一句是否已经到了应当兑现该伏笔的时机？”
FSCR: 与 FAP 相同，但当前上下文 = 相似旧句 + 最近窗口
CFPG: {Foreshadow, Trigger.observable_conditions, Payoff, status} + 当前前缀
      → 逐项检查 trigger，并显式输出 should_payoff
```

Candidate extraction 的关键限制是“F/P 必须有非平凡间隔、Trigger 必须可观察、不能只是主题呼应”；verifier 的拒绝原则是“任一关键 rubric 失败即 `accepted=false`”。这两条提示词直接决定了下文 25/5 的筛选结果。

## 4. F–T–P 抽取结果

### 4.1 总体结果

| 阶段 | 输入 | 输出 | 比例 |
| --- | ---: | ---: | ---: |
| 短篇作品 | 10 | 10 | 100% |
| Candidate extraction | 10 篇全文 | 30 条候选 | 每篇 3 条 |
| Verifier | 30 条候选 | 25 条接受 | 83.33% |
| Rejected | 30 条候选 | 5 条拒绝 | 16.67% |

25 条 accepted triples 的 F–P 平均距离为 43.08 个段落，中位数为 25，最小值为 4，最大值为 174。这说明该数据确实包含跨较长文本区间的叙事依赖，而不只是相邻段落中的普通因果关系。

### 4.2 分作品结果

| story_id | candidates | accepted | rejected | 接受率 |
| --- | ---: | ---: | ---: | ---: |
| `speckled_band` | 3 | 1 | 2 | 33.33% |
| `red_headed_league` | 3 | 3 | 0 | 100% |
| `necklace` | 3 | 2 | 1 | 66.67% |
| `gift_of_the_magi` | 3 | 2 | 1 | 66.67% |
| `last_leaf` | 3 | 3 | 0 | 100% |
| `tell_tale_heart` | 3 | 3 | 0 | 100% |
| `cask_of_amontillado` | 3 | 3 | 0 | 100% |
| `to_build_a_fire` | 3 | 3 | 0 | 100% |
| `medicine` | 3 | 2 | 1 | 66.67% |
| `cricket` | 3 | 3 | 0 | 100% |
| **合计** | **30** | **25** | **5** | **83.33%** |

### 4.3 重新组织后的类型分布

旧版把 `object / psychological / spatial / red_herring / retrospective` 放在同一字段，混淆了文本承载形式、语义领域和叙事功能。新版先按“伏笔是什么形式的文本证据”确定互斥主类型，再单独标记叙事功能。逐条复核结果保存在 [cfpg_taxonomy_v2.json](../data/cfpg_taxonomy_v2.json)。

| 伏笔主类型 | 定义 | accepted | 占比 |
| --- | --- | ---: | ---: |
| `character_state` 人物状态 | 持续的心理、身体、身份、欲望或行为状态 | 6 | 24% |
| `dialogue` 对话/言语 | 人物说出的描述、警告、承诺或内心引语 | 6 | 24% |
| `object` 物件 | 具体物件或可辨识实体 | 4 | 16% |
| `rule` 规则 | 自然、社会、制度或人物奉行的明确原则 | 3 | 12% |
| `environment_description` 环境描写 | 空间、天气、地貌或环境危险 | 3 | 12% |
| `event` 事件 | 已发生的行动、变化或感知事件 | 2 | 8% |
| `narrator_commentary` 叙述者评论 | 叙述者直接给出的预告或元叙事判断 | 1 | 4% |

| 独立叙事功能 | accepted | 占比 |
| --- | ---: | ---: |
| `retrospective_reinterpretation` 回顾性重释 | 6 | 24% |
| `direct_setup` 直接铺垫 | 5 | 20% |
| `misdirection` 误导 | 4 | 16% |
| `ironic_contrast` 反讽对照 | 3 | 12% |
| `warning` 警告 | 3 | 12% |
| `anomaly` 反常细节 | 2 | 8% |
| `symbolic_reframing` 象征性重构 | 2 | 8% |

`red_herring` 已被删除为主类型，原来两条相关候选现在分别归类为：

- 《斑点带子案》遗言：主类型 `dialogue`，叙事功能 `misdirection`；
- 《麦琪的礼物》德拉的祈祷：主类型 `dialogue`，叙事功能 `misdirection`。

| Payoff 类型 | accepted | 占比 |
| --- | ---: | ---: |
| `literal` 直接兑现 | 10 | 40% |
| `delayed_revelation` 延迟揭示 | 5 | 20% |
| `ironic` 反讽回收 | 5 | 20% |
| `symbolic` 象征回收 | 4 | 16% |
| `misdirection` 误导揭示 | 1 | 4% |

对话/言语与人物状态各占 24%，说明短篇原文中的伏笔经常依附人物话语和持续状态，而不只是具体物件。环境描写被单列为 12%，对应《最后一片叶子》的砖墙与藤蔓、《生火》的暗泉雪地和《药》的丁字街刑场。literal payoff 占 40%；象征性 payoff 仍只占 16%。

### 4.4 伏笔跨度分布

| F–P 距离 | 数量 | 占比 |
| --- | ---: | ---: |
| 4–10 段 | 7 | 28% |
| 11–25 段 | 6 | 24% |
| 26–50 段 | 5 | 20% |
| 51–100 段 | 5 | 20% |
| 101–174 段 | 2 | 8% |

13/25（52%）的伏笔在 25 段以内回收，7/25（28%）跨越超过 50 段。最长两条都来自《红发会》：严格到岗规则到骗局解释跨 129 段；助手低薪、钻地窖到隧道阴谋解释跨 174 段。因不同作品的段落粒度不同，这里的“段落距离”适合在本数据内部排序，不宜直接等价于论文的句子距离。

### 4.5 典型通过案例

#### A. 《斑点带子案》：假铃绳与通风口 → 蛇的杀人通道

- ID：`speckled_band:ftp_candidate:000002`
- F：`P0143-P0158`，Holmes 发现铃绳没有连接电线，通风口也反常地通向隔壁房间。
- T：隔壁房间出现保险箱、牛奶碟、通风口下的椅子和打成圈的鞭子，构成“存在受训动物”的可观察条件。
- P：`P0237-P0238`，蛇经通风口和铃绳下到床边，Holmes 用手杖击打铃绳。
- 跨度：94 段。
- 通过原因：P 直接解释了 F 中两个反常物件的功能，是明确的因果清偿，而非物件再次出现。
- 原始文件：[原文](../../dataset/normalized_texts/speckled_band.txt) · [候选 JSONL](../results/extraction/runs/20260701_short_story_cfpg_v3_verified/candidates/speckled_band_ftp_candidates_20260701_short_story_cfpg_v3_verified.jsonl) · [verifier JSONL](../results/extraction/runs/20260701_short_story_cfpg_v3_verified/verified/speckled_band_ftp_verified_20260701_short_story_cfpg_v3_verified.jsonl) · [review](../results/extraction/runs/20260701_short_story_cfpg_v3_verified/reviews/speckled_band_ftp_review_20260701_short_story_cfpg_v3_verified.md)

#### B. 《项链》：被当作钻石的项链 → 赝品揭示

- ID：`necklace:ftp_candidate:000001`
- F：`P0046-P0048`，Mathilde 看到项链时把它当成昂贵钻石，并产生强烈欲望。
- T：舞会后项链丢失，夫妻借债购买真钻石项链归还。
- P：`P0122`，Forestier 说明原项链只是价值五百法郎的赝品。
- 跨度：76 段。
- 通过原因：结尾提供新信息，反向改写前文对物件价值的理解，并解释十年债务为何成为讽刺性悲剧。
- 原始文件：[原文](../../dataset/normalized_texts/necklace.txt) · [候选 JSONL](../results/extraction/runs/20260701_short_story_cfpg_v3_verified/candidates/necklace_ftp_candidates_20260701_short_story_cfpg_v3_verified.jsonl) · [verifier JSONL](../results/extraction/runs/20260701_short_story_cfpg_v3_verified/verified/necklace_ftp_verified_20260701_short_story_cfpg_v3_verified.jsonl) · [review](../results/extraction/runs/20260701_short_story_cfpg_v3_verified/reviews/necklace_ftp_review_20260701_short_story_cfpg_v3_verified.md)

#### C. 《药》：夏瑜被当作“疯子” → 坟上花圈

- ID：`medicine:ftp_candidate:000002`
- F：茶馆谈论夏瑜被处决、劝牢头造反却被众人误解。
- T：清明时夏四奶奶来到夏瑜坟前，并发现红白花圈。
- P：花圈表明仍有人纪念夏瑜，回收其是否完全被社会遗忘的悬置。
- 跨度：22 段；类型为 `symbolic`。
- 通过原因：花圈是可观察物件，并非抽象主题判断；它对前文“被所有人误解”的状态提供了具体反证。
- 原始文件：[原文](../../dataset/normalized_texts/medicine.txt) · [候选 JSONL](../results/extraction/runs/20260701_short_story_cfpg_v3_verified/candidates/medicine_ftp_candidates_20260701_short_story_cfpg_v3_verified.jsonl) · [verifier JSONL](../results/extraction/runs/20260701_short_story_cfpg_v3_verified/verified/medicine_ftp_verified_20260701_short_story_cfpg_v3_verified.jsonl) · [review](../results/extraction/runs/20260701_short_story_cfpg_v3_verified/reviews/medicine_ftp_review_20260701_short_story_cfpg_v3_verified.md)

#### D. 《促织》：儿子失魂与异虫 → “身化促织”

- ID：`cricket:ftp_candidate:000002`
- F：`P0004-P0005`，儿子投井后复苏但神气痴木，同时出现异常小促织。
- T：小促织先后斗败强虫和鸡，表现出超常行为。
- P：`P0008`，儿子恢复后自述“身化促织，轻捷善斗”。
- 跨度：4 段。
- 通过原因：最终自述直接解释“失魂”和异虫的超常表现，是最紧凑的延迟揭示案例。
- 原始文件：[原文](../../dataset/normalized_texts/cricket.txt) · [候选 JSONL](../results/extraction/runs/20260701_short_story_cfpg_v3_verified/candidates/cricket_ftp_candidates_20260701_short_story_cfpg_v3_verified.jsonl) · [verifier JSONL](../results/extraction/runs/20260701_short_story_cfpg_v3_verified/verified/cricket_ftp_verified_20260701_short_story_cfpg_v3_verified.jsonl) · [review](../results/extraction/runs/20260701_short_story_cfpg_v3_verified/reviews/cricket_ftp_review_20260701_short_story_cfpg_v3_verified.md)

### 4.6 典型拒绝案例

#### A. 《斑点带子案》：“speckled band”遗言 → 蛇

- ID：`speckled_band:ftp_candidate:000001`。
- 表面上是合理伏笔：Julia 的遗言最终由斑点蛇解释。
- 拒绝原因：候选给出的 Trigger 证据不在 verifier 接收到的 setup/payoff 窗口中，`trigger_validity=false`。
- 分析：这是典型的 **span/window 假阴性**，并不意味着文学关系不存在，而是当前证据窗口不足。这说明 verifier 结果尚不能直接当作人工 gold。
- 原始文件：[rejected aggregate](../results/extraction/runs/20260701_short_story_cfpg_v3_verified/rejected_candidates_20260701_short_story_cfpg_v3_verified.jsonl) · [作品 verifier](../results/extraction/runs/20260701_short_story_cfpg_v3_verified/verified/speckled_band_ftp_verified_20260701_short_story_cfpg_v3_verified.jsonl) · [review](../results/extraction/runs/20260701_short_story_cfpg_v3_verified/reviews/speckled_band_ftp_review_20260701_short_story_cfpg_v3_verified.md)

#### B. 《麦琪的礼物》：两件珍宝 → 两份失效礼物

- ID：`gift_of_the_magi:ftp_candidate:000001`。
- F 是 Jim 的金表和 Della 的长发；P 应是两人分别卖掉珍宝购买表链和发梳。
- 拒绝原因：候选 payoff window 没有覆盖“Jim 卖掉手表”这一关键事实，无法在给定证据内验证完整互换结构。
- 分析：同样属于证据 span 不完整造成的拒绝，提示后续应允许 verifier 请求扩窗或修正 span，而不是立即删除候选。
- 原始文件：[作品候选](../results/extraction/runs/20260701_short_story_cfpg_v3_verified/candidates/gift_of_the_magi_ftp_candidates_20260701_short_story_cfpg_v3_verified.jsonl) · [作品 verifier](../results/extraction/runs/20260701_short_story_cfpg_v3_verified/verified/gift_of_the_magi_ftp_verified_20260701_short_story_cfpg_v3_verified.jsonl) · [review](../results/extraction/runs/20260701_short_story_cfpg_v3_verified/reviews/gift_of_the_magi_ftp_review_20260701_short_story_cfpg_v3_verified.md)

#### C. 《药》：人血馒头能治病 → 小栓之墓

- ID：`medicine:ftp_candidate:000001`。
- F 是把人血馒头视作治病“药”；P 是清明墓地场景证明小栓已经死亡。
- 拒绝原因：候选 Trigger 只描述小栓继续咳嗽，不能充分解释为什么此时进入墓地 payoff，`trigger_validity=false`。
- 分析：这里暴露了论文 F–T–P 定义在既定文学文本上的难点：读者能确认 F/P，但“触发 payoff 时机”的最小可观察条件未必在原文中显式存在。
- 原始文件：[作品候选](../results/extraction/runs/20260701_short_story_cfpg_v3_verified/candidates/medicine_ftp_candidates_20260701_short_story_cfpg_v3_verified.jsonl) · [作品 verifier](../results/extraction/runs/20260701_short_story_cfpg_v3_verified/verified/medicine_ftp_verified_20260701_short_story_cfpg_v3_verified.jsonl) · [review](../results/extraction/runs/20260701_short_story_cfpg_v3_verified/reviews/medicine_ftp_review_20260701_short_story_cfpg_v3_verified.md)

## 5. Oracle Timing Smoke Test

### 5.1 配置

| 参数 | 值 |
| --- | --- |
| run_id | `oracle_smoke_20260713` |
| 作品 | `cricket`（《促织》） |
| case | `cricket:ftp_candidate:000001` |
| 生成模型 | `deepseek-v4-pro` |
| judge 模型 | `deepseek-v4-pro` |
| 方法 | `prompt`, `cfpg` |
| gold anchor | `P0009S001` |

该案例的 F 是宫廷喜好促织造成地方层层压榨，T 是成名献上异虫后获得奖赏并改变命运，P 是“异史氏曰”对制度传导和个人命运荒谬性的总结。

### 5.2 结果

| 方法 | Should-Payoff Rate | Average Score |
| --- | ---: | ---: |
| `prompt` | 不适用 | 1.0 |
| `cfpg` | 1.0 | 1.0 |

CFPG gate 判断 trigger 已满足，置信度为 1.0，并正确指出 P0008 中赏成、进上、入邑庠和家道暴富等证据。Prompt 与 CFPG 均生成了与真实下一句同轨迹的内容，因此 entailment 得分都是 1.0。

这个结果只能说明端到端链路能够运行，不能证明 CFPG 优于 Prompt。该作品是经典公版文本，两个方法都几乎复现了原句，存在明显的模型训练数据记忆风险。此外，生成模型和 judge 相同，会带来 self-judge 偏差。

### 5.3 两种方法的实际输出示例

Gold anchor `P0009S001`：

> 異史氏曰：「天子偶用一物，未必不過此已忘；而奉行者即為定例。」

无控制 Prompt 生成：

> 異史氏曰：「天子偶用一物，未必不過此已忘；而奉行者即為定例，加以官貪吏虐，民日貼婦賣兒，更無休止。」

CFPG 先输出 gate 决策：`should_payoff=true`、`trigger_satisfied=true`、`confidence=1.0`。随后生成的一句是：

> 异史氏曰：“天子偶用一物，未必不过此已忘；而奉行者即为定例。

两者都蕴含 gold 句的关键轨迹，judge 因此均给 1.0。CFPG 的原始模型响应实际继续生成了后续评论，但实验代码按论文“一句 continuation”口径截取第一句进行评判。完整响应、gate evidence 和 judge rationale 见 [oracle.jsonl](../results/oracle_smoke_20260713/oracle.jsonl)。

## 6. 与原论文的结果比较

### 6.1 数据规模与跨度

| 项目 | 原论文 | 本实验 | 是否可直接比较 |
| --- | ---: | ---: | --- |
| 输入 | BookSum 长篇摘要 | 短篇小说原文 | 否，原文噪声和文体信息更多 |
| 作品数 | 148 books | 10 stories | 可比较规模，不可比较质量 |
| Validated F–P | 629 | 25 | 本实验还是单 verifier bootstrap |
| 平均跨度 | 20.9 句 | 43.08 段 | 否，单位和段落粒度不同 |
| 中位跨度 | 13 句 | 25 段 | 否 |
| 最大跨度 | 230 句 | 174 段 | 否 |
| Object foreshadow | 48.2% | 16% | 类型体系不同；本实验从原文中另分人物状态、环境描写和叙述者评论 |

本实验的 25 条不是论文 629 条数据的等价子集。最明显的变化是：摘要将事件压缩成少量句子，而原文中的同一伏笔可能跨过大量对话和描写段落。因此 43.08 段不能被解释为“比论文 20.9 句更长一倍”，只能说明短篇原文版确实形成了长距离测试案例。

### 6.2 Oracle Timing 效果

| 数据 / Base model | Prompt Avg. Score | CFPG Should-Payoff | CFPG Avg. Score | CFPG 相对 Prompt 增量 |
| --- | ---: | ---: | ---: | ---: |
| Paper / GPT-4.1-mini | 0.569 | 1.000 | 0.911 | +0.342 |
| Paper / Claude-Haiku-4.5 | 0.657 | 0.965 | 0.940 | +0.283 |
| Paper / Qwen2.5-3B | 0.481 | 0.998 | 0.781 | +0.300 |
| Paper / Qwen2.5-7B | 0.517 | 1.000 | 0.797 | +0.280 |
| Paper / Qwen2.5-14B | 0.583 | 1.000 | 0.898 | +0.315 |
| Paper / Llama-3.1-8B | 0.530 | 1.000 | 0.802 | +0.272 |
| **本实验 / DeepSeek V4 Pro / 1 case** | **1.000** | **1.000** | **1.000** | **0.000** |

论文在六个模型上都观察到 CFPG 相对 Prompt 提升 0.272–0.342。本实验 smoke case 没有观察到提升，因为 Prompt 已经准确续写经典原文，形成 ceiling effect。样本数只有 1，置信区间和统计显著性都没有意义。因此当前结果既不能复现论文的提升幅度，也不能反驳论文结论。

### 6.3 Grounded Tracking 效果

论文 GPT-4.1-mini 的核心结果如下；本实验对应流程尚未实际运行：

| 方法 | Correct Detection | Early | Late | Localization Error | Fidelity |
| --- | ---: | ---: | ---: | ---: | ---: |
| Paper FAP | 58.0% | 235 | 17 | 8.85 | 0.453 |
| Paper FSCR | 48.6% | 306 | 7 | 13.05 | 0.382 |
| Paper CFPG | 69.8% | 166 | 11 | 5.76 | 0.647 |
| 本实验 FAP | 未运行 | 未运行 | 未运行 | 未运行 | 未运行 |
| 本实验 FSCR | 未运行 | 未运行 | 未运行 | 未运行 | 未运行 |
| 本实验 CFPG | 未运行 | 未运行 | 未运行 | 未运行 | 未运行 |

论文中 CFPG 相对 FAP 的主要改善是检测率 +11.8 个百分点、Early Trigger 减少 69、Localization Error 降低 3.09、Fidelity 提升约 0.194（论文表格标注为 +0.221，与表中显示值的直接相减不一致）。本实验只有在跑完约 10,098 次逐句 decision 后才能检查短篇原文上是否保留这些趋势。

### 6.4 是否已经完全复现论文

| 论文组成 | 当前状态 | 证据或缺口 |
| --- | --- | --- |
| F–T–P 表示 | 已复现 | 25 条句级案例保留 F/T/P 和证据 span |
| 从文本抽取候选 | 已复现但有改动 | 直接读原文；30 条候选 |
| Payoff alignment verification | 部分复现 | 单 verifier；论文是 symbolic gate + 两个独立 rubric verifier |
| Oracle Timing 代码 | 已复现 | Prompt/CFPG/gate/generation/judge 均已实现 |
| Oracle Timing 全量结果 | **未复现** | 仅 1/25 案例 |
| FAP / FSCR / CFPG Tracking 代码 | 已复现 | 三种方法和论文指标均已实现 |
| Grounded Tracking 全量结果 | **未复现** | 尚未运行 |
| Error attribution taxonomy | **未复现** | 需要先获得全量错误案例 |
| Attention causal saliency | **未复现** | API 模型不提供内部 attention |
| 双人质量检查 | **未复现** | 当前没有 100 条双人标注 |

所以准确说法是：**已经完成论文方法的工程适配和 F–T–P 数据抽取，尚未完成论文实验结果的全量复现。**

### 6.5 为什么 Oracle 显示“当前 1 / 25”

这里的“未完成”指的是 **全量结果尚未执行**，不是 Oracle 代码没有实现。需要区分四个层次：

| 层次 | Oracle 当前状态 | 含义 |
| --- | --- | --- |
| 方法设计 | 已完成 | 已实现论文的 payoff 前截断、Prompt baseline、CFPG gate 和显式 payoff 控制 |
| 程序实现 | 已完成 | `run_short_story_cfpg.py --experiment oracle` 可以遍历全部案例并断点续跑 |
| 小规模验证 | 已完成 | 《促织》1 条案例已真实调用 API，生成、judge 和汇总均成功 |
| 全量实验结果 | **未完成** | 25 条中只运行 1 条，另外 24 条没有生成结果 |

25 条 F–T–P 案例已经全部准备在 [cfpg_cases.jsonl](../data/cfpg_cases.jsonl)。每个案例需要运行：

1. Prompt baseline 生成一次；
2. Prompt continuation judge 一次；
3. CFPG gate 判断一次；
4. CFPG 条件生成一次；
5. CFPG continuation judge 一次。

因此完整 Oracle 是 `25 × 5 = 125` 次模型调用，最终 `oracle.jsonl` 应包含 `25 × 2 = 50` 条方法结果。目前 [oracle.jsonl](../results/oracle_smoke_20260713/oracle.jsonl) 只有 2 行，即同一条《促织》案例的 Prompt 和 CFPG 结果；所以前端显示 `1 / 25`。

当时没有直接启动剩余 24 条，原因是：

- 先用 1 条案例检查 API 兼容性和 token 配置；第一次 smoke 确实发现无控制生成正文为空，需要提高 completion budget；
- 全量调用会产生实际 API 成本，应在模型、judge 和预算确定后运行；
- 现有经典小说存在模型背诵风险，且旧抽取分类和 annotation leakage 尚需先修正；
- 单案例已经足够验证工程链路，但不足以形成论文效果结论。

全量 Oracle 的完成标准是：Prompt 和 CFPG 各有 25 条结果、CFPG 有 25 次 gate 决策、所有 50 条 continuation 都有 judge 输出，汇总表中两种方法的 `cases` 都等于 25。修正分类不会改变 F/P anchor，因此可以在当前 `taxonomy_v2` 和中文统计更新后继续执行。

Grounded Tracking 的情况不同：代码也已实现，但逐句扫描的最坏上限约为 10,098 次 decision，再加触发后的生成和 judge，运行成本远高于 Oracle。因此它当前属于“代码完成、全量结果未执行”。

## 7. 当前结论

1. 短篇原文可以直接用于 CFPG，不需要先压缩为摘要；稳定的段落和句级 ID 足以支持 F–T–P 证据定位。
2. 已抽取的 25 条结构平均跨越 43.08 个段落，能够测试长距离伏笔回收。
3. Oracle gate、条件生成、LLM judge 和指标汇总链路已在真实 API 上跑通。
4. 单个《促织》案例中 CFPG 正确激活 payoff，但 Prompt 同样生成正确轨迹，暂时不能形成方法优劣结论。
5. 必须完成全量 Oracle 和 Grounded Tracking 后，才能与论文表 1、表 2 做方法级比较。

## 8. 已知问题与风险

### 8.1 生成评测未完成（最大缺口）

- **Oracle 全量未跑。** 25 条 accepted triples 中仅运行 1 条（《促织》），剩余 24 条约 120 次 API 调用尚未执行。
- **Grounded Tracking 全量未跑。** 逐句在线扫描的 FAP、FSCR、CFPG Tracking 三种方法代码已完成，但最坏上限约 10,098 次 decision 调用，全部未实际运行。

### 8.2 数据与方法

- **样本量极小。** 25 条 vs 论文的 629 条，10 篇作品 vs 论文的 148 本书，统计意义不足。
- **数据源不同。** 本实验用短篇原文，论文用 BookSum 长篇小说摘要，两者跨度单位（段 vs 句）和文体特征不可直接比较。
- **经典文本记忆污染。** 10 篇均为名作（福尔摩斯、欧亨利、鲁迅、蒲松龄等），模型可能背诵原文，Oracle Timing 得分会虚高。
- **单模型 verifier。** 论文使用两个独立 verifier 对四项 rubric 共同过滤，当前只有单模型判定。
- **段落→句级 weak alignment。** F/P span 通过确定性词汇重合转换为句级 anchor，未经人工复核，可能对不准。
- **Annotation leakage。** 抽取 run `v3_verified` 曾为英文作品插入中文辅助译文，并为部分作品提供 seed YAML 上下文，不适合作为最终无泄漏结果。
- **伏笔覆盖不完整。** 每篇固定抽取 3 条，且经过单模型自动抽取+验证，未经人工通读审查。人工校验发现部分作品中可能存在其他有意义的 F–T–P 结构未被模型识别，当前 25 条不能代表各作品的完整伏笔集合。需要人工通读全文核对抽取覆盖率，或放宽候选数量并引入多模型交叉验证。

### 8.3 实验设计

- **生成与评判使用同一模型。** 当前 smoke test 用 DeepSeek V4 Pro 既生成又评判，正式实验应使用独立 judge model。
- **Attention saliency 无法复现。** 论文使用了内部注意力分析，但 API 模型不提供内部 attention。
- **双人质量检查未完成。** 论文有 100 条双人标注的质量控制，本实验未开展。
- **译文版权未核验。** 8 篇英文作品的现有中文译文可内部使用，但来源授权状态尚未逐篇确认。

### 8.4 已有结果

- **Ceiling effect。** 《促织》1 条 smoke case 中 Prompt 和 CFPG 均得 1.0，CFPG 相对 Prompt 增量 = 0，既不能复现论文的 +0.272~0.342 提升，也不能反驳论文结论。

## 9. 后续实验

完整实验预计包含约 125 次 Oracle API 调用，以及最多 10,098 次在线 decision 调用，另加触发后的生成和 judge 调用。

检查调用规模：

```bash
python foreshadow/short_stories/cfpg/scripts/run_short_story_cfpg.py --dry-run
```

运行完整 Oracle：

```bash
python foreshadow/short_stories/cfpg/scripts/run_short_story_cfpg.py \
  --experiment oracle \
  --run-id oracle_full
```

运行论文口径的逐句在线实验：

```bash
python foreshadow/short_stories/cfpg/scripts/run_short_story_cfpg.py \
  --experiment tracking \
  --stride 1 \
  --run-id tracking_full
```

建议正式运行前先进行 clean-source F–T–P 重抽取，并使用独立的 `--judge-model`。完整操作说明见实验根目录的 [README](../README.md)。

## 10. 可视化前端

静态前端已经生成：[打开 dashboard.html](dashboard.html)。它不依赖后端或外部 JavaScript 库，可以直接打开，包含：

- 10/30/25、接受率和跨度 KPI；
- 从原文、候选抽取、verifier、句级适配到生成评测的流程及完成状态；
- 逐作品接受/拒绝条形图；
- F–P 跨度分布、Foreshadow 类型和 Payoff 类型分布；
- 7 份实际 Prompt 模板及版本号，可展开查看 system/user 全文；
- Prompt 与 CFPG 的 Oracle 原始输出和论文结果对照；
- 30 条候选的作品、状态、类型和关键词筛选；
- 每条候选到原文、candidate JSONL、verifier JSONL 和 review 的链接；
- 完全复现审计清单与已知限制。

前端由结构化结果重新生成，而不是手工维护。数据更新后运行：

```bash
python foreshadow/short_stories/cfpg/scripts/render_cfpg_report_frontend.py
```

生成器：[render_cfpg_report_frontend.py](../scripts/render_cfpg_report_frontend.py)。

## 11. 全部 30 条候选的分类修订审计

下表展示历史模型标签、人工复核后的互斥主类型和独立叙事功能。历史标签只用于追踪旧结果，不再参与新版统计。

| candidate_id | 状态 | 历史标签 | 新主类型 | 叙事功能 |
| --- | --- | --- | --- | --- |
| `cask_of_amontillado:ftp_candidate:000001` | 通过 | `object` | `object` | `retrospective_reinterpretation` |
| `cask_of_amontillado:ftp_candidate:000002` | 通过 | `rule` | `rule` | `direct_setup` |
| `cask_of_amontillado:ftp_candidate:000003` | 通过 | `object` | `dialogue` | `misdirection` |
| `cricket:ftp_candidate:000001` | 通过 | `social` | `rule` | `ironic_contrast` |
| `cricket:ftp_candidate:000002` | 通过 | `psychological` | `event` | `retrospective_reinterpretation` |
| `cricket:ftp_candidate:000003` | 通过 | `social` | `character_state` | `ironic_contrast` |
| `gift_of_the_magi:ftp_candidate:000001` | 拒绝 | `object` | `object` | `ironic_contrast` |
| `gift_of_the_magi:ftp_candidate:000002` | 通过 | `symbolic` | `narrator_commentary` | `symbolic_reframing` |
| `gift_of_the_magi:ftp_candidate:000003` | 通过 | `red_herring` | `dialogue` | `misdirection` |
| `last_leaf:ftp_candidate:000001` | 通过 | `object` | `character_state` | `direct_setup` |
| `last_leaf:ftp_candidate:000002` | 通过 | `symbolic` | `dialogue` | `retrospective_reinterpretation` |
| `last_leaf:ftp_candidate:000003` | 通过 | `spatial` | `environment_description` | `direct_setup` |
| `medicine:ftp_candidate:000001` | 拒绝 | `symbolic` | `object` | `ironic_contrast` |
| `medicine:ftp_candidate:000002` | 通过 | `social` | `dialogue` | `symbolic_reframing` |
| `medicine:ftp_candidate:000003` | 通过 | `spatial` | `environment_description` | `retrospective_reinterpretation` |
| `necklace:ftp_candidate:000001` | 通过 | `object` | `object` | `misdirection` |
| `necklace:ftp_candidate:000002` | 通过 | `psychological` | `character_state` | `ironic_contrast` |
| `necklace:ftp_candidate:000003` | 拒绝 | `retrospective` | `object` | `misdirection` |
| `red_headed_league:ftp_candidate:000001` | 通过 | `psychological` | `character_state` | `anomaly` |
| `red_headed_league:ftp_candidate:000002` | 通过 | `rule` | `rule` | `misdirection` |
| `red_headed_league:ftp_candidate:000003` | 通过 | `retrospective` | `dialogue` | `retrospective_reinterpretation` |
| `speckled_band:ftp_candidate:000001` | 拒绝 | `red_herring` | `dialogue` | `misdirection` |
| `speckled_band:ftp_candidate:000002` | 通过 | `object` | `object` | `anomaly` |
| `speckled_band:ftp_candidate:000003` | 拒绝 | `rule` | `event` | `retrospective_reinterpretation` |
| `tell_tale_heart:ftp_candidate:000001` | 通过 | `psychological` | `character_state` | `direct_setup` |
| `tell_tale_heart:ftp_candidate:000002` | 通过 | `psychological` | `event` | `retrospective_reinterpretation` |
| `tell_tale_heart:ftp_candidate:000003` | 通过 | `object` | `object` | `direct_setup` |
| `to_build_a_fire:ftp_candidate:000001` | 通过 | `rule` | `dialogue` | `warning` |
| `to_build_a_fire:ftp_candidate:000002` | 通过 | `spatial` | `environment_description` | `warning` |
| `to_build_a_fire:ftp_candidate:000003` | 通过 | `psychological` | `character_state` | `warning` |
