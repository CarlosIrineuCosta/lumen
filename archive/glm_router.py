#!/usr/bin/env python3
"""
Routes appropriate tasks to GLM CLI for implementation.
GLM handles: testing, documentation, well-defined implementations, repetitive work.
"""

import json
import sys
import subprocess
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
STATE_FILE = PROJECT_ROOT / ".claude" / "state" / "session_state.json"

def should_delegate_to_glm(tool_input):
    """
    Decide if task should go to GLM based on task characteristics.
    GLM is good at: testing, documentation, well-defined implementations.
    """
    description = tool_input.get('description', '').lower()
    
    # Keywords that indicate GLM-suitable work
    glm_keywords = [
        'test', 'testing', 'pytest', 'unittest',
        'documentation', 'docs', 'readme',
        'implement', 'create component',  'refactor',
        'quality assurance', 'validation', 'verify'
    ]
    
    # Keywords that indicate work should stay with Claude
    claude_keywords = [
        'architecture', 'design', 'plan',
        'authentication', 'security', 'auth',
        'router', 'state management', 'coordination'
    ]
    
    # Check for Claude-specific work first
    if any(kw in description for kw in claude_keywords):
        return False
    
    # Check for GLM-suitable work
    if any(kw in description for kw in glm_keywords):
        return True
    
    return False

def call_glm(task_description, context_files=None):
    """
    Call GLM CLI with task. Adjust command based on your GLM setup.
    """
    if context_files is None:
        context_files = []
    
    # Build context from files
    context = ""
    for file_path in context_files:
        try:
            full_path = PROJECT_ROOT / file_path
            if full_path.exists():
                with open(full_path, 'r', encoding='utf-8') as f:
                    context += f"\n\n=== {file_path} ===\n{f.read()}"
        except Exception as e:
            context += f"\n\n=== {file_path} (Error reading: {e}) ===\n"
    
    # Create structured prompt for GLM
    prompt = f"""You are implementing a task for the Lumen project.

Task Description:
{task_description}

Context from project files:
{context}

Please implement this task following these guidelines:
1. Use vanilla JavaScript (no React/Vue/build tools)
2. Follow PMM (Poor Man's Modules) pattern with window.Lumen* objects
3. Keep modules under 400 lines
4. Return your response in this XML format:

<implementation>
[Your code here]
</implementation>

<files_changed>
path/to/file1.js
path/to/file2.py
</files_changed>

<explanation>
[Brief explanation of what you did]
</explanation>

<test_commands>
[Commands to verify the implementation]
</test_commands>

<needs_review>
[Any areas that need architectural review or decisions]
</needs_review>
"""
    
    # TODO: Adjust this command based on how YOU invoke GLM CLI
    # Example possibilities:
    # glm_command = ['glm', 'chat', '--prompt', prompt]
    # glm_command = ['python', '-m', 'glm', 'chat', prompt]
    # glm_command = ['glm-cli', '--model', 'glm-4', '--input', '-']
    
    # Call the GLM worker script
    glm_command = ['python', 'scripts/agents/glm_worker.py', '--task', task_desc[:200]]
    
    try:
        result = subprocess.run(
            glm_command,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            cwd=PROJECT_ROOT
        )
        
        return {
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr,
            'command': ' '.join(glm_command)
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'GLM task timed out after 5 minutes',
            'output': '',
            'command': ' '.join(glm_command)
        }
    except FileNotFoundError:
        return {
            'success': False,
            'error': 'GLM worker not found. Check scripts/agents/glm_worker.py exists.',
            'output': '',
            'command': ' '.join(glm_command)
        }

def log_delegation(task_desc, result):
    """Log delegation to state file for tracking."""
    try:
        if STATE_FILE.exists():
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
        else:
            state = {'delegated_to_glm': [], 'glm_failures': 0}
        
        delegation_record = {
            'timestamp': time.time(),
            'task': task_desc,
            'success': result['success'],
            'error': result.get('error', '')
        }
        
        state['delegated_to_glm'].append(delegation_record)
        if not result['success']:
            state['glm_failures'] = state.get('glm_failures', 0) + 1
        
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not log delegation: {e}", file=sys.stderr)

def main():
    """
    Main hook entry point.
    Reads tool input from stdin, decides if GLM should handle it.
    """
    try:
        tool_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        print("Error: Could not parse tool input JSON", file=sys.stderr)
        sys.exit(0)  # Don't block Claude if we can't parse
    
    tool_input = tool_data.get('tool_input', {})
    
    # Decide if we should delegate
    if not should_delegate_to_glm(tool_input):
        # Let Claude handle it
        sys.exit(0)
    
    # Delegate to GLM
    task_desc = tool_input.get('description', 'No description provided')
    context_files = tool_input.get('context_files', [])
    
    print(f"Delegating task to GLM: {task_desc[:100]}...", file=sys.stderr)
    
    result = call_glm(task_desc, context_files)
    
    log_delegation(task_desc, result)
    
    if result['success']:
        # Parse GLM's response and inject it as modified tool input
        output = {
            "continue": True,
            "modifiedInput": {
                **tool_input,
                "glm_response": result['output'],
                "note": "Task delegated to GLM"
            }
        }
        print(json.dumps(output))
        sys.exit(0)
    else:
        # GLM failed, let Claude try
        error_msg = f"GLM delegation failed: {result['error']}. Claude will handle this task."
        output = {
            "continue": True,
            "suppressOutput": False
        }
        print(json.dumps(output), file=sys.stdout)
        print(error_msg, file=sys.stderr)
        sys.exit(0)

if __name__ == '__main__':
    main()
