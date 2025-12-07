#!/bin/bash

# =============================================================================
# Lumen Agent System Installation Script
# =============================================================================
# This script sets up the Lumen Multi-Agent System in a new project
# Creates directories, copies files, creates symlinks, and validates installation
# =============================================================================

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_SYSTEM_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(pwd)"
FORCE_INSTALL=false
VERBOSE=false

# Print functions
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Help function
show_help() {
    cat << EOF
Lumen Agent System Installation Script

This script sets up the Lumen Multi-Agent System in a new project.

USAGE:
    setup_hooks.sh [OPTIONS]

OPTIONS:
    -f, --force        Force installation even if directories exist
    -v, --verbose      Enable verbose output
    -h, --help         Show this help message

EXAMPLES:
    ./setup_hooks.sh                      # Normal installation
    ./setup_hooks.sh --force              # Force overwrite existing files
    ./setup_hooks.sh --verbose            # Verbose output

DESCRIPTION:
    The script will:
    1. Create required directories in the project root
    2. Copy template files with relative paths
    3. Create symlinks for agent-system components
    4. Set up Claude Code integration
    5. Validate the installation
EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -f|--force)
                FORCE_INSTALL=true
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# Validate prerequisites
validate_prerequisites() {
    print_info "Validating prerequisites..."

    # Check if we're in a project root
    if [[ ! -d "$AGENT_SYSTEM_DIR" ]]; then
        print_error "Agent system directory not found at $AGENT_SYSTEM_DIR"
        exit 1
    fi

    # Check if agent-system structure exists
    required_agent_dirs=("commands" "config" "docs" "hooks" "prompts" "scripts" "templates")
    for dir in "${required_agent_dirs[@]}"; do
        if [[ ! -d "$AGENT_SYSTEM_DIR/$dir" ]]; then
            print_error "Required agent-system directory missing: $dir"
            exit 1
        fi
    done

    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        print_warning "Python3 not found. Some features may not work properly."
    fi

    print_success "Prerequisites validated"
}

# Create project directories
create_directories() {
    print_info "Creating project directories..."

    local dirs=(
        ".agents"
        ".agents/reviews"
        ".agents/backup"
        ".agents/logs"
        "scripts"
        "scripts/agents"
        "docs"
        "docs/agent_system"
        "docs/project_history"
    )

    for dir in "${dirs[@]}"; do
        local target_dir="$PROJECT_ROOT/$dir"
        if [[ -d "$target_dir" && "$FORCE_INSTALL" == false ]]; then
            print_warning "Directory exists, skipping: $dir"
        else
            if mkdir -p "$target_dir"; then
                print_success "Created directory: $dir"
            else
                print_error "Failed to create directory: $dir"
                exit 1
            fi
        fi
    done
}

# Copy template files
copy_templates() {
    print_info "Copying template files..."

    # Check if templates exist in the templates directory first
    local template_source="$AGENT_SYSTEM_DIR/templates"
    if [[ ! -d "$template_source" ]]; then
        template_source="$AGENT_SYSTEM_DIR"
    fi

    # Create basic coordination files if they don't exist
    local templates=(
        "COORDINATION.md"
        "AGENT_SUMMARY.md"
        "TASKS_TRACKING.md"
    )

    for template in "${templates[@]}"; do
        local source="$template_source/$template"
        local target="$PROJECT_ROOT/$template"

        # Create default files if not found
        if [[ ! -f "$source" ]]; then
            if [[ ! -f "$target" ]]; then
                print_info "Creating default $template..."
                case "$template" in
                    "COORDINATION.md")
                        cat > "$target" << 'EOF'
# Lumen Agent Coordination Status

**Last Updated**: $(date '+%Y-%m-%d %H:%M')

## Current Task
- **Task**: Not assigned
- **Status**: Idle
- **Details**: Waiting for task assignment

## Active Agents
- **Orchestrator**: Claude
- **Backend**: Available
- **Frontend**: Available
- **DevOps**: Available

## Recent Activities
- System initialization completed
- Ready for task assignment

## Next Steps
1. Assign tasks through orchestrator
2. Track progress in coordination logs
3. Maintain quality gates
EOF
                        ;;
                    "AGENT_SUMMARY.md")
                        cat > "$target" << 'EOF'
# Lumen Agent Activity Summary

**Generated**: $(date '+%Y-%m-%d %H:%M')

## System Status
- **Overall Status**: Active
- **Last Activity**: System initialization
- **Quality Gates**: All clear

## Agent Activities
### Orchestrator (Claude)
- Role: High-level coordination and decision-making
- Status: Ready
- Recent: System setup completed

### Backend Agent
- Role: Backend development and API management
- Status: Available
- Recent: No tasks assigned

### Frontend Agent
- Role: Frontend development and UI implementation
- Status: Available
- Recent: No tasks assigned

### DevOps Agent
- Role: Deployment and infrastructure management
- Status: Available
- Recent: No tasks assigned

## Quality Assurance
- **Quality Gates**: All passed
- **Code Reviews**: Pending
- **Validation**: Complete
EOF
                        ;;
                    "TASKS_TRACKING.md")
                        cat > "$target" << 'EOF'
# Lumen Task Tracking

**Last Updated**: $(date '+%Y-%m-%d %H:%M')

## Task Queue
- **No active tasks**

## Completed Tasks
- System initialization ✅

## Task Categories
1. **Development Tasks**
   - Backend development
   - Frontend development
   - API integration

2. **Quality Assurance**
   - Code review
   - Testing
   - Validation

3. **DevOps Tasks**
   - Deployment
   - Infrastructure
   - Monitoring

## Task Assignment
Tasks are assigned through the orchestrator (Claude) and delegated to appropriate specialized agents.

## Progress Tracking
- Use AGENT_SUMMARY.md for activity tracking
- Use COORDINATION.md for current status
- Use .agents/ directory for detailed logs
EOF
                        ;;
                esac
                print_success "Created default template: $template"
            else
                print_warning "Template exists, skipping: $template"
            fi
        else
            if [[ -f "$target" && "$FORCE_INSTALL" == false ]]; then
                print_warning "File exists, skipping: $template"
            else
                if cp "$source" "$target"; then
                    print_success "Copied template: $template"
                else
                    print_error "Failed to copy template: $template"
                    exit 1
                fi
            fi
        fi
    done
}

# Copy configuration files
copy_configs() {
    print_info "Copying configuration files..."

    # Copy environment template
    local env_source="$AGENT_SYSTEM_DIR/config/.env.example"
    local env_target="$PROJECT_ROOT/.env.example"

    if [[ -f "$env_source" ]]; then
        if [[ -f "$env_target" && "$FORCE_INSTALL" == false ]]; then
            print_warning "Environment file exists, skipping: .env.example"
        else
            if cp "$env_source" "$env_target"; then
                print_success "Copied environment template: .env.example"
            else
                print_error "Failed to copy environment template"
                exit 1
            fi
        fi
    fi

    # Copy hook settings
    local hooks_source="$AGENT_SYSTEM_DIR/config/hooks_settings.json"
    local hooks_target_dir="$PROJECT_ROOT/.claude"
    local hooks_target="$hooks_target_dir/hooks_settings.json"

    # Create .claude directory if it doesn't exist
    if [[ ! -d "$hooks_target_dir" ]]; then
        mkdir -p "$hooks_target_dir"
        print_info "Created .claude directory"
    fi

    if [[ -f "$hooks_source" ]]; then
        if [[ -f "$hooks_target" && "$FORCE_INSTALL" == false ]]; then
            print_warning "Hook settings exist, skipping: hooks_settings.json"
        else
            if cp "$hooks_source" "$hooks_target"; then
                print_success "Copied hook settings: hooks_settings.json"
            else
                print_error "Failed to copy hook settings"
                exit 1
            fi
        fi
    fi
}

# Create symlinks
create_symlinks() {
    print_info "Creating symlinks..."

    local symlinks=(
        "agent-system"
        "ai-agent.sh"
        "codex_wrapper.py"
        "gemini_wrapper.py"
        "multi_llm_coordinator.py"
        "agent_coordinator.py"
        "parallel_coordinator.py"
        "process_proposals.py"
        "hooks"
    )

    # Create agent-system directory if it doesn't exist
    if [[ ! -L "$PROJECT_ROOT/agent-system" && ! -d "$PROJECT_ROOT/agent-system" ]]; then
        ln -sf "$AGENT_SYSTEM_DIR" "$PROJECT_ROOT/agent-system"
        print_success "Created symlink: agent-system -> $AGENT_SYSTEM_DIR"
    elif [[ -L "$PROJECT_ROOT/agent-system" ]]; then
        if [[ "$FORCE_INSTALL" == true ]]; then
            rm -f "$PROJECT_ROOT/agent-system"
            ln -sf "$AGENT_SYSTEM_DIR" "$PROJECT_ROOT/agent-system"
            print_success "Updated symlink: agent-system -> $AGENT_SYSTEM_DIR"
        else
            print_warning "Symlink exists: agent-system"
        fi
    elif [[ -d "$PROJECT_ROOT/agent-system" ]]; then
        if [[ "$FORCE_INSTALL" == true ]]; then
            print_warning "agent-system is a real directory, not a symlink. Skipping for safety."
        else
            print_warning "agent-system directory exists, skipping: agent-system"
        fi
    fi

    # Handle ai-agent.sh symlink (special case - goes to scripts/agents/)
    if [[ -f "$AGENT_SYSTEM_DIR/scripts/ai-agent.sh" ]]; then
        local ai_agent_source="$AGENT_SYSTEM_DIR/scripts/ai-agent.sh"
        local ai_agent_target="$PROJECT_ROOT/scripts/agents/ai-agent.sh"

        if [[ ! -d "$PROJECT_ROOT/scripts/agents" ]]; then
            mkdir -p "$PROJECT_ROOT/scripts/agents"
        fi

        if [[ -L "$ai_agent_target" ]]; then
            if [[ "$FORCE_INSTALL" == true ]]; then
                rm -f "$ai_agent_target"
                ln -sf "$ai_agent_source" "$ai_agent_target"
                print_success "Updated symlink: scripts/agents/ai-agent.sh"
            else
                print_warning "Symlink exists: scripts/agents/ai-agent.sh"
            fi
        elif [[ -e "$ai_agent_target" ]]; then
            if [[ "$FORCE_INSTALL" == true ]]; then
                rm -rf "$ai_agent_target"
                ln -sf "$ai_agent_source" "$ai_agent_target"
                print_success "Overwrote and created symlink: scripts/agents/ai-agent.sh"
            else
                print_warning "File exists, skipping: scripts/agents/ai-agent.sh"
            fi
        else
            ln -sf "$ai_agent_source" "$ai_agent_target"
            print_success "Created symlink: scripts/agents/ai-agent.sh"
        fi
    else
        print_warning "Source not found for symlink: scripts/ai-agent.sh"
    fi

    # Create other symlinks in project root
    for symlink in "${symlinks[@]:1}"; do
        # Skip ai-agent.sh as it's handled above
        if [[ "$symlink" == "ai-agent.sh" ]]; then
            continue
        fi

        local source="$AGENT_SYSTEM_DIR/scripts/$symlink"
        local target="$PROJECT_ROOT/scripts/$symlink"

        if [[ -f "$source" || -d "$source" ]]; then
            if [[ -L "$target" ]]; then
                if [[ "$FORCE_INSTALL" == true ]]; then
                    rm -f "$target"
                    ln -sf "$source" "$target"
                    print_success "Updated symlink: scripts/$symlink"
                else
                    print_warning "Symlink exists: scripts/$symlink"
                fi
            elif [[ -e "$target" ]]; then
                if [[ "$FORCE_INSTALL" == true ]]; then
                    rm -rf "$target"
                    ln -sf "$source" "$target"
                    print_success "Overwrote and created symlink: scripts/$symlink"
                else
                    print_warning "File exists, skipping: scripts/$symlink"
                fi
            else
                ln -sf "$source" "$target"
                print_success "Created symlink: scripts/$symlink"
            fi
        else
            print_warning "Source not found for symlink: scripts/$symlink"
        fi
    done

    # Create hooks symlink
    local hooks_source="$AGENT_SYSTEM_DIR/hooks"
    local hooks_target="$PROJECT_ROOT/hooks"

    if [[ -d "$hooks_source" ]]; then
        if [[ -L "$hooks_target" ]]; then
            if [[ "$FORCE_INSTALL" == true ]]; then
                rm -f "$hooks_target"
                ln -sf "$hooks_source" "$hooks_target"
                print_success "Updated symlink: hooks"
            else
                print_warning "Symlink exists: hooks"
            fi
        elif [[ -e "$hooks_target" ]]; then
            if [[ "$FORCE_INSTALL" == true ]]; then
                rm -rf "$hooks_target"
                ln -sf "$hooks_source" "$hooks_target"
                print_success "Overwrote and created symlink: hooks"
            else
                print_warning "Directory exists, skipping: hooks"
            fi
        else
            ln -sf "$hooks_source" "$hooks_target"
            print_success "Created symlink: hooks"
        fi
    else
        print_warning "Source not found for symlink: hooks"
    fi
}

# Set up VS Code configuration
setup_vscode() {
    print_info "Setting up VS Code configuration..."

    local vscode_dir="$PROJECT_ROOT/.vscode"
    if [[ ! -d "$vscode_dir" ]]; then
        mkdir -p "$vscode_dir"
    fi

    # Copy VS Code settings
    local vscode_settings="$AGENT_SYSTEM_DIR/templates/.vscode/settings.json"
    local vscode_tasks="$AGENT_SYSTEM_DIR/templates/.vscode/tasks.json"
    local vscode_launch="$AGENT_SYSTEM_DIR/templates/.vscode/launch.json"

    if [[ -f "$vscode_settings" ]]; then
        cp "$vscode_settings" "$vscode_dir/settings.json"
        print_success "Copied VS Code settings"
    fi

    if [[ -f "$vscode_tasks" ]]; then
        cp "$vscode_tasks" "$vscode_dir/tasks.json"
        print_success "Copied VS Code tasks"
    fi

    if [[ -f "$vscode_launch" ]]; then
        cp "$vscode_launch" "$vscode_dir/launch.json"
        print_success "Copied VS Code launch configuration"
    fi
}

# Set up Python virtual environment
setup_venv() {
    print_info "Setting up Python virtual environment..."

    local venv_path="$AGENT_SYSTEM_DIR/scripts/.venv"

    if [[ ! -d "$venv_path" ]]; then
        print_info "Creating Python virtual environment..."
        cd "$AGENT_SYSTEM_DIR/scripts"
        python3 -m venv .venv
        cd "$PROJECT_ROOT"
        print_success "Created virtual environment: $venv_path"
    else
        print_success "Virtual environment already exists: $venv_path"
    fi

    # Install requirements
    local requirements="$AGENT_SYSTEM_DIR/scripts/requirements.txt"
    if [[ -f "$requirements" ]]; then
        print_info "Installing Python dependencies..."
        cd "$AGENT_SYSTEM_DIR/scripts"
        .venv/bin/pip install -r requirements.txt
        cd "$PROJECT_ROOT"
        print_success "Installed Python dependencies"
    fi
}

# Set up file permissions
setup_permissions() {
    print_info "Setting up file permissions..."

    # Make scripts executable
    local scripts=(
        "$AGENT_SYSTEM_DIR/scripts/ai-agent.sh"
        "$AGENT_SYSTEM_DIR/scripts/review_entire_system.sh"
        "$AGENT_SYSTEM_DIR/scripts/multi_llm_coordinator.py"
        "$AGENT_SYSTEM_DIR/scripts/agent_coordinator.py"
        "$AGENT_SYSTEM_DIR/scripts/parallel_coordinator.py"
        "$AGENT_SYSTEM_DIR/scripts/process_proposals.py"
        "$AGENT_SYSTEM_DIR/scripts/codex_wrapper.py"
        "$AGENT_SYSTEM_DIR/scripts/gemini_wrapper.py"
        "$AGENT_SYSTEM_DIR/validate.py"
    )

    for script in "${scripts[@]}"; do
        if [[ -f "$script" ]]; then
            chmod +x "$script"
            if [[ "$VERBOSE" == true ]]; then
                print_info "Made executable: $script"
            fi
        fi
    done

    # Set proper permissions for directories
    chmod 755 "$PROJECT_ROOT/.agents"
    chmod 755 "$AGENT_SYSTEM_DIR"
}

# Validate installation
validate_installation() {
    print_info "Validating installation..."

    local validation_errors=0

    # Check required directories
    local required_dirs=(
        ".agents"
        ".agents/reviews"
        ".agents/backup"
        ".agents/logs"
        "agent-system"
        "agent-system/scripts"
        "agent-system/hooks"
        "agent-system/config"
        "agent-system/templates"
    )

    for dir in "${required_dirs[@]}"; do
        if [[ ! -d "$PROJECT_ROOT/$dir" ]]; then
            print_error "Missing directory: $dir"
            validation_errors=$((validation_errors + 1))
        fi
    done

    # Check required files
    local required_files=(
        "COORDINATION.md"
        "AGENT_SUMMARY.md"
        "TASKS_TRACKING.md"
        ".env.example"
        ".claude/hooks_settings.json"
        "agent-system/validate.py"
        "agent-system/scripts/agent_coordinator.py"
        "agent-system/hooks/core/quality_gate.py"
        "agent-system/hooks/core/completion_checker.py"
    )

    for file in "${required_files[@]}"; do
        if [[ ! -f "$PROJECT_ROOT/$file" ]]; then
            print_error "Missing file: $file"
            validation_errors=$((validation_errors + 1))
        fi
    done

    # Check symlinks
    local symlinks=(
        "agent-system"
        "scripts/agents/ai-agent.sh"
        "scripts/codex_wrapper.py"
        "scripts/gemini_wrapper.py"
        "scripts/multi_llm_coordinator.py"
        "scripts/agent_coordinator.py"
        "scripts/parallel_coordinator.py"
        "scripts/process_proposals.py"
        "hooks"
    )

    for symlink in "${symlinks[@]}"; do
        if [[ ! -L "$PROJECT_ROOT/$symlink" ]]; then
            print_error "Missing or broken symlink: $symlink"
            validation_errors=$((validation_errors + 1))
        fi
    done

    # Check additional script symlinks
    local script_symlinks=(
        "codex_wrapper.py"
        "gemini_wrapper.py"
        "multi_llm_coordinator.py"
        "agent_coordinator.py"
        "parallel_coordinator.py"
        "process_proposals.py"
    )

    for script in "${script_symlinks[@]}"; do
        if [[ ! -L "$PROJECT_ROOT/scripts/$script" ]]; then
            print_error "Missing or broken symlink: scripts/$script"
            validation_errors=$((validation_errors + 1))
        fi
    done

    if [[ $validation_errors -eq 0 ]]; then
        print_success "Installation validation passed!"
    else
        print_error "Installation validation failed with $validation_errors errors"
        return 1
    fi
}

# Generate post-installation instructions
generate_instructions() {
    print_info "Generating post-installation instructions..."

    cat << EOF > "$PROJECT_ROOT/AGENT_SYSTEM_SETUP.md"
# Agent System Setup Instructions

This document provides instructions for using the Lumen Multi-Agent System that has been set up in this project.

## Next Steps

### 1. Environment Configuration
- Copy \`.\env.example\` to \`.\env\` and configure your API keys
- The system supports GLM (no API key needed), Codex, Gemini, and other LLMs

### 2. Claude Code Integration
- The system is integrated with Claude Code hooks for automatic quality control
- Hook settings are configured in \`.\claude/hooks_settings.json\`

### 3. Available Commands

#### System Validation
\`\`\`bash
./agent-system/validate.py
\`\`\`

#### Agent Operations
\`\`\`bash
# Run AI agent
./scripts/agents/ai-agent.sh

# Coordinate agents
./agent-system/scripts/agent_coordinator.py

# Process proposals
./agent-system/scripts/process_proposals.py

# Multiple LLM coordination
./agent-system/scripts/multi_llm_coordinator.py
\`\`\`

#### Quality Control
\`\`\`bash
# Quality gate check
./agent-system/hooks/core/quality_gate.py

# Completion checker
./agent-system/hooks/core/completion_checker.py

# Session tracking
./agent-system/hooks/session/session_tracker.py
\`\`\`

### 4. Project Management

#### Coordination Files
- \`COORDINATION.md\` - Project coordination status
- \`AGENT_SUMMARY.md\` - Agent activity summary
- \`TASKS_TRACKING.md\` - Task progress tracking

#### Directories
- \`.agents/\` - Agent data and reviews
- \`.agents/reviews/\` - Code reviews and feedback
- \`.agents/backup/\` - Backup files
- \`.agents/logs/\` - Agent activity logs

### 5. VS Code Integration

The system includes VS Code configuration for:
- Python environment setup
- Task runner configuration
- Debugging setup
- Code formatting and linting

### 6. Features

#### Multi-Agent Coordination
- Orchestrator (Claude) manages overall workflow
- Specialized agents handle specific domains
- Structured communication between agents
- Quality gates and validation mechanisms

#### Supported LLMs
- **GLM**: Integrated through Claude Code (no API key needed)
- **Codex**: For code generation and review
- **Gemini**: For general AI assistance
- **Multi-LLM Coordination**: Use multiple models simultaneously

#### Quality Control
- Automatic quality gate validation
- Root protection hooks
- Session tracking
- Progress monitoring

### 7. Troubleshooting

#### Common Issues
- **Permission errors**: Run \`chmod +x\` on script files
- **Python import errors**: Ensure virtual environment is set up
- **Hook failures**: Check hook settings in \`.\claude/hooks_settings.json\`
- **Symlink errors**: Use \`--force\` option to recreate symlinks

#### Validation
Run the validation script to check system integrity:
\`\`\`bash
./agent-system/validate.py
\`\`\`

### 8. Customization

#### Adding New Agents
1. Create agent scripts in \`agent-system/scripts/\`
2. Add hooks in \`agent-system/hooks/\`
3. Update configuration in \`agent-system/config/\`
4. Update documentation

#### Modifying Templates
- Templates are in \`agent-system/templates/\`
- VS Code settings in \`agent-system/templates/.vscode/\`
- Update project files as needed

## Support

For issues or questions, refer to:
- \`agent-system/README.md\` - System documentation
- \`agent-system/docs/\` - Detailed guides
- \`COORDINATION.md\` - Current project status
EOF

    print_success "Generated setup instructions: AGENT_SYSTEM_SETUP.md"
}

# Main installation function
main() {
    print_info "Starting Lumen Agent System installation..."
    print_info "Project root: $PROJECT_ROOT"
    print_info "Agent system directory: $AGENT_SYSTEM_DIR"

    # Parse arguments
    parse_args "$@"

    # Execute installation steps
    validate_prerequisites
    create_directories
    copy_templates
    copy_configs
    create_symlinks
    setup_vscode
    setup_venv
    setup_permissions
    validate_installation
    generate_instructions

    # Print completion message
    print_success "Lumen Agent System installation completed successfully!"

    cat << EOF

## Installation Summary

✅ Directories created in project root
✅ Template files copied
✅ Configuration files set up
✅ Symlinks created for agent-system components
✅ VS Code configuration applied
✅ Python virtual environment set up
✅ File permissions configured
✅ Installation validated
✅ Setup instructions generated

## Quick Start

1. Validate the system: \`./agent-system/validate.py\`
2. Read setup instructions: \`cat AGENT_SYSTEM_SETUP.md\`
3. Start using the agent system with Claude Code

The Lumen Multi-Agent System is now ready for use in your project!
EOF
}

# Run main function with all arguments
main "$@"