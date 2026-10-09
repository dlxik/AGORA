from dataclasses import dataclass
from typing import Dict
from .models import ViewpointAgent


@dataclass
class Interaction:
    round_id: int
    source: str
    target: str
    action: str
    argument: str
    position_delta: float = 0.0
    strength_delta: float = 0.0


ALLOWED_ACTIONS = {
    "present_argument",
    "support",
    "attack",
    "challenge",
    "provide_evidence",
}


def apply_interaction(agents: Dict[str, ViewpointAgent], event: Interaction) -> None:
    if event.action not in ALLOWED_ACTIONS:
        raise ValueError(f"Unsupported action: {event.action}")
    if event.source not in agents or event.target not in agents:
        raise KeyError("Interaction references an unknown agent")

    target = agents[event.target]
    target.position += event.position_delta
    target.strength += event.strength_delta

    if event.action == "provide_evidence":
        target.evidence.append(event.argument)

    target.clamp()
