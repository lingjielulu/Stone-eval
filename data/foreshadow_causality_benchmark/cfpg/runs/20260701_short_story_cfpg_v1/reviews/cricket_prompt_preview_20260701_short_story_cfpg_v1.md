# Short Story CFPG Prompt Preview

## system

```text
你是短篇小说伏笔-触发-回收结构标注员。任务是在给定的全文段落时间线中，高召回抽取候选 Foreshadow-Trigger-Payoff 三元组。只能依据输入文本，不得使用外部知识或你对作品结局的先验记忆。只输出合法 JSON。
```

## user

```text
请对下面的短篇小说段落时间线执行第一步：高召回候选识别。

作品：
- story_id: cricket
- title: 促織
- language: zh

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
[P0001] 宣德間，宮中尚促織之戲，歲征民間。此物故非西產。有華陰令，欲媚上官，以一頭進，試使斗而才，因責常供。令以責之里正。

[P0002] 市中游俠兒，得佳者籠養之，昂其直，居為奇貨。里胥猾黠，假此科斂丁口，每責一頭，輒傾數家之產。

[P0003] 邑有成名者，操童子業，久不售。為人迂訥，遂為猾胥報充里正役，百計營謀不能脫。不終歲，薄產累盡。會征促織，成不敢斂戶口，而又無所賠償，憂悶欲死。妻曰：「死何益？不如自行搜覓，冀有萬一之得。」成然之。早出暮歸，提竹筒銅絲籠，于敗堵叢草處探石發穴，靡計不施，迄無濟。即捕三兩頭，又劣弱，不中于款。宰嚴限追比，旬余，杖至百，兩股間膿血流離，并蟲不能行捉矣。轉側床頭，惟思自盡。時村中來一駝背巫，能以神卜。成妻具資詣問，見紅女白婆，填塞門戶。入其室，則密室垂簾，簾外設香幾。問者爇香于鼎，再拜。巫從旁望空代祝，唇吻翕辟，不知何詞，各各竦立以聽。少間，簾內擲一紙出，即道人意中事，無毫髮爽。成妻納錢案上，焚香以拜。食頃，簾動，片紙拋落。拾視之，非字而畫，中繪殿閣類蘭若，后小山下怪石亂臥，針針叢棘，青麻頭伏焉；旁一蟆，若將跳舞。展玩不可曉。然睹促織，隱中胸懷，折藏之，歸以示成。成反復自念：「得無教我獵蟲所耶？」細矚景狀，與村東大佛閣真逼似。乃強起扶杖，執圖詣寺后，有古陵蔚起。循陵而走，見蹲石鱗鱗，儼然類畫。遂于蒿萊中側聽徐行，似尋針芥，而心、目、耳力俱窮，絕無蹤響。冥搜未已，一癩頭蟆猝然躍去。成益愕，急逐之。蟆入草間，躡跡披求，見有蟲伏棘根，遽撲之，入石穴中。掭以尖草不出，以筒水灌之始出。狀極俊健，逐而得之。審視：巨身修尾，青項金翅。大喜，籠歸，舉家慶賀，雖連城拱璧不啻也。土于盆而養之，蟹白栗黃，備極護愛。留待限期，以塞官責。

[P0004] 成有子九歲，窺父不在，竊發盆，蟲躍躑徑出，迅不可捉。及撲入手，已股落腹裂，斯須就斃。兒懼，啼告母。母聞之，面色灰死，大罵曰：「業根，死期至矣！翁歸，自與汝復算耳！」兒涕而出。未幾成入，聞妻言如被冰雪。怒索兒，兒渺然不知所往；既而，得其尸于井。因而化怒為悲，搶呼欲絕。夫妻向隅，茅舍無煙，相對默然，不復聊賴。

[P0005] 日將暮，取兒藁葬，近撫之，氣息惙然。喜置榻上，半夜復蘇，夫妻心稍慰。但兒神氣癡木，奄奄思睡，成顧蟋蟀籠虛，則氣斷聲吞，亦不復以兒為念，自昏達曙，目不交睫。東曦既駕，僵臥長愁。忽聞門外蟲鳴，驚起覘視，蟲宛然尚在，喜而捕之。一鳴輒躍去，行且速。覆之以掌，虛若無物；手裁舉，則又超而躍。急趁之，折過墻隅，迷其所往。徘徊四顧，見蟲伏壁上。審諦之，短小，黑赤色，頓非前物。成以其小，劣之；惟彷徨瞻顧，尋所逐者。壁上小蟲。忽躍落襟袖間，視之，形若土狗，梅花翅，方首長脛，意似良。喜而收之。將獻公堂，惴惴恐不當意，思試之斗以覘之。

[P0006] 村中少年好事者，馴養一蟲，自名「蟹殼青」，日與子弟角，無不勝。欲居之以為利，而高其直，亦無售者。徑造廬訪成。視成所蓄，掩口胡盧而笑。因出己蟲，納比籠中。成視之，龐然修偉，自增慚怍，不敢與較。少年固強之。顧念：蓄劣物終無所用，不如拚博一笑。因合納斗盆。小蟲伏不動，蠢若木雞。少年又大笑。試以豬鬣毛撩撥蟲須，仍不動。少年又笑。屢撩之，蟲暴怒，直奔，遂相騰擊，振奮作聲。俄見小蟲躍起，張尾伸須，直龁敵領。少年大駭，解令休止。蟲翹然矜鳴，似報主知。成大喜。

[P0007] 方共瞻玩，一雞瞥來，徑進一啄。成駭立愕呼。幸啄不中，蟲躍去尺有咫。雞健進，逐逼之，蟲已在爪下矣。成倉猝莫知所救，頓足失色。旋見雞伸頸擺撲；臨視，則蟲集冠上，力叮不釋。成益驚喜，掇置籠中。

[P0008] 翼日進宰。宰見其小，怒訶成。成述其異，宰不信。試與他蟲斗，蟲盡靡；又試之雞，果如成言。乃賞成，獻諸撫軍。撫軍大悅，以金籠進上，細疏其能。既入宮中，舉天下所貢蝴蝶、螳螂、油利撻、青絲額……一切異狀，遍試之，無出其右者。每聞琴瑟之聲，則應節而舞，益奇之。上大嘉悅，詔賜撫臣名馬衣緞。撫軍不忘所自，無何，宰以「卓異」聞。宰悅，免成役；又囑學使，俾入邑庠。后歲餘，成子精神復舊，自言：「身化促織，輕捷善斗，今始蘇耳。」撫軍亦厚賚成。不數歲，田百頃，樓閣萬椽，牛羊蹄躈各千計。一出門，裘馬過世家焉。

[P0009] 異史氏曰：「天子偶用一物，未必不過此已忘；而奉行者即為定例。加之官貪吏虐，民日貼婦賣兒，更無休止。故天子一跬步皆關民命，不可忽也。第成氏子以蠹貧，以促織富，裘馬揚揚。當其為里正、受撲責時，豈意其至此哉！天將以酬長厚者，遂使撫臣、令尹、并受促織恩蔭。聞之：一人飛升，仙及雞犬。信夫！」

中文辅助译文段落时间线（可能为空；只能辅助理解，gold evidence 仍必须回到原文段落）：
(none)

已有人工标注上下文（可能为空；若存在，只作参考，不要机械复制）：
metadata:
  story_id: cricket
  title: "促織"
  author: "蒲松齡"
  language: zh
  source_text_path: data/foreshadow_causality_benchmark/normalized_texts/cricket.txt
  source_url: https://zh.wikisource.org/wiki/%E8%81%8A%E9%BD%8B%E5%BF%97%E7%95%B0/%E7%AC%AC04%E5%8D%B7
  copyright_status: public_domain
  genre: classical_chinese_fantastic_tale
  length_level: short
  structure_type: [social, symbolic]
annotation_guide:
  focus:
    - 標注皇帝喜好、地方官奉行、里胥科斂、成名家庭破產之間的層級因果。
    - 標注巫圖、蟲、兒子投井、魂化促織和獻蟲成功之間的奇幻回收鏈。
    - 標注結尾「異史氏曰」對制度因果的顯性總結。
  boundary_notes:
    - 兒子魂化促織屬於敘事現實中的奇幻事件，可標為 symbolic 或 real-fantastic，不應強行還原為幻覺。
    - 「皇帝偶用一物」是制度鏈的頂層原因，不是普通背景。
events:
  - event_id: CR_E01
    story_id: cricket
    chapter_or_section: whole_story
    text_span: P0001-P0002
    summary: 宮中崇尚斗促織，地方官為媚上而把進貢壓力層層轉嫁給民間。
    participants: [皇帝, 華陰令, 里正, 里胥, 民戶]
    location: 宮中與華陰
    time: 宣德年間
    event_type: social_pressure
    certainty: {value: certain}
    narrative_reality_level: {value: real}
  - event_id: CR_E02
    story_id: cricket
    chapter_or_section: whole_story
    text_span: P0003
    summary: 成名被充里正役，因無法交促織而破產受杖，妻子求巫得圖。
    participants: [成名, 成妻, 里胥, 縣宰, 駝背巫]
    location: 華陰
    time: 征促織期間
    event_type: social_pressure
    certainty: {value: certain}
    narrative_reality_level: {value: real}
  - event_id: CR_E03
    story_id: cricket
    chapter_or_section: whole_story
    text_span: P0003
    summary: 成名依巫圖到佛閣後尋找，捕得一頭俊健促織。
    participants: [成名, 駝背巫]
    location: 村東大佛閣後
    time: 受圖之後
    event_type: discovery
    certainty: {value: certain}
    narrative_reality_level: {value: real}
  - event_id: CR_E04
    story_id: cricket
    chapter_or_section: whole_story
    text_span: P0004
    summary: 成名九歲兒子偷看促織，失手弄死蟲，恐懼出走並被發現投井。
    participants: [成名之子, 成妻, 成名]
    location: 成名家
    time: 獻蟲前
    event_type: accident
    certainty: {value: certain}
    narrative_reality_level: {value: real}
  - event_id: CR_E05
    story_id: cricket
    chapter_or_section: whole_story
    text_span: P0005
    summary: 兒子復蘇後癡木，成名聽見新蟲鳴，捕得一頭短小但異常敏捷的促織。
    participants: [成名, 成名之子, 成妻]
    location: 成名家
    time: 兒子投井後次日
    event_type: discovery
    certainty: {value: certain}
    narrative_reality_level: {value: real}
  - event_id: CR_E06
    story_id: cricket
    chapter_or_section: whole_story
    text_span: P0006-P0007
    summary: 小促織在斗蟲和遭雞啄時展現異能，證明其非尋常蟲。
    participants: [成名, 少年, 小促織, 雞]
    location: 成名家
    time: 獻官前試斗
    event_type: revelation
    certainty: {value: certain}
    narrative_reality_level: {value: real}
  - event_id: CR_E07
    story_id: cricket
    chapter_or_section: whole_story
    text_span: P0008
    summary: 小促織被獻給縣宰、撫軍和宮中，屢試皆勝，成名因此免役入庠並致富。
    participants: [成名, 縣宰, 撫軍, 皇帝, 小促織]
    location: 縣衙、撫軍、宮中
    time: 獻蟲後
    event_type: revelation
    certainty: {value: certain}
    narrative_reality_level: {value: real}
  - event_id: CR_E08
    story_id: cricket
    chapter_or_section: whole_story
    text_span: P0008
    summary: 成名之子恢復精神，自述自己曾魂化促織。
    participants: [成名之子, 成名]
    location: 成名家
    time: 獻蟲成功後一年多
    event_type: revelation
    certainty: {value: certain}
    narrative_reality_level: {value: symbolic}
  - event_id: CR_E09
    story_id: cricket
    chapter_or_section: whole_story
    text_span: P0009
    summary: 異史氏總結天子一時喜好如何經由官貪吏虐關係到民命。
    participants: [異史氏]
    location: narrator_commentary
    time: 敘事結尾
    event_type: revelation
    certainty: {value: certain}
    narrative_reality_level: {value: narrated}
causal_edges:
  - edge_id: CR_C01
    story_id: cricket
    source_event_id: CR_E01
    target_event_id: CR_E02
    relation_type: causes
    strength: {value: strong}
    evidence_text_span: P0001-P0003
    explanation: 宮中需求經地方官和胥吏傳導，直接造成成名家庭承擔促織徵收壓力。
  - edge_id: CR_C02
    story_id: cricket
    source_event_id: CR_E02
    target_event_id: CR_E03
    relation_type: motivates
    strength: {value: strong}
    evidence_text_span: P0003
    explanation: 成名被逼到無法脫身，妻子求巫和成名按圖尋蟲都是危機下的求生行動。
  - edge_id: CR_C03
    story_id: cricket
    source_event_id: CR_E03
    target_event_id: CR_E04
    relation_type: enables
    strength: {value: medium}
    evidence_text_span: P0003-P0004
    explanation: 捕得佳蟲使家庭暫有解困希望，也使兒子偷看和弄死蟲成為可能。
  - edge_id: CR_C04
    story_id: cricket
    source_event_id: CR_E04
    target_event_id: CR_E05
    relation_type: causes
    strength: {value: strong}
    evidence_text_span: P0004-P0005
    explanation: 兒子投井與失蟲危機引出後續新蟲出現和兒子神氣癡木的奇幻轉折。
  - edge_id: CR_C05
    story_id: cricket
    source_event_id: CR_E05
    target_event_id: CR_E06
    relation_type: enables
    strength: {value: strong}
    evidence_text_span: P0005-P0007
    explanation: 新小促織被捕後，才有試斗和對雞反擊，揭示其超常能力。
  - edge_id: CR_C06
    story_id: cricket
    source_event_id: CR_E06
    target_event_id: CR_E07
    relation_type: causes
    strength: {value: strong}
    evidence_text_span: P0006-P0008
    explanation: 小促織屢試皆勝，使縣宰和撫軍相信其價值並層層進獻。
  - edge_id: CR_C07
    story_id: cricket
    source_event_id: CR_E08
    target_event_id: CR_E05
    relation_type: reveals
    strength: {value: strong}
    evidence_text_span: P0005-P0008
    explanation: 兒子自述魂化促織，回頭解釋新蟲的出現和異能。
  - edge_id: CR_C08
    story_id: cricket
    source_event_id: CR_E01
    target_event_id: CR_E09
    relation_type: reveals
    strength: {value: strong}
    evidence_text_span: P0001-P0009
    explanation: 故事末尾的評論明確揭示頂層喜好和基層苦難之間的制度因果。
foreshadowing_units:
  - foreshadowing_id: CR_F01
    story_id: cricket
    foreshadowing_text_span: P0001-P0002
    foreshadowing_summary: 宮中斗促織和地方徵收建立全篇制度規則。
    foreshadowing_type: social
    trigger_event_id: CR_E02
    payoff_event_id: CR_E09
    payoff_text_span: P0009
    payoff_summary: 異史氏明確回收「天子一跬步皆關民命」的制度因果。
    payoff_type: symbolic
    confidence: {value: high}
    explanation: 開篇制度壓力在結尾被概括為民命受權力任意性牽動。
  - foreshadowing_id: CR_F02
    story_id: cricket
    foreshadowing_text_span: P0003
    foreshadowing_summary: 巫圖中的殿閣、怪石、棘叢、青麻頭和蟆指向尋蟲地點。
    foreshadowing_type: symbolic
    trigger_event_
...
```
