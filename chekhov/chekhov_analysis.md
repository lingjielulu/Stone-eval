# 安东·契诃夫短篇小说 — 清洗后可视化分析

**来源**: Project Gutenberg eBook #57333
**原始文本**: `chekhov/chekhov_short_stories.txt`
**清洗脚本**: `data/chekhov/scripts/preprocess_chekhov.py`
**统计产物**: `data/chekhov/processed/stats.json`

---

## 阅读导览

这份报告使用规范化清洗后的口径：从目录解析出 218 个标题，在正文中检测到 213 个故事段，经过别名归一和重复标题选择后，形成 201 篇 canonical 故事。后续统计和分析默认使用这 201 篇。canonical 语料总词数为 845,027，平均 4,204.11 词，中位数 2,242 词。

**关键观察**

| 观察点 | 结论 |
|---|---|
| 清洗状态 | 已完成可复现预处理；边界修复、标题归一、重复标题选择都记录在 manifest 中。 |
| 分析口径 | 当前报告使用 `stories_canonical`，即每个 canonical title 保留最长检测段。 |
| 篇幅主体 | 1K-5K 词故事共 148 篇，占 73.6%，仍是主体。 |
| 长尾作品 | 20K+ 共 6 篇，其中 `THE DUEL`、`THE STEPPE`、`MY LIFE` 形成最明显的长篇尾部。 |
| 后续伏笔统计 | 这版清洗结果已经具备 story_id、标题、正文边界、词数、段落数和质量标记，可作为伏笔候选抽取的稳定输入。 |

## 数据仪表盘

| 指标 | 数值 |
|---|---:|
| 最终清洗后分析篇数 | 201 |
| 目录标题数 | 218 |
| 正文检测故事段 | 213 |
| canonical 故事数 | 201 |
| 未匹配目录标题 | 16 |
| 重复 canonical 标题 | 12 |
| canonical 总词数 | 845,027 |
| 平均词数 | 4,204.11 |
| 中位词数 | 2,242 |
| 最短篇词数 | 645 |
| 最长篇词数 | 39,871 |

## 篇幅分布

> 横向条按最大桶归一化。当前最大桶为 1K-2K，共 77 篇。

| 词数范围 | 篇数 | 占比 | 可视化 |
| --- | --- | --- | --- |
| <500 | 0 | 0.0% |  |
| 500-1K | 11 | 5.5% | ████ |
| 1K-2K | 77 | 38.3% | ██████████████████████████████ |
| 2K-5K | 71 | 35.3% | ████████████████████████████ |
| 5K-10K | 27 | 13.4% | ███████████ |
| 10K-20K | 9 | 4.5% | ████ |
| 20K+ | 6 | 3.0% | ██ |

**篇幅结构速读**

| 分层 | 覆盖范围 | 说明 |
|---|---|---|
| 微型短篇 | 500-1K | 共 11 篇，适合观察契诃夫的单场景讽刺和反讽收束。 |
| 标准短篇 | 1K-5K | 共 148 篇，是后续伏笔/回收统计的主样本区间。 |
| 中长篇 | 5K-20K | 共 36 篇，人物关系和多场景推进更明显。 |
| 长篇/中篇 | 20K+ | 共 6 篇，应在伏笔统计中单独分层，避免篇幅优势影响频次。 |

## 主题词密度

> 这是基于清洗后 canonical 正文的轻量词表统计，单位为“每千词平均命中次数”。它适合做宏观导航，不等同于人工主题标注。

| 排名 | 主题 | 平均密度 | 相对强度 | 可视化 |
| --- | --- | --- | --- | --- |
| 1 | 家庭 | 5.01 | 100% | ██████████████████████████████ |
| 2 | 宗教/信仰 | 2.21 | 44% | █████████████ |
| 3 | 自然/风景 | 2.07 | 41% | ████████████ |
| 4 | 爱情/浪漫 | 1.83 | 37% | ███████████ |
| 5 | 贫困/阶级 | 1.69 | 34% | ██████████ |
| 6 | 饮酒 | 1.61 | 32% | ██████████ |
| 7 | 疾病/医学 | 1.54 | 31% | █████████ |
| 8 | 死亡 | 1.46 | 29% | █████████ |
| 9 | 官僚/社会 | 1.37 | 27% | ████████ |
| 10 | 艺术/创作 | 1.16 | 23% | ███████ |

## 最长 20 篇

> 相对篇幅按本组最长 `THE DUEL` 归一化。

| 排名 | 英文标题 | 词数 | story_id | 相对篇幅 |
| --- | --- | --- | --- | --- |
| 1 | THE DUEL | 39,871 | chekhov_the_duel_01 | ██████████████████████████████ |
| 2 | THE STEPPE | 38,074 | chekhov_the_steppe_01 | █████████████████████████████ |
| 3 | MY LIFE | 37,548 | chekhov_my_life_01 | ████████████████████████████ |
| 4 | A DREARY STORY | 23,814 | chekhov_a_dreary_story_01 | ██████████████████ |
| 5 | A TEDIOUS STORY | 22,284 | chekhov_a_tedious_story_01 | █████████████████ |
| 6 | WARD NO. 6 | 21,449 | chekhov_ward_no_6_01 | ████████████████ |
| 7 | THE WIFE | 17,791 | chekhov_the_wife_01 | █████████████ |
| 8 | IN THE RAVINE | 16,190 | chekhov_in_the_ravine_01 | ████████████ |
| 9 | A WOMAN'S KINGDOM | 16,008 | chekhov_a_woman_s_kingdom_01 | ████████████ |
| 10 | LIGHTS | 15,231 | chekhov_lights_01 | ███████████ |
| 11 | A LIVING CHATTEL | 13,310 | chekhov_a_living_chattel_01 | ██████████ |
| 12 | PEASANTS | 12,932 | chekhov_peasants_01 | ██████████ |
| 13 | THE PARTY | 12,558 | chekhov_the_party_01 | █████████ |
| 14 | THE MURDER | 12,297 | chekhov_the_murder_01 | █████████ |
| 15 | ARIADNE | 10,457 | chekhov_ariadne_01 | ████████ |
| 16 | THE GRASSHOPPER | 9,747 | chekhov_the_grasshopper_01 | ███████ |
| 17 | THE TEACHER OF LITERATURE | 8,995 | chekhov_the_teacher_of_literature_01 | ███████ |
| 18 | A NERVOUS BREAKDOWN | 8,706 | chekhov_a_nervous_breakdown_01 | ███████ |
| 19 | THE FIT | 8,144 | chekhov_the_fit_01 | ██████ |
| 20 | KASHTANKA | 7,671 | chekhov_kashtanka_01 | ██████ |

## 最短 20 篇

| 排名 | 英文标题 | 词数 | story_id |
| --- | --- | --- | --- |
| 1 | A BLUNDER | 645 | chekhov_a_blunder_01 |
| 2 | A COUNTRY COTTAGE | 661 | chekhov_a_country_cottage_01 |
| 3 | JOY | 666 | chekhov_joy_01 |
| 4 | FAT AND THIN | 751 | chekhov_fat_and_thin_01 |
| 5 | THE ALBUM | 763 | chekhov_the_album_01 |
| 6 | AN ENIGMATIC NATURE | 804 | chekhov_an_enigmatic_nature_01 |
| 7 | THAT WRETCHED BOY | 822 | chekhov_that_wretched_boy_01 |
| 8 | IN THE GRAVEYARD | 883 | chekhov_in_the_graveyard_01 |
| 9 | AN INQUIRY | 886 | chekhov_an_inquiry_01 |
| 10 | A LIVING CALENDAR | 943 | chekhov_a_living_calendar_01 |
| 11 | THE DEATH OF A GOVERNMENT CLERK | 950 | chekhov_the_death_of_a_government_clerk_01 |
| 12 | IN AN HOTEL | 1,006 | chekhov_in_an_hotel_01 |
| 13 | A CLASSICAL STUDENT | 1,084 | chekhov_a_classical_student_01 |
| 14 | HUSH! | 1,104 | chekhov_hush_01 |
| 15 | AFTER THE THEATRE | 1,137 | chekhov_after_the_theatre_01 |
| 16 | GRISHA | 1,197 | chekhov_grisha_01 |
| 17 | AT THE BARBER'S | 1,224 | chekhov_at_the_barber_s_01 |
| 18 | OH! THE PUBLIC | 1,225 | chekhov_oh_the_public_01 |
| 19 | THE ORATOR | 1,252 | chekhov_the_orator_01 |
| 20 | A CHAMELEON | 1,253 | chekhov_a_chameleon_01 |

## 清洗质量记录

| 项目 | 说明 |
|---|---|
| 标题归一 | `GOUSSIEV` 归一为 `GUSEV`。 |
| 重复选择 | 同一 canonical title 出现多次时，默认保留词数最长的段作为 canonical。 |
| 版面修复 | 对少数 run-in heading 做显式修复，例如 `MY LIFE`、`GOUSSIEV/GUSEV` 相关边界。 |
| 未匹配目录项 | 多数来自非契诃夫附录、其他作者作品或正文无独立标题的目录项。 |

| 质量标记 | 计数 |
| --- | --- |
| duplicate_canonical_title | 12 |
| known_layout_sensitive_title | 4 |
| short_segment_under_500_words | 1 |
| title_alias_normalized | 1 |

## 重复 Canonical 标题

| 标题 | 检测段数 |
| --- | --- |
| A GENTLEMAN FRIEND | 2 |
| AFTER THE THEATRE | 2 |
| ENEMIES | 2 |
| EXPENSIVE LESSONS | 2 |
| GOOSEBERRIES | 2 |
| GUSEV | 2 |
| IN EXILE | 2 |
| MY LIFE | 2 |
| OLD AGE | 2 |
| THE BET | 2 |
| TYPHUS | 2 |
| VANKA | 2 |

## 未匹配目录标题

THE QUEEN OF SPADES, THE CLOAK, THE DISTRICT DOCTOR, THE CHRISTMAS TREE AND THE WEDDING, GOD SEES THE TRUTH, BUT WAITS, HOW A MUZHIK FED TWO OFFICIALS, THE SHADES, A PHANTASY, THE SIGNAL, HIDE AND SEEK, DETHRONED, THE SERVANT, ONE AUTUMN NIGHT, HER LOVER, LAZARUS, THE REVOLUTIONIST, THE OUTRAGE--A TRUE STORY

## 面向伏笔统计的下一步

| 层级 | 建议字段 | 用途 |
|---|---|---|
| story | `story_id`, `canonical_title`, `word_count`, `quality_flags` | 控制篇幅和清洗质量对伏笔频次的影响。 |
| location | paragraph index, token span, relative position | 判断 setup/payoff 距离和分布。 |
| cue | entity, object, motif, warning, prophecy, odd detail | 抽取潜在伏笔候选。 |
| payoff | later event, reversal, revelation, repetition | 验证候选是否真的被回收。 |
| confidence | rule score, model score, reviewer decision | 区分自动候选和人工确认样本。 |
