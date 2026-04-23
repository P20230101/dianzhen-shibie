# Branch Mapping

Rules:
- One task per row.
- `Dispatch Branch` must stay `dispatch/tasks`.
- `Integration Method` must be `rebase --onto` or `cherry-pick`.
- `Status` must match the task state on the board.

| Task ID | Title | Dispatch Branch | Dev Branch | Integration Method | Status |
|---|---|---|---|---|---|
| TASK-027 | Figure understanding unit record implementation | dispatch/tasks | codex/task-027-figure-unit-record | rebase --onto | Doing |
| TASK-026 | JMRT 2021 radial hybrid sample expansion | dispatch/tasks | codex/task-026-jmrt-radial-hybrid | rebase --onto | Done |
| TASK-025 | High-density honeycomb sample expansion | dispatch/tasks | codex/task-025-extract-high-density-honeycomb | rebase --onto | Done |
| TASK-024 | Octagonal lattice sample expansion | dispatch/tasks | feat/task-024-extract-matdes-2018-octagonal | rebase --onto | Done |
| TASK-023 | BCC lattice sample expansion | dispatch/tasks | feat/task-023-extract-matdes-2019-bcc | rebase --onto | Done |
| TASK-022 | Hybrid plate-rod lattice sample expansion | dispatch/tasks | feat/task-022-extract-hprl | rebase --onto | Done |
| TASK-021 | Octet truss lattice sample expansion | dispatch/tasks | feat/task-021-extract-octet | rebase --onto | Done |
| TASK-020 | BCCz+cross sample expansion | dispatch/tasks | feat/task-020-extract-bccz-cross | rebase --onto | Done |
| TASK-001 | P1 first minimal chain | dispatch/tasks | feat/task-001-min-pipeline | rebase --onto | Done |
| TASK-002 | Excel input adapter for seed intake | dispatch/tasks | feat/task-002-input-excel | rebase --onto | Done |
| TASK-003 | PDF first-pass register extractor | dispatch/tasks | feat/task-003-input-pdf | rebase --onto | Done |
| TASK-004 | PDF subtype enrichment and register sync | dispatch/tasks | feat/task-004-extract-subtypes | rebase --onto | Done |
| TASK-005 | PDF intake manifest adapter | dispatch/tasks | feat/task-005-input-pdf-intake | rebase --onto | Done |
| TASK-006 | Retrieval corpus from canonical PDF library | dispatch/tasks | feat/task-006-retrieval-corpus | rebase --onto | Done |
| TASK-007 | Retrieval query ranking and candidate export | dispatch/tasks | feat/task-007-extract-query | rebase --onto | Done |
| TASK-008 | Lightweight KG projection from validated sample/evidence | dispatch/tasks | feat/task-008-export-kg | rebase --onto | Done |
| TASK-009 | External retrieval KG smoke verification | dispatch/tasks | feat/task-009-smoke-retrieval-kg | rebase --onto | Done |
| TASK-010 | P1 sample review promotion and KG population | dispatch/tasks | feat/task-010-review-approval | rebase --onto | Done |
| TASK-011 | PDF sample expansion from the library | dispatch/tasks | feat/task-011-extract-paper-sample | rebase --onto | Done |
| TASK-012 | AddMA gyroid sample expansion | dispatch/tasks | feat/task-012-addma-gyroid-sample | rebase --onto | Done |
| TASK-013 | Petal-shaped honeycomb sample expansion | dispatch/tasks | feat/task-013-extract-psh-honeycomb | rebase --onto | Done |
| TASK-014 | Star auxetic honeycomb sample expansion | dispatch/tasks | feat/task-014-extract-star-auxetic | rebase --onto | Done |
| TASK-015 | Vertex-based hierarchical honeycomb sample expansion | dispatch/tasks | feat/task-015-extract-hierarchical-honeycomb | rebase --onto | Done |
| TASK-016 | 3D printed hierarchical honeycomb sample expansion | dispatch/tasks | feat/task-016-extract-matdes-hierarchical | rebase --onto | Done |
| TASK-017 | Bio-inspired hierarchical honeycomb sample expansion | dispatch/tasks | feat/task-017-extract-bioinspired-hierarchical | rebase --onto | Done |
| TASK-018 | Bio-inspired spatial lattice sample expansion | dispatch/tasks | feat/task-018-extract-bioinspired-spatial-lattice | rebase --onto | Done |
| TASK-019 | 3D metamaterial sample expansion | dispatch/tasks | feat/task-019-extract-engstruct-metamaterial | rebase --onto | Done |

## Split Notes

- `TASK-002` owns the P1 workbook seed, transform, and validation chain.
- `TASK-003` and `TASK-004` share the register extractor, but `TASK-004` extends it to the canonical register outputs.
- `TASK-006` and `TASK-007` share `scripts/retrieval_kg_common.py`.
- `TASK-008`, `TASK-009`, and `TASK-010` sit on top of the KG projection layer, with `TASK-010` reusing `scripts/project_knowledge_graph.py` after promoting the review state.
- `TASK-011` starts from the PDF library and extends the existing promotion and KG path with one additional paper-derived sample bundle.
- `TASK-012` extends `TASK-011` with a second paper-derived sample bundle and reuses the same promotion and KG path.
- `TASK-013` extends `TASK-012` with a PSH honeycomb bundle and reuses the same promotion and KG path.
- `TASK-014` extends `TASK-013` with a star auxetic honeycomb bundle and reuses the same promotion and KG path.
- `TASK-015` extends `TASK-014` with a vertex-based hierarchical honeycomb bundle and reuses the same promotion and KG path.
- `TASK-016` extends `TASK-015` with a 3D printed hierarchical honeycomb bundle and reuses the same promotion and KG path.
- `TASK-017` extends `TASK-016` with a bio-inspired hierarchical honeycomb bundle and reuses the same promotion and KG path.
- `TASK-018` extends `TASK-017` with the bio-inspired spatial lattice bundle and reuses the same promotion and KG path.
- `TASK-019` extends `TASK-018` with the EngStruct 2023 3D metamaterial bundle and reuses the same promotion and KG path.
- `TASK-020` extends `TASK-019` with the BCCz+cross lattice bundle and reuses the same promotion and KG path.
- `TASK-021` extends `TASK-020` with an Octet truss lattice bundle and reuses the same promotion and KG path.
- `TASK-022` extends `TASK-021` with a hybrid plate-rod lattice bundle and reuses the same promotion and KG path.
- `TASK-023` extends `TASK-022` with a BCC lattice bundle and reuses the same promotion and KG path.
- `TASK-024` extends `TASK-023` with an Octagonal lattice bundle and reuses the same promotion and KG path.
- `TASK-025` extends `TASK-024` with a high-density honeycomb bundle and reuses the same promotion and KG path.
- `TASK-026` extends `TASK-025` with a radial hybrid TPMS bundle and reuses the same promotion and KG path.
- `TASK-027` extends the standalone figure-understanding layer with unit-level crops, records, and report cards.
