# 前 80 回摘要与伏笔报告

## 概览

本报告记录《红楼梦》前 80 回在 CFPG 复现链路中的摘要、伏笔候选、Trigger 候选和 Foreshadow-Trigger-Payoff 验证实验。当前已经完成 BookSum-style 章节摘要、摘要句时间线、宽口径伏笔层、分窗候选抽取和 F-T-P 验证。

当前结论：

- 摘要覆盖第 1-80 回，无缺章。
- 摘要句时间线共 504 句，平均每回 6.3 句。
- 宽口径伏笔层基础条目 1019 条；合并 candidate extraction 中实际用作 F 的句子后为 1057 条。
- 分窗抽取产生 38 个 F-P candidates，并为每个候选生成 provisional Trigger。
- 验证阶段得到 30 个 unique verified F-T-P triples，8 个 rejected candidates。
- 现有结果可作为第一版细口径三元组数据，但仍需要人工抽样审查、schema 清洗和续作评价前的质量控制。

## 文献问题与方法

### BookSum：长叙事摘要问题

论文链接：[BookSum: A Collection of Datasets for Long-form Narrative Summarization](https://arxiv.org/abs/2105.08209)

动机：现有摘要数据集多集中在新闻、论文、专利等文本上。这些文本通常篇幅较短、结构固定、事实显式、布局偏差强，模型可以依赖文章开头、段落结构或显式事实完成摘要。这样的数据不足以考察文学叙事中更难的能力：跨章节因果关系、非线性时间关系、并行情节、人物状态变化和高抽象度内容选择。

问题定义：BookSum 定义的问题是 long-form narrative summarization，即长篇叙事文本摘要。目标是在小说、戏剧、故事等文学文本上，生成覆盖核心情节、人物和叙事结构的高抽象度摘要。

主要贡献：

- 提出并发布面向长篇文学叙事的多层级摘要数据集，补足新闻类短文本摘要数据无法覆盖的长程叙事场景。
- 将 paragraph、chapter、book 三个粒度组织到同一数据框架中，使长叙事摘要可以按层级建模和评估。
- 证明文学摘要具有更强抽象性、更少位置偏置和更长输入输出长度，对模型的长上下文理解、内容选择和生成能力提出更高要求。

BookSum 的方法是构建一个文学领域的长叙事摘要数据集：

1. 数据来源
   - 原文来自 Project Gutenberg 公版文本，覆盖 novels、plays、stories 等文学作品。
   - 摘要来自 Web Archive 中的人工写作学习指南或章节/全书摘要。

2. 层级组织
   - paragraph-level：段落输入，短摘要。
   - chapter-level：章节输入，多句摘要。
   - book-level：整本书输入，多段摘要。
   - 三个层级形成从短到长、从局部到全书的摘要任务。

3. 清洗与对齐
   - 清除原文元数据、摘要中的 HTML、作者注释和分析性材料。
   - 将原文手动/半自动切成章节，再切成段落。
   - 将 full text、chapter、paragraph 和 summary 做对齐；章节级依赖标题和章节号，段落级使用 sentence-transformer 相似度和 stable matching，并辅以人工检查。

4. 数据规模和意义
   - BookSum 包含 217 个书名、6327 个章节。
   - 最终形成 146532 个 paragraph-level、12630 个 chapter-level、405 个 book-level 样本。
   - 它的关键价值是提供人工写作的高抽象度摘要，并保留长篇叙事中的跨段、跨章、跨书级别结构。

对本项目的启发是：先把《红楼梦》前 80 回组织成 BookSum-style 章节摘要和摘要句时间线，再在这个压缩但可审查的中间层上做伏笔抽取，而不是直接从完整古白话原文中抽取。

### CFPG：伏笔回收问题

论文链接：[Codified Foreshadowing-Payoff Text Generation](https://arxiv.org/abs/2601.07033)

动机：LLM 已经能生成局部流畅、风格一致的故事，但长叙事质量不只取决于句子是否顺畅，还取决于早期设置是否在合适时机被兑现。现有故事生成和评测常关注局部连贯、角色一致或风格一致，却很少显式检查“叙事承诺是否被回收”。因此模型可能看起来连贯，却忘记伏笔、过早兑现、错误兑现，或只做主题呼应而没有具体 payoff。

问题定义：CFPG 定义的问题是 foreshadowing-payoff realization，即模型是否能识别、追踪并兑现早先埋下的叙事承诺。关键不只是找到 Foreshadow 和 Payoff，还要判断何时应该兑现，因此论文引入 Trigger 作为时机门控。

主要贡献：

- 将长叙事一致性重新定义为 narrative commitment fulfillment，即早期叙事承诺是否被及时、具体、逻辑地兑现。
- 提出 Foreshadow-Trigger-Payoff 表示，把伏笔回收从隐式语义关联转化为可追踪的结构化谓词。
- 基于 BookSum 摘要构建 sentence-anchored foreshadow-payoff 数据，并通过多阶段验证减少主题性伪关联。
- 在生成框架中引入 Foreshadow Pool 和 Trigger gate，使模型只在触发条件满足时激活 payoff，降低过早兑现和遗漏兑现。

CFPG 的核心方法是把叙事承诺形式化为 Foreshadow-Trigger-Payoff 三元组：

1. Foreshadow
   - 早期设置、异常、物件、承诺、规则或决定。
   - 它形成尚未清偿的叙事债务。

2. Trigger
   - 使伏笔进入可兑现状态的具体叙事条件。
   - Trigger 用来区分“现在应该兑现”和“还不该兑现”。

3. Payoff
   - 具体事件、揭示、解释或决定。
   - 它必须逻辑上回收 Foreshadow，并由 Trigger 激活。

CFPG 的生成框架维护一个 Foreshadow Pool，里面保存待回收的 `(F, T, P)`。每一步生成前先检查当前上下文是否满足 Trigger，只把满足条件的 Payoff 注入生成要求；生成后再更新状态，移除已回收伏笔，并加入新伏笔。

论文的数据构造也基于 BookSum 摘要，而不是完整小说原文。流程为三步：

1. Sentence-level candidate identification
   - 在 BookSum 的抽象摘要句序列中抽取候选 foreshadow-payoff 句对。
   - 这一阶段追求召回，允许弱候选进入下一步。

2. Payoff alignment verification
   - 验证 payoff 位置附近的上下文是否真正构成 setup 的因果/叙事回收。
   - 过滤掉主题呼应、隐喻关联、提前暗示但没有具体回收的候选。

3. Rubric-based filtering
   - 按 setup validity、payoff validity、temporal separation、foreshadow justification 四个维度过滤。
   - 只有两个 verifier 都接受的候选才进入最终数据。

论文最终从 148 本书中得到 629 个 validated foreshadow-payoff pairs，平均 payoff 距离为 20.9 个句子，中位数为 13 个句子。这个规模说明最终 F-P/F-T-P 数据应当比原始候选少很多，强调高精度验证，而不是简单保留所有潜在伏笔。

## 本实验方法

本实验模仿 BookSum 的 chapter-level summary 组织方式。BookSum 的核心价值不是提供伏笔标注，而是把长篇文本压缩成章节级、可对齐、可切句的摘要层。对《红楼梦》而言，直接在完整原文上抽伏笔成本高、噪声大，因此当前流程先构建摘要中间层，再进入 CFPG 的候选抽取和验证。

当前链路分为四层：

1. 章节摘要层
   - 输入：前 80 回分回文本。
   - 模型：`deepseek-v4-pro`。
   - Prompt 版本：[`honglou_booksum_chapter_v2_full80`](../../prompts/honglou_prompts.md)，对应 `booksum_chapter_summary` block。
   - 每回输出 summary、summary sentences、key events、character state changes、unresolved setups、foreshadow notes、poem/dream/prophecy/object items。

2. 摘要句时间线层
   - 将每回 `summary_sentences` 展平成全书级句子序列。
   - 每句保留 `global_sentence_index`、`chapter_index`、`chapter_sentence_index` 和来源摘要 ID。
   - 该层为后续 Foreshadow-Payoff 候选抽取提供时间顺序。

3. 宽口径伏笔层
   - 从章节摘要中的三类字段汇总：
     - `summary_unresolved_setup`
     - `summary_foreshadow_note`
     - `summary_poem_dream_prophecy_object`
   - 这一层追求召回，不追求最终精确。

4. Trigger / verified F-T-P 层
   - 使用 `candidate_extraction` prompt 以 40 个摘要句为窗口、30 句步长进行分窗抽取，每窗最多 3 个候选。
   - 抽取阶段生成 38 个 F-P candidates，并附带 provisional Trigger。
   - 使用 `candidate_verification` prompt 对每个候选做 setup/payoff/trigger/connection 验证。
   - 验证阶段得到 30 个 unique verified F-T-P triples，8 个 rejected candidates。

## 从宽到细的评价标准与过滤

当前实验不是一次性直接生成最终三元组，而是按“高召回候选池 -> 可定位候选句对 -> verified F-T-P”的顺序逐层收紧。

### 第 1 层：宽口径伏笔层

目标：尽量保留可能有后续回收价值的叙事设置，追求召回，不作为最终三元组。

进入标准：

- 来自章节摘要中的 `unresolved_setups`：尚未解决的决定、冲突、承诺、风险、身份问题或关系张力。
- 来自章节摘要中的 `foreshadow_notes`：摘要阶段显式标出的伏笔说明。
- 来自章节摘要中的 `poem/dream/prophecy/object items`：诗词、梦境、预言、物件、象征和名号等可能承载后文意义的元素。

这一层只判断“是否值得进入候选池”，不要求已经找到 payoff，也不要求 trigger 可观察。`candidate`、`pending`、`resolved_in_chapter` 是状态标签，不是最终通过/拒绝标签。

### 第 2 层：F-P + Trigger 候选层

目标：从宽口径候选池和摘要句时间线中找出可定位的 Foreshadow-Payoff 句对，并生成 provisional Trigger。

进入标准：

- Foreshadow 必须早于 Payoff，二者都要能定位到摘要句时间线中的 `global_sentence_index`。
- Foreshadow 应当是具体的叙事承诺、异常、物件、预言、决定、规则或话语行为。
- Payoff 必须提供新信息、揭示、后果或行动，能够回看解释 Foreshadow。
- 二者不能只是同一主题、人物性格或氛围的重复。
- Trigger 必须描述可观察的叙事条件，用来解释为什么此时进入 payoff，而不是简单复述 payoff 本身。

执行口径：

- 使用 40 条摘要句滑窗，步长 30 条摘要句。
- 全书 504 条摘要句理论上形成 17 个窗口，其中 16 个窗口产生了保留候选。
- 每个窗口最多保留 3 个候选。
- 相同 Foreshadow-Payoff 句对会去重。

### 第 3 层：verified F-T-P 层

目标：判断候选是否真正形成可用于后续评价的 Foreshadow-Trigger-Payoff 三元组。

通过标准：

- `setup_validity`：Foreshadow 本身成立，且不是已经当场解决的普通事件。
- `payoff_validity`：Payoff 是具体事件、揭示、解释或决定，不是泛泛主题呼应。
- `temporal_separation`：Foreshadow 和 Payoff 之间存在非平凡时间间隔。
- `foreshadow_justification`：读到 Payoff 后，回看 Foreshadow 能合理解释为伏笔。
- `trigger_validity`：Trigger 是可观察叙事条件，且不等同于 Payoff 本身。
- `connection_validity`：Foreshadow、Trigger、Payoff 之间存在叙事因果或承诺兑现关系。
- `is_thematic_echo_only=false`：不是单纯主题、意象或人物性格重复。
- `is_unsupported_by_evidence=false`：不能依赖摘要句证据之外的臆测。

### 过滤结果统计

| 阶段 | 输入 | 输出/保留 | 保留率 | 过滤率 | 过滤或备注 |
| --- | ---: | ---: | ---: | ---: | --- |
| 摘要句时间线 | 80 回摘要 | 504 句 | - | - | 后续抽取的时间轴 |
| 宽口径伏笔层 | 摘要结构化字段 | 1057 条 | - | - | 高召回候选池，不做最终过滤 |
| F-P candidate extraction | 1057 条宽口径伏笔 + 504 条摘要句 | 38 个 F-P candidates | 3.60% | 96.40% | 17 个窗口中 16 个产生候选，每窗最多 3 个，重复句对去重 |
| F+Trigger 渲染层 | 38 个 F-P candidates | 38 条 F+Trigger rows | 100.00% | 0.00% | 每个候选附带 provisional Trigger |
| F-T-P verification | 38 个 candidates | 30 个 unique verified triples | 78.95% | 21.05% | 8 个 rejected candidates |

从宽口径伏笔层到最终 verified F-T-P 的端到端保留率为 2.84%，过滤率为 97.16%。这个比例符合当前实验定位：宽口径层负责召回和人工审查入口，verified 层负责形成可用于后续续作评价的高精度三元组池。

人类可读跳转入口：

| 收紧阶段 | 本轮结果 | 人类可读跳转 |
| --- | ---: | --- |
| 宽口径伏笔层 | 1057 条 | [伏笔层 review](foreshadows/honglou_foreshadows_20260611_deepseek_honglou_original80.review.md) |
| F+Trigger 候选层 | 38 条 | [Trigger 候选 review](foreshadow_triggers/honglou_foreshadow_triggers_20260611_deepseek_honglou_original80.review.md#L3) |
| verified F-T-P 层 | 30 条 | [accepted triples review](verified/honglou_ftp_triples_20260611_deepseek_honglou_original80.unique.review.md#L3) |
| rejected candidates | 8 条 | [rejected candidates review](verified/honglou_ftp_triples_20260611_deepseek_honglou_original80.unique.review.md#L275) |
| 合格 Trigger 样例 | 1 条 | [foreshadow_trigger:000001](foreshadow_triggers/honglou_foreshadow_triggers_20260611_deepseek_honglou_original80.review.md#L5) / [ftp:000001](verified/honglou_ftp_triples_20260611_deepseek_honglou_original80.unique.review.md#L5) |
| 不合格 Trigger 样例 | 2 条 | [贾瑞 foreshadow_trigger:000006](foreshadow_triggers/honglou_foreshadow_triggers_20260611_deepseek_honglou_original80.review.md#L64) / [金钏儿 foreshadow_trigger:000013](foreshadow_triggers/honglou_foreshadow_triggers_20260611_deepseek_honglou_original80.review.md#L143) |

### 与原始论文对比

原始 CFPG 论文报告的是最终数据集统计，而没有公开 Stage 1 原始候选总数，因此不能严格对比“初始候选 -> verified”的过滤率。可直接对比的是最终数据规模、类型分布、payoff 距离和质量控制口径。

| 指标 | CFPG 论文 | 本实验 |
| --- | ---: | ---: |
| 文本来源 | BookSum 多书摘要 | 《红楼梦》前 80 回 AI 生成 BookSum-style 摘要 |
| 覆盖书籍 | 148 本 | 1 部作品的前 80 回 |
| 最终 validated / verified F-P 或 F-T-P | 629 条 | 30 条 |
| 平均每书/每作品 verified 数 | 4.25 条/书 | 30 条/前 80 回 |
| 平均 payoff 距离 | 20.9 句 | 8.6 句 |
| payoff 距离中位数 | 13.0 句 | 9.0 句 |
| payoff 距离 75 分位 | 29.0 句 | 11.8 句 |
| payoff 距离 90 分位 | 45.0 句 | 14.1 句 |
| 最大 payoff 距离 | 230 句 | 20 句 |
| 平均 extraction confidence | 0.98 | 0.84 |
| 人工质量检查 | 100 条样本，pair validity agreement 0.87 | 尚未人工复核 |

类型分布对比：

| 类型 | CFPG 论文 | 本实验 verified F-T-P |
| --- | ---: | ---: |
| `object` | 48.2% | 13.3% |
| `event` | 35.3% | 30.0% |
| `speech_act` | 9.7% | 43.3% |
| `rule` | 5.1% | 3.3% |
| `symbol` | 1.7% | 3.3% |
| `dream` / `poem` | 未单列 | 各 3.3% |

主要差异：

1. 本实验更偏短距离回收
   - 论文的平均距离 20.9 句、最大 230 句，强调长程依赖。
   - 本实验平均距离 8.6 句、最大 20 句，说明当前滑窗与每窗最多 3 个候选的设置更容易抽到局部或中程回收。

2. 本实验 `speech_act` 占比偏高
   - 论文中 object/event 合计超过 80%，强调可观察物件和事件链。
   - 本实验中 speech_act 为 43.3%，说明当前 prompt 更容易把誓言、警告、决定、计谋和人物话语识别为伏笔。

3. 本实验缺少论文级人工验证
   - 论文对 100 条样本做双人质量检查，pair validity agreement 为 0.87，setup/payoff/connection 也分别报告一致性。
   - 本实验目前只有 LLM verifier 自动结果，下一步需要人工抽样复核 accepted 30 条和 rejected 8 条，才能评估 precision。

4. 过滤比例不可完全同口径比较
   - 本实验记录了宽口径 1057 条到最终 30 条的端到端保留率 2.84%。
   - 论文只报告最终 629 条 validated pairs，没有给出 Stage 1 候选总数，因此无法计算论文的同口径端到端保留率。

候选类型分布：

| 类型 | F-P candidates | verified F-T-P |
| --- | ---: | ---: |
| `speech_act` | 17 | 13 |
| `event` | 11 | 9 |
| `object` | 5 | 4 |
| `poem` | 1 | 1 |
| `symbol` | 1 | 1 |
| `rule` | 1 | 1 |
| `dream` | 1 | 1 |
| `identity` | 1 | 0 |

Rejected candidates 的失败项如下。失败项可重叠，因此总数大于 8。

| 失败项 | 数量 |
| --- | ---: |
| `trigger_validity=false` | 8 |
| `setup_validity=false` | 1 |
| `foreshadow_justification=false` | 1 |
| `connection_validity=false` | 1 |
| `is_thematic_echo_only=true` | 1 |
| `is_unsupported_by_evidence=true` | 1 |

本轮 rejected 的主要问题是 Trigger 不合格：很多候选的 Foreshadow 和 Payoff 本身有联系，但 provisional Trigger 复述了 Payoff，或把 Payoff 结果放进触发条件，不能作为“何时应该兑现”的独立门控条件。

accepted 和 rejected Trigger 的详细结果可以直接看以下文件：

- accepted F-T-P：机器可读结果在 [verified/honglou_ftp_triples_20260611_deepseek_honglou_original80.unique.jsonl](verified/honglou_ftp_triples_20260611_deepseek_honglou_original80.unique.jsonl)，人工查看版在 [verified/honglou_ftp_triples_20260611_deepseek_honglou_original80.unique.review.md](verified/honglou_ftp_triples_20260611_deepseek_honglou_original80.unique.review.md)。
- accepted/rejected 混排的 Trigger 候选：人工查看版在 [foreshadow_triggers/honglou_foreshadow_triggers_20260611_deepseek_honglou_original80.review.md](foreshadow_triggers/honglou_foreshadow_triggers_20260611_deepseek_honglou_original80.review.md)，每条标题后标有 `[accepted]` 或 `[rejected]`。
- rejected candidates：机器可读结果在 [verified/honglou_rejected_candidates_20260611_deepseek_honglou_original80.jsonl](verified/honglou_rejected_candidates_20260611_deepseek_honglou_original80.jsonl)，失败项汇总在 [../cfpg_reports/20260611_deepseek_honglou_original80/verification_report.json](../cfpg_reports/20260611_deepseek_honglou_original80/verification_report.json)。

Trigger 合格与不合格的差别可以从以下样例看出：

- 合格样例：[英莲预言诗](foreshadow_triggers/honglou_foreshadow_triggers_20260611_deepseek_honglou_original80.review.md#L5) 的 F 是“有命无运”和四句预言，T 是门子在审理薛蟠案时揭示被卖婢女就是英莲，并讲明被拐、被卖、薛蟠夺人的经过，P 是案底被完整揭开。这个 Trigger 是独立可观察的揭示场景，解释了为什么此刻能兑现早前预言。
- 不合格样例 1：[贾瑞案](foreshadow_triggers/honglou_foreshadow_triggers_20260611_deepseek_honglou_original80.review.md#L64) 的 F 是凤姐决意施以手段，P 是贾瑞照“风月宝鉴”正面后精尽人亡；候选 T 写成“凤姐设相思局、贾瑞崩溃、最终照正面而亡”。这里 T 已经把 Payoff 结局写进去，只是在复述兑现结果。
- 不合格样例 2：[金钏儿案](foreshadow_triggers/honglou_foreshadow_triggers_20260611_deepseek_honglou_original80.review.md#L143) 的 F 是金钏儿被王夫人打骂撵出，P 是金钏儿投井而死；候选 T 是“金钏儿投井的消息传到贾府，众人得知其死讯”。这个 T 是回收事件的报道，不是能提前判断“何时应兑现”的独立门控条件。

### 分层结果保存位置

| 层级 | 机器可读 | 人类可读/报告 |
| --- | --- | --- |
| 摘要层 | [honglou_booksum/original_80_chapter_summaries.jsonl](honglou_booksum/original_80_chapter_summaries.jsonl) | [honglou_booksum/original_80_chapter_summaries.review.md](honglou_booksum/original_80_chapter_summaries.review.md) |
| 摘要句时间线 | [summary_alignments/original_80_summary_sentence_timeline_20260611_deepseek_honglou_original80.jsonl](summary_alignments/original_80_summary_sentence_timeline_20260611_deepseek_honglou_original80.jsonl) | [layers/honglou_cfpg_layers_20260611_deepseek_honglou_original80.review.md](layers/honglou_cfpg_layers_20260611_deepseek_honglou_original80.review.md) |
| 宽口径伏笔层 | [foreshadows/honglou_foreshadows_20260611_deepseek_honglou_original80.jsonl](foreshadows/honglou_foreshadows_20260611_deepseek_honglou_original80.jsonl) | [foreshadows/honglou_foreshadows_20260611_deepseek_honglou_original80.review.md](foreshadows/honglou_foreshadows_20260611_deepseek_honglou_original80.review.md) |
| F-P candidates | [candidates/honglou_candidates_20260611_deepseek_honglou_original80.jsonl](candidates/honglou_candidates_20260611_deepseek_honglou_original80.jsonl) | [../cfpg_reports/20260611_deepseek_honglou_original80/candidate_extraction_report.json](../cfpg_reports/20260611_deepseek_honglou_original80/candidate_extraction_report.json) |
| F+Trigger 候选层 | [foreshadow_triggers/honglou_foreshadow_triggers_20260611_deepseek_honglou_original80.jsonl](foreshadow_triggers/honglou_foreshadow_triggers_20260611_deepseek_honglou_original80.jsonl) | [foreshadow_triggers/honglou_foreshadow_triggers_20260611_deepseek_honglou_original80.review.md](foreshadow_triggers/honglou_foreshadow_triggers_20260611_deepseek_honglou_original80.review.md) |
| verified F-T-P 层 | [verified/honglou_ftp_triples_20260611_deepseek_honglou_original80.unique.jsonl](verified/honglou_ftp_triples_20260611_deepseek_honglou_original80.unique.jsonl) | [verified/honglou_ftp_triples_20260611_deepseek_honglou_original80.unique.review.md](verified/honglou_ftp_triples_20260611_deepseek_honglou_original80.unique.review.md) |
| rejected candidates | [verified/honglou_rejected_candidates_20260611_deepseek_honglou_original80.jsonl](verified/honglou_rejected_candidates_20260611_deepseek_honglou_original80.jsonl) | [../cfpg_reports/20260611_deepseek_honglou_original80/verification_report.json](../cfpg_reports/20260611_deepseek_honglou_original80/verification_report.json) |

## 结果文件

入口 README：

[README.md](README.md)

设计文档：

[../../docs/cfpg_reproduction_design.md](../../docs/cfpg_reproduction_design.md)

Prompt 文件：

[../../prompts/honglou_prompts.md](../../prompts/honglou_prompts.md)

总览文件：

[layers/honglou_cfpg_layers_20260611_deepseek_honglou_original80.review.md](layers/honglou_cfpg_layers_20260611_deepseek_honglou_original80.review.md)

摘要层：

- 机器可读：[honglou_booksum/original_80_chapter_summaries.jsonl](honglou_booksum/original_80_chapter_summaries.jsonl)
- 人类可读：[honglou_booksum/original_80_chapter_summaries.review.md](honglou_booksum/original_80_chapter_summaries.review.md)

摘要句时间线：

- 机器可读：[summary_alignments/original_80_summary_sentence_timeline_20260611_deepseek_honglou_original80.jsonl](summary_alignments/original_80_summary_sentence_timeline_20260611_deepseek_honglou_original80.jsonl)

伏笔层：

- 机器可读：[foreshadows/honglou_foreshadows_20260611_deepseek_honglou_original80.jsonl](foreshadows/honglou_foreshadows_20260611_deepseek_honglou_original80.jsonl)
- 人类可读：[foreshadows/honglou_foreshadows_20260611_deepseek_honglou_original80.review.md](foreshadows/honglou_foreshadows_20260611_deepseek_honglou_original80.review.md)

伏笔 + Trigger 候选层：

- 机器可读：[foreshadow_triggers/honglou_foreshadow_triggers_20260611_deepseek_honglou_original80.jsonl](foreshadow_triggers/honglou_foreshadow_triggers_20260611_deepseek_honglou_original80.jsonl)
- 人类可读：[foreshadow_triggers/honglou_foreshadow_triggers_20260611_deepseek_honglou_original80.review.md](foreshadow_triggers/honglou_foreshadow_triggers_20260611_deepseek_honglou_original80.review.md)

候选源文件：

- 机器可读：[candidates/honglou_candidates_20260611_deepseek_honglou_original80.jsonl](candidates/honglou_candidates_20260611_deepseek_honglou_original80.jsonl)

已验证 F-T-P 层：

- 机器可读：[verified/honglou_ftp_triples_20260611_deepseek_honglou_original80.unique.jsonl](verified/honglou_ftp_triples_20260611_deepseek_honglou_original80.unique.jsonl)
- 人类可读：[verified/honglou_ftp_triples_20260611_deepseek_honglou_original80.unique.review.md](verified/honglou_ftp_triples_20260611_deepseek_honglou_original80.unique.review.md)
- rejected candidates：[verified/honglou_rejected_candidates_20260611_deepseek_honglou_original80.jsonl](verified/honglou_rejected_candidates_20260611_deepseek_honglou_original80.jsonl)

运行报告：

- 抽取报告：[../cfpg_reports/20260611_deepseek_honglou_original80/candidate_extraction_report.json](../cfpg_reports/20260611_deepseek_honglou_original80/candidate_extraction_report.json)
- 验证报告：[../cfpg_reports/20260611_deepseek_honglou_original80/verification_report.json](../cfpg_reports/20260611_deepseek_honglou_original80/verification_report.json)

## 数据量

### 摘要层

| 指标 | 数量 |
| --- | ---: |
| 覆盖章节 | 80 |
| 摘要句 | 504 |
| 平均每回摘要句 | 6.3 |
| 关键事件 | 593 |
| 人物状态变化 | 404 |
| 未解决 setup | 376 |
| 伏笔说明 | 339 |
| 诗词/梦境/预言/物件 | 304 |
| 生成 warning | 0 |

摘要句数分布：

| 每回摘要句数 | 章节数 |
| --- | ---: |
| 4 | 4 |
| 5 | 13 |
| 6 | 35 |
| 7 | 18 |
| 8 | 4 |
| 9 | 5 |
| 10 | 1 |

### 伏笔层

| 来源层 | 数量 |
| --- | ---: |
| `summary_unresolved_setup` | 376 |
| `summary_foreshadow_note` | 339 |
| `summary_poem_dream_prophecy_object` | 304 |
| `candidate_extraction` | 38 |
| 总计 | 1057 |

| 状态 | 数量 |
| --- | ---: |
| `candidate` | 681 |
| `pending` | 366 |
| `resolved_in_chapter` | 10 |

| 类型 | 数量 |
| --- | ---: |
| `event` | 300 |
| `speech_act` | 244 |
| `object` | 191 |
| `poem` | 174 |
| `identity` | 34 |
| `prophecy` | 26 |
| `dream` | 24 |
| `symbol` | 18 |
| `rule` | 18 |
| 空类型 | 15 |
| `name_symbol` | 7 |
| `other` | 4 |
| `status_quo` | 2 |

摘要来源的基础宽口径伏笔为 1019 条；渲染后把 38 个 candidate extraction 中实际用作 F 的摘要句也并入伏笔层，因此当前伏笔层总计 1057 条。

### 细口径候选与验证层

| 指标 | 数量 |
| --- | ---: |
| F-P candidates | 38 |
| F+Trigger rows | 38 |
| verified F-T-P triples | 30 |
| unique verified F-T-P triples | 30 |
| rejected candidates | 8 |

| verified 类型 | 数量 |
| --- | ---: |
| `speech_act` | 13 |
| `event` | 9 |
| `object` | 4 |
| `poem` | 1 |
| `symbol` | 1 |
| `rule` | 1 |
| `dream` | 1 |

## 示例

### 示例 1：神话楔子

位置：第 1 回。

伏笔：神瑛侍者与绛珠仙草的前世灌溉之德，绛珠立誓以一生眼泪还报，引出风流冤家下凡历幻缘。

证据：`他若下世为人，我也同去走一道，但把我一生所有的眼泪还他，也还得过了。`

分析：这是全书级长程伏笔，不应在最终三元组里粗糙地绑定为一个单点 payoff。更合理的做法是拆成多个可观察 trigger，例如宝黛相遇、情感债务显化、病弱与泪尽等节点，再分别验证 payoff。

### 示例 2：英莲预言

位置：第 1 回。

伏笔：癞头僧对英莲的断言及诗句，以“有命无运”“菱花空对雪澌澌”等预示其命运多舛。

证据：`惯养娇生笑你痴，菱花空对雪澌澌。好防佳节元宵后，便是烟消火灭时。`

分析：该伏笔具有分段回收特征。元宵被拐和甄家火灾已经回收一部分，但“菱花”“雪”等意象仍指向后续身份和婚姻命运。后续验证层需要允许一个 Foreshadow 对应多个 Payoff。

### 示例 3：贾府衰败信号

位置：第 2 回。

伏笔：冷子兴说贾府“内囊却也尽上来了”，儿孙一代不如一代。

证据：`外面的架子虽没很倒，内囊却也尽上来了...儿孙，竟一代不如一代了。`

分析：这是家族衰败主线的早期显性信号。它适合进入 narrative commitment pool，但不适合只绑定一个 payoff。后续应在经济困顿、内部管理失序、抄检和政治失势等多个事件上追踪状态变化。

### 示例 4：第 5 回判词与曲文

第 5 回是伏笔密度最高的章节之一。当前宽口径伏笔层会把诗词、梦境、预言和物件条目纳入 `summary_poem_dream_prophecy_object`，因此判词和曲文已经作为伏笔载体保留在伏笔层中。本轮细口径抽取采用每窗最多 3 个候选的保守设置，优先产生可在摘要句时间线中找到 payoff 的 F-P pair；因此第 5 回判词并不等于全部都会进入 verified F-T-P。后续若要专门处理判词，需要提高每窗候选数，或以第 5 回判词作为人工种子做 targeted extraction。

## 质量分析

### 有效性

当前摘要层基本达到了 BookSum-style 中间层的目标：它把每回压缩为 4-10 个摘要句，同时保留关键事件、人物状态变化和潜在伏笔字段。对 CFPG 而言，这比直接从古白话全文抽取候选更稳定，也更便于人工审查。

宽口径伏笔层的召回较高，特别是对《红楼梦》中重要的诗词、梦境、判词、预言、物件、身份和婚姻承诺有较好覆盖。第 5 回等伏笔密集章节被识别为高密度章节，符合文本直觉。

细口径 F-T-P 验证已经跑通：38 个 F-P candidates 中，30 个通过 verifier，8 个被拒绝。通过项以 speech_act、event 和 object 为主，说明当前 prompt 更擅长抽取有明确话语承诺、事件延续或物件回收的伏笔，而对主题性、象征性和超长程判词仍较保守。

### 局限

1. 当前 verified triples 仍是第一版自动结果
   - 30 个 verified F-T-P 尚未经过人工逐条审查。
   - verifier 会过滤主题性伪关联，但也可能误收局部因果、误拒隐喻回收。

2. 召回受窗口和候选数限制
   - 本轮使用 40 句窗口、30 句步长、每窗最多 3 个候选。
   - 这能降低噪声和成本，但会漏掉超长距离伏笔，尤其是第 5 回判词、家族衰败、宝黛还泪等全书级线索。

3. 类型 schema 需要清洗
   - 存在 15 条空类型。
   - `poem`、`prophecy`、`symbol`、`name_symbol` 等边界有重叠。

4. LLM 摘要不是人工 BookSum
   - BookSum 摘要是人工标记，本实验用 DeepSeek 生成。
   - LLM 可能引入先验红楼知识，把后文理解提前写入当前回伏笔说明。

5. 证据还不是严格 span 对齐
   - 当前 evidence quote 便于阅读，但未记录精确字符 span。
   - 若要做论文级数据集，需要补 source span 或句级对齐。

## 下一步

1. 人工抽样审查 verified triples
   - 优先检查 accepted 30 条和 rejected 8 条。
   - 重点看是否存在局部因果误收、主题性误收、Trigger 过宽或 Payoff 不具体。

2. 提高召回
   - 对第 5 回判词、还泪神话、贾府衰败等全书级线索做 targeted extraction。
   - 增大 `--max-candidates` 或使用更长窗口，比较新增候选质量。

3. 清洗伏笔层和类型 schema
   - 合并重复条目。
   - 补齐空类型。
   - 区分局部回收、跨章节回收和主题性伏笔。

4. 进入续作评价
   - 用 verified F-T-P pool 检查续作是否过早兑现、遗漏兑现、错误兑现或只做主题呼应。
