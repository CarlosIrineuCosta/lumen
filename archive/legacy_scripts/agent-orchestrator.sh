#!/bin/bash
# Agent Orchestrator - Central command system for multi-agent development
# This script is designed to be called by Claude Code via slash commands

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project paths
PROJECT_ROOT="$(dirname "$(dirname "$(realpath "$0")")")"
TASKS_DIR="$PROJECT_ROOT/tasks"
DOCS_DIR="$PROJECT_ROOT/docs"
POSTBOX_DIR="$PROJECT_ROOT/.postbox"
AGENTS_DIR="$PROJECT_ROOT/.agents"
SCREENSHOTS_DIR="$PROJECT_ROOT/docs/screenshots"

# Ensure directories exist
mkdir -p "$TASKS_DIR" "$POSTBOX_DIR" "$AGENTS_DIR" "$SCREENSHOTS_DIR"
# Function to display usage
show_usage() {
    cat << EOF
====================================================================
                    AGENT ORCHESTRATOR
====================================================================
Usage: agent-orchestrator.sh [COMMAND] [OPTIONS]

COMMANDS:
    init                    Initialize project structure with AGENTS.md
    verify [files]          Run verification chain on changed files
    task-sync              Sync documentation with code changes
    test-suite [type]       Run specific test suite (unit/integration/ui)
    review [agent]         Request code review from specific agent
    status                 Show current project status
    plan [task]           Create implementation plan for task
    complete              Run after completing any task (triggers verification)
    screenshot [name]      Take UI screenshot and save to docs
    update-context        Update AGENTS.md with current state

OPTIONS:
    --json               Output in JSON format for parsing
    --verbose            Show detailed output
    --agent [name]       Specify which agent to use (gemini/claude/codex)

EXAMPLES:
    ./agent-orchestrator.sh init
    ./agent-orchestrator.sh verify backend/api.py frontend/index.js
    ./agent-orchestrator.sh test-suite unit --json
    ./agent-orchestrator.sh review gemini
    ./agent-orchestrator.sh complete

====================================================================
EOF
}