"""
Character social network analysis for story evaluation.

Inspired by:
    Evaluating LLM Story Generation through Large-scale Network Analysis
    of Social Structures (NeurIPS 2025)
    https://arxiv.org/abs/2510.18932

Builds signed character networks from text and computes:
    - edge density
    - average clustering coefficient
    - assortative mixing
    - positive/negative edge ratio (social bias detection)
"""

from dataclasses import dataclass, field


@dataclass
class CharacterNode:
    name: str
    mentions: int = 0
    dialogue_turns: int = 0


@dataclass
class CharacterEdge:
    source: str
    target: str
    weight: float
    sentiment: float = 0.0  # positive > 0, negative < 0


@dataclass
class NetworkMetrics:
    num_characters: int
    num_edges: int
    edge_density: float
    avg_clustering: float
    assortativity: float
    positive_edge_ratio: float
    avg_interaction_weight: float


@dataclass
class NetworkResult:
    chapter: str
    model_name: str
    metrics: NetworkMetrics | None = None
    characters: list = field(default_factory=list)
    edges: list = field(default_factory=list)
