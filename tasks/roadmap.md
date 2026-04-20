# Project Roadmap

## Current Position

- `NOW: P0 / M0`
- `Milestone Date: 2026-04-21`
- `Milestone Name: M0 可控开发启动验收`
- `Acceptance Focus: establish a controllable development start, not a final product release`

| Phase | Goal | What Must Be Ready | Exit Signal | Branch Policy |
|---|---|---|---|---|
| `P0 / M0` | Establish controllable development state | dispatch workflow, schema and mapping contract, overview docs, branch policy | `2026-04-21` M0 accepted | Governance stays on `dispatch/tasks` |
| `P1` | Run the first minimal end-to-end chain | input entry, parsed layer, extracted output, sample and evidence alignment, minimal review or export closure | the first real task runs through one execution branch | Keep the package on the same execution branch |
| `P2` | Expand capabilities in parallel | stable interfaces inherited from `P1` | modular packages can move without conflicting writes | New execution branches allowed by package |
| `P3` | Integrate and package deliverables | stabilized outputs from `P2` | integration-ready deliverable set exists | Use an isolated integration branch |

## Phase Priorities

### `P0 / M0`

- Project goal and boundary are clear
- Dispatch workflow is operational
- Schema and mapping contract are stable enough for execution planning
- Next execution packages are visible

### `P1`

- The first minimal chain is runnable
- Core interfaces are no longer drifting

### `P2`

- Input adapters, extraction modules, review helpers, and export outputs can split safely

### `P3`

- Parallel outputs are collected into a stable delivery set
