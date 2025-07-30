#!/usr/bin/env python3

import os
import sys
from .generator import generate_workspace_file

def find_workspace_root():
    """Find workspace root by looking for src directory."""
    current_dir = os.getcwd()
    while current_dir != "/":
        if os.path.isdir(os.path.join(current_dir, "src")):
            return current_dir
        current_dir = os.path.dirname(current_dir)
    return None

def main():
    """Main CLI entry point."""
    if len(sys.argv) > 1:
        workspace_path = sys.argv[1]
    else:
        workspace_path = find_workspace_root()
        if not workspace_path:
            print("Error: Could not find workspace root (directory containing 'src' folder)")
            sys.exit(1)

    try:
        output_file = generate_workspace_file(workspace_path)
        print(f"Generated workspace file: {output_file}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()