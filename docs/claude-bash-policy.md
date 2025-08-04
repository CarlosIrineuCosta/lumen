# Claude Code Bash Execution Policy

## When Claude Should Ask User to Run Commands

**ONLY ask the user to run bash commands when there are actual environmental issues:**

1. **Directory Navigation Issues**: When you need to run a command from a different directory than your current working directory and the command fails due to path issues

2. **Process Management**: When dealing with server processes, background tasks, or anything that might get stuck or require interactive input

3. **Permission or Access Issues**: When commands fail due to file permissions, missing directories, or access restrictions

4. **Long-Running Operations**: When commands might take significant time or could hang

5. **System-Level Operations**: When dealing with process killing, port management, or system service operations

## Example Scenarios:
- Starting/stopping servers with `nohup` and background processes
- Running scripts from different directories where path resolution fails
- Commands that require `sudo` or special permissions
- Operations that modify system-level resources (ports, processes)
- Any command that previously failed due to directory or permission issues

## Instruction Format:
"Please run this from bash: `[command]`"

Then explain what the command will do and why it needs to be run manually.

## Updated: 2025-08-04
**Key Rule**: Run bash commands directly for normal troubleshooting. Only ask for help with genuine environmental barriers.

## Serena Investigation Needed
- User still learning Serena capabilities
- Claude should explore Serena's memory and project management features
- Current usage is minimal (mainly file finding)

## Daily Project Management
- Always document session start time in daily .md files
- Use TodoWrite for complex multi-step tasks
- Clean up server processes daily to prevent conflicts