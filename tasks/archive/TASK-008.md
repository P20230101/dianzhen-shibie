# Task Card

- Task ID: `TASK-008`
- Title: `Lightweight KG projection from validated sample/evidence`
- Goal: `Project accepted samples and verified evidence into a lightweight knowledge graph JSON.`
- Dispatch Branch: `dispatch/tasks`
- Dev Branch: `feat/task-008-export-kg`
- Integration Method: `rebase --onto`
- Dependencies: `TASK-007 complete; validated sample and evidence artifacts available`

## Acceptance Criteria
- `scripts/project_knowledge_graph.py` reads validated samples and evidence.
- `outputs/kg/knowledge_graph.json` is written by the CLI.
- Fixture tests cover accepted-sample gating and verified-evidence gating.

## Verification
- `python -m pytest -q tests/test_retrieval_kg_common.py tests/test_project_knowledge_graph.py`
- `python scripts/project_knowledge_graph.py --samples outputs/p1/extracted/samples_v1.json --evidence outputs/p1/extracted/evidence_v1.json --out outputs/kg/knowledge_graph.json`
- `python -m pytest -q tests/test_retrieval_kg_common.py tests/test_project_knowledge_graph.py` -> passed
- `python scripts/project_knowledge_graph.py --samples outputs/p1/extracted/samples_v1.json --evidence outputs/p1/extracted/evidence_v1.json --out outputs/kg/knowledge_graph.json` -> wrote `outputs/kg/knowledge_graph.json`

## Status Log
Append one line for every state change. Minimum lifecycle entries: `Created`, `Started`, `Blocked` (if any), `Resumed` (if any), `Done`, and `Archived`.
- `2026-04-20 21:08 | Created on dispatch/tasks`
- `2026-04-20 21:13 | Started on feat/task-008-export-kg`
- `2026-04-20 21:13 | Done | KG projector and fixture smoke verified`
- `2026-04-20 21:13 | Archived to tasks/archive/`
