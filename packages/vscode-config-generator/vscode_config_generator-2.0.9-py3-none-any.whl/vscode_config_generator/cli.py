#!/usr/bin/env python3

import argparse
import os
import sys
from .generator import generate_workspace_config, generate_package_config

def find_workspace_root(cwd=None):
    """Find workspace root by looking for workspace pattern."""
    if not cwd:
        cwd = os.getcwd()
    parts = [part for part in cwd.split('/') if part != ""] 
    for i, part in enumerate(parts): 
        if part.lower() in ["workspace","workplace"]: 
            return "/" + "/".join(parts[:i+2]) if i+1 < len(parts) else None 
    return None 

def find_package_root(cwd = None): 
    """Find package root (first directory under src/)."""
    if not cwd:
        cwd = os.getcwd()
    parts = [part for part in cwd.split('/') if part != ""] 
    for i, part in enumerate(parts): 
        if part.lower() in ["workspace","workplace"]: 
            return "/" + "/".join(parts[:i+4]) if i+3 < len(parts) else None 
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
    
    # Check for conflicting flags
    if args.workspace and args.package:
        print("Error: Cannot specify both --workspace and --package flags")
        sys.exit(1)
    
    # Auto-detect mode if no flags specified
    if not args.workspace and not args.package:
        package_root = find_package_root()
        workspace_root = find_workspace_root()
        if package_root:
            # In package - use package mode
            args.package = True
            target_path = package_root
        elif workspace_root:
            # In workspace - use workspace mode
            args.workspace = True
            target_path = workspace_root
    if args.package:
        if not args.path:
            package_root = find_package_root(args.path)
        else:
            package_root = find_package_root()
        target_path = package_root
    elif args.workspace:
        if args.path:
            workspace_root = find_workspace_root(args.path)
        else:
            workspace_root = find_workspace_root()
        target_path = workspace_root
    try:
        if not target_path:
            # If we get here, couldn't find appropriate root
            print("Error: Could not determine workspace or package root")
            sys.exit(1)
        generate_package_config(target_path)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()