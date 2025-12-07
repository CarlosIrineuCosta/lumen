#!/bin/bash
# Quick setup for new project with Lumen coordination system

set -e

if [ -z "$1" ]; then
    echo "Usage: ./setup_new_project.sh PROJECT_NAME"
    exit 1
fi

PROJECT=$1
BASE=~/Storage/projects
SOURCE=$BASE/lumen
TARGET=$BASE/$PROJECT

echo "Setting up $PROJECT with Lumen coordination..."

mkdir -p $TARGET
cd $SOURCE

echo "Copying .claude/ (hooks and settings)..."
cp -r .claude $TARGET/
rm -rf $TARGET/.claude/state/* 2>/dev/null || true

echo "Copying agent-system/ (portable multi-agent system)..."
cp -r agent-system $TARGET/

echo "Creating COORDINATION.md in root..."
cat > $TARGET/COORDINATION.md << 'EOF'
# Agent Coordination Status

**Last Updated**: Not started
**Active Agent**: None

## Current Task
- **Task**: No active task
- **Status**: Idle

## Agent Locations
- Claude Code: Primary orchestrator
- GLM: Code generation via internal Task tool
- Codex: Code review via CLI
- Gemini: Research via CLI
EOF

echo "Copying non-legacy scripts/..."
# Exclude scripts/agents (moved to agent-system) and agent-related scripts
rsync -av --exclude='agents' --exclude='agent-*' --exclude='test_zai_*' scripts/ $TARGET/scripts/ || true

echo "Copying config files..."
cp .env.example $TARGET/
cp .gitignore $TARGET/ 2>/dev/null || true

echo "Creating workspace..."
cat > $TARGET/$PROJECT.code-workspace << EOF
{
    "folders": [{"path": "."}],
    "settings": {
        "workbench.sideBar.location": "right",
        "workbench.panel.defaultLocation": "bottom",
        "terminal.integrated.defaultProfile.linux": "bash",
        "workbench.editor.enablePreview": false
    },
    "extensions": {
        "recommendations": [
            "kilocode.kilo-code",
            "sst-dev.opencode",
            "ms-python.python",
            "esbenp.prettier-vscode"
        ]
    }
}
EOF

chmod +x $TARGET/.claude/hooks/*.py 2>/dev/null || true
chmod +x $TARGET/scripts/**/*.py 2>/dev/null || true

echo ""
echo "✅ Project $PROJECT created!"
echo ""
echo "Next:"
echo "1. cd $TARGET"
echo "2. cp .env.example .env && nano .env"
echo "3. code $PROJECT.code-workspace"
echo "4. claude"
