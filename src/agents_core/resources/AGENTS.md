# AGENTS.md — Root Contract for Coding Agents

> **Purpose.** This repository is agent-operated. This file is the single source of truth for how agents (e.g., Codex) must behave.

## Non-Negotiables (Immutable)
1. **No placeholders or partial code.** Do not produce examples, stubs, TODOs-instead-of-code, mock functions, or “left as an exercise”. Implement fully, robustly, and safely.
2. **Virtual Environments are Mandatory.** You must always use a virtual environment (venv) for Python projects. Never install packages globally.
3. **End-of-session update is mandatory.** Before opening any PR or pushing any branch, you **must** run:
   ```bash
   agents validate
   ```
   The push/PR must be aborted if this command fails.
4. Machine-readable control plane. Internal state lives under /.agents/ (JSON only). Human docs live in README.md, VISION.md, OVERVIEW.md, and module READMEs.
5. Link everything. When a task needs context elsewhere, include precise cross-file references: {"file":"path", "line":N, "end_line":M, "anchor":"#heading"}.
6. Idempotence. All scripts and generated artifacts must be repeatable. No brittle, one-shot steps.

## First Run (Bootstrap)

On first contact in a repo:
- [ ] **Read intent**: Read `VISION.md` (top intent) and `OVERVIEW.md` (structure).
- [ ] **Initialize**: Execute `agents init`.
  - This performs a deep scan, builds `.agents/index.json`, initializes `.agents/priorities.json`, seeds a `modules/*/tasks.json` for discovered modules, and validates all JSON against schemas.

## Session Loop (Every Time You Code)

Follow this workflow for every coding session:

### 1. Planning
- [ ] **Identify the next task**: Read `.agents/index.json` and `.agents/priorities.json`. The next task is strictly the first item in the `queue` array.
- [ ] **Update context**: Read the relevant `modules/*/tasks.json` to understand the specific task details and criteria.

### 2. Execution
- [ ] **Implement fully**: Implement the task robustly and safely. **Crucial**: No placeholders or partial code.
- [ ] **Update supporting docs**: Update or create documentation as needed.
- [ ] **Write back context**:
  - Append decisions and rationale to the relevant task’s `notes[]`.
  - If new cross-module knowledge emerges, add `refs[]` with exact file+line spans.
  - If new sub-work appears, split it into atomic tasks with clear acceptance criteria.

### 3. Housekeeping (MANDATORY)
- [ ] **Self-Memory**: Update `tasks.json` -> `next_notes[]` for the *next* agent/session.
- [ ] **Validate and Sync**: Run `agents validate`.
  - This validates JSON, refreshes indices, updates ROADMAP snapshots, commits, and pushes.
  - **Must pass** before any commit/push. If it fails, fix and rerun.

## File Hierarchy
•VISION.md — immutable high-level goals, guardrails, and anti-drift constraints.
•OVERVIEW.md — current shape of the system, module map, and links to task files.
•.agents/index.json — machine index of modules, docs, and link targets.
•.agents/priorities.json — dynamic, ordered list of tasks (critical-path first).
•.agents/modules/*/tasks.json — atomic, verifiable tasks per module.

## Git Conventions
All commits must follow the Conventional Commits specification: `<type>(<scope>): <description>`
- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **chore**: Updating build tasks, package manager configs, etc.
- **agent**: chore(agent): post-session update @ {timestamp}

## Quality Gates (before marking a task done)
•Deterministic acceptance tests (unit/integration) exist and pass.
•Performance/complexity is appropriate for expected scale.
•Security considerations addressed (inputs validated, secrets not hard-coded, least privilege).
•Observability (logs/metrics) and failure handling implemented where relevant.
•Code Cleanliness maintained (no unused imports, no commented-out code blocks, no legacy implementation comments).

## Notes for Future You (Self-Memory)
•At the end of each task, append an actionable next_notes[] with hints you would have wanted before starting the next task.
•If priorities changed during your session, update .agents/priorities.json using the scripts. Never leave the repo in a state that requires implicit memory.

Compliance with this contract is required for any PR authored by an agent.
