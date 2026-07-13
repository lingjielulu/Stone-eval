# Short Story CFPG Prompt Preview

## system

```text
你是短篇小说伏笔-触发-回收结构标注员。任务是在给定的全文段落时间线中，高召回抽取候选 Foreshadow-Trigger-Payoff 三元组。只能依据输入文本，不得使用外部知识或你对作品结局的先验记忆。只输出合法 JSON。
```

## user

```text
请对下面的短篇小说段落时间线执行第一步：高召回候选识别。

作品：
- story_id: last_leaf
- title: The Last Leaf
- language: en

操作化定义：
- Foreshadow(F): 较早段落引入具体但当时未完全解释/解决的叙事元素，包括物件、异常、规则、空间结构、心理症状、承诺、警告、谎言、身份线索、象征物或关键话语。
- Trigger(T): 使伏笔进入可兑现状态的可观察叙事条件。Trigger 必须是文本中可以定位的事件、发现、行动、状态变化或条件满足，不要写“命运展开”“气氛成熟”这类抽象词。
- Payoff(P): 较晚段落提供具体事件、解释、履行、反转、否定、失败或主题性回收，用来清偿 F 的叙事债务。

本步骤只产生候选，不等同最终 gold。优先召回，但不要输出纯主题呼应或普通即时因果。

硬性约束：
1. payoff_span 必须晚于 foreshadow_span。
2. F/P 之间应有非平凡间隔；普通相邻段落即时因果不要输出。
3. 每条候选必须给 proposed_trigger，且 trigger 必须可观察。
4. 每条候选必须给 paragraph span，例如 "P0012" 或 "P0012-P0015"。
5. 每条候选必须能在输入段落中找到证据。
6. 候选数量最多 8 个。
7. 如果没有合格候选，输出 {"candidates": []}。

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
[P0001] In a little district west of Washington Square the streets have run crazy and broken themselves into small strips called “places.” These “places” make strange angles and curves. One street crosses itself a time or two. An artist once discovered a valuable possibility in this street. Suppose a collector with a bill for paints, paper and canvas should, in traversing this route, suddenly meet himself coming back, without a cent having been paid on account!

[P0002] So, to quaint old Greenwich Village the art people soon came prowling, hunting for north windows and eighteenth-century gables and Dutch attics and low rents. Then they imported some pewter mugs and a chafing dish or two from Sixth avenue, and became a “colony.”

[P0003] At the top of a squatty, three-story brick Sue and Johnsy had their studio. “Johnsy” was familiar for Joanna. One was from Maine; the other from California. They had met at the _table d’hôte_ of an Eighth street “Delmonico’s,” and found their tastes in art, chicory salad and bishop sleeves so congenial that the joint studio resulted.

[P0004] That was in May. In November a cold, unseen stranger, whom the doctors called Pneumonia, stalked about the colony, touching one here and there with his icy fingers. Over on the east side this ravager strode boldly, smiting his victims by scores, but his feet trod slowly through the maze of the narrow and moss-grown “places.”

[P0005] Mr. Pneumonia was not what you would call a chivalric old gentleman. A mite of a little woman with blood thinned by California zephyrs was hardly fair game for the red-fisted, short-breathed old duffer. But Johnsy he smote; and she lay, scarcely moving, on her painted iron bedstead, looking through the small Dutch window-panes at the blank side of the next brick house.

[P0006] One morning the busy doctor invited Sue into the hallway with a shaggy, gray eyebrow.

[P0007] “She has one chance in—let us say, ten,” he said, as he shook down the mercury in his clinical thermometer. “And that chance is for her to want to live. This way people have of lining-up on the side of the undertaker makes the entire pharmacopeia look silly. Your little lady has made up her mind that she’s not going to get well. Has she anything on her mind?”

[P0008] “She—she wanted to paint the Bay of Naples some day,” said Sue.

[P0009] “Paint?—bosh! Has she anything on her mind worth thinking about twice—a man, for instance?”

[P0010] “A man?” said Sue, with a jew’s-harp twang in her voice. “Is a man worth—but, no, doctor; there is nothing of the kind.”

[P0011] “Well, it is the weakness, then,” said the doctor. “I will do all that science, so far as it may filter through my efforts, can accomplish. But whenever my patient begins to count the carriages in her funeral procession I subtract 50 per cent. from the curative power of medicines. If you will get her to ask one question about the new winter styles in cloak sleeves I will promise you a one-in-five chance for her, instead of one in ten.”

[P0012] After the doctor had gone Sue went into the workroom and cried a Japanese napkin to a pulp. Then she swaggered into Johnsy’s room with her drawing board, whistling ragtime.

中文辅助译文段落时间线（可能为空；只能辅助理解，gold evidence 仍必须回到原文段落）：
[P0001] 在华盛顿广场西面的一个小区里，街道仿佛发了狂似的分成了许多叫做“巷子”的小胡 同。这些“巷子”形成许多奇特的角度和曲线。一条街有时自己本身就交 叉了不止一次。有一回一个画家发现这条街有他的可贵之处。如果一个商人去收颜料、纸张和画布的账款，在这条街上转弯抹角、大兜圈子的时候，突然碰到一毛钱也没收到、空手而归的自己，那才有意思呢！

[P0002] 所以，不久之后不少画家就摸索到这个古色古香的老格林尼治村来了。他们逛来逛去，寻求朝北的窗户、18世纪的三角墙、荷兰式的阁楼，以及低廉的房租。然后，他们又从第六街买来一些锡蜡杯子和一两只烘锅，组成了一个“艺术区”。

[P0003] 苏艾和琼珊在一座矮墩墩的的三层楼砖屋的顶楼设立了她们的画室。“琼珊”是琼西的昵称。她俩一个来自缅因州，一个是加利福尼亚州人。她们是在德尔蒙戈饭馆吃客饭时碰到的，彼此一谈，发现她们对艺术、饮食、衣着的口味十分相投，结果便联合租下了那间画室。

[P0004] 那是5月里的事。到了11月，一个冷酷的、肉眼看不见的、医生们叫做“肺炎”的不速之客，在艺术区里悄悄地游荡，用他冰冷的手指头这里碰一下那里碰一下。在广场东头，这个破坏者明目张胆地踏着大步，一下子就击倒几十个受害者，可是在迷宫一样、狭窄而铺满青的“胡 同”里，他的步伐就慢了下来。

[P0005] 肺炎先生不是一个你们心目中行侠仗义的老绅士。一个身子单薄，被加利福尼亚州的西风刮得没有血色的弱女子，本来不应该是这个有着红拳头的、呼吸急促的老家伙打击的对象。然而，琼西却遭到了打击；她躺在一张油漆过的铁床 上，一动也不动，凝望着小小的荷兰式玻璃窗外对面砖房的空墙。

[P0006] 一天早晨，那个忙碌的医生扬了扬他那毛茸茸的灰白色眉毛，把苏叫到外边的走廊上。

[P0007] “我看，她的病只有一成希望，”他说，一面把体温 表里的水银甩下去，“这一成希望在于她自己要不要活下去。人们不想活，情愿照顾殡仪馆的生意，这种精神状态使医药一筹莫展。你的这位小姐满肚子以为自己不会好了。她有什么心事吗？”

[P0008] “她——她希望有一天能够去画那不勒斯海湾。”苏艾说。

[P0009] “绘画？——别瞎扯了！她心里有没有值得想两次的事情。比如说，[1] 男人？”

[P0010] “男人？”苏艾像吹口琴似的扯着嗓子说，“男人难道值得... ...不，医生，没有这样的事。”

[P0011] “能达到的全部力量去治疗她。可要是我的病人开始算计会有多少辆马车送她出丧，我就得把治疗的效果减掉百分之五十。只要你能想法让她对冬季大衣袖子的时新式样感到兴趣而提出一两个问题，那我可以向你保证把医好她的机会从十分之一提高到五分之一。”医生走后，苏艾走进工作室里，把一条日本餐巾哭成一团 湿。后来她手里拿着画板，装做精神抖擞的样子走进琼西的屋子，嘴里吹着爵士音乐调子。

[P0012] 琼西躺着，脸朝着窗口，被子底下的身体纹丝不动。苏以为她睡着了，赶忙停止吹口哨。

已有人工标注上下文（可能为空；若存在，只作参考，不要机械复制）：
(none)
```
