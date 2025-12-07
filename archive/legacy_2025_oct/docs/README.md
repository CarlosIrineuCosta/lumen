# Multi-Agent Coordination System

## Overview

This system enables parallel task execution using GLM agents coordinated by Claude Code, implementing a gatekeeper pattern to prevent conflicts and ensure code quality.

## Architecture

```
User → /delegate command → Coordinator → GLM Workers (parallel) → Claude Code (gatekeeper) → User approval → Code changes
```

### Components

1. **GLM Worker** (`scripts/agents/glm_worker.py`)
   - Executes individual tasks via GLM API
   - Isolated from codebase (read-only access)
   - Outputs proposals to `.agents/output/`

2. **Coordinator** (`scripts/agents/parallel_coordinator.py`)
   - Parses multi-task requests
   - Spawns workers in parallel
   - Detects conflicts
   - Categorizes changes (safe vs risky)

3. **Slash Command** (`.claude/commands/delegate.md`)
   - User interface for task delegation
   - Returns control immediately
   - Passes proposal to Claude Code

4. **Claude Code** (you)
   - Reads all GLM outputs
   - Coordinates conflicting changes
   - Auto-applies safe changes (tests, docs)
   - Requests approval for risky changes (code edits)

## Directory Structure

```
.agents/
├── queue/              Task manifests with file locks
│   └── task_TIMESTAMP.json
├── output/             Raw GLM outputs (isolated by timestamp)
│   └── TIMESTAMP/
│       ├── 1_review.md
│       ├── 2_test.py
│       └── 3_docs.md
├── coordinated/        Unified proposals from coordinator
│   └── proposal_TIMESTAMP.json
└── applied/            History of applied changes
    └── applied_TIMESTAMP.md
```

## Usage

### Single Task

```bash
/delegate review "check security" backend/auth.py
```

### Multiple Parallel Tasks

```bash
/delegate review "security issues" auth.py AND test auth.py AND docs
```

### Task Types

- **review** - Security, performance, and best practice analysis
- **test** - Generate comprehensive pytest tests
- **docs** - Create/update documentation
- **search** - Research information and gather context

### Check Status

```bash
/delegate status
```

## Workflow

### 1. User Delegates Tasks

```bash
/delegate review "security" auth.py AND test auth.py
```

### 2. Coordinator Creates Manifest

```json
{
  "task_id": "20251001_120530",
  "tasks": [
    {"id": 1, "type": "review", "files": ["auth.py"]},
    {"id": 2, "type": "test", "files": ["auth.py"]}
  ],
  "locked_files": ["auth.py"],
  "status": "running"
}
```

### 3. GLM Workers Execute in Parallel

- Worker 1: Analyzes auth.py for security issues → `1_review.md`
- Worker 2: Generates tests for auth.py → `2_test.py`

### 4. Coordinator Detects Conflicts

Checks if multiple tasks try to edit the same file in incompatible ways.

### 5. Coordinator Categorizes Changes

**Safe changes** (auto-applied by Claude Code):
- Test file generation
- Documentation updates
- Research outputs

**Risky changes** (require approval):
- Code modifications from reviews
- Refactoring suggestions

### 6. Claude Code Coordinates

Reads proposal:
```json
{
  "safe_changes": [
    {"type": "test", "output": "2_test.py"}
  ],
  "risky_changes": [
    {"type": "review", "output": "1_review.md"}
  ],
  "conflicts": []
}
```

### 7. Claude Code Presents to User

```
Agent tasks completed. Here's what I found:

SAFE CHANGES (auto-applied):
[x] Added 8 security tests to test_auth.py

RISKY CHANGES (need approval):
[ ] Fix: Add rate limiting (auth.py:45)
[ ] Fix: Validate token expiry (auth.py:78)
[ ] Fix: Hash passwords with bcrypt (auth.py:23)

No conflicts detected. Apply risky changes?
```

### 8. User Approves

User says "yes" → Claude Code applies changes using Edit tool

## Safety Features

### File Locking

Manifest includes `locked_files` to track which files are being analyzed.

### Read-Only GLM Workers

GLM agents can only:
- Read specified files
- Generate proposals
- Save to isolated output directory

GLM agents CANNOT:
- Modify codebase directly
- Access files outside their task scope
- Communicate with each other

### Gatekeeper Pattern

Claude Code is the only entity that:
- Applies changes to codebase
- Resolves conflicts
- Merges proposals
- Validates safety

### Change Categorization

**Auto-apply (safe):**
- Test files (new files, isolated)
- Documentation (markdown files)
- Research outputs (no code changes)

**Require approval (risky):**
- Code modifications
- Refactoring
- Security fixes (need review)

## Configuration

### GLM Model

Default: `glm-4.5-flash` (FREE tier)

Edit `scripts/agents/glm_worker.py` to change:
```python
GLM_MODEL = "glm-4.6"  # Paid, better for complex tasks
```

### Timeouts

Default: 5 minutes per task batch

Edit `scripts/agents/parallel_coordinator.py`:
```python
success = coordinator.wait_for_completion(tasks, timeout=600)  # 10 minutes
```

### Task Prompts

Customize GLM behavior in `scripts/agents/glm_worker.py`:
```python
TASK_PROMPTS = {
    "review": "...",  # Customize review instructions
    "test": "...",    # Customize test generation
    # ...
}
```

## Examples

### Example 1: Security Review + Tests

```bash
/delegate review "security vulnerabilities" backend/auth.py AND test backend/auth.py
```

**Result:**
- GLM analyzes auth.py for security issues
- GLM generates comprehensive tests
- Claude Code auto-applies tests (safe)
- Claude Code presents security fixes for approval (risky)

### Example 2: Documentation Research

```bash
/delegate search "FastAPI authentication best practices" AND docs
```

**Result:**
- GLM researches FastAPI auth patterns
- GLM suggests documentation updates
- Claude Code auto-applies docs (safe)
- User gets summary of findings

### Example 3: Multi-File Refactoring

```bash
/delegate review "improve error handling" models.py utils.py AND test models.py utils.py
```

**Result:**
- GLM reviews both files for error handling
- GLM generates tests for both
- Coordinator detects if changes conflict
- Claude Code presents unified proposal
- User approves/rejects changes

## Troubleshooting

### Tasks timing out

Increase timeout in `parallel_coordinator.py` or use faster model:
```python
GLM_MODEL = "glm-4.5-air"  # Faster but requires credits
```

### GLM API errors

Check API key in `scripts/agents/glm_worker.py`:
```python
GLM_API_KEY = "your_key_here"
```

### Proposals not appearing

Check `.agents/queue/` for failed manifests:
```bash
cat .agents/queue/task_*.json
```

### Conflicts detected incorrectly

Review coordinator logic in `parallel_coordinator.py`:
```python
def detect_conflicts(self, tasks):
    # Customize conflict detection
```

## Advanced Usage

### Custom Task Types

Add to `TASK_PROMPTS` in `glm_worker.py`:
```python
TASK_PROMPTS["refactor"] = """You are a refactoring expert..."""
```

Then use:
```bash
/delegate refactor "simplify logic" complex_function.py
```

### Integration with Other Tools

Chain with existing slash commands:
```bash
/delegate test backend/api.py
# ... review and apply ...
/check  # Run full test suite
```

### Batch Processing

Create script to process multiple files:
```bash
for file in backend/*.py; do
    /delegate review "security" "$file"
done
```

## Comparison to Manual Workflow

**Before (sequential):**
1. Ask Claude Code to review security
2. Wait for review
3. Ask Claude Code to write tests
4. Wait for tests
5. Ask Claude Code to update docs
6. Wait for docs

Total time: 15-20 minutes of Claude Code's attention

**After (parallel):**
1. `/delegate review "security" auth.py AND test auth.py AND docs`
2. GLM agents work in parallel (2-3 minutes)
3. Claude Code coordinates (30 seconds)
4. User approves (10 seconds)

Total time: 3-4 minutes, only 40 seconds of Claude Code's attention

## Cost Comparison

**GLM-4.5-Flash (FREE):**
- Review + Tests + Docs: $0.00
- Limitation: Usage limits, slower

**GLM-4.6 (Paid, $3/month minimum):**
- Review + Tests + Docs: ~$0.01
- Faster, better quality

**Claude Sonnet 4 (comparison):**
- Same tasks: ~$0.50-1.00
- Highest quality but 50-100x more expensive

## Future Enhancements

- [ ] Add retry logic for failed tasks
- [ ] Implement task priority queue
- [ ] Add streaming output for long tasks
- [ ] Support for more AI providers (Gemini, etc.)
- [ ] Web UI for task monitoring
- [ ] Automatic conflict resolution
- [ ] Learning from user approvals
