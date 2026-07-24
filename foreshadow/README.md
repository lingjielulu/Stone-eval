# Foreshadow 研究工作区

伏笔识别、Foreshadow–Trigger–Payoff（F–T–P）抽取和 CFPG 复现按研究对象分为
三组。小说语料随对应实验组保存；顶层 [`poetry_data/`](../poetry_data/) 只保留诗歌数据。

```text
foreshadow/
├── short_stories/   # 多作者短篇小说 benchmark 与 CFPG 实验
│   ├── dataset/     # 原文、规范化文本、标注和 schema
│   ├── scripts/     # 下载、清洗、候选生成和校验
│   ├── cfpg/        # CFPG 数据、prompt、实验、报告与结果
│   ├── results/     # Medicine 等独立分析 demo
│   └── tests/
├── honglou/         # 《红楼梦》实验组
│   ├── docs/
│   ├── prompts/
│   ├── scripts/
│   └── results/     # CFPG、运行报告与价值图
├── chekhov/         # 契诃夫语料与伏笔分析组
│   ├── dataset/
│   ├── docs/
│   ├── scripts/
│   └── results/
└── common/          # 跨实验共用的 CFPG prompt 工具
```

## 实验入口

- [短篇小说组](short_stories/README.md)
- [《红楼梦》组](honglou/README.md)
- [契诃夫组](chekhov/README.md)
- [诗歌数据](../poetry_data/README.md)

所有命令均从仓库根目录执行。
