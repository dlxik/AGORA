from copy import deepcopy
from typing import Dict, List, Tuple
from .interaction import Interaction, apply_interaction
from .models import Argument, ViewpointAgent


def build_demo_agents() -> Dict[str, ViewpointAgent]:
    # The texts below are intentionally illustrative, CTQ-inspired placeholders.
    # They are not asserted as factual claims about the real case.
    a1 = Argument("A1", "Wait for verified information before drawing a conclusion.", "public")
    a2 = Argument("A2", "The available process raises concerns that deserve scrutiny.", "public")
    a3 = Argument("A3", "Current evidence is incomplete, so confidence should remain limited.", "public")
    a4 = Argument("A4", "A newly released official clarification provides additional evidence.", "institutional")

    return {
        "V1": ViewpointAgent(
            "V1", "Verification-first viewpoint", "collective", [a1],
            position=0.25, strength=0.40
        ),
        "V2": ViewpointAgent(
            "V2", "Procedural-concern viewpoint", "collective", [a2],
            position=-0.55, strength=0.55
        ),
        "V3": ViewpointAgent(
            "V3", "Uncertain / wait-for-evidence viewpoint", "collective", [a3],
            position=0.00, strength=0.35
        ),
        "I1": ViewpointAgent(
            "I1", "Institutional information agent", "institutional", [a4],
            position=0.65, strength=0.70
        ),
    }


def build_demo_events() -> List[Interaction]:
    return [
        Interaction(
            1, "V2", "V1", "attack",
            "Challenges the confidence of the verification-first viewpoint.",
            position_delta=-0.05, strength_delta=0.02,
        ),
        Interaction(
            1, "V1", "V3", "support",
            "Supports delaying judgment until evidence is verified.",
            position_delta=0.08, strength_delta=0.03,
        ),
        Interaction(
            2, "I1", "V3", "provide_evidence",
            "Adds an official clarification as new evidence.",
            position_delta=0.35, strength_delta=0.10,
        ),
        Interaction(
            2, "I1", "V2", "challenge",
            "Challenges part of the procedural-concern viewpoint with new evidence.",
            position_delta=0.20, strength_delta=-0.08,
        ),
        Interaction(
            3, "V3", "V2", "support",
            "After revision, V3 still supports keeping unresolved concerns visible.",
            position_delta=0.05, strength_delta=0.02,
        ),
    ]


def run_simulation() -> Tuple[List[dict], List[Interaction]]:
    agents = build_demo_agents()
    events = build_demo_events()
    snapshots = []

    def snapshot(round_id: int, label: str) -> None:
        snapshots.append({
            "round": round_id,
            "label": label,
            "agents": deepcopy(agents),
        })

    snapshot(0, "Initial viewpoint society")

    current_round = None
    for event in events:
        if current_round is None:
            current_round = event.round_id
        if event.round_id != current_round:
            snapshot(current_round, f"After round {current_round}")
            current_round = event.round_id
        apply_interaction(agents, event)

    if current_round is not None:
        snapshot(current_round, f"After round {current_round}")

    return snapshots, events
