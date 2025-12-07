# System Audit Task: Agent Coordination & Legacy Cleanup

**Task ID**: SYSTEM_AUDIT_001  
**Date Created**: 2025-11-18  
**Target**: Codex + GLM coordination  
**Expected Duration**: 45-60 minutes  
**Output**: Single MD report with findings and cleanup recommendations

---

## Objective

Audit the entire agent coordination system to determine:
1. What's actually being used vs legacy code
2. Whether coordination tracking works or is broken
3. Which files can be safely archived
4. Fix coordination monitoring if broken
5. Provide concrete cleanup plan with file lists

---

## Context: The Problem

Current state is messy with multiple overlapping systems:
- `.agents/` folder with old JSON files from Jan 2025 + active `tasks.json`
- `agents/` folder with documentation + possibly active `COORDINATION.md`
- `COORDINATION.md` at root that barely updates (last: Nov 18 02:43)
- `.claude/hooks/` system that may or may not use the coordination files
- `scripts/agents/` with coordinator scripts that may be redundant
- No visible tracking of GLM/Codex parallel operations
- Watch command monitoring file that doesn't change

The handoff report claims Terminal 3 watches `agents/COORDINATION.md` but actual file is at root `/COORDINATION.md`. Current root file shows no LLM activity tracking despite hooks supposedly delegating to GLM/Codex.

---

## Phase 1: Git History Analysis

**Task**: Identify when the hooks-based system was introduced and what existed before.

### Commands to Run:
```bash
cd ~/Storage/projects/lumen

# Find when .claude/hooks/ was created
git log --diff-filter=A --follow --format=%aI --name-only -- .claude/hooks/ | head -20

# Find when coordination files were created
git log --diff-filter=A --follow --format=%aI --name-only -- COORDINATION.md
git log --diff-filter=A --follow --format=%aI --name-only -- agents/COORDINATION.md
git log --diff-filter=A --follow --format=%aI --name-only -- .agents/

# Get commits before hooks system (estimate: 2-3 months ago)
git log --since="2025-08-01" --until="2025-11-01" --oneline --name-only

# Find last modification dates of .agents/ JSON files
find .agents/ -name "*.json" -type f -exec ls -l {} \; | sort -k6,7
```

### Expected Output Report:
```markdown
## Git History Analysis Results

### Hooks System Timeline
- .claude/hooks/ created: [DATE]
- First hook commit: [COMMIT HASH] - [MESSAGE]
- Files in initial commit: [LIST]

### Coordination Files Timeline
- COORDINATION.md (root) created: [DATE]
- agents/COORDINATION.md created: [DATE]
- .agents/ folder created: [DATE]
- Last .agents/*.json modification: [DATE]

### Pre-Hooks System
- Commits between [START DATE] and [HOOKS DATE]:
  [LIST OF RELEVANT COMMITS WITH FILES]

### Conclusion
[Explain what system existed before hooks, when transition happened]
```

---

## Phase 2: Code Analysis - What Actually Runs

**Task**: Trace execution flow to determine which coordination files are actually used.

### Files to Analyze:

#### 1. Hook System Analysis
```bash
# Check what the hooks actually call
grep -r "COORDINATION" .claude/hooks/*.py
grep -r "tasks.json" .claude/hooks/*.py
grep -r "agent_coordinator" .claude/hooks/*.py

# Check if hooks call external LLMs
grep -r "glm\|codex\|GLM\|Codex" .claude/hooks/*.py

# Check hook configuration
cat .claude/hooks/hooks_settings.json 2>/dev/null || echo "No settings file"
```

#### 2. Agent Coordinator Analysis
```bash
# Trace agent_coordinator.py dependencies
grep -n "COORDINATION_FILE\|TASKS_FILE" scripts/agents/agent_coordinator.py

# Check what calls agent_coordinator
grep -r "agent_coordinator.py" .claude/ scripts/ .agents/

# Check if coordinator is imported by hooks
grep -r "agent_coordinator\|coordinator" .claude/hooks/*.py
```

#### 3. Parallel Operation Tracking
```bash
# Find any logging/tracking mechanisms
find . -name "*.log" -o -name "*status*" -o -name "*tracking*" | grep -v node_modules

# Check if GLM/Codex operations write status anywhere
grep -r "write.*status\|update.*coordination\|log.*progress" scripts/llm/*.py scripts/agents/*.py
```

### Expected Output Report:
```markdown
## Code Flow Analysis Results

### Hook Execution Chain
1. glm_router.py:
   - Reads: [FILES]
   - Writes: [FILES]
   - Calls: [SCRIPTS/COMMANDS]
   - Logs to: [LOCATION]

2. quality_gate.py:
   - Reads: [FILES]
   - Writes: [FILES]
   - Calls: [SCRIPTS/COMMANDS]
   - Logs to: [LOCATION]

3. completion_checker.py:
   - Reads: [FILES]
   - Writes: [FILES]
   - Calls: [SCRIPTS/COMMANDS]
   - Logs to: [LOCATION]

### Agent Coordinator Usage
- Called by: [LIST OF CALLERS or "NONE FOUND"]
- Writes to: [ACTUAL PATHS]
- Still relevant: YES/NO
- Redundant with hooks: YES/NO

### Coordination File Usage Matrix
| File | Read By | Written By | Last Modified | Purpose | Status |
|------|---------|------------|---------------|---------|--------|
| COORDINATION.md (root) | | | 2025-11-18 02:43 | | |
| agents/COORDINATION.md | | | | | |
| .agents/tasks.json | | | 2025-11-18 02:43 | | |

### Tracking Mechanisms Found
[List any status files, logs, or tracking systems discovered]

### Conclusion
[Explain actual execution flow, what's redundant, what's missing]
```

---

## Phase 3: Test Live System Behavior

**Task**: Execute operations and observe what actually happens.

### Test Sequence:

#### Test 1: Manual Coordination Update
```bash
cd ~/Storage/projects/lumen

# Run coordinator manually
python scripts/agents/agent_coordinator.py update \
  "Test audit task" \
  "Codex" \
  "in_progress" \
  "Testing coordination system"

# Check what changed
ls -l COORDINATION.md agents/COORDINATION.md .agents/tasks.json

# View file contents
echo "=== Root COORDINATION.md ===" && cat COORDINATION.md
echo "=== agents/COORDINATION.md ===" && cat agents/COORDINATION.md 2>/dev/null || echo "File not found"
echo "=== tasks.json ===" && cat .agents/tasks.json
```

#### Test 2: Hook Execution Trace
```bash
# Enable debug mode if available
export DEBUG=1
export VERBOSE=1

# Create a simple test file that should trigger hooks
echo "# Test file" > test_hook_trigger.py
echo "def test(): pass" >> test_hook_trigger.py

# Check if hooks have debug/verbose flags
grep -r "debug\|verbose\|DEBUG\|VERBOSE" .claude/hooks/*.py

# Try manual hook execution
cd .claude/hooks
python glm_router.py --help 2>&1 || echo "No CLI interface"
python quality_gate.py --help 2>&1 || echo "No CLI interface"
```

#### Test 3: Live Monitoring
```bash
# In one terminal, monitor all coordination files
watch -n 1 'echo "=== COORDINATION.md ===" && cat COORDINATION.md && echo && echo "=== tasks.json ===" && cat .agents/tasks.json'

# In another terminal, trigger a Claude Code task that should delegate
# (Document what you observe)
```

### Expected Output Report:
```markdown
## Live System Test Results

### Test 1: Manual Coordination
Files modified after update command:
- COORDINATION.md (root): [YES/NO] - [NEW CONTENT or "No change"]
- agents/COORDINATION.md: [EXISTS? YES/NO] - [CONTENT]
- .agents/tasks.json: [YES/NO] - [NEW CONTENT or "No change"]

Conclusion: agent_coordinator.py [IS/IS NOT] functional

### Test 2: Hook Tracing
- Hooks have debug mode: [YES/NO]
- Manual execution possible: [YES/NO]
- Debug output location: [PATH or "None found"]

### Test 3: Live Monitoring
During Claude Code session with GLM/Codex delegation:
- COORDINATION.md updates: [FREQUENCY]
- tasks.json updates: [FREQUENCY]
- Other files modified: [LIST]
- Visible LLM activity tracking: [YES/NO/WHERE]

Conclusion: [Describe actual behavior vs expected behavior]
```

---

## Phase 4: File Inventory & Dating

**Task**: Complete inventory of agent-related files with creation/modification dates.

### Commands:
```bash
cd ~/Storage/projects/lumen

# Complete inventory with dates
echo "=== .agents/ inventory ===" > /tmp/file_inventory.txt
find .agents/ -type f -exec ls -lh {} \; >> /tmp/file_inventory.txt

echo -e "\n=== agents/ inventory ===" >> /tmp/file_inventory.txt
find agents/ -type f -exec ls -lh {} \; >> /tmp/file_inventory.txt

echo -e "\n=== .claude/ inventory ===" >> /tmp/file_inventory.txt
find .claude/ -type f -exec ls -lh {} \; >> /tmp/file_inventory.txt

echo -e "\n=== scripts/agents/ inventory ===" >> /tmp/file_inventory.txt
find scripts/agents/ -type f -exec ls -lh {} \; >> /tmp/file_inventory.txt

echo -e "\n=== Root coordination files ===" >> /tmp/file_inventory.txt
ls -lh COORDINATION.md AGENTS.md 2>/dev/null >> /tmp/file_inventory.txt

cat /tmp/file_inventory.txt

# Get file counts and sizes
du -sh .agents/ agents/ .claude/ scripts/agents/
find .agents/ -name "*.json" | wc -l
```

### Expected Output Report:
```markdown
## File Inventory Results

### .agents/ Folder (Total Size: X MB)
| File | Size | Modified | Notes |
|------|------|----------|-------|
| tasks.json | | 2025-11-18 | Active |
| coordinated/proposal_*.json | | 2025-01-XX | Legacy (10+ files) |
| messages/*.json | | | Legacy |
| queue/*.json | | | Legacy |

### agents/ Folder (Total Size: X MB)
| File | Size | Modified | Referenced By |
|------|------|----------|---------------|
| COORDINATION.md | | | ? |
| FILE_ORGANIZATION.md | | | Self-reference |
| AGENT_SETUP_*.md | | | Legacy LM Studio |

### .claude/ Folder (Total Size: X MB)
| File | Size | Modified | Purpose |
|------|------|----------|---------|
| hooks/glm_router.py | | | Active |
| hooks/quality_gate.py | | | Active |
| hooks/completion_checker.py | | | Active |
| agents/ (folder) | | | Empty? |

### scripts/agents/ Folder (Total Size: X MB)
| File | Size | Modified | Used By |
|------|------|----------|---------|
| agent_coordinator.py | | | ? |
| ai-agent.sh | | | ? |

### Summary Statistics
- Total .agents/ JSON files: X
- Files older than 2025-10-01: X
- Files modified in Nov 2025: X
- Duplicate documentation files: X
```

---

## Phase 5: Cleanup Recommendations

**Task**: Based on all findings, provide concrete cleanup plan.

### Expected Output Report:
```markdown
## Cleanup Recommendations

### Category 1: Safe to Archive (Confirmed Legacy)
Move to `archive/legacy_2025_jan/`:
- [ ] .agents/coordinated/*.json (10+ files from Jan 2025)
- [ ] .agents/messages/ (if unused)
- [ ] .agents/queue/ (if unused)
- [ ] agents/AGENT_SETUP_INSTRUCTIONS.md (LM Studio obsolete)
- [ ] agents/AGENT_SYSTEM_COMPLETE.md (LM Studio obsolete)
- [ ] agents/CLAUDE_CODE_DETAILED_INSTRUCTIONS.md (LM Studio obsolete)
- [ ] .claude/agents/ (if empty/unused)

### Category 2: Needs Fixing Before Keeping
| File | Issue | Fix Required |
|------|-------|--------------|
| COORDINATION.md | Doesn't track LLM ops | Add hook logging or remove |
| agent_coordinator.py | Redundant with hooks? | Remove or integrate |
| agents/COORDINATION.md | Duplicate? | Clarify purpose or remove |

### Category 3: Keep (Confirmed Active)
- .agents/tasks.json
- .claude/hooks/*.py
- scripts/llm/*.py (GLM/Codex wrappers)
- [Others confirmed in use]

### Category 4: Documentation Consolidation
Current documentation is scattered:
- agents/*.md (6 files)
- .claude/docs/*.md
- Root *.md files

Recommendation:
[Provide structure for consolidated docs]

### Proposed Final Structure
```
lumen/
├── .claude/
│   ├── hooks/          # Active coordination (3 files)
│   └── docs/           # Consolidated docs
├── .agents/
│   └── tasks.json      # Only active tracking file
├── scripts/
│   ├── llm/           # API wrappers
│   └── agents/        # [Keep if needed, else remove]
├── docs/
│   └── agents/        # All agent documentation (consolidated)
└── archive/
    └── legacy_2025_jan/  # All old JSON, obsolete docs
```

### Implementation Script
Provide bash script to execute cleanup:
[Include script that moves files per recommendations]
```

---

## Phase 6: Monitoring System Fix (If Needed)

**Task**: If COORDINATION.md doesn't track LLM operations, implement proper tracking.

### Options to Evaluate:

#### Option A: Fix COORDINATION.md to Show LLM Activity
Modify hooks to write status:
```python
# In glm_router.py, quality_gate.py
def log_llm_activity(llm_name, task, status):
    """Append to COORDINATION.md with timestamp"""
    # Implementation
```

#### Option B: Create New Tracking File
Create `.claude/llm_activity.log` or similar:
```
[2025-11-18 14:23:45] GLM: Code review started - auth.py
[2025-11-18 14:24:12] GLM: Code review completed - 3 issues found
[2025-11-18 14:24:15] Codex: Fix implementation started
```

#### Option C: Terminal Dashboard
Create live monitoring script:
```bash
#!/bin/bash
# scripts/monitor_llms.sh
# Shows real-time status of all LLM operations
```

### Expected Output:
```markdown
## Monitoring System Recommendations

Current Issues:
- [List what's broken/missing]

Recommended Solution: [A/B/C or combination]

Implementation:
- Files to modify: [LIST]
- New files to create: [LIST]
- Watch command to use: [COMMAND]

Code Changes Required:
[Provide exact code modifications needed]
```

---

## Final Deliverable Structure

All findings should be compiled into:

**`SYSTEM_AUDIT_REPORT_2025-11-18.md`**

### Required Sections:
1. Executive Summary (what's working, what's broken, what's legacy)
2. Git History Analysis (when hooks introduced, what existed before)
3. Code Flow Analysis (execution paths, redundancies)
4. Live Test Results (what actually happens)
5. File Inventory (complete list with dates/sizes)
6. Cleanup Plan (3 categories: archive, fix, keep)
7. Monitoring Fix (if needed)
8. Implementation Script (ready-to-run bash)

---

## Execution Notes for Claude Code

**Run from**: `~/Storage/projects/lumen/`  
**Execution time**: 45-60 minutes  
**Save all outputs**: Create `/tmp/audit_outputs/` for intermediate files  

**Critical**: Do not execute cleanup until report is reviewed by Charles.

**Checkpoints**: After each phase, save findings to:
- `/tmp/audit_outputs/phase1_git.txt`
- `/tmp/audit_outputs/phase2_code.txt`
- `/tmp/audit_outputs/phase3_tests.txt`
- `/tmp/audit_outputs/phase4_inventory.txt`

**Delegation**: 
- Phase 1-2: Codex (code analysis)
- Phase 3: GLM (testing, observation)
- Phase 4: Either (file operations)
- Phase 5-6: Codex (architectural decisions)

---

## Questions to Answer

By the end, this report MUST answer:

1. ✓ Does `agent_coordinator.py` actually get called by anything?
2. ✓ Are hooks logging their LLM delegations anywhere?
3. ✓ Is `COORDINATION.md` functional or vestigial?
4. ✓ Which JSON files in `.agents/` are legacy vs active?
5. ✓ Is there duplicate documentation that should be consolidated?
6. ✓ What's the correct watch command for monitoring?
7. ✓ Can we safely delete `.claude/agents/` if empty?
8. ✓ Should `agents/COORDINATION.md` exist or is it a duplicate?
9. ✓ What created all those proposal JSON files from January?
10. ✓ How do we actually track parallel GLM/Codex operations?

---

## Success Criteria

This task is complete when:
- [x] Full git history timeline established
- [x] Every agent-related file categorized (keep/fix/archive)
- [x] Execution flow mapped and redundancies identified
- [x] Live system behavior documented
- [x] Concrete cleanup plan with file lists provided
- [x] Monitoring system fixed or deprecated
- [x] Bash script ready to execute cleanup
- [x] Charles can run cleanup confidently without breaking system

---

**END OF TASK**
