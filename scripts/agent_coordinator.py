#!/usr/bin/env python3
"""
Agent Coordinator for Lumen Project
Manages status updates, task tracking, and AI code reviews
"""

import json
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
COORDINATION_FILE = PROJECT_ROOT / "COORDINATION.md"
TASKS_FILE = PROJECT_ROOT / ".agents" / "tasks.json"
REVIEWS_DIR = PROJECT_ROOT / ".agents" / "reviews"
AI_AGENT_SCRIPT = PROJECT_ROOT / "scripts" / "agents" / "ai-agent.sh"

# Ensure directories exist
TASKS_FILE.parent.mkdir(exist_ok=True)
REVIEWS_DIR.mkdir(exist_ok=True)

def load_tasks():
    """Load task history"""
    if TASKS_FILE.exists():
        with open(TASKS_FILE, 'r') as f:
            return json.load(f)
    return {"tasks": [], "current": None}

def save_tasks(tasks):
    """Save task history"""
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=2)

def update_coordination_status(task_name, agent, status, details=""):
    """Update COORDINATION.md with current status"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M GMT-3")
    
    content = f"""# Lumen Agent Coordination Status

**Last Updated**: {timestamp}
**Active Agent**: {agent}

## Current Task
- **Task**: {task_name}
- **Status**: {status}
- **Details**: {details}

## Agent Locations
- Claude Code: Linux (100.106.201.33) - Primary Development
- Z.ai GLM: Cloud API - Code Analysis & Reasoning
- Cloud APIs: SambaNova/OpenRouter - Optional Analysis
"""
    
    with open(COORDINATION_FILE, 'w') as f:
        f.write(content)

def update_task(task_name, agent, status, details=""):
    """Update current task status"""
    tasks = load_tasks()
    
    # Record in history
    task_entry = {
        "task": task_name,
        "agent": agent,
        "status": status,
        "details": details,
        "timestamp": datetime.now().isoformat()
    }
    
    tasks["current"] = task_entry
    tasks["tasks"].append(task_entry)
    
    save_tasks(tasks)
    update_coordination_status(task_name, agent, status, details)
    
    print(f"✅ Task updated: {task_name}")
    print(f"   Agent: {agent}")
    print(f"   Status: {status}")

def complete_task(task_name, next_task=""):
    """Mark task as complete and optionally set next task"""
    tasks = load_tasks()
    
    if tasks["current"] and tasks["current"]["task"] == task_name:
        tasks["current"]["status"] = "Completed"
        tasks["current"]["completed_at"] = datetime.now().isoformat()
    
    if next_task:
        update_coordination_status(next_task, "Pending", "Waiting for assignment", "")
    else:
        update_coordination_status("No active task", "All Agents", "Idle", "")
    
    save_tasks(tasks)
    print(f"✅ Task completed: {task_name}")
    if next_task:
        print(f"📋 Next task: {next_task}")

def request_review(prompt, *files):
    """Request AI code review"""
    if not AI_AGENT_SCRIPT.exists():
        print("ERROR: AI agent script not found")
        return
    
    # Generate review filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    review_file = REVIEWS_DIR / f"review_{timestamp}.md"
    
    print("🤖 Requesting AI review...")
    
    try:
        # Call AI agent with auto-selection
        cmd = [str(AI_AGENT_SCRIPT), "auto", prompt]
        cmd.extend(files)
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Save review
            with open(review_file, 'w') as f:
                f.write(f"# Code Review\n\n")
                f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
                f.write(f"**Prompt**: {prompt}\n")
                f.write(f"**Files**: {', '.join(files)}\n\n")
                f.write("## Review\n\n")
                f.write(result.stdout)
            
            print(f"✅ Review saved: {review_file}")
            print("\n--- Review Content ---")
            print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
        else:
            print(f"❌ Review failed: {result.stderr}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

def list_tasks():
    """List recent tasks"""
    tasks = load_tasks()
    
    print("\n📋 Recent Tasks\n" + "="*50)
    
    if tasks["current"]:
        print(f"\n🔵 Current Task:")
        print(f"   {tasks['current']['task']}")
        print(f"   Status: {tasks['current']['status']}")
        print(f"   Agent: {tasks['current']['agent']}")
    
    print(f"\n📜 Task History (last 10):")
    for task in tasks["tasks"][-10:]:
        timestamp = datetime.fromisoformat(task["timestamp"]).strftime("%m/%d %H:%M")
        print(f"   [{timestamp}] {task['task']} - {task['status']}")

def main():
    """Main CLI interface"""
    if len(sys.argv) < 2:
        print("""
Lumen Agent Coordinator

Usage:
  python agent_coordinator.py update <task> <agent> <status> [details]
  python agent_coordinator.py complete <task> [next_task]
  python agent_coordinator.py review <prompt> <file1> [file2...]
  python agent_coordinator.py list

Commands:
  update   - Update current task status
  complete - Mark task as complete
  review   - Request AI code review
  list     - Show recent tasks
""")
        print("""
Examples:
  python agent_coordinator.py update "Fix CORS issues" "Claude Code" "In Progress" "Adding credentials to fetch"
  python agent_coordinator.py complete "Fix CORS issues" "Test auth flow"
  python agent_coordinator.py review "Check for security issues" backend/auth.py
""")
        return
    
    command = sys.argv[1]
    
    if command == "update" and len(sys.argv) >= 5:
        task = sys.argv[2]
        agent = sys.argv[3]
        status = sys.argv[4]
        details = sys.argv[5] if len(sys.argv) > 5 else ""
        update_task(task, agent, status, details)
    
    elif command == "complete" and len(sys.argv) >= 3:
        task = sys.argv[2]
        next_task = sys.argv[3] if len(sys.argv) > 3 else ""
        complete_task(task, next_task)
    
    elif command == "review" and len(sys.argv) >= 4:
        prompt = sys.argv[2]
        files = sys.argv[3:]
        request_review(prompt, *files)
    
    elif command == "list":
        list_tasks()
    
    else:
        print("ERROR: Invalid command or arguments")
        print_help()  # Show help

if __name__ == "__main__":
    main()
