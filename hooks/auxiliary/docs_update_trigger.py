#!/usr/bin/env python3
"""
Documentation Update Trigger Hook
Automatically triggers documentation review after code modifications
Ensures code changes are properly documented

This hook runs after Edit/Write operations to:
1. Identify modified files
2. Determine if documentation needs updating
3. Trigger /docs_review if documentation is affected
4. Update .claude/tasks.json with tracking
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
import subprocess
from typing import List, Dict, Set, Optional

# Project root
PROJECT_ROOT = Path(__file__).parent.parent

# Paths to monitor for documentation updates
DOC_PATHS = {
    'backend': ['app/api', 'app/services', 'app/models', 'app/storage'],
    'frontend': ['js/modules', 'js/components'],
    'scripts': ['agents', 'llm'],
    'docs': ['core', 'reports', 'tasks', 'analysis', 'coordination'],
    '.claude': ['commands', 'hooks']
}

# File patterns that require documentation updates
DOC_REQUIRED_PATTERNS = [
    'endpoint', 'router', 'model', 'service', 'handler',
    'component', 'module', 'config', 'schema'
]

# Files that always need documentation check
CRITICAL_FILES = [
    'README.md',
    'ARCHITECTURE.md',
    'API.md',
    'DEVELOPMENT.md',
    'DEPLOYMENT.md',
    'CHANGELOG.md'
]

def parse_tool_input():
    """Parse tool input from stdin"""
    try:
        tool_data = json.load(sys.stdin)
        return tool_data
    except json.JSONDecodeError as e:
        print(f"Error parsing tool input: {e}", file=sys.stderr)
        return None

def get_modified_files(tool_input: Dict) -> List[str]:
    """Get list of modified files from tool input"""
    modified_files = []

    # From files parameter
    if 'files' in tool_input:
        modified_files.extend(tool_input['files'])

    # From tool_name and paths
    if 'tool_name' in tool_input and 'paths' in tool_input:
        tool_name = tool_input['tool_name']
        paths = tool_input['paths']

        if tool_name in ['Edit', 'Write']:
            for path in paths:
                modified_files.append(str(path))

    return list(set(modified_files))

def documentation_affected(files: List[str]) -> bool:
    """Check if documentation needs updating based on modified files"""
    if not files:
        return False

    for file_path in files:
        # Check if it's a critical file
        if any(file_path.endswith(f) for f in CRITICAL_FILES):
            return True

        # Check if file path contains documentation-relevant patterns
        abs_path = os.path.join(PROJECT_ROOT, file_path)
        for pattern in DOC_REQUIRED_PATTERNS:
            if pattern in file_path.lower():
                return True

        # Check if file is in monitored directories
        for doc_path, subdirs in DOC_PATHS.items():
            if file_path.startswith(doc_path + '/'):
                # Check if any subdirectory matches
                if any(subdir in file_path for subdir in subdirs):
                    return True

    return False

def create_docs_review_task(modified_files: List[str], auto_trigger: bool = False) -> Optional[str]:
    """Create a documentation review task"""
    task_id = f"docs_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    task_file = PROJECT_ROOT / '.claude' / 'tasks' / f"{task_id}.json"

    # Ensure tasks directory exists
    task_file.parent.mkdir(parents=True, exist_ok=True)

    task_data = {
        'id': task_id,
        'timestamp': datetime.now().isoformat(),
        'description': f'Documentation review for {len(modified_files)} modified files',
        'status': 'pending',
        'modified_files': modified_files,
        'auto_trigger': auto_trigger,
        'priority': 'high'
    }

    # Write task file
    with open(task_file, 'w') as f:
        json.dump(task_data, f, indent=2)

    return task_id

def update_main_tasks(task_id: str):
    """Update main tasks.json with new task"""
    tasks_file = PROJECT_ROOT / '.claude' / 'tasks.json'

    tasks = []
    if tasks_file.exists():
        with open(tasks_file, 'r') as f:
            tasks = json.load(f)

    # Add new task
    tasks.append({
        'id': task_id,
        'timestamp': datetime.now().isoformat(),
        'description': f'Trigger documentation review (task: {task_id})',
        'status': 'completed',
        'triggered_by': 'auto_hook',
        'agent': 'docs_update_trigger.py'
    })

    # Write back
    with open(tasks_file, 'w') as f:
        json.dump(tasks, f, indent=2)

def trigger_docs_review(auto_trigger: bool = False, force: bool = False):
    """Trigger the /docs_review slash command"""
    if not force and not auto_trigger:
        return

    print("📝 Triggering documentation review...", file=sys.stderr)

    # Run docs review script directly
    cmd = [str(PROJECT_ROOT / 'commands' / 'docs_review.sh'), 'docs/core']

    if auto_trigger:
        cmd.append('--auto-update')

    try:
        # Change to project root
        original_dir = os.getcwd()
        os.chdir(PROJECT_ROOT)

        subprocess.run(cmd, capture_output=True, check=False)
        print("📋 Documentation review completed", file=sys.stderr)

        # Change back to original directory
        os.chdir(original_dir)
    except subprocess.CalledProcessError as e:
        print(f"Warning: Could not trigger docs_review: {e}", file=sys.stderr)
    except FileNotFoundError:
        # Try with absolute path
        try:
            subprocess.run(['/home/cdc/.claude/commands/docs_review.sh', 'docs/core'],
                          capture_output=True, check=False)
            print("📋 Documentation review completed (via absolute path)", file=sys.stderr)
        except Exception as e:
            print(f"Warning: Could not trigger docs_review: {e}", file=sys.stderr)

def main():
    """Main hook execution"""
    tool_input = parse_tool_input()
    if not tool_input:
        print("No tool input received", file=sys.stderr)
        sys.exit(0)

    # Get modified files
    modified_files = get_modified_files(tool_input)

    if not modified_files:
        sys.exit(0)  # No changes, nothing to do

    # Check if documentation is affected
    if documentation_affected(modified_files):
        # Create documentation review task
        task_id = create_docs_review_task(modified_files, auto_trigger=True)

        # Update main tasks tracking
        update_main_tasks(task_id)

        # Auto-trigger documentation review
        trigger_docs_review(auto_trigger=True)
    else:
        # File changes don't affect documentation
        print("📝 Code changes don't require documentation updates", file=sys.stderr)

if __name__ == '__main__':
    main()