"""
Emotional arc analysis for long-form story evaluation.

Inspired by:
    The emotional arcs of stories are dominated by six basic shapes (EPJ Data Science, 2016)
    https://arxiv.org/abs/1606.07772

6 universal emotional arcs:
    - Rags to Riches (rise)
    - Tragedy / Riches to Rags (fall)
    - Man in a Hole (fall-rise)
    - Icarus (rise-fall)
    - Cinderella (rise-fall-rise)
    - Oedipus (fall-rise-fall)

Applied to HongLou Meng: compare the emotional arc of original 80 chapters
against continuations to detect emotional trajectory drift.
"""

from dataclasses import dataclass, field
from enum import Enum


class ArcType(str, Enum):
    RISE = "rise"
    FALL = "fall"
    FALL_RISE = "fall-rise"
    RISE_FALL = "rise-fall"
    RISE_FALL_RISE = "rise-fall-rise"
    FALL_RISE_FALL = "fall-rise-fall"


ARC_LABELS = {
    ArcType.RISE: "白手起家 (Rags to Riches)",
    ArcType.FALL: "悲剧/从富到贫 (Tragedy)",
    ArcType.FALL_RISE: "洞里的人 (Man in a Hole)",
    ArcType.RISE_FALL: "伊卡洛斯 (Icarus)",
    ArcType.RISE_FALL_RISE: "灰姑娘 (Cinderella)",
    ArcType.FALL_RISE_FALL: "俄狄浦斯 (Oedipus)",
}


@dataclass
class SentimentPoint:
    chapter: str
    segment: int
    sentiment_score: float
    text_preview: str = ""


@dataclass
class EmotionArcResult:
    chapter: str
    model_name: str
    arc_type: ArcType | None = None
    arc_label: str = ""
    sentiment_curve: list = field(default_factory=list)
    correlation_with_original: float = 0.0
