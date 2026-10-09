from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _json_for_script(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def render_html(
    snapshots: list[dict[str, Any]],
    mapping: dict[str, Any],
    output_path: Path,
) -> Path:
    html = HTML_TEMPLATE.replace("__SNAPSHOTS__", _json_for_script(snapshots))
    html = html.replace("__MAPPING_METHOD__", _json_for_script(mapping["method"]))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    return output_path


HTML_TEMPLATE = r'''<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AGORA Blue Sky — CTQ Temporal Argument Graph</title>
<style>
:root {
  --ink:#18212f; --muted:#627083; --paper:#f5f7fb; --panel:#ffffff;
  --line:#dbe2ea; --blue:#2264d1; --cyan:#00a8c7; --green:#23845b;
  --red:#c94646; --amber:#b97812; --support:#279567; --attack:#d14e4e;
}
* { box-sizing:border-box; }
body { margin:0; color:var(--ink); background:var(--paper); font:14px/1.45 Inter,Segoe UI,Arial,sans-serif; }
header { background:linear-gradient(120deg,#12213a,#173e78); color:white; padding:22px 28px 18px; }
header h1 { margin:0 0 5px; font-size:24px; letter-spacing:.1px; }
header p { margin:0; color:#d7e5ff; max-width:980px; }
.timeline-shell { background:#fff; border-bottom:1px solid var(--line); padding:14px 24px 12px; position:sticky; top:0; z-index:20; }
.timeline-top { display:flex; gap:10px; align-items:center; }
button,.mode-button { border:1px solid #bdc9d7; background:#fff; color:var(--ink); border-radius:8px; padding:7px 12px; cursor:pointer; font-weight:600; }
button:hover { border-color:var(--blue); color:var(--blue); }
button.active { color:#fff; background:var(--blue); border-color:var(--blue); }
.slider-wrap { flex:1; display:flex; align-items:center; gap:12px; min-width:260px; }
#timeSlider { --progress:0%; appearance:none; flex:1; height:7px; border-radius:999px; cursor:pointer; outline:none; background:linear-gradient(90deg,var(--blue) 0 var(--progress),#ced7e2 var(--progress) 100%); }
#timeSlider::-webkit-slider-thumb { appearance:none; width:23px; height:23px; border-radius:50%; background:#fff; border:6px solid var(--blue); box-shadow:0 2px 8px #17304f55; cursor:grab; }
#timeSlider:active::-webkit-slider-thumb { cursor:grabbing; transform:scale(1.08); }
#timeSlider::-moz-range-thumb { width:13px; height:13px; border-radius:50%; background:#fff; border:6px solid var(--blue); box-shadow:0 2px 8px #17304f55; cursor:grab; }
#timeSlider:focus-visible { box-shadow:0 0 0 4px #2264d122; }
#timeValue { min-width:38px; text-align:center; padding:4px 8px; border-radius:999px; color:#fff; background:var(--blue); font-weight:800; }
.ticks { display:grid; grid-template-columns:repeat(6,1fr); margin:7px 102px 0 208px; color:var(--muted); font-weight:700; }
.ticks span { position:relative; text-align:center; cursor:pointer; padding-top:7px; user-select:none; }
.ticks span::before { content:''; position:absolute; top:-7px; left:50%; width:8px; height:8px; border-radius:50%; background:#c4ceda; transform:translateX(-50%); }
.ticks span:hover,.ticks span.active { color:var(--blue); }
.ticks span.active::before { background:var(--blue); box-shadow:0 0 0 4px #2264d11f; }
.event-card { display:grid; grid-template-columns:180px 1fr 1fr; gap:14px; margin-top:12px; }
.event-card > div { background:#f4f7fb; border:1px solid #e1e7ef; border-radius:9px; padding:9px 11px; min-height:66px; }
.event-card .event-main { grid-row:span 1; }
.eyebrow { font-size:11px; text-transform:uppercase; letter-spacing:.6px; color:var(--muted); font-weight:800; }
#timestampTitle { font-size:17px; font-weight:800; margin:3px 0; }
.layout { display:grid; grid-template-columns:minmax(0,1fr) 350px; gap:14px; padding:14px; }
.canvas-panel,.detail-panel,.controls { background:var(--panel); border:1px solid var(--line); border-radius:12px; box-shadow:0 3px 16px #17304f0d; }
.toolbar { display:flex; flex-wrap:wrap; gap:8px 14px; align-items:center; padding:11px 13px; border-bottom:1px solid var(--line); }
.mode-switch { display:flex; gap:4px; padding-right:12px; border-right:1px solid var(--line); }
.filter-group { display:flex; align-items:center; gap:8px; }
.filter-group label { display:flex; align-items:center; gap:4px; color:#405065; }
select { padding:6px 8px; border:1px solid #bdc9d7; border-radius:7px; background:#fff; }
.graph-wrap { position:relative; height:650px; overflow:hidden; border-radius:0 0 12px 12px; background:radial-gradient(circle at 50% 45%,#fff 0,#f8faff 70%,#f1f5fb 100%); }
#graph { width:100%; height:100%; touch-action:none; cursor:grab; }
#graph.panning { cursor:grabbing; }
.node { cursor:grab; }
.node:active { cursor:grabbing; }
.node rect { stroke-width:2.5; filter:drop-shadow(0 3px 4px #1b365522); }
.node.new rect { stroke:var(--cyan)!important; stroke-width:5; filter:drop-shadow(0 0 7px #00a8c766); }
.node text { pointer-events:none; font-weight:750; fill:#172335; text-anchor:middle; }
.node .sub { font-size:10px; font-weight:600; fill:#526176; }
.edge-visible { fill:none; stroke-width:2.2; opacity:.82; stroke-linecap:round; }
.edge-hit { fill:none; stroke:transparent; stroke-width:14; cursor:pointer; }
.edge-new { stroke-width:4; filter:drop-shadow(0 0 3px #00a8c7); }
.hover-tooltip { position:absolute; display:none; z-index:15; width:min(430px,calc(100% - 24px)); max-height:430px; overflow:hidden; pointer-events:none; color:#172335; background:#fffffff7; border:1px solid #b8c6d6; border-radius:10px; padding:11px 13px; box-shadow:0 12px 35px #17304f30; backdrop-filter:blur(5px); }
.hover-tooltip.visible { display:block; }
.hover-tooltip strong { display:block; margin-bottom:4px; font-size:14px; color:#113a70; }
.hover-tooltip .tooltip-meta { margin-bottom:7px; color:#5c6b7f; font-size:12px; }
.hover-tooltip .tooltip-row { margin-top:5px; }
.hover-tooltip .tooltip-sources { margin-top:7px; padding-top:6px; border-top:1px solid #e1e7ef; font-size:12px; color:#4b5b70; }
.graph-summary { position:absolute; left:12px; bottom:10px; background:#ffffffec; border:1px solid var(--line); border-radius:8px; padding:6px 9px; color:var(--muted); }
.detail-panel { padding:16px; min-height:650px; overflow:auto; max-height:756px; }
.detail-panel h2 { margin:0 0 5px; font-size:19px; }
.detail-panel h3 { margin:18px 0 6px; font-size:14px; }
.detail-panel p { margin:6px 0; }
.detail-panel ul { padding-left:19px; }
.detail-panel a { color:var(--blue); overflow-wrap:anywhere; }
.detail-placeholder { color:var(--muted); padding-top:35px; text-align:center; }
.pill { display:inline-block; padding:2px 7px; border-radius:999px; font-size:11px; font-weight:800; margin:2px 3px 2px 0; background:#edf1f6; }
.pill.accepted { color:#176b49; background:#dff5ea; }
.pill.rejected { color:#a52f2f; background:#fde5e5; }
.pill.undecided { color:#8a5907; background:#fff0cd; }
.pill.support { color:#176b49; background:#dff5ea; }
.pill.attack { color:#a52f2f; background:#fde5e5; }
.legend { display:flex; flex-wrap:wrap; gap:10px 16px; padding:10px 14px; border-top:1px solid var(--line); background:#fff; }
.legend-item { display:flex; align-items:center; gap:6px; color:#526176; }
.dot { width:12px; height:12px; border-radius:3px; }
.line-key { width:26px; height:0; border-top:3px solid; position:relative; }
.line-key:after { content:'›'; position:absolute; right:-2px; top:-12px; font-size:18px; font-weight:900; }
.method-note { margin:0 14px 14px; padding:11px 13px; color:#46566b; background:#eef4ff; border-left:4px solid var(--blue); border-radius:6px; }
@media (max-width:980px) {
  .layout { grid-template-columns:1fr; }
  .detail-panel { min-height:240px; max-height:none; }
  .event-card { grid-template-columns:1fr; }
  .ticks { margin-left:0; margin-right:0; }
}
</style>
</head>
<body>
<header>
  <h1>AGORA Blue Sky — Đồ thị lập luận CTQ theo thời gian</h1>
  <p>Lập luận tường minh → đồ thị thời gian → cụm quan điểm → agent quan điểm có thể truy nguyên. t1…t6 là các trạng thái thông tin thực, không phải vòng tương tác nhân tạo.</p>
</header>

<section class="timeline-shell">
  <div class="timeline-top">
    <button id="prevButton" title="Mốc trước">← Trước</button>
    <button id="playButton" title="Phát hoặc tạm dừng">▶ Phát</button>
    <div class="slider-wrap">
      <input id="timeSlider" type="range" min="0" max="5" step="1" value="0" aria-label="Kéo để chọn một trong sáu mốc thời gian">
      <output id="timeValue" for="timeSlider" aria-live="polite">t1</output>
    </div>
    <button id="nextButton" title="Mốc sau">Sau →</button>
  </div>
  <div class="ticks" id="ticks"></div>
  <div class="event-card">
    <div class="event-main"><div class="eyebrow">Trạng thái đang xem</div><div id="timestampTitle"></div><div id="timestampEvent"></div></div>
    <div><div class="eyebrow">Thông tin công khai</div><div id="publicInfo"></div></div>
    <div><div class="eyebrow">Thông tin chính thức</div><div id="officialInfo"></div></div>
  </div>
</section>

<main class="layout">
  <section class="canvas-panel">
    <div class="toolbar">
      <div class="mode-switch">
        <button class="active" id="argumentMode">Argument Graph</button>
        <button id="viewpointMode">Viewpoint Agent</button>
      </div>
      <div class="filter-group" id="argumentFilters">
        <label>Loại <select id="argType"><option value="all">Tất cả</option><option value="A_K">A_K</option><option value="A_D">A_D</option></select></label>
        <label><input id="showRejected" type="checkbox" checked> rejected</label>
        <label><input id="showUndecided" type="checkbox" checked> undecided</label>
        <label><input id="onlyNew" type="checkbox"> chỉ mới xuất hiện</label>
      </div>
      <div class="filter-group">
        <label><input id="showSupport" type="checkbox" checked> support</label>
        <label><input id="showAttack" type="checkbox" checked> attack</label>
        <button id="resetView">Đặt lại khung nhìn</button>
      </div>
    </div>
    <div class="graph-wrap" id="graphWrap">
      <svg id="graph" viewBox="0 0 1180 650" role="img" aria-label="Đồ thị lập luận CTQ tương tác">
        <defs>
          <marker id="arrowSupport" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#279567"/></marker>
          <marker id="arrowAttack" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#d14e4e"/></marker>
        </defs>
        <rect id="graphBg" width="1180" height="650" fill="transparent"/>
        <g id="viewport"><g id="edges"></g><g id="nodes"></g></g>
      </svg>
      <div class="graph-summary" id="graphSummary"></div>
      <div class="hover-tooltip" id="hoverTooltip" role="tooltip"></div>
    </div>
    <div class="legend">
      <span class="legend-item"><span class="dot" style="background:#dff5ea;border:2px solid #23845b"></span>accepted</span>
      <span class="legend-item"><span class="dot" style="background:#fde5e5;border:2px solid #c94646"></span>rejected</span>
      <span class="legend-item"><span class="dot" style="background:#fff0cd;border:2px solid #b97812"></span>undecided</span>
      <span class="legend-item"><span class="dot" style="background:white;border:3px solid #00a8c7"></span>mới tại mốc này</span>
      <span class="legend-item"><span class="line-key" style="border-color:#279567;color:#279567"></span>support</span>
      <span class="legend-item"><span class="line-key" style="border-color:#d14e4e;color:#d14e4e"></span>attack</span>
      <span class="legend-item"><span class="dot" style="background:#fff;border:2px solid #2264d1"></span>có official_document</span>
      <span class="legend-item"><span class="dot" style="background:#fff;border:2px solid #7656a8"></span>có authority_statement</span>
    </div>
    <p class="method-note" id="methodNote"></p>
  </section>
  <aside class="detail-panel" id="detailPanel"><div class="detail-placeholder">Chọn một node hoặc cạnh để xem provenance và chi tiết.</div></aside>
</main>

<script>
const SNAPSHOTS = __SNAPSHOTS__;
const MAPPING_METHOD = __MAPPING_METHOD__;
const NS = 'http://www.w3.org/2000/svg';
const initialParams = new URLSearchParams(location.search);
const initialTime = Math.max(0,Math.min(5,Number(initialParams.get('t')||0)));
const initialMode = initialParams.get('mode')==='viewpoints'?'viewpoints':'arguments';
const state = {
  time:initialTime, mode:initialMode, argType:'all', showSupport:true, showAttack:true,
  showRejected:true, showUndecided:true, onlyNew:false, playing:null,
  transform:{x:0,y:0,k:1}, positions:{arguments:{},viewpoints:{}}
};
const $ = id => document.getElementById(id);
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const truncate = (value,n=70) => value.length>n ? value.slice(0,n-1)+'…' : value;

function statusStyle(status) {
  return {
    accepted:{fill:'#dff5ea',stroke:'#23845b'},
    rejected:{fill:'#fde5e5',stroke:'#c94646'},
    undecided:{fill:'#fff0cd',stroke:'#b97812'}
  }[status] || {fill:'#edf1f6',stroke:'#7b8796'};
}

function argumentPasses(arg) {
  if (state.argType !== 'all' && arg.arg_type !== state.argType) return false;
  if (!state.showRejected && arg.status === 'rejected') return false;
  if (!state.showUndecided && arg.status === 'undecided') return false;
  if (state.onlyNew && !arg.newly_introduced) return false;
  return true;
}

function filteredData() {
  const snap = SNAPSHOTS[state.time];
  const args = snap.arguments.filter(argumentPasses);
  const visibleIds = new Set(args.map(a=>a.id));
  const relations = snap.relations.filter(r =>
    visibleIds.has(r.source) && visibleIds.has(r.target) &&
    ((r.relation_type==='support' && state.showSupport) || (r.relation_type==='attack' && state.showAttack))
  );
  if (state.mode === 'arguments') return {nodes:args,edges:relations,arguments:args};

  const nodes = snap.viewpoints.map(v => {
    const active = v.arguments.filter(argumentPasses);
    const counts = {accepted:0,rejected:0,undecided:0};
    const composition = {};
    active.forEach(a => {
      counts[a.status]++;
      a.sources.forEach(s => composition[s.source_type]=(composition[s.source_type]||0)+1);
    });
    return {...v,arguments:active,active_argument_ids:active.map(a=>a.id),status_counts:counts,source_composition:composition};
  }).filter(v=>v.arguments.length);
  const viewpointIds = new Set(nodes.map(v=>v.id));
  const edges = snap.viewpoint_relations.map(edge => {
    const underlying = edge.argument_relations.filter(r => visibleIds.has(r.source_arg) && visibleIds.has(r.target_arg));
    return {...edge,argument_relations:underlying,relation_ids:underlying.map(r=>r.relation_id)};
  }).filter(edge => edge.argument_relations.length && viewpointIds.has(edge.source) && viewpointIds.has(edge.target) &&
    ((edge.relation_type==='support' && state.showSupport) || (edge.relation_type==='attack' && state.showAttack)));
  return {nodes,edges,arguments:args};
}

function initialPosition(id, mode) {
  if (mode === 'viewpoints') {
    const n = Number(id.replace(/\D/g,'')) || 1;
    const angle = -Math.PI/2 + (n-1)*2*Math.PI/7;
    return {x:590+270*Math.cos(angle),y:325+245*Math.sin(angle)};
  }
  const n = Number(id.replace(/\D/g,'')) || 1;
  const inner = n <= 9;
  const count = inner ? 9 : 18;
  const slot = inner ? n-1 : n-10;
  const angle = -Math.PI/2 + slot*2*Math.PI/count;
  const rx = inner ? 245 : 485, ry = inner ? 155 : 275;
  return {x:590+rx*Math.cos(angle),y:325+ry*Math.sin(angle)};
}

function positionFor(id) {
  const cache = state.positions[state.mode];
  if (!cache[id]) cache[id] = initialPosition(id,state.mode);
  return cache[id];
}

function edgePath(a,b) {
  const dx=b.x-a.x, dy=b.y-a.y, d=Math.max(1,Math.hypot(dx,dy));
  const ux=dx/d, uy=dy/d, shorten=state.mode==='arguments'?78:92;
  const x1=a.x+ux*shorten, y1=a.y+uy*shorten, x2=b.x-ux*shorten, y2=b.y-uy*shorten;
  return {d:`M ${x1} ${y1} L ${x2} ${y2}`};
}

function moveTooltip(event) {
  const tooltip=$('hoverTooltip'), wrap=$('graphWrap'), box=wrap.getBoundingClientRect();
  let left=event.clientX-box.left+16, top=event.clientY-box.top+16;
  const width=tooltip.offsetWidth||400, height=tooltip.offsetHeight||180;
  if(left+width>box.width-8) left=event.clientX-box.left-width-16;
  if(top+height>box.height-8) top=event.clientY-box.top-height-16;
  tooltip.style.left=`${Math.max(8,left)}px`; tooltip.style.top=`${Math.max(8,top)}px`;
}
function showTooltip(html,event){const tooltip=$('hoverTooltip');tooltip.innerHTML=html;tooltip.classList.add('visible');moveTooltip(event);}
function hideTooltip(){const tooltip=$('hoverTooltip');tooltip.classList.remove('visible');}
function nodeTooltip(node) {
  if(state.mode==='viewpoints') {
    const counts=node.status_counts, composition=Object.entries(node.source_composition).map(([k,v])=>`${esc(k)}: ${v}`).join(' · ');
    return `<strong>${esc(node.id)} — ${esc(node.name)}</strong><div class="tooltip-meta">Viewpoint agent · ${node.arguments.length}/${node.all_argument_ids.length} argument đang active</div>
      <div class="tooltip-row">${esc(node.description)}</div>
      <div class="tooltip-row"><b>Trạng thái:</b> accepted ${counts.accepted} · rejected ${counts.rejected} · undecided ${counts.undecided}</div>
      <div class="tooltip-row"><b>Argument active:</b> ${node.active_argument_ids.map(esc).join(', ')}</div>
      <div class="tooltip-sources"><b>Nguồn:</b> ${composition||'Không có'}</div>`;
  }
  return `<strong>${esc(node.id)} — ${esc(node.arg_type)}</strong><div class="tooltip-meta">introduced_at: ${esc(node.introduced_at)}${node.active_until?' · active_until: '+esc(node.active_until):''} · status: ${esc(node.status||'null (lịch sử)')}</div>
    <div class="tooltip-row"><b>Premise:</b> ${esc(node.premise)}</div>
    <div class="tooltip-row"><b>Rule:</b> ${node.rule?esc(node.rule):'<i>null — không có rule được nguồn hỗ trợ trực tiếp</i>'}</div>
    <div class="tooltip-row"><b>Conclusion:</b> ${esc(node.conclusion)}</div>
    <div class="tooltip-sources"><b>Nguồn:</b> ${node.source_ids.map(esc).join(', ')} · <b>Vai trò:</b> ${esc(node.temporal_role)}</div>`;
}
function edgeTooltip(edge) {
  if(state.mode==='viewpoints') return `<strong>${esc(edge.source)} → ${esc(edge.target)}</strong><div class="tooltip-meta">${esc(edge.relation_type)} · ${edge.relation_ids.length} quan hệ argument nền</div>
    <div class="tooltip-row"><b>Relation IDs:</b> ${edge.relation_ids.map(esc).join(', ')}</div>
    <div class="tooltip-row"><b>Liên kết nền:</b> ${edge.argument_relations.map(r=>`${esc(r.source_arg)} → ${esc(r.target_arg)}`).join('; ')}</div>
    <div class="tooltip-sources"><b>Evidence:</b> ${edge.evidence_sources.map(esc).join(', ')}</div>`;
  return `<strong>${esc(edge.id)} — ${esc(edge.relation_type)}</strong><div class="tooltip-meta">${esc(edge.source)} → ${esc(edge.target)} · introduced_at: ${esc(edge.introduced_at)} · confidence: ${esc(edge.confidence)}</div>
    <div class="tooltip-row"><b>Conflict type:</b> ${esc(edge.conflict_type||'null')}</div>
    <div class="tooltip-row">${esc(edge.notes)}</div>
    <div class="tooltip-sources"><b>Evidence:</b> ${edge.evidence_sources.map(esc).join(', ')}</div>`;
}

function render() {
  updateTimeline();
  const data=filteredData(), edgesLayer=$('edges'), nodesLayer=$('nodes');
  edgesLayer.replaceChildren(); nodesLayer.replaceChildren();
  const nodeById=new Map(data.nodes.map(n=>[n.id,n]));

  data.edges.forEach(edge => {
    const p=edgePath(positionFor(edge.source),positionFor(edge.target));
    const group=document.createElementNS(NS,'g');
    const visible=document.createElementNS(NS,'path');
    visible.setAttribute('d',p.d);
    visible.setAttribute('class','edge-visible'+(edge.newly_introduced?' edge-new':''));
    visible.setAttribute('stroke',edge.relation_type==='support'?'#279567':'#d14e4e');
    visible.setAttribute('marker-end',`url(#arrow${edge.relation_type==='support'?'Support':'Attack'})`);
    const hit=document.createElementNS(NS,'path');
    hit.setAttribute('d',p.d); hit.setAttribute('class','edge-hit');
    const title=document.createElementNS(NS,'title');
    title.textContent=state.mode==='arguments'
      ? `${edge.id}: ${edge.source} → ${edge.target} (${edge.relation_type})`
      : `${edge.source} → ${edge.target}: ${edge.relation_type} (${edge.relation_ids.length} quan hệ)`;
    hit.appendChild(title); hit.addEventListener('click',e=>{e.stopPropagation();showEdgeDetail(edge);});
    hit.addEventListener('mouseenter',e=>showTooltip(edgeTooltip(edge),e));
    hit.addEventListener('mousemove',moveTooltip); hit.addEventListener('mouseleave',hideTooltip);
    group.append(visible,hit); edgesLayer.appendChild(group);
  });

  data.nodes.forEach(node => {
    const p=positionFor(node.id), group=document.createElementNS(NS,'g');
    group.setAttribute('class','node'+((node.newly_introduced||node.newly_active_arguments)?' new':''));
    group.setAttribute('transform',`translate(${p.x} ${p.y})`); group.dataset.id=node.id;
    const rect=document.createElementNS(NS,'rect');
    const w=state.mode==='arguments'?142:176, h=state.mode==='arguments'?62:74;
    rect.setAttribute('x',-w/2); rect.setAttribute('y',-h/2); rect.setAttribute('width',w); rect.setAttribute('height',h); rect.setAttribute('rx',12);
    if (state.mode==='arguments') {
      const style=statusStyle(node.status); rect.setAttribute('fill',style.fill);
      let stroke=style.stroke;
      if (node.sources.some(s=>s.source_type==='official_document')) stroke='#2264d1';
      else if (node.sources.some(s=>s.source_type==='authority_statement')) stroke='#7656a8';
      rect.setAttribute('stroke',stroke);
    } else { rect.setAttribute('fill','#e8f0ff'); rect.setAttribute('stroke','#315f9e'); }
    const title=document.createElementNS(NS,'title');
    title.textContent=state.mode==='arguments' ? `${node.id} — ${node.conclusion}` : `${node.id} — ${node.name}`;
    const line1=document.createElementNS(NS,'text'); line1.setAttribute('y',-9); line1.setAttribute('font-size','12'); line1.textContent=node.id;
    const line2=document.createElementNS(NS,'text'); line2.setAttribute('y',8); line2.setAttribute('font-size','10');
    line2.textContent=state.mode==='arguments'?`${node.arg_type} · ${node.status||'status null'}`:truncate(node.name,28);
    const line3=document.createElementNS(NS,'text'); line3.setAttribute('y',23); line3.setAttribute('class','sub');
    line3.textContent=state.mode==='arguments'?(node.newly_introduced?'Mới tại mốc này':node.temporal_role):`${node.arguments.length} lập luận · A${node.status_counts.accepted}/R${node.status_counts.rejected}/U${node.status_counts.undecided}`;
    group.append(rect,title,line1,line2,line3);
    group.addEventListener('click',e=>{e.stopPropagation();showNodeDetail(node);});
    group.addEventListener('mouseenter',e=>showTooltip(nodeTooltip(node),e));
    group.addEventListener('mousemove',moveTooltip); group.addEventListener('mouseleave',hideTooltip);
    group.addEventListener('pointerdown',e=>{hideTooltip();startNodeDrag(e);});
    nodesLayer.appendChild(group);
  });
  $('graphSummary').textContent=`${data.nodes.length} node · ${data.edges.length} cạnh · ${data.arguments.length} lập luận đang lọc`;
  applyTransform();
}

function updateTimeline() {
  const t=SNAPSHOTS[state.time].timestamp;
  $('timeSlider').value=state.time;
  $('timeSlider').style.setProperty('--progress',`${state.time/5*100}%`);
  $('timeValue').value=t.timestamp_id; $('timeValue').textContent=t.timestamp_id;
  $('timestampTitle').textContent=`${t.timestamp_id} · ${t.date_start}${t.date_end!==t.date_start?' → '+t.date_end:''} · ${t.label}`;
  $('timestampEvent').textContent=t.event;
  $('publicInfo').textContent=t.public_information_available;
  $('officialInfo').textContent=t.official_information_available;
  [...$('ticks').children].forEach((el,i)=>el.classList.toggle('active',i===state.time));
}

function sourceList(argument) {
  if (!argument.sources.length) return '<p>Không có source ID.</p>';
  return '<ul>'+argument.sources.map(s=>`<li><a href="${esc(s.url)}" target="_blank" rel="noreferrer">${esc(s.source_id)}</a> — ${esc(s.title||'Chưa xác minh tiêu đề')}<br><small>${esc(s.source_type)} · ${esc(s.publisher)} · ${esc(s.verification_status)}</small></li>`).join('')+'</ul>';
}

function argumentBlock(a) {
  return `<div><h3>${esc(a.id)} <span class="pill ${esc(a.status)}">${esc(a.status)}</span></h3>
    <p><b>Kết luận:</b> ${esc(a.conclusion)}</p><p><b>Nguồn:</b> ${a.source_ids.map(esc).join(', ')}</p></div>`;
}

function showNodeDetail(node) {
  if (state.mode==='viewpoints') {
    const composition=Object.entries(node.source_composition).map(([k,v])=>`<span class="pill">${esc(k)}: ${v}</span>`).join(' ');
    $('detailPanel').innerHTML=`<div class="eyebrow">Viewpoint agent</div><h2>${esc(node.id)} — ${esc(node.name)}</h2>
      <p>${esc(node.description)}</p>
      <p><span class="pill accepted">accepted ${node.status_counts.accepted}</span><span class="pill rejected">rejected ${node.status_counts.rejected}</span><span class="pill undecided">undecided ${node.status_counts.undecided}</span></p>
      <h3>Lập luận đang active (${node.arguments.length}/${node.all_argument_ids.length})</h3>${node.arguments.map(argumentBlock).join('')||'<p>Không có.</p>'}
      <h3>Thành phần nguồn</h3><p>${composition||'Không có.'}</p>
      <h3>Quan hệ incident</h3><p>support: ${node.support_relations} · attack: ${node.attack_relations}</p>
      <h3>Quy tắc dựng agent</h3><p>${esc(MAPPING_METHOD)}</p>`;
    return;
  }
  const statusLabel=node.status||'null (lịch sử)';
  $('detailPanel').innerHTML=`<div class="eyebrow">Argument node</div><h2>${esc(node.id)} <span class="pill ${esc(node.status||'')}">${esc(statusLabel)}</span></h2>
    <p><span class="pill">${esc(node.arg_type)}</span><span class="pill">${esc(node.temporal_role)}</span>${node.newly_introduced?'<span class="pill">mới tại mốc này</span>':''}</p>
    <h3>Premise</h3><p>${esc(node.premise)}</p>
    <h3>Rule</h3><p>${node.rule?esc(node.rule):'<i>null — không có quy tắc được nguồn hỗ trợ trực tiếp</i>'}</p>
    <h3>Conclusion</h3><p>${esc(node.conclusion)}</p>
    <h3>Thời gian và trạng thái</h3><p>introduced_at: <b>${esc(node.introduced_at)}</b>${node.active_until?' · active_until: <b>'+esc(node.active_until)+'</b>':''}</p>
    <p>${esc(node.status_reason)}</p><p><b>Grounded by:</b> ${node.grounded_by.map(esc).join(', ')}</p>
    <h3>Nguồn</h3>${sourceList(node)}`;
}

function showEdgeDetail(edge) {
  if (state.mode==='viewpoints') {
    $('detailPanel').innerHTML=`<div class="eyebrow">Viewpoint relation tổng hợp</div><h2>${esc(edge.source)} → ${esc(edge.target)}</h2>
      <p><span class="pill ${esc(edge.relation_type)}">${esc(edge.relation_type)}</span> · ${edge.relation_ids.length} quan hệ nền</p>
      <h3>Quan hệ argument có thể truy nguyên</h3><ul>${edge.argument_relations.map(r=>`<li>${esc(r.relation_id)}: ${esc(r.source_arg)} → ${esc(r.target_arg)}${r.conflict_type?' · '+esc(r.conflict_type):''}</li>`).join('')}</ul>
      <h3>Evidence sources</h3><p>${edge.evidence_sources.map(esc).join(', ')}</p>`;
    return;
  }
  $('detailPanel').innerHTML=`<div class="eyebrow">Argument relation</div><h2>${esc(edge.id)}</h2>
    <p><span class="pill ${esc(edge.relation_type)}">${esc(edge.relation_type)}</span>${edge.conflict_type?' <span class="pill">'+esc(edge.conflict_type)+'</span>':''}</p>
    <p><b>${esc(edge.source)} → ${esc(edge.target)}</b></p><p>${esc(edge.notes)}</p>
    <p><b>introduced_at:</b> ${esc(edge.introduced_at)} · <b>confidence:</b> ${esc(edge.confidence)}</p>
    <p><b>Hiệu lực:</b> ${esc(edge.valid_from||'null')} → ${esc(edge.valid_to||'không giới hạn')}</p>
    <p><b>Evidence sources:</b> ${edge.evidence_sources.map(esc).join(', ')}</p>`;
}

function setMode(mode) {
  state.mode=mode; $('argumentMode').classList.toggle('active',mode==='arguments'); $('viewpointMode').classList.toggle('active',mode==='viewpoints');
  $('methodNote').textContent=mode==='viewpoints' ? MAPPING_METHOD : 'Node và cạnh được dựng trực tiếp từ CSV canonical; không có status, source hoặc relation nào được suy đoán.';
  $('detailPanel').innerHTML='<div class="detail-placeholder">Chọn một node hoặc cạnh để xem provenance và chi tiết.</div>';
  render();
}

function applyTransform(){ $('viewport').setAttribute('transform',`translate(${state.transform.x} ${state.transform.y}) scale(${state.transform.k})`); }
function resetView(){ state.transform={x:0,y:0,k:1}; applyTransform(); }
function graphPoint(event) {
  const svg=$('graph'), pt=svg.createSVGPoint(); pt.x=event.clientX; pt.y=event.clientY;
  const p=pt.matrixTransform($('viewport').getScreenCTM().inverse()); return {x:p.x,y:p.y};
}
let dragging=null, panning=null;
function startNodeDrag(event){ event.stopPropagation(); const id=event.currentTarget.dataset.id; const p=positionFor(id), g=graphPoint(event); dragging={id,dx:p.x-g.x,dy:p.y-g.y,pointer:event.pointerId}; $('graph').setPointerCapture(event.pointerId); }
$('graph').addEventListener('pointerdown',event=>{ if(event.target.closest('.node'))return; panning={x:event.clientX,y:event.clientY,tx:state.transform.x,ty:state.transform.y,pointer:event.pointerId}; $('graph').setPointerCapture(event.pointerId); $('graph').classList.add('panning'); });
$('graph').addEventListener('pointermove',event=>{
  if(dragging){const p=graphPoint(event);state.positions[state.mode][dragging.id]={x:p.x+dragging.dx,y:p.y+dragging.dy};render();}
  else if(panning){const box=$('graph').getBoundingClientRect(),sx=1180/box.width,sy=650/box.height;state.transform.x=panning.tx+(event.clientX-panning.x)*sx;state.transform.y=panning.ty+(event.clientY-panning.y)*sy;applyTransform();}
});
$('graph').addEventListener('pointerup',()=>{dragging=null;panning=null;$('graph').classList.remove('panning');});
$('graph').addEventListener('wheel',event=>{event.preventDefault();state.transform.k=Math.max(.45,Math.min(2.4,state.transform.k*(event.deltaY<0?1.12:.89)));applyTransform();},{passive:false});
$('graph').addEventListener('click',event=>{if(event.target.id==='graph'||event.target.id==='graphBg')$('detailPanel').innerHTML='<div class="detail-placeholder">Chọn một node hoặc cạnh để xem provenance và chi tiết.</div>';});

function setTime(index){ state.time=Math.max(0,Math.min(5,index)); render(); }
function togglePlay(){
  if(state.playing){clearInterval(state.playing);state.playing=null;$('playButton').textContent='▶ Phát';return;}
  $('playButton').textContent='⏸ Dừng';state.playing=setInterval(()=>{if(state.time===5){togglePlay();return;}setTime(state.time+1);},1700);
}

SNAPSHOTS.forEach((snap,index)=>{const tick=document.createElement('span');tick.textContent=snap.timestamp.timestamp_id;tick.onclick=()=>setTime(index);$('ticks').appendChild(tick);});
$('timeSlider').addEventListener('input',e=>setTime(Number(e.target.value)));
$('prevButton').onclick=()=>setTime(state.time-1); $('nextButton').onclick=()=>setTime(state.time+1); $('playButton').onclick=togglePlay;
$('argumentMode').onclick=()=>setMode('arguments'); $('viewpointMode').onclick=()=>setMode('viewpoints'); $('resetView').onclick=resetView;
$('argType').onchange=e=>{state.argType=e.target.value;render();};
['showSupport','showAttack','showRejected','showUndecided','onlyNew'].forEach(id=>$(id).onchange=e=>{state[id]=e.target.checked;render();});
setMode(initialMode);
</script>
</body>
</html>
'''
