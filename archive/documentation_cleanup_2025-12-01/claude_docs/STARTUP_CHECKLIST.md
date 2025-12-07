# Tomorrow's Startup Checklist

## Before Starting Claude Code

- [ ] Review this checklist
- [ ] Have GLM CLI command ready to share
- [ ] Have Codex CLI command ready to share

## In Claude Code - First Actions

1. **Read system documentation:**
   ```
   Read .claude/CLAUDE_CODE_INSTRUCTIONS.md
   Read .claude/QUICK_REFERENCE.md
   Read docs/tasks_2025-10-22.md
   ```

2. **Share CLI commands with Claude:**
   - "Here's my GLM CLI command: [your command]"
   - "Here's my Codex CLI command: [your command]"
   - Claude will update the wrapper scripts

3. **Verify hooks configuration:**
   ```
   Check .claude/settings.json exists
   If not, copy from .claude/hooks_settings.json
   ```

4. **Test the system:**
   ```python
   # Test GLM router
   python .claude/hooks/glm_router.py
   
   # Test quality gate
   python .claude/hooks/quality_gate.py
   
   # Check state
   cat .claude/state/session_state.json
   ```

5. **Start with first task:**
   - Read current priorities in docs/tasks_2025-10-22.md
   - Pick authentication race condition fix
   - Let hooks auto-delegate testing to GLM
   - Review GLM's responses
   - Integrate and verify

## Questions to Ask Claude

1. "Can you read .claude/CLAUDE_CODE_INSTRUCTIONS.md and confirm you understand the multi-LLM orchestration system?"

2. "What are the critical issues in docs/tasks_2025-10-22.md that I should focus on?"

3. "Here's my GLM CLI command: [paste command]. Can you update scripts/llm/glm_cli.py?"

4. "Here's my Codex CLI command: [paste command]. Can you update scripts/llm/codex_cli.py?"

5. "Can we test the GLM routing with a simple task?"

## Expected Workflow

```
You: "Fix the auth race condition in frontend/js/modules/auth.js"
  ↓
Claude analyzes task
  ↓
Claude implements fix
  ↓
Hook triggers quality gate
  ↓
GLM reviews Claude's implementation
  ↓
If approved: Continue
If issues: Claude addresses feedback
  ↓
Completion checker verifies:
  - Tests exist (GLM generates)
  - Docs updated
  ↓
Task complete!
```

## Files Claude Will Reference

- `.claude/CLAUDE_CODE_INSTRUCTIONS.md` ← Main instructions
- `.claude/QUICK_REFERENCE.md` ← Quick routing guide
- `.claude/docs/CHARTER.md` ← System architecture
- `docs/tasks_2025-10-22.md` ← Current tasks
- `.claude/state/session_state.json` ← Delegation tracking

## What Success Looks Like

After configuration:
- ✅ CLI wrappers updated with your commands
- ✅ Hooks routing tasks automatically
- ✅ GLM generating tests for your changes
- ✅ Quality gate reviewing your code
- ✅ Completion checker ensuring nothing missed
- ✅ Auth race condition fixed
- ✅ API connectivity stable

## Troubleshooting

**If hooks aren't working:**
```powershell
# Check settings
cat .claude/settings.json

# Test individual hooks
python .claude/hooks/glm_router.py
python .claude/hooks/quality_gate.py

# Check for errors in state file
cat .claude/state/session_state.json
```

**If GLM/Codex not responding:**
- Verify CLI commands in wrapper scripts
- Test commands manually in terminal
- Check timeout settings (default 300s)

## Remember

- This system SAVES you tokens by delegating to GLM
- Cross-agent verification PREVENTS overconfidence
- Hooks are AUTOMATIC - no manual delegation needed
- Claude Code is the ARCHITECT - you guide, they implement

## Project Constraints

- ❌ No React, Vue, Angular
- ❌ No webpack, Vite, build tools
- ✅ Vanilla JavaScript only
- ✅ PMM (Poor Man's Modules) pattern
- ✅ window.Lumen* global objects
- ✅ Modules max 400 lines

## Your Role Tomorrow

1. Configure the CLI wrappers (5 minutes)
2. Test the system (10 minutes)
3. Start fixing auth race condition (main work)
4. Let GLM handle testing (automatic)
5. Review and integrate responses (as needed)

---

**Total setup time: ~15 minutes**
**Then: Focus on actual development!**

The system is ready. Just need your GLM/Codex commands to complete setup.

See you tomorrow!
