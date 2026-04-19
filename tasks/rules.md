# Dispatch Rules

## Allowed On dispatch/tasks
- Task breakdown
- Status updates
- Branch assignment
- Dispatch rules
- Task archive

## Not Allowed On dispatch/tasks
- Business code development
- Feature implementation
- Direct code integration to main

## Branch Flow
1. Update task records on `dispatch/tasks`
2. Create dev branch from `dispatch/tasks`
3. Implement on dev branch
4. Move code to `main` using `rebase --onto` or `cherry-pick`

## Integration Rule
- Do not merge `dispatch/tasks` directly into `main`
- Do not merge a dev branch directly into `main` if it still carries dispatch history
