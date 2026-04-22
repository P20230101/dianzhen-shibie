# Workspace Task Map Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a fact-based workspace map that assigns the current mixed implementation files to `TASK-002` through `TASK-010` and records the current branch mismatch.

**Architecture:** One markdown inventory file captures the mapping. The file is derived from existing task cards, branch heads, and file contents. No product code changes are made.

**Tech Stack:** Markdown, Git, PowerShell

---

### Task 1: Write the workspace inventory

**Files:**
- Create: `tasks/workspace-map.md`

- [ ] **Step 1: Write the inventory content**

Create a markdown table with one row each for `TASK-002` through `TASK-010`. For every row, include:
- the task purpose,
- the primary implementation files,
- the tests,
- the generated artifacts,
- the current branch state.

- [ ] **Step 2: Record the current branch snapshot**

Add a short section at the top that states:
- `dispatch/tasks` is at the latest governance commit,
- `feat/task-002-input-excel` and `feat/task-005-input-pdf-intake` still point at `c16d956`,
- `feat/task-006-retrieval-corpus`, `feat/task-007-extract-query`, `feat/task-008-export-kg`, and `feat/task-009-smoke-retrieval-kg` still point at `2425004`,
- `feat/task-010-review-approval` points at `82269b7`,
- no `TASK-011` is opened.

- [ ] **Step 3: Verify the referenced paths**

Run:

```powershell
rg -n "p1_seed.py|p1_transform.py|p1_validate_export.py|build_pdf_register.py|build_pdf_intake_manifest.py|build_retrieval_corpus.py|query_retrieval.py|project_knowledge_graph.py|promote_p1_review.py|test_external_retrieval_kg_smoke.py" tasks/workspace-map.md
```

Expected: every referenced path appears exactly where it should in the inventory and there are no placeholder rows.

- [ ] **Step 4: Check markdown hygiene**

Run:

```powershell
git diff --check -- tasks/workspace-map.md
```

Expected: no whitespace or patch-format errors.

- [ ] **Step 5: Commit the map**

Run:

```powershell
git add tasks/workspace-map.md
git commit -m "docs: add workspace task map"
```

Expected: a single commit containing only the workspace inventory.
