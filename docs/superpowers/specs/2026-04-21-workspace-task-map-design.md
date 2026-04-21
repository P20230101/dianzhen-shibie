# Workspace Task Map Design

## 1. Goal

Document the current mixed workspace and assign the untracked implementation files and generated artifacts to `TASK-002` through `TASK-010` without changing product behavior.

## 2. Scope

### 2.1 In Scope

- Create a single fact-based inventory at `tasks/workspace-map.md`.
- Record which current files belong to which task.
- Record the current branch mismatch where branch heads lag behind the workspace.
- Keep `TASK-011` out of the repository state and out of the mapping.

### 2.2 Out of Scope

- Code changes to the product pipeline.
- Branch creation, rebasing, or cherry-picking.
- Automatic fallback mapping when evidence is missing.
- Any new task assignment.

## 3. Architecture

The design uses one markdown inventory file as the source of truth for the current split decision. The inventory is derived from task cards, branch heads, file contents, and generated artifacts already present in the repository. It does not introduce a new workflow or data model; it simply makes the current state explicit so the workspace can be separated safely.

## 4. Components

- `tasks/workspace-map.md`: the only new deliverable.
- Task evidence rows: one row each for `TASK-002` through `TASK-010`.
- Branch snapshot section: records the current branch head for the affected execution branches.

## 5. Data Flow

1. Read the task cards and archived records to confirm task titles and dependencies.
2. Read the current workspace files to identify the implementation files, tests, and generated artifacts.
3. Compare those files with `git branch` output to capture the current branch mismatch.
4. Write the inventory table and split notes into `tasks/workspace-map.md`.

## 6. Error Handling

- If a file is shared by multiple tasks, list it in every owning row and say so explicitly.
- If a task has no committed branch head yet, mark it as workspace-only.
- If the evidence is insufficient, leave the item out rather than guessing.

## 7. Testing

- Verify every referenced path exists in the repository.
- Verify the inventory contains no `TASK-011` references.
- Run `git diff --check` on the new markdown files.

## 8. Success Criteria

- A reader can tell which current files belong to each task.
- Shared files are clearly marked.
- Current branch state is recorded next to the owning task.
- The mapping stays limited to `TASK-002` through `TASK-010`.
