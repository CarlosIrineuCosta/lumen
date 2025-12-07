#!/usr/bin/env python3
"""
Session tracker hook: Manages session state and tracks agent activity.
Handles:
- Session initialization and updates
- Agent activity tracking
- Cross-agent review monitoring
- Session lifecycle management
- Hook execution tracking
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Project configuration
# Calculate project root relative to the hook location
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
STATE_FILE = PROJECT_ROOT / ".claude" / "state" / "session_state.json"
HOOKS_LOG_FILE = PROJECT_ROOT / ".claude" / "state" / "hooks_log.json"

def ensure_state_directory():
    """Ensure the state directory exists."""
    state_dir = STATE_FILE.parent
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir

def load_session_state():
    """Load session state from file with error handling."""
    default_state = {
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

    try:
        if STATE_FILE.exists():
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)
                # Merge with default to ensure all fields exist
                for key, value in default_state.items():
                    if key not in state:
                        state[key] = value
                return state
        else:
            return default_state
    except (json.JSONDecodeError, IOError, OSError) as e:
        print(f"Warning: Could not load session state: {e}", file=sys.stderr)
        return default_state

def save_session_state(state):
    """Save session state to file with error handling."""
    try:
        ensure_state_directory()

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

def log_hook_execution(hook_name, status="success", details=None):
    """Log hook execution for tracking purposes."""
    try:
        logs = []
        if HOOKS_LOG_FILE.exists():
            with open(HOOKS_LOG_FILE, 'r', encoding='utf-8') as f:
                logs = json.load(f)

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "hook": hook_name,
            "status": status,
            "details": details
        }

        logs.append(log_entry)

        # Keep only last 100 log entries
        if len(logs) > 100:
            logs = logs[-100:]

        ensure_state_directory()
        with open(HOOKS_LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)

    except Exception as e:
        print(f"Warning: Could not log hook execution: {e}", file=sys.stderr)

def update_session_activity(state, agent_name="claude", task_description=""):
    """Update session activity information."""
    current_time = datetime.now().isoformat()

    # Initialize session if not started
    if not state.get("session_start"):
        state["session_start"] = current_time
        # Generate session ID based on timestamp
        state["session_id"] = f"session_{int(datetime.now().timestamp())}"

    # Update activity tracking
    state["last_activity"] = current_time
    state["last_agent"] = agent_name

    if task_description:
        state["current_task"] = task_description

    return state

def track_hook_execution(state, hook_name):
    """Track which hooks have been executed."""
    if "hooks_executed" not in state:
        state["hooks_executed"] = []

    # Add hook if not already tracked
    if hook_name not in state["hooks_executed"]:
        state["hooks_executed"].append(hook_name)

    return state

def track_cross_agent_reviews(state):
    """Track cross-agent review activities."""
    # Update pending reviews status
    if "pending_reviews" not in state:
        state["pending_reviews"] = []

    # Clean up old completed reviews (older than 1 hour)
    current_time = datetime.now()
    cleaned_reviews = []

    for review in state.get("pending_reviews", []):
        try:
            review_time = datetime.fromisoformat(review.get("timestamp", ""))
            # Keep reviews from last hour
            if (current_time - review_time).total_seconds() < 3600:
                cleaned_reviews.append(review)
        except:
            # Keep malformed reviews for safety
            cleaned_reviews.append(review)

    state["pending_reviews"] = cleaned_reviews
    return state

def end_session(state):
    """Handle session end tasks."""
    current_time = datetime.now().isoformat()

    # Calculate session duration
    session_duration = None
    if state.get("session_start"):
        try:
            start_time = datetime.fromisoformat(state["session_start"])
            end_time = datetime.fromisoformat(current_time)
            session_duration = str(end_time - start_time)
        except:
            session_duration = "Unknown"

    # Log session end
    session_end_log = {
        "session_id": state.get("session_id"),
        "session_start": state.get("session_start"),
        "session_end": current_time,
        "session_duration": session_duration,
        "total_tasks_completed": state.get("total_tasks_completed", 0),
        "hooks_executed": state.get("hooks_executed", []),
        "last_agent": state.get("last_agent", "claude")
    }

    log_hook_execution("session_tracker", "session_end", session_end_log)

    # Reset session state but keep some statistics
    final_state = {
        "current_task": "",
        "delegated_to_glm": [],
        "delegated_to_codex": [],
        "pending_reviews": [],
        "last_agent": "claude",
        "glm_failures": 0,
        "codex_failures": 0,
        "session_start": None,
        "total_tasks_completed": state.get("total_tasks_completed", 0),
        "hooks_executed": [],
        "last_activity": current_time,
        "session_id": None,
        "previous_session_id": state.get("session_id")
    }

    return final_state

def main():
    """Main hook function."""
    try:
        # Parse input from stdin (hook system passes tool data)
        tool_data = {}
        try:
            tool_data = json.load(sys.stdin)
        except json.JSONDecodeError:
            # No input or invalid JSON, continue with defaults
            pass

        # Get current state
        state = load_session_state()

        # Determine hook action based on tool data
        action = tool_data.get("action", "update")
        agent_name = tool_data.get("agent", "claude")
        task_description = tool_data.get("task", "")
        hook_name = tool_data.get("hook_name", "session_tracker")

        if action == "end_session":
            # Handle session end
            final_state = end_session(state)
            if save_session_state(final_state):
                log_hook_execution(hook_name, "success", {"action": "end_session"})
                print("Session ended successfully", file=sys.stderr)
                sys.exit(0)
            else:
                print("Failed to save session end state", file=sys.stderr)
                sys.exit(1)

        else:
            # Update session activity
            state = update_session_activity(state, agent_name, task_description)

            # Track hook execution
            state = track_hook_execution(state, hook_name)

            # Track cross-agent reviews
            state = track_cross_agent_reviews(state)

            # Save updated state
            if save_session_state(state):
                log_hook_execution(hook_name, "success", {
                    "action": "update",
                    "agent": agent_name,
                    "task": task_description,
                    "session_id": state.get("session_id")
                })
                print("Session state updated successfully", file=sys.stderr)
                sys.exit(0)
            else:
                print("Failed to save session state", file=sys.stderr)
                sys.exit(1)

    except KeyboardInterrupt:
        print("Session tracker interrupted", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        error_msg = f"Unexpected error in session tracker: {e}"
        print(error_msg, file=sys.stderr)
        log_hook_execution("session_tracker", "error", {"error": str(e)})
        sys.exit(1)

if __name__ == '__main__':
    main()