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

- `P0 / M0: 可控开发启动阶段`
- `Nearest Milestone: 2026-04-21 | M0 可控开发启动验收`

## What The Project Is Doing Now

- Stabilizing the repository governance and dispatch workflow
- Locking the first usable schema and mapping contract
- Preparing the first executable development package and branch policy

## In Scope Now

- Repository governance and dispatch workflow
- Schema and mapping contract
- Task decomposition and branch policy
- Acceptance-ready project overview materials

## Not In Scope Now

- Full paper ingestion pipeline
- Full extraction automation
- Full review tooling
- Final UI or complete product shell

## Current Deliverables

- `schemas/samples/schema_v1.json`
- `schemas/evidence/schema_v1.json`
- `mappings/structure/structure_mapping.csv`
- `mappings/material/material_mapping.csv`
- `mappings/process/process_mapping.csv`
- `tasks/workflow.md`
- `tasks/rules.md`
- `tasks/templates/task-template.md`

## Next Actions

1. Hold new task assignment until `TASK-020` has a unique target and `dispatch/tasks` matches the local implementation state.
