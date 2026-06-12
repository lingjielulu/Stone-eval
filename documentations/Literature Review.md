# Literature Review

## Literatuer Review

### 写作方案: Multi NPC 驱动还是 剧情驱动?

#### IBSEN ACL 2024  https://arxiv\.org/abs/2407\.01093 导演\-演员 Agent 合作生成可控/互动式剧本

导演根据情节目标生成剧本，向演员提供必要的剧情信息，导演查询聊天记录情况，指导下一轮对话；一旦玩家介入，立即更新新的剧情和对话脚本，让演员及时反映，玩家不受到控制。

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=YjZmMTE4MDFhMjBhYjlkYmIyNmQ5YzlmZmVlZDE3OTFfNWUyYTA3Y2ZlZDFmY2Y5Zjc5YjYyNGFmNjAwYTcwNjRfSUQ6NzY0NjY4MDc3Njg2MDA5MzM3OF8xNzgwNjMwMzU3OjE3ODA3MTY3NTdfVjM)



#### LongWriter\-Zero ICRL 2026 https://arxiv\.org/abs/2506\.18841  通过 RL \- GRPO 生成超长文本 

长度 / 写作 / 格式 3个奖励模型 \+ CoT Thinking prompt 通过\<think\>引入中间推理步骤 

32B 8 nodes \* 8 H800 GPUs

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=Yzg5MTg5YmYyYjIyMDhiZjc5NjVjODQ0MTg4YjEwOWJfOWY3YmM4YWZjNjQ1M2E3NTg0YmM5YjVjOGI3NmI5ZmZfSUQ6NzY0NjY4MDc3NjcxMzUzODUwN18xNzgwNjMwMzU3OjE3ODA3MTY3NTdfVjM)

#### **Codified Foreshadowing\-Payoff Text Generation ****https://arxiv\.org/abs/2601\.07033**** 伏笔追踪**



### 评价标准： 

#### Long Story Eval ACL\-2025 https://arxiv\.org/abs/2512\.12839 从真实作品 / 读者总结的长故事评价标准

https://github\.com/DingyiYang/LongStoryEval\.git

1. 理解读者最看重哪些评价方面：情节和人物 \> 主题 \> 世界观和写作质量 （data: 600本新书\+评论）

2. 探索长篇故事的有效评价方法 **LongStoryEval **

3. 提出了 **NovelCritique **\(8B\) 基于摘要评价 \(对比 基于章节聚合 / 基于阅读顺序增量更新 更优\)

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=OWE3NmQxMTUxOGE1YjAwZGRiYTZhYTkxYmVlNTJmYjdfN2E1MmM3YWZhNWI3ZjUwMTg3MmJlOTlhNGU2MDA0NDZfSUQ6NzY0NjY4MDc3OTUxODc0MTQ2NV8xNzgwNjMwMzU3OjE3ODA3MTY3NTdfVjM)

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=OWM5ZTQ1MjViMzMxYjEzOTU0ODg1NjM1Zjg3YjIzY2FfYjc1MTRhN2EzYzA4NDI4MDY3ZDJmMDVmODVmN2QzYTFfSUQ6NzY0NjY4MDc3NzM0MjcxNjg2Nl8xNzgwNjMwMzU3OjE3ODA3MTY3NTdfVjM)

#### ConStory\-Bench ACL\-2026 https://github\.com/Picrew/ConStory\-Bench LLM 长叙事一致性错误分类

https://github\.com/Picrew/ConStory\-Bench\.git

首次系统化定义长篇故事生成 \(Generation /  Continuation /  Expansion / Completion\) 的一致性错误分类体系，包含 5 个顶层类别、19 个细粒度子类型，覆盖 2000 个提示

并且开发了 ConStory\-Checker 自动化评估流程，用精确的文本支持判断

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=ZWJmYTEzMTA1YTNhMDhhMjFmNzFkMTExOWI4YWFhZWFfMDM1ZmM0NDNlNDEzYzc4NzVjYzI3YmZjMTA1ZTYzMjZfSUQ6NzY0NjY4MDc3OTYzNjIzMTExMF8xNzgwNjMwMzU3OjE3ODA3MTY3NTdfVjM)



#### 6 Emotion arcs https://arxiv\.org/abs/1606\.07772 基于机器学习发现了 6 种通用情感曲线 \(rise / fall\)

**Hedonometer 情感分析工具 ****https://hedonometer\.org/timeseries/en\_all/?from=2022\-01\-01\&to=2023\-06\-30\#**

- “Rags to riches” \(rise\)\.
“白手起家”（崛起）

- “Tragedy”, or “Riches to rags” \(fall\)\.
“悲剧”，或“从富到贫”（衰落）

- “Man in a hole” \(fall\-rise\)\.
“洞里的人”（跌倒\-上升）

- “Icarus” \(rise\-fall\)\.  “伊卡洛斯”（崛起\-陨落）。

- “Cinderella” \(rise\-fall\-rise\)\.
“灰姑娘”（起\-落\-起）

- “Oedipus” \(fall\-rise\-fall\)\.
“俄狄浦斯”（堕落\-崛起\-堕落）

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MjIyMWYzY2VlOTlhMjkyMGYzZWUzZTM1NGVjMTFlM2JfNzc2ZGMzZjM1OGYxNmY2ZDY2NWQzYzFmMTg5ZmE1MmRfSUQ6NzY0NjY4MDc3ODUxNjU0ODU3OF8xNzgwNjMwMzU3OjE3ODA3MTY3NTdfVjM)

#### LLM Story Social Network NeurIPS 2025 https://arxiv\.org/abs/2510\.18932 LLM 积极社交偏见 

首先画人物社交关系网络图（基于对话/提及/行动交互）：node是人物，weighted edge 是关系

然后对图的：边密度（实际边数量/全连接图的边数量），边权重（人物关系正负性），平均聚类系数（量化顶点另据之间的联系程度分析小世界性），同配性混合（数值相似的定点彼此相邻的可能性）做统计分析

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=OGRmYTE1ZTQ2ZDkwNTJjYmY3MmYxOTQ0NTI3YzdjODJfMDdmMTI4MzFmZDM5Zjg1NTYyNDBmNDhiOTNhODQ0NTNfSUQ6NzY0Njk3NzUyMTE1Mzk2OTMzMF8xNzgwNjMwMzU3OjE3ODA3MTY3NTdfVjM)

开头的钩子 \- 衔接



