import argparse
import sys
from pathlib import Path
from agents_core.install import install
from agents_core.scan import scan

def main():
    parser = argparse.ArgumentParser(description="Agents Core Tooling")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # init
    parser_init = subparsers.add_parser("init", help="Bootstrap agents in the current project")
    parser_init.add_argument("--root", default=None, help="Project root directory (default: current)")

    # scan
    parser_scan = subparsers.add_parser("scan", help="Scan for modules and update index")
    parser_scan.add_argument("--root", default=None, help="Project root directory (default: current)")
    parser_scan.add_argument("--refresh-index", action="store_true", help="Regenerate index.json")

    # validate
    parser_val = subparsers.add_parser("validate", help="Validate all schemas and task files")
    parser_val.add_argument("--root", default=None, help="Project root directory (default: current)")

    args = parser.parse_args()

    # Determine Root
    root_dir = Path.cwd()
    if args.root:
        root_dir = Path(args.root).resolve()

    if args.command == "init":
        install(root_dir)
        # Auto-scan after init
        scan(root_dir, refresh_index=True)
    elif args.command == "scan":
        scan(root_dir, refresh_index=args.refresh_index)
    elif args.command == "validate":
        scan(root_dir, validate_only=True)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
