# Methodology

## Current workflow

1. Collect and verify a source pool for each case.
2. Identify meaningful information-state timestamps without daily over-segmentation.
3. Represent arguments as premises, rules, and conclusions with source and temporal provenance.
4. Record time-dependent argument status separately from the argument definition.
5. Add support or attack relations only when their conflict or support basis is explainable.
6. Construct temporal graph snapshots from information available at each timestamp.
7. Validate the representation on a small second case.

## Audit principles

- Do not invent sources, quotations, dates, decisions, or rules.
- Use `null` for unknown values and document the uncertainty.
- Do not use later information to characterize an earlier information state.
- Trace material factual claims and annotations to source identifiers.
- Review argument annotations in batches of no more than five new arguments.

## Current exclusions

Automated reasoning, ASP encoding, agent implementation, and large-scale evaluation are not part of the current phase.

