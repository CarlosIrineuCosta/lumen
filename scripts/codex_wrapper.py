#!/usr/bin/env python3
"""
Codex CLI wrapper for code review and security analysis
"""

import subprocess
import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Configuration
CODEX_CLI = os.getenv('CODEX_CLI_PATH', 'codex')

def call_codex(task_description, context_files=None, model=None):
    """
    Call Codex CLI with task for code review and security analysis
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

    # Create structured prompt for Codex
    prompt = f"""You are Codex, a code security and optimization expert.

Task Description:
{task_description}

Context from project files:
{context}

Please provide a comprehensive review focusing on:
1. Security vulnerabilities
2. Performance bottlenecks
3. Code quality issues
4. Optimization opportunities

Format your response as:

<review>
[Detailed code review with specific recommendations]
</review>

<security_issues>
[List any security concerns with severity levels]
</security_issues>

<optimizations>
[Suggested performance optimizations]
</optimizations>
"""

    # Build command based on available options
    cmd = [CODEX_CLI]

    if model:
        cmd.extend(['--model', model])

    # Add prompt
    cmd.extend(['--prompt', prompt])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            cwd=Path.cwd()
        )

        return {
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr,
            'command': ' '.join(cmd)
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Codex task timed out after 5 minutes',
            'output': '',
            'command': ' '.join(cmd)
        }
    except FileNotFoundError:
        return {
            'success': False,
            'error': f'Codex CLI not found at {CODEX_CLI}. Install or update CODEX_CLI_PATH.',
            'output': '',
            'command': ' '.join(cmd)
        }

def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: python codex_wrapper.py --task 'description' [--files file1.py,file2.js] [--model model-name]")
        sys.exit(1)

    task = ""
    files = []
    model = None

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '--task' and i + 1 < len(sys.argv):
            task = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--files' and i + 1 < len(sys.argv):
            files = sys.argv[i + 1].split(',')
            i += 2
        elif sys.argv[i] == '--model' and i + 1 < len(sys.argv):
            model = sys.argv[i + 1]
            i += 2
        else:
            i += 1

    if not task:
        print("Error: --task is required")
        sys.exit(1)

    result = call_codex(task, files, model)

    if result['success']:
        print(result['output'])
    else:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()