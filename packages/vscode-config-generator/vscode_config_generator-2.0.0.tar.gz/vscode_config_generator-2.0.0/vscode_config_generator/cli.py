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
    
    # Default to package mode if no flags specified
    if not args.workspace and not args.package:
        args.package = True
    
    if args.path:
        target_path = args.path
    elif args.workspace:
        target_path = find_workspace_root()
        if not target_path:
            print("Error: Could not find workspace root")
            sys.exit(1)
    else:
        target_path = os.getcwd()
    
    try:
        if args.workspace:
            generate_workspace_config(target_path)
        else:
            generate_package_config(target_path)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()