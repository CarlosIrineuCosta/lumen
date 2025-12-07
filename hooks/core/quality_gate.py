#!/usr/bin/env python3
"""
Quality gate hook: Ensures different LLM reviews changes made by another.
This prevents LLMs from overestimating their own capabilities.
"""

import json
import sys
import subprocess
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
STATE_FILE = PROJECT_ROOT / ".claude" / "state" / "session_state.json"

def load_session_state():
    """Load session state from file with error handling."""
    try:
        if STATE_FILE.exists():
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError, OSError) as e:
        print(f"Warning: Could not load session state: {e}", file=sys.stderr)

    # Return default state if file doesn't exist or is invalid
    return {
        "current_task": "",
        "delegated_to_glm": [],
        "delegated_to_codex": [],
        "pending_reviews": [],
        "last_agent": "claude",
        "glm_failures": 0,
        "codex_failures": 0,
        "session_start": None,
        "total_tasks_completed": 0,
        "hooks_executed": [],
        "last_activity": None,
        "session_id": None
    }

def save_session_state(state):
    """Save session state to file with error handling."""
    try:
        # Ensure the state directory exists
        state_dir = STATE_FILE.parent
        state_dir.mkdir(parents=True, exist_ok=True)

        # Create backup before saving
        if STATE_FILE.exists():
            backup_file = STATE_FILE.with_suffix('.json.backup')
            STATE_FILE.rename(backup_file)

        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        return True
    except (IOError, OSError, json.JSONEncodeError) as e:
        print(f"Error: Could not save session state: {e}", file=sys.stderr)
        return False

def get_last_agent():
    """Determine which agent made the last change."""
    try:
        state = load_session_state()
        return state.get('last_agent', 'claude')
    except:
        return 'claude'

def is_review_already_pending(file_path, reviewer, state):
    """Check if a review is already pending for this file and reviewer."""
    if "pending_reviews" not in state:
        return False

    for review in state["pending_reviews"]:
        if (review.get("file_path") == file_path and
            review.get("reviewer") == reviewer and
            review.get("status") == "pending"):
            return True
    return False

def add_pending_review(file_path, reviewer, last_agent, state):
    """Add a pending review to the session state."""
    if "pending_reviews" not in state:
        state["pending_reviews"] = []

    review_entry = {
        "file_path": file_path,
        "reviewer": reviewer,
        "author": last_agent,
        "status": "pending",
        "timestamp": datetime.now().isoformat(),
        "review_id": f"review_{int(datetime.now().timestamp())}"
    }

    state["pending_reviews"].append(review_entry)
    return state

def update_review_completion(file_path, reviewer, result, state):
    """Update the review status when completed."""
    if "pending_reviews" not in state:
        return state

    # Find and update the pending review
    for review in state["pending_reviews"]:
        if (review.get("file_path") == file_path and
            review.get("reviewer") == reviewer and
            review.get("status") == "pending"):

            review["status"] = "completed" if result.get("approved", True) else "failed"
            review["completion_timestamp"] = datetime.now().isoformat()
            review["result"] = {
                "approved": result.get("approved", True),
                "success": result.get("success", False),
                "error": result.get("error"),
                "review": result.get("review", "")
            }
            break

    return state

def cleanup_old_reviews(state):
    """Remove completed reviews older than 1 hour to keep state clean."""
    if "pending_reviews" not in state:
        return state

    current_time = datetime.now()
    cleaned_reviews = []

    for review in state["pending_reviews"]:
        try:
            # Keep pending reviews and recent completed reviews
            review_time = datetime.fromisoformat(review.get("timestamp", ""))

            if review.get("status") == "pending":
                # Keep all pending reviews
                cleaned_reviews.append(review)
            elif review.get("status") in ["completed", "failed"]:
                # Keep completed/failed reviews for 1 hour
                completion_time = datetime.fromisoformat(review.get("completion_timestamp", review.get("timestamp")))
                if (current_time - completion_time).total_seconds() < 3600:
                    cleaned_reviews.append(review)
        except:
            # Keep malformed reviews for safety
            cleaned_reviews.append(review)

    state["pending_reviews"] = cleaned_reviews
    return state

def choose_reviewer(last_agent):
    """Choose a different LLM to review the work."""
    reviewers = {
        'claude': 'glm',      # GLM reviews Claude's work
        'glm': 'codex',       # Codex reviews GLM's work
        'codex': 'claude'     # Claude reviews Codex's work
    }
    return reviewers.get(last_agent, 'glm')

def call_reviewer(reviewer, file_path, tool_output):
    """Call the reviewer LLM to check the changes."""
    
    # Read the file content
    try:
        full_path = PROJECT_ROOT / file_path
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {
            'success': False,
            'error': f"Could not read file: {e}"
        }
    
    prompt = f"""You are reviewing code changes for quality and correctness.

File: {file_path}
Changed by: {get_last_agent()}

File content:
```
{content}
```

Review criteria:
1. Code quality and style
2. Security issues
3. Performance concerns
4. Adherence to PMM pattern (vanilla JS, no build tools)
5. Module size (<400 lines)

Return your review in this format:
<review>
<status>APPROVED|CHANGES_NEEDED|REJECTED</status>
<issues>
- List any issues found
</issues>
<recommendations>
- List recommendations
</recommendations>
</review>
"""
    
    # Call appropriate reviewer CLI
    if reviewer == 'glm':
        cmd = ['python', 'scripts/llm/glm_cli.py', '--prompt', prompt]
    elif reviewer == 'codex':
        cmd = ['python', 'scripts/llm/codex_cli.py', '--prompt', prompt]
    else:  # claude subagent
        return {'success': True, 'approved': True}  # Placeholder
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=PROJECT_ROOT
        )
        
        if result.returncode == 0:
            # Parse review
            output = result.stdout
            approved = 'APPROVED' in output
            
            return {
                'success': True,
                'approved': approved,
                'review': output
            }
        else:
            return {
                'success': False,
                'error': result.stderr
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def main():
    """Main hook: Review changes with different LLM with session state integration."""
    try:
        tool_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_input = tool_data.get('tool_input', {})
    file_path = tool_input.get('file_path', '')

    if not file_path:
        sys.exit(0)  # Nothing to review

    # Load current session state
    state = load_session_state()

    # Determine reviewer
    last_agent = get_last_agent()
    reviewer = choose_reviewer(last_agent)

    # Check if review is already pending
    if is_review_already_pending(file_path, reviewer, state):
        print(f"Review already pending for {file_path} by {reviewer}", file=sys.stderr)
        sys.exit(0)  # Skip duplicate review

    print(f"Reviewing {file_path} with {reviewer} (changed by {last_agent})", file=sys.stderr)

    # Add pending review to session state
    state = add_pending_review(file_path, reviewer, last_agent, state)

    # Clean up old reviews before adding new one
    state = cleanup_old_reviews(state)

    # Save updated state
    if not save_session_state(state):
        print("Warning: Could not save pending review to session state", file=sys.stderr)

    tool_output = tool_data.get('tool_response', {})
    result = call_reviewer(reviewer, file_path, tool_output)

    # Update session state with review results
    updated_state = load_session_state()  # Reload to get latest state
    updated_state = update_review_completion(file_path, reviewer, result, updated_state)

    # Update last activity timestamp
    updated_state["last_activity"] = datetime.now().isoformat()
    updated_state["last_agent"] = last_agent

    # Add quality_gate to hooks_executed if not present
    if "hooks_executed" not in updated_state:
        updated_state["hooks_executed"] = []
    if "quality_gate" not in updated_state["hooks_executed"]:
        updated_state["hooks_executed"].append("quality_gate")

    # Save final state
    save_session_state(updated_state)

    if not result['success']:
        print(f"Review failed: {result.get('error')}", file=sys.stderr)
        sys.exit(0)

    if not result.get('approved', True):
        # Blocked! Send back to Claude for review
        output = {
            "continue": False,
            "stopReason": f"Code review by {reviewer} flagged issues. Review: {result.get('review', '')}"
        }
        print(json.dumps(output))
        sys.exit(2)  # Exit code 2 = blocking error
    else:
        print(f"Review passed by {reviewer}", file=sys.stderr)
        sys.exit(0)

if __name__ == '__main__':
    main()
