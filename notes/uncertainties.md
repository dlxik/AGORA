# Uncertainties

## U-001: Data serialization format

- Status: open
- Question: Should source, timeline, argument, status, and relation records use CSV, JSON, JSONL, YAML, or a combination?
- Impact: Determines schema files, validation tooling, and handling of list-valued fields.

## U-002: Identifier conventions

- Status: open
- Question: What exact formats should be used for `source_id`, `timestamp_id`, `arg_id`, and `relation_id`?
- Impact: Affects cross-file references and long-term stability.

## U-003: Source preservation policy

- Status: open
- Question: Which source types should be archived locally, and what metadata such as access time or checksum is required?
- Impact: Affects reproducibility, copyright handling, privacy, and resilience to link disappearance.

## U-004: Git baseline workflow

- Status: resolved
- Resolution: The directory was initialized as a new Git repository with `main` as the default branch and `https://github.com/dlxik/AGORA.git` as `origin`.
- Impact: Component branches can now be created from the reviewed setup baseline.
