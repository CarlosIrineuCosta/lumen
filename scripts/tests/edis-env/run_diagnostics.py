#!/usr/bin/env python3
"""
Comprehensive diagnostic test runner for Lumen platform

This script runs a complete set of diagnostic tests to identify why photos
aren't displaying despite successful authentication.

Usage:
    python tests/tools/run_diagnostics.py [--quick] [--live-only] [--db-only]
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def run_pytest_command(test_path, markers=None, extra_args=None):
    """Run a pytest command with proper error handling"""
    cmd = ["python", "-m", "pytest", test_path, "-v", "-s"]
    
    if markers:
        cmd.extend(["-m", markers])
    
    if extra_args:
        cmd.extend(extra_args)
    
    print(f"Running: {' '.join(cmd)}")
    print("-" * 40)
    
    try:
        result = subprocess.run(cmd, cwd=backend_path, capture_output=False)
        return result.returncode == 0
    except Exception as e:
        print(f"Failed to run command: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Run Lumen diagnostic tests")
    parser.add_argument("--quick", action="store_true", 
                       help="Run only quick diagnostic tests")
    parser.add_argument("--live-only", action="store_true",
                       help="Run only live system tests")
    parser.add_argument("--db-only", action="store_true", 
                       help="Run only database diagnostic tests")
    parser.add_argument("--no-external", action="store_true",
                       help="Skip tests requiring external services")
    
    args = parser.parse_args()
    
    print_header("LUMEN PLATFORM DIAGNOSTIC TEST SUITE")
    print("This suite diagnoses photo display issues and system health")
    print(f"Running from: {backend_path}")
    
    success_count = 0
    total_tests = 0
    
    # Ensure we're in the right directory
    os.chdir(backend_path)
    
    if args.db_only or not args.live_only:
        print_header("1. DATABASE AUTHENTICATION DIAGNOSTICS")
        print("Checking database connectivity and authentication...")
        
        test_path = "tests/diagnostics/test_database_auth.py"
        markers = "diagnostics and database"
        
        if args.no_external:
            markers += " and not external"
        
        if run_pytest_command(test_path, markers):
            success_count += 1
        total_tests += 1
    
    if not args.db_only and not args.live_only:
        print_header("2. PHOTO PIPELINE DIAGNOSTICS") 
        print("Testing end-to-end photo display pipeline...")
        
        test_path = "tests/diagnostics/test_photo_pipeline.py"
        markers = "diagnostics and photos"
        
        if args.no_external:
            markers += " and not external"
        
        if run_pytest_command(test_path, markers):
            success_count += 1
        total_tests += 1
    
    if args.live_only or not args.quick:
        print_header("3. LIVE SYSTEM HEALTH DIAGNOSTICS")
        print("Testing live system accessibility and performance...")
        
        test_path = "tests/diagnostics/test_live_system.py"
        markers = "diagnostics and live"
        
        if run_pytest_command(test_path, markers):
            success_count += 1
        total_tests += 1
    
    if not args.quick and not args.db_only and not args.live_only:
        print_header("4. ID VALIDATION INTEGRATION TESTS")
        print("Testing comprehensive ID validation system...")
        
        test_path = "tests/integration/test_id_validation_integration.py"
        markers = "integration and id_validation"
        
        if run_pytest_command(test_path, markers):
            success_count += 1
        total_tests += 1
    
    # Summary
    print_header("DIAGNOSTIC TEST SUMMARY")
    print(f"Tests completed: {success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("✅ All diagnostic tests passed!")
        print("If photos still aren't displaying, check the test output above for warnings.")
    else:
        print(f"❌ {total_tests - success_count} test suite(s) failed")
        print("The failing tests indicate the source of the photo display issue.")
    
    print("\nNext steps:")
    print("1. Review test output above for specific error messages")
    print("2. Focus on the first failing test - usually the root cause")
    print("3. For database issues: Check GCP authentication and Cloud SQL permissions")
    print("4. For photo pipeline issues: Verify GCS bucket access and signed URL generation")
    
    return success_count == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)