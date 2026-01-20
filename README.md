# Agents Core

Core tooling and protocol for managing agentic coding workflows. This package provides the "Agentic Control Plane" required for autonomous agents to operate safely and effectively within a repository.

## Installation

```bash
# Clone the repository
git clone https://github.com/wabi-sabi42/agents.git
cd agents

# Install in editable mode
pip install -e .
```

## Quick Start (for Agents)

If this is your first time in a project:
1. Read [VISION.md](./VISION.md) and [OVERVIEW.md](./OVERVIEW.md).
2. Initialize the project control plane:
   ```bash
   agents init
   ```

## CLI Reference

### `agents init`
Bootstraps the project with the `.agents/` directory, seeds the `index.json`, creates `priorities.json`, and copies the [AGENTS.md](./AGENTS.md) contract to the project root.

### `agents scan`
Scans the project for code modules and updates `.agents/index.json`.
- `--refresh-index`: Force regeneration of the index.

### `agents validate`
Validates all machine-readable state (`index.json`, `priorities.json`, and all module `tasks.json` files) against the project's JSON schemas.

### `agents update`
A high-level orchestration command designed for end-of-session synchronization. It performs:
1. Project scan and index refresh.
2. Schema validation.
3. Pretty-printing of the index for human inspection.
4. Git staging (`add -A`).
5. Git commit (with timestamp and runbook pointer).
6. Git push (with automatic rebase/retry logic).

## The Agentic Contract
All agents operating in a repository initialized with this tooling must adhere to the rules defined in [AGENTS.md](./AGENTS.md).

## Development and Testing
To run the test suite:
```bash
python3 tests/test_update.py
```
