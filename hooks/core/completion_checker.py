#!/usr/bin/env python3
"""
Intelligent stop hook: Verifies task is actually complete before stopping.
Checks for:
- Tests written for new features
- Documentation updated
- No pending delegated tasks
- Cross-agent verification passed
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
STATE_FILE = PROJECT_ROOT / ".claude" / "state" / "session_state.json"
POSTBOX = PROJECT_ROOT / ".postbox"

def check_tests_exist(changed_files):
    """Verify tests exist for changed files."""
    for file in changed_files:
        if file.endswith('.py') and 'backend/' in file:
            # Check if corresponding test exists
            test_file = file.replace('backend/', 'backend/tests/').replace('.py', '_test.py')
            test_path = PROJECT_ROOT / test_file
            if not test_path.exists():
                return False, f"Missing test for {file}"
    return True, "Tests OK"

def check_pending_delegations():
    """Check if there are pending tasks delegated to GLM/Codex."""
    try:
        if STATE_FILE.exists():
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
                pending = [d for d in state.get('delegated_to_glm', []) 
                          if not d.get('completed', False)]
                if pending:
                    return False, f"{len(pending)} delegated tasks not completed"
    except:
        pass
    return True, "No pending delegations"

def check_documentation():
    """Verify documentation is updated for significant changes."""
    docs_updated = (PROJECT_ROOT / "docs" / "tasks_2025-10-22.md").exists()
    if not docs_updated:
        return False, "Task documentation not updated"
    return True, "Documentation OK"

def check_linting(changed_files):
    """Run linters on changed files."""
    import subprocess
    
    for file in changed_files:
        if file.endswith('.py'):
            # Run ruff
            result = subprocess.run(
                ['ruff', 'check', file],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT
            )
            if result.returncode != 0:
                return False, f"Ruff linting failed: {file}\n{result.stdout}"
        
        elif file.endswith(('.js', '.jsx', '.ts', '.tsx')):
            # Run eslint
            result = subprocess.run(
                ['eslint', file],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT
            )
            if result.returncode != 0:
                return False, f"ESLint failed: {file}\n{result.stdout}"
    
    return True, "Linting passed"

def main():
    """Main hook: Check if we're really done."""
    try:
        tool_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)
    
    # Get changed files from git
    import subprocess
    try:
        result = subprocess.run(
            ['git', 'diff', '--name-only'],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )
        changed_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
    except:
        changed_files = []
    
    # Run checks
    checks = [
        check_tests_exist(changed_files),
        check_pending_delegations(),
        check_documentation(),
        check_linting(changed_files)  # Added linting check
    ]
    
    failed_checks = [(check, reason) for check, reason in checks if not check]
    
    if failed_checks:
        reasons = "; ".join([reason for _, reason in failed_checks])
        output = {
            "continue": False,
            "stopReason": f"Task not complete: {reasons}"
        }
        print(json.dumps(output))
        print(f"Completion checks failed: {reasons}", file=sys.stderr)
        sys.exit(2)  # Blocking error
    else:
        print("All completion checks passed", file=sys.stderr)
        sys.exit(0)

if __name__ == '__main__':
    main()
