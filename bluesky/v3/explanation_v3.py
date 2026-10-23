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


def conflict_explanation(public_id: str, reference_id: str | None, score: float, relation_ids: list[str]) -> str:
    fact = (
        f"FACT: canonical attack {','.join(relation_ids)} connects {public_id} to {reference_id}."
        if relation_ids else f"FACT: no canonical attack from {public_id} to an eligible A_K was recorded."
    )
    return (
        f"{fact} MODEL: C={score:.4f} is the maximum grounded pair score in H. "
        "LIMITATION: text-only contradiction is not inferred."
    )


def steering_explanation(argument_id: str, score: float, downstream_count: int) -> str:
    return (
        f"FACT: {argument_id} precedes and has observable linkage to {downstream_count} downstream A_D argument(s). "
        f"MODEL: normalized outgoing steering proxy S={score:.4f}. "
        "LIMITATION: precedence and structural linkage do not prove causal influence."
    )


def risk_explanation(argument_id: str, conflict: float, steering: float, risk: float) -> str:
    return (
        f"FACT: the trace supplies canonical conflict/linkage evidence for {argument_id}. "
        f"MODEL: configured f(C,S) maps C={conflict:.4f}, S={steering:.4f} to RS={risk:.4f}. "
        "LIMITATION: RS prioritizes review; it does not establish factual harmfulness."
    )


def priority_explanation(argument_id: str, rank: int, risk: float) -> str:
    return (
        f"MODEL: {argument_id} is priority {rank} after descending RS={risk:.4f} "
        "with argument-ID tie-break. LIMITATION: rank is configuration-dependent."
    )


def alert_explanation(alert_type: str, current: float, previous: float | None, threshold: float) -> str:
    prior = "N/A" if previous is None else f"{previous:.4f}"
    return (
        f"MODEL: {alert_type} triggered by previous={prior}, current={current:.4f}, "
        f"configured threshold={threshold:.4f}. LIMITATION: deterministic model alert, not a factual incident claim."
    )
