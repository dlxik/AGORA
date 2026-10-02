# AGORA

AGORA (Argument Graphs over Official and Real-world Assertions) is a long-term research project on temporal argumentation over evolving public claims and authoritative information.

The master case concerns public and official discussions related to the THPT Chuyen Tuyen Quang case (CTQ). Household business taxation is the validation case.

## Current phase

The repository is in its initial setup phase. Research data has not yet been collected or annotated.

Current work is limited to data preparation and temporal representation. Solver code, ASP encodings, and multi-agent implementations are out of scope at this stage.

## Repository organization

- `docs/`: research framing, methodology, and architecture documentation.
- `data/raw/`: source material preserved by case.
- `data/sources/`: source inventories and metadata.
- `data/timelines/`: information-availability timelines.
- `data/annotations/`: manual argument, status, and relation annotations.
- `data/processed/`: derived data suitable for later analysis.
- `graphs/`: temporal graph snapshots and visualizations.
- `notes/`: status, decisions, uncertainties, and source-review records.

The repository is organized by project function rather than by calendar week.

## Research constraints

- Every material factual claim must remain traceable to a source identifier.
- Publication dates and source authority must not be guessed.
- Later information must not be projected backward into earlier timeline states.
- Argument status is time-dependent.
- Agents may support monitoring, extraction, grounding, and explanation, but do not replace the symbolic reasoning core.

