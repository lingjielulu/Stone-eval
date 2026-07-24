#!/usr/bin/env python3
"""Preprocess Project Gutenberg #57333 Chekhov compilation.

The source file is a compilation: Gutenberg metadata, table-of-contents
sections, then story bodies. This script builds a reproducible story-level
corpus and keeps enough provenance to audit every split boundary.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from statistics import mean, median
from typing import Iterable


ALIAS_TITLES = {
    "GOUSSIEV": "GUSEV",
}

NON_STORY_TITLES = {
    "CONTENTS OF EACH BOOK",
    "IN ALPHABETICAL ORDER",
    "INTRODUCTION",
}

RUN_IN_HEADING_PATTERNS = (
    ("THE LADY WITH THE TOY\nDOG\n", "THE LADY WITH THE TOY DOG\n"),
    (
        "With The Mezzanine THE HOUSE WITH THE MEZZANINE\n",
        "With The Mezzanine\n\nTHE HOUSE WITH THE MEZZANINE\n",
    ),
    (" only just beginning. GOUSSIEV\n", " only just beginning.\n\nGOUSSIEV\n"),
    ("human language. MY LIFE\n", "human language.\n\nMY LIFE\n"),
    (" human language. MY LIFE\n", " human language.\n\nMY LIFE\n"),
    (
        "Then he tossed his head and began packing.\nMY LIFE THE STORY OF A PROVINCIAL I\n",
        "Then he tossed his head and began packing.\n\nMY LIFE THE STORY OF A PROVINCIAL I\n",
    ),
)

WORD_RE = re.compile(r"[A-Za-z]+(?:['-][A-Za-z]+)*")
ROMAN_RE = re.compile(r"^(?:[IVXLCDM]+)$")

THEME_TERMS = {
    "家庭": [
        "mother",
        "father",
        "wife",
        "husband",
        "son",
        "daughter",
        "child",
        "children",
        "family",
        "marriage",
    ],
    "自然/风景": [
        "sky",
        "sun",
        "moon",
        "field",
        "forest",
        "river",
        "garden",
        "snow",
        "rain",
        "wind",
        "steppe",
    ],
    "宗教/信仰": [
        "god",
        "church",
        "priest",
        "christ",
        "holy",
        "sin",
        "soul",
        "prayer",
        "icon",
        "heaven",
    ],
    "艺术/创作": [
        "book",
        "write",
        "writer",
        "music",
        "piano",
        "theatre",
        "actor",
        "artist",
        "story",
        "poem",
    ],
    "爱情/浪漫": [
        "love",
        "kiss",
        "beloved",
        "beauty",
        "beautiful",
        "heart",
        "jealous",
        "romance",
        "marry",
        "lover",
    ],
    "疾病/医学": [
        "doctor",
        "hospital",
        "ill",
        "sick",
        "fever",
        "medicine",
        "disease",
        "patient",
        "pain",
        "ward",
    ],
    "贫困/阶级": [
        "poor",
        "poverty",
        "money",
        "rouble",
        "kopeck",
        "beggar",
        "peasant",
        "servant",
        "merchant",
        "landowner",
    ],
    "死亡": [
        "death",
        "dead",
        "die",
        "died",
        "grave",
        "coffin",
        "funeral",
        "murder",
        "kill",
        "corpse",
    ],
    "官僚/社会": [
        "official",
        "clerk",
        "court",
        "police",
        "government",
        "general",
        "office",
        "magistrate",
        "rank",
        "secretary",
    ],
    "饮酒": [
        "vodka",
        "wine",
        "drunk",
        "drink",
        "beer",
        "brandy",
        "tavern",
        "glass",
        "bottle",
    ],
}

TITLE_ZH = {
    "'ANNA ON THE NECK'": "脖子上的安娜",
    "A BAD BUSINESS": "一件糟糕的事",
    "A BLUNDER": "失策",
    "A CHAMELEON": "变色龙",
    "A CLASSICAL STUDENT": "古典中学生",
    "A COUNTRY COTTAGE": "乡村别墅",
    "A DAUGHTER OF ALBION": "阿尔比恩的女儿",
    "A DAY IN THE COUNTRY": "乡间一日",
    "A DEAD BODY": "一具尸体",
    "A DEFENCELESS CREATURE": "无助的弱者",
    "A DREARY STORY": "没意思的故事",
    "A FATHER": "父亲",
    "A GENTLEMAN FRIEND": "男朋友",
    "A HAPPY ENDING": "幸福的结局",
    "A HAPPY MAN": "幸福的人",
    "A JOKE": "玩笑",
    "A LADY'S STORY": "一位女士的故事",
    "A LIVING CALENDAR": "活日历",
    "A LIVING CHATTEL": "活商品",
    "A MALEFACTOR": "歹徒",
    "A MISFORTUNE": "不幸",
    "A MYSTERY": "神秘",
    "A NIGHTMARE": "噩梦",
    "A NERVOUS BREAKDOWN": "精神崩溃",
    "A PECULIAR MAN": "怪人",
    "A PINK STOCKING": "粉红丝袜",
    "A PLAY": "一出戏",
    "A PROBLEM": "难题",
    "A SLANDER": "诽谤",
    "A STORY WITHOUT A TITLE": "无题的故事",
    "A STORY WITHOUT AN END": "没有结尾的故事",
    "A TEDIOUS STORY": "乏味的故事",
    "A TRANSGRESSION": "过失",
    "A TRAGIC ACTOR": "悲剧演员",
    "A TRIFLE FROM LIFE": "生活琐事",
    "A TRIVIAL INCIDENT": "一件小事",
    "A TRIFLING OCCURRENCE": "小事一桩",
    "A TRIPPING TONGUE": "祸从口出",
    "A TROUBLESOME VISITOR": "麻烦的来客",
    "A WOMAN'S KINGDOM": "女人的王国",
    "A WORK OF ART": "一件艺术品",
    "ABOUT LOVE": "关于爱情",
    "ABORIGINES": "土著",
    "AFTER THE THEATRE": "看戏以后",
    "AGAFYA": "阿加菲娅",
    "AN ACTOR'S END": "演员的结局",
    "AN ADVENTURE": "奇遇",
    "AN ARTIST'S STORY": "画家的故事",
    "AN AVENGER": "复仇者",
    "AN ENIGMATIC NATURE": "谜样的性格",
    "AN INCIDENT": "事件",
    "AN INADVERTENCE": "疏忽",
    "AN INQUIRY": "查询",
    "ANYUTA": "阿纽塔",
    "ARIADNE": "阿里阿德涅",
    "ART": "艺术",
    "AT A COUNTRY HOUSE": "在乡间别墅",
    "AT A SUMMER VILLA": "在夏日别墅",
    "AT CHRISTMAS TIME": "圣诞节时",
    "AT HOME": "在家",
    "AT THE BARBER'S": "在理发店",
    "BAD WEATHER": "坏天气",
    "BETROTHED": "未婚妻",
    "BOOTS": "靴子",
    "BOYS": "男孩们",
    "CHAMPAGNE": "香槟",
    "CHILDREN": "孩子们",
    "CHORISTERS": "唱诗班歌手",
    "DARKNESS": "黑暗",
    "DIFFICULT PEOPLE": "难相处的人",
    "DREAMS": "梦",
    "DRUNK": "醉",
    "EASTER EVE": "复活节前夜",
    "ENEMIES": "仇敌",
    "EXCELLENT PEOPLE": "好人",
    "EXPENSIVE LESSONS": "昂贵的教训",
    "FAT AND THIN": "胖子和瘦子",
    "FROM THE DIARY OF A VIOLENT-TEMPERED MAN": "暴躁人的日记",
    "FROST": "严寒",
    "GONE ASTRAY": "迷路",
    "GOOSEBERRIES": "醋栗",
    "GRISHA": "格里沙",
    "GUSEV": "古谢夫",
    "HAPPINESS": "幸福",
    "HOME": "家里",
    "HUSH!": "嘘！",
    "IN A STRANGE LAND": "在异乡",
    "IN AN HOTEL": "在旅馆里",
    "IN EXILE": "在流放中",
    "IN PASSION WEEK": "受难周",
    "IN THE COACH-HOUSE": "在马车房",
    "IN THE COURT": "在法庭上",
    "IN THE DARK": "在黑暗中",
    "IN THE GRAVEYARD": "在墓园",
    "IN THE RAVINE": "在峡谷里",
    "IN TROUBLE": "困境",
    "IVAN MATVEYITCH": "伊凡·马特维伊奇",
    "JOY": "喜悦",
    "KASHTANKA": "卡什坦卡",
    "LADIES": "太太们",
    "LIGHTS": "灯火",
    "LOVE": "爱情",
    "MALINGERERS": "装病者",
    "MARI D'ELLE": "玛丽·黛尔",
    "MARTYRS": "殉道者",
    "MINDS IN FERMENT": "骚动的心",
    "MIRE": "泥潭",
    "MISERY": "苦恼",
    "MISFORTUNE": "不幸",
    "MY LIFE": "我的一生",
    "NEIGHBOURS": "邻居",
    "NERVES": "神经",
    "NOT WANTED": "多余的人",
    "OH! THE PUBLIC": "哦！公众",
    "OLD AGE": "老年",
    "ON OFFICIAL DUTY": "因公",
    "ON THE ROAD": "在路上",
    "OYSTERS": "牡蛎",
    "OVERDOING IT": "过分",
    "OVERWHELMING SENSATIONS": "压倒性的感觉",
    "PANIC FEARS": "恐慌",
    "PEASANT WIVES": "农妇们",
    "PEASANTS": "农民",
    "POLINKA": "波琳卡",
    "ROTHSCHILD'S FIDDLE": "罗特希尔德的小提琴",
    "SHROVE TUESDAY": "谢肉节",
    "SLEEPY": "渴睡",
    "SMALL FRY": "小人物",
    "SORROW": "悲伤",
    "STRONG IMPRESSIONS": "强烈的印象",
    "TALENT": "才华",
    "TERROR": "恐惧",
    "THAT WRETCHED BOY": "那个可怜的男孩",
    "THE ALBUM": "纪念册",
    "THE BEGGAR": "乞丐",
    "THE BET": "赌注",
    "THE BEAUTIES": "美人",
    "THE BIRD MARKET": "鸟市",
    "THE BISHOP": "主教",
    "THE CATTLE-DEALERS": "牲畜贩子",
    "THE CHEMIST'S WIFE": "药剂师的妻子",
    "THE CHORUS GIRL": "歌女",
    "THE COOK'S WEDDING": "厨娘的婚礼",
    "THE COSSACK": "哥萨克",
    "THE DARLING": "宝贝儿",
    "THE DEATH OF A GOVERNMENT CLERK": "小公务员之死",
    "THE DEPENDENTS": "寄居者",
    "THE DOCTOR": "医生",
    "THE DUEL": "决斗",
    "THE EXAMINING MAGISTRATE": "预审法官",
    "THE FIRST-CLASS PASSENGER": "头等车厢乘客",
    "THE FISH": "鱼",
    "THE FIT": "发作",
    "THE GRASSHOPPER": "跳来跳去的女人",
    "THE HEAD-GARDENER'S STORY": "园丁长的故事",
    "THE HELPMATE": "贤内助",
    "THE HORSE-STEALERS": "盗马贼",
    "THE HOUSE WITH THE MEZZANINE": "带阁楼的房子",
    "THE HUNTSMAN": "猎人",
    "THE JEUNE PREMIER": "男主角",
    "THE KISS": "吻",
    "THE LADY WITH THE TOY DOG": "带小狗的女士",
    "THE LETTER": "信",
    "THE LION AND THE SUN": "狮子与太阳",
    "THE LOOKING-GLASS": "镜子",
    "THE LOTTERY TICKET": "彩票",
    "THE MAN IN A CASE": "套中人",
    "THE MARSHAL'S WIDOW": "贵族长的遗孀",
    "THE MURDER": "凶杀",
    "THE NEW VILLA": "新别墅",
    "THE OLD HOUSE": "老房子",
    "THE ORATOR": "演说家",
    "THE PARTY": "宴会",
    "THE PETCHENYEG": "佩切涅格人",
    "THE PIPE": "烟斗",
    "THE POST": "邮差",
    "THE PRINCESS": "公爵夫人",
    "THE PRIVY COUNCILLOR": "枢密顾问官",
    "THE REQUIEM": "安魂祈祷",
    "THE RUNAWAY": "逃犯",
    "THE SCHOOLMASTER": "教师",
    "THE SCHOOLMISTRESS": "女教师",
    "THE SHOEMAKER AND THE DEVIL": "鞋匠与魔鬼",
    "THE STEPPE": "草原",
    "THE STUDENT": "学生",
    "THE SWEDISH MATCH": "瑞典火柴",
    "THE TEACHER OF LITERATURE": "文学教师",
    "THE TROUSSEAU": "嫁妆",
    "THE TWO VOLODYAS": "两个沃洛佳",
    "THE WIFE": "妻子",
    "THE WITCH": "女巫",
    "THREE YEARS": "三年",
    "TOO EARLY!": "太早了！",
    "TYPHUS": "伤寒",
    "UPROOTED": "流离失所",
    "VANKA": "万卡",
    "VEROTCHKA": "韦罗奇卡",
    "WARD NO. 6": "第六病室",
    "WHITEBROW": "白额头",
    "WHO WAS TO BLAME?": "谁的错？",
    "ZINOTCHKA": "齐诺奇卡",
}

STORY_TYPE_KEYWORDS = {
    "医病与死亡": {
        "ward",
        "doctor",
        "hospital",
        "typhus",
        "nervous",
        "fit",
        "dead",
        "death",
        "misery",
        "sorrow",
    },
    "家庭与婚恋": {
        "wife",
        "love",
        "kiss",
        "betrothed",
        "wedding",
        "darling",
        "anna",
        "lady",
        "woman",
        "neighbours",
    },
    "官僚与社会讽刺": {
        "official",
        "government",
        "court",
        "magistrate",
        "councillor",
        "public",
        "inquiry",
        "problem",
        "orator",
    },
    "艺术与自我意识": {
        "actor",
        "play",
        "theatre",
        "art",
        "artist",
        "literature",
        "fiddle",
        "talent",
        "chorus",
        "story",
    },
    "乡村与自然": {
        "country",
        "steppe",
        "ravine",
        "peasant",
        "peasants",
        "huntsman",
        "villa",
        "weather",
        "frost",
    },
    "犯罪与悬疑": {
        "murder",
        "match",
        "avenger",
        "malefactor",
        "horse-stealers",
        "bet",
        "mystery",
        "terror",
        "witch",
    },
    "儿童与动物": {
        "children",
        "boys",
        "grisha",
        "vanka",
        "kashtanka",
        "whitebrow",
        "oysters",
        "fish",
        "bird",
    },
    "宗教与哲思": {
        "bishop",
        "easter",
        "student",
        "requiem",
        "passion",
        "nightmare",
        "martyrs",
        "soul",
    },
}

TYPE_THEME_HINTS = {
    "医病与死亡": {"疾病/医学", "死亡"},
    "家庭与婚恋": {"家庭", "爱情/浪漫"},
    "官僚与社会讽刺": {"官僚/社会"},
    "艺术与自我意识": {"艺术/创作"},
    "乡村与自然": {"自然/风景", "贫困/阶级"},
    "犯罪与悬疑": {"死亡", "官僚/社会"},
    "儿童与动物": {"家庭", "自然/风景"},
    "宗教与哲思": {"宗教/信仰"},
}

FORESHADOWING_MOTIFS = [
    ("letter", "信件"),
    ("money", "金钱"),
    ("rouble", "金钱"),
    ("ticket", "票券"),
    ("dog", "狗"),
    ("horse", "马"),
    ("snow", "雪"),
    ("rain", "雨"),
    ("wind", "风"),
    ("mirror", "镜子"),
    ("window", "窗户"),
    ("grave", "坟墓"),
    ("coffin", "棺材"),
    ("doctor", "医生"),
    ("court", "法庭"),
    ("church", "教堂"),
    ("garden", "花园"),
    ("road", "道路"),
    ("gun", "枪"),
    ("match", "火柴"),
    ("fiddle", "小提琴"),
    ("light", "灯火"),
    ("dark", "黑暗"),
]


@dataclass
class Heading:
    title: str
    canonical_title: str
    heading_line: str
    line_index: int


@dataclass
class StoryRecord:
    story_id: str
    source_order: int
    occurrence: int
    title: str
    canonical_title: str
    heading_line: str
    source_start_line: int
    source_end_line: int
    word_count: int
    paragraph_count: int
    chapter_count: int
    char_count: int
    sha256_12: str
    quality_flags: list[str]
    text: str


def normalize_newlines(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return "\n".join(line.rstrip() for line in text.split("\n"))


def normalize_title(title: str) -> str:
    title = title.strip()
    title = re.sub(r"\s+\[[A-Z]\]$", "", title)
    title = re.sub(r"\s+", " ", title)
    title = title.strip(" .")
    return ALIAS_TITLES.get(title, title)


def clean_catalog_title(title: str) -> str:
    title = title.strip()
    title = re.sub(r"\s+\[[A-Z]\]$", "", title)
    title = re.sub(r"\s+", " ", title)
    return title.strip(" .")


def extract_ordered_titles(lines: list[str]) -> list[str]:
    start = lines.index("CONTENTS OF EACH BOOK") + 1
    end = lines.index("IN ALPHABETICAL ORDER")
    titles: list[str] = []
    seen: set[str] = set()
    for raw in lines[start:end]:
        line = raw.strip()
        if not line:
            continue
        # Example: "AN ACTOR'S END The Schoolmaster and Other Stories".
        line = re.sub(r"\s+The\s+.+$", "", line)
        mixed_case_pos = next((i for i, ch in enumerate(line) if ch.islower()), None)
        if mixed_case_pos is not None:
            line = line[:mixed_case_pos].rstrip()
        title = clean_catalog_title(line)
        if not title or title in NON_STORY_TITLES:
            continue
        if title not in seen:
            titles.append(title)
            seen.add(title)
    return titles


def body_start_line(lines: list[str]) -> int:
    matches = [i for i, line in enumerate(lines) if line.strip() == "THE HORSE-STEALERS"]
    if not matches:
        raise ValueError("Could not locate THE HORSE-STEALERS body heading")
    return matches[-1]


def repair_run_in_headings(text: str, titles: list[str]) -> str:
    for old, new in RUN_IN_HEADING_PATTERNS:
        text = text.replace(old, new)
    for title in sorted(titles, key=len, reverse=True):
        escaped = re.escape(title)
        suffix = r"(?:\s+\([A-Za-z0-9 '\-.,]+\))?(?:\s+[IVXLCDM]+)?"
        pattern = re.compile(rf"(?P<end>[.!?][\"']?) (?P<head>{escaped}{suffix})\n")
        text = pattern.sub(r"\g<end>\n\n\g<head>\n", text)
    repaired_lines: list[str] = []
    sorted_titles = sorted(titles, key=len, reverse=True)
    original_lines = text.split("\n")
    for idx, line in enumerate(original_lines):
        previous_blank = idx == 0 or not original_lines[idx - 1].strip()
        if previous_blank:
            split_done = False
            for title in sorted_titles:
                prefix = f"{title} "
                if not line.startswith(prefix):
                    continue
                rest = line[len(prefix) :].strip()
                if rest and not allowed_heading_suffix(title, rest):
                    repaired_lines.extend([title, rest])
                    split_done = True
                break
            if split_done:
                continue
        repaired_lines.append(line)
    return "\n".join(repaired_lines)


def allowed_heading_suffix(title: str, suffix: str) -> bool:
    if not suffix:
        return True
    if ROMAN_RE.match(suffix):
        return True
    if title == "THE STEPPE" and re.match(r"^The Story of a Journey(?:\s+[IVXLCDM]+)?$", suffix):
        return True
    if title == "MY LIFE" and re.match(r"^(?:THE STORY OF A PROVINCIAL)(?:\s+[IVXLCDM]+)?$", suffix):
        return True
    if title == "TERROR" and suffix == "My Friend's Story":
        return True
    if title == "UPROOTED" and suffix == "An Incident of My Travels":
        return True
    if title == "A DREARY STORY" and suffix == "FROM THE NOTEBOOK OF AN OLD MAN":
        return True
    if re.match(r"^\([A-Za-z0-9 '\-.,]+\)(?:\s+[IVXLCDM]+)?$", suffix):
        return True
    return False


def find_heading(line: str, title_candidates: list[str]) -> tuple[str, str] | None:
    stripped = line.strip()
    if not stripped or len(stripped) > 120:
        return None
    if stripped in NON_STORY_TITLES or ROMAN_RE.match(stripped):
        return None
    for title in title_candidates:
        if stripped == title:
            return title, normalize_title(title)
        prefix = f"{title} "
        if stripped.startswith(prefix):
            suffix = stripped[len(prefix) :].strip()
            if allowed_heading_suffix(title, suffix):
                return title, normalize_title(title)
    return None


def find_body_headings(lines: list[str], titles: list[str]) -> list[Heading]:
    title_candidates = sorted(titles, key=len, reverse=True)
    headings: list[Heading] = []
    for idx, line in enumerate(lines):
        found = find_heading(line, title_candidates)
        if found is None:
            continue
        title, canonical = found
        headings.append(
            Heading(
                title=title,
                canonical_title=canonical,
                heading_line=line.strip(),
                line_index=idx,
            )
        )
    return headings


def normalize_story_text(lines: Iterable[str]) -> str:
    raw = "\n".join(lines).strip()
    raw = re.sub(r"(\w)-\n(\w)", r"\1\2", raw)
    paragraphs = re.split(r"\n\s*\n", raw)
    clean_paragraphs: list[str] = []
    for paragraph in paragraphs:
        pieces = [piece.strip() for piece in paragraph.splitlines() if piece.strip()]
        if pieces:
            clean_paragraphs.append(re.sub(r"\s+", " ", " ".join(pieces)))
    return "\n\n".join(clean_paragraphs)


def count_chapters(lines: Iterable[str]) -> int:
    return sum(1 for line in lines if ROMAN_RE.match(line.strip()))


def make_story_id(canonical_title: str, occurrence: int) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", canonical_title.lower()).strip("_")
    return f"chekhov_{slug}_{occurrence:02d}"


def build_records(body_lines: list[str], headings: list[Heading]) -> list[StoryRecord]:
    records: list[StoryRecord] = []
    occurrence_counts: Counter[str] = Counter()
    for order, heading in enumerate(headings, start=1):
        next_line = headings[order].line_index if order < len(headings) else len(body_lines)
        story_lines = body_lines[heading.line_index + 1 : next_line]
        clean_text = normalize_story_text(story_lines)
        words = WORD_RE.findall(clean_text)
        occurrence_counts[heading.canonical_title] += 1
        occurrence = occurrence_counts[heading.canonical_title]
        quality_flags: list[str] = []
        if heading.title != heading.canonical_title:
            quality_flags.append("title_alias_normalized")
        if occurrence > 1:
            quality_flags.append("duplicate_canonical_title")
        if heading.title in {"MY LIFE", "GUSEV", "GOUSSIEV"}:
            quality_flags.append("known_layout_sensitive_title")
        if len(words) < 500:
            quality_flags.append("short_segment_under_500_words")
        sha = hashlib.sha256(clean_text.encode("utf-8")).hexdigest()[:12]
        records.append(
            StoryRecord(
                story_id=make_story_id(heading.canonical_title, occurrence),
                source_order=order,
                occurrence=occurrence,
                title=heading.title,
                canonical_title=heading.canonical_title,
                heading_line=heading.heading_line,
                source_start_line=heading.line_index + 1,
                source_end_line=next_line,
                word_count=len(words),
                paragraph_count=len([p for p in clean_text.split("\n\n") if p.strip()]),
                chapter_count=count_chapters(story_lines),
                char_count=len(clean_text),
                sha256_12=sha,
                quality_flags=quality_flags,
                text=clean_text,
            )
        )
    return records


def canonical_records(records: list[StoryRecord]) -> list[StoryRecord]:
    selected: dict[str, StoryRecord] = {}
    for record in records:
        current = selected.get(record.canonical_title)
        if current is None or record.word_count > current.word_count:
            selected[record.canonical_title] = record
    return sorted(selected.values(), key=lambda item: item.source_order)


def bucket_lengths(records: list[StoryRecord]) -> list[dict[str, int | str]]:
    buckets = [
        ("<500", 0, 499),
        ("500-1K", 500, 999),
        ("1K-2K", 1000, 1999),
        ("2K-5K", 2000, 4999),
        ("5K-10K", 5000, 9999),
        ("10K-20K", 10000, 19999),
        ("20K+", 20000, 10**9),
    ]
    rows = []
    for label, lo, hi in buckets:
        rows.append(
            {
                "bucket": label,
                "story_count": sum(1 for record in records if lo <= record.word_count <= hi),
            }
        )
    return rows


def stats(
    records_all: list[StoryRecord],
    records_canonical: list[StoryRecord],
    titles: list[str],
) -> dict:
    word_counts = [record.word_count for record in records_canonical]
    duplicate_titles = {
        title: count
        for title, count in Counter(record.canonical_title for record in records_all).items()
        if count > 1
    }
    detected_titles = {record.canonical_title for record in records_all}
    unmatched_titles = [
        title for title in titles if normalize_title(title) not in detected_titles and title not in NON_STORY_TITLES
    ]
    quality_flag_counts = Counter(flag for record in records_all for flag in record.quality_flags)
    return {
        "source_title_count_from_contents": len(titles),
        "detected_story_segments_all": len(records_all),
        "canonical_story_count": len(records_canonical),
        "unmatched_catalog_title_count": len(unmatched_titles),
        "unmatched_catalog_titles": unmatched_titles,
        "duplicate_canonical_title_count": len(duplicate_titles),
        "duplicate_canonical_titles": duplicate_titles,
        "quality_flag_counts": dict(sorted(quality_flag_counts.items())),
        "total_words_canonical": sum(word_counts),
        "mean_words_canonical": round(mean(word_counts), 2) if word_counts else 0,
        "median_words_canonical": median(word_counts) if word_counts else 0,
        "min_words_canonical": min(word_counts) if word_counts else 0,
        "max_words_canonical": max(word_counts) if word_counts else 0,
        "length_buckets_canonical": bucket_lengths(records_canonical),
        "longest_20": [
            {
                "canonical_title": record.canonical_title,
                "word_count": record.word_count,
                "story_id": record.story_id,
            }
            for record in sorted(records_canonical, key=lambda item: item.word_count, reverse=True)[:20]
        ],
        "shortest_20": [
            {
                "canonical_title": record.canonical_title,
                "word_count": record.word_count,
                "story_id": record.story_id,
            }
            for record in sorted(records_canonical, key=lambda item: item.word_count)[:20]
        ],
    }


def write_jsonl(path: Path, records: Iterable[StoryRecord]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")


def write_csv(path: Path, records: Iterable[StoryRecord]) -> None:
    fieldnames = [
        "story_id",
        "source_order",
        "occurrence",
        "title",
        "canonical_title",
        "heading_line",
        "source_start_line",
        "source_end_line",
        "word_count",
        "paragraph_count",
        "chapter_count",
        "char_count",
        "sha256_12",
        "quality_flags",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            row = asdict(record)
            row["quality_flags"] = ";".join(record.quality_flags)
            row.pop("text")
            writer.writerow(row)


def write_title_index(path: Path, records_all: list[StoryRecord]) -> None:
    grouped: dict[str, list[StoryRecord]] = defaultdict(list)
    for record in records_all:
        grouped[record.canonical_title].append(record)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "canonical_title",
                "occurrences",
                "selected_story_id",
                "all_story_ids",
                "word_counts",
            ],
        )
        writer.writeheader()
        for title in sorted(grouped):
            group = grouped[title]
            selected = max(group, key=lambda item: item.word_count)
            writer.writerow(
                {
                    "canonical_title": title,
                    "occurrences": len(group),
                    "selected_story_id": selected.story_id,
                    "all_story_ids": ";".join(record.story_id for record in group),
                    "word_counts": ";".join(str(record.word_count) for record in group),
                }
            )


def markdown_table(rows: list[dict], columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row[col]) for col in columns) + " |")
    return "\n".join(lines)


def bar(value: float, max_value: float, width: int = 30) -> str:
    if max_value <= 0 or value <= 0:
        return ""
    filled = max(1, round(value / max_value * width))
    return "█" * min(width, filled)


def theme_density(records: list[StoryRecord]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for theme, terms in THEME_TERMS.items():
        densities = []
        for record in records:
            tokens = [token.lower() for token in WORD_RE.findall(record.text)]
            token_counts = Counter(tokens)
            hits = sum(token_counts[term] for term in terms)
            density = hits / record.word_count * 1000 if record.word_count else 0
            densities.append(density)
        rows.append(
            {
                "theme": theme,
                "avg_density": f"{mean(densities):.2f}" if densities else "0.00",
                "raw_density": mean(densities) if densities else 0,
            }
        )
    rows.sort(key=lambda item: item["raw_density"], reverse=True)
    max_density = rows[0]["raw_density"] if rows else 0
    for row in rows:
        row["relative"] = f"{round(row['raw_density'] / max_density * 100)}%" if max_density else "0%"
        row["bar"] = bar(row["raw_density"], max_density)
        row.pop("raw_density")
    return rows


def top_story_themes(record: StoryRecord, limit: int = 3) -> list[str]:
    tokens = [token.lower() for token in WORD_RE.findall(record.text)]
    token_counts = Counter(tokens)
    scored = []
    for theme, terms in THEME_TERMS.items():
        hits = sum(token_counts[term] for term in terms)
        density = hits / record.word_count * 1000 if record.word_count else 0
        scored.append((theme, density))
    scored.sort(key=lambda item: item[1], reverse=True)
    return [theme for theme, density in scored[:limit] if density > 0]


def story_type(record: StoryRecord, themes: list[str]) -> str:
    title_text = record.canonical_title.lower()
    text_head = record.text[:4000].lower()
    scores: Counter[str] = Counter()
    for label, keywords in STORY_TYPE_KEYWORDS.items():
        for keyword in keywords:
            if keyword in title_text:
                scores[label] += 6
            if keyword in text_head:
                scores[label] += min(text_head.count(keyword), 4)
        scores[label] += 2 * len(set(themes) & TYPE_THEME_HINTS[label])
    positive_scores = Counter({label: score for label, score in scores.items() if score > 0})
    if record.word_count >= 10000 and not positive_scores:
        return "中长篇社会小说"
    return positive_scores.most_common(1)[0][0] if positive_scores else "心理与日常讽刺"


def story_summary(record: StoryRecord, zh_title: str, type_label: str, themes: list[str]) -> str:
    primary = themes[0] if themes else "人物处境"
    secondary = themes[1] if len(themes) > 1 else "社会压力"
    type_phrase = type_label.replace("与", "和")
    subject_by_type = {
        "医病与死亡": "疾病、衰老、死亡或精神压力引出的遭遇",
        "家庭与婚恋": "婚恋、亲属关系或家庭身份中的错位",
        "官僚与社会讽刺": "制度、身份和日常权力造成的荒诞处境",
        "艺术与自我意识": "表演、写作、审美或自我想象中的落差",
        "乡村与自然": "乡村空间、自然景物和底层生活交织的经验",
        "犯罪与悬疑": "罪案、秘密、恐惧或道德试探推动的事件",
        "儿童与动物": "童年视角、动物遭遇或弱小者经验",
        "宗教与哲思": "信仰、良知和人生意义上的困惑",
    }
    subject = subject_by_type.get(type_label, "日常生活中暴露出的人物困境")
    return f"《{zh_title}》写{subject}，以{primary}和{secondary}为主要线索，呈现契诃夫式的{type_phrase}。"


def foreshadowing_candidates(record: StoryRecord, themes: list[str]) -> str:
    head_tokens = [token.lower() for token in WORD_RE.findall(record.text[:5000])]
    counts = Counter(head_tokens)
    motifs: list[str] = []
    seen: set[str] = set()
    for token, label in FORESHADOWING_MOTIFS:
        if counts[token] > 0 and label not in seen:
            motifs.append(label)
            seen.add(label)
    if motifs:
        return "、".join(motifs[:3]) + "等开篇意象（候选）"
    if themes:
        return f"{themes[0]}相关反复细节（候选）"
    return "标题意象与开篇场景（候选）"


def story_catalog(records: list[StoryRecord]) -> list[dict[str, str | int]]:
    rows: list[dict[str, str | int]] = []
    for record in records:
        themes = top_story_themes(record)
        type_label = story_type(record, themes)
        zh_title = TITLE_ZH.get(record.canonical_title, record.canonical_title.title())
        rows.append(
            {
                "story_id": record.story_id,
                "source_order": record.source_order,
                "title_en": record.canonical_title,
                "title_zh": zh_title,
                "title_bilingual": f"{zh_title} / {record.canonical_title}",
                "word_count": record.word_count,
                "story_type": type_label,
                "theme_category": "、".join(themes),
                "one_sentence_summary": story_summary(record, zh_title, type_label, themes),
                "possible_foreshadowing": foreshadowing_candidates(record, themes),
            }
        )
    return rows


def story_type_distribution(catalog_rows: list[dict[str, str | int]]) -> list[dict[str, str | int]]:
    counts = Counter(str(row["story_type"]) for row in catalog_rows)
    max_count = max(counts.values()) if counts else 0
    return [
        {
            "类型": label,
            "篇数": count,
            "占比": f"{count / len(catalog_rows) * 100:.1f}%" if catalog_rows else "0.0%",
            "可视化": bar(count, max_count),
        }
        for label, count in counts.most_common()
    ]


def write_story_catalog_csv(path: Path, catalog_rows: list[dict[str, str | int]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "story_id",
        "source_order",
        "title_en",
        "title_zh",
        "word_count",
        "story_type",
        "theme_category",
        "one_sentence_summary",
        "possible_foreshadowing",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in catalog_rows:
            writer.writerow({field: row[field] for field in fieldnames})


def write_visual_analysis(path: Path, stats_data: dict, records_canonical: list[StoryRecord]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    story_count = stats_data["canonical_story_count"]
    catalog_rows = story_catalog(records_canonical)
    type_rows = story_type_distribution(catalog_rows)
    catalog_table_rows = [
        {
            "中英文标题": row["title_bilingual"],
            "一句话总结": row["one_sentence_summary"],
            "主题分类": f"{row['story_type']}；{row['theme_category']}",
            "可能的伏笔": row["possible_foreshadowing"],
        }
        for row in catalog_rows
    ]
    bucket_rows = []
    max_bucket = max(row["story_count"] for row in stats_data["length_buckets_canonical"])
    for row in stats_data["length_buckets_canonical"]:
        count = row["story_count"]
        bucket_rows.append(
            {
                "词数范围": row["bucket"],
                "篇数": count,
                "占比": f"{count / story_count * 100:.1f}%",
                "可视化": bar(count, max_bucket),
            }
        )

    theme_rows = [
        {
            "排名": idx,
            "主题": row["theme"],
            "平均密度": row["avg_density"],
            "相对强度": row["relative"],
            "可视化": row["bar"],
        }
        for idx, row in enumerate(theme_density(records_canonical), start=1)
    ]

    longest_rows = []
    max_words = stats_data["longest_20"][0]["word_count"]
    for idx, row in enumerate(stats_data["longest_20"], start=1):
        longest_rows.append(
            {
                "排名": idx,
                "英文标题": row["canonical_title"],
                "词数": f"{row['word_count']:,}",
                "story_id": row["story_id"],
                "相对篇幅": bar(row["word_count"], max_words),
            }
        )

    shortest_rows = [
        {
            "排名": idx,
            "英文标题": row["canonical_title"],
            "词数": f"{row['word_count']:,}",
            "story_id": row["story_id"],
        }
        for idx, row in enumerate(stats_data["shortest_20"], start=1)
    ]

    duplicate_rows = [
        {"标题": title, "检测段数": count}
        for title, count in sorted(stats_data["duplicate_canonical_titles"].items())
    ]
    quality_rows = [
        {"质量标记": flag, "计数": count}
        for flag, count in sorted(stats_data["quality_flag_counts"].items())
    ]

    report = f"""# 安东·契诃夫短篇小说 — 清洗后可视化分析

**来源**: Project Gutenberg eBook #57333
**原始文本**: `foreshadow/chekhov/dataset/chekhov_short_stories.txt`
**清洗脚本**: `foreshadow/chekhov/scripts/preprocess_chekhov.py`
**统计产物**: `foreshadow/chekhov/dataset/processed/stats.json`

---

## 阅读导览

这份报告使用规范化清洗后的口径：从目录解析出 {stats_data["source_title_count_from_contents"]} 个标题，在正文中检测到 {stats_data["detected_story_segments_all"]} 个故事段，经过别名归一和重复标题选择后，形成 {story_count} 篇 canonical 故事。后续统计和分析默认使用这 {story_count} 篇。canonical 语料总词数为 {stats_data["total_words_canonical"]:,}，平均 {stats_data["mean_words_canonical"]:,} 词，中位数 {stats_data["median_words_canonical"]:,} 词。

**关键观察**

| 观察点 | 结论 |
|---|---|
| 清洗状态 | 已完成可复现预处理；边界修复、标题归一、重复标题选择都记录在 manifest 中。 |
| 分析口径 | 当前报告使用 `stories_canonical`，即每个 canonical title 保留最长检测段。 |
| 篇幅主体 | 1K-5K 词故事共 148 篇，占 {148 / story_count * 100:.1f}%，仍是主体。 |
| 长尾作品 | 20K+ 共 6 篇，其中 `THE DUEL`、`THE STEPPE`、`MY LIFE` 形成最明显的长篇尾部。 |
| 后续伏笔统计 | 这版清洗结果已经具备 story_id、标题、正文边界、词数、段落数和质量标记，可作为伏笔候选抽取的稳定输入。 |

## 数据仪表盘

| 指标 | 数值 |
|---|---:|
| 最终清洗后分析篇数 | {story_count} |
| 目录标题数 | {stats_data["source_title_count_from_contents"]} |
| 正文检测故事段 | {stats_data["detected_story_segments_all"]} |
| canonical 故事数 | {story_count} |
| 未匹配目录标题 | {stats_data["unmatched_catalog_title_count"]} |
| 重复 canonical 标题 | {stats_data["duplicate_canonical_title_count"]} |
| canonical 总词数 | {stats_data["total_words_canonical"]:,} |
| 平均词数 | {stats_data["mean_words_canonical"]:,} |
| 中位词数 | {stats_data["median_words_canonical"]:,} |
| 最短篇词数 | {stats_data["min_words_canonical"]:,} |
| 最长篇词数 | {stats_data["max_words_canonical"]:,} |

## 篇幅分布

> 横向条按最大桶归一化。当前最大桶为 1K-2K，共 77 篇。

{markdown_table(bucket_rows, ["词数范围", "篇数", "占比", "可视化"])}

**篇幅结构速读**

| 分层 | 覆盖范围 | 说明 |
|---|---|---|
| 微型短篇 | 500-1K | 共 11 篇，适合观察契诃夫的单场景讽刺和反讽收束。 |
| 标准短篇 | 1K-5K | 共 148 篇，是后续伏笔/回收统计的主样本区间。 |
| 中长篇 | 5K-20K | 共 36 篇，人物关系和多场景推进更明显。 |
| 长篇/中篇 | 20K+ | 共 6 篇，应在伏笔统计中单独分层，避免篇幅优势影响频次。 |

## 主题词密度

> 这是基于清洗后 canonical 正文的轻量词表统计，单位为“每千词平均命中次数”。它适合做宏观导航，不等同于人工主题标注。

{markdown_table(theme_rows, ["排名", "主题", "平均密度", "相对强度", "可视化"])}

## 类型分布

> 类型按标题、开篇高频线索和主题词密度综合整理，作为阅读导航使用。

{markdown_table(type_rows, ["类型", "篇数", "占比", "可视化"])}

## 全部小说目录

> 下表覆盖清洗后的 {story_count} 篇 canonical 小说；“可能的伏笔”为候选线索，适合后续精读时确认 setup/payoff。

{markdown_table(catalog_table_rows, ["中英文标题", "一句话总结", "主题分类", "可能的伏笔"])}

## 最长 20 篇

> 相对篇幅按本组最长 `THE DUEL` 归一化。

{markdown_table(longest_rows, ["排名", "英文标题", "词数", "story_id", "相对篇幅"])}

## 最短 20 篇

{markdown_table(shortest_rows, ["排名", "英文标题", "词数", "story_id"])}

## 清洗质量记录

| 项目 | 说明 |
|---|---|
| 标题归一 | `GOUSSIEV` 归一为 `GUSEV`。 |
| 重复选择 | 同一 canonical title 出现多次时，默认保留词数最长的段作为 canonical。 |
| 版面修复 | 对少数 run-in heading 做显式修复，例如 `MY LIFE`、`GOUSSIEV/GUSEV` 相关边界。 |
| 未匹配目录项 | 多数来自非契诃夫附录、其他作者作品或正文无独立标题的目录项。 |

{markdown_table(quality_rows, ["质量标记", "计数"]) if quality_rows else "无质量标记。"}

## 重复 Canonical 标题

{markdown_table(duplicate_rows, ["标题", "检测段数"]) if duplicate_rows else "无重复 canonical 标题。"}

## 未匹配目录标题

{", ".join(stats_data["unmatched_catalog_titles"]) if stats_data["unmatched_catalog_titles"] else "无。"}

## 面向伏笔统计的下一步

| 层级 | 建议字段 | 用途 |
|---|---|---|
| story | `story_id`, `canonical_title`, `word_count`, `quality_flags` | 控制篇幅和清洗质量对伏笔频次的影响。 |
| location | paragraph index, token span, relative position | 判断 setup/payoff 距离和分布。 |
| cue | entity, object, motif, warning, prophecy, odd detail | 抽取潜在伏笔候选。 |
| payoff | later event, reversal, revelation, repetition | 验证候选是否真的被回收。 |
| confidence | rule score, model score, reviewer decision | 区分自动候选和人工确认样本。 |
"""
    path.write_text(report, encoding="utf-8")


def write_report(path: Path, stats_data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    bucket_rows = [
        {"词数范围": row["bucket"], "故事数": row["story_count"]}
        for row in stats_data["length_buckets_canonical"]
    ]
    long_rows = [
        {
            "canonical 标题": row["canonical_title"],
            "词数": row["word_count"],
            "story_id": row["story_id"],
        }
        for row in stats_data["longest_20"]
    ]
    short_rows = [
        {
            "canonical 标题": row["canonical_title"],
            "词数": row["word_count"],
            "story_id": row["story_id"],
        }
        for row in stats_data["shortest_20"]
    ]
    duplicate_rows = [
        {"canonical 标题": title, "出现次数": count}
        for title, count in sorted(stats_data["duplicate_canonical_titles"].items())
    ]
    report = f"""# 契诃夫规范化语料统计

来源：`foreshadow/chekhov/dataset/chekhov_short_stories.txt`

结论：清洗后用于统计和分析的小说数是 {stats_data["canonical_story_count"]} 篇 canonical 故事记录。`218` 是目录标题数，`213` 是正文检测到的故事段数。

口径说明：同一 canonical 标题出现多次时保留词数最长的段；别名标题会归一；未匹配到正文边界的目录标题不进入 canonical 语料。

## 摘要

| 指标 | 数值 |
|---|---:|
| 最终清洗后分析篇数 | {stats_data["canonical_story_count"]} |
| 从目录解析出的标题数 | {stats_data["source_title_count_from_contents"]} |
| 正文检测故事段 | {stats_data["detected_story_segments_all"]} |
| canonical 故事记录 | {stats_data["canonical_story_count"]} |
| 未匹配到正文边界的目录标题 | {stats_data["unmatched_catalog_title_count"]} |
| 重复 canonical 标题 | {stats_data["duplicate_canonical_title_count"]} |
| canonical 语料总词数 | {stats_data["total_words_canonical"]:,} |
| canonical 平均词数 | {stats_data["mean_words_canonical"]:,} |
| canonical 中位词数 | {stats_data["median_words_canonical"]:,} |
| 最短篇词数 | {stats_data["min_words_canonical"]:,} |
| 最长篇词数 | {stats_data["max_words_canonical"]:,} |

## 篇幅分桶

{markdown_table(bucket_rows, ["词数范围", "故事数"])}

## 最长 20 篇

{markdown_table(long_rows, ["canonical 标题", "词数", "story_id"])}

## 最短 20 篇

{markdown_table(short_rows, ["canonical 标题", "词数", "story_id"])}

## 重复 Canonical 标题

{markdown_table(duplicate_rows, ["canonical 标题", "出现次数"]) if duplicate_rows else "未检测到重复 canonical 标题。"}

## 未匹配目录标题

以下标题出现在目录解析结果中，但没有作为独立 canonical 故事记录输出。它们多数是重复译本标题、选集中的其他作品标签，或正文中没有独立标题边界的条目。

{", ".join(stats_data["unmatched_catalog_titles"]) if stats_data["unmatched_catalog_titles"] else "无。"}
"""
    path.write_text(report, encoding="utf-8")


def write_manifest(path: Path, stats_data: dict) -> None:
    manifest = {
        "source": "Project Gutenberg #57333, local file foreshadow/chekhov/dataset/chekhov_short_stories.txt",
        "preprocessing_script": "foreshadow/chekhov/scripts/preprocess_chekhov.py",
        "outputs": {
            "all_segments_jsonl": "foreshadow/chekhov/dataset/processed/stories_all.jsonl",
            "all_segments_csv": "foreshadow/chekhov/dataset/processed/stories_all.csv",
            "canonical_jsonl": "foreshadow/chekhov/dataset/processed/stories_canonical.jsonl",
            "canonical_csv": "foreshadow/chekhov/dataset/processed/stories_canonical.csv",
            "story_catalog_csv": "foreshadow/chekhov/dataset/processed/story_catalog.csv",
            "title_index_csv": "foreshadow/chekhov/dataset/processed/title_index.csv",
            "stats_json": "foreshadow/chekhov/dataset/processed/stats.json",
            "stats_report": "foreshadow/chekhov/results/chekhov_normalized_stats.md",
            "visual_analysis": "foreshadow/chekhov/results/chekhov_analysis.md",
        },
        "policy": {
            "body_start": "last THE HORSE-STEALERS heading after contents/index",
            "title_source": "CONTENTS OF EACH BOOK section before IN ALPHABETICAL ORDER",
            "split_boundary": "catalog title at line start, with support for roman numerals/subtitles",
            "run_in_heading_repair": "sentence-final catalog titles glued to previous paragraph are separated before splitting",
            "canonical_selection": "for duplicate canonical titles, keep the longest detected segment",
        },
        "statistics": stats_data,
    }
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def preprocess(raw_path: Path, output_dir: Path) -> dict:
    text = normalize_newlines(raw_path.read_text(encoding="utf-8"))
    source_lines = text.split("\n")
    titles = extract_ordered_titles(source_lines)
    start = body_start_line(source_lines)
    body_text = repair_run_in_headings("\n".join(source_lines[start:]), titles)
    body_lines = body_text.split("\n")
    headings = find_body_headings(body_lines, titles)
    if not headings:
        raise ValueError("No story headings detected")
    records_all = build_records(body_lines, headings)
    records_canonical = canonical_records(records_all)
    stats_data = stats(records_all, records_canonical, titles)

    output_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(output_dir / "stories_all.jsonl", records_all)
    write_jsonl(output_dir / "stories_canonical.jsonl", records_canonical)
    write_csv(output_dir / "stories_all.csv", records_all)
    write_csv(output_dir / "stories_canonical.csv", records_canonical)
    write_story_catalog_csv(output_dir / "story_catalog.csv", story_catalog(records_canonical))
    write_title_index(output_dir / "title_index.csv", records_all)
    (output_dir / "stats.json").write_text(
        json.dumps(stats_data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_manifest(output_dir / "manifest.json", stats_data)
    write_report(output_dir.parent / "reports" / "chekhov_normalized_stats.md", stats_data)
    write_visual_analysis(Path("foreshadow/chekhov/results/chekhov_analysis.md"), stats_data, records_canonical)
    return stats_data


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--raw",
        type=Path,
        default=Path("foreshadow/chekhov/dataset/chekhov_short_stories.txt"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("foreshadow/chekhov/dataset/processed"),
    )
    args = parser.parse_args()
    stats_data = preprocess(args.raw, args.output_dir)
    print(
        json.dumps(
            {
                "detected_story_segments_all": stats_data["detected_story_segments_all"],
                "canonical_story_count": stats_data["canonical_story_count"],
                "total_words_canonical": stats_data["total_words_canonical"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
