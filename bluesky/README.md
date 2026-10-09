# AGORA Blue Sky: Agentic Public Deliberation

## Core idea

Today, public arguments are usually treated as passive data to be classified, clustered, or connected in an argument graph.

This prototype explores a different abstraction:

> What if collective viewpoints themselves became autonomous, stateful agents whose behavior is grounded in explicit argument structures?

The conceptual transition is:

`Arguments -> Viewpoint Clusters -> Viewpoint Agents -> Interaction -> Emergent Opinion Dynamics`

## Agent model

A viewpoint agent contains:

- **beliefs**: explicit arguments represented by the agent;
- **evidence**: evidence currently available to the agent;
- **position**: its current stance on the issue, represented in the demo on `[-1, 1]`;
- **strength**: the current prominence/prevalence of the viewpoint on `[0, 1]`.

The demo contains three collective viewpoint agents and one institutional information agent.

Personal/organizational agents are part of the longer-term vision and are intentionally not implemented here.

## Interaction model

The proof-of-concept supports:

- `present_argument`
- `support`
- `attack`
- `challenge`
- `provide_evidence`

Interactions modify observable agent state. The rules are deliberately deterministic so every change can be traced back to an explicit interaction.

## Running

From the repository root:

```bash
python -m bluesky.demo
```

This prints the state after each round and generates:

`bluesky/outputs/demo.html`

Open that file in a browser to inspect the round-by-round viewpoint society and interaction trace.

## What the demo demonstrates

The initial state contains competing and uncertain viewpoints. During the simulation:

1. public viewpoint agents support and challenge one another;
2. an institutional agent contributes new evidence;
3. the uncertain viewpoint revises its position;
4. a challenged viewpoint changes both position and strength;
5. the system records the resulting dynamics across rounds.

The argument texts are intentionally illustrative CTQ-inspired placeholders. They are not asserted as factual claims about the real case.

## Relation to the main AGORA research core

The main AGORA research direction remains argument-centered: extracting, representing, relating, weighting, and explaining conflicting arguments.

This Blue Sky branch extends that representation one conceptual step further:

`Argument graph -> Viewpoint agents -> Multi-agent interaction -> Emergent dynamics`

The agent layer is therefore an extension of the argumentation core, not a replacement for it.

## Research questions suggested by the prototype

1. How can collective viewpoints be represented as autonomous agents while preserving their underlying argument structure?
2. How can argument structures serve as an internal reasoning substrate for belief and position revision?
3. How should viewpoint agents support, attack, challenge, and exchange evidence with one another?
4. What collective opinion dynamics can emerge from these interactions?
5. How can institutional agents participate without turning the environment into centralized opinion control?

## Next iteration

Possible next steps are automatic viewpoint clustering, richer belief revision, temporal argument graphs, configurable interaction protocols, and a more interactive visualization.
