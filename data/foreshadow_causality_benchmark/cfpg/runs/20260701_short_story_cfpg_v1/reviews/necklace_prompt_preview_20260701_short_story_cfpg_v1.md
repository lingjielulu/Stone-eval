# Short Story CFPG Prompt Preview

## system

```text
你是短篇小说伏笔-触发-回收结构标注员。任务是在给定的全文段落时间线中，高召回抽取候选 Foreshadow-Trigger-Payoff 三元组。只能依据输入文本，不得使用外部知识或你对作品结局的先验记忆。只输出合法 JSON。
```

## user

```text
请对下面的短篇小说段落时间线执行第一步：高召回候选识别。

作品：
- story_id: necklace
- title: The Diamond Necklace
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
[P0001] The girl was one of those pretty and charming young creatures who sometimes are born, as if by a slip of fate, into a family of clerks. She had no dowry, no expectations, no way of being known, understood, loved, married by any rich and distinguished man; so she let herself be married to a little clerk of the Ministry of Public Instruction.

[P0002] She dressed plainly because she could not dress well, but she was unhappy as if she had really fallen from a higher station; since with women there is neither caste nor rank, for beauty, grace and charm take the place of family and birth. Natural ingenuity, instinct for what is elegant, a supple mind are their sole hierarchy, and often make of women of the people the equals of the very greatest ladies.

[P0003] Mathilde suffered ceaselessly, feeling herself born to enjoy all delicacies and all luxuries. She was distressed at the poverty of her dwelling, at the bareness of the walls, at the shabby chairs, the ugliness of the curtains. All those things, of which another woman of her rank would never even have been conscious, tortured her and made her angry. The sight of the little Breton peasant who did her humble housework aroused in her despairing regrets and bewildering dreams. She thought of silent antechambers hung with Oriental tapestry, illumined by tall bronze candelabra, and of two great footmen in knee breeches who sleep in the big armchairs, made drowsy by the oppressive heat of the stove. She thought of long reception halls hung with ancient silk, of the dainty cabinets containing priceless curiosities and of the little coquettish perfumed reception rooms made for chatting at five o'clock with intimate friends, with men famous and sought after, whom all women envy and whose attention they all desire.

[P0004] When she sat down to dinner, before the round table covered with a tablecloth in use three days, opposite her husband, who uncovered the soup tureen and declared with a delighted air, “Ah, the good soup! I don't know anything better than that,” she thought of dainty dinners, of shining silverware, of tapestry that peopled the walls with ancient personages and with strange birds flying in the midst of a fairy forest; and she thought of delicious dishes served on marvellous plates and of the whispered gallantries to which you listen with a sphinxlike smile while you are eating the pink meat of a trout or the wings of a quail.

[P0005] She had no gowns, no jewels, nothing. And she loved nothing but that. She felt made for that. She would have liked so much to please, to be envied, to be charming, to be sought after.

[P0006] She had a friend, a former schoolmate at the convent, who was rich, and whom she did not like to go to see any more because she felt so sad when she came home.

[P0007] But one evening her husband reached home with a triumphant air and holding a large envelope in his hand.

[P0008] “There,” said he, “there is something for you.”

[P0009] She tore the paper quickly and drew out a printed card which bore these words:

[P0010] The Minister of Public Instruction and Madame Georges Ramponneau request the honor of M. and Madame Loisel's company at the palace of the Ministry on Monday evening, January 18th.

[P0011] Instead of being delighted, as her husband had hoped, she threw the invitation on the table crossly, muttering:

[P0012] “What do you wish me to do with that?”

[P0013] “Why, my dear, I thought you would be glad. You never go out, and this is such a fine opportunity. I had great trouble to get it. Every one wants to go; it is very select, and they are not giving many invitations to clerks. The whole official world will be there.”

[P0014] She looked at him with an irritated glance and said impatiently:

[P0015] “And what do you wish me to put on my back?”

[P0016] He had not thought of that. He stammered:

[P0017] “Why, the gown you go to the theatre in. It looks very well to me.”

[P0018] He stopped, distracted, seeing that his wife was weeping. Two great tears ran slowly from the corners of her eyes toward the corners of her mouth.

[P0019] “What's the matter? What's the matter?” he answered.

[P0020] By a violent effort she conquered her grief and replied in a calm voice, while she wiped her wet cheeks:

[P0021] “Nothing. Only I have no gown, and, therefore, I can't go to this ball. Give your card to some colleague whose wife is better equipped than I am.”

[P0022] He was in despair. He resumed:

[P0023] “Come, let us see, Mathilde. How much would it cost, a suitable gown, which you could use on other occasions—something very simple?”

[P0024] She reflected several seconds, making her calculations and wondering also what sum she could ask without drawing on herself an immediate refusal and a frightened exclamation from the economical clerk.

[P0025] Finally she replied hesitating:

[P0026] “I don't know exactly, but I think I could manage it with four hundred francs.”

[P0027] He grew a little pale, because he was laying aside just that amount to buy a gun and treat himself to a little shooting next summer on the plain of Nanterre, with several friends who went to shoot larks there of a Sunday.

[P0028] But he said:

[P0029] “Very well. I will give you four hundred francs. And try to have a pretty gown.”

[P0030] The day of the ball drew near and Madame Loisel seemed sad, uneasy, anxious. Her frock was ready, however. Her husband said to her one evening:

[P0031] “What is the matter? Come, you have seemed very queer these last three days.”

[P0032] And she answered:

[P0033] “It annoys me not to have a single piece of jewelry, not a single ornament, nothing to put on. I shall look poverty-stricken. I would almost rather not go at all.”

[P0034] “You might wear natural flowers,” said her husband. “They're very stylish at this time of year. For ten francs you can get two or three magnificent roses.”

[P0035] She was not convinced.

[P0036] “No; there's nothing more humiliating than to look poor among other women who are rich.”

[P0037] “How stupid you are!” her husband cried. “Go look up your friend, Madame Forestier, and ask her to lend you some jewels. You're intimate enough with her to do that.”

[P0038] She uttered a cry of joy:

[P0039] “True! I never thought of it.”

[P0040] The next day she went to her friend and told her of her distress.

[P0041] Madame Forestier went to a wardrobe with a mirror, took out a large jewel box, brought it back, opened it and said to Madame Loisel:

[P0042] “Choose, my dear.”

[P0043] She saw first some bracelets, then a pearl necklace, then a Venetian gold cross set with precious stones, of admirable workmanship. She tried on the ornaments before the mirror, hesitated and could not make up her mind to part with them, to give them back. She kept asking:

[P0044] “Haven't you any more?”

[P0045] “Why, yes. Look further; I don't know what you like.”

[P0046] Suddenly she discovered, in a black satin box, a superb diamond necklace, and her heart throbbed with an immoderate desire. Her hands trembled as she took it. She fastened it round her throat, outside her high-necked waist, and was lost in ecstasy at her reflection in the mirror.

[P0047] Then she asked, hesitating, filled with anxious doubt:

[P0048] “Will you lend me this, only this?”

[P0049] “Why, yes, certainly.”

[P0050] She threw her arms round her friend's neck, kissed her passionately, then fled with her treasure.

[P0051] The night of the ball arrived. Madame Loisel was a great success. She was prettier than any other woman present, elegant, graceful, smiling and wild with joy. All the men looked at her, asked her name, sought to be introduced. All the attaches of the Cabinet wished to waltz with her. She was remarked by the minister himself.

[P0052] She danced with rapture, with passion, intoxicated by pleasure, forgetting all in the triumph of her beauty, in the glory of her success, in a sort of cloud of happiness comprised of all this homage, admiration, these awakened desires and of that sense of triumph which is so sweet to woman's heart.

[P0053] She left the ball about four o'clock in the morning. Her husband had been sleeping since midnight in a little deserted anteroom with three other gentlemen whose wives were enjoying the ball.

[P0054] He threw over her shoulders the wraps he had brought, the modest wraps of common life, the poverty of which contrasted with the elegance of the ball dress. She felt this and wished to escape so as not to be remarked by the other women, who were enveloping themselves in costly furs.

[P0055] Loisel held her back, saying: “Wait a bit. You will catch cold outside. I will call a cab.”

[P0056] But she did not listen to him and rapidly descended the stairs. When they reached the street they could not find a carriage and began to look for one, shouting after the cabmen passing at a distance.

[P0057] They went toward the Seine in despair, shivering with cold. At last they found on the quay one of those ancient night cabs which, as though they were ashamed to show their shabbiness during the day, are never seen round Paris until after dark.

[P0058] It took them to their dwelling in the Rue des Martyrs, and sadly they mounted the stairs to their flat. All was ended for her. As to him, he reflected that he must be at the ministry at ten o'clock that morning.

[P0059] She removed her wraps before the glass so as to see herself once more in all her glory. But suddenly she uttered a cry. She no longer had the necklace around her neck!

[P0060] “What is the matter with you?” demanded her husband, already half undressed.

[P0061] She turned distractedly toward him.

[P0062] “I have—I have—I've lost Madame Forestier's necklace,” she cried.

[P0063] He stood up, bewildered.

[P0064] “What!—how? Impossible!”

[P0065] They looked among the folds of her skirt, of her cloak, in her pockets, everywhere, but did not find it.

[P0066] “You're sure you had it on when you left the ball?” he asked.

[P0067] “Yes, I felt it in the vestibule of the minister's house.”

[P0068] “But if you had lost it in the street we should have heard it fall. It must be in the cab.”

[P0069] “Yes, probably. Did you take his number?”

[P0070] “No. And you—didn't you notice it?”

[P0071] “No.”

[P0072] They looked, thunderstruck, at each other. At last Loisel put on his clothes.

[P0073] “I shall go back on foot,” said he, “over the whole route, to see whether I can find it.”

[P0074] He went out. She sat waiting on a chair in her ball dress, without strength to go to bed, overwhelmed, without any fire, without a thought.

[P0075] Her husband returned about seven o'clock. He had found nothing.

[P0076] He went to police headquarters, to the newspaper offices to offer a reward; he went to the cab companies—everywhere, in fact, whither he was urged by the least spark of hope.

[P0077] She waited all day, in the same condition of mad fear before this terrible calamity.

[P0078] Loisel returned at night with a hollow, pale face. He had discovered nothing.

[P0079] “You must write to your friend,” said he, “that you have broken the clasp of her necklace and that you are having it mended. That will give us time to turn round.”

[P0080] She wrote at his dictation.

[P0081] At the end of a week they had lost all hope. Loisel, who had aged five years, declared:

[P0082] “We must consider how to replace that ornament.”

[P0083] The next day they took the box that had contained it and went to the jeweler whose name was found within. He consulted his books.

[P0084] “It was not I, madame, who sold that necklace; I must simply have furnished the case.”

[P0085] Then they went from jeweler to jeweler, searching for a necklace like the other, trying to recall it, both sick with chagrin and grief.

[P0086] They found, in a shop at the Palais Royal, a string of diamonds that seemed to them exactly like the one they had lost. It was worth forty thousand francs. They could have it for thirty-six.

[P0087] So they begged the jeweler not to sell it for three days yet. And they made a bargain that he should buy it back for thirty-four thousand francs, in case they should find the lost necklace before the end of February.

[P0088] Loisel possessed eighteen thousand francs which his father had left him. He would borrow the rest.

[P0089] He did borrow, asking a thousand francs of one, five hundred of another, five louis here, three louis there. He gave notes, took up ruinous obligations, dealt with usurers and all the race of lenders. He compromised all the rest of his life, risked signing a note without even knowing whether he could meet it; and, frightened by the trouble yet to come, by the black misery that was about to fall upon him, by the prospect of all the physical privations and moral tortures that he was to suffer, he went to get the new necklace, laying upon the jeweler's counter thirty-six thousand francs.

[P0090] When Madame Loisel took back the necklace Madame Forestier said to her with a chilly manner:

[P0091] “You should have returned it sooner; I might have needed it.”

[P0092] She did not open the case, as her friend had so much feared. If she had detected the substitution, what would she have thought, what would she have said? Would she not have taken Madame Loisel for a thief?

[P0093] Thereafter Madame Loisel knew the horrible existence of the needy. She bore her part, however, with sudden heroism. That dreadful debt must be paid. She would pay it. They dismissed their servant; they changed their lodgings; they rented a garret under the roof.

[P0094] She came to know what heavy housework meant and the odious cares of the kitchen. She washed the dishes, using her dainty fingers and rosy nails on greasy pots and pans. She washed the soiled linen, the shirts and the dishcloths, which she dried upon a line; she carried the slops down to the street every morning and carried up the water, stopping for breath at every landing. And dressed like a woman of the people, she went to the fruiterer, the grocer, the butcher, a basket on her arm, bargaining, meeting with impertinence, defending her miserable money, sou by sou.

[P0095] Every month they had to meet some notes, renew others, obtain more time.

[P0096] Her husband worked evenings, making up a tradesman's accounts, and late at night he often copied manuscript for five sous a page.

[P0097] This life lasted ten years.

[P0098] At the end of ten years they had paid everything, everything, with the rates of usury and the accumulations of the compound interest.

[P0099] Madame Loisel looked old now. She had become the woman of impoverished households—strong and hard and rough. With frowsy hair, skirts askew and red hands, she talked loud while washing the floor with great swishes of water. But sometimes, when her husband was at the office, she sat down near the window and she thought of that gay evening of long ago, of that ball where she had been so beautiful and so admired.

[P0100] What would have happened if she had not lost that necklace? Who knows? who knows? How strange and changeful is life! How small a thing is needed to make or ruin us!

[P0101] But one Sunday, having gone to take a walk in the Champs Elysees to refresh herself after the labors of the week, she suddenly perceived a woman who was leading a child. It was Madame Forestier, still young, still beautiful, still charming.

[P0102] Madame Loisel felt moved. Should she speak to her? Yes, certainly. And now that she had paid, she would tell her all about it. Why not?

[P0103] She went up.

[P0104] “Good-day, Jeanne.”

[P0105] The other, astonished to be familiarly addressed by this plain good- wife, did not recognize her at all and stammered:

[P0106] “But—madame!—I do not know—You must have mistaken.”

[P0107] “No. I am Mathilde Loisel.”

[P0108] Her friend uttered a cry.

[P0109] “Oh, my poor Mathilde! How you are changed!”

[P0110] “Yes, I have had a pretty hard life, since I last saw you, and great poverty—and that because of you!”

[P0111] “Of me! How so?”

[P0112] “Do you remember that diamond necklace you lent me to wear at the ministerial ball?”

[P0113] “Yes. Well?”

[P0114] “Well, I lost it.”

[P0115] “What do you mean? You brought it back.”

[P0116] “I brought you back another exactly like it. And it has taken us ten years to pay for it. You can understand that it was not easy for us, for us who had nothing. At last it is ended, and I am very glad.”

[P0117] Madame Forestier had stopped.

[P0118] “You say that you bought a necklace of diamonds to replace mine?”

[P0119] “Yes. You never noticed it, then! They were very similar.”

[P0120] And she smiled with a joy that was at once proud and ingenuous.

[P0121] Madame Forestier, deeply moved, took her hands.

[P0122] “Oh, my poor Mathilde! Why, my necklace was paste! It was worth at most only five hundred francs!”

中文辅助译文段落时间线（可能为空；只能辅助理解，gold evidence 仍必须回到原文段落）：
[P0001] 世上有这样一些女子，容貌姣好，风姿绰约，却偏被命运安排错了，出生在一个小职员家庭。她就是其中的一个。她没有陪嫁，没有可能指望得到的遗产，没有任何方法让一个有钱有地位的男子认识她、了解她、爱她、娶她；于是只好听任家人把她嫁给公共教育部的一个小科员。

[P0002] 她没有钱装饰打扮，只能粗衣布服；但是她非常委屈，就像被降低了身份一样。其实女人本身并没有阶层和种类；她们的美貌、她们的丰韵﹑她们的魅力，就可以作为她们的出身和门第。她们唯一的分野，在于天生的机智、本能的优雅和头脑的灵活；有了这些品质，平民家的姑娘也能与最显耀的贵妇媲美。

[P0003] 她总觉得自己生来就应该珠围翠拥、享尽荣华富贵，因此终日悲悲切切。住房简陋，墙无饰物，座椅破旧，衣着寒酸，让她食不甘味。这一切，换了另一个与她同阶层的女子，也许根本就不会在意，但是却让她痛心疾首，怨愤难平。每当她看到那个矮小的布列塔尼 [ 布列塔尼：法国西部的一个大区。]女人，为她做卑微的家务活儿，她就懊恼不迭，想入非非。她会想到四周悬挂着东方壁毯、青铜高脚灯照得通明的幽静的候见室；想到候见室里两个穿短套裤的高大男仆，被暖气管的高温烤得昏昏沉沉，正在宽大的安乐椅里酣睡。她会想到四壁覆盖着古老丝绸的大客厅；想到陈列着珍贵古玩的精致橱柜以及熏香扑鼻的小巧的内客厅，那是同最知心的男友在午后五点钟促膝倾谈的地方，这些男人无不是女人们垂涎不已﹑梦寐求之、极力邀宠的名流。

[P0004] 每当她坐在那张桌布三天没洗换的圆桌旁吃晚饭，坐在对面的丈夫掀开菜盆，眉飞色舞地赞叹：“啊！多么香的炖肉！我真不知道还有比这更好的了……”她却想着那些丰盛的宴席、闪亮的银餐具、墙上绣有古代人物和仙林珍禽的壁毯﹑盛在精美盘碟中的佳肴，想着享用粉红色鲈鱼或者松鸡翅﹑面带斯芬克斯 [ 斯芬克斯：古埃及狮身人面石雕像的音译。希腊神话中带翼狮身女怪也叫此名，今常用于隐喻谜一样的人物。] 式的神秘微笑听着绵绵情话的情景。

[P0005] 她没有漂亮的衣裳，没有珠宝首饰，什么也没有。而她爱的偏偏就是这些；她觉得自己就是为此而生的。她多么希望能够让男人们喜欢、女人们羡慕，令人瞩目，广受青睐。

[P0006] 她有一个有钱的女友，那是她在女子寄宿学校读书时的同学，她再也不愿去见她了，因为每次回来她都痛不欲生，伤心、悔恨、绝望、苦恼好几天。

[P0007] 一天晚上，她丈夫回家的时候手里拿着一个大信封，满脸扬扬得意的神色。

[P0008] “喏，”他说，“这是给你的。”

[P0009] 她连忙拆开信封，从里面抽出一张卡片，上面印着：

[P0010] 公共教育部长乔治·朗波诺及夫人谨荣幸地邀请罗瓦赛尔先生及夫人光临定于一月十八日（星期一）在本部大楼举行之晚会。

[P0011] 她非但没有像她丈夫所期望的那样欢天喜地，反而气恼地把请柬往桌子上一扔，咕哝着说：

[P0012] “你想想，我要这个干什么？”

[P0013] “可是，亲爱的，我原以为你会很高兴的。你从来也不出门做客，这可是个机会，而且是个难得的机会！我费了很大力气才弄到这张请柬。大家都想要，很难得到，一般是很少给小职员的。你在那里可以看到所有官方人士。”

[P0014] 她用愤怒的目光瞪着他，不耐烦地说：

[P0015] “你想想，我穿什么去？”

[P0016] 他倒没有想到这一点。他吞吞吐吐地说：

[P0017] “你上剧院穿的那条连衣裙呀，依我看，那一条就挺好……”

[P0018] 他说不下去了；见妻子已经哭起来，他又是惊讶又是慌张。两滴大大的泪珠从他妻子的眼角慢慢地流向嘴角。他结结巴巴地问：

[P0019] “你怎么啦？你怎么啦？”

[P0020] 她强打精神把痛苦压了下去，然后擦着被泪水沾湿的两颊，用平静的语调说：

[P0021] “什么事也没有。只不过我没有衣服，反正不能去参加晚会。你还是把请柬随便送给哪个同事吧，他的太太一定比我穿得体面。”

[P0022] 他感到歉疚，马上又说：

[P0023] “别呀，玛蒂尔德。一套过得去的衣裳，别的机会还可以穿的、十分简单的衣裳，得花多少钱？”

[P0024] 她想了几秒钟，心里算了几笔账，同时也在考虑提出怎样一个数目才不致当场就遭到这个节俭的科员拒绝，也不致把他吓得叫出声来。

[P0025] 最后，她吞吞吐吐地说：

[P0026] “我也说不准；不过我看有四百法郎就能拿下来。”

[P0027] 他的脸色变得有点苍白，因为他正好积攒下这样一笔钱，准备买一支枪，夏天和几个朋友去南泰尔平原打猎玩。这些朋友每个星期日都去那里打云雀。

[P0028] 不过他还是说：

[P0029] “好吧。我就给你四百法郎。你可得尽量做一条漂漂亮亮的连衣裙啊。”

[P0030] 晚会的日子临近了，罗瓦赛尔太太好像又发起愁来，忧心忡忡，坐卧不宁。她的衣服可是已经准备停当了呀。一天晚上，丈夫问她：

[P0031] “喂，你怎么啦？三天来你一直怪怪的。”

[P0032] 她回答说：

[P0033] “我既没有首饰，也没有珠宝，身上什么戴得出去的东西也没有，这让我苦恼。我的样子会寒碜死了。我宁可不去参加这个晚会。”

[P0034] 他说：

[P0035] “你就戴几朵鲜花呀。在这个季节，这是很美的。花十个法郎就能买到两三朵非常好看的玫瑰花。”

[P0036] 她丝毫没有被说服。

[P0037] “不行……在那些阔太太中间，显出一副穷酸相，没有比这更丢脸的了。”

[P0038] 她丈夫忽然大喊道：

[P0039] “你真糊涂，去找你的朋友弗莱斯蒂埃太太，跟她借几样首饰就是了。以你跟她的交情，是可以张这个口的。”

[P0040] 她高兴得叫了起来：

[P0041] “真的，我竟然一点儿也没想到。”

[P0042] 第二天，她就到这位朋友家去，对她说了这件苦恼的事。

[P0043] 弗莱斯蒂埃太太立刻走到一个带穿衣镜的衣橱前，取出一个大首饰盒，拿过来打开，对罗瓦赛尔太太说：

[P0044] “尽管挑吧！亲爱的。”

[P0045] 她首先看了几只手镯，又看了一串珍珠项链，然后是一个威尼斯造的镶嵌珠宝的金十字架，做工精致极了。她戴上这些首饰对着镜子左照右照，犹豫不决，舍不得摘下来还给主人。她还总是问：

[P0046] “你再没有别的了？”

[P0047] “有啊。你自己找吧。我不知道你喜欢什么。”

[P0048] 她忽然在一个黑缎子的盒子里发现一条非常华丽的钻石项链，顿时喜欢得心怦怦跳。她拿项链的手也直打哆嗦。她把这条项链戴在脖子上，连衣裙的高领外面，对着镜子里的自己欣喜若狂。

[P0049] 然后，她虽然没有把握，还是焦急不安地问：

[P0050] “你可以把这一件借给我吗？只借这一件。”

[P0051] “当然，完全没问题。”

[P0052] 她扑上去一把搂住朋友的脖子，冲动地拥吻了她一下，便带着宝贝一溜烟地跑回家。

[P0053] 晚会的日子到了。罗瓦赛尔太太大获成功。她比所有的女士都美丽；她既雅致又妩媚，满面春风，快活得几乎发狂。所有的男士都盯着她，打听她的姓名，求人引见。部长办公室的人员全都要和她共舞一曲。部长也注意到了她。

[P0054] 她兴奋地跳舞，发了疯似的投入，快乐得陶醉了；她沉溺在她的美貌的胜利和成功的光辉里，沉溺在所有那些奉承、赞美、爱慕以及对女人来说如此完美的胜利的幸福的云雾里，什么也不去想了。

[P0055] 她在早晨四点钟才离开。她丈夫从半夜起就在一间空荡荡的小客厅里睡着了；那里还有另外三位先生，他们的太太也都在尽情欢乐。

[P0056] 他怕她出门受寒，连忙把带来的衣裳披在她身上，那是日常穿的衣裳，很寒碜，和漂亮的舞衣极不调和。她马上意识到这一点；为了不让身裹豪华皮衣的太太们发现，她想赶快溜走。

[P0057] 罗瓦赛尔拉住她，说：

[P0058] “等一等啊。到外面你会着凉。我去叫一辆马车。”

[P0059] 不过她根本不听他的，飞快地走下楼梯。他们到了街上，那里没有出租马车；于是他们就找起来；见一辆马车在远处走过，他们就追着向车夫大声喊叫。

[P0060] 他们向南朝塞纳河走去，冻得直打哆嗦，几乎绝望了。终于在沿河马路上找到一辆夜间拉客的旧马车。这种马车在巴黎只有天黑以后才看得到，好像它们在白天会自惭形秽似的。

[P0061] 这辆车一直把他们送到殉道者街，他们的家门口；他们凄凄惨惨地爬上楼回到家里。对她来说，一切到此结束。而他呢，还想着要在十点钟赶到部里上班。

[P0062] 她对着镜子脱下披在肩上的旧衣裳，想再看看荣极一时的自己。但是她忽然大叫一声。原来她脖子上的项链不见了。

[P0063] 她丈夫这时衣裳已经脱了一半，问道：

[P0064] “你怎么啦？”

[P0065] 她已经吓坏了，转身对他说：

[P0066] “我……我……我向弗莱斯蒂埃太太借的项链不见了。”

[P0067] 他大吃一惊，猛地站起来：

[P0068] “什么！……怎么会！……这不可能！”

[P0069] 于是他们在裙子的褶皱里﹑大氅的夹层里﹑衣兜里搜寻。还是没找到。

[P0070] 他问：

[P0071] “你确实记得离开舞会的时候还戴着吗？”

[P0072] “是啊，在部里的前厅里我还摸过它呢。”

[P0073] “不过，如果是在街上丢的，掉下来的时候我们会听见的呀。大概是掉在车上了。”

[P0074] “对，有可能。你记下车号了吗？”

[P0075] “没有。你呢，你也没注意车号？”

[P0076] “没有。”

[P0077] 他们你看我，我看你，惊呆了。最后罗瓦赛尔重新穿上衣裳，说：

[P0078] “我去把我们刚才步行的这段路再走一遍，看看能不能找到。”

[P0079] 说完他就走了出去。她就这样穿着晚会的衣裳，连上床睡下的气力都没有了，沮丧地倒在一张椅子上，既不生火也不想什么。

[P0080] 将近七点钟丈夫回来了。他什么也没找到。

[P0081] 他随即又去警察局和各报馆，请他们代为悬赏寻找；又去出租小马车的各家车行，总之，凡是可能有一点儿希望的地方都去了。

[P0082] 她整天都等着，因为面对这个可怕的灾难，她一直处于惊慌失措的状态。

[P0083] 罗瓦赛尔傍晚才回来，脸也消瘦了，面色惨白。他毫无所获。

[P0084] “只好给你那位朋友写封信了，”他说，“就说你把链子的搭扣弄断了，正在找人修理。这样我们可以有个应付的时间。”

[P0085] 于是他说她写。

[P0086] 过了一个星期，他们已经失去一切希望。

[P0087] 罗瓦赛尔一下子老了五岁。他说：

[P0088] “只好考虑买一条赔她了。”

[P0089] 第二天，他们拿了那个装项链的盒子，按照盒里面印的字号，前往那家珠宝店。珠宝商查了几个账簿，说：

[P0090] “太太，这条项链不是我这儿卖出的，只有盒子是我这儿配的。”

[P0091] 他们于是跑了一家又一家珠宝店，凭他们的记忆，要找一条一模一样的项链。两个人都万分苦恼、心急如焚。

[P0092] 他们在王宫广场的一家店里找到一条钻石项链，看样子跟他们寻找的那一条完全一样。这件首饰原价四万法郎。如果他们要的话，店家三万六就可以卖给他们。

[P0093] 于是他们要求珠宝商三天之内不要卖掉；并且谈妥了条件，如果在二月底以前找到原物，这条项链便作价三万四千法郎由店家收回。

[P0094] 罗瓦赛尔手头有父亲留给他的一万八千法郎。其余的只能借了。

[P0095] 罗瓦赛尔就借起钱来，跟这个借一千法郎，跟那个借五百；这儿借五个路易 [ 路易：自一八○三年起至第一次世界大战之间在法国使用的二十法郎一枚的金币。]，那儿借三个。他签了不少借据，订了不少足以让他倾家荡产的契约，而且不得不同高利贷者和形形色色放债人打交道。他把自己整个下半生都押上了，不管能否偿还就冒险签下字据。他深知未来会有无限烦恼，经受极端的贫困，物质上会饱尝匮乏，精神上会历尽磨难；尽管对这种前景满怀恐惧，他还是把三万六千法郎放到那个商人的柜台上，取来了那条新项链。

[P0096] 罗瓦赛尔太太把首饰还给弗莱斯蒂埃太太时，这位太太面带不悦地说：

[P0097] “你应该早点还给我才对，也许我用得着呢。”

[P0098] 弗莱斯蒂埃太太没有打开盒子看；她的朋友怕的就是这个。如果她发现掉了包，她会怎么想？怎么说？会不会把她当作窃贼呢？

[P0099] 罗瓦赛尔太太可算体验到了缺吃少穿的那种可怕的生活。好在她已经断然而且勇敢地拿定了主意：这笔骇人听闻的债务必须偿还；她一定要偿还。他们辞退了女仆，搬了家，租了一间顶楼的陋室。

[P0100] 她可算体验到了笨重的家务劳动和厨房里的让人腻烦的活儿。锅碗瓢盆都得她自己刷洗，油腻的陶器和铁锅底磨坏了她玫瑰色的手指甲。脏衣服、衬衫、抹布也都得自己洗，然后晾在绳子上。她每天早上把垃圾搬到街上，再把水提到楼上，上一层楼就要停下喘一口气。她穿着和普通平民一样的衣裳，挎着篮子上水果店、杂货店、肉店，没完没了地还价，一个苏一个苏地捍卫她那可怜的钱袋，免不了挨人骂。

[P0101] 每个月都要还几笔债，还有一些则要续借，延长偿还期限。

[P0102] 丈夫每天晚上都要替一个商人誊清账目；夜间还常常替人抄写，抄一页挣五个苏。

[P0103] 这样的生活过了十年。

[P0104] 十年以后，他们把债全部还清了，分文不差，连同高利贷的利息，以及利滚利的利息。

[P0105] 现在，罗瓦赛尔太太看上去苍老了。她变成了穷苦人家里的女强人，又坚忍，又粗犷。头发不注意梳理，裙子穿得歪歪斜斜，两只手通红，说话大嗓门，用大盆大盆的水冲洗地板。不过在她丈夫还在办公室的时候，她偶尔还会坐到窗前，缅怀当年的那个晚会，在那次舞会上她曾是那么美丽，受到那么热情的欢迎。

[P0106] 如果她没有丢失那条项链，今天会是怎样呢？谁知道？谁知道呢？生活就是这么奇怪！这么变幻莫测！只须一点小事就能断送你或者拯救你！

[P0107] 一个星期日，她去香榭丽舍林荫道遛弯儿，缓解一下一周的劳累。猛地，她看见一个妇女带着孩子在散步。原来是弗莱斯蒂埃太太，她还是那么年轻，那么水灵，那么迷人。

[P0108] 罗瓦赛尔太太非常激动。去跟她说话吗？去，当然要去。债务都还清了，她可以把一切都告诉她了。为什么不呢？

[P0109] 于是她走了过去。

[P0110] “您好，让娜。”

[P0111] 对方竟一点也没有认出她来，听见这平民女子如此亲昵地称呼自己，甚感诧异。

[P0112] “可是……太太！……我不知道……您大概认错人了吧。”

[P0113] “没有。我是玛蒂尔德·罗瓦赛尔。”

[P0114] 她的朋友大叫一声。

[P0115] “哎呀！……我可怜的玛蒂尔德，你的变化真大呀！”

[P0116] “是的，自从上一次跟你见面以后，我的日子就很艰难，甚至可以说是穷困潦倒……而这都是因为你！……”

[P0117] “因为我……这是怎么回事？”

[P0118] “你总记得你借给我去参加部里晚会的那条项链吧？”

[P0119] “记得呀，那又怎么啦？”

[P0120] “那又怎么啦！我把它丢了。”

[P0121] “怎么会呢！你不是还给我了吗？”

[P0122] “我还给你的是另外一条一模一样的。为了买它，我们整整还了十年的债。你知道，对我们来说这可不是一件容易的事，我们被弄得简直一无所有。这一切终于都结束了；我太高兴了。”

已有人工标注上下文（可能为空；若存在，只作参考，不要机械复制）：
metadata:
  story_id: necklace
  title: "The Diamond Necklace"
  author: "Guy de Maupassant"
  language: en
  source_text_path: data/foreshadow_causality_benchmark/normalized_texts/necklace.txt
  source_url: https://gutenberg.pglaf.org/3/0/9/3090/3090-0.txt
  copyright_status: public_domain
  genre: twist_realism
  length_level: short
  structure_type: [twist]
annotation_guide:
  focus:
    - Mark Mathilde's class anxiety as a motivational cause, not merely background characterization.
    - Track the necklace as an object clue whose value is assumed rather than verified.
    - Mark the delayed revelation as both payoff and causal reinterpretation of ten years of hardship.
  boundary_notes:
    - Treat the replacement necklace and the borrowed necklace as separate objects.
    - The final sentence is a payoff, but it should not erase the real economic consequences caused by the replacement.
events:
  - event_id: NE_E01
    story_id: necklace
    chapter_or_section: setup
    text_span: P0001-P0006
    summary: Mathilde Loisel feels trapped by modest circumstances and longs for luxury and admiration.
    participants: [Mathilde Loisel]
    location: Loisel home
    time: before the ball invitation
    event_type: internal_state
    certainty: {value: certain}
    narrative_reality_level: {value: real}
  - event_id: NE_E02
    story_id: necklace
    chapter_or_section: setup
    text_span: P0007-P0029
    summary: Loisel brings an invitation, and Mathilde demands a suitable gown before she will attend.
    participants: [Mathilde Loisel, Monsieur Loisel]
    location: Loisel home
    time: before the ball
    event_type: decision
    certainty: {value: certain}
    narrative_reality_level: {value: real}
  - event_id: NE_E03
    story_id: necklace
    chapter_or_section: setup
    text_span: P0043-P0048
    summary: Mathilde borrows what appears to be a superb diamond necklace from Madame Forestier.
    participants: [Mathilde Loisel, Madame Forestier]
    location: Madame Forestier's home
    time: before the ball
    event_type: action
    certainty: {value: certain}
    narrative_reality_level: {value: real}
  - event_id: NE_E04
    story_id: necklace
    chapter_or_section: crisis
    text_span: P0059-P0062
    summary: After the ball Mathilde discovers that the borrowed necklace is missing.
    participants: [Mathilde Loisel, Monsieur Loisel]
    location: Loisel home
    time: after the ball
    event_type: accident
    certainty: {value: certain}
    narrative_reality_level: {value: real}
  - event_id: NE_E05
    story_id: necklace
    chapter_or_section: crisis
    text_span: P0079-P0089
    summary: The Loisels conceal the loss, buy a costly replacement, and incur crushing debt.
    participants: [Mathilde Loisel, Monsieur Loisel]
    location: Paris jewelers and lenders
    time: after the loss
    event_type: deception
    certainty: {value: certain}
    narrative_reality_level: {value: real}
  - event_id: NE_E06
    story_id: necklace
    chapter_or_section: aftermath
    text_span: P0091-P0100
    summary: The Loisels spend ten years repaying the debt and fall into hard poverty.
    participants: [Mathilde Loisel, Monsieur Loisel]
    location: Paris
    time: ten years
    event_type: action
    certainty: {value: certain}
    narrative_reality_level: {value: real}
  - event_id: NE_E07
    story_id: necklace
    chapter_or_section: resolution
    text_span: P0112-P0122
    summary: Madame Forestier reveals that the original necklace was paste and worth very little.
    participants: [Mathilde Loisel, Madame Forestier]
    location: Champs Elysees
    time: ten years later
    event_type: revelation
    certainty: {value: certain}
    narrative_reality_level: {value: real}
causal_edges:
  - edge_id: NE_C01
    story_id: necklace
    source_event_id: NE_E01
    target_event_id: NE_E02
    relation_type: motivates
    strength: {value: strong}
    evidence_text_span: P0001-P0029
    explanation: Mathilde's desire for higher-status appearance motivates her rejection of attending without a gown.
  - edge_id: NE_C02
    story_id: necklace
    source_event_id: NE_E01
    target_event_id: NE_E03
    relation_type: motivates
    strength: {value: strong}
    evidence_text_span: P0005-P0048
    explanation: Her longing for jewels motivates the borrowing of the necklace.
  - edge_id: NE_C03
    story_id: necklace
    source_event_id: NE_E04
    target_event_id: NE_E05
    relation_type: causes
    strength: {value: strong}
    evidence_text_span: P0059-P0089
    explanation: Losing the necklace directly leads to the search, concealment, replacement purchase, and debt.
  - edge_id: NE_C04
    story_id: necklace
    source_event_id: NE_E05
    target_event_id: NE_E06
    relation_type: causes
    strength: {value: strong}
    evidence_text_span: P0089-P0100
    explanation: The replacement debt causes the decade of poverty and labor.
  - edge_id: NE_C05
    story_id: necklace
    source_event_id: NE_E07
    target_event_id: NE_E05
    relation_type: reveals
    strength: {value: strong}
    evidence_text_span: P0112-P0122
    explanation: The final revelation shows that the replacement response was based on a mistaken value assumption.
foreshadowing_units:
  - foreshadowing_id: NE_F01
    story_id: necklace
    foreshadowing_text_span: P0043-P0048
    foreshadowing_summary: Mathilde chooses the superb-looking necklace because of appearance, without verifying value.
    foreshadowing_type: object
    trigger_event_id: NE_E04
    payoff_event_id: NE_E07
    payoff_text_span: P0112-P0122
    payoff_summary: The object is revealed to have been paste, making the sacrifice tragically disproportionate.
    payoff_type: delayed_revelation
    confidence: {value: high}
    explanation: The necklace's assumed value is the hinge of the story's delayed twist.
  - foreshadowing_id: NE_F02
    story_id: necklace
    foreshadowing_text_span: P0001-P0006
    foreshadowing_summary: Mathilde's class anxiety
...
```
