#!/bin/bash

# Overnight Test Runner for Lumen Backend
# Runs all 599 tests with comprehensive reporting while user sleeps

set -e

PROJECT_ROOT="/home/cdc/Storage/NVMe/projects/lumen"
BACKEND_DIR="$PROJECT_ROOT/backend"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_DIR="$PROJECT_ROOT/scripts/tests/reports"
EMAIL_REPORT="/tmp/lumen_test_summary_$TIMESTAMP.txt"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Lumen Overnight Test Suite - Started at $(date) ===${NC}"
echo "Project root: $PROJECT_ROOT"
echo "Report directory: $REPORT_DIR"
echo

# Function to cleanup on exit
cleanup() {
    echo -e "${YELLOW}Cleaning up processes...${NC}"
    if [[ -n "$FIREBASE_PID" ]]; then
        kill $FIREBASE_PID 2>/dev/null || true
    fi
    if [[ -n "$BACKEND_PID" ]]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    wait
    echo -e "${GREEN}Cleanup completed${NC}"
}
trap cleanup EXIT

# Create report directory
mkdir -p "$REPORT_DIR"

# Function to log with timestamp
log_with_timestamp() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$REPORT_DIR/execution.log"
}

log_with_timestamp "Starting overnight test execution"

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"
missing_deps=()

if ! command -v firebase &> /dev/null; then
    missing_deps+=("firebase-tools")
fi

if ! command -v python3 &> /dev/null; then
    missing_deps+=("python3")
fi

if ! command -v psql &> /dev/null; then
    missing_deps+=("postgresql-client")
fi

if [[ ${#missing_deps[@]} -ne 0 ]]; then
    echo -e "${RED}ERROR: Missing dependencies: ${missing_deps[*]}${NC}"
    exit 1
fi

# Check database exists
log_with_timestamp "Verifying PostgreSQL test database"
if ! psql -lqt | cut -d \| -f 1 | grep -qw lumen_test; then
    echo -e "${RED}ERROR: lumen_test database not found${NC}"
    echo "Create with: createdb lumen_test"
    echo "Then import schema: psql lumen_test < backend/schema_production.sql"
    exit 1
fi

# Navigate to project root
cd "$PROJECT_ROOT"

# Start Firebase emulator
log_with_timestamp "Starting Firebase emulator"
firebase emulators:start --only auth,storage --project lumen-photo-app-20250731 > "$REPORT_DIR/firebase_emulator.log" 2>&1 &
FIREBASE_PID=$!

# Wait for Firebase emulator
log_with_timestamp "Waiting for Firebase emulator to initialize"
for i in {1..30}; do
    if curl -s http://localhost:9099 > /dev/null 2>&1 && curl -s http://localhost:9199 > /dev/null 2>&1; then
        log_with_timestamp "Firebase emulator ready (auth:9099, storage:9199)"
        break
    fi
    sleep 2
    if [[ $i -eq 30 ]]; then
        echo -e "${RED}ERROR: Firebase emulator failed to start${NC}"
        exit 1
    fi
done

# Start backend server
cd "$BACKEND_DIR"
source venv/bin/activate

log_with_timestamp "Starting backend server"

# Set environment variables for testing
export TESTING=true
export FIREBASE_USE_EMULATOR=true
export DATABASE_URL="postgresql:///lumen_test"

python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 > "$REPORT_DIR/backend_server.log" 2>&1 &
BACKEND_PID=$!

# Wait for backend server
log_with_timestamp "Waiting for backend server to initialize"
for i in {1..20}; do
    if curl -s http://localhost:8080/health > /dev/null 2>&1; then
        log_with_timestamp "Backend server ready (localhost:8080)"
        break
    fi
    sleep 3
    if [[ $i -eq 20 ]]; then
        echo -e "${RED}ERROR: Backend server failed to start${NC}"
        exit 1
    fi
done

# Test execution phases
declare -a TEST_PHASES=(
    "unit:Unit Tests:../scripts/tests/ -k 'not integration and not playwright and not slow'"
    "integration:Integration Tests:../scripts/tests/ -k 'integration and not playwright'"
    "auth:Authentication Tests:../scripts/tests/test_auth_*.py"
    "photos:Photo Service Tests:../scripts/tests/test_photo_*.py"
    "database:Database Tests:../scripts/tests/test_*database*.py"
    "models:Model Tests:../scripts/tests/test_*model*.py"
    "endpoints:API Endpoint Tests:../scripts/tests/test_*endpoints*.py"
    "services:Service Tests:../scripts/tests/test_*service*.py"
)

# Initialize summary
total_tests=0
total_passed=0
total_failed=0
total_errors=0
total_skipped=0

# Create summary header
{
    echo "LUMEN OVERNIGHT TEST EXECUTION SUMMARY"
    echo "======================================"
    echo "Started: $(date)"
    echo "Test Environment: Local with Firebase Emulator"
    echo "Database: PostgreSQL (lumen_test)"
    echo "Total Test Files: $(find ../scripts/tests/ -name 'test_*.py' | wc -l)"
    echo
} > "$REPORT_DIR/summary.txt"

# Run test phases
for phase in "${TEST_PHASES[@]}"; do
    IFS=':' read -r phase_name phase_desc phase_pattern <<< "$phase"
    
    log_with_timestamp "Starting $phase_desc"
    echo -e "${BLUE}=== $phase_desc ===${NC}"
    
    # Run tests with detailed output
    pytest_start_time=$(date +%s)
    
    python -m pytest $phase_pattern \
        --tb=short \
        --maxfail=50 \
        --html="$REPORT_DIR/${phase_name}_report.html" \
        --self-contained-html \
        --junit-xml="$REPORT_DIR/${phase_name}_junit.xml" \
        -v \
        --durations=10 \
        > "$REPORT_DIR/${phase_name}_output.txt" 2>&1
    
    phase_exit_code=$?
    pytest_end_time=$(date +%s)
    phase_duration=$((pytest_end_time - pytest_start_time))
    
    # Parse results
    if [[ -f "$REPORT_DIR/${phase_name}_output.txt" ]]; then
        phase_summary=$(tail -10 "$REPORT_DIR/${phase_name}_output.txt" | grep -E "= .* in .*s =")
        
        # Extract numbers from pytest output
        phase_passed=$(echo "$phase_summary" | grep -o '[0-9]\+ passed' | cut -d' ' -f1 || echo "0")
        phase_failed=$(echo "$phase_summary" | grep -o '[0-9]\+ failed' | cut -d' ' -f1 || echo "0")
        phase_errors=$(echo "$phase_summary" | grep -o '[0-9]\+ error' | cut -d' ' -f1 || echo "0")
        phase_skipped=$(echo "$phase_summary" | grep -o '[0-9]\+ skipped' | cut -d' ' -f1 || echo "0")
        
        # Accumulate totals
        total_passed=$((total_passed + phase_passed))
        total_failed=$((total_failed + phase_failed))
        total_errors=$((total_errors + phase_errors))
        total_skipped=$((total_skipped + phase_skipped))
        
        phase_total=$((phase_passed + phase_failed + phase_errors + phase_skipped))
        total_tests=$((total_tests + phase_total))
    else
        phase_passed=0
        phase_failed=0
        phase_errors=0
        phase_skipped=0
    fi
    
    # Determine status
    if [[ $phase_exit_code -eq 0 ]]; then
        phase_status="${GREEN}PASSED${NC}"
    else
        phase_status="${RED}FAILED${NC}"
    fi
    
    # Log phase results
    log_with_timestamp "$phase_desc completed: $phase_passed passed, $phase_failed failed, $phase_errors errors, $phase_skipped skipped (${phase_duration}s)"
    echo -e "$phase_status - Duration: ${phase_duration}s"
    
    # Add to summary
    {
        echo "$phase_desc:"
        echo "  Status: $(if [[ $phase_exit_code -eq 0 ]]; then echo "PASSED"; else echo "FAILED"; fi)"
        echo "  Duration: ${phase_duration}s"
        echo "  Results: $phase_passed passed, $phase_failed failed, $phase_errors errors, $phase_skipped skipped"
        echo
    } >> "$REPORT_DIR/summary.txt"
    
    # Brief pause between phases
    sleep 2
done

# Final summary
end_time=$(date)
total_duration=$(($(date +%s) - $(date -d "$start_time" +%s 2>/dev/null || date +%s)))

{
    echo "FINAL RESULTS:"
    echo "============="
    echo "Total Tests: $total_tests"
    echo "Passed: $total_passed"
    echo "Failed: $total_failed"
    echo "Errors: $total_errors"
    echo "Skipped: $total_skipped"
    echo
    echo "Success Rate: $(if [[ $total_tests -gt 0 ]]; then echo "scale=1; $total_passed * 100 / $total_tests" | bc; else echo "0"; fi)%"
    echo "Completed: $end_time"
    echo "Total Duration: ${total_duration}s ($(($total_duration / 3600))h $(($total_duration % 3600 / 60))m)"
    echo
    echo "Reports available in: $REPORT_DIR"
} >> "$REPORT_DIR/summary.txt"

# Create email summary
cp "$REPORT_DIR/summary.txt" "$EMAIL_REPORT"

# Final console output
echo
echo -e "${GREEN}=== OVERNIGHT TEST EXECUTION COMPLETE ===${NC}"
echo -e "${BLUE}Results Summary:${NC}"
echo "  Total Tests: $total_tests"
echo "  Passed: $total_passed"
echo "  Failed: $total_failed"
echo "  Errors: $total_errors"
echo "  Skipped: $total_skipped"
echo
echo -e "${BLUE}Success Rate: $(if [[ $total_tests -gt 0 ]]; then echo "scale=1; $total_passed * 100 / $total_tests" | bc; else echo "0"; fi)%${NC}"
echo
echo -e "${BLUE}Detailed reports available in:${NC}"
echo "  $REPORT_DIR"
echo
echo -e "${BLUE}Key files:${NC}"
echo "  • summary.txt - Overall results"
echo "  • *_report.html - Detailed HTML reports for each phase"
echo "  • *_junit.xml - JUnit XML for CI/CD integration"
echo "  • execution.log - Full execution log"
echo

# Check if we should send notification
if command -v mail &> /dev/null; then
    mail -s "Lumen Overnight Test Results - $(if [[ $total_failed -eq 0 && $total_errors -eq 0 ]]; then echo 'SUCCESS'; else echo 'ISSUES FOUND'; fi)" "$(whoami)@localhost" < "$EMAIL_REPORT" 2>/dev/null || true
fi

# Exit with appropriate code
if [[ $total_failed -gt 0 || $total_errors -gt 0 ]]; then
    echo -e "${YELLOW}Some tests failed or had errors. Check detailed reports.${NC}"
    exit 1
else
    echo -e "${GREEN}All tests passed successfully!${NC}"
    exit 0
fi