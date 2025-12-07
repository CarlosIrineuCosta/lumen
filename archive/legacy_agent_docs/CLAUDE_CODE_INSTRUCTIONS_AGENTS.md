# Claude Code Instructions - Multi-Agent Setup

## Overview
This document contains instructions for setting up the new multi-agent coordination system on the Linux development server (100.106.201.33).

**Project Location**: `/home/cdc/Storage/NVMe/projects/lumen/`

## Immediate Tasks

### 1. Install LM Studio Headless
```bash
cd /home/cdc/Storage/NVMe/projects/lumen
chmod +x scripts/agents/install-lmstudio.sh
./scripts/agents/install-lmstudio.sh
```

### 2. Configure API Keys (if available)
```bash
# Add to ~/.bashrc
echo 'export SAMBANOVA_API_KEY="your_key"' >> ~/.bashrc
echo 'export OPENROUTER_API_KEY="your_key"' >> ~/.bashrc
source ~/.bashrc
```

### 3. Start LM Studio Server
```bash
cd ~/lmstudio
./start-lmstudio-server.sh
# Server will run on http://localhost:1234
```

### 4. Test Agent Scripts
```bash
cd /home/cdc/Storage/NVMe/projects/lumen
chmod +x scripts/agents/ai-agent.sh
chmod +x scripts/agents/test-setup.sh

# Run the test
./scripts/agents/test-setup.sh

# Test AI agent auto-selection
./scripts/agents/ai-agent.sh auto "Test connection"

# Test specific provider
./scripts/agents/ai-agent.sh lmstudio "Review this code" "" backend/main.py
```

## Usage Examples

### Update Task Status
```bash
python scripts/agents/agent_coordinator.py update "Install LM Studio" "Claude Code" "Completed"
```

### Request Code Review
```bash
python scripts/agents/agent_coordinator.py review "Check CORS implementation" backend/middleware/cors.py
```

### Complete Task
```bash
python scripts/agents/agent_coordinator.py complete "Install LM Studio" "Configure dual GPU"
```

## File Structure
```
lumen/
├── COORDINATION.md              # Current status (check this)
├── scripts/
│   └── agents/
│       ├── install-lmstudio.sh  # LM Studio installer
│       ├── ai-agent.sh          # Multi-provider AI
│       ├── agent_coordinator.py # Coordination script
│       └── test-setup.sh        # Test the installation
└── .agents/
    ├── tasks.json              # Task history
    └── reviews/                # AI code reviews
```

## What This Replaces

The old 123-line AGENTS.md file has been replaced with:
- **COORDINATION.md** (15 lines) - Current status only
- **Automated scripts** - Handle actual coordination
- **AI providers** - Local + cloud for different use cases

## Key Points

1. **LM Studio** runs locally for private code reviews
2. **COORDINATION.md** shows current status (15 lines max)
3. **AI Agent** auto-selects best available provider
4. **Python coordinator** tracks tasks and reviews
5. **No more bloated context** from long AGENTS.md files

## Next Steps After Setup

1. Download a model in LM Studio (recommend llama-3.2-3b-instruct)
2. Test code review on backend files
3. Set up systemd service for auto-start
4. Install dual GPUs when hardware arrives

## Troubleshooting

- If LM Studio fails: Check `nvidia-smi` output
- If API fails: Ensure port 1234 is not in use
- If scripts fail: Check file permissions with `chmod +x`
- Missing jq: Install with `sudo apt-get install jq`
