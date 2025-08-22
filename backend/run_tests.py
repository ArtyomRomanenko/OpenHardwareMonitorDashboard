#!/usr/bin/env python3
"""
Test runner script for Open Hardware Monitor Dashboard backend tests.
This script provides an easy way to run different types of tests.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors gracefully"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print('='*60)
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ SUCCESS")
        if result.stdout:
            print("Output:")
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ FAILED")
        print(f"Exit code: {e.returncode}")
        if e.stdout:
            print("STDOUT:")
            print(e.stdout)
        if e.stderr:
            print("STDERR:")
            print(e.stderr)
        return False

def check_dependencies():
    """Check if required testing dependencies are installed"""
    print("🔍 Checking testing dependencies...")
    
    required_packages = ['pytest', 'pytest-cov', 'pytest-mock']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Install with: python -m pip install " + " ".join(missing_packages))
        return False
    
    print("✅ All testing dependencies are installed")
    return True

def run_unit_tests():
    """Run unit tests"""
    return run_command(
        "python -m pytest tests/ -v --tb=short -m 'not integration and not slow'",
        "Unit Tests"
    )

def run_integration_tests():
    """Run integration tests"""
    return run_command(
        "python -m pytest tests/ -v --tb=short -m integration",
        "Integration Tests"
    )

def run_all_tests():
    """Run all tests"""
    return run_command(
        "python -m pytest tests/ -v --tb=short",
        "All Tests"
    )

def run_tests_with_coverage():
    """Run tests with coverage report"""
    return run_command(
        "python -m pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing",
        "Tests with Coverage Report"
    )

def run_specific_test_file(test_file):
    """Run tests from a specific file"""
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return False
    
    return run_command(
        f"python -m pytest {test_file} -v --tb=short",
        f"Specific Test File: {test_file}"
    )

def run_insights_engine_tests():
    """Run insights engine tests specifically"""
    return run_command(
        "python -m pytest tests/test_insights_engine.py -v --tb=short",
        "Insights Engine Tests"
    )

def run_data_processor_tests():
    """Run data processor tests specifically"""
    return run_command(
        "python -m pytest tests/test_data_processor.py -v --tb=short",
        "Data Processor Tests"
    )

def run_api_tests():
    """Run API endpoint tests specifically"""
    return run_command(
        "python -m pytest tests/test_api_endpoints.py -v --tb=short",
        "API Endpoint Tests"
    )

def main():
    """Main test runner function"""
    print("🚀 Open Hardware Monitor Dashboard - Test Runner")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('app') or not os.path.exists('tests'):
        print("❌ Please run this script from the backend directory")
        print("Current directory:", os.getcwd())
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'unit':
            success = run_unit_tests()
        elif command == 'integration':
            success = run_integration_tests()
        elif command == 'coverage':
            success = run_tests_with_coverage()
        elif command == 'insights':
            success = run_insights_engine_tests()
        elif command == 'data':
            success = run_data_processor_tests()
        elif command == 'api':
            success = run_api_tests()
        elif command == 'file' and len(sys.argv) > 2:
            success = run_specific_test_file(sys.argv[2])
        else:
            print("❌ Unknown command. Available commands:")
            print("  unit        - Run unit tests only")
            print("  integration - Run integration tests only")
            print("  coverage    - Run tests with coverage report")
            print("  insights    - Run insights engine tests")
            print("  data        - Run data processor tests")
            print("  api         - Run API endpoint tests")
            print("  file <path> - Run tests from specific file")
            print("  all         - Run all tests (default)")
            sys.exit(1)
    else:
        # Default: run all tests
        success = run_all_tests()
    
    # Print summary
    print("\n" + "="*60)
    if success:
        print("🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print("💥 Some tests failed. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
