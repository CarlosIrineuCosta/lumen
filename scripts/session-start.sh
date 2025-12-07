#!/bin/bash
# Session Start Script for /start command
# Usage: ./scripts/session-start.sh

PROJECT_ROOT="/home/cdc/Storage/NVMe/projects/lumen"
TODAY=$(date +%Y-%m-%d)
START_TIME=$(date +%H:%M:%S)

echo "=== Lumen Project Session Start ==="
echo "Date: $TODAY"
echo "Time: $START_TIME"

# Watson Time Tracking Integration
echo
echo "🕐 Starting Watson time tracking..."

# Stop any existing Watson timer
WATSON_STATUS=$(watson status 2>&1)
if [[ "$WATSON_STATUS" != *"No project started"* ]]; then
    echo "⏹️  Stopping existing Watson timer..."
    watson stop
fi

# Start new timer for Lumen project with date tag
SESSION_TAG="session_$TODAY"
echo "▶️  Starting Watson timer: Lumen +$SESSION_TAG"
watson start Lumen +$SESSION_TAG

# Verify timer started
echo "📊 Watson Status:"
watson status
echo

# Look for today's orchestration file
START_FILE="$PROJECT_ROOT/start-here-$TODAY.md"

if [ -f "$START_FILE" ]; then
    echo "✓ Found today's orchestration file: start-here-$TODAY.md"
    echo "📋 Reading session plan..."
    echo
    echo "=== TODAY'S ORCHESTRATION PLAN ==="
    cat "$START_FILE"
    echo
    echo "=== END OF PLAN ==="
else
    # Look for most recent start-here file
    RECENT_FILE=$(find "$PROJECT_ROOT" -name "start-here-*.md" -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
    
    if [ -n "$RECENT_FILE" ]; then
        echo "⚠️  No file for today ($TODAY)"
        echo "📋 Found recent orchestration file: $(basename "$RECENT_FILE")"
        echo "Reading most recent plan..."
        echo
        echo "=== RECENT ORCHESTRATION PLAN ==="
        cat "$RECENT_FILE"
        echo
        echo "=== END OF PLAN ==="
        echo
        echo "💡 Consider creating start-here-$TODAY.md for today's specific plan"
    else
        echo "❌ No orchestration files found"
        echo "📝 Creating basic session start template..."
        
        cat > "$START_FILE" << EOF
# Session Start - $TODAY

## Priority Tasks
- [ ] Review current project status
- [ ] Check for any pending issues
- [ ] Continue with development work

## Orchestration Instructions  
1. Present this plan using ExitPlanMode before execution
2. Only proceed after explicit user approval
3. Use TodoWrite to track all multi-step tasks

## Session Context
**Previous Session**: No previous orchestration file found
**Current Status**: Check docs/tasks_YYYYMMDD.md for project state
**Known Issues**: Review opusdev/docs/drafts/ for any pending issues

## Implementation Plan
1. Review project documentation
2. Check server status if needed
3. Proceed with development priorities

---
*Auto-generated session start file*
EOF
        
        echo "✓ Created start-here-$TODAY.md"
        echo "📋 Reading generated plan..."
        echo
        cat "$START_FILE"
    fi
fi

echo
echo "🚀 Session ready!"
echo "💡 NEXT: Present this plan to user and wait for approval before proceeding"
echo "⚙️  Remember to use TodoWrite for multi-step tasks"