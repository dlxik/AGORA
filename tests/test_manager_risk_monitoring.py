from __future__ import annotations

import unittest
from dataclasses import replace

from bluesky.src.loader import load_ctq_data
from bluesky.src.temporal_graph import build_temporal_snapshots
from bluesky.src.viewpoint import add_viewpoint_layers
from bluesky.v3.config_v3 import DEFAULT_V3_CONFIG
from bluesky.v3.conflict import ConflictEvaluator
from bluesky.v3.risk import RiskEvaluator
from bluesky.v3.simulation_v3 import DynamicSocietySimulation
from bluesky.v3.steering import SteeringEvaluator
from bluesky.v3.visualizer_v3 import HTML


class ManagerRiskMonitoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = load_ctq_data()
        cls.snapshots = build_temporal_snapshots(cls.data)
        add_viewpoint_layers(cls.snapshots, cls.data["viewpoint_mapping"])
        cls.trace = DynamicSocietySimulation(cls.data, cls.snapshots).run()
        cls.conflict = ConflictEvaluator(cls.data, cls.snapshots, DEFAULT_V3_CONFIG.conflict)
        cls.steering = SteeringEvaluator(
            cls.data, cls.snapshots, cls.trace, DEFAULT_V3_CONFIG.steering
        )

    def test_conflict_uses_max_pair_and_preserves_provenance(self) -> None:
        result = self.conflict.evaluate("CTQ-A012", 0, 3)
        scores = [row["score"] for row in result["pairwise_conflicts"]]
        self.assertEqual(max(scores), result["conflict_score"])
        self.assertEqual("CTQ-A015", result["maximizing_reference_argument_id"])
        self.assertEqual(["CTQ-R025"], result["maximizing_pair"]["relation_ids"])
        self.assertTrue(result["maximizing_pair"]["source_ids"])

    def test_conflict_does_not_fabricate_attack(self) -> None:
        result = self.conflict.evaluate("CTQ-A002", 0, 5)
        self.assertEqual(0.0, result["conflict_score"])
        self.assertIsNone(result["maximizing_pair"])
        self.assertTrue(all(row["attack"] == 0 for row in result["pairwise_conflicts"]))

    def test_conflict_only_uses_reference_arguments_available_in_h(self) -> None:
        result = self.conflict.evaluate("CTQ-A002", 0, 0)
        selected = {row["final_arg_id"]: row for row in self.data["selected"]}
        rank = {row["timestamp_id"]: index for index, row in enumerate(self.data["timeline"])}
        self.assertTrue(all(
            selected[row["reference_argument_id"]]["arg_type"] == "A_K"
            and rank[selected[row["reference_argument_id"]]["introduced_at"]] <= 0
            for row in result["pairwise_conflicts"]
        ))

    def test_conflict_is_bounded_and_deterministic(self) -> None:
        first = self.conflict.evaluate("CTQ-A011", 0, 5)
        second = self.conflict.evaluate("CTQ-A011", 0, 5)
        self.assertEqual(first, second)
        self.assertGreaterEqual(first["conflict_score"], 0.0)
        self.assertLessEqual(first["conflict_score"], 1.0)

    def test_temporal_order_and_no_future_to_past_influence(self) -> None:
        selected = {row["final_arg_id"]: row for row in self.data["selected"] if row["arg_type"] == "A_D"}
        earlier = min(selected, key=lambda key: selected[key]["introduced_at"])
        later = max(selected, key=lambda key: selected[key]["introduced_at"])
        self.assertEqual(1.0, self.steering.pairwise(earlier, later, 0, 5)["T"])
        reverse = self.steering.pairwise(later, earlier, 0, 5)
        self.assertEqual(0.0, reverse["T"])
        self.assertEqual(0.0, reverse["I"])
        same_time = [key for key, row in selected.items() if row["introduced_at"] == "t1"]
        self.assertGreaterEqual(len(same_time), 2)
        self.assertEqual(0.0, self.steering.pairwise(same_time[0], same_time[1], 0, 5)["T"])

    def test_pairwise_influence_formula_bounds_and_provenance(self) -> None:
        pair = self.steering.pairwise("CTQ-A004", "CTQ-A006", 0, 5)
        self.assertAlmostEqual(pair["T"] * pair["L"] * pair["P"], pair["I"], places=4)
        self.assertGreaterEqual(pair["L"], 0.0)
        self.assertLessEqual(pair["L"], 1.0)
        self.assertGreaterEqual(pair["P"], 0.0)
        self.assertLessEqual(pair["P"], 1.0)
        self.assertIn("relation_ids", pair)
        self.assertIn("interaction_ids", pair)
        self.assertIn("revision_ids", pair)
        self.assertEqual(pair, self.steering.pairwise("CTQ-A004", "CTQ-A006", 0, 5))

    def test_steering_is_normalized_pairwise_sum(self) -> None:
        result = self.steering.evaluate("CTQ-A004", 0, 5)
        expected = round(
            sum(row["I"] for row in result["pairwise_influence"]) / result["denominator"], 4
        )
        self.assertEqual(expected, result["steering_score"])
        self.assertGreaterEqual(result["steering_score"], 0.0)
        self.assertLessEqual(result["steering_score"], 1.0)
        self.assertIn("interaction_ids", result)
        self.assertIn("revision_ids", result)

    def test_risk_formula_config_and_bands(self) -> None:
        evaluator = RiskEvaluator(DEFAULT_V3_CONFIG.risk)
        conflict = {"conflict_score": 0.8, "maximizing_pair": {"relation_ids": ["R"]}}
        steering = {"steering_score": 0.4, "pairwise_influence": [{"evidence_level": "MEDIUM"}]}
        result = evaluator.evaluate("X", conflict, steering)
        expected = round(0.5 * 0.8 + 0.2 * 0.4 + 0.3 * 0.8 * 0.4, 4)
        self.assertEqual(expected, result["risk_score"])
        changed = RiskEvaluator(replace(DEFAULT_V3_CONFIG.risk, alpha=0.2)).evaluate("X", conflict, steering)
        self.assertNotEqual(result["risk_score"], changed["risk_score"])
        self.assertEqual("LOW", evaluator.band(0.29))
        self.assertEqual("MEDIUM", evaluator.band(0.30))
        self.assertEqual("MEDIUM_HIGH", evaluator.band(0.50))
        self.assertEqual("HIGH", evaluator.band(0.70))

    def test_ranking_contains_only_ad_and_stable_ties(self) -> None:
        selected_types = {row["final_arg_id"]: row["arg_type"] for row in self.data["selected"]}
        for window in self.trace["risk_monitoring"]["by_window"].values():
            rows = window["ranked_arguments"]
            self.assertTrue(all(selected_types[row["argument_id"]] == "A_D" for row in rows))
            self.assertEqual(
                rows,
                sorted(rows, key=lambda row: (-row["risk_score"], row["argument_id"])),
            )

    def test_trace_and_ui_expose_manager_view_without_removing_v3(self) -> None:
        self.assertIn("risk_monitoring", self.trace)
        self.assertIn("Agent Society", HTML)
        self.assertIn("Risk Monitoring", HTML)
        self.assertIn("function inspectInSociety", HTML)
        for label in ("Lập luận", "Hoạt động", "Xã hội", "Sự kiện", "Chỉ số"):
            self.assertIn(label, HTML)

    def test_displayed_formula_uses_serialized_config(self) -> None:
        methodology = self.trace["risk_monitoring"]["methodology"]
        risk_config = methodology["config"]["risk"]
        self.assertEqual(DEFAULT_V3_CONFIG.risk.alpha, risk_config["alpha"])
        self.assertEqual(DEFAULT_V3_CONFIG.risk.beta, risk_config["beta"])
        self.assertEqual(DEFAULT_V3_CONFIG.risk.gamma, risk_config["gamma"])
        self.assertIn("coeff.alpha", HTML)
        self.assertIn("coeff.beta", HTML)
        self.assertIn("coeff.gamma", HTML)


if __name__ == "__main__":
    unittest.main()
