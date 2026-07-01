# Short Story CFPG Prompt Preview

## system

```text
你是短篇小说伏笔-触发-回收结构标注员。任务是在给定的全文段落时间线中，高召回抽取候选 Foreshadow-Trigger-Payoff 三元组。只能依据输入文本，不得使用外部知识或你对作品结局的先验记忆。只输出合法 JSON。
```

## user

```text
请对下面的短篇小说段落时间线执行第一步：高召回候选识别。

作品：
- story_id: red_headed_league
- title: red_headed_league
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
[P0001] II. THE RED-HEADED LEAGUE

[P0002] I had called upon my friend, Mr. Sherlock Holmes, one day in the autumn of last year and found him in deep conversation with a very stout, florid-faced, elderly gentleman with fiery red hair. With an apology for my intrusion, I was about to withdraw when Holmes pulled me abruptly into the room and closed the door behind me.

[P0003] “You could not possibly have come at a better time, my dear Watson,” he said cordially.

[P0004] “I was afraid that you were engaged.”

[P0005] “So I am. Very much so.”

[P0006] “Then I can wait in the next room.”

[P0007] “Not at all. This gentleman, Mr. Wilson, has been my partner and helper in many of my most successful cases, and I have no doubt that he will be of the utmost use to me in yours also.”

[P0008] The stout gentleman half rose from his chair and gave a bob of greeting, with a quick little questioning glance from his small fat-encircled eyes.

[P0009] “Try the settee,” said Holmes, relapsing into his armchair and putting his fingertips together, as was his custom when in judicial moods. “I know, my dear Watson, that you share my love of all that is bizarre and outside the conventions and humdrum routine of everyday life. You have shown your relish for it by the enthusiasm which has prompted you to chronicle, and, if you will excuse my saying so, somewhat to embellish so many of my own little adventures.”

[P0010] “Your cases have indeed been of the greatest interest to me,” I observed.

[P0011] “You will remember that I remarked the other day, just before we went into the very simple problem presented by Miss Mary Sutherland, that for strange effects and extraordinary combinations we must go to life itself, which is always far more daring than any effort of the imagination.”

[P0012] “A proposition which I took the liberty of doubting.”

[P0013] “You did, Doctor, but none the less you must come round to my view, for otherwise I shall keep on piling fact upon fact on you until your reason breaks down under them and acknowledges me to be right. Now, Mr. Jabez Wilson here has been good enough to call upon me this morning, and to begin a narrative which promises to be one of the most singular which I have listened to for some time. You have heard me remark that the strangest and most unique things are very often connected not with the larger but with the smaller crimes, and occasionally, indeed, where there is room for doubt whether any positive crime has been committed. As far as I have heard, it is impossible for me to say whether the present case is an instance of crime or not, but the course of events is certainly among the most singular that I have ever listened to. Perhaps, Mr. Wilson, you would have the great kindness to recommence your narrative. I ask you not merely because my friend Dr. Watson has not heard the opening part but also because the peculiar nature of the story makes me anxious to have every possible detail from your lips. As a rule, when I have heard some slight indication of the course of events, I am able to guide myself by the thousands of other similar cases which occur to my memory. In the present instance I am forced to admit that the facts are, to the best of my belief, unique.”

[P0014] The portly client puffed out his chest with an appearance of some little pride and pulled a dirty and wrinkled newspaper from the inside pocket of his greatcoat. As he glanced down the advertisement column, with his head thrust forward and the paper flattened out upon his knee, I took a good look at the man and endeavoured, after the fashion of my companion, to read the indications which might be presented by his dress or appearance.

[P0015] I did not gain very much, however, by my inspection. Our visitor bore every mark of being an average commonplace British tradesman, obese, pompous, and slow. He wore rather baggy grey shepherd’s check trousers, a not over-clean black frock-coat, unbuttoned in the front, and a drab waistcoat with a heavy brassy Albert chain, and a square pierced bit of metal dangling down as an ornament. A frayed top-hat and a faded brown overcoat with a wrinkled velvet collar lay upon a chair beside him. Altogether, look as I would, there was nothing remarkable about the man save his blazing red head, and the expression of extreme chagrin and discontent upon his features.

[P0016] Sherlock Holmes’ quick eye took in my occupation, and he shook his head with a smile as he noticed my questioning glances. “Beyond the obvious facts that he has at some time done manual labour, that he takes snuff, that he is a Freemason, that he has been in China, and that he has done a considerable amount of writing lately, I can deduce nothing else.”

[P0017] Mr. Jabez Wilson started up in his chair, with his forefinger upon the paper, but his eyes upon my companion.

[P0018] “How, in the name of good-fortune, did you know all that, Mr. Holmes?” he asked. “How did you know, for example, that I did manual labour. It’s as true as gospel, for I began as a ship’s carpenter.”

[P0019] “Your hands, my dear sir. Your right hand is quite a size larger than your left. You have worked with it, and the muscles are more developed.”

[P0020] “Well, the snuff, then, and the Freemasonry?”

[P0021] “I won’t insult your intelligence by telling you how I read that, especially as, rather against the strict rules of your order, you use an arc-and-compass breastpin.”

[P0022] “Ah, of course, I forgot that. But the writing?”

[P0023] “What else can be indicated by that right cuff so very shiny for five inches, and the left one with the smooth patch near the elbow where you rest it upon the desk?”

[P0024] “Well, but China?”

[P0025] “The fish that you have tattooed immediately above your right wrist could only have been done in China. I have made a small study of tattoo marks and have even contributed to the literature of the subject. That trick of staining the fishes’ scales of a delicate pink is quite peculiar to China. When, in addition, I see a Chinese coin hanging from your watch-chain, the matter becomes even more simple.”

[P0026] Mr. Jabez Wilson laughed heavily. “Well, I never!” said he. “I thought at first that you had done something clever, but I see that there was nothing in it after all.”

[P0027] “I begin to think, Watson,” said Holmes, “that I make a mistake in explaining. ‘_Omne ignotum pro magnifico_,’ you know, and my poor little reputation, such as it is, will suffer shipwreck if I am so candid. Can you not find the advertisement, Mr. Wilson?”

[P0028] “Yes, I have got it now,” he answered with his thick red finger planted halfway down the column. “Here it is. This is what began it all. You just read it for yourself, sir.”

[P0029] I took the paper from him and read as follows:

[P0030] “TO THE RED-HEADED LEAGUE: On account of the bequest of the late Ezekiah Hopkins, of Lebanon, Pennsylvania, U.S.A., there is now another vacancy open which entitles a member of the League to a salary of £ 4 a week for purely nominal services. All red-headed men who are sound in body and mind and above the age of twenty-one years, are eligible. Apply in person on Monday, at eleven o’clock, to Duncan Ross, at the offices of the League, 7 Pope’s Court, Fleet Street.”

[P0031] “What on earth does this mean?” I ejaculated after I had twice read over the extraordinary announcement.

[P0032] Holmes chuckled and wriggled in his chair, as was his habit when in high spirits. “It is a little off the beaten track, isn’t it?” said he. “And now, Mr. Wilson, off you go at scratch and tell us all about yourself, your household, and the effect which this advertisement had upon your fortunes. You will first make a note, Doctor, of the paper and the date.”

[P0033] “It is _The Morning Chronicle_ of April 27, 1890. Just two months ago.”

[P0034] “Very good. Now, Mr. Wilson?”

[P0035] “Well, it is just as I have been telling you, Mr. Sherlock Holmes,” said Jabez Wilson, mopping his forehead; “I have a small pawnbroker’s business at Coburg Square, near the City. It’s not a very large affair, and of late years it has not done more than just give me a living. I used to be able to keep two assistants, but now I only keep one; and I would have a job to pay him but that he is willing to come for half wages so as to learn the business.”

[P0036] “What is the name of this obliging youth?” asked Sherlock Holmes.

[P0037] “His name is Vincent Spaulding, and he’s not such a youth, either. It’s hard to say his age. I should not wish a smarter assistant, Mr. Holmes; and I know very well that he could better himself and earn twice what I am able to give him. But, after all, if he is satisfied, why should I put ideas in his head?”

[P0038] “Why, indeed? You seem most fortunate in having an _employé_ who comes under the full market price. It is not a common experience among employers in this age. I don’t know that your assistant is not as remarkable as your advertisement.”

[P0039] “Oh, he has his faults, too,” said Mr. Wilson. “Never was such a fellow for photography. Snapping away with a camera when he ought to be improving his mind, and then diving down into the cellar like a rabbit into its hole to develop his pictures. That is his main fault, but on the whole he’s a good worker. There’s no vice in him.”

[P0040] “He is still with you, I presume?”

[P0041] “Yes, sir. He and a girl of fourteen, who does a bit of simple cooking and keeps the place clean—that’s all I have in the house, for I am a widower and never had any family. We live very quietly, sir, the three of us; and we keep a roof over our heads and pay our debts, if we do nothing more.

[P0042] “The first thing that put us out was that advertisement. Spaulding, he came down into the office just this day eight weeks, with this very paper in his hand, and he says:

[P0043] “‘I wish to the Lord, Mr. Wilson, that I was a red-headed man.’

[P0044] “‘Why that?’ I asks.

[P0045] “‘Why,’ says he, ‘here’s another vacancy on the League of the Red-headed Men. It’s worth quite a little fortune to any man who gets it, and I understand that there are more vacancies than there are men, so that the trustees are at their wits’ end what to do with the money. If my hair would only change colour, here’s a nice little crib all ready for me to step into.’

[P0046] “‘Why, what is it, then?’ I asked. You see, Mr. Holmes, I am a very stay-at-home man, and as my business came to me instead of my having to go to it, I was often weeks on end without putting my foot over the door-mat. In that way I didn’t know much of what was going on outside, and I was always glad of a bit of news.

[P0047] “‘Have you never heard of the League of the Red-headed Men?’ he asked with his eyes open.

[P0048] “‘Never.’

[P0049] “‘Why, I wonder at that, for you are eligible yourself for one of the vacancies.’

[P0050] “‘And what are they worth?’ I asked.

[P0051] “‘Oh, merely a couple of hundred a year, but the work is slight, and it need not interfere very much with one’s other occupations.’

[P0052] “Well, you can easily think that that made me prick up my ears, for the business has not been over good for some years, and an extra couple of hundred would have been very handy.

[P0053] “‘Tell me all about it,’ said I.

[P0054] “‘Well,’ said he, showing me the advertisement, ‘you can see for yourself that the League has a vacancy, and there is the address where you should apply for particulars. As far as I can make out, the League was founded by an American millionaire, Ezekiah Hopkins, who was very peculiar in his ways. He was himself red-headed, and he had a great sympathy for all red-headed men; so, when he died, it was found that he had left his enormous fortune in the hands of trustees, with instructions to apply the interest to the providing of easy berths to men whose hair is of that colour. From all I hear it is splendid pay and very little to do.’

[P0055] “‘But,’ said I, ‘there would be millions of red-headed men who would apply.’

[P0056] “‘Not so many as you might think,’ he answered. ‘You see it is really confined to Londoners, and to grown men. This American had started from London when he was young, and he wanted to do the old town a good turn. Then, again, I have heard it is no use your applying if your hair is light red, or dark red, or anything but real bright, blazing, fiery red. Now, if you cared to apply, Mr. Wilson, you would just walk in; but perhaps it would hardly be worth your while to put yourself out of the way for the sake of a few hundred pounds.’

[P0057] “Now, it is a fact, gentlemen, as you may see for yourselves, that my hair is of a very full and rich tint, so that it seemed to me that if there was to be any competition in the matter I stood as good a chance as any man that I had ever met. Vincent Spaulding seemed to know so much about it that I thought he might prove useful, so I just ordered him to put up the shutters for the day and to come right away with me. He was very willing to have a holiday, so we shut the business up and started off for the address that was given us in the advertisement.

[P0058] “I never hope to see such a sight as that again, Mr. Holmes. From north, south, east, and west every man who had a shade of red in his hair had tramped into the city to answer the advertisement. Fleet Street was choked with red-headed folk, and Pope’s Court looked like a coster’s orange barrow. I should not have thought there were so many in the whole country as were brought together by that single advertisement. Every shade of colour they were—straw, lemon, orange, brick, Irish-setter, liver, clay; but, as Spaulding said, there were not many who had the real vivid flame-coloured tint. When I saw how many were waiting, I would have given it up in despair; but Spaulding would not hear of it. How he did it I could not imagine, but he pushed and pulled and butted until he got me through the crowd, and right up to the steps which led to the office. There was a double stream upon the stair, some going up in hope, and some coming back dejected; but we wedged in as well as we could and soon found ourselves in the office.”

[P0059] “Your experience has been a most entertaining one,” remarked Holmes as his client paused and refreshed his memory with a huge pinch of snuff. “Pray continue your very interesting statement.”

[P0060] “There was nothing in the office but a couple of wooden chairs and a deal table, behind which sat a small man with a head that was even redder than mine. He said a few words to each candidate as he came up, and then he always managed to find some fault in them which would disqualify them. Getting a vacancy did not seem to be such a very easy matter, after all. However, when our turn came the little man was much more favourable to me than to any of the others, and he closed the door as we entered, so that he might have a private word with us.

[P0061] “‘This is Mr. Jabez Wilson,’ said my assistant, ‘and he is willing to fill a vacancy in the League.’

[P0062] “‘And he is admirably suited for it,’ the other answered. ‘He has every requirement. I cannot recall when I have seen anything so fine.’ He took a step backward, cocked his head on one side, and gazed at my hair until I felt quite bashful. Then suddenly he plunged forward, wrung my hand, and congratulated me warmly on my success.

[P0063] “‘It would be injustice to hesitate,’ said he. ‘You will, however, I am sure, excuse me for taking an obvious precaution.’ With that he seized my hair in both his hands, and tugged until I yelled with the pain. ‘There is water in your eyes,’ said he as he released me. ‘I perceive that all is as it should be. But we have to be careful, for we have twice been deceived by wigs and once by paint. I could tell you tales of cobbler’s wax which would disgust you with human nature.’ He stepped over to the window and shouted through it at the top of his voice that the vacancy was filled. A groan of disappointment came up from below, and the folk all trooped away in different directions until there was not a red-head to be seen except my own and that of the manager.

[P0064] “‘My name,’ said he, ‘is Mr. Duncan Ross, and I am myself one of the pensioners upon the fund left by our noble benefactor. Are you a married man, Mr. Wilson? Have you a family?’

[P0065] “I answered that I had not.

[P0066] “His face fell immediately.

[P0067] “‘Dear me!’ he said gravely, ‘that is very serious indeed! I am sorry to hear you say that. The fund was, of course, for the propagation and spread of the red-heads as well as for their maintenance. It is exceedingly unfortunate that you should be a bachelor.’

[P0068] “My face lengthened at this, Mr. Holmes, for I thought that I was not to have the vacancy after all; but after thinking it over for a few minutes he said that it would be all right.

[P0069] “‘In the case of another,’ said he, ‘the objection might be fatal, but we must stretch a point in favour of a man with such a head of hair as yours. When shall you be able to enter upon your new duties?’

[P0070] “‘Well, it is a little awkward, for I have a business already,’ said I.

[P0071] “‘Oh, never mind about that, Mr. Wilson!’ said Vincent Spaulding. ‘I should be able to look after that for you.’

[P0072] “‘What would be the hours?’ I asked.

[P0073] “‘Ten to two.’

[P0074] “Now a pawnbroker’s business is mostly done of an evening, Mr. Holmes, especially Thursday and Friday evening, which is just before pay-day; so it would suit me very well to earn a little in the mornings. Besides, I knew that my assistant was a good man, and that he would see to anything that turned up.

[P0075] “‘That would suit me very well,’ said I. ‘And the pay?’

[P0076] “‘Is £ 4 a week.’

[P0077] “‘And the work?’

[P0078] “‘Is purely nominal.’

[P0079] “‘What do you call purely nominal?’

[P0080] “‘Well, you have to be in the office, or at least in the building, the whole time. If you leave, you forfeit your whole position forever. The will is very clear upon that point. You don’t comply with the conditions if you budge from the office during that time.’

[P0081] “‘It’s only four hours a day, and I should not think of leaving,’ said I.

[P0082] “‘No excuse will avail,’ said Mr. Duncan Ross; ‘neither sickness nor business nor anything else. There you must stay, or you lose your billet.’

[P0083] “‘And the work?’

[P0084] “‘Is to copy out the _Encyclopædia Britannica_. There is the first volume of it in that press. You must find your own ink, pens, and blotting-paper, but we provide this table and chair. Will you be ready to-morrow?’

[P0085] “‘Certainly,’ I answered.

[P0086] “‘Then, good-bye, Mr. Jabez Wilson, and let me congratulate you once more on the important position which you have been fortunate enough to gain.’ He bowed me out of the room and I went home with my assistant, hardly knowing what to say or do, I was so pleased at my own good fortune.

[P0087] “Well, I thought over the matter all day, and by evening I was in low spirits again; for I had quite persuaded myself that the whole affair must be some great hoax or fraud, though what its object might be I could not imagine. It seemed altogether past belief that anyone could make such a will, or that they would pay such a sum for doing anything so simple as copying out the _Encyclopædia Britannica_. Vincent Spaulding did what he could to cheer me up, but by bedtime I had reasoned myself out of the whole thing. However, in the morning I determined to have a look at it anyhow, so I bought a penny bottle of ink, and with a quill-pen, and seven sheets of foolscap paper, I started off for Pope’s Court.

[P0088] “Well, to my surprise and delight, everything was as right as possible. The table was set out ready for me, and Mr. Duncan Ross was there to see that I got fairly to work. He started me off upon the letter A, and then he left me; but he would drop in from time to time to see that all was right with me. At two o’clock he bade me good-day, complimented me upon the amount that I had written, and locked the door of the office after me.

[P0089] “This went on day after day, Mr. Holmes, and on Saturday the manager came in and planked down four golden sovereigns for my week’s work. It was the same next week, and the same the week after. Every morning I was there at ten, and every afternoon I left at two. By degrees Mr. Duncan Ross took to coming in only once of a morning, and then, after a time, he did not come in at all. Still, of course, I never dared to leave the room for an instant, for I was not sure when he might come, and the billet was such a good one, and suited me so well, that I would not risk the loss of it.

[P0090] “Eight weeks passed away like this, and I had written about Abbots and Archery and Armour and Architecture and Attica, and hoped with diligence that I might get on to the B’s before very long. It cost me something in foolscap, and I had pretty nearly filled a shelf with my writings. And then suddenly the whole business came to an end.”

[P0091] “To an end?”

[P0092] “Yes, sir. And no later than this morning. I went to my work as usual at ten o’clock, but the door was shut and locked, with a little square of cardboard hammered on to the middle of the panel with a tack. Here it is, and you can read for yourself.”

[P0093] He held up a piece of white cardboard about the size of a sheet of note-paper. It read in this fashion:

[P0094] “THE RED-HEADED LEAGUE IS DISSOLVED. October 9, 1890.”

[P0095] Sherlock Holmes and I surveyed this curt announcement and the rueful face behind it, until the comical side of the affair so completely overtopped every other consideration that we both burst out into a roar of laughter.

[P0096] “I cannot see that there is anything very funny,” cried our client, flushing up to the roots of his flaming head. “If you can do nothing better than laugh at me, I can go elsewhere.”

[P0097] “No, no,” cried Holmes, shoving him back into the chair from which he had half risen. “I really wouldn’t miss your case for the world. It is most refreshingly unusual. But there is, if you will excuse my saying so, something just a little funny about it. Pray what steps did you take when you found the card upon the door?”

[P0098] “I was staggered, sir. I did not know what to do. Then I called at the offices round, but none of them seemed to know anything about it. Finally, I went to the landlord, who is an accountant living on the ground floor, and I asked him if he could tell me what had become of the Red-headed League. He said that he had never heard of any such body. Then I asked him who Mr. Duncan Ross was. He answered that the name was new to him.

[P0099] “‘Well,’ said I, ‘the gentleman at No. 4.’

[P0100] “‘What, the red-headed man?’

[P0101] “‘Yes.’

[P0102] “‘Oh,’ said he, ‘his name was William Morris. He was a solicitor and was using my room as a temporary convenience until his new premises were ready. He moved out yesterday.’

[P0103] “‘Where could I find him?’

[P0104] “‘Oh, at his new offices. He did tell me the address. Yes, 17 King Edward Street, near St. Paul’s.’

[P0105] “I started off, Mr. Holmes, but when I got to that address it was a manufactory of artificial knee-caps, and no one in it had ever heard of either Mr. William Morris or Mr. Duncan Ross.”

[P0106] “And what did you do then?” asked Holmes.

[P0107] “I went home to Saxe-Coburg Square, and I took the advice of my assistant. But he could not help me in any way. He could only say that if I waited I should hear by post. But that was not quite good enough, Mr. Holmes. I did not wish to lose such a place without a struggle, so, as I had heard that you were good enough to give advice to poor folk who were in need of it, I came right away to you.”

[P0108] “And you did very wisely,” said Holmes. “Your case is an exceedingly remarkable one, and I shall be happy to look into it. From what you have told me I think that it is possible that graver issues hang from it than might at first sight appear.”

[P0109] “Grave enough!” said Mr. Jabez Wilson. “Why, I have lost four pound a week.”

[P0110] “As far as you are personally concerned,” remarked Holmes, “I do not see that you have any grievance against this extraordinary league. On the contrary, you are, as I understand, richer by some £ 30, to say nothing of the minute knowledge which you have gained on every subject which comes under the letter A. You have lost nothing by them.”

[P0111] “No, sir. But I want to find out about them, and who they are, and what their object was in playing this prank—if it was a prank—upon me. It was a pretty expensive joke for them, for it cost them two and thirty pounds.”

[P0112] “We shall endeavour to clear up these points for you. And, first, one or two questions, Mr. Wilson. This assistant of yours who first called your attention to the advertisement—how long had he been with you?”

[P0113] “About a month then.”

[P0114] “How did he come?”

[P0115] “In answer to an advertisement.”

[P0116] “Was he the only applicant?”

[P0117] “No, I had a dozen.”

[P0118] “Why did you pick him?”

[P0119] “Because he was handy and would come cheap.”

[P0120] “At half wages, in fact.”

[P0121] “Yes.”

[P0122] “What is he like, this Vincent Spaulding?”

[P0123] “Small, stout-built, very quick in his ways, no hair on his face, though he’s not short of thirty. Has a white splash of acid upon his forehead.”

[P0124] Holmes sat up in his chair in considerable excitement. “I thought as much,” said he. “Have you ever observed that his ears are pierced for earrings?”

[P0125] “Yes, sir. He told me that a gipsy had done it for him when he was a lad.”

[P0126] “Hum!” said Holmes, sinking back in deep thought. “He is still with you?”

[P0127] “Oh, yes, sir; I have only just left him.”

[P0128] “And has your business been attended to in your absence?”

[P0129] “Nothing to complain of, sir. There’s never very much to do of a morning.”

[P0130] “That will do, Mr. Wilson. I shall be happy to give you an opinion upon the subject in the course of a day or two. To-day is Saturday, and I hope that by Monday we may come to a conclusion.”

[P0131] “Well, Watson,” said Holmes when our visitor had left us, “what do you make of it all?”

[P0132] “I make nothing of it,” I answered frankly. “It is a most mysterious business.”

[P0133] “As a rule,” said Holmes, “the more bizarre a thing is the less mysterious it proves to be. It is your commonplace, featureless crimes which are really puzzling, just as a commonplace face is the most difficult to identify. But I must be prompt over this matter.”

[P0134] “What are you going to do, then?” I asked.

[P0135] “To smoke,” he answered. “It is quite a three pipe problem, and I beg that you won’t speak to me for fifty minutes.” He curled himself up in his chair, with his thin knees drawn up to his hawk-like nose, and there he sat with his eyes closed and his black clay pipe thrusting out like the bill of some strange bird. I had come to the conclusion that he had dropped asleep, and indeed was nodding myself, when he suddenly sprang out of his chair with the gesture of a man who has made up his mind and put his pipe down upon the mantelpiece.

[P0136] “Sarasate plays at the St. James’s Hall this afternoon,” he remarked. “What do you think, Watson? Could your patients spare you for a few hours?”

[P0137] “I have nothing to do to-day. My practice is never very absorbing.”

[P0138] “Then put on your hat and come. I am going through the City first, and we can have some lunch on the way. I observe that there is a good deal of German music on the programme, which is rather more to my taste than Italian or French. It is introspective, and I want to introspect. Come along!”

[P0139] We travelled by the Underground as far as Aldersgate; and a short walk took us to Saxe-Coburg Square, the scene of the singular story which we had listened to in the morning. It was a poky, little, shabby-genteel place, where four lines of dingy two-storied brick houses looked out into a small railed-in enclosure, where a lawn of weedy grass and a few clumps of faded laurel bushes made a hard fight against a smoke-laden and uncongenial atmosphere. Three gilt balls and a brown board with “JABEZ WILSON” in white letters, upon a corner house, announced the place where our red-headed client carried on his business. Sherlock Holmes stopped in front of it with his head on one side and looked it all over, with his eyes shining brightly between puckered lids. Then he walked slowly up the street, and then down again to the corner, still looking keenly at the houses. Finally he returned to the pawnbroker’s, and, having thumped vigorously upon the pavement with his stick two or three times, he went up to the door and knocked. It was instantly opened by a bright-looking, clean-shaven young fellow, who asked him to step in.

[P0140] “Thank you,” said Holmes, “I only wished to ask you how you would go from here to the Strand.”

[P0141] “Third right, fourth left,” answered the assistant promptly, closing the door.

[P0142] “Smart fellow, that,” observed Holmes as we walked away. “He is, in my judgment, the fourth smartest man in London, and for daring I am not sure that he has not a claim to be third. I have known something of him before.”

[P0143] “Evidently,” said I, “Mr. Wilson’s assistant counts for a good deal in this mystery of the Red-headed League. I am sure that you inquired your way merely in order that you might see him.”

[P0144] “Not him.”

[P0145] “What then?”

[P0146] “The knees of his trousers.”

[P0147] “And what did you see?”

[P0148] “What I expected to see.”

[P0149] “Why did you beat the pavement?”

[P0150] “My dear doctor, this is a time for observation, not for talk. We are spies in an enemy’s country. We know something of Saxe-Coburg Square. Let us now explore the parts which lie behind it.”

[P0151] The road in which we found ourselves as we turned round the corner from the retired Saxe-Coburg Square presented as great a contrast to it as the front of a picture does to the back. It was one of the main arteries which conveyed the traffic of the City to the north and west. The roadway was blocked with the immense stream of commerce flowing in a double tide inward and outward, while the footpaths were black with the hurrying swarm of pedestrians. It was difficult to realise as we looked at the line of fine shops and stately business premises that they really abutted on the other side upon the faded and stagnant square which we had just quitted.

[P0152] “Let me see,” said Holmes, standing at the corner and glancing along the line, “I should like just to remember the order of the houses here. It is a hobby of mine to have an exact knowledge of London. There is Mortimer’s, the tobacconist, the little newspaper shop, the Coburg branch of the City and Suburban Bank, the Vegetarian Restaurant, and McFarlane’s carriage-building depot. That carries us right on to the other block. And now, Doctor, we’ve done our work, so it’s time we had some play. A sandwich and a cup of coffee, and then off to violin-land, where all is sweetness and delicacy and harmony, and there are no red-headed clients to vex us with their conundrums.”

[P0153] My friend was an enthusiastic musician, being himself not only a very capable performer but a composer of no ordinary merit. All the afternoon he sat in the stalls wrapped in the most perfect happiness, gently waving his long, thin fingers in time to the music, while his gently smiling face and his languid, dreamy eyes were as unlike those of Holmes the sleuth-hound, Holmes the relentless, keen-witted, ready-handed criminal agent, as it was possible to conceive. In his singular character the dual nature alternately asserted itself, and his extreme exactness and astuteness represented, as I have often thought, the reaction against the poetic and contemplative mood which occasionally predominated in him. The swing of his nature took him from extreme languor to devouring energy; and, as I knew well, he was never so truly formidable as when, for days on end, he had been lounging in his armchair amid his improvisations and his black-letter editions. Then it was that the lust of the chase would suddenly come upon him, and that his brilliant reasoning power would rise to the level of intuition, until those who were unacquainted with his methods would look askance at him as on a man whose knowledge was not that of other mortals. When I saw him that afternoon so enwrapped in the music at St. James’s Hall I felt that an evil time might be coming upon those whom he had set himself to hunt down.

[P0154] “You want to go home, no doubt, Doctor,” he remarked as we emerged.

[P0155] “Yes, it would be as well.”

[P0156] “And I have some business to do which will take some hours. This business at Coburg Square is serious.”

[P0157] “Why serious?”

[P0158] “A considerable crime is in contemplation. I have every reason to believe that we shall be in time to stop it. But to-day being Saturday rather complicates matters. I shall want your help to-night.”

[P0159] “At what time?”

[P0160] “Ten will be early enough.”

[P0161] “I shall be at Baker Street at ten.”

[P0162] “Very well. And, I say, Doctor, there may be some little danger, so kindly put your army revolver in your pocket.” He waved his hand, turned on his heel, and disappeared in an instant among the crowd.

[P0163] I trust that I am not more dense than my neighbours, but I was always oppressed with a sense of my own stupidity in my dealings with Sherlock Holmes. Here I had heard what he had heard, I had seen what he had seen, and yet from his words it was evident that he saw clearly not only what had happened but what was about to happen, while to me the whole business was still confused and grotesque. As I drove home to my house in Kensington I thought over it all, from the extraordinary story of the red-headed copier of the _Encyclopædia_ down to the visit to Saxe-Coburg Square, and the ominous words with which he had parted from me. What was this nocturnal expedition, and why should I go armed? Where were we going, and what were we to do? I had the hint from Holmes that this smooth-faced pawnbroker’s assistant was a formidable man—a man who might play a deep game. I tried to puzzle it out, but gave it up in despair and set the matter aside until night should bring an explanation.

[P0164] It was a quarter-past nine when I started from home and made my way across the Park, and so through Oxford Street to Baker Street. Two hansoms were standing at the door, and as I entered the passage I heard the sound of voices from above. On entering his room, I found Holmes in animated conversation with two men, one of whom I recognised as Peter Jones, the official police agent, while the other was a long, thin, sad-faced man, with a very shiny hat and oppressively respectable frock-coat.

[P0165] “Ha! Our party is complete,” said Holmes, buttoning up his pea-jacket and taking his heavy hunting crop from the rack. “Watson, I think you know Mr. Jones, of Scotland Yard? Let me introduce you to Mr. Merryweather, who is to be our companion in to-night’s adventure.”

[P0166] “We’re hunting in couples again, Doctor, you see,” said Jones in his consequential way. “Our friend here is a wonderful man for starting a chase. All he wants is an old dog to help him to do the running down.”

[P0167] “I hope a wild goose may not prove to be the end of our chase,” observed Mr. Merryweather gloomily.

[P0168] “You may place considerable confidence in Mr. Holmes, sir,” said the police agent loftily. “He has his own little methods, which are, if he won’t mind my saying so, just a little too theoretical and fantastic, but he has the makings of a detective in him. It is not too much to say that once or twice, as in that business of the Sholto murder and the Agra treasure, he has been more nearly correct than the official force.”

[P0169] “Oh, if you say so, Mr. Jones, it is all right,” said the stranger with deference. “Still, I confess that I miss my rubber. It is the first Saturday night for seven-and-twenty years that I have not had my rubber.”

[P0170] “I think you will find,” said Sherlock Holmes, “that you will play for a higher stake to-night than you have ever done yet, and that the play will be more exciting. For you, Mr. Merryweather, the stake will be some £ 30,000; and for you, Jones, it will be the man upon whom you wish to lay your hands.”

[P0171] “John Clay, the murderer, thief, smasher, and forger. He’s a young man, Mr. Merryweather, but he is at the head of his profession, and I would rather have my bracelets on him than on any criminal in London. He’s a remarkable man, is young John Clay. His grandfather was a royal duke, and he himself has been to Eton and Oxford. His brain is as cunning as his fingers, and though we meet signs of him at every turn, we never know where to find the man himself. He’ll crack a crib in Scotland one week, and be raising money to build an orphanage in Cornwall the next. I’ve been on his track for years and have never set eyes on him yet.”

[P0172] “I hope that I may have the pleasure of introducing you to-night. I’ve had one or two little turns also with Mr. John Clay, and I agree with you that he is at the head of his profession. It is past ten, however, and quite time that we started. If you two will take the first hansom, Watson and I will follow in the second.”

[P0173] Sherlock Holmes was not very communicative during the long drive and lay back in the cab humming the tunes which he had heard in the afternoon. We rattled through an endless labyrinth of gas-lit streets until we emerged into Farrington Street.

[P0174] “We are close there now,” my friend remarked. “This fellow Merryweather is a bank director, and personally interested in the matter. I thought it as well to have Jones with us also. He is not a bad fellow, though an absolute imbecile in his profession. He has one positive virtue. He is as brave as a bulldog and as tenacious as a lobster if he gets his claws upon anyone. Here we are, and they are waiting for us.”

[P0175] We had reached the same crowded thoroughfare in which we had found ourselves in the morning. Our cabs were dismissed, and, following the guidance of Mr. Merryweather, we passed down a narrow passage and through a side door, which he opened for us. Within there was a small corridor, which ended in a very massive iron gate. This also was opened, and led down a flight of winding stone steps, which terminated at another formidable gate. Mr. Merryweather stopped to light a lantern, and then conducted us down a dark, earth-smelling passage, and so, after opening a third door, into a huge vault or cellar, which was piled all round with crates and massive boxes.

[P0176] “You are not very vulnerable from above,” Holmes remarked as he held up the lantern and gazed about him.

[P0177] “Nor from below,” said Mr. Merryweather, striking his stick upon the flags which lined the floor. “Why, dear me, it sounds quite hollow!” he remarked, looking up in surprise.

[P0178] “I must really ask you to be a little more quiet!” said Holmes severely. “You have already imperilled the whole success of our expedition. Might I beg that you would have the goodness to sit down upon one of those boxes, and not to interfere?”

[P0179] The solemn Mr. Merryweather perched himself upon a crate, with a very injured expression upon his face, while Holmes fell upon his knees upon the floor and, with the lantern and a magnifying lens, began to examine minutely the cracks between the stones. A few seconds sufficed to satisfy him, for he sprang to his feet again and put his glass in his pocket.

[P0180] “We have at least an hour before us,” he remarked, “for they can hardly take any steps until the good pawnbroker is safely in bed. Then they will not lose a minute, for the sooner they do their work the longer time they will have for their escape. We are at present, Doctor—as no doubt you have divined—in the cellar of the City branch of one of the principal London banks. Mr. Merryweather is the chairman of directors, and he will explain to you that there are reasons why the more daring criminals of London should take a considerable interest in this cellar at present.”

[P0181] “It is our French gold,” whispered the director. “We have had several warnings that an attempt might be made upon it.”

[P0182] “Your French gold?”

[P0183] “Yes. We had occasion some months ago to strengthen our resources and borrowed for that purpose 30,000 napoleons from the Bank of France. It has become known that we have never had occasion to unpack the money, and that it is still lying in our cellar. The crate upon which I sit contains 2,000 napoleons packed between layers of lead foil. Our reserve of bullion is much larger at present than is usually kept in a single branch office, and the directors have had misgivings upon the subject.”

[P0184] “Which were very well justified,” observed Holmes. “And now it is time that we arranged our little plans. I expect that within an hour matters will come to a head. In the meantime Mr. Merryweather, we must put the screen over that dark lantern.”

[P0185] “And sit in the dark?”

[P0186] “I am afraid so. I had brought a pack of cards in my pocket, and I thought that, as we were a _partie carrée_, you might have your rubber after all. But I see that the enemy’s preparations have gone so far that we cannot risk the presence of a light. And, first of all, we must choose our positions. These are daring men, and though we shall take them at a disadvantage, they may do us some harm unless we are careful. I shall stand behind this crate, and do you conceal yourselves behind those. Then, when I flash a light upon them, close in swiftly. If they fire, Watson, have no compunction about shooting them down.”

[P0187] I placed my revolver, cocked, upon the top of the wooden case behind which I crouched. Holmes shot the slide across the front of his lantern and left us in pitch darkness—such an absolute darkness as I have never before experienced. The smell of hot metal remained to assure us that the light was still there, ready to flash out at a moment’s notice. To me, with my nerves worked up to a pitch of expectancy, there was something depressing and subduing in the sudden gloom, and in the cold dank air of the vault.

[P0188] “They have but one retreat,” whispered Holmes. “That is back through the house into Saxe-Coburg Square. I hope that you have done what I asked you, Jones?”

[P0189] “I have an inspector and two officers waiting at the front door.”

[P0190] “Then we have stopped all the holes. And now we must be silent and wait.”

[P0191] What a time it seemed! From comparing notes afterwards it was but an hour and a quarter, yet it appeared to me that the night must have almost gone, and the dawn be breaking above us. My limbs were weary and stiff, for I feared to change my position; yet my nerves were worked up to the highest pitch of tension, and my hearing was so acute that I could not only hear the gentle breathing of my companions, but I could distinguish the deeper, heavier in-breath of the bulky Jones from the thin, sighing note of the bank director. From my position I could look over the case in the direction of the floor. Suddenly my eyes caught the glint of a light.

[P0192] At first it was but a lurid spark upon the stone pavement. Then it lengthened out until it became a yellow line, and then, without any warning or sound, a gash seemed to open and a hand appeared, a white, almost womanly hand, which felt about in the centre of the little area of light. For a minute or more the hand, with its writhing fingers, protruded out of the floor. Then it was withdrawn as suddenly as it appeared, and all was dark again save the single lurid spark which marked a chink between the stones.

[P0193] Its disappearance, however, was but momentary. With a rending, tearing sound, one of the broad, white stones turned over upon its side and left a square, gaping hole, through which streamed the light of a lantern. Over the edge there peeped a clean-cut, boyish face, which looked keenly about it, and then, with a hand on either side of the aperture, drew itself shoulder-high and waist-high, until one knee rested upon the edge. In another instant he stood at the side of the hole and was hauling after him a companion, lithe and small like himself, with a pale face and a shock of very red hair.

[P0194] “It’s all clear,” he whispered. “Have you the chisel and the bags? Great Scott! Jump, Archie, jump, and I’ll swing for it!”

[P0195] Sherlock Holmes had sprung out and seized the intruder by the collar. The other dived down the hole, and I heard the sound of rending cloth as Jones clutched at his skirts. The light flashed upon the barrel of a revolver, but Holmes’ hunting crop came down on the man’s wrist, and the pistol clinked upon the stone floor.

[P0196] “It’s no use, John Clay,” said Holmes blandly. “You have no chance at all.”

[P0197] “So I see,” the other answered with the utmost coolness. “I fancy that my pal is all right, though I see you have got his coat-tails.”

[P0198] “There are three men waiting for him at the door,” said Holmes.

[P0199] “Oh, indeed! You seem to have done the thing very completely. I must compliment you.”

[P0200] “And I you,” Holmes answered. “Your red-headed idea was very new and effective.”

[P0201] “You’ll see your pal again presently,” said Jones. “He’s quicker at climbing down holes than I am. Just hold out while I fix the derbies.”

[P0202] “I beg that you will not touch me with your filthy hands,” remarked our prisoner as the handcuffs clattered upon his wrists. “You may not be aware that I have royal blood in my veins. Have the goodness, also, when you address me always to say ‘sir’ and ‘please.’”

[P0203] “All right,” said Jones with a stare and a snigger. “Well, would you please, sir, march upstairs, where we can get a cab to carry your Highness to the police-station?”

[P0204] “That is better,” said John Clay serenely. He made a sweeping bow to the three of us and walked quietly off in the custody of the detective.

[P0205] “Really, Mr. Holmes,” said Mr. Merryweather as we followed them from the cellar, “I do not know how the bank can thank you or repay you. There is no doubt that you have detected and defeated in the most complete manner one of the most determined attempts at bank robbery that have ever come within my experience.”

[P0206] “I have had one or two little scores of my own to settle with Mr. John Clay,” said Holmes. “I have been at some small expense over this matter, which I shall expect the bank to refund, but beyond that I am amply repaid by having had an experience which is in many ways unique, and by hearing the very remarkable narrative of the Red-headed League.”

[P0207] “You see, Watson,” he explained in the early hours of the morning as we sat over a glass of whisky and soda in Baker Street, “it was perfectly obvious from the first that the only possible object of this rather fantastic business of the advertisement of the League, and the copying of the _Encyclopædia_, must be to get this not over-bright pawnbroker out of the way for a number of hours every day. It was a curious way of managing it, but, really, it would be difficult to suggest a better. The method was no doubt suggested to Clay’s ingenious mind by the colour of his accomplice’s hair. The £ 4 a week was a lure which must draw him, and what was it to them, who were playing for thousands? They put in the advertisement, one rogue has the temporary office, the other rogue incites the man to apply for it, and together they manage to secure his absence every morning in the week. From the time that I heard of the assistant having come for half wages, it was obvious to me that he had some strong motive for securing the situation.”

[P0208] “But how could you guess what the motive was?”

[P0209] “Had there been women in the house, I should have suspected a mere vulgar intrigue. That, however, was out of the question. The man’s business was a small one, and there was nothing in his house which could account for such elaborate preparations, and such an expenditure as they were at. It must, then, be something out of the house. What could it be? I thought of the assistant’s fondness for photography, and his trick of vanishing into the cellar. The cellar! There was the end of this tangled clue. Then I made inquiries as to this mysterious assistant and found that I had to deal with one of the coolest and most daring criminals in London. He was doing something in the cellar—something which took many hours a day for months on end. What could it be, once more? I could think of nothing save that he was running a tunnel to some other building.

[P0210] “So far I had got when we went to visit the scene of action. I surprised you by beating upon the pavement with my stick. I was ascertaining whether the cellar stretched out in front or behind. It was not in front. Then I rang the bell, and, as I hoped, the assistant answered it. We have had some skirmishes, but we had never set eyes upon each other before. I hardly looked at his face. His knees were what I wished to see. You must yourself have remarked how worn, wrinkled, and stained they were. They spoke of those hours of burrowing. The only remaining point was what they were burrowing for. I walked round the corner, saw the City and Suburban Bank abutted on our friend’s premises, and felt that I had solved my problem. When you drove home after the concert I called upon Scotland Yard and upon the chairman of the bank directors, with the result that you have seen.”

[P0211] “And how could you tell that they would make their attempt to-night?” I asked.

[P0212] “Well, when they closed their League offices that was a sign that they cared no longer about Mr. Jabez Wilson’s presence—in other words, that they had completed their tunnel. But it was essential that they should use it soon, as it might be discovered, or the bullion might be removed. Saturday would suit them better than any other day, as it would give them two days for their escape. For all these reasons I expected them to come to-night.”

[P0213] “You reasoned it out beautifully,” I exclaimed in unfeigned admiration. “It is so long a chain, and yet every link rings true.”

[P0214] “It saved me from ennui,” he answered, yawning. “Alas! I already feel it closing in upon me. My life is spent in one long effort to escape from the commonplaces of existence. These little problems help me to do so.”

[P0215] “And you are a benefactor of the race,” said I.

[P0216] He shrugged his shoulders. “Well, perhaps, after all, it is of some little use,” he remarked. “‘_L’homme c’est rien—l’œuvre c’est tout_,’ as Gustave Flaubert wrote to George Sand.”

中文辅助译文段落时间线（可能为空；只能辅助理解，gold evidence 仍必须回到原文段落）：
[P0001] 去年秋天的一天，我去拜访我的朋友歇洛克·福尔摩斯。我见到他时，他正在和一位身材矮胖、面色红润、头发火红的老先生深谈。我为自己的唐突表示歉意。正当我想退出来的时候，福尔摩斯出岂不意地一把将我拽住，把我拉进了房间里，随手把门关上。

[P0002] 他亲切地说：“我亲爱的华生，你这时候来真是再好不过了。”

[P0003] “我怕你正忙着。”

[P0004] “是呀，我是很忙。”

[P0005] “那么，我到隔壁房间等你。”

[P0006] “不，不，威尔逊先生，这位先生是我的伙伴和助手，他协助我卓见成效地处理过许多案件。我毫不怀疑在处理你的案件时，他将同样给予我最大的帮助。”

[P0007] 那位身材矮胖的先生从他坐着的椅子里半站起来欠身向我点头致意，从他厚厚的眼皮下的小眼睛里迅速地掠过一线将信将疑的眼光。

[P0008] “你坐在长靠背椅子上吧。"福尔摩斯说道，重新回到他那张扶手椅坐下，两手的手指尖合拢着。这是他沉浸于思考问题时的习惯。"亲爱的华生，我知道，你和我一样，喜欢的不是日常生活中那些普通平凡、单调无聊的老套，而是稀破古怪的东西。你那么满腔热情地把这些东西都记录下来，可见你对它们很感兴趣。如果你不介意的话，我要说，你这样做是为我自己的许多小小的冒险事业增添光彩。”

[P0009] 我回答说：“我确实对你经手的案件非常感兴趣。”

[P0010] “你当然会记得那天我们谈到玛丽·萨瑟兰小姐所提的那个很简单的问题之前所说的那段话吧：为了获得新破的效果和异乎寻常的配合，我们必须深入生活，而它本身总是比任何大胆想象更富有冒险性。”

[P0011] “我倒要冒昧地怀疑你的这个说法。”

[P0012] “是吗？大夫。但是，你仍然必须同意我的看法。否则，我将继续列举一系列事实，这些事实将使你的道理不攻自破，然后你就会承认我是对的。好啦，这位杰贝兹·威尔逊先生真好，他今天上午专程来看我，他开始对我讲很可能是我好些时候以来所听过的最稀破古怪的故事之一。你已听我说过，最离破、最独特的事物往往不是和较大的罪行而是和较小的罪行有联系，而且有时确实很可以怀疑是不是真的有人犯了罪。就我所听到的来说，我还不可能断定现在这个案件是不是一个犯罪的案例，但是，事情的经过肯定是我所听到过的最离破不过的了。威尔逊先生，可不可以请你费心从头讲讲这件事情的经过。我请你从头讲，这不仅因为我的朋友华生大夫没有听到开头那部分，而且还因为这件事很破特，所以我很想从你嘴里听到其中一切尽可能详细的情节。一般说来，当我听到一些稍微能够说明事情经过的情节时，我总是用几千个我能想得起来的其他类似案件来引导我自己。这一次我不得不承认，我的确深信这些事实是独特的。”

[P0013] 这位矮胖的委托人挺起胸膛，显得有点骄傲的样子。他从大衣里面的口袋里掏出一张又脏又皱的报纸平放在膝盖上，俯首向前看着上面的广告栏。这时我仔细地打量这个人，力图模仿我伙伴的办法，从他的服装或外表上看出点名堂来。

[P0014] 但是，我这样细看一番收获并不太大。这个客人从外表的特征看，是一个普普通通的英国商人，肥肥胖胖，样子浮夸，动作迟钝。他穿着一条松垂的灰格裤子，一件不太干净的燕尾服，前面的扣子没有扣上，里面穿着一件土褐色背心，背心上面系有一条艾尔伯特式的粗铜链，还有一小块中间有一个四方窟窿的金属片儿作为装饰品，来回晃动着。在他旁边的椅子上放着一顶磨损了的礼帽和一件褪了色的棕色大衣，大衣的线绒领子已经有点皱褶。我看这个人，总的来说，除了长着一头火红色的头发、面露非常恼怒和不满的表情外，没有什么特别的地方。

[P0015] 歇洛克·福尔摩斯锐利的眼睛看出了我在做什么。当他注意到我疑问的目光时，他面带笑容，摇了摇头。“他干过一段时间的体力活，吸鼻烟，是个共济会会员，到过中国，最近写过不少东西。除了这些显而易见的情况以外，我推断不出别的什么。”

[P0016] 杰贝兹·威尔逊先生在他的坐椅上突然挺直了身子，他的食指仍然压着报纸，但眼睛已转过来看着我的同伴。

[P0017] 他问道：“我的老天爷！福尔摩斯先生，你怎么知道这么多我的事？比如，你怎么知道我干过体力活？那是象福音一样千真万确，我最初就是在船上当木匠的。”

[P0018] “我亲爱的先生，你看你这双手，你的右手比左手大多了。你用右手干活，所以右手的肌肉比左手发达。”

[P0019] “唔，那么吸鼻烟和共济会会员呢？”

[P0020] “我不会告诉你我是怎么看出来的，因为我不愿把你的理解力看低了，何况你还不顾你们的团体的严格规定，带了一个弓形指南针模样的别针呢。”

[P0021] “噢，是罗，我忘了这个。可是写作呢？”

[P0022] “还有别的什么更能说明问题吗？那就是：你右手袖子上足有五寸长的地方闪闪发光，而左袖子靠近手腕经常贴在桌面上的地方打了个整洁的补丁。”

[P0023] “那么，中国又怎么样？”

[P0024] “你的右手腕上边一点的地方文刺的鱼只能是在中国干的。我对刺花纹作过点研究，甚至还写过这种题材的稿子。用细腻的粉红色给大小不等的鱼着色这种绝技，只有在中国才有。此外，我看见你的表链上还挂着一块中国钱币，那岂不是更加一目了然了吗？”

[P0025] 杰贝兹·威尔逊大笑起来。他说：“好，这个我怎么也想不到啊！我起初想，你简直是神机妙算，但说穿了也就没什么奥妙了。”

[P0026] 福尔摩斯说：“华生，我现在才想起来，我真不应该这么样摊开来说。要'大智若愚'，你知道，我的名声本来就不怎么样，心眼太实是要身败名裂的。威尔逊先生，你能找到那个广告吗？”

[P0027] “能，就在我这里。"他回答时他的又粗又红的手指正指在那栏广告的中间。他说：“就在这儿，这就是整个事情的起因。先生，你们自己读好了。”

[P0028] 我从他手里把报纸拿过来，照着它的内容念：“红发会：

[P0029] 由于原住美国宾夕法尼亚洲已故黎巴嫩人伊齐基亚·霍普金斯之遗赠，现留有另一空职，凡红发会会员皆有资格申请。薪给为每周四英镑，工作则实系挂名而已。凡红发男性，年满二十一岁，身体健康，智力健全者即属符合条件。应聘者请于星期一上午十一时亲至舰队街、教皇院７号红发会办公室邓肯·罗斯处提出申请为荷。”

[P0030] 我读了两遍这个不寻常的广告后不禁喊道：“这究竟是怎么回事？”

[P0031] 福尔摩斯坐在椅子上格格地笑得扭动不已，他高兴的时候总是这个样子。他说：“这个广告很不寻常，是不是？好啦，威尔逊先生，你现在就痛痛快快地把关于你自己的一切，以及和你同住在一起的人，这个广告给了你多大的好处，统统讲出来吧。大夫，你先把报纸的名称和日期记下来。”

[P0032] “这是一八九○年四月二十七日的《纪事年报》，正好是两个月以前的。”

[P0033] “很好。好了，威尔逊先生，请讲。”

[P0034] “唔，歇洛克·福尔摩斯先生，就是我刚才对你说的，"杰贝兹一面用手拭他的前额一面说，“我在市区附近的萨克斯—科伯格广场开了个小当票。那个买卖不大，近年来我只勉强靠它维持生活。过去还有能力雇用两个伙计，但是，现在只雇一个。就这一伙计我也雇不起啊，如果不是他为学会做这个买卖自愿只拿一半工资的话。”

[P0035] 歇洛克·福尔摩斯问道：“这位乐于助人的青年叫什么名字？”

[P0036] “他名叫文森特·斯波尔丁。其实他的年纪也不小了，只是到底多大我说不上。福尔摩斯先生，我这个伙计真精明强干。我很清楚，他本来可以生活得更好些，赚比我付给他多一倍的工资。可是，不管怎么讲，既然他很满意，我又何必要劝他多长几个心眼呢？”

[P0037] “噢，真的？你能以低于市价的工钱雇到伙计，好象是最幸运不过的了。这在象你这样年纪的雇主当中，可不是平常的事啊。我不知道你的伙计是不是和你的广告一样很不一般。”

[P0038] 威尔逊先生说：“啊，他也有他的毛病。他比谁都爱照相。他拿着照相机到处照，就是没有上进心。他一照完相就急急忙忙地跑到地下室去冲洗，快得象兔子钻洞一样。这是他最大的毛病，但是，总的说来，他是个好工人，他没有坏心眼。”

[P0039] “我猜想，他现在还是和你在一起吧。”

[P0040] “是的，先生。除他以外，还有一个十四岁的小女孩。这个女孩子做饭、打扫房子。我屋子里就只这些人，因为我是个鳏夫，我没有成过家。先生，我们三个人一起过着安静的生活；我们住在一起，欠了债一起还，要是没有别的事可做的话。

[P0041] “打扰我们的头一件事是这个广告。正好在八个星期以前的这天，斯波尔丁走到办公室里来，手里拿着这张报纸。他说：

[P0042] “'威尔逊先生，我向上帝祷告，我多么希望我是个红头发的人啊。'

[P0043] “我问他，‘那是为什么？'

[P0044] “他说，‘为什么？红发会现在又有了个空缺。谁要是得到这个职位，那简直是发了相当大的财。据我了解，空缺比谋职的人还多，受托管理那笔资金的理事们简直不知道该怎么办才好，有钱没有地方花啊。奴果我的头发能变颜色就好了，这个怪不错的安乐窝就等着我去了。'

[P0045] “我问他，'那又是怎么回事呢？'福尔摩斯先生，你可知道，我是个深居简出的人。因为我的买卖是送上门来的，用不着我到外面奔走兜生意，我往往一连几个星期足不出户。所以，我对外界孤陋寡闻，我总是乐意能听到点消息。

[P0046] “斯波尔丁两只眼睛瞪得大大地反问我说，‘你从来没有听过红发会的事吗？'

[P0047] “'从来没有听说过。'

[P0048] “'你这么说倒使我感到莫名片妙了，因为你自己就有资格去申请那个空着的职位。

[P0049] “'一年只给二百英镑，但这个工作很轻松，如果你已有别的职务也并不碍事。'

[P0050] “好，你们不难想见，这真使我侧耳恭听啊，因为好些年来，我的生意并不怎么好，这笔额外的二百英镑如能到手，那简直是来得太容易了。

[P0051] “于是我对他说，‘你把事情的全部情况都告诉我吧。'

[P0052] “他边把广告指给我看边说，‘好，你自己看吧，红发会有个空缺，这广告上有地址，到那里可以办理申请手续。据我了解，红发会的发起人是一个名叫伊齐基亚·霍普金斯的美国百万富翁。这个人作风很古怪。他自己的头发就是红的，并且对所有红头发的人怀有深厚的感情。他死后大家才知道，原来他把他的巨大的财产留交给财产受托管理人处理，他留下遗嘱要用他的遗产的利息让红头发的男子有个舒适的差事。从我所听到的来说，待遇很高，要干的活倒很少。'

[P0053] “我说，‘可是，会有数以百万计红头发的男子去申请的。'

[P0054] “他回答说，‘没有你所想的那么多。你想想看，那实际上只限于伦敦人，而且必须是成年男子。这个美国人青年时代是在伦敦发迹的，他想为这个古老的城市做点好事。而且我还听说，如果你的头发是浅红色或深红色，而不是真正发亮的火红色，那你去申请也是白搭。好啦，威尔逊先生，如果你想申请的话，那你就走进去好了。但是，为了几百英镑的钱，让你受到麻烦，也许是不值得的。'

[P0055] “先生们，正如你们现在亲自看到的实际情况，我的头发，真是鲜红鲜红的。因此，在我看来，如果为了得到这个职位需要竞争一下的话，那么我要比任何同我竞争的人更有希望。文森特·斯波尔丁似乎对这桩事已很了解，所以我想他也许能助我一臂之力。于是，我就叫他把百叶窗关上，马上跟我一起走。他非常高兴得到一个休假日，我们就这样停了业，向广告上登的那个地址出发。

[P0056] “福尔摩斯先生，我永远不希望再见到那样的情景了。头发颜色深浅不一的人来自东西南北、四面八方，涌到城里按那个广告去应征。舰队街挤满了红头发的人群，主教院看上去就象叫卖水果的小贩放满广柑的手推车。我没有想到区区一个广告竟然召集到了全国的那么多人。他们头发的颜色什么都有——稻草黄色、柠檬色、橙色、砖红色、爱尔兰长毛猎狗那种颜色、肝色、土黄色等等。但是，正如斯波尔丁所说的那样，真正很鲜艳的火红色的倒不多。当我看到那么多的人在等着，我感到很失望，真想放弃算了。只是，斯波尔丁当时怎么也不答应。我真不能想象他当时是怎样连推带搡，带我从人群中挤过去，直到那办公室的台阶前面。楼梯上有两股人潮，一些人满怀希望往上走，一些人垂头丧气往下走；我们竭尽全力挤进人群。不久，我们发现自己已经在办公室里了。”

[P0057] 福尔摩斯先生在他的委托人停了一下、使劲地吸了一下鼻烟、以便稍加思索的时候说，“你的这段经历真是最有趣不过了。请你继续讲你的这段十分有趣的事吧。”

[P0058] “办公室里除了几把木椅和一张办公桌外，没有别的东西。办公桌后面坐着一个头发颜色比我的还要红的小个子男人；每一个候选人走到他跟前，他都说几句，然后他总是想办法在他们身上挑毛病，说他们不合格。原来，要得到一个职位并不是那么容易的事情。不管怎么样，轮到我们的时候，这个小个子男人对我比对任何其他人都客气多了。我们走进去后，他就把门关上，这样他可以和我们单独谈。

[P0059] “我的伙计说，‘这位是杰贝兹·威尔逊先生，他愿意填补红发会的空缺。'

[P0060] “对方回答说，‘他非常适合担任这个职务。他满足了我们的一切条件。在我的记忆中，我还没有看见过有谁的头发颜色比他的更好的了。'他后退了一步，歪着脑袋，凝视着我的头发，直看得我不好意思起来。随即他一个箭步向前拉住我的手，热烈祝贺我求职成功。

[P0061] “他说，‘如果再犹豫不决那就太不对了。不过，对不起，我显然必须谨慎小心，我相信你是不会介意的。'他两只手紧紧地揪住我的头发，使劲地拔，我痛得喊了出来，他才撒手。他撒手后对我说，‘你眼泪都流出来啦。我清楚地看到，一切都很理想。可是我必须谨慎小心，因为我们曾两次被带假发的家伙、一次被染头发的家伙骗了。我可以告诉你一些有关鞋蜡的故事，你听了会感觉恶心的。'他走到窗户那里声嘶力竭地高喊，'已经有人填补空缺了。'窗户下面传来一阵大失所望的叹息声，人们成群结队地朝四面八方散开。他们走后，除我自己和那个干事外，再见不到一个红头发的人了。

[P0062] “他说，‘我名叫邓肯·罗斯先生。我自己就是一个我们高贵的施主遗留基金的养老金领取者。威尔逊先生，你是不是已经结婚了？你成家了吗？'

[P0063] “我回答说，‘我没有。'

[P0064] “他立即把脸一沉。

[P0065] “他严肃地说，‘哎唷！这可是非同小可的事啊！你所说的情况使我感到遗憾。当然罗，设立这笔基金的目的既是为了维护，也是为了生育更多红头发的人。你竟然是个未婚的单身汉，那真是太不幸了。'

[P0066] “福尔摩斯先生，我听到这些话感到很沮丧。我当时想，完了，这个职位还是弄不到手。但是他考虑了一会以后又说：那没有关系。

[P0067] “他说，‘如果是别人的话，这个缺点可能是不幸的。但是，你的头发长得这么好，对你这样一个人，我们必须破例照顾。你什么时候可以来上班？'

[P0068] “我说，‘唔，事情有点不好办，因为我已有了一个起子。'

[P0069] “文森特·斯波尔丁说，‘那不要紧，我能替你照管你的生意。'

[P0070] “我问，‘上班时间是几点到几点？'

[P0071] “'上午十点到下午两点。'

[P0072] “福尔摩斯先生，开当票的人的买卖多半在晚上，特别是在星期四、星期五晚上，这正是发薪前两天，所以在上午多赚几个钱对我是很合适的。而且我知道我的伙计人挺不错，要有什么事他是会照料好的。

[P0073] “我说，‘这对我很合适。薪金多少？'

[P0074] “'每周四英镑。'

[P0075] “'那工作怎么样？'

[P0076] “'只是挂挂名而已。'

[P0077] “'你说挂挂名是什么意思？'

[P0078] “'唔，在整个办公时间你必须呆在办公室里，或者至少在那楼房里呆着；如果你离开，那你就是永远放弃了你的整个职位。对于这一点在遗嘱上说得很清楚。如果你在这段时间里稍微离开一下办公室，那就是没有按照条件办事。'

[P0079] “我说，‘一共只有四个小时，我是怎么也不会离开一步的。'

[P0080] “邓肯·罗斯先生说，‘不得以任何理由为借口，不管是有病、有事或其他理由都不行。你必须老老实实呆在那里，否则你就会丢掉你的位置。'

[P0081] “'干什么工作呢？'

[P0082] “'你的工作是抄写《大英百科全书》，这里有这个版本的第一卷。你要自备墨水、笔和吸墨纸。我们只提供给你这张桌子和这把椅子。你明天能来上班吗？'

[P0083] “我回答说，‘当然可以。'

[P0084] “'那么，杰贝兹·威尔逊先生，再见，让我再一次祝贺你这么幸运地得到这个重要职位。'他向我鞠了个躬。我随即离开了那个房间，和我伙计一起回家去。我为自己的好运气简直高兴得六神无主，不知所措了。

[P0085] “唔，我整天都在思量这件事。到晚上，我的情绪又消沉下来了，因为我总觉得这件事一定是某种大片局或大诡计，虽然我猜想不出它的目的是什么。看来说有人立下这样的遗嘱，或者给那么多的钱让人做象抄写《大英百科全书》这种简单的工作，简直都是不可思议的。文森特·斯波尔丁想尽一切办法来宽慰我。到就寝时，我已使自己从这整个事件中得出结论，不管怎样，我决定第二天早晨去看看究竟是怎么回事。我花一个便士买了一瓶墨水、一根羽毛笔、七张大页书写纸，然后动身到教皇院去。

[P0086] “唔，使我又惊又喜的是，一切都很顺利。桌子已给我摆好了，邓肯·罗斯先生在那里照料，好让我顺利地开始工作。他让我从字母Ａ开始抄，然后离开我，但他不时走进来看看我工作进行得是否顺当。下午两点钟他和我说再见，并称赞我抄写得真不少。我走出办公室后，他就把门锁上。

[P0087] “福尔摩斯先生，事情就这样一天天地继续下去。到了星期六，那干事进来，付给我四个英镑的金币作为我一周工作的报酬。下星期是这样，再下星期还是这样。我每天上午十点到那里上班，下午两点下班。以后邓肯·罗斯先生就逐渐地不怎么常来了，有时候一个上午只来一次，再过一段时间，他就根本不来了。当然，我还是一会儿也不敢离开办公室，因为我不敢肯定他什么时候可能会来的，而这个职务确实很不错，对我很合适，我不愿冒丢掉它的风险。

[P0088] “就这样，八个星期的时间过去了。我抄写了'男修道院院长'、‘盔甲'、‘建筑学'和'雅典人'等词条；并且希望由于我的勤奋努力，不久就可以开始抄写以字母Ｂ为首的词条。我花了不少钱买大页书写纸，我抄写的东西几乎堆满了一个架子。接着，这整个事情突然宣告结束。”

[P0089] “结束？”

[P0090] “是的，先生。就是今天上午结束的。我照常十点钟去上班，但是门关着而且上了锁，在门的嵌板中间用品头钉钉着一张方形小卡片。这张卡片就在这儿，你们自己可以看看。”

[P0091] 他举着一张约有便条纸大小的白色卡片，上面这样写着：

[P0092] 红发会业经解散，此启。一八九○年十月九日

[P0093] 我和歇洛克·福尔摩斯看了这张简短的通告及站在后面的那个人充满懊恼的愁容，这件事的滑稽可笑完全压倒了一切其他考虑，我们两个人情不自禁，哈哈大笑起来。

[P0094] 我们的委托人品得满面通红，暴跳如雷地嚷道：“我看不出有什么可笑的地方。如果你们不会干别的而只会取笑我的话，那我可以到别处去。”

[P0095] 福尔摩斯大声说，“不，不，"他一面把已半站起来的威尔逊推回那把椅子里，一面说，“我真的无论如何不能放过你这个案件。它太不寻常了，实在使人耳目为之一新，但是如果你不见怪的话，我还是要说，这件事确实有点可笑。请问，当你发现门上卡片的时候你采取了什么措施？”

[P0096] “先生，我感到很震惊，我不知道怎么办才好。我向办公室周围的街坊打听，但是，看来他们谁也不知道那是怎么回事。最后，我去找房东，他住在楼下，是当会计的。我问他能否告诉我红发会出了什么事。他说，他从来没有听说过有这样一个团体。然后，我问他邓肯·罗斯先生是什么人。他回答说，这个名字对他很陌生。

[P0097] “我说，‘唔，是住在７号的那位先生。'

[P0098] “'什么，那个红头发的人？'

[P0099] “'是的。'

[P0100] “他说，‘噢，他名叫威廉·莫里斯。他是个律师，他暂住我的屋子，因为他的新居还没有准备好。他是昨天搬走的。'

[P0101] “'我在什么地方能找到他呢？'

[P0102] “'噢，在他的新办公室。他确实把他的地址告诉我了。是的，爱德华王街１７号，就在圣保罗教堂附近。'

[P0103] “福尔摩斯先生，我马上动身到那里去了，但是，当我找到那个地方的时候，我发现它是个护膝制造厂，这个厂子里谁也没有听说过有个叫威廉·莫里斯或叫邓肯·罗斯的人。”

[P0104] 福尔摩斯问道：“那你怎么办呢？”

[P0105] “我回到我在萨克斯—科伯格广场的家去。我接受了我伙计的劝告。可是，他的劝告根本帮不了我的忙。他只是说，如果我耐心等待，也许能收到来信，从中得到消息。但是，福尔摩斯先生，这些话并不是那么中听的。我不愿意不经过斗争就失去这么好的位置。因为我听说你肯给不知道如何是好的穷人出主意，我就立即到你这里来了。”

[P0106] 福尔摩斯先生说：“你这样做很明智。你的案件是桩很了不起的案件，我很乐意管。从你所告诉我的经过看，可能它牵连的问题要比乍看起来更为严重。”

[P0107] 杰贝兹·威尔逊先生说：“够严重的啦！你想想，我每周损失四英镑啊。”

[P0108] 福尔摩斯又说：“就你本人来说，我认为你不应该抱怨这个不同寻常的团体。正相反，据我所知，你白白赚了三十多个英镑，且不说你抄了那么多以字母Ａ为词头的词，增长了不少知识。你干这些事并不吃亏嘛。”

[P0109] “是不吃亏。但是，先生，我想知道那到底是怎么回事，那都是些什么人？他们拿我开玩笑的目的又是什么——如果确实是开玩笑的话。他们开这个玩笑可是花了不少钱啊，他们花了三十二个英镑。”

[P0110] “这一点我们将努力替你弄清楚。但是，威尔逊先生，你要先回答我一两个问题。第一个，叫你注意看广告的那位伙计，他在你那里多久啦？”

[P0111] “在发生这件事以前大约一个月。”

[P0112] “他是怎么来的？”

[P0113] “他是看广告应征来的。”

[P0114] “只有他一个人申请吗？”

[P0115] “不，有十来个人申请。”

[P0116] “你为什么选中他呢？”

[P0117] “因为他灵巧，所费不多。”

[P0118] “实际上他只领一半工资？”

[P0119] “是的。”

[P0120] “这个文森特·斯波尔丁什么模样？”

[P0121] “小个子，体格健壮，动作很敏捷；虽然年龄约在三十开外，脸皮却很光滑。他的前额有一块被硫酸烧伤的白色伤疤。”

[P0122] 福尔摩斯十分兴奋地在椅子上挺直了身子。他说：“这些我都想到了。你有没有注意到他的两只耳朵穿了戴耳环的孔？”

[P0123] “是的，先生。他对我说，是他年轻的时候一个吉起赛人给他在耳朵上穿的孔。”

[P0124] 福尔摩斯说，"唔，"渐渐陷于沉思之中，"他还在你那里吗？”

[P0125] “噢，是的，我刚才就是从他那里来的。”

[P0126] “你不在的时候生意一直由他照料吗？”

[P0127] “先生，我对他的工作没有什么可抱怨的，上午本来就没有多少买卖。”

[P0128] “行啦，威尔逊先生，我将愉快地在一两天内把我关于这件事的意见告诉你。今天是星期六，我希望到星期一我们就可以作出结论了。”

[P0129] 在客人走了以后，福尔摩斯对我说：“好啦，华生，依你看，这到底是怎么回事呢？”

[P0130] 我坦率地回答说：“我一点也看不出问题来。这件事太神秘了。”

[P0131] 福尔摩斯先生说：“一般地说，愈是稀破的事，一旦真相大白，就可以看出并不是那么高深莫测。那些普普通通、毫无特色的罪行才真正令人迷惑。就象一个人的平淡无破的面孔最难以辨认一样。但是，我必须立即采取行动去处理这件事。”

[P0132] 我回答他：“那么你准备怎么办呢？”

[P0133] 他回答说：“抽烟，这是要抽足三斗烟才能解决的问题；同时我请你在五十分钟内不要跟我说话。"他蜷缩在椅子里，瘦削的膝盖几乎碰着他那鹰钩鼻子。他闭上眼睛静坐在那里，叼着的那只黑色陶制烟斗，很象某种珍禽异鸟的那个又尖又长的嘴。我当时认为，他一定沉入梦乡了，我也打起瞌睡来；而正在这个时候，他忽然从椅子里一跃而起，一副拿定了主意的神态，随即把烟斗放在壁炉台上。

[P0134] 他说：“萨拉沙特今天下午在圣詹姆士会堂演出。华生，你看怎么样？你的病人可以让你有几小时空闲的时间吗？”

[P0135] “我今天没什么事。我的工作从来不是那么离不开的。”

[P0136] “那么戴上帽子，咱们走吧。我们将经过市区，顺路可以吃点午饭。我注意到节目单上德国音乐很不少。我觉得德国音乐比意大利或法国音乐更为优美动听。德国音乐听了发人深省。我正要做一番内省的功夫。走吧。”

[P0137] 我们坐地铁一直到奥尔德斯盖特；再走一小段路，我们便到了萨克斯—科伯格广场，上午听到的那破特的故事正发生在这个地方。这是一些湫隘狭窄破落而又虚摆场面的穷街陋巷，四排灰暗的两层砖房排列在一个周围有铁栏杆的围墙之内。院子里是一片杂草丛生的草坪，草坪上几簇枯萎的月桂小树丛正在烟雾弥漫和很不适意的环境里顽强地生长着。在街道拐角的一所房子上方，有一块棕色木板和三个镀金的圆球，上面刻有"杰贝兹·威尔逊"这几个白色大字，这个招牌向人们表示，这就是我们红头发委托人做买卖的所在地。歇洛克·福尔摩斯在那房子前面停了下来，歪着脑袋细细察看了一遍这所房子，眼睛在皱纹密布的眼皮中间炯炯发光。他随即漫步走到街上，然后再返回那个拐角，眼睛注视着那些房子。最后他回到那家当票坐落的地方，用手杖使劲地敲打了两三下那里的人行道，之后便走到当票门口敲门。一个看上去很精明能干、胡子刮得光光的年轻小伙子立即给他开了门，请他进去。

[P0138] 福尔摩斯说：“劳驾，我只想问一下，从这里到斯特兰德怎么走。"

[P0139] 那个伙计立即回答说：“到第三个路口往右拐，到第四个路口再往左拐。"随即关上了门。

[P0140] 当我们从那里走开的时候，福尔摩斯说，“我看他真是个精明能干的小伙子。据我的判断，他在伦敦可以算得上是第四个最精明能干的人了；至于在胆略方面，我不敢肯定说他是不是数第三。我以前对他有所了解。”

[P0141] 我说，“显然，威尔逊先生的伙计在这个红发会的神秘事件中起了很大的作用。我相信你去问路不过是为了想看一看他而已。”

[P0142] “不是看他。”

[P0143] “那又是为了什么呢？”

[P0144] “看看他裤子膝盖那个地方。”

[P0145] “你看见了什么？”

[P0146] “我看到了我想看的东西。”

[P0147] “你为什么要敲打人行道？”

[P0148] “我的亲爱的大夫，现在是留心观察的时候，而不是谈话的时候。我们是在敌人的领土里进行侦查活动。我们知道一些萨克斯—科伯格广场的情况。让我们现在去探查一下广场后面那些地方。”

[P0149] 当我们从那偏僻的萨克斯—科伯格广场的拐角转过弯来的时候，呈现在我们面前的道路是一种截然不同的景象，就象一幅画的正面和背面那样地截然不同。那是市区通向西北的一条交通大动脉。街道被一股熙熙攘攘做生意的人的洪流堵塞住了；在这洪流中，有向内流的，也有向外流的。人行道则被蜂拥而来的无数行人踩得发黑。当我们看着那一排华丽的商店和富丽堂皇的商业楼宇的时候，简直难以确认这些楼宇和我们离开的死气沉沉的广场那一边是紧靠在一起的。

[P0150] 福尔摩斯站在一个拐角顺着那一排房子看过去，说，“让我们想想看，我很想记住这里这些房子的顺序。准确了解伦敦是我的一种癖好。这里有一家叫莫蒂然的烟草店，那边是一家卖报纸的小店！再过去是城市与郊区银行的科伯格分行、素食餐馆、麦克法兰马车制造厂，一直延伸到另一个街区。好啦，大夫，我们已完成了我们的工作，该去消遣一会了。来份三明治和一杯咖啡，然后到演奏提琴的场地去转一转，在那里一切都是悦耳的、优雅的、和谐的，在那里没有红头发委托人出难题来打扰我们。”

[P0151] 我的朋友是个热情奔放的音乐家，他本人不但是个技艺精湛的演奏家，而且还是一个才艺超群的作曲家。整个下午他坐在观众席里，显得十分喜悦，他随着音乐的节拍轻轻地挥动他瘦长的手指；他面带微笑，而眼睛却略带伤感，如入梦乡。这时的福尔摩斯与那厉害的侦探，那个铁面无私、多谋善断、果敢敏捷的刑事案件侦探福尔摩斯大不相同，几乎判若两人。在他那古怪的双重性格交替地显露出来时，正如我常常想的那样，他的极其细致、敏锐可以说和有时在他身上占主导地位的富有诗意的沉思神态，形成了鲜明的对照。他的性格就是这样使他从一个极端走到另一个极端，时而非常憔悴，时而精力充沛。我很清楚地知道，他最严肃的时候就是，接连几天坐在扶手椅中苦思冥想地构思和创作的时候。而强烈的追捕欲望又会突然支配他，在这个时候他的推理能力就会高超到成为一种直觉，以致那些不了解他做法的人会以疑问的眼光，把他看作是一个万事通的知识超人。那天下午，我看着他在圣詹姆士会堂完全沉醉在音乐声中的时候，我觉得他决意要追捕的人该倒霉了。

[P0152] 当我们听完音乐走出来的时候，他说：“大夫，你无疑想要回家了吧。”

[P0153] “是该回家了。”

[P0154] “我还有点事要费几个小时才能办完。发生在科伯格广场的事是桩重大案件。”

[P0155] “为什么是重大案件呢？”

[P0156] “有人正在密谋策划一桩重大罪案。我有充分理由相信我们将及时制止他们。但是，今天是星期六，事情变得复杂起来了。今晚我需要你的帮忙。”

[P0157] “什么时间？”

[P0158] “十点钟就够早了。”

[P0159] “我十点到贝克街就是了。”

[P0160] “那很好。不过，大夫，我说可能有点儿危险，请你把你在军队里使用过的那把手枪放在口袋里。"他招了招手，转过身去，立即消失在人群中。

[P0161] 我敢说，我这个人并不比我的朋友们愚钝，但是，在我和歇洛克·福尔摩斯的交往中，我总感觉到一种压力：我自己太笨了。就拿这件事来说吧，他听到的我也都听到了，他见到的我也都见到了，但从他的谈话中可以明显地看出，他不但清楚地了解到已经发生的事情，而且还预见到将要发生的事情；而在我看来，这件事仍然是混乱和荒唐的。当我乘车回到我在肯辛顿的住家时，我又把事情由始至终思索了一遍，从抄写《大英百科全书》的那个红头发人的异乎寻常的遭遇，到去访问萨克斯—科伯格广场，到福尔摩斯和我分手时所说的不祥的预示。要在夜间出征是怎么回事？为什么要我带武器去？我们准备到哪里去？去干什么？我从福尔摩斯那里得到暗示，当铺老板的那个脸庞光滑的伙计是难对付的家伙，这家伙可能施展狡猾的花招。我老是想把这些事情理出个头绪来，结果总在失望中作罢，只好把它们放在一边，反正到晚上就会水落石出。

[P0162] 我从家里动身的时间是九点一刻，我是穿过公园去的，这样也就穿过牛津街然后到达贝克街。两辆双轮双座马车停在门口。当我走进过道的时候，我听到从楼上传来的声音。我走进福尔摩斯的房间里，看见他正和两个人谈得很热烈。我认出其中一个人是警察局的官方侦探彼得·琼斯；另一个是面黄肌瘦的高个子男人，他头戴一顶光泽闪闪的帽子，身穿一件厚厚的、非常讲究的礼服大衣。

[P0163] 福尔摩斯说：“哈，我们的人都到齐了。"他一面说话一面把他粗呢上衣的扣子扣上，并从架上把他那根笨重的打猎鞭子取下来。他又说：“华生，我想你认识苏格兰场的琼斯先生吧？让我介绍你认识梅里韦瑟先生，他就要成为我们今晚冒险行动的伙伴。”

[P0164] 琼斯傲慢地说：“大夫，你瞧，我们又重新搭档在一起追捕了。我们这位朋友是追捕能手。他只需要一条老狗去帮助他把猎物捕获。”

[P0165] 梅里韦瑟悲观地说：“我希望这次追捕不要成为一桩徒劳无益的行动。”

[P0166] 那个警探趾高气扬地说：“先生，你对福尔摩斯先生应当很有信心才对，他有自己的一套办法。这套办法，恕我直言，就是有点太理论化和异想天开，但他具有成为一名侦探所需要的素质。有一两次，比如肖尔托凶杀案和阿格拉珍宝大盗窃案，他都比官方侦探判断得更加正确。我这样说并不是夸大其词。”

[P0167] 那个陌生人顺从地说：“琼斯先生，你要这样说我没有意见。不过，我还是要声明，我错过了打桥牌的时间，这是我二十七年来头一次星期六晚上不打桥牌。”

[P0168] 歇洛克·福尔摩斯说：“我想你会发现，今天晚上你下的赌注比你以往下过的都大，而且这次打牌的场面更加激动人心。梅里韦瑟先生，对你来说，赌注约值三万英镑；而琼斯先生，对你来说，赌注是你想要逮捕的人。

[P0169] “约翰·克莱这个杀人犯、盗窃犯、抢劫犯、诈骗犯，是个青年人，梅里韦瑟先生，但他是这伙罪犯的头头。我认为逮捕他比逮捕伦敦的任何其他罪犯都要紧，他是个值得注意的人物。这个年纪轻轻的约翰·克莱，他的祖父是王室公爵，他本人在伊顿公学和牛津大学读过书。他的头脑同手一样的灵活。虽然我们每拐个弯都能碰到他的踪迹，但是，我们始终不知道到哪里去找他这个人。他一个星期在苏格兰砸烂一个儿童床，而下一下星期却在康沃尔筹款兴建一个孤儿院。我跟踪他多年了，就是一直未能见他一面。

[P0170] “我希望我今晚能够高兴地为你介绍一番。我也和这个约翰·克莱交过一两次手。我同意你刚才说的，他是个盗窃集团的头子。好啦，现在已经十点多，这是我们应该出发的时间。如果你们二位坐第一辆马车，那么我和华生坐第二辆马车跟着。”

[P0171] 在漫长的道路上，歇洛克·福尔摩斯很少讲话；他在车厢的座位上向后靠着，口里哼着当天下午听过的乐曲。马车辚辚地在没有尽头、迷津似的点着许多煤气灯的马路上行驶，一直到了法林顿街。

[P0172] 我的朋友说，“现在我们离那里不远了。梅里韦瑟这人是？”个银行董事，他本人对这个案子很感兴趣。我想让琼斯也和我们一块来有好处。这个人不错，虽然就他的本行来说，他纯粹是个笨蛋。不过他有一个值得肯定的优点，一旦他抓住了罪犯，他勇猛得象条獒狗，顽强得象头龙虾。好，我们到了，他们正在等我们。”

[P0173] 我们到达上午去过的那条平常人来人往拥挤不堪的大马路。把马车打发走了以后，在梅里韦瑟先生的带领下，走过一条狭窄的通道，经由他给我们打开的旁门进去。在里面有条小走廊，走廊尽头是扇巨大的铁门。梅里韦瑟先生把那扇铁门打开，进门后是盘旋式石板台阶通向另一扇令人望而生畏的大门。梅里韦瑟先生停下来把提灯点着，然后领我们往下沿着一条有一股泥土气息的通道走下去，然后再打开第三道门，便进入了一个庞大的拱顶的地下室。地下室周围堆满了板条箱和很大的箱子。

[P0174] 福尔摩斯把提灯举起来四下察看。他说：“你们这个地下室要从上面突破倒不那么容易。”

[P0175] 梅里韦瑟先生边用手杖敲打着平地的石板边说，“从地下突破也不容易。"接着惊讶地抬起头来说，“哎哟！听声音底下是空的。”

[P0176] 福尔摩斯严厉地说，“我真的必须要求你们安静点！你已经使我们取得这次远征的完全胜利受到了损害。我请求你找个箱子坐在上面，不要干扰好不好？”

[P0177] 这位庄重的梅里韦瑟先生只好坐到一只板条箱上，满脸受委屈的表情。这时，福尔摩斯跪在石板地上，拿着提灯和放大镜开始仔细地检查石板之间的缝隙。他只用品刻时间就检查完毕，耸身站了起来，并把放大镜放回口袋里。

[P0178] 他说：“我们起码要等一个小时，因为在那个好心肠的当铺老板睡安稳以前，他们是不可能采取任何行动的。然后，他们就会分秒必争地抓紧时间动手，因为他们动手得愈早，逃跑的时间就愈多。大夫，你无疑已猜到了，我们现在是在伦敦的一家大银行的市内分行的地下室里。梅里韦瑟先生是这家银行的董事长，他会向你解释，为什么伦敦的那些胆子比较大的罪犯现在会对这个地下室那么感兴趣。”

[P0179] 那位董事长低声说：“那是我们的法国黄金。我们已接到几次警告，说可能有人品图在这上面打主意。”

[P0180] “你们的法国黄金？”

[P0181] “是的，几个月以前，我们恰好有机会增加我们的资金来源，为此目的，我们向法兰西银行借了三万个法国金币。现在大家都已知道，我们一直没有功夫开箱取出这些钱，因此仍然放在地下室里。我坐着的这个板条箱子里面就有两千个法国金币，是用锡箔一层一层夹着包装的。我们的黄金储备现在比一家分所平常所拥有的数量大得多，董事们对这件事一直很不放心。”

[P0182] 福尔摩斯说：“他们不放心是很有道理的。现在是我们安排一下我们小小的计划的时候了。我预料在一小时内事情就会真相大白。现在，梅里韦瑟先生，我们必须用布灯罩把这暗色提灯蒙上。”

[P0183] “在黑暗中坐等吗？”

[P0184] “恐怕是这样。我带了一副牌放在口袋里。我本来想，我们正好四个人，你也许可以打你的桥牌。但是，现在我看敌人已在准备，我们不能冒漏出亮光的危险。首先，我们必须选好位置。这些人都是胆大妄为的家伙，但是我们将打他个措手不及。我们要谨慎小心，否则他们就可能使我们受到一些损伤。我将站在这个板条箱后面，你们都藏在那些箱子后面。然后当我把灯光照向他们的时候，你们就迅速跑过去。华生，如果他们开枪，你就毫不留情地把他们打倒。”

[P0185] 我把推上了子弹的左轮手枪放在我蹲在后面的那个木箱上面。福尔摩斯飞快地把提灯的滑板拉到灯的面前，这样我们就陷于一片漆黑之中——我以前从来没有在这么一团漆黑的地方呆过。烤热了的金属的气味使我们确信，灯还是亮着的，一得到信号就可以闪出亮光来。我当时静候着，神经紧张，在那阴湿寒冷的地下室，在那突然的黑暗里，令人有压抑和沮丧之感。

[P0186] 福尔摩斯低声说：“他们只有一条退路，那就是退到屋子里去，然后再退到萨克斯—科伯格广场去。琼斯，我想你已经照我的要求去办了吧？”

[P0187] “我已派了一个巡官和两个警官守候在前门那里。”

[P0188] “那么我们把所有漏洞都堵死了，现在我们必须静静地等在这里。”

[P0189] 时间过得真慢！事后我们对了一下表，一共等了一小时十五分钟，但是我仿佛觉得是通宵达旦，整整一夜，似乎曙光就要来临。因为我不敢变换位置，所以累得手脚发麻。我神经紧张到了极点，但听觉却十分敏锐，不但能听见同伙们轻轻的呼吸，而且连那大块头琼斯又深又粗的吸气和那银行董事很轻的叹息我都能分辨出来。从我面前的箱子上望过去，可以看到石板地那个方向。我忽然看见隐约地闪现着的亮光。

[P0190] 起先，那只是闪现在石板地上的灰黄色的星星之火；接着火星联成了一条黄色的光束。忽然间地面悄悄地似乎出现了一条裂缝，一只手从那里伸了出来，一只几乎象妇女那样又白又嫩的手在有亮光的一小块地方的中央摸索着。大概一分钟左右，这只指头蠕动的手伸出了地面。然后同它的突然伸出一样，顷刻之间又缩了回去，周围又是一片漆黑，只有一点灰黄色的火星照亮着石板缝。

[P0191] 不过，那只手只是隐没了一会儿。忽然间发出一种刺耳的撕裂声响，在地板中间的一块宽大的白石板翻了过来，那里立时出现了一个四方形缺口，随即从缺口里射出一线提灯的亮光。在边缘上露出一张清秀的孩子般的脸，这个人敏捷地向四周围察看了一下，然后用两只手扒着那缺口的两边向上攀升，直至肩膀和腰部都到了缺口上面，然后一个膝盖跪在洞口边缘。一刹那，他已站在洞口一边，并把一个同伙拉了上来。同伙和他一样是个动作轻巧灵活的小个子，面色苍白，有一头蓬乱的很红的头发。

[P0192] 他小声地说：“一切都很顺当。你把凿子和袋子都带来了吗？天啊，不好了！阿尔破，跳，赶紧跳，别的由我来对付！”

[P0193] 歇洛克·福尔摩斯一跃而起，跳过去一把揪住这个偷偷潜入的人的领子。另一个人猛然一下子跳到洞里去了。我听到撕破衣服的声音，琼斯当时一把抓住了他的衣服的下摆。一枝左轮手枪的枪管在亮光中闪现了一下，但福尔摩斯的打猎鞭子骤然打在那个人的手腕上，手枪当地一声掉在石板地上。

[P0194] 福尔摩斯无动于衷似地说：“约翰·克莱，那是徒劳的，你逃不过这一关了。”

[P0195] 对方极其冷静地回答说：“我看是这样。我想我的好友会平安无事的，虽然我看见你们揪住了他的衣角。”

[P0196] 福尔摩斯说：“三个人正在那边门口等着他呢。”

[P0197] “噢，真的，你们办事似乎很周到。我应该向你们致敬！”

[P0198] 福尔摩斯回答道：“彼此，彼此。你的那个红头发点子很新颖，也很有效。”

[P0199] 琼斯说：“你将会同你的伙伴愉快地会面的。他钻进洞里的动作比我来得快。伸出手来，让我铐上。”

[P0200] 当手铐把我们的俘虏的手腕扣上的时候，他说：“我请求你们不要用你们的脏手碰我。你们也许不知道我是皇族后裔。我还要请你们跟我说话时，在任何时候都要用'先生'和'请'字。”

[P0201] 琼斯瞪大眼睛，忍住了笑说：“好吧，唔，‘先生'请你往台阶上走吧，到了上面，我们可以弄辆马车把阁下送到警察局去。可以吗？”

[P0202] 约翰·克莱安详地说：“这就好些。"他向我们三人很快地鞠了个躬，然后默默无言地在警探的监护下走了出去。

[P0203] 当我们跟在他们后面从地下室走出来的时候，梅里韦瑟先生说：“我真不知道我们银行该怎么感谢和酬劳你们才好。毫无疑问，你们用了最严谨周密的方法来侦察和破案；这个案件是我经历中从未见过的最精心策划的一起盗窃银行案。”

[P0204] 福尔摩斯说：“我自己就有一两笔帐要和约翰·克莱算。我为这个案子花了点钱，我想银行会付给我这些钱的。但是，除此以外，我还得到其他方面的优厚报酬，这次破案的经验在许多方面都是独一无二的。光是听那红发会的很不寻常的故事也就收获不小了。”

[P0205] 清晨，我们在贝克街喝加苏打水的威士忌酒的时候，福尔摩斯解释说：“华生，你看，从一开始就十分明显，这个红发会的那个稀破古怪的广告和抄写《大英百科全书》的唯一可能的目的，是使这个糊里糊涂的当票老板每天离开他的店铺几个小时。这种做法很新破，但确实很难想出比这更巧妙的办法。这个办法无疑说明克莱的别出心裁，他利用品同谋犯的头发颜色。每周四英镑肯定是引他上钩的诱饵。对他们这些想把成千成万英镑弄到手的人来说，这点钱算得了什么呢？他们登了广告，一个流氓搞了个临时办公室，另一个流氓怂恿他去申请那个职位。他们合谋保证他每周每天上午离开他的店铺。从我听到那伙计只拿一半工资的时候起，我就看出，显然他到那当票当伙计是有某种特殊动机的。”

[P0206] “可是，你是怎么猜出他的动机的呢？”

[P0207] “如果在那店铺里有女人的话，我本来会怀疑无非是搞些庸俗的风流事。可是，根本不是那么回事。这个当票老板做的是小本经营的买卖，当票里没有什么值钱的东西，值不得他们如此精心策划，花那么多钱。因此，他们的目标肯定不在当票。那么可能搞什么呢？我想到这个伙计喜欢照相，想到他经常出没于地下室这个诡计。地下室！这就找到了这个错综复杂的案件的线索。然后，我调查了这个神秘的伙计的情况。我发现，我的对手是伦敦头脑最冷静、胆子最大的罪犯之一，他在地下室里搞了名堂，而且要连续几个月每天干许多小时才行。那再问一下，可能搞什么呢？我想除了挖一条通往其他楼房的地道以外，不可能是其他什么东西。

[P0208] “当我们去察看作案地点时，我心里就明白了。我用手杖敲打人行道使你感到惊讶，我当时是要弄清楚地下室是朝前还是朝后延伸的。它不是朝前延伸。然后我按门铃，正如我所希望的，是那伙计出来开门。我们曾经有过一些较量。但是，在这以前，彼此从未面对面相见过。我几乎没看他的脸，我想要看的是他的膝盖。你自己也一定觉察到，他的裤子膝部那个地方是多么破旧、皱褶和肮脏。这些情况说明，他花了多少时间去挖地道。这样唯一未解决的问题是，他们为什么挖地道？于是，我在那拐角周围巡视一番，我看到原来那城市与郊区银行和我们的朋友的房子紧挨着。我觉得问题解决了。当你在我们听完音乐坐车回家的时候，我走访了苏格兰场和这家银行的董事长，结果如何，你已经看到了。”

[P0209] 我问他：“你怎么能断定他们会在当天晚上作案呢？”

[P0210] “唔，他们的红发会办公室关门大吉是个讯号：他们对杰贝兹·威尔逊先生人在当票里已不在乎了。换句话说，他们的地道已经挖通了。但是，最重要的是，由于地道有可能被发现，黄金有可能被搬走，所以他们务必尽快利用这条地道。星期六比其他日子对他们更合适，这样他们有两天的空隙可供逃跑。根据上述种种理由，我预料他们会在今天晚上下手。”

[P0211] 我以毫不掩饰的钦佩心情赞叹道：“你这样推理真是太棒了。这一连串的推理可谓长矣，但每个环节都证明你的推断是正确的。”

[P0212] 他回答说："这免得我感到无聊。"他打个哈欠，接着说，“唉，我已觉得生活够无聊的了。我的一生就是力求不要在庸庸碌碌中虚度过去。这些小小的案件帮了我的忙。”

[P0213] 我说：“你真是造福人类啊！”

[P0214] 他耸了耸肩，说道，“唔，总而言之，这也许还有点用处。正如居斯塔夫·福楼拜在给乔治·桑的信中所说的，‘人是渺小的——著作就是一切。'“

已有人工标注上下文（可能为空；若存在，只作参考，不要机械复制）：
(none)
```
