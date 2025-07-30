# Workspace Generator

Generate VS Code workspace files for multi-package projects.

## Installation

```bash
pip install vscode_workspace_config_generator
```

## Usage

```bash
# Generate VS Code workspace config for current directory (auto-detect workspace root)
generate-vscode-workspace-config

# Generate VS Code workspace config for specific directory
generate-vscode-workspace-config /path/to/workspace
```

## What it does

- Scans the `src/` directory for packages
- Creates a `.code-workspace` file with folder configurations
- Includes debug configuration for Python remote debugging

## Remote Debugging Setup

To use the remote debugger configuration, add this code to your Python script:

```python
import debugpy; debugpy.listen(5678);print("🛑 Waiting for debugger to attach on port 5678...");debugpy.wait_for_client()
```