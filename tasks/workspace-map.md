# Workspace Task Map

## Snapshot

- Dispatch branch: `dispatch/tasks`
- Dispatch head: `b5c16a4`
- Current dev branch: `feat/task-010-review-approval`
- No `TASK-011` is opened.

## Mapping

| Task | Primary implementation files | Tests | Generated artifacts | Current branch state |
|---|---|---|---|---|
| TASK-002 | `scripts/p1_seed.py`, `scripts/p1_transform.py`, `scripts/p1_validate_export.py`, `scripts/p1_pipeline_common.py` | `tests/test_p1_workbook_seed_adapter.py` | `data/p1/seed_input.json`, `outputs/p1/seed/seed_input.json`, `outputs/p1/parsed/parsed_sample.json`, `outputs/p1/extracted/samples_v1.json`, `outputs/p1/extracted/evidence_v1.json`, `outputs/p1/review/p1_chain_report.json` | Committed; `feat/task-002-input-excel` now points at `3b7b702` and contains the P1 workbook seed chain. |
| TASK-003 | `scripts/build_pdf_register.py`, `tests/test_pdf_register_extractor.py` | `tests/test_pdf_register_extractor.py` | `data/01_raw/pdfs/paper_register_first_pass.csv`, `data/01_raw/pdfs/paper_register_first_pass.md` | Workspace-only; no committed branch head carries the current extractor implementation yet. |
| TASK-004 | `scripts/build_pdf_register.py`, `tests/test_pdf_register_extractor.py` | `tests/test_pdf_register_extractor.py` | `data/01_raw/pdfs/paper_register.csv`, `data/01_raw/pdfs/paper_register.md` | Workspace-only; this is the canonical-register extension of the same extractor used by `TASK-003`. |
| TASK-005 | `scripts/build_pdf_intake_manifest.py` | `tests/test_pdf_intake_manifest.py` | `data/02_parsed/pdf_intake_manifest.json` | Workspace-only; `feat/task-005-input-pdf-intake` still points at `c16d956` and does not contain the manifest adapter. |
| TASK-006 | `scripts/build_retrieval_corpus.py`, `scripts/retrieval_kg_common.py` | `tests/test_build_retrieval_corpus.py` | `data/02_retrieval/corpus.jsonl`, `data/02_retrieval/corpus_manifest.json` | Committed; `feat/task-006-retrieval-corpus` now contains the retrieval corpus build and helper layer. |
| TASK-007 | `scripts/query_retrieval.py`, `scripts/retrieval_kg_common.py` | `tests/test_query_retrieval.py` | `outputs/retrieval/candidates.json` | Committed; `feat/task-007-extract-query` now contains the retrieval ranking and candidate export. |
| TASK-008 | `scripts/project_knowledge_graph.py`, `scripts/retrieval_kg_common.py` | `tests/test_retrieval_kg_common.py`, `tests/test_project_knowledge_graph.py` | `outputs/kg/knowledge_graph.json` | Committed; `feat/task-008-export-kg` now contains the KG projection from validated sample and evidence data. |
| TASK-009 | `tests/test_external_retrieval_kg_smoke.py` | `tests/test_external_retrieval_kg_smoke.py` | Smoke fixtures only under `tests/fixtures/external_retrieval_kg/` | Committed; `feat/task-009-smoke-retrieval-kg` now contains the smoke coverage for retrieval and KG. |
| TASK-010 | `scripts/promote_p1_review.py`, `tests/test_promote_p1_review.py`, `scripts/project_knowledge_graph.py` | `tests/test_promote_p1_review.py`, `tests/test_project_knowledge_graph.py`, `tests/test_external_retrieval_kg_smoke.py` | `outputs/p1/extracted/samples_v1.json`, `outputs/p1/extracted/evidence_v1.json`, `outputs/kg/knowledge_graph.json` | Workspace-only; the mixed workspace still holds the implementation files untracked. |

## Split Notes

- `TASK-002` owns the P1 workbook seed, transform, and validation chain.
- `TASK-003` and `TASK-004` share the register extractor, but `TASK-004` extends it to the canonical register outputs.
- `TASK-006` and `TASK-007` share `scripts/retrieval_kg_common.py`.
- `TASK-008`, `TASK-009`, and `TASK-010` sit on top of the KG projection layer, with `TASK-010` reusing `scripts/project_knowledge_graph.py` after promoting the review state.
- `TASK-011` is intentionally absent.
