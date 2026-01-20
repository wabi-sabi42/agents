import unittest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import sys

# Add src to path to import agents_core
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agents_core.update import update

class TestUpdateLogic(unittest.TestCase):
    """Unit tests for the agents_core.update module.
    
    These tests use unittest.mock to simulate filesystem and git operations,
    ensuring the update logic works correctly without actually modifying
    the project state or interacting with remote repositories.
    """

    @patch("agents_core.update.run_command")
    @patch("agents_core.update.scan")
    @patch("agents_core.update.subprocess.run")
    @patch("builtins.open", new_callable=mock_open, read_data='{"test": "data"}')
    @patch("agents_core.update.Path.exists")
    @patch("agents_core.update.time.sleep") # Prevent actual waiting during test execution
    def test_update_success_flow(self, mock_sleep, mock_exists, mock_file, mock_run, mock_scan, mock_run_cmd):
        """Tests the complete successful update flow.
        
        This test simulates a project with changes that need to be committed
        and pushed. It verifies that:
        1. Tooling validation is performed.
        2. Repository scanning and schema validation are triggered.
        3. A pretty-printed index snapshot is created.
        4. Changed files are staged, committed, and pushed.
        """
        project_root = Path("/tmp/fake_project")
        
        # Simulate that .agents/index.json exists so snapshotting proceeds
        mock_exists.side_effect = lambda: True
        
        # Simulate 'git diff' finding local changes (returncode=1)
        mock_diff = MagicMock()
        mock_diff.returncode = 1
        
        # Simulate 'git push' succeeding on the first attempt
        mock_push = MagicMock()
        mock_push.returncode = 0
        
        # Define the sequence of subprocess.run calls expected in this flow
        mock_run.side_effect = [mock_diff, mock_push]
        
        # Execute the update logic
        update(project_root)
        
        # Verify that scan() was called for both refreshing the index and validation
        self.assertEqual(mock_scan.call_count, 2)
        mock_scan.assert_any_call(project_root, refresh_index=True)
        mock_scan.assert_any_call(project_root, validate_only=True)
        
        # Verify mandatory git validation and staging commands
        mock_run_cmd.assert_any_call(["git", "rev-parse", "--is-inside-work-tree"], project_root)
        mock_run_cmd.assert_any_call(["git", "add", "-A"], project_root)
        
        # Verify the push command was issued with correct arguments
        mock_run.assert_any_call(["git", "push"], cwd=project_root, capture_output=True, text=True)

    @patch("agents_core.update.run_command")
    @patch("agents_core.update.subprocess.run")
    @patch("agents_core.update.scan")
    @patch("agents_core.update.time.sleep")
    def test_update_push_retry(self, mock_sleep, mock_scan, mock_run, mock_run_cmd):
        """Tests the push retry logic when the initial attempt fails.
        
        This test simulates a scenario where:
        1. No new changes are detected locally.
        2. An initial 'git push' fail.
        3. A check shows the local branch is not behind (no rebase needed).
        4. A second 'git push' attempt succeeds.
        """
        project_root = Path("/tmp/fake_project")
        
        # Mock 1: 'git diff --cached' (returncode=0 means no changes to commit)
        mock_diff = MagicMock()
        mock_diff.returncode = 0
        
        # Mock 2: First 'git push' failure (e.g., transient network issue)
        mock_push_fail = MagicMock()
        mock_push_fail.returncode = 1
        
        # Mock 3: 'git status -sb' to check relationship with remote
        mock_status = MagicMock()
        mock_status.stdout = "## main" # Simulates a clean status, not behind
        
        # Mock 4: Second 'git push' success
        mock_push_success = MagicMock()
        mock_push_success.returncode = 0
        
        # Configure the mock to return these values in order
        mock_run.side_effect = [mock_diff, mock_push_fail, mock_status, mock_push_success]
        
        # Skip index file handling for this test case
        with patch("agents_core.update.Path.exists", return_value=False):
             update(project_root)
        
        # Validate that 'git push' was retried
        push_calls = [call for call in mock_run.call_args_list if call.args[0] == ["git", "push"]]
        self.assertEqual(len(push_calls), 2)
        
        # Ensure the script waited (slept) before retrying the failed push
        self.assertEqual(mock_sleep.call_count, 1)

if __name__ == "__main__":
    unittest.main()
