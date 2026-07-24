"""
红楼梦价值转化拆解 · 适配 Schema

从 ScriptGeneration/Test/schemas_extended.py 派生，将交互叙事 schema 适配为
线性文学叙事中的价值转化图（Value Transformation Graph）。

核心概念（Robert McKee, Story）：
    有效的场景 = 发生了价值转化的故事事件（value-charged condition 从 + → − 或 − → +）

节点类型：
    scene_node:     关键价值转化场景（替代 interactive_node）
    transition_node: 场景间过渡桥段
    ending_node:     结局指向

原 schema 的非线性结构（分支选项→不同结局）在线性叙事中被重新利用：
    - makes_available 始终指向唯一的下一节点（线性推进）
    - foreshadow_refs / payoff_refs 构建跨章节的非顺序连接
    - value_transformations 记录每个场景的价值转化

Usage:
    from foreshadow.honglou.common.honglou_value_graph_schema import (
        ValueTransformation, CharacterDecision,
        SceneNode, TransitionNode, EndingNode,
        HonglouStructuredScript,
        build_linear_chain, validate_script
    )
"""

from __future__ import annotations

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


# ============================================================
# Enums
# ============================================================

# ValueDirection and ValueAxis are plain strings (not enums) because LLM output
# may contain variant forms (e.g. "+ → − → +" for multi-step transformations).
# The canonical value axes are defined in default_factory of HonglouStructuredScript.value_axes.

class NodeType(str, Enum):
    SCENE = "scene_node"
    TRANSITION = "transition_node"
    ENDING = "ending_node"


class StoryGenre(str, Enum):
    TRAGEDY = "tragedy"
    COMEDY = "comedy"
    LEGEND = "legend"
    SATIRE = "satire"


# ============================================================
# Core models — 价值转化拆解专用
# ============================================================

class ValueTransformation(BaseModel):
    """一条价值轴上的单次转化。

    例如：黛玉焚稿断痴情
      axis: "爱 vs 怨"
      from_state: "痴恋"
      to_state: "绝望"
      direction: "+ → −"
    """
    axis: str = Field(description="价值轴，如 '兴 vs 衰', '爱 vs 怨' 等")
    from_state: str = Field(description="转化前的价值状态 (如 '荣盛', '相知', '团圆')")
    to_state: str = Field(description="转化后的价值状态 (如 '衰微', '猜忌', '离散')")
    direction: str = Field(description="转化方向，如 '+ → −', '− → +', 或复杂多步 '+ → − → +'")
    turning_point_event: str = Field(
        default="",
        description="触发转化的关键事件描述（一句话）"
    )
    characters_involved: list[str] = Field(
        default_factory=list,
        description="涉及的核心角色"
    )
    evidence_quote: str = Field(
        default="",
        description="原文证据（最多40字）"
    )


class CharacterDecision(BaseModel):
    """角色在场景中做出的关键抉择。

    替代原 schema 的 PlayerChoice。在线性叙事中角色只有一个实际选择，
    但可以记录其隐含的替代可能（这些替代构成文学张力）。
    """
    decision: str = Field(description="角色实际做出的决定")
    implicit_alternatives: list[str] = Field(
        default_factory=list,
        description="在那一刻隐含的替代选择（角色未走的路）"
    )
    value_tags: list[str] = Field(
        default_factory=list,
        description="该决定触及的价值标签，如 ['反抗', '顺从', '痴情']"
    )
    value_transformations: list[ValueTransformation] = Field(
        default_factory=list,
        description="由此决定引发的价值转化"
    )


# ============================================================
# NPC, Item, Relationship, Region（保留自原 schema）
# ============================================================

class NPC(BaseModel):
    name: str
    role: str = Field(default="", description="在故事中的角色定位 (如 '主角', '金陵十二钗正册')")
    appearance: str = ""
    background: str = ""
    character: str = ""
    abilities: list[str] = Field(default_factory=list)
    secrets: list[str] = Field(default_factory=list)
    fate_arc: str = Field(default="", description="命运弧线概括 (如 '从荣华到惨死')")
    poem_prophecy: str = Field(default="", description="判词/曲文揭示的命运")


class Item(BaseModel):
    item_id: str = Field(description="物品ID (i#### 格式)")
    name: str
    appearance: str = ""
    description: str = ""
    symbolic_meaning: str = Field(default="", description="象征意义")
    usages: list[str] = Field(default_factory=list)


class Relationship(BaseModel):
    agent_pair: list[str] = Field(min_length=2, max_length=2)
    rel_type: str = Field(description="关系类型: lovers, spouses, rivals, friends, family, master_servant 等")
    description: str = ""
    value_axis: Optional[str] = Field(default=None, description="主要在这条价值轴上波动，如 '爱 vs 怨'")
    key_turning_points: list[str] = Field(default_factory=list, description="关系的关键转折点描述")


class Region(BaseModel):
    name: str
    category: str = "zone"
    description: str = ""
    symbolic_meaning: str = Field(default="", description="空间象征意义 (如 大观园=青春乌托邦)")


# ============================================================
# Node Types
# ============================================================

class SceneNode(BaseModel):
    """关键价值转化场景节点。

    替代原 schema 的 interactive_node。不再有玩家选择，
    而是记录角色抉择及其引发的价值转化。
    """
    id: str = Field(description="唯一标识符，如 'a1_baoyu_meets_daiyu'")
    type: NodeType = Field(default=NodeType.SCENE)
    group: str = Field(description="所属组/幕，如 'Act1_Rise'")
    chapter_range: str = Field(
        default="",
        description="跨度，如 '003-003' 或 '005-005'"
    )
    title: str = Field(default="", description="场景标题，如 '宝黛初会'")

    trigger_condition: str = Field(
        default="自动触发",
        description="触发条件（线性叙事中通常为'前一节点完成'）"
    )
    node_dependencies: Optional[dict] = Field(
        default=None,
        description="前置依赖节点"
    )

    narrative: str = Field(
        default="",
        description="场景叙事描述（概括版，基于BookSum摘要）"
    )
    summary_sentence_indices: list[int] = Field(
        default_factory=list,
        description="对应的摘要句 global_sentence_index 列表"
    )

    character_decisions: list[CharacterDecision] = Field(
        default_factory=list,
        description="角色的关键抉择"
    )
    value_transformations: list[ValueTransformation] = Field(
        default_factory=list,
        description="场景中发生的价值转化"
    )

    npc_states: dict[str, dict] = Field(default_factory=dict)

    foreshadow_refs: list[str] = Field(
        default_factory=list,
        description="关联的伏笔 F-T-P 三元组 ID，如 'honglou:original_80:ftp:000001'"
    )
    payoff_refs: list[str] = Field(
        default_factory=list,
        description="关联的回收 F-T-P 三元组 ID"
    )


class TransitionNode(BaseModel):
    """场景间过渡节点。

    替代原 schema 的 outcome_node。线性叙事中连接两个 scene_node。
    """
    id: str
    type: NodeType = Field(default=NodeType.TRANSITION)
    group: str = ""
    trigger_condition: str = "前一节点完成"
    node_dependencies: Optional[dict] = None
    narrative: str = Field(default="", description="过渡叙述")
    makes_available: list[str] = Field(
        default_factory=list,
        description="解锁的下一节点ID（线性叙事中通常只有1个）"
    )
    makes_unavailable: list[str] = Field(default_factory=list)


class EndingNode(BaseModel):
    """结局指向节点。

    标记故事弧线的终结方向。因原作80回未完，此处置指向性结局。
    """
    id: str
    type: NodeType = Field(default=NodeType.ENDING)
    group: str = "Endings"
    trigger_condition: str = ""
    ending_title: str = ""
    narrative: str = ""
    value_alignment: list[str] = Field(
        default_factory=list,
        description="此结局与哪些价值侧对齐"
    )
    value_transformation_summary: str = Field(
        default="",
        description="全篇价值转化的总结"
    )


# ============================================================
# Top-Level Script
# ============================================================

class HonglouStructuredScript(BaseModel):
    """红楼梦结构脚本（顶层）。"""
    title: str = "红楼梦"
    story_type: StoryGenre = StoryGenre.TRAGEDY
    genre_tags: list[StoryGenre] = Field(default_factory=lambda: [StoryGenre.TRAGEDY, StoryGenre.LEGEND])
    value_axes: list[str] = Field(
        default_factory=lambda: [
            "兴 vs 衰", "爱 vs 怨", "真 vs 假", "聚 vs 散",
            "自由 vs 束缚", "情 vs 理", "清 vs 浊", "生 vs 死",
        ]
    )
    version: str = "0.1.0"
    version_notes: str = "基于BookSum摘要+价值转化方法论的初次拆解"

    source: str = Field(
        default="foreshadow/honglou/results/cfpg/honglou_booksum/original_80_chapter_summaries.jsonl",
        description="摘要数据来源"
    )
    chapter_count: int = Field(default=80, description="章数")
    summary_sentence_count: int = Field(default=504, description="摘要句数")
    ftp_triple_count: int = Field(default=30, description="已验证F-T-P三元组数")

    groups: list[str] = Field(
        default_factory=lambda: [
            "Prologue",
            "Act1_Rise",
            "Act2_Climax",
            "Act3_Turn",
            "Act4_Fall",
            "Endings",
            "ForeshadowLines",
        ]
    )
    start_nodes: list[str] = Field(default_factory=list)
    endings: list[str] = Field(default_factory=list)

    npc: list[NPC] = Field(default_factory=list)
    items: list[Item] = Field(default_factory=list)
    relationships: list[Relationship] = Field(default_factory=list)
    regions: list[Region] = Field(default_factory=list)

    nodes: list[SceneNode | TransitionNode | EndingNode] = Field(
        default_factory=list,
        description="所有节点（scene + transition + ending）"
    )

    # 跨章伏笔线索引
    foreshadow_lines: list[dict] = Field(
        default_factory=list,
        description="已验证F-T-P三元组的结构化记录"
    )


# ============================================================
# Utilities
# ============================================================

def build_linear_chain(scene_nodes: list[SceneNode]) -> list[TransitionNode]:
    """为线性场景列表自动生成 transition_node 链。"""
    transitions = []
    for i in range(len(scene_nodes) - 1):
        t = TransitionNode(
            id=f"trans_{i:03d}",
            group=scene_nodes[i].group,
            narrative=f"从「{scene_nodes[i].title}」过渡到「{scene_nodes[i+1].title}」",
            makes_available=[scene_nodes[i + 1].id],
        )
        transitions.append(t)
    return transitions


def validate_script(script: HonglouStructuredScript) -> list[str]:
    """验证脚本结构完整性。"""
    errors = []
    node_ids = {n.id for n in script.nodes}
    scene_ids = {n.id for n in script.nodes if n.type == NodeType.SCENE}
    transition_ids = {n.id for n in script.nodes if n.type == NodeType.TRANSITION}
    ending_ids = {n.id for n in script.nodes if n.type == NodeType.ENDING}

    # 检查 makes_available 引用完整性
    for n in script.nodes:
        if hasattr(n, "makes_available"):
            for target in n.makes_available:
                if target not in node_ids:
                    errors.append(f"Node '{n.id}' makes_available '{target}' not found")

    # 检查 start_nodes 有效性
    for sid in script.start_nodes:
        if sid not in node_ids:
            errors.append(f"start_node '{sid}' not in nodes")

    # 检查 endings 有效性
    for eid in script.endings:
        if eid not in ending_ids:
            errors.append(f"ending '{eid}' not found or not an ending_node")

    # 检查 F-T-P 引用
    all_ftp_ids = {f["id"] for f in script.foreshadow_lines}
    for n in script.nodes:
        if hasattr(n, "foreshadow_refs"):
            for ref in n.foreshadow_refs:
                if ref not in all_ftp_ids:
                    errors.append(f"foreshadow_ref '{ref}' in node '{n.id}' not found in foreshadow_lines")
        if hasattr(n, "payoff_refs"):
            for ref in n.payoff_refs:
                if ref not in all_ftp_ids:
                    errors.append(f"payoff_ref '{ref}' in node '{n.id}' not found in foreshadow_lines")

    return errors
