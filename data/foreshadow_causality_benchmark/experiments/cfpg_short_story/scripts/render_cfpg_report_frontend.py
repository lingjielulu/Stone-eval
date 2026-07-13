"""Render a self-contained, human-readable CFPG experiment dashboard."""

from __future__ import annotations

import argparse
import html
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[5]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from cfpg_prompt_utils import load_prompt_templates  # noqa: E402


RUN_ID = "20260701_short_story_cfpg_v3_verified"
EXPERIMENT_ROOT = Path(
    "data/foreshadow_causality_benchmark/experiments/cfpg_short_story"
)
RUN_DIR = EXPERIMENT_ROOT / "results/extraction/runs" / RUN_ID
ORACLE_DIR = EXPERIMENT_ROOT / "results/oracle_smoke_20260713"
PROMPT_FILE = EXPERIMENT_ROOT / "prompts/short_story_prompts.md"
TAXONOMY_FILE = EXPERIMENT_ROOT / "data/cfpg_taxonomy_v2.json"
DEFAULT_OUTPUT = EXPERIMENT_ROOT / "reports/dashboard.html"
REPORT_MD = EXPERIMENT_ROOT / "reports/experiment_report.md"
REPORT_HTML = EXPERIMENT_ROOT / "reports/experiment_report.html"
REPORT_CSS = EXPERIMENT_ROOT / "reports/report.css"
PROMPT_ORDER = [
    "short_story_candidate_extraction",
    "short_story_candidate_verification",
    "short_story_fap_decision",
    "short_story_cfpg_decision",
    "short_story_continuation",
    "short_story_continuation_judge",
    "short_story_tracking_decision",
]

TITLES = {
    "speckled_band": "斑点带子案",
    "red_headed_league": "红发会",
    "necklace": "项链",
    "gift_of_the_magi": "麦琪的礼物",
    "last_leaf": "最后一片叶子",
    "tell_tale_heart": "泄密的心",
    "cask_of_amontillado": "一桶白葡萄酒",
    "to_build_a_fire": "生火",
    "medicine": "药",
    "cricket": "促织",
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def frontend_case(
    item: dict[str, Any], accepted: bool, taxonomy: dict[str, Any]
) -> dict[str, Any]:
    candidate = item["candidate"]
    verdict = item.get("verdict", {})
    story_id = candidate["story_id"]
    normalized = taxonomy["cases"][candidate["candidate_id"]]
    chinese_source_dir = (
        "normalized_texts" if story_id in {"medicine", "cricket"} else "normalized_texts_zh"
    )
    return {
        "id": candidate["candidate_id"],
        "story_id": story_id,
        "title": TITLES.get(story_id, story_id),
        "accepted": accepted,
        "foreshadow_span": candidate.get("foreshadow_span", ""),
        "payoff_span": candidate.get("payoff_span", ""),
        "distance": candidate.get("distance_paragraphs"),
        "primary_type": normalized["primary_type"],
        "narrative_function": normalized["narrative_function"],
        "legacy_foreshadow_type": candidate.get("foreshadow_type", "unknown"),
        "payoff_type": candidate.get("payoff_type", "unknown"),
        "foreshadow": normalized["foreshadow_zh"],
        "trigger": normalized["trigger_zh"],
        "payoff": normalized["payoff_zh"],
        "rationale": normalized.get(
            "decision_zh", "通过：setup、payoff、时间间隔、伏笔合理性、Trigger 和连接有效性均满足当前 verifier rubric。"
        ),
        "rejection_reason": normalized.get("decision_zh", ""),
        "foreshadow_excerpt": candidate.get("foreshadow_text", "")[:700],
        "payoff_excerpt": candidate.get("payoff_text", "")[:700],
        "links": {
            "source": f"../../../novels/{chinese_source_dir}/{story_id}.txt",
            "source_original": f"../../../novels/normalized_texts/{story_id}.txt",
            "review": (
                f"../results/extraction/runs/{RUN_ID}/reviews/"
                f"{story_id}_ftp_review_{RUN_ID}.md"
            ),
            "candidates": (
                f"../results/extraction/runs/{RUN_ID}/candidates/"
                f"{story_id}_ftp_candidates_{RUN_ID}.jsonl"
            ),
            "verified": (
                f"../results/extraction/runs/{RUN_ID}/verified/"
                f"{story_id}_ftp_verified_{RUN_ID}.jsonl"
            ),
        },
    }


def escape_script_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False).replace("</", "<\\/")


def build_payload() -> dict[str, Any]:
    summary = read_json(RUN_DIR / "summary.json")
    taxonomy = read_json(TAXONOMY_FILE)
    accepted_items = read_jsonl(RUN_DIR / f"accepted_triples_{RUN_ID}.jsonl")
    rejected_items = read_jsonl(RUN_DIR / f"rejected_candidates_{RUN_ID}.jsonl")
    cases = [frontend_case(item, True, taxonomy) for item in accepted_items]
    cases.extend(frontend_case(item, False, taxonomy) for item in rejected_items)
    prompts = load_prompt_templates(PROMPT_FILE)
    prompt_payload = [
        {
            "key": prompt.key,
            "version": prompt.version,
            "system": prompt.system,
            "user": prompt.user,
        }
        for prompt in (prompts[key] for key in PROMPT_ORDER)
    ]
    oracle_rows = read_jsonl(ORACLE_DIR / "oracle.jsonl")
    oracle_summary = read_json(ORACLE_DIR / "summary.json")
    distances = [case["distance"] for case in cases if case["accepted"] and case["distance"] is not None]
    bins = [(4, 10), (11, 25), (26, 50), (51, 100), (101, 174)]
    span_bins = [
        {"label": f"{start}–{end}", "count": sum(start <= value <= end for value in distances)}
        for start, end in bins
    ]
    return {
        "summary": summary,
        "cases": cases,
        "prompts": prompt_payload,
        "oracle": oracle_rows,
        "oracle_summary": oracle_summary,
        "span_bins": span_bins,
        "accepted_types": dict(
            Counter(case["primary_type"] for case in cases if case["accepted"])
        ),
        "narrative_functions": dict(
            Counter(case["narrative_function"] for case in cases if case["accepted"])
        ),
        "payoff_types": dict(Counter(case["payoff_type"] for case in cases if case["accepted"])),
        "generated_at": "2026-07-13",
    }


def render(payload: dict[str, Any]) -> str:
    data = escape_script_json(payload)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CFPG 短篇原文复现实验</title>
<style>
:root {{
  --ink:#17231f; --muted:#66726d; --paper:#f4f0e7; --panel:#fffdf8;
  --line:#d8d1c3; --green:#1f6b53; --green2:#8fbda7; --red:#a5483f;
  --gold:#bc812f; --blue:#416b83; --shadow:0 14px 35px rgba(34,47,41,.09);
}}
*{{box-sizing:border-box}} html{{scroll-behavior:smooth}}
body{{margin:0;background:var(--paper);color:var(--ink);font-family:Inter,"Noto Sans SC","PingFang SC",sans-serif;line-height:1.65}}
a{{color:var(--green);text-decoration:none}} a:hover{{text-decoration:underline}}
.shell{{max-width:1320px;margin:auto;padding:28px}}
.hero{{background:linear-gradient(135deg,#153e32 0%,#235e49 58%,#b77b2e 140%);color:white;border-radius:26px;padding:48px;box-shadow:var(--shadow);position:relative;overflow:hidden}}
.hero:after{{content:"F → T → P";position:absolute;right:38px;bottom:-30px;font:700 90px/1 Georgia,serif;opacity:.08}}
.eyebrow{{font-size:12px;letter-spacing:.18em;text-transform:uppercase;opacity:.72}}
h1{{font:700 clamp(30px,4vw,54px)/1.16 Georgia,"Noto Serif SC",serif;margin:10px 0 14px}}
.hero p{{max-width:850px;font-size:17px;opacity:.9}} .hero-links{{display:flex;gap:12px;flex-wrap:wrap;margin-top:24px}}
.button{{background:white;color:#164534;border-radius:999px;padding:9px 16px;font-weight:700;font-size:13px}}
.button.ghost{{background:rgba(255,255,255,.12);color:white;border:1px solid rgba(255,255,255,.25)}}
.status{{display:inline-flex;align-items:center;gap:8px;background:#fff2cf;color:#704d10;border:1px solid #e1c276;border-radius:999px;padding:7px 12px;font-size:13px;font-weight:700;margin-top:18px}}
.grid{{display:grid;gap:18px}} .kpis{{grid-template-columns:repeat(6,1fr);margin:22px 0}}
.card{{background:var(--panel);border:1px solid var(--line);border-radius:18px;padding:22px;box-shadow:0 4px 18px rgba(34,47,41,.04)}}
.kpi .value{{font:700 32px/1 Georgia,serif;color:var(--green)}} .kpi .label{{font-size:13px;color:var(--muted);margin-top:6px}}
.section{{margin-top:42px}} .section-head{{display:flex;align-items:end;justify-content:space-between;gap:20px;margin-bottom:16px}}
h2{{font:700 30px/1.2 Georgia,"Noto Serif SC",serif;margin:0}} h3{{margin:0 0 10px;font-size:18px}} .sub{{color:var(--muted);max-width:760px}}
.flow{{display:grid;grid-template-columns:repeat(5,1fr);gap:28px;align-items:stretch}}
.flow-step{{position:relative;background:var(--panel);border:1px solid var(--line);border-radius:17px;padding:18px}}
.flow-step:not(:last-child):after{{content:"→";position:absolute;right:-23px;top:42%;font-size:25px;color:var(--gold)}}
.step-num{{font:700 24px Georgia;color:var(--green)}} .step-state{{font-size:12px;font-weight:700;color:var(--green);text-transform:uppercase}}
.step-state.pending{{color:var(--red)}}
.two{{grid-template-columns:1.25fr .75fr}} .three{{grid-template-columns:repeat(3,1fr)}}
.story-row{{display:grid;grid-template-columns:180px 1fr 70px;gap:12px;align-items:center;margin:11px 0;font-size:13px}}
.track{{height:13px;background:#e9e4da;border-radius:20px;overflow:hidden;display:flex}} .accepted{{background:var(--green)}} .rejected{{background:var(--red)}}
.legend{{display:flex;gap:16px;font-size:12px;color:var(--muted)}} .dot{{width:9px;height:9px;border-radius:50%;display:inline-block;margin-right:5px}}
.bar-row{{display:grid;grid-template-columns:125px 1fr 42px;gap:10px;align-items:center;margin:10px 0;font-size:13px}} .bar{{height:11px;background:#ebe5da;border-radius:10px;overflow:hidden}} .bar i{{display:block;height:100%;background:var(--green);border-radius:10px}}
table{{width:100%;border-collapse:collapse;font-size:13px}} th,td{{padding:11px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}} th{{color:var(--muted);font-weight:600}}
.tag{{display:inline-flex;padding:3px 9px;border-radius:999px;background:#e3efe9;color:var(--green);font-size:11px;font-weight:700}} .tag.bad{{background:#f5dfdc;color:var(--red)}}
.callout{{border-left:4px solid var(--gold);background:#fff7e4;padding:16px 18px;border-radius:4px 14px 14px 4px}}
.tabs{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px}} .tab{{border:1px solid var(--line);background:var(--panel);padding:8px 12px;border-radius:10px;cursor:pointer;color:var(--muted)}} .tab.active{{background:var(--green);color:white;border-color:var(--green)}}
.prompt{{display:none}} .prompt.active{{display:block}} details{{border:1px solid var(--line);border-radius:13px;background:#faf7f0;margin-top:10px}} summary{{cursor:pointer;padding:12px 15px;font-weight:700}} pre{{white-space:pre-wrap;word-break:break-word;margin:0;padding:16px;border-top:1px solid var(--line);font:12px/1.65 ui-monospace,SFMono-Regular,monospace;max-height:450px;overflow:auto}}
.filters{{display:grid;grid-template-columns:1.5fr repeat(3,1fr);gap:10px;margin-bottom:14px}} input,select{{width:100%;border:1px solid var(--line);background:white;padding:10px;border-radius:10px;color:var(--ink)}}
.case-list{{display:grid;grid-template-columns:repeat(2,1fr);gap:13px}} .case{{padding:17px;border:1px solid var(--line);border-radius:15px;background:#fff}} .case-top{{display:flex;justify-content:space-between;gap:10px}} .case-id{{font:600 12px ui-monospace,monospace;color:var(--muted)}} .ftp{{margin-top:12px;font-size:13px}} .ftp b{{color:var(--green)}} .case-links{{display:flex;flex-wrap:wrap;gap:12px;margin-top:12px;font-size:12px}}
.complete{{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}} .check{{padding:12px;border-radius:12px;background:#eef6f2;font-size:13px}} .check.no{{background:#f8e8e5}} .check.partial{{background:#fff2cf}} .check strong{{display:block}}
.oracle-text{{font-family:"Noto Serif SC",serif;background:#f8f4eb;padding:13px;border-radius:12px;font-size:13px}}
.footer{{color:var(--muted);font-size:12px;text-align:center;padding:42px 0 18px}}
@media(max-width:1000px){{.kpis{{grid-template-columns:repeat(3,1fr)}}.flow{{grid-template-columns:1fr}}.flow-step:after{{display:none}}.two,.three{{grid-template-columns:1fr}}}}
@media(max-width:680px){{.shell{{padding:14px}}.hero{{padding:28px 22px}}.kpis{{grid-template-columns:repeat(2,1fr)}}.case-list{{grid-template-columns:1fr}}.filters{{grid-template-columns:1fr}}.story-row{{grid-template-columns:120px 1fr 45px}}}}
</style>
</head>
<body>
<main class="shell">
  <header class="hero">
    <div class="eyebrow">Stone-eval · Narrative causality benchmark</div>
    <h1>CFPG 短篇原文复现实验</h1>
    <p>把长篇摘要上的 Foreshadow–Trigger–Payoff 框架迁移到 10 篇短篇小说原文。页面区分数据抽取、句级适配、Oracle 生成和在线追踪，所有结论都能回到原始 JSONL、review 与原文段落。</p>
    <div class="status">◐ 部分复现：抽取完成，完整生成评测待运行</div>
    <div class="hero-links"><a class="button" href="experiment_report.html">阅读渲染报告</a><a class="button ghost" href="experiment_report.md">原始 Markdown</a><a class="button ghost" href="../results/extraction/runs/{RUN_ID}/summary.json">抽取 summary.json</a><a class="button ghost" href="../results/oracle_smoke_20260713/oracle.jsonl">Oracle 原始结果</a></div>
  </header>

  <section class="grid kpis" id="kpis"></section>

  <section class="section">
    <div class="section-head"><div><h2>实验流程与完成状态</h2><div class="sub">绿色为已完成并有落盘结果；红色为代码已实现但尚无全量运行结果。</div></div></div>
    <div class="flow">
      <div class="flow-step"><div class="step-state">完成</div><div class="step-num">10 篇</div><h3>短篇原文</h3><div class="sub">直接输入 normalized_texts，不经过摘要。</div></div>
      <div class="flow-step"><div class="step-state">完成</div><div class="step-num">30 条</div><h3>候选抽取</h3><div class="sub">每篇最多 3 条 F–T–P 候选。</div></div>
      <div class="flow-step"><div class="step-state">完成</div><div class="step-num">25 / 5</div><h3>Verifier</h3><div class="sub">25 接受，5 拒绝；单模型验证。</div></div>
      <div class="flow-step"><div class="step-state">完成</div><div class="step-num">25 条</div><h3>句级适配</h3><div class="sub">P#### → P####S### weak alignment。</div></div>
      <div class="flow-step"><div class="step-state pending">部分完成</div><div class="step-num">1 / 25</div><h3>生成评测</h3><div class="sub">Oracle smoke 已跑；全量 Oracle/Tracking 未跑。</div></div>
    </div>
  </section>

  <section class="section grid two">
    <div class="card"><div class="section-head"><div><h2>逐作品结果</h2><div class="sub">每篇固定抽取 3 条，条形图显示接受与拒绝。</div></div><div class="legend"><span><i class="dot accepted"></i>接受</span><span><i class="dot rejected"></i>拒绝</span></div></div><div id="stories"></div></div>
    <div class="card"><h2>伏笔跨度</h2><div class="sub">25 条 accepted triples 的 F–P 段落距离。</div><div id="spans" style="margin-top:20px"></div><div class="callout" style="margin-top:18px"><b>均值 43.08</b>，中位数 25，范围 4–174 段。数据包含显著的长距离叙事依赖。</div></div>
  </section>

  <section class="section grid three">
    <div class="card"><h2>伏笔主类型</h2><div class="sub">只描述文本承载形式</div><div id="ftypes"></div></div>
    <div class="card"><h2>叙事功能</h2><div class="sub">误导、警告、反讽等独立维度</div><div id="functions"></div></div>
    <div class="card"><h2>Payoff 类型</h2><div id="ptypes"></div></div>
  </section>

  <section class="section">
    <div class="section-head"><div><h2>各流程采用的提示词</h2><div class="sub">展示实际模板和版本号。句级适配是确定性程序，不调用模型。</div></div><a href="../prompts/short_story_prompts.md">打开权威 Prompt 文件 ↗</a></div>
    <div class="tabs" id="prompt-tabs"></div><div id="prompt-panels"></div>
  </section>

  <section class="section grid two">
    <div class="card"><h2>Oracle smoke：真实输出</h2><div id="oracle"></div></div>
    <div class="card"><h2>与原论文比较</h2>
      <table><thead><tr><th>数据 / 模型</th><th>方法</th><th>Should-Payoff</th><th>Avg. Score</th></tr></thead><tbody>
        <tr><td>Paper BookSum / GPT-4.1-mini</td><td>Prompt</td><td>—</td><td>0.569</td></tr>
        <tr><td>Paper BookSum / GPT-4.1-mini</td><td>CFPG</td><td>1.000</td><td>0.911</td></tr>
        <tr><td>Paper BookSum / Claude-Haiku-4.5</td><td>CFPG</td><td>0.965</td><td>0.940</td></tr>
        <tr><td>本实验《促织》/ DeepSeek V4 Pro</td><td>Prompt</td><td>—</td><td>1.000</td></tr>
        <tr><td>本实验《促织》/ DeepSeek V4 Pro</td><td>CFPG</td><td>1.000</td><td>1.000</td></tr>
      </tbody></table>
      <div class="callout" style="margin-top:16px">本实验只有 1 个经典文本案例，且 Prompt 已几乎复现原文，不能与论文的 629 条 BookSum 数据直接比较，也不能据此声称超过论文。</div>
    </div>
  </section>

  <section class="section">
    <div class="section-head"><div><h2>30 条候选结果浏览器</h2><div class="sub">筛选作品、接受状态与类型；每条都提供原文、候选、verifier 和 review 链接。</div></div><div id="shown"></div></div>
    <div class="filters"><input id="search" placeholder="搜索 F / T / P / ID"><select id="story-filter"><option value="">全部小说</option></select><select id="status-filter"><option value="">全部状态</option><option value="accepted">通过</option><option value="rejected">拒绝</option></select><select id="type-filter"><option value="">全部类型</option></select></div>
    <div class="case-list" id="cases"></div>
  </section>

  <section class="section grid two">
    <div class="card"><h2>复现完成度审计</h2><div class="complete">
      <div class="check"><strong>✓ 短篇原文输入</strong>10 篇，不生成摘要</div>
      <div class="check"><strong>✓ F–T–P 抽取</strong>30 条候选，25 条通过</div>
      <div class="check"><strong>✓ Oracle 实现</strong>Prompt / CFPG + judge</div>
      <div class="check"><strong>✓ Tracking 实现</strong>FAP / FSCR / CFPG</div>
      <div class="check no"><strong>✗ 双独立 verifier</strong>当前只有单模型 verifier</div>
      <div class="check partial"><strong>△ Oracle 全量运行</strong>代码完成；结果当前 1 / 25</div>
      <div class="check partial"><strong>△ Tracking 全量运行</strong>代码完成；结果尚未运行</div>
      <div class="check no"><strong>✗ Attention saliency</strong>API 模型无法读取内部注意力</div>
    </div></div>
    <div class="card"><h2>结论边界</h2><p>这是<strong>方法与指标的部分复现</strong>，不是论文数值的完全复现。Oracle 和 Tracking 的程序均已实现；“1 / 25”表示只完成 1 条真实 API 运行，不表示缺少代码。</p><p>主要结果缺口是剩余 24 条 Oracle、逐句 tracking、双 verifier、人评和 attention 分析。现有经典小说也可能被模型记忆，正式结论需要 clean-source 重抽取、独立 judge 和未公开文本对照。</p><a href="experiment_report.html">查看 Oracle 完整度说明 ↗</a></div>
  </section>
  <div class="footer">Generated from local JSON/JSONL · 2026-07-13 · No external frontend dependencies</div>
</main>
<script id="report-data" type="application/json">{data}</script>
<script>
const D=JSON.parse(document.getElementById('report-data').textContent);
const $=s=>document.querySelector(s); const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]));
const kpis=[['10','测试小说'],['30','候选 F–T–P'],['25','Verifier 通过'],['83.33%','接受率'],['43.08','平均跨度 / 段'],['1 / 25','Oracle 已运行']];
$('#kpis').innerHTML=kpis.map(x=>`<div class="card kpi"><div class="value">${{x[0]}}</div><div class="label">${{x[1]}}</div></div>`).join('');
const stories=D.summary.stories; $('#stories').innerHTML=stories.map(s=>`<div class="story-row"><span><b>${{esc(s.story_id)}}</b><br><small>${{esc((D.cases.find(c=>c.story_id===s.story_id)||{{}}).title||'')}}</small></span><div class="track"><i class="accepted" style="width:${{s.accepted_count/3*100}}%"></i><i class="rejected" style="width:${{s.rejected_count/3*100}}%"></i></div><b>${{s.accepted_count}} / 3</b></div>`).join('');
function bars(target,obj,color='var(--green)'){{const max=Math.max(...Object.values(obj));$(target).innerHTML=Object.entries(obj).sort((a,b)=>b[1]-a[1]).map(([k,v])=>`<div class="bar-row"><span>${{esc(k)}}</span><div class="bar"><i style="width:${{v/max*100}}%;background:${{color}}"></i></div><b>${{v}}</b></div>`).join('')}}
const typeNames={{object:'物件',event:'事件',dialogue:'对话/言语',rule:'规则',environment_description:'环境描写',character_state:'人物状态',narrator_commentary:'叙述者评论'}};
const functionNames={{direct_setup:'直接铺垫',anomaly:'反常细节',misdirection:'误导',warning:'警告',retrospective_reinterpretation:'回顾性重释',ironic_contrast:'反讽对照',symbolic_reframing:'象征性重构'}};
const payoffNames={{literal:'直接兑现',delayed_revelation:'延迟揭示',ironic:'反讽回收',symbolic:'象征回收',misdirection:'误导揭示'}};
function named(obj,names){{return Object.fromEntries(Object.entries(obj).map(([k,v])=>[names[k]||k,v]))}}
bars('#ftypes',named(D.accepted_types,typeNames));bars('#functions',named(D.narrative_functions,functionNames),'var(--gold)');bars('#ptypes',named(D.payoff_types,payoffNames),'var(--blue)');
const maxBin=Math.max(...D.span_bins.map(x=>x.count));$('#spans').innerHTML=D.span_bins.map(x=>`<div class="bar-row"><span>${{x.label}} 段</span><div class="bar"><i style="width:${{x.count/maxBin*100}}%;background:var(--gold)"></i></div><b>${{x.count}}</b></div>`).join('');
const promptNames={{short_story_candidate_extraction:'① 候选抽取',short_story_candidate_verification:'② 严格验证',short_story_fap_decision:'③ FAP 决策',short_story_cfpg_decision:'④ CFPG Gate',short_story_continuation:'⑤ 一句续写',short_story_continuation_judge:'⑥ 轨迹评判',short_story_tracking_decision:'旧版状态追踪'}};
$('#prompt-tabs').innerHTML=D.prompts.map((p,i)=>`<button class="tab ${{i===0?'active':''}}" data-i="${{i}}">${{esc(promptNames[p.key]||p.key)}}</button>`).join('');
$('#prompt-panels').innerHTML=D.prompts.map((p,i)=>`<div class="prompt card ${{i===0?'active':''}}" data-i="${{i}}"><div class="case-top"><h3>${{esc(p.key)}}</h3><span class="tag">${{esc(p.version)}}</span></div><details open><summary>System prompt</summary><pre>${{esc(p.system)}}</pre></details><details><summary>User prompt template</summary><pre>${{esc(p.user)}}</pre></details></div>`).join('');
document.querySelectorAll('.tab').forEach(b=>b.onclick=()=>{{document.querySelectorAll('.tab,.prompt').forEach(x=>x.classList.remove('active'));b.classList.add('active');document.querySelector(`.prompt[data-i="${{b.dataset.i}}"]`).classList.add('active')}});
$('#oracle').innerHTML=D.oracle.map(r=>`<div style="margin:15px 0"><div class="case-top"><h3>${{r.method.toUpperCase()}}</h3><span class="tag">Score ${{r.judgment.score}}</span></div>${{r.activation_decision?`<p><b>Gate:</b> ${{r.should_payoff?'触发':'不触发'}} · confidence ${{r.activation_decision.confidence}}</p>`:'<p class="sub">无显式 gate</p>'}}<div class="oracle-text">${{esc(r.generated_continuation)}}</div><p class="sub"><b>Judge:</b> ${{esc(r.judgment.rationale)}}</p></div>`).join('');
const storyOptions=[...new Set(D.cases.map(c=>c.story_id))];$('#story-filter').innerHTML+=[...storyOptions].map(x=>`<option value="${{x}}">${{x}} · ${{esc(D.cases.find(c=>c.story_id===x).title)}}</option>`).join('');
const types=[...new Set(D.cases.map(c=>c.primary_type))].sort();$('#type-filter').innerHTML+=types.map(x=>`<option value="${{x}}">${{typeNames[x]||x}}</option>`).join('');
function renderCases(){{const q=$('#search').value.toLowerCase(),story=$('#story-filter').value,status=$('#status-filter').value,type=$('#type-filter').value;const rows=D.cases.filter(c=>(!story||c.story_id===story)&&(!status||(status==='accepted')===c.accepted)&&(!type||c.primary_type===type)&&(!q||JSON.stringify(c).toLowerCase().includes(q)));$('#shown').textContent=`显示 ${{rows.length}} / ${{D.cases.length}} 条`;$('#cases').innerHTML=rows.map(c=>`<article class="case"><div class="case-top"><div><div class="case-id">${{esc(c.id)}}</div><b>${{esc(c.title)}} · ${{esc(c.story_id)}}</b></div><span class="tag ${{c.accepted?'':'bad'}}">${{c.accepted?'通过':'拒绝'}}</span></div><div style="margin-top:8px"><span class="tag">${{esc(typeNames[c.primary_type]||c.primary_type)}}</span> <span class="tag">${{esc(functionNames[c.narrative_function]||c.narrative_function)}}</span> <span class="tag">跨度 ${{c.distance}} 段</span></div><div class="ftp"><p><b>F ${{esc(c.foreshadow_span)}}</b> · ${{esc(c.foreshadow)}}</p><p><b>T</b> · ${{esc(c.trigger)}}</p><p><b>P ${{esc(c.payoff_span)}}</b> · ${{esc(c.payoff)}}</p>${{c.accepted?`<p><b>Verifier</b> · ${{esc(c.rationale)}}</p>`:`<p style="color:var(--red)"><b>拒绝原因</b> · ${{esc(c.rejection_reason||c.rationale)}}</p>`}}</div><details><summary>查看原始语言摘录</summary><pre>F: ${{esc(c.foreshadow_excerpt)}}\n\nP: ${{esc(c.payoff_excerpt)}}</pre></details><div class="case-links"><a href="${{c.links.source}}">中文全文 ↗</a><a href="${{c.links.source_original}}">原语言全文 ↗</a><a href="${{c.links.review}}">Review ↗</a><a href="${{c.links.candidates}}">Candidates JSONL ↗</a><a href="${{c.links.verified}}">Verifier JSONL ↗</a></div></article>`).join('')}}
['#search','#story-filter','#status-filter','#type-filter'].forEach(s=>$(s).addEventListener('input',renderCases));renderCases();
</script>
</body></html>"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(payload), encoding="utf-8")
    subprocess.run(
        [
            "pandoc",
            str(REPORT_MD),
            "--standalone",
            "--toc",
            "--toc-depth=3",
            "--self-contained",
            f"--css={REPORT_CSS}",
            "--metadata=lang:zh-CN",
            "--metadata=title:CFPG 短篇小说原文复现实验报告",
            f"--output={REPORT_HTML}",
        ],
        check=True,
    )
    print(
        f"wrote {args.output} with {len(payload['cases'])} cases and "
        f"{len(payload['prompts'])} prompt templates; rendered {REPORT_HTML}"
    )


if __name__ == "__main__":
    main()
