#!/bin/bash
# Session End Script for /end command
# Usage: ./scripts/session-end.sh

PROJECT_ROOT="/home/cdc/Storage/NVMe/projects/lumen"
TODAY=$(date +%Y-%m-%d)
TOMORROW=$(date -d tomorrow +%Y-%m-%d)
TIMESTAMP=$(date +%H:%M:%S)
FULL_TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "=== Lumen Project Session End ==="
echo "Date: $TODAY"
echo "Time: $TIMESTAMP"

# Watson Time Tracking Integration
echo
echo "🕐 Stopping Watson time tracking..."

# Check if Watson is running
WATSON_STATUS=$(watson status 2>&1)
if [[ "$WATSON_STATUS" == *"No project started"* ]]; then
    echo "⚠️  No Watson timer is currently running"
    SESSION_DURATION="Not tracked"
    TOTAL_TIME="Not available"
else
    # Stop Watson timer
    echo "⏹️  Stopping Watson timer..."
    STOP_OUTPUT=$(watson stop)
    echo "$STOP_OUTPUT"

    # Extract session duration from Watson
    SESSION_DURATION="Unknown duration"
    if [[ "$STOP_OUTPUT" =~ started[[:space:]]+([0-9]+)[[:space:]]+(second|minute|hour)s?[[:space:]]+ago ]]; then
        # Extract the time value and unit
        TIME_VALUE="${BASH_REMATCH[1]}"
        TIME_UNIT="${BASH_REMATCH[2]}"
        case $TIME_UNIT in
            second) SESSION_DURATION="${TIME_VALUE}s" ;;
            minute) SESSION_DURATION="${TIME_VALUE}m" ;;
            hour) SESSION_DURATION="${TIME_VALUE}h" ;;
        esac
    else
        # Fallback: get today's report and extract duration
        DAILY_REPORT=$(watson report --project Lumen --day 2>/dev/null)
        if [[ "$DAILY_REPORT" =~ Lumen[[:space:]]*-[[:space:]]*([0-9]+[hms][[:space:]]*[0-9]*[hms]*[[:space:]]*[0-9]*[hms]*|[0-9]+[hms]) ]]; then
            SESSION_DURATION="${BASH_REMATCH[1]}"
        fi
    fi

    echo "⏱️  Session Duration: $SESSION_DURATION"

    # Get total project time
    echo "📊 Getting total project time..."
    TOTAL_TIME=$(watson report --project Lumen --day 2>/dev/null | grep "Total:" | awk '{print $2}' || echo "Unknown")
    if [[ "$TOTAL_TIME" == *"Unknown"* ]] || [[ -z "$TOTAL_TIME" ]]; then
        # Fallback: try aggregate method
        AGGREGATE_TIME=$(watson aggregate --project Lumen 2>/dev/null | grep -A1 "Lumen" | tail -1 | sed 's/.*- //' || echo "Unknown")
        if [[ "$AGGREGATE_TIME" != *"Unknown"* ]] && [[ -n "$AGGREGATE_TIME" ]]; then
            TOTAL_TIME="$AGGREGATE_TIME"
        fi
    fi
    echo "📈 Total Lumen Project Time: $TOTAL_TIME"

    # Update totaltime.md log
    TOTALTIME_FILE="$PROJECT_ROOT/docs/totaltime.md"
    echo "📝 Updating time log: $TOTALTIME_FILE"

    # Create or update the totaltime.md file
    if [[ ! -f "$TOTALTIME_FILE" ]]; then
        # Create new file with header
        cat > "$TOTALTIME_FILE" << EOF
# Lumen Development Time Log

## Total Time: $TOTAL_TIME

## Sessions

EOF
    fi

    # Add session entry
    cat >> "$TOTALTIME_FILE" << EOF
### Session: $FULL_TIMESTAMP
- **Duration**: $SESSION_DURATION
- **Total Project Time**: $TOTAL_TIME
- **Notes**: Development session completed

EOF

    # Update total time in header if we have it
    if [[ "$TOTAL_TIME" != "Unknown" ]]; then
        sed -i "s/## Total Time: .*/## Total Time: $TOTAL_TIME/" "$TOTALTIME_FILE"
    fi

    echo "✓ Time log updated successfully"
fi

echo

# Define the unchangeable files to review
REVIEW_FILES=(
    "docs/tasks_$(date +%Y%m%d).md"
    "CLAUDE.md"
    "opusdev/README.md"
    "opusdev/ARCHITECTURE.md"
)

echo "📋 Reviewing determined documentation files..."
echo

# Check each review file for recent changes
for file in "${REVIEW_FILES[@]}"; do
    filepath="$PROJECT_ROOT/$file"
    if [ -f "$filepath" ]; then
        # Check if file was modified in last 24 hours
        if [ $(find "$filepath" -mtime -1 -type f | wc -l) -gt 0 ]; then
            echo "📝 MODIFIED: $file (changed in last 24h)"
            # Show last modified time
            echo "   Last modified: $(stat -c %y "$filepath")"
        else
            echo "✓ Unchanged: $file"
        fi
    else
        echo "❌ Missing: $file"
    fi
done

echo
echo "🔍 Checking git status..."
cd "$PROJECT_ROOT"
git_status=$(git status --porcelain)
git_log=$(git log --oneline -n 3)

if [ -n "$git_status" ]; then
    echo "📊 Git Status (uncommitted changes):"
    git status --short
    echo
    echo "📈 Recent commits:"
    echo "$git_log"
else
    echo "✓ No uncommitted changes"
    echo "📈 Recent commits:"
    echo "$git_log"
fi

echo
echo "📁 Checking draft files..."
draft_count=$(find "$PROJECT_ROOT/opusdev/docs/drafts" -name "*.md" -type f 2>/dev/null | wc -l)
echo "Draft files in opusdev/docs/drafts/: $draft_count"

if [ $draft_count -gt 10 ]; then
    echo "⚠️  High number of draft files - consider cleanup"
fi

echo
echo "🗓️  Preparing tomorrow's orchestration file..."

# Create tomorrow's start file
TOMORROW_FILE="$PROJECT_ROOT/start-here-$TOMORROW.md"

cat > "$TOMORROW_FILE" << EOF
# Session Start - $TOMORROW

## Priority Tasks (Generated from previous session)
- [ ] Review session-end results from $TODAY
- [ ] Address any uncommitted git changes
- [ ] Continue with development priorities

## Orchestration Instructions
1. Present this plan using ExitPlanMode before execution
2. Only proceed after explicit user approval
3. Use TodoWrite to track all multi-step tasks

## Session Context
**Previous Session**: $TODAY - Session ended at $TIMESTAMP
**Current Status**: Check docs/tasks_YYYYMMDD.md for latest project state
**Git Status**: $(if [ -n "$git_status" ]; then echo "Uncommitted changes pending"; else echo "Clean working tree"; fi)

## Files Modified Recently
$(for file in "${REVIEW_FILES[@]}"; do
    filepath="$PROJECT_ROOT/$file"
    if [ -f "$filepath" ] && [ $(find "$filepath" -mtime -1 -type f | wc -l) -gt 0 ]; then
        echo "- $file (modified in last 24h)"
    fi
done)

## Implementation Plan
1. Review any pending changes from previous session
2. Address git status if needed
3. Continue with development work
4. Monitor draft files cleanup

## Notes for Tomorrow
- Draft files count: $draft_count
- Last commits: $(echo "$git_log" | head -1)

---
*Auto-generated by /end command from $TODAY session*
EOF

echo "✅ Created start-here-$TOMORROW.md"

echo
echo "🏁 Session End Summary:"
echo "   ⏱️  Session Duration: $SESSION_DURATION"
echo "   📈 Total Project Time: $TOTAL_TIME"
echo "   📝 Reviewed ${#REVIEW_FILES[@]} documentation files"
echo "   🗓️  Created tomorrow's orchestration file"
echo "   📊 Git status checked"
echo "   📁 Draft files: $draft_count"

echo
echo "🤖 CLAUDE ASSISTANT ACTIONS NEEDED:"
echo "1. Present this summary to user"
echo "2. Ask about git commit/push if there are changes"
echo "3. Offer to archive/delete today's start-here-$TODAY.md file"
echo "4. Update TodoWrite status if applicable"

# Check if today's orchestration file exists
TODAY_FILE="$PROJECT_ROOT/start-here-$TODAY.md"
if [ -f "$TODAY_FILE" ]; then
    echo
    echo "📋 Today's orchestration file found: start-here-$TODAY.md"
    echo "🗂️  Cleanup options:"
    echo "   A) Archive to docs/archive/development-drafts/"
    echo "   B) Delete (recommended if tasks completed)"
    echo "   C) Keep for reference (not recommended long-term)"
fi