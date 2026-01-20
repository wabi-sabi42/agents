# Project Vision: Agents Core

## Primary Objective
To provide a **deterministic, verifiable, and self-documenting control plane** for autonomous coding agents. This repository contains the tools required to bootstrap and maintain a machine-readable environment where agents can operate with maximum context and zero ambiguity.

## Core Pillars

### 1. Zero Ambiguity
Coding agents must never guess project structure or task priority. All intents must be codified in `.agents/priorities.json` and `tasks.json` files.

### 2. Verified Integrity
All machine-readable state ($index$, $priorities$, $tasks$) must be validated against strict JSON schemas before any commit or PR is finalized.

### 3. Native Agent Integration
The tooling is designed to be invoked directly by agents. The `update` command automates the "housekeeping" of the repo (scanning, validating, commits, and pushes), ensuring the repository state remains perfectly synced with reality.

### 4. Self-Documenting Evolution
As the project grows, the `scan` command dynamically updates the `index.json`, mapping modules to their respective tasks. The documentation and the implementation are two sides of the same coin.

## Anti-Drift Constraints
- **No placeholders**: Implementation is either complete or explicitly tracked as an open task.
- **Machine-first**: Internal state is stored in JSON for reliability, then mirrored to human-readable docs for transparency.
- **Idempotent Operations**: All CLI commands must be safe to run repeatedly.
