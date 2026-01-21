import unittest
import json
import os
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
from unittest.mock import patch, MagicMock

# Add src to path to import agents_core
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agents_core.scan import scan, discover_modules, ensure_task_files

class TestScanLogic(unittest.TestCase):
    """Unit tests for the agents_core.scan module.
    
    These tests verify module discovery, index maintenance, and 
    schema validation logic.
    """

    def setUp(self):
        self.test_dir = TemporaryDirectory()
        self.project_root = Path(self.test_dir.name)
        # Setup basic .agents structure for scan (which expects it to exist)
        self.agents_dir = self.project_root / ".agents"
        self.agents_dir.mkdir()
        (self.agents_dir / "schemas").mkdir()

    def tearDown(self):
        self.test_dir.cleanup()

    def test_discover_modules(self):
        """Tests discovery of modules in src/."""
        mod_dir = self.project_root / "src" / "my_module"
        mod_dir.mkdir(parents=True)
        (mod_dir / "main.py").touch()
        
        mods = discover_modules(self.project_root)
        self.assertEqual(len(mods), 1)
        self.assertEqual(mods[0]["name"], "my_module")
        self.assertEqual(mods[0]["path"], "src/my_module")

    def test_scan_refresh_index(self):
        """Tests that scan creates/updates index.json."""
        mod_dir = self.project_root / "src" / "my_app"
        mod_dir.mkdir(parents=True)
        (mod_dir / "app.ts").touch()
        
        scan(self.project_root, refresh_index=True)
        
        index_path = self.agents_dir / "index.json"
        self.assertTrue(index_path.is_file())
        
        with open(index_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(len(data["modules"]), 1)
            self.assertEqual(data["modules"][0]["name"], "my_app")

    def test_scan_preserve_docs(self):
        """Tests that scan doesn't overwrite existing docs in index.json."""
        index_path = self.agents_dir / "index.json"
        initial_content = {
            "$schema": "schemas/index.schema.json",
            "version": 1,
            "modules": [],
            "docs": [{"title": "Existing Doc", "path": "docs/EXISTING.md"}]
        }
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(initial_content, f)

        # Create a module to trigger an update
        mod_dir = self.project_root / "src" / "new_mod"
        mod_dir.mkdir(parents=True)
        (mod_dir / "main.py").touch()
        
        scan(self.project_root, refresh_index=True)
        
        with open(index_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(len(data["docs"]), 1)
            self.assertEqual(data["docs"][0]["title"], "Existing Doc")
            self.assertEqual(len(data["modules"]), 1)

    def test_ensure_task_files(self):
        """Tests automatic creation of tasks.json for discovered modules."""
        mods = [{
            "name": "test_mod",
            "path": "src/test_mod",
            "tasks_file": ".agents/modules/test_mod/tasks.json"
        }]
        
        ensure_task_files(self.project_root, mods)
        
        task_file = self.project_root / ".agents/modules/test_mod/tasks.json"
        self.assertTrue(task_file.is_file())
        
        with open(task_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(data["module"], "test_mod")

    @patch("agents_core.scan.validate")
    def test_scan_validate_only(self, mock_validate):
        """Tests the validation-only mode."""
        index_path = self.agents_dir / "index.json"
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump({
                "$schema": "schemas/index.schema.json",
                "version": 1,
                "modules": []
            }, f)
            
        # Should call validate once for index
        # (It would also call for priorities and task files if they existed/were referenced)
        scan(self.project_root, validate_only=True)
        self.assertTrue(mock_validate.called)

if __name__ == "__main__":
    unittest.main()
