# Agent Orchestration System - Claude Code Setup Instructions

## IMPORTANT: NO WSL - Run everything through Claude Code's native commands

## Step 1: Create the Main AGENTS.md File

Replace your existing CLAUDE.md with this new AGENTS.md in project root:

```markdown
# AGENTS.md - Multi-Agent Development Configuration

## Project Overview
Project: Lumen Photo Management System
Type: Full-stack web application
Status: Active Development

## Architecture
- Frontend: Vanilla JS + Web Components + Tailwind CSS (NO REACT!)
- Backend: Python FastAPI
- Database: SQLite (development), PostgreSQL (production)
- Storage: Firebase Storage for images
- Auth: Firebase Authentication

## Agent Roles
1. **Claude Code** (Primary): Implementation and architecture
2. **Gemini CLI** (Verifier): Code review and issue detection
3. **Codex CLI** (Tester): Test execution and validation

## Current Tasks
See: ./tasks/2024-09-19.md

## Verification Protocol
After each task completion, run:
1. Check git diff for changed files
2. Call Gemini to review changes
3. Run pytest on backend
4. Update .postbox/completed.md

## Directory Structure
```
/frontend      - UI components and client code
/backend       - API and business logic
/docs          - Documentation and screenshots
/scripts       - Automation and tools
/tasks         - Daily task files
/.postbox      - Agent communication
/.agents       - Agent-specific configs
```

## Code Standards
- NO React/Next.js imports
- Prefer vanilla JS over frameworks
- Use Web Components for reusability
- Keep functions under 50 lines
- Document complex logic inline

## Testing Requirements
- Unit tests for all backend functions
- Integration tests for API endpoints  
- UI tests for critical workflows
- Screenshot evidence for UI changes

## Component Library
Location: ./frontend/components/
Status: Migrating from React to Web Components
Docs: ./docs/components/README.md
```

## Step 2: Create Directory Structure

Run these commands in Claude Code:

```bash
# Create directories
mkdir -p tasks
mkdir -p .postbox
mkdir -p .agents
mkdir -p .agents/messages
mkdir -p docs/screenshots

# Create postbox files
touch .postbox/todo.md
touch .postbox/completed.md
touch .postbox/issues.md

# Create initial task file
echo "# Tasks for $(date +%Y-%m-%d)" > tasks/$(date +%Y-%m-%d).md
```

## Step 3: Create Python Agent Protocol Script

Save this as `scripts/agent_protocol.py`:

```python
#!/usr/bin/env python3
"""
Agent Communication Protocol - JSON-first structured responses
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from enum import Enum

class AgentRole(Enum):
    CLAUDE = "claude-code"
    GEMINI = "gemini-cli"
    CODEX = "codex-cli"
    HUMAN = "human"

class MessageType(Enum):
    TASK = "task"
    VERIFICATION = "verification"
    REVIEW = "review"
    COMPLETION = "completion"
    ERROR = "error"
    STATUS = "status"
    PLAN = "plan"

class AgentProtocol:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.postbox_dir = self.project_root / ".postbox"
        self.agents_dir = self.project_root / ".agents"
        self.ensure_directories()
        
    def ensure_directories(self):
        self.postbox_dir.mkdir(exist_ok=True)
        self.agents_dir.mkdir(exist_ok=True)
        (self.agents_dir / "messages").mkdir(exist_ok=True)
        
    def create_message(self, 
                      from_agent: AgentRole,
                      to_agent: AgentRole,
                      message_type: MessageType,
                      content: Dict[str, Any]) -> Dict:
        
        message = {
            "id": datetime.now().strftime("%Y%m%d_%H%M%S_%f"),
            "timestamp": datetime.now().isoformat(),
            "from": from_agent.value,
            "to": to_agent.value,
            "type": message_type.value,
            "content": content,
            "status": "pending"
        }
        
        # Save message to file
        message_file = self.agents_dir / "messages" / f"{message['id']}.json"
        with open(message_file, 'w') as f:
            json.dump(message, f, indent=2)
            
        return message
    
    def create_verification_request(self, files: List[str]) -> Dict:
        verification = {
            "files": files,
            "timestamp": datetime.now().isoformat(),
            "checks": ["syntax", "style", "security", "performance"]
        }
        
        msg = self.create_message(
            from_agent=AgentRole.CLAUDE,
            to_agent=AgentRole.GEMINI,
            message_type=MessageType.VERIFICATION,
            content=verification
        )
        
        return msg
    
    def generate_summary(self) -> Dict:
        summary = {
            "timestamp": datetime.now().isoformat(),
            "tasks": {"open": 0, "completed": 0},
            "recent_activity": []
        }
        
        # Count tasks
        todo_file = self.postbox_dir / "todo.md"
        if todo_file.exists():
            with open(todo_file, 'r') as f:
                content = f.read()
                summary["tasks"]["open"] = content.count("- [ ]")
        
        completed_file = self.postbox_dir / "completed.md"
        if completed_file.exists():
            with open(completed_file, 'r') as f:
                content = f.read()
                summary["tasks"]["completed"] = content.count("- [x]")
        
        return summary

if __name__ == "__main__":
    protocol = AgentProtocol()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "verify" and len(sys.argv) > 2:
            files = sys.argv[2:]
            result = protocol.create_verification_request(files)
            print(json.dumps(result, indent=2))
        
        elif command == "summary":
            result = protocol.generate_summary()
            print(json.dumps(result, indent=2))
    else:
        print("Usage: agent_protocol.py [verify|summary] [args]")
```

## Step 4: Claude Code Commands to Use

### Initialize Project Structure
```python
# Run this in Claude Code to set up everything
import os
from pathlib import Path

# Create directories
dirs = ['tasks', '.postbox', '.agents', '.agents/messages', 'docs/screenshots']
for d in dirs:
    Path(d).mkdir(parents=True, exist_ok=True)

# Create postbox files
files = ['.postbox/todo.md', '.postbox/completed.md', '.postbox/issues.md']
for f in files:
    Path(f).touch()

print("✓ Agent structure initialized")
```

### Daily Workflow Commands

#### 1. Check Status
```python
# Show project status
import json
from pathlib import Path
from datetime import date

today = date.today().strftime("%Y-%m-%d")
tasks_file = Path(f"tasks/{today}.md")

print("====== PROJECT STATUS ======")

# Check today's tasks
if tasks_file.exists():
    with open(tasks_file) as f:
        lines = [l for l in f if l.startswith("- [")]
        print(f"Today's tasks: {len(lines)}")
        for line in lines[:5]:
            print(line.strip())

# Check TODOs
todo = Path(".postbox/todo.md")
if todo.exists():
    with open(todo) as f:
        todos = f.read().count("- [ ]")
        print(f"Pending TODOs: {todos}")

# Check git status
import subprocess
result = subprocess.run(['git', 'status', '--short'], capture_output=True, text=True)
if result.stdout:
    print("Git changes:")
    print(result.stdout)
```

#### 2. Run Verification After Task Completion
```python
# Post-completion verification
import subprocess
import json
from datetime import datetime

# Get changed files
result = subprocess.run(['git', 'diff', '--name-only'], capture_output=True, text=True)
changed_files = result.stdout.strip().split('\n')

if changed_files and changed_files[0]:
    print(f"Verifying {len(changed_files)} files...")
    
    # Create verification request
    verification = {
        "timestamp": datetime.now().isoformat(),
        "files": changed_files,
        "status": "pending"
    }
    
    # Save to agents directory
    with open(f".agents/verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
        json.dump(verification, f, indent=2)
    
    # Call Gemini for review (if available)
    for file in changed_files:
        print(f"Please review: {file}")
        # Here you would call: gemini-cli -p "Review this file for issues: {file}"
    
    # Run tests
    print("Running tests...")
    subprocess.run(['python', '-m', 'pytest', 'backend/tests/', '-v'])
else:
    print("No changes to verify")
```

#### 3. Sync Documentation
```python
# Sync docs with code
import ast
from pathlib import Path

print("Syncing documentation...")

# Find all Python files
for py_file in Path("backend").rglob("*.py"):
    with open(py_file) as f:
        try:
            tree = ast.parse(f.read())
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    docstring = ast.get_docstring(node)
                    if docstring:
                        print(f"{py_file.name}::{node.name} - documented")
        except:
            pass

print("✓ Documentation sync complete")
```

## Step 5: Slash Commands Configuration

Add to your Claude Code configuration:

```json
{
  "commands": {
    "status": "Show project status",
    "verify": "Run verification on changed files",
    "sync": "Sync documentation with code",
    "complete": "Mark task complete and run verification"
  }
}
```

## Step 6: Daily Workflow

### Morning
1. Check status: Run the status command
2. Review tasks in `tasks/YYYY-MM-DD.md`

### During Development
1. Pick a task from `.postbox/todo.md`
2. Implement the solution
3. Run verification command after completion
4. Move task to `.postbox/completed.md`

### End of Day
1. Run status command
2. Update tomorrow's task file
3. Commit changes

## Alternative: PowerShell Scripts

If you prefer PowerShell scripts that work on Windows:

Save as `scripts/agent-status.ps1`:

```powershell
# Agent Status Script
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Today = Get-Date -Format "yyyy-MM-dd"

Write-Host "====== PROJECT STATUS ======" -ForegroundColor Blue

# Check today's tasks
$TaskFile = "$ProjectRoot\tasks\$Today.md"
if (Test-Path $TaskFile) {
    Write-Host "Today's Tasks:" -ForegroundColor Yellow
    Get-Content $TaskFile | Where-Object {$_ -match "^- \["} | Select-Object -First 5
}

# Check TODOs
$TodoFile = "$ProjectRoot\.postbox\todo.md"
if (Test-Path $TodoFile) {
    $Todos = (Get-Content $TodoFile | Where-Object {$_ -match "^- \[ \]"}).Count
    Write-Host "Pending TODOs: $Todos" -ForegroundColor Yellow
}

# Git status
Write-Host "Git Status:" -ForegroundColor Yellow
git status --short
```

## Key Points

1. **NO WSL** - Everything runs natively in Claude Code or PowerShell
2. **Central AGENTS.md** - Single source of truth for all agents
3. **JSON Protocol** - Structured communication via Python script
4. **Hook-based Verification** - Not continuous monitoring
5. **Simple Commands** - Easy to remember and execute

## Remember

- One task at a time
- Verify after each completion
- Keep AGENTS.md updated
- Use vanilla JS, no React
- Document everything in markdown
