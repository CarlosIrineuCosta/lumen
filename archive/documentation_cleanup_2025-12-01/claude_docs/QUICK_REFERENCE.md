# Quick Reference Card - Multi-LLM Agent System

## File Locations

```
.claude/
├── hooks/
│   ├── glm_router.py              ← Routes to GLM
│   ├── quality_gate.py            ← Cross-agent review
│   └── completion_checker.py      ← Verify task done
├── docs/
│   ├── CHARTER.md                 ← System rules
│   └── RESPONSE_FORMATS.md        ← Communication formats
├── state/
│   └── session_state.json         ← Track delegations
├── README.md                      ← Full documentation
├── INSTALLATION_SUMMARY.md        ← What was created
├── QUICK_REFERENCE.md             ← This file
└── hooks_settings.json            ← Hook configuration

scripts/llm/
├── glm_cli.py                     ← TODO: Configure
└── codex_cli.py                   ← TODO: Configure
```

## Tomorrow Morning Checklist

- [ ] 1. Update `scripts/llm/glm_cli.py` with your GLM command
- [ ] 2. Update `scripts/llm/codex_cli.py` with your Codex command
- [ ] 3. Copy `.claude/hooks_settings.json` to `.claude/settings.json`
- [ ] 4. Test GLM routing: `python .claude/hooks/glm_router.py`
- [ ] 5. Test quality gate: `python .claude/hooks/quality_gate.py`
- [ ] 6. Review `.claude/docs/CHARTER.md` for routing rules
- [ ] 7. Start Claude Code and test with simple task

## Routing Quick Guide

| Task Type | Goes To | Why |
|-----------|---------|-----|
| Testing | GLM | Good at test generation |
| Documentation | GLM | Good at writing docs |
| Implementation (clear spec) | GLM | Handles bulk work |
| Backend optimization | Codex | Database/performance expert |
| Security audit | Codex | Security focused |
| Architecture | Claude | Best at high-level design |
| Authentication | Claude | Complex state management |
| Router logic | Claude | Cross-component coordination |

## Hook Execution Flow

```
1. User submits prompt
   ↓
2. UserPromptSubmit hook analyzes task
   ↓
3. PreToolUse hook decides routing
   ↓
4. If routed to GLM/Codex:
   - External LLM processes task
   - Returns XML formatted response
   - Claude integrates response
   ↓
5. PostToolUse quality gate
   - Different LLM reviews work
   - Blocks if issues found
   ↓
6. Stop hook verifies completion
   - Tests exist?
   - Docs updated?
   - No pending work?
   ↓
7. Task complete!
```

## Cross-Agent Verification

Who reviews whom:
- Claude's work → GLM reviews
- GLM's work → Codex reviews
- Codex's work → Claude reviews

**Rule**: Implementer CANNOT review their own work

## Common Issues & Fixes

### "GLM CLI not found"
→ Update `scripts/llm/glm_cli.py` with correct command

### "Hook not triggering"
→ Check `.claude/settings.json` has hooks configured

### "Quality gate blocking everything"
→ Adjust criteria in `.claude/hooks/quality_gate.py`

### "Completion checker too strict"
→ Modify checks in `.claude/hooks/completion_checker.py`

## State File Location

Track delegations: `.claude/state/session_state.json`

Contains:
- Which tasks delegated to GLM/Codex
- Failure counts
- Pending reviews
- Last agent used

## Testing Commands

```bash
# Test GLM routing
python .claude/hooks/glm_router.py

# Test quality gate
python .claude/hooks/quality_gate.py

# Test completion checker
python .claude/hooks/completion_checker.py

# Check session state
cat .claude/state/session_state.json
```

## Important Files to Configure

1. **scripts/llm/glm_cli.py** - Your GLM command (line ~10)
2. **scripts/llm/codex_cli.py** - Your Codex command (line ~11)
3. **.claude/settings.json** - Copy from hooks_settings.json

## Emergency Disable

To disable all hooks temporarily:

```powershell
Rename-Item .claude\settings.json .claude\settings.json.backup
```

Re-enable:

```powershell
Rename-Item .claude\settings.json.backup .claude\settings.json
```

## Questions for Tomorrow

Share with Claude:
1. Your GLM CLI invocation command
2. Your Codex CLI invocation command
3. Any path corrections needed

---

**Remember**: This system SAVES tokens by routing bulk work to GLM!
