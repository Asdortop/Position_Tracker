#!/usr/bin/env python3
"""
Comprehensive Test Runner for Position Tracker API

This script runs all tests to ensure the position tracker works perfectly
under all kinds of different trade inputs and scenarios.
"""

import asyncio
import subprocess
import sys
import os
import time
from pathlib import Path

def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_section(title):
    """Print a formatted section header."""
    print(f"\n--- {title} ---")

def run_command(command, description):
    """Run a command and return success status."""
    print(f"\nRunning: {description}")
    print(f"Command: {command}")
    
    start_time = time.time()
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    end_time = time.time()
    
    print(f"Duration: {end_time - start_time:.2f} seconds")
    
    if result.returncode == 0:
        print("✅ SUCCESS")
        if result.stdout:
            print("Output:", result.stdout)
    else:
        print("❌ FAILED")
        print("Error:", result.stderr)
    
    return result.returncode == 0

def check_dependencies():
    """Check if all required dependencies are installed."""
    print_header("CHECKING DEPENDENCIES")
    
    dependencies = [
        ("python", "Python interpreter"),
        ("pip", "Python package installer"),
        ("pytest", "Testing framework"),
    ]
    
    all_installed = True
    for cmd, desc in dependencies:
        result = subprocess.run(f"which {cmd}", shell=True, capture_output=True)
        if result.returncode == 0:
            print(f"✅ {desc}: Found")
        else:
            print(f"❌ {desc}: Not found")
            all_installed = False
    
    return all_installed

def install_test_dependencies():
    """Install test dependencies."""
    print_header("INSTALLING TEST DEPENDENCIES")
    
    commands = [
        ("pip install -r test_requirements.txt", "Install test requirements"),
        ("pip install -r requirements.txt", "Install main requirements"),
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    
    return True

def run_unit_tests():
    """Run unit tests."""
    print_header("RUNNING UNIT TESTS")
    
    commands = [
        ("pytest tests/test_processing_service.py -v", "Core business logic tests"),
        ("pytest tests/test_edge_cases.py -v", "Edge case tests"),
        ("pytest tests/test_fifo_scenarios.py -v", "FIFO scenario tests"),
    ]
    
    all_passed = True
    for command, description in commands:
        if not run_command(command, description):
            all_passed = False
    
    return all_passed

def run_integration_tests():
    """Run integration tests."""
    print_header("RUNNING INTEGRATION TESTS")
    
    commands = [
        ("pytest tests/test_api_endpoints.py -v", "API endpoint tests"),
    ]
    
    all_passed = True
    for command, description in commands:
        if not run_command(command, description):
            all_passed = False
    
    return all_passed

def run_performance_tests():
    """Run performance tests."""
    print_header("RUNNING PERFORMANCE TESTS")
    
    commands = [
        ("pytest tests/test_performance.py -v", "Performance tests"),
    ]
    
    all_passed = True
    for command, description in commands:
        if not run_command(command, description):
            all_passed = False
    
    return all_passed

def run_all_tests():
    """Run all tests with coverage."""
    print_header("RUNNING ALL TESTS WITH COVERAGE")
    
    command = "pytest tests/ -v --cov=app --cov-report=html --cov-report=term"
    return run_command(command, "All tests with coverage report")

def run_specific_test_scenarios():
    """Run specific test scenarios to validate core functionality."""
    print_header("RUNNING SPECIFIC TEST SCENARIOS")
    
    scenarios = [
        ("pytest tests/test_processing_service.py::TestProcessingService::test_buy_trade_processing -v", "Basic buy trade"),
        ("pytest tests/test_processing_service.py::TestProcessingService::test_sell_trade_fifo_processing -v", "FIFO sell trade"),
        ("pytest tests/test_processing_service.py::TestProcessingService::test_short_term_capital_gains_calculation -v", "Short-term tax calculation"),
        ("pytest tests/test_processing_service.py::TestProcessingService::test_long_term_capital_gains_calculation -v", "Long-term tax calculation"),
        ("pytest tests/test_edge_cases.py::TestEdgeCases::test_zero_quantity_trade -v", "Zero quantity edge case"),
        ("pytest tests/test_fifo_scenarios.py::TestFIFOScenarios::test_complex_fifo_scenario_1 -v", "Complex FIFO scenario"),
    ]
    
    all_passed = True
    for command, description in scenarios:
        if not run_command(command, description):
            all_passed = False
    
    return all_passed

def run_stress_tests():
    """Run stress tests with large datasets."""
    print_header("RUNNING STRESS TESTS")
    
    commands = [
        ("pytest tests/test_performance.py::TestPerformance::test_large_dataset_performance -v", "Large dataset test"),
        ("pytest tests/test_performance.py::TestPerformance::test_bulk_trade_processing_performance -v", "Bulk trade processing"),
        ("pytest tests/test_performance.py::TestPerformance::test_concurrent_trade_processing -v", "Concurrent processing"),
    ]
    
    all_passed = True
    for command, description in commands:
        if not run_command(command, description):
            all_passed = False
    
    return all_passed

def generate_test_report():
    """Generate a comprehensive test report."""
    print_header("GENERATING TEST REPORT")
    
    # Run tests and generate report
    command = "pytest tests/ --html=test_report.html --self-contained-html -v"
    success = run_command(command, "Generate HTML test report")
    
    if success:
        print("\n📊 Test report generated: test_report.html")
        print("📊 Coverage report generated: htmlcov/index.html")
    
    return success

def cleanup_test_files():
    """Clean up test database files."""
    print_header("CLEANING UP TEST FILES")
    
    test_files = [
        "test_position_tracker.db",
        "test_report.html",
        "htmlcov/",
        ".pytest_cache/",
        "__pycache__/",
        "tests/__pycache__/",
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            if os.path.isdir(file_path):
                import shutil
                shutil.rmtree(file_path)
                print(f"🗑️  Removed directory: {file_path}")
            else:
                os.remove(file_path)
                print(f"🗑️  Removed file: {file_path}")

def main():
    """Main test runner function."""
    print_header("POSITION TRACKER COMPREHENSIVE TEST SUITE")
    print("This script will thoroughly test your position tracker application")
    print("to ensure it works perfectly under all kinds of different trade inputs.")
    
    # Check if we're in the right directory
    if not os.path.exists("app/main.py"):
        print("❌ Error: Please run this script from the position-tracker-main directory")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Missing dependencies. Please install them first.")
        sys.exit(1)
    
    # Install test dependencies
    if not install_test_dependencies():
        print("❌ Failed to install test dependencies.")
        sys.exit(1)
    
    # Run tests
    test_results = {}
    
    print_section("Core Functionality Tests")
    test_results["unit"] = run_unit_tests()
    
    print_section("API Integration Tests")
    test_results["integration"] = run_integration_tests()
    
    print_section("Performance Tests")
    test_results["performance"] = run_performance_tests()
    
    print_section("Specific Test Scenarios")
    test_results["scenarios"] = run_specific_test_scenarios()
    
    print_section("Stress Tests")
    test_results["stress"] = run_stress_tests()
    
    print_section("Comprehensive Test Suite")
    test_results["all"] = run_all_tests()
    
    # Generate report
    test_results["report"] = generate_test_report()
    
    # Print summary
    print_header("TEST RESULTS SUMMARY")
    
    for test_type, passed in test_results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_type.upper():<15}: {status}")
    
    # Overall result
    all_passed = all(test_results.values())
    overall_status = "✅ ALL TESTS PASSED" if all_passed else "❌ SOME TESTS FAILED"
    
    print(f"\n{'='*60}")
    print(f" OVERALL RESULT: {overall_status}")
    print(f"{'='*60}")
    
    if all_passed:
        print("\n🎉 Congratulations! Your position tracker is working perfectly!")
        print("📊 Check test_report.html and htmlcov/index.html for detailed reports.")
        print("🚀 Your application is ready for production!")
    else:
        print("\n⚠️  Some tests failed. Please review the output above and fix the issues.")
        print("🔧 Check the test reports for detailed information.")
    
    # Ask about cleanup
    if input("\nDo you want to clean up test files? (y/n): ").lower() == 'y':
        cleanup_test_files()
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
