"""
Consistency error detection for long-form Chinese classical novel continuation.

Inspired by ConStory-Bench (ACL 2026):
    Lost in Stories: Consistency Bugs in Long Story Generation by LLMs
    https://github.com/Picrew/ConStory-Bench

5 categories, 19 subtypes adapted for Chinese classical novels:
    - Characterization: memory contradictions, knowledge conflicts, skill/power fluctuations
    - Factual Detail: appearance mismatches, nomenclature confusions, quantitative errors
    - Narrative Style: perspective shifts, tone inconsistencies, style breaks
    - Timeline & Plot: time contradictions, duration errors, causality violations, abandoned plots
    - World-building & Setting: rule violations, social norm conflicts, geographical contradictions
"""

from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# prompt templates — adapted for Chinese classical novels
# ---------------------------------------------------------------------------

CHARACTERIZATION_PROMPT = """你是一位古典小说审稿人，正在检查续写章节中的人物一致性。

请读以下原文片段和续写片段，检查续写中是否存在以下人员物一致性问题：
1. 记忆矛盾：人物忘记了前文中已知的事实
2. 知识冲突：人物表现出不应该具备的知识
3. 性格偏离：人物的言行与前文建立的性格严重不符
4. 能力波动：人物的能力/权力出现不合理的突变

原文片段：
{source_text}

续写片段：
{continuation_text}

请列出所有发现的不一致问题，格式如下：
- [类别] 原文依据 (原文中的具体文字) -> 续文问题 (续文中的具体文字) -> 说明

如果没有发现问题，回复"无一致性问题"。
"""

FACTUAL_DETAIL_PROMPT = """你是一位古典小说审稿人，正在检查续写章节中的事实细节一致性。

请读以下原文片段和续写片段，检查续写中是否存在以下问题：
1. 外貌矛盾：人物的外貌特征与原文描述不符
2. 称谓错误：人物称谓、别号使用错误
3. 数量错误：物品数量、时间跨度等数值错误
4. 服饰/器皿错误：不符合时代或前文设定

原文片段：
{source_text}

续写片段：
{continuation_text}

请列出所有发现的不一致问题，格式如下：
- [类别] 原文依据 -> 续文问题 -> 说明

如果没有发现问题，回复"无一致性问题"。
"""

NARRATIVE_STYLE_PROMPT = """你是一位古典小说审稿人，正在检查续写章节的叙事风格一致性。

请读以下原文片段和续写片段，检查续写中是否存在以下问题：
1. 视角偏移：叙述视角在不该切换的地方突然切换
2. 语气断裂：叙述语气突然从典雅变为通俗，或反之
3. 文体失调：诗词联句等的格律/韵律使用错误
4. 章回体违规：开头、结尾的章回体格式不符合惯例

原文片段（含回末、回目）：
{source_text}

续写片段：
{continuation_text}

请列出所有发现的不一致问题，格式如下：
- [类别] 原文依据 -> 续文问题 -> 说明

如果没有发现问题，回复"无一致性问题"。
"""

TIMELINE_PLOT_PROMPT = """你是一位古典小说审稿人，正在检查续写章节的时间线与情节一致性。

请读以下原文片段和续写片段，检查续写中是否存在以下问题：
1. 时间矛盾：时间顺序与原文不可调和
2. 时长错误：事件持续时间不合理
3. 因果断裂：续文的因果逻辑与前文不贯通
4. 伏笔丢失：前文明确伏笔在续文中无声无息消失
5. 人物出场失误：已死、远嫁、出家、失踪人物错误出场

原文片段：
{source_text}

续写片段：
{continuation_text}

请列出所有发现的不一致问题，格式如下：
- [类别] 原文依据 -> 续文问题 -> 说明

如果没有发现问题，回复"无一致性问题"。
"""

WORLD_BUILDING_PROMPT = """你是一位古典小说审稿人，正在检查续写章节的世界观一致性。

请读以下原文片段和续写片段，检查续写中是否存在以下问题：
1. 制度违例：违反清代/小说设定的礼法、家族制度
2. 地理矛盾：地理位置、建筑格局与前文不符
3. 社会规范冲突：与小说设定的社会阶层行为规范矛盾
4. 神话体系矛盾：与小说的神话框架/太虚幻境设定冲突

原文片段：
{source_text}

续写片段：
{continuation_text}

请列出所有发现的不一致问题，格式如下：
- [类别] 原文依据 -> 续文问题 -> 说明

如果没有发现问题，回复"无一致性问题"。
"""

CATEGORY_PROMPTS = {
    "characterization": CHARACTERIZATION_PROMPT,
    "factual_detail": FACTUAL_DETAIL_PROMPT,
    "narrative_style": NARRATIVE_STYLE_PROMPT,
    "timeline_plot": TIMELINE_PLOT_PROMPT,
    "world_building": WORLD_BUILDING_PROMPT,
}

CATEGORY_LABELS = {
    "characterization": "人物一致性",
    "factual_detail": "事实细节",
    "narrative_style": "叙事风格",
    "timeline_plot": "时间线与情节",
    "world_building": "世界观与设定",
}


@dataclass
class ConsistencyError:
    category: str
    source_evidence: str
    continuation_issue: str
    explanation: str


@dataclass
class ConsistencyResult:
    chapter: str
    model_name: str
    total_errors: int
    errors_by_category: dict = field(default_factory=dict)
    errors: list = field(default_factory=list)


def build_judge_prompt(category: str, source_text: str, continuation_text: str) -> str:
    template = CATEGORY_PROMPTS.get(category)
    if template is None:
        raise ValueError(f"Unknown category: {category}. Valid: {list(CATEGORY_PROMPTS)}")
    return template.format(source_text=source_text, continuation_text=continuation_text)
