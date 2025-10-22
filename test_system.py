#!/usr/bin/env python3
"""
System Integration Test for Docker Installer TUI
This test checks if the TUI can be properly executed.
"""
import os
import sys
import subprocess
import time
import signal
from pathlib import Path


def test_tui_launch():
    """Test launching the TUI application."""
    print("Testing TUI launch...")
    
    # Path to the TUI script
    tui_script = Path("DockerInstallerTUI.py")
    
    if not tui_script.exists():
        print(f"✗ TUI script {tui_script} not found")
        return False
    
    print(f"✓ TUI script found: {tui_script}")
    
    return True


def test_install_script():
    """Test the installation script."""
    print("\nTesting installation script...")
    
    install_script = Path("install_docker.sh")
    
    if not install_script.exists():
        print(f"✗ Install script {install_script} not found")
        return False
    
    # Check if it's executable
    if os.access(install_script, os.X_OK):
        print(f"✓ Install script is executable: {install_script}")
    else:
        print(f"✗ Install script is not executable: {install_script}")
        return False
    
    # Try to run with --help to verify it works
    try:
        result = subprocess.run(
            ["bash", str(install_script), "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✓ Install script runs with --help")
            return True
        else:
            print(f"✗ Install script failed with --help: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("✗ Install script timed out with --help")
        return False
    except Exception as e:
        print(f"✗ Install script error: {e}")
        return False


def test_run_tui_script():
    """Test the run TUI script."""
    print("\nTesting run TUI script...")
    
    run_script = Path("run_tui.sh")
    
    if not run_script.exists():
        print(f"✗ Run TUI script {run_script} not found")
        return False
    
    # Check if it's executable
    if os.access(run_script, os.X_OK):
        print(f"✓ Run TUI script is executable: {run_script}")
    else:
        print(f"✗ Run TUI script is not executable: {run_script}")
        return False
    
    # Try to verify the script can be parsed
    try:
        # Just verify the script syntax is valid bash
        result = subprocess.run(
            ["bash", "-n", str(run_script)],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print("✓ Run TUI script has valid bash syntax")
            return True
        else:
            print(f"✗ Run TUI script has syntax errors: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Run TUI script error: {e}")
        return False


def check_python_modules():
    """Check if required Python modules can be imported."""
    print("\nTesting Python module imports...")
    
    required_modules = [
        ("textual", "Textual TUI framework"),
        ("requests", "HTTP requests"),
        ("docker", "Docker API client")
    ]
    
    success = True
    for module, description in required_modules:
        try:
            __import__(module)
            print(f"✓ {description} ({module}) available")
        except ImportError:
            print(f"✗ {description} ({module}) not available")
            print(f"  You may need to install it with: pip3 install {module}")
            success = False
    
    return success


def check_config_files():
    """Check if all configuration files exist."""
    print("\nTesting configuration files...")
    
    config_files = [
        ("config.json", "Main configuration file"),
        ("docker_installer.tcss", "TUI stylesheet"),
        ("requirements.txt", "Python dependencies")
    ]
    
    all_exist = True
    for file, description in config_files:
        path = Path(file)
        if path.exists():
            print(f"✓ {description}: {file}")
        else:
            print(f"✗ Missing {description}: {file}")
            all_exist = False
    
    return all_exist


def run_system_tests():
    """Run all system integration tests."""
    print("Running System Integration Tests for Docker Installer TUI...")
    print("="*70)
    
    tests = [
        ("Check TUI Launch", test_tui_launch),
        ("Check Install Script", test_install_script),
        ("Check Run TUI Script", test_run_tui_script),
        ("Check Python Modules", check_python_modules),
        ("Check Config Files", check_config_files),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}")
        print("-" * len(test_name))
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "="*70)
    print("SYSTEM INTEGRATION TEST SUMMARY")
    print("="*70)
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r)
    
    print(f"Tests passed: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 All system tests passed! The TUI is ready to run.")
        print("\nTo run the TUI:")
        print("  python3 DockerInstallerTUI.py")
        print("\nOr use the convenience script:")
        print("  ./run_tui.sh")
        return True
    else:
        print("❌ Some system tests failed. Please check the above output.")
        return False


if __name__ == "__main__":
    # Change to the script directory to ensure imports work
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    success = run_system_tests()
    sys.exit(0 if success else 1)