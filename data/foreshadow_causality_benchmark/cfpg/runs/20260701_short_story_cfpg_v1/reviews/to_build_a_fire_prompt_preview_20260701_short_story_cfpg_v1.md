# Short Story CFPG Prompt Preview

## system

```text
你是短篇小说伏笔-触发-回收结构标注员。任务是在给定的全文段落时间线中，高召回抽取候选 Foreshadow-Trigger-Payoff 三元组。只能依据输入文本，不得使用外部知识或你对作品结局的先验记忆。只输出合法 JSON。
```

## user

```text
请对下面的短篇小说段落时间线执行第一步：高召回候选识别。

作品：
- story_id: to_build_a_fire
- title: To Build A Fire
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
[P0001] Day had broken cold and grey, exceedingly cold and grey, when the man turned aside from the main Yukon trail and climbed the high earth-bank, where a dim and little-travelled trail led eastward through the fat spruce timberland. It was a steep bank, and he paused for breath at the top, excusing the act to himself by looking at his watch. It was nine o’clock. There was no sun nor hint of sun, though there was not a cloud in the sky. It was a clear day, and yet there seemed an intangible pall over the face of things, a subtle gloom that made the day dark, and that was due to the absence of sun. This fact did not worry the man. He was used to the lack of sun. It had been days since he had seen the sun, and he knew that a few more days must pass before that cheerful orb, due south, would just peep above the sky-line and dip immediately from view.

[P0002] The man flung a look back along the way he had come. The Yukon lay a mile wide and hidden under three feet of ice. On top of this ice were as many feet of snow. It was all pure white, rolling in gentle undulations where the ice-jams of the freeze-up had formed. North and south, as far as his eye could see, it was unbroken white, save for a dark hair-line that curved and twisted from around the spruce-covered island to the south, and that curved and twisted away into the north, where it disappeared behind another spruce-covered island. This dark hair-line was the trail—the main trail—that led south five hundred miles to the Chilcoot Pass, Dyea, and salt water; and that led north seventy miles to Dawson, and still on to the north a thousand miles to Nulato, and finally to St. Michael on Bering Sea, a thousand miles and half a thousand more.

[P0003] But all this—the mysterious, far-reaching hairline trail, the absence of sun from the sky, the tremendous cold, and the strangeness and weirdness of it all—made no impression on the man. It was not because he was long used to it. He was a new-comer in the land, a _chechaquo_, and this was his first winter. The trouble with him was that he was without imagination. He was quick and alert in the things of life, but only in the things, and not in the significances. Fifty degrees below zero meant eighty odd degrees of frost. Such fact impressed him as being cold and uncomfortable, and that was all. It did not lead him to meditate upon his frailty as a creature of temperature, and upon man’s frailty in general, able only to live within certain narrow limits of heat and cold; and from there on it did not lead him to the conjectural field of immortality and man’s place in the universe. Fifty degrees below zero stood for a bite of frost that hurt and that must be guarded against by the use of mittens, ear-flaps, warm moccasins, and thick socks. Fifty degrees below zero was to him just precisely fifty degrees below zero. That there should be anything more to it than that was a thought that never entered his head.

[P0004] As he turned to go on, he spat speculatively. There was a sharp, explosive crackle that startled him. He spat again. And again, in the air, before it could fall to the snow, the spittle crackled. He knew that at fifty below spittle crackled on the snow, but this spittle had crackled in the air. Undoubtedly it was colder than fifty below—how much colder he did not know. But the temperature did not matter. He was bound for the old claim on the left fork of Henderson Creek, where the boys were already. They had come over across the divide from the Indian Creek country, while he had come the roundabout way to take a look at the possibilities of getting out logs in the spring from the islands in the Yukon. He would be in to camp by six o’clock; a bit after dark, it was true, but the boys would be there, a fire would be going, and a hot supper would be ready. As for lunch, he pressed his hand against the protruding bundle under his jacket. It was also under his shirt, wrapped up in a handkerchief and lying against the naked skin. It was the only way to keep the biscuits from freezing. He smiled agreeably to himself as he thought of those biscuits, each cut open and sopped in bacon grease, and each enclosing a generous slice of fried bacon.

[P0005] He plunged in among the big spruce trees. The trail was faint. A foot of snow had fallen since the last sled had passed over, and he was glad he was without a sled, travelling light. In fact, he carried nothing but the lunch wrapped in the handkerchief. He was surprised, however, at the cold. It certainly was cold, he concluded, as he rubbed his numbed nose and cheek-bones with his mittened hand. He was a warm-whiskered man, but the hair on his face did not protect the high cheek-bones and the eager nose that thrust itself aggressively into the frosty air.

[P0006] At the man’s heels trotted a dog, a big native husky, the proper wolf-dog, grey-coated and without any visible or temperamental difference from its brother, the wild wolf. The animal was depressed by the tremendous cold. It knew that it was no time for travelling. Its instinct told it a truer tale than was told to the man by the man’s judgment. In reality, it was not merely colder than fifty below zero; it was colder than sixty below, than seventy below. It was seventy-five below zero. Since the freezing-point is thirty-two above zero, it meant that one hundred and seven degrees of frost obtained. The dog did not know anything about thermometers. Possibly in its brain there was no sharp consciousness of a condition of very cold such as was in the man’s brain. But the brute had its instinct. It experienced a vague but menacing apprehension that subdued it and made it slink along at the man’s heels, and that made it question eagerly every unwonted movement of the man as if expecting him to go into camp or to seek shelter somewhere and build a fire. The dog had learned fire, and it wanted fire, or else to burrow under the snow and cuddle its warmth away from the air.

[P0007] The frozen moisture of its breathing had settled on its fur in a fine powder of frost, and especially were its jowls, muzzle, and eyelashes whitened by its crystalled breath. The man’s red beard and moustache were likewise frosted, but more solidly, the deposit taking the form of ice and increasing with every warm, moist breath he exhaled. Also, the man was chewing tobacco, and the muzzle of ice held his lips so rigidly that he was unable to clear his chin when he expelled the juice. The result was that a crystal beard of the colour and solidity of amber was increasing its length on his chin. If he fell down it would shatter itself, like glass, into brittle fragments. But he did not mind the appendage. It was the penalty all tobacco-chewers paid in that country, and he had been out before in two cold snaps. They had not been so cold as this, he knew, but by the spirit thermometer at Sixty Mile he knew they had been registered at fifty below and at fifty-five.

[P0008] He held on through the level stretch of woods for several miles, crossed a wide flat of nigger-heads, and dropped down a bank to the frozen bed of a small stream. This was Henderson Creek, and he knew he was ten miles from the forks. He looked at his watch. It was ten o’clock. He was making four miles an hour, and he calculated that he would arrive at the forks at half-past twelve. He decided to celebrate that event by eating his lunch there.

[P0009] The dog dropped in again at his heels, with a tail drooping discouragement, as the man swung along the creek-bed. The furrow of the old sled-trail was plainly visible, but a dozen inches of snow covered the marks of the last runners. In a month no man had come up or down that silent creek. The man held steadily on. He was not much given to thinking, and just then particularly he had nothing to think about save that he would eat lunch at the forks and that at six o’clock he would be in camp with the boys. There was nobody to talk to and, had there been, speech would have been impossible because of the ice-muzzle on his mouth. So he continued monotonously to chew tobacco and to increase the length of his amber beard.

[P0010] Once in a while the thought reiterated itself that it was very cold and that he had never experienced such cold. As he walked along he rubbed his cheek-bones and nose with the back of his mittened hand. He did this automatically, now and again changing hands. But rub as he would, the instant he stopped his cheek-bones went numb, and the following instant the end of his nose went numb. He was sure to frost his cheeks; he knew that, and experienced a pang of regret that he had not devised a nose-strap of the sort Bud wore in cold snaps. Such a strap passed across the cheeks, as well, and saved them. But it didn’t matter much, after all. What were frosted cheeks? A bit painful, that was all; they were never serious.

[P0011] Empty as the man’s mind was of thoughts, he was keenly observant, and he noticed the changes in the creek, the curves and bends and timber-jams, and always he sharply noted where he placed his feet. Once, coming around a bend, he shied abruptly, like a startled horse, curved away from the place where he had been walking, and retreated several paces back along the trail. The creek he knew was frozen clear to the bottom—no creek could contain water in that arctic winter—but he knew also that there were springs that bubbled out from the hillsides and ran along under the snow and on top the ice of the creek. He knew that the coldest snaps never froze these springs, and he knew likewise their danger. They were traps. They hid pools of water under the snow that might be three inches deep, or three feet. Sometimes a skin of ice half an inch thick covered them, and in turn was covered by the snow. Sometimes there were alternate layers of water and ice-skin, so that when one broke through he kept on breaking through for a while, sometimes wetting himself to the waist.

[P0012] That was why he had shied in such panic. He had felt the give under his feet and heard the crackle of a snow-hidden ice-skin. And to get his feet wet in such a temperature meant trouble and danger. At the very least it meant delay, for he would be forced to stop and build a fire, and under its protection to bare his feet while he dried his socks and moccasins. He stood and studied the creek-bed and its banks, and decided that the flow of water came from the right. He reflected awhile, rubbing his nose and cheeks, then skirted to the left, stepping gingerly and testing the footing for each step. Once clear of the danger, he took a fresh chew of tobacco and swung along at his four-mile gait.

[P0013] In the course of the next two hours he came upon several similar traps. Usually the snow above the hidden pools had a sunken, candied appearance that advertised the danger. Once again, however, he had a close call; and once, suspecting danger, he compelled the dog to go on in front. The dog did not want to go. It hung back until the man shoved it forward, and then it went quickly across the white, unbroken surface. Suddenly it broke through, floundered to one side, and got away to firmer footing. It had wet its forefeet and legs, and almost immediately the water that clung to it turned to ice. It made quick efforts to lick the ice off its legs, then dropped down in the snow and began to bite out the ice that had formed between the toes. This was a matter of instinct. To permit the ice to remain would mean sore feet. It did not know this. It merely obeyed the mysterious prompting that arose from the deep crypts of its being. But the man knew, having achieved a judgment on the subject, and he removed the mitten from his right hand and helped tear out the ice-particles. He did not expose his fingers more than a minute, and was astonished at the swift numbness that smote them. It certainly was cold. He pulled on the mitten hastily, and beat the hand savagely across his chest.

[P0014] At twelve o’clock the day was at its brightest. Yet the sun was too far south on its winter journey to clear the horizon. The bulge of the earth intervened between it and Henderson Creek, where the man walked under a clear sky at noon and cast no shadow. At half-past twelve, to the minute, he arrived at the forks of the creek. He was pleased at the speed he had made. If he kept it up, he would certainly be with the boys by six. He unbuttoned his jacket and shirt and drew forth his lunch. The action consumed no more than a quarter of a minute, yet in that brief moment the numbness laid hold of the exposed fingers. He did not put the mitten on, but, instead, struck the fingers a dozen sharp smashes against his leg. Then he sat down on a snow-covered log to eat. The sting that followed upon the striking of his fingers against his leg ceased so quickly that he was startled, he had had no chance to take a bite of biscuit. He struck the fingers repeatedly and returned them to the mitten, baring the other hand for the purpose of eating. He tried to take a mouthful, but the ice-muzzle prevented. He had forgotten to build a fire and thaw out. He chuckled at his foolishness, and as he chuckled he noted the numbness creeping into the exposed fingers. Also, he noted that the stinging which had first come to his toes when he sat down was already passing away. He wondered whether the toes were warm or numbed. He moved them inside the moccasins and decided that they were numbed.

[P0015] He pulled the mitten on hurriedly and stood up. He was a bit frightened. He stamped up and down until the stinging returned into the feet. It certainly was cold, was his thought. That man from Sulphur Creek had spoken the truth when telling how cold it sometimes got in the country. And he had laughed at him at the time! That showed one must not be too sure of things. There was no mistake about it, it was cold. He strode up and down, stamping his feet and threshing his arms, until reassured by the returning warmth. Then he got out matches and proceeded to make a fire. From the undergrowth, where high water of the previous spring had lodged a supply of seasoned twigs, he got his firewood. Working carefully from a small beginning, he soon had a roaring fire, over which he thawed the ice from his face and in the protection of which he ate his biscuits. For the moment the cold of space was outwitted. The dog took satisfaction in the fire, stretching out close enough for warmth and far enough away to escape being singed.

[P0016] When the man had finished, he filled his pipe and took his comfortable time over a smoke. Then he pulled on his mittens, settled the ear-flaps of his cap firmly about his ears, and took the creek trail up the left fork. The dog was disappointed and yearned back toward the fire. This man did not know cold. Possibly all the generations of his ancestry had been ignorant of cold, of real cold, of cold one hundred and seven degrees below freezing-point. But the dog knew; all its ancestry knew, and it had inherited the knowledge. And it knew that it was not good to walk abroad in such fearful cold. It was the time to lie snug in a hole in the snow and wait for a curtain of cloud to be drawn across the face of outer space whence this cold came. On the other hand, there was keen intimacy between the dog and the man. The one was the toil-slave of the other, and the only caresses it had ever received were the caresses of the whip-lash and of harsh and menacing throat-sounds that threatened the whip-lash. So the dog made no effort to communicate its apprehension to the man. It was not concerned in the welfare of the man; it was for its own sake that it yearned back toward the fire. But the man whistled, and spoke to it with the sound of whip-lashes, and the dog swung in at the man’s heels and followed after.

[P0017] The man took a chew of tobacco and proceeded to start a new amber beard. Also, his moist breath quickly powdered with white his moustache, eyebrows, and lashes. There did not seem to be so many springs on the left fork of the Henderson, and for half an hour the man saw no signs of any. And then it happened. At a place where there were no signs, where the soft, unbroken snow seemed to advertise solidity beneath, the man broke through. It was not deep. He wetted himself half-way to the knees before he floundered out to the firm crust.

[P0018] He was angry, and cursed his luck aloud. He had hoped to get into camp with the boys at six o’clock, and this would delay him an hour, for he would have to build a fire and dry out his foot-gear. This was imperative at that low temperature—he knew that much; and he turned aside to the bank, which he climbed. On top, tangled in the underbrush about the trunks of several small spruce trees, was a high-water deposit of dry firewood—sticks and twigs principally, but also larger portions of seasoned branches and fine, dry, last-year’s grasses. He threw down several large pieces on top of the snow. This served for a foundation and prevented the young flame from drowning itself in the snow it otherwise would melt. The flame he got by touching a match to a small shred of birch-bark that he took from his pocket. This burned even more readily than paper. Placing it on the foundation, he fed the young flame with wisps of dry grass and with the tiniest dry twigs.

[P0019] He worked slowly and carefully, keenly aware of his danger. Gradually, as the flame grew stronger, he increased the size of the twigs with which he fed it. He squatted in the snow, pulling the twigs out from their entanglement in the brush and feeding directly to the flame. He knew there must be no failure. When it is seventy-five below zero, a man must not fail in his first attempt to build a fire—that is, if his feet are wet. If his feet are dry, and he fails, he can run along the trail for half a mile and restore his circulation. But the circulation of wet and freezing feet cannot be restored by running when it is seventy-five below. No matter how fast he runs, the wet feet will freeze the harder.

[P0020] All this the man knew. The old-timer on Sulphur Creek had told him about it the previous fall, and now he was appreciating the advice. Already all sensation had gone out of his feet. To build the fire he had been forced to remove his mittens, and the fingers had quickly gone numb. His pace of four miles an hour had kept his heart pumping blood to the surface of his body and to all the extremities. But the instant he stopped, the action of the pump eased down. The cold of space smote the unprotected tip of the planet, and he, being on that unprotected tip, received the full force of the blow. The blood of his body recoiled before it. The blood was alive, like the dog, and like the dog it wanted to hide away and cover itself up from the fearful cold. So long as he walked four miles an hour, he pumped that blood, willy-nilly, to the surface; but now it ebbed away and sank down into the recesses of his body. The extremities were the first to feel its absence. His wet feet froze the faster, and his exposed fingers numbed the faster, though they had not yet begun to freeze. Nose and cheeks were already freezing, while the skin of all his body chilled as it lost its blood.

[P0021] But he was safe. Toes and nose and cheeks would be only touched by the frost, for the fire was beginning to burn with strength. He was feeding it with twigs the size of his finger. In another minute he would be able to feed it with branches the size of his wrist, and then he could remove his wet foot-gear, and, while it dried, he could keep his naked feet warm by the fire, rubbing them at first, of course, with snow. The fire was a success. He was safe. He remembered the advice of the old-timer on Sulphur Creek, and smiled. The old-timer had been very serious in laying down the law that no man must travel alone in the Klondike after fifty below. Well, here he was; he had had the accident; he was alone; and he had saved himself. Those old-timers were rather womanish, some of them, he thought. All a man had to do was to keep his head, and he was all right. Any man who was a man could travel alone. But it was surprising, the rapidity with which his cheeks and nose were freezing. And he had not thought his fingers could go lifeless in so short a time. Lifeless they were, for he could scarcely make them move together to grip a twig, and they seemed remote from his body and from him. When he touched a twig, he had to look and see whether or not he had hold of it. The wires were pretty well down between him and his finger-ends.

[P0022] All of which counted for little. There was the fire, snapping and crackling and promising life with every dancing flame. He started to untie his moccasins. They were coated with ice; the thick German socks were like sheaths of iron half-way to the knees; and the mocassin strings were like rods of steel all twisted and knotted as by some conflagration. For a moment he tugged with his numbed fingers, then, realizing the folly of it, he drew his sheath-knife.

[P0023] But before he could cut the strings, it happened. It was his own fault or, rather, his mistake. He should not have built the fire under the spruce tree. He should have built it in the open. But it had been easier to pull the twigs from the brush and drop them directly on the fire. Now the tree under which he had done this carried a weight of snow on its boughs. No wind had blown for weeks, and each bough was fully freighted. Each time he had pulled a twig he had communicated a slight agitation to the tree—an imperceptible agitation, so far as he was concerned, but an agitation sufficient to bring about the disaster. High up in the tree one bough capsized its load of snow. This fell on the boughs beneath, capsizing them. This process continued, spreading out and involving the whole tree. It grew like an avalanche, and it descended without warning upon the man and the fire, and the fire was blotted out! Where it had burned was a mantle of fresh and disordered snow.

[P0024] The man was shocked. It was as though he had just heard his own sentence of death. For a moment he sat and stared at the spot where the fire had been. Then he grew very calm. Perhaps the old-timer on Sulphur Creek was right. If he had only had a trail-mate he would have been in no danger now. The trail-mate could have built the fire. Well, it was up to him to build the fire over again, and this second time there must be no failure. Even if he succeeded, he would most likely lose some toes. His feet must be badly frozen by now, and there would be some time before the second fire was ready.

[P0025] Such were his thoughts, but he did not sit and think them. He was busy all the time they were passing through his mind, he made a new foundation for a fire, this time in the open; where no treacherous tree could blot it out. Next, he gathered dry grasses and tiny twigs from the high-water flotsam. He could not bring his fingers together to pull them out, but he was able to gather them by the handful. In this way he got many rotten twigs and bits of green moss that were undesirable, but it was the best he could do. He worked methodically, even collecting an armful of the larger branches to be used later when the fire gathered strength. And all the while the dog sat and watched him, a certain yearning wistfulness in its eyes, for it looked upon him as the fire-provider, and the fire was slow in coming.

[P0026] When all was ready, the man reached in his pocket for a second piece of birch-bark. He knew the bark was there, and, though he could not feel it with his fingers, he could hear its crisp rustling as he fumbled for it. Try as he would, he could not clutch hold of it. And all the time, in his consciousness, was the knowledge that each instant his feet were freezing. This thought tended to put him in a panic, but he fought against it and kept calm. He pulled on his mittens with his teeth, and threshed his arms back and forth, beating his hands with all his might against his sides. He did this sitting down, and he stood up to do it; and all the while the dog sat in the snow, its wolf-brush of a tail curled around warmly over its forefeet, its sharp wolf-ears pricked forward intently as it watched the man. And the man as he beat and threshed with his arms and hands, felt a great surge of envy as he regarded the creature that was warm and secure in its natural covering.

[P0027] After a time he was aware of the first far-away signals of sensation in his beaten fingers. The faint tingling grew stronger till it evolved into a stinging ache that was excruciating, but which the man hailed with satisfaction. He stripped the mitten from his right hand and fetched forth the birch-bark. The exposed fingers were quickly going numb again. Next he brought out his bunch of sulphur matches. But the tremendous cold had already driven the life out of his fingers. In his effort to separate one match from the others, the whole bunch fell in the snow. He tried to pick it out of the snow, but failed. The dead fingers could neither touch nor clutch. He was very careful. He drove the thought of his freezing feet; and nose, and cheeks, out of his mind, devoting his whole soul to the matches. He watched, using the sense of vision in place of that of touch, and when he saw his fingers on each side the bunch, he closed them—that is, he willed to close them, for the wires were drawn, and the fingers did not obey. He pulled the mitten on the right hand, and beat it fiercely against his knee. Then, with both mittened hands, he scooped the bunch of matches, along with much snow, into his lap. Yet he was no better off.

[P0028] After some manipulation he managed to get the bunch between the heels of his mittened hands. In this fashion he carried it to his mouth. The ice crackled and snapped when by a violent effort he opened his mouth. He drew the lower jaw in, curled the upper lip out of the way, and scraped the bunch with his upper teeth in order to separate a match. He succeeded in getting one, which he dropped on his lap. He was no better off. He could not pick it up. Then he devised a way. He picked it up in his teeth and scratched it on his leg. Twenty times he scratched before he succeeded in lighting it. As it flamed he held it with his teeth to the birch-bark. But the burning brimstone went up his nostrils and into his lungs, causing him to cough spasmodically. The match fell into the snow and went out.

[P0029] The old-timer on Sulphur Creek was right, he thought in the moment of controlled despair that ensued: after fifty below, a man should travel with a partner. He beat his hands, but failed in exciting any sensation. Suddenly he bared both hands, removing the mittens with his teeth. He caught the whole bunch between the heels of his hands. His arm-muscles not being frozen enabled him to press the hand-heels tightly against the matches. Then he scratched the bunch along his leg. It flared into flame, seventy sulphur matches at once! There was no wind to blow them out. He kept his head to one side to escape the strangling fumes, and held the blazing bunch to the birch-bark. As he so held it, he became aware of sensation in his hand. His flesh was burning. He could smell it. Deep down below the surface he could feel it. The sensation developed into pain that grew acute. And still he endured it, holding the flame of the matches clumsily to the bark that would not light readily because his own burning hands were in the way, absorbing most of the flame.

[P0030] At last, when he could endure no more, he jerked his hands apart. The blazing matches fell sizzling into the snow, but the birch-bark was alight. He began laying dry grasses and the tiniest twigs on the flame. He could not pick and choose, for he had to lift the fuel between the heels of his hands. Small pieces of rotten wood and green moss clung to the twigs, and he bit them off as well as he could with his teeth. He cherished the flame carefully and awkwardly. It meant life, and it must not perish. The withdrawal of blood from the surface of his body now made him begin to shiver, and he grew more awkward. A large piece of green moss fell squarely on the little fire. He tried to poke it out with his fingers, but his shivering frame made him poke too far, and he disrupted the nucleus of the little fire, the burning grasses and tiny twigs separating and scattering. He tried to poke them together again, but in spite of the tenseness of the effort, his shivering got away with him, and the twigs were hopelessly scattered. Each twig gushed a puff of smoke and went out. The fire-provider had failed. As he looked apathetically about him, his eyes chanced on the dog, sitting across the ruins of the fire from him, in the snow, making restless, hunching movements, slightly lifting one forefoot and then the other, shifting its weight back and forth on them with wistful eagerness.

[P0031] The sight of the dog put a wild idea into his head. He remembered the tale of the man, caught in a blizzard, who killed a steer and crawled inside the carcass, and so was saved. He would kill the dog and bury his hands in the warm body until the numbness went out of them. Then he could build another fire. He spoke to the dog, calling it to him; but in his voice was a strange note of fear that frightened the animal, who had never known the man to speak in such way before. Something was the matter, and its suspicious nature sensed danger,—it knew not what danger but somewhere, somehow, in its brain arose an apprehension of the man. It flattened its ears down at the sound of the man’s voice, and its restless, hunching movements and the liftings and shiftings of its forefeet became more pronounced but it would not come to the man. He got on his hands and knees and crawled toward the dog. This unusual posture again excited suspicion, and the animal sidled mincingly away.

[P0032] The man sat up in the snow for a moment and struggled for calmness. Then he pulled on his mittens, by means of his teeth, and got upon his feet. He glanced down at first in order to assure himself that he was really standing up, for the absence of sensation in his feet left him unrelated to the earth. His erect position in itself started to drive the webs of suspicion from the dog’s mind; and when he spoke peremptorily, with the sound of whip-lashes in his voice, the dog rendered its customary allegiance and came to him. As it came within reaching distance, the man lost his control. His arms flashed out to the dog, and he experienced genuine surprise when he discovered that his hands could not clutch, that there was neither bend nor feeling in the lingers. He had forgotten for the moment that they were frozen and that they were freezing more and more. All this happened quickly, and before the animal could get away, he encircled its body with his arms. He sat down in the snow, and in this fashion held the dog, while it snarled and whined and struggled.

[P0033] But it was all he could do, hold its body encircled in his arms and sit there. He realized that he could not kill the dog. There was no way to do it. With his helpless hands he could neither draw nor hold his sheath-knife nor throttle the animal. He released it, and it plunged wildly away, with tail between its legs, and still snarling. It halted forty feet away and surveyed him curiously, with ears sharply pricked forward. The man looked down at his hands in order to locate them, and found them hanging on the ends of his arms. It struck him as curious that one should have to use his eyes in order to find out where his hands were. He began threshing his arms back and forth, beating the mittened hands against his sides. He did this for five minutes, violently, and his heart pumped enough blood up to the surface to put a stop to his shivering. But no sensation was aroused in the hands. He had an impression that they hung like weights on the ends of his arms, but when he tried to run the impression down, he could not find it.

[P0034] A certain fear of death, dull and oppressive, came to him. This fear quickly became poignant as he realized that it was no longer a mere matter of freezing his fingers and toes, or of losing his hands and feet, but that it was a matter of life and death with the chances against him. This threw him into a panic, and he turned and ran up the creek-bed along the old, dim trail. The dog joined in behind and kept up with him. He ran blindly, without intention, in fear such as he had never known in his life. Slowly, as he ploughed and floundered through the snow, he began to see things again—the banks of the creek, the old timber-jams, the leafless aspens, and the sky. The running made him feel better. He did not shiver. Maybe, if he ran on, his feet would thaw out; and, anyway, if he ran far enough, he would reach camp and the boys. Without doubt he would lose some fingers and toes and some of his face; but the boys would take care of him, and save the rest of him when he got there. And at the same time there was another thought in his mind that said he would never get to the camp and the boys; that it was too many miles away, that the freezing had too great a start on him, and that he would soon be stiff and dead. This thought he kept in the background and refused to consider. Sometimes it pushed itself forward and demanded to be heard, but he thrust it back and strove to think of other things.

[P0035] It struck him as curious that he could run at all on feet so frozen that he could not feel them when they struck the earth and took the weight of his body. He seemed to himself to skim along above the surface and to have no connection with the earth. Somewhere he had once seen a winged Mercury, and he wondered if Mercury felt as he felt when skimming over the earth.

[P0036] His theory of running until he reached camp and the boys had one flaw in it: he lacked the endurance. Several times he stumbled, and finally he tottered, crumpled up, and fell. When he tried to rise, he failed. He must sit and rest, he decided, and next time he would merely walk and keep on going. As he sat and regained his breath, he noted that he was feeling quite warm and comfortable. He was not shivering, and it even seemed that a warm glow had come to his chest and trunk. And yet, when he touched his nose or cheeks, there was no sensation. Running would not thaw them out. Nor would it thaw out his hands and feet. Then the thought came to him that the frozen portions of his body must be extending. He tried to keep this thought down, to forget it, to think of something else; he was aware of the panicky feeling that it caused, and he was afraid of the panic. But the thought asserted itself, and persisted, until it produced a vision of his body totally frozen. This was too much, and he made another wild run along the trail. Once he slowed down to a walk, but the thought of the freezing extending itself made him run again.

[P0037] And all the time the dog ran with him, at his heels. When he fell down a second time, it curled its tail over its forefeet and sat in front of him facing him curiously eager and intent. The warmth and security of the animal angered him, and he cursed it till it flattened down its ears appeasingly. This time the shivering came more quickly upon the man. He was losing in his battle with the frost. It was creeping into his body from all sides. The thought of it drove him on, but he ran no more than a hundred feet, when he staggered and pitched headlong. It was his last panic. When he had recovered his breath and control, he sat up and entertained in his mind the conception of meeting death with dignity. However, the conception did not come to him in such terms. His idea of it was that he had been making a fool of himself, running around like a chicken with its head cut off—such was the simile that occurred to him. Well, he was bound to freeze anyway, and he might as well take it decently. With this new-found peace of mind came the first glimmerings of drowsiness. A good idea, he thought, to sleep off to death. It was like taking an anæsthetic. Freezing was not so bad as people thought. There were lots worse ways to die.

[P0038] He pictured the boys finding his body next day. Suddenly he found himself with them, coming along the trail and looking for himself. And, still with them, he came around a turn in the trail and found himself lying in the snow. He did not belong with himself any more, for even then he was out of himself, standing with the boys and looking at himself in the snow. It certainly was cold, was his thought. When he got back to the States he could tell the folks what real cold was. He drifted on from this to a vision of the old-timer on Sulphur Creek. He could see him quite clearly, warm and comfortable, and smoking a pipe.

[P0039] “You were right, old hoss; you were right,” the man mumbled to the old-timer of Sulphur Creek.

[P0040] Then the man drowsed off into what seemed to him the most comfortable and satisfying sleep he had ever known. The dog sat facing him and waiting. The brief day drew to a close in a long, slow twilight. There were no signs of a fire to be made, and, besides, never in the dog’s experience had it known a man to sit like that in the snow and make no fire. As the twilight drew on, its eager yearning for the fire mastered it, and with a great lifting and shifting of forefeet, it whined softly, then flattened its ears down in anticipation of being chidden by the man. But the man remained silent. Later, the dog whined loudly. And still later it crept close to the man and caught the scent of death. This made the animal bristle and back away. A little longer it delayed, howling under the stars that leaped and danced and shone brightly in the cold sky. Then it turned and trotted up the trail in the direction of the camp it knew, where were the other food-providers and fire-providers.

中文辅助译文段落时间线（可能为空；只能辅助理解，gold evidence 仍必须回到原文段落）：
[P0001] 天已破晓，灰冷异常。有个男人从育空步道的干道转出来，爬上高高的河堤，那里有另一条模糊难辨、人迹罕至的步道向东而去，穿过长满粗壮云杉的林地。河堤陡峭，爬到顶时他停下来喘着气，为了掩饰喘吁，他看了看表。时间是九点，天空万里无云，却不见太阳，连太阳的影儿都没有。好歹是个晴天，但万物都好像蒙着一层无形的尸布，影影绰绰的阴郁把天色衬托得越发暗淡，这都是因为没有了太阳。但他并没怎么担心，对此已经习以为常了。日头有好多天没露脸了。他知道还得再等待几天，那个明亮的光球才会从正南方的天际线昙花一现般探一下头出来。

[P0002] 那人回头朝来路看了一眼。育空河有一英里宽，横陈在三英尺厚的冰封之下。冰层之上又覆盖着同样厚的积雪，白茫茫一片，绵延起伏。这起伏中藏匿着严寒期的凌汛。视线所及之处，从南到北都是一成不变的白色，只有一条黑色的细线从南边长满云杉的小岛那里蜿蜒而来，又一直蜿蜒向北，消失在另一座长满云杉的小岛。这条黑色的细线就是那条步道——那条干道，向南五百英里通向奇尔库特山口，再到戴雅，直到海边；向北七十英里通向道森，再向北一千英里到努拉托，还要继续走一千五百多英里最终到达白令海的圣迈克尔。

[P0003] 但这一切——神秘、绵长而细小的步道，没有太阳的天空，刺骨的严寒，以及这种种的陌生和怪异，都丝毫没能使那人心生畏惧。倒不是因为他早已司空见惯。他初来乍到，是个新手，第一次在这里过冬。问题在于他缺乏想象力。对周遭的事物他的确表现得聪敏机警，但这仅限于事物表象，对背后的意义却不开窍。零下五十度相当于露点以下八十几度。这种情况在他眼里只不过是“冷”、“不舒服”，仅此而已。他完全没有想到作为恒温动物的自己的脆弱，也没有进一步想到人类普遍的脆弱——只能在很有限的冷热范围内生存，更没有推想到有关“不朽”以及“人类在宇宙中的地位“这些事情。零下五十度对他来说只是无足轻重的霜冻——有点痛，只需穿戴连指手套、耳罩、保暖的鹿皮靴和厚袜子就可以抵御的霜冻。零下五十度就是零下五十度。除此以外，他什么也没多想。

[P0004] 当他转身继续往前走时，随口吐了口唾沫。一声尖锐而剧烈的脆响把他吓了一跳。他又吐了一口。再向天上吐了一口，唾沫在落地之前就已经噼啪作响地凝结了。他知道，气温在零下五十度时，唾沫落地后会冻成冰，但现在还在空中就已经凝结了。不用说，气温肯定已经低于零下五十度——至于低多少，他不清楚。他觉得温度不重要；重要的是一定要前往亨德森河分岔口左边的旧矿区，伙伴们已经在那里了。他们翻过印地安溪地区的分水岭，又绕道来看看有没有可能开春后把育空河小岛上的原木顺流运出去。他会在六点前到达营地，没错，要天黑以后才能到了，但伙伴们都会在那里，生着火，有热腾腾的晚饭等着他。至于午餐，他按了按外套下面鼓鼓的包袱。午餐就放在衬衫下面，包着手帕，贴着身体。只有这样里面的松饼才不会冻住。每块松饼都切开两半，涂上腌肉的油脂，再夹上一块煎腌肉。想到这些松饼，他忍不住得意地笑起来。

[P0005] 他在巨大的云杉树之间穿行，步道已经辨认不清。自从上次有雪橇经过，雪已经下了一英尺厚，而他庆幸自己没有雪橇，轻装上阵。其实，除了用手帕包着的午餐以外，他什么都没带。但是他没想到天会这么冷。他一边戴着手套揉搓冻麻的鼻子和颧骨，一边心想这天确实冷。他留着浓密的络腮胡，但脸上的毛发却保护不了他的高颧骨和那只不由分说刺进冷风中的大鼻子。

[P0006] 有条狗小跑着跟在那人身后，那是一条土生土长的大型哈士奇犬，一条像模像样的狼狗，灰色的皮毛，与它的近亲，野狼相比，不论在外观或脾性上都没有两样。酷寒让它消沉。它知道，现在不是出行的时候。本能的指示要比那人头脑的判断更加真切。事实上，气温不只是比零下五十度低一点；而是比零下六十度、七十度还低。实际已经达到了零下七十五度。零上三十二度是露点，这就是说此时已达到露点以下一百零七度。狗对温度没有概念。可能它的头脑不像人那样对很冷这个状态有明确的意识。但这畜生拥有本能。它脑中闪过一丝模糊但来势汹汹的担忧，这担忧逼使它灰溜溜地紧跟在那人身后，并急切地揣测着他的每个异动，像在期待他能找个营地或随便什么地方生火避寒。这条狗知道什么是火，而且它盼着有火取暖，要不然它就钻进雪里，蜷起来抵御冷空气。

[P0007] 它呼出的水汽在皮毛上凝结成细小的霜粉，尤其在下巴、口鼻和眼睫毛都被结晶的哈气染白了。那人的红胡子也结了一层更厚实的霜，他每一次呼吸，温润的哈气所结成的冰就在一点点增加。另外，那人还嚼着烟丝，冰就像牲口的口套一样紧紧箍住他的双唇，以至于吐出烟沫时都没法保持下巴的清洁。久而久之，琥珀一样的冰晶在胡子上越结越多。如果摔倒，这些冰溜子就会像玻璃一样脆生生地碎一地。但他觉得这些附属物都无所谓。在他们那，这是所有嚼烟丝的都要付出的代价，而且之前两次寒流过境时他也出过门。他知道，那两次没有这次冷，根据六十英里[1]的酒精温度计显示，那两次的气温分别是零下五十度和五十五度。

[P0008] 他在平展的树林中坚持走了几英里，穿过一片宽阔平坦的“黑鬼头”草地，又从岸边下到一条冰封的河床上。这就是亨德森溪，现在离河汊还有十英里。他看了看表，时间是十点。如果每小时走四英里，他估摸着能在十二点半到达河汊。他准备在那里吃午餐，就当庆祝。

[P0009] 当那人沿着冰面大摇大摆前行时，狗又凑到他跟前，耷拉着尾巴，一副沮丧的样子。以前雪橇经过的痕迹依然清晰可辨，但从上次以来，压痕上已经落了十几英寸的积雪。这条寂静的小溪一个月来没人往来经过了。那人继续稳健前行。什么也没想，他一心盼着到河汊吃午饭，再在六点与伙伴们在营地会合，别的没什么好想的。身边没有人可以说话，就算有，嘴上罩着的冰也让他没法开口。他只是继续单调地嚼着烟丝，琥珀色的胡子不断增长。

[P0010] 天真冷，从没见过这么冷的，这样的想法时不时会跳出来。他一边走，一边用手套背面不自觉地揉搓颧骨和鼻子，偶尔换一下手。但不管怎么揉，只要一停下来，颧骨就又冻麻了，紧接着，鼻头也没了知觉。他想到脸肯定要冻伤，心里突然为自己没有设计出像巴德在寒流来时戴的那种鼻罩而感到一阵遗憾。这种罩子也盖着脸，可以把脸鼻一起保护起来。不过也无所谓，脸被冻了算什么？有点痛而已，没什么大不了的。

[P0011] 尽管那人脑子里空空如也，但他的观察力却很敏锐，他注意到了小河的变化，注意到了河弯、河曲以及阻塞在河道中的原木，而且他非常清楚该往哪里下脚。有一次，遇到一个水弯子，他像受惊的马一样突然跳开，然后沿原路绕开，退回到步道上。他知道，虽然那条小河已经冻透了——在那个极地的寒冬，没有哪条小河还能淌水——但山坡上依然会有泉眼往外冒水，泉水流淌在积雪之下、冰面之上。他清楚，就算最冷的寒流，这些泉水也不会冻住，他也同样清楚这其中的危险。它们无异于陷阱。隐藏在雪下面的水洼，可能有三英寸深，也可能有三英尺深。有时，水上面结了半英寸厚的冰壳，再盖着雪。有时，水和冰壳层层交叠，当一层踩穿，就会层层踩穿，有时陷进去会没到腰部。

[P0012] 这就是为什么他如此仓皇后退。他感到了脚底下变形了，又听到雪下冰壳的碎裂声。在这种温度下把脚弄湿意味着麻烦和危险。至少也会耽误时间，因为他不得不停下来生火，在火边光着脚，好让鞋袜烘干。他站定不动，观察着河床及两岸，确认水流来自右边。思考片刻，他揉了揉鼻子和脸颊，然后沿着边缘绕到左边，步步留心，一步一试探。摆脱了危险后，他立刻新嚼了一口烟丝，继续以四英里的速度大步向前。

[P0013] 在接下来的两个小时里，他还遇到了几个类似的陷阱。通常隐蔽水洼上方的积雪会凹下去且带有结晶，这就表示有危险。不过，有一回他差点陷进去；还有一回，他怀疑不安全，就强迫狗走在前面。但狗不情愿。它畏缩不前，最后被那人硬推出去。它快速穿过那片洁白无印的雪面。突然，冰被踩穿了，它身子猛地倾侧，又迅速挣扎着逃到了更结实的地方。它的前爪和腿都湿透了，粘着的水一眨眼功夫就结成了冰。它迅速舔掉腿上的冰，然后在雪地上趴下，开始咬爪子缝里的冰。这都是出于本能。留着冰不管，很快爪子就会酸痛难忍。它并不明白这些，只是顺服从发自身体最深处的神秘的提示。但与动物不同，那人却是通过判断发现了危险。他取下右手手套，开始帮狗摘掉冰粒子。让他震惊的是，手指还不到裸露一分钟就已经麻木。天真的很冷啊。他赶忙戴上手套，在胸口狠劲拍打起来。

[P0014] 十二点是一天最亮的时刻。然而冬季太阳南巡得太远，已经无法越出地平线。大地的隆起把它和亨德森河隔开，以至于那人走在正午的晴空下，地上却连一点影子也没有。到了十二点半，他一分不差地抵达河汊。他对行进的速度感到满意。如果保持下去，他肯定会在六点前与伙伴们会合。他解开外套和衬衫，取出午餐。这个动作用了还不到十几秒钟，但就这短短一会儿，裸露的手指已经整个冻麻了。他没有立即戴回手套，而是狠狠地在腿上拍了十几下。之后，他坐在一根盖着雪的木头上准备吃饭。还没来得及吃一口松饼，刚才手指拍打腿部时的刺痛就已经消失了，他大吃一惊，又马上拍打了一阵，再把手套戴上。为了吃东西，只能露着另一只手。刚想吃一口，却发现被冰箍住的嘴张不开。他忘了该生火来解冻脸上的冰。他笑自己太蠢，而就在笑的这一会儿功夫，麻木感再度悄悄渗入裸露的手指。他还发现最开始坐下时脚趾头的刺痛也已经消失了。他在想这会儿的脚趾是暖的还是麻的。他试着在靴子里动了动，发现已经全冻僵了。

[P0015] 他急忙戴上手套，站起身，心中有些害怕。他来来回回地跺着脚，直到重新有了刺痛感。他想，这天确实非常冷。有个住在硫磺溪的人说过有时这里会有多冷，说的一点不假。他当时还嘲笑了他！人真不能太自以为是啊。天冷得毋庸置疑。他来来回回地跨着步、跺着脚、甩着胳膊，直到恢复了温暖才放心地停下来。然后，他拿出火柴准备生火。他从灌木丛中找到些木柴，都是上个春天涨水时冲过来的。他小心翼翼地点着一团小火苗，很快就烧旺起来。他在火旁烤化脸上的冰，就着温暖吃起了松饼。至此，人类的智慧战胜了外界的寒冷。狗也心满意足地取着暖，在离火不近不远刚刚好的位置伸着懒腰，温暖又不至烧伤。

[P0016] 吃完午饭，他填上烟斗，一边抽着一边享受片刻的安逸。然后他戴上手套，把帽子上护耳紧紧盖住耳朵，开始沿河汊左边分出的河道继续前行。那条狗有些失望，舍不得那堆火。那人对寒冷知之甚少，可能他的祖祖辈辈都对寒冷，真正的寒冷，冰点以下一百零七度的寒冷一无所知。但那狗知道；它的祖祖辈辈都知道，而它继承了这门学问。它知道，在如此可怕的寒冷中出行是不可取的。这时候应该躲在雪地的洞里，等着云彩遮住天空，隔绝从那而来的寒冷。但是，狗和那人之间并没有什么亲密的关系。一个是另一个的奴隶，狗得到的唯一爱抚是鞭子的爱抚以及主人威胁抽鞭子时的怒吼。所以它无心把自己的忧虑透露给那人。它也不关心那人的安危；想回到火堆旁只是为了它自己。但是那人吹了个口哨，用抽鞭子时的吼声唤它，狗只好赶忙跑过去，尾随其后。

[P0017] 那人只要一嚼烟丝，胡子上琥珀色的冰溜子就又重新长出来。他湿润的呼吸很快还把小胡子、眉毛和睫毛染白了。亨德森河的左河汊这片似乎没有那么多的水洼，走了半个小时，连一个都没有遇到。但就在这时，状况却发生了。就在一个毫无危险迹象的地方，柔软完整的积雪本该表明下面是结实的，但他往那里一踩，却陷了下去。陷得不深，水没过半条小腿，他连忙挣扎着拔腿迈到结实的地方。

[P0018] 他很恼火，大声咒骂着这遭倒霉事。原计划在六点钟抵达营地与伙伴们会合，这下得耽误一个小时，因为他必须生火，烘干脚上的装备。他心里清楚这是当务之急，特别是在这样的低温里。他连忙调头爬上河岸。在几棵小云杉树周围的灌木丛里，杂乱地堆积着涨水时留下的干柴——主要是些枝丫，但也有大截的干树枝和干细的枯草。他把几块大点的木头铺了一层在雪地上，用来防止刚着的火苗被融化的雪水浇灭。他又从口袋里掏出一小块桦树皮，这东西比纸更易燃，火柴在上面一划，就点着了。他再把它放在铺好的木头上，用小把小把干草和最细的干树枝喂着火苗。

[P0019] 他缓慢而谨慎地操作着，心中清楚此刻所面临的危险。渐渐地火烧了起来，他开始往里添一些稍大的木柴。他蹲在雪地上，从交杂的灌木丛里拽出一些枝丫，直接扔进火里。他清楚不能有一点闪失。在零下七十五度生火必须一次成功，尤其脚还湿着。如果脚是干的，火没点着，他还可以沿着步道跑半英里，恢复血液循环。但是，零下七十五度再怎么跑步，也恢复不了又湿又冻的脚部血液循环。跑再快，湿脚都只会越来越僵。

[P0020] 那人心知肚明。上个秋天硫磺溪的老前辈警告过，现在他总算深有体会了。他的脚已经毫无知觉。为了生火，他不得不脱下手套，没多久手指就又麻木了。每小时四英里的步速能让心脏不断把血液抽送到体表和四肢末梢。一旦停下来，抽送的作用就减弱了。冷风侵袭着赤裸的地表，而他，就站在赤裸的地表之上，迎接着酷寒的全面暴击。他体内的血液也退缩了。血液是活的，就像狗，也会躲起来，遮蔽自己抵御寒冷。只要他保持每小时四英里的速度，不管怎么样，血液都会被抽送到体表；但现在血液收缩到身体深处。手脚首先感到缺血，尽管湿漉漉的脚和裸露的手指都还没被完全冻僵，但脚冻得越快，就表示手指会麻得越快。鼻子和脸已经僵了，全身的皮肤也逐渐在失血中变得冰冷。

[P0021] 但火已经烧旺起来。他还算是安全的。脚趾、鼻子和脸颊只不过着了霜。刚才他往火里添手指大小的枝丫。再过一会儿，就能添些手腕粗细的树枝，然后他就可以脱掉湿漉漉的鞋袜，一边烘干，一边凑近双脚烤烤火。当然，得先用雪来擦一遍。总算生火成功，他安全了。他又想起了硫磺溪老前辈的警告，不禁笑起来。这位老前辈定下死规：温度低于零下五十度时，禁止任何人在克朗代克单独出行。但是他做到了；是发生了一些意外，但他可是一个人，而且自救成功。他心想，那些老前辈都柔弱得像女人，至少一部分是。人只要保持冷静就不会有事。是男人都可以单独出行。但让他没想到的是，脸颊和鼻子这么快就能被冻僵。他也没有料到手指这么一会儿就不听使唤了——他连一根树枝都抓不住，手合不起来，就像已经不长在身上了。捡树枝的时候，他必须看一下是不是真的抓住了。身体和手指的联系完全掉线了。

[P0022] 但所有这些都不算什么。这火烧得噼啪作响，火焰飞舞。有火，生命就有保障。他开始脱靴。鞋面已经被冰包住，厚厚的德国袜套着半条腿，硬得就像铁皮鞘；鞋带像被火烧过的钢丝，扭曲打结。他用冻麻的手指拉扯了一会儿，突然发现这是白费力，于是抽出了鞘刀。

[P0023] 不过，还没等切断鞋带，状况就来了。这是他自己的疏忽，或者说，错误。他不应该在树下生火，而应该在开阔地——哪怕在树底下更省事，可以随时拽出灌木丛里的树枝直接丢进火里。他头顶上的树枝上落了厚厚的积雪。数周无风，每条树枝上都是已经积满了雪。他每次扯动树下的枝丫，都会造成轻微的震动——在他眼中微乎其微却足以带来灾难。突然，高处一条树枝上的全部积雪倾倒下来，落在下面的树枝上，翻倒了更多积雪。连锁反应蔓延到整棵树。最后好像雪崩一般，毫无征兆地，大堆积雪落在那人和火上面，火焰顷刻熄灭！刚才的火堆，已经盖上了一摊碎雪。

[P0024] 那人惊得目瞪口呆，像是刚被判了死刑。他呆坐了一会儿，凝视着熄灭的火堆。不久，他变得异常平静。也许硫磺溪的老前辈是对的。如果有个同行的伙伴，他就不会有危险了。同伴现在就能重新生火。不管怎样，现在只能靠自己再生一次，并且这次决不能再有一点差池。就算成功了，他也多半会失去几个脚趾。他脚上的冻伤肯定已经非常严重了，而且再生好火还需要一阵。

[P0025] 他这么思考着，但他并不是干坐在那里思考。这些念头闪过的时候他一直忙活着，他为火堆重新铺了一层木头，这次换在了开阔地，不会再有可恶的树木把火扑灭。接下来，他从涨水时冲过来的浮渣中收集了干草和小树枝。不听使唤的手指已经不抓不起东西了，只能一把一把地舀。这里面掺杂了许多腐烂的树枝和青苔这些用不着的东西，但他只能尽力而为。他有条不紊地操作着，甚至还收集了一些稍大的树枝，抱在臂弯里，方便等火着起来后用。整个过程里，那条狗始终坐在一旁观望，眼露切望，它指望他生火，而火却迟迟不来。

[P0026] 万事俱备，那人把手伸到口袋里再掏一块桦树皮。虽然手指感觉不到，但他知道树皮就在那里，他能听到摸索时发出的清脆的沙沙声。想尽了办法，却还是抓不住。他不住地想自己脚上的冻伤每时每刻都在加剧。这让他陷入恐慌，但他极力克制，保持着冷静。他咬住手套把手抽出来，来回甩动手臂，以全力拍打身体两侧。他本来坐着拍，又站起来拍。而那条狗一直坐在雪地里，它的狼鬃尾巴盘过来温暖地护住前爪，它盯着那人的时候，两只跟狼一样的尖耳直探向前。而当那人拍打胳膊和双手时，他看着那畜生有天然的皮毛保护，尽享温暖和安全，心中不禁一阵嫉妒。

[P0027] 过了会儿，经过拍拍打打的手指总算有了微弱的感觉。这细小的刺痛感渐渐强烈起来，最后变得痛不欲生，但那人对此满心欢呼起来。他赶忙脱下右手的手套，终于掏出了树皮。暴露在外的手指很快又麻木了。他立刻拿出那捆硫磺火柴。但酷寒已经使手指失去了活力。就在他费劲地想从一捆火柴里抽出一根时，整捆都掉在了雪地里。他想把火柴从雪里抠出来，但没有成功。僵死的手指既不能碰也不能抓。他小心翼翼，全神贯注在火柴上，不再去想冻僵的脚，还有鼻子和脸颊。他盯着火柴，用视觉代替触觉，当他看到火柴已经被围在手指之间，他就合拢手指——其实手筋已经缩紧，手指早就不听使唤了，合拢手指只是在意念中想想。于是他戴回右手套，再狠狠地拍打膝盖，然后用带着手套的两手把那捆火柴连着雪一起捧到腿面上，但情况并不乐观。

[P0028] 经过一番努力，他总算用两掌末端夹起了火柴捆。他这样夹着把它送到嘴边。当他强行张嘴时，裂开的冰发出噼里啪啦的响声。他把下颌往里收，翘起上唇，再用上排牙齿刮着火柴捆，想弄一根出来。他成功了，总算叼出一根，但又掉在了腿上。情况并没有好转，他怎么也捡不起来。然后灵机一动，他躬身咬住火柴，再在腿上摩擦。划了二十次总算点燃了。他就叼着烧着的火柴凑近树皮。但燃烧的硫磺味窜入鼻孔，吸进肺里，他一阵狂咳。火柴掉进雪里，熄灭了。

[P0029] 硫磺溪的老前辈是对的，他在接踵而来的绝望中强撑着，心里想：气温低于零下五十度就必须结伴出行。他继续拍打双手，但毫无知觉。突然，他用牙咬着去掉手套，露出双手。他用双掌末端夹住整捆火柴。好在胳膊肌肉还没有冻僵，还能用腕力夹住火柴。他就这样将整捆在腿上摩擦起来。火焰一下子迸发出来，七十根硫磺火柴一起划着了！没有风，火柴继续燃着。他一边侧着头避开呛人的烟雾，一边把烧着的火柴凑到树皮上。就在这时，手有了知觉。那里烧着了，连焦味都闻得到。表皮之下的深处隐约传来痛感，越来越强烈，渐渐变得灼痛难忍。但他还是忍着，笨拙地想引燃树皮，但太难了，因为已经烧着的手吸收了大部分的火焰。

[P0030] 终于，他再也无法坚持，两手猛地抽搐了一下。炽热的火柴落在雪里，嘶嘶作响，但幸好树皮点燃了。他赶忙把干草和最细的枝丫放在火焰上。他没法用手挑拣，只能用两掌末端夹起燃料，他尽量用牙齿咬掉树枝上的腐木和青苔。他小心翼翼又笨手笨脚地护着这团火。火就是命，决不能熄灭！就在这时，血液已经从体表退去，他开始发抖，行动变得更加笨拙。有一大块青苔直接砸在小火上。他想用手指把它扒出去，但颤抖让他一下子用力过猛，小火的核心被破坏了，烧着的草和树枝四散开。他试着再把它们拨拢到一起，但尽管极力控制，还是不住地颤抖，树枝被扒得到处都是，希望已经渺茫。终于，每根树枝接连冒起一缕缕的烟，火熄了。生火的人失败了。他无动于衷地环顾四周，突然看到了那条狗，就坐在火堆灰烬的另一面，一边不安地耸动身子，一边交替着微微抬起前爪，显得急切焦躁。

[P0031] 看到这条狗，一个疯狂的念头跳出来。他听说以前有人被困在暴风雪中，他杀了一头牛，爬进尸体里，于是救了自己一命。他想把狗杀了，再把手塞进温暖的尸体里，直到消冻。这样他就能再生一堆火。他叫那狗，唤它过来；但他的声音里有一种陌生的恐惧感把那畜生吓住了。它从没听过那人这样说话。有什么不对劲，它多疑的天性嗅到了危险——它不知道是什么危险，但在头脑里，恍惚闪过一丝对那人的警惕。听到那人的声音，它的耳朵耷拉下来，不安的耸动以及踮脚都越来越剧烈。但它就是不过来。于是他手脚并用，向狗爬去。这种不寻常的姿势再次激起了狗的怀疑，它迈着碎步躲开了。

[P0032] 那人在雪地里坐起身，花了一会儿时间勉强让自己冷静下来。然后，他用牙齿咬着把手套戴上，再双脚站立起来。他先是低头看了一眼，确保自己是真的站起来了，因为双脚已经丧失知觉，让他找不到站在地面上的感觉。他起身的动作打消了狗的疑虑；当他带着抽鞭子的声音向狗咆哮时，它表现出习惯性的顺从向他走来。正当那畜生走到触手可及的距离时，那人再也控制不住，猛然伸手向狗扑去，却震惊地发现自己的手已全无知觉，不能抓东西，连手指也无法弯曲。那一瞬间他忘记了手已经冻僵，而且越冻越僵硬。说时迟那时快，狗还来不及跳开，他已经用胳膊一下子环扣住它。他跌坐在雪地里，那条狗咆哮着、呜咽着、挣扎着。

[P0033] 坐在那里，紧紧地抱着狗，他意识到自己根本弄不死它，一点办法也没有。这双没用的手，既不能拔刀，也不能握刀，更不能掐死它。他终于松开手，那狗夹着尾巴猛蹿出去，一个劲地咆哮着。跑出四十英尺外，它稀奇地回望着他，耳朵直挺挺地向前探着。那人低头看了看，找到两手的位置，还挂在胳膊末端。他惊奇一个人竟然要用眼睛去找手的位置。想到这，他又赶快来回甩动双臂，戴着手套拍打身体两侧。猛拍了五分钟，心脏总算把足够的血液抽送到体表，颤抖停止了。但手还是没有任何知觉。他想象着手像重物一样挂在他的双臂末端，但当他试着寻找这种感觉时，却一点也感觉不到手还挂在那里。

[P0034] 一种对死亡的恐惧向他袭来，沉闷而压抑。当他发现这已经不再是冻伤手指脚趾，或失去手脚那么简单，而是关乎生死，且情况极其严峻的时候，恐惧感立即变得强烈起来。陷入了恐慌的他转身沿着模糊破败步道，在河床上奔跑起来。那条狗从后面跟上来。他漫无目的地跑着，像瞎了一样，此刻的恐惧一辈子从未有过。当他跌跌撞撞地在雪中跑了一会儿，周围的事物慢慢地清晰起来——河岸、阻塞在河弯子里的原木、光秃秃的山杨树，还有天空。奔跑让他感觉好些了，颤抖停止了。或许，继续跑下去，脚就会解冻；而且如果一直跑下去，说不定能直接跑到营地，见到伙伴们。几根手指和脚趾肯定是保不住了，还有脸上的一些部位；但只要能赶到那里，伙伴们就能照顾他，至少能保住性命。与此同时，有另一个想法回荡在脑海：他永远也到不了营地，见不到伙伴们；距离太遥远，冰冻太严重，用不了多久他就会冻僵、死掉。他撇开这个念头，停止思考。但这个念头又时不时窜出来，占据大脑，他再次把它极力压下去，逼自己想些别的事情。

[P0035] 他的双脚已经冻得无法在踩在地面上并撑起全身重量时产生任何知觉，他惊奇地发现自己居然还能继续奔跑。他感觉像是在地表之上滑行，完全脱离了地面。他曾在什么地方看见过长着翅膀的墨丘利，他猜这大概就是墨丘利掠过地表时的感觉吧。

[P0036] 一口气跑到营地和伙伴们那里的这个理论有个漏洞：他耐力不够。好几次，他踉跄跌到，勉强站起来，没挪几步就又跌到。当他试着起身，却起不来。他心想必须坐着歇歇，接下来不能再跑了，一直走就好。当他坐着恢复呼吸后，一阵温暖和惬意传来，他不再发抖，甚至好像有一团温暖的光进入胸膛和躯干。他赶忙碰碰鼻子和脸颊，却发现依然毫无知觉。跑步无法让面部解冻，也无法让手脚恢复知觉。然后，他忽然想到，身体冻僵的部分一定还在扩散。他马上打消这个想法，尽量忘掉或想些别的事情；他明白这种想法所能引起的恐慌，而恐慌最让他害怕。但这个念头挥之不去，越想越像真的，他仿佛看到自己被整个冻僵的景象。这实在太可怕了，他再次沿步道狂奔了一段。一放慢脚步，那冻伤正在吞噬全身的念头就又迫使他继续奔跑起来。

[P0037] 那条狗一直跟着他跑，紧随其后。当他再次摔倒时，它坐在他面前，好奇又急切地看着他，尾巴盘过来围着前爪。那畜生的温暖和安逸把他激怒了，他咒骂起来，骂得狗耷拉下耳朵。这一次，他更快就又开始颤抖起来。他就要输掉这场与严寒的抗争了。冷气从四面八方钻进身体。这个念头再次催使他跑起来，但跑了不到一百英尺，他就踉踉跄跄地一头栽倒下去。这是他最后一次感到慌乱。当呼吸和情绪逐渐恢复，他坐起来，脑海中有滋有味地构想着要有尊严地迎接死亡。然而，一点尊严也没感受到。他觉得他一直在愚弄自己，像一只砍掉脑袋的鸡一样跑来跑去——这是他能想到的比方。反正，无论如何都在劫难逃，还不如体面地接受死亡。这一新生的平静让他开始感到昏昏欲睡。他想，在睡眠中死去倒也不错，就像服用麻药一样。被冻死并不像人们想象的那么糟糕。还有很多更糟糕的死法。

[P0038] 他想象着第二天伙伴们找到他的尸体的情形。突然间，他发现自己竟和他们在一起，沿着步道寻找自己。而且，还是与他们一起，他来到步道的一个转弯处，发现自己躺在雪地里。不再属于自己，他仿佛灵魂出窍，与伙伴们站在一起，望着雪中的自己。他想，这确实冷啊。等回到美国，他要告诉亲朋们什么才是真正的寒冷。幻境逐渐变化，硫磺河的老前辈浮现在眼前，能一清二楚地看到他抽着烟斗，温暖又惬意。

[P0039] “你是对的，老家伙，你是对的。”那人对硫磺溪的老前辈喃喃地说。

[P0040] 最后，那人昏昏沉沉地进入了从未感受过的、最舒适、最享受的睡眠之中。那狗面对他坐着，等待着。短暂的白天即将在漫长而迟缓的黄昏中谢幕，可没有一点生火的迹象，此外，在狗的经验中，它从未见过那人像这样坐在雪地里而不生火。随着暮色逐渐暗沉，对火的切望已经占据了它全部的意识，它一边焦急地左右交替着抬起前爪，一边小声呜咽，它的耳朵耷拉着，像是知道自己的不安分会招致那人的呵斥。但他始终沉默不语。过了一阵，狗大声哀鸣起来。再后来，它悄悄地靠近那人，嗅到了死亡的气味。这让它毛骨悚然，赶忙退避。它又流连了一会儿，在冷空中闪烁舞动着的繁星下嚎叫起来。然后，它转过身，沿着步道朝它熟悉的营地方向跑去，那里还有其他能喂食和生火的人。

已有人工标注上下文（可能为空；若存在，只作参考，不要机械复制）：
metadata:
  story_id: to_build_a_fire
  title: "To Build a Fire"
  author: "Jack London"
  language: en
  source_text_path: data/foreshadow_causality_benchmark/normalized_texts/to_build_a_fire.txt
  source_url: https://gutenberg.pglaf.org/2/4/2/2429/2429-0.txt
  copyright_status: public_domain
  genre: naturalism
  length_level: short
  structure_type: [naturalist]
annotation_guide:
  focus:
    - Mark environmental rules as causal constraints, not atmospheric description.
    - Track the old-timer's advice as rule foreshadowing whose payoff is literal survival failure.
    - Preserve the contrast between the man's reasoning and the dog's instinctive knowledge.
  boundary_notes:
    - The dog is an agent with instinctive state, but its actions are not human motivations.
    - Most causal edges are physical or rule-based; avoid over-psychologizing them.
events:
  - event_id: TF_E01
    story_id: to_build_a_fire
    chapter_or_section: setup
    text_span: P0003-P0007
    summary: The man underestimates extreme cold while the dog instinctively recognizes danger.
    participants: [the man, the dog]
    location: Yukon trail
    time: morning
    event_type: internal_state
    certainty: {value: certain}
    narrative_reality_level: {value: real}
  - event_id: TF_E02
    story_id: to_build_a_fire
    chapter_or_section: travel
    text_span: P0011-P0013
    summary: The man recognizes hidden spring traps and observes the danger of wetting feet.
    participants: [the man, the dog]
    location: Henderson Creek
    time: late morning
    event_type: discovery
    certainty: {value: certain}
    narrative_reality_level: {value: real}
  - event_id: TF_E03
    story_id: to_build_a_fire
    chapter_or_section: first_fire
    text_span: P0014-P0016
    summary: The man builds a first fire for lunch, then leaves it despite the dog's desire to stay.
    participants: [the man, the dog]
    location: fork of Henderson Creek
    time: noon
    event_type: action
    certainty: {value: certain}
    narrative_reality_level: {value: real}
  - event_id: TF_E04
    story_id: to_build_a_fire
    chapter_or_section: accident
    text_span: P0017-P0019
    summary: The man breaks through hidden ice, wets himself to the knees, and must build a fire immediately.
    participants: [the man]
    location: left fork of Henderson Creek
    time: afternoon
    event_type: accident
    certainty: {value: certain}
    narrative_reality_level: {value: real}
  - event_id: TF_E05
    story_id: to_build_a_fire
    chapter_or_section: accident
    text_span: P0020-P0023
    summary: The man builds under a spruce tree, shakes loose snow from its boughs, and the snow extinguishes the fire.
    participants: [the man]
    location: under small spruce trees
    time: after wetting his feet
    event_type: accident
    certainty: {value: certain}
    narrative_reality_level: {value: real}
  - event_id: TF_E06
    story_id: to_build_a_fire
    chapter_or_section: failed_recovery
    text_span: P0024-P0030
    summary: With frozen hands, the man fails to make a sustainable second fire.
    participants: [the man]
    location: open snow near the creek
    time: after the first fire is extinguished
    event_type: action
    certainty: {value: certain}
    narrative_reality_level: {value: real}
  - event_id: TF_E07
    story_id: to_build_a_fire
    chapter_or_section: failed_recovery
    text_span: P0031-P0033
    summary: The man tries to kill the dog for warmth but cannot use his frozen hands.
    participants: [the man, the dog]
    location: snow near the failed fire
    time: near death
    event_type: action
    certainty: {value: certain}
    narrative_reality_level: {value: real}
  - event_id: TF_E08
    story_id: to_build_a_fire
    chapter_or_section: resolution
    text_span: P0034-P0040
    summary: The man panics, accepts death, freezes, and the dog leaves for camp.
    participants: [the man, the dog]
    location: Yukon trail
    time: twilight
    event_type: death
    certainty: {value: certain}
    narrative_reality_level: {value: real}
causal_edges:
  - edge_id: TF_C01
    story_id: to_build_a_fire
    source_event_id: TF_E01
    target_event_id: TF_E04
    relation_type: enables
    strength: {value: medium}
    evidence_text_span: P0003-P0019
    explanation: The man's lack of imagination and underestimation of cold allow him to continue alone into conditions where a foot-wetting accident becomes lethal.
  - edge_id: TF_C02
    story_id: to_build_a_fire
    source_event_id: TF_E04
    target_event_id: TF_E05
    relation_type: causes
    strength: {value: strong}
    evidence_text_span: P0017-P0023
    explanation: Wet feet in extreme cold require immediate fire-building, creating the high-stakes first attempt.
  - edge_id: TF_C03
    story_id: to_build_a_fire
    source_event_id: TF_E05
    target_event_id: TF_E06
    relation_type: causes
    strength: {value: strong}
    evidence_text_span: P0023-P0030
    explanation: Snow from the spruce destroys the successful fire, forcing a second attempt after the man's hands and feet have worsened.
  - edge_id: TF_C04
    story_id: to_build_a_fire
    source_event_id: TF_E06
    target_event_id: TF_E07
    relation_type: motivates
    strength: {value: strong}
    evidence_text_span: P0030-P0031
    explanation: The failed second fire drives the desperate idea of using the dog's body heat.
  - edge_id: TF_C05
    story_id: to_build_a_fire
    source_event_id: TF_E06
    target_event_id: TF_E08
    relation_type: causes
    strength: {value: strong}
    evidence_text_span: P0030-P0040
    explanation: Failure to restore fire removes the last available survival mechanism.
  - edge_id: TF_C06
    story_id: to_build_a_fire
    source_event_id: TF_E07
    target_event_id: TF_E08
    relation_type: prevents
    strength: {value: medium}
    evidence_text_span: P0031-P0033
    explanation: Frozen hands prevent him from killing the dog or using it as a heat source.
foreshad
...
```
