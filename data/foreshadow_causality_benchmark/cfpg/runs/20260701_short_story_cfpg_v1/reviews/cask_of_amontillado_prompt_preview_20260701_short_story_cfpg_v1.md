# Short Story CFPG Prompt Preview

## system

```text
你是短篇小说伏笔-触发-回收结构标注员。任务是在给定的全文段落时间线中，高召回抽取候选 Foreshadow-Trigger-Payoff 三元组。只能依据输入文本，不得使用外部知识或你对作品结局的先验记忆。只输出合法 JSON。
```

## user

```text
请对下面的短篇小说段落时间线执行第一步：高召回候选识别。

作品：
- story_id: cask_of_amontillado
- title: The Cask Of Amontillado
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
[P0001] The thousand injuries of Fortunato I had borne as I best could; but when he ventured upon insult, I vowed revenge. You, who so well know the nature of my soul, will not suppose, however, that I gave utterance to a threat. _At length_ I would be avenged; this was a point definitively settled—but the very definitiveness with which it was resolved, precluded the idea of risk. I must not only punish, but punish with impunity. A wrong is unredressed when retribution overtakes its redresser. It is equally unredressed when the avenger fails to make himself felt as such to him who has done the wrong.

[P0002] It must be understood, that neither by word nor deed had I given Fortunato cause to doubt my good will. I continued, as was my wont, to smile in his face, and he did not perceive that my smile _now_ was at the thought of his immolation.

[P0003] He had a weak point—this Fortunato—although in other regards he was a man to be respected and even feared. He prided himself on his connoisseurship in wine. Few Italians have the true virtuoso spirit. For the most part their enthusiasm is adopted to suit the time and opportunity—to practise imposture upon the British and Austrian _millionaires_. In painting and gemmary, Fortunato, like his countrymen, was a quack—but in the matter of old wines he was sincere. In this respect I did not differ from him materially: I was skilful in the Italian vintages myself, and bought largely whenever I could.

[P0004] It was about dusk, one evening during the supreme madness of the carnival season, that I encountered my friend. He accosted me with excessive warmth, for he had been drinking much. The man wore motley. He had on a tight-fitting parti-striped dress, and his head was surmounted by the conical cap and bells. I was so pleased to see him, that I thought I should never have done wringing his hand.

[P0005] I said to him: “My dear Fortunato, you are luckily met. How remarkably well you are looking to-day! But I have received a pipe of what passes for Amontillado, and I have my doubts.”

[P0006] “How?” said he. “Amontillado? A pipe? Impossible! And in the middle of the carnival!”

[P0007] “I have my doubts,” I replied; “and I was silly enough to pay the full Amontillado price without consulting you in the matter. You were not to be found, and I was fearful of losing a bargain.”

[P0008] “Amontillado!”

[P0009] “I have my doubts.”

[P0010] “Amontillado!”

[P0011] “And I must satisfy them.”

[P0012] “Amontillado!”

[P0013] “As you are engaged, I am on my way to Luchesi. If any one has a critical turn, it is he. He will tell me—”

[P0014] “Luchesi cannot tell Amontillado from Sherry.”

[P0015] “And yet some fools will have it that his taste is a match for your own.”

[P0016] “Come, let us go.”

[P0017] “Whither?”

[P0018] “To your vaults.”

[P0019] “My friend, no; I will not impose upon your good nature. I perceive you have an engagement. Luchesi—”

[P0020] “I have no engagement;—come.”

[P0021] “My friend, no. It is not the engagement, but the severe cold with which I perceive you are afflicted. The vaults are insufferably damp. They are encrusted with nitre.”

[P0022] “Let us go, nevertheless. The cold is merely nothing. Amontillado! You have been imposed upon. And as for Luchesi, he cannot distinguish Sherry from Amontillado.”

[P0023] Thus speaking, Fortunato possessed himself of my arm. Putting on a mask of black silk, and drawing a _roquelaire_ closely about my person, I suffered him to hurry me to my palazzo.

[P0024] There were no attendants at home; they had absconded to make merry in honor of the time. I had told them that I should not return until the morning, and had given them explicit orders not to stir from the house. These orders were sufficient, I well knew, to insure their immediate disappearance, one and all, as soon as my back was turned.

[P0025] I took from their sconces two flambeaux, and giving one to Fortunato, bowed him through several suites of rooms to the archway that led into the vaults. I passed down a long and winding staircase, requesting him to be cautious as he followed. We came at length to the foot of the descent, and stood together on the damp ground of the catacombs of the Montresors.

[P0026] The gait of my friend was unsteady, and the bells upon his cap jingled as he strode.

[P0027] “The pipe,” said he.

[P0028] “It is farther on,” said I; “but observe the white web-work which gleams from these cavern walls.”

[P0029] He turned towards me, and looked into my eyes with two filmy orbs that distilled the rheum of intoxication.

[P0030] “Nitre?” he asked, at length.

[P0031] “Nitre,” I replied. “How long have you had that cough?”

[P0032] “Ugh! ugh! ugh!—ugh! ugh! ugh!—ugh! ugh! ugh!—ugh! ugh! ugh!—ugh! ugh! ugh!”

[P0033] My poor friend found it impossible to reply for many minutes.

[P0034] “It is nothing,” he said, at last.

[P0035] “Come,” I said, with decision, “we will go back; your health is precious. You are rich, respected, admired, beloved; you are happy, as once I was. You are a man to be missed. For me it is no matter. We will go back; you will be ill, and I cannot be responsible. Besides, there is Luchesi—”

[P0036] “Enough,” he said; “the cough is a mere nothing; it will not kill me. I shall not die of a cough.”

[P0037] “True—true,” I replied; “and, indeed, I had no intention of alarming you unnecessarily—but you should use all proper caution. A draught of this Medoc will defend us from the damps.”

[P0038] Here I knocked off the neck of a bottle which I drew from a long row of its fellows that lay upon the mould.

[P0039] “Drink,” I said, presenting him the wine.

[P0040] He raised it to his lips with a leer. He paused and nodded to me familiarly, while his bells jingled.

[P0041] “I drink,” he said, “to the buried that repose around us.”

[P0042] “And I to your long life.”

[P0043] He again took my arm, and we proceeded.

[P0044] “These vaults,” he said, “are extensive.”

[P0045] “The Montresors,” I replied, “were a great and numerous family.”

[P0046] “I forget your arms.”

[P0047] “A huge human foot d’or, in a field azure; the foot crushes a serpent rampant whose fangs are imbedded in the heel.”

[P0048] “And the motto?”

[P0049] “_Nemo me impune lacessit_.”

[P0050] “Good!” he said.

[P0051] The wine sparkled in his eyes and the bells jingled. My own fancy grew warm with the Medoc. We had passed through walls of piled bones, with casks and puncheons intermingling, into the inmost recesses of the catacombs. I paused again, and this time I made bold to seize Fortunato by an arm above the elbow.

[P0052] “The nitre!” I said: “see, it increases. It hangs like moss upon the vaults. We are below the river’s bed. The drops of moisture trickle among the bones. Come, we will go back ere it is too late. Your cough—”

[P0053] “It is nothing,” he said; “let us go on. But first, another draught of the Medoc.”

[P0054] I broke and reached him a flagon of De Grâve. He emptied it at a breath. His eyes flashed with a fierce light. He laughed and threw the bottle upwards with a gesticulation I did not understand.

[P0055] I looked at him in surprise. He repeated the movement—a grotesque one.

[P0056] “You do not comprehend?” he said.

[P0057] “Not I,” I replied.

[P0058] “Then you are not of the brotherhood.”

[P0059] “How?”

[P0060] “You are not of the masons.”

[P0061] “Yes, yes,” I said, “yes, yes.”

[P0062] “You? Impossible! A mason?”

[P0063] “A mason,” I replied.

[P0064] “A sign,” he said.

[P0065] “It is this,” I answered, producing a trowel from beneath the folds of my _roquelaire_.

[P0066] “You jest,” he exclaimed, recoiling a few paces. “But let us proceed to the Amontillado.”

[P0067] “Be it so,” I said, replacing the tool beneath the cloak, and again offering him my arm. He leaned upon it heavily. We continued our route in search of the Amontillado. We passed through a range of low arches, descended, passed on, and descending again, arrived at a deep crypt, in which the foulness of the air caused our flambeaux rather to glow than flame.

[P0068] At the most remote end of the crypt there appeared another less spacious. Its walls had been lined with human remains, piled to the vault overhead, in the fashion of the great catacombs of Paris. Three sides of this interior crypt were still ornamented in this manner. From the fourth the bones had been thrown down, and lay promiscuously upon the earth, forming at one point a mound of some size. Within the wall thus exposed by the displacing of the bones, we perceived a still interior recess, in depth about four feet, in width three, in height six or seven. It seemed to have been constructed for no especial use in itself, but formed merely the interval between two of the colossal supports of the roof of the catacombs, and was backed by one of their circumscribing walls of solid granite.

[P0069] It was in vain that Fortunato, uplifting his dull torch, endeavored to pry into the depths of the recess. Its termination the feeble light did not enable us to see.

[P0070] “Proceed,” I said; “herein is the Amontillado. As for Luchesi—”

[P0071] “He is an ignoramus,” interrupted my friend, as he stepped unsteadily forward, while I followed immediately at his heels. In an instant he had reached the extremity of the niche, and finding his progress arrested by the rock, stood stupidly bewildered. A moment more and I had fettered him to the granite. In its surface were two iron staples, distant from each other about two feet, horizontally. From one of these depended a short chain, from the other a padlock. Throwing the links about his waist, it was but the work of a few seconds to secure it. He was too much astounded to resist. Withdrawing the key I stepped back from the recess.

[P0072] “Pass your hand,” I said, “over the wall; you cannot help feeling the nitre. Indeed it is _very_ damp. Once more let me _implore_ you to return. No? Then I must positively leave you. But I must first render you all the little attentions in my power.”

[P0073] “The Amontillado!” ejaculated my friend, not yet recovered from his astonishment.

[P0074] “True,” I replied; “the Amontillado.”

[P0075] As I said these words I busied myself among the pile of bones of which I have before spoken. Throwing them aside, I soon uncovered a quantity of building stone and mortar. With these materials and with the aid of my trowel, I began vigorously to wall up the entrance of the niche.

[P0076] I had scarcely laid the first tier of my masonry when I discovered that the intoxication of Fortunato had in a great measure worn off. The earliest indication I had of this was a low moaning cry from the depth of the recess. It was _not_ the cry of a drunken man. There was then a long and obstinate silence. I laid the second tier, and the third, and the fourth; and then I heard the furious vibrations of the chain. The noise lasted for several minutes, during which, that I might hearken to it with the more satisfaction, I ceased my labors and sat down upon the bones. When at last the clanking subsided, I resumed the trowel, and finished without interruption the fifth, the sixth, and the seventh tier. The wall was now nearly upon a level with my breast. I again paused, and holding the flambeaux over the mason-work, threw a few feeble rays upon the figure within.

[P0077] A succession of loud and shrill screams, bursting suddenly from the throat of the chained form, seemed to thrust me violently back. For a brief moment I hesitated—I trembled. Unsheathing my rapier, I began to grope with it about the recess; but the thought of an instant reassured me. I placed my hand upon the solid fabric of the catacombs, and felt satisfied. I reapproached the wall. I replied to the yells of him who clamored. I re-echoed—I aided—I surpassed them in volume and in strength. I did this, and the clamorer grew still.

[P0078] It was now midnight, and my task was drawing to a close. I had completed the eighth, the ninth, and the tenth tier. I had finished a portion of the last and the eleventh; there remained but a single stone to be fitted and plastered in. I struggled with its weight; I placed it partially in its destined position. But now there came from out the niche a low laugh that erected the hairs upon my head. It was succeeded by a sad voice, which I had difficulty in recognising as that of the noble Fortunato. The voice said—

[P0079] “Ha! ha! ha!—he! he!—a very good joke indeed—an excellent jest. We will have many a rich laugh about it at the palazzo—he! he! he!—over our wine—he! he! he!”

[P0080] “The Amontillado!” I said.

[P0081] “He! he! he!—he! he! he!—yes, the Amontillado. But is it not getting late? Will not they be awaiting us at the palazzo, the Lady Fortunato and the rest? Let us be gone.”

[P0082] “Yes,” I said, “let us be gone.”

[P0083] “_For the love of God, Montressor!_”

[P0084] “Yes,” I said, “for the love of God!”

[P0085] But to these words I hearkened in vain for a reply. I grew impatient. I called aloud—

[P0086] “Fortunato!”

[P0087] No answer. I called again—

[P0088] “Fortunato!”

[P0089] No answer still. I thrust a torch through the remaining aperture and let it fall within. There came forth in return only a jingling of the bells. My heart grew sick—on account of the dampness of the catacombs. I hastened to make an end of my labor. I forced the last stone into its position; I plastered it up. Against the new masonry I re-erected the old rampart of bones. For the half of a century no mortal has disturbed them. _In pace requiescat!_

中文辅助译文段落时间线（可能为空；只能辅助理解，gold evidence 仍必须回到原文段落）：
[P0001] 对福尔图纳托加于我的无数次伤害，我过去一直都尽可能地一忍了之；可当那次他斗胆侮辱了我，我就立下了以牙还牙的誓言。你对我的脾性了如指掌，无论如何也不会认为我的威胁是虚张声势。我总有一天会报仇雪恨；这是一个明确设立的目标——正是设立这目标之明确性消除了我对危险的顾虑。我不仅非要惩罚他不可，而且必须做到惩罚他之后我自己不受惩罚。若是复仇者自己受到了惩罚，那就不能算已报仇雪恨。若是复仇者没让那作恶者知道是谁在报复，那同样也不能算是报仇雪恨。

[P0002] 不言而喻，到当时为止我的一言一行都不曾让福尔图纳托怀疑过我居心叵测。我一如既往地冲他微笑，而他丝毫没看出当时我的微笑已是笑里藏刀。

[P0003] 他有一个弱点——我是说福尔图纳托——尽管他在其他方面可以说是个值得尊敬乃至值得敬畏的人。他吹嘘说他是个品酒的行家。很少有意大利人真正具有鉴赏家的气质。大概他们的热情多半都被用来寻机求缘，见风使舵——蒙骗那些英格兰和奥地利富翁。在名画和珠宝方面，福尔图纳托和他的同胞一样是个冒充内行的骗子 ——不过说到陈年老酒，他可是识货的里手行家。在这方面我与他相去无几：我自己对意大利名葡萄酒十分在行，一有机会总是大量买进。

[P0004] 那是在狂欢节高潮期的一天傍晚，当薄暮降临之时我遇见了我那位朋友。他非常亲热地与我搭话，因为他酒已经喝得不少。那家伙装扮成一个小丑，身穿有杂色条纹的紧身衣，头戴挂有戏铃的圆锥形便帽。我当时是那么乐意见到他，以致于我认为可能我从来不曾那样热烈地与他握过手。

[P0005] 我对他说——“我亲爱的福尔图纳托，碰见你真是不胜荣幸。你今天的气色看上去真是好极了！可我刚买进了一大桶据认为是蒙特亚产的白葡萄酒， 而我对此没有把握。”

[P0006] “怎么会？”他说。“蒙特亚白葡萄酒？一大桶？不可能！尤其在这狂欢节期间！”

[P0007] “我也感到怀疑，”我答道，“我真傻，居然没向你请教就照蒙特亚酒的价格付了钱。当时没找到你，而我生怕错过了一笔买卖。”

[P0008] “蒙特亚酒！”

[P0009] “我拿不准。”

[P0010] “蒙特亚酒！”

[P0011] “我非弄清楚不可。”

[P0012] “蒙特亚酒！”

[P0013] “因为你忙，我这正想去找卢切西。如果说还有人能分出真假，那就是他。他会告诉我——”

[P0014] “卢切西不可能分清蒙特亚酒和雪利酒。”

[P0015] “可有些傻瓜说他的本事与你不相上下。”

[P0016] “得啦，咱们走吧。”

[P0017] “上哪儿？”

[P0018] “去你家地窖。”

[P0019] “我的朋友，这不行；我不想利用你的好心。我看出你有个约会。卢切西——”

[P0020] “我没什么约会；——走吧。”

[P0021] “我的朋友，这不行。原因倒不在于你有没有约会，而是我看你正冷得够呛。我家地窖潮湿不堪。窖洞里到处都结满了硝石。”

[P0022] “可咱们还是走吧。这冷算不了什么。蒙特亚酒！你肯定被人蒙了。至于卢切西，他辨不出啥是雪利酒啥是蒙特亚酒。”

[P0023] 福尔图纳托一边说一边拉住我一条胳膊。我戴上黑绸面具，裹紧身上的短披风，然后容他催着我回我的府邸。

[P0024] 家里不见一个仆人；他们早就溜出门狂欢去了。我告诉过他们我要第二天早晨才回家，并明确地命令他们不许外出。我清楚地知道，这命令足以保证他们等我一转背就溜个精光。

[P0025] 我从他们的火台上取了两支火把，将其中一支递给福尔图纳托，然后点头哈腰地领他穿过几套房间，走向通往地窖的拱廊。我走下一段长长的盘旋式阶梯，一路提醒着紧随我后边的他多加小心。我们终于下完阶梯，一起站在了蒙特雷索家酒窖兼墓窖的湿地上。

[P0026] 我朋友的步态不甚平稳，每走一步他帽子上的戏铃都丁当作响。

[P0027] “那桶酒呢？”他问。

[P0028] “在前面，”我说，“可请看洞壁上这些白花花的网状物。”

[P0029] 他转身朝向我，用他那双因中酒而渗出粘液的朦胧醉眼窥视我的眼睛。

[P0030] “硝石？”他终于问道。

[P0031] “硝石。”我回答。“你这样咳嗽有多久了？”

[P0032] “咳！咳！咳！——咳！咳！咳！——咳！咳！咳！——咳！咳！咳！——咳！咳！咳！”

[P0033] 我可怜的朋友好几分钟内没法回答。

[P0034] “这没什么。”他最后终于说。

[P0035] “喂，”我断然说道，“咱们回去吧；你的健康要紧。你有钱，体面，有人敬慕，受人爱戴；你真幸运，就像我从前一样。你应该多保重。至于我，这倒无所谓。咱们回去吧；你会生病的，要那样我可担待不起。再说，还有卢切西——”

[P0036] “别再说了，”他道，“咳嗽算不了什么；它不会要我的命。我也不会死于咳嗽。”

[P0037] “当然——当然，”我答道，“其实我也无意这么不必要地吓唬你——不过你应该尽量小心谨慎。咱们来点梅多克红葡萄酒去去潮吧。”

[P0038] 说完我从堆放在窖土上的一长溜酒瓶中抽出一瓶，敲掉了瓶嘴。

[P0039] “喝吧。”我说着把酒递给他。

[P0040] 他睨视了我一眼，把酒瓶凑到嘴边。接着他停下来朝我亲热地点了点头，他帽子上的戏铃随之丁当作响。

[P0041] “我为安息在我们周围的死者们干杯。”他说。

[P0042] “我为你的长寿干杯。”

[P0043] 他再次挽起我的胳膊，我们继续往前走。

[P0044] “这些地窖，”他说，“可真大。”

[P0045] “蒙特雷索家是个人丁兴旺的大家族。”我回答说。

[P0046] “我记不起你家的纹章图案了。”

[P0047] “蓝色的底衬上一只金色的大脚；金脚正把一条毒牙咬进脚后跟的巨蛇踩得粉身碎骨。”

[P0048] “那纹章上的铭词呢？”

[P0049] “凡伤我者必受惩罚。”

[P0050] “妙！”他说。

[P0051] 酒在他的眼睛里闪耀，那些戏铃越发丁零当郎。我自己的想象力也因梅多克酒而兴奋起来。我们已经穿过由尸骨和大小酒桶堆成的一道道墙，来到了地窖的幽深之处。我又停了下来，这回还不揣冒昧地抓住了福尔图纳托的上臂。

[P0052] “硝石！”我说，“瞧，越来越多了，就像苔藓挂在窖顶。我们是在河床的下面。水珠正滴在尸骨间。喂，咱们回去吧，趁现在还来得及，你的咳嗽——”

[P0053] “这没什么，”他说，“我们继续走吧。不过先再来瓶梅多克酒。”

[P0054] 我开了一小瓶格拉夫白葡萄酒递给他。他把酒一饮而尽。他眼里闪出一种可怕的目光。他一阵哈哈大笑，并且用一种令我莫名其妙的手势把酒瓶往上一抛。

[P0055] 我诧异地盯着他。他又重复了那个手势——一个古怪的手势。

[P0056] “你不懂？”他问。

[P0057] “我不懂。”我答。

[P0058] “那你就不是哥儿们。”

[P0059] “什么？”

[P0060] “你就不是个mason。”

[P0061] “我是的，”我说，“是的，是的。”

[P0062] “你？不可能！一个mason？”

[P0063] “一个masorn。”我回答。

[P0064] “给个暗号。”他说。

[P0065] “这就是。”我一边回答一边从我短披风的褶层下取出一把泥刀。

[P0066] “你在开玩笑，”他惊叫一声并往后退了几步。“不过咱们还是去看那桶蒙特亚酒吧。”

[P0067] “这样也好。”我说着把泥刀重新放回披风下面，又伸出胳膊让他挽住。他重重地靠在了我胳臂上。我们继续往前去找那桶蒙特亚酒。我们穿过了一连串低矮的拱道，向下，往前，再向下，最后进了一个幽深的墓穴，里边混浊的空气使我们的火把只冒火苗而不发光亮。

[P0068] 这个墓穴的远端连着另一个更小的墓穴，里面曾一直顺墙排满尸骨，照巴黎那些大墓窟的样子一直推到拱顶。当时这小墓穴有三面墙依然照原样陈列着骨骸，可沿第四面墙堆放的尸骨已被推倒，乱七八糟地铺在地上，有一处形成了一个骨堆。在这面因推倒尸骨而暴露出来的墙上，我们看到了一个更小的凹洞，大约有四英尺深，三英尺宽，六七英尺高。这凹洞看上去仿佛当初被建造时就没派什么特别用场，不过是窖顶两边庞大的支撑体间一个小小的空隙，它的里端是一道坚硬的花岗岩石壁。

[P0069] 福尔图纳托举起他手中昏暗的火把，尽力窥视凹洞深处，可他枉费了一番心机。微弱的火光没法让我们看清凹洞里端。“进去吧，”我说，“那桶蒙特亚酒就在里面。至于说卢切西——”

[P0070] “他是个笨蛋！”我朋友打断我的话，偏偏倒倒朝里走去，而我则跟着他寸步不离。眨眼之间他已走到凹洞尽头，发现去路被石墙挡住；他正傻乎乎地站在那儿发愣，我已用锁链把他锁在了那道花岗石墙上。原来石壁上嵌着两颗U形大铁钉，两钉平行相距约两英尺。一颗钉上垂着一条不长的铁链，另一颗上则悬着一把挂锁。将那根铁链绕过他腰间再把链端牢牢锁上，这不过是几秒钟内的事。他当时惊得没有反抗。我抽出钥匙，退出了凹洞。

[P0071] “伸手摸摸墙，”我站在洞口说，“你肯定会摸到硝石。这儿的确太潮了。请允许我再次求你回去。你不？那我当然得留下你了。不过我先得尽力稍稍侍候你一番。”

[P0072] “蒙特亚酒！”我朋友脱口而出，他当时还没回过神来。

[P0073] “当然，”我说，“蒙特亚酒。”

[P0074] 说着话我已经在我刚才提到的那个骨堆上忙活开了。我把骨骸一块块抛到一边，下面很快就露出了不少砌墙用的石块和灰泥。用这些材料并凭借我那把泥刀，我开始干劲十足地砌墙封那个洞口。

[P0075] 我连第一层石块都还没砌好就发现福尔图纳托酒已醒了一大半。我最初知道这一点是因为凹洞深处传来一声低低的悲号。那不是一个醉汉发出的声音。接下来便是一阵长长的、令人难耐的寂静。我一连砌好了第二层、第三层和第四层；这时我听见了那根铁链猛烈的震动声。声音延续了好几分钟，为了听得更称心如意，这几分钟里我停止干活，坐在了骨堆上。等那阵当啷声终于平静下来，我才又重新拿起泥刀，一口气砌完了第五层、第六层和第七层。这时墙已差不多齐我胸高。我又歇了下来，将火把举过新砌的墙头，把一点微弱的光线照射到里边那个身影上。

[P0076] 突然，一串凄厉的尖叫声从那被锁住的人影嗓子里冒出，仿佛是猛地将我朝后推了—把。我一时间趑趄不前——我浑身发抖。随后我拔出佩剑，伸进凹洞里四下探戳；但转念一想我又安下心来，伸手摸摸那墓洞坚固的结构，我完全消除了内心的恐惧。我重新回到墙前，一声声地回应那个人的尖叫：我应着他叫——我帮着他叫 ——我的音量和力度都压过了他的叫声。我这么一叫，那尖叫者反倒渐渐哑了。

[P0077] 此时已深更半夜，我的活儿也接近尾声。我已经砌完了第八层、第九层和第十层。现在最后的第十一层也快完工，只剩下最后一块石头没砌上并抹灰。我使劲儿搬起这块沉甸甸的石头，将其一角搁上它预定的位置。可就在这时，凹洞里突然传出一阵令我毛发倒立的惨笑，紧接着又传出一个悲哀的声音，我好不容易才听出那是高贵的福尔图纳托在说话。那声音说——

[P0078] “哈！哈！哈！——嘿！嘿！——真是个有趣的玩笑——一个绝妙的玩笑。待会儿回到屋里，我们准会笑个痛快——嘿！嘿！嘿！——边喝酒边笑——嘿！嘿！嘿！”

[P0079] “蒙特亚酒！”我说。

[P0080] “嘿！嘿！嘿！——嘿！嘿！嘿！——对，蒙特亚酒。可天是不是太晚了？难道他们不正在屋里等咱们吗，福尔图纳托夫人和其他人？咱们去吧。”

[P0081] “对，”我说，“咱们去吧。”

[P0082] “看在上帝分上，蒙特雷索！”

[P0083] “对，”我说，“看在上帝分上。”

[P0084] 可说完这句话之后我怎么听也听不到回声。我渐渐沉不住气了，便大声喊道——

[P0085] “福尔图纳托！”

[P0086] 没有回答。我再喊——

[P0087] “福尔图纳托！”

[P0088] 还是没有回答。于是我将一支火把伸进那个尚未砌上的墙孔，并任其掉了下去。传出来的回声只是那些戏铃的一阵丁当，我开始感到恶心——由于地窖里潮湿的缘故。我赶紧干完我那份活儿，把最后一块石头塞进它的位置并抹好泥灰。靠着新砌的那堵石墙我重新竖起了原来那道尸骨组成的护壁。半个世纪以来没人再动过那些尸骨。愿亡灵安息！

已有人工标注上下文（可能为空；若存在，只作参考，不要机械复制）：
(none)
```
