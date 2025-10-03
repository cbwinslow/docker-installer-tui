#!/usr/bin/env python3
"""
Docker Installation Test Script
This script tests that the installation script can be imported and run without errors.
"""
import os
import sys
import subprocess
from pathlib import Path

def test_script_syntax():
    """Test that the Python script has valid syntax."""
    script_path = Path("DockerInstaller.py")
    if not script_path.exists():
        print(f"ERROR: {script_path} does not exist")
        return False
    
    # Test syntax by compiling
    try:
        compile(script_path.read_text(), str(script_path), 'exec')
        print("✓ Python syntax is valid")
        return True
    except SyntaxError as e:
        print(f"✗ Python syntax error: {e}")
        return False

def test_help_output():
    """Test that the script can run with --help flag."""
    try:
        result = subprocess.run(
            [sys.executable, "DockerInstaller.py", "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print("✓ Script runs with --help flag")
            return True
        else:
            print(f"✗ Script failed with --help flag: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("✗ Script timed out with --help flag")
        return False
    except Exception as e:
        print(f"✗ Error running script with --help flag: {e}")
        return False

def check_dependencies():
    """Check if required dependencies are available."""
    dependencies = ["docker", "curl", "apt"]
    
    available = []
    unavailable = []
    
    for dep in dependencies:
        result = subprocess.run(["which", dep], capture_output=True)
        if result.returncode == 0:
            available.append(dep)
        else:
            unavailable.append(dep)
    
    if unavailable:
        print(f"⚠ Some dependencies not found in system: {unavailable}")
    else:
        print("✓ All dependencies are available in system")
    
    print(f"  Available: {available}")
    return True

def main():
    """Main test function."""
    print("Testing Docker Installation Script...")
    print("="*50)
    
    all_tests_passed = True
    
    # Change to the script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run tests
    if not test_script_syntax():
        all_tests_passed = False
    
    if not test_help_output():
        all_tests_passed = False
    
    check_dependencies()
    
    print("="*50)
    if all_tests_passed:
        print("✓ All tests passed! The script is ready to use.")
    else:
        print("✗ Some tests failed. Please review the output above.")
    
    return 0 if all_tests_passed else 1

if __name__ == "__main__":
    sys.exit(main())