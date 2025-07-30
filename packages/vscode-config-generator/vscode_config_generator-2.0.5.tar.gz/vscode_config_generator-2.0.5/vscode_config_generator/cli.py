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

def find_package_root():
    """Find package root (first directory under src/)."""
    current_dir = os.getcwd()
    
    while current_dir != "/":
        parent_dir = os.path.dirname(current_dir)
        grandparent_dir = os.path.dirname(parent_dir)
        
        # If parent is 'src' and grandparent has 'workspace' in path
        if os.path.basename(parent_dir) == "src" and "workspace" in grandparent_dir:
            return current_dir
        current_dir = parent_dir
    return None

def is_closer_to_package():
    """Check if we're closer to a package than workspace root."""
    package_root = find_package_root()
    workspace_root = find_workspace_root()
    current_dir = os.getcwd()
    
    if not package_root or not workspace_root:
        return False
    
    # Calculate distance to each
    package_distance = len(os.path.relpath(current_dir, package_root).split('/'))
    workspace_distance = len(os.path.relpath(current_dir, workspace_root).split('/'))
    
    return package_distance <= workspace_distance

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
        if is_closer_to_package():
            # Closer to package - use package mode
            args.package = True
            package_root = find_package_root()
            if package_root:
                target_path = package_root
        else:
            # Closer to workspace - use workspace mode
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