import sys
import json
from pathlib import Path

def install(project_root: Path):
    """
    Bootstrap the agent environment in the given project root.
    Copies schemas and AGENTS.md from the package resources.
    """
    print(f"[agents] Bootstrapping in: {project_root}")
    
    agents_dir = project_root / ".agents"
    schemas_dir = agents_dir / "schemas"
    schemas_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy Schemas
    try:
        from importlib.resources import files
        schema_pkg = files("agents_core.resources.schemas")
        for item in schema_pkg.iterdir():
            if item.is_file() and item.name.endswith(".json"):
                dest = schemas_dir / item.name
                dest.write_bytes(item.read_bytes())
                print(f"[agents] Copied schema: {item.name}")
    except ImportError:
        print("[agents][ERR] Python 3.9+ required for resource handling.")
        sys.exit(1)

    # Copy AGENTS.md
    try:
        res_pkg = files("agents_core.resources")
        agents_md = res_pkg / "AGENTS.md"
        if agents_md.is_file():
            dest = project_root / "AGENTS.md"
            dest.write_bytes(agents_md.read_bytes())
            print(f"[agents] Copied AGENTS.md to {dest}")
    except Exception as e:
        print(f"[agents][WARN] Could not copy AGENTS.md: {e}")

    # Ensure index/priorities exist
    index_path = agents_dir / "index.json"
    if not index_path.exists():
        idx_content = {
            "$schema": "schemas/index.schema.json",
            "version": 1,
            "generated_at": "bootstrap",
            "modules": [],
            "docs": []
        }
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(idx_content, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print("[agents] Created .agents/index.json")

    priorities_path = agents_dir / "priorities.json"
    if not priorities_path.exists():
        prio_content = {
            "$schema": "schemas/priorities.schema.json",
            "version": 1,
            "updated_at": "bootstrap",
            "policy": {
                "strategy": "critical_path_first",
                "tie_breakers": ["dependency_depth", "risk", "value"]
            },
            "queue": []
        }
        with open(priorities_path, "w", encoding="utf-8") as f:
            json.dump(prio_content, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print("[agents] Created .agents/priorities.json")

    print("[agents] Bootstrap complete.")
