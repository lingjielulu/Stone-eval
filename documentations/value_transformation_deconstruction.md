# 红楼梦剧情价值转化拆解 · 设计文档

## 一、动机

ScriptGeneration/Test 中的 schema 是一套**非线性交互叙事**的结构化表示（节点→选择→分支→结局），而《红楼梦》前80回是一部**线性长篇小说**。本实验的目标是：**将非线性 schema 适配为线性价值转化图（Value Transformation Graph），用于拆解《红楼梦》剧情结构。**

核心理论依据来自 Robert McKee《Story》：
> "A scene is a story event... that turns a value-charged condition of a character's life from positive to negative or negative to positive."

即：有效的场景/节点 = **发生了价值转化的故事事件**。

## 二、Schema 适配策略

### 2.1 原 Schema（ScriptGeneration/Test）

```
interactive_node (玩家选择点)
  ├─ choices[] → outcome_node (分支结果) → makes_available → 下个节点
  └─ 最终 → ending_node (结局)
```

特点：**多分支、玩家驱动、能力/价值双重测试**。

### 2.2 适配后 Schema（本实验）

```
scene_node (关键场景/价值转化点)
  ├─ character_decisions[] (角色做出的抉择)
  │    ├─ decision (实际选择)
  │    ├─ implicit_alternatives (隐含的其他可能)
  │    └─ value_transformation (由此引发的价值转化)
  ├─ consequences → transition_node → makes_available → 下个线性节点
  └─ 跨章连接: foreshadow_refs / payoff_refs
```

关键改动：

| 原字段 | 适配后 | 说明 |
|--------|--------|------|
| `interactive_node` | `scene_node` | 不再是玩家选择点，而是**线性故事中发生价值转化的关键场景** |
| `choices[]` (玩家选项) | `character_decisions[]` (角色抉择) | 记录角色实际做出的决定及其隐含的替代可能，以及由此带来的价值转化 |
| `outcome_node` (分支结果) | `transition_node` (过渡) | 连接两个场景的桥梁，线性递进 |
| `ending_node` | `ending_node` | 保留，但代表故事的自然结局而非玩家达成的结局 |
| `choice_type` (value/ability) | 移除 | 线性叙事无需区分能力测试 |
| `difficulty`, `time_pressure` | 移除 | 游戏机制字段 |
| — | `value_transformation` | **新增**：{ axis, from, to, turning_point } |
| — | `foreshadow_refs[]` | **新增**：关联已验证的伏笔-回收三元组 |
| — | `chapter_range` | **新增**：跨章跨度标记 |

### 2.3 非线性结构的线性化

原 schema 中 `outcome_node` 通过 `makes_available: [node_id]` 实现分支。在线性叙事中：
- 每个 `scene_node` 只有一个唯一的后续节点（或两三个分支汇合点，如宝钗/黛玉线交叠）
- `makes_available` 始终只包含 **一个** 下一节点ID
- 跨章伏笔通过 `foreshadow_refs` / `payoff_refs` 建立**非顺序连接**（这是 schema 的非线性能力在线性叙事中的最佳用途）

## 三、价值转化方法论

### 3.1 价值轴定义（Value Axes）

为《红楼梦》定义 8 条价值轴，每条轴有两个极端状态：

| 价值轴 | + 极 | − 极 | 说明 |
|--------|------|------|------|
| 兴 vs 衰 | 繁荣、权势、昌盛 | 萧条、败落、凋零 | 贾府的家族命运线 |
| 爱 vs 怨 | 亲密、理解、相知 | 猜忌、隔阂、怨恨 | 宝黛钗情感线 |
| 真 vs 假 | 真实、本真、觉悟 | 虚幻、伪装、执迷 | 全书哲学主题 |
| 聚 vs 散 | 团圆、欢聚、热闹 | 离散、冷清、孤独 | 宴席与离散的母题 |
| 自由 vs 束缚 | 自主、反抗、脱俗 | 礼教、命运、枷锁 | 宝玉的精神困境 |
| 情 vs 理 | 痴情、任性、天然 | 世故、克制、功利 | 宝玉 vs 贾政/宝钗 |
| 清 vs 浊 | 洁净、灵秀、女儿世界 | 污浊、功利、男人世界 | 宝玉的世界观 |
| 生 vs 死 | 生命、青春、活力 | 死亡、衰病、凋零 | 群芳命运的终极指向 |

### 3.2 转化识别规则

从 BookSum 摘要句中提取价值转化节点，依据以下信号：

1. **关键事件**（`key_events` 中的事件）——如"元春省亲""抄检大观园""黛玉焚稿"
2. **角色状态变化**（`character_state_changes`）——角色的情感/地位/关系发生了从+到−或−到+的改变
3. **诗歌/梦境/预言**——第五回判词、葬花吟、中秋联句等
4. **伏笔-回收对**（已验证的30个F-T-P三元组）——这些是跨章节的结构性连接

### 3.3 转化方向

每个节点的 `value_transformation` 记录一个或多个价值轴上的转化：

```json
{
  "value_transformations": [
    {
      "axis": "兴 vs 衰",
      "from": "盛极",
      "to": "将衰",
      "turning_point_event": "元春省亲时流泪说“当日既送我到那不得见人的去处”",
      "characters_involved": ["贾元春", "贾母", "王夫人"]
    }
  ]
}
```

## 四、节点层级设计

### 4.1 三层粒度

| 层级 | Group | 粒度 | 数量预估 | 示例 |
|------|-------|------|---------|------|
| 宏观弧 | `Arc` | 5幕结构 | ~8 | 序幕、兴起、鼎盛、转折、衰败、结局 |
| 中观节点 | `Act1..Act5` | 价值转化场景 | ~40-60 | 黛玉进府、宝钗认玉、元春省亲、宝玉挨打、抄检大观园… |
| 微观连接 | `Shared` | 跨章伏笔线 | ~30 | 30条已验证F-T-P三元组 |

### 4.2 Group 规划

```
groups: [
  "Prologue",      # 第1回：神话序幕（甄士隐梦幻识通灵）
  "Act1_Rise",     # 第2-18回：贾府兴盛期（黛玉进府→元春省亲）
  "Act2_Climax",   # 第19-53回：大观园鼎盛期（宝玉与众钗的诗酒生活）
  "Act3_Turn",     # 第54-69回：转衰期（探春理家→尤氏姐妹之死）
  "Act4_Fall",     # 第70-80回：加速败落（抄检大观园→晴雯之死→迎春误嫁）
  "Endings",       # 结局指向（80回末尾的衰落暗示）
  "ForeshadowLines" # 横跨多章的伏笔线节点
]
```

### 4.3 节点类型

```python
class SceneNode:    # 价值转化场景
    id, group, chapter_range, narrative, 
    character_decisions[], value_transformations[],
    trigger_condition, node_dependencies,
    foreshadow_refs[], payoff_refs[]

class TransitionNode: # 场景间过渡
    id, narrative, makes_available[]

class EndingNode:   # 结局指向
    id, ending_title, narrative, 
    value_alignment[], value_transformation_summary
```

## 五、与现有数据的集成

### 5.1 数据来源

- `data/processed/cfpg/honglou_booksum/original_80_chapter_summaries.jsonl`：80章 BookSum 风格摘要
- `data/processed/cfpg/summary_alignments/original_80_summary_sentence_timeline_*.jsonl`：504句摘要时间线
- `data/processed/cfpg/verified/honglou_ftp_triples_*.jsonl`：30条已验证 F-T-P 三元组

### 5.2 生成流程

```
504句摘要时间线
  → LLM 识别价值转化句 (用 value_axes 提示)
  → 合并相邻转化句为一个 SceneNode
  → 补充 character_decisions + value_transformations
  → 嵌入已验证的 F-T-P 三元组作为 foreshadow_refs / payoff_refs
  → 生成完整 structured_script JSON
```

### 5.3 输出位置

```
outputs/honglou_value_graph/
├── honglou_structured_script.json    # 完整结构脚本
├── honglou_value_graph_visualization.html # D3 交互式可视化
└── generation_summary.json           # 生成摘要统计
```

## 六、使用场景

1. **续书评估**：对比 80 回后的续书在价值转化图上是否符合原著的转化逻辑
2. **结构分析**：识别曹雪芹埋设的伏笔-回收结构密度
3. **生成指导**：作为 LLM 续写时的结构约束（"必须在下个节点完成从 X 到 Y 的价值转化"）
4. **跨作品比较**：与其他长篇小说的价值转化密度、弧线对比

## 七、局限与注意事项

1. **摘要失真**：BookSum 摘要是 LLM 生成的，可能遗漏、曲解或过分简化原著的价值转化
2. **LLM 先验知识**：识别价值转化时 LLM 可能带入对《红楼梦》的既有解读而非严格从摘要文本推断
3. **粒度选择**：每章 4-10 句摘要，约 504 句；但价值转化场景可能跨句、跨章，需要合适的聚合窗口
4. **线性强制**：原著虽然有主线，但也有并线叙事（如黛玉线和宝钗线交错），线性化会丢失一些平行性
