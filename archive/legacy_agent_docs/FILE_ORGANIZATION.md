# Agent Files Organization Summary

## Files Kept in Root
- `AGENTS.md` - Main 123-line agent configuration (keeping as requested)

## Files Moved to `/agents` Directory
- `AGENT_SETUP_INSTRUCTIONS.md` - Original setup instructions
- `AGENT_SYSTEM_COMPLETE.md` - System completion documentation
- `CLAUDE_CODE_INSTRUCTIONS_AGENTS.md` - Basic Claude Code instructions
- `CLAUDE_CODE_DETAILED_INSTRUCTIONS.md` - NEW detailed instructions with LM Studio setup
- `COORDINATION.md` - Lightweight 15-line status file

## Scripts Location: `/scripts/agents/`
- `install-lmstudio.sh` - Installs LM Studio with Xvfb for headless operation
- `ai-agent.sh` - Multi-provider AI interface (LM Studio/SambaNova/OpenRouter)
- `agent_coordinator.py` - Python coordination script for task management
- `test-setup.sh` - Tests the installation

## Hidden Directories
- `/.agents/` - Contains tasks.json and reviews/ directory

## File Structure After Reorganization
```
lumen/
├── AGENTS.md                    # Main agent config (stays in root)
├── agents/                      # All other agent documentation
│   ├── AGENT_SETUP_INSTRUCTIONS.md
│   ├── AGENT_SYSTEM_COMPLETE.md
│   ├── CLAUDE_CODE_INSTRUCTIONS_AGENTS.md
│   ├── CLAUDE_CODE_DETAILED_INSTRUCTIONS.md
│   └── COORDINATION.md
├── scripts/
│   └── agents/
│       ├── install-lmstudio.sh
│       ├── ai-agent.sh
│       ├── agent_coordinator.py
│       └── test-setup.sh
└── .agents/
    ├── tasks.json
    └── reviews/
```

## For Claude Code
Tell Claude Code to read: `/home/cdc/Storage/NVMe/projects/lumen/agents/CLAUDE_CODE_DETAILED_INSTRUCTIONS.md`

This file contains:
- Explanation of the Xvfb headless issue
- Step-by-step installation process
- Troubleshooting guide
- Daily workflow examples
- Systemd service setup for persistence
