import sys
import shutil
import importlib.resources
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
    # We use importlib.resources (Python 3.9+ style preferably, but staying compat with 3.8+ using files)
    # Using the Traversable API if available or older path API
    try:
        from importlib.resources import files
        schema_pkg = files("agents_core.resources.schemas")
        for item in schema_pkg.iterdir():
            if item.is_file() and item.name.endswith(".json"):
                dest = schemas_dir / item.name
                dest.write_bytes(item.read_bytes())
                print(f"[agents] Copied schema: {item.name}")
    except ImportError:
        # Fallback for older python if needed, but we requested >=3.8, so 'files' might need backport or 3.9
        # actually 3.9+ has files(). For 3.8 we might need pkg_resources or legacy API.
        # Let's assume 3.9+ or backport for simplicity, or implement legacy fallback.
        # For this environment, we likely have modern python.
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
        index_path.write_text(
            '{"$schema":"schemas/index.schema.json","version":1,"generated_at":"bootstrap","modules":[],"docs":[]}',
            encoding="utf-8"
        )
        print("[agents] Created .agents/index.json")

    priorities_path = agents_dir / "priorities.json"
    if not priorities_path.exists():
        priorities_path.write_text(
            '{"$schema":"schemas/priorities.schema.json","version":1,"updated_at":"bootstrap","policy":{"strategy":"critical_path_first","tie_breakers":["dependency_depth","risk","value"]},"queue":[]}',
            encoding="utf-8"
        )
        print("[agents] Created .agents/priorities.json")

    print("[agents] Bootstrap complete.")
