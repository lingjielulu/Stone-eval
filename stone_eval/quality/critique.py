"""
Long story quality evaluation via summary-based critique.

Inspired by NovelCritique / LongStoryEval (ACL 2025):
    What Matters in Evaluating Book-Length Stories?
    https://github.com/DingyiYang/LongStoryEval

Evaluates stories across 8 top-level criteria weighted for Chinese classical novels:
    1. 情节 (Plot)
    2. 人物 (Characters)
    3. 主题 (Theme)
    4. 世界观 (World-building)
    5. 写作质量 (Writing Quality)
    6. 情感 (Emotion)
    7. 章回结构 (Chapter Structure) — Chinese novel specific
    8. 伏笔兑现 (Foreshadowing Payoff) — Key for HongLou Meng
"""

from dataclasses import dataclass, field

CRITIQUE_CRITERIA = {
    "情节": "故事线索是否连贯、推进是否自然、是否有起伏张弛",
    "人物": "人物性格是否一致、人物关系是否合理、人物命运是否符合判词约束",
    "主题": "是否延续原作的悼亡/警世/自悔主旨，不背离核心意图",
    "世界观": "家族制度、礼法秩序、神话背景是否与前80回一致",
    "写作质量": "文言/白话比例是否恰当、笔法是否近曹氏风格、辞藻是否典雅",
    "情感": "情感表达是否克制含蓄、是否以形写神而非直白宣泄",
    "章回结构": "回目对联质量、回来-回末格式是否规范、伏笔钩子是否到位",
    "伏笔兑现": "判词/灯谜/诗词中的谶语是否在后续情节中合理应验",
}

CRITIQUE_PROMPT = """你是一位古典文学评论家。请根据以下标准评估这篇续写的质量。

评分标准（每项 1-10 分）：

{criteria}

续写摘要：
{summary}

请为每项评分并给出简评，格式如下：

## 总评分：X/10

{aspects_format}

## 总体评价
（1-2 句总结）
"""


@dataclass
class CritiqueScore:
    aspect: str
    score: float
    comment: str


@dataclass
class CritiqueResult:
    chapter: str
    model_name: str
    overall_score: float
    aspect_scores: list = field(default_factory=list)
    summary: str = ""


def build_critique_prompt(summary: str) -> str:
    criteria_text = "\n".join(f"- {k}：{v}" for k, v in CRITIQUE_CRITERIA.items())
    aspects_format = "\n".join(f"### {k}：X/10\n（简评）" for k in CRITIQUE_CRITERIA)
    return CRITIQUE_PROMPT.format(
        criteria=criteria_text,
        summary=summary,
        aspects_format=aspects_format,
    )
