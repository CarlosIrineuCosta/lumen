#!/bin/bash
# Mandatory server startup script with proper environment loading
# Use this script instead of running uvicorn directly to avoid database connection issues

set -e  # Exit on any error

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"

echo "Starting Lumen backend server..."
echo "Project root: $PROJECT_ROOT"
echo "Backend directory: $BACKEND_DIR"

# Check if backend directory exists
if [[ ! -d "$BACKEND_DIR" ]]; then
    echo "Error: Backend directory not found at $BACKEND_DIR"
    exit 1
fi

# Check if .env file exists
ENV_FILE="$BACKEND_DIR/.env"
if [[ ! -f "$ENV_FILE" ]]; then
    echo "Error: .env file not found at $ENV_FILE"
    echo "Please create the .env file with your database configuration."
    exit 1
fi

echo "Loading environment variables from $ENV_FILE..."

# Source the .env file and export all variables
set -a  # Automatically export all variables
source "$ENV_FILE"
set +a  # Turn off auto-export

# Ensure PostgreSQL is available; attempt to start it if not
ensure_database() {
    local host="${DB_HOST:-localhost}"
    local port="${DB_PORT:-5432}"
    local name="${DB_NAME:-postgres}"
    local user="${DB_USER:-postgres}"
    local password="${DB_PASSWORD:-}"

    echo "Ensuring PostgreSQL is running (${user}@${host}:${port}/${name})..."

    if PGPASSWORD="$password" pg_isready -h "$host" -p "$port" -d "$name" -U "$user" >/dev/null 2>&1; then
        echo "PostgreSQL is already accepting connections."
        return 0
    fi

    echo "PostgreSQL not reachable; attempting automatic start..."

    local started="false"

    if command -v systemctl >/dev/null 2>&1; then
        if systemctl is-active --quiet postgresql; then
            started="true"
        elif systemctl start postgresql >/dev/null 2>&1; then
            started="true"
        fi

        if [[ "$started" = "false" ]] && systemctl --user status postgresql >/dev/null 2>&1; then
            if systemctl --user start postgresql >/dev/null 2>&1; then
                started="true"
            fi
        fi
    fi

    if [[ "$started" = "false" ]] && command -v service >/dev/null 2>&1; then
        if service postgresql start >/dev/null 2>&1; then
            started="true"
        fi
    fi

    if [[ "$started" = "false" ]] && command -v pg_lsclusters >/dev/null 2>&1 && command -v pg_ctlcluster >/dev/null 2>&1; then
        while read -r version cluster status owner port_ _; do
            if [[ "$cluster" = "main" ]]; then
                if pg_ctlcluster --skip-systemctl "$version" "$cluster" start >/dev/null 2>&1; then
                    started="true"
                    break
                fi
            fi
        done < <(pg_lsclusters 2>/dev/null)
    fi

    if [[ "$started" = "false" ]] && command -v pg_ctl >/dev/null 2>&1 && [[ -n "${PGDATA:-}" ]]; then
        mkdir -p "$PROJECT_ROOT/logs"
        if pg_ctl -D "$PGDATA" -l "$PROJECT_ROOT/logs/postgres.log" start >/dev/null 2>&1; then
            started="true"
        fi
    fi

    for attempt in {1..10}; do
        if PGPASSWORD="$password" pg_isready -h "$host" -p "$port" -d "$name" -U "$user" >/dev/null 2>&1; then
            echo "PostgreSQL is ready."
            return 0
        fi
        sleep 1
    done

    echo "Error: Unable to verify PostgreSQL is running after automatic attempts." >&2
    echo "Please start PostgreSQL manually and rerun this script." >&2
    exit 1
}

ensure_database

# Verify critical environment variables are set
REQUIRED_VARS=("DATABASE_URL" "DB_NAME" "DB_USER" "DB_PASSWORD" "DB_HOST" "DB_PORT")
MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if [[ -z "${!var}" ]]; then
        MISSING_VARS+=("$var")
    fi
done

if [[ ${#MISSING_VARS[@]} -gt 0 ]]; then
    echo "Error: Missing required environment variables:"
    printf '  %s\n' "${MISSING_VARS[@]}"
    echo "Please check your .env file."
    exit 1
fi

echo "Environment variables loaded successfully."
echo "Database: $DB_NAME at $DB_HOST:$DB_PORT"

# Change to backend directory
cd "$BACKEND_DIR"

# Check if virtual environment exists
if [[ ! -d "venv" ]]; then
    echo "Error: Virtual environment not found at $BACKEND_DIR/venv"
    echo "Please create and activate your virtual environment first."
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Verify uvicorn is available
if ! command -v uvicorn &> /dev/null; then
    echo "Error: uvicorn not found in virtual environment"
    echo "Please install uvicorn: pip install uvicorn"
    exit 1
fi

# Test database connection before starting server
echo "Testing database connection..."
python -c "
import os
from sqlalchemy import text
from app.database.connection import engine
try:
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
        print('✓ Database connection successful')
except Exception as e:
    print(f'✗ Database connection failed: {e}')
    exit(1)
"

if [[ $? -ne 0 ]]; then
    echo "Database connection test failed. Please check your configuration."
    exit 1
fi

# Start the server
echo "Starting uvicorn server..."
echo "API will be available at: http://100.106.201.33:8080"
echo "API docs will be available at: http://100.106.201.33:8080/docs"
echo ""
echo "Press Ctrl+C to stop the server"

# Use exec to replace the shell process with uvicorn
exec python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
