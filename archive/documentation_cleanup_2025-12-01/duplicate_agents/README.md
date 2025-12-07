# Lumen Multi-Agent System

A portable, CLI-based multi-agent coordination system for AI-assisted development.

## Architecture

### Agent Roles

- **Claude Code (Architect)**: Architecture, design, security, final decisions
- **GLM (Worker)**: Testing, documentation, implementation, repetitive tasks
- **Codex (Reviewer)**: Code review, security checks, backend optimization
- **Gemini (Mega-Context Analyst)**: 1M token context for large codebase analysis
- **OpenCode (Backup)**: Additional LLM capability as needed

## Quick Setup

### Prerequisites

1. Python 3.11+
2. Required Python packages:
   ```bash
   pip install python-dotenv
   ```
3. GLM model available through Claude Code's Task tool

### Environment Variables

Create a `.env` file in your project root:

```env
# GLM Configuration
GLM_API_KEY=your_glm_api_key_here
GLM_MODEL=glm-4.5-flash
GLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4/

# Optional: Other LLM CLI paths
CODEX_CLI_PATH=/usr/local/bin/codex
GEMINI_CLI_PATH=/usr/local/bin/gemini
OPENCODE_CLI_PATH=/usr/local/bin/opencode
```

## Usage

### 1. Task Delegation

The system automatically routes tasks to appropriate agents based on keywords:

- **Testing/Documentation/Implementation** → GLM
- **Code Review/Security** → Codex
- **Large Context (>100k tokens)** → Gemini
- **Additional Analysis** → OpenCode

### 2. Manual Agent Invocation

#### GLM (Internal)
GLM is called automatically through Claude Code's internal task routing.
The system detects when a task is suitable for GLM (testing, documentation, implementation)
and delegates it internally without requiring external API calls.

#### Parallel Coordination
```bash
python agent-system/scripts/parallel_coordinator.py "Complex task description"
```

#### System Review
```bash
./agent-system/scripts/review_entire_system.sh
```

### 3. Hook System

The hook system provides automatic quality checks:

- **Quality Gate**: Routes work between agents for review
- **Completion Checker**: Ensures tasks are fully complete
- **GLM Router**: Automatically delegates appropriate tasks

Configure hooks in your Claude Code settings:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{
          "type": "command",
          "command": "python agent-system/hooks/quality_gate.py"
        }]
      }
    ],
    "Stop": [
      {
        "hooks": [{
          "type": "command",
          "command": "python agent-system/hooks/completion_checker.py"
        }]
      }
    ]
  }
}
```

## Integration with VS Code

1. Copy the `agent-system` directory to your project root
2. Add to `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "./agent-system/scripts/.venv/bin/python",
  "files.exclude": {
    "**/.agent-system": true
  }
}
```

## Task Flow

1. User request → Claude Code (primary)
2. Task routing based on content and context size
3. Parallel execution when appropriate
4. Proposals → Claude Code review
5. Safe changes auto-applied, risky changes require approval
6. Quality gates verify cross-agent work

## Monitoring

Track agent activity in:
- `docs/coordination/COORDINATION.md` - Current task status
- `.claude/state/session_state.json` - Session tracking
- Git history - All agent changes are committed

## Security

- GLM runs internally through Claude Code - no external API access
- CLI tools run locally with proper isolation
- Cross-agent reviews prevent self-validation
- Quality gates enforce security checks

## Troubleshooting

### GLM Not Working
- GLM is called internally through Claude Code's Task tool
- No API keys or external dependencies needed
- Check hook configuration in Claude Code settings

### CLI Tools Not Found
- Ensure CLI tools are in PATH
- Update paths in .env file

### Hooks Not Triggering
- Verify hook configuration in Claude Code settings
- Check hook script permissions: `chmod +x agent-system/hooks/*.py`