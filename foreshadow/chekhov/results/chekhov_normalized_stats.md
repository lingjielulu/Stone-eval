# 契诃夫规范化语料统计

来源：`foreshadow/chekhov/dataset/chekhov_short_stories.txt`

结论：清洗后用于统计和分析的小说数是 201 篇 canonical 故事记录。`218` 是目录标题数，`213` 是正文检测到的故事段数。

口径说明：同一 canonical 标题出现多次时保留词数最长的段；别名标题会归一；未匹配到正文边界的目录标题不进入 canonical 语料。

## 摘要

| 指标 | 数值 |
|---|---:|
| 最终清洗后分析篇数 | 201 |
| 从目录解析出的标题数 | 218 |
| 正文检测故事段 | 213 |
| canonical 故事记录 | 201 |
| 未匹配到正文边界的目录标题 | 16 |
| 重复 canonical 标题 | 12 |
| canonical 语料总词数 | 845,027 |
| canonical 平均词数 | 4,204.11 |
| canonical 中位词数 | 2,242 |
| 最短篇词数 | 645 |
| 最长篇词数 | 39,871 |

## 篇幅分桶

| 词数范围 | 故事数 |
| --- | --- |
| <500 | 0 |
| 500-1K | 11 |
| 1K-2K | 77 |
| 2K-5K | 71 |
| 5K-10K | 27 |
| 10K-20K | 9 |
| 20K+ | 6 |

## 最长 20 篇

| canonical 标题 | 词数 | story_id |
| --- | --- | --- |
| THE DUEL | 39871 | chekhov_the_duel_01 |
| THE STEPPE | 38074 | chekhov_the_steppe_01 |
| MY LIFE | 37548 | chekhov_my_life_01 |
| A DREARY STORY | 23814 | chekhov_a_dreary_story_01 |
| A TEDIOUS STORY | 22284 | chekhov_a_tedious_story_01 |
| WARD NO. 6 | 21449 | chekhov_ward_no_6_01 |
| THE WIFE | 17791 | chekhov_the_wife_01 |
| IN THE RAVINE | 16190 | chekhov_in_the_ravine_01 |
| A WOMAN'S KINGDOM | 16008 | chekhov_a_woman_s_kingdom_01 |
| LIGHTS | 15231 | chekhov_lights_01 |
| A LIVING CHATTEL | 13310 | chekhov_a_living_chattel_01 |
| PEASANTS | 12932 | chekhov_peasants_01 |
| THE PARTY | 12558 | chekhov_the_party_01 |
| THE MURDER | 12297 | chekhov_the_murder_01 |
| ARIADNE | 10457 | chekhov_ariadne_01 |
| THE GRASSHOPPER | 9747 | chekhov_the_grasshopper_01 |
| THE TEACHER OF LITERATURE | 8995 | chekhov_the_teacher_of_literature_01 |
| A NERVOUS BREAKDOWN | 8706 | chekhov_a_nervous_breakdown_01 |
| THE FIT | 8144 | chekhov_the_fit_01 |
| KASHTANKA | 7671 | chekhov_kashtanka_01 |

## 最短 20 篇

| canonical 标题 | 词数 | story_id |
| --- | --- | --- |
| A BLUNDER | 645 | chekhov_a_blunder_01 |
| A COUNTRY COTTAGE | 661 | chekhov_a_country_cottage_01 |
| JOY | 666 | chekhov_joy_01 |
| FAT AND THIN | 751 | chekhov_fat_and_thin_01 |
| THE ALBUM | 763 | chekhov_the_album_01 |
| AN ENIGMATIC NATURE | 804 | chekhov_an_enigmatic_nature_01 |
| THAT WRETCHED BOY | 822 | chekhov_that_wretched_boy_01 |
| IN THE GRAVEYARD | 883 | chekhov_in_the_graveyard_01 |
| AN INQUIRY | 886 | chekhov_an_inquiry_01 |
| A LIVING CALENDAR | 943 | chekhov_a_living_calendar_01 |
| THE DEATH OF A GOVERNMENT CLERK | 950 | chekhov_the_death_of_a_government_clerk_01 |
| IN AN HOTEL | 1006 | chekhov_in_an_hotel_01 |
| A CLASSICAL STUDENT | 1084 | chekhov_a_classical_student_01 |
| HUSH! | 1104 | chekhov_hush_01 |
| AFTER THE THEATRE | 1137 | chekhov_after_the_theatre_01 |
| GRISHA | 1197 | chekhov_grisha_01 |
| AT THE BARBER'S | 1224 | chekhov_at_the_barber_s_01 |
| OH! THE PUBLIC | 1225 | chekhov_oh_the_public_01 |
| THE ORATOR | 1252 | chekhov_the_orator_01 |
| A CHAMELEON | 1253 | chekhov_a_chameleon_01 |

## 重复 Canonical 标题

| canonical 标题 | 出现次数 |
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

以下标题出现在目录解析结果中，但没有作为独立 canonical 故事记录输出。它们多数是重复译本标题、选集中的其他作品标签，或正文中没有独立标题边界的条目。

THE QUEEN OF SPADES, THE CLOAK, THE DISTRICT DOCTOR, THE CHRISTMAS TREE AND THE WEDDING, GOD SEES THE TRUTH, BUT WAITS, HOW A MUZHIK FED TWO OFFICIALS, THE SHADES, A PHANTASY, THE SIGNAL, HIDE AND SEEK, DETHRONED, THE SERVANT, ONE AUTUMN NIGHT, HER LOVER, LAZARUS, THE REVOLUTIONIST, THE OUTRAGE--A TRUE STORY
