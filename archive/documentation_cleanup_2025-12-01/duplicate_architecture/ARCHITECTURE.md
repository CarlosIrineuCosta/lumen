# Lumen Multi-Agent System Architecture

## Overview

The Lumen Multi-Agent System is a portable, CLI-based coordination system that enables multiple AI agents to collaborate on software development tasks. It uses a combination of Python scripts, shell scripts, and configuration files to route tasks to appropriate LLMs based on task characteristics.

## System Components

### 1. Core Scripts

#### GLM Worker (`glm_worker.py`)
- **Purpose**: Primary workhorse for implementation tasks
- **Handles**: Testing, documentation, implementation, repetitive tasks
- **Interface**: Z.ai GLM API
- **Features**: Task-specific prompts, structured output, error handling

#### Codex Wrapper (`codex_wrapper.py`)
- **Purpose**: Security and performance review
- **Handles**: Code review, security audit, performance optimization
- **Interface**: Codex CLI tool
- **Features**: Security-focused analysis, optimization recommendations

#### Gemini Wrapper (`gemini_wrapper.py`)
- **Purpose**: Large context analysis (up to 1M tokens)
- **Handles**: Whole-project analysis, documentation generation
- **Interface**: Gemini CLI tool
- **Features**: Massive context support, holistic insights

#### Multi-LLM Coordinator (`multi_llm_coordinator.py`)
- **Purpose**: Intelligent task routing
- **Features**:
  - Automatic task analysis
  - Context size estimation
  - Keyword-based routing
  - Parallel execution support

### 2. Coordination Scripts

#### Agent Coordinator (`agent_coordinator.py`)
- Task tracking and status management
- Integration with AI services
- Coordination.md updates

#### Parallel Coordinator (`parallel_coordinator.py`)
- Spawns multiple GLM workers
- Conflict detection
- Unified proposal generation

#### Process Proposals (`process_proposals.py`)
- List and format agent proposals
- Interface between agents and Claude Code

### 3. Quality Assurance Hooks

#### Quality Gate (`quality_gate.py`)
- Cross-agent review enforcement
- PMM pattern validation
- Security and performance checks
- Routes work between Claude → GLM → Codex

#### Completion Checker (`completion_checker.py`)
- Test existence validation
- Pending delegation checks
- Documentation verification
- Lint and format checks

#### GLM Router (`glm_router.py`)
- Automatic task delegation to GLM
- Keyword-based routing logic
- State tracking
- Error handling

## Task Routing Logic

```python
def route_task(task_description, context_files):
    # Analyze task characteristics
    if 'test' in task or 'docs' in task:
        return 'GLM'  # Implementation
    if 'security' in task or 'review' in task:
        return 'Codex'  # Security review
    if estimated_tokens > 100000:
        return 'Gemini'  # Large context
    if 'analyze' in task:
        return 'OpenCode'  # Additional analysis
    return 'Claude'  # Architecture, design
```

## Integration Points

### 1. Claude Code Hooks
```json
{
  "hooks": {
    "PostToolUse": [{"command": "python agent-system/hooks/quality_gate.py"}],
    "Stop": [{"command": "python agent-system/hooks/completion_checker.py"}]
  }
}
```

### 2. VS Code Integration
- Task definitions for running agents
- Settings for Python environment
- Integrated terminal commands

### 3. Environment Variables
```env
GLM_API_KEY=...
CODEX_CLI_PATH=...
GEMINI_CLI_PATH=...
```

## Data Flow

```
User Request
    ↓
Claude Code (Architect)
    ↓
Task Analysis (keywords, context size)
    ↓
┌─────────────┬─────────────┬─────────────┐
│    GLM      │    Codex    │   Gemini    │
│  Testing    │   Security  │ Large Ctxt  │
│  Docs       │ Performance │ Analysis    │
│ Implementation│ Review     │             │
└─────────────┴─────────────┴─────────────┘
    ↓
Proposals/Reviews
    ↓
Claude Code Review
    ↓
Apply Changes
    ↓
Quality Gates
    ↓
Complete
```

## Security Considerations

1. **No API Calls**: All LLMs run locally via CLI tools
2. **Cross-Review**: Agents review each other's work
3. **Sandboxing**: GLM worker only reads, doesn't write
4. **Validation**: Multiple quality checks

## Performance Optimization

1. **Parallel Execution**: Multiple agents can work simultaneously
2. **Context Caching**: Reuse context between related tasks
3. **Selective Routing**: Only use expensive LLMs when needed
4. **Timeout Management**: Prevent runaway processes

## Extensibility

The system is designed to be easily extended:

1. **Add New LLMs**: Create wrapper script following the pattern
2. **Custom Routing**: Modify routing logic in multi_llm_coordinator.py
3. **New Hooks**: Add additional quality checks
4. **Integration**: Add new IDE or editor support

## Troubleshooting

### Common Issues

1. **GLM Worker Fails**: Check GLM_API_KEY and zai-sdk installation
2. **CLI Not Found**: Update paths in .env file
3. **Hooks Not Triggering**: Verify Claude Code settings
4. **Permission Errors**: Run `chmod +x` on scripts

### Debug Mode

Enable debug output:
```bash
export AGENT_DEBUG=1
python agent-system/scripts/multi_llm_coordinator.py --task "debug test"
```