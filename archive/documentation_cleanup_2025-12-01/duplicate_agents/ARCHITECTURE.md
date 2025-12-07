# Multi-LLM Agent System - Architecture & Merger Plan

**Date**: 2025-11-30
**Purpose**: Merge diverged repos (simple-agents + Lumen) into SOLID hierarchical agent system

---

## Current State: simple-agents Repo

### What Exists
This repository contains a **flat orchestration system** with basic routing:

#### Core Files
- **`orchestrator.py`** (8.8KB)
  - Simple keyword-based routing between LLMs
  - Treats all models as peers (no hierarchy)
  - Routes based on task keywords (coding, reasoning, multimodal, etc.)
  - Calls wrappers via subprocess

- **`glm_cli.py`** (4.3KB)
  - Python wrapper for GLM API
  - Makes HTTP requests to `https://api.z.ai/api/coding/paas/v4`
  - Supports GLM-4.5 and GLM-4.5-air models
  - Subscription-based pricing ($3-15/month)

#### Wrapper Scripts
- **`gemini_wrapper.sh`** + **`gemini.exp`**
  - Bash wrapper for Google Gemini CLI
  - Expect script for interactive sessions
  - Supports gemini-1.5-pro and gemini-1.5-flash

- **`codex_wrapper.sh`** + **`codex.exp`**
  - Bash wrapper for OpenAI Codex/GPT CLI
  - Expect script for automation
  - Supports GPT-4 and GPT-4o-mini

- **`glm_wrapper.sh`** + **`glm.exp`**
  - Bash wrapper calling glm_cli.py
  - Expect automation

#### Support Files
- `setup.sh` - Installation and setup automation
- `test.sh` - Test suite for all LLMs
- `README.md` - Documentation of current flat system
- `.gitignore` - Standard ignores
- `agent-new/GEMINI_CODEX_IMPLEMENTATION.md` - Implementation notes

### Current Architecture (Flat)

User → orchestrator.py → [Keyword Analysis] → Route to ONE LLM: ├─ GLM (cost-effective coding) ├─ Codex/GPT (complex reasoning) ├─ Gemini (fast/multimodal) └─ Claude (placeholder)


**Problems with Current Approach:**
- No hierarchy or supervision
- Single LLM handles entire task
- No task decomposition
- No quality review or validation
- Inefficient use of expensive models for simple subtasks
- No specialized roles (testing, documentation, code review)

---

## Desired State: Hierarchical SOLID Agent System

### Architecture Overview

User Request ↓ ┌─────────────────────────────────────────────┐ │ ORCHESTRATOR (Claude Sonnet 4.5) │ │ - Analyzes request │ │ - Decomposes into subtasks │ │ - Plans execution strategy │ │ - Delegates to Senior/Workers │ │ - Aggregates results │ └─────────────────────────────────────────────┘ ↓ ┌─────────────────────────────────────────────┐ │ SENIOR SUPERVISOR (Claude Opus) │ │ - Reviews complex architectural decisions │ │ - Validates Orchestrator's plan │ │ - Supervises critical/complex work │ │ - Quality control for worker output │ │ - Handles escalations │ └─────────────────────────────────────────────┘ ↓ ┌─────────────────────────────────────────────┐ │ WORKERS (Specialized agents) │ │ │ │ ┌─────────────────────────────────────┐ │ │ │ GLM-4.5 / GLM-4.5-air │ │ │ │ - Writing tests (token-heavy) │ │ │ │ - Documentation generation │ │ │ │ - Simple coding tasks │ │ │ │ - Cost: Subscription ($3-15/mo) │ │ │ └─────────────────────────────────────┘ │ │ │ │ ┌─────────────────────────────────────┐ │ │ │ Gemini 1.5 Pro │ │ │ │ - Test generation (token-heavy) │ │ │ │ - Documentation writing │ │ │ │ - Multimodal tasks (image analysis) │ │ │ │ - Fast iteration tasks │ │ │ └─────────────────────────────────────┘ │ │ │ │ ┌─────────────────────────────────────┐ │ │ │ Claude Haiku │ │ │ │ - Quick/simple tasks │ │ │ │ - Code formatting │ │ │ │ - Simple refactoring │ │ │ │ - Fast validation checks │ │ │ └─────────────────────────────────────┘ │ └─────────────────────────────────────────────┘


### SOLID Principles Applied

#### Single Responsibility Principle
Each agent has ONE clear responsibility:
- **Orchestrator**: Planning and coordination only
- **Senior**: Review and supervision only
- **Workers**: Execution of specific task types only

#### Open/Closed Principle
- System open for extension (add new workers/models)
- Closed for modification (core orchestration logic stable)
- Easy to add new LLM workers without changing orchestrator

#### Liskov Substitution Principle
- Any worker implementing the `Worker` interface can be substituted
- All workers respond to same command interface
- Results have consistent structure

#### Interface Segregation Principle
- Workers only implement methods they need
- Orchestrator interface separate from Worker interface
- Senior interface separate from both

#### Dependency Inversion Principle
- Orchestrator depends on Worker abstraction, not concrete implementations
- Workers don't depend on Orchestrator implementation details
- All communication through defined interfaces

### Role Definitions

#### Orchestrator (Claude Sonnet 4.5)
**Responsibilities:**
- Parse and understand user request
- Decompose into subtasks
- Identify task complexity and requirements
- Select appropriate workers
- Coordinate execution flow
- Aggregate and synthesize results
- Present final output to user

**When to escalate to Senior:**
- Architectural decisions needed
- Complex design patterns required
- Multi-file refactoring
- Critical security decisions
- Conflicting worker outputs

**Tools:**
- Task decomposition framework
- Worker selection logic
- Result aggregation system
- Progress tracking

#### Senior Supervisor (Claude Opus)
**Responsibilities:**
- Review Orchestrator's execution plan
- Validate architectural decisions
- Supervise complex/critical tasks
- Review worker output quality
- Handle escalations
- Make final decisions on conflicts

**When engaged:**
- User explicitly requests "senior review"
- Orchestrator identifies complexity > threshold
- Workers produce conflicting results
- Critical code changes (security, performance, data)
- New architectural patterns needed

**Tools:**
- Code review framework
- Architecture validation
- Quality metrics
- Decision logging

#### Worker: GLM (Subscription-based, Token-Heavy Tasks)
**Primary Responsibilities:**
- Writing comprehensive test suites
- Generating detailed documentation
- Creating examples and tutorials
- Simple CRUD operations
- Batch processing tasks

**Why GLM for these tasks:**
- Subscription model = fixed cost (economical for high token usage)
- Tests and docs require many tokens to generate
- Quality adequate for documentation
- Fast enough for these tasks

**Models:**
- `glm-4.5`: Complex test scenarios, detailed docs
- `glm-4.5-air`: Simple tests, basic documentation

#### Worker: Gemini 1.5 Pro (Fast, Multimodal, Token-Heavy)
**Primary Responsibilities:**
- Test case generation
- Documentation with examples
- Image/diagram analysis (multimodal)
- Quick iteration on drafts
- Data validation tasks

**Why Gemini for these tasks:**
- Fast response times for iteration
- Good at generating test scenarios
- Multimodal capabilities (analyze screenshots, diagrams)
- Efficient for high-token tasks

**Model:**
- `gemini-1.5-pro`: Primary model for these tasks

#### Worker: Claude Haiku (Fast, Simple Tasks)
**Primary Responsibilities:**
- Code formatting
- Simple refactoring (rename, extract method)
- Quick validation checks
- File operations
- Simple string transformations

**Why Haiku:**
- Fastest response time
- Lowest cost for simple operations
- Still high quality for straightforward tasks
- Good for rapid feedback loops

**Model:**
- `claude-3-haiku`: Fast simple operations

### Task Routing Logic

```python
class TaskRouter:
    def route_task(self, task_description, complexity, token_estimate):
        # High complexity → escalate to Senior
        if complexity > 8:
            return "senior"

        # Token-heavy tasks → GLM or Gemini
        if token_estimate > 10000:
            if "test" in task_description or "documentation" in task_description:
                # Prefer subscription-based for high tokens
                return "glm" if self.glm_available else "gemini"

        # Multimodal → Gemini
        if requires_multimodal(task_description):
            return "gemini"

        # Simple quick tasks → Haiku
        if complexity < 3 and token_estimate < 1000:
            return "haiku"

        # Default: delegate to Orchestrator's judgment
        return "orchestrator_decides"

Example Task Flow
User Request: "Add user authentication to the application with tests and documentation"

1. ORCHESTRATOR (Sonnet 4.5) receives request
   - Analyzes: Complex feature, needs architecture review
   - Escalates to SENIOR for architectural approval

2. SENIOR (Opus) reviews
   - Recommends: JWT-based auth, specific libraries
   - Approves plan, delegates back to Orchestrator

3. ORCHESTRATOR decomposes:
   Task A: Implement auth logic (complex) → SENIOR supervises
   Task B: Write unit tests (token-heavy) → GLM
   Task C: Write integration tests (token-heavy) → GEMINI
   Task D: Generate API documentation (token-heavy) → GLM
   Task E: Format code (simple) → HAIKU

4. Parallel execution:
   - SENIOR + ORCHESTRATOR: Auth implementation (collaborative)
   - GLM: Generates 50+ unit tests (subscription = cheap)
   - GEMINI: Creates integration test scenarios
   - GLM: Writes comprehensive API docs

5. Sequential cleanup:
   - HAIKU: Formats all new code

6. SENIOR: Final review of auth implementation

7. ORCHESTRATOR: Aggregates, presents to user

Cost Optimization Strategy
Principle: Use cheapest adequate model for each task

Task Type	Model	Reasoning
Planning/Coordination	Sonnet 4.5	Needs intelligence, but low token usage
Architecture Review	Opus	Critical decisions, worth the cost
Tests (high volume)	GLM	Subscription = fixed cost, unlimited tokens
Documentation	GLM	Same - subscription economical for docs
Multimodal	Gemini	Only model with vision capabilities
Simple operations	Haiku	Cheapest per token, adequate quality
Expected Savings: 60-80% vs using Opus for everything

Implementation Requirements
What Needs to Be Built
1. Core Orchestrator Enhancement
Current: orchestrator.py (simple routing)
Needed:
Task decomposition system
Complexity analysis
Token estimation
Parallel task execution
Result aggregation
State management
2. Senior Supervisor System
Needed:
Integration with Claude Opus API
Review framework
Escalation triggers
Decision logging
Quality metrics
3. Worker Abstractions
Needed:
Common Worker interface
Task queuing system
Parallel execution framework
Result formatting
Error handling & retry logic
4. Specialized Worker Implementations
GLM Worker: Enhanced glm_cli.py with Worker interface
Gemini Worker: Enhanced gemini wrapper with Worker interface
Haiku Worker: New Claude Haiku integration with Worker interface
5. Communication Layer
Needed:
Standard message format (JSON)
Task definitions
Result schema
Error reporting
Progress updates
6. Monitoring & Logging
Needed:
Token usage tracking
Cost estimation
Performance metrics
Task success/failure rates
Decision audit trail
Integration Points with Lumen Repo
Questions to Answer:

Does Lumen have hooks system already built?
Does Lumen have supervision/review implemented?
What's the state of worker abstractions in Lumen?
Are there better implementations of any components?
What can we salvage from each repo?
Files to Merge/Reconcile
Orchestrator logic (which version is more advanced?)
Worker implementations (compare both versions)
Hooks system (if exists in Lumen)
Supervision system (if exists in Lumen)
Configuration management
Testing frameworks
Next Steps
For This Session (simple-agents)
✅ Document current state (this file)
Ready for user to copy to Lumen project
For Next Session (Lumen)
Compare Lumen implementation with simple-agents baseline
Identify best components from each repo
Design merged architecture
Implement hierarchical SOLID system:
Orchestrator (Sonnet 4.5)
Senior Supervisor (Opus)
Workers (GLM, Gemini, Haiku)
Add hooks and supervision if not in Lumen
Implement cost tracking
Create comprehensive tests
Document final system
Technical Decisions to Make
1. Communication Protocol
REST API between agents?
Message queue (RabbitMQ, Redis)?
Direct function calls with asyncio?
gRPC for performance?
2. State Management
Centralized state in Orchestrator?
Distributed state across workers?
Database for task history?
In-memory only?
3. Failure Handling
Retry logic per worker?
Fallback to different worker?
Escalate failures to Senior?
User notification?
4. Concurrency Model
asyncio for Python async/await?
Thread pools?
Process pools?
Hybrid approach?
5. Configuration
YAML config files?
Environment variables?
Dynamic configuration?
Per-task config overrides?
Success Metrics
System should achieve:
Cost Reduction: 60-80% vs single-model approach
Quality: Senior review ensures high quality on critical tasks
Speed: Parallel execution of independent subtasks
Scalability: Easy to add new workers/models
Maintainability: SOLID principles = clean, testable code
Key Performance Indicators:
Average cost per user request
Task completion time (vs single-model baseline)
Success rate (% of tasks completed without error)
Token usage per task type
User satisfaction (quality of results)
Questions for Lumen Repo Analysis
When reviewing Lumen, check:

Architecture: Is there already a hierarchical system?
Hooks: What hooks exist? (pre-task, post-task, error hooks?)
Supervision: Is there a review/approval system?
Workers: How are workers implemented? Any abstractions?
State Management: How is task state tracked?
Configuration: How are models/workers configured?
Testing: What test infrastructure exists?
Monitoring: Any logging/metrics/cost tracking?
Error Handling: How are failures handled?
Documentation: What's already documented?
File Inventory: simple-agents Repo
simple-agents/
├── orchestrator.py (8860 bytes) - Core routing logic
├── glm_cli.py (4359 bytes) - GLM Python wrapper
├── gemini_wrapper.sh (530 bytes) - Gemini bash wrapper
├── gemini.exp (660 bytes) - Gemini expect automation
├── codex_wrapper.sh (525 bytes) - Codex bash wrapper
├── codex.exp (649 bytes) - Codex expect automation
├── glm_wrapper.sh (891 bytes) - GLM bash wrapper
├── glm.exp (643 bytes) - GLM expect automation
├── setup.sh (3624 bytes) - Installation script
├── test.sh (4181 bytes) - Test suite
├── README.md (6453 bytes) - Current documentation
├── SOLUTION_SUMMARY.md (1278 bytes) - Summary notes
├── _FILES_NEEDED.md (1303 bytes) - Missing files list
├── .gitignore (3293 bytes) - Git ignores
└── agent-new/
    └── GEMINI_CODEX_IMPLEMENTATION.md (4829 bytes) - Implementation notes

Total: 14 files, ~37KB of code/docs

Git Branch Status
Current branch: claude/merge-diverged-repos-013iVfFGk944eVkTEoLaXiCm
Status: Clean working directory
Recent commit: 04506bc - "Initial commit: Multi-LLM orchestration system"
End of Summary
This document represents the complete state of simple-agents and the desired target architecture.
