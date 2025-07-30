#!/usr/bin/env python3

import argparse
import os
import sys
from .generator import generate_workspace_config, generate_package_config

def find_workspace_root():
    """Find workspace root by looking for workspace pattern."""
    current_dir = os.getcwd()
    
    while current_dir != "/":
        parent_dir = os.path.dirname(current_dir)
        if "workspace" in parent_dir and os.path.isdir(os.path.join(current_dir, "src")):
            return current_dir
        current_dir = parent_dir
    return None

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Generate VS Code configurations")
    parser.add_argument("--workspace", action="store_true", help="Generate workspace config")
    parser.add_argument("--package", action="store_true", help="Generate package config")
    parser.add_argument("path", nargs="?", help="Target path")
    
    args = parser.parse_args()
    
    if args.path:
        target_path = args.path
    else:
        target_path = os.getcwd()
    
    # Auto-detect mode if no flags specified
    if not args.workspace and not args.package:
        workspace_root = find_workspace_root()
        if workspace_root and target_path == workspace_root:
            # Only use workspace mode if we're AT the workspace root
            args.workspace = True
            target_path = workspace_root
        else:
            # Use package mode if we're in a subdirectory or no workspace found
            args.package = True
    
    try:
        if args.workspace:
            if not args.path:
                target_path = find_workspace_root() or target_path
            generate_workspace_config(target_path)
        else:
            generate_package_config(target_path)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()