# 伏笔与因果短篇小说 Benchmark

这个目录用于建立一批适合伏笔系统和因果系统使用的中短篇小说样本。它不是文学评论项目，而是一个可清洗、可标注、可校验、可扩展的数据基础，用来评测系统是否能识别：

- 早期伏笔、误导线索和象征性照应
- 触发事件与后文 payoff
- 事件之间的因果边，而不只是时间顺序
- 人物动机、知识状态、误解和心理压力
- 后续长篇续写所需的未回收线索与因果约束

## 目录结构

```text
data/foreshadow_causality_benchmark/
  novels/                # 短篇小说数据
    raw_texts/           # 下载的公版原始文本或 API 返回
    normalized_texts/    # 切出单篇后的 UTF-8 段落编号文本
    raw_texts_zh/        # 中文译文原始文本；来源授权状态在审计文件中逐条标注
    normalized_texts_zh/ # 中文译文清洗结果；授权不明来源仅用于内部比对
    annotations/         # 人工校正后的 YAML 标注
    annotations/candidates/
                         # 弱规则生成的候选事件/伏笔/因果提示
    cfpg/                # 短篇小说 CFPG 抽取运行结果
  poetry/                # 诗词数据
  schemas/               # JSON Schema
  scripts/               # 下载、清洗、候选生成、校验脚本
  evaluation/            # 后续放评测输入/输出格式
  docs/                  # 后续放标注规范、批次说明
```

## 当前样本

核心 10 篇候选已全部落地。《摸彩》(The Lottery) 仍处版权保护，以 Phase 2 的《最后一片叶子》、《罗生门》补位：

| story_id | 作品 | 语言 | 来源 | 当前状态 |
| --- | --- | --- | --- | --- |
| `speckled_band` | The Adventure of the Speckled Band | EN | Project Gutenberg #1661 | 原文、规范化文本、样例标注 |
| `red_headed_league` | The Red-Headed League | EN | Project Gutenberg #1661 | 原文、规范化文本 |
| `necklace` | The Diamond Necklace | EN | Project Gutenberg #3090 | 原文、规范化文本、样例标注 |
| `gift_of_the_magi` | The Gift of the Magi | EN | Project Gutenberg #7256 | 原文、规范化文本 |
| `last_leaf` | The Last Leaf | EN | Project Gutenberg #3707 | 原文、规范化文本 |
| `tell_tale_heart` | The Tell-Tale Heart | EN | Project Gutenberg #2148 | 原文、规范化文本 |
| `cask_of_amontillado` | The Cask of Amontillado | EN | Project Gutenberg #2148 | 原文、规范化文本 |
| `to_build_a_fire` | To Build a Fire | EN | Project Gutenberg #2429 | 原文、规范化文本、样例标注 |
| `medicine` | 藥 | ZH | Wikisource | 原文 API、规范化文本、样例标注 |
| `cricket` | 促織 | ZH | Wikisource | 原文 API、规范化文本、样例标注 |
| `rashomon` | 羅生門 | JA | 青空文庫 (aozora.gr.jp) | 原文、规范化文本 |

所有当前原文来源均按公版文本处理。`metadata.source_url` 记录了具体下载入口。

8 篇非中文原文已补齐中文译文清洗文件，位于 `novels/normalized_texts_zh/`。这些译文来自中文网站转载，译者和授权状态未逐篇确认；`docs/chinese_translation_audit.json` 记录了每个来源 URL、抽取格式和 `license_note`。在公开发布或引用译文正文前，需要替换为公版/授权译本或完成版权核验。

当前中文译文来源概览：

| story_id | 中文题名 | 中文来源状态 |
| --- | --- | --- |
| `speckled_band` | 斑点带子案 | 名著小说网转载；授权未确认 |
| `red_headed_league` | 红发会 | 名著小说网转载；授权未确认 |
| `necklace` | 项链 | 可阅文学网转载；授权未确认 |
| `gift_of_the_magi` | 麦琪的礼物 | 可阅文学网转载；授权未确认 |
| `last_leaf` | 最后一片叶子 | 中华典藏网转载；授权未确认 |
| `tell_tale_heart` | 泄密的心 | chinesebooks.github.io 转载；授权未确认 |
| `cask_of_amontillado` | 一桶白葡萄酒 | 搜狐文章转载；授权未确认 |
| `to_build_a_fire` | 生火 | 简书译文；授权未确认 |


## 数据集设计

详细选篇原则、核心 10 篇候选、三阶段建设方案和当前 seed 样本定位见：

- `docs/dataset_design.md`

简要原则是：优先选择结构信号强、伏笔回收明确、因果链清楚、标注一致性较高且可合法获取的中短篇。第一阶段重点是让流程可运行，所以先用推理、反转、自然主义、复仇/犯罪等样本；暂不优先选择超长篇、强意识流、过度开放隐喻文本或高度依赖外部文化注释的文本。

## Schema 核心结构

每篇作品是一份 YAML，包含：

- `metadata`: 作品、来源、版权、公版状态、结构类型
- `annotation_guide`: 本篇标注重点和边界说明
- `events`: 事件节点，含段落跨度、参与者、地点、时间、事件类型、确定性、叙事现实层级
- `causal_edges`: 因果边，关系类型包括 `causes`, `enables`, `motivates`, `prevents`, `reveals`, `misleads_about`, `symbolically_echoes`, `contradicts`
- `foreshadowing_units`: 伏笔-触发-payoff 三元组
- `characters`: 人物稳定特征，以及关键事件下的动机、知识状态、情绪和目标

完整字段约束见 `schemas/story_schema.json`。

## 运行流程

下载来源文本：

```bash
python data/foreshadow_causality_benchmark/scripts/download_sources.py
```

切分并规范化文本：

```bash
python data/foreshadow_causality_benchmark/scripts/prepare_texts.py
```

为某篇生成弱候选，供人工校正：

```bash
python data/foreshadow_causality_benchmark/scripts/build_candidates.py speckled_band
```

校验所有 YAML 标注：

```bash
python data/foreshadow_causality_benchmark/scripts/validate_dataset.py
```

## 如何新增一篇小说

1. 将公版或授权原文放入 `novels/raw_texts/`，并记录来源 URL。
2. 在 `scripts/prepare_texts.py` 的 `STORIES` 中增加 `StorySpec`，写清 `story_id`、原文文件、起止标题和 `min_line`。
3. 运行 `prepare_texts.py`，确认 `novels/normalized_texts/{story_id}.txt` 段落编号正确。
4. 运行 `build_candidates.py {story_id}` 生成弱候选。
5. 复制现有 `novels/annotations/*.yaml` 的结构，人工写入/校正事件、因果边、伏笔三元组和人物状态。
6. 运行 `validate_dataset.py`，修复所有引用错误和必填字段缺失。

## 用于系统评测

这个 benchmark 可以支持五类任务：

- 伏笔识别：输入全文或段落，输出候选伏笔与解释。
- Payoff 匹配：输入伏笔，定位触发事件和后文 payoff。
- 因果图构建：输出事件节点与因果边，区分因果和时间顺序。
- 叙事现实/不确定性建模：后续接入多版本叙事文本时，保留 disputed 或 symbolic 层级。
- 长篇续写准备：追踪未回收伏笔、仍在推进的因果链，并约束续写不破坏既有结构。

当前五篇标注是 seed gold，不是穷尽全量标注。建议后续每篇至少经过两轮人工复核：第一轮检查事件粒度和因果边，第二轮检查伏笔/payoff 边界和误导线索。
