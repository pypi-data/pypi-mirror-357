#!/usr/bin/env python3

import argparse
import os
import sys
from .generator import generate_workspace_config, generate_package_config

def find_workspace_root():
    """Find workspace root by looking for workspace pattern."""
    current_dir = os.getcwd()
    
    # Look for the pattern: /path/workspace/WORKSPACE_NAME/
    while current_dir != "/":
        parent_dir = os.path.dirname(current_dir)
        grandparent_dir = os.path.dirname(parent_dir)
        
        # If grandparent contains 'workspace' and current has 'src'
        if "workspace" in grandparent_dir and os.path.isdir(os.path.join(current_dir, "src")):
            return current_dir
        current_dir = parent_dir
    return None

def find_package_root():
    """Find package root (first directory under src/)."""
    cwd = os.getcwd()
    parts = cwd.split('/')
    
    # Find 'src' in the path
    for i, part in enumerate(parts):
        if part == "src" and i + 1 < len(parts):
            # Return the first directory after src
            package_path = '/'.join(parts[:i+2])
            return package_path
    return None

def is_in_package():
    """Check if current path contains /src/packagename/."""
    cwd = os.getcwd()
    parts = cwd.split('/')
    
    # Look for pattern: .../src/packagename/...
    for i, part in enumerate(parts):
        if part == "src" and i + 1 < len(parts):
            return True
    return False

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
        if is_in_package():
            # In package - use package mode
            args.package = True
            package_root = find_package_root()
            if package_root:
                target_path = package_root
        else:
            # Not in package - use workspace mode
            args.workspace = True
            workspace_root = find_workspace_root()
            if workspace_root:
                target_path = workspace_root
    
    try:
        if args.workspace:
            if not args.path:
                workspace_root = find_workspace_root()
                if workspace_root:
                    target_path = workspace_root
            generate_workspace_config(target_path)
        else:
            # Package mode
            if not args.path:
                package_root = find_package_root()
                if package_root:
                    target_path = package_root
            generate_package_config(target_path)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()