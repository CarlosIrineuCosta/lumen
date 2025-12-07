---
description: End session with comprehensive review and next-day preparation
---

# End Session

## Context
!`git status --porcelain`
!`git log --oneline -5`
!`find docs/drafts -name "*.md" -type f | wc -l`

## Task
Perform comprehensive session review and prepare for next day.

## Session Review Steps

### 1. Run Changed Files Testing
!`git diff --name-only HEAD~1 HEAD | head -10`

Detect modified files and run targeted tests:
```bash
# Create test report directory
mkdir -p logs

# Generate test report for session
REPORT_FILE="logs/session-test-$(date +%Y-%m-%d-%H-%M).log"
echo "=== Session Test Report $(date) ===" > "$REPORT_FILE"

# Test changed backend files
CHANGED_BACKEND=$(git diff --name-only HEAD~1 HEAD | grep "backend.*\.py$" | head -5)
if [ -n "$CHANGED_BACKEND" ]; then
    echo "Changed backend files:" >> "$REPORT_FILE"
    echo "$CHANGED_BACKEND" >> "$REPORT_FILE"
    
    # Run tests for backend changes
    cd backend && source venv/bin/activate
    pytest tests/ -x --tb=short >> "../$REPORT_FILE" 2>&1
    echo "Backend tests: $?" >> "../$REPORT_FILE"
fi

# Test changed frontend files
CHANGED_FRONTEND=$(git diff --name-only HEAD~1 HEAD | grep -E "\.(html|js|css)$" | head -5)
if [ -n "$CHANGED_FRONTEND" ]; then
    echo "Changed frontend files:" >> "$REPORT_FILE"
    echo "$CHANGED_FRONTEND" >> "$REPORT_FILE"
    
    # Basic frontend validation
    curl -f http://100.106.201.33:8000/lumen-app.html >/dev/null 2>&1
    echo "Frontend accessibility test: $?" >> "$REPORT_FILE"
fi

echo "Session test report saved to: $REPORT_FILE"
```

### 2. Task Completion Tracking
Move completed tasks to organized tracking:
```bash
echo "=== TASK COMPLETION TRACKING ==="

# Check for start-here files with completed tasks
START_FILES=$(find . -name "start-here-*.md" -type f | head -5)

if [ -n "$START_FILES" ]; then
    echo "Processing task completion from start-here files..."
    
    # Create completed tasks file if it doesn't exist
    mkdir -p docs
    if [ ! -f "docs/tasks_completed.md" ]; then
        echo "# Completed Tasks Log" > docs/tasks_completed.md
        echo "" >> docs/tasks_completed.md
        echo "**Purpose**: Track all completed development tasks for better project management and knowledge retention." >> docs/tasks_completed.md
        echo "" >> docs/tasks_completed.md
        echo "---" >> docs/tasks_completed.md
    fi
    
    # Process each start-here file for completed tasks
    echo "$START_FILES" | while read start_file; do
        [ -n "$start_file" ] && [ -f "$start_file" ] && {
            TASK_DATE=$(basename "$start_file" .md | sed 's/start-here-//')
            echo "" >> docs/tasks_completed.md
            echo "## Completed Tasks from $TASK_DATE" >> docs/tasks_completed.md
            
            # Extract completed checkboxes (✅ or [x]) from start-here files
            grep -E "^- \[(x|X|✅)\]" "$start_file" 2>/dev/null | sed 's/^- \[(x|X|✅)\]/- ✅/' >> docs/tasks_completed.md || true
            
            echo "✅ Processed completed tasks from $start_file"
        }
    done
    
    echo "Task completion tracking updated in docs/tasks_completed.md"
else
    echo "No start-here files found for task processing"
fi
```

### 3. Documentation Cleanup (Automated)
!`find docs/drafts -name "*.md" -mtime +30 | wc -l`

Automatically clean up old documentation:
```bash
echo "=== AUTOMATIC DOCUMENTATION CLEANUP ==="

# Count files over 30 days old
OLD_DRAFTS=$(find docs/drafts -name "*.md" -mtime +30)
OLD_COUNT=$(echo "$OLD_DRAFTS" | wc -l)

if [ "$OLD_COUNT" -gt 0 ]; then
    echo "Found $OLD_COUNT draft files over 30 days old"
    
    # Create archive directory with date
    ARCHIVE_DIR="docs/archive/development-drafts/$(date +%Y-%m)"
    mkdir -p "$ARCHIVE_DIR"
    
    # Move old files to archive
    echo "$OLD_DRAFTS" | while read file; do
        [ -n "$file" ] && mv "$file" "$ARCHIVE_DIR/"
    done
    
    echo "✅ Archived $OLD_COUNT old draft files to $ARCHIVE_DIR"
else
    echo "✅ No draft files need archiving"
fi

# Consolidate scattered docs if any found
SCATTERED_DOCS=$(find . -name "draft" -type d 2>/dev/null)
if [ -n "$SCATTERED_DOCS" ]; then
    echo "⚠️  Found scattered draft directories - consolidating..."
    find . -name "draft" -type d -exec mv {}/* docs/drafts/ \; 2>/dev/null || true
fi
```

### 3. Review Determined Files
Check these 4 files for changes (UNCHANGEABLE list):
- @docs/tasks_20250902.md
- @CLAUDE.md  
- @README.md
- @docs/ARCHITECTURE.md

### 4. Git Status Analysis
- Check for uncommitted changes
- Review recent commits
- Offer to commit and push if needed

### 5. Next Day Preparation
Create `docs/tasks_[tomorrow].md` with:
- Completed tasks from today's session
- Test report summary from session
- Remaining items from current orchestration
- New priorities discovered
- Context from current session

Include test results in tomorrow's context:
```markdown
## Test Results from [Today's Date]
- Session test report: logs/session-test-[date].log
- Backend changes tested: [✅/❌]
- Frontend changes tested: [✅/❌]
- Issues discovered: [Any problems found]
```

### 6. Cleanup Options
- Archive today's orchestration file to `docs/archive/development-drafts/`
- Include test report in session summary
- Update TodoWrite status
- Clean up old test reports (keep last 7 days only)

## Git Management
If uncommitted changes detected:
1. Present summary of changes
2. Offer to create commit with descriptive message
3. Ask about pushing to remote

## Next Day File Template
Use this structure for tomorrow's tasks file:

```markdown
# Tasks - [TOMORROW_DATE]

## Priority Tasks
- [ ] [Task from previous session]
- [ ] [New priority discovered]

## Session Context
**Previous Session**: [Summary of today's work]
**Current Status**: [From CURRENT_STATUS.md]
**Known Issues**: [Any blockers or concerns]

## Implementation Plan
[Specific actions for tomorrow]

---
*Auto-generated by /end command*
```