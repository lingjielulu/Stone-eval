#!/usr/bin/env python3
"""
红楼梦价值转化图生成脚本

基于 BookSum 摘要时间线 + 已验证 F-T-P 三元组，通过 LLM 识别关键价值转化场景，
生成符合 honglou_schema.py 的结构化脚本 JSON。

Usage:
    python foreshadow/honglou/scripts/build_honglou_value_graph.py                    # 使用默认路径
    python foreshadow/honglou/scripts/build_honglou_value_graph.py --force             # 强制重新生成
    python foreshadow/honglou/scripts/build_honglou_value_graph.py --max-scenes 40     # 限制场景数
    python foreshadow/honglou/scripts/build_honglou_value_graph.py --dry-run           # 预览不生成
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import click
from dotenv import load_dotenv
from openai import OpenAI

# Add project root to path
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from foreshadow.honglou.common.honglou_value_graph_schema import (
    NodeType,
    NPC, Item, Relationship, Region,
    SceneNode, TransitionNode, EndingNode,
    HonglouStructuredScript,
    build_linear_chain, validate_script,
)

load_dotenv()

# ============================================================
# Paths
# ============================================================
DATA_DIR = REPO_ROOT / "foreshadow" / "honglou" / "results" / "cfpg"
OUTPUT_DIR = REPO_ROOT / "foreshadow" / "honglou" / "results" / "value_graph"

SUMMARY_JSONL = DATA_DIR / "honglou_booksum" / "original_80_chapter_summaries.jsonl"
TIMELINE_JSONL = DATA_DIR / "summary_alignments" / "original_80_summary_sentence_timeline_20260611_deepseek_honglou_original80.jsonl"
FTP_JSONL = DATA_DIR / "verified" / "honglou_ftp_triples_20260611_deepseek_honglou_original80.jsonl"


# ============================================================
# Helpers
# ============================================================

def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"Missing: {path}")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").strip().splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


# ============================================================
# LLM API
# ============================================================

def create_client() -> OpenAI:
    return OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
        base_url=os.environ.get("OPENAI_BASE_URL"),
    )


def call_llm(
    client: OpenAI,
    system: str,
    user: str,
    model: str = "deepseek-v4-pro",
    temperature: float = 0.2,
    max_retries: int = 3,
) -> Optional[dict]:
    for attempt in range(max_retries):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=temperature,
                response_format={"type": "json_object"},
            )
            content = resp.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            print(f"  LLM call attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    print("  LLM call exhausted retries.")
    return None


# ============================================================
# Stage 1: Build static assets (NPCs, Items, Relations, Regions)
# ============================================================

def build_static_npcs() -> list[NPC]:
    """构建核心角色列表（金陵十二钗正册 + 关键配角）。"""
    return [
        NPC(name="贾宝玉", role="主角, 神瑛侍者转世",
            appearance="面若中秋之月，色如春晓之花，鬓若刀裁，眉如墨画。项上金螭璎珞圈，系着一块美玉。",
            background="荣国府贾政次子，衔通灵宝玉而生。天生痴情，厌恶仕途经济，独爱女儿洁净世界。",
            character="情不情——对无情之物亦有情。任性、痴狂、叛逆礼教，厌恶禄蠹。",
            abilities=["诗词", "品茶", "胭脂膏子制作", "参禅悟道"],
            secrets=["衔玉而生的来历", "梦中太虚幻境的见闻"],
            fate_arc="从富贵公子到看破红尘出家",
            poem_prophecy="无故寻愁觅恨，有时似傻如狂"),
        NPC(name="林黛玉", role="主角, 绛珠仙草转世, 金陵十二钗正册",
            appearance="两弯似蹙非蹙罥烟眉，一双似喜非喜含情目。态生两靥之愁，娇袭一身之病。",
            background="林如海之女，贾母外孙女。母贾敏早逝，进京依贾府。以还泪报恩，天生诗人气质。",
            character="敏感多疑，才华横溢，孤标傲世。深情而自尊，以诗为命。",
            abilities=["诗词冠绝群芳", "琴艺", "棋艺", "参禅"],
            secrets=["对宝玉的深情", "对自己的命运预感"],
            fate_arc="泪尽而亡——从寄人篱下到焚稿断痴情",
            poem_prophecy="玉带林中挂，金簪雪里埋"),
        NPC(name="薛宝钗", role="金陵十二钗正册",
            appearance="唇不点而红，眉不画而翠，脸若银盆，眼如水杏。肌肤丰泽，举止娴雅。",
            background="薛家之女，薛蟠之妹。进京待选，长住贾府。佩金锁，上有‘不离不弃，芳龄永继’八字。",
            character="稳重和平，博学多识，恪守礼教规训。是封建淑女的完美典范。",
            abilities=["博学广识", "处世周全", "绘画鉴赏", "药理"],
            secrets=["对宝玉的情愫", "金锁与通灵宝玉的‘金玉良缘’"],
            fate_arc="金玉良缘成空——从待选才人到独守空闺",
            poem_prophecy="可叹停机德，堪怜咏絮才"),
        NPC(name="王熙凤", role="金陵十二钗正册",
            appearance="一双丹凤三角眼，两弯柳叶吊梢眉。身量苗条，体格风骚。粉面含春威不露。",
            background="荣国府管家媳妇，贾琏之妻。精明强干，掌管府中大小事务。",
            character="嘴甜心苦，两面三刀。有才亦有毒，能笑里藏刀。",
            abilities=["管家理财", "口才", "权术", "识人"],
            secrets=["放高利贷", "弄权铁槛寺", "逼死尤二姐"],
            fate_arc="从权倾府中到机关算尽反误卿命",
            poem_prophecy="一从二令三人木，哭向金陵事更哀"),
        NPC(name="贾元春", role="金陵十二钗正册",
            appearance="凤冠霞帔，贵气逼人。",
            background="贾政长女，入宫为妃，加封贤德妃。元宵省亲是贾府鼎盛的顶点。",
            character="深宫寂寞，思念家人。将大观园留给弟弟妹妹。",
            abilities=["宫廷礼仪", "诗书"],
            secrets=["宫中的悲苦", "家族衰败的预感"],
            fate_arc="从荣升贵妃到暴病薨逝",
            poem_prophecy="虎兕相逢大梦归"),
        NPC(name="贾探春", role="金陵十二钗正册",
            appearance="削肩细腰，长挑身材，鸭蛋脸儿，俊眼修眉，顾盼神飞。",
            background="贾政庶女，赵姨娘所出。才自精明志自高，是大观园的改革家。",
            character="精明果断，有男儿气概。对庶出身份敏感，对家族忧心。",
            abilities=["管家除弊", "诗书", "书法", "领导力"],
            secrets=["对嫡庶之别的痛恨", "对家族衰败的洞察"],
            fate_arc="远嫁海疆——从大观园理家到一帆风雨路三千",
            poem_prophecy="清明涕送江边望，千里东风一梦遥"),
        NPC(name="史湘云", role="金陵十二钗正册",
            appearance="蜂腰猿背，鹤势螂形。豪爽中不失妩媚。",
            background="史家侯门之后，父母早亡，由叔叔抚养。常来贾府做客。",
            character="英豪阔大，心直口快。醉卧芍药裀，割腥啖膻——最具名士风度。",
            abilities=["诗词敏捷", "针线（被迫）", "饮酒"],
            secrets=["在叔叔家的苦日子", "对宝玉的特殊情谊"],
            fate_arc="云散高唐——从名士风流到湘江水逝"),
        NPC(name="妙玉", role="金陵十二钗正册",
            appearance="品貌出众，带发修行的女尼。",
            background="苏州官宦之女，因多病遁入空门。后被贾府请入大观园栊翠庵。",
            character="孤僻高傲，有洁癖。身在佛门心在世外。对宝玉暗藏好感。",
            abilities=["茶道", "诗书", "佛法"],
            secrets=["对宝玉的心事", "出身来历"],
            fate_arc="可怜金玉质，终陷淖泥中"),
        NPC(name="贾迎春", role="金陵十二钗正册",
            appearance="肌肤微丰，合中身材，腮凝新荔，鼻腻鹅脂，温柔沉默。",
            background="贾赦庶女。性格懦弱，人称二木头。",
            character="温柔到懦弱，无能到可悲。最不像贵族小姐的贵族小姐。",
            abilities=["围棋（仅此而已）"],
            secrets=["对贾府阴暗面的恐惧"],
            fate_arc="误嫁中山狼——从懦弱小姐到被虐致死",
            poem_prophecy="金闺花柳质，一载赴黄粱"),
        NPC(name="贾惜春", role="金陵十二钗正册",
            appearance="身量未足，形容尚小。",
            background="贾珍之妹，宁国府小姐。自幼在荣府长大。",
            character="冷面冷心，善于绘画。看透宁府的肮脏后选择出世。",
            abilities=["绘画（大观园图）"],
            secrets=["对宁国府的厌恶"],
            fate_arc="独卧青灯古佛旁——从侯门小姐到出家为尼"),
        NPC(name="秦可卿", role="金陵十二钗正册",
            appearance="鲜艳妩媚，有似宝钗；袅娜风流，又如黛玉。",
            background="宁国府贾蓉之妻。来历不明（养生堂抱养）。",
            character="温柔和平，被合族赞许。但死于不可言说的丑闻。",
            abilities=["治家"],
            secrets=["与贾珍的不伦关系", "真正的身世来历"],
            fate_arc="最早凋零的金钗——从天香楼到悬梁自缢"),
        NPC(name="李纨", role="金陵十二钗正册",
            appearance="朴实无华，青春守寡的模样。",
            background="贾珠之妻，贾兰之母。丈夫早逝，青春丧偶。",
            character="如槁木死灰，一心教子。是大观园诗社的社长。",
            abilities=["评诗", "教子", "治家（不争）"],
            secrets=["守寡的苦楚"],
            fate_arc="凤冠霞帔的晚年——从槁木死灰到母凭子贵"),
        NPC(name="贾巧姐", role="金陵十二钗正册",
            appearance="幼小。",
            background="王熙凤之女。",
            character="年幼，命运多舛。",
            abilities=[],
            secrets=[],
            fate_arc="从侯门千金到荒村纺绩——被刘姥姥所救",
            poem_prophecy="偶因济刘氏，巧得遇恩人"),
        NPC(name="贾母", role="贾府最高权威",
            appearance="白发如银，满面慈祥。富态雍容的老封君。",
            background="史侯家小姐嫁入贾府。经历贾府最鼎盛时期。",
            character="溺爱孙辈，享乐至上。洞察世情但不愿面对现实。",
            abilities=["品鉴（戏曲、饮食、女红）", "人情世故"],
            secrets=["对家族衰败的预感但不愿相信"],
            fate_arc="从安享富贵到目睹家破"),
        NPC(name="贾政", role="荣国府当家老爷",
            appearance="端方严肃，道学先生的打扮。",
            background="贾代善次子，贾宝玉之父。工部员外郎。",
            character="古板迂腐，崇尚仕途经济。对宝玉又爱又恨。",
            abilities=["仕途", "诗书（但常附庸风雅）"],
            secrets=["年轻时也曾诗酒风流"],
            fate_arc="从望子成龙到无奈接受"),
        NPC(name="贾琏", role="荣国府长房长子",
            appearance="俊俏风流的青年公子。",
            background="贾赦之子，王熙凤之夫。",
            character="好色无能，怕老婆但又不断偷腥。",
            abilities=["应酬社交", "管理外务"], secrets=[],
            fate_arc="从风流公子到家破人亡"),
        NPC(name="贾珍", role="宁国府当家",
            appearance="中年贵族的做派。",
            background="贾敬之子，宁国府族长。",
            character="荒淫无耻，只有门口两个石狮子是干净的。",
            abilities=["场面应酬"], secrets=["与秦可卿的丑事"],
            fate_arc="从骄奢淫逸到家亡人散"),
        NPC(name="袭人", role="宝玉首席丫鬟, 金陵十二钗又副册",
            appearance="柔媚姣俏，温顺可人。",
            background="本名花珍珠，贾母丫鬟，后给宝玉。与宝玉有云雨之情。",
            character="温柔和顺，忠心为主。但劝宝玉走仕途时显露出她的世俗局限。",
            abilities=["伺候周到", "忍耐", "调解关系"],
            secrets=["与宝玉的私情", "劝宝玉读书的真实动机"],
            fate_arc="堪羡优伶有福——从首席丫鬟到嫁给蒋玉菡"),
        NPC(name="晴雯", role="宝玉丫鬟, 金陵十二钗又副册",
            appearance="水蛇腰，削肩膀，眉眼有几分像黛玉。",
            background="赖大家买的丫鬟，送给贾母，贾母给宝玉。",
            character="心比天高，身为下贱。爽直泼辣，不懂收敛。",
            abilities=["针线（病补雀金裘）"],
            secrets=["对宝玉的感情"],
            fate_arc="被逐大观园含冤而死——从最出挑的丫鬟到风流夭折",
            poem_prophecy="霁月难逢，彩云易散。心比天高，身为下贱"),
        NPC(name="紫鹃", role="黛玉首席丫鬟",
            appearance="清秀机灵。",
            background="贾母丫鬟鹦哥，给黛玉使唤。",
            character="忠心耿耿，一心为黛玉。敢试宝玉真心。",
            abilities=["体贴", "慧心"],
            secrets=["为黛玉试探宝玉"],
            fate_arc="从黛玉最亲之人到伴青灯古佛"),
        NPC(name="平儿", role="凤姐通房丫鬟",
            appearance="极清俊，举止温柔。",
            background="凤姐陪嫁丫鬟，贾琏通房。",
            character="善良温厚，在夹缝中周旋。是凤姐之威和贾琏之俗之间的缓冲。",
            abilities=["处事柔和", "调停"],
            secrets=["知道凤姐放高利贷"],
            fate_arc="从夹缝生存到扶正（续书）"),
        NPC(name="刘姥姥", role="乡村老妪",
            appearance="村野老妪，满面风霜却精神矍铄。",
            background="王家远亲，狗儿之岳母。",
            character="知恩图报，大智若愚。三进荣国府，见证了贾府的盛衰。",
            abilities=["世事洞明", "人情练达", "讲故事"],
            secrets=[],
            fate_arc="从攀附求助到救人报恩"),
        NPC(name="贾雨村", role="结构性线索人物",
            appearance="腰圆背厚，面阔口方，剑眉星眼。",
            background="生于仕宦之家的穷儒。甄士隐资助其赶考。",
            character="忘恩负义，徇私枉法。是封建官场的缩影。",
            abilities=["诗书", "权术"],
            secrets=["知晓英莲下落", "受甄士隐大恩而未报"],
            fate_arc="从落魄书生到徇私枉法的官僚"),
        NPC(name="甄士隐", role="序幕人物",
            appearance="面如冠玉，气质不凡的乡绅。",
            background="姑苏阊门乡绅，资助贾雨村，失女，火灾后悟道出家。",
            character="看破红尘的先行者。是全书的引路人。",
            abilities=["诗书"],
            secrets=[],
            fate_arc="从富贵乡绅到悟道出家——全书命运的缩影"),
        NPC(name="薛蟠", role="薛家长子",
            appearance="粗豪骄横的富家子弟。",
            background="薛姨妈之子，宝钗之兄。打死冯渊抢英莲。",
            character="呆霸王，愚拙粗鲁。但对母亲妹妹有真情。",
            abilities=["经商（不行）", "惹祸（在行）"],
            secrets=[],
            fate_arc="从土豪恶霸到被柳湘莲痛打"),
        NPC(name="尤二姐", role="贾琏的二房",
            appearance="标致温柔。",
            background="尤氏继母之女。被贾琏偷娶为二房。",
            character="温柔软弱，从良无门。",
            abilities=[], secrets=[],
            fate_arc="被凤姐逼死——从私藏外室到吞金自逝"),
        NPC(name="尤三姐", role="尤二姐之妹",
            appearance="风流标致，性格刚烈。",
            background="尤氏继母之女。暗中自许柳湘莲。",
            character="刚烈如火，以死明志。",
            abilities=[], secrets=[],
            fate_arc="自刎殉情——从自许终身到一剑封喉"),
    ]


def build_static_items() -> list[Item]:
    """构建关键物品列表。"""
    return [
        Item(item_id="i0001", name="通灵宝玉", appearance="大如雀卵，灿若明霞，莹润如酥，五色花纹缠护。",
             description="贾宝玉出生时衔在口中的美玉，上有'莫失莫忘，仙寿恒昌'篆文。",
             symbolic_meaning="贾宝玉的前世真身/本真自我的象征",
             usages=["证明宝玉非凡来历", "与宝钗金锁配对"]),
        Item(item_id="i0002", name="金锁", appearance="璎珞项圈上挂的金锁，有'不离不弃，芳龄永继'八字。",
             description="薛宝钗从小佩戴的金锁，癞头和尚所赠八字吉谶。",
             symbolic_meaning="封建婚姻制度/命运安排的象征",
             usages=["与通灵宝玉配对构成'金玉良缘'"]),
        Item(item_id="i0003", name="金陵十二钗正册/副册/又副册",
             appearance="太虚幻境薄命司中的三本册子。",
             description="记录金陵十二钗等女子命运的画册与判词。",
             symbolic_meaning="命运的不可抗拒性",
             usages=["预言群钗命运", "全书结构的缩影"]),
        Item(item_id="i0004", name="冷香丸", appearance="埋在梨花树下的药丸，异香异气。",
             description="治疗薛宝钗热毒的奇方：春天白牡丹花蕊、夏天白荷花蕊、秋天白芙蓉花蕊、冬天白梅花蕊，加雨水、露水、霜水、雪水调匀。",
             symbolic_meaning="宝钗冷性人格的隐喻——用极端清凉克制先天热毒",
             usages=["象征宝钗的以理化情"]),
        Item(item_id="i0005", name="护官符", appearance="一张写有四大家族权势谱系的纸条。",
             description="贾不假，白玉为堂金作马。阿房宫，三百里，住不下金陵一个史。东海缺少白玉床，龙王来请金陵王。丰年好大雪，珍珠如土金如铁。",
             symbolic_meaning="四大家族互相勾连的权势网络",
             usages=["揭示封建官场的利益共同体"]),
        Item(item_id="i0006", name="《红楼梦》十二支曲",
             appearance="太虚幻境中警幻仙姑命人演唱的十四支曲子。",
             description="从'红楼梦引子'到'收尾·飞鸟各投林'，暗含十二钗等女子的命运。",
             symbolic_meaning="全书悲剧结局的最完整预言",
             usages=["预言全部主要人物的命运结局"]),
        Item(item_id="i0007", name="玻璃炕屏", appearance="精致的玻璃屏风。",
             description="王熙凤娘家给她的嫁妆，被贾蓉借去摆场面。",
             symbolic_meaning="贾府表面富贵的空架子",
             usages=["侧面展现贾蓉与凤姐关系"]),
        Item(item_id="i0008", name="绣春囊", appearance="绣着春宫图的香囊。",
             description="在大观园山石后被傻大姐捡到的淫秽之物。",
             symbolic_meaning="大观园不再洁净的标志——象征着青春乌托邦的污染",
             usages=["引发抄检大观园的直接导火索"]),
        Item(item_id="i0009", name="雀金裘", appearance="用孔雀金线织成的华贵氅衣。",
             description="贾母给宝玉的俄罗斯国进贡雀金裘，宝玉赴宴时烧了一个洞。",
             symbolic_meaning="宝玉被宠爱的象征",
             usages=["晴雯带病连夜补好——晴雯之忠与艺的极致展现"]),
        Item(item_id="i0010", name="葬花锄/花帚/花囊",
             appearance="黛玉葬花所用的小锄和花帚。",
             description="黛玉在大观园中扫花葬花的工具。",
             symbolic_meaning="对青春易逝的哀悼——为自己也为群芳先行祭奠",
             usages=["葬花吟的直接道具"]),
    ]


def build_static_relationships() -> list[Relationship]:
    """构建核心关系列表。"""
    return [
        Relationship(agent_pair=["贾宝玉", "林黛玉"],
                     rel_type="lovers", value_axis="爱 vs 怨",
                     description="木石前盟——前世为神瑛侍者与绛珠仙草，今世以泪偿还。青梅竹马，精神知己，但终被'金玉良缘'阻隔。",
                     key_turning_points=["宝黛初会（第3回）", "共读西厢（第23回）", "葬花吟（第27回）",
                                         "宝玉挨打黛玉探视（第34回）", "慧紫鹃情辞试莽玉（第57回）"]),
        Relationship(agent_pair=["贾宝玉", "薛宝钗"],
                     rel_type="acquaintances", value_axis="情 vs 理",
                     description="金玉良缘——封建婚姻的安排。宝钗的理性克制与宝玉的痴情任性互为镜面。",
                     key_turning_points=["宝玉识金锁（第8回）", "宝钗生日点戏说禅（第22回）"]),
        Relationship(agent_pair=["林黛玉", "薛宝钗"],
                     rel_type="rivals",
                     description="情敌与知己——从互相猜忌（黛玉的醋意）到冰释前嫌（钗黛合好），二人最终互相理解。",
                     key_turning_points=["黛玉在宝钗面前失言西厢记句（第42回）", "宝钗送燕窝（第45回）"]),
        Relationship(agent_pair=["贾宝玉", "贾政"],
                     rel_type="family", value_axis="情 vs 理",
                     description="父子冲突——封建家长与叛逆儿子的根本矛盾。宝玉挨打是冲突爆发的顶点。",
                     key_turning_points=["宝玉抓周（第2回）", "贾政训斥宝玉读书（第9回）", "宝玉挨打（第33回）"]),
        Relationship(agent_pair=["王熙凤", "贾琏"],
                     rel_type="spouses",
                     description="强势妻子与懦弱丈夫——权力争夺、偷腥背叛、最终关系破裂。",
                     key_turning_points=["贾琏偷取多姑娘（第21回）", "凤姐生日贾琏偷鲍二媳妇（第44回）", "偷娶尤二姐（第65回）"]),
        Relationship(agent_pair=["贾宝玉", "晴雯"],
                     rel_type="master_servant",
                     description="最像黛玉的丫鬟——晴雯是黛玉的影子，她的被逐和死亡预告了黛玉的命运。",
                     key_turning_points=["晴雯撕扇（第31回）", "晴雯病补雀金裘（第52回）", "晴雯被逐夭亡（第77回）"]),
        Relationship(agent_pair=["贾宝玉", "袭人"],
                     rel_type="master_servant",
                     description="温顺的规训者——袭人是宝钗的影子，她试图用温柔将宝玉推上仕途。",
                     key_turning_points=["袭人与宝玉初试云雨（第6回）", "袭人劝宝玉读书（第19回）"]),
        Relationship(agent_pair=["贾母", "王夫人"],
                     rel_type="family",
                     description="婆媳博弈——贾母护黛玉（木石前盟），王夫人选宝钗（金玉良缘）。",
                     key_turning_points=["王夫人撵晴雯（第77回）——间接表明对黛玉的态度"]),
    ]


def build_static_regions() -> list[Region]:
    """构建核心空间/区域列表。"""
    return [
        Region(name="大观园", category="zone",
               description="为元春省亲修建的省亲别墅，后成为宝玉与众钗的生活空间。",
               symbolic_meaning="青春乌托邦——女儿世界的最后庇护所，也是即将被毁灭的乐园"),
        Region(name="荣国府", category="zone",
               description="贾政一支的居所，全书主要叙事空间。",
               symbolic_meaning="封建贵族家庭的缩影——外表显赫，内里腐烂"),
        Region(name="宁国府", category="zone",
               description="贾珍一支的居所，道德败坏最为严重。",
               symbolic_meaning="伦理秩序的崩塌——'只剩门口两个石狮子是干净的'"),
        Region(name="太虚幻境", category="zone",
               description="警幻仙姑所在的仙界。",
               symbolic_meaning="命运揭示之所——预知一切却无法改变的悲剧宿命"),
        Region(name="潇湘馆", category="zone",
               description="黛玉居所，翠竹掩映。",
               symbolic_meaning="黛玉高洁孤傲的人格象征——斑竹泪，潇湘妃子"),
        Region(name="蘅芜苑", category="zone",
               description="宝钗居所，异草奇香。",
               symbolic_meaning="宝钗冷香内敛的人格——表面朴素，内里精致"),
        Region(name="怡红院", category="zone",
               description="宝玉居所，富贵精致的院落。",
               symbolic_meaning="宝玉的红尘享乐世界——千红一窟，万艳同杯"),
        Region(name="铁槛寺/馒头庵", category="zone",
               description="贾府家庙与邻近的尼庵。",
               symbolic_meaning="宗教场所的世俗腐败——凤姐弄权铁槛寺"),
    ]


# ============================================================
# Stage 2: LLM-based scene extraction from timeline
# ============================================================

SYSTEM_PROMPT_SCENE_EXTRACTION = """你是《红楼梦》叙事结构分析专家。你的任务是从给定的摘要句时间线中，识别发生了**价值转化**的关键场景。

## 价值转化定义（Robert McKee）

一个有效的场景 = 某个价值轴上发生从+到-或从-到+的转化。价值轴包括：
1. 兴 vs 衰：贾府的家族命运
2. 爱 vs 怨：宝黛钗的情感关系
3. 真 vs 假：全书哲学主题（幻与空）
4. 聚 vs 散：团圆与分离
5. 自由 vs 束缚：个人与封建礼教的冲突
6. 情 vs 理：痴情与理性的冲突
7. 清 vs 浊：女儿世界 vs 男人世界
8. 生 vs 死：生命力的盛衰

## 识别标准

- 选取发生了**显著价值转化**的句子或连续几句
- 转化的方向明确（从什么状态到什么状态）
- 转化由一个明确的转折事件触发
- 一个场景可以涵盖多条价值轴上的同时转化

## 输出要求

输出一个JSON，包含 `scenes` 数组，每个场景：
- `title`: 场景名称（如"宝黛初会"、"元春省亲"）
- `sentence_indices`: 对应的摘要句global_index列表（含开头和结尾句之间的所有句）
- `chapter_range`: "开始章-结束章"
- `narrative`: 场景简述
- `character_decisions`: 角色抉择，每个包含 decision, implicit_alternatives, value_tags (3-5个)
- `value_transformations`: 价值转化，每个包含 axis, from_state, to_state, direction, turning_point_event, characters_involved
- `group`: 属于哪一幕 (Prologue/Act1_Rise/Act2_Climax/Act3_Turn/Act4_Fall)
- `is_turning_point`: 是否为关键转折点

请专注于**重大**价值转化场景，不要输出琐碎的日常过渡。控制在指定数量内。"""


def build_timeline_batches(timeline: list[dict], batch_size: int = 50) -> list[list[dict]]:
    """将时间线分批用于LLM处理。"""
    return [timeline[i:i + batch_size] for i in range(0, len(timeline), batch_size)]


def timeline_to_text(sentences: list[dict]) -> str:
    """将一批摘要句转换为LLM可读的文本格式。"""
    lines = []
    for s in sentences:
        idx = s["global_sentence_index"]
        ch = s["chapter_index"]
        text = s["text"]
        lines.append(f"[S{idx}] 第{ch}回: {text}")
    return "\n".join(lines)


def extract_scenes_from_batch(
    client: OpenAI,
    timeline_batch: list[dict],
    batch_index: int,
    max_scenes_per_batch: int = 8,
) -> list[dict]:
    """从一批摘要句中提取价值转化场景。"""
    timeline_text = timeline_to_text(timeline_batch)
    user_prompt = f"""以下是《红楼梦》前80回摘要句时间线的第 {batch_index + 1} 批。

## 时间线

{timeline_text}

## 任务

从上述句子中识别**重大价值转化场景**，最多 {max_scenes_per_batch} 个。

请以JSON格式输出，格式如下：
{{
  "scenes": [
    {{
      "title": "场景名称",
      "sentence_indices": [起始句index, ..., 结束句index],
      "chapter_range": "开始章-结束章",
      "narrative": "2-3句场景概述",
      "character_decisions": [
        {{
          "decision": "角色实际做出的决定",
          "implicit_alternatives": ["可能但未做的选择1", "可能但未做的选择2"],
          "value_tags": ["标签1", "标签2", "标签3"]
        }}
      ],
      "value_transformations": [
        {{
          "axis": "兴 vs 衰",
          "from_state": "转化前的状态",
          "to_state": "转化后的状态",
          "direction": "+ → −",
          "turning_point_event": "引发转化的关键事件",
          "characters_involved": ["角色1", "角色2"]
        }}
      ],
      "group": "Act1_Rise",
      "is_turning_point": false
    }}
  ]
}}

注意：
- 只输出真正有实质价值转化的场景，不要输出过渡性、日常性内容
- value_tags 从以下选择：痴情、决裂、隐忍、反抗、顺从、觉悟、幻灭、守护、背叛、牺牲、自毁、宽恕、复仇、面对、逃避、独立、依附
- direction 只能是："+ → −", "− → +"
- group 可选值：Prologue (第1回), Act1_Rise (2-18回), Act2_Climax (19-53回), Act3_Turn (54-69回), Act4_Fall (70-80回)
- 如果这批句子中没有重大价值转化场景，返回空数组
"""

    result = call_llm(client, SYSTEM_PROMPT_SCENE_EXTRACTION, user_prompt)
    if result and "scenes" in result:
        return result["scenes"]
    return []


# ============================================================
# Stage 3: Merge F-T-P triples
# ============================================================

def merge_ftp_triples(
    scenes: list[SceneNode],
    ftp_triples: list[dict],
    timeline: list[dict],
) -> list[dict]:
    """将已验证的F-T-P三元组嵌入到场景节点中。"""
    foreshadow_lines = []

    # 建立 sentence_index -> scene 映射
    scene_by_sentence: dict[int, str] = {}
    for scene in scenes:
        for idx in scene.summary_sentence_indices:
            scene_by_sentence[idx] = scene.id

    for triple in ftp_triples:
        f = triple.get("foreshadow", {})
        p = triple.get("payoff", {})
        t = triple.get("trigger", {})

        f_idx = f.get("global_sentence_index")
        p_idx = p.get("global_sentence_index")

        ftp_record = {
            "id": triple.get("id", ""),
            "foreshadow": f,
            "trigger": t,
            "payoff": p,
            "distance_chapters": triple.get("distance_chapters"),
            "confidence": triple.get("confidence"),
        }
        foreshadow_lines.append(ftp_record)

        # 关联到场景节点
        if f_idx is not None and f_idx in scene_by_sentence:
            for scene in scenes:
                if scene.id == scene_by_sentence[f_idx]:
                    scene.foreshadow_refs.append(triple.get("id", ""))
        if p_idx is not None and p_idx in scene_by_sentence:
            for scene in scenes:
                if scene.id == scene_by_sentence[p_idx]:
                    scene.payoff_refs.append(triple.get("id", ""))

    return foreshadow_lines


# ============================================================
# Stage 4: Build ending nodes
# ============================================================

def build_ending_nodes() -> list[EndingNode]:
    """构建80回末尾指向性结局节点。"""
    return [
        EndingNode(
            id="ending_family_decline",
            group="Endings",
            ending_title="贾府衰败大方向",
            trigger_condition="第80回: 迎春误嫁, 香菱受虐, 大观园渐空",
            narrative="第80回终结于迎春误嫁中山狼、香菱屈受贪夫棒。大观园群芳渐散，贾府外强中干已显露无遗。"
                       "在曹雪芹原设计中，此后将有贾府被抄、黛玉泪尽而亡、宝玉出家等一系列悲剧结局。",
            value_alignment=["衰", "散", "怨", "死"],
            value_transformation_summary="全书从'兴'(甄士隐资助贾雨村→元春省亲)走向'衰'(抄检大观园→迎春误嫁)，"
                                        "从'聚'(诗社欢聚→寿怡红群芳开夜宴)走向'散'(晴雯被逐→迎春出嫁)，"
                                        "从'爱'(宝黛初会→共读西厢)走向'怨'(误解→阴阳两隔)，"
                                        "从'生'(青春活力→大观园诗酒生活)走向'死'(秦可卿→尤二姐→晴雯→即将的黛玉)。"
                                        "最终'好一似食尽鸟投林，落了片白茫茫大地真干净'。",
        ),
        EndingNode(
            id="ending_baoyu_awakening",
            group="Endings",
            ending_title="宝玉觉悟方向",
            trigger_condition="第80回: 宝玉对群芳凋零的痛感积累",
            narrative="宝玉经历了晴雯之死、迎春误嫁、香菱受虐后，对女儿世界的洁净幻想逐渐破灭。"
                       "按照第五回判词/曲文的预言和脂砚斋批语，宝玉最终将悬崖撒手、出家为僧。",
            value_alignment=["假→真", "爱→空", "情→悟"],
            value_transformation_summary="贾宝玉从痴于情(情不情)走向觉悟于空(悟空)，"
                                        "这是全书最核心的个人价值转化弧线。",
        ),
    ]


# ============================================================
# Stage 5: Assemble final script
# ============================================================

def assemble_script(
    scenes: list[SceneNode],
    transitions: list[TransitionNode],
    endings: list[EndingNode],
    npcs: list[NPC],
    items: list[Item],
    relationships: list[Relationship],
    regions: list[Region],
    foreshadow_lines: list[dict],
) -> HonglouStructuredScript:
    """组装最终的结构脚本。"""
    all_nodes = list(scenes) + list(transitions) + list(endings)
    start = scenes[0].id if scenes else ""
    end_ids = [e.id for e in endings]

    script = HonglouStructuredScript(
        start_nodes=[start],
        endings=end_ids,
        npc=npcs,
        items=items,
        relationships=relationships,
        regions=regions,
        nodes=all_nodes,
        foreshadow_lines=foreshadow_lines,
    )
    return script


# ============================================================
# CLI
# ============================================================

@click.command()
@click.option("--force", is_flag=True, help="Force regeneration even if output exists")
@click.option("--max-scenes", default=45, help="Maximum number of scene nodes to extract")
@click.option("--batch-size", default=50, help="Timeline sentences per LLM batch")
@click.option("--max-scenes-per-batch", default=7, help="Max scenes per batch")
@click.option("--dry-run", is_flag=True, help="Preview without LLM calls")
@click.option("--skip-llm", is_flag=True, help="Skip LLM extraction, use cached scenes")
def main(
    force: bool,
    max_scenes: int,
    batch_size: int,
    max_scenes_per_batch: int,
    dry_run: bool,
    skip_llm: bool,
):
    """生成红楼梦价值转化图结构化脚本。"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_json = OUTPUT_DIR / "honglou_structured_script.json"
    output_scenes_cache = OUTPUT_DIR / "extracted_scenes_cache.jsonl"

    if not force and output_json.exists():
        print(f"Output already exists: {output_json}")
        print("Use --force to regenerate.")
        return

    click.echo("=" * 60)
    click.echo("红楼梦价值转化图生成器")
    click.echo("=" * 60)

    # Step 0: Load data
    click.echo("\n[Step 0] 加载数据...")
    timeline = read_jsonl(TIMELINE_JSONL)
    ftp_triples = read_jsonl(FTP_JSONL)
    click.echo(f"  摘要句: {len(timeline)} 句 (全局索引 0–{len(timeline)-1})")
    click.echo(f"  F-T-P 三元组: {len(ftp_triples)} 条")

    if dry_run:
        click.echo("\n[Dry run] 将处理以下数据:")
        batches = build_timeline_batches(timeline, batch_size)
        click.echo(f"  批次: {len(batches)} (每批 {batch_size} 句)")
        for i, b in enumerate(batches):
            click.echo(f"    Batch {i+1}: S{b[0]['global_sentence_index']}–S{b[-1]['global_sentence_index']} "
                        f"(第{b[0]['chapter_index']}–{b[-1]['chapter_index']}回)")
        return

    # Step 1: Static assets
    click.echo("\n[Step 1] 构建静态资产...")
    npcs = build_static_npcs()
    items = build_static_items()
    relationships = build_static_relationships()
    regions = build_static_regions()
    click.echo(f"  NPC: {len(npcs)} | Items: {len(items)} | "
               f"Relations: {len(relationships)} | Regions: {len(regions)}")

    # Step 2: LLM scene extraction
    all_scenes_raw: list[dict] = []

    if skip_llm and output_scenes_cache.exists():
        click.echo(f"\n[Step 2] 从缓存加载场景 (--skip-llm)...")
        all_scenes_raw = read_jsonl(output_scenes_cache)
        click.echo(f"  缓存场景: {len(all_scenes_raw)}")
    else:
        click.echo("\n[Step 2] LLM 识别价值转化场景...")
        client = create_client()
        batches = build_timeline_batches(timeline, batch_size)
        click.echo(f"  共 {len(batches)} 批，每批 {batch_size} 句")

        total_scenes = 0
        for i, batch in enumerate(batches):
            ch_start = batch[0]["chapter_index"]
            ch_end = batch[-1]["chapter_index"]
            click.echo(f"  处理 Batch {i+1}/{len(batches)} (第{ch_start}–{ch_end}回)... ", nl=False)

            batch_scenes = extract_scenes_from_batch(
                client, batch, i, max_scenes_per_batch
            )
            total_scenes += len(batch_scenes)
            all_scenes_raw.extend(batch_scenes)
            click.echo(f"提取 {len(batch_scenes)} 个场景")

            if total_scenes >= max_scenes:
                click.echo(f"  已达到 max_scenes={max_scenes}，停止提取。")
                break

            # Rate limiting
            if i < len(batches) - 1:
                time.sleep(1.5)

        click.echo(f"  总计提取 {len(all_scenes_raw)} 个价值转化场景")

        # Cache raw scenes
        write_jsonl(output_scenes_cache, all_scenes_raw)
        click.echo(f"  已缓存至: {output_scenes_cache}")

    # Step 3: Convert to SceneNode objects
    click.echo("\n[Step 3] 转换为 SceneNode 对象...")

    def _normalize_indices(raw_indices: list) -> list[int]:
        """Normalize sentence indices: strip 'S' prefix, convert to int."""
        result = []
        for v in raw_indices:
            if isinstance(v, str):
                v = v.lstrip("S")
            try:
                result.append(int(v))
            except (ValueError, TypeError):
                continue
        return result

    scenes: list[SceneNode] = []
    for i, raw in enumerate(all_scenes_raw):
        sid = f"scene_{i+1:03d}_{raw.get('title', '').replace(' ', '_')[:20]}"
        sn = SceneNode(
            id=sid,
            group=raw.get("group", "Act2_Climax"),
            chapter_range=raw.get("chapter_range", ""),
            title=raw.get("title", ""),
            narrative=raw.get("narrative", ""),
            summary_sentence_indices=_normalize_indices(raw.get("sentence_indices", [])),
            character_decisions=raw.get("character_decisions", []),
            value_transformations=[
                {
                    "axis": vt.get("axis", ""),
                    "from_state": vt.get("from_state", ""),
                    "to_state": vt.get("to_state", ""),
                    "direction": vt.get("direction", ""),
                    "turning_point_event": vt.get("turning_point_event", ""),
                    "characters_involved": vt.get("characters_involved", []),
                }
                for vt in raw.get("value_transformations", [])
            ],
        )
        scenes.append(sn)

    click.echo(f"  SceneNode: {len(scenes)}")

    # Step 4: Build transitions (linear chain)
    click.echo("\n[Step 4] 构建线性过渡链...")
    transitions = build_linear_chain(scenes)
    click.echo(f"  TransitionNode: {len(transitions)}")

    # Step 5: Merge F-T-P triples
    click.echo("\n[Step 5] 嵌入 F-T-P 三元组...")
    foreshadow_lines = merge_ftp_triples(scenes, ftp_triples, timeline)
    click.echo(f"  Foreshadow lines: {len(foreshadow_lines)}")

    # Step 6: Build endings
    click.echo("\n[Step 6] 构建结局节点...")
    endings = build_ending_nodes()
    click.echo(f"  EndingNode: {len(endings)}")

    # Step 7: Assemble
    click.echo("\n[Step 7] 组装最终脚本...")
    script = assemble_script(
        scenes, transitions, endings,
        npcs, items, relationships, regions,
        foreshadow_lines,
    )

    # Step 8: Validate
    click.echo("\n[Step 8] 验证脚本...")
    errors = validate_script(script)
    if errors:
        click.echo(f"  发现 {len(errors)} 个问题:")
        for e in errors:
            click.echo(f"    - {e}")
    else:
        click.echo("  验证通过 ✓")

    # Step 9: Write output
    click.echo(f"\n[Step 9] 写入输出文件...")
    write_json(output_json, script.model_dump(mode="json"))
    click.echo(f"  已写入: {output_json}")

    # Summary
    summary = {
        "generated_at": datetime.now().isoformat(),
        "title": script.title,
        "total_nodes": len(script.nodes),
        "scene_nodes": len(scenes),
        "transition_nodes": len(transitions),
        "ending_nodes": len(endings),
        "npc_count": len(script.npc),
        "item_count": len(script.items),
        "relationship_count": len(script.relationships),
        "region_count": len(script.regions),
        "foreshadow_lines": len(script.foreshadow_lines),
        "value_axes": script.value_axes,
        "groups": script.groups,
        "validation_errors": errors,
    }
    write_json(OUTPUT_DIR / "generation_summary.json", summary)

    click.echo(f"\n{'=' * 60}")
    click.echo("生成完成!")
    click.echo(f"  输出: {output_json}")
    click.echo(f"  摘要: {OUTPUT_DIR / 'generation_summary.json'}")
    click.echo(f"{'=' * 60}")


if __name__ == "__main__":
    main()
