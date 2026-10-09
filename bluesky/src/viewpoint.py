from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any


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
        incident = defaultdict(lambda: {"support": 0, "attack": 0})
        for relation in snapshot["relations"]:
            incident[relation["source"]][relation["relation_type"]] += 1
            incident[relation["target"]][relation["relation_type"]] += 1

        viewpoint_nodes: list[dict[str, Any]] = []
        for viewpoint in mapping["viewpoints"]:
            active_ids = [
                argument_id
                for argument_id in viewpoint["argument_ids"]
                if argument_id in argument_by_id and argument_by_id[argument_id]["active"]
            ]
            if not active_ids:
                continue
            active_arguments = [argument_by_id[argument_id] for argument_id in active_ids]
            status_counts = Counter(argument["status"] for argument in active_arguments)
            source_composition = Counter(
                source["source_type"]
                for argument in active_arguments
                for source in argument["sources"]
            )
            viewpoint_nodes.append({
                "id": viewpoint["viewpoint_id"],
                "name": viewpoint["name"],
                "description": viewpoint["description"],
                "all_argument_ids": viewpoint["argument_ids"],
                "active_argument_ids": active_ids,
                "arguments": active_arguments,
                "status_counts": {
                    "accepted": status_counts["accepted"],
                    "rejected": status_counts["rejected"],
                    "undecided": status_counts["undecided"],
                },
                "source_composition": dict(sorted(source_composition.items())),
                "support_relations": sum(incident[arg_id]["support"] for arg_id in active_ids),
                "attack_relations": sum(incident[arg_id]["attack"] for arg_id in active_ids),
                "newly_active_arguments": sum(
                    1 for argument in active_arguments if argument["newly_introduced"]
                ),
            })

        aggregate: dict[tuple[str, str, str], dict[str, Any]] = {}
        for relation in snapshot["relations"]:
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
                    "argument_relations": [],
                    "evidence_sources": [],
                }
            edge = aggregate[key]
            edge["relation_ids"].append(relation["id"])
            edge["argument_relations"].append({
                "relation_id": relation["id"],
                "source_arg": relation["source"],
                "target_arg": relation["target"],
                "conflict_type": relation["conflict_type"],
            })
            for source_id in relation["evidence_sources"]:
                if source_id not in edge["evidence_sources"]:
                    edge["evidence_sources"].append(source_id)

        snapshot["viewpoints"] = viewpoint_nodes
        snapshot["viewpoint_relations"] = list(aggregate.values())

    return snapshots

