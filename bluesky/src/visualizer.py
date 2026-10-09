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
.transition-summary { margin-top:10px; padding:9px 11px; border:1px solid #d8e4f2; border-radius:9px; background:#f8fbff; }
.transition-summary .summary-row { display:flex; flex-wrap:wrap; gap:6px; margin-top:5px; }
.transition-summary .summary-detail { margin-top:6px; color:#526176; font-size:12px; }
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
.node.historical { opacity:.46; }
.node.new .new-halo { display:block; }
.new-halo { display:none; fill:none; stroke:var(--cyan); stroke-width:4; stroke-dasharray:7 4; filter:drop-shadow(0 0 5px #00a8c777); }
.node.contextual rect { stroke-dasharray:7 4; }
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
.pill.activity { color:#44556b; background:#e8edf4; }
.why-changed { margin-top:14px; padding:11px 12px; border-left:4px solid var(--cyan); border-radius:6px; background:#eefbfe; }
.why-changed h3 { margin-top:0; color:#12647a; }
.legend { display:flex; flex-wrap:wrap; gap:10px 16px; padding:10px 14px; border-top:1px solid var(--line); background:#fff; }
.legend-item { display:flex; align-items:center; gap:6px; color:#526176; }
.dot { width:12px; height:12px; border-radius:3px; }
.dot.historical { opacity:.42; }
.dot.contextual { border-style:dashed!important; }
.source-badge { width:12px; height:12px; border-radius:50%; border:2px solid white; box-shadow:0 0 0 1px #8491a2; }
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
  <div class="transition-summary" id="transitionSummary"></div>
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
          <marker id="arrowSupport" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" markerUnits="userSpaceOnUse" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#279567"/></marker>
          <marker id="arrowAttack" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" markerUnits="userSpaceOnUse" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#d14e4e"/></marker>
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
      <span class="legend-item"><span class="dot" style="background:white;border:3px dashed #00a8c7"></span>mới tại mốc này</span>
      <span class="legend-item"><span class="dot historical" style="background:#dff5ea;border:2px solid #334155"></span>lịch sử (mờ)</span>
      <span class="legend-item"><span class="line-key" style="border-color:#279567;color:#279567"></span>support</span>
      <span class="legend-item"><span class="line-key" style="border-color:#d14e4e;color:#d14e4e"></span>attack</span>
      <span class="legend-item"><span class="source-badge" style="background:#2264d1"></span>official_document</span>
      <span class="legend-item"><span class="source-badge" style="background:#7656a8"></span>authority_statement</span>
      <span class="legend-item"><span class="source-badge" style="background:#f09a32"></span>social</span>
      <span class="legend-item"><span class="source-badge" style="background:#7b8796"></span>news</span>
      <span class="legend-item"><span class="dot contextual" style="background:#e8f0ff;border:2px solid #315f9e"></span>lớp bối cảnh/thể chế</span>
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
const requestedTime = Number(initialParams.get('t')||0);
const initialTime = Number.isFinite(requestedTime)?Math.max(0,Math.min(5,requestedTime)):0;
const initialMode = initialParams.get('mode')==='viewpoints'?'viewpoints':'arguments';
const state = {
  time:initialTime, mode:initialMode, argType:'all', showSupport:true, showAttack:true,
  showRejected:true, showUndecided:true, onlyNew:false, playing:null,
  transform:{x:0,y:0,k:1}, positions:{arguments:{},viewpoints:{}},
  pinned:{arguments:new Set(),viewpoints:new Set()}, layoutSignature:{arguments:'',viewpoints:''}
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
  if (!state.showRejected && arg.semantic_status === 'rejected') return false;
  if (!state.showUndecided && arg.semantic_status === 'undecided') return false;
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

  const nodes = snap.viewpoints;
  const viewpointIds = new Set(nodes.map(v=>v.id));
  const edges = snap.viewpoint_relations.filter(edge => viewpointIds.has(edge.source) && viewpointIds.has(edge.target) &&
    ((edge.relation_type==='support' && state.showSupport) || (edge.relation_type==='attack' && state.showAttack)));
  return {nodes,edges,arguments:snap.arguments};
}

function hashNumber(value) {
  let h=2166136261;
  for(const c of value){h^=c.charCodeAt(0);h=Math.imul(h,16777619);}
  return (h>>>0)/4294967295;
}

function positionFor(id) {
  const cache = state.positions[state.mode];
  if (!cache[id]) cache[id] = {x:590,y:325};
  return cache[id];
}

function ensureLayout(data,forceReset=false) {
  const mode=state.mode, cache=state.positions[mode], pinned=state.pinned[mode];
  const signature=data.nodes.map(n=>n.id).sort().join('|')+'::'+data.edges.map(e=>`${e.source}>${e.target}:${e.relation_type}`).sort().join('|');
  if(!forceReset && state.layoutSignature[mode]===signature) return;
  if(forceReset){state.positions[mode]={};state.pinned[mode]=new Set();state.layoutSignature[mode]='';}
  const positions=state.positions[mode], previouslyPlaced=new Set(Object.keys(positions));
  const neighbors=new Map(data.nodes.map(n=>[n.id,[]]));
  data.edges.forEach(e=>{neighbors.get(e.source)?.push(e.target);neighbors.get(e.target)?.push(e.source);});
  data.nodes.forEach((node,index)=>{
    if(positions[node.id]) return;
    const known=(neighbors.get(node.id)||[]).map(id=>positions[id]).filter(Boolean);
    const jx=(hashNumber(node.id+'x')-.5)*80, jy=(hashNumber(node.id+'y')-.5)*80;
    if(known.length){positions[node.id]={x:known.reduce((s,p)=>s+p.x,0)/known.length+jx,y:known.reduce((s,p)=>s+p.y,0)/known.length+jy};}
    else {const angle=2*Math.PI*hashNumber(node.id),radius=75+220*hashNumber(node.id+'r');positions[node.id]={x:590+radius*Math.cos(angle),y:325+radius*.75*Math.sin(angle)};}
  });
  const anchors=Object.fromEntries(data.nodes.map(n=>[n.id,{...positions[n.id]}]));
  const iterations=previouslyPlaced.size?80:190, ideal=mode==='arguments'?205:270, minDistance=mode==='arguments'?156:205;
  for(let step=0;step<iterations;step++){
    const delta=Object.fromEntries(data.nodes.map(n=>[n.id,{x:0,y:0}]));
    for(let i=0;i<data.nodes.length;i++) for(let j=i+1;j<data.nodes.length;j++){
      const a=data.nodes[i].id,b=data.nodes[j].id,pa=positions[a],pb=positions[b];
      let dx=pb.x-pa.x,dy=pb.y-pa.y,dist=Math.max(2,Math.hypot(dx,dy));
      if(dist<3){dx=(hashNumber(a+b)-.5)*2;dy=(hashNumber(b+a)-.5)*2;dist=Math.max(2,Math.hypot(dx,dy));}
      const repulse=Math.min(18,11500/(dist*dist))+(dist<minDistance?(minDistance-dist)*.045:0),ux=dx/dist,uy=dy/dist;
      delta[a].x-=ux*repulse;delta[a].y-=uy*repulse;delta[b].x+=ux*repulse;delta[b].y+=uy*repulse;
    }
    data.edges.forEach(e=>{const a=positions[e.source],b=positions[e.target];if(!a||!b)return;const dx=b.x-a.x,dy=b.y-a.y,d=Math.max(2,Math.hypot(dx,dy)),pull=(d-ideal)*.018,ux=dx/d,uy=dy/d;delta[e.source].x+=ux*pull;delta[e.source].y+=uy*pull;delta[e.target].x-=ux*pull;delta[e.target].y-=uy*pull;});
    data.nodes.forEach(n=>{const p=positions[n.id],d=delta[n.id],anchor=anchors[n.id],anchorStrength=previouslyPlaced.has(n.id)?.075:.008;d.x+=(590-p.x)*.006+(anchor.x-p.x)*anchorStrength;d.y+=(325-p.y)*.006+(anchor.y-p.y)*anchorStrength;});
    const cap=7*(1-step/iterations)+.7;
    data.nodes.forEach(n=>{if(state.pinned[mode].has(n.id))return;const p=positions[n.id],d=delta[n.id],mag=Math.max(1,Math.hypot(d.x,d.y)),scale=Math.min(1,cap/mag);p.x=Math.max(92,Math.min(1088,p.x+d.x*scale));p.y=Math.max(55,Math.min(595,p.y+d.y*scale));});
  }
  state.layoutSignature[mode]=signature;
}

function edgePath(a,b,index=0,total=1) {
  const dx=b.x-a.x, dy=b.y-a.y, d=Math.max(1,Math.hypot(dx,dy));
  const ux=dx/d, uy=dy/d, halfWidth=state.mode==='arguments'?71:88,halfHeight=state.mode==='arguments'?31:37;
  const borderDistance=Math.min(halfWidth/Math.max(.001,Math.abs(ux)),halfHeight/Math.max(.001,Math.abs(uy)));
  const startCut=Math.min(borderDistance+3,Math.max(4,d/2-4)),endCut=Math.min(borderDistance+10,Math.max(4,d/2-4));
  const x1=a.x+ux*startCut, y1=a.y+uy*startCut, x2=b.x-ux*endCut, y2=b.y-uy*endCut;
  if(total===1) return {d:`M ${x1} ${y1} L ${x2} ${y2}`};
  const offset=(index-(total-1)/2)*38,nx=-uy,ny=ux,cx=(x1+x2)/2+nx*offset,cy=(y1+y2)/2+ny*offset;
  return {d:`M ${x1} ${y1} Q ${cx} ${cy} ${x2} ${y2}`};
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
    return `<strong>${esc(node.id)} — ${esc(node.name)}</strong><div class="tooltip-meta">${node.kind==='contextual'?'Lớp bối cảnh/thể chế':'Viewpoint tập thể'} · ${node.active_argument_ids.length} active · ${node.historical_argument_ids.length} lịch sử</div>
      <div class="tooltip-row">${esc(node.description)}</div>
      <div class="tooltip-row"><b>Trạng thái:</b> accepted ${counts.accepted} · rejected ${counts.rejected} · undecided ${counts.undecided}</div>
      <div class="tooltip-row"><b>Argument active:</b> ${node.active_argument_ids.map(esc).join(', ')}</div>
      <div class="tooltip-row"><b>Tương tác:</b> vào S${node.incoming_support}/A${node.incoming_attack} · ra S${node.outgoing_support}/A${node.outgoing_attack}</div>
      <div class="tooltip-sources"><b>Nguồn:</b> ${composition||'Không có'}</div>`;
  }
  return `<strong>${esc(node.id)} — ${esc(node.arg_type)}</strong><div class="tooltip-meta">introduced_at: ${esc(node.introduced_at)}${node.active_until?' · active_until: '+esc(node.active_until):''} · ${esc(node.activity)} · status: ${esc(node.semantic_status)}</div>
    <div class="tooltip-row"><b>Premise:</b> ${esc(node.premise)}</div>
    <div class="tooltip-row"><b>Rule:</b> ${node.rule?esc(node.rule):'<i>null — không có rule được nguồn hỗ trợ trực tiếp</i>'}</div>
    <div class="tooltip-row"><b>Conclusion:</b> ${esc(node.conclusion)}</div>
    <div class="tooltip-sources"><b>Nguồn:</b> ${node.source_ids.map(esc).join(', ')} · <b>Vai trò:</b> ${esc(node.temporal_role)}</div>`;
}
function edgeTooltip(edge) {
  if(state.mode==='viewpoints') return `<strong>${esc(edge.source)} → ${esc(edge.target)}</strong><div class="tooltip-meta">${esc(edge.relation_type)} · ${edge.relation_ids.length} quan hệ argument nền</div>
    <div class="tooltip-row"><b>Relation IDs:</b> ${edge.relation_ids.map(esc).join(', ')}</div>
    <div class="tooltip-row"><b>Mới tại mốc này:</b> ${(edge.new_relation_ids||[]).map(esc).join(', ')||'Không'}</div>
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
  ensureLayout(data);
  edgesLayer.replaceChildren(); nodesLayer.replaceChildren();
  const pairGroups=new Map();
  data.edges.forEach(edge=>{const key=[edge.source,edge.target].sort().join('|');if(!pairGroups.has(key))pairGroups.set(key,[]);pairGroups.get(key).push(edge);});

  data.edges.forEach(edge => {
    const siblings=pairGroups.get([edge.source,edge.target].sort().join('|')),p=edgePath(positionFor(edge.source),positionFor(edge.target),siblings.indexOf(edge),siblings.length);
    const group=document.createElementNS(NS,'g');
    const visible=document.createElementNS(NS,'path');
    visible.setAttribute('d',p.d);
    visible.setAttribute('class','edge-visible'+(edge.newly_introduced?' edge-new':''));
    visible.setAttribute('stroke',edge.relation_type==='support'?'#279567':'#d14e4e');
    if(state.mode==='viewpoints') visible.setAttribute('stroke-width',String(2+Math.min(6,edge.relation_ids.length*1.25)));
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
    const isNew=node.newly_introduced||(node.newly_active_arguments&&node.newly_active_arguments.length);
    const historical=state.mode==='arguments'&&node.activity==='historical';
    group.setAttribute('class','node'+(isNew?' new':'')+(historical?' historical':'')+(node.kind==='contextual'?' contextual':''));
    group.setAttribute('transform',`translate(${p.x} ${p.y})`); group.dataset.id=node.id;
    const rect=document.createElementNS(NS,'rect');
    const w=state.mode==='arguments'?142:176, h=state.mode==='arguments'?62:74;
    const halo=document.createElementNS(NS,'rect');halo.setAttribute('class','new-halo');halo.setAttribute('x',-w/2-6);halo.setAttribute('y',-h/2-6);halo.setAttribute('width',w+12);halo.setAttribute('height',h+12);halo.setAttribute('rx',16);
    rect.setAttribute('x',-w/2); rect.setAttribute('y',-h/2); rect.setAttribute('width',w); rect.setAttribute('height',h); rect.setAttribute('rx',12);
    if (state.mode==='arguments') {
      const style=statusStyle(node.semantic_status); rect.setAttribute('fill',style.fill);rect.setAttribute('stroke','#334155');
    } else { rect.setAttribute('fill','#e8f0ff'); rect.setAttribute('stroke','#315f9e'); }
    const title=document.createElementNS(NS,'title');
    title.textContent=state.mode==='arguments' ? `${node.id} — ${node.conclusion}` : `${node.id} — ${node.name}`;
    const line1=document.createElementNS(NS,'text'); line1.setAttribute('y',-9); line1.setAttribute('font-size','12'); line1.textContent=node.id;
    const line2=document.createElementNS(NS,'text'); line2.setAttribute('y',8); line2.setAttribute('font-size','10');
    line2.textContent=state.mode==='arguments'?`${node.arg_type} · ${node.semantic_status}`:truncate(node.name,28);
    const line3=document.createElementNS(NS,'text'); line3.setAttribute('y',23); line3.setAttribute('class','sub');
    line3.textContent=state.mode==='arguments'?(node.newly_introduced?'Mới tại mốc này':node.activity==='historical'?'Lịch sử · status được giữ':node.temporal_role):`${node.active_argument_ids.length} active · ${node.historical_argument_ids.length} lịch sử`;
    group.append(halo,rect,title,line1,line2,line3);
    if(state.mode==='arguments'){
      const priority=['official_document','authority_statement','social','news'],type=priority.find(k=>node.sources.some(s=>s.source_type===k))||'news';
      const badge=document.createElementNS(NS,'circle');badge.setAttribute('cx',w/2-10);badge.setAttribute('cy',-h/2+10);badge.setAttribute('r',6);badge.setAttribute('fill',({official_document:'#2264d1',authority_statement:'#7656a8',social:'#f09a32',news:'#7b8796'})[type]);badge.setAttribute('stroke','#fff');badge.setAttribute('stroke-width','2');group.appendChild(badge);
    }
    group.addEventListener('click',e=>{e.stopPropagation();showNodeDetail(node);});
    group.addEventListener('mouseenter',e=>showTooltip(nodeTooltip(node),e));
    group.addEventListener('mousemove',moveTooltip); group.addEventListener('mouseleave',hideTooltip);
    group.addEventListener('pointerdown',e=>{hideTooltip();startNodeDrag(e);});
    nodesLayer.appendChild(group);
  });
  $('graphSummary').textContent=`${data.nodes.length} node · ${data.edges.length} cạnh · ${data.arguments.length} lập luận ${state.mode==='viewpoints'?'khả dụng':'đang lọc'}`;
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
  const c=SNAPSHOTS[state.time].changes||{},changed=(c.changed_statuses||[]).map(x=>`${x.arg_id}: ${x.from} → ${x.to}`),activity=(c.activity_changes||[]).map(x=>`${x.arg_id}: ${x.from} → ${x.to}`),agentChanges=(c.new_viewpoint_interactions||[]).map(x=>`${x.source} → ${x.target} (${x.relation_type}: ${x.relation_ids.join(', ')})`);
  $('transitionSummary').innerHTML=`<div class="eyebrow">${esc(c.transition||'Snapshot hiện tại')}</div><div class="summary-row"><span class="pill">+${(c.new_arguments||[]).length} argument</span><span class="pill support">+${(c.new_support_relations||[]).length} support</span><span class="pill attack">+${(c.new_attack_relations||[]).length} attack</span><span class="pill">${changed.length} đổi status</span><span class="pill activity">${activity.length} đổi activity</span></div><div class="summary-detail">${[changed.length?'Status: '+changed.join('; '):'',activity.length?'Activity: '+activity.join('; '):'',agentChanges.length?'Tương tác viewpoint mới: '+agentChanges.join('; '):''].filter(Boolean).map(esc).join('<br>')||'Không có thay đổi so với snapshot trước.'}</div>`;
  [...$('ticks').children].forEach((el,i)=>el.classList.toggle('active',i===state.time));
}

function sourceList(argument) {
  if (!argument.sources.length) return '<p>Không có source ID.</p>';
  return '<ul>'+argument.sources.map(s=>`<li><a href="${esc(s.url)}" target="_blank" rel="noreferrer">${esc(s.source_id)}</a> — ${esc(s.title||'Chưa xác minh tiêu đề')}<br><small>${esc(s.source_type)} · ${esc(s.publisher)} · ${esc(s.verification_status)}</small></li>`).join('')+'</ul>';
}

function argumentBlock(a) {
  return `<div><h3>${esc(a.id)} <span class="pill ${esc(a.semantic_status)}">${esc(a.semantic_status)}</span> <span class="pill activity">${esc(a.activity)}</span></h3>
    <p><b>Kết luận:</b> ${esc(a.conclusion)}</p><p><b>Mốc:</b> ${esc(a.introduced_at)}${a.active_until?' → '+esc(a.active_until):''} · <b>Nguồn:</b> ${a.source_ids.map(esc).join(', ')}</p></div>`;
}

function showNodeDetail(node) {
  if (state.mode==='viewpoints') {
    const composition=Object.entries(node.source_composition).map(([k,v])=>`<span class="pill">${esc(k)}: ${v}</span>`).join(' ');
    const incident=SNAPSHOTS[state.time].new_viewpoint_interactions.filter(e=>e.source===node.id||e.target===node.id);
    const changes=node.state_change;
    $('detailPanel').innerHTML=`<div class="eyebrow">${node.kind==='contextual'?'Lớp bối cảnh/thể chế':'Viewpoint agent tập thể'}</div><h2>${esc(node.id)} — ${esc(node.name)}</h2>
      <p>${esc(node.description)}</p>
      <h3>Trạng thái quan điểm</h3><p><b>Tóm tắt:</b> ${esc(node.position_summary)}</p><p><b>Quy tắc bao gồm:</b> ${esc(node.inclusion_rule)}</p>
      <p><span class="pill accepted">accepted ${node.status_counts.accepted}</span><span class="pill rejected">rejected ${node.status_counts.rejected}</span><span class="pill undecided">undecided ${node.status_counts.undecided}</span></p>
      <p><b>Active:</b> ${node.active_argument_ids.map(esc).join(', ')||'Không có'}<br><b>Lịch sử:</b> ${node.historical_argument_ids.map(esc).join(', ')||'Không có'}</p>
      <h3>Lập luận khả dụng (${node.arguments.length}/${node.all_argument_ids.length})</h3>${node.arguments.map(argumentBlock).join('')||'<p>Không có.</p>'}
      <h3>Thành phần nguồn</h3><p>${composition||'Không có.'}</p>
      <h3>Tương tác có căn cứ</h3><p>Vào: support ${node.incoming_support} · attack ${node.incoming_attack}<br>Ra: support ${node.outgoing_support} · attack ${node.outgoing_attack}</p>
      <ul>${incident.map(e=>`<li>${esc(e.source)} → ${esc(e.target)} · ${esc(e.relation_type)} · mới: ${e.new_relation_ids.map(esc).join(', ')}</li>`).join('')||'<li>Không có tương tác liên-viewpoint mới tại mốc này.</li>'}</ul>
      <div class="why-changed"><h3>WHY THIS CHANGED</h3><p><b>Argument mới active:</b> ${changes.newly_active.map(esc).join(', ')||'Không'}<br><b>Chuyển lịch sử:</b> ${changes.became_historical.map(esc).join(', ')||'Không'}</p><p><b>Đổi phân bố status:</b> ${Object.entries(changes.status_count_changes).map(([k,v])=>`${esc(k)} ${v.from}→${v.to}`).join('; ')||'Không'}<br><b>Đổi quan hệ:</b> ${Object.entries(changes.relation_count_changes).map(([k,v])=>`${esc(k)} ${v.from}→${v.to}`).join('; ')||'Không'}</p></div>
      <h3>Quy tắc dựng agent</h3><p>${esc(MAPPING_METHOD)}</p>`;
    return;
  }
  const explanation=node.change_explanation;
  $('detailPanel').innerHTML=`<div class="eyebrow">Argument node</div><h2>${esc(node.id)} <span class="pill ${esc(node.semantic_status)}">${esc(node.semantic_status)}</span></h2>
    <p><span class="pill">${esc(node.arg_type)}</span><span class="pill">${esc(node.temporal_role)}</span><span class="pill activity">${esc(node.activity)}</span>${node.newly_introduced?'<span class="pill">mới tại mốc này</span>':''}</p>
    <h3>Premise</h3><p>${esc(node.premise)}</p>
    <h3>Rule</h3><p>${node.rule?esc(node.rule):'<i>null — không có quy tắc được nguồn hỗ trợ trực tiếp</i>'}</p>
    <h3>Conclusion</h3><p>${esc(node.conclusion)}</p>
    <h3>Thời gian và trạng thái</h3><p>introduced_at: <b>${esc(node.introduced_at)}</b>${node.active_until?' · active_until: <b>'+esc(node.active_until)+'</b>':''}</p>
    <p><b>Status basis:</b> ${esc(node.status_basis)}${node.status_basis==='carried_forward'?' từ '+esc(node.status_timestamp):''}</p><p>${esc(node.status_reason)}</p><p><b>Grounded by:</b> ${node.grounded_by.map(esc).join(', ')}</p>
    <h3>Quan hệ đi vào</h3><p><b>Support:</b> ${node.incoming_support.map(esc).join(', ')||'Không'}<br><b>Attack:</b> ${node.incoming_attack.map(esc).join(', ')||'Không'}</p>
    <div class="why-changed"><h3>WHY THIS CHANGED</h3>${explanation.changed?`<p><b>Status:</b> ${explanation.status_change?esc(explanation.status_change.from)+' → '+esc(explanation.status_change.to):'không đổi'}<br><b>Activity:</b> ${explanation.activity_change?esc(explanation.activity_change.from)+' → '+esc(explanation.activity_change.to):'không đổi'}</p><p><b>Argument chứng cứ mới:</b> ${explanation.new_evidence_arguments.map(esc).join(', ')||'Không'}<br><b>Quan hệ liên quan:</b> ${explanation.relevant_relation_ids.map(esc).join(', ')||'Không'}<br><b>Nguồn:</b> ${explanation.evidence_sources.map(esc).join(', ')||'Không'}</p><ul>${explanation.interpretation.map(x=>`<li>${esc(x)}</li>`).join('')}</ul>`:'<p>Không có thay đổi semantic/activity tại mốc này; trạng thái được giữ từ dữ liệu đã biết.</p>'}</div>
    <h3>Nguồn</h3>${sourceList(node)}`;
}

function showEdgeDetail(edge) {
  if (state.mode==='viewpoints') {
    $('detailPanel').innerHTML=`<div class="eyebrow">Viewpoint relation tổng hợp</div><h2>${esc(edge.source)} → ${esc(edge.target)}</h2>
      <p><span class="pill ${esc(edge.relation_type)}">${esc(edge.relation_type)}</span> · ${edge.relation_ids.length} quan hệ nền</p>
      <p><b>Mới tại mốc này:</b> ${edge.new_relation_ids.map(esc).join(', ')||'Không'}</p>
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
  $('argumentFilters').style.display=mode==='arguments'?'flex':'none';
  $('methodNote').textContent=mode==='viewpoints' ? MAPPING_METHOD : 'Node và cạnh được dựng trực tiếp từ CSV canonical; không có status, source hoặc relation nào được suy đoán.';
  $('detailPanel').innerHTML='<div class="detail-placeholder">Chọn một node hoặc cạnh để xem provenance và chi tiết.</div>';
  render();
}

function applyTransform(){ $('viewport').setAttribute('transform',`translate(${state.transform.x} ${state.transform.y}) scale(${state.transform.k})`); }
function resetView(){ state.transform={x:0,y:0,k:1};state.layoutSignature[state.mode]='';ensureLayout(filteredData(),true);render(); }
function graphPoint(event) {
  const svg=$('graph'), pt=svg.createSVGPoint(); pt.x=event.clientX; pt.y=event.clientY;
  const p=pt.matrixTransform($('viewport').getScreenCTM().inverse()); return {x:p.x,y:p.y};
}
let dragging=null, panning=null;
function startNodeDrag(event){ event.stopPropagation(); const id=event.currentTarget.dataset.id; const p=positionFor(id), g=graphPoint(event); state.pinned[state.mode].add(id);dragging={id,dx:p.x-g.x,dy:p.y-g.y,pointer:event.pointerId}; $('graph').setPointerCapture(event.pointerId); }
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
