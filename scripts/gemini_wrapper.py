#!/usr/bin/env python3
"""
Gemini CLI wrapper for large context analysis (up to 1M tokens)
"""

import subprocess
import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Configuration
GEMINI_CLI = os.getenv('GEMINI_CLI_PATH', 'gemini')

def call_gemini(task_description, context_files=None, model='gemini-1.5-pro'):
    """
    Call Gemini CLI with support for large context (up to 1M tokens)
    """
    if context_files is None:
        context_files = []

    # Build context from files
    context = ""
    total_size = 0

    for file_path in context_files:
        try:
            full_path = Path(file_path)
            if full_path.exists():
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    context += f"\n\n=== {file_path} ===\n{content}"
                    total_size += len(content)
        except Exception as e:
            context += f"\n\n=== {file_path} (Error reading: {e}) ===\n"

    # Create structured prompt for Gemini
    prompt = f"""You are Gemini, a large-context AI analyst with access to 1M token context.

Task Description:
{task_description}

Context from project files ({len(context_files)} files, ~{total_size//1000}k tokens):
{context}

Please provide comprehensive analysis:

<analysis>
[Your detailed analysis of the entire codebase or task]
</analysis>

<documentation>
[Generate or update documentation as needed]
</documentation>

<tests>
[Create comprehensive tests for the code]
</tests>

<findings>
[Key findings and recommendations]
</findings>

Note: You have access to the full context, so please provide holistic insights.
"""

    # Build command with large context support
    cmd = [GEMINI_CLI, '--model', model, '--max-tokens', '800000']

    # Add prompt
    cmd.extend(['--prompt', prompt])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout for large context
            cwd=Path.cwd()
        )

        return {
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr,
            'command': ' '.join(cmd),
            'context_size': total_size
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Gemini task timed out after 10 minutes (large context)',
            'output': '',
            'command': ' '.join(cmd)
        }
    except FileNotFoundError:
        return {
            'success': False,
            'error': f'Gemini CLI not found at {GEMINI_CLI}. Install or update GEMINI_CLI_PATH.',
            'output': '',
            'command': ' '.join(cmd)
        }

def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: python gemini_wrapper.py --task 'description' [--files file1.py,file2.js,...] [--model model-name]")
        sys.exit(1)

    task = ""
    files = []
    model = 'gemini-1.5-pro'

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

    # For large context, automatically include entire project if no files specified
    if not files:
        print("Warning: No files specified. Gemini will analyze entire project.")
        # Find all relevant source files
        for pattern in ['**/*.py', '**/*.js', '**/*.ts', '**/*.json', '**/*.md']:
            files.extend(Path.cwd().glob(pattern))
        files = [str(f) for f in files if '.git' not in str(f) and 'node_modules' not in str(f)]

    result = call_gemini(task, files, model)

    if result['success']:
        print(result['output'])
        print(f"\n--- Analysis Summary ---", file=sys.stderr)
        print(f"Files analyzed: {len(files)}", file=sys.stderr)
        print(f"Context size: ~{result.get('context_size', 0)//1000}k tokens", file=sys.stderr)
    else:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()