# Task Card

- Task ID: `TASK-006`
- Title: `Retrieval corpus from canonical PDF library`
- Goal: `Materialize the canonical retrieval corpus and manifest from the existing PDF library.`
- Dispatch Branch: `dispatch/tasks`
- Dev Branch: `feat/task-006-retrieval-corpus`
- Integration Method: `rebase --onto`
- Dependencies: `TASK-005 complete; canonical PDF register and library already available`

## Acceptance Criteria
- `data/02_retrieval/corpus.jsonl` exists and contains non-empty retrieval chunks.
- `data/02_retrieval/corpus_manifest.json` exists and reports nonzero paper and chunk counts.
- Retrieval fixture tests pass against the shared corpus utilities.

## Verification
- `python -m pytest -q tests/test_retrieval_kg_common.py tests/test_build_retrieval_corpus.py` -> passed
- `python scripts/build_retrieval_corpus.py --register data/01_raw/pdfs/paper_register.csv --library data/01_raw/pdfs/library --out data/02_retrieval/corpus.jsonl --manifest data/02_retrieval/corpus_manifest.json` -> wrote `data/02_retrieval/corpus.jsonl` with 4,432 chunks across 17 papers and `data/02_retrieval/corpus_manifest.json`

## Status Log
Append one line for every state change. Minimum lifecycle entries: `Created`, `Started`, `Blocked` (if any), `Resumed` (if any), `Done`, and `Archived`.
- `2026-04-20 20:36 | Created on dispatch/tasks`
- `2026-04-20 20:39 | Started on feat/task-006-retrieval-corpus`
- `2026-04-20 20:54 | Done | 17 papers | 4,432 chunks`
- `2026-04-20 20:54 | Archived to tasks/archive/`
