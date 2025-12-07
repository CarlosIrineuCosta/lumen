#!/bin/bash
# Virtual Environment Rebuild Script for Lumen Project
# Automates Python virtual environment recreation with proper dependencies

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Project paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"
VENV_DIR="$BACKEND_DIR/venv"

log_info "Lumen Project Virtual Environment Rebuild"
log_info "Project Root: $PROJECT_ROOT"
log_info "Backend Dir: $BACKEND_DIR"
log_info "Venv Target: $VENV_DIR"

# Validate project structure
if [[ ! -d "$BACKEND_DIR" ]]; then
    log_error "Backend directory not found: $BACKEND_DIR"
    exit 1
fi

if [[ ! -f "$BACKEND_DIR/requirements.txt" ]]; then
    log_error "requirements.txt not found in backend directory"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>/dev/null || echo "Not found")
log_info "Python version: $PYTHON_VERSION"

if ! command -v python3 >/dev/null 2>&1; then
    log_error "Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

# Remove existing virtual environment if it exists
if [[ -d "$VENV_DIR" ]]; then
    log_warn "Removing existing virtual environment..."
    rm -rf "$VENV_DIR"
fi

# Create new virtual environment
log_info "Creating new virtual environment..."
cd "$BACKEND_DIR"
python3 -m venv venv

# Verify virtual environment was created
if [[ ! -f "$VENV_DIR/bin/activate" ]]; then
    log_error "Failed to create virtual environment"
    exit 1
fi

log_info "Virtual environment created successfully"

# Activate virtual environment and install dependencies
log_info "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip to latest version
log_info "Upgrading pip..."
python -m pip install --upgrade pip

# Install requirements
log_info "Installing project dependencies..."
pip install -r requirements.txt

# Verify key dependencies are installed
log_info "Verifying critical dependencies..."
CRITICAL_DEPS=("fastapi" "uvicorn" "sqlalchemy" "psycopg2-binary")

for dep in "${CRITICAL_DEPS[@]}"; do
    if pip show "$dep" >/dev/null 2>&1; then
        VERSION=$(pip show "$dep" | grep Version | cut -d' ' -f2)
        log_info "✓ $dep: $VERSION"
    else
        log_error "✗ Missing critical dependency: $dep"
        exit 1
    fi
done

# Show installed packages summary
log_info "Virtual environment rebuild complete!"
log_info "Installed packages: $(pip list | wc -l) packages"

# Show activation instructions
cat << EOF

${GREEN}Virtual Environment Ready!${NC}

To activate the virtual environment:
  cd $BACKEND_DIR
  source venv/bin/activate

To start the backend server:
  python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

To deactivate:
  deactivate

EOF

log_info "Virtual environment rebuild completed successfully"