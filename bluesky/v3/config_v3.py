from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace

from bluesky.v2.config import DEFAULT_CONFIG, ReasoningWeights, SimulationConfig


@dataclass(frozen=True)
class SemanticsConfig:
    damping: float = 0.35
    convergence_epsilon: float = 0.0001
    max_iterations: int = 40
    accepted_threshold: float = 0.62
    rejected_threshold: float = 0.38


@dataclass(frozen=True)
class ViewpointDynamicsConfig:
    split_candidate_threshold: float = 0.45
    merge_candidate_threshold: float = 0.68
    stabilization_threshold: float = 0.72
    persistent_steps: int = 2
    enable_runtime_split_merge: bool = False


@dataclass(frozen=True)
class DynamicsConfig:
    persistent_conflict_steps: int = 2
    confidence_gap_threshold: float = 0.08
    consensus_threshold: float = 0.72
    fragmentation_threshold: float = 0.25


@dataclass(frozen=True)
class AblationConfig:
    source_quality: bool = True
    relation_confidence: bool = True
    observed_action_effects: bool = True
    institutional_policy: bool = True
    viewpoint_dynamics: bool = True


@dataclass(frozen=True)
class V3Config:
    v2: SimulationConfig = field(default_factory=lambda: DEFAULT_CONFIG)
    semantics: SemanticsConfig = field(default_factory=SemanticsConfig)
    semantic_revision_blend: float = 0.35
    viewpoint_dynamics: ViewpointDynamicsConfig = field(default_factory=ViewpointDynamicsConfig)
    dynamics: DynamicsConfig = field(default_factory=DynamicsConfig)
    ablations: AblationConfig = field(default_factory=AblationConfig)

    def effective_v2_config(self) -> SimulationConfig:
        reasoning: ReasoningWeights = self.v2.reasoning
        if not self.ablations.source_quality:
            reasoning = replace(reasoning, evidence_quality=0.0)
        if not self.ablations.relation_confidence:
            reasoning = replace(
                reasoning,
                relation_confidence={key: 1.0 for key in reasoning.relation_confidence},
            )
        if not self.ablations.observed_action_effects:
            reasoning = replace(
                reasoning,
                observed_support_action=0.0,
                observed_attack_action=0.0,
                observed_challenge_action=0.0,
                observed_evidence_action=0.0,
            )
        return replace(self.v2, reasoning=reasoning)

    def to_dict(self) -> dict:
        return asdict(self)


DEFAULT_V3_CONFIG = V3Config()
