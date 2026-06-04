# Stone-eval

《红楼梦》续写评价套件。从一致性、叙事质量、人物关系网络、情感曲线四个维度评估续作质量，与 [Stone](https://github.com/lingjielulu/HongLou-continuation-LLM) 生成主库配套使用。

## 评价维度

| 维度 | 模块 | 灵感来源 | 论文 |
|------|------|---------|------|
| 一致性错误检测 | `stone_eval.consistency` | ConStory-Bench | [ACL 2026](https://arxiv.org/abs/2603.05890) |
| 叙事质量评分 | `stone_eval.quality` | NovelCritique / LongStoryEval | [ACL 2025](https://arxiv.org/abs/2512.12839) |
| 人物社交网络 | `stone_eval.social` | LLM Story Social Network | [NeurIPS 2025](https://arxiv.org/abs/2510.18932) |
| 情感曲线分析 | `stone_eval.emotion` | 6 Emotional Arcs | [EPJ 2016](https://arxiv.org/abs/1606.07772) |

## 目录结构

```text
stone_eval/
├── consistency/       # 5类19子类一致性检测（LLM-as-judge）
│   ├── checker.py     # prompt templates + data structures
├── quality/           # 8维度叙事质量评分
│   ├── critique.py    # 中文古典小说评价标准
├── social/            # 人物关系图构建与分析
│   ├── network.py     # networkx-based metrics
├── emotion/           # 情感曲线提取与聚类
│   ├── arcs.py        # 6种通用情感弧线
├── cli.py             # 统一命令行入口
data/
├── prompts/           # 评测 prompt 模板
├── gold/              # 人工标注 gold standard
outputs/               # 评测输出
scripts/               # 批量运行脚本
```

## 快速开始

```bash
# 安装
pip install -e .

# 复制环境变量
cp .env.example .env
# 编辑 .env 填入 API key

# 单章一致性检测
stone-eval consistency \
  --source ../Stone/data/chapters/chapter_080.txt \
  --continuation ../Stone/generations/prompt_baseline/chapter_081.txt

# 单章质量评分
stone-eval critique --summary chapter_081_summary.md

# 人物社交网络分析
stone-eval social --text chapter_081.txt

# 情感曲线分析
stone-eval emotion --text chapter_081.txt --reference original_arc.json

# 批量全维度评测
bash scripts/run_consistency.sh
bash scripts/run_critique.sh
bash scripts/run_social.sh
bash scripts/run_emotion.sh
```

## 评价维度详解

### 1. 一致性错误检测

基于 LLM-as-judge，逐章对比原文与续文，检测 5 大类错误：

- **人物一致性**：记忆矛盾、知识冲突、性格偏离、能力波动
- **事实细节**：外貌矛盾、称谓错误、数量错误、服饰器皿错误
- **叙事风格**：视角偏移、语气断裂、文体失调、章回体违规
- **时间线与情节**：时间矛盾、时长错误、因果断裂、伏笔丢失、人物出场失误
- **世界观与设定**：制度违例、地理矛盾、社会规范冲突、神话体系矛盾

### 2. 叙事质量评分

8 维度1-10分制，针对红楼梦特化：

- 情节、人物、主题、世界观、写作质量、情感、章回结构、伏笔兑现

### 3. 人物社交网络

从文本中抽取人物共现与交互，构建带符号的关系图：

- 边密度、平均聚类系数、同配性混合、正负关系比例

### 4. 情感曲线

将章节分段打分，拟合 6 种通用情感弧线之一，与原文前 80 回曲线计算相关性。

## 与 Stone 主库的关系

```text
Stone (生成)                    Stone-eval (评价)
───────────                    ───────────────
IBSEN Multi-Agent → 生成续文 → ConStory-Bench 一致性检测
CFPG 伏笔系统 → 伏笔注入     → NovelCritique 质量评分
LongWriter → 长文本 backbone → Social Network 人物偏差
                              → Emotion Arc 情感漂移
```

## License

MIT
