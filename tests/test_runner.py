"""
Test runner for AI Code Agent
"""
import os
import sys
import subprocess
import pytest
from pathlib import Path


def run_tests():
    """Run all tests for the AI Code Agent"""
    print("Running AI Code Agent Test Suite")
    print("=" * 50)
    
    # Get the tests directory
    tests_dir = Path(__file__).parent
    project_root = tests_dir.parent
    
    # Change to project root
    os.chdir(project_root)
    
    # Test files to run
    test_files = [
        "tests/test_file_operations.py",
        "tests/test_context_management.py",
    ]
    
    # Run tests with pytest
    try:
        # Run each test file individually for better error reporting
        for test_file in test_files:
            if os.path.exists(test_file):
                print(f"\nRunning {test_file}...")
                result = subprocess.run([
                    sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✓ {test_file} passed")
                else:
                    print(f"✗ {test_file} failed")
                    print(result.stdout)
                    print(result.stderr)
            else:
                print(f"⚠ {test_file} not found")
        
        # Run all tests together
        print(f"\nRunning all tests together...")
        result = subprocess.run([
            sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ All tests passed!")
        else:
            print("✗ Some tests failed")
            print(result.stdout)
            print(result.stderr)
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"Error running tests: {e}")
        return False


def run_specific_test(test_name):
    """Run a specific test"""
    print(f"Running specific test: {test_name}")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", f"tests/{test_name}", "-v", "--tb=short"
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"Error running test {test_name}: {e}")
        return False


def run_coverage():
    """Run tests with coverage"""
    print("Running tests with coverage...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", "tests/", "--cov=main", "--cov-report=html", "--cov-report=term"
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"Error running coverage: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "coverage":
            success = run_coverage()
        else:
            success = run_specific_test(sys.argv[1])
    else:
        success = run_tests()
    
    sys.exit(0 if success else 1)
