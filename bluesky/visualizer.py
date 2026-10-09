from html import escape
from pathlib import Path
from typing import List


def _position_label(x: float) -> str:
    if x < -0.2:
        return "skeptical / opposing"
    if x > 0.2:
        return "supportive / accepting"
    return "uncertain / neutral"


def render_html(snapshots: List[dict], events, output_path: str) -> Path:
    cards = []
    for snap in snapshots:
        agents = snap["agents"]
        agent_html = []
        for agent in agents.values():
            kind = "Institutional" if agent.kind == "institutional" else "Collective viewpoint"
            beliefs = "".join(f"<li>{escape(a.text)}</li>" for a in agent.beliefs)
            evidence = "".join(f"<li>{escape(e)}</li>" for e in agent.evidence) or "<li>None added yet</li>"
            agent_html.append(f"""
            <div class="agent {'institutional' if agent.kind == 'institutional' else ''}">
              <h3>{escape(agent.id)} — {escape(agent.name)}</h3>
              <div class="meta">{kind}</div>
              <div><b>Position:</b> {agent.position:.2f} ({_position_label(agent.position)})</div>
              <div><b>Strength:</b> {agent.strength:.2f}</div>
              <div class="bar"><span style="width:{agent.strength*100:.0f}%"></span></div>
              <details><summary>Beliefs / arguments</summary><ul>{beliefs}</ul></details>
              <details><summary>Evidence received</summary><ul>{evidence}</ul></details>
            </div>
            """)
        cards.append(f"""
        <section>
          <h2>Round {snap['round']}: {escape(snap['label'])}</h2>
          <div class="grid">{''.join(agent_html)}</div>
        </section>
        """)

    event_rows = "".join(
        f"<tr><td>{e.round_id}</td><td>{e.source}</td><td>{escape(e.action)}</td>"
        f"<td>{e.target}</td><td>{escape(e.argument)}</td>"
        f"<td>{e.position_delta:+.2f}</td><td>{e.strength_delta:+.2f}</td></tr>"
        for e in events
    )

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>AGORA Blue Sky Demo</title>
<style>
body {{ font-family: Arial, sans-serif; max-width: 1200px; margin: 32px auto; padding: 0 20px; background:#f7f7f8; color:#222; }}
h1 {{ margin-bottom: 4px; }}
.subtitle {{ color:#555; margin-bottom:28px; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(250px,1fr)); gap:14px; }}
.agent {{ background:white; border:1px solid #ddd; border-radius:12px; padding:16px; box-shadow:0 2px 6px #00000010; }}
.agent.institutional {{ border:2px solid #555; }}
.meta {{ font-size:12px; color:#666; margin-bottom:10px; text-transform:uppercase; }}
.bar {{ height:8px; background:#e6e6e6; border-radius:8px; overflow:hidden; margin:7px 0 10px; }}
.bar span {{ display:block; height:100%; background:#555; }}
section {{ margin:34px 0; }}
table {{ width:100%; border-collapse:collapse; background:white; }}
th,td {{ border:1px solid #ddd; padding:8px; vertical-align:top; }}
th {{ background:#eee; }}
.callout {{ background:white; border-left:5px solid #333; padding:14px 18px; margin:20px 0; }}
</style>
</head>
<body>
<h1>AGORA — From Static Arguments to Agentic Public Deliberation</h1>
<p class="subtitle">Proof-of-concept: explicit argument structures become stateful viewpoint agents whose interactions generate observable opinion dynamics.</p>
<div class="callout">
<b>What to look for:</b> V3 changes from uncertainty after receiving institutional evidence; V2 is challenged and its strength decreases. The demo is deterministic and traceable to explicit interactions, not free-form role-play.
</div>
{''.join(cards)}
<h2>Interaction trace</h2>
<table>
<tr><th>Round</th><th>Source</th><th>Action</th><th>Target</th><th>Argument / evidence</th><th>Δ position</th><th>Δ strength</th></tr>
{event_rows}
</table>
</body></html>"""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    return path
