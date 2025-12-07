#!/usr/bin/env bash
# Restart helper for Lumen backend (FastAPI) and frontend (dev server).
# Stops any existing processes on the standard ports, then relaunches each service.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd)"
BACKEND_SCRIPT="$ROOT_DIR/scripts/start-server.sh"
FRONTEND_DIR="$ROOT_DIR/frontend"
LOG_DIR="$ROOT_DIR/logs"
BACKEND_LOG="$LOG_DIR/backend.restart.log"
FRONTEND_LOG="$LOG_DIR/frontend.restart.log"
BACKEND_PID_FILE="$LOG_DIR/backend.restart.pid"
FRONTEND_PID_FILE="$LOG_DIR/frontend.restart.pid"

PYTHON_BIN=""
if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v python)"
else
    echo "Python interpreter not found on PATH" >&2
    exit 1
fi

mkdir -p "$LOG_DIR"

# CLI options
FORCE_KILL=false

usage() {
    cat <<EOF
Usage: \
  ${BASH_SOURCE[0]} [--force]

Options:
  --force    Also terminate any other process bound to the service ports if
             tagged Lumen processes are not found.
  -h, --help Show this help text.
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --force)
            FORCE_KILL=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            usage >&2
            exit 1
            ;;
    esac
done

# Read database settings from backend/.env (fall back to sensible defaults)
DB_ENV_FILE="$ROOT_DIR/backend/.env"
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="lumen_development"
DB_USER="lumen_dev"
DB_PASSWORD=""

if [[ -f "$DB_ENV_FILE" ]]; then
    while IFS='=' read -r key value; do
        case "$key" in
            DB_HOST) DB_HOST=${value:-$DB_HOST} ;;
            DB_PORT) DB_PORT=${value:-$DB_PORT} ;;
            DB_NAME) DB_NAME=${value:-$DB_NAME} ;;
            DB_USER) DB_USER=${value:-$DB_USER} ;;
            DB_PASSWORD) DB_PASSWORD=${value:-$DB_PASSWORD} ;;
        esac
    done < <(grep -E '^(DB_HOST|DB_PORT|DB_NAME|DB_USER|DB_PASSWORD)=' "$DB_ENV_FILE")
fi

port_in_use() {
    local port="$1"
    if command -v lsof >/dev/null 2>&1; then
        lsof -ti tcp:"$port" >/dev/null 2>&1
        return $?
    fi

    if command -v fuser >/dev/null 2>&1; then
        fuser "${port}/tcp" >/dev/null 2>&1
        return $?
    fi

    # Fallback: attempt to open the port; success means someone is listening.
    if (exec 3<>/dev/tcp/127.0.0.1/$port) 2>/dev/null; then
        exec 3<&-
        exec 3>&-
        return 0
    fi

    return 1
}

stop_port() {
    local port="$1"
    if command -v lsof >/dev/null 2>&1; then
        local pids
        pids="$(lsof -ti tcp:"$port" 2>/dev/null || true)"
        if [[ -n "$pids" ]]; then
            echo "Force stopping processes on port $port: $pids"
            kill $pids 2>/dev/null || true
            sleep 1
        fi
    else
        echo "lsof not found; attempting fuser on port $port"
        fuser -k "${port}/tcp" 2>/dev/null || true
        sleep 1
    fi
}

identify_port_pids() {
    local port="$1"
    local pids=""

    if command -v lsof >/dev/null 2>&1; then
        pids="$(lsof -ti tcp:"$port" 2>/dev/null || true)"
    elif command -v fuser >/dev/null 2>&1; then
        pids="$(fuser -n tcp "$port" 2>/dev/null | tr ' ' '\n' | grep -E '^[0-9]+$' || true)"
    fi

    echo "$pids"
}

stop_service() {
    local service="$1"
    local pid_file="$2"
    local tag="$3"

    if [[ ! -f "$pid_file" ]]; then
        echo "No recorded PID file for $service ($pid_file)"
        return 1
    fi

    local recorded_pid=""
    local recorded_pgid=""
    read -r recorded_pid recorded_pgid < "$pid_file" || true

    if [[ -z "$recorded_pid" ]]; then
        echo "PID file $pid_file is empty; removing"
        rm -f "$pid_file"
        return 1
    fi

    if ! kill -0 "$recorded_pid" 2>/dev/null; then
        echo "$service (PID $recorded_pid) not running; cleaning up stale PID file"
        rm -f "$pid_file"
        return 1
    fi

    local environ_file="/proc/$recorded_pid/environ"
    local tagged=false
    if [[ -r "$environ_file" ]]; then
        if tr '\0' '\n' < "$environ_file" | grep -qx "LUMEN_SERVICE=$tag"; then
            tagged=true
        fi
    fi

    if [[ "$tagged" != true ]]; then
        if ! is_lumen_process "$recorded_pid" "$service"; then
            echo "PID $recorded_pid is running but does not appear to be tagged as $service; skipping"
            return 2
        fi
    fi

    local target_pgid="$recorded_pgid"
    if [[ -z "$target_pgid" ]]; then
        target_pgid="$(ps -o pgid= -p "$recorded_pid" 2>/dev/null | tr -d ' ')"
    fi

    echo "Stopping $service (PID $recorded_pid${target_pgid:+, PGID $target_pgid})"
    if [[ -n "$target_pgid" ]]; then
        kill -- -"$target_pgid" 2>/dev/null || true
    fi
    kill "$recorded_pid" 2>/dev/null || true
    sleep 1

    if kill -0 "$recorded_pid" 2>/dev/null; then
        echo "Failed to stop $service (PID $recorded_pid)"
        return 3
    fi

    rm -f "$pid_file"
    return 0
}

is_lumen_process() {
    local pid="$1"
    local label="$2"

    if ! kill -0 "$pid" 2>/dev/null; then
        return 1
    fi

    local environ_file="/proc/$pid/environ"
    if [[ -r "$environ_file" ]]; then
        if tr '\0' '\n' < "$environ_file" | grep -q '^LUMEN_SERVICE='; then
            return 0
        fi
    fi

    local cmdline_file="/proc/$pid/cmdline"
    if [[ -r "$cmdline_file" ]]; then
        local cmdline
        cmdline="$(tr '\0' ' ' < "$cmdline_file")"
        if [[ "$cmdline" == *"$BACKEND_SCRIPT"* ]]; then
            return 0
        fi
        if [[ "$cmdline" == *"$FRONTEND_DIR/serve.py"* ]]; then
            return 0
        fi
        if [[ "$cmdline" == *"$ROOT_DIR"* ]]; then
            return 0
        fi
    fi

    if [[ -n "$label" ]]; then
        local command
        command="$(ps -o command= -p "$pid" 2>/dev/null || true)"
        if [[ "$command" == *"$ROOT_DIR"* ]]; then
            return 0
        fi
    fi

    return 1
}

reclaim_port() {
    local port="$1"
    local label="$2"

    local pids
    pids="$(identify_port_pids "$port")"

    if [[ -z "$pids" ]]; then
        if port_in_use "$port"; then
            if [[ "$FORCE_KILL" == true ]]; then
                stop_port "$port"
                return
            fi
            echo "Port $port is still in use by an unknown process. Re-run with --force to reclaim it." >&2
            exit 1
        fi
        return
    fi

    local killed_any=false
    local -a unknown_pids=()

    for pid in $pids; do
        if is_lumen_process "$pid" "$label"; then
            local pgid
            pgid="$(ps -o pgid= -p "$pid" 2>/dev/null | tr -d ' ')"
            if [[ -n "$pgid" ]]; then
                echo "Stopping $label process group (PID $pid, PGID $pgid) holding port $port"
                kill -- -"$pgid" 2>/dev/null || true
            fi
            kill "$pid" 2>/dev/null || true
            killed_any=true
        else
            unknown_pids+=("$pid")
        fi
    done

    if [[ "$killed_any" == true ]]; then
        sleep 1
    fi

    if port_in_use "$port"; then
        if [[ ${#unknown_pids[@]} -gt 0 ]]; then
            if [[ "$FORCE_KILL" == true ]]; then
                echo "Force killing non-Lumen processes on port $port: ${unknown_pids[*]}"
                stop_port "$port"
                return
            fi
            echo "Port $port is held by non-Lumen processes (${unknown_pids[*]}). Re-run with --force to terminate them." >&2
            exit 1
        fi

        if [[ "$FORCE_KILL" == true ]]; then
            stop_port "$port"
        else
            echo "Port $port remains busy after stopping known Lumen processes. Re-run with --force if you are sure it is safe." >&2
            exit 1
        fi
    fi
}

start_backend() {
    if [[ ! -x "$BACKEND_SCRIPT" ]]; then
        echo "Backend script not executable: $BACKEND_SCRIPT" >&2
        exit 1
    fi

    echo "Starting backend via $BACKEND_SCRIPT (logs -> $BACKEND_LOG)"
    pushd "$ROOT_DIR" >/dev/null
    nohup env LUMEN_SERVICE=backend "$BACKEND_SCRIPT" >>"$BACKEND_LOG" 2>&1 &
    BACKEND_PID=$!
    BACKEND_PGID="$(ps -o pgid= -p "$BACKEND_PID" 2>/dev/null | tr -d ' ')"
    popd >/dev/null
    printf '%s %s\n' "$BACKEND_PID" "$BACKEND_PGID" > "$BACKEND_PID_FILE"
    echo "Backend PID: $BACKEND_PID"
}

start_frontend() {
    if [[ ! -f "$FRONTEND_DIR/serve.py" ]]; then
        echo "Frontend serve.py not found"
        exit 1
    fi

    echo "Starting frontend via $PYTHON_BIN frontend/serve.py (logs -> $FRONTEND_LOG)"
    pushd "$FRONTEND_DIR" >/dev/null
    nohup env LUMEN_SERVICE=frontend "$PYTHON_BIN" serve.py >>"$FRONTEND_LOG" 2>&1 &
    FRONTEND_PID=$!
    FRONTEND_PGID="$(ps -o pgid= -p "$FRONTEND_PID" 2>/dev/null | tr -d ' ')"
    popd >/dev/null
    printf '%s %s\n' "$FRONTEND_PID" "$FRONTEND_PGID" > "$FRONTEND_PID_FILE"
    echo "Frontend PID: $FRONTEND_PID"
}

wait_for_port() {
    local port="$1"
    local service="$2"
    local attempts=15

    for attempt in $(seq 1 "$attempts"); do
        if (exec 3<>/dev/tcp/127.0.0.1/$port) 2>/dev/null; then
            exec 3<&-
            exec 3>&-
            echo "$service is listening on port $port (check ${attempt}s)."
            return 0
        fi
        sleep 1
    done

    echo "Warning: $service did not confirm listening on port $port after ${attempts}s" >&2
    return 1
}

ensure_database() {
    echo "Checking PostgreSQL availability (${DB_USER}@${DB_HOST}:${DB_PORT}/${DB_NAME})..."

    if PGPASSWORD="$DB_PASSWORD" pg_isready -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -U "$DB_USER" >/dev/null 2>&1; then
        echo "Database is ready."
        return 0
    fi

    echo "Database not reachable; attempting to start PostgreSQL service..."

    if command -v systemctl >/dev/null 2>&1; then
        systemctl start postgresql >/dev/null 2>&1 || true
        systemctl --user start postgresql >/dev/null 2>&1 || true
    fi

    if command -v service >/dev/null 2>&1; then
        service postgresql start >/dev/null 2>&1 || true
    fi

    if command -v pg_ctlcluster >/dev/null 2>&1; then
        pg_ctlcluster --skip-systemctl 16 main start >/dev/null 2>&1 || true
        pg_ctlcluster --skip-systemctl 15 main start >/dev/null 2>&1 || true
    fi

    if PGPASSWORD="$DB_PASSWORD" pg_isready -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -U "$DB_USER" >/dev/null 2>&1; then
        echo "Database is ready."
        return 0
    fi

    echo "Unable to verify PostgreSQL is running. Please start it manually (e.g., systemctl start postgresql) and rerun this script." >&2
    exit 1
}

main() {
    echo "=== Lumen restart utility ==="

    echo "Stopping existing services (ports 8080 & 8000)..."
    stop_service "backend" "$BACKEND_PID_FILE" "backend" || true
    stop_service "frontend" "$FRONTEND_PID_FILE" "frontend" || true

    if port_in_use 8080; then
        echo "Port 8080 still in use after checking backend PID file."
        reclaim_port 8080 "backend"
    fi

    if port_in_use 8000; then
        echo "Port 8000 still in use after checking frontend PID file."
        reclaim_port 8000 "frontend"
    fi

    ensure_database

    echo "Launching backend..."
    start_backend
    sleep 2

    echo "Launching frontend..."
    start_frontend

    echo "\nConfirming services..."
    wait_for_port 8080 "Backend"
    wait_for_port 8000 "Frontend"

    cat <<MSG

Backend log:   $BACKEND_LOG
Backend PID:   \\$(cat "$BACKEND_PID_FILE" 2>/dev/null || echo "unknown")
Frontend log:  $FRONTEND_LOG
Frontend PID:  \\$(cat "$FRONTEND_PID_FILE" 2>/dev/null || echo "unknown")

Backend URL:   http://localhost:8080
Frontend URL:  http://localhost:8000

Use 'tail -f <log>' to monitor output. Press Ctrl+C in a terminal running each service to stop them manually.
MSG
}

main "$@"
