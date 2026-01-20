"""Module for post-session update logic."""

import datetime
import json
import logging
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

from agents_core.scan import scan

# Configure logging to match Google standards
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def run_command(cmd: list, cwd: Path, abort_on_error: bool = True) -> subprocess.CompletedProcess:
    """Runs a shell command and returns the result.
    
    Args:
        cmd: List of command arguments.
        cwd: Working directory.
        abort_on_error: Whether to exit on error.
        
    Returns:
        The result of the command.
    """
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {' '.join(cmd)}")
        if e.stdout:
            logger.error(f"STDOUT: {e.stdout}")
        if e.stderr:
            logger.error(f"STDERR: {e.stderr}")
        if abort_on_error:
            sys.exit(1)
        return e

def update(project_root: Path):
    """Integrates post-session update logic.
    
    Args:
        project_root: The root directory of the project.
    """
    logger.info("Validating tooling...")
    # Check for git
    run_command(["git", "rev-parse", "--is-inside-work-tree"], project_root)
    
    logger.info("Running repo scan + validation...")
    # 1. Refresh index
    scan(project_root, refresh_index=True)
    # 2. Validate
    scan(project_root, validate_only=True)
    
    logger.info("Snapshotting ROADMAP (OVERVIEW.md pointers)...")
    index_path = project_root / ".agents" / "index.json"
    pretty_index_path = project_root / ".agents" / "index.pretty.json"
    
    if index_path.exists():
        try:
            with open(index_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            with open(pretty_index_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.write("\n")
        except Exception as e:
            logger.error(f"Failed to create pretty index: {e}")
            sys.exit(1)
    
    logger.info("Git add/commit...")
    run_command(["git", "add", "-A"], project_root)
    
    # Check for changes
    diff_result = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=project_root
    )
    
    if diff_result.returncode != 0:
        ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        commit_msg = f"chore(agent): post-session update @ {ts}"
        run_command(["git", "commit", "-m", commit_msg, "-m", "Runbook: agents update"], project_root)
    else:
        logger.info("No changes to commit.")
    
    # Push with basic retry
    retries = 3
    for i in range(1, retries + 1):
        push_result = subprocess.run(
            ["git", "push"],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        
        if push_result.returncode == 0:
            logger.info("Pushed successfully.")
            return

        logger.warning(f"Push failed (attempt {i}/{retries}).")
        
        # Check if behind
        status_result = subprocess.run(
            ["git", "status", "-sb"],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        if "[behind" in status_result.stdout:
            logger.info("Remote has new commits. Attempting 'git pull --rebase --autostash'...")
            pull_result = subprocess.run(
                ["git", "pull", "--rebase", "--autostash"],
                cwd=project_root
            )
            if pull_result.returncode == 0:
                logger.info("Rebase completed. Retrying push immediately...")
                continue
            else:
                logger.error("Automatic rebase failed. Resolve conflicts and rerun the script.")
                sys.exit(1)
        
        if i < retries:
            logger.info("Retrying in 3s...")
            time.sleep(3)
            
    logger.error(f"Push failed after {retries} attempts.")
    sys.exit(1)
