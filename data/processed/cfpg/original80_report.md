# 前 80 回摘要与伏笔报告

## 概览

本报告记录《红楼梦》前 80 回在 CFPG 复现链路中的摘要与伏笔候选实验。当前完成的是数据准备和宽口径伏笔发现阶段：已经生成 BookSum-style 章节摘要、摘要句时间线和伏笔候选层；尚未完成 Foreshadow-Trigger-Payoff 三元组验证。

当前结论：

- 摘要覆盖第 1-80 回，无缺章。
- 摘要句时间线共 504 句，平均每回 6.3 句。
- 宽口径伏笔层共 1019 条。
- 伏笔 + Trigger 候选层目前为空，verified F-T-P 层尚未生成。
- 现有结果适合做人工审查、候选池构建和下一步 F-P/Trigger 抽取，但不能直接作为最终三元组数据集使用。

## 文献问题与方法

### BookSum：长叙事摘要问题

BookSum 论文定义的问题是 long-form narrative summarization，即长篇叙事文本摘要。作者指出，新闻、论文、专利等常见摘要数据集通常文本较短、结构固定、事实显式、布局偏差强，不能充分考察长篇叙事中的远距离因果关系、时间关系、并行情节和丰富话语结构。

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

CFPG 论文定义的问题是 foreshadowing-payoff realization，即模型是否能兑现早先埋下的叙事承诺。作者认为，现有故事生成和评测常关注局部连贯、风格一致或角色一致，但缺少对“伏笔是否在合适时机被具体回收”的显式建模。LLM 可能写出局部流畅的故事，却忘记伏笔、过早兑现、错误兑现或只做主题呼应。

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
   - Prompt 版本：`honglou_booksum_chapter_v2_full80`。
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
   - 当前尚未正式生成。
   - 后续需要从摘要句时间线和伏笔层抽取 F-P 候选，再验证 Trigger 是否可观察、Payoff 是否真正回收 Foreshadow。

## 结果文件

入口 README：

[README.md](README.md)

设计文档：

[../../../documentations/cfpg_reproduction_design.md](../../../documentations/cfpg_reproduction_design.md)

Prompt 文件：

[../../../prompts/cfpg/honglou_prompts.md](../../../prompts/cfpg/honglou_prompts.md)

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

该层当前为 0 条。

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
| 总计 | 1019 |

| 状态 | 数量 |
| --- | ---: |
| `candidate` | 643 |
| `pending` | 366 |
| `resolved_in_chapter` | 10 |

| 类型 | 数量 |
| --- | ---: |
| `event` | 289 |
| `speech_act` | 227 |
| `object` | 186 |
| `poem` | 173 |
| `identity` | 33 |
| `prophecy` | 26 |
| `dream` | 23 |
| `symbol` | 17 |
| `rule` | 17 |
| 空类型 | 15 |
| `name_symbol` | 7 |
| `other` | 4 |
| `status_quo` | 2 |

每回伏笔条目平均 12.74 条，中位数 13 条；最少 5 条，最多 24 条。伏笔密度最高的章节包括第 5、50、63、22、1、51、37、18 回。

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

第 5 回是伏笔密度最高的章节之一。当前宽口径伏笔层会把诗词、梦境、预言和物件条目纳入 `summary_poem_dream_prophecy_object`，因此判词和曲文已经作为伏笔载体保留在伏笔层中。但它们还没有进入 verified F-T-P，因为 Trigger 和 Payoff 验证尚未执行。

## 质量分析

### 有效性

当前摘要层基本达到了 BookSum-style 中间层的目标：它把每回压缩为 4-10 个摘要句，同时保留关键事件、人物状态变化和潜在伏笔字段。对 CFPG 而言，这比直接从古白话全文抽取候选更稳定，也更便于人工审查。

宽口径伏笔层的召回较高，特别是对《红楼梦》中重要的诗词、梦境、判词、预言、物件、身份和婚姻承诺有较好覆盖。第 5 回等伏笔密集章节被识别为高密度章节，符合文本直觉。

### 局限

1. 当前不是最终三元组
   - 1019 条伏笔是候选层，不是 verified F-T-P。
   - 其中包含主题性、重复性和过宽泛条目。

2. Trigger 层尚未形成
   - 现在还没有“何时应当兑现”的触发条件。
   - 因此还不能用当前数据评价续作是否兑现伏笔。

3. 类型 schema 需要清洗
   - 存在 15 条空类型。
   - `poem`、`prophecy`、`symbol`、`name_symbol` 等边界有重叠。

4. LLM 摘要不是人工 BookSum
   - BookSum 摘要是人工标记，本实验用 DeepSeek 生成。
   - LLM 可能引入先验红楼知识，把后文理解提前写入当前回伏笔说明。

5. 证据还不是严格 span 对齐
   - 当前 evidence quote 便于阅读，但未记录精确字符 span。
   - 若要做论文级数据集，需要补 source span 或句级对齐。

## README 是否合并

不建议把本报告合并进 README。

README 的职责是导航：设计文档、prompt、结果文件和脚本入口。实验报告的职责是记录方法、统计、例子和分析。两者只需要在 README 中互相链接，不应合并成一个过长文档。

## 下一步

1. 执行 candidate extraction
   - 输入摘要句时间线和宽口径伏笔层。
   - 输出 Foreshadow-Payoff 候选和 provisional Trigger。

2. 执行 candidate verification
   - 验证 Foreshadow、Trigger、Payoff 是否具体、可观察、可定位。
   - 输出 verified F-T-P triples。

3. 做人工抽样审查
   - 优先检查第 1、2、5、22、50、63 回。
   - 重点检查判词、梦境、诗词、物件、身份错认、婚姻承诺和家族衰败线索。

4. 清洗伏笔层
   - 合并重复条目。
   - 补齐空类型。
   - 区分局部回收、跨章节回收和主题性伏笔。
