# Short Story CFPG Prompt Preview

## system

```text
你是短篇小说伏笔-触发-回收结构标注员。任务是在给定的全文段落时间线中，高召回抽取候选 Foreshadow-Trigger-Payoff 三元组。只能依据输入文本，不得使用外部知识或你对作品结局的先验记忆。只输出合法 JSON。
```

## user

```text
请对下面的短篇小说段落时间线执行第一步：高召回候选识别。

作品：
- story_id: speckled_band
- title: speckled_band
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
[P0001] VIII. THE ADVENTURE OF THE SPECKLED BAND

[P0002] On glancing over my notes of the seventy odd cases in which I have during the last eight years studied the methods of my friend Sherlock Holmes, I find many tragic, some comic, a large number merely strange, but none commonplace; for, working as he did rather for the love of his art than for the acquirement of wealth, he refused to associate himself with any investigation which did not tend towards the unusual, and even the fantastic. Of all these varied cases, however, I cannot recall any which presented more singular features than that which was associated with the well-known Surrey family of the Roylotts of Stoke Moran. The events in question occurred in the early days of my association with Holmes, when we were sharing rooms as bachelors in Baker Street. It is possible that I might have placed them upon record before, but a promise of secrecy was made at the time, from which I have only been freed during the last month by the untimely death of the lady to whom the pledge was given. It is perhaps as well that the facts should now come to light, for I have reasons to know that there are widespread rumours as to the death of Dr. Grimesby Roylott which tend to make the matter even more terrible than the truth.

[P0003] It was early in April in the year ’83 that I woke one morning to find Sherlock Holmes standing, fully dressed, by the side of my bed. He was a late riser, as a rule, and as the clock on the mantelpiece showed me that it was only a quarter-past seven, I blinked up at him in some surprise, and perhaps just a little resentment, for I was myself regular in my habits.

[P0004] “Very sorry to knock you up, Watson,” said he, “but it’s the common lot this morning. Mrs. Hudson has been knocked up, she retorted upon me, and I on you.”

[P0005] “What is it, then—a fire?”

[P0006] “No; a client. It seems that a young lady has arrived in a considerable state of excitement, who insists upon seeing me. She is waiting now in the sitting-room. Now, when young ladies wander about the metropolis at this hour of the morning, and knock sleepy people up out of their beds, I presume that it is something very pressing which they have to communicate. Should it prove to be an interesting case, you would, I am sure, wish to follow it from the outset. I thought, at any rate, that I should call you and give you the chance.”

[P0007] “My dear fellow, I would not miss it for anything.”

[P0008] I had no keener pleasure than in following Holmes in his professional investigations, and in admiring the rapid deductions, as swift as intuitions, and yet always founded on a logical basis with which he unravelled the problems which were submitted to him. I rapidly threw on my clothes and was ready in a few minutes to accompany my friend down to the sitting-room. A lady dressed in black and heavily veiled, who had been sitting in the window, rose as we entered.

[P0009] “Good-morning, madam,” said Holmes cheerily. “My name is Sherlock Holmes. This is my intimate friend and associate, Dr. Watson, before whom you can speak as freely as before myself. Ha! I am glad to see that Mrs. Hudson has had the good sense to light the fire. Pray draw up to it, and I shall order you a cup of hot coffee, for I observe that you are shivering.”

[P0010] “It is not cold which makes me shiver,” said the woman in a low voice, changing her seat as requested.

[P0011] “What, then?”

[P0012] “It is fear, Mr. Holmes. It is terror.” She raised her veil as she spoke, and we could see that she was indeed in a pitiable state of agitation, her face all drawn and grey, with restless frightened eyes, like those of some hunted animal. Her features and figure were those of a woman of thirty, but her hair was shot with premature grey, and her expression was weary and haggard. Sherlock Holmes ran her over with one of his quick, all-comprehensive glances.

[P0013] “You must not fear,” said he soothingly, bending forward and patting her forearm. “We shall soon set matters right, I have no doubt. You have come in by train this morning, I see.”

[P0014] “You know me, then?”

[P0015] “No, but I observe the second half of a return ticket in the palm of your left glove. You must have started early, and yet you had a good drive in a dog-cart, along heavy roads, before you reached the station.”

[P0016] The lady gave a violent start and stared in bewilderment at my companion.

[P0017] “There is no mystery, my dear madam,” said he, smiling. “The left arm of your jacket is spattered with mud in no less than seven places. The marks are perfectly fresh. There is no vehicle save a dog-cart which throws up mud in that way, and then only when you sit on the left-hand side of the driver.”

[P0018] “Whatever your reasons may be, you are perfectly correct,” said she. “I started from home before six, reached Leatherhead at twenty past, and came in by the first train to Waterloo. Sir, I can stand this strain no longer; I shall go mad if it continues. I have no one to turn to—none, save only one, who cares for me, and he, poor fellow, can be of little aid. I have heard of you, Mr. Holmes; I have heard of you from Mrs. Farintosh, whom you helped in the hour of her sore need. It was from her that I had your address. Oh, sir, do you not think that you could help me, too, and at least throw a little light through the dense darkness which surrounds me? At present it is out of my power to reward you for your services, but in a month or six weeks I shall be married, with the control of my own income, and then at least you shall not find me ungrateful.”

[P0019] Holmes turned to his desk and, unlocking it, drew out a small case-book, which he consulted.

[P0020] “Farintosh,” said he. “Ah yes, I recall the case; it was concerned with an opal tiara. I think it was before your time, Watson. I can only say, madam, that I shall be happy to devote the same care to your case as I did to that of your friend. As to reward, my profession is its own reward; but you are at liberty to defray whatever expenses I may be put to, at the time which suits you best. And now I beg that you will lay before us everything that may help us in forming an opinion upon the matter.”

[P0021] “Alas!” replied our visitor, “the very horror of my situation lies in the fact that my fears are so vague, and my suspicions depend so entirely upon small points, which might seem trivial to another, that even he to whom of all others I have a right to look for help and advice looks upon all that I tell him about it as the fancies of a nervous woman. He does not say so, but I can read it from his soothing answers and averted eyes. But I have heard, Mr. Holmes, that you can see deeply into the manifold wickedness of the human heart. You may advise me how to walk amid the dangers which encompass me.”

[P0022] “I am all attention, madam.”

[P0023] “My name is Helen Stoner, and I am living with my stepfather, who is the last survivor of one of the oldest Saxon families in England, the Roylotts of Stoke Moran, on the western border of Surrey.”

[P0024] Holmes nodded his head. “The name is familiar to me,” said he.

[P0025] “The family was at one time among the richest in England, and the estates extended over the borders into Berkshire in the north, and Hampshire in the west. In the last century, however, four successive heirs were of a dissolute and wasteful disposition, and the family ruin was eventually completed by a gambler in the days of the Regency. Nothing was left save a few acres of ground, and the two-hundred-year-old house, which is itself crushed under a heavy mortgage. The last squire dragged out his existence there, living the horrible life of an aristocratic pauper; but his only son, my stepfather, seeing that he must adapt himself to the new conditions, obtained an advance from a relative, which enabled him to take a medical degree and went out to Calcutta, where, by his professional skill and his force of character, he established a large practice. In a fit of anger, however, caused by some robberies which had been perpetrated in the house, he beat his native butler to death and narrowly escaped a capital sentence. As it was, he suffered a long term of imprisonment and afterwards returned to England a morose and disappointed man.

[P0026] “When Dr. Roylott was in India he married my mother, Mrs. Stoner, the young widow of Major-General Stoner, of the Bengal Artillery. My sister Julia and I were twins, and we were only two years old at the time of my mother’s re-marriage. She had a considerable sum of money—not less than £ 1000 a year—and this she bequeathed to Dr. Roylott entirely while we resided with him, with a provision that a certain annual sum should be allowed to each of us in the event of our marriage. Shortly after our return to England my mother died—she was killed eight years ago in a railway accident near Crewe. Dr. Roylott then abandoned his attempts to establish himself in practice in London and took us to live with him in the old ancestral house at Stoke Moran. The money which my mother had left was enough for all our wants, and there seemed to be no obstacle to our happiness.

[P0027] “But a terrible change came over our stepfather about this time. Instead of making friends and exchanging visits with our neighbours, who had at first been overjoyed to see a Roylott of Stoke Moran back in the old family seat, he shut himself up in his house and seldom came out save to indulge in ferocious quarrels with whoever might cross his path. Violence of temper approaching to mania has been hereditary in the men of the family, and in my stepfather’s case it had, I believe, been intensified by his long residence in the tropics. A series of disgraceful brawls took place, two of which ended in the police-court, until at last he became the terror of the village, and the folks would fly at his approach, for he is a man of immense strength, and absolutely uncontrollable in his anger.

[P0028] “Last week he hurled the local blacksmith over a parapet into a stream, and it was only by paying over all the money which I could gather together that I was able to avert another public exposure. He had no friends at all save the wandering gipsies, and he would give these vagabonds leave to encamp upon the few acres of bramble-covered land which represent the family estate, and would accept in return the hospitality of their tents, wandering away with them sometimes for weeks on end. He has a passion also for Indian animals, which are sent over to him by a correspondent, and he has at this moment a cheetah and a baboon, which wander freely over his grounds and are feared by the villagers almost as much as their master.

[P0029] “You can imagine from what I say that my poor sister Julia and I had no great pleasure in our lives. No servant would stay with us, and for a long time we did all the work of the house. She was but thirty at the time of her death, and yet her hair had already begun to whiten, even as mine has.”

[P0030] “Your sister is dead, then?”

[P0031] “She died just two years ago, and it is of her death that I wish to speak to you. You can understand that, living the life which I have described, we were little likely to see anyone of our own age and position. We had, however, an aunt, my mother’s maiden sister, Miss Honoria Westphail, who lives near Harrow, and we were occasionally allowed to pay short visits at this lady’s house. Julia went there at Christmas two years ago, and met there a half-pay major of marines, to whom she became engaged. My stepfather learned of the engagement when my sister returned and offered no objection to the marriage; but within a fortnight of the day which had been fixed for the wedding, the terrible event occurred which has deprived me of my only companion.”

[P0032] Sherlock Holmes had been leaning back in his chair with his eyes closed and his head sunk in a cushion, but he half opened his lids now and glanced across at his visitor.

[P0033] “Pray be precise as to details,” said he.

[P0034] “It is easy for me to be so, for every event of that dreadful time is seared into my memory. The manor-house is, as I have already said, very old, and only one wing is now inhabited. The bedrooms in this wing are on the ground floor, the sitting-rooms being in the central block of the buildings. Of these bedrooms the first is Dr. Roylott’s, the second my sister’s, and the third my own. There is no communication between them, but they all open out into the same corridor. Do I make myself plain?”

[P0035] “Perfectly so.”

[P0036] “The windows of the three rooms open out upon the lawn. That fatal night Dr. Roylott had gone to his room early, though we knew that he had not retired to rest, for my sister was troubled by the smell of the strong Indian cigars which it was his custom to smoke. She left her room, therefore, and came into mine, where she sat for some time, chatting about her approaching wedding. At eleven o’clock she rose to leave me, but she paused at the door and looked back.

[P0037] “‘Tell me, Helen,’ said she, ‘have you ever heard anyone whistle in the dead of the night?’

[P0038] “‘Never,’ said I.

[P0039] “‘I suppose that you could not possibly whistle, yourself, in your sleep?’

[P0040] “‘Certainly not. But why?’

[P0041] “‘Because during the last few nights I have always, about three in the morning, heard a low, clear whistle. I am a light sleeper, and it has awakened me. I cannot tell where it came from—perhaps from the next room, perhaps from the lawn. I thought that I would just ask you whether you had heard it.’

[P0042] “‘No, I have not. It must be those wretched gipsies in the plantation.’

[P0043] “‘Very likely. And yet if it were on the lawn, I wonder that you did not hear it also.’

[P0044] “‘Ah, but I sleep more heavily than you.’

[P0045] “‘Well, it is of no great consequence, at any rate.’ She smiled back at me, closed my door, and a few moments later I heard her key turn in the lock.”

[P0046] “Indeed,” said Holmes. “Was it your custom always to lock yourselves in at night?”

[P0047] “Always.”

[P0048] “And why?”

[P0049] “I think that I mentioned to you that the Doctor kept a cheetah and a baboon. We had no feeling of security unless our doors were locked.”

[P0050] “Quite so. Pray proceed with your statement.”

[P0051] “I could not sleep that night. A vague feeling of impending misfortune impressed me. My sister and I, you will recollect, were twins, and you know how subtle are the links which bind two souls which are so closely allied. It was a wild night. The wind was howling outside, and the rain was beating and splashing against the windows. Suddenly, amid all the hubbub of the gale, there burst forth the wild scream of a terrified woman. I knew that it was my sister’s voice. I sprang from my bed, wrapped a shawl round me, and rushed into the corridor. As I opened my door I seemed to hear a low whistle, such as my sister described, and a few moments later a clanging sound, as if a mass of metal had fallen. As I ran down the passage, my sister’s door was unlocked, and revolved slowly upon its hinges. I stared at it horror-stricken, not knowing what was about to issue from it. By the light of the corridor-lamp I saw my sister appear at the opening, her face blanched with terror, her hands groping for help, her whole figure swaying to and fro like that of a drunkard. I ran to her and threw my arms round her, but at that moment her knees seemed to give way and she fell to the ground. She writhed as one who is in terrible pain, and her limbs were dreadfully convulsed. At first I thought that she had not recognised me, but as I bent over her she suddenly shrieked out in a voice which I shall never forget, ‘Oh, my God! Helen! It was the band! The speckled band!’ There was something else which she would fain have said, and she stabbed with her finger into the air in the direction of the Doctor’s room, but a fresh convulsion seized her and choked her words. I rushed out, calling loudly for my stepfather, and I met him hastening from his room in his dressing-gown. When he reached my sister’s side she was unconscious, and though he poured brandy down her throat and sent for medical aid from the village, all efforts were in vain, for she slowly sank and died without having recovered her consciousness. Such was the dreadful end of my beloved sister.”

[P0052] “One moment,” said Holmes, “are you sure about this whistle and metallic sound? Could you swear to it?”

[P0053] “That was what the county coroner asked me at the inquiry. It is my strong impression that I heard it, and yet, among the crash of the gale and the creaking of an old house, I may possibly have been deceived.”

[P0054] “Was your sister dressed?”

[P0055] “No, she was in her night-dress. In her right hand was found the charred stump of a match, and in her left a match-box.”

[P0056] “Showing that she had struck a light and looked about her when the alarm took place. That is important. And what conclusions did the coroner come to?”

[P0057] “He investigated the case with great care, for Dr. Roylott’s conduct had long been notorious in the county, but he was unable to find any satisfactory cause of death. My evidence showed that the door had been fastened upon the inner side, and the windows were blocked by old-fashioned shutters with broad iron bars, which were secured every night. The walls were carefully sounded, and were shown to be quite solid all round, and the flooring was also thoroughly examined, with the same result. The chimney is wide, but is barred up by four large staples. It is certain, therefore, that my sister was quite alone when she met her end. Besides, there were no marks of any violence upon her.”

[P0058] “How about poison?”

[P0059] “The doctors examined her for it, but without success.”

[P0060] “What do you think that this unfortunate lady died of, then?”

[P0061] “It is my belief that she died of pure fear and nervous shock, though what it was that frightened her I cannot imagine.”

[P0062] “Were there gipsies in the plantation at the time?”

[P0063] “Yes, there are nearly always some there.”

[P0064] “Ah, and what did you gather from this allusion to a band—a speckled band?”

[P0065] “Sometimes I have thought that it was merely the wild talk of delirium, sometimes that it may have referred to some band of people, perhaps to these very gipsies in the plantation. I do not know whether the spotted handkerchiefs which so many of them wear over their heads might have suggested the strange adjective which she used.”

[P0066] Holmes shook his head like a man who is far from being satisfied.

[P0067] “These are very deep waters,” said he; “pray go on with your narrative.”

[P0068] “Two years have passed since then, and my life has been until lately lonelier than ever. A month ago, however, a dear friend, whom I have known for many years, has done me the honour to ask my hand in marriage. His name is Armitage—Percy Armitage—the second son of Mr. Armitage, of Crane Water, near Reading. My stepfather has offered no opposition to the match, and we are to be married in the course of the spring. Two days ago some repairs were started in the west wing of the building, and my bedroom wall has been pierced, so that I have had to move into the chamber in which my sister died, and to sleep in the very bed in which she slept. Imagine, then, my thrill of terror when last night, as I lay awake, thinking over her terrible fate, I suddenly heard in the silence of the night the low whistle which had been the herald of her own death. I sprang up and lit the lamp, but nothing was to be seen in the room. I was too shaken to go to bed again, however, so I dressed, and as soon as it was daylight I slipped down, got a dog-cart at the Crown Inn, which is opposite, and drove to Leatherhead, from whence I have come on this morning with the one object of seeing you and asking your advice.”

[P0069] “You have done wisely,” said my friend. “But have you told me all?”

[P0070] “Yes, all.”

[P0071] “Miss Roylott, you have not. You are screening your stepfather.”

[P0072] “Why, what do you mean?”

[P0073] For answer Holmes pushed back the frill of black lace which fringed the hand that lay upon our visitor’s knee. Five little livid spots, the marks of four fingers and a thumb, were printed upon the white wrist.

[P0074] “You have been cruelly used,” said Holmes.

[P0075] The lady coloured deeply and covered over her injured wrist. “He is a hard man,” she said, “and perhaps he hardly knows his own strength.”

[P0076] There was a long silence, during which Holmes leaned his chin upon his hands and stared into the crackling fire.

[P0077] “This is a very deep business,” he said at last. “There are a thousand details which I should desire to know before I decide upon our course of action. Yet we have not a moment to lose. If we were to come to Stoke Moran to-day, would it be possible for us to see over these rooms without the knowledge of your stepfather?”

[P0078] “As it happens, he spoke of coming into town to-day upon some most important business. It is probable that he will be away all day, and that there would be nothing to disturb you. We have a housekeeper now, but she is old and foolish, and I could easily get her out of the way.”

[P0079] “Excellent. You are not averse to this trip, Watson?”

[P0080] “By no means.”

[P0081] “Then we shall both come. What are you going to do yourself?”

[P0082] “I have one or two things which I would wish to do now that I am in town. But I shall return by the twelve o’clock train, so as to be there in time for your coming.”

[P0083] “And you may expect us early in the afternoon. I have myself some small business matters to attend to. Will you not wait and breakfast?”

[P0084] “No, I must go. My heart is lightened already since I have confided my trouble to you. I shall look forward to seeing you again this afternoon.” She dropped her thick black veil over her face and glided from the room.

[P0085] “And what do you think of it all, Watson?” asked Sherlock Holmes, leaning back in his chair.

[P0086] “It seems to me to be a most dark and sinister business.”

[P0087] “Dark enough and sinister enough.”

[P0088] “Yet if the lady is correct in saying that the flooring and walls are sound, and that the door, window, and chimney are impassable, then her sister must have been undoubtedly alone when she met her mysterious end.”

[P0089] “What becomes, then, of these nocturnal whistles, and what of the very peculiar words of the dying woman?”

[P0090] “I cannot think.”

[P0091] “When you combine the ideas of whistles at night, the presence of a band of gipsies who are on intimate terms with this old doctor, the fact that we have every reason to believe that the doctor has an interest in preventing his stepdaughter’s marriage, the dying allusion to a band, and, finally, the fact that Miss Helen Stoner heard a metallic clang, which might have been caused by one of those metal bars that secured the shutters falling back into its place, I think that there is good ground to think that the mystery may be cleared along those lines.”

[P0092] “But what, then, did the gipsies do?”

[P0093] “I cannot imagine.”

[P0094] “I see many objections to any such theory.”

[P0095] “And so do I. It is precisely for that reason that we are going to Stoke Moran this day. I want to see whether the objections are fatal, or if they may be explained away. But what in the name of the devil!”

[P0096] The ejaculation had been drawn from my companion by the fact that our door had been suddenly dashed open, and that a huge man had framed himself in the aperture. His costume was a peculiar mixture of the professional and of the agricultural, having a black top-hat, a long frock-coat, and a pair of high gaiters, with a hunting-crop swinging in his hand. So tall was he that his hat actually brushed the cross bar of the doorway, and his breadth seemed to span it across from side to side. A large face, seared with a thousand wrinkles, burned yellow with the sun, and marked with every evil passion, was turned from one to the other of us, while his deep-set, bile-shot eyes, and his high, thin, fleshless nose, gave him somewhat the resemblance to a fierce old bird of prey.

[P0097] “Which of you is Holmes?” asked this apparition.

[P0098] “My name, sir; but you have the advantage of me,” said my companion quietly.

[P0099] “I am Dr. Grimesby Roylott, of Stoke Moran.”

[P0100] “Indeed, Doctor,” said Holmes blandly. “Pray take a seat.”

[P0101] “I will do nothing of the kind. My stepdaughter has been here. I have traced her. What has she been saying to you?”

[P0102] “It is a little cold for the time of the year,” said Holmes.

[P0103] “What has she been saying to you?” screamed the old man furiously.

[P0104] “But I have heard that the crocuses promise well,” continued my companion imperturbably.

[P0105] “Ha! You put me off, do you?” said our new visitor, taking a step forward and shaking his hunting-crop. “I know you, you scoundrel! I have heard of you before. You are Holmes, the meddler.”

[P0106] My friend smiled.

[P0107] “Holmes, the busybody!”

[P0108] His smile broadened.

[P0109] “Holmes, the Scotland Yard Jack-in-office!”

[P0110] Holmes chuckled heartily. “Your conversation is most entertaining,” said he. “When you go out close the door, for there is a decided draught.”

[P0111] “I will go when I have had my say. Don’t you dare to meddle with my affairs. I know that Miss Stoner has been here. I traced her! I am a dangerous man to fall foul of! See here.” He stepped swiftly forward, seized the poker, and bent it into a curve with his huge brown hands.

[P0112] “See that you keep yourself out of my grip,” he snarled, and hurling the twisted poker into the fireplace he strode out of the room.

[P0113] “He seems a very amiable person,” said Holmes, laughing. “I am not quite so bulky, but if he had remained I might have shown him that my grip was not much more feeble than his own.” As he spoke he picked up the steel poker and, with a sudden effort, straightened it out again.

[P0114] “Fancy his having the insolence to confound me with the official detective force! This incident gives zest to our investigation, however, and I only trust that our little friend will not suffer from her imprudence in allowing this brute to trace her. And now, Watson, we shall order breakfast, and afterwards I shall walk down to Doctors’ Commons, where I hope to get some data which may help us in this matter.”

[P0115] It was nearly one o’clock when Sherlock Holmes returned from his excursion. He held in his hand a sheet of blue paper, scrawled over with notes and figures.

[P0116] “I have seen the will of the deceased wife,” said he. “To determine its exact meaning I have been obliged to work out the present prices of the investments with which it is concerned. The total income, which at the time of the wife’s death was little short of £ 1,100, is now, through the fall in agricultural prices, not more than £ 750. Each daughter can claim an income of £ 250, in case of marriage. It is evident, therefore, that if both girls had married, this beauty would have had a mere pittance, while even one of them would cripple him to a very serious extent. My morning’s work has not been wasted, since it has proved that he has the very strongest motives for standing in the way of anything of the sort. And now, Watson, this is too serious for dawdling, especially as the old man is aware that we are interesting ourselves in his affairs; so if you are ready, we shall call a cab and drive to Waterloo. I should be very much obliged if you would slip your revolver into your pocket. An Eley’s No. 2 is an excellent argument with gentlemen who can twist steel pokers into knots. That and a tooth-brush are, I think, all that we need.”

[P0117] At Waterloo we were fortunate in catching a train for Leatherhead, where we hired a trap at the station inn and drove for four or five miles through the lovely Surrey lanes. It was a perfect day, with a bright sun and a few fleecy clouds in the heavens. The trees and wayside hedges were just throwing out their first green shoots, and the air was full of the pleasant smell of the moist earth. To me at least there was a strange contrast between the sweet promise of the spring and this sinister quest upon which we were engaged. My companion sat in the front of the trap, his arms folded, his hat pulled down over his eyes, and his chin sunk upon his breast, buried in the deepest thought. Suddenly, however, he started, tapped me on the shoulder, and pointed over the meadows.

[P0118] “Look there!” said he.

[P0119] A heavily timbered park stretched up in a gentle slope, thickening into a grove at the highest point. From amid the branches there jutted out the grey gables and high roof-tree of a very old mansion.

[P0120] “Stoke Moran?” said he.

[P0121] “Yes, sir, that be the house of Dr. Grimesby Roylott,” remarked the driver.

[P0122] “There is some building going on there,” said Holmes; “that is where we are going.”

[P0123] “There’s the village,” said the driver, pointing to a cluster of roofs some distance to the left; “but if you want to get to the house, you’ll find it shorter to get over this stile, and so by the footpath over the fields. There it is, where the lady is walking.”

[P0124] “And the lady, I fancy, is Miss Stoner,” observed Holmes, shading his eyes. “Yes, I think we had better do as you suggest.”

[P0125] We got off, paid our fare, and the trap rattled back on its way to Leatherhead.

[P0126] “I thought it as well,” said Holmes as we climbed the stile, “that this fellow should think we had come here as architects, or on some definite business. It may stop his gossip. Good-afternoon, Miss Stoner. You see that we have been as good as our word.”

[P0127] Our client of the morning had hurried forward to meet us with a face which spoke her joy. “I have been waiting so eagerly for you,” she cried, shaking hands with us warmly. “All has turned out splendidly. Dr. Roylott has gone to town, and it is unlikely that he will be back before evening.”

[P0128] “We have had the pleasure of making the Doctor’s acquaintance,” said Holmes, and in a few words he sketched out what had occurred. Miss Stoner turned white to the lips as she listened.

[P0129] “Good heavens!” she cried, “he has followed me, then.”

[P0130] “So it appears.”

[P0131] “He is so cunning that I never know when I am safe from him. What will he say when he returns?”

[P0132] “He must guard himself, for he may find that there is someone more cunning than himself upon his track. You must lock yourself up from him to-night. If he is violent, we shall take you away to your aunt’s at Harrow. Now, we must make the best use of our time, so kindly take us at once to the rooms which we are to examine.”

[P0133] The building was of grey, lichen-blotched stone, with a high central portion and two curving wings, like the claws of a crab, thrown out on each side. In one of these wings the windows were broken and blocked with wooden boards, while the roof was partly caved in, a picture of ruin. The central portion was in little better repair, but the right-hand block was comparatively modern, and the blinds in the windows, with the blue smoke curling up from the chimneys, showed that this was where the family resided. Some scaffolding had been erected against the end wall, and the stone-work had been broken into, but there were no signs of any workmen at the moment of our visit. Holmes walked slowly up and down the ill-trimmed lawn and examined with deep attention the outsides of the windows.

[P0134] “This, I take it, belongs to the room in which you used to sleep, the centre one to your sister’s, and the one next to the main building to Dr. Roylott’s chamber?”

[P0135] “Exactly so. But I am now sleeping in the middle one.”

[P0136] “Pending the alterations, as I understand. By the way, there does not seem to be any very pressing need for repairs at that end wall.”

[P0137] “There were none. I believe that it was an excuse to move me from my room.”

[P0138] “Ah! that is suggestive. Now, on the other side of this narrow wing runs the corridor from which these three rooms open. There are windows in it, of course?”

[P0139] “Yes, but very small ones. Too narrow for anyone to pass through.”

[P0140] “As you both locked your doors at night, your rooms were unapproachable from that side. Now, would you have the kindness to go into your room and bar your shutters?”

[P0141] Miss Stoner did so, and Holmes, after a careful examination through the open window, endeavoured in every way to force the shutter open, but without success. There was no slit through which a knife could be passed to raise the bar. Then with his lens he tested the hinges, but they were of solid iron, built firmly into the massive masonry. “Hum!” said he, scratching his chin in some perplexity, “my theory certainly presents some difficulties. No one could pass these shutters if they were bolted. Well, we shall see if the inside throws any light upon the matter.”

[P0142] A small side door led into the whitewashed corridor from which the three bedrooms opened. Holmes refused to examine the third chamber, so we passed at once to the second, that in which Miss Stoner was now sleeping, and in which her sister had met with her fate. It was a homely little room, with a low ceiling and a gaping fireplace, after the fashion of old country-houses. A brown chest of drawers stood in one corner, a narrow white-counterpaned bed in another, and a dressing-table on the left-hand side of the window. These articles, with two small wicker-work chairs, made up all the furniture in the room save for a square of Wilton carpet in the centre. The boards round and the panelling of the walls were of brown, worm-eaten oak, so old and discoloured that it may have dated from the original building of the house. Holmes drew one of the chairs into a corner and sat silent, while his eyes travelled round and round and up and down, taking in every detail of the apartment.

[P0143] “Where does that bell communicate with?” he asked at last pointing to a thick bell-rope which hung down beside the bed, the tassel actually lying upon the pillow.

[P0144] “It goes to the housekeeper’s room.”

[P0145] “It looks newer than the other things?”

[P0146] “Yes, it was only put there a couple of years ago.”

[P0147] “Your sister asked for it, I suppose?”

[P0148] “No, I never heard of her using it. We used always to get what we wanted for ourselves.”

[P0149] “Indeed, it seemed unnecessary to put so nice a bell-pull there. You will excuse me for a few minutes while I satisfy myself as to this floor.” He threw himself down upon his face with his lens in his hand and crawled swiftly backward and forward, examining minutely the cracks between the boards. Then he did the same with the wood-work with which the chamber was panelled. Finally he walked over to the bed and spent some time in staring at it and in running his eye up and down the wall. Finally he took the bell-rope in his hand and gave it a brisk tug.

[P0150] “Why, it’s a dummy,” said he.

[P0151] “Won’t it ring?”

[P0152] “No, it is not even attached to a wire. This is very interesting. You can see now that it is fastened to a hook just above where the little opening for the ventilator is.”

[P0153] “How very absurd! I never noticed that before.”

[P0154] “Very strange!” muttered Holmes, pulling at the rope. “There are one or two very singular points about this room. For example, what a fool a builder must be to open a ventilator into another room, when, with the same trouble, he might have communicated with the outside air!”

[P0155] “That is also quite modern,” said the lady.

[P0156] “Done about the same time as the bell-rope?” remarked Holmes.

[P0157] “Yes, there were several little changes carried out about that time.”

[P0158] “They seem to have been of a most interesting character—dummy bell-ropes, and ventilators which do not ventilate. With your permission, Miss Stoner, we shall now carry our researches into the inner apartment.”

[P0159] Dr. Grimesby Roylott’s chamber was larger than that of his step-daughter, but was as plainly furnished. A camp-bed, a small wooden shelf full of books, mostly of a technical character, an armchair beside the bed, a plain wooden chair against the wall, a round table, and a large iron safe were the principal things which met the eye. Holmes walked slowly round and examined each and all of them with the keenest interest.

[P0160] “What’s in here?” he asked, tapping the safe.

[P0161] “My stepfather’s business papers.”

[P0162] “Oh! you have seen inside, then?”

[P0163] “Only once, some years ago. I remember that it was full of papers.”

[P0164] “There isn’t a cat in it, for example?”

[P0165] “No. What a strange idea!”

[P0166] “Well, look at this!” He took up a small saucer of milk which stood on the top of it.

[P0167] “No; we don’t keep a cat. But there is a cheetah and a baboon.”

[P0168] “Ah, yes, of course! Well, a cheetah is just a big cat, and yet a saucer of milk does not go very far in satisfying its wants, I daresay. There is one point which I should wish to determine.” He squatted down in front of the wooden chair and examined the seat of it with the greatest attention.

[P0169] “Thank you. That is quite settled,” said he, rising and putting his lens in his pocket. “Hullo! Here is something interesting!”

[P0170] The object which had caught his eye was a small dog lash hung on one corner of the bed. The lash, however, was curled upon itself and tied so as to make a loop of whipcord.

[P0171] “What do you make of that, Watson?”

[P0172] “It’s a common enough lash. But I don’t know why it should be tied.”

[P0173] “That is not quite so common, is it? Ah, me! it’s a wicked world, and when a clever man turns his brains to crime it is the worst of all. I think that I have seen enough now, Miss Stoner, and with your permission we shall walk out upon the lawn.”

[P0174] I had never seen my friend’s face so grim or his brow so dark as it was when we turned from the scene of this investigation. We had walked several times up and down the lawn, neither Miss Stoner nor myself liking to break in upon his thoughts before he roused himself from his reverie.

[P0175] “It is very essential, Miss Stoner,” said he, “that you should absolutely follow my advice in every respect.”

[P0176] “I shall most certainly do so.”

[P0177] “The matter is too serious for any hesitation. Your life may depend upon your compliance.”

[P0178] “I assure you that I am in your hands.”

[P0179] “In the first place, both my friend and I must spend the night in your room.”

[P0180] Both Miss Stoner and I gazed at him in astonishment.

[P0181] “Yes, it must be so. Let me explain. I believe that that is the village inn over there?”

[P0182] “Yes, that is the Crown.”

[P0183] “Very good. Your windows would be visible from there?”

[P0184] “Certainly.”

[P0185] “You must confine yourself to your room, on pretence of a headache, when your stepfather comes back. Then when you hear him retire for the night, you must open the shutters of your window, undo the hasp, put your lamp there as a signal to us, and then withdraw quietly with everything which you are likely to want into the room which you used to occupy. I have no doubt that, in spite of the repairs, you could manage there for one night.”

[P0186] “Oh, yes, easily.”

[P0187] “The rest you will leave in our hands.”

[P0188] “But what will you do?”

[P0189] “We shall spend the night in your room, and we shall investigate the cause of this noise which has disturbed you.”

[P0190] “I believe, Mr. Holmes, that you have already made up your mind,” said Miss Stoner, laying her hand upon my companion’s sleeve.

[P0191] “Perhaps I have.”

[P0192] “Then, for pity’s sake, tell me what was the cause of my sister’s death.”

[P0193] “I should prefer to have clearer proofs before I speak.”

[P0194] “You can at least tell me whether my own thought is correct, and if she died from some sudden fright.”

[P0195] “No, I do not think so. I think that there was probably some more tangible cause. And now, Miss Stoner, we must leave you for if Dr. Roylott returned and saw us our journey would be in vain. Good-bye, and be brave, for if you will do what I have told you, you may rest assured that we shall soon drive away the dangers that threaten you.”

[P0196] Sherlock Holmes and I had no difficulty in engaging a bedroom and sitting-room at the Crown Inn. They were on the upper floor, and from our window we could command a view of the avenue gate, and of the inhabited wing of Stoke Moran Manor House. At dusk we saw Dr. Grimesby Roylott drive past, his huge form looming up beside the little figure of the lad who drove him. The boy had some slight difficulty in undoing the heavy iron gates, and we heard the hoarse roar of the Doctor’s voice and saw the fury with which he shook his clinched fists at him. The trap drove on, and a few minutes later we saw a sudden light spring up among the trees as the lamp was lit in one of the sitting-rooms.

[P0197] “Do you know, Watson,” said Holmes as we sat together in the gathering darkness, “I have really some scruples as to taking you to-night. There is a distinct element of danger.”

[P0198] “Can I be of assistance?”

[P0199] “Your presence might be invaluable.”

[P0200] “Then I shall certainly come.”

[P0201] “It is very kind of you.”

[P0202] “You speak of danger. You have evidently seen more in these rooms than was visible to me.”

[P0203] “No, but I fancy that I may have deduced a little more. I imagine that you saw all that I did.”

[P0204] “I saw nothing remarkable save the bell-rope, and what purpose that could answer I confess is more than I can imagine.”

[P0205] “You saw the ventilator, too?”

[P0206] “Yes, but I do not think that it is such a very unusual thing to have a small opening between two rooms. It was so small that a rat could hardly pass through.”

[P0207] “I knew that we should find a ventilator before ever we came to Stoke Moran.”

[P0208] “My dear Holmes!”

[P0209] “Oh, yes, I did. You remember in her statement she said that her sister could smell Dr. Roylott’s cigar. Now, of course that suggested at once that there must be a communication between the two rooms. It could only be a small one, or it would have been remarked upon at the coroner’s inquiry. I deduced a ventilator.”

[P0210] “But what harm can there be in that?”

[P0211] “Well, there is at least a curious coincidence of dates. A ventilator is made, a cord is hung, and a lady who sleeps in the bed dies. Does not that strike you?”

[P0212] “I cannot as yet see any connection.”

[P0213] “Did you observe anything very peculiar about that bed?”

[P0214] “No.”

[P0215] “It was clamped to the floor. Did you ever see a bed fastened like that before?”

[P0216] “I cannot say that I have.”

[P0217] “The lady could not move her bed. It must always be in the same relative position to the ventilator and to the rope—or so we may call it, since it was clearly never meant for a bell-pull.”

[P0218] “Holmes,” I cried, “I seem to see dimly what you are hinting at. We are only just in time to prevent some subtle and horrible crime.”

[P0219] “Subtle enough and horrible enough. When a doctor does go wrong he is the first of criminals. He has nerve and he has knowledge. Palmer and Pritchard were among the heads of their profession. This man strikes even deeper, but I think, Watson, that we shall be able to strike deeper still. But we shall have horrors enough before the night is over; for goodness’ sake let us have a quiet pipe and turn our minds for a few hours to something more cheerful.”

[P0220] About nine o’clock the light among the trees was extinguished, and all was dark in the direction of the Manor House. Two hours passed slowly away, and then, suddenly, just at the stroke of eleven, a single bright light shone out right in front of us.

[P0221] “That is our signal,” said Holmes, springing to his feet; “it comes from the middle window.”

[P0222] As we passed out he exchanged a few words with the landlord, explaining that we were going on a late visit to an acquaintance, and that it was possible that we might spend the night there. A moment later we were out on the dark road, a chill wind blowing in our faces, and one yellow light twinkling in front of us through the gloom to guide us on our sombre errand.

[P0223] There was little difficulty in entering the grounds, for unrepaired breaches gaped in the old park wall. Making our way among the trees, we reached the lawn, crossed it, and were about to enter through the window when out from a clump of laurel bushes there darted what seemed to be a hideous and distorted child, who threw itself upon the grass with writhing limbs and then ran swiftly across the lawn into the darkness.

[P0224] “My God!” I whispered; “did you see it?”

[P0225] Holmes was for the moment as startled as I. His hand closed like a vice upon my wrist in his agitation. Then he broke into a low laugh and put his lips to my ear.

[P0226] “It is a nice household,” he murmured. “That is the baboon.”

[P0227] I had forgotten the strange pets which the Doctor affected. There was a cheetah, too; perhaps we might find it upon our shoulders at any moment. I confess that I felt easier in my mind when, after following Holmes’ example and slipping off my shoes, I found myself inside the bedroom. My companion noiselessly closed the shutters, moved the lamp onto the table, and cast his eyes round the room. All was as we had seen it in the daytime. Then creeping up to me and making a trumpet of his hand, he whispered into my ear again so gently that it was all that I could do to distinguish the words:

[P0228] “The least sound would be fatal to our plans.”

[P0229] I nodded to show that I had heard.

[P0230] “We must sit without light. He would see it through the ventilator.”

[P0231] I nodded again.

[P0232] “Do not go asleep; your very life may depend upon it. Have your pistol ready in case we should need it. I will sit on the side of the bed, and you in that chair.”

[P0233] I took out my revolver and laid it on the corner of the table.

[P0234] Holmes had brought up a long thin cane, and this he placed upon the bed beside him. By it he laid the box of matches and the stump of a candle. Then he turned down the lamp, and we were left in darkness.

[P0235] How shall I ever forget that dreadful vigil? I could not hear a sound, not even the drawing of a breath, and yet I knew that my companion sat open-eyed, within a few feet of me, in the same state of nervous tension in which I was myself. The shutters cut off the least ray of light, and we waited in absolute darkness.

[P0236] From outside came the occasional cry of a night-bird, and once at our very window a long drawn catlike whine, which told us that the cheetah was indeed at liberty. Far away we could hear the deep tones of the parish clock, which boomed out every quarter of an hour. How long they seemed, those quarters! Twelve struck, and one and two and three, and still we sat waiting silently for whatever might befall.

[P0237] Suddenly there was the momentary gleam of a light up in the direction of the ventilator, which vanished immediately, but was succeeded by a strong smell of burning oil and heated metal. Someone in the next room had lit a dark-lantern. I heard a gentle sound of movement, and then all was silent once more, though the smell grew stronger. For half an hour I sat with straining ears. Then suddenly another sound became audible—a very gentle, soothing sound, like that of a small jet of steam escaping continually from a kettle. The instant that we heard it, Holmes sprang from the bed, struck a match, and lashed furiously with his cane at the bell-pull.

[P0238] “You see it, Watson?” he yelled. “You see it?”

[P0239] But I saw nothing. At the moment when Holmes struck the light I heard a low, clear whistle, but the sudden glare flashing into my weary eyes made it impossible for me to tell what it was at which my friend lashed so savagely. I could, however, see that his face was deadly pale and filled with horror and loathing. He had ceased to strike and was gazing up at the ventilator when suddenly there broke from the silence of the night the most horrible cry to which I have ever listened. It swelled up louder and louder, a hoarse yell of pain and fear and anger all mingled in the one dreadful shriek. They say that away down in the village, and even in the distant parsonage, that cry raised the sleepers from their beds. It struck cold to our hearts, and I stood gazing at Holmes, and he at me, until the last echoes of it had died away into the silence from which it rose.

[P0240] “What can it mean?” I gasped.

[P0241] “It means that it is all over,” Holmes answered. “And perhaps, after all, it is for the best. Take your pistol, and we will enter Dr. Roylott’s room.”

[P0242] With a grave face he lit the lamp and led the way down the corridor. Twice he struck at the chamber door without any reply from within. Then he turned the handle and entered, I at his heels, with the cocked pistol in my hand.

[P0243] It was a singular sight which met our eyes. On the table stood a dark-lantern with the shutter half open, throwing a brilliant beam of light upon the iron safe, the door of which was ajar. Beside this table, on the wooden chair, sat Dr. Grimesby Roylott clad in a long grey dressing-gown, his bare ankles protruding beneath, and his feet thrust into red heelless Turkish slippers. Across his lap lay the short stock with the long lash which we had noticed during the day. His chin was cocked upward and his eyes were fixed in a dreadful, rigid stare at the corner of the ceiling. Round his brow he had a peculiar yellow band, with brownish speckles, which seemed to be bound tightly round his head. As we entered he made neither sound nor motion.

[P0244] “The band! the speckled band!” whispered Holmes.

[P0245] I took a step forward. In an instant his strange headgear began to move, and there reared itself from among his hair the squat diamond-shaped head and puffed neck of a loathsome serpent.

[P0246] “It is a swamp adder!” cried Holmes; “the deadliest snake in India. He has died within ten seconds of being bitten. Violence does, in truth, recoil upon the violent, and the schemer falls into the pit which he digs for another. Let us thrust this creature back into its den, and we can then remove Miss Stoner to some place of shelter and let the county police know what has happened.”

[P0247] As he spoke he drew the dog-whip swiftly from the dead man’s lap, and throwing the noose round the reptile’s neck he drew it from its horrid perch and, carrying it at arm’s length, threw it into the iron safe, which he closed upon it.

[P0248] Such are the true facts of the death of Dr. Grimesby Roylott, of Stoke Moran. It is not necessary that I should prolong a narrative which has already run to too great a length by telling how we broke the sad news to the terrified girl, how we conveyed her by the morning train to the care of her good aunt at Harrow, of how the slow process of official inquiry came to the conclusion that the doctor met his fate while indiscreetly playing with a dangerous pet. The little which I had yet to learn of the case was told me by Sherlock Holmes as we travelled back next day.

[P0249] “I had,” said he, “come to an entirely erroneous conclusion which shows, my dear Watson, how dangerous it always is to reason from insufficient data. The presence of the gipsies, and the use of the word ‘band,’ which was used by the poor girl, no doubt, to explain the appearance which she had caught a hurried glimpse of by the light of her match, were sufficient to put me upon an entirely wrong scent. I can only claim the merit that I instantly reconsidered my position when, however, it became clear to me that whatever danger threatened an occupant of the room could not come either from the window or the door. My attention was speedily drawn, as I have already remarked to you, to this ventilator, and to the bell-rope which hung down to the bed. The discovery that this was a dummy, and that the bed was clamped to the floor, instantly gave rise to the suspicion that the rope was there as a bridge for something passing through the hole and coming to the bed. The idea of a snake instantly occurred to me, and when I coupled it with my knowledge that the doctor was furnished with a supply of creatures from India, I felt that I was probably on the right track. The idea of using a form of poison which could not possibly be discovered by any chemical test was just such a one as would occur to a clever and ruthless man who had had an Eastern training. The rapidity with which such a poison would take effect would also, from his point of view, be an advantage. It would be a sharp-eyed coroner, indeed, who could distinguish the two little dark punctures which would show where the poison fangs had done their work. Then I thought of the whistle. Of course he must recall the snake before the morning light revealed it to the victim. He had trained it, probably by the use of the milk which we saw, to return to him when summoned. He would put it through this ventilator at the hour that he thought best, with the certainty that it would crawl down the rope and land on the bed. It might or might not bite the occupant, perhaps she might escape every night for a week, but sooner or later she must fall a victim.

[P0250] “I had come to these conclusions before ever I had entered his room. An inspection of his chair showed me that he had been in the habit of standing on it, which of course would be necessary in order that he should reach the ventilator. The sight of the safe, the saucer of milk, and the loop of whipcord were enough to finally dispel any doubts which may have remained. The metallic clang heard by Miss Stoner was obviously caused by her stepfather hastily closing the door of his safe upon its terrible occupant. Having once made up my mind, you know the steps which I took in order to put the matter to the proof. I heard the creature hiss as I have no doubt that you did also, and I instantly lit the light and attacked it.”

[P0251] “With the result of driving it through the ventilator.”

[P0252] “And also with the result of causing it to turn upon its master at the other side. Some of the blows of my cane came home and roused its snakish temper, so that it flew upon the first person it saw. In this way I am no doubt indirectly responsible for Dr. Grimesby Roylott’s death, and I cannot say that it is likely to weigh very heavily upon my conscience.”

中文辅助译文段落时间线（可能为空；只能辅助理解，gold evidence 仍必须回到原文段落）：
[P0001] 八年来，我研究了我的朋友歇洛克·福尔摩斯的破案方法，记录了七十多个案例。我粗略地翻阅一下这些案例的记录，发现许多案例是悲剧性的，也有一些是喜剧性的，其中很大一部分仅仅是离奇古怪而已，但是却没有一例是平淡无奇的。这是因为，他做工作与其说是为了获得酬金，还不如说是出于对他那门技艺的爱好。除了显得独特或甚至于是近乎荒诞无稽的案情外，他对其它案情从来是不屑一顾，拒不参与任何侦查的。可是，在所有这些变化多端的案例中，我却回忆不起有哪一例会比萨里郡斯托克莫兰的闻名的罗伊洛特家族①那一例更具有异乎寻常的特色了。现在谈论的这件事，发生在我和福尔摩斯交往的早期。那时，我们都是单身汉，在贝克街合住一套寓所。本来我早就可以把这件事记录下来，但是，当时我曾作出严守秘密的保证，直至上月，由于我为之作出过保证的那位女士不幸过早地逝世，方始解除了这种约束。现在，大概是使真相大白于天下的时候了，因为我确实知道，外界对于格里姆斯比·罗伊洛特医生之死众说纷纭，广泛流传着各种谣言。这些谣言使得这桩事情变得比实际情况更加骇人听闻。

[P0002] ①英格兰东南部一郡。——译者注

[P0003] 事情发生在一八八三年四月初的时候。一天早上，我一觉醒来，发现歇洛克·福尔摩斯穿得整整齐齐，站在我的床边。一般来说，他是一个爱睡懒觉的人，而壁炉架上的时钟，才刚七点一刻，我有些诧异地朝他眨了眨眼睛，心里还有点不乐意，因为我自己的生活习惯是很有规律的。

[P0004] “对不起，把你叫醒了，华生，"他说，“但是，你我今天早上都命该如此，先是赫德森太太被敲门声吵醒，接着她报复似地来吵醒我，现在是我来把你叫醒。”

[P0005] “那么，什么事——失火了吗？”

[P0006] “不，是一位委托人。好象是一位年轻的女士来临，她情绪相当激动，坚持非要见我不可。现在她正在起居室里等候。你瞧，如果有些年轻的女士这么一清早就徘徊于这个大都市，甚至把还在梦乡的人从床上吵醒，我认为那必定是一件紧急的事情，她们不得不找人商量。假如这件事将是一件有趣的案子，那么，我肯定你一定希望从一开始就能有所了解。我认为无论如何应该把你叫醒，给予你这个机会。”

[P0007] “我的老兄，那我是无论如何也不肯失掉这个机会的。”

[P0008] 我最大的乐趣就是观察福尔摩斯进行专业性的调查工作，欣赏他迅速地做出推论，他推论之敏捷，犹如是单凭直觉而做出的，但却总是建立在逻辑的基础之上。他就是依靠这些解决了委托给他的疑难问题。我匆匆地穿上衣服，几分钟后就准备就绪，随同我的朋友来到楼下的起居室。一位女士端坐窗前，她身穿黑色衣服，蒙着厚厚的面纱。她在我们走进房间时站起身来。

[P0009] “早上好，小姐，"福尔摩斯愉快地说道，“我的名字是歇洛克·福尔摩斯。这位是我的挚友和伙伴华生医生。在他面前，你可以象在我面前一样地谈话，不必顾虑。哈！赫德森太太想得很周到，我很高兴看到她已经烧旺了壁炉。请凑近炉火坐坐，我叫人给你端一杯热咖啡，我看你在发抖。”

[P0010] “我不是因为觉得冷才发抖的，"那个女人低声地说，同时，她按照福尔摩斯的请求换了个座位。

[P0011] “那么，是为什么呢？”

[P0012] “福尔摩斯先生，是因为害怕和感到恐惧。"她一边说着，一边掀起了面纱，我们能够看出，她确实是处于万分焦虑之中，引人怜悯。她脸色苍白，神情沮丧，双眸惊惶不安，酷似一头被追逐的动物的眼睛。她的身材相貌象是三十岁模样，可是，她的头发却未老先衰夹杂着几缕银丝，表情萎靡憔悴。歇洛克·福尔摩斯迅速地从上到下打量了她一下。

[P0013] “你不必害怕，"他探身向前，轻轻地拍拍她的手臂，安慰她说，“我毫不怀疑，我们很快就会把事情处理好的，我知道，你是今天早上坐火车来的。”

[P0014] “那么说，你认识我？”

[P0015] “不，我注意到你左手的手套里有一张回程车票的后半截。你一定是很早就动身的，而且在到达车站之前，还乘坐过单马车在崎岖的泥泞道路上行驶了一段漫长的路程。"①

[P0016] ①原文为ｄｏｇｃａｒｔ－，是有背对背两个座位的双轮单马车。——译者注

[P0017] 那位女士猛地吃了一惊，惶惑地凝视着我的同伴。

[P0018] “这里面没什么奥妙，亲爱的小姐，"他笑了笑说。“你外套的左臂上，至少有七处溅上了泥。这些泥迹都是新沾上的。除了单马车以外，没有什么其它车辆会这样地甩起泥巴来，并且只有你坐在车夫左面才会溅到泥的。”

[P0019] “不管你是怎么判断出来的，你说得完全正确，"她说，“我六点钟前离家上路，六点二十到达莱瑟黑德，然后乘坐开往滑铁卢的第一班火车来的。先生，这么紧张我再也受不了啦，这样下去我会发疯的。我是求助无门——一个能帮忙的人也没有，除了只有那么一个人关心我，可是他这可怜的人儿，也是爱莫能助。我听人说起过你，福尔摩斯先生，我是从法林托歇太太那儿听说的，你曾经在她极需帮助的时候援助过她。我正是从她那儿打听到你的地址的。噢，先生，你不也可以帮帮我的忙吗？至少可以对陷于黑暗深渊的我指出一线光明的吧。目前我无力酬劳你对我的帮助，但在一个月或一个半月以内，我即将结婚，那时就能支配我自己的收入，你至少可以发现，我不是一个忘恩负义的人。”

[P0020] 福尔摩斯转身走向他的办公桌，打开抽屉的锁，从中取出一本小小的案例簿，翻阅了一下。

[P0021] “法林托歇，"他说，“啊，是的，我想起了那个案子，是一件和猫儿眼宝石女冠冕有关的案子。华生，我想起那还是你来以前的事呢。小姐，我只能说我很乐于为你这个案子效劳，就象我曾经为你的朋友那桩案子效劳一样。至于酬劳，我的职业本身就是它的酬劳；但是，你可以在你感到最合适的时候，随意支付我在这件事上可能付出的费用。那么，现在请你把可能有助于对这件事作出判断的一切告诉我们吧。”

[P0022] “唉，"我们的来客回答说，“我处境的可怕之处在于我所担心害怕的东西十分模糊，我的疑虑完全是由一些琐碎的小事引起的。这些小事在别人看起来可能是微不足道的，在所有的人当中，甚至我最有权利取得其帮助和指点的人，也把我告诉他的关于这件事的一切看做是一个神经质的女人的胡思乱想。他倒没有这么说，但是，我能从他安慰我的答话和回避的眼神中觉察出来。我听说，福尔摩斯先生，你能看透人们心中种种邪恶。请你告诉我，在危机四伏的情况下，我该如何办。”

[P0023] “我十分留意地听你讲，小姐。”

[P0024] “我的名字叫海伦·斯托纳，我和我的继父住在一起，他是位于萨里郡西部边界的斯托克莫兰的罗伊洛特家族——英国最古老的撒克逊家族之一——的最后的一个生存者。”

[P0025] 福尔摩斯点点头，“这个名字我很熟悉，"他说。

[P0026] “这个家族一度是英伦最富有的家族之一，它的产业占地极广，超出了本郡的边界，北至伯克郡，西至汉普郡。可是到了上个世纪，连续四代子嗣都属生性荒淫浪荡、挥霍无度之辈，到了摄政时期终于被一个赌棍最后搞得倾家荡产。除了几①亩土地和一座二百年的古老邱宅外，其它都已荡然无存，而那座邸宅也已典押得差不多了。最后的一位地主在那里苟延残喘地过着落破王孙的可悲生活。但是他的独生子，我的继父，认识到他必须使自己适应这种新的情况，从一位亲戚那里借到一笔钱，这笔钱使他得到了一个医学学位，并且出国到了加尔各答行医，在那儿凭借他的医术和坚强的个性，业务非常发达。可是，由于家里几次被盗，他在盛怒之下，殴打当地人管家致死，差一点因为这个被判处死刑。就这样，他遭到长期监禁。后来，返回英国，变成一个性格暴躁、失意潦倒的人。

[P0027] ①英王乔治四世皇太子的摄政时期即自１８１１年至１８２０年期间。——译者注

[P0028] “罗伊洛特医生在印度时娶了我的母亲。她当时是孟加拉炮兵司令斯托纳少将的年轻遗孀，斯托纳太太。我和我的姐姐朱莉娅是孪生姐妹，我母亲再婚的时候，我们年仅两岁。她有一笔相当可观的财产，每年的进项不少于一千英镑。我们和罗伊洛特医生住在一平时，她就立下遗嘱把财产全部遗赠给他，但附有一个条件，那就是在我们结婚后，每年要拨给我们一定数目的金钱。我们返回英伦不久，我们的母亲就去世了。她是八年前在克鲁附近一次火车事故中丧生的。在这之后，罗伊洛特医生放弃了重新在伦敦开业的意图，带我们一起到斯托克莫兰祖先留下的古老邸宅里过活。我母亲遗留的钱足够应付我们的一切需要，看来我们的幸福似乎是毫无问题的了。

[P0029] “但是，大约在这段时间里，我们的继父发生了可怕的变化。起初，邻居们看到斯托克莫兰的罗伊洛特的后裔回到这古老家族的邸宅，都十分高兴。可是他一反与邻居们交朋友或互相往来的常态，把自己关在房子里，深居简出，不管碰到什么人，都一味穷凶极恶地与之争吵。这种近乎癫狂的暴戾脾气，在这个家族中，是有遗传性的。我相信我的继父是由于长期旅居于热带地方，致使这种脾气变本加厉。一系列使人丢脸的争吵发生了。其中两次，一直吵到违警罪法庭才算罢休。结果，他成了村里人人望而生畏的人。人们一看到他，无不敬而远之，赶紧躲开，因为他是一个力大无穷的人，当他发怒的时候，简直是什么人也控制不了他。

[P0030] “上星期他把村里的铁匠从栏杆上扔进了小河，只是在我花掉了尽我所能收罗到的钱以后，才避免了又一次当众出丑。除了那些到处流浪的吉卜赛人以外，他没有任何朋友。他允许那些流浪者在那一块象征着家族地位的几亩荆棘丛生的土地上扎营。他会到他们帐篷里去接受他们作为报答的殷勤款待。有时候随同他们出去流浪长达数周之久。他还对印度的动物有着强烈的爱好。这些动物是一个记者送给他的。目前，他有一只印度猎豹和一只狒狒，这两只动物就在他的土地上自由自在地跑来跑去，村里人就象害怕它们的主人一样害怕它们。

[P0031] “通过我说的这些情况，你们不难想象我和可怜的姐姐朱莉娅是没有什么生活乐趣的。没有外人会愿意跟我们长期相处，在很长一个时期里，我们操持所有的家务。我姐姐死的时候，才仅仅三十岁。可是她早已两鬓斑白了，甚至和我现在的头发一样白。”

[P0032] “那么，你姐姐已经死了？”

[P0033] “她刚好是两年前死的，我想对你说的正是有关她去世的事。你可以理解，过着我刚才所叙述的那种生活，我们几乎见不到任何和我年龄相仿和地位相同的人。不过，我们有一个姨妈，叫霍洛拉·韦斯法尔小姐，她是我母亲的老处女姐妹，住在哈罗附近，我们偶尔得到允许，到她家去短期作客。两年前，朱莉娅在圣诞节到她家去，在那里认识了一位领半薪的海军陆战队少校，并和他缔结了婚约。我姐姐归来后，我继父闻知这一婚约，并未对此表示反对。但是，在预定举行婚礼之前不到两周的时候，可怕的事情发生了，从而夺去了我唯一的伴侣。”

[P0034] 福尔摩斯一直仰靠在椅背上，闭着眼睛，头靠在椅背靠垫上。但是，这时他半睁开眼，看了一看他的客人。

[P0035] “请把细节说准确些。"他说。

[P0036] “这对我来说很容易，因为在那可怕的时刻发生的每一件事，都已经深深印在我的记忆里。我已经说过，庄园的邸宅是极其古老的，只有一侧的耳房现在住着人。这一侧的耳房的卧室在一楼，起居室位于房子的中间部位。这些卧室中第一间是罗伊洛特医生的，第二间是我姐姐的，第三间是我自己的。这些房间彼此互不相通，但是房门都是朝向一条共同的过道开的。我讲清楚了没有？”

[P0037] “非常清楚。”

[P0038] “三个房间的窗子都是朝向草坪开的。发生不幸的那个晚上，罗伊洛特医生早早就回到了自己的房间，可是我们知道他并没有就寝，因为我姐姐被他那强烈的印度雪茄烟味熏得苦不胜言，他抽这种雪茄已经上了瘾。因此，她离开自己的房间，来到我的房间里逗留了一些时间，和我谈起她即将举行的婚礼。到了十一点钟，她起身回自己的房间，但是走到门口时停了下来，回过头来。

[P0039] “'告诉我，海伦，'她说，‘在夜深人静的时候，你听到过有人吹口哨没有？'

[P0040] “'从来没有听到过，'我说。

[P0041] “'我想你睡着的时候，不可能吹口哨吧？'

[P0042] “'当然不会，你为什么要问这个呢？'

[P0043] “'因为这几天的深夜，大约清晨三点钟左右，我总是听到轻轻的清晰的口哨声。我是一个睡不沉的人，所以就被吵醒了。我说不出那声音是从哪儿来的，可能来自隔壁房间，也可能来自草坪。我当时就想，我得问问你是否也听到了。'

[P0044] “'没有，我没听到过。一定是种植园里那些讨厌的吉卜赛人。'

[P0045] “'极其可能。可是如果是从草坪那儿来的，我感到奇怪你怎么会没有同样地听到。'

[P0046] “'啊，但是，我一般睡得比你沉。'

[P0047] “'好啦，不管怎么说，这关系都不大。'她扭过头对我笑笑，接着把我的房门关上。不一会儿，我就听到她的钥匙在门锁里转动的声音。”

[P0048] “什么？"福尔摩斯说，“这是不是你们的习惯，夜里总是把自己锁在屋子里？”

[P0049] “总是这样。”

[P0050] “为什么呢？”

[P0051] “我想我和你提到过，医生养了一只印度猎豹和一只狒狒。不把门锁上，我们感到不大安全。”

[P0052] “是这么回事。请你接着说下去。”

[P0053] “那天晚上，我睡不着。一种大祸临头的模糊感觉压在我心头。你会记得我们姐儿俩是孪生姐妹，你知道，联接这样两个血肉相连的心的纽带是有多么微妙。那天晚上是个暴风雨之夜，外面狂风怒吼，雨点劈劈啪啪地打在窗户上。突然，在风雨嘈杂声中，传来一声女人惊恐的狂叫，我听出那是我姐姐的声音。我一下子从床上跳了起来，裹上了一块披巾，就冲向了过道。就在我开启房门时，我仿佛听到一声轻轻的就象我姐姐说的那样的口哨声，稍停，又听到哐啷一声，仿佛是一块金属的东西倒在地上。就在我顺着过道跑过去的时候，只看见我姐姐的门锁已开，房门正在慢慢地移动着。我吓呆了，瞪着双眼看着，不知道会有什么东西从门里出来。借着过道的灯光，我看见我姐姐出现在房门口，她的脸由于恐惧而雪白如纸，双手摸索着寻求援救，整个身体就象醉汉一样摇摇晃晃。我跑上前去，双手拥抱住她。这时只见她似乎双膝无力。颓然跌倒在地。她象一个正在经受剧痛的人那样翻滚扭动，她的四肢可怕地抽搐。起初我以为她没有认出是我，可是当我俯身要抱她时，她突然发出凄厉的叫喊，那叫声我是一辈子也忘不了的。她叫喊的是，‘唉，海伦！天啊！是那条带子！那条带斑点的带子！'她似乎言犹未尽，还很想说些别的什么，她把手举在空中，指向医生的房间，但是抽搐再次发作，她说不出话来了。我疾步奔跑出去，大声喊我的继父，正碰上他穿着睡衣，急急忙忙地从他的房间赶过来。他赶到我姐姐身边时，我姐姐已经不省人事了。尽管他给她灌下了白兰地，并从村里请来了医生，但一切努力都是徒劳无功的，因为她已奄奄一息，濒临死亡，直至咽气之前，再也没有重新苏醒。这就是我那亲爱的姐姐的悲惨结局。”

[P0054] “等一等，"福尔摩斯说，“你敢十分肯定听到那口哨声和金属碰撞声了吗？你能保证吗？”

[P0055] “本郡验尸官在调查时也正是这样问过我的。我是听到的，它给我的印象非常深。可是在猛烈的风暴声和老房子嘎嘎吱吱的一片响声中，我也有可能听错。”

[P0056] “你姐姐还穿着白天的衣服吗？”

[P0057] “没有，她穿着睡衣。在她的右手中发现了一根烧焦了的火柴棍，左手里有个火柴盒。”

[P0058] “这说明在出事的时候，她划过火柴，并向周围看过，这一点很重要。验尸官得出了什么结论？”

[P0059] “他非常认真地调查了这个案子，因为罗伊洛特医生的品行在郡里早已臭名昭著，但是他找不出任何能说服人的致死原因。我证明，房门总是由室内的门锁锁住的，窗子也是由带有宽铁杠的老式百叶窗护挡着，每天晚上都关得严严的。墙壁仔细地敲过，发现四面都很坚固，地板也经过了彻底检查，结果也是一样。烟囱倒是很宽阔，但也是用了四个大锁环闩上的。因此，可以肯定我姐姐在遭到不幸的时候，只有她一个人在房间里。再说，她身上没有任何暴力的痕迹。”

[P0060] “会不会是毒药？”

[P0061] “医生们为此做了检查，但查不出来。”

[P0062] “那么，你认为这位不幸的女士的死因是什么呢？”

[P0063] “尽管我想象不出是什么东西吓坏了她，可是我相信她致死的原因纯粹是由于恐惧和精神上的震惊。”

[P0064] “当时种植园里有吉卜赛人吗？”

[P0065] “有的，那儿几乎总是有些吉卜赛人。”

[P0066] “啊，从她提到的带子——带斑点的带子，你推想出什么来没有？”

[P0067] “有时我觉得，那只不过是精神错乱时说的胡话，有时又觉得，可能指的是某一帮人。也许指的就是种植园里那些吉①卜赛人。他们当中有那么多人头上戴着带点子的头巾，我不知道这是否可以说明她所使用的那个奇怪的形容词。”

[P0068] ①原文ｂａｎｄ作"带子"解，亦作"一帮"解。——译者注

[P0069] 福尔摩斯摇摇头，好象这样的想法远远不能使他感到满意。

[P0070] “这里面还大有文章。"他说，“请继续讲下去。”

[P0071] “从那以后，两年过去了，一直到最近，我的生活比以往更加孤单寂寞。然而，一个月前，很荣幸有一位认识多年的亲密朋友向我求婚。他的名字叫阿米塔奇——珀西·阿米塔奇，是住在里丁附近克兰活特的阿米塔奇先生的二儿子。我继父对这件婚事没有表示异议，我们商定在春天的时候结婚。两天前，这所房子西边的耳房开始进行修缮，我卧室的墙壁被钻了些洞，所以我不得不搬到我姐姐丧命的那房间里去住，睡在她睡过的那张床上。昨天晚上，我睁着眼睛躺在床上，回想起她那可怕的遭遇，在这寂静的深夜，我突然听到曾经预兆她死亡的轻轻的口哨声，请想想看，我当时被吓成什么样子！我跳了起来，把灯点着，但是在房间里什么也没看到。可是我实在是吓得魂不附体，再也不敢重新上床。我穿上了衣服，天一亮，我悄悄地出来，在邸宅对面的克朗旅店雇了一辆单马车，坐车到莱瑟黑德，又从那里来到你这儿，唯一的目的是来拜访你并向你请教。”

[P0072] “你这样做很聪明，"我的朋友说，“但是你是否一切全说了？”

[P0073] “是的，一切。”

[P0074] “罗伊洛特小姐，你并没有全说。你在袒护你的继父。”

[P0075] “哎呀！你这是什么意思？”

[P0076] 为了回答她的话，福尔摩斯拉起了遮住我们客人放在膝头上那只手的黑色花边袖口的褶边。白皙的手腕上，印有五小块乌青的伤痕，那是四个手指和一个拇指的指痕。

[P0077] “你受过虐待。"福尔摩斯说。

[P0078] 这位女士满脸绯红，遮住受伤的手腕说，“他是一个身体强健的人，他也许不知道自己的力气有多大。”

[P0079] 大家沉默了好长时间，在这段时间里福尔摩斯将手托着下巴，凝视着劈啪作响的炉火。

[P0080] 最后他说：“这是一件十分复杂的案子。在决定要采取什么步骤以前，我希望了解的细节真是多得不可胜数。不过，我们已经是刻不容缓的了。假如我们今天到斯托克莫兰去，我们是否可能在你继父不知道的情况下，查看一下这些房间呢？”

[P0081] “很凑巧，他谈起过今天要进城来办理一些十分重要的事情。他很可能一整天都不在家，这就不会对你有任何妨碍了。眼下我们有一位女管家，但是她已年迈而且愚笨，我很容易把她支开。”

[P0082] “好极了，华生，你不反对走一趟吧？”

[P0083] “决不反对。”

[P0084] “那么，我们两个人都要去的。你自己有什么要办的事吗？”

[P0085] “既然到了城里，有一两件事我想去办一下。但是，我将乘坐十二点钟的火车赶回去，好及时在那儿等候你们。”

[P0086] “你可以在午后不久等候我们。我自己有些业务上的小事要料理一下。你不呆一会儿吃一点早点吗？”

[P0087] “不，我得走啦。我把我的烦恼事向你们吐露以后，我的心情轻松多了。我盼望下午能再见到你们。"她把那厚厚的黑色面纱拉下来蒙在脸上，悄悄地走出了房间。

[P0088] “华生，你对这一切有何感想？"歇洛克·福尔摩斯向后一仰，靠在椅背上问道。

[P0089] “在我看来，是一个十分阴险毒辣的阴谋。”

[P0090] “是够阴险毒辣的。”

[P0091] “可是，如果这位女士所说的地板和墙壁没受到什么破坏，由门窗和烟囱是钻不进去的这些情况没有错的话，那么，她姐姐莫名奇妙地死去时，无疑是一个人在屋里的。”

[P0092] “可是，那夜半哨声是怎么回事？那女人临死时非常奇怪的话又如何解释呢？”

[P0093] “我想不出来。”

[P0094] “夜半哨声；同这位老医生关系十分密切的一帮吉卜赛人的出现；我们有充分理由相信医生气图阻止他继女结婚的这个事实；那句临死时提到的有关带子的话；最后还有海伦·斯托纳小姐听到的哐啷一下的金属碰撞声（那声音可能是由一根扣紧百叶窗的金属杠落回到原处引起的）；当你把所有这些情况联系起来的时候，我想有充分根据认为：沿着这些线索就可以解开这个谜了。”

[P0095] “然而那些吉卜赛人都干了些什么呢？”

[P0096] “我想象不出。”

[P0097] “我觉得任何这一类的推理都有许多缺陷。”

[P0098] “我觉得是这样。恰恰就是由于这个原因，我们今天才要到斯托克莫兰去。我想看看这些缺陷是无法弥补的呢，还是可以解释得通的。可是，真见鬼，这到底是怎么回事呢？”

[P0099] 我伙伴这声突如其来的喊叫是因为我们的门突然被人撞开了。一个彪形大汉堵在房门口。他的装束很古怪，既象一个专家，又象一个庄稼汉。他头戴黑色大礼帽，身穿一件长礼服，脚上却穿着一双有绑腿的高统靴，手里还挥动着一根猎鞭。他长得如此高大，他的帽子实际上都擦到房门上的横楣了。他块头之大，几乎把门的两边堵得严严实实。他那张布满皱纹、被太阳炙晒得发黄、充满邪恶神情的宽脸，一会儿朝我瞧瞧，一会儿朝福尔摩斯瞧瞧。他那一双凶光毕露的深陷的眼睛和那细长的高鹰钩的鼻子，使他看起来活象一头老朽、残忍的猛禽。

[P0100] “你们俩谁是福尔摩斯？"这个怪物问道。

[P0101] “先生，我就是，可是失敬得很，你是哪一位？"我的伙伴平静地说。

[P0102] “我是斯托克莫兰的格里姆斯比·罗伊洛特医生。”

[P0103] “哦，医生，"福尔摩斯和蔼地说，“请坐。”

[P0104] “不用来这一套，我知道我的继女到你这里来过，因为我在跟踪她。她对你都说了些什么？”

[P0105] “今年这个时候天气还这么冷，"福尔摩斯说。

[P0106] “她都对你说了些什么？"老头暴跳如雷地叫喊起来。

[P0107] “但是我听说番红花将开得很不错，"我的伙伴谈笑自如地接着说。

[P0108] “哈！你想搪塞我，是不是？"我们这位新客人向前跨上一步，挥动着手中的猎鞭说，“我认识你，你这个无赖！我早就听说过你。你是福尔摩斯，一个爱管闲事的人。”

[P0109] 我的朋友微微一笑。

[P0110] “福尔摩斯，好管闲事的家伙！”

[P0111] 他更加笑容可掬。

[P0112] “福尔摩斯，你这个苏格兰场的自命不凡的芝麻官！”

[P0113] 福尔摩斯格格地笑了起来。"你的话真够风趣的，"他说。

[P0114] “你出去的时候把门关上，因为明明有一股穿堂风。”

[P0115] “我把话说完就走。你竟敢来干预我的事。我知道斯托纳小姐来过这里，我跟踪了她。我可是一个不好惹的危险人物！你瞧这个。"他迅速地向前走了几步，抓起火钳，用他那双褐色的大手把它拗弯。

[P0116] “小心点别让我抓住你，"他咆哮着说，顺手把扭弯的火钳扔到壁炉里，大踏步地走出了房间。

[P0117] “他真象一个非常和蔼可亲的人，"福尔摩斯哈哈大笑说：

[P0118] “我的块头没有他那么大，但是假如他在这儿多呆一会儿，我会让他看看，我的手劲比他的小不了多少。"说着，他拾起那条钢火钳，猛一使劲，就把它重新弄直了。

[P0119] “真好笑，他竟那么蛮横地把我和官厅侦探人员混为一谈！然而，这么一段插曲却为我们的调查增添了风趣，我唯一希望的是我们的小朋友不会由于粗心大意让这个畜生跟踪上了而遭受什么折磨。好了，华生，我们叫他们开早饭吧，饭后我要步行到医师协会去，我希望在那儿能搞到一些有助于我们处理这件案子的材料。”

[P0120] 歇洛克·福尔摩斯回来时已快要一点了。他手中拿着一张蓝纸，上面潦草地写着一些笔记和数字。

[P0121] “我看到了那位已故的妻子的遗嘱，"他说，“为了确定它确切的意义，我不得不计算出遗嘱中所列的那些投资有多大进项。其全部收入在那位女人去世的时候略少于一千一百英镑，现在，由于农产评价格下跌，至多不超过七百五十英镑。可是每个女儿一结婚就有权索取二百五十英镑的收入。因此，很明显，假如两个小姐都结了婚，这位'妙人儿'就会只剩下菲薄的收入，甚至即使一个结了婚也会弄得他很狼狈。我早上的工作没有白费，因为它证明了他有着最强烈的动机以防止这一类事情发生。华生，现在再不抓紧就太危险了，特别是那老头已经知道我们对他的事很感兴趣；所以，如果你准备好了，我们就去雇一辆马车，前往滑铁卢车站。假如你悄悄地把你的左轮手枪揣在口袋里，我将非常感激。对于能把钢火钳扭成结的先生，一把埃利二号是最能解决争端的工具了。我想这个东西连同一把牙刷就是我们的全部需要。”

[P0122] 在滑铁卢，我们正好赶上一班开往莱瑟黑德的火车。到站后，我们从车站旅店雇了一辆双轮轻便马车，沿着可爱的萨里单行车道行驶了五六英里。那天天气极好，阳光明媚，晴空中白云轻飘。树木和路边的树篱刚刚露出第一批嫩枝，空气中散发着令人心旷神怡的湿润的泥土气息。对于我来说，至少觉得这春意盎然的景色和我们从事的这件不祥的调查是一个奇特的对照。我的伙伴双臂交叉地坐在马车的前部，帽子耷拉下来遮住了眼睛，头垂到胸前，深深地陷入沉思之中。可是蓦地他抬起头来，拍了拍我的肩膀，指着对面的草地。

[P0123] “你瞧，那边，"他说。

[P0124] 一片树木茂密的园地，随着不很陡的斜坡向上延伸，在最高处形成了密密的一片丛林。树丛之中矗立着一座十分古老的邸宅的灰色山墙和高高的屋顶。

[P0125] “斯托克莫兰？"他说。

[P0126] “是的，先生，那是格里姆斯比·罗伊洛特医生的房子，”马车夫说。

[P0127] “那边正在大兴土木，"福尔摩斯说，“那就是我们要去的地方。”

[P0128] “村子在那儿，"马车夫遥指左面的一簇屋顶说，“但是，如果你们想到那幢房子那里去，你们这样走会更近一些：跨过篱笆两边的台阶，然后顺着地里的小路走。就在那儿，那位小姐正在走着的那条小路。”

[P0129] “我想，那位小姐就是斯托纳小姐，"福尔摩斯手遮着眼睛，仔细地瞧着说。“是的，我看我们最好还是照你的意思办。”

[P0130] 我们下了车，付了车钱，马车嘎啦嘎啦地朝莱瑟黑德行驶回去。

[P0131] 当我们走上台阶时，福尔摩斯说：“我认为还是让这个家伙把我们当成是这里的建筑师，或者是来办事的人为好，省得他闲话连篇。午安，斯托纳小姐。你瞧，我们是说到做到的。”

[P0132] 我们这位早上来过的委托人急急忙忙地赶上前来迎接我们，脸上流露出高兴的神色。"我一直在焦急地盼着你们，"她热情地和我们边握手边大声说道，“一切都很顺利。罗伊洛特医生进城了，看来他傍晚以前是不会回来了。”

[P0133] “我们已经高兴地认识了医生。"福尔摩斯说。接着他把经过大概地叙述了一番。听着听着，斯托纳小姐的整个脸和嘴唇都变得刷白。

[P0134] “天哪！"她叫道，“那么，他一直在跟着我了。”

[P0135] “看来是这样。”

[P0136] “他太狡猾了，我无时无刻不感到受着他的控制。他回来后会说什么呢？”

[P0137] “他必须保护他自己，因为他可能发现，有比他更狡猾的人跟踪他。今天晚上，你一定要把门锁上不放他进去。如果他很狂暴，我们就送你去哈罗你姨妈家里。现在，我们得抓紧时间，所以，请马上带我们到需要检查的那些房间去。”

[P0138] 这座邸宅是用灰色的石头砌的，石壁上布满了青苔，中央部分高高矗立，两侧是弧形的边房，象一对蟹钳似地向两边延伸。一侧的边房窗子都已经破碎，用木板堵着，房顶也有一部分坍陷了，完全是一副荒废残破的景象。房子的中央部分也是年久失修。可是，右首那一排房子却比较新，窗子里窗帘低垂，烟囱上蓝烟袅袅，说明这里是这家人居住的地方。靠山墙竖着一些脚手架，墙的石头部分已经凿通，但是我们到达那里时却没见到有工人的迹象。福尔摩斯在那块草草修剪过的草坪上缓慢地走来走去，十分仔细地检查了窗子的外部。

[P0139] “我想，这是你过去的寝室，当中那间是你姐姐的房间，挨着主楼的那间是罗伊洛特医生的卧室。”

[P0140] “一点也不错。但是现在我在当中那间睡觉。”

[P0141] “我想这是因为房屋正在修缮中。顺便说说，那座山墙似乎并没有任何加以修缮的迫切需要吧。”

[P0142] “根本不需要，我相信那只不过是要我从我的房间里搬出来的一个借口。”

[P0143] “啊，这很说明问题。嗯，这狭窄边房的另一边是那一条三个房间的房门都朝向它开的过道。里面当然也有窗子的吧？”

[P0144] “有的，不过是一些非常窄小的窗子。太窄了，人钻不进去。”

[P0145] “既然你俩晚上都锁上自己的房门，从那一边进入你们的房间是不可能的了。现在，麻烦你到你的房间里去，并且闩上百叶窗。”

[P0146] 斯托纳小姐照他吩咐的做了。福尔摩斯十分仔细地检查开着的窗子，然后用尽各种方法想打开百叶窗，但就是打不开。连一条能容一把刀子插进去把闩杠撬起来的裂缝也没有。随后，他用凸透镜检查了合叶，可是合叶是铁制的，牢牢地嵌在坚硬的石墙上。“嗯，"他有点困惑不解地搔着下巴说，“我的推理肯定有些说不通的地方。如果这些百叶窗闩上了，是没有人能够钻进去的。好吧，我们来看看里边是否有什么线索能帮助我们弄明白事情的真相。”

[P0147] 一道小小的侧门通向刷得雪白的过道，三间卧室的房门都朝向这个过道。福尔摩斯不想检查第三个房间，所以我们马上就来到第二间，也就是斯托纳小姐现在用作寝室、她的姐姐不幸去世的那个房间。这是一间简朴的小房间，按照乡村旧式邸宅的样式盖的，有低低的天花板和一个开口式的壁炉。房间的一隅立着一只带抽屉的褐色橱柜，另一隅安置着一张窄窄的罩着白色床罩的床，窗子的左侧是一只梳妆台。这些家具加上两把柳条椅子就是这个房间的全部摆设了，只是正当中还有一块四方形的威尔顿地毯而已，房间四周的木板和墙上的嵌板是蛀孔斑斑的棕色栎木，十分陈旧，并且褪了色。很可能当年建筑这座房子时就已经有这些木板和嵌板了。福尔摩斯搬了一把椅子到墙角，默默地坐在那里，他的眼睛却前前后后，上上下下不停地巡视，他观察细致入微，对房间的每个细节都注意到了。

[P0148] 最后，他指着悬挂在床边的一根粗粗的铃拉绳问道，“这个铃通什么地方？"那绳头的流苏实际上就搭在枕头上。

[P0149] “通到管家的房间里。”

[P0150] “看样子它比其他东西都要新些。”

[P0151] “是的，才装上一两年。”

[P0152] “我想是你姐姐要求装上的吧？”

[P0153] “不是，我从来没有听说她用过它。我们想要什么东西总是自己去取的。”

[P0154] “是啊，看来没有必要在那儿安装这么好的一根铃绳。对不起，让我花几分钟搞清楚这地板。"他趴了下去，手里拿着他的放大镜，迅速地前后匍匐移动，十分仔细地检查木板间的裂缝。接着他对房间里的嵌板做了同样的检查。最后，他走到床前，目不转睛地打量了它好一会，又顺着墙上下来回瞅着。末了他把铃绳握在手中，突然使劲拉了一下。

[P0155] “咦！这只是做样子的，"他说。

[P0156] “不响吗？”

[P0157] “不响，上面甚至没有接上线。这很有意思，现在你能看清，绳子刚好是系在小小的通气孔上面的钩子上。”

[P0158] “多么荒唐的做法啊！我以前从来没有注意到这个。”

[P0159] “非常奇怪！"福尔摩斯手拉着铃绳喃喃地说，“这房间里有一两个十分特别的地方。例如，造房子的人有多么愚蠢，竟会把通气孔朝向隔壁房间，花费同样的工夫，他本来可以把它通向户外的。”

[P0160] “那也是新近的事，"这位小姐说。

[P0161] “是和铃绳同时安装的吗？"福尔摩斯问。

[P0162] “是的，有好几处小改动是那时候进行的。”

[P0163] “这些东西实在太有趣了——摆样子的铃绳，不通风的通气孔。你要是允许的话，斯托纳小姐，我们到里面那一间去检查检查看。”

[P0164] 格里姆斯比·罗伊洛特医生的房间比他继女的较为宽敞，但房间里的陈设也是那么简朴。一张行军床，一个摆满书籍的小木制书架，架上的书籍多数是技术性的，床边是一把扶手椅，靠墙有一把普通的木椅，一张圆桌和一只大铁保险柜，这些就是一眼就能看到的主要家具和杂物。福尔摩斯在房间里慢慢地绕了一圈，全神贯注地，逐一地将它们都检查了一遍。

[P0165] 他敲敲保险柜问道：“这里面是什么？”

[P0166] “我继父业务上的文件。”

[P0167] “噢，那么你看见过里面的了？”

[P0168] “仅仅一次，那是几年以前。我记得里面装满了文件。”

[P0169] “比方说，里边不会有一只猫吗？”

[P0170] “不会，多么奇怪的想法！”

[P0171] “哦，看看这个！"他从保险柜上边拿起一个盛奶的浅碟。

[P0172] “不，我们没养猫。但是有一只印度猎豹和一只狒狒。”

[P0173] “啊，是的，当然！嗯，一只印度猎豹也差不多就是一只大猫，可是，我敢说要满足它的需要，一碟奶怕不怎么够吧。还有一个特点，我必须确定一下。"他蹲在木椅前，聚精会神地检查了椅子面。

[P0174] “谢谢你，差不多可以解决了。"说着，他站了起来把手中的放大镜放在衣袋里。"喂，这儿有件很有意思的东西！”

[P0175] 引其他注意的是挂在床头上的一根小打狗鞭子。不过，这根鞭子是卷着的，而且打成结，以使鞭绳盘成一个圈。

[P0176] “你怎么理解这件事，华生？”

[P0177] “那只不过是一根普通的鞭子。但我不明白，为什么要打成结？”

[P0178] “并不那么太平通吧，哎呀，这真是个万恶的世界，一个聪明人如果把脑子用在为非作歹上，那就糟透了。我想我现在已经察看够了，斯托纳小姐，如果你许可的话，我们到外面草坪上去走走。”

[P0179] 我从来没有见到过我的朋友在离开调查现场时，脸色是那样的严峻，或者说，表情是那样的阴沉。我们在草坪上来来回回地走着，无论是斯托纳小姐或者是我，都不想打断他的思路，直到他自己从沉思中恢复过来为止。

[P0180] “斯托纳小姐，"他说，“至关重要的是你在一切方面都必须绝对按我所说的去做。”

[P0181] “我一定照办。”

[P0182] “事情太严重了，不容有片刻犹豫。你的生命可能取决于你是否听从我的话。”

[P0183] “我向你保证，我一切听从你的吩咐。”

[P0184] “首先，我的朋友和我都必须在你的房间里过夜。”

[P0185] 斯托纳小姐和我都惊愕地看着他。

[P0186] “对，必须这样，让我来解释一下。我相信，那儿就是村里的旅店？”

[P0187] “是的，那是克朗旅店。”

[P0188] “好得很。从那儿看得见你的窗子？”

[P0189] “当然。”

[P0190] “你继父回来时，你一定要假装头疼，把自己关在房间里。然后，当你听到他夜里就寝后，你就必须打开你那扇窗户的百叶窗，解开窗户的搭扣，把灯摆在那儿作为给我们的信号，随后带上你可能需要的东西，悄悄地回到你过去住的房间。我毫不怀疑，尽管尚在修理，你还是能在那里住一宵的。”

[P0191] “噢，是的，没问题。”

[P0192] “其余的事情就交给我们处理好了。”

[P0193] “可是，你们打算怎么办呢？”

[P0194] “我们要在你的卧室里过夜，我们要调查打扰你的这种声音是怎么来的。”

[P0195] “我相信，福尔摩斯先生，你已经打定了主意。"斯托纳小姐拉着我同伴的袖子说。

[P0196] “也许是这样。”

[P0197] “那么，发发慈悲吧，告诉我，我姐姐是什么原因死的？”

[P0198] “我倒希望在有了更确切的证据之后再说。”

[P0199] “你至少可以告诉我，我的想法是否正确，她也许是突然受惊而死的。”

[P0200] “不，我不认为是那样。我认为可能有某种更为具体的原因。好啦，斯托纳小姐，我们必须离开你了，因为，要是罗伊洛特医生回来见到了我们，我们这次行程就会成为徒劳的了。再见，要勇敢些，只要你按照我告诉你的话去做，你尽可以放心，我们将很快解除威胁着你的危险。”

[P0201] 歇洛克·福尔摩斯和我没费什么事就在克朗旅店订了一间卧室和一间起居室。房间在二层楼，我们可以从窗子俯瞰斯托克莫兰庄园林荫道旁的大门和住人的边房。黄昏时刻，我们看到格里姆斯比·罗伊洛特医生驱车过去，他那硕大的躯体出现在给他赶车的瘦小的少年身旁，显得格外突出。那男仆在打开沉重的大铁门时，稍稍费了点事，我们听到医生嘶哑的咆哮声，并且看到他由于激怒而对那男仆挥舞着拳头。马车继续前进。过一会儿，我们看到树丛里突然照耀出一道灯光，原来这是有一间起居室点上了灯。

[P0202] “你知道吗，华生？"福尔摩斯说。这时，夜幕逐渐降临。我们正坐在一起谈话，“今天晚上你同我一起来，我的确不无顾虑，因为确实存在着明显的危险因素。”

[P0203] “我能助一臂之力吗？”

[P0204] “你在场可能会起很重要的作用。”

[P0205] “那么，我当然应该来。”

[P0206] “非常感谢！”

[P0207] “你说到危险。显然，你在这些房间里看到的东西比我看到的要多得多。”

[P0208] “不，但是我认为，我可能稍微多推断出一些东西。我想你同我一样看到了所有的东西。”

[P0209] “除了那铃绳以外，我没有看到其它值得注意的东西。至于那东西有什么用途，我承认，那不是我所能想象得出来的。”

[P0210] “你也看到那通气孔了吧？”

[P0211] “是的，但是我想在两个房间之间开个小洞，并不是什么异乎寻常的事。那洞口是那么窄小，连个耗子都很难钻过去。”

[P0212] “在我们没来斯托克莫兰以前，我就知道，我们将会发现一个通气孔。”

[P0213] “哎呀，亲爱的福尔摩斯！”

[P0214] “哦，是的，我知道的。你记得当初她在叙述中提到她姐姐能闻到罗伊洛特医生的雪茄烟味。那么，当然这立刻表明在两个房间当中必定有一个通道。可是，它只可能是非常窄小的，不然在验尸官的询问中，就会被提到。因此，我推断是一个通气孔。”

[P0215] “但是，那又会有什么妨害呢？”

[P0216] “嗯，至少在时间上有着奇妙的巧合，凿了一个通气孔，挂了一条绳索，睡在床上的一位小姐送了命。这难道还不足以引起你的注意吗？”

[P0217] “我仍然看不透其间有什么联系。”

[P0218] “你注意到那张床有什么非常特别的地方吗？”

[P0219] “没有。”

[P0220] “它是用螺钉固定在地板上的。你以前见到过一张那样固定的床吗？”

[P0221] “我不敢说见到过。”

[P0222] “那位小姐移动不了她的床。那张床就必然总是保持在同一相应的位置上，既对着通气孔，又对着铃绳——也许我们可以这样称呼它，因为显而易见，它从来也没有被当作铃绳用过。”

[P0223] “福尔摩斯，"我叫了起来，“我似乎隐约地领会到你暗示着什么。我们刚好来得及防止发生某种阴险而可怕的罪行。”

[P0224] “真够阴险可怕的。一个医生堕入歧途，他就是罪魁祸首。他既有胆量又有知识。帕尔默和气里查德就在他们这一行中名列前茅，但这个人更高深莫测。但是，华生，我想我们会比他更高明。不过天亮之前，担心害怕的事情还多得很；看在上帝的份上，让我们静静地抽一斗烟，换换脑筋。在这段时间里，想点愉快的事情吧。”

[P0225] 大约九点钟的时候，树丛中透过来的灯光熄灭了，庄园邸宅那边一片漆黑。两个小时缓慢地过去了，突然刚好时钟在打十一点的时候，我们的正前方出现了一盏孤灯，照射出明亮的灯火。

[P0226] “那是我们的信号，"福尔摩斯跳了起来说，“是从当中那个房间照出来的。”

[P0227] 我们向外走的时候，他和旅店老板交谈了几句话，解释说我们要连夜去访问一个熟友，可能会在那里过夜。一会儿，我们就来到了漆黑的路上，凉飕飕的冷风吹在脸上，在朦胧的夜色中，昏黄的灯光在我们的前方闪烁，引导我们去完成阴郁的使命。

[P0228] 由于山墙年久失修，到处是残墙断垣，我们轻而易举地进入了庭院。我们穿过树丛，又越过草坪，正待通过窗子进屋时，突然从一丛月桂树中，窜出了一个状若丑陋畸形的孩子的东西，它扭动着四肢纵身跳到草坪上，随即飞快地跑过草坪，消失在黑暗中。

[P0229] “天哪！"我低低地叫了一声，“你看到了吗？”

[P0230] 此刻，福尔摩斯和我一样，也吓了一大跳。他在激动中用象老虎钳似的手攥住了我的手腕。接着，他低声地笑了起来，把嘴唇凑到了我的耳朵上。

[P0231] “真是不错的一家子！"他低声地说，“这就是那只狒狒。”

[P0232] 我已经忘了医生所宠爱的奇特动物。还有一只印度猎豹呢！我们随时都有可能发现它趴在我们的肩上。我学着福尔摩斯的样子，脱下鞋，钻进了卧室。我承认，直到这时，我才感到放心一些。我的伙伴毫无声息地关上了百叶窗，把灯挪到桌子上，向屋子四周瞧了瞧。室内一切，和我们白天见到的一样，他蹑手蹑脚地走到我跟前，把手圈成喇叭形，再次对着我的耳朵小声说：“哪怕是最小的声音，都会破坏我们的计划。"声音轻得我刚能听出他说的是些什么。

[P0233] 我点头表示我听见了。

[P0234] “我们必须摸黑坐着，他会从通气孔发现有亮光的。”

[P0235] 我又点了点头。

[P0236] “千万别睡着，这关系到你的性命。把你的手枪准备好，以防万一我们用得着它。我坐在床边，你坐在那把椅子上。”

[P0237] 我取出左轮手枪，放在桌子角上。

[P0238] 福尔摩斯带来了一根又细又长的藤鞭，把它放在身边的床上。床旁边放了一盒火柴和一个蜡烛头。然后，他吹熄了灯，我们就呆在黑暗中了。

[P0239] 我怎么也忘不了那次可怕的守夜。我听不见一点声响，甚至连喘气的声音也听不见。可是我知道，我的伙伴正睁大眼睛坐着，和我只有咫尺之隔，并且一样处于神经紧张的状态。百叶窗把可能照到房间的最小光线都遮住了。我们在伸手不见五指的漆黑中等待着。外面偶尔传来猫头鹰的叫声，有一次就在我们的窗前传来二声长长的猫叫似的哀鸣，这说明那只印度猎豹确实在到处乱跑。我们还听到远处教堂深沉的钟声，每隔一刻钟就沉重地敲响一次。每刻钟仿佛都是无限漫长！敲了十二点、一点、两点、三点，我们一直沉默地端坐在那里等待着可能出现的任何情况。

[P0240] 突然，从通气孔那个方向闪现出一道瞬刻即逝的亮光，随之而来的是一股燃烧煤油和加热金属的强烈气味。隔壁房间里有人点着了一盏遮光灯。我听到了轻轻挪动的声音。接着，一切又都沉寂下来。可是那气味却越来越浓。我竖起耳朵坐了足足半个小时，突然，我听到另一种声音——一种非常柔和轻缓的声音，就象烧开了的水壶嘶嘶地喷着气。在我们听到这声音的一瞬间，福尔摩斯从床上跳了起来，划着了一根火柴，用他那根藤鞭猛烈地抽打那铃绳。

[P0241] “你看见了没有，华生？"他大声地嚷着，“你看见了没有？”

[P0242] 可是我什么也没有看见。就在福尔摩斯划着火柴的时候，我听到一声低沉、清晰的口哨声。但是，突如其来的耀眼亮光照着我疲倦的眼睛，使我看不清我朋友正在拚命抽打的是什么东西。可是我却看到，他的脸死一样地苍白，满脸恐怖和憎恶的表情。

[P0243] 他已停止了抽打，朝上注视着通气孔，紧接着在黑夜的寂静之中，突然爆发出一声我有生以来未听到过的最可怕的尖叫。而且叫声越来越高，这是交织着痛苦、恐惧和愤怒的令人可怖的尖声哀号。据说这喊声把远在村里，甚至远教区的人们都从熟睡中惊醒。这一叫声使我们为之毛骨悚然。我站在那里，呆呆地望着福尔摩斯，他也呆呆地望着我，一直到最后的回声渐趋消失，一切又恢复了原来的寂静时为止。

[P0244] “这是什么意思？"我忐忑不安地说。

[P0245] “这意思是事情就这样了结了，"福尔摩斯回答道。“而且，总的来看，这可能是最好的结局。带着你的手枪，我们到罗伊洛特医生的房间去。”

[P0246] 他点着了灯，带头走过过道，表情非常严峻。他敲了两次卧室的房门，里面没有回音，他随手转动了门把手，进入房内，我紧跟在他身后，手里握着扳起击铁的手枪。

[P0247] 出现在我们眼前的是一幅奇特的景象。桌上放着一盏遮光灯，遮光板半开着，一道亮光照到柜门半开的铁保险柜上。桌上旁边的那把木椅上，坐着格里姆斯比·罗伊洛特医生，他身上披着一件长长的灰色睡衣，睡衣下面露出一双赤裸的脚脖子，两脚套在红色土耳其无跟拖鞋里，膝盖上横搭着我们白天看到的那把短柄长鞭子。他的下巴向上翘起，他的一双眼睛恐怖地、僵直地盯着天花板的角落。他的额头上绕着一条异样的、带有褐色斑点的黄带子，那条带子似乎紧紧地缠在他的头上，我们走进去的时候，他既没有作声，也没有动一动。

[P0248] “带子！带斑点的带子！"福尔摩斯压低了声音说。

[P0249] 我向前跨了一步。只见他那条异样的头饰开始蠕动起来，从他的头发中间昂然钻出一条又粗又短、长着钻石型的头部和胀鼓鼓的脖子、令人恶心的毒蛇。

[P0250] “这是一条沼地蝰蛇！"福尔摩斯喊道，“印度最毒的毒蛇。医生被咬后十秒钟内就已经死去了。真是恶有恶报，阴谋家掉到他要害别人而挖的陷坑里去了。让我们把这畜生弄回到它的巢里去，然后我们就可以把斯托纳小姐转移到一个安全的地方，再让地方警察知道发生了些什么事情。”

[P0251] 说着话，他迅即从死者膝盖上取过打狗鞭子，将活结甩过去，套住那条爬虫的脖子，从它可怕地盘踞着的地方把它拉了起来，伸长了手臂提着它，扔到铁柜子里，随手将柜门关上。

[P0252] 这就是斯托克莫兰的格里姆斯比·罗伊洛特医生死亡的真实经过。这个叙述已经够长的了，至于我们怎样把这悲痛的消息告诉那吓坏了的小姐；怎样乘坐早车陪送她到哈罗，交给她好心的姨妈照看；冗长的警方调查怎样最后得出结论，认为医生是在不明智地玩弄他豢养的危险宠物时丧生的等等，就没有必要在这里一一赘述了。有关这件案子我还不太了解的一点情况，福尔摩斯在第二天回城的路上告诉了我。

已有人工标注上下文（可能为空；若存在，只作参考，不要机械复制）：
metadata:
  story_id: speckled_band
  title: "The Adventure of the Speckled Band"
  author: "Arthur Conan Doyle"
  language: en
  source_text_path: data/foreshadow_causality_benchmark/normalized_texts/speckled_band.txt
  source_url: https://www.gutenberg.org/cache/epub/1661/pg1661.txt
  copyright_status: public_domain
  genre: mystery
  length_level: short
  structure_type: [mystery]
annotation_guide:
  focus:
    - Mark material clues that are first presented as odd household details and later become parts of the murder mechanism.
    - Distinguish the gypsy "band" interpretation from the actual snake payoff as a red herring.
    - Track Holmes's reconstruction of causality from physical traces rather than confession.
  boundary_notes:
    - Treat Helen's testimony as narrated but reliable unless contradicted by later deduction.
    - Use paragraph identifiers from the normalized text for stable spans.
events:
  - event_id: SB_E01
    story_id: speckled_band
    chapter_or_section: whole_story
    text_span: P0028-P0051
    summary: Helen reports Julia's death after nightly whistles, a metallic sound, and the phrase "speckled band."
    participants: [Helen Stoner, Julia Stoner, Dr. Grimesby Roylott]
    location: Stoke Moran
    time: two years before the investigation
    event_type: death
    certainty: {value: certain}
    narrative_reality_level: {value: narrated}
  - event_id: SB_E02
    story_id: speckled_band
    chapter_or_section: investigation
    text_span: P0068
    summary: Repairs force Helen into Julia's former bedroom, and she hears the same low whistle.
    participants: [Helen Stoner, Dr. Grimesby Roylott]
    location: Stoke Moran
    time: two days before the night watch
    event_type: action
    certainty: {value: certain}
    narrative_reality_level: {value: narrated}
  - event_id: SB_E03
    story_id: speckled_band
    chapter_or_section: investigation
    text_span: P0143-P0158
    summary: Holmes observes the dummy bell-rope, the ventilator between rooms, and the fixed relation of bed, rope, and wall.
    participants: [Sherlock Holmes, Dr. Watson, Helen Stoner]
    location: Julia's bedroom
    time: daytime inspection
    event_type: discovery
    certainty: {value: certain}
    narrative_reality_level: {value: real}
  - event_id: SB_E04
    story_id: speckled_band
    chapter_or_section: investigation
    text_span: P0159-P0168
    summary: Holmes finds Roylott's safe, the saucer of milk, the chair, and the lash-like stock in the adjacent room.
    participants: [Sherlock Holmes, Dr. Watson, Dr. Grimesby Roylott]
    location: Roylott's bedroom
    time: daytime inspection
    event_type: discovery
    certainty: {value: certain}
    narrative_reality_level: {value: real}
  - event_id: SB_E05
    story_id: speckled_band
    chapter_or_section: deduction
    text_span: P0207-P0217
    summary: Holmes deduces that smoke smell implied a ventilator and that the bed's fixed position matters.
    participants: [Sherlock Holmes, Dr. Watson]
    location: near Stoke Moran
    time: before the night watch
    event_type: revelation
    certainty: {value: certain}
    narrative_reality_level: {value: real}
  - event_id: SB_E06
    story_id: speckled_band
    chapter_or_section: climax
    text_span: P0237-P0239
    summary: During the night watch Holmes hears the signal, strikes at the bell-pull, and drives the creature back.
    participants: [Sherlock Holmes, Dr. Watson, Dr. Grimesby Roylott]
    location: Julia's bedroom
    time: night watch
    event_type: action
    certainty: {value: certain}
    narrative_reality_level: {value: real}
  - event_id: SB_E07
    story_id: speckled_band
    chapter_or_section: resolution
    text_span: P0243-P0247
    summary: Roylott is found dead with the speckled swamp adder around him, revealing the murder mechanism.
    participants: [Sherlock Holmes, Dr. Watson, Dr. Grimesby Roylott]
    location: Roylott's bedroom
    time: after the snake returns
    event_type: revelation
    certainty: {value: certain}
    narrative_reality_level: {value: real}
causal_edges:
  - edge_id: SB_C01
    story_id: speckled_band
    source_event_id: SB_E02
    target_event_id: SB_E03
    relation_type: enables
    strength: {value: strong}
    evidence_text_span: P0068-P0158
    explanation: Helen's move into the fatal room makes the room's artificial arrangement available for inspection and for a repeated attack.
  - edge_id: SB_C02
    story_id: speckled_band
    source_event_id: SB_E03
    target_event_id: SB_E05
    relation_type: reveals
    strength: {value: strong}
    evidence_text_span: P0207-P0217
    explanation: The dummy bell-rope, ventilator, and fixed bed reveal that the room is configured as a delivery path rather than ordinary furniture.
  - edge_id: SB_C03
    story_id: speckled_band
    source_event_id: SB_E04
    target_event_id: SB_E05
    relation_type: reveals
    strength: {value: medium}
    evidence_text_span: P0159-P0168
    explanation: The safe, milk, chair, and lash-like object support the inference that Roylott keeps and controls an animal.
  - edge_id: SB_C04
    story_id: speckled_band
    source_event_id: SB_E06
    target_event_id: SB_E07
    relation_type: causes
    strength: {value: strong}
    evidence_text_span: P0237-P0247
    explanation: Holmes's blow sends the snake back through the ventilator, leading it to bite Roylott.
  - edge_id: SB_C05
    story_id: speckled_band
    source_event_id: SB_E01
    target_event_id: SB_E05
    relation_type: misleads_about
    strength: {value: medium}
    evidence_text_span: P0051-P0091
    explanation: Julia's "speckled band" phrase initially points toward gypsies before the phrase is reinterpreted as the snake.
foreshadowing_units:
  - foreshadowing_id: SB_F01
    story_id: speckled_band
    foreshadowing_text_span: P0143-P0158
    foreshadowing_summary: The bell-rope and ventilator are odd because they do not serve their apparent household functions.
    foreshad
...
```
