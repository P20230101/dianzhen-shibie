# Branch Strategy

## Reading Guide

- `留在 dispatch/tasks` = dispatch-only asset, do not open an execution branch
- `同支线推进` = keep the package in one execution branch until the package is stable
- `可新开支线` = open a new execution branch only after the package-specific preconditions are satisfied

## Current Branch Classes

| Classification | Work Package | Current Rule | Suggested Branch Pattern |
|---|---|---|---|
| `留在 dispatch/tasks` | Project overview, roadmap, branch policy, board, branch map, workflow, templates, rules | Maintain only on `dispatch/tasks` | `N/A` |
| `同支线推进` | Data contract bundle (`schemas/`, `mappings/`, validation boundary) | Keep in one execution branch until the contract is stable | `feat/task-xxx-data-contract` |
| `同支线推进` | First minimal end-to-end chain | Keep in one execution branch until the first chain is truly runnable | `feat/task-xxx-min-pipeline` |
| `可新开支线` | Input adapters | Allowed only after `P1` interfaces are stable | `feat/task-xxx-input-<topic>` |
| `可新开支线` | Extraction enhancements | Allowed only after sample and evidence interfaces are stable | `feat/task-xxx-extract-<topic>` |
| `可新开支线` | Review or cleaning helpers | Allowed only after the review boundary is stable | `feat/task-xxx-review-<topic>` |
| `可新开支线` | Export or delivery outputs | Allowed only after the output contract is stable | `feat/task-xxx-export-<topic>` |

## Do Not Split Yet

- Any work that changes `schemas/` and `mappings/` together
- Any work that defines the first real sample and evidence flow
- Any work whose acceptance criteria are still shared by multiple packages

## Can Split Later Only If

1. The input and output contract is stable.
2. The write set is not shared.
3. The acceptance boundary is independent.

## Recommended Next Execution Package

- `P1 first minimal chain`
- `Suggested first branch: feat/task-xxx-min-pipeline`
- `Package scope: input entry, parsed layer, extracted output, sample and evidence alignment, minimal review or export closure`
