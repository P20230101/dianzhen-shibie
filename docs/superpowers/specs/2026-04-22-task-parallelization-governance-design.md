# Task Parallelization Governance Design

## Goal

Allow future paper-expansion tasks to run on multiple execution branches in parallel without conflicting writes, while keeping canonical outputs and knowledge-graph integration under controlled serial promotion.

## Why This Design Exists

The current post-`TASK-010` expansion tasks reuse the same core files:

- `scripts/build_pdf_sample_bundle.py`
- `tests/test_build_pdf_sample_bundle.py`
- `tests/test_promote_p1_review.py`
- `outputs/p1/extracted/samples_v1.json`
- `outputs/p1/extracted/evidence_v1.json`
- `outputs/kg/knowledge_graph.json`

This means the current workflow fails the branch-splitting gate in `tasks/branch-strategy.md`:

1. the write set is shared
2. the acceptance boundary is not independent
3. global KG growth is being used as a per-task acceptance signal

The shortest-path fix is not “open more branches now”; it is to change what future tasks are allowed to write.

## Constraints

- No compatibility or patchwork branch strategy.
- No redesign of the entire extraction pipeline.
- Keep the existing canonical outputs and promotion flow.
- Preserve `dispatch/tasks` as the only place for planning, task release, board updates, branch mapping, and task archive updates.
- Keep the change narrowly focused on making future paper-expansion tasks parallel-safe.

## Non-Goals

- Replacing the current schema or mapping contracts.
- Rewriting the P1 seed / transform / validate chain.
- Replacing the current KG projection logic.
- Turning every current historical task into a new storage format immediately.

## Recommended Approach

Use a two-layer execution model:

1. `extract-paper-bundle` tasks run in parallel and produce only paper-local bundle artifacts.
2. `promote-bundle-batch` tasks run serially and merge selected bundles into canonical outputs and KG.

This is the minimum change that makes later tasks parallel-safe without disrupting the current main line.

## Task Classes After The Change

### 1. `extract-paper-bundle`

Purpose:
Create one paper-local sample/evidence bundle from one paper target.

Parallel policy:
May run on multiple execution branches in parallel after the bundle contract is stabilized.

Allowed writes:

- `data/03_bundle_specs/<paper-id>.json`
- `outputs/p1/bundles/<paper-id>/sample.json`
- `outputs/p1/bundles/<paper-id>/evidence.json`
- `tests/fixtures/pdf_sample_bundle/expected_sample_<paper-id>.json`
- `tests/fixtures/pdf_sample_bundle/expected_evidence_<paper-id>.json`
- a paper-specific task card and dispatch records on `dispatch/tasks`

Not allowed:

- direct writes to `outputs/p1/extracted/samples_v1.json`
- direct writes to `outputs/p1/extracted/evidence_v1.json`
- direct writes to `outputs/kg/knowledge_graph.json`

Acceptance boundary:

- the paper bundle builds successfully
- the bundle matches the bundle contract
- the paper-specific tests pass
- the bundle is ready for later promotion

### 2. `promote-bundle-batch`

Purpose:
Take one or more completed bundles and merge them into canonical extracted outputs, then regenerate downstream review/KG outputs.

Parallel policy:
Must stay serial on one execution branch.

Allowed writes:

- `outputs/p1/extracted/samples_v1.json`
- `outputs/p1/extracted/evidence_v1.json`
- `outputs/kg/knowledge_graph.json`

Acceptance boundary:

- selected bundles are merged correctly
- promotion passes
- KG regeneration passes
- integration-level tests pass

### 3. `parser-capability`

Purpose:
Change shared parser or builder logic when a new paper family cannot fit the current bundle builder contract.

Parallel policy:
Must stay serial while it changes shared logic.

Allowed writes:

- `scripts/build_pdf_sample_bundle.py`
- shared tests for the builder / promotion boundary

Acceptance boundary:

- shared bundle builder remains stable
- existing paper fixtures still pass
- new paper family is supported

## Storage Model

### Bundle Spec

Each future paper-expansion task should become mostly data-driven through a paper spec file:

- `data/03_bundle_specs/<paper-id>.json`

This spec holds the paper-specific extraction configuration needed by `build_pdf_sample_bundle.py`.

### Bundle Outputs

Each paper writes only its own bundle directory:

- `outputs/p1/bundles/<paper-id>/sample.json`
- `outputs/p1/bundles/<paper-id>/evidence.json`

This is the key isolation layer. It removes direct contention on canonical aggregate outputs.

### Canonical Outputs

Only promotion tasks write:

- `outputs/p1/extracted/samples_v1.json`
- `outputs/p1/extracted/evidence_v1.json`
- `outputs/kg/knowledge_graph.json`

## Data Flow

### Parallel Flow

1. select one paper target
2. create or update its paper spec
3. run `build_pdf_sample_bundle.py --paper-id <paper-id>`
4. write only that paper’s bundle outputs
5. run paper-specific tests
6. close the bundle task

### Serial Integration Flow

1. select completed bundle outputs for promotion
2. merge them into canonical extracted outputs
3. run review promotion
4. regenerate the knowledge graph
5. run integration-level verification
6. close the promotion task

## Branch Rules After The Change

### May Open In Parallel

- multiple `extract-paper-bundle` tasks for different papers
- independent input adapters
- independent extraction helpers that do not touch shared core files

### Must Stay Serial

- `parser-capability` changes
- `promote-bundle-batch` tasks
- any task touching canonical extracted outputs or KG outputs directly
- any task changing shared schemas, mappings, or validation boundaries

## One-Time Migration Task

Before true parallelization starts, run one serial conversion task:

`TASK-XXX | bundle-output decoupling for paper expansion`

This task does only three things:

1. make `build_pdf_sample_bundle.py` write paper-local bundle outputs
2. make the builder load per-paper specs from `data/03_bundle_specs/`
3. keep canonical promotion and KG generation as a separate later step

This is the minimum viable refactor that unlocks parallel future tasks.

## Testing Strategy

### Bundle-Level Tests

Used by `extract-paper-bundle` tasks:

- validate the per-paper spec loads correctly
- validate generated sample bundle matches expected fixture
- validate generated evidence bundle matches expected fixture

### Integration-Level Tests

Used by `promote-bundle-batch` tasks:

- merge selected bundles into canonical outputs
- run review promotion
- run KG projection
- confirm downstream outputs are valid

### Regression Guard

When `parser-capability` changes shared builder logic, existing bundle fixtures must continue to pass.

## Failure Handling

If a future paper requires changes to shared parser behavior, do not force that work into a parallel paper bundle task. Stop and reclassify it as `parser-capability`.

If a task needs to touch canonical outputs directly, do not keep it as `extract-paper-bundle`. Reclassify it as `promote-bundle-batch`.

If two future tasks want to edit the same shared builder or shared regression tests, do not run them in parallel.

## Expected Outcome

After this change:

- future paper-expansion tasks stop fighting over canonical outputs
- paper-local bundle tasks can be released on multiple execution branches
- canonical extracted outputs and KG stay under one controlled promotion path
- branch splitting follows the repository’s existing governance rules instead of bypassing them

## Recommendation

Approve one serial refactor task first to introduce the bundle-isolation layer.

Only after that task lands should future paper-expansion tasks be released in parallel.
