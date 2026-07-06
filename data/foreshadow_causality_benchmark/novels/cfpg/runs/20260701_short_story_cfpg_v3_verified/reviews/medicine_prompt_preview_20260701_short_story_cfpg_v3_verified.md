# Short Story CFPG Prompt Preview

## system

```text
你是短篇小说伏笔-触发-回收结构标注员。任务是在给定的全文段落时间线中，高召回抽取候选 Foreshadow-Trigger-Payoff 三元组。只能依据输入文本，不得使用外部知识或你对作品结局的先验记忆。只输出合法 JSON。
```

## user

```text
请对下面的短篇小说段落时间线执行第一步：高召回候选识别。

作品：
- story_id: medicine
- title: 藥
- language: zh

操作化定义：
- Foreshadow(F): 较早段落引入具体但当时未完全解释/解决的叙事元素，包括物件、异常、规则、空间结构、心理症状、承诺、警告、谎言、身份线索、象征物或关键话语。
- Trigger(T): 使伏笔进入可兑现状态的可观察叙事条件。Trigger 必须是文本中可以定位的事件、发现、行动、状态变化或条件满足，不要写“命运展开”“气氛成熟”这类抽象词。
- Payoff(P): 较晚段落提供具体事件、解释、履行、反转、否定、失败或主题性回收，用来清偿 F 的叙事债务。

本步骤只产生候选，不等同最终 gold。优先召回，但不要输出纯主题呼应或普通即时因果。
对于结构明确的短篇，通常应输出 3-8 个候选；宁可标为 low confidence，也不要因为要求过严而漏掉明显的 delayed setup/payoff。

硬性约束：
1. payoff_span 必须晚于 foreshadow_span。
2. F/P 之间应有非平凡间隔；普通相邻段落即时因果不要输出。
3. 每条候选必须给 proposed_trigger，且 trigger 必须可观察。
4. 每条候选必须给 paragraph span，例如 "P0012" 或 "P0012-P0015"。
5. 每条候选必须能在输入段落中找到证据。
6. 候选数量最多 3 个。
7. 顶层 JSON 必须包含 candidates 数组，严禁输出空对象 {}。
8. 如果没有合格候选，输出 {"candidates": []}。

优先类型：
- object: 物件早期出现，后期发挥关键功能。
- rule: 规则/自然法则/社会规则早期建立，后文兑现。
- psychological: 心理异常或感官执念预示后续行为。
- spatial: 空间结构预示后续危险或行动路径。
- social: 社会习俗/制度压力预示后续悲剧。
- symbolic: 意象在后文形成主题性回收。
- red_herring: 早期误导线索，后文被重释。
- retrospective: 读到结尾后才确认前文是伏笔。

输出 JSON object，字段严格如下：
{
  "candidates": [
    {
      "foreshadow_span": "P0001-P0002",
      "payoff_span": "P0030",
      "foreshadow_summary": "...",
      "payoff_summary": "...",
      "proposed_trigger": {
        "description": "...",
        "observable_conditions": ["..."]
      },
      "relation_description": "...",
      "foreshadow_type": "object|rule|psychological|spatial|social|symbolic|red_herring|retrospective",
      "payoff_type": "literal|ironic|symbolic|negative|misdirection|delayed_revelation",
      "stage1_confidence": "high|medium|low",
      "stage1_rationale": "..."
    }
  ]
}

原文段落时间线：
[P0001] 秋天的後半夜，月亮下去了，太陽還沒有出，只剩下一片烏藍的天；除了夜遊的東西，什麽都睡着。華老栓忽然坐起身。擦着火柴，點上遍身油膩的燈盞，茶館的兩間屋子裏，便瀰滿了靑白的光。

[P0002] 『小栓的爹，你就去麽？』是一個老女人的聲音。裏邊的小屋子裏，也發出一陣咳嗽。

[P0003] 『唔。』老栓一面聽，一面應，一面扣上衣服；伸手過去說，『你給我罷。』

[P0004] 華大媽在枕頭底下掏了半天，掏出一包洋錢，交給老栓，老栓接了，抖抖的裝入衣袋，又在外面按了兩下；便點上燈籠，吹熄燈盞，走向裏屋子去了。那屋子裏面，正在窸窸窣窣的響，接着便是一通咳嗽。老栓候他平靜下去，纔低低的叫道：『小栓……你不要起來。……店麽？你娘會安排的。』

[P0005] 老栓聽得兒子不再說話，料他安心睡了；便出了門，走到街上。街上黑沈沈的一無所有，只有一條灰白的路，看得分明。燈光照着他的兩脚，一前一後的走。有時也遇到幾隻狗，可是一隻也沒有叫。天氣比屋子裏冷得多了；老栓倒覺爽快，彷彿一旦變了少年，得了神通，有給人生命的本領似的，跨步格外高遠。而且路也愈走愈分明，天也愈走愈亮了。

[P0006] 老栓正在專心走路，忽然喫了一驚，遠遠裏看見一條丁字街，明明白白橫着。他便退了幾步，尋到一家關着門的鋪子，蹩進簷下，靠門立住了。好一會，身上覺得有些發冷。

[P0007] 『哼，老頭子。』

[P0008] 『倒高興。……』

[P0009] 老栓又喫一驚，睜眼看時，幾個人從他面前過去了。一個還回頭看他，樣子不甚分明，但很像久餓的人見了食物一般，眼裏閃出一種攫取的光。老栓看看燈籠，已經熄了。按一按衣袋，硬硬的還在。仰起頭兩面一望，只見許多古怪的人，三三兩兩，鬼似的在那里徘徊；定睛再看，卻也看不出什麽別的奇怪。

[P0010] 沒有多久，又見幾個兵，在那邊走動；衣服前後的一個大白圓圈，遠地裏也看得淸楚，走過面前的，並且看出號衣上暗紅色的鑲邊。——一陣腳步聲響，一眨眼，已經擁過了一大簇人。那三三兩兩的人，也忽然合作一堆，潮一般向前趕；將到丁字街口，便突然立住，簇成一個半圓。

[P0011] 老栓也向那邊看，卻只見一堆人的後背；頸項都伸得很長，彷彿許多鴨，被無形的手揑住了的，向上提着。靜了一會，似乎有點聲音，便又動搖起來，轟的一聲，都向後退；一直散到老栓立着的地方，幾乎將他擠倒了。

[P0012] 『喂！一手交錢，一手交貨！』一個渾身黑色的人，站在老栓面前，眼光正像兩把刀。刺得老栓縮小了一半。那人一隻大手，向他攤着；一隻手卻撮着一個鮮紅的饅頭，那紅的還是一點一點的往下滴。

[P0013] 老栓慌忙摸出洋錢，扯抖的想交給他，卻又不敢去接他的東西。那人便焦急起來，嚷道，『怕什麽？怎的不拿！』老栓還躊躇着；黑的人便搶過燈籠，一把扯下紙罩，裹了饅頭，塞與老栓；一手抓過洋錢，揑一揑，轉身去了。嘴裏哼着說：『這老東西……。』

[P0014] 『這給誰治病的呀？』老栓也似乎聽得有人問他，但他並不答應；他的精神，現在只在一個包上，彷彿抱着一個十世單傳的嬰兒，別的事情，都已置之度外了。他現在要將這包裏的新的生命，移植到他家裏，收穫許多幸福。太陽也出來了；在他面前，顯出一條大道，直到他家中，後面也照見丁字有頭破匾上『古口亭口』這四個黯淡的金字。

[P0015] 老栓走到家，店面早經收拾乾淨，一排一排的茶桌，滑溜溜的發光。但是沒有客人；只有小栓坐在裏排的桌前喫飯，大粒的汗，從額上滾下，夾襖也貼住了脊心，兩塊肩胛骨高高凸出，印成一個陽文的『八』字。老栓見這樣子，不免皺一皺展開的眉心。他的女人，從竈下急急走出，睜着眼睛，嘴脣有些發抖。

[P0016] 『得了麽？』

[P0017] 『得了。』

[P0018] 兩個人一齊走進竈下，商量了一會；華大媽便出去了，不多時，拏着一片老荷葉回來，攤在桌上。老栓也打開燈籠罩，用荷葉重新包了那紅的饅頭。小栓也喫完飯，他的母親慌忙說：——

[P0019] 『小栓——你坐着，不要到這裏來。』

[P0020] 一面整頓了竈火，老栓便把一個碧綠的包，一個紅紅白白的破燈籠，一同塞在竈裏，一陣紅黑的火燄過去時，店屋裏散滿了一種奇怪的香味。

[P0021] 『好香！你們喫什麽點心呀？』這是駝背五少爺到了。這人每天總在茶館裏過日，來得最早，去得最遲，此時恰恰蹩到臨街的壁角的桌邊，便坐下問話，然而沒有人答應他。『炒米粥麽？』仍然沒有人應。老栓匆匆走出，給他泡上茶。

[P0022] 『小栓進來罷！』華大媽叫小栓進了裏面的屋子，中間放好一條凳，小栓坐了。他的母親端過一碟烏黑的圓東西，輕輕說：——

[P0023] 『喫下去罷，——病便好了。』

[P0024] 小栓撮起這黑東西，看了一會，似乎拏着自己的性命一般，心裏說不出的奇怪。十分小心的拗開了，焦皮裏面竄出一道白氣，白氣散了，是兩半個白麵的饅頭。——不多工夫，已經全在肚裏了，卻全忘了什麽味；面前只剩下一張空盤。他的旁邊，一面立着他的父親，一面立着他的母親，兩人的眼光，都彷彿要在他身裏注進什麽又要取出什麽似的；便禁不住心跳起來，按着胸膛，又是一陣咳嗽。

[P0025] 『睡一會罷，——便好了。』

[P0026] 小栓依他母親的話，咳着睡了。華大媽候他喘氣平靜，纔輕輕的給他蓋上了滿幅補釘的夾被。

[P0027] 店裏坐着許多人，老栓也忙了，提着大銅壺，一趟一趟的給客人沖茶；兩個眼眶，都圍着一圈黑線。

[P0028] 『老栓，你有些不舒服麽？——你生病麽？』一個花白鬍子的人說。

[P0029] 『沒有。』

[P0030] 『沒有？——我想笑嘻嘻的，原也不像……』花白鬍子便取消了自己的話。

[P0031] 『老栓只是忙。要是他的兒子……』駝背五少爺話還未完，突然闖進了一個滿臉橫肉的人，被一件玄色布衫，散着紐釦，用很寬的玄色腰帶，胡亂綑在腰間。剛進門，便對老栓嚷道：——

[P0032] 『喫了麽？好了麽？老栓，就是運氣了你！你運氣，要不是我信息靈。……』

[P0033] 老栓一手提了茶壺，一手恭恭敬敬的垂着；笑嘻嘻的聽。滿座的人，也都恭恭敬敬的聽。華大媽也黑着眼眶，笑嘻嘻的送出茶碗茶葉來，加上一個橄欖，老栓便去沖了水。

[P0034] 『這是包好！這是與衆不同的。你想，趁熱的拏來，趁熱喫下。』橫肉的人只是嚷。

[P0035] 『眞的呢，要沒有康大叔照顧，怎麽會這樣……』華大媽也很感激的謝他。

[P0036] 『包好，包好！這樣的趁熱喫下。這樣的人血饅頭，什麽癆病都包好！』

[P0037] 華大媽聽到『癆病』這兩個字，變了一點臉色，似乎有些不高興；但又立刻堆上笑，搭赸着走開了。這康大叔卻沒有覺察，仍然提高了喉嚨只是嚷，嚷得裏面睡着的小栓也合夥咳嗽起來。

[P0038] 『原來你家小栓碰到了這樣的好運氣了。這病自然一定全好；怪不得老栓整天的笑着呢。』花白鬍子一面說，一面走到康大叔面前，低聲下氣的問道，『康大叔——聽說今天結果的一個犯人，便是夏家的孩子，那是誰的孩子？究竟是什麽事？』

[P0039] 『誰的？不就是夏四奶奶的兒子麽？那個小傢伙！』康大叔見衆人都聳起耳朵聽他，便格外高興，橫肉塊塊飽綻，越發大聲說，『這小東西不要命，不要就是了。我可是這一回一點沒有得到好處；連剝下來的衣服，都給管牢的紅眼睛阿義拏去了。——第一要算我們栓叔運氣；第二是夏三爺賞了二十五兩雪白的銀子，獨自落腰包，一文不花。』

[P0040] 小栓慢慢的從小屋子走出，兩手按了胸口，不住的咳嗽；走到竈下，盛出一碗冷飯，泡上熱水，坐下便喫。華大媽跟着他走，輕輕的問道，『小栓你好些麽？——你仍舊只是肚餓？……』

[P0041] 『包好，包好！』康大叔瞥了小栓一眼，仍然回過臉，對衆人說，『夏三爺眞是乖角兒，要是他不先吿官，連他滿門抄斬。現在怎樣？銀子！——這小東西也眞不成東西！關在牢裏，還要勸牢頭造反。』

[P0042] 『阿呀，那還了得。』坐在後排的一個二十多歲的人，很現出氣憤模樣。

[P0043] 『你要曉得紅眼睛阿義是去盤盤底細的，他卻和他攀談了。他說：這大淸的天下是我們大家的。你想：這是人話麽？紅眼睛原知道他家裏只有一個老娘，可是沒有料到他竟會那麽窮，搾不出一點油水，已經氣破肚皮了。他還要老虎頭上搔癢，便給他兩個嘴巴！』

[P0044] 『義哥是一手好拳棒，這兩下，一定够他受用了。』壁角的駝背忽然高興起來。

[P0045] 『他這賤骨頭打不怕，還要說可憐可憐哩。』

[P0046] 花白鬍子的人說，『打了這種東西，有什麽可憐呢？』

[P0047] 康大叔顯出看他不上的樣子，冷笑着說，『你沒有聽淸我的話；看他神氣，是說阿義可憐哩！』

[P0048] 聽着的人的眼光，忽然有些板滯；話也停頓了，小栓已經喫完飯，喫得滿身流汗，頭上都冒出蒸氣來。

[P0049] 『阿義可憐——瘋話，簡直是發了瘋了。』花白鬍子恍然大悟似的說。

[P0050] 『發了瘋了。』二十多歲的人也恍然大悟的說。

[P0051] 店裏的坐客，便又現出活氣，談笑起來。小栓也趁着熱鬧，拚命咳嗽；康大叔走上前，拍他肩膀說：——

[P0052] 『包好！小栓——你不要這麽咳。包好！』

[P0053] 『瘋了。』駝背五少爺點着頭說。

[P0054] 西關外靠着城根的地面，本是一塊官地；中間歪歪斜斜一條細路，是貪走便道的人，用鞋底造成的，但卻成了自然的界限。路的左邊，都埋着死刑和瘦斃的人，右邊是窮人的叢塚。兩面都已埋到層層疊疊，宛然闊人家裏祝壽時候的饅頭。

[P0055] 這一年的淸明，分外寒冷；楊柳纔吐出半粒米大的新芽。天明未久，華大媽已在右邊的一坐新墳前面，排出四碟菜，一碗飯，哭了一場。化過紙，呆呆的坐在地上；彷彿等候什麽似的，但自己也說不出等候什麽。微風起來，吹動他短髮，確乎比去年白得多了。

[P0056] 小路上又來了一個女人，也是半白頭髮，襤褸的衣裙；提一個破舊的朱漆圓籃，外挂一串紙錠，三步一歇的走。忽然見華大媽坐在地上看他，便有些躊躇，慘白的臉上，現出些羞愧的顏色；但終于硬着頭皮，走到左邊的一坐墳前，放下了籃子。

[P0057] 那墳與小栓的墳，一字兒排着，中間只隔一條小路。華大媽看他排好四碟菜，一碗飯，立着哭了一通，化過紙錠；心裏暗暗地想，『這墳裏的也是兒子了。』那老女人徘徊觀望了一回，忽然手脚有些發抖，蹌蹌踉踉退下幾步，瞪着眼只是發怔。

[P0058] 華大媽見這樣子，生怕他傷心到快要發狂了；便忍不住立起身，跨過小路，低聲對他說，『你這位老奶奶不要傷心了，——我們還是回去罷。』

[P0059] 那人點一點頭，眼睛仍然向上瞪着；也低聲吃吃的說道，『你看。——看這是什麽呢？』

[P0060] 華大媽跟了他指頭看去，眼光便到了前面的墳，這墳上草根還沒有全合，露出一塊一塊的黃土，煞是難看。再往上仔細看時，卻不覺也喫一驚；——分明有一圈紅白的花，圍着那尖圓的墳頂。

[P0061] 他們的眼睛都已老花多年了，但望這紅白的花，卻還能明白看見。花也不很多，圓圓的排成一個圈，不很精神，倒也整齊。華大媽忙看他兒子和別人的墳，卻只有不怕冷的幾點靑白小花，零星開着；便覺得心裏忽然感到一種不足和空虛，不願意根究。那老女人又走近幾步，細看了一遍，自言自語的說，『這沒有根，不像自己開的！這地方有誰來呢？孩子不會來玩；——親戚本家早不來了。——這是怎麽一回事呢？』他想了又想，忽又流下淚來，大聲說道：——

[P0062] 『瑜兒，他們都寃枉了你，你還是忘不了，傷心不過，今天特意顯點靈，要我知道麽？』他四面一看，只見一隻烏鴉，站在一株沒有葉的樹上，便接着說，『我知道了。——瑜兒，可憐他們坑了你，他們將來總有報應，天都知道；你閉了眼睛就是了。——你如果眞在這裏，聽到我的話，——便教這烏鴉飛上你的墳頂，給我看罷。』

[P0063] 微風早經停息了；枯草支支直立，有如銅絲。一絲發抖的聲音，在空氣中愈顫愈細，細到沒有，周圍便都是死一般靜。兩人站在枯草叢裏，仰面看那烏鴉；那烏鴉也在筆直的樹枝間，縮着頭，鐵鑄一般站着。

[P0064] 許多的工夫過去了；上墳的人漸漸增多，幾個老的小的，在土墳間出沒。

[P0065] 華大媽不知怎的，似乎卸下了一挑重擔，便想到要走；一面勸着說，『我們還是回去罷。』

[P0066] 那老女人歎一口氣，無精打采的收起飯菜；又遲疑了一刻，終于慢慢地走了。嘴裏自言自語的說，『這是怎麽一回事呢？……』

[P0067] 他們走不上二三十步遠，忽聽得背後『啞——』的一聲大叫；兩個人都竦然的回過頭，只見那烏鴉張開兩翅，一挫身，直向着遠處的天空，箭也似的飛去了。

[P0068] （一九一九年四月。）

中文辅助译文段落时间线（可能为空；只能辅助理解，gold evidence 仍必须回到原文段落）：
(none)

已有人工标注上下文（可能为空；若存在，只作参考，不要机械复制）：
metadata:
  story_id: medicine
  title: "藥"
  author: "魯迅"
  language: zh
  source_text_path: data/foreshadow_causality_benchmark/novels/normalized_texts/medicine.txt
  source_url: https://zh.wikisource.org/wiki/%E8%97%A5
  copyright_status: public_domain_wikisource_pd_1996_and_pd_china_organization
  genre: modern_chinese_symbolic_realism
  length_level: short
  structure_type: [symbolic, social]
annotation_guide:
  focus:
    - 標注華老栓買人血饅頭、夏瑜被處刑、小栓病情與墳場相遇之間的雙線結構。
    - 把人血饅頭標為迷信性物件與社會誤解的交叉伏筆，不只標為普通道具。
    - 標注花環與烏鴉作為象徵性 payoff；花環提示革命者並未完全無人理解，烏鴉則拒絕直接神蹟化解釋。
  boundary_notes:
    - 「人血饅頭治癆病」是人物信念，不應標為客觀有效因果。
    - 夏瑜的革命行動多由茶客轉述呈現，事件可標為 narrated，但其被處刑和被誤解是敘事中的穩定事實。
events:
  - event_id: MD_E01
    story_id: medicine
    chapter_or_section: 一
    text_span: P0001-P0005
    summary: 華老栓帶錢出門，準備為小栓尋找治病的「藥」。
    participants: [華老栓, 華大媽, 小栓]
    location: 華家茶館
    time: 秋天後半夜
    event_type: decision
    certainty: {value: certain}
    narrative_reality_level: {value: real}
  - event_id: MD_E02
    story_id: medicine
    chapter_or_section: 一
    text_span: P0010-P0014
    summary: 處刑現場的人群聚集，華老栓用洋錢買到蘸血的饅頭。
    participants: [華老栓, 康大叔, 圍觀者, 夏瑜]
    location: 丁字街口
    time: 清晨
    event_type: action
    certainty: {value: certain}
    narrative_reality_level: {value: real}
  - event_id: MD_E03
    story_id: medicine
    chapter_or_section: 二
    text_span: P0018-P0026
    summary: 華家把人血饅頭烤給小栓吃，期待它治好癆病。
    participants: [華老栓, 華大媽, 小栓]
    location: 華家茶館
    time: 清晨回家後
    event_type: action
    certainty: {value: certain}
    narrative_reality_level: {value: real}
  - event_id: MD_E04
    story_id: medicine
    chapter_or_section: 三
    text_span: P0036-P0052
    summary: 康大叔和茶客談論人血饅頭、夏瑜被殺以及夏瑜在獄中勸牢頭造反。
    participants: [康大叔, 華老栓, 華大媽, 茶客, 小栓, 夏瑜]
    location: 華家茶館
    time: 同日茶館營業時
    event_type: dialogue
    certainty: {value: certain}
    narrative_reality_level: {value: narrated}
  - event_id: MD_E05
    story_id: medicine
    chapter_or_section: 四
    text_span: P0054-P0057
    summary: 清明時華大媽在小栓墳前祭奠，夏四奶奶到相鄰墳前祭奠夏瑜。
    participants: [華大媽, 夏四奶奶, 小栓, 夏瑜]
    location: 西關外墳地
    time: 次年清明
    event_type: discovery
    certainty: {value: certain}
    narrative_reality_level: {value: real}
  - event_id: MD_E06
    story_id: medicine
    chapter_or_section: 四
    text_span: P0060-P0062
    summary: 夏四奶奶發現夏瑜墳上有紅白花環，將其理解為兒子顯靈或伸冤。
    participants: [夏四奶奶, 華大媽, 夏瑜]
    location: 夏瑜墳前
    time: 清明
    event_type: revelation
    certainty: {value: certain}
    narrative_reality_level: {value: symbolic}
  - event_id: MD_E07
    story_id: medicine
    chapter_or_section: 四
    text_span: P0062-P0067
    summary: 夏四奶奶請烏鴉飛到墳頂作為顯靈證據，但烏鴉最後飛向遠處天空。
    participants: [夏四奶奶, 華大媽, 烏鴉]
    location: 墳地
    time: 清明
    event_type: revelation
    certainty: {value: certain}
    narrative_reality_level: {value: symbolic}
causal_edges:
  - edge_id: MD_C01
    story_id: medicine
    source_event_id: MD_E01
    target_event_id: MD_E02
    relation_type: motivates
    strength: {value: strong}
    evidence_text_span: P0001-P0014
    explanation: 華家相信人血饅頭能治病，這一信念促使華老栓帶錢去處刑現場購買。
  - edge_id: MD_C02
    story_id: medicine
    source_event_id: MD_E02
    target_event_id: MD_E03
    relation_type: enables
    strength: {value: strong}
    evidence_text_span: P0012-P0026
    explanation: 華老栓買到蘸血饅頭，使華家能將它作為「藥」給小栓吃。
  - edge_id: MD_C03
    story_id: medicine
    source_event_id: MD_E04
    target_event_id: MD_E02
    relation_type: reveals
    strength: {value: strong}
    evidence_text_span: P0038-P0047
    explanation: 茶館談話揭示早晨被處刑者是夏瑜，華老栓購買的「藥」來自革命者的血。
  - edge_id: MD_C04
    story_id: medicine
    source_event_id: MD_E03
    target_event_id: MD_E05
    relation_type: prevents
    strength: {value: strong}
    evidence_text_span: P0024-P0055
    explanation: 人血饅頭沒有治好小栓；墳場祭奠反向證明迷信療法無效。
  - edge_id: MD_C05
    story_id: medicine
    source_event_id: MD_E04
    target_event_id: MD_E06
    relation_type: symbolically_echoes
    strength: {value: medium}
    evidence_text_span: P0041-P0062
    explanation: 茶客對夏瑜的誤解與墳上花環形成照應，後者提示夏瑜可能並非完全孤立。
foreshadowing_units:
  - foreshadowing_id: MD_F01
    story_id: medicine
    foreshadowing_text_span: P0012-P0015
    foreshadowing_summary: 鮮紅饅頭被當作能帶回「新生命」的藥。
    foreshadowing_type: symbolic
    trigger_event_id: MD_E03
    payoff_event_id: MD_E05
    payoff_text_span: P0054-P0057
    payoff_summary: 小栓已死，墳場場景否定人血饅頭的療效。
    payoff_type: negative
    confidence: {value: high}
    explanation: 物件被人物視作救命藥，結局證明其只是迷信和暴力消費的象徵。
  - foreshadowing_id: MD_F02
    story_id: medicine
    foreshadowing_text_span: P0038-P0047
    foreshadowing_summary: 茶客把夏瑜理解為「不要命」和「發瘋」的人。
    foreshadowing_type: social
    trigger_event_id: MD_E05
    payoff_event_id: MD_E06
    payoff_text_span: P0060-P0062
    payoff_summary: 夏瑜墳上的花環回收革命者被誤解但仍可能有人悼念的線索。
    payoff_type: symbolic
    confidence: {value: high}
    explanation: 社會誤解在墳場被象徵性打開，但不是用明確敘事答案解決。
  - foreshadowing_id: MD_F03
    story_id: medicine
    foreshadowing_text_span: P0054
    foreshadowing_summary: 墳地小路把死刑者和窮人分隔在兩邊。
    foreshadowing_type: social
    trigger_event_id: MD_E05
    payoff_event_id: MD_E05
    payoff_text_span: P0055-P0057
    payoff_summary: 兩位母親在相鄰墳前相遇，將華家和夏家兩條敘事線並置。
    payoff_type: symbolic
    confidence: {value: medium}
    explanation: 空間分界把社會分類可視化，又讓兩條悲劇線在同一場景中相互照亮。
characters:
  - character_id: MD_CH01
    story_id: medicine
    name: 華老栓
    role: 茶館主人 / 求藥者
    stable_traits: [順從, 迷信, 愛子心切]
    current_motivation_by_event:
      - event_id: MD_E02
        motivation: 想治好小栓的癆病。
        knowledge_state: 相信人血饅頭是有效偏方，不理解夏瑜的政治含義。
        emotional_state: 緊張而懷有希望。
        goal: 用錢換得能救兒子的藥。
  - character_id: MD_CH02
    story_id: medicine
    name: 夏瑜
    role: 被處刑的革命者
    stable_traits: [反抗, 孤立, 被民眾誤解]
    current_motivation_by_event:
      - event_id: MD_E04
        motivation: 勸牢頭造反，延續革命信念。
        knowledge_state: 知道自己身處監禁和處刑危險。
        emotional_state: 堅持。
        goal: 喚醒他人而非求生。
  - character_id: MD_CH03
    story_id: medicine
    name:
...
```
