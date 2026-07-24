# 红楼梦剧情价值转化图（Value Transformation Graph）

## 概述

基于 ScriptGeneration/Test 的**交互叙事 schema**，将其适配为**线性叙事价值转化图**，用于结构化解构《红楼梦》前80回的剧情。

核心理论：Robert McKee《Story》——有效的场景 = 发生了价值转化的故事事件（value-charged condition 从 + → − 或 − → +）。

## 目录结构

```
foreshadow/honglou/results/value_graph/
├── README.md                              # 本文件
├── honglou_structured_script.json         # 主体输出：结构化脚本 JSON
├── honglou_value_graph_visualization.html # D3 交互式可视化
└── generation_summary.json               # 生成摘要统计

foreshadow/honglou/scripts/
├── build_honglou_value_graph.py          # 生成结构化脚本
└── render_honglou_value_graph_html.py    # 生成 D3 可视化 HTML

foreshadow/honglou/docs/
└── value_transformation_deconstruction.md # 设计文档

stone_eval/
└── honglou_schema.py                     # 适配后的 Pydantic schema
```

## Schema 适配策略

| 原 schema | 适配后 | 改动 |
|-----------|--------|------|
| `interactive_node` (玩家选择) | `scene_node` (价值转化场景) | 移除游戏机制字段，加入 `value_transformations` + `character_decisions` |
| `outcome_node` (分支结果) | `transition_node` (线性过渡) | `makes_available` 始终指向唯一下一节点 |
| `choices[]` (多选项) | `character_decisions[]` (角色抉择) | 记录实际决定 + 隐含替代可能 |
| `ending_node` (多结局) | `ending_node` (结局指向) | 标记80回末尾的衰败方向 |

非线性的分支能力被复用为**跨章伏笔连接**（`foreshadow_refs` / `payoff_refs`），嵌入30条已验证的F-T-P三元组。

## 八条价值轴

1. **兴 vs 衰** — 贾府家族命运
2. **爱 vs 怨** — 宝黛钗情感线
3. **真 vs 假** — 全书哲学主题（幻与空）
4. **聚 vs 散** — 宴席与离散母题
5. **自由 vs 束缚** — 个人与封建礼教冲突
6. **情 vs 理** — 痴情与理性的冲突
7. **清 vs 浊** — 女儿世界 vs 男人世界
8. **生 vs 死** — 群芳命运的终极指向

## 生成结果

| 指标 | 数值 |
|------|------|
| 场景节点 | 30 (价值转化场景) |
| 过渡节点 | 29 (线性串联) |
| 结局节点 | 2 |
| 节点总计 | 61 |
| NPC | 27 (金陵十二钗正册 + 关键配角) |
| 物品 | 10 |
| 关系 | 8 组 |
| 空间 | 8 处 |
| 伏笔三元组 | 30 条 |

**按幕分布**: Prologue(1) → Act1_Rise(3) → Act2_Climax(13) → Act3_Turn(6) → Act4_Fall(7)

**价值轴覆盖**: 爱vs怨(11次) > 兴vs衰=聚vs散=生vs死(各9) > 清vs浊=情vs理=自由vs束缚(各4) > 真vs假(3)

## 使用方法

### 读取结构化脚本

```python
import json
from foreshadow.honglou.common.honglou_value_graph_schema import HonglouStructuredScript

with open("foreshadow/honglou/results/value_graph/honglou_structured_script.json") as f:
    script = HonglouStructuredScript.model_validate(json.load(f))

for node in script.nodes:
    if node.type == "scene_node":
        for vt in node.value_transformations:
            print(f"{node.title}: {vt.axis} [{vt.from_state} → {vt.to_state}]")
```

### 重新生成

```bash
# 使用缓存的 LLM 提取结果快速重建
python foreshadow/honglou/scripts/build_honglou_value_graph.py --force --skip-llm

# 完整重新生成（需要 API key）
python foreshadow/honglou/scripts/build_honglou_value_graph.py --force

# 重新生成 D3 交互式可视化
python foreshadow/honglou/scripts/render_honglou_value_graph_html.py
```

## 数据来源

- `foreshadow/honglou/results/cfpg/honglou_booksum/original_80_chapter_summaries.jsonl` — 80章 BookSum 风格摘要（DeepSeek v4-pro 生成）
- `foreshadow/honglou/results/cfpg/summary_alignments/original_80_summary_sentence_timeline_*.jsonl` — 504句摘要时间线
- `foreshadow/honglou/results/cfpg/verified/honglou_ftp_triples_*.jsonl` — 30条已验证 Foreshadow-Trigger-Payoff 三元组

## 设计局限

1. **摘要失真** — BookSum 摘要是 LLM 生成的，可能遗漏或简化原著的价值转化
2. **LLM 先验知识** — 识别价值转化时 LLM 可能带入对《红楼梦》的既有解读
3. **粒度限制** — 30个场景对80回长篇只是宏观概括，细节场景和日常过渡未收录
4. **线性强制** — 并线叙事（黛玉线/宝钗线交错）在线性化过程中丢失了平行性
