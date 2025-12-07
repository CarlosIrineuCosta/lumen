# Multi-LLM Agent Orchestration System for Lumen

## Overview

This system enables Claude Code to orchestrate work between multiple LLMs (GLM and Codex) using hooks, with built-in cross-agent verification to prevent overconfidence.

## Architecture

```
Claude Code (Primary Orchestrator)
├── Hooks System (lifecycle control)
├── Subagents (Claude-native for architecture/review)
└── External LLM Workers (via bash)
    ├── GLM CLI (testing, implementation, documentation)
    └── Codex CLI (backend optimization, security)
```

## Directory Structure

```
.claude/
├── hooks/                          # Hook scripts
│   ├── glm_router.py              # Routes tasks to GLM
│   ├── codex_router.py            # Routes tasks to Codex  
│   ├── quality_gate.py            # Cross-agent verification
│   └── completion_checker.py      # Intelligent stop hook
├── agents/                         # Agent configurations (future)
├── state/                          # Session state tracking
│   └── session_state.json
├── docs/                           # Reference documentation (moved to archive)
└── hooks_settings.json             # Hook configuration

scripts/llm/
├── glm_cli.py                      # GLM CLI wrapper
└── codex_cli.py                    # Codex CLI wrapper
```

## Setup Instructions

### Step 1: Configure CLI Wrappers

Edit the CLI wrapper scripts to match your actual GLM/Codex setup:

1. **GLM**: Edit `scripts/llm/glm_cli.py`
   - Update the `call_glm()` function with your actual GLM invocation
   - Examples are in the comments

2. **Codex**: Edit `scripts/llm/codex_cli.py`
   - Update the `call_codex()` function with your actual Codex invocation

### Step 2: Enable Hooks

Copy `.claude/hooks_settings.json` to `.claude/settings.json`:

```bash
cp .claude/hooks_settings.json .claude/settings.json
```

Or merge with existing settings if you have custom configuration.

### Step 3: Test the System

1. **Test GLM routing:**
   ```bash
   python .claude/hooks/glm_router.py
   # Provide test input via stdin
   ```

2. **Test quality gate:**
   ```bash
   python .claude/hooks/quality_gate.py
   ```

3. **Test completion checker:**
   ```bash
   python .claude/hooks/completion_checker.py
   ```

## How It Works

### Task Routing

When Claude Code starts a task:

1. **UserPromptSubmit hook** analyzes the task type
2. **PreToolUse hook** decides routing:
   - Testing/documentation → GLM
   - Backend optimization → Codex
   - Architecture/auth → Stay in Claude

### Cross-Agent Verification

After any file modification:

1. **PostToolUse hook** triggers quality gate
2. System determines which LLM made the change
3. Different LLM reviews the work:
   - Claude's work → GLM reviews
   - GLM's work → Codex reviews
   - Codex's work → Claude reviews
4. If review fails, task is blocked (exit code 2)

### Completion Verification

Before Claude Code stops:

1. **Stop hook** verifies:
   - Tests exist for new backend code
   - No pending delegated tasks
   - Documentation updated
2. If incomplete, blocks with specific reason
3. Claude must address issues before stopping

## Routing Rules

See `docs/coordination/COORDINATION.md` for detailed routing rules.

**Quick Reference:**
- **GLM**: tests, docs, well-defined implementations
- **Codex**: backend optimization, security, database
- **Claude**: architecture, auth, router, integration

## Response Formats

All LLMs must respond in standardized XML format.

See `docs/core/API.md` for complete specification.

## State Management

Session state is tracked in `.claude/state/session_state.json`:

```json
{
  "current_task": "",
  "delegated_to_glm": [],
  "pending_reviews": [],
  "last_agent": "claude",
  "glm_failures": 0
}
```

## Benefits

1. **Token Cost Savings**: GLM handles bulk work
2. **Quality Assurance**: Cross-agent verification
3. **Clear Responsibilities**: Each LLM has defined role
4. **Transparent**: All delegation logged
5. **Fail-Safe**: Falls back to Claude if external LLM fails
6. **No API Costs**: CLI/subscription-based only

## Troubleshooting

### GLM/Codex Not Found

Update the CLI wrapper paths in hook scripts:
- Edit `.claude/hooks/glm_router.py` line with `glm_command`
- Edit `.claude/hooks/quality_gate.py` reviewer commands

### Hook Not Triggering

1. Check `.claude/settings.json` is properly configured
2. Verify hook scripts are executable
3. Check hook script has no syntax errors:
   ```bash
   python .claude/hooks/glm_router.py --help
   ```

### Cross-Agent Verification Blocking

If reviews are too strict:
1. Adjust review criteria in `.claude/hooks/quality_gate.py`
2. Temporarily disable quality gate in settings.json
3. Check state file for which agent made changes

## Next Steps

1. Configure your GLM/Codex CLI commands
2. Test basic routing with simple task
3. Verify cross-agent review works
4. Run through complete workflow
5. Monitor `.claude/state/session_state.json` for delegation tracking

## Questions?

Check the documentation:
- `docs/coordination/COORDINATION.md` - System architecture and rules
- `docs/core/API.md` - LLM communication formats
- `docs/tasks_2025-12-01.md` - Current project tasks

## Automation Scripts

For setup automation, see `setup_new_project.sh` for creating new projects with Lumen coordination system. Phase 6 will introduce additional automation scripts for streamlined deployment and maintenance.

---

**Status**: Ready for configuration and testing
**Created**: November 15, 2025
**Last Updated**: December 6, 2025
