import unittest
import json
import os
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
import sys

# Add src to path to import agents_core
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agents_core.install import install

class TestInstallLogic(unittest.TestCase):
    """Unit tests for the agents_core.install module.
    
    These tests use a TemporaryDirectory to verify that the bootstrap
    logic correctly creates the .agents/ structure and deploys
    documentation templates.
    """

    def setUp(self):
        self.test_dir = TemporaryDirectory()
        self.project_root = Path(self.test_dir.name)

    def tearDown(self):
        self.test_dir.cleanup()

    def test_install_fresh_bootstrap(self):
        """Tests bootstrap in a fresh directory."""
        install(self.project_root)

        # 1. Check directory structure
        agents_dir = self.project_root / ".agents"
        schemas_dir = agents_dir / "schemas"
        self.assertTrue(agents_dir.is_dir())
        self.assertTrue(schemas_dir.is_dir())

        # 2. Check schemas
        expected_schemas = ["index.schema.json", "priorities.schema.json", "tasks.schema.json", "common.schema.json"]
        for schema in expected_schemas:
            self.assertTrue((schemas_dir / schema).is_file(), f"Missing schema: {schema}")

        # 3. Check documentation
        self.assertTrue((self.project_root / "AGENTS.md").is_file())
        self.assertTrue((self.project_root / "VISION.md").is_file())
        self.assertTrue((self.project_root / "OVERVIEW.md").is_file())

        # 4. Check control plane state
        index_path = agents_dir / "index.json"
        priorities_path = agents_dir / "priorities.json"
        self.assertTrue(index_path.is_file())
        self.assertTrue(priorities_path.is_file())

        # Verify index structure
        with open(index_path, "r", encoding="utf-8") as f:
            index_data = json.load(f)
            self.assertEqual(index_data["$schema"], "schemas/index.schema.json")
            self.assertEqual(index_data["version"], 1)

    def test_install_idempotency(self):
        """Tests that install does not overwrite existing custom content."""
        # Pre-seed VISION.md with custom content
        custom_vision = "# My Custom Vision"
        install(self.project_root) # First pass
        
        vision_path = self.project_root / "VISION.md"
        with open(vision_path, "w", encoding="utf-8") as f:
            f.write(custom_vision)
        
        # Second pass
        install(self.project_root)
        
        # Verify it wasn't overwritten
        with open(vision_path, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), custom_vision)

    def test_install_missing_schemas_idempotency(self):
        """Tests that install restores missing schemas but keeps others."""
        install(self.project_root)
        
        schema_to_delete = self.project_root / ".agents" / "schemas" / "tasks.schema.json"
        schema_to_delete.unlink()
        
        install(self.project_root)
        
        # Verify it was restored
        self.assertTrue(schema_to_delete.is_file())

if __name__ == "__main__":
    unittest.main()
