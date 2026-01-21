# System Overview

## Repository Structure
[Provide a high-level map of the project directory structure.]

## Module Map
- **[Module Name]**: [Description of responsibility and links to documentation/tasks.]
- **[Module Name]**: [Description of responsibility and links to documentation/tasks.]

## Operational Flow
1. **[Step 1]**: [Description]
2. **[Step 2]**: [Description]

## Control Plane
The agentic control plane lives in `.agents/`.
- `index.json`: Repository map.
- `priorities.json`: Global task queue.
- `modules/*/tasks.json`: Atomic unit-of-work tracking.
