import argparse
import json
import sys
from pathlib import Path
from importlib.resources import files
from jsonschema import validate
from referencing import Registry, Resource

def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[scan][ERR] Failed to read {path}: {e}", file=sys.stderr)
        sys.exit(1)

def write_json(path, obj):
    tmp = Path(str(path) + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")
    tmp.replace(path)

def get_registry():
    registry = Registry()
    # Load all schemas from package resources
    try:
        schema_pkg = files("agents_core.resources.schemas")
        for item in schema_pkg.iterdir():
            if item.is_file() and item.name.endswith(".json"):
                try:
                    data = json.loads(item.read_text(encoding="utf-8"))
                    if "$id" in data:
                        resource = Resource.from_contents(data)
                        registry = registry.with_resource(uri=data["$id"], resource=resource)
                except Exception:
                    continue
    except Exception as e:
        print(f"[scan][WARN] Failed to load schemas from package: {e}")
        
    return registry

def validate_against_schema(instance, schema_name, registry):
    try:
        schema_pkg = files("agents_core.resources.schemas")
        schema_file = schema_pkg / schema_name
        schema = json.loads(schema_file.read_text(encoding="utf-8"))
        validate(instance=instance, schema=schema, registry=registry)
    except Exception as e:
        print(f"[scan][ERR] Validation failed for schema {schema_name}: {e}\nInstance: {json.dumps(instance, indent=2)}", file=sys.stderr)
        sys.exit(1)

def discover_modules(project_root: Path):
    candidates = []
    # Scan common directories
    for rel in ["src", "app", "apps", "packages", "services", "modules"]:
        p = project_root / rel
        if p.exists():
            for path in p.rglob("*"):
                if path.is_dir():
                    has_code = any(fn.suffix in {".py",".ts",".tsx",".js",".jsx",".go",".rs",".swift",".kt",".java"} 
                                   for fn in path.iterdir() if fn.is_file())
                    if has_code:
                        mod_name = path.name
                        candidates.append((mod_name, path.relative_to(project_root)))
    
    seen_paths, used_slugs, mods = set(), set(), []
    for name, rel_path in candidates:
        if rel_path in seen_paths: continue
        seen_paths.add(rel_path)
        
        slug = name
        idx = 2
        while slug in used_slugs:
            slug = f"{name}-{idx}"
            idx += 1
        used_slugs.add(slug)
        
        # Determine tasks file location
        # If the module is specifically "core" and mapped to "scripts" (legacy case), handle it?
        # For now, standard behavior: .agents/modules/<slug>/tasks.json
        tasks_file = f".agents/modules/{slug}/tasks.json"
        
        mods.append({
            "name": slug,
            "path": str(rel_path),
            "tasks_file": tasks_file
        })
    return mods

def ensure_task_files(project_root: Path, mods):
    # Load template from resources
    template_content = None
    try:
        tpl_pkg = files("agents_core.resources.templates")
        tpl_file = tpl_pkg / "module_tasks.json"
        if tpl_file.is_file():
            template_content = tpl_file.read_text(encoding="utf-8")
    except Exception:
        pass

    for m in mods:
        path = project_root / m["tasks_file"]
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            if template_content:
                content = template_content.replace("__MODULE_NAME__", m["name"])
                content = content.replace("__TIMESTAMP_OR_BOOTSTRAP__", "scan")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"[scan] created {path}")
            else:
                write_json(path, {
                    "$schema": "schemas/tasks.schema.json",
                    "module": m["name"],
                    "updated_at": "scan",
                    "tasks": []
                })
                print(f"[scan] created {path} (fallback)")

def scan(project_root: Path, refresh_index: bool = False, validate_only: bool = False):
    agents_dir = project_root / ".agents"
    if not agents_dir.exists() and not validate_only:
        print("[scan][ERR] .agents directory not found. Run 'agents init' first.", file=sys.stderr)
        sys.exit(1)

    registry = get_registry()
    
    # 1. Validation Logic
    if validate_only:
        index_path = agents_dir / "index.json"
        priorities_path = agents_dir / "priorities.json"
        
        if index_path.exists():
            idx = load_json(index_path)
            validate_against_schema(idx, "index.schema.json", registry)
            
            # Validate all modules referenced in index
            for mod in idx.get("modules", []):
                tf = project_root / mod["tasks_file"]
                if not tf.exists():
                     print(f"[scan][ERR] Missing task file: {tf}", file=sys.stderr)
                     sys.exit(1)
                tasks = load_json(tf)
                validate_against_schema(tasks, "tasks.schema.json", registry)
        
        if priorities_path.exists():
            prio = load_json(priorities_path)
            validate_against_schema(prio, "priorities.schema.json", registry)
            
        print("[scan] validation OK")
        return

    # 2. Scan Logic
    existing_index = {}
    index_path = agents_dir / "index.json"
    if index_path.exists():
        existing_index = load_json(index_path)
    
    mods = discover_modules(project_root)
    
    # Preserve existing docs/config
    final_mods = []
    # Map by name for easy lookup
    existing_mod_map = {m["name"]: m for m in existing_index.get("modules", [])}
    
    for m in mods:
        if m["name"] in existing_mod_map:
            # Keep existing config (like docs) but update path if changed? 
            # For simplicity, we merge info.
            merged = existing_mod_map[m["name"]].copy()
            merged["path"] = m["path"] # Update path in case it moved
            # Keep the old tasks_file location to avoid losing data
            m["tasks_file"] = merged["tasks_file"]
            final_mods.append(merged)
        else:
            final_mods.append(m)
            
    # Write Index
    if refresh_index or not index_path.exists():
        idx = {
            "$schema": "schemas/index.schema.json",
            "version": 1,
            "generated_at": "scan",
            "modules": final_mods,
            "docs": existing_index.get("docs", [])
        }
        write_json(index_path, idx)
        print(f"[scan] updated {index_path}")
        
    # Ensure tasks files
    ensure_task_files(project_root, final_mods)
