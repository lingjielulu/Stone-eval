# 红楼梦共享语料

这里保存被多个实验使用的红楼梦语料。它是共享资源，不代表本仓库承担续写
生成实验。

## 内容

| 路径 | 说明 |
|---|---|
| `红楼梦.txt` | 原始文本，本地保留 |
| `continuations/` | 从外部来源导入的续作文本，本地保留 |
| `prepared/chapters/` | 展开的章节文本 |
| `prepared/constory/` | ConStory-Bench 输入格式 |
| `prepared/longstoryeval/` | LongStoryEval book JSON |
| `prepared/manifest.json` | 派生语料清单 |
| `prepared/reports/` | 语料验证报告 |

大体积语料与派生文件默认由 `.gitignore` 排除。可使用
`stone-eval prepare-corpus` 重新生成 `prepared/`，并使用
`stone-eval validate-corpus` 验证。

情感分析词表不属于语料库，统一位于 `resources/lexicons/`。
