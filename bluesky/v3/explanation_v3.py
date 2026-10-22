from __future__ import annotations

from typing import Any

from bluesky.v2.explanation import concise_step_log


def society_step_log(step: dict[str, Any]) -> list[str]:
    lines = concise_step_log(step)
    prefix = f"[{step['timestamp']}:k{step['deliberation_step']}]"
    semantics = step["argumentation_semantics"]
    lines.append(
        f"{prefix} SEMANTICS {semantics['method']} iterations={semantics['iterations']} "
        f"converged={semantics['converged']}"
    )
    metrics = step["society_metrics_v3"]
    lines.append(
        f"{prefix} SOCIETY dominant={metrics['dominant_viewpoint']} "
        f"convergence_proxy={metrics['convergence_proxy']:.4f} "
        f"fragmentation_proxy={metrics['fragmentation_proxy']:.4f}"
    )
    for event in step["society_events"]:
        lines.append(
            f"{prefix} EVENT {event['event_type']} agents={','.join(event['involved_agents']) or '-'}"
        )
    return lines
