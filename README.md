# Stone-eval

中文长叙事评测、文学分析与伏笔研究工作区。评测实现、方法说明和已有运行记录
按功能统一放在 `stone_eval/`，语料和词典由 `resources/` 集中管理。

## 目录

```text
stone_eval/       可复用的评测与语料处理代码
foreshadow/       伏笔研究：短篇小说、红楼梦、契诃夫
poetry_data/      诗歌数据
resources/        公共语料库与情感分析词典
third_party/      外部 Git 子模块
docs/             项目级说明与历史归档
```

## 当前功能与运行记录

| 功能 | 状态 | 入口 |
|---|---|---|
| 《红楼梦》情感弧线 | 已完成 NTUSD 与模型基线 | `stone_eval/emotion/` |
| 《红楼梦》ConStory smoke test | 已完成原作 80 回 smoke run | `stone_eval/consistency/` |
| 《红楼梦》LongStoryEval 适配 | 已完成输入准备，未完成正式评价 | `stone_eval/quality/` |
| 伏笔研究 | 多组实验持续进行 | `foreshadow/` |

`consistency`、`critique`、`social`、`emotion` 和 `all` 等旧 CLI 命令中仍有
占位实现；可运行入口和完成状态以各模块 README 为准。

## 公共内容

- `stone_eval/`：按评测功能组织的 Python 实现、方法说明与运行记录。
- `resources/corpora/hongloumeng/`：红楼梦原作、外部导入文本及派生格式。
- `resources/lexicons/ntusd/`：情感分析使用的公共 NTUSD 词表。
- `third_party/`：ConStory-Bench 与 LongStoryEval。

红楼梦价值图 schema 只服务伏笔工作，因此保留在
`foreshadow/honglou/common/`，不进入公共资源目录。

## 安装

```bash
pip install -e .
cp .env.example .env
```

常用入口：

- 情感弧线：`stone_eval/emotion/README.md`
- ConStory smoke：`stone_eval/consistency/README.md`
- LongStoryEval：`stone_eval/quality/README.md`
- 伏笔工作区：`foreshadow/README.md`
- 诗歌数据：`poetry_data/README.md`

## License

MIT
