#!/usr/bin/env python3
"""Generate D3.js visualization HTML from honglou_structured_script.json."""
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT = PROJECT_ROOT / "outputs" / "honglou_value_graph" / "honglou_structured_script.json"
OUTPUT = PROJECT_ROOT / "outputs" / "honglou_value_graph" / "honglou_value_graph_visualization.html"

GROUP_COLORS = {
    "Prologue":    {"fill": "#e8eaf6", "stroke": "#3949ab", "label": "序幕"},
    "Act1_Rise":   {"fill": "#e3f2fd", "stroke": "#1e88e5", "label": "兴起"},
    "Act2_Climax": {"fill": "#fff3e0", "stroke": "#fb8c00", "label": "鼎盛"},
    "Act3_Turn":   {"fill": "#fce4ec", "stroke": "#e53935", "label": "转折"},
    "Act4_Fall":   {"fill": "#f3e5f5", "stroke": "#8e24aa", "label": "衰败"},
    "Endings":     {"fill": "#e8f5e9", "stroke": "#2e7d32", "label": "结局"},
    "ForeshadowLines": {"fill": "#efebe9", "stroke": "#6d4c41", "label": "伏笔"},
}

HTML_TEMPLATE = r"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>红楼梦 · 价值转化图</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, "Noto Sans CJK SC", "Microsoft YaHei", sans-serif;
  background: #fafafa; overflow: hidden; width: 100vw; height: 100vh;
}
#app { display: flex; width: 100%; height: 100%; }
#graph-panel { flex: 1; min-width: 0; display: flex; flex-direction: column; }
#graph-canvas { flex: 1; min-height: 0; position: relative; }
svg#main-svg { width: 100%; height: 100%; }
#sidebar { width: 336px; min-width: 280px; border-left: 1px solid #ddd; overflow-y: auto; padding: 16px 14px; background: #fff; }
#sidebar h2 { font-size: 17px; color: #263238; margin-bottom: 6px; }
#sidebar h3 { font-size: 13px; color: #546e7a; margin: 14px 0 4px; }
#sidebar .stat { font-size: 12px; color: #78909c; line-height: 1.7; }
#detail { margin-top: 12px; padding: 10px; background: #f5f5f5; border-radius: 6px; font-size: 12px; line-height: 1.55; color: #37474f; }
#detail .title { font-size: 14px; font-weight: 700; color: #263238; }
#detail .group { display: inline-block; margin: 4px 0; padding: 1px 7px; border-radius: 4px; font-size: 11px; }
#detail .vt { margin: 3px 0; padding: 2px 6px; border-left: 3px solid #ff9800; font-size: 11px; background: #fff8e1; }
#detail .ref { font-size: 11px; color: #6d4c41; }
#legend { position: absolute; left: 12px; bottom: 12px; padding: 8px 12px; background: rgba(255,255,255,.92); border-radius: 6px; border: 1px solid #e0e0e0; font-size: 11px; line-height: 1.7; }
#legend span { display: inline-block; min-width: 100px; }
#legend .dot { display: inline-block; width: 10px; height: 10px; border-radius: 2px; margin-right: 5px; vertical-align: middle; position: relative; top: -1px; }
#legend .dot.ending { border-radius: 50%; }
#controls { position: absolute; right: 12px; top: 12px; display: flex; gap: 4px; }
#controls button { padding: 4px 10px; border: 1px solid #ccc; border-radius: 4px; background: #fff; cursor: pointer; font-size: 12px; }
#controls button:hover { background: #f5f5f5; }
#search { position: absolute; left: 12px; top: 12px; }
#search input { padding: 4px 8px; border: 1px solid #ccc; border-radius: 4px; width: 180px; font-size: 12px; }
#panel-resizer { height: 8px; border-top: 1px solid #ddd; border-bottom: 1px solid #ddd; background: #eceff1; cursor: row-resize; flex: 0 0 auto; }
#panel-resizer:hover { background: #cfd8dc; }
#foreshadow-panel { height: 300px; min-height: 120px; max-height: 70vh; background: #fff; padding: 10px 14px; overflow: hidden; display: flex; flex-direction: column; }
#foreshadow-panel h3 { font-size: 13px; color: #263238; margin-bottom: 6px; }
#foreshadow-list { flex: 1; min-height: 0; overflow-y: auto; padding-right: 6px; }
.foreshadow-item { padding: 7px 0; border-bottom: 1px solid #eee; font-size: 11px; line-height: 1.55; color: #37474f; }
.foreshadow-item .meta { color: #78909c; font-family: Consolas, "SFMono-Regular", monospace; }
.foreshadow-item .stage { margin-top: 2px; }
.foreshadow-item .stage-label { display: inline-block; min-width: 48px; font-weight: 700; color: #546e7a; }
.foreshadow-item .trigger .stage-label { color: #fb8c00; }
.foreshadow-item .payoff .stage-label { color: #e91e63; }
.edge-label { font-size: 9px; fill: #90a4ae; pointer-events: none; }
.ft-edge { stroke-dasharray: 5,3; }
.tooltip { position: absolute; pointer-events: none; padding: 6px 8px; background: rgba(33,33,33,.88); color: #fff; border-radius: 4px; font-size: 11px; max-width: 240px; line-height: 1.4; display: none; z-index: 10; }
</style>
</head>
<body>
<div id="app">
  <div id="graph-panel">
    <div id="graph-canvas">
      <svg id="main-svg"></svg>
      <div id="search"><input type="text" placeholder="搜索场景…" id="search-input"></div>
      <div id="controls">
        <button onclick="zoomIn()">＋</button>
        <button onclick="zoomOut()">－</button>
        <button onclick="zoomReset()">重置</button>
      </div>
      <div id="legend">__LEGEND__</div>
      <div class="tooltip" id="tooltip"></div>
    </div>
    <div id="panel-resizer" title="拖拽调整伏笔列表高度"></div>
    <div id="foreshadow-panel">
      <h3>伏笔 - Trigger - 回收列表（全部 30 条）</h3>
      <div id="foreshadow-list"></div>
    </div>
  </div>
  <div id="sidebar">
    <h2>红楼梦 · 价值转化图</h2>
    <p class="stat">前80回 | __SCENES__ 个场景节点 | __NODES__ 个节点</p>
    <p class="stat">__NPCS__ NPC | 30条伏笔三元组 | 8条价值轴</p>
    <h3>价值轴</h3>
    <p class="stat">__AXES__</p>
    <div id="detail"><em>点击节点查看详情</em></div>
  </div>
</div>
<script src="https://d3js.org/d3.v7.min.js"></script>
<script>
const data = __DATA__;

const groupColors = __GROUP_COLORS__;

const nodeTypes = {
  "scene_node": { shape: "rect", r: 0, w: 150, h: 52, cls: "scene" },
  "transition_node": { shape: "circle", r: 6, w: 0, h: 0, cls: "trans" },
  "ending_node": { shape: "circle", r: 28, w: 0, h: 0, cls: "ending" },
};

function chapterLabel(d) {
  if (!d.chapter_range) return "";
  const raw = String(d.chapter_range);
  return raw.includes("回") ? `第${raw}` : `第${raw}回`;
}

function nodeColor(d) {
  if (d.type === "ending_node") return groupColors["Endings"] || {fill:"#e8f5e9", stroke:"#2e7d32"};
  if (d.type === "transition_node") return {fill: "#bdbdbd", stroke: "#757575"};
  return groupColors[d.group] || {fill: "#eceff1", stroke: "#90a4ae"};
}

// Build graph
const graphNodes = [];
const graphEdges = [];
const nodeMap = {};

function chapterStart(value) {
  const match = String(value || "").match(/\d+/);
  return match ? Number(match[0]) : Number.MAX_SAFE_INTEGER;
}

for (const n of data.nodes) {
  const t = nodeTypes[n.type] || nodeTypes["scene_node"];
  let label = "";
  if (n.type === "scene_node") {
    label = n.title || n.id;
  } else if (n.type === "ending_node") {
    label = (n.ending_title || n.id).substring(0, 12);
  } else {
    label = "";
  }
  const gn = {
    id: n.id, type: n.type, group: n.group, label: label,
    narrative: n.narrative || "",
    chapter_range: n.chapter_range || "",
    value_transformations: n.value_transformations || [],
    character_decisions: n.character_decisions || [],
    foreshadow_refs: n.foreshadow_refs || [],
    payoff_refs: n.payoff_refs || [],
    shape: t.shape, r: t.r, w: t.w, h: t.h, cls: t.cls,
    sourceIndex: graphNodes.length,
    startChapter: chapterStart(n.chapter_range),
  };
  graphNodes.push(gn);
  nodeMap[n.id] = gn;
}

const sceneNodes = graphNodes.filter(n => n.type === "scene_node");
const transitionNodes = graphNodes.filter(n => n.type === "transition_node");
const endingNodes = graphNodes.filter(n => n.type === "ending_node");
const chronologicalScenes = sceneNodes
  .slice()
  .sort((a, b) => (a.startChapter - b.startChapter) || (a.sourceIndex - b.sourceIndex));

const layout = { left: 110, top: 90, col: 190, row: 135, columns: 6 };
function timelinePosition(index) {
  return {
    x: layout.left + (index % layout.columns) * layout.col,
    y: layout.top + Math.floor(index / layout.columns) * layout.row,
  };
}

chronologicalScenes.forEach((node, index) => {
  const p = timelinePosition(index);
  node.timeIndex = index;
  node.x = node.fx = p.x;
  node.y = node.fy = p.y;
});

transitionNodes.forEach((node, index) => {
  const source = chronologicalScenes[index];
  const target = chronologicalScenes[index + 1];
  if (!source || !target) return;
  node.timeIndex = index + 0.5;
  node.x = node.fx = (source.fx + target.fx) / 2;
  node.y = node.fy = (source.fy + target.fy) / 2;
  graphEdges.push({ source: source.id, target: node.id, type: "linear" });
  graphEdges.push({ source: node.id, target: target.id, type: "linear" });
});

const endingY = layout.top + Math.ceil(chronologicalScenes.length / layout.columns) * layout.row + 20;
endingNodes.forEach((node, index) => {
  node.timeIndex = chronologicalScenes.length + index;
  node.x = node.fx = layout.left + (layout.columns / 2 - 0.5 + index) * layout.col;
  node.y = node.fy = endingY;
});
for (const ending of endingNodes) {
  const lastScene = chronologicalScenes[chronologicalScenes.length - 1];
  if (lastScene) graphEdges.push({ source: lastScene.id, target: ending.id, type: "ending" });
}

// Foreshadow/payoff edges
for (const n of graphNodes) {
  if (n.type !== "scene_node") continue;
  for (const ref of n.foreshadow_refs) {
    for (const m of graphNodes) {
      if (m.type === "scene_node" && m.payoff_refs && m.payoff_refs.includes(ref)) {
        graphEdges.push({ source: n.id, target: m.id, type: "foreshadow", ref: ref });
      }
    }
  }
}

// D3 setup
const svg = document.getElementById("main-svg");
const width = () => document.getElementById("graph-canvas").clientWidth;
const height = () => document.getElementById("graph-canvas").clientHeight;
svg.setAttribute("viewBox", `0 0 1200 900`);

const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
svg.appendChild(g);

// Defs
const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
defs.innerHTML = `<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#90a4ae"/></marker>`;
svg.appendChild(defs);

// Edge group
const edgeG = document.createElementNS("http://www.w3.org/2000/svg", "g");
g.appendChild(edgeG);

// Node group
const nodeG = document.createElementNS("http://www.w3.org/2000/svg", "g");
g.appendChild(nodeG);

// Simulation
function edgeEndpointId(endpoint) {
  return endpoint && typeof endpoint === "object" ? endpoint.id : endpoint;
}

const validGraphEdges = graphEdges.filter(e => nodeMap[edgeEndpointId(e.source)] && nodeMap[edgeEndpointId(e.target)]);

const simulation = d3.forceSimulation(graphNodes)
  .force("link", d3.forceLink(validGraphEdges).id(d => d.id).distance(d => d.type === "foreshadow" ? 220 : 80).strength(0.05))
  .force("charge", d3.forceManyBody().strength(-40))
  .force("collide", d3.forceCollide(45))
  .alpha(0.01);

const link = d3.select(edgeG).selectAll("path")
  .data(validGraphEdges)
  .join("path")
  .attr("class", d => d.type === "foreshadow" ? "ft-edge" : "")
  .attr("fill", "none")
  .attr("stroke", d => d.type === "foreshadow" ? "#e91e63" : d.type === "ending" ? "#66a06f" : "#bdbdbd")
  .attr("stroke-width", d => d.type === "foreshadow" ? 2.5 : d.type === "ending" ? 2 : 1.8)
  .attr("opacity", d => d.type === "foreshadow" ? 0.7 : d.type === "ending" ? 0.6 : 0.55)
  .attr("marker-end", d => d.type === "linear" || d.type === "ending" ? "url(#arrow)" : null);

const nodeSel = d3.select(nodeG).selectAll("g")
  .data(graphNodes)
  .join("g")
  .attr("cursor", d => d.type === "transition_node" ? "default" : "pointer")
  .call(d3.drag()
    .on("start", (event, d) => { if (!event.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
    .on("drag", (event, d) => { d.fx = event.x; d.fy = event.y; })
    .on("end", (event, d) => { if (!event.active) simulation.alphaTarget(0); d.fx = d.x; d.fy = d.y; }))
  .on("click", (event, d) => showDetail(d))
  .on("mouseenter", (event, d) => { showTooltip(event, d); })
  .on("mouseleave", () => { document.getElementById("tooltip").style.display = "none"; });

nodeSel.filter(d => d.shape === "rect").append("rect")
  .attr("width", d => d.w).attr("height", d => d.h)
  .attr("x", d => -d.w/2).attr("y", d => -d.h/2)
  .attr("rx", 6).attr("ry", 6)
  .attr("fill", d => (nodeColor(d)).fill)
  .attr("stroke", d => (nodeColor(d)).stroke)
  .attr("stroke-width", 2.2);

nodeSel.filter(d => d.shape === "rect").append("text")
  .attr("text-anchor", "middle").attr("dy", "-0.25em")
  .attr("fill", "#263238").attr("font-size", "11px").attr("font-weight", "600")
  .text(d => d.label.length > 14 ? d.label.substring(0, 13) + "…" : d.label);

nodeSel.filter(d => d.type === "scene_node").append("text")
  .attr("text-anchor", "middle").attr("dy", "1.2em")
  .attr("fill", "#607d8b").attr("font-size", "9px")
  .text(d => chapterLabel(d));

nodeSel.filter(d => d.shape === "circle" && d.type === "transition_node").append("circle")
  .attr("r", d => d.r)
  .attr("fill", "#bdbdbd").attr("stroke", "#9e9e9e").attr("stroke-width", 1.5);

nodeSel.filter(d => d.shape === "circle" && d.type === "ending_node").append("circle")
  .attr("r", d => d.r)
  .attr("fill", d => (nodeColor(d)).fill)
  .attr("stroke", d => (nodeColor(d)).stroke)
  .attr("stroke-width", 3)
  .attr("stroke-dasharray", "6,3");

nodeSel.filter(d => d.type === "ending_node").append("text")
  .attr("text-anchor", "middle").attr("dy", "0.35em")
  .attr("fill", "#263238").attr("font-size", "10px").attr("font-weight", "600")
  .text(d => d.label);

simulation.on("tick", () => {
  link.attr("d", d => {
    if (d.type === "linear" || d.type === "ending") {
      return `M ${d.source.x} ${d.source.y} L ${d.target.x} ${d.target.y}`;
    }
    const dx = d.target.x - d.source.x;
    const dy = d.target.y - d.source.y;
    const dr = Math.sqrt(dx * dx + dy * dy) * 2.5;
    return `M ${d.source.x} ${d.source.y} A ${dr} ${dr} 0 0 1 ${d.target.x} ${d.target.y}`;
  });
  nodeSel.attr("transform", d => `translate(${d.x}, ${d.y})`);
});

// Zoom
const zoom = d3.zoom().scaleExtent([0.2, 4]).on("zoom", (event) => {
  g.setAttribute("transform", event.transform);
});
d3.select(svg).call(zoom);

function zoomIn() { d3.select(svg).transition().call(zoom.scaleBy, 1.3); }
function zoomOut() { d3.select(svg).transition().call(zoom.scaleBy, 0.7); }
function zoomReset() { d3.select(svg).transition().call(zoom.transform, d3.zoomIdentity); }

// Detail panel
function showDetail(d) {
  if (d.type === "transition_node") return;
  const detail = document.getElementById("detail");
  let html = `<div class="title">${d.label || d.id}</div>`;
  const c = nodeColor(d);
  html += `<div class="group" style="background:${c.fill};border:1px solid ${c.stroke};">${d.group} | ${d.chapter_range}</div>`;
  if (d.narrative) html += `<p style="margin-top:6px;">${d.narrative.substring(0, 180)}${d.narrative.length > 180 ? '…' : ''}</p>`;
  if (d.value_transformations && d.value_transformations.length) {
    html += `<p style="margin-top:4px;font-weight:600;font-size:11px;">价值转化:</p>`;
    for (const vt of d.value_transformations) {
      html += `<div class="vt">${vt.axis}: ${vt.from_state} → ${vt.to_state} (${vt.direction})<br><small>${vt.turning_point_event || ''}</small></div>`;
    }
  }
  if (d.character_decisions && d.character_decisions.length) {
    html += `<p style="margin-top:4px;font-weight:600;font-size:11px;">角色抉择:</p>`;
    for (const cd of d.character_decisions) {
      html += `<p style="font-size:11px;margin:2px 0;">▸ ${cd.decision} <small style="color:#78909c;">[${cd.value_tags ? cd.value_tags.join(', ') : ''}]</small></p>`;
    }
  }
  if (d.foreshadow_refs && d.foreshadow_refs.length) {
    html += `<p class="ref" style="margin-top:4px;">🔮 伏笔: ${d.foreshadow_refs.join(', ')}</p>`;
  }
  if (d.payoff_refs && d.payoff_refs.length) {
    html += `<p class="ref">📌 回收: ${d.payoff_refs.join(', ')}</p>`;
  }
  detail.innerHTML = html;
}

function showTooltip(event, d) {
  if (d.type === "transition_node") return;
  const tip = document.getElementById("tooltip");
  tip.style.display = "block";
  tip.style.left = (event.pageX + 12) + "px";
  tip.style.top = (event.pageY - 10) + "px";
  tip.innerHTML = `<b>${d.label}</b> [${d.group}]<br>${d.chapter_range ? '第' + d.chapter_range + '回' : ''}${d.value_transformations && d.value_transformations.length ? '<br>' + d.value_transformations.map(v => v.axis).join(' | ') : ''}`;
}

// Search
document.getElementById("search-input").addEventListener("input", function() {
  const q = this.value.toLowerCase();
  for (const n of graphNodes) {
    if (n.type === "transition_node") continue;
    const el = nodeSel.filter(d => d.id === n.id);
    if (q && !n.label.toLowerCase().includes(q) && !n.id.toLowerCase().includes(q) && !n.narrative.toLowerCase().includes(q)) {
      el.attr("opacity", 0.15);
    } else {
      el.attr("opacity", 1);
    }
  }
  link.attr("opacity", q ? 0.1 : d => d.type === "foreshadow" ? 0.7 : 0.5);
});

// Resize
window.addEventListener("resize", () => {
  simulation.alpha(0.1).restart();
});

function shortText(value, maxLength = 96) {
  const text = String(value || "").trim();
  return text.length > maxLength ? text.slice(0, maxLength - 1) + "…" : text;
}

function appendStage(parent, className, label, text) {
  const line = document.createElement("div");
  line.className = `stage ${className}`;
  const stageLabel = document.createElement("span");
  stageLabel.className = "stage-label";
  stageLabel.textContent = label;
  line.appendChild(stageLabel);
  line.append(text);
  parent.appendChild(line);
}

function renderForeshadowList() {
  const list = document.getElementById("foreshadow-list");
  const rows = data.foreshadow_lines || [];
  for (const row of rows) {
    const item = document.createElement("div");
    item.className = "foreshadow-item";

    const meta = document.createElement("div");
    meta.className = "meta";
    const fChapter = row.foreshadow && row.foreshadow.chapter_index ? `第${row.foreshadow.chapter_index}回` : "伏笔";
    const tChapter = row.trigger && row.trigger.chapter_index ? `第${row.trigger.chapter_index}回` : "Trigger";
    const pChapter = row.payoff && row.payoff.chapter_index ? `第${row.payoff.chapter_index}回` : "回收";
    const distance = row.distance_chapters !== undefined ? ` · 间隔${row.distance_chapters}回` : "";
    meta.textContent = `${row.id} · ${fChapter} → ${tChapter} → ${pChapter}${distance}`;

    const foreshadow = shortText(row.foreshadow && (row.foreshadow.description || row.foreshadow.text));
    const trigger = shortText(row.trigger && row.trigger.description);
    const payoff = shortText(row.payoff && (row.payoff.description || row.payoff.text));

    item.appendChild(meta);
    appendStage(item, "foreshadow", "伏笔", foreshadow);
    appendStage(item, "trigger", "Trigger", trigger);
    appendStage(item, "payoff", "回收", payoff);
    list.appendChild(item);
  }
}

function setupPanelResizer() {
  const resizer = document.getElementById("panel-resizer");
  const panel = document.getElementById("foreshadow-panel");
  const graphPanel = document.getElementById("graph-panel");
  let startY = 0;
  let startHeight = 0;
  let dragging = false;

  resizer.addEventListener("mousedown", (event) => {
    dragging = true;
    startY = event.clientY;
    startHeight = panel.getBoundingClientRect().height;
    document.body.style.cursor = "row-resize";
    document.body.style.userSelect = "none";
  });

  window.addEventListener("mousemove", (event) => {
    if (!dragging) return;
    const available = graphPanel.getBoundingClientRect().height;
    const nextHeight = Math.max(120, Math.min(available * 0.7, startHeight - (event.clientY - startY)));
    panel.style.height = `${nextHeight}px`;
  });

  window.addEventListener("mouseup", () => {
    if (!dragging) return;
    dragging = false;
    document.body.style.cursor = "";
    document.body.style.userSelect = "";
  });
}

renderForeshadowList();
setupPanelResizer();
</script>
</body>
</html>"""


def build_legend(colors):
    items = []
    for g, c in colors.items():
        dot_cls = 'ending' if g == 'Endings' else ''
        items.append(
            f'<span><span class="dot {dot_cls}" style="background:{c["fill"]};border:2px solid {c["stroke"]}"></span>{c["label"]}</span>'
        )
    items.append('<br><span style="color:#e91e63;">--- 伏笔回收线</span>')
    items.append('<span style="color:#bdbdbd;">── 场景过渡线</span>')
    return "\n".join(items)


def main():
    with open(INPUT) as f:
        data = json.load(f)

    scenes = [n for n in data["nodes"] if n["type"] == "scene_node"]
    npc_count = len(data.get("npc", []))
    axes = data.get("value_axes", [])
    axes_str = " · ".join(axes)

    html = HTML_TEMPLATE
    html = html.replace("__DATA__", json.dumps(data, ensure_ascii=False))
    html = html.replace("__GROUP_COLORS__", json.dumps(GROUP_COLORS, ensure_ascii=False))
    html = html.replace("__LEGEND__", build_legend(GROUP_COLORS))
    html = html.replace("__SCENES__", str(len(scenes)))
    html = html.replace("__NODES__", str(len(data["nodes"])))
    html = html.replace("__NPCS__", str(npc_count))
    html = html.replace("__AXES__", axes_str)
    html = html.replace("__GROUP_COLORS__", json.dumps(GROUP_COLORS, ensure_ascii=False))

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"Wrote: {OUTPUT} ({len(html):,} bytes)")


if __name__ == "__main__":
    main()
