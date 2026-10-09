from __future__ import annotations

from datetime import date
from typing import Any

from .loader import TIMESTAMP_IDS


def _split_ids(value: str) -> list[str]:
    return [item for item in value.split(";") if item]


def _date(value: str) -> date | None:
    return date.fromisoformat(value) if value else None


def build_temporal_snapshots(data: dict[str, Any]) -> list[dict[str, Any]]:
    rank = {timestamp_id: index for index, timestamp_id in enumerate(TIMESTAMP_IDS)}
    canonical_by_id = {row["arg_id"]: row for row in data["canonical"]}
    source_by_id = {row["source_id"]: row for row in data["sources"]}
    status_by_key = {
        (row["arg_id"], row["timestamp_id"]): row for row in data["statuses"]
    }
    snapshots: list[dict[str, Any]] = []

    for timestamp in data["timeline"]:
        timestamp_id = timestamp["timestamp_id"]
        timestamp_rank = rank[timestamp_id]
        visible_arguments: list[dict[str, Any]] = []

        for selected in data["selected"]:
            canonical = canonical_by_id[selected["final_arg_id"]]
            introduced_rank = rank[selected["introduced_at"]]
            if introduced_rank > timestamp_rank:
                continue

            status_row = status_by_key.get((selected["final_arg_id"], timestamp_id))
            active_until = canonical["active_until"] or "t6"
            should_be_active = rank[active_until] >= timestamp_rank
            if should_be_active and status_row is None:
                raise ValueError(f"Thiếu status cho argument active {selected['final_arg_id']} tại {timestamp_id}")

            source_ids = _split_ids(selected["source_ids"])
            visible_arguments.append({
                "id": selected["final_arg_id"],
                "candidate_id": selected["candidate_id"],
                "arg_type": selected["arg_type"],
                "premise": canonical["premise"],
                "rule": canonical["rule"] or None,
                "conclusion": canonical["conclusion"],
                "source_ids": source_ids,
                "source_type": selected["source_type"],
                "sources": [
                    {
                        "source_id": source_id,
                        "title": source_by_id[source_id]["title"],
                        "url": source_by_id[source_id]["url"],
                        "source_type": source_by_id[source_id]["source_type"],
                        "publisher": source_by_id[source_id]["publisher"],
                        "verification_status": source_by_id[source_id]["verification_status"],
                    }
                    for source_id in source_ids
                ],
                "introduced_at": selected["introduced_at"],
                "active_until": canonical["active_until"] or None,
                "temporal_role": selected["temporal_role"],
                "status": status_row["status"] if status_row else None,
                "status_reason": status_row["reason"] if status_row else "Không có bản ghi status tại mốc này; node được giữ để biểu diễn lập luận lịch sử và quan hệ thời gian.",
                "grounded_by": _split_ids(status_row["grounded_by"]) if status_row else [],
                "active": status_row is not None,
                "newly_introduced": selected["introduced_at"] == timestamp_id,
            })

        visible_ids = {argument["id"] for argument in visible_arguments}
        start = _date(timestamp["date_start"])
        end = _date(timestamp["date_end"])
        visible_relations: list[dict[str, Any]] = []
        for relation in data["relations"]:
            relation_start = _date(relation["valid_from"])
            relation_end = _date(relation["valid_to"])
            is_introduced = rank[relation["introduced_at"]] <= timestamp_rank
            is_date_valid = (
                (relation_start is None or relation_start <= end)
                and (relation_end is None or relation_end >= start)
            )
            endpoints_visible = (
                relation["source_arg"] in visible_ids and relation["target_arg"] in visible_ids
            )
            if not (is_introduced and is_date_valid and endpoints_visible):
                continue
            visible_relations.append({
                "id": relation["relation_id"],
                "source": relation["source_arg"],
                "target": relation["target_arg"],
                "relation_type": relation["relation_type"],
                "conflict_type": relation["conflict_type"] or None,
                "introduced_at": relation["introduced_at"],
                "valid_from": relation["valid_from"] or None,
                "valid_to": relation["valid_to"] or None,
                "evidence_sources": _split_ids(relation["evidence_sources"]),
                "confidence": relation["confidence"],
                "notes": relation["notes"],
                "newly_introduced": relation["introduced_at"] == timestamp_id,
            })

        snapshots.append({
            "timestamp": timestamp,
            "arguments": visible_arguments,
            "relations": visible_relations,
        })

    return snapshots

