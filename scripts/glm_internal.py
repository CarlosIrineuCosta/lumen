#!/usr/bin/env python3
"""
Internal GLM caller using Claude Code's Task tool
Routes GLM requests through the same mechanism Claude Code uses internally
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime

def call_glm_internal(task_description, context_files=None):
    """
    Call GLM internally through Claude Code's Task tool
    This uses the same internal mechanism as when Claude Code calls other models
    """
    if context_files is None:
        context_files = []

    # Build context from files
    context = ""
    for file_path in context_files:
        try:
            full_path = Path(file_path)
            if full_path.exists():
                with open(full_path, 'r', encoding='utf-8') as f:
                    context += f"\n\n=== {file_path} ===\n{f.read()}"
        except Exception as e:
            context += f"\n\n=== {file_path} (Error reading: {e}) ===\n"

    # Create a structured prompt that would be sent to GLM
    prompt = f"""You are GLM (glm-4.5-flash), an AI assistant helping with the Lumen project.

Task: {task_description}

{context if context else ''}

Please provide a response following this format:

<analysis>
[Your analysis and approach]
</analysis>

<implementation>
[Any code or implementation details]
</implementation>

<files_to_change>
[List any files that need to be modified]
</files_to_change>

<test_commands>
[Commands to test the implementation]
</test_commands>
"""

    # In the actual Claude Code environment, this would trigger the Task tool
    # For now, we'll create a placeholder that Claude Code can execute
    return {
        'requires_claude_code': True,
        'prompt': prompt,
        'model': 'glm-4.5-flash',
        'task': task_description,
        'context_files': context_files
    }

def main():
    """CLI entry point - when called from outside Claude Code"""
    if len(sys.argv) < 2:
        print("Usage: python glm_internal.py --task 'description' [--files file1.py,file2.js]")
        print("Note: This script is designed to be called from within Claude Code")
        sys.exit(1)

    task = ""
    files = []

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '--task' and i + 1 < len(sys.argv):
            task = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--files' and i + 1 < len(sys.argv):
            files = sys.argv[i + 1].split(',')
            i += 2
        else:
            i += 1

    if not task:
        print("Error: --task is required")
        sys.exit(1)

    result = call_glm_internal(task, files)

    # Return the structured prompt that Claude Code can use
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()