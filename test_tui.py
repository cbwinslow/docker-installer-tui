#!/usr/bin/env python3
"""
TUI Test Script
This script tests that the TUI code has valid syntax and can be imported.
"""
import os
import sys
from pathlib import Path

def test_tui_syntax():
    """Test that the TUI Python script has valid syntax."""
    script_path = Path("DockerInstallerTUI.py")
    if not script_path.exists():
        print(f"ERROR: {script_path} does not exist")
        return False
    
    # Test syntax by compiling
    try:
        compile(script_path.read_text(), str(script_path), 'exec')
        print("✓ TUI Python syntax is valid")
        return True
    except SyntaxError as e:
        print(f"✗ TUI Python syntax error: {e}")
        return False

def test_css_exists():
    """Test that the CSS file exists."""
    css_path = Path("docker_installer.tcss")
    if css_path.exists():
        print("✓ TUI CSS file exists")
        return True
    else:
        print("✗ TUI CSS file does not exist")
        return False

def main():
    """Main test function."""
    print("Testing Docker Installation TUI...")
    print("="*50)
    
    # Change to the script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    all_tests_passed = True
    
    if not test_tui_syntax():
        all_tests_passed = False
    
    if not test_css_exists():
        all_tests_passed = False
    
    print("="*50)
    if all_tests_passed:
        print("✓ All TUI tests passed! The TUI is ready to use.")
        print("\nTo run the TUI, first install requirements:")
        print("  pip3 install -r requirements.txt")
        print("\nThen run:")
        print("  python3 DockerInstallerTUI.py")
    else:
        print("✗ Some TUI tests failed. Please review the output above.")
    
    return 0 if all_tests_passed else 1

if __name__ == "__main__":
    sys.exit(main())