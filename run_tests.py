#!/usr/bin/env python3
"""
Comprehensive test runner for the horse breed service.

This script runs all tests with proper coverage reporting,
performance monitoring, and detailed output formatting.
"""

import sys
import os
import subprocess
import time
from pathlib import Path


def run_command(command, description):
    """Run a command and handle output."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print('='*60)
    
    start_time = time.time()
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    end_time = time.time()
    
    print(f"Duration: {end_time - start_time:.2f} seconds")
    
    if result.stdout:
        print("STDOUT:")
        print(result.stdout)
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    if result.returncode != 0:
        print(f"❌ FAILED: {description}")
        return False
    else:
        print(f"✅ PASSED: {description}")
        return True
    
    return result.returncode == 0


def main():
    """Main test runner function."""
    print("🐎 Horse Breed Service - Comprehensive Test Suite")
    print("="*60)
    
    # Change to project root directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Ensure we're in a virtual environment
    if not os.environ.get('VIRTUAL_ENV') and not sys.prefix != sys.base_prefix:
        print("⚠️  Warning: Not running in virtual environment")
        print("   Consider activating your virtual environment first:")
        print("   .\\horse-breed-service-env\\Scripts\\activate")
    
    # Test commands to run
    test_commands = [
        {
            "command": "python -m pytest tests/unit/core/test_exceptions.py -v --tb=short",
            "description": "Unit Tests - Custom Exceptions"
        },
        {
            "command": "python -m pytest tests/unit/core/test_error_handlers.py -v --tb=short",
            "description": "Unit Tests - Error Handlers"
        },
        {
            "command": "python -m pytest tests/unit/core/test_enhanced_logging.py -v --tb=short",
            "description": "Unit Tests - Enhanced Logging"
        },
        {
            "command": "python -m pytest tests/unit/api/test_monitoring_endpoints.py -v --tb=short",
            "description": "Unit Tests - Monitoring Endpoints"
        },
        {
            "command": "python -m pytest tests/unit/api/test_horse_breed_endpoints.py -v --tb=short",
            "description": "Unit Tests - Horse Breed Endpoints"
        },
        {
            "command": "python -m pytest tests/integration/test_system_integration.py -v --tb=short -m integration",
            "description": "Integration Tests - System Integration"
        },
        {
            "command": "python -m pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing --cov-fail-under=80",
            "description": "Complete Test Suite with Coverage"
        },
        {
            "command": "python -m pytest tests/ -v -m performance --tb=short",
            "description": "Performance Tests"
        },
        {
            "command": "python -m pytest tests/ -v -m monitoring --tb=short",
            "description": "Monitoring Tests"
        }
    ]
    
    # Run tests
    passed_tests = 0
    failed_tests = 0
    
    for test_info in test_commands:
        success = run_command(test_info["command"], test_info["description"])
        if success:
            passed_tests += 1
        else:
            failed_tests += 1
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print('='*60)
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"📊 Total:  {passed_tests + failed_tests}")
    
    if failed_tests == 0:
        print("\n🎉 All tests passed! Your service is ready for production.")
        return 0
    else:
        print(f"\n⚠️  {failed_tests} test suite(s) failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)