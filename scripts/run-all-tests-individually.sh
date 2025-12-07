#!/bin/bash

# Run all test files individually to avoid collection issues
# Execute from project root: ./scripts/run-all-tests-individually.sh

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_DIR="$PROJECT_ROOT/scripts/tests/reports"

# Colors
RED='\033[0;31m'        # Keep red for actual errors only
GREEN='\033[0;32m'      # Bright green for success
DIM_GREEN='\033[2;32m'  # Dim green for test status
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Running All Test Files Individually ===${NC}"
echo "Started: $(date)"
echo "Project root: $PROJECT_ROOT"
echo "Report directory: $REPORT_DIR"
echo

# Create report directory
mkdir -p "$REPORT_DIR"

# Navigate to backend and activate venv
cd "$BACKEND_DIR"
source venv/bin/activate

# Set environment variables - Use same database as main app
export TESTING=true
export FIREBASE_USE_EMULATOR=true
# DATABASE_URL will be read from .env file (single database approach)

# Find all test files
TEST_FILES=($(find ../scripts/tests/ -name "test_*.py" -type f | sort))
TOTAL_FILES=${#TEST_FILES[@]}

echo -e "${BLUE}Found $TOTAL_FILES test files to process${NC}"
echo

# Counters
processed=0
passed_files=0
failed_files=0
total_tests=0
total_passed=0
total_failed=0

# Process each file
for test_file in "${TEST_FILES[@]}"; do
    processed=$((processed + 1))
    filename=$(basename "$test_file")
    
    echo -e "${BLUE}[$processed/$TOTAL_FILES] Running $test_file${NC}"
    
    # Run the test file
    if python -m pytest "$test_file" -v --tb=short --junit-xml="$REPORT_DIR/${filename%.py}_junit.xml" > "$REPORT_DIR/${filename%.py}_output.txt" 2>&1; then
        echo -e "${GREEN}  ✓ PASSED${NC}"
        passed_files=$((passed_files + 1))
    else
        echo -e "${DIM_GREEN}  ✗ FAILED${NC}"
        failed_files=$((failed_files + 1))
    fi
    
    # Extract test counts from output
    if [[ -f "$REPORT_DIR/${filename%.py}_output.txt" ]]; then
        file_summary=$(tail -5 "$REPORT_DIR/${filename%.py}_output.txt" | grep -E "= .* in .*s =")
        file_passed=$(echo "$file_summary" | grep -o '[0-9]\+ passed' | cut -d' ' -f1 || echo "0")
        file_failed=$(echo "$file_summary" | grep -o '[0-9]\+ failed' | cut -d' ' -f1 || echo "0")
        
        total_passed=$((total_passed + file_passed))
        total_failed=$((total_failed + file_failed))
        total_tests=$((total_tests + file_passed + file_failed))
        
        echo "    Tests: $file_passed passed, $file_failed failed"
    fi
    
    echo
done

# Final summary
echo -e "${GREEN}=== EXECUTION COMPLETE ===${NC}"
echo "Completed: $(date)"
echo
echo "File Summary:"
echo "  Total Files: $TOTAL_FILES"
echo "  Passed Files: $passed_files"
echo "  Failed Files: $failed_files"
echo
echo "Test Summary:"
echo "  Total Tests: $total_tests"
echo "  Passed Tests: $total_passed"
echo "  Failed Tests: $total_failed"
echo "  Success Rate: $(if [[ $total_tests -gt 0 ]]; then echo "scale=1; $total_passed * 100 / $total_tests" | bc; else echo "0"; fi)%"
echo
echo "Detailed reports in: $REPORT_DIR"
echo

# Exit with appropriate code
if [[ $failed_files -gt 0 ]]; then
    echo -e "${YELLOW}Some test files had failures. Check detailed reports.${NC}"
    exit 1
else
    echo -e "${GREEN}All test files completed successfully!${NC}"
    exit 0
fi