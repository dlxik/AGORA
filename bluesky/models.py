from dataclasses import dataclass, field
from typing import List


@dataclass
class Argument:
    id: str
    text: str
    source: str
    evidence: List[str] = field(default_factory=list)


@dataclass
class ViewpointAgent:
    id: str
    name: str
    kind: str  # "collective" or "institutional"
    beliefs: List[Argument]
    position: float  # -1..1
    strength: float  # 0..1
    evidence: List[str] = field(default_factory=list)

    def clamp(self) -> None:
        self.position = max(-1.0, min(1.0, self.position))
        self.strength = max(0.0, min(1.0, self.strength))
