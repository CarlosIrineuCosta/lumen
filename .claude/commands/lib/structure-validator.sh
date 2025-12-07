#!/bin/bash
# Structure-Independent Validation Library for Lumen Commands
# This library provides functions to dynamically detect project structure
# and validate required files without hardcoded paths

# Global variables for detected paths
declare -g PROJECT_ROOT=""
declare -g BACKEND_DIR=""
declare -g FRONTEND_DIR=""
declare -g SCRIPTS_DIR=""
declare -g PYTHON_VENV=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_debug() {
    echo -e "${BLUE}[DEBUG]${NC} $1"
}

# Detect project root directory
# Looks for key indicators: CLAUDE.md, backend/, .git/
detect_project_root() {
    local current_dir=$(pwd)
    local search_dir="$current_dir"
    
    # Search upwards for project indicators
    while [[ "$search_dir" != "/" ]]; do
        if [[ -f "$search_dir/CLAUDE.md" ]] && [[ -d "$search_dir/backend" ]] && [[ -d "$search_dir/.git" ]]; then
            PROJECT_ROOT="$search_dir"
            log_debug "Project root detected: $PROJECT_ROOT"
            return 0
        fi
        search_dir=$(dirname "$search_dir")
    done
    
    # Fallback: check if we're already in a valid project directory
    if [[ -f "./CLAUDE.md" ]] && [[ -d "./backend" ]]; then
        PROJECT_ROOT=$(pwd)
        log_debug "Project root detected (current dir): $PROJECT_ROOT"
        return 0
    fi
    
    log_error "Could not detect project root. Ensure you're in the Lumen project directory."
    return 1
}

# Detect backend directory
# Looks for Python app with FastAPI main.py
detect_backend_dir() {
    if [[ -z "$PROJECT_ROOT" ]]; then
        log_error "Project root not set. Call detect_project_root first."
        return 1
    fi
    
    # Common backend locations to check
    local backend_candidates=(
        "$PROJECT_ROOT/backend"
        "$PROJECT_ROOT/server"
        "$PROJECT_ROOT/api"
    )
    
    for dir in "${backend_candidates[@]}"; do
        if [[ -d "$dir" ]] && [[ -f "$dir/app/main.py" || -f "$dir/main.py" ]]; then
            BACKEND_DIR="$dir"
            log_debug "Backend directory detected: $BACKEND_DIR"
            return 0
        fi
    done
    
    # Search for any directory with FastAPI main.py
    local found_backend=$(find "$PROJECT_ROOT" -name "main.py" -path "*/app/*" -exec dirname {} \; 2>/dev/null | head -1)
    if [[ -n "$found_backend" ]]; then
        BACKEND_DIR=$(dirname "$found_backend")
        log_debug "Backend directory found via search: $BACKEND_DIR"
        return 0
    fi
    
    log_error "Backend directory not found. Expected structure with app/main.py"
    return 1
}

# Detect frontend directory
# Looks for HTML files and static assets
detect_frontend_dir() {
    if [[ -z "$PROJECT_ROOT" ]]; then
        log_error "Project root not set. Call detect_project_root first."
        return 1
    fi
    
    # Common frontend locations to check
    local frontend_candidates=(
        "$PROJECT_ROOT/frontend"
        "$PROJECT_ROOT/client"
        "$PROJECT_ROOT/web"
        "$PROJECT_ROOT/public"
    )
    
    for dir in "${frontend_candidates[@]}"; do
        if [[ -d "$dir" ]] && [[ -f "$dir/lumen-app.html" || -f "$dir/index.html" ]]; then
            FRONTEND_DIR="$dir"
            log_debug "Frontend directory detected: $FRONTEND_DIR"
            return 0
        fi
    done
    
    # Search for lumen-app.html specifically
    local found_frontend=$(find "$PROJECT_ROOT" -name "lumen-app.html" -exec dirname {} \; 2>/dev/null | head -1)
    if [[ -n "$found_frontend" ]]; then
        FRONTEND_DIR="$found_frontend"
        log_debug "Frontend directory found via search: $FRONTEND_DIR"
        return 0
    fi
    
    log_error "Frontend directory not found. Expected lumen-app.html or index.html"
    return 1
}

# Detect scripts directory
detect_scripts_dir() {
    if [[ -z "$PROJECT_ROOT" ]]; then
        log_error "Project root not set. Call detect_project_root first."
        return 1
    fi
    
    # Common script locations
    local script_candidates=(
        "$PROJECT_ROOT/scripts"
        "$PROJECT_ROOT/bin"
        "$PROJECT_ROOT/tools"
    )
    
    for dir in "${script_candidates[@]}"; do
        if [[ -d "$dir" ]] && [[ -x "$dir/server-manager.sh" || -x "$dir/session-start.sh" ]]; then
            SCRIPTS_DIR="$dir"
            log_debug "Scripts directory detected: $SCRIPTS_DIR"
            return 0
        fi
    done
    
    # Search for server-manager.sh
    local found_scripts=$(find "$PROJECT_ROOT" -name "server-manager.sh" -executable -exec dirname {} \; 2>/dev/null | head -1)
    if [[ -n "$found_scripts" ]]; then
        SCRIPTS_DIR="$found_scripts"
        log_debug "Scripts directory found via search: $SCRIPTS_DIR"
        return 0
    fi
    
    log_warn "Scripts directory not found. Some commands may not work."
    return 1
}

# Detect Python virtual environment
detect_python_venv() {
    if [[ -z "$BACKEND_DIR" ]]; then
        log_error "Backend directory not set. Call detect_backend_dir first."
        return 1
    fi
    
    # Common venv locations
    local venv_candidates=(
        "$BACKEND_DIR/venv"
        "$BACKEND_DIR/.venv"
        "$BACKEND_DIR/env"
        "$PROJECT_ROOT/venv"
        "$PROJECT_ROOT/.venv"
    )
    
    for venv in "${venv_candidates[@]}"; do
        if [[ -f "$venv/bin/activate" ]]; then
            PYTHON_VENV="$venv"
            log_debug "Python venv detected: $PYTHON_VENV"
            return 0
        fi
    done
    
    log_error "Python virtual environment not found. Expected venv/bin/activate"
    return 1
}

# Initialize all paths - main function to call
init_project_structure() {
    log_info "Detecting project structure..."
    
    detect_project_root || return 1
    detect_backend_dir || return 1
    detect_frontend_dir || return 1
    detect_scripts_dir || log_warn "Scripts directory not found - some features may be limited"
    detect_python_venv || return 1
    
    log_info "Project structure detection complete"
    return 0
}

# Validate critical files exist
validate_critical_files() {
    local validation_failed=0
    
    log_info "Validating critical files..."
    
    # Backend validation
    if [[ -n "$BACKEND_DIR" ]]; then
        local critical_backend=(
            "$BACKEND_DIR/app/main.py:Backend main application"
            "$BACKEND_DIR/requirements.txt:Python dependencies"
            "$PYTHON_VENV/bin/activate:Python virtual environment"
        )
        
        for file_desc in "${critical_backend[@]}"; do
            local file_path="${file_desc%%:*}"
            local description="${file_desc##*:}"
            
            if [[ -f "$file_path" ]]; then
                log_info "✓ $description: $file_path"
            else
                log_error "✗ Missing $description: $file_path"
                validation_failed=1
            fi
        done
    fi
    
    # Frontend validation
    if [[ -n "$FRONTEND_DIR" ]]; then
        local critical_frontend=(
            "$FRONTEND_DIR/lumen-app.html:Main application HTML"
        )
        
        for file_desc in "${critical_frontend[@]}"; do
            local file_path="${file_desc%%:*}"
            local description="${file_desc##*:}"
            
            if [[ -f "$file_path" ]]; then
                log_info "✓ $description: $file_path"
            else
                log_error "✗ Missing $description: $file_path"
                validation_failed=1
            fi
        done
    fi
    
    # Scripts validation
    if [[ -n "$SCRIPTS_DIR" ]]; then
        local critical_scripts=(
            "$SCRIPTS_DIR/server-manager.sh:Server management script"
        )
        
        for file_desc in "${critical_scripts[@]}"; do
            local file_path="${file_desc%%:*}"
            local description="${file_desc##*:}"
            
            if [[ -x "$file_path" ]]; then
                log_info "✓ $description: $file_path"
            else
                log_warn "! Missing or not executable $description: $file_path"
            fi
        done
    fi
    
    return $validation_failed
}

# Get project URLs based on detected structure
get_project_urls() {
    if [[ -z "$PROJECT_ROOT" ]]; then
        log_error "Project structure not initialized. Call init_project_structure first."
        return 1
    fi
    
    # Default Tailscale IP (can be made configurable)
    local HOST_IP="100.106.201.33"
    
    echo "Backend API: http://$HOST_IP:8080"
    echo "API Docs: http://$HOST_IP:8080/docs"
    echo "API Redoc: http://$HOST_IP:8080/redoc"
    echo "Frontend: http://$HOST_IP:8000"
    echo "Main App: http://$HOST_IP:8000/lumen-app.html"
}

# Create backup directory with timestamp
create_backup_dir() {
    local backup_base="${PROJECT_ROOT}/backup"
    local timestamp=$(date +%Y%m%d-%H%M%S)
    local backup_dir="${backup_base}/backup-${timestamp}"
    
    mkdir -p "$backup_dir"
    echo "$backup_dir"
}

# Check if we're in a valid project directory
check_project_context() {
    if ! detect_project_root; then
        cat << EOF
${RED}ERROR: Not in a valid Lumen project directory${NC}

This command requires being run from within the Lumen project directory.
The project should contain:
  - CLAUDE.md (project instructions)
  - backend/ directory (development files)
  - .git/ directory (version control)

Please navigate to your Lumen project directory and try again.
EOF
        return 1
    fi
    return 0
}

# Print detected structure (for debugging)
print_structure() {
    if [[ -z "$PROJECT_ROOT" ]]; then
        log_error "Project structure not initialized"
        return 1
    fi
    
    cat << EOF
${GREEN}Detected Project Structure:${NC}
Project Root: $PROJECT_ROOT
Backend Dir:  $BACKEND_DIR
Frontend Dir: $FRONTEND_DIR
Scripts Dir:  $SCRIPTS_DIR
Python Venv:  $PYTHON_VENV

$(get_project_urls)
EOF
}

# Export functions for use in other scripts
export -f log_info log_warn log_error log_debug
export -f detect_project_root detect_backend_dir detect_frontend_dir detect_scripts_dir detect_python_venv
export -f init_project_structure validate_critical_files get_project_urls
export -f create_backup_dir check_project_context print_structure