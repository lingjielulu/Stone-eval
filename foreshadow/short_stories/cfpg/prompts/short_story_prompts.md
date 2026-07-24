# Short Story CFPG Prompt Templates

本文件是 `foreshadow/short_stories/dataset` 短篇伏笔实验的权威 prompt 文件。脚本按 `prompt:key` 读取模板，运行时只替换 `{{placeholder}}`。

可用占位符：

- `short_story_candidate_extraction`: `{{story_id}}`, `{{story_title}}`, `{{language}}`, `{{max_candidates}}`, `{{paragraph_timeline}}`, `{{zh_paragraph_timeline}}`, `{{annotation_context}}`
- `short_story_candidate_verification`: `{{candidate_id}}`, `{{story_id}}`, `{{story_title}}`, `{{foreshadow_span}}`, `{{foreshadow_text}}`, `{{payoff_span}}`, `{{payoff_text}}`, `{{proposed_trigger_json}}`, `{{relation_description}}`, `{{setup_window}}`, `{{payoff_window}}`
- `short_story_tracking_decision`: `{{story_id}}`, `{{story_title}}`, `{{current_prefix}}`, `{{pending_pool_json}}`
- `short_story_fap_decision`: `{{story_id}}`, `{{story_title}}`, `{{current_context}}`, `{{foreshadow_description}}`
- `short_story_cfpg_decision`: `{{story_id}}`, `{{story_title}}`, `{{current_context}}`, `{{triple_json}}`
- `short_story_continuation`: `{{story_id}}`, `{{story_title}}`, `{{current_context}}`, `{{guidance}}`
- `short_story_continuation_judge`: `{{story_id}}`, `{{story_title}}`, `{{foreshadow_description}}`, `{{payoff_description}}`, `{{gold_continuation}}`, `{{generated_continuation}}`

<!-- prompt:short_story_candidate_extraction version:short_story_ftp_extraction_v3 -->
```system
你是短篇小说伏笔-触发-回收结构标注员。任务是在给定的全文段落时间线中，高召回抽取候选 Foreshadow-Trigger-Payoff 三元组。只能依据输入文本，不得使用外部知识或你对作品结局的先验记忆。只输出合法 JSON。
```
```user
请对下面的短篇小说段落时间线执行第一步：高召回候选识别。

作品：
- story_id: {{story_id}}
- title: {{story_title}}
- language: {{language}}

操作化定义：
- Foreshadow(F): 较早段落引入具体但当时未完全解释/解决的叙事元素，包括物件、异常、规则、空间结构、心理症状、承诺、警告、谎言、身份线索、象征物或关键话语。
- Trigger(T): 使伏笔进入可兑现状态的可观察叙事条件。Trigger 必须是文本中可以定位的事件、发现、行动、状态变化或条件满足，不要写“命运展开”“气氛成熟”这类抽象词。
- Payoff(P): 较晚段落提供具体事件、解释、履行、反转、否定、失败或主题性回收，用来清偿 F 的叙事债务。

本步骤只产生候选，不等同最终 gold。优先召回，但不要输出纯主题呼应或普通即时因果。
对于结构明确的短篇，通常应输出 3-8 个候选；宁可标为 low confidence，也不要因为要求过严而漏掉明显的 delayed setup/payoff。

硬性约束：
1. payoff_span 必须晚于 foreshadow_span。
2. F/P 之间应有非平凡间隔；普通相邻段落即时因果不要输出。
3. 每条候选必须给 proposed_trigger，且 trigger 必须可观察。
4. 每条候选必须给 paragraph span，例如 "P0012" 或 "P0012-P0015"。
5. 每条候选必须能在输入段落中找到证据。
6. 候选数量最多 {{max_candidates}} 个。
7. 顶层 JSON 必须包含 candidates 数组，严禁输出空对象 {}。
8. 如果没有合格候选，输出 {"candidates": []}。

分类必须分成两个互不混淆的维度：

1. primary_type 只描述伏笔在文本中的主要承载形式，必须选最主要的一种：
- object: 具体物件或可辨识实体。
- event: 已发生的行动、变化或感知事件。
- dialogue: 人物说出的信息、警告、承诺、描述或内心引语。
- rule: 自然规律、制度约束、社会规则或人物明确奉行的原则。
- environment_description: 空间布局、天气、地貌或环境危险描写。
- character_state: 人物持续的心理、身体、身份、欲望或行为状态。
- narrator_commentary: 叙述者直接给出的评论、预告或元叙事判断。

2. narrative_function 描述叙事作用：
- direct_setup: 直接建立后续行动或结果所需条件。
- anomaly: 引入当时无法解释的反常细节。
- misdirection: 诱导人物或读者形成后来被纠正的解释；red herring 应放在这里，不能作为 primary_type。
- warning: 提前说明风险、后果或应遵守条件。
- retrospective_reinterpretation: payoff 后才确认前文细节的真实意义。
- ironic_contrast: 通过前后命运或价值反差形成讽刺回收。
- symbolic_reframing: 后文以具体象征或评论重新界定前文意义。

输出 JSON object，字段严格如下：
{
  "candidates": [
    {
      "foreshadow_span": "P0001-P0002",
      "payoff_span": "P0030",
      "foreshadow_summary": "...",
      "payoff_summary": "...",
      "proposed_trigger": {
        "description": "...",
        "observable_conditions": ["..."]
      },
      "relation_description": "...",
      "primary_type": "object|event|dialogue|rule|environment_description|character_state|narrator_commentary",
      "narrative_function": "direct_setup|anomaly|misdirection|warning|retrospective_reinterpretation|ironic_contrast|symbolic_reframing",
      "payoff_type": "literal|ironic|symbolic|negative|misdirection|delayed_revelation",
      "stage1_confidence": "high|medium|low",
      "stage1_rationale": "..."
    }
  ]
}

原文段落时间线：
{{paragraph_timeline}}

中文辅助译文段落时间线（可能为空；只能辅助理解，gold evidence 仍必须回到原文段落）：
{{zh_paragraph_timeline}}

已有人工标注上下文（可能为空；若存在，只作参考，不要机械复制）：
{{annotation_context}}
```
<!-- /prompt -->

<!-- prompt:short_story_fap_decision version:short_story_fap_decision_v1 -->
```system
你是在线叙事状态判断器。只能根据已经出现的文本判断下一句是否应当回收给定伏笔，不得假设未来情节。只输出合法 JSON。
```
```user
作品：{{story_title}}（{{story_id}}）

未解决的伏笔：{{foreshadow_description}}

当前已读上下文：
{{current_context}}

判断下一句是否已经到了应当兑现该伏笔的时机。只有文本中出现了具体、可观察的充分条件时才触发；人物、物件或主题再次出现不算触发。

输出：
{"should_payoff": false, "confidence": 0.0, "evidence_segment_ids": [], "rationale": "..."}
```
<!-- /prompt -->

<!-- prompt:short_story_cfpg_decision version:short_story_cfpg_decision_v1 -->
```system
你是 CFPG codify gate。你维护显式 Foreshadow-Trigger-Payoff 因果谓词，只能根据已经出现的文本判断 Trigger 是否满足。只输出合法 JSON。
```
```user
作品：{{story_title}}（{{story_id}}）

待处理的结构化谓词：
{{triple_json}}

当前已读上下文：
{{current_context}}

逐项检查 trigger.observable_conditions。只有触发条件已由当前文本支持，且 payoff 尚未发生时，下一句才 should_payoff=true。不要因词汇相似而提前触发。

输出：
{"should_payoff": false, "trigger_satisfied": false, "payoff_already_observed": false, "confidence": 0.0, "evidence_segment_ids": [], "rationale": "..."}
```
<!-- /prompt -->

<!-- prompt:short_story_continuation version:short_story_continuation_v1 -->
```system
你是小说续写模型。续写一句，与原文语言、时态和叙事视角一致。不要解释任务，不要输出 JSON。
```
```user
作品：{{story_title}}（{{story_id}}）

当前文本：
{{current_context}}

控制信息：
{{guidance}}

只续写紧接着的一句话。如果控制信息要求兑现 payoff，应通过具体可观察事件自然完成，不要元叙事地说“伏笔得到了回收”。
```
<!-- /prompt -->

<!-- prompt:short_story_continuation_judge version:short_story_continuation_judge_v1 -->
```system
你是叙事蕴含评测器。比较模型续写与真实下一句是否沿着同一因果轨迹，并判断伏笔是否被兑现。只输出合法 JSON。
```
```user
作品：{{story_title}}（{{story_id}}）
伏笔：{{foreshadow_description}}
目标 payoff：{{payoff_description}}

真实下一句：
{{gold_continuation}}

模型续写：
{{generated_continuation}}

评分严格采用论文的三档 narrative entailment：
- 1.0：模型续写蕴含真实轨迹，关键事件、决定或揭示一致；允许措辞不同。
- 0.5：中性或相容，但没有实现相同的关键轨迹。
- 0.0：与真实轨迹或既有因果状态矛盾。

payoff_realized 只有在模型续写具体实现目标 payoff 时为 true。
输出：
{"label": "entailment|neutral|contradiction", "score": 0.5, "payoff_realized": false, "rationale": "..."}
```
<!-- /prompt -->

<!-- prompt:short_story_candidate_verification version:short_story_ftp_verification_v1 -->
```system
你是短篇小说 Foreshadow-Trigger-Payoff verifier。任务是严格判断一个候选是否构成真实叙事回收。只能依据给定段落窗口，不得使用外部知识。只输出合法 JSON。
```
```user
请验证下面候选是否构成真实 Foreshadow-Trigger-Payoff 三元组。

作品：
- story_id: {{story_id}}
- title: {{story_title}}

候选：
- candidate_id: {{candidate_id}}
- F {{foreshadow_span}}: {{foreshadow_text}}
- P {{payoff_span}}: {{payoff_text}}
- proposed_trigger: {{proposed_trigger_json}}
- relation_description: {{relation_description}}

Setup window:
{{setup_window}}

Payoff window:
{{payoff_window}}

Rubric：
1. setup_validity: F 是否引入具体叙事元素，且当时未完全解释/解决。
2. payoff_validity: P 是否提供新信息，履行、解决、解释、否定或回顾性重释 F。
3. temporal_separation: F/P 是否有非平凡间隔，非即时因果。
4. foreshadow_justification: 读到 P 后，F 是否可合理回看为伏笔。
5. trigger_validity: Trigger 是否是可观察叙事条件，能解释 payoff 的时机。
6. connection_validity: F/P 是否不是主题呼应、意象重复或人物再次出现，而是真实叙事回收。

拒绝条件：
- 只是主题相似或意象重复。
- 只是同一人物/物件再次出现，没有状态变化。
- 只是普通局部因果。
- Trigger 是抽象概念，不可观察。
- 证据窗口中看不到 payoff 对 setup 的清偿。

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
  "evidence_spans": ["P0001", "P0030"],
  "rejection_reason": ""
}
```
<!-- /prompt -->

<!-- prompt:short_story_tracking_decision version:short_story_tracking_v1 -->
```system
你是短篇小说伏笔状态追踪器。任务是在只看到当前前缀的情况下，判断 pending pool 中每个伏笔是否仍 pending、triggered、resolved 或 violated。不得使用未来文本。只输出合法 JSON。
```
```user
请基于当前故事前缀判断 pending pool 状态。

作品：
- story_id: {{story_id}}
- title: {{story_title}}

当前前缀：
{{current_prefix}}

pending pool:
{{pending_pool_json}}

状态定义：
- pending: F 已出现，但 T 未满足。
- triggered: T 已满足，P 应进入可兑现状态，但当前前缀尚未清楚 resolved。
- resolved: P 已在当前前缀中发生。
- violated: 当前前缀与 F/T/P 约束矛盾。

输出 JSON object：
{
  "decisions": [
    {
      "triple_id": "...",
      "status": "pending|triggered|resolved|violated",
      "trigger_satisfied": false,
      "evidence_spans": ["P0001"],
      "rationale": "..."
    }
  ]
}
```
<!-- /prompt -->
