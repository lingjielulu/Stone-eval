# HongLou CFPG Prompt Templates

本文件是当前 CFPG 链路的权威 prompt 文件。Python 脚本按 `prompt:key` 读取模板，运行时替换 `{{placeholder}}`。

可用占位符：

- `booksum_chapter_summary`: `{{chapter_title}}`, `{{chapter_text}}`
- `candidate_extraction`: `{{max_candidates}}`, `{{summary_timeline}}`, `{{chapter_notes}}`
- `candidate_verification`: `{{candidate_id}}`, `{{foreshadow_sentence_index}}`, `{{foreshadow_text}}`, `{{payoff_sentence_index}}`, `{{payoff_text}}`, `{{proposed_trigger_json}}`, `{{relation_description}}`, `{{setup_window}}`, `{{payoff_window}}`

<!-- prompt:booksum_chapter_summary version:honglou_booksum_chapter_v2_full80 -->
```system
你是《红楼梦》古白话叙事摘要标注员。任务是模仿 BookSum 的人工文学摘要，为单回文本生成高质量中文摘要，同时保留后续伏笔-回收抽取所需的叙事线索。只能依据本回输入文本，不得使用你对后续章节的外部知识；不得写出本回正文未出现的人名、结局或后文解释。只输出合法 JSON。
```
```user
请为下面这一回生成 BookSum-style chapter summary。

要求：
1. summary 写成 4-8 句连贯中文，概括本回关键事件、因果推进和人物状态变化。
2. 不要只写主线剧情；必须额外列出本回出现的潜在伏笔材料。
3. 伏笔材料包括：未解释异常、承诺/誓言、关键对话/人物话语、梦境、诗词/判词/偈语/灯谜、关键物件、制度/规则、身份线索。
4. 只基于本回，不要提前透露后文答案；不要写本回未出现的人名、人物归宿、后文身份揭示或后文结局。若某线索在本回已经解决，要标为 resolved_in_chapter。
5. 每个列表项都要给 evidence_quote，引用本回原文中的短证据，不要超过 40 个汉字。
6. 输出必须是一个 JSON object，字段严格如下：
{
  "chapter_summary": "4-8句中文摘要",
  "key_events": [
    {"event": "...", "evidence_quote": "..."}
  ],
  "character_state_changes": [
    {"character": "...", "state_change": "...", "evidence_quote": "..."}
  ],
  "unresolved_setups": [
    {"setup": "...", "type": "object|event|speech_act|rule|identity|other", "status": "pending|resolved_in_chapter", "evidence_quote": "..."}
  ],
  "foreshadow_notes": [
    {"note": "...", "type": "object|event|speech_act|rule|symbol|dream|poem", "why_it_matters_without_future_spoilers": "只说明该线索在本回为何形成悬念，不得引用后文知识", "evidence_quote": "..."}
  ],
  "poem_dream_prophecy_objects": [
    {"item": "...", "category": "poem|dream|prophecy|object|name_symbol", "literal_content": "...", "evidence_quote": "..."}
  ],
  "warnings": []
}

回目：
{{chapter_title}}

正文：
<<<
{{chapter_text}}
>>>
```
<!-- /prompt -->

<!-- prompt:candidate_extraction version:honglou_ftp_extraction_v3_full80 -->
```system
任务：在给定的《红楼梦》BookSum-style 摘要句子时间线中，高召回抽取候选 Foreshadow-Payoff 句对，并给出 provisional Trigger。下面的用户消息会完整定义术语、约束和输出格式。只能依据给定摘要句子和 notes，不得使用后文或外部知识。只输出 JSON。
```
```user
执行第一步：高召回候选识别。请抽取候选 Foreshadow-Payoff 句对。

本步骤基于 Foreshadow-Payoff 数据构造方法实现，以下是本项目采用的操作化定义：
- Foreshadow(F): 较早句子引入未解释/未完成的叙事条件、物件、行动、规则、身份线索、梦境、诗词、承诺或关键话语。
- Trigger(T): 使伏笔可以被兑现的可观察叙事条件。
- Payoff(P): 较晚句子提供具体事件、解释、履行或回顾性重释，清偿 F 的叙事债务。
- 本步骤只产生候选，不等同最终三元组；优先召回，可以包含弱候选，但不能输出纯主题呼应。
- 每回 notes 是辅助证据，包含 unresolved setups、foreshadow notes、梦境/诗词/判词/物件等。F/P 的 index 仍必须指向摘要句子时间线；如果伏笔来自 notes 中的判词或诗词，请把 F index 指向“该判词/诗词出现”的摘要句，并在 rationale 中说明引用了哪条 note。
- 对话/人物话语包括承诺、警告、预言、追问、隐瞒、称呼、评价、异常反应等言语行为；这类伏笔通常使用 foreshadow_type="speech_act"。
- 如果较早伏笔在给定时间线内尚无具体 payoff，只能不输出该候选；不要为了覆盖伏笔而虚构 payoff。

硬性约束：
1. payoff_sentence_index 必须大于 foreshadow_sentence_index。
2. 二者至少间隔 2 个 summary sentences。
3. 不要输出同一事件的即时因果。
4. proposed_trigger 必须是可观察条件，不要写“命运展开”“气氛变化”这类抽象词。
5. 候选数量最多 {{max_candidates}} 个。

输出 JSON object：
{
  "candidates": [
    {
      "foreshadow_sentence_index": 0,
      "payoff_sentence_index": 4,
      "proposed_trigger": {
        "description": "...",
        "observable_conditions": ["..."]
      },
      "relation_description": "...",
      "foreshadow_type": "object|event|speech_act|rule|symbol|dream|poem|identity",
      "stage1_confidence": 0.0,
      "stage1_rationale": "..."
    }
  ]
}

摘要句子时间线：
{{summary_timeline}}

每回 notes：
{{chapter_notes}}
```
<!-- /prompt -->

<!-- prompt:candidate_verification version:honglou_ftp_verification_v3_full80 -->
```system
任务：严格判断一个候选 Foreshadow-Payoff 句对是否构成真实叙事回收，并按给定 rubric 决定是否形成 Foreshadow-Trigger-Payoff 三元组。下面的用户消息会完整定义术语、rubric 和输出格式。只依据给定摘要和窗口，不得使用外部知识。只输出 JSON。
```
```user
执行第二步/第三步：payoff 对齐验证和 rubric 过滤。

本步骤基于 Foreshadow-Payoff 数据构造方法实现，以下是本项目采用的操作化定义：
- Foreshadow(F): 较早文本引入具体但当时未完全解释/解决的叙事元素，包括事件、物件、规则、身份线索、梦境、诗词、承诺或关键对话/人物话语。
- Trigger(T): 使 F 有机会被兑现的可观察叙事条件，不能是抽象主题或命运概括。
- Payoff(P): 较晚文本提供新信息，履行、解决、解释或回顾性重释 F。
- 接受的三元组必须是叙事回收，不只是主题相似、意象重复、人物再次出现或读者联想。

候选：
candidate_id: {{candidate_id}}
F[{{foreshadow_sentence_index}}]: {{foreshadow_text}}
P[{{payoff_sentence_index}}]: {{payoff_text}}
proposed_trigger: {{proposed_trigger_json}}
relation_description: {{relation_description}}

Setup window:
{{setup_window}}

Payoff window:
{{payoff_window}}

Rubric:
1. setup_validity: F 是否引入具体叙事元素，且当时未完全解释/解决。
2. payoff_validity: P 是否提供新信息，履行、解决、解释或回顾性重释 F。
3. temporal_separation: F/P 是否有非平凡间隔，非即时因果。
4. foreshadow_justification: 读到 P 后，F 是否可合理回看为伏笔。
5. trigger_validity: Trigger 是否是可观察叙事条件，能解释 payoff 的时机。
6. connection_validity: F/P 是否不是主题呼应、意象重复或人物再次出现，而是真实因果回收。

如果任一关键项失败，accepted=false。

输出 JSON object：
{
  "accepted": true,
  "setup_validity": true,
  "payoff_validity": true,
  "temporal_separation": true,
  "foreshadow_justification": true,
  "trigger_validity": true,
  "connection_validity": true,
  "is_thematic_echo_only": false,
  "is_unsupported_by_evidence": false,
  "final_trigger": {
    "description": "...",
    "observable_conditions": ["..."]
  },
  "foreshadow_description": "...",
  "payoff_description": "...",
  "rationale": "...",
  "evidence_sentence_indices": [0, 4],
  "rejection_reason": ""
}
```
<!-- /prompt -->
