# Handoff Specification: Lumen Agent System Rebuild
**Session Date**: 2025-11-18  
**Status**: Audit in progress, rebuild spec ready  
**Next Session**: System cleanup and proper hook implementation

---

## Context Summary

Charles has a multi-LLM development system where:
- **Claude Code (Primary)**: Main architect using Claude Pro subscription
- **GLM (Z.ai)**: Cost-effective worker for implementations, testing, docs
- **Codex (OpenAI)**: Code review and quality checks
- **Gemini**: Available via native CLI
- **OpenCode**: Lightweight alternative

**Current Problem**: The agent coordination system evolved organically and is now messy with overlapping components, broken hooks configuration, and unclear separation between legacy and active code.

**Current Session Progress**:
1. Fixed Z.ai confusion - Claude Code IS using Pro subscription correctly
2. Identified broken `hooks_settings.json` (references 5 missing hooks)
3. Started system audit running in Claude Code
4. This spec prepares for cleanup and proper implementation

---

## System Architecture Goals

### Design Principles
1. **Claude Code as Architect**: Never intercepted, always in control
2. **Explicit Delegation**: Claude Code explicitly delegates to other LLMs via Task tool
3. **No Automatic Interception**: Hooks for quality checks only, not routing
4. **Clear Separation**: Hooks vs Scripts vs Documentation
5. **Minimal Coordination Files**: Single source of truth for status

### Execution Model
```
User → Claude Code (Architect)
         ↓
    Analyzes task
         ↓
    Decides delegation:
    - Keep it (architecture, security, complex decisions)
    - Delegate to GLM (tests, docs, well-defined implementations)
    - Delegate to Codex (code review, quality analysis)
         ↓
    Uses Task tool explicitly:
    "Task: Implement login form validation
     Delegate to: GLM
     Context: [files]
     Requirements: [specs]"
         ↓
    Quality hooks run AFTER completion:
    - Linting (ruff, eslint)
    - Test verification
    - Documentation check
         ↓
    User reviews final result
```

---

## Reference Files for Next Session

### Current System Analysis (From This Session)

**Location**: `Z:\Storage\projects\lumen\`

**Audit Output** (will be completed):
- `SYSTEM_AUDIT_REPORT_2025-11-18.md` - Complete analysis of current state
- `/tmp/audit_phase1.txt` - Git history timeline
- `/tmp/audit_phase2.txt` - File inventory with dates
- `/tmp/audit_phase3.txt` - Code flow analysis
- `/tmp/audit_phase4.txt` - Live test results

**Current Configuration Files**:
- `~/.claude/settings.json` - User-level (has MCP servers, NO API redirection)
- `.claude/hooks_settings.json` - Project hooks (BROKEN - refs 5 missing hooks)
- `.claude/settings.local.json` - Project permissions
- `.env` - API keys for GLM, Codex, etc.

**Existing Hooks** (3 files):
- `.claude/hooks/glm_router.py` (221 lines) - Routes tasks to GLM, currently configured to intercept PreToolUse
- `.claude/hooks/quality_gate.py` - Post-execution quality checks
- `.claude/hooks/completion_checker.py` - Verifies tests, docs, linting

**Missing Hooks** (referenced but don't exist):
- `load_session_state.py`
- `analyze_task_type.py`
- `codex_router.py`
- `auth_check.py`
- `subagent_verify.py`

**Agent Scripts**:
- `scripts/agents/agent_coordinator.py` (210 lines) - Writes to COORDINATION.md and .agents/tasks.json
- `scripts/agents/ai-agent.sh` - Multi-provider AI interface
- `scripts/llm/glm_cli.py` - GLM API wrapper
- `scripts/llm/codex_cli.py` - Codex API wrapper
- `scripts/llm/claude_cli.py` - Claude API wrapper

**Coordination Files**:
- `COORDINATION.md` (root) - 16 lines, last update Nov 18 02:43 - barely changes
- `agents/COORDINATION.md` - Unclear if duplicate or different purpose
- `.agents/tasks.json` - Active task tracking

**Legacy Material** (to be archived):
- `.agents/coordinated/*.json` - 10+ proposal files from January 2025
- `.agents/messages/` - Old coordination protocol
- `.agents/queue/` - Old coordination protocol
- `agents/*.md` - 6 documentation files, mostly about obsolete LM Studio setup

---

## Handoff Documentation from Previous Session

**Location**: `Z:\Storage\projects\lumen\Claude_--_HANDOFF_REPORT_-_2025_nov-18.md`

Key points from that session:
- System evolved from trying to fix VS Code layout
- User has sophisticated multi-LLM orchestration via hooks
- Hooks system wasn't fully documented
- Multiple coordination files with unclear purposes
- Some hooks reference files that don't exist

---

## Specification for Clean Implementation

### Phase 1: Cleanup (Based on Audit Results)

**Archive Structure**:
```
archive/
├── legacy_2025_jan/
│   ├── agents_json/           # .agents/coordinated/*.json
│   ├── messages/              # .agents/messages/
│   ├── queue/                 # .agents/queue/
│   └── docs_obsolete/         # agents/*.md (LM Studio stuff)
└── pre_rebuild_backup/
    ├── .agents/               # Full backup before changes
    ├── .claude/
    └── agents/
```

**Files to Keep**:
- `.agents/tasks.json` (if audit shows it's actively used)
- `.claude/hooks/*.py` (existing 3 hooks - will be refactored)
- `scripts/llm/*.py` (API wrappers)
- `COORDINATION.md` (if audit shows it's used) OR delete if redundant

**Files to Remove**:
- `.claude/agents/` (empty folder)
- Duplicate COORDINATION.md (if two exist)
- `scripts/agents/agent_coordinator.py` (if audit shows it's unused)

### Phase 2: Hook System Redesign

**Objectives**:
1. Remove automatic delegation hooks (glm_router.py from PreToolUse)
2. Keep quality hooks (PostToolUse, Stop)
3. Add optional monitoring hooks (track what's happening)
4. Fix hooks_settings.json to only reference existing hooks

**New Hook Architecture**:

**File**: `.claude/hooks_settings.json`
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "bash_tool|str_replace|create_file",
        "hooks": [{
          "type": "command",
          "command": "python .claude/hooks/quality_gate.py",
          "timeout": 30000
        }]
      }
    ],
    "Stop": [{
      "hooks": [{
        "type": "command",
        "command": "python .claude/hooks/completion_checker.py",
        "timeout": 60000
      }]
    }],
    "SessionStart": [{
      "hooks": [{
        "type": "command",
        "command": "python .claude/hooks/session_init.py"
      }]
    }]
  }
}
```

**Hook Purposes**:

1. **quality_gate.py** (PostToolUse)
   - Run after file edits
   - Check code style, basic syntax
   - Log issues but don't block (let Claude fix)
   - NO delegation to other LLMs

2. **completion_checker.py** (Stop)
   - Run when Claude finishes task
   - Verify: tests exist, docs updated, linting passes
   - Block completion if critical issues found
   - NO delegation to other LLMs

3. **session_init.py** (SessionStart) - NEW
   - Load environment variables
   - Display available LLMs and their purposes
   - Check API keys are configured
   - Show last coordination status

**Hooks to Remove/Refactor**:
- `glm_router.py` - Remove from PreToolUse intercept, convert to manual delegation script

### Phase 3: Manual Delegation System

**Objective**: Claude Code explicitly delegates via Task tool, not automatic hooks

**Implementation**:

**File**: `.claude/docs/DELEGATION_GUIDE.md`
```markdown
# Multi-LLM Delegation Guide

## When to Delegate

### Keep in Claude Code (Do NOT delegate):
- Architecture and design decisions
- Security and authentication
- Complex problem-solving
- Coordination between components
- User interaction and requirements gathering

### Delegate to GLM:
- Test implementation (pytest, jest)
- Documentation writing
- Well-defined feature implementations
- Refactoring with clear specs
- Repetitive code generation

### Delegate to Codex:
- Code review and quality analysis
- Security vulnerability scanning
- Performance optimization suggestions
- Best practices verification

## How to Delegate

Use the Task tool explicitly:

```
Task: Implement user login form validation
Delegate to: GLM via scripts/llm/glm_cli.py
Context files: 
- frontend/components/LoginForm.jsx
- backend/routes/auth.py
Requirements:
- Email validation
- Password strength check
- Error messages
- Tests included
```

## Manual Delegation Scripts

### GLM Worker Script
`scripts/agents/delegate_to_glm.sh <task_file>`

### Codex Review Script
`scripts/agents/delegate_to_codex.sh <code_file>`
```

**File**: `scripts/agents/delegate_to_glm.sh`
```bash
#!/bin/bash
# Manual delegation to GLM for implementation work

TASK_FILE=$1
CONTEXT_FILES=$2

if [ -z "$TASK_FILE" ]; then
    echo "Usage: delegate_to_glm.sh <task_description_file> [context_files]"
    exit 1
fi

# Read task description
TASK=$(cat "$TASK_FILE")

# Build context
CONTEXT=""
if [ -n "$CONTEXT_FILES" ]; then
    for file in $CONTEXT_FILES; do
        CONTEXT+="=== $file ===\n$(cat $file)\n\n"
    done
fi

# Call GLM
python scripts/llm/glm_cli.py --task "$TASK" --context "$CONTEXT"
```

### Phase 4: Status Monitoring (Optional)

**If needed**: Simple status dashboard showing what each LLM is doing

**File**: `.claude/hooks/monitor_status.py` (SessionStart hook)
```python
#!/usr/bin/env python3
"""
Display status of multi-LLM system at session start
"""
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
STATUS_FILE = PROJECT_ROOT / ".agents" / "llm_status.json"

def display_status():
    print("=== Multi-LLM System Status ===")
    print(f"Primary: Claude Code (Claude Pro)")
    print(f"Workers:")
    print(f"  - GLM (Z.ai): Available for implementations")
    print(f"  - Codex (OpenAI): Available for reviews")
    print(f"  - Gemini: Available via CLI")
    
    # Show last activity if tracked
    if STATUS_FILE.exists():
        with open(STATUS_FILE) as f:
            status = json.load(f)
            print(f"\nLast activity:")
            for llm, info in status.items():
                print(f"  {llm}: {info.get('last_task', 'No recent activity')}")

if __name__ == '__main__':
    display_status()
```

### Phase 5: Documentation Consolidation

**Structure**:
```
.claude/
└── docs/
    ├── SYSTEM_OVERVIEW.md      # High-level architecture
    ├── DELEGATION_GUIDE.md     # When and how to delegate
    ├── HOOKS_REFERENCE.md      # What each hook does
    └── agents/
        ├── SETUP.md            # Initial setup for new projects
        └── TROUBLESHOOTING.md  # Common issues
```

**Consolidate from**:
- `agents/*.md` (6 files)
- `.claude/*.md` (scattered docs)
- Root `AGENTS.md`

---

## Implementation Checklist for Next Session

### Pre-Implementation
- [ ] Review `SYSTEM_AUDIT_REPORT_2025-11-18.md`
- [ ] Confirm which files are legacy vs active
- [ ] Verify agent_coordinator.py is unused/redundant

### Cleanup Phase
- [ ] Create backup: `archive/pre_rebuild_backup_YYYYMMDD/`
- [ ] Move legacy JSON files to `archive/legacy_2025_jan/`
- [ ] Remove empty `.claude/agents/` folder
- [ ] Remove or archive obsolete documentation
- [ ] Remove `agent_coordinator.py` if unused

### Hook System Rebuild
- [ ] Create new `hooks_settings.json` (only existing hooks)
- [ ] Refactor `glm_router.py` to remove PreToolUse intercept
- [ ] Create `session_init.py` hook
- [ ] Test each hook individually: `python .claude/hooks/HOOK.py`
- [ ] Verify hooks don't break Claude Code operation

### Delegation System
- [ ] Create `DELEGATION_GUIDE.md`
- [ ] Create `delegate_to_glm.sh` script
- [ ] Create `delegate_to_codex.sh` script
- [ ] Test manual delegation workflow
- [ ] Document in CLAUDE.md for reference

### Documentation
- [ ] Create `.claude/docs/` structure
- [ ] Write `SYSTEM_OVERVIEW.md`
- [ ] Write `HOOKS_REFERENCE.md`
- [ ] Consolidate scattered MD files
- [ ] Update root `CLAUDE.md` with system overview

### Verification
- [ ] Start Claude Code, verify hooks don't error
- [ ] Test delegation to GLM manually
- [ ] Test delegation to Codex manually
- [ ] Verify quality_gate catches issues
- [ ] Verify completion_checker blocks when needed
- [ ] Confirm no automatic interception of tool calls

---

## Key Files for Next Claude Session

**Must Review**:
1. `SYSTEM_AUDIT_REPORT_2025-11-18.md` - Findings from current audit
2. This spec - `REBUILD_SPECIFICATION.md`
3. Current hooks: `.claude/hooks/*.py` (understand before refactoring)

**Reference**:
- Claude Code hooks docs: https://docs.anthropic.com/en/docs/claude-code/hooks
- Handoff from previous session: `Claude_--_HANDOFF_REPORT_-_2025_nov-18.md`

**Environment**:
- Linux machine: 100.106.201.33 (Z:\ on Windows)
- Projects: `~/Storage/projects/lumen/`
- Claude Code: Use `claude` command (already fixed, no Z.ai intercept)

---

## Expected Outcomes

After next session completes:

**Clean Structure**:
```
lumen/
├── .claude/
│   ├── hooks/
│   │   ├── quality_gate.py          # Refactored
│   │   ├── completion_checker.py    # Refactored
│   │   └── session_init.py          # New
│   ├── hooks_settings.json          # Fixed (only real hooks)
│   └── docs/                        # Consolidated docs
│       ├── SYSTEM_OVERVIEW.md
│       ├── DELEGATION_GUIDE.md
│       ├── HOOKS_REFERENCE.md
│       └── agents/
├── scripts/
│   ├── llm/                         # API wrappers (unchanged)
│   └── agents/
│       ├── delegate_to_glm.sh       # New
│       └── delegate_to_codex.sh     # New
├── archive/
│   └── legacy_2025_jan/             # Archived old system
└── CLAUDE.md                        # Updated with system info
```

**Working System**:
- Claude Code operates cleanly without automatic interception
- Quality hooks provide safety checks without blocking workflow
- Manual delegation scripts available for explicit LLM routing
- Clear documentation for how to use the system
- No confusion about what's active vs legacy

---

## Critical User Preferences (Reference)

From user preferences:
- NEVER use emojis
- No "baby colors" - sophisticated dark themes
- Fonts: Montserrat, Roboto
- Machine: Windows 11, 64GB RAM, RTX 3080Ti
- Languages: Python and React
- Communication: Realistic assessments, no sycophantic behavior
- When wrong: Understand issue, offer solution, minimal apologies
- Programming: Analyze first, ask questions, act after
- Answers: Long and detailed except for objective questions
- Use web search/MCPs to check facts

**User Context**:
- Developer/consultant building AI systems for law firms
- Photographer managing 300K+ RAW images
- Writer working on noir novel
- Cost-conscious: prefers subscriptions over API usage
- Experienced: criticize code freely, he values realistic assessments

---

## Session Boundary Notes

**What This Session Completed**:
1. Identified that Claude Code IS using Pro subscription (not Z.ai)
2. Found broken hooks_settings.json (refs 5 missing hooks)
3. Started comprehensive system audit
4. Created this rebuild specification

**What Next Session Must Do**:
1. Review audit report findings
2. Execute cleanup based on audit
3. Rebuild hook system properly
4. Implement manual delegation
5. Consolidate documentation
6. Verify system works end-to-end

**Do NOT**:
- Assume files without checking audit report
- Delete anything before backing up
- Implement hooks that intercept automatically
- Create complex coordination systems
- Add unnecessary abstractions

**DO**:
- Follow audit findings strictly
- Back up before any deletion
- Keep hooks simple and focused
- Make delegation explicit and manual
- Document everything clearly
- Test each component individually

---

## Quick Start for Next Session

```bash
# 1. Navigate to project
cd ~/Storage/projects/lumen

# 2. Review audit report
cat SYSTEM_AUDIT_REPORT_2025-11-18.md

# 3. Review this spec
cat REBUILD_SPECIFICATION.md

# 4. Start Claude Code
claude

# 5. Begin with: "I've reviewed the audit report and rebuild spec. 
#    Let's start with cleanup phase based on audit findings."
```

---

**End of Specification**
