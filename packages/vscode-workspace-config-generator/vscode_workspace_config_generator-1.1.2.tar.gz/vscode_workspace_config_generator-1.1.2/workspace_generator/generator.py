#!/usr/bin/env python3

import json
import os
from pathlib import Path

def generate_workspace_file(workspace_path):
    """Generate VS Code workspace file for a multi-package project."""
    workspace_name = os.path.basename(workspace_path)
    
    src_path = os.path.join(workspace_path, "src")
    if not os.path.exists(src_path):
        raise FileNotFoundError(f"src directory not found in {workspace_path}")

    packages = sorted([d for d in os.listdir(src_path) 
                      if os.path.isdir(os.path.join(src_path, d))])

    workspace_config = {
        "folders": [
            {
                "name": f"📦 {package}",
                "path": f"src/{package}"
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
                            "remoteRoot": f"src/{package}"
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
    
    return output_file