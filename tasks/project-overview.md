# Project Overview

## One-Sentence Goal

Build a controlled lattice crashworthiness literature database that turns paper evidence into normalized sample-level data.

## Scope Note

This page describes the current execution and governance target for the repository. It does not replace the product-level goal defined by:

- `点阵吸能文献数据库实施方案_纳入Excel原型.md`
- `最小系统实现方案.md`
- `数据库清洗与字段标准化方案.md`
- `Lattice crashworthiness data.xlsx`

Those files define the product main line. This page only tracks how the repository is being organized right now to support that main line.

## Current Phase

- `P3 / closeout phase`
- `Nearest Milestone: 2026-04-23 | P3 closeout active`

## What The Project Is Doing Now

- Integrating the current sample-expansion results into the closed repository state
- Reconciling the phase-facing documentation so P3 reads as a closeout state
- Freezing the current output set and avoiding new sample-expansion tasks

## In Scope Now

- Closeout reconciliation of the sample-expansion line
- Final verification that all completed tasks remain closed
- Repository governance and dispatch workflow
- Task decomposition and branch policy

## Not In Scope Now

- New sample bundles
- New extraction targets
- New execution branches for the closed line
- Reopening completed tasks

## Current Deliverables

- `scripts/build_pdf_sample_bundle.py`
- `scripts/promote_p1_review.py`
- `scripts/project_knowledge_graph.py`
- `tests/test_build_pdf_sample_bundle.py`
- `tests/test_promote_p1_review.py`
- `tests/test_project_knowledge_graph.py`
- `outputs/p1/extracted/samples_v1.json`
- `outputs/p1/extracted/evidence_v1.json`
- `outputs/kg/knowledge_graph.json`
- `schemas/samples/schema_v1.json`
- `schemas/evidence/schema_v1.json`
- `mappings/structure/structure_mapping.csv`
- `mappings/material/material_mapping.csv`
- `mappings/process/process_mapping.csv`
- `tasks/workflow.md`
- `tasks/rules.md`
- `tasks/templates/task-template.md`

## Next Actions

1. Keep `dispatch/tasks` aligned with the closed state.
2. Do not open any new sample-expansion task from the finished run.
