# Using Agents Core

`agents-core` is a CLI tool that provides validation, schema enforcement, and workflow automation for agentic coding.

## Installation

Install the package via pip:

```bash
pip install agents-core
```
(Or install from your git submodule if developing locally: `pip install vendor/agents`)

## Usage

### 1. Initialize a Project
Run this in the root of your repository to bootstrap the `.agents` folder, schemas, and `AGENTS.md`.

```bash
agents init
```

### 2. Scan for Modules
If you have added new directories or code modules, update the index:

```bash
agents scan
```
This will:
- Discover code modules.
- Create/Update `tasks.json` files for each module.
- Update `.agents/index.json`.

### 3. Validate
Ensure all your task files and schemas are valid:

```bash
agents validate
```

### 4. Continuous Integration
Add this to your CI pipeline to prevent drift:

```bash
agents validate
```
