from __future__ import annotations

from typing import Any

from .config_v3 import V3Config
from .conflict import ConflictEvaluator
from .explanation_v3 import priority_explanation
from .risk import RiskEvaluator
from .steering import SteeringEvaluator


class RiskMonitoringEngine:
    """Build reproducible current-to-date H_t rankings for public discourse A_D."""

    def __init__(
        self,
        data: dict[str, Any],
        snapshots: list[dict[str, Any]],
        trace: dict[str, Any],
        config: V3Config,
    ) -> None:
        self.data = data
        self.snapshots = snapshots
        self.trace = trace
        self.config = config
        self.conflict = ConflictEvaluator(data, snapshots, config.conflict)
        self.steering = SteeringEvaluator(data, snapshots, trace, config.steering)
        self.risk = RiskEvaluator(config.risk)
        self.catalog = trace["argument_catalog"]

    def build(self) -> dict[str, Any]:
        by_window: dict[str, Any] = {}
        history: dict[str, list[dict[str, Any]]] = {
            argument_id: []
            for argument_id, row in self.catalog.items() if row["arg_type"] == "A_D"
        }
        previous: dict[str, dict[str, float]] = {}
        steering_streaks = {argument_id: 0 for argument_id in history}
        all_alerts = []
        for end_index, timeline in enumerate(self.data["timeline"]):
            window_id = timeline["timestamp_id"]
            eligible = self.steering.eligible_discourse(0, end_index)
            rows = []
            for argument_id in eligible:
                conflict = self.conflict.evaluate(argument_id, 0, end_index)
                steering = self.steering.evaluate(argument_id, 0, end_index)
                risk = self.risk.evaluate(argument_id, conflict, steering)
                current = {
                    "conflict": conflict["conflict_score"],
                    "steering": steering["steering_score"],
                    "risk": risk["risk_score"],
                }
                steering_streaks[argument_id] = (
                    steering_streaks[argument_id] + 1
                    if current["steering"] >= self.config.risk.high_steering_threshold else 0
                )
                alerts = self.risk.alerts(
                    argument_id, current, previous.get(argument_id), steering_streaks[argument_id]
                )
                row = {
                    "argument_id": argument_id,
                    "conclusion": self.catalog[argument_id]["conclusion"],
                    "owner_viewpoint": self.trace["argument_owner"][argument_id],
                    "introduced_at": self.catalog[argument_id]["introduced_at"],
                    "conflict_score": current["conflict"],
                    "steering_score": current["steering"],
                    "risk_score": current["risk"],
                    "risk_band": risk["risk_band"],
                    "assessment_quality": risk["assessment_quality"],
                    "above_risk_threshold": risk["above_risk_threshold"],
                    "conflict_evidence": conflict,
                    "steering_evidence": steering,
                    "risk_detail": risk,
                    "alerts": alerts,
                    "trend": {
                        "conflict_delta": round(current["conflict"] - previous.get(argument_id, current)["conflict"], 4),
                        "steering_delta": round(current["steering"] - previous.get(argument_id, current)["steering"], 4),
                        "risk_delta": round(current["risk"] - previous.get(argument_id, current)["risk"], 4),
                    },
                }
                rows.append(row)
                previous[argument_id] = current
                all_alerts.extend({"window_id": window_id, **alert} for alert in alerts)
            ranked = sorted(rows, key=lambda row: (-row["risk_score"], row["argument_id"]))
            for rank, row in enumerate(ranked, 1):
                row["priority_rank"] = rank
                row["priority_explanation"] = priority_explanation(
                    row["argument_id"], rank, row["risk_score"]
                )
                history[row["argument_id"]].append({
                    "window_id": window_id,
                    "H_l": self.data["timeline"][0]["date_start"],
                    "H_u": timeline["date_end"],
                    "conflict": row["conflict_score"],
                    "steering": row["steering_score"],
                    "risk": row["risk_score"],
                    "risk_band": row["risk_band"],
                    "assessment_quality": row["assessment_quality"]["category"],
                    "rank": rank,
                })
            by_window[window_id] = {
                "window_id": window_id,
                "H_l": self.data["timeline"][0]["date_start"],
                "H_u": timeline["date_end"],
                "timestamp_label": timeline["label"],
                "monitored_argument_count": len(ranked),
                "high_risk_count": sum(row["risk_band"] == "HIGH" for row in ranked),
                "high_conflict_count": sum(
                    row["conflict_score"] >= self.config.risk.high_conflict_threshold for row in ranked
                ),
                "high_steering_count": sum(
                    row["steering_score"] >= self.config.risk.high_steering_threshold for row in ranked
                ),
                "risk_set_X_R": [row["argument_id"] for row in ranked if row["above_risk_threshold"]],
                "ranked_arguments": ranked,
            }
        return {
            "methodology": {
                "scope": "Rank_H(B) chỉ áp dụng trên B(H), là tập con của A_D",
                "conflict_formula": "C(x,H)=max_{k in A_K(H)} Attack*RelationConfidence*Validity*Authority",
                "influence_formula": "I(A,B)=T(A,B)*L(A,B)*P(A,B)",
                "steering_formula": "S(x,H)=sum_{j!=i} I(x,x_j)/max(1,|A_D(H)|-1)",
                "risk_formula": "RS(x,H)=alpha*C(x,H)+beta*S(x,H)+gamma*C(x,H)*S(x,H)",
                "config": {
                    "conflict": self.config.to_dict()["conflict"],
                    "steering": self.config.to_dict()["steering"],
                    "risk": self.config.to_dict()["risk"],
                },
                "thresholds": {
                    "LOW": f"< {self.config.risk.low_threshold}",
                    "MEDIUM": f"[{self.config.risk.low_threshold}, {self.config.risk.medium_threshold})",
                    "MEDIUM_HIGH": f"[{self.config.risk.medium_threshold}, {self.config.risk.high_threshold})",
                    "HIGH": f">= {self.config.risk.high_threshold}",
                    "tau_R": self.config.risk.risk_alert_threshold,
                },
                "limitations": [
                    "Xung đột chỉ tính quan hệ tấn công có hướng chính tắc và tường minh; không tự tạo mâu thuẫn từ văn bản.",
                    "Định hướng là chỉ báo bằng chứng liên kết, không phải ảnh hưởng hay tiếp xúc nhân quả đã được chứng minh.",
                    "Rủi ro là đường cơ sở có thể cấu hình để ưu tiên rà soát, không phải mức độ gây hại thực tế.",
                    "k chỉ được dùng làm bằng chứng mô phỏng; H là thời gian thực theo ngày.",
                ],
            },
            "by_window": by_window,
            "argument_history": history,
            "alerts": all_alerts,
        }
