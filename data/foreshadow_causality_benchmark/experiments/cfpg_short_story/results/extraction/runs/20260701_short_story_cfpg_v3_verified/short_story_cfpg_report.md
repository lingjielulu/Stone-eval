# 短篇小说 CFPG 伏笔实验报告

## 概览

本报告记录 `foreshadow_causality_benchmark` 核心 10 篇短篇小说的 Foreshadow-Trigger-Payoff 候选抽取与 verifier 实验。本轮不经过摘要层，直接使用 `normalized_texts` 的段落时间线；英文作品同步插入 `normalized_texts_zh` 的中文辅助译文，已有 seed YAML 的作品插入人工标注上下文作为参考。

当前结论：

- 有效 run：`20260701_short_story_cfpg_v3_verified`。
- 结果集中保存于：`data/foreshadow_causality_benchmark/novels/cfpg/runs/20260701_short_story_cfpg_v3_verified`。
- Prompt 集中维护于：`prompts/cfpg/short_story_prompts.md`。
- 抽取脚本：`data/foreshadow_causality_benchmark/scripts/extract_short_story_ftp.py`。
- 覆盖核心作品：10 篇。
- Candidate extraction 产出：30 条候选。
- Verifier 接受：25 条 verified F-T-P。
- Verifier 拒绝：5 条。
- Verifier 接受率：83.33%。

## 方法

本轮实验沿用 CFPG 的三元组定义，但针对短篇做两点调整：

- 不做 BookSum-style 摘要，直接在全文段落 ID 上定位 evidence。
- 每篇最多抽取 3 个高召回候选，再逐条运行 verifier；这是为了避免长 prompt 下 JSON 输出被截断，同时贴近红楼梦报告中“每窗最多 3 个候选”的口径。

运行配置：

| 参数 | 值 |
| --- | --- |
| run_id | `20260701_short_story_cfpg_v3_verified` |
| model | `deepseek-v4-pro` |
| max_candidates | 3 / story |
| max_output_tokens | 8192 |
| input text | full paragraph timeline |
| bilingual aid | English stories include Chinese translation when available |
| verification | enabled |

## 输出目录

| 输出 | 路径 |
| --- | --- |
| prompt previews | `data/foreshadow_causality_benchmark/novels/cfpg/runs/20260701_short_story_cfpg_v3_verified/reviews` |
| raw extraction JSON | `data/foreshadow_causality_benchmark/novels/cfpg/runs/20260701_short_story_cfpg_v3_verified/candidates` |
| normalized candidates | `data/foreshadow_causality_benchmark/novels/cfpg/runs/20260701_short_story_cfpg_v3_verified/candidates` |
| verifier JSONL | `data/foreshadow_causality_benchmark/novels/cfpg/runs/20260701_short_story_cfpg_v3_verified/verified` |
| accepted aggregate | `data/foreshadow_causality_benchmark/novels/cfpg/runs/20260701_short_story_cfpg_v3_verified/accepted_triples_20260701_short_story_cfpg_v3_verified.jsonl` |
| rejected aggregate | `data/foreshadow_causality_benchmark/novels/cfpg/runs/20260701_short_story_cfpg_v3_verified/rejected_candidates_20260701_short_story_cfpg_v3_verified.jsonl` |
| summary JSON | `data/foreshadow_causality_benchmark/novels/cfpg/runs/20260701_short_story_cfpg_v3_verified/summary.json` |

## 过滤结果统计

| 阶段 | 输入 | 输出/保留 | 保留率 | 备注 |
| --- | ---: | ---: | ---: | --- |
| 核心作品 | 10 篇 | 10 篇 | 100.00% | 核心 10 篇，不含 `rashomon` 扩展样本 |
| Candidate extraction | 10 篇全文 | 30 条候选 | - | 每篇最多 3 条 |
| F-T-P verification | 30 条候选 | 25 条 accepted | 83.33% | 5 条 rejected |

## 分作品结果

| story_id | 作品 | candidates | accepted | rejected | review |
| --- | --- | ---: | ---: | ---: | --- |
| `speckled_band` | The Adventure of the Speckled Band / 斑点带子案 | 3 | 1 | 2 | [review](reviews/speckled_band_ftp_review_20260701_short_story_cfpg_v3_verified.md) |
| `red_headed_league` | The Red-Headed League / 红发会 | 3 | 3 | 0 | [review](reviews/red_headed_league_ftp_review_20260701_short_story_cfpg_v3_verified.md) |
| `necklace` | The Diamond Necklace / 项链 | 3 | 2 | 1 | [review](reviews/necklace_ftp_review_20260701_short_story_cfpg_v3_verified.md) |
| `gift_of_the_magi` | The Gift of the Magi / 麦琪的礼物 | 3 | 2 | 1 | [review](reviews/gift_of_the_magi_ftp_review_20260701_short_story_cfpg_v3_verified.md) |
| `last_leaf` | The Last Leaf / 最后一片叶子 | 3 | 3 | 0 | [review](reviews/last_leaf_ftp_review_20260701_short_story_cfpg_v3_verified.md) |
| `tell_tale_heart` | The Tell-Tale Heart / 泄密的心 | 3 | 3 | 0 | [review](reviews/tell_tale_heart_ftp_review_20260701_short_story_cfpg_v3_verified.md) |
| `cask_of_amontillado` | The Cask of Amontillado / 一桶白葡萄酒 | 3 | 3 | 0 | [review](reviews/cask_of_amontillado_ftp_review_20260701_short_story_cfpg_v3_verified.md) |
| `to_build_a_fire` | To Build a Fire / 生火 | 3 | 3 | 0 | [review](reviews/to_build_a_fire_ftp_review_20260701_short_story_cfpg_v3_verified.md) |
| `medicine` | 藥 | 3 | 2 | 1 | [review](reviews/medicine_ftp_review_20260701_short_story_cfpg_v3_verified.md) |
| `cricket` | 促織 | 3 | 3 | 0 | [review](reviews/cricket_ftp_review_20260701_short_story_cfpg_v3_verified.md) |

## 类型分布

| foreshadow_type | candidates | accepted |
| --- | ---: | ---: |
| `object` | 7 | 6 |
| `psychological` | 6 | 6 |
| `red_herring` | 2 | 1 |
| `retrospective` | 2 | 1 |
| `rule` | 4 | 3 |
| `social` | 3 | 3 |
| `spatial` | 3 | 3 |
| `symbolic` | 3 | 2 |

| payoff_type | accepted |
| --- | ---: |
| `delayed_revelation` | 5 |
| `ironic` | 5 |
| `literal` | 10 |
| `misdirection` | 1 |
| `symbolic` | 4 |

## Payoff 距离

| 指标 | 段落数 |
| --- | ---: |
| count | 25 |
| min | 4 |
| median | 25 |
| mean | 43.08 |
| max | 174 |

## Accepted 样例

### speckled_band:ftp_candidate:000002

- F: `P0143-P0158` Holmes discovers odd details in Julia's bedroom: a bell-rope that is a dummy, a ventilator connecting to Roylott's room, and the bed fixed in place relative to the rope and ventilator.
- T: Holmes's examination of Roylott's bedroom reveals a safe, a saucer of milk, a chair positioned under the ventilator, and a looped whip, which together suggest the presence of a trained snake.
- P: `P0237-P0238` During the night watch, Holmes strikes at the bell-pull with a cane as a snake comes through the ventilator, revealing the rope as a bridge for the snake to reach the bed.
- verifier rationale: The dummy bell-rope and the connecting ventilator, introduced without explanation, are later revealed as the means for a trained snake to enter the room and reach the bed. The payoff directly resolves the earlier anomalies, making this a valid narrative payoff.

### red_headed_league:ftp_candidate:000001

- F: `P0035-P0039` Mr. Wilson's assistant, Vincent Spaulding, works for half wages and has a peculiar habit of taking photographs and frequently disappearing into the cellar to develop them.
- T: Holmes observes the assistant's worn and stained trouser knees and then taps the pavement to determine the cellar's direction.
- P: `P0209-P0210` Holmes reveals that Spaulding is actually the criminal John Clay, who took the job to tunnel from the cellar into the neighboring bank vault.
- verifier rationale: The half wages in P0035 introduce an unexplained anomaly that is directly resolved in P0207 when Holmes reveals the assistant's true motive—digging a tunnel to the bank. The trigger in P0210 (observing the knees and tapping the pavement) provides the observable moment that confirms the theory and precipitates the climax.

### red_headed_league:ftp_candidate:000002

- F: `P0078-P0082` The Red-headed League's conditions require the holder to stay in the office from 10 am to 2 pm without exception, or else forfeit the position.
- T: Holmes hears Wilson's story and begins to see the importance of the time commitment, leading him to investigate the assistant and the premises.
- P: `P0207` Holmes explains that the league was a ruse to get Wilson out of his shop for several hours each day, allowing the criminals to tunnel undisturbed.
- verifier rationale: The seemingly arbitrary rule is later explicitly revealed as the core plot device to keep Wilson away from his business. The payoff directly explains and fulfills the foreshadowing, with clear temporal separation and an observable trigger in Holmes's investigation.

### red_headed_league:ftp_candidate:000003

- F: `P0121-P0124` Wilson describes Spaulding as small, stout-built, quick, clean-shaven, with an acid scar on his forehead. Holmes excitedly asks if his ears are pierced, noting that he had thought as much.
- T: Holmes recognizes the physical description of the assistant as matching the criminal John Clay, prompting his inquiry about the pierced ears.
- P: `P0169-P0170` It is revealed that the assistant is the notorious criminal John Clay, a young man of noble descent and exceptional cunning, confirming Holmes's earlier recognition.
- verifier rationale: The foreshadowing introduces specific character details (stout build, acid splash, no facial hair) and Holmes's significant reaction, which are later paid off when Holmes names John Clay, the criminal matching those features. The trigger (Holmes's visible excitement and question) is an observable narrative event that bridges the setup and payoff across a non-trivial gap, not merely thematic. The payoff directly resolves the earlier hint by revealing the assistant's true identity.

### necklace:ftp_candidate:000001

- F: `P0046-P0048` Mathilde finds a superb diamond necklace in a black satin box at Madame Forestier's, her heart throbs with immoderate desire, and she puts it on in ecstasy.
- T: Mathilde loses the necklace after the ball and is forced to replace it with a genuine diamond necklace at great cost.
- P: `P0122` Madame Forestier reveals that the original necklace was paste and worth only five hundred francs.
- verifier rationale: The setup introduces the necklace's assumed high value, unresolved. The payoff reveals it was fake, directly resolving the setup. The trigger (losing and replacing it) is observable and explains why the truth emerges later. The connection is a narrative payoff, not thematic echo.

## Rejected 样例

### speckled_band:ftp_candidate:000001

- F: `P0051` Julia Stoner's dying words: 'It was the band! The speckled band!' and the subsequent speculation that it might refer to a band of gypsies with spotted handkerchiefs.
- P: `P0244-P0246` Upon finding Dr. Roylott dead with the snake around his head, Holmes recognizes the 'speckled band' as the snake itself, revealing the true meaning.
- rejection: Trigger validity failed: the observable conditions are not found in the given paragraphs, making the trigger unverifiable.

### speckled_band:ftp_candidate:000003

- F: `P0037-P0043` Julia mentions hearing a low, clear whistle in the dead of night several nights before her death, and Helen later hears a whistle just before the fatal scream.
- P: `P0249-P0250` Holmes explains that the whistle was used by Dr. Roylott to recall the snake back through the ventilator before morning.
- rejection: Trigger condition is not supported by the provided evidence windows; the event of Helen hearing the whistle again is not present in the setup or payoff segments.

### necklace:ftp_candidate:000003

- F: `P0041-P0050` Madame Forestier generously and casually lends Mathilde any jewel she wants, including the diamond necklace, without hesitation.
- P: `P0122` Madame Forestier reveals the necklace was paste, suggesting she was never worried about the loan because of its low value.
- rejection: Setup window lacks the specific foreshadowing event (casual lending of the necklace), making the setup incomplete. Without this, the payoff cannot be seen as a resolution of an earlier narrative element.

### gift_of_the_magi:ftp_candidate:000001

- F: `P0010` The couple's two prized possessions are introduced: Jim's gold watch (family heirloom) and Della's beautiful long hair.
- P: `P0039-P0045` Della buys a platinum chain for Jim's watch, but Jim has sold the watch to buy tortoise-shell combs for Della's hair; both gifts are rendered useless.
- rejection: The provided payoff window does not contain the necessary information to resolve the foreshadowing: Jim's sale of the watch is missing, so the connection cannot be verified.

### medicine:ftp_candidate:000001

- F: `P0012-P0014` 華老栓用洋錢買到一個蘸著鮮血的饅頭，視之為能帶給小栓新生命的藥。
- P: `P0054-P0057` 清明時節，華大媽在小栓墳前祭奠，揭示小栓已死，人血饅頭未能治好他的癆病。
- rejection: Trigger does not justify the timing of the payoff; the coughing scene does not directly explain why the grave scene occurs at Qingming.

## 运行问题记录

本轮正式统计采用 `v3_verified`。此前两个诊断 run 不计入统计：

- `20260701_short_story_cfpg_v1`: `max_candidates=8`, `max_output_tokens=2048`，模型返回 `{}`，normalized candidates 为 0。
- `20260701_short_story_cfpg_v2`: 增加 schema 校验后确认 `{}` 为无效输出；提高 token 后出现截断 JSON。
- `20260701_short_story_cfpg_v3_verified`: 将每篇候选数降为 3，并使用 `max_output_tokens=8192`，完整跑通 extraction + verification。

## 后续处理

- 25 条 accepted 仍是 LLM verifier 结果，不等同 gold；进入 `annotations/*.yaml` 前需要人工复核。
- 5 条 rejected 可用于调 prompt 边界，尤其是主题呼应、普通因果和 span 粒度问题。
- 下一步可以把 accepted 聚合结果映射到现有 schema 的 `foreshadowing_units` 草稿层，再人工审查 trigger/payoff event 绑定。
