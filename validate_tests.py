#!/usr/bin/env python3
"""
Quick test validation script.

Runs a subset of tests to validate the test setup is working correctly.
"""

import subprocess
import sys
import os
from pathlib import Path


def main():
    """Run quick validation tests."""
    print("🔍 Quick Test Validation")
    print("="*40)
    
    # Change to project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print("Testing pytest configuration...")
    
    # Test basic pytest functionality
    result = subprocess.run([
        "python", "-m", "pytest", "--version"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("❌ pytest not working correctly")
        print(result.stderr)
        return 1
    
    print(f"✅ {result.stdout.strip()}")
    
    # Test coverage functionality
    result = subprocess.run([
        "python", "-c", "import pytest_cov; print('pytest-cov available')"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("⚠️  pytest-cov not installed - coverage reporting will be disabled")
        print("   To install: pip install pytest-cov")
        coverage_available = False
    else:
        print("✅ Coverage plugin available")
        coverage_available = True
    
    # Run a simple test
    print("\nRunning basic test validation...")
    
    result = subprocess.run([
        "python", "-m", "pytest", 
        "tests/unit/core/test_exceptions.py::TestCustomExceptions::test_horse_breed_not_found_error",
        "-v"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Basic test execution working")
    else:
        print("❌ Basic test execution failed")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        return 1
    
    print("\n🎉 Test setup validation completed successfully!")
    print("\nYou can now run the full test suite with:")
    print("  python run_tests.py")
    print("\nOr individual test categories:")
    print("  python -m pytest tests/unit/ -v")
    print("  python -m pytest tests/integration/ -v -m integration")
    print("  python -m pytest tests/ --cov=app --cov-report=html")
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)