from __future__ import annotations

from collections import Counter
from typing import Any


STATE_COUNT_FIELDS = (
    "incoming_support",
    "incoming_attack",
    "outgoing_support",
    "outgoing_attack",
)


def add_viewpoint_layers(
    snapshots: list[dict[str, Any]], mapping: dict[str, Any]
) -> list[dict[str, Any]]:
    argument_to_viewpoint = {
        argument_id: viewpoint["viewpoint_id"]
        for viewpoint in mapping["viewpoints"]
        for argument_id in viewpoint["argument_ids"]
    }

    for snapshot in snapshots:
        argument_by_id = {argument["id"]: argument for argument in snapshot["arguments"]}
        aggregate = _aggregate_interactions(snapshot["relations"], argument_to_viewpoint)
        interaction_counts = _interaction_counts(aggregate.values())
        viewpoint_nodes: list[dict[str, Any]] = []

        for viewpoint in mapping["viewpoints"]:
            available_arguments = [
                argument_by_id[argument_id]
                for argument_id in viewpoint["argument_ids"]
                if argument_id in argument_by_id
            ]
            if not available_arguments:
                continue
            active_arguments = [a for a in available_arguments if a["activity"] == "active"]
            historical_arguments = [a for a in available_arguments if a["activity"] == "historical"]
            status_counts = Counter(argument["semantic_status"] for argument in available_arguments)
            source_composition = Counter(
                source["source_type"]
                for argument in available_arguments
                for source in argument["sources"]
            )
            counts = interaction_counts.get(viewpoint["viewpoint_id"], {})
            viewpoint_nodes.append({
                "id": viewpoint["viewpoint_id"],
                "kind": viewpoint["kind"],
                "name": viewpoint["name"],
                "description": viewpoint["description"],
                "position_summary": viewpoint["position_summary"],
                "inclusion_rule": viewpoint["inclusion_rule"],
                "all_argument_ids": viewpoint["argument_ids"],
                "available_argument_ids": [a["id"] for a in available_arguments],
                "active_argument_ids": [a["id"] for a in active_arguments],
                "historical_argument_ids": [a["id"] for a in historical_arguments],
                "arguments": available_arguments,
                "active_arguments": active_arguments,
                "historical_arguments": historical_arguments,
                "status_counts": {
                    "accepted": status_counts["accepted"],
                    "rejected": status_counts["rejected"],
                    "undecided": status_counts["undecided"],
                },
                "source_composition": dict(sorted(source_composition.items())),
                "incoming_support": counts.get("incoming_support", 0),
                "incoming_attack": counts.get("incoming_attack", 0),
                "outgoing_support": counts.get("outgoing_support", 0),
                "outgoing_attack": counts.get("outgoing_attack", 0),
                "newly_active_arguments": [a["id"] for a in active_arguments if a["newly_introduced"]],
            })

        snapshot["viewpoints"] = viewpoint_nodes
        snapshot["viewpoint_relations"] = list(aggregate.values())
        snapshot["new_viewpoint_interactions"] = [
            interaction for interaction in aggregate.values() if interaction["new_relation_ids"]
        ]
        snapshot["changes"]["new_viewpoint_interactions"] = [
            {
                "source": interaction["source"],
                "target": interaction["target"],
                "relation_type": interaction["relation_type"],
                "relation_ids": interaction["new_relation_ids"],
            }
            for interaction in snapshot["new_viewpoint_interactions"]
        ]

    _add_agent_state_diffs(snapshots)
    return snapshots


def _aggregate_interactions(
    relations: list[dict[str, Any]], argument_to_viewpoint: dict[str, str]
) -> dict[tuple[str, str, str], dict[str, Any]]:
    aggregate: dict[tuple[str, str, str], dict[str, Any]] = {}
    for relation in relations:
        source_viewpoint = argument_to_viewpoint[relation["source"]]
        target_viewpoint = argument_to_viewpoint[relation["target"]]
        if source_viewpoint == target_viewpoint:
            continue
        key = (source_viewpoint, target_viewpoint, relation["relation_type"])
        if key not in aggregate:
            aggregate[key] = {
                "id": f"{source_viewpoint}-{target_viewpoint}-{relation['relation_type']}",
                "source": source_viewpoint,
                "target": target_viewpoint,
                "relation_type": relation["relation_type"],
                "relation_ids": [],
                "new_relation_ids": [],
                "argument_relations": [],
                "evidence_sources": [],
                "newly_introduced": False,
            }
        edge = aggregate[key]
        edge["relation_ids"].append(relation["id"])
        if relation["newly_introduced"]:
            edge["new_relation_ids"].append(relation["id"])
            edge["newly_introduced"] = True
        edge["argument_relations"].append({
            "relation_id": relation["id"],
            "source_arg": relation["source"],
            "target_arg": relation["target"],
            "relation_type": relation["relation_type"],
            "conflict_type": relation["conflict_type"],
            "newly_introduced": relation["newly_introduced"],
        })
        for source_id in relation["evidence_sources"]:
            if source_id not in edge["evidence_sources"]:
                edge["evidence_sources"].append(source_id)
    return aggregate


def _interaction_counts(interactions: Any) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = {}
    for interaction in interactions:
        amount = len(interaction["relation_ids"])
        source = counts.setdefault(interaction["source"], {})
        target = counts.setdefault(interaction["target"], {})
        source[f"outgoing_{interaction['relation_type']}"] = source.get(
            f"outgoing_{interaction['relation_type']}", 0
        ) + amount
        target[f"incoming_{interaction['relation_type']}"] = target.get(
            f"incoming_{interaction['relation_type']}", 0
        ) + amount
    return counts


def _add_agent_state_diffs(snapshots: list[dict[str, Any]]) -> None:
    previous_nodes: dict[str, dict[str, Any]] = {}
    for snapshot in snapshots:
        current_nodes = {node["id"]: node for node in snapshot["viewpoints"]}
        for node in snapshot["viewpoints"]:
            previous = previous_nodes.get(node["id"])
            previous_active = set(previous["active_argument_ids"]) if previous else set()
            previous_historical = set(previous["historical_argument_ids"]) if previous else set()
            count_changes = {}
            relation_changes = {}
            for status in ("accepted", "rejected", "undecided"):
                old = previous["status_counts"][status] if previous else 0
                new = node["status_counts"][status]
                if old != new:
                    count_changes[status] = {"from": old, "to": new}
            for field in STATE_COUNT_FIELDS:
                old = previous[field] if previous else 0
                new = node[field]
                if old != new:
                    relation_changes[field] = {"from": old, "to": new}
            node["state_change"] = {
                "newly_active": [arg_id for arg_id in node["active_argument_ids"] if arg_id not in previous_active],
                "became_historical": [arg_id for arg_id in node["historical_argument_ids"] if arg_id not in previous_historical],
                "status_count_changes": count_changes,
                "relation_count_changes": relation_changes,
            }
        previous_nodes = current_nodes
