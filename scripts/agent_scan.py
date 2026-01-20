#!/usr/bin/env python3
"""Compatibility script for agent scan."""

import sys
import argparse
from pathlib import Path
from agents_core.scan import scan

def main():
    parser = argparse.ArgumentParser(description="Compatibility wrapper for agents scan")
    parser.add_argument("--root", default=None, help="Project root")
    parser.add_argument("--refresh-index", action="store_true", help="Refresh index")
    parser.add_argument("--validate", action="store_true", help="Validate only")
    
    args = parser.parse_args()
    
    root_dir = Path.cwd()
    if args.root:
        root_dir = Path(args.root).resolve()
        
    if args.validate:
        scan(root_dir, validate_only=True)
    else:
        scan(root_dir, refresh_index=args.refresh_index)

if __name__ == "__main__":
    main()
