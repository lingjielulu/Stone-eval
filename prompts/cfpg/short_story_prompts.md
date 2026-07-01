# Short Story CFPG Prompt Templates

本文件是 `data/foreshadow_causality_benchmark` 短篇伏笔实验的权威 prompt 文件。脚本按 `prompt:key` 读取模板，运行时只替换 `{{placeholder}}`。

可用占位符：

- `short_story_candidate_extraction`: `{{story_id}}`, `{{story_title}}`, `{{language}}`, `{{max_candidates}}`, `{{paragraph_timeline}}`, `{{zh_paragraph_timeline}}`, `{{annotation_context}}`
- `short_story_candidate_verification`: `{{candidate_id}}`, `{{story_id}}`, `{{story_title}}`, `{{foreshadow_span}}`, `{{foreshadow_text}}`, `{{payoff_span}}`, `{{payoff_text}}`, `{{proposed_trigger_json}}`, `{{relation_description}}`, `{{setup_window}}`, `{{payoff_window}}`
- `short_story_tracking_decision`: `{{story_id}}`, `{{story_title}}`, `{{current_prefix}}`, `{{pending_pool_json}}`

<!-- prompt:short_story_candidate_extraction version:short_story_ftp_extraction_v2 -->
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

优先类型：
- object: 物件早期出现，后期发挥关键功能。
- rule: 规则/自然法则/社会规则早期建立，后文兑现。
- psychological: 心理异常或感官执念预示后续行为。
- spatial: 空间结构预示后续危险或行动路径。
- social: 社会习俗/制度压力预示后续悲剧。
- symbolic: 意象在后文形成主题性回收。
- red_herring: 早期误导线索，后文被重释。
- retrospective: 读到结尾后才确认前文是伏笔。

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
      "foreshadow_type": "object|rule|psychological|spatial|social|symbolic|red_herring|retrospective",
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
