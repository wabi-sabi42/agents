# Agent Session Workflow

Follow this checklist for every coding session to ensure compliance with `AGENTS.md`.

## 1. Bootstrap (First Run Only)
- [ ] Read `VISION.md` and `OVERVIEW.md`.
- [ ] Run `bash scripts/agent_bootstrap.sh`.

## 2. Planning
- [ ] Read `.agents/index.json` and `.agents/priorities.json`.
- [ ] Run `bash scripts/agent_next_step.sh` to identify the next task.
- [ ] **Crucial**: No placeholders in code.

## 3. Execution
- [ ] Implement the task fully.
- [ ] Update `tasks.json` -> `notes` with decisions/rationale.
- [ ] Add `refs` for cross-module dependencies.
- [ ] If new work arises, split into new atomic tasks.

## 4. Housekeeping (Mandatory)
- [ ] Update `tasks.json` -> `next_notes` for the *next* agent/session.
- [ ] Run `bash scripts/agent_post_session_update.sh`.
  - [ ] **Must pass** before any commit/push.
  - [ ] If it fails, fix and rerun.
