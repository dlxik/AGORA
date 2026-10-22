from __future__ import annotations

from typing import Any

from bluesky.v2.validation import validate_trace_provenance


def validate_v3_trace(
    trace: dict[str, Any], data: dict[str, Any], snapshots: list[dict[str, Any]]
) -> dict[str, int]:
    base_counts = validate_trace_provenance(trace, data, snapshots)
    argument_ids = {row["final_arg_id"] for row in data["selected"]}
    relation_ids = {row["relation_id"] for row in data["relations"]}
    source_ids = {row["source_id"] for row in data["sources"]}
    agent_ids = {row["viewpoint_id"] for row in data["viewpoint_mapping"]["viewpoints"]}
    errors: list[str] = []
    event_ids: set[str] = set()
    counts = {**base_counts, "semantics": 0, "events": 0, "institutional_actions": 0}
    for run in trace["timestamps"]:
        for step in run["steps"]:
            semantics = step["argumentation_semantics"]
            counts["semantics"] += 1
            if set(semantics["input_argument_ids"]) - argument_ids:
                errors.append(f"{run['timestamp']}:k{step['deliberation_step']} semantics có argument lạ")
            if set(semantics["input_relation_ids"]) - relation_ids:
                errors.append(f"{run['timestamp']}:k{step['deliberation_step']} semantics có relation lạ")
            for result in semantics["results"].values():
                if result["semantic_status"] not in {"accepted", "rejected", "undecided"}:
                    errors.append(f"Semantic status không hợp lệ: {result['semantic_status']}")
            for audit in step["institutional_protocol_audit"]:
                counts["institutional_actions"] += 1
                if not audit["valid"]:
                    errors.append(f"Institutional action vi phạm: {audit['action_id']}")
            for event in step["society_events"]:
                counts["events"] += 1
                if event["event_id"] in event_ids:
                    errors.append(f"Society event ID trùng: {event['event_id']}")
                event_ids.add(event["event_id"])
                if set(event["involved_agents"]) - agent_ids:
                    errors.append(f"{event['event_id']} có agent không thuộc runtime base")
                if set(event["involved_arguments"]) - argument_ids:
                    errors.append(f"{event['event_id']} có argument lạ")
                provenance = event["provenance"]
                if set(provenance.get("argument_ids", [])) - argument_ids:
                    errors.append(f"{event['event_id']} có provenance argument lạ")
                if set(provenance.get("relation_ids", [])) - relation_ids:
                    errors.append(f"{event['event_id']} có provenance relation lạ")
                if set(provenance.get("source_ids", [])) - source_ids:
                    errors.append(f"{event['event_id']} có provenance source lạ")
                if not event["explanation"] or not event["threshold"]:
                    errors.append(f"{event['event_id']} thiếu explanation/threshold")
            metrics = step["society_metrics_v3"]
            if metrics["simulation_convergence"] and not metrics["convergence_consensus_separated"]:
                errors.append("Simulation convergence bị đồng nhất với consensus")
            if step["runtime_society_structure"]["base_mapping_immutable"] is not True:
                errors.append("Runtime society không đánh dấu base mapping bất biến")
    if errors:
        raise ValueError("V3 trace không hợp lệ:\n- " + "\n- ".join(errors))
    return counts
