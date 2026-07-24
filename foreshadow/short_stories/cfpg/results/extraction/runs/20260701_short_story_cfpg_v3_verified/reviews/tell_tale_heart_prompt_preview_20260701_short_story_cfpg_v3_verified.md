# Short Story CFPG Prompt Preview

## system

```text
你是短篇小说伏笔-触发-回收结构标注员。任务是在给定的全文段落时间线中，高召回抽取候选 Foreshadow-Trigger-Payoff 三元组。只能依据输入文本，不得使用外部知识或你对作品结局的先验记忆。只输出合法 JSON。
```

## user

```text
请对下面的短篇小说段落时间线执行第一步：高召回候选识别。

作品：
- story_id: tell_tale_heart
- title: The Tell-Tale Heart
- language: en

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
[P0001] True!—nervous—very, very dreadfully nervous I had been and am; but why will you say that I am mad? The disease had sharpened my senses—not destroyed—not dulled them. Above all was the sense of hearing acute. I heard all things in the heaven and in the earth. I heard many things in hell. How, then, am I mad? Hearken! and observe how healthily—how calmly I can tell you the whole story.

[P0002] It is impossible to say how first the idea entered my brain; but once conceived, it haunted me day and night. Object there was none. Passion there was none. I loved the old man. He had never wronged me. He had never given me insult. For his gold I had no desire. I think it was his eye! yes, it was this! He had the eye of a vulture—a pale blue eye, with a film over it. Whenever it fell upon me, my blood ran cold; and so by degrees—very gradually—I made up my mind to take the life of the old man, and thus rid myself of the eye forever.

[P0003] Now this is the point. You fancy me mad. Madmen know nothing. But you should have seen me. You should have seen how wisely I proceeded—with what caution—with what foresight—with what dissimulation I went to work! I was never kinder to the old man than during the whole week before I killed him. And every night, about midnight, I turned the latch of his door and opened it—oh, so gently! And then, when I had made an opening sufficient for my head, I put in a dark lantern, all closed, closed, that no light shone out, and then I thrust in my head. Oh, you would have laughed to see how cunningly I thrust it in! I moved it slowly—very, very slowly, so that I might not disturb the old man’s sleep. It took me an hour to place my whole head within the opening so far that I could see him as he lay upon his bed. Ha!—would a madman have been so wise as this? And then, when my head was well in the room, I undid the lantern cautiously—oh, so cautiously—cautiously (for the hinges creaked)—I undid it just so much that a single thin ray fell upon the vulture eye. And this I did for seven long nights—every night just at midnight—but I found the eye always closed; and so it was impossible to do the work; for it was not the old man who vexed me, but his Evil Eye. And every morning, when the day broke, I went boldly into the chamber, and spoke courageously to him, calling him by name in a hearty tone, and inquiring how he has passed the night. So you see he would have been a very profound old man, indeed, to suspect that every night, just at twelve, I looked in upon him while he slept.

[P0004] Upon the eighth night I was more than usually cautious in opening the door. A watch’s minute hand moves more quickly than did mine. Never before that night had I felt the extent of my own powers—of my sagacity. I could scarcely contain my feelings of triumph. To think that there I was, opening the door, little by little, and he not even to dream of my secret deeds or thoughts. I fairly chuckled at the idea; and perhaps he heard me; for he moved on the bed suddenly, as if startled. Now you may think that I drew back—but no. His room was as black as pitch with the thick darkness, (for the shutters were close fastened, through fear of robbers,) and so I knew that he could not see the opening of the door, and I kept pushing it on steadily, steadily.

[P0005] I had my head in, and was about to open the lantern, when my thumb slipped upon the tin fastening, and the old man sprang up in bed, crying out—“Who’s there?”

[P0006] I kept quite still and said nothing. For a whole hour I did not move a muscle, and in the meantime I did not hear him lie down. He was still sitting up in the bed listening;—just as I have done, night after night, hearkening to the death watches in the wall.

[P0007] Presently I heard a slight groan, and I knew it was the groan of mortal terror. It was not a groan of pain or of grief—oh, no!—it was the low stifled sound that arises from the bottom of the soul when overcharged with awe. I knew the sound well. Many a night, just at midnight, when all the world slept, it has welled up from my own bosom, deepening, with its dreadful echo, the terrors that distracted me. I say I knew it well. I knew what the old man felt, and pitied him, although I chuckled at heart. I knew that he had been lying awake ever since the first slight noise, when he had turned in the bed. His fears had been ever since growing upon him. He had been trying to fancy them causeless, but could not. He had been saying to himself—“It is nothing but the wind in the chimney—it is only a mouse crossing the floor,” or “It is merely a cricket which has made a single chirp.” Yes, he had been trying to comfort himself with these suppositions: but he had found all in vain. All in vain; because Death, in approaching him had stalked with his black shadow before him, and enveloped the victim. And it was the mournful influence of the unperceived shadow that caused him to feel—although he neither saw nor heard—to feel the presence of my head within the room.

[P0008] When I had waited a long time, very patiently, without hearing him lie down, I resolved to open a little—a very, very little crevice in the lantern. So I opened it—you cannot imagine how stealthily, stealthily—until, at length a single dim ray, like the thread of the spider, shot from out the crevice and fell full upon the vulture eye.

[P0009] It was open—wide, wide open—and I grew furious as I gazed upon it. I saw it with perfect distinctness—all a dull blue, with a hideous veil over it that chilled the very marrow in my bones; but I could see nothing else of the old man’s face or person: for I had directed the ray as if by instinct, precisely upon the damned spot.

[P0010] And have I not told you that what you mistake for madness is but over-acuteness of the sense?—now, I say, there came to my ears a low, dull, quick sound, such as a watch makes when enveloped in cotton. I knew that sound well, too. It was the beating of the old man’s heart. It increased my fury, as the beating of a drum stimulates the soldier into courage.

[P0011] But even yet I refrained and kept still. I scarcely breathed. I held the lantern motionless. I tried how steadily I could maintain the ray upon the eye. Meantime the hellish tattoo of the heart increased. It grew quicker and quicker, and louder and louder every instant. The old man’s terror must have been extreme! It grew louder, I say, louder every moment!—do you mark me well? I have told you that I am nervous: so I am. And now at the dead hour of the night, amid the dreadful silence of that old house, so strange a noise as this excited me to uncontrollable terror. Yet, for some minutes longer I refrained and stood still. But the beating grew louder, louder! I thought the heart must burst. And now a new anxiety seized me—the sound would be heard by a neighbour! The old man’s hour had come! With a loud yell, I threw open the lantern and leaped into the room. He shrieked once—once only. In an instant I dragged him to the floor, and pulled the heavy bed over him. I then smiled gaily, to find the deed so far done. But, for many minutes, the heart beat on with a muffled sound. This, however, did not vex me; it would not be heard through the wall. At length it ceased. The old man was dead. I removed the bed and examined the corpse. Yes, he was stone, stone dead. I placed my hand upon the heart and held it there many minutes. There was no pulsation. He was stone dead. His eye would trouble me no more.

[P0012] If still you think me mad, you will think so no longer when I describe the wise precautions I took for the concealment of the body. The night waned, and I worked hastily, but in silence. First of all I dismembered the corpse. I cut off the head and the arms and the legs.

[P0013] I then took up three planks from the flooring of the chamber, and deposited all between the scantlings. I then replaced the boards so cleverly, so cunningly, that no human eye—not even his—could have detected any thing wrong. There was nothing to wash out—no stain of any kind—no blood-spot whatever. I had been too wary for that. A tub had caught all—ha! ha!

[P0014] When I had made an end of these labors, it was four o’clock—still dark as midnight. As the bell sounded the hour, there came a knocking at the street door. I went down to open it with a light heart,—for what had I now to fear? There entered three men, who introduced themselves, with perfect suavity, as officers of the police. A shriek had been heard by a neighbour during the night; suspicion of foul play had been aroused; information had been lodged at the police office, and they (the officers) had been deputed to search the premises.

[P0015] I smiled,—for what had I to fear? I bade the gentlemen welcome. The shriek, I said, was my own in a dream. The old man, I mentioned, was absent in the country. I took my visitors all over the house. I bade them search—search well. I led them, at length, to his chamber. I showed them his treasures, secure, undisturbed. In the enthusiasm of my confidence, I brought chairs into the room, and desired them here to rest from their fatigues, while I myself, in the wild audacity of my perfect triumph, placed my own seat upon the very spot beneath which reposed the corpse of the victim.

[P0016] The officers were satisfied. My manner had convinced them. I was singularly at ease. They sat, and while I answered cheerily, they chatted of familiar things. But, ere long, I felt myself getting pale and wished them gone. My head ached, and I fancied a ringing in my ears: but still they sat and still chatted. The ringing became more distinct:—it continued and became more distinct: I talked more freely to get rid of the feeling: but it continued and gained definiteness—until, at length, I found that the noise was not within my ears.

[P0017] No doubt I now grew _very_ pale;—but I talked more fluently, and with a heightened voice. Yet the sound increased—and what could I do? It was a low, dull, quick sound—much such a sound as a watch makes when enveloped in cotton. I gasped for breath—and yet the officers heard it not. I talked more quickly—more vehemently; but the noise steadily increased. I arose and argued about trifles, in a high key and with violent gesticulations; but the noise steadily increased. Why would they not be gone? I paced the floor to and fro with heavy strides, as if excited to fury by the observations of the men—but the noise steadily increased. Oh God! what could I do? I foamed—I raved—I swore! I swung the chair upon which I had been sitting, and grated it upon the boards, but the noise arose over all and continually increased. It grew louder—louder—louder! And still the men chatted pleasantly, and smiled. Was it possible they heard not? Almighty God!—no, no! They heard!—they suspected!—they knew!—they were making a mockery of my horror!—this I thought, and this I think. But anything was better than this agony! Anything was more tolerable than this derision! I could bear those hypocritical smiles no longer! I felt that I must scream or die! and now—again!—hark! louder! louder! louder! _louder!_

[P0018] “Villains!” I shrieked, “dissemble no more! I admit the deed!—tear up the planks!—here, here!—It is the beating of his hideous heart!”

中文辅助译文段落时间线（可能为空；只能辅助理解，gold evidence 仍必须回到原文段落）：
[P0001] 告密的心〔美国〕爱伦坡

[P0002] 不错，神经质，我是非常神经质的，现在还是如此！但是你们何以说我疯了呢？我的这种病并没有毁灭或迟钝了我的感觉，反而使我的感觉更加灵敏——特别是听觉更加灵敏了。

[P0003] 我听见天上地上所有的一切，我还听见地狱里的许多东西。那么，我何以会是疯了呢？你们仔细地听我看我是怎样稳健安闲的，把整个事件的原委都讲出来。我不能告诉你们这思想最初是怎样进到我的脑子里来的，但一旦有了之后，便日夜萦回于心中。我并没有什么目的，什么冲动。我本来是爱那个老头子的。

[P0004] 他从没有做过对不起我的事，也没有侮辱过我。至于他的金子，我毫无贪婪之心。我想仍是因为他那眼睛的缘故。是的，就是他有一只眼，好像兀鹰的眼——灰蓝色，上面盖着一层膜。每当我瞥见那眼的时候，全身的血便好像都冷了，于是久而久之我渐渐决意要置他于死地，我就可以永远不再看见那只眼睛。

[P0005] 在我槍杀这老头子前一星期当中，我待他再好也没有了。每晚大约到半夜的时候，我便转着他房间的门纽，轻轻地开着。开着的宽度可以容纳我的头的时候，我便伸入一盏四周紧闭一点不露光的灯笼，然后我把头伸入。

[P0006] 你们看了我伸入时那种异常小心的态度，一定觉得可笑的。我慢慢地移动，慢慢地，以免惊动了那老头子的睡眠。我花了一小时的功夫，才把头伸入，刚可以看他睡在床上的情形。哼！一个疯子会像我这样的机警么？等我的头都伸入之后，我便非常小心地，非常小心地（因为那灯笼的轴钮处转动时有响声）把灯笼揭开一个小孔，射出一线小小的灯光，刚刚照在他那如兀鹰的眼睛上。像这样我接连做了七夜之久，每夜都是在半夜的时候，但每次我发觉他那只眼睛总是闭着的，所以我不能动手，因为令我日夜不安的，是他那只可恶的眼睛，而并非他本人。

[P0007] 等到每天清早的时候，我便大胆地走到他房里去，泰然地和他讲话，很亲热地叫他的名字，并问他一夜睡得怎样。如果那老头子还疑心我每晚在半夜十二点去偷看他，那他一定是一个很深沉的人。到第八夜我去开门的时候，比以往更加小心了。我的动作，比一只表上的分针还要慢些。

[P0008] 在这晚之前，我自己也不知我有这样大的能力，这样的机警。我差不多忍不住这种胜利的感觉。你们想：我一点一点地开着门，而他作梦也没有梦到我这种秘密的行为和念头。

[P0009] 我差不多要笑起来；恐怕他听见了，因为他忽然在床上翻身，似乎被惊动了。你想我会退缩么——不。因为房里是漆黑的（四周的窗子都紧闭了，以防盗贼），所以他不会看见我开门，而我仍继续慢慢地前进着。我的头伸入了，正预备打开灯的时候，忽然我的大拇指挂在那锡钮子上，那老头子便从床上爬起来，喊着：“谁在这里？”我静默着一言不发。整整的有一小时之久，我连一下子都没有动，但同时我没有听见他睡下去。他一直坐在床上静听——正如我每晚在墙边守候一样。

[P0010] 忽然我听见一声小小的叹息，我听了马上就晓得这是一种极度恐怖的叹声。这不是一种痛苦或忧愁的呻吟，而是因着一种非常的恐怖从心灵的深处发出的一种生硬的低声。我很懂得这种声音。常常在半夜到处寂静的时候，我也从心怀的深处听见这种声音，同时使我的惧怕更加深沉。我再说：我是很明白这种声音的。我晓得那老头子有怎样的感觉，我也可怜他，虽然我骨子里是很开心的。我晓得他最初在床上翻动的时候，便一直是醒着了。

[P0011] 从那时候，他的惧怕便逐渐增长。他勉强要把这种惧怕想做是无端的，但是不能够。他对自己说：“不过是烟囱吹进来的风罢了——不过是老鼠在地板上跑过，”或是“蟋蟀叫了一声。”

[P0012] 是的，他想用这些假定来安慰自己，但是都无用，因为死亡走近他的时候，已经有黑影在他面前，把他包围住了。就是这种黑影的影响，使他“感觉”到伸入他房里的头，虽然他并没有看见或听见。我耐心等了许久还未听见他睡下的时候，我便决心把灯打开一点——只打开一点点。于是我一点点打开，偷偷地，偷偷地，直到最后一条小小的光线，好像蛛丝一样，从灯笼里发出来，正射在他那秃鹰似的眼睛上。那眼睛是开着的——大大的开着的。我注视那眼睛的时候，不禁气愤填膺。我看得非常之清楚，全是苍灰色，盖着一层可怕的薄膜，令我看了冷入骨髓。

[P0013] 但此外我看不见那老头子的脸或身体，因为我刚巧把那一线光射在那眼珠上。而现在——我不是对你们说过，我是神经过于敏锐，而你们误以为我是疯了么？——而现在我听到了一种低钝而短促的声音，正如一只表包在棉花里所发出的声音一样。我对这声音也是再熟悉没有了。那是这老头子心跳的声音。

[P0014] 这声音更增加了我的愤怒，正如军队的鼓声更增加了士兵的勇气一样。但即使如此，我还是保持着耐心毫不移动。我抑着气息，稳持着灯笼，一点也不动。我要看我把这线光射在他眼上，能保持多久。同时，那可怕的心跳声继续增强。那声音愈来愈快，愈来愈大。那老头子的惧怕，一定是到了极点了！我说，那声音愈来愈大，愈来愈大，你们听清楚了么？我也说过我的神经是非常敏锐的。而现在半夜在这老屋子可怕的寂静之中，这种声音实在令我感到一种不可耐的恐怖。然而我还是再保持了几分钟的镇静。而那声音愈来愈大，恐怕他的心要裂了。

[P0015] 忽然一种新的恐惧捉住了我——这声音恐怕邻居听见了。这老头子的末日到了！我大叫一声，把整个灯笼打开，跳入房中。他叫了一声——只叫了一声。我马上把他拖到地上，把床罩在他身上。然后我开心的笑着，我要干的事已经干到这个程度了。但是那心的跳声，还是继续了一些时。

[P0016] 这我并不怕什么，这声音并不会透出墙外。最后，那声音停止了。这老头子死了。我把床移开，来查看他的尸首。他的确是像石头一样的死了。我把手放在他心上，按了好几分钟。他的心不跳了，他是像石头一样的死了。他的眼睛再不会令我恼怒了。如果你们还以为我是疯子的话，只要你们听我讲述我是如何小心地藏匿尸首，那你们就不会再以为我是疯子了。夜将尽了，我必须赶快工作，不过不能弄出声音。起先，我把他分割开来。我把他的头和四肢，都割下来。然后我把地板揭起三块板子，把肢体都存放在木干之间。我再把板子好好地盖上，盖得丝毫不露痕迹，任何人的眼睛都看不出什么毛病来——即使是那老头子的眼珠。没有什么要洗刷的，没有什么污迹。我对于这类的事是太聪明了。用一个盆子把这些都弄好了。哈哈！我把这些都做完之后，已经是四点钟了，但到处还是像半夜一样黑暗的。

[P0017] 等到敲钟的时候，我听见有人敲大门的声音，我心里很轻快地下去开了门——因为现在我还怕什么呢？当时进来了三个人，很客气地自称为警署的官员。他们说这里有一个邻居在半夜听见叫声，恐怕有歹人的行为，便通知了警署，他们（那些警官）是被派到这里来搜查的。我笑着——因为我还怕什么呢？我对那三位警官表示欢迎之意。我说，那叫声乃是在梦中呓语喊出来的。那老头子，我说是往乡间去了。我带那三位往全屋各处查看，请他们细心的检查。最后我带他们到那老头子房里。我把他的财物给他们看，并未有人拿动。在我这种自信的热心中，我还拿些椅子进房来，请他们三位休息一下，至于我自己，则大胆地把自己的座位正放在那尸首的上面。那些警官觉得满意了。

[P0018] 我的态度使他们相信我了。我现出若无其事的样子。他们坐着，我一方面很高兴地答他们的话，他们也随便谈着。但不久，我觉得自己的脸色有些发白，只希望他们赶快走了。我的头疼痛，觉得耳里轰轰作声，但他们还是坐着，还是谈着话。我耳里的声音更清楚了——它继续下去而且愈加明白起来。

已有人工标注上下文（可能为空；若存在，只作参考，不要机械复制）：
(none)
```
