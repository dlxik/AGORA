from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from bluesky.v2.visualizer_v2 import HTML as V2_HTML


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def _replace(html: str, old: str, new: str) -> str:
    if old not in html:
        raise ValueError(f"Không tìm thấy V2 template hook: {old[:80]}")
    return html.replace(old, new)


V3_CSS = r'''
.tabs button{padding-left:5px;padding-right:5px;font-size:11px}
.society-row{display:grid;grid-template-columns:1fr auto;gap:8px;padding:7px 8px;border-bottom:1px solid #e6ebf1;font-size:12px}.society-row b:last-child{color:#174b8a}
.event-card{margin:8px 0;padding:9px 10px;border:1px solid #dce5ef;border-left:4px solid var(--violet);border-radius:8px;background:#f8fbff;cursor:pointer;font-size:12px}.event-card:hover{background:#eef4ff}.event-card b{color:#173e78}.event-card small{color:var(--muted)}
.semantics-compare{margin-top:14px;padding-top:10px;border-top:1px solid #dce5ef}.semantic-row{display:grid;grid-template-columns:1fr auto;gap:6px;margin:5px 0;padding:7px 8px;border-radius:7px;background:#f4f0ff;font-size:11px}
.agent.dominant rect{stroke:#e39224;stroke-width:4}.agent.event-highlight rect{stroke:#ff9f1a;stroke-width:5;filter:drop-shadow(0 0 9px #ff9f1a99)}.agent.persistent-conflict rect{stroke:#ef4d5a;stroke-dasharray:5 3}.v3-badge{font-size:9px;fill:#9b5b00!important;font-weight:950!important;paint-order:stroke;stroke:#fff;stroke-width:3px}.v3-split{fill:#9b2c7f!important}
.proxy-note{padding:8px 9px;border-radius:8px;background:#fff7e8;color:#6c4a17;font-size:11px}
'''


V3_JS = r'''
function societyPanel(){const m=current().step.society_metrics_v3,cohesion=m.viewpoint_cohesion,prevalence=m.structural_prevalence;$('society').innerHTML=`<h2>Xã hội động</h2><div class="pill">${esc(current().run.timestamp)} / k${current().step.deliberation_step}</div><div class="profile-summary"><b>Dominant:</b> ${esc(m.dominant_viewpoint||'không')}<br><b>Convergence proxy:</b> ${m.convergence_proxy.toFixed(3)} · <b>Consensus proxy:</b> ${m.consensus_proxy.toFixed(3)}<br><b>Fragmentation:</b> ${m.fragmentation_proxy.toFixed(3)} · <b>Polarization:</b> ${m.polarization_proxy.toFixed(3)}</div><div class="proxy-note">Đây là proxy cấu trúc của mô phỏng, không phải mức ủng hộ hay đồng thuận xã hội thật.</div><h3>COHESION / PREVALENCE</h3>${Object.keys(cohesion).map(id=>`<div class="society-row"><span><b>${esc(id)}</b><br><small>cohesion ${cohesion[id].cohesion.toFixed(3)} · split ${cohesion[id].split_score.toFixed(3)}</small></span><b>${(prevalence[id]?.structural_prevalence||0).toFixed(3)}</b></div>`).join('')}<h3>SPLIT CANDIDATES</h3>${m.split_candidates.map(x=>`<div class="card">${esc(x.agent_id)} · ${x.score.toFixed(3)} / ${x.threshold}</div>`).join('')||'<div class="card">Không có.</div>'}<h3>MERGE CANDIDATES</h3>${m.merge_candidates.map(x=>`<div class="card">${x.agents.map(esc).join(' + ')} · ${x.score.toFixed(3)} / ${x.threshold}</div>`).join('')||'<div class="card">Không có.</div>'}<h3>COMPONENTS</h3><div class="card">${m.weakly_connected_components.map(x=>x.map(esc).join(' ↔ ')).join('<br>')}<br><small>Isolated: ${m.isolated_agents.map(esc).join(', ')||'không'}</small></div>`}
function highlightAgents(ids){document.querySelectorAll('.agent').forEach(n=>n.classList.toggle('event-highlight',ids.includes(n.dataset.id)))}
function eventsPanel(){const ti=state.t,ki=state.k,visible=TRACE.society_events.filter(e=>{const ei=TRACE.timestamps.findIndex(r=>r.timestamp===e.timestamp);return ei<ti||(ei===ti&&e.deliberation_step<=ki)});$('events').innerHTML=`<h2>Society Events</h2><div class="proxy-note">SocietyEvent là sự kiện cấu trúc có provenance, không phải trục thời gian thứ ba.</div>${visible.map(e=>`<div class="event-card" data-event-agents="${esc(e.involved_agents.join(','))}"><small>${esc(e.timestamp)} / k${e.deliberation_step}</small><br><b>${esc(e.event_type)}</b><br>${esc(e.involved_agents.join(' ↔ ')||'toàn xã hội')}<br><small>${esc(e.explanation)}</small></div>`).join('')||'<div class="empty">Chưa có society event tới bước này.</div>'}`;document.querySelectorAll('[data-event-agents]').forEach(card=>card.onclick=()=>highlightAgents(card.dataset.eventAgents.split(',').filter(Boolean)))}
function enhanceReasoningPanel(){if(state.edge!==null)return;const id=state.agent;if(!id)return;const step=current().step,owned=Object.keys(step.agent_states_after[id]?.belief_states||{}),rows=owned.map(arg=>step.argumentation_semantics.results[arg]).filter(Boolean);if(!rows.length)return;const box=document.createElement('section');box.className='semantics-compare';box.innerHTML=`<h3>HEURISTIC ↔ ARGUMENTATION SEMANTICS</h3>${rows.map(x=>`<div class="semantic-row"><span><b>${esc(x.argument_id)}</b><br>${esc(x.semantic_status)}</span><span>H ${x.heuristic_score.toFixed(3)} · S <b>${x.semantic_score.toFixed(3)}</b> · revise <b>${x.revision_blend_score.toFixed(3)}</b></span></div>`).join('')}<small>${esc(step.argumentation_semantics.method)} · acceptability proxy, không phải factual truth.</small>`;$('reasoning').appendChild(box)}
function decorateV3Graph(){const step=current().step,m=step.society_metrics_v3,split=new Set(m.split_candidates.map(x=>x.agent_id)),conflict=new Set(step.society_events.filter(e=>e.event_type==='PERSISTENT_CONFLICT').flatMap(e=>e.involved_agents));document.querySelectorAll('.agent').forEach(node=>{const id=node.dataset.id,p=m.structural_prevalence[id]?.structural_prevalence||0,c=m.viewpoint_cohesion[id]?.cohesion||0;node.classList.toggle('dominant',id===m.dominant_viewpoint);node.classList.toggle('persistent-conflict',conflict.has(id));const rect=node.querySelector('rect');rect.style.strokeWidth=(2.5+p*2).toFixed(2);if(c>.72)rect.style.filter=`drop-shadow(0 0 ${Math.round(3+c*5)}px rgba(22,185,120,.42))`;if(id===m.dominant_viewpoint||split.has(id)){const badge=document.createElementNS('http://www.w3.org/2000/svg','text');badge.setAttribute('x','82');badge.setAttribute('y','-8');badge.setAttribute('class',`v3-badge ${split.has(id)?'v3-split':''}`);badge.textContent=id===m.dominant_viewpoint?'◆ DOMINANT':'◇ SPLIT?';node.appendChild(badge)}})}
'''


def _template() -> str:
    html = V2_HTML
    html = _replace(html, "<title>AGORA V2 — Autonomous Argumentative Agents</title>", "<title>AGORA V3 — Dynamic Agent Society</title>")
    html = _replace(html, "content:'V2'", "content:'V3'")
    html = _replace(html, '<div class="subtitle">V2 · Argumentative Agents</div>', '<div class="subtitle">V3 · Dynamic Agent Society</div>')
    html = _replace(html, '<div class="version">DETERMINISTIC BASELINE</div>', '<div class="version">SEMANTICS · SOCIETY DYNAMICS</div>')
    html = _replace(html, "</style>", V3_CSS + "\n</style>")
    html = _replace(
        html,
        '<aside class="rail"><nav class="tabs"><button class="active" data-tab="reasoning">Lập luận</button><button data-tab="activity">Hoạt động</button><button data-tab="metrics">Chỉ số</button></nav><section class="panel" id="reasoning"></section><section class="panel" id="activity" hidden></section><section class="panel" id="metrics" hidden></section></aside>',
        '<aside class="rail"><nav class="tabs"><button class="active" data-tab="reasoning">Lập luận</button><button data-tab="activity">Hoạt động</button><button data-tab="society">Xã hội</button><button data-tab="events">Sự kiện</button><button data-tab="metrics">Chỉ số</button></nav><section class="panel" id="reasoning"></section><section class="panel" id="activity" hidden></section><section class="panel" id="society" hidden></section><section class="panel" id="events" hidden></section><section class="panel" id="metrics" hidden></section></aside>',
    )
    html = _replace(html, "function metricsPanel(){", V3_JS + "\nfunction metricsPanel(){")
    html = _replace(
        html,
        "function renderPanels(){if(state.edge!==null)interactionPanel();else reasoningPanel();activityPanel();metricsPanel()}function render(){buttons();phase();renderGraph();renderPanels()}",
        "function renderPanels(){if(state.edge!==null)interactionPanel();else reasoningPanel();enhanceReasoningPanel();activityPanel();societyPanel();eventsPanel();metricsPanel()}function render(){buttons();phase();renderGraph();decorateV3Graph();renderPanels()}",
    )
    html = _replace(
        html,
        "['reasoning','activity','metrics'].forEach(id=>$(id).hidden=id!==b.dataset.tab)",
        "['reasoning','activity','society','events','metrics'].forEach(id=>$(id).hidden=id!==b.dataset.tab)",
    )
    return html


HTML = _template()


def render_v3_html(trace: dict[str, Any], mapping: dict[str, Any], output_path: Path) -> Path:
    html = HTML.replace("__TRACE__", _json(trace)).replace("__MAPPING__", _json(mapping))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    return output_path
