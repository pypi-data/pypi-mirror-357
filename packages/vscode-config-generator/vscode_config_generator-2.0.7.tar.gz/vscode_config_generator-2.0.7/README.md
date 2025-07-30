# VS Code Config Generator

Generate VS Code configurations for projects.

## Installation

```bash
pip install vscode_config_generator
```

## Usage

```bash
# Generate package config (default) - creates .vscode/launch.json
generate-vscode-config

# Generate workspace config - creates .code-workspace file
generate-vscode-config --workspace

# Specify path
generate-vscode-config --package /path/to/package
generate-vscode-config --workspace /path/to/workspace
```

## Remote Debugging Setup

To use the remote debugger configuration, add this code to your Python script:

```python
import debugpy; debugpy.listen(5678);print("🛑 Waiting for debugger to attach on port 5678...");debugpy.wait_for_client()
```