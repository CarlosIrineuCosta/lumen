#!/bin/bash

# Lumen Backend Test Runner
# Convenient script for running different test configurations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Ensure we're in the backend directory
cd "$(dirname "$0")"

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source venv/bin/activate
fi

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to run tests with proper error handling
run_tests() {
    local cmd="$1"
    local description="$2"
    
    print_status "Running $description..."
    
    if eval "$cmd"; then
        print_success "$description completed successfully"
        return 0
    else
        print_error "$description failed"
        return 1
    fi
}

# Parse command line arguments
case "${1:-all}" in
    "unit"|"u")
        print_status "Running unit tests (fast)"
        run_tests "pytest tests/ -m unit -v" "unit tests"
        ;;
    
    "integration"|"i")
        print_status "Running integration tests"
        run_tests "pytest tests/ -m integration -v" "integration tests"
        ;;
    
    "auth"|"a")
        print_status "Running authentication tests"
        run_tests "pytest tests/ -m auth -v" "authentication tests"
        ;;
    
    "photos"|"p")
        print_status "Running photo management tests"
        run_tests "pytest tests/ -m photos -v" "photo tests"
        ;;
    
    "coverage"|"cov"|"c")
        print_status "Running all tests with coverage report"
        run_tests "pytest tests/ --cov=app --cov-report=term-missing --cov-report=html" "tests with coverage"
        print_status "HTML coverage report generated in htmlcov/"
        ;;
    
    "quick"|"q")
        print_status "Running quick test suite (unit tests only)"
        run_tests "pytest tests/ -m unit --tb=short" "quick tests"
        ;;
    
    "parallel"|"par")
        print_status "Running tests in parallel"
        run_tests "pytest tests/ -n auto" "parallel tests"
        ;;
    
    "watch"|"w")
        print_status "Running tests in watch mode (requires pytest-watch)"
        if command -v ptw &> /dev/null; then
            ptw -- -m unit
        else
            print_error "pytest-watch not installed. Install with: pip install pytest-watch"
            exit 1
        fi
        ;;
    
    "debug"|"d")
        if [ -z "$2" ]; then
            print_error "Debug mode requires test path: ./run_tests.sh debug tests/unit/test_user_model.py"
            exit 1
        fi
        print_status "Running test in debug mode: $2"
        run_tests "pytest -vvv -s --tb=long $2" "debug test"
        ;;
    
    "install"|"setup")
        print_status "Installing test dependencies"
        pip install -r requirements.txt
        print_success "Test dependencies installed"
        ;;
    
    "clean")
        print_status "Cleaning test artifacts"
        rm -rf .pytest_cache/ htmlcov/ .coverage __pycache__/
        find . -name "*.pyc" -delete
        find . -name "__pycache__" -type d -exec rm -rf {} +
        print_success "Test artifacts cleaned"
        ;;
    
    "all"|"")
        print_status "Running complete test suite"
        
        # Run unit tests first (fast feedback)
        if run_tests "pytest tests/ -m unit" "unit tests"; then
            print_success "Unit tests passed"
        else
            print_error "Unit tests failed - skipping integration tests"
            exit 1
        fi
        
        # Run integration tests
        if run_tests "pytest tests/ -m integration" "integration tests"; then
            print_success "Integration tests passed"
        else
            print_error "Integration tests failed"
            exit 1
        fi
        
        # Generate coverage report
        print_status "Generating coverage report..."
        pytest tests/ --cov=app --cov-report=term-missing --cov-fail-under=70
        
        print_success "All tests completed successfully!"
        ;;
    
    "help"|"h"|"-h"|"--help")
        echo "Lumen Backend Test Runner"
        echo ""
        echo "Usage: ./run_tests.sh [COMMAND] [OPTIONS]"
        echo ""
        echo "Commands:"
        echo "  all, (default)     Run complete test suite"
        echo "  unit, u           Run unit tests only (fast)"
        echo "  integration, i    Run integration tests"
        echo "  auth, a          Run authentication tests"
        echo "  photos, p        Run photo management tests"
        echo "  coverage, cov, c Run tests with coverage report"
        echo "  quick, q         Run quick test suite (unit tests, short output)"
        echo "  parallel, par    Run tests in parallel"
        echo "  watch, w         Run tests in watch mode (requires pytest-watch)"
        echo "  debug, d <path>  Run specific test in debug mode"
        echo "  install, setup   Install test dependencies"
        echo "  clean           Clean test artifacts"
        echo "  help, h         Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./run_tests.sh                    # Run all tests"
        echo "  ./run_tests.sh unit               # Run unit tests only"
        echo "  ./run_tests.sh coverage           # Run with coverage"
        echo "  ./run_tests.sh debug tests/unit/test_user_model.py"
        echo "  ./run_tests.sh parallel           # Run tests in parallel"
        echo ""
        exit 0
        ;;
    
    *)
        print_error "Unknown command: $1"
        echo "Use './run_tests.sh help' for available commands"
        exit 1
        ;;
esac

# Print summary
if [ $? -eq 0 ]; then
    print_success "Test run completed successfully"
    exit 0
else
    print_error "Test run failed"
    exit 1
fi