# Claude Code Session Management Setup

## Overview
This system provides `/start` and `/end` slash commands for structured session management with automatic orchestration file handling, documentation review, and git management.

## Installation

### Option 1: Direct Integration (Recommended)
If Claude Code supports custom slash commands, add to your Claude Code settings:

```json
{
  "slash_commands": {
    "/start": {
      "description": "Start session with orchestration file",
      "command": "./scripts/session-start.sh",
      "working_directory": "/home/cdc/Storage/NVMe/projects/wasenet"
    },
    "/end": {
      "description": "End session with review and preparation", 
      "command": "./scripts/session-end.sh",
      "working_directory": "/home/cdc/Storage/NVMe/projects/wasenet"
    }
  }
}
```

### Option 2: Manual Usage
If slash commands aren't supported, use these as regular commands:

```bash
# Start session
./scripts/session-start.sh

# End session  
./scripts/session-end.sh
```

## Usage Instructions

### Starting a Session with `/start`

1. Type `/start` in Claude Code
2. System will:
   - Look for `start-here-[today].md` in project root
   - If not found, use most recent `start-here-*.md` file
   - If none exist, create a basic template
   - Display the orchestration plan

3. **CRITICAL**: The AI assistant must:
   - Present the plan using ExitPlanMode before any execution
   - Wait for explicit user approval
   - Use TodoWrite for multi-step tasks

### Ending a Session with `/end`

1. Type `/end` in Claude Code
2. System will automatically:
   - Review the 4 determined documentation files for changes
   - Check git status and recent commits
   - Count draft files in `opusdev/docs/drafts/`
   - Create tomorrow's `start-here-[date].md` file
   - Provide cleanup options for today's orchestration file

3. **AI Assistant Actions Required**:
   - Present the end-session summary
   - Ask about git commit/push if there are uncommitted changes
   - Offer to archive/delete today's orchestration file
   - Update TodoWrite status

## File Structure

```
wasenet/
├── start-here-[date].md          # Daily orchestration files
├── scripts/
│   ├── session-start.sh          # /start command implementation
│   └── session-end.sh            # /end command implementation
├── .claude/
│   ├── settings-session-management.json
│   ├── session-commands.md
│   └── SESSION_MANAGEMENT_SETUP.md (this file)
└── docs/archive/development-drafts/  # Archive location for old orchestration files
```

## Determined Review Files
These 4 files are UNCHANGEABLE and always reviewed by `/end`:

1. `CURRENT_STATUS.md` - Project status and milestones
2. `CLAUDE.md` - AI assistant instructions
3. `opusdev/README.md` - Development guide
4. `opusdev/ARCHITECTURE.md` - Technical architecture

## Workflow Examples

### Typical Day Start:
```
User: /start
Claude: [Reads start-here-2025-08-30.md, presents plan via ExitPlanMode]
User: Approve plan
Claude: [Executes plan with TodoWrite tracking]
```

### Typical Day End:
```
User: /end
Claude: [Runs review, creates tomorrow's file, checks git]
       📊 Session Summary:
       - CURRENT_STATUS.md: Modified
       - Git: 3 uncommitted changes
       - Draft files: 12
       - Created start-here-2025-08-31.md
       
       Would you like me to commit and push changes?
User: Yes, commit with message about session work
Claude: [Creates commit and push]
       Would you like me to archive today's start-here-2025-08-30.md?
```

## Benefits

1. **Structured Sessions**: Clear start/end with defined workflows
2. **Automatic Documentation**: Daily orchestration files track progress
3. **Change Monitoring**: Tracks modifications to critical documentation
4. **Git Management**: Integrated commit/push workflow
5. **Cleanup Automation**: Prevents accumulation of temporary files
6. **Consistent Process**: Same workflow every session, prevents chaos

## Safety Features

- **Approval Required**: All plans must be presented and approved
- **TodoWrite Integration**: Multi-step tasks properly tracked
- **Archive System**: Historical orchestration files preserved
- **Git Status Checking**: Never lose uncommitted work
- **File Change Detection**: Monitor critical documentation

## Troubleshooting

### `/start` not finding files:
```bash
# Check for existing orchestration files
find /home/cdc/Storage/NVMe/projects/wasenet -name "start-here-*.md"
```

### `/end` permissions issue:
```bash
# Ensure scripts are executable
chmod +x /home/cdc/Storage/NVMe/projects/wasenet/scripts/*.sh
```

### Hook configuration:
```bash
# Check Claude Code settings directory
ls -la ~/.config/claude-code/
```

## Extension Ideas

- **Weekly Reviews**: `/week-end` command for broader project review  
- **Project Status**: `/status` command for quick project health check
- **Draft Cleanup**: `/cleanup-drafts` for managing temporary files
- **Git Automation**: Enhanced git workflow with branch management

This session management system ensures consistent, organized development workflows while preventing documentation chaos and lost work.