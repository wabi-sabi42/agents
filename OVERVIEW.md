# System Overview: Agents Core

This document maps the structural components of the `agents-core` repository.

## Repository Structure

```text
.
├── AGENTS.md           # The root contract for coding agents (mandatory protocol)
├── VISION.md           # High-level intent and immutable project pillars
├── OVERVIEW.md         # This map of the system (current document)
├── README.md           # User guide and CLI reference
├── pyproject.toml      # Project configuration and entry points
├── src/                # Source code
│   └── agents_core/
│       ├── cli.py      # Argument parsing and command routing
│       ├── install.py  # Project initialization (bootstrap) logic
│       ├── scan.py     # Module discovery and index generation
│       ├── update.py   # Post-session automation (commit/push logic)
│       └── resources/  # Embedded schemas and document templates
└── tests/              # Unit and integration test suite
```

## Module Definitions

### `agents_core`
The primary package. It provides the CLI interface and the logic for the "Agentic Control Plane".

- **`cli.py`**: The entry point. It maps subcommands (`init`, `scan`, `validate`, `update`) to their handlers.
- **`install.py`**: Responsible for the `init` command. It seeds the project with the necessary metadata and schemas.
- **`scan.py`**: The "eyes" of the system. It traverses the filesystem to find code modules and keeps `.agents/index.json` updated.
- **`update.py`**: The orchestration layer for end-of-session synchronization.

### Control Plane (`.agents/`)
When initialized in a target repository, the tooling creates a `.agents/` directory containing:
- **`index.json`**: Machine-readable project map.
- **`priorities.json`**: The ordered task queue for agents.
- **`schemas/`**: JSON schemas used to validate project state.

## Operational Flow

1. **Bootstrap**: Run `agents init` to prepare a repo for agentic operation.
2. **Maintenance**: Run `agents scan` after adding new code to refresh the index.
3. **Validation**: Run `agents validate` to ensure all metadata is consistent.
4. **Sync**: Run `agents update` to bundle scanning, validation, and git syncing into a single step.
