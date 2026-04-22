# Branch Mapping

Rules:
- One task per row.
- `Dispatch Branch` must stay `dispatch/tasks`.
- `Integration Method` must be `rebase --onto` or `cherry-pick`.
- `Status` must match the task state on the board.

| Task ID | Title | Dispatch Branch | Dev Branch | Integration Method | Status |
|---|---|---|---|---|---|
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
