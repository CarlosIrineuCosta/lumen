# Multi-Agent System - Quick Start Guide

## What Was Built Today

A complete multi-agent coordination system where you can delegate tasks to GLM agents while continuing to code.

## The One Command You Need

```bash
/delegate review "description" file1.py AND test file2.py AND docs
```

This runs multiple tasks **in parallel** using GLM agents, then I (Claude Code) coordinate the results and present them to you.

## How to Use Tomorrow

### Option 1: Quick Single-File Review

```bash
/delegate review "check for security issues" backend/app/api/endpoints/auth.py
```

GLM will analyze the file and return findings in ~30 seconds.

### Option 2: Comprehensive System Review

```bash
./scripts/agents/review_entire_system.sh
```

This reviews your entire backend in batches:
- All API endpoints
- All services
- Storage and caching
- Database models
- Generates missing tests
- Updates documentation

Takes ~10-15 minutes to complete.

### Option 3: Custom Parallel Tasks

```bash
# Review multiple files + generate tests
/delegate review "performance issues" service1.py service2.py AND test service1.py AND test service2.py

# Research and document
/delegate search "FastAPI best practices" AND docs

# Full workflow
/delegate review "security" auth.py AND test auth.py AND docs AND search "OAuth2 security patterns"
```

## After Tasks Complete

I'll present results like this:

```
Agent tasks completed. Here's what I found:

SAFE CHANGES (auto-applied):
[x] Added 8 security tests to test_auth.py
[x] Updated AGENTS.md with OAuth2 patterns

RISKY CHANGES (need approval):
[ ] Fix: Add rate limiting (auth.py:45)
[ ] Fix: Hash passwords with bcrypt (auth.py:23)
[ ] Refactor: Extract duplicate code (auth.py:120-145)

No conflicts detected. Apply risky changes?
```

You say "yes" or "apply individually" and I'll make the changes.

## Task Types Available

- **review** - Code review (security, performance, best practices)
- **test** - Generate comprehensive pytest tests
- **docs** - Update/create documentation
- **search** - Research topics and gather information

## Check Status

```bash
/delegate status
```

Shows recent agent work and available proposals.

## Process Proposals Manually

```bash
# List all proposals
python3 scripts/agents/process_proposals.py list

# Show summary of recent proposals
python3 scripts/agents/process_proposals.py summary

# Show specific proposal with full content
python3 scripts/agents/process_proposals.py show 20251001_001309
```

## File Locations

All agent work is organized:

```
.agents/
├── README.md           - Full documentation
├── queue/              - Active tasks (while running)
├── output/             - Raw GLM outputs
│   └── 20251001_001309/
│       ├── 1_review.md
│       ├── 2_test.py
│       └── 3_docs.md
├── coordinated/        - My unified proposals (JSON)
└── applied/            - History of applied changes
```

## Current Test Results

We tested with `backend/app/api/endpoints/auth.py` and GLM found:
- Duplicate function definition
- SQL injection risk
- User enumeration vulnerability
- Missing rate limiting
- Performance issues with DB connections
- Missing transaction handling

Full report: `.agents/output/20251001_001309/1_review.md`

## Cost

**Currently using:** GLM-4.5-Flash (FREE)
- No cost
- Usage limits apply
- Good quality for most tasks

**Upgrade option:** GLM-4.6 ($3/month minimum)
- Better quality
- Faster
- Higher limits
- Change in `scripts/agents/glm_worker.py`

## Architecture

```
You → /delegate command
  ↓
Coordinator parses request
  ↓
GLM Workers (parallel, isolated)
  ↓
I (Claude Code) coordinate
  ↓
Present unified proposal
  ↓
You approve
  ↓
I apply changes safely
```

**Key safety:** GLM agents can only READ files and generate proposals. Only I (Claude Code) can modify your codebase.

## Workflow for Tomorrow

### Morning:

```bash
# 1. Run comprehensive review while you have coffee
./scripts/agents/review_entire_system.sh

# 2. Check what was found
python3 scripts/agents/process_proposals.py summary

# 3. Start coding
# I'll present findings as you work
```

### During Development:

```bash
# Quick checks while coding
/delegate review "security" new_feature.py AND test new_feature.py

# Continue coding while GLM works
# I'll notify when complete
```

### End of Day:

```bash
# Check all agent work
python3 scripts/agents/process_proposals.py summary $(date +%Y%m%d)

# Review and apply findings
```

## Troubleshooting

**If tasks timeout:**
- Increase timeout in `scripts/agents/parallel_coordinator.py`
- Or use faster model (requires paid subscription)

**If API errors:**
- Check API key in `scripts/agents/glm_worker.py`
- Verify you're not hitting rate limits (FREE tier)

**If results seem wrong:**
- Review GLM output in `.agents/output/TIMESTAMP/`
- Adjust prompts in `scripts/agents/glm_worker.py`

## Next Steps

1. Try the comprehensive review tomorrow morning
2. Review findings and apply safe changes
3. Use `/delegate` for quick checks during development
4. Consider upgrading to GLM-4.6 if you like the system

## More Information

- Full docs: `.agents/README.md`
- System overview: `AGENTS.md`
- Slash command help: `.claude/commands/delegate.md`

## Test It Now

Try this simple command to see it work:

```bash
/delegate review "find any issues" backend/app/services/photo_service_v2.py
```

Takes ~30 seconds, you'll get a full security and best practices review.
