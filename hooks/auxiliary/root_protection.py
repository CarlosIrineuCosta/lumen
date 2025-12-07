#!/usr/bin/env python3
"""
Root Directory Protection Hook
Prevents creation of documentation files in project root
Enforces documentation organization standards
"""

import json
import sys
import os
from pathlib import Path

def parse_tool_input():
    """Parse tool input from stdin"""
    try:
        tool_data = json.load(sys.stdin)
        return tool_data
    except json.JSONDecodeError:
        return None

def check_root_violation(tool_input):
    """Check if operation would create docs in root"""
    if not tool_input:
        return False

    # Get file paths from tool input
    file_paths = []

    if 'files' in tool_input:
        file_paths.extend(tool_input['files'])

    if 'tool_name' in tool_input and 'paths' in tool_input:
        if tool_input['tool_name'] in ['Write', 'Edit']:
            file_paths.extend(tool_input['paths'])

    # Check for documentation files in root
    project_root = Path('.')
    violations = []

    for file_path in file_paths:
        path = Path(file_path)

        # Check if it's a documentation file
        if path.suffix.lower() == '.md':
            # Check if it's in root directory
            if path.parent == project_root or str(path).startswith('./'):
                violations.append(str(path))

    return violations

def main():
    """Main hook execution"""
    tool_input = parse_tool_input()
    if not tool_input:
        sys.exit(0)

    violations = check_root_violation(tool_input)

    if violations:
        print("❌ ROOT DIRECTORY VIOLATION DETECTED!", file=sys.stderr)
        print("Documentation files must NOT be created in project root.", file=sys.stderr)
        print(f"Violating files: {', '.join(violations)}", file=sys.stderr)
        print("", file=sys.stderr)
        print("Allowed locations for documentation:", file=sys.stderr)
        print("- docs/ (main documentation)", file=sys.stderr)
        print("- docs/core/ (core documentation)", file=sys.stderr)
        print("- docs/reports/ (generated reports)", file=sys.stderr)
        print("- docs/tasks/ (task documentation)", file=sys.stderr)
        print("- docs/analysis/ (analysis documents)", file=sys.stderr)
        print("- docs/coordination/ (coordination docs)", file=sys.stderr)
        print("- .claude/ (Claude-specific files)", file=sys.stderr)
        print("", file=sys.stderr)
        print("Please move your documentation to an appropriate directory.", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)

if __name__ == '__main__':
    main()