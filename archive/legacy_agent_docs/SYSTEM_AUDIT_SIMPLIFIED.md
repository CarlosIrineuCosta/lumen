# System Audit Task - Simplified for Direct Execution

**Task ID**: SYSTEM_AUDIT_001  
**Date**: 2025-11-18  
**Execution**: Run directly in Claude Code terminal without hooks
**Output**: `SYSTEM_AUDIT_REPORT_2025-11-18.md`

---

## Current Situation

The agent coordination system is messy with multiple overlapping components:
- `.agents/` folder with old JSON files from Jan 2025 + active `tasks.json`
- `agents/` folder with documentation
- `COORDINATION.md` at root that barely updates
- `.claude/hooks/` with 3 hooks but `hooks_settings.json` references 5 missing hooks
- `scripts/agents/` with coordinator scripts
- Uncertainty about what's active vs legacy

**Problem**: Hooks configuration is broken (references missing hooks), causing Claude Code issues.

---

## Phase 1: Git History Timeline

```bash
cd ~/Storage/projects/lumen

echo "=== PHASE 1: Git History Analysis ===" | tee /tmp/audit_phase1.txt

# When was .claude/hooks/ created?
echo -e "\n## Hooks System Creation" | tee -a /tmp/audit_phase1.txt
git log --diff-filter=A --format="%aI %h %s" --name-only -- .claude/hooks/ | head -30 | tee -a /tmp/audit_phase1.txt

# When was coordination system created?
echo -e "\n## Coordination Files History" | tee -a /tmp/audit_phase1.txt
git log --diff-filter=A --format="%aI %h" -- COORDINATION.md agents/COORDINATION.md .agents/ | head -10 | tee -a /tmp/audit_phase1.txt

# Find commits from Aug-Nov 2025 (before and after hooks)
echo -e "\n## Recent Major Changes" | tee -a /tmp/audit_phase1.txt
git log --since="2025-08-01" --oneline --grep="agent\|hook\|coordination" | tee -a /tmp/audit_phase1.txt

# Last modification dates of .agents/ JSON files
echo -e "\n## Legacy JSON Files Dating" | tee -a /tmp/audit_phase1.txt
find .agents/ -name "*.json" -type f -exec ls -lh {} \; | sort -k6,7 | tee -a /tmp/audit_phase1.txt

cat /tmp/audit_phase1.txt
```

**Expected output**: Timeline showing when hooks replaced old agent system

---

## Phase 2: File Inventory with Purposes

```bash
echo "=== PHASE 2: Complete File Inventory ===" | tee /tmp/audit_phase2.txt

# Complete inventory with dates
echo -e "\n## .agents/ Folder Inventory" | tee -a /tmp/audit_phase2.txt
find .agents/ -type f -exec ls -lh {} \; | tee -a /tmp/audit_phase2.txt

echo -e "\n## agents/ Folder Inventory" | tee -a /tmp/audit_phase2.txt
find agents/ -type f -exec ls -lh {} \; | tee -a /tmp/audit_phase2.txt

echo -e "\n## .claude/ Folder Structure" | tee -a /tmp/audit_phase2.txt
tree -L 3 .claude/ | tee -a /tmp/audit_phase2.txt

echo -e "\n## scripts/agents/ Contents" | tee -a /tmp/audit_phase2.txt
ls -lh scripts/agents/ | tee -a /tmp/audit_phase2.txt

# File counts
echo -e "\n## Summary Statistics" | tee -a /tmp/audit_phase2.txt
echo "Total .agents/ JSON files: $(find .agents/ -name '*.json' | wc -l)" | tee -a /tmp/audit_phase2.txt
echo "Files older than Oct 2025: $(find .agents/ -name '*.json' -type f ! -newermt '2025-10-01' | wc -l)" | tee -a /tmp/audit_phase2.txt
echo "Files modified Nov 2025: $(find .agents/ -name '*.json' -type f -newermt '2025-11-01' | wc -a /tmp/audit_phase2.txt

cat /tmp/audit_phase2.txt
```

---

## Phase 3: Code Flow Analysis

```bash
echo "=== PHASE 3: Code Execution Flow ===" | tee /tmp/audit_phase3.txt

# What do hooks actually reference?
echo -e "\n## Hook Dependencies" | tee -a /tmp/audit_phase3.txt
for hook in .claude/hooks/*.py; do
    echo -e "\n### $(basename $hook)" | tee -a /tmp/audit_phase3.txt
    grep -n "import\|COORDINATION\|tasks.json\|agent_coordinator" "$hook" | head -20 | tee -a /tmp/audit_phase3.txt
done

# What calls agent_coordinator.py?
echo -e "\n## Agent Coordinator Usage" | tee -a /tmp/audit_phase3.txt
echo "agent_coordinator.py writes to:" | tee -a /tmp/audit_phase3.txt
grep -n "COORDINATION_FILE\|TASKS_FILE" scripts/agents/agent_coordinator.py | tee -a /tmp/audit_phase3.txt

echo -e "\nCalled by:" | tee -a /tmp/audit_phase3.txt
grep -r "agent_coordinator.py" .claude/ scripts/ 2>/dev/null | tee -a /tmp/audit_phase3.txt

# Check hooks_settings.json
echo -e "\n## Hooks Configuration" | tee -a /tmp/audit_phase3.txt
cat .claude/hooks_settings.json | tee -a /tmp/audit_phase3.txt

echo -e "\n## Missing Hooks Referenced" | tee -a /tmp/audit_phase3.txt
for hook in $(grep -o '"command".*\.py"' .claude/hooks_settings.json | grep -o '[^/]*\.py' | sort -u); do
    if [ ! -f ".claude/hooks/$hook" ]; then
        echo "MISSING: $hook" | tee -a /tmp/audit_phase3.txt
    fi
done

cat /tmp/audit_phase3.txt
```

---

## Phase 4: Live System Test

```bash
echo "=== PHASE 4: Testing Current State ===" | tee /tmp/audit_phase4.txt

# Test agent_coordinator manually
echo -e "\n## Testing agent_coordinator.py" | tee -a /tmp/audit_phase4.txt
echo "Before test - files state:" | tee -a /tmp/audit_phase4.txt
ls -l COORDINATION.md .agents/tasks.json 2>&1 | tee -a /tmp/audit_phase4.txt

python scripts/agents/agent_coordinator.py update \
    "System audit test" \
    "Audit" \
    "in_progress" \
    "Testing coordination system" 2>&1 | tee -a /tmp/audit_phase4.txt

echo -e "\nAfter test - files state:" | tee -a /tmp/audit_phase4.txt
ls -l COORDINATION.md .agents/tasks.json 2>&1 | tee -a /tmp/audit_phase4.txt

echo -e "\n## Current COORDINATION.md Content" | tee -a /tmp/audit_phase4.txt
cat COORDINATION.md | tee -a /tmp/audit_phase4.txt

echo -e "\n## Current tasks.json Content" | tee -a /tmp/audit_phase4.txt
cat .agents/tasks.json | tee -a /tmp/audit_phase4.txt

# Test if hooks can execute
echo -e "\n## Hook Execution Test" | tee -a /tmp/audit_phase4.txt
for hook in .claude/hooks/*.py; do
    echo "Testing: $(basename $hook)" | tee -a /tmp/audit_phase4.txt
    python "$hook" < /dev/null 2>&1 | head -5 | tee -a /tmp/audit_phase4.txt
done

cat /tmp/audit_phase4.txt
```

---

## Phase 5: Analysis and Recommendations

Create the report by analyzing all phases:

```bash
cat > SYSTEM_AUDIT_REPORT_2025-11-18.md << 'EOFEOF'
# System Audit Report - Lumen Agent Coordination
**Date**: 2025-11-18  
**Status**: Complete

## Executive Summary

[To be filled after reviewing all phase outputs]

### Key Findings
1. Hook system status: [Working/Broken/Partially functional]
2. Agent coordinator status: [Active/Unused/Redundant]
3. Legacy files count: [X files from before YYYY-MM]
4. Documentation redundancy: [X duplicate files]

## 1. Git History Analysis

[Copy from /tmp/audit_phase1.txt]

**Interpretation**:
- Hooks system introduced: [DATE]
- Previous coordination system: [DESCRIPTION]
- Migration status: [Complete/Incomplete]

## 2. File Inventory

[Copy from /tmp/audit_phase2.txt]

**Categorization**:

### Confirmed Active Files
- `.agents/tasks.json` - Last modified: [DATE]
- `COORDINATION.md` - Last modified: [DATE]
- [Others based on recent modification dates]

### Confirmed Legacy Files (Pre-Oct 2025)
- `.agents/coordinated/*.json` - [COUNT] files from Jan 2025
- [List others with dates]

### Documentation Files (Need consolidation)
- [List all MD files in agents/ with purposes]

## 3. Code Flow Analysis

[Copy from /tmp/audit_phase3.txt]

**Execution Paths**:

### Hooks System
Currently configured hooks:
1. glm_router.py - [Status: Exists/Missing]
2. quality_gate.py - [Status: Exists/Missing]
3. completion_checker.py - [Status: Exists/Missing]
4. [Others from hooks_settings.json]

**Problem**: hooks_settings.json references [X] missing hooks:
- [List missing hooks]

### Agent Coordinator
- Writes to: [PATHS from grep results]
- Called by: [CALLERS or "NONE FOUND"]
- Status: [Functional but unused/Integrated with hooks/Obsolete]

## 4. Live Test Results

[Copy from /tmp/audit_phase4.txt]

**Findings**:
- agent_coordinator.py [WORKS/FAILS]: [Description]
- COORDINATION.md [UPDATES/STATIC]: [Last update time]
- tasks.json [UPDATES/STATIC]: [Last update time]
- Hook execution: [ALL PASS/SOME FAIL/ALL FAIL]

## 5. Cleanup Recommendations

### ARCHIVE (Confirmed Legacy - Move to archive/legacy_2025_jan/)
```
[List files with dates showing they're from Jan-Sept 2025 and not modified since]
```

### FIX BEFORE KEEPING
```
File: hooks_settings.json
Issue: References 5 missing hooks
Action: Remove references to non-existent hooks OR create minimal stub hooks

File: COORDINATION.md
Issue: Not tracking GLM/Codex operations
Action: Either enhance with hook logging or deprecate

File: agent_coordinator.py
Issue: Unclear if still used by any system
Action: Remove if redundant with hooks, or document its purpose
```

### KEEP (Confirmed Active)
```
[List files modified in Nov 2025 or referenced by active code]
```

### CONSOLIDATE DOCUMENTATION
Current scattered docs in agents/:
- AGENT_SETUP_INSTRUCTIONS.md
- AGENT_SYSTEM_COMPLETE.md
- CLAUDE_CODE_INSTRUCTIONS_AGENTS.md
- CLAUDE_CODE_DETAILED_INSTRUCTIONS.md
- FILE_ORGANIZATION.md

Recommendation: Consolidate to `.claude/docs/agents/` with clear structure

## 6. Proposed Final Structure

```
lumen/
├── .claude/
│   ├── hooks/              # Only working hooks
│   │   ├── quality_gate.py
│   │   └── completion_checker.py
│   ├── hooks_settings.json # Fixed configuration
│   └── docs/
│       └── agents/         # Consolidated documentation
├── .agents/
│   └── tasks.json          # Only if still used
├── scripts/
│   ├── llm/               # API wrappers for GLM, Codex, etc.
│   └── agents/            # Only if coordinator still needed
├── docs/
│   └── system/            # High-level system docs
└── archive/
    └── legacy_2025_jan/   # All old JSON, obsolete docs
```

## 7. Implementation Script

```bash
#!/bin/bash
# cleanup_system.sh - Execute after approval

# Backup everything first
mkdir -p archive/pre_cleanup_backup_$(date +%Y%m%d)
cp -r .agents/ .claude/ agents/ archive/pre_cleanup_backup_$(date +%Y%m%d)/

# Archive legacy JSON files
mkdir -p archive/legacy_2025_jan/agents_json
mv .agents/coordinated/*.json archive/legacy_2025_jan/agents_json/ 2>/dev/null || true
mv .agents/messages/ archive/legacy_2025_jan/ 2>/dev/null || true
mv .agents/queue/ archive/legacy_2025_jan/ 2>/dev/null || true

# [Add more commands based on findings]

echo "Cleanup complete. Review archive/ and test system."
```

## 8. Next Steps

1. **Review this report** - Confirm categorizations are correct
2. **Test cleanup script** - In separate branch first
3. **Fix hooks_settings.json** - Remove references to missing hooks
4. **Decide on coordination** - Keep agent_coordinator or deprecate
5. **Consolidate docs** - Move to single location
6. **Implement proper tracking** - If hooks don't track GLM/Codex ops

## Appendices

### A. Complete Hooks Specification
[Document proper hook system design based on official Claude Code docs]

### B. File Dating Matrix
[Table of all files with creation/modification dates]

### C. Command Reference
[List of useful commands for future maintenance]
EOFEOF

cat SYSTEM_AUDIT_REPORT_2025-11-18.md
```

---

## Execution Instructions

1. Copy all bash commands above
2. Run them sequentially in Claude Code terminal
3. Review each phase output in `/tmp/audit_phase*.txt`
4. Fill in the report template with findings
5. Save final report as `SYSTEM_AUDIT_REPORT_2025-11-18.md`

**Do NOT execute any cleanup** - only analysis and recommendations.

---

## Success Criteria

Report must answer:
- ✓ What hooks configuration is broken?
- ✓ Is agent_coordinator.py still used?
- ✓ Which JSON files are legacy vs active?
- ✓ Where does COORDINATION.md get updated?
- ✓ Which documentation files are duplicates?
- ✓ What's the correct cleanup sequence?

**Estimated time**: 20-30 minutes
