# Task Card

- Task ID: `TASK-007`
- Title: `Retrieval query ranking and candidate export`
- Goal: `Rank retrieval corpus chunks for a query and export the top candidates as JSON.`
- Dispatch Branch: `dispatch/tasks`
- Dev Branch: `feat/task-007-extract-query`
- Integration Method: `rebase --onto`
- Dependencies: `TASK-006 complete; canonical retrieval corpus available`

## Acceptance Criteria
- `scripts/query_retrieval.py` ranks corpus chunks from a query payload.
- `outputs/retrieval/candidates.json` is written by the CLI.
- Fixture tests cover the ranking order and export shape.

## Verification
- `python -m pytest -q tests/test_query_retrieval.py tests/test_retrieval_kg_common.py` -> passed
- `python scripts/query_retrieval.py --corpus data/02_retrieval/corpus.jsonl --query tests/fixtures/external_retrieval_kg/mini_query.json --out outputs/retrieval/candidates.json` -> wrote `outputs/retrieval/candidates.json`

## Status Log
Append one line for every state change. Minimum lifecycle entries: `Created`, `Started`, `Blocked` (if any), `Resumed` (if any), `Done`, and `Archived`.
- `2026-04-20 20:58 | Created on dispatch/tasks`
- `2026-04-20 21:04 | Started on feat/task-007-extract-query`
- `2026-04-20 21:04 | Done | query ranking and export verified`
- `2026-04-20 21:04 | Archived to tasks/archive/`
