#!/usr/bin/env python3
"""
Test runner script for Lumen backend tests.

This script provides comprehensive test execution with different
test suites, coverage reporting, and result formatting.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd
        )
        return result
    except Exception as e:
        print(f"Error running command: {e}")
        return None


def install_test_requirements():
    """Install test requirements"""
    print("Installing test requirements...")
    backend_dir = Path(__file__).parent.parent
    requirements_file = Path(__file__).parent / "requirements.txt"

    cmd = f"pip install -r {requirements_file}"
    result = run_command(cmd, cwd=backend_dir)

    if result and result.returncode == 0:
        print("✓ Test requirements installed successfully")
    else:
        print("✗ Failed to install test requirements")
        if result:
            print(result.stderr)
        return False

    return True


def run_unit_tests(verbose=False, coverage=False):
    """Run unit tests"""
    print("\n" + "="*50)
    print("RUNNING UNIT TESTS")
    print("="*50)

    backend_dir = Path(__file__).parent.parent
    test_dir = Path(__file__).parent

    cmd = ["python", "-m", "pytest"]

    # Add test files
    test_files = [
        "test_connection_pool.py",
        "test_cors_configuration.py",
        "test_location_service_security.py",
        "test_cache_invalidation.py"
    ]

    for test_file in test_files:
        test_path = test_dir / test_file
        if test_path.exists():
            cmd.append(str(test_path))

    # Add options
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")

    if coverage:
        cmd.extend([
            "--cov=app",
            "--cov-report=html",
            "--cov-report=term-missing",
            "--cov-fail-under=80"
        ])

    cmd.extend([
        "--tb=short",
        "--color=yes",
        "-x"  # Stop on first failure
    ])

    result = run_command(" ".join(cmd), cwd=backend_dir)

    if result and result.returncode == 0:
        print("\n✓ All unit tests passed!")
        if coverage:
            print("📊 Coverage report generated in htmlcov/")
    else:
        print("\n✗ Some unit tests failed!")
        if result:
            print(result.stdout)
            print(result.stderr)

    return result and result.returncode == 0


def run_integration_tests(verbose=False):
    """Run integration tests"""
    print("\n" + "="*50)
    print("RUNNING INTEGRATION TESTS")
    print("="*50)

    backend_dir = Path(__file__).parent.parent

    cmd = [
        "python", "-m", "pytest",
        "-m", "integration",
        "-v" if verbose else "-q",
        "--tb=short",
        "--color=yes"
    ]

    result = run_command(" ".join(cmd), cwd=backend_dir)

    if result and result.returncode == 0:
        print("\n✓ All integration tests passed!")
    else:
        print("\n✗ Some integration tests failed!")
        if result:
            print(result.stdout)
            print(result.stderr)

    return result and result.returncode == 0


def run_security_tests():
    """Run security tests"""
    print("\n" + "="*50)
    print("RUNNING SECURITY TESTS")
    print("="*50)

    backend_dir = Path(__file__).parent.parent

    # Run bandit security analysis
    print("Running bandit security analysis...")
    bandit_cmd = "bandit -r app/ -f json -o bandit-report.json"
    result = run_command(bandit_cmd, cwd=backend_dir)

    if result and result.returncode == 0:
        print("✓ Bandit security analysis completed")
    else:
        print("⚠ Bandit found some security issues or failed to run")

    # Run safety check for dependencies
    print("Running safety dependency check...")
    safety_cmd = "safety check --json --output safety-report.json"
    result = run_command(safety_cmd, cwd=backend_dir)

    if result and result.returncode == 0:
        print("✓ Safety dependency check completed")
    else:
        print("⚠ Safety found some vulnerable dependencies")

    return True


def run_code_quality_tests():
    """Run code quality tests"""
    print("\n" + "="*50)
    print("RUNNING CODE QUALITY TESTS")
    print("="*50)

    backend_dir = Path(__file__).parent.parent

    tests_passed = True

    # Run flake8 linting
    print("Running flake8 linting...")
    flake8_cmd = "flake8 app/ --max-line-length=88 --extend-ignore=E203,W503"
    result = run_command(flake8_cmd, cwd=backend_dir)

    if result and result.returncode == 0:
        print("✓ Flake8 linting passed")
    else:
        print("✗ Flake8 found some linting issues")
        tests_passed = False

    # Run black formatting check
    print("Running black formatting check...")
    black_cmd = "black --check app/"
    result = run_command(black_cmd, cwd=backend_dir)

    if result and result.returncode == 0:
        print("✓ Black formatting check passed")
    else:
        print("✗ Black formatting check failed - run 'black app/' to fix")
        tests_passed = False

    # Run isort import sorting check
    print("Running isort import sorting check...")
    isort_cmd = "isort --check-only app/"
    result = run_command(isort_cmd, cwd=backend_dir)

    if result and result.returncode == 0:
        print("✓ Isort import sorting check passed")
    else:
        print("✗ Isort import sorting check failed - run 'isort app/' to fix")
        tests_passed = False

    return tests_passed


def generate_test_report():
    """Generate comprehensive test report"""
    print("\n" + "="*50)
    print("GENERATING TEST REPORT")
    print("="*50)

    backend_dir = Path(__file__).parent.parent

    # Generate HTML test report
    cmd = [
        "python", "-m", "pytest",
        "--html=test-report.html",
        "--self-contained-html",
        "-q"
    ]

    result = run_command(" ".join(cmd), cwd=backend_dir)

    if result and result.returncode == 0:
        print("✓ Test report generated: test-report.html")
    else:
        print("✗ Failed to generate test report")

    return result and result.returncode == 0


def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description="Lumen backend test runner")
    parser.add_argument(
        "--install",
        action="store_true",
        help="Install test requirements"
    )
    parser.add_argument(
        "--unit",
        action="store_true",
        help="Run unit tests only"
    )
    parser.add_argument(
        "--integration",
        action="store_true",
        help="Run integration tests only"
    )
    parser.add_argument(
        "--security",
        action="store_true",
        help="Run security tests only"
    )
    parser.add_argument(
        "--quality",
        action="store_true",
        help="Run code quality tests only"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage report"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all tests and checks"
    )

    args = parser.parse_args()

    # Change to backend directory
    backend_dir = Path(__file__).parent.parent
    os.chdir(backend_dir)

    # Install requirements if requested
    if args.install or args.all:
        if not install_test_requirements():
            sys.exit(1)

    all_passed = True

    # Run tests based on arguments
    if args.all or not any([args.unit, args.integration, args.security, args.quality]):
        # Run all tests
        if not run_unit_tests(args.verbose, args.coverage):
            all_passed = False

        if not run_integration_tests(args.verbose):
            all_passed = False

        if not run_security_tests():
            all_passed = False

        if not run_code_quality_tests():
            all_passed = False

        generate_test_report()
    else:
        # Run specific test suites
        if args.unit:
            if not run_unit_tests(args.verbose, args.coverage):
                all_passed = False

        if args.integration:
            if not run_integration_tests(args.verbose):
                all_passed = False

        if args.security:
            if not run_security_tests():
                all_passed = False

        if args.quality:
            if not run_code_quality_tests():
                all_passed = False

    # Print final results
    print("\n" + "="*50)
    print("TEST RUN SUMMARY")
    print("="*50)

    if all_passed:
        print("🎉 All tests and checks passed!")
        sys.exit(0)
    else:
        print("❌ Some tests or checks failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()