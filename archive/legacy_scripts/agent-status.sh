#!/bin/bash
# Agent Status Script - For Linux (NOT Windows!)

PROJECT_ROOT="$(dirname "$(dirname "$(realpath "$0")")")"
TODAY=$(date +%Y-%m-%d)

echo ""
echo -e "\033[0;34m====== PROJECT STATUS ======\033[0m"
echo ""

# Check today's tasks
if [ -f "$PROJECT_ROOT/tasks/$TODAY.md" ]; then
    echo -e "\033[1;33mToday's Tasks:\033[0m"
    grep "^- \[" "$PROJECT_ROOT/tasks/$TODAY.md" 2>/dev/null | head -10
fi

# Check TODOs
if [ -f "$PROJECT_ROOT/.postbox/todo.md" ]; then
    TODO_COUNT=$(grep -c "^- \[ \]" "$PROJECT_ROOT/.postbox/todo.md" 2>/dev/null || echo 0)
    echo ""
    echo -e "\033[1;33mPending TODOs: $TODO_COUNT\033[0m"
fi

# Check completed
if [ -f "$PROJECT_ROOT/.postbox/completed.md" ]; then
    COMPLETED=$(grep -c "^- \[x\]" "$PROJECT_ROOT/.postbox/completed.md" 2>/dev/null || echo 0)
    echo -e "\033[0;32mCompleted Tasks: $COMPLETED\033[0m"
fi

# Git status
echo ""
echo -e "\033[1;33mGit Status:\033[0m"
cd "$PROJECT_ROOT" && git status --short

echo ""
echo -e "\033[0;34m============================\033[0m"
