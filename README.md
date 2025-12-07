# Agent System

A comprehensive multi-agent development system designed for coordinated software engineering workflows. This system provides structured coordination between an orchestrator (Claude) and multiple specialized agents.

## Architecture Overview

The Agent System implements a hierarchical coordination model with distinct roles:

### Core Components

1. **Orchestrator (Claude)**: High-level coordination and decision-making
   - Manages overall project workflow
   - Delegates tasks to specialized agents
   - Ensures quality and consistency across implementations

2. **Specialized Agents**: Domain-specific implementers
   - Handle specific technical domains (backend, frontend, DevOps, etc.)
   - Operate with well-defined interfaces and constraints
   - Maintain autonomy within their specialized domains

3. **Coordination Framework**: Structured communication layer
   - Standardized interfaces between agents
   - Quality gates and validation mechanisms
   - Progress tracking and completion verification

### System Characteristics

- **Modular Design**: Each agent operates independently within its domain
- **Structured Communication**: Well-defined interfaces and protocols
- **Quality Assurance**: Built-in validation and quality gates
- **Scalable Architecture**: Easy to add new specialized agents
- **Process Transparency**: Clear workflow visibility and audit trails

## System Validation

The enhanced validation script (`validate.py`) provides comprehensive system health checks:

### Running Validation
```bash
cd agent-system
python3 validate.py
```

### Validation Coverage
- Directory structure validation
- Dependency checking and installation
- Script syntax and import validation
- Hook functionality testing
- Configuration file validation
- Agent communication testing
- Session state functionality
- Symlink validation
- Cross-agent review system
- Permission checking

### System Health Assessment
The validation script provides:
- Overall system health score (0-100%)
- Detailed check results with pass/fail status
- Actionable recommendations for fixes
- Clear success/failure reporting

See `docs/VALIDATION_SCRIPT.md` for detailed validation documentation.

## Installation Instructions

For new projects, see the following files for setup instructions:

- **Templates**: `/agent-system/templates/` - Project initialization templates
- **Configuration**: `/agent-system/config/` - System configuration files
- **Environment Setup**: `/agent-system/config/.env.example` - Environment variables template
- **Hook Settings**: `/agent-system/config/hooks_settings.json` - Hook configuration

Key installation points:
1. Copy templates to project root
2. Configure environment variables
3. Set up hooks for quality control
4. Initialize project structure
5. Run validation script to verify setup

## Agent Workflow

### Typical Workflow Process

1. **Project Analysis**: Orchestrator conducts initial project assessment
2. **Task Decomposition**: High-level tasks broken into domain-specific components
3. **Agent Assignment**: Tasks delegated to appropriate specialized agents
4. **Parallel Execution**: Agents work concurrently in their domains
5. **Quality Validation**: Results pass through quality gates
6. **Integration**: Components are integrated and tested
7. **Completion Verification**: Final validation against project requirements

### Communication Flow

- **Upward Communication**: Agents report progress and issues to orchestrator
- **Downward Communication**: Orchestrator provides guidance and constraints
- **Peer Communication**: Agents coordinate interfaces and dependencies
- **Artifact Exchange**: Structured exchange of deliverables between agents

## Directory Structure

```
agent-system/
├── commands/          # Executable command scripts
├── config/           # Configuration files and settings
├── docs/             # Documentation and guides
├── hooks/            # Quality control and validation hooks
│   ├── core/         # Core validation hooks
│   └── auxiliary/    # Helper and utility hooks
├── prompts/          # Agent-specific prompts and templates
├── scripts/          # Python utilities and coordination scripts
├── templates/        # Project initialization templates
└── validate.py       # System validation script
```

### Component Roles

- **Commands**: High-level operations and system commands
- **Hooks**: Quality control points and validation logic
- **Scripts**: Coordination and utility scripts
- **Templates**: Project initialization boilerplates
- **Prompts**: Agent-specific interaction patterns

## System Operation

### Claude as Orchestrator

Claude operates as the central orchestrator with these responsibilities:

- **Strategic Planning**: Defines high-level project architecture and approach
- **Resource Allocation**: Assigns tasks to appropriate specialized agents
- **Quality Oversight**: Ensures deliverables meet quality standards
- **Integration Management**: Coordinates between different agent outputs
- **Progress Tracking**: Monitors overall project progress and milestones

### Specialized Agents

Specialized agents operate with clear boundaries:

- **Domain Expertise**: Each agent focuses on specific technical domains
- **Interface Compliance**: Agents follow standardized interfaces and protocols
- **Autonomous Operation**: Agents execute tasks independently within constraints
- **Quality Accountability**: Agents ensure their deliverables meet quality standards

### Coordination Mechanisms

The system uses several coordination mechanisms:

- **Structured Prompts**: Well-defined interaction templates for consistent communication
- **Quality Gates**: Validation points that must be passed before proceeding
- **Artifact Standards**: Defined formats and structures for exchanged deliverables
- **Progress Reporting**: Regular status updates and milestone tracking

## Troubleshooting

For troubleshooting guidance, see `/docs/troubleshooting.md`. Key topics covered:
- Common issues and their solutions
- Debug hook failures and quality gate problems
- Agent communication troubleshooting
- Configuration and setup issues

## Best Practices

1. **Clear Task Definition**: Ensure tasks are well-defined before delegation
2. **Quality Gates**: Always pass through defined validation points
3. **Interface Compliance**: Maintain consistent interfaces between agents
4. **Progress Reporting**: Provide regular updates on task completion
5. **Documentation**: Keep documentation current with system changes

## Contributing

When extending the system:

1. **Define Clear Interfaces**: New agents must follow established patterns
2. **Implement Quality Hooks**: Add appropriate validation for new components
3. **Update Documentation**: Keep README and docs current
4. **Test Integration**: Ensure new components work with existing system
5. **Follow Templates**: Use established patterns for consistency

---

*For detailed implementation guidance, refer to the specific documentation files and templates referenced throughout this document.*