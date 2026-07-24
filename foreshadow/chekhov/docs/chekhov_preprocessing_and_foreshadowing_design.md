# 契诃夫语料预处理与伏笔分析设计

## 目标

基于 `foreshadow/chekhov/dataset/chekhov_short_stories.txt` 构建一个可复现的契诃夫短篇小说语料库，并将该语料库作为后续伏笔提取、回收匹配和跨作品统计汇总的基础。

预处理阶段必须是确定性的、可审计的。伏笔分析阶段之后可以加入模型辅助标注，但它应当消费这里生成的稳定故事 ID、规范标题、文本 span 和语料 manifest。

## 来源特征

源文本来自 Project Gutenberg #57333，是一个汇编文本，而不是每篇故事一个独立文件。它包含：

| 区域 | 处理方式 |
|---|---|
| Gutenberg 元数据 | 从故事语料中排除。 |
| `CONTENTS OF EACH BOOK` | 用作标题目录。 |
| `IN ALPHABETICAL ORDER` 索引 | 从故事语料中排除。 |
| 故事正文区域 | 从索引之后最后一个 `THE HORSE-STEALERS` 标题开始。 |
| 混合选集条目 | 只有检测到正文标题时才保留；仅出现在目录中的非契诃夫条目保持 unmatched。 |

源文本存在重复译本和排版缺陷。例如：

| 缺陷 | 处理方式 |
|---|---|
| `THE BET`、`TYPHUS`、`ENEMIES` 等重复标题 | 全部保存在 `stories_all`；在 `stories_canonical` 中选择最长片段。 |
| `GOUSSIEV` 与 `GUSEV` 的别名拼写 | 规范标题归一为 `GUSEV`；每条记录保留原始标题。 |
| `... human language. MY LIFE` 这类正文粘连标题 | 在切分前插入故事边界。 |
| `JOY IT was...` 这类标题和正文首行同处一行 | 当前面有空行时，拆成标题行和正文行。 |
| `THE LADY WITH THE TOY / DOG` 这类换行标题 | 在边界检测前修复。 |

## 当前流水线

脚本：`foreshadow/chekhov/scripts/preprocess_chekhov.py`

1. 归一化换行符并去除行尾空白。
2. 从 `CONTENTS OF EACH BOOK` 中解析有序标题候选。
3. 在最后一个 `THE HORSE-STEALERS` 标题处定位故事正文起点。
4. 修复已知和通用的标题粘连缺陷。
5. 根据目录标题检测故事边界，支持副标题和罗马数字章节。
6. 归一化故事文本：
   - 修复 `snow-\nstorm` 这类跨行断词；
   - 合并段落内部的物理换行；
   - 保留段落分隔。
7. 输出全部检测片段和规范语料。
8. 生成统计信息、重复标题索引和 manifest。

## 输出 Schema

每条 JSONL 记录包含：

| 字段 | 含义 |
|---|---|
| `story_id` | 稳定 slug 加重复出现序号。 |
| `source_order` | 在正文中检测到的片段顺序。 |
| `occurrence` | 该规范标题的出现次数。 |
| `title` | 匹配到的源标题。 |
| `canonical_title` | 用于分组的归一化标题。 |
| `heading_line` | 修复后的原始检测标题行。 |
| `source_start_line`, `source_end_line` | 修复后正文区域坐标系中的行号范围。 |
| `word_count`, `paragraph_count`, `chapter_count`, `char_count` | 基础长度特征。 |
| `sha256_12` | 规范化故事文本的短哈希。 |
| `quality_flags` | 重复、别名或排版敏感标记。 |
| `text` | 规范化后的故事文本。 |

## 当前语料统计

由当前脚本生成：

| 指标 | 数值 |
|---|---:|
| 已解析目录标题 | 218 |
| 已检测故事片段 | 213 |
| 规范故事记录 | 201 |
| 规范语料总词数 | 845,027 |
| 每篇故事词数中位数 | 2,242 |
| 重复规范标题 | 12 |
| 未匹配目录标题 | 16 |

这 16 个未匹配目录标题保留在 `processed/manifest.json` 中；它们大多是源目录列出的非契诃夫选集条目，但该切分器没有将其输出为契诃夫故事正文。

## 伏笔分析需求

下一阶段不仅要识别孤立的伏笔候选，还应识别它们后续是否被回收，以及如何回收。一个有用的基本单位是 setup-payoff pair（铺垫-回收对）。

建议记录 schema：

| 字段 | 含义 |
|---|---|
| `foreshadow_id` | 稳定 ID：故事 ID 加局部序号。 |
| `story_id`, `canonical_title` | 关联到规范化语料。 |
| `setup_text` | setup 的短证据引文或释义 span。 |
| `setup_location` | 段落索引、句子索引，以及可选字符偏移。 |
| `payoff_text` | 回收证据 span；未回收信号可为空。 |
| `payoff_location` | 段落、句子、偏移位置；可为空。 |
| `signal_type` | 物件、预言、警告、重复母题、反讽对照、人物秘密、环境征兆、对话线索、结构平行。 |
| `payoff_type` | 字面应验、反讽倒置、延迟揭示、主题回响、误导线索、未回收。 |
| `confidence` | 0-1 置信度或序数标签。 |
| `explanation` | 一句简洁说明：为什么认为 setup 和 payoff 相关。 |
| `characters` | 涉及的人物名；如果可检测。 |
| `motifs` | 重复出现的物件、短语、地点、疾病、债务、信件、天气征兆或社会线索。 |
| `evidence_policy` | 证据来源：规则生成、模型辅助或人工验证。 |

## 伏笔流水线建议

1. **句子与段落索引**
   - 增加确定性的英文散文句子切分器。
   - 输出 `processed/story_units.jsonl`，包含段落 ID 和句子 ID。

2. **setup 候选提取**
   - 规则优先的第一遍：
     - 早期引入的显著物件；
     - 警告、誓言、预言、梦、信件、债务、疾病、武器、旅行计划；
     - 重复出现的异常短语或意象；
     - 前三分之一出现、后三分之一复现的细节。
   - 可选 LLM 步骤：
     - 输出受约束的 JSON；
     - 证据 span 必须引用或指向已有句子 ID；
     - 不允许没有来源锚点的自由解释。

3. **payoff 匹配**
   - 在后续故事单元中搜索词汇复现、实体复现、语义复现或反转。
   - 强制时间顺序：payoff 必须发生在 setup 之后。
   - 允许未回收 setup，但必须显式标记。

4. **验证**
   - 拒绝 setup/payoff 证据过于泛化的配对。
   - 至少要求一个具体共享锚点：物件、短语、人物、事件、地点或母题。
   - 不静默丢弃不确定案例，而是以较低置信度保存。

5. **统计与摘要**
   - 按故事统计：setup 数、已回收数、未回收数、setup-payoff 距离。
   - 按长度桶统计：每 1,000 词的伏笔密度。
   - 按 signal type 统计：物件线索、对话警告、母题回响等。
   - 按 payoff type 统计：字面、反讽、主题、误导。
   - 跨故事汇总：契诃夫常见的伏笔机制。

## 建议后续文件

| 路径 | 用途 |
|---|---|
| `scripts/index_story_units.py` | 为规范语料建立段落/句子索引。 |
| `scripts/extract_foreshadowing.py` | 基于规则和可选模型辅助的候选提取。 |
| `processed/story_units.jsonl` | 已索引的句子和段落。 |
| `processed/foreshadow_candidates.jsonl` | 原始 setup 候选。 |
| `processed/foreshadow_pairs.jsonl` | 匹配后的 setup-payoff 对。 |
| `reports/chekhov_foreshadowing_stats.md` | 面向人工阅读的伏笔统计摘要。 |

## 待决策项

| 决策 | 默认建议 |
|---|---|
| 重复译本 | 聚合统计使用 `stories_canonical`；翻译对比时检查 `stories_all`。 |
| 证据粒度 | 先使用句子 ID；只有需要时再增加字符偏移。 |
| LLM 使用方式 | 仅在确定性候选生成之后使用；必须要求句子 ID 证据。 |
| 人工审核 | 优先审核影响较大的长篇：`THE DUEL`、`THE STEPPE`、`MY LIFE`、`WARD NO. 6`、`IN THE RAVINE`。 |
