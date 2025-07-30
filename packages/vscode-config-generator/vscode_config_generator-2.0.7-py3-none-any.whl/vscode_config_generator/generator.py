#!/usr/bin/env python3

import json
import os

def generate_workspace_config(workspace_path):
    """Generate VS Code workspace file for multi-package project."""
    workspace_name = os.path.basename(workspace_path)
    
    # Check for src directory first, fallback to direct child directories
    src_path = os.path.join(workspace_path, "src")
    if os.path.exists(src_path):
        packages = sorted([d for d in os.listdir(src_path) 
                          if os.path.isdir(os.path.join(src_path, d))])
        folder_base = "src"
    else:
        # Use direct child directories as packages
        packages = sorted([d for d in os.listdir(workspace_path) 
                          if os.path.isdir(os.path.join(workspace_path, d)) and not d.startswith('.')])
        folder_base = "."

    workspace_config = {
        "folders": [
            {
                "name": f"📦 {package}",
                "path": f"{folder_base}/{package}" if folder_base != "." else package
            }
            for package in packages
        ],
        "launch": {
            "version": "0.2.0",
            "configurations": [
                {
                    "name": "Python Debugger: Remote Attach Service Tests",
                    "type": "debugpy",
                    "request": "attach",
                    "connect": {
                        "host": "localhost",
                        "port": 5678
                    },
                    "justMyCode": False,
                    "pathMappings": [
                        {
                            "localRoot": f"${{workspaceFolder:📦 {package}}}",
                            "remoteRoot": f"{folder_base}/{package}" if folder_base != "." else package
                        }
                        for package in packages
                    ]
                }
            ]
        }
    }

    output_file = os.path.join(workspace_path, f"{workspace_name}.code-workspace")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(workspace_config, f, indent=4, ensure_ascii=False)

    print(f"Generated workspace file: {output_file}")
    print("\n📝 To use remote debugging, add this to your Python code:")
    print('import debugpy; debugpy.listen(5678);print("🛑 Waiting for debugger to attach on port 5678...");debugpy.wait_for_client()')

def generate_package_config(package_path):
    """Generate VS Code launch.json for single package."""
    package_name = os.path.basename(package_path)
    vscode_dir = os.path.join(package_path, ".vscode")
    os.makedirs(vscode_dir, exist_ok=True)
    
    launch_config = {
        "version": "0.2.0",
        "configurations": [
            {
                "name": f"Python Debugger: Remote Attach Service Tests ({package_name})",
                "type": "debugpy",
                "request": "attach",
                "connect": {
                    "host": "localhost",
                    "port": 5678
                },
                "justMyCode": False,
                "pathMappings": [
                    {
                        "localRoot": "${workspaceFolder}",
                        "remoteRoot": "."
                    }
                ]
            }
        ]
    }
    
    output_file = os.path.join(vscode_dir, "launch.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(launch_config, f, indent=4, ensure_ascii=False)
    
    print(f"Generated launch config: {output_file}")
    print("\\n📝 To use remote debugging, add this to your Python code:")
    print('import debugpy; debugpy.listen(5678);print("🛑 Waiting for debugger to attach on port 5678...");debugpy.wait_for_client()')