const state = {
  stories: [],
  story: null,
  texts: { en: null, zh: null },
  taxonomy: null,
  annotations: [],
  seeds: [],
  activeId: null,
  activeSeedId: null,
  aiVisible: false,
  language: "parallel",
  selection: null,
  dirty: false,
};

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const getActive = () => state.annotations.find((item) => item.annotation_id === state.activeId);

function escapeHtml(value = "") {
  return String(value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;",
  })[char]);
}

function getPath(object, path) {
  return path.split(".").reduce((value, key) => value?.[key], object);
}

function setPath(object, path, value) {
  const keys = path.split(".");
  const last = keys.pop();
  let target = object;
  keys.forEach((key) => {
    if (!target[key]) target[key] = {};
    target = target[key];
  });
  target[last] = value;
}

async function api(path, options = {}) {
  const response = await fetch(path, options);
  const value = await response.json();
  if (!response.ok) {
    const details = value.details?.join("；");
    throw new Error(details || value.error || `HTTP ${response.status}`);
  }
  return value;
}

function showToast(message, kind = "") {
  const toast = $("#toast");
  toast.textContent = message;
  toast.className = `toast visible ${kind}`;
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => { toast.className = "toast"; }, 2800);
}

function setDirty(value = true) {
  state.dirty = value;
  $("#saveState").textContent = value ? "有未保存更改" : "已保存";
  $("#saveState").classList.toggle("dirty", value);
}

function optionMarkup(values, blank = "请选择") {
  return `<option value="">${blank}</option>` + Object.entries(values)
    .map(([value, label]) => `<option value="${value}">${escapeHtml(label)} · ${value}</option>`)
    .join("");
}

function initTaxonomy() {
  $("#primaryType").innerHTML = optionMarkup(state.taxonomy.primary_types);
  $("#narrativeFunction").innerHTML = optionMarkup(state.taxonomy.narrative_functions);
  $("#payoffType").innerHTML = optionMarkup(state.taxonomy.payoff_types);
  $("#confidence").innerHTML = optionMarkup(state.taxonomy.confidence);
  $("#status").innerHTML = optionMarkup(state.taxonomy.status, "请选择状态");
}

function renderStoryOptions() {
  $("#storySelect").innerHTML = state.stories.map((story) => {
    const languages = story.has_en && story.has_zh ? "EN / 中" : story.has_zh ? "中" : story.source_language.toUpperCase();
    return `<option value="${story.story_id}">${escapeHtml(story.title_zh)} · ${escapeHtml(story.title_en)}  [${languages}]</option>`;
  }).join("");
}

function languageAvailability() {
  $$("[data-lang]").forEach((button) => {
    const lang = button.dataset.lang;
    const available = lang === "parallel"
      ? state.texts.en && state.texts.zh
      : Boolean(state.texts[lang]);
    button.disabled = !available;
    button.classList.toggle("active", state.language === lang);
  });
}

function paragraphMap(lang) {
  return new Map((state.texts[lang]?.paragraphs || []).map((item) => [item.id, item.text]));
}

function resolveSpanIds(span, lang) {
  if (!span) return [];
  const paragraphs = state.texts[lang]?.paragraphs || [];
  const [start, end = start] = span.split("-");
  const startIndex = paragraphs.findIndex((item) => item.id === start);
  const endIndex = paragraphs.findIndex((item) => item.id === end);
  if (startIndex < 0 || endIndex < startIndex) return [];
  return paragraphs.slice(startIndex, endIndex + 1).map((item) => item.id);
}

function spanFor(part, lang) {
  if (!part) return "";
  return part[`span_${lang}`] || (
    state.story?.source_language === lang ? part.span : ""
  );
}

function selectionFor(part, lang) {
  return part?.[`selection_${lang}`] || null;
}

function renderAnnotatedText(text, paragraphId, lang, active) {
  if (!active) return escapeHtml(text);
  const intervals = [];
  ["f", "t", "p"].forEach((role) => {
    const selection = selectionFor(active[role], lang);
    if (!selection) return;
    const startNo = paragraphNumber(selection.start_paragraph);
    const endNo = paragraphNumber(selection.end_paragraph);
    const currentNo = paragraphNumber(paragraphId);
    if (currentNo < startNo || currentNo > endNo) return;
    const start = currentNo === startNo ? selection.start_offset : 0;
    const end = currentNo === endNo ? selection.end_offset : text.length;
    if (end > start) intervals.push({ start, end, role });
  });
  if (!intervals.length) return escapeHtml(text);
  const boundaries = new Set([0, text.length]);
  intervals.forEach(({ start, end }) => {
    boundaries.add(Math.max(0, Math.min(text.length, start)));
    boundaries.add(Math.max(0, Math.min(text.length, end)));
  });
  const points = [...boundaries].sort((a, b) => a - b);
  return points.slice(0, -1).map((start, index) => {
    const end = points[index + 1];
    const roles = intervals
      .filter((interval) => interval.start < end && interval.end > start)
      .map((interval) => `exact-${interval.role}`)
      .join(" ");
    const content = escapeHtml(text.slice(start, end));
    return roles ? `<mark class="${roles}">${content}</mark>` : content;
  }).join("");
}

function quoteForSpan(span, lang) {
  const map = paragraphMap(lang);
  return resolveSpanIds(span, lang).map((id) => map.get(id)).filter(Boolean).join("\n\n");
}

function renderText() {
  const pane = $("#textPane");
  const active = getActive();
  const marks = {};
  const aiMarks = {};
  if (active) {
    ["f", "t", "p"].forEach((role) => {
      ["en", "zh"].forEach((lang) => {
        if (selectionFor(active[role], lang)) return;
        resolveSpanIds(spanFor(active[role], lang), lang).forEach((id) => {
          marks[id] = marks[id] || new Set();
          marks[id].add(role);
        });
      });
    });
  }
  if (state.aiVisible) {
    const visibleSeeds = state.activeSeedId
      ? state.seeds.filter((seed) => seed.seed_id === state.activeSeedId)
      : state.seeds;
    visibleSeeds.forEach((seed, seedIndex) => {
      ["f", "t", "p"].forEach((role) => {
        const span = seed[role]?.span;
        ["en", "zh"].forEach((lang) => {
          resolveSpanIds(span, lang).forEach((id) => {
            aiMarks[id] = aiMarks[id] || [];
            aiMarks[id].push({ role, seedIndex: state.seeds.indexOf(seed) + 1 });
          });
        });
      });
    });
  }
  const langOrder = state.language === "parallel" ? ["en", "zh"] : [state.language];
  const ids = [];
  langOrder.forEach((lang) => {
    (state.texts[lang]?.paragraphs || []).forEach((item) => {
      if (!ids.includes(item.id)) ids.push(item.id);
    });
  });
  pane.className = `text-pane mode-${state.language}`;
  pane.innerHTML = ids.map((id) => {
    const roleClasses = [...(marks[id] || [])].map((role) => `marked-${role}`).join(" ");
    const aiItems = aiMarks[id] || [];
    const aiClasses = [...new Set(aiItems.map((item) => `ai-${item.role}`))].join(" ");
    const aiBadges = aiItems.length
      ? `<span class="ai-badges">${[...new Map(aiItems.map((item) => [`${item.seedIndex}-${item.role}`, item])).values()]
          .map((item) => `<i class="ai-badge ${item.role}">AI${item.seedIndex}·${item.role.toUpperCase()}</i>`).join("")}</span>`
      : "";
    if (state.language === "parallel") {
      const enText = paragraphMap("en").get(id) || "";
      const zhText = paragraphMap("zh").get(id) || "";
      return `<article class="paragraph parallel-row ${roleClasses} ${aiClasses}" data-id="${id}">
        <button class="paragraph-id" title="选择整段 ${id}">${id}</button>
        <div class="text-column" data-id="${id}" data-lang="en" lang="en">${enText ? renderAnnotatedText(enText, id, "en", active) : "—"}</div>
        <div class="text-column" data-id="${id}" data-lang="zh" lang="zh-CN">${zhText ? renderAnnotatedText(zhText, id, "zh", active) : "—"}</div>
        ${aiBadges}
      </article>`;
    }
    const text = paragraphMap(state.language).get(id);
    if (!text) return "";
    return `<article class="paragraph ${roleClasses} ${aiClasses}" data-id="${id}">
      <button class="paragraph-id" title="选择整段 ${id}">${id}</button>
      <div class="text-column" data-id="${id}" data-lang="${state.language}" lang="${state.language}">${renderAnnotatedText(text, id, state.language, active)}</div>
      ${aiBadges}
    </article>`;
  }).join("");
}

function paragraphNumber(id) {
  return Number(id?.slice(1)) || 0;
}

function selectionSpan() {
  if (!state.selection) return "";
  const { start_paragraph: start, end_paragraph: end } = state.selection;
  return start === end ? start : `${start}-${end}`;
}

function offsetWithin(element, node, offset) {
  const range = document.createRange();
  range.selectNodeContents(element);
  range.setEnd(node, offset);
  return range.toString().length;
}

function captureBrowserSelection() {
  const browserSelection = window.getSelection();
  if (!browserSelection || browserSelection.isCollapsed || !browserSelection.rangeCount) return;
  const range = browserSelection.getRangeAt(0);
  const startElement = range.startContainer.nodeType === Node.ELEMENT_NODE
    ? range.startContainer : range.startContainer.parentElement;
  const endElement = range.endContainer.nodeType === Node.ELEMENT_NODE
    ? range.endContainer : range.endContainer.parentElement;
  const startColumn = startElement?.closest(".text-column");
  const endColumn = endElement?.closest(".text-column");
  if (!startColumn || !endColumn || !$("#textPane").contains(startColumn) || !$("#textPane").contains(endColumn)) return;
  if (startColumn.dataset.lang !== endColumn.dataset.lang) {
    browserSelection.removeAllRanges();
    showToast("请只选择一种语言；中英文范围需要分别标记", "warning");
    return;
  }
  const text = range.toString();
  if (!text.trim()) return;
  state.selection = {
    language: startColumn.dataset.lang,
    start_paragraph: startColumn.dataset.id,
    start_offset: offsetWithin(startColumn, range.startContainer, range.startOffset),
    end_paragraph: endColumn.dataset.id,
    end_offset: offsetWithin(endColumn, range.endContainer, range.endOffset),
    text,
  };
  $("#selectionLabel").textContent = `已选 ${state.selection.language === "zh" ? "中文" : "EN"} ${selectionSpan()} · ${text.length} 字符`;
}

function selectWholeParagraph(id) {
  const lang = state.language === "parallel" ? "en" : state.language;
  const text = paragraphMap(lang).get(id);
  if (!text) return;
  state.selection = {
    language: lang,
    start_paragraph: id,
    start_offset: 0,
    end_paragraph: id,
    end_offset: text.length,
    text,
  };
  $("#selectionLabel").textContent = `已选整段 ${lang === "zh" ? "中文" : "EN"} ${id} · ${text.length} 字符`;
}

function assignSelection(role) {
  const active = getActive();
  const span = selectionSpan();
  if (!active) return showToast("请先新建或选择一条三元组", "warning");
  if (!span) return showToast("请先在正文中拖选文字", "warning");
  active[role] = active[role] || {};
  const lang = state.selection.language;
  active[role][`span_${lang}`] = span;
  active[role][`selection_${lang}`] = { ...state.selection };
  active[role][`quote_${lang}`] = state.selection.text;
  if (state.story.source_language === lang || (state.story.source_language === "ja" && lang === "en")) {
    active[role].span = span;
  }
  setDirty();
  renderAll();
  $(`[data-jump="${role}"]`)?.focus();
}

function newAnnotation(seed = null) {
  const suffix = String(Date.now()).slice(-8);
  const item = {
    annotation_id: `${state.story.story_id}_ftp_${suffix}`,
    story_id: state.story.story_id,
    status: "draft",
    annotator: "",
    language_basis: state.texts.en && state.texts.zh ? "bilingual" : state.story.source_language,
    source: seed ? "cfpg_seed" : "manual",
    seed_id: seed?.seed_id || null,
    f: { span: "", span_en: "", span_zh: "", selection_en: null, selection_zh: null, quote_en: "", quote_zh: "", summary_en: "", summary_zh: "" },
    t: { span: "", span_en: "", span_zh: "", selection_en: null, selection_zh: null, quote_en: "", quote_zh: "", summary_en: "", summary_zh: "" },
    p: { span: "", span_en: "", span_zh: "", selection_en: null, selection_zh: null, quote_en: "", quote_zh: "", summary_en: "", summary_zh: "" },
    primary_type: "",
    narrative_function: "",
    payoff_type: "",
    confidence: "medium",
    rationale: "",
    notes: "",
  };
  if (seed) {
    ["f", "t", "p"].forEach((key) => Object.assign(item[key], seed[key] || {}));
    ["f", "t", "p"].forEach((key) => {
      if (item[key].span) item[key].span_en = item[key].span;
    });
    Object.assign(item, {
      primary_type: seed.primary_type || "",
      narrative_function: seed.narrative_function || "",
      payoff_type: seed.payoff_type || "",
      rationale: seed.rationale || "",
      notes: "由 CFPG 参考候选导入；请核对原文边界和解释后再标记为已复核。",
    });
    ["f", "t", "p"].forEach((key) => {
      item[key].quote_en = quoteForSpan(item[key].span, "en");
      item[key].quote_zh = quoteForSpan(item[key].span_zh, "zh");
    });
  }
  state.annotations.push(item);
  state.activeId = item.annotation_id;
  setDirty();
  renderAll();
}

function deleteActive() {
  const active = getActive();
  if (!active || !window.confirm(`删除 ${active.annotation_id}？保存后将从人工标注文件移除。`)) return;
  state.annotations = state.annotations.filter((item) => item !== active);
  state.activeId = state.annotations[0]?.annotation_id || null;
  setDirty();
  renderAll();
}

function spanLabel(part) {
  if (!part) return "尚未选择段落";
  const spans = [
    part.span_en ? `EN ${part.span_en}` : "",
    part.span_zh ? `中 ${part.span_zh}` : "",
  ].filter(Boolean).join(" · ");
  return spans ? `${spans} · ${part.summary_zh || part.summary_en || "待概括"}` : "尚未选择段落";
}

function renderList() {
  const reviewed = state.annotations.filter((item) => ["reviewed", "adjudicated"].includes(item.status)).length;
  $("#annotationCount").textContent = state.annotations.length;
  $("#progressText").textContent = `${reviewed} / ${state.annotations.length} 条已复核`;
  $("#progressBar").style.width = `${state.annotations.length ? reviewed / state.annotations.length * 100 : 0}%`;
  $("#annotationList").innerHTML = state.annotations.length ? state.annotations.map((item, index) => `
    <button class="annotation-item ${item.annotation_id === state.activeId ? "active" : ""}" data-id="${escapeHtml(item.annotation_id)}">
      <span class="item-index">${String(index + 1).padStart(2, "0")}</span>
      <span class="item-main">
        <strong>${escapeHtml(item.f?.summary_zh || item.f?.summary_en || "未命名伏笔")}</strong>
        <small>${escapeHtml(item.f?.span || item.f?.span_en || item.f?.span_zh || "F?")} → ${escapeHtml(item.t?.span || item.t?.span_en || item.t?.span_zh || "T?")} → ${escapeHtml(item.p?.span || item.p?.span_en || item.p?.span_zh || "P?")}</small>
      </span>
      <i class="status-dot ${item.status}" title="${escapeHtml(state.taxonomy.status[item.status] || item.status)}"></i>
    </button>`).join("") : `<p class="rail-empty">尚无标注。新建空白三元组，或从下方参考候选导入。</p>`;
}

function renderSeeds() {
  $("#seedCount").textContent = state.seeds.length;
  $("#aiCount").textContent = state.seeds.length;
  $("#aiToggle").classList.toggle("active", state.aiVisible);
  $("#aiToggle").innerHTML = `<i></i>${state.aiVisible ? "隐藏" : "显示"} AI 结果 <b id="aiCount">${state.seeds.length}</b>`;
  $("#aiToggle").disabled = !state.seeds.length;
  $("#seedList").innerHTML = state.seeds.length ? state.seeds.map((seed, index) => `
    <article class="seed-card ${seed.seed_id === state.activeSeedId ? "active" : ""}">
      <span class="seed-no">候选 ${String(index + 1).padStart(2, "0")}</span>
      <strong>${escapeHtml(seed.f.summary_zh || seed.f.summary_en || seed.seed_id)}</strong>
      <small>${escapeHtml(seed.f.span || "F?")} → ${escapeHtml(seed.t.span || "T?")} → ${escapeHtml(seed.p.span || "P?")}</small>
      <div class="seed-actions">
        <button data-preview="${escapeHtml(seed.seed_id)}">${seed.seed_id === state.activeSeedId ? "显示全部" : "正文定位"}</button>
        <button data-seed="${escapeHtml(seed.seed_id)}">导入并校正</button>
      </div>
    </article>`).join("") : `<p class="rail-empty">该篇暂无 CFPG 候选。</p>`;
}

function renderEditor() {
  const item = getActive();
  $("#emptyEditor").classList.toggle("hidden", Boolean(item));
  $("#editorForm").classList.toggle("hidden", !item);
  if (!item) return;
  $("#annotationId").value = item.annotation_id;
  $$("[data-field]", $("#editorForm")).forEach((field) => {
    field.value = getPath(item, field.dataset.field) ?? "";
  });
  ["f", "t", "p"].forEach((role) => {
    const button = $(`[data-jump="${role}"]`);
    button.textContent = spanLabel(item[role]);
    button.classList.toggle("empty", !item[role]?.span_en && !item[role]?.span_zh && !item[role]?.span);
  });
}

function renderHeader() {
  const story = state.story;
  $("#storySelect").value = story.story_id;
  $("#storyTitle").textContent = `${story.title_zh} · ${story.title_en}`;
  const languages = story.has_en && story.has_zh ? "中英双语" : story.has_zh ? "中文原文" : story.source_language.toUpperCase();
  $("#storyMeta").textContent = `${story.author}  ·  ${languages}`;
  $("#storyKicker").textContent = story.story_id.replaceAll("_", " ").toUpperCase();
}

function renderAll() {
  renderHeader();
  languageAvailability();
  renderList();
  renderSeeds();
  renderEditor();
  renderText();
}

function bestLanguage() {
  if (state.texts.en && state.texts.zh) return "parallel";
  if (state.texts.zh) return "zh";
  return "en";
}

async function loadStory(storyId, force = false) {
  if (state.dirty && !force && !window.confirm("当前小说有未保存更改，仍要切换吗？")) {
    $("#storySelect").value = state.story.story_id;
    return;
  }
  const [storyData, annotationData, seedData] = await Promise.all([
    api(`/api/story/${storyId}`),
    api(`/api/annotations/${storyId}`),
    api(`/api/seeds/${storyId}`),
  ]);
  state.story = storyData.story;
  state.texts = storyData.texts;
  state.annotations = annotationData.annotations || [];
  state.seeds = seedData.seeds || [];
  state.activeId = state.annotations[0]?.annotation_id || null;
  state.activeSeedId = null;
  state.aiVisible = false;
  state.language = bestLanguage();
  state.selection = null;
  $("#selectionLabel").textContent = "在正文中拖选任意文字";
  setDirty(false);
  renderAll();
}

async function save() {
  if (!state.story) return;
  $("#saveButton").disabled = true;
  $("#saveState").textContent = "正在保存…";
  try {
    const result = await api(`/api/annotations/${state.story.story_id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        schema_version: "ftp_manual_annotation_v1",
        story_id: state.story.story_id,
        annotations: state.annotations,
      }),
    });
    state.annotations = result.annotations;
    setDirty(false);
    renderAll();
    showToast(`已保存 ${state.annotations.length} 条标注`, "success");
  } catch (error) {
    setDirty(true);
    showToast(error.message, "error");
  } finally {
    $("#saveButton").disabled = false;
  }
}

function bindEvents() {
  $("#storySelect").addEventListener("change", (event) => loadStory(event.target.value));
  $$(".language-switch button").forEach((button) => button.addEventListener("click", () => {
    state.language = button.dataset.lang;
    languageAvailability();
    renderText();
  }));
  $("#textPane").addEventListener("mouseup", () => {
    window.setTimeout(captureBrowserSelection, 0);
  });
  $("#textPane").addEventListener("click", (event) => {
    const paragraphButton = event.target.closest(".paragraph-id");
    if (paragraphButton) selectWholeParagraph(paragraphButton.closest(".paragraph").dataset.id);
  });
  $$("[data-assign]").forEach((button) => button.addEventListener("click", () => assignSelection(button.dataset.assign)));
  $("#newButton").addEventListener("click", () => newAnnotation());
  $$('[data-action="new"]').forEach((button) => button.addEventListener("click", () => newAnnotation()));
  $("#deleteButton").addEventListener("click", deleteActive);
  $("#saveButton").addEventListener("click", save);
  $("#annotationList").addEventListener("click", (event) => {
    const button = event.target.closest("[data-id]");
    if (button) {
      state.activeId = button.dataset.id;
      state.selection = null;
      renderAll();
    }
  });
  $("#seedToggle").addEventListener("click", () => $("#seedList").classList.toggle("hidden"));
  $("#aiToggle").addEventListener("click", () => {
    state.aiVisible = !state.aiVisible;
    state.activeSeedId = null;
    $("#seedList").classList.toggle("hidden", !state.aiVisible);
    renderSeeds();
    renderText();
  });
  $("#seedList").addEventListener("click", (event) => {
    const button = event.target.closest("[data-seed]");
    if (button) newAnnotation(state.seeds.find((seed) => seed.seed_id === button.dataset.seed));
    const preview = event.target.closest("[data-preview]");
    if (preview) {
      state.aiVisible = true;
      state.activeSeedId = state.activeSeedId === preview.dataset.preview ? null : preview.dataset.preview;
      renderSeeds();
      renderText();
      const seed = state.seeds.find((item) => item.seed_id === preview.dataset.preview);
      const firstParagraph = seed?.f?.span?.split("-")[0];
      document.querySelector(`.paragraph[data-id="${firstParagraph}"]`)?.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  });
  $("#editorForm").addEventListener("input", (event) => {
    const item = getActive();
    if (!item) return;
    if (event.target === $("#annotationId")) {
      if (!event.target.value.trim()) return;
      item.annotation_id = event.target.value.trim();
      state.activeId = item.annotation_id;
    } else if (event.target.dataset.field) {
      setPath(item, event.target.dataset.field, event.target.value);
    }
    setDirty();
    renderList();
  });
  $("#editorForm").addEventListener("change", (event) => {
    if (event.target.dataset.field) renderList();
  });
  $$("[data-jump]").forEach((button) => button.addEventListener("click", () => {
    const part = getActive()?.[button.dataset.jump];
    const desiredLanguage = state.language === "parallel" ? "en" : state.language;
    const span = spanFor(part, desiredLanguage) || part?.span;
    const id = span?.split("-")[0];
    document.querySelector(`.paragraph[data-id="${id}"]`)?.scrollIntoView({ behavior: "smooth", block: "center" });
  }));
  document.addEventListener("keydown", (event) => {
    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "s") {
      event.preventDefault();
      save();
    }
    if (!["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement.tagName) && ["f", "t", "p"].includes(event.key.toLowerCase())) {
      assignSelection(event.key.toLowerCase());
    }
  });
  window.addEventListener("beforeunload", (event) => {
    if (state.dirty) {
      event.preventDefault();
      event.returnValue = "";
    }
  });
}

async function init() {
  try {
    const [storiesData, taxonomy] = await Promise.all([api("/api/stories"), api("/api/taxonomy")]);
    state.stories = storiesData.stories;
    state.taxonomy = taxonomy;
    initTaxonomy();
    renderStoryOptions();
    bindEvents();
    const requested = new URLSearchParams(location.search).get("story");
    const storyId = state.stories.some((item) => item.story_id === requested)
      ? requested : state.stories[0]?.story_id;
    if (storyId) await loadStory(storyId, true);
  } catch (error) {
    document.body.innerHTML = `<main class="fatal"><h1>无法启动标注台</h1><p>${escapeHtml(error.message)}</p></main>`;
  }
}

init();
