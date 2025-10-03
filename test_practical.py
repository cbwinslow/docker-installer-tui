#!/usr/bin/env python3
"""
Practical Test Suite for Docker Installer TUI
This test suite verifies practical functionality of the Docker Installer TUI.
"""
import os
import sys
import subprocess
import time
import tempfile
from pathlib import Path
import json

def check_prerequisites():
    """Check if prerequisites are available."""
    print("Checking prerequisites...")
    
    # Check if required packages are available
    try:
        import textual
        print(f"✓ Textual: {textual.__version__}")
    except ImportError:
        print("✗ Textual not found")
        return False
    
    try:
        import requests
        print(f"✓ Requests: {requests.__version__}")
    except ImportError:
        print("✗ Requests not found")
        return False
    
    try:
        import docker
        print(f"✓ Docker: {docker.__version__}")
    except ImportError:
        print("✗ Docker not found")
        # This might be ok if Docker is not installed yet
    
    return True


def check_files_exist():
    """Check if all required files exist."""
    print("\nChecking required files...")
    
    required_files = [
        "DockerInstaller.py",
        "DockerInstallerTUI.py",
        "docker_installer.tcss",
        "requirements.txt",
        "config.json",
        "README.md"
    ]
    
    all_found = True
    for file in required_files:
        if Path(file).exists():
            print(f"✓ {file}")
        else:
            print(f"✗ {file}")
            all_found = False
    
    return all_found


def check_syntax():
    """Check syntax of Python files."""
    print("\nChecking Python syntax...")
    
    python_files = ["DockerInstaller.py", "DockerInstallerTUI.py", "test_suite.py"]
    
    all_good = True
    for file in python_files:
        try:
            with open(file, 'r') as f:
                compile(f.read(), file, 'exec')
            print(f"✓ {file} syntax OK")
        except SyntaxError as e:
            print(f"✗ {file} syntax error: {e}")
            all_good = False
        except Exception as e:
            print(f"✗ {file} error: {e}")
            all_good = False
    
    return all_good


def test_config_loading():
    """Test that configuration loads properly."""
    print("\nTesting configuration loading...")
    
    try:
        from DockerInstaller import ConfigManager
        config = ConfigManager("config.json")
        
        # Test basic config values
        log_level = config.get_value("log_level", "INFO")
        password_path = config.get_value("password_file_path")
        
        print(f"✓ Config loaded - log_level: {log_level}")
        print(f"✓ Config loaded - password_path: {password_path}")
        
        return True
    except Exception as e:
        print(f"✗ Config loading failed: {e}")
        return False


def test_api_integration():
    """Test API components."""
    print("\nTesting API integration...")
    
    try:
        from DockerInstallerTUI import DockerHubAPI
        api = DockerHubAPI()
        
        # Test that the API object can be created
        print("✓ DockerHubAPI object created")
        
        # Test that it has required methods
        assert hasattr(api, 'search_images'), "search_images method missing"
        assert hasattr(api, 'get_popular_images'), "get_popular_images method missing"
        assert hasattr(api, 'get_image_details'), "get_image_details method missing"
        
        print("✓ DockerHubAPI methods available")
        
        return True
    except Exception as e:
        print(f"✗ API integration test failed: {e}")
        return False


def test_ai_helper():
    """Test AI helper functionality."""
    print("\nTesting AI helper...")
    
    try:
        from DockerInstallerTUI import AIHelper
        ai_helper = AIHelper()
        
        print("✓ AIHelper object created")
        
        # Test that methods exist
        assert hasattr(ai_helper, '_check_ollama'), "_check_ollama method missing"
        assert hasattr(ai_helper, 'get_docker_advice'), "get_docker_advice method missing"
        
        print("✓ AIHelper methods available")
        print(f"  Ollama available: {ai_helper.ollama_available}")
        
        return True
    except Exception as e:
        print(f"✗ AI helper test failed: {e}")
        return False


def test_docker_hub_api():
    """Test Docker Hub API functionality."""
    print("\nTesting Docker Hub API access...")
    
    try:
        import requests
        from DockerInstallerTUI import DockerHubAPI
        
        # Create API instance
        api = DockerHubAPI()
        
        # Test that we can make a basic request (without actually sending it in tests)
        print("✓ DockerHubAPI can be instantiated")
        
        # Test that methods exist
        assert hasattr(api, 'search_images'), "search_images method missing"
        assert hasattr(api, 'get_popular_images'), "get_popular_images method missing"
        
        print("✓ DockerHubAPI methods available")
        
        return True
    except Exception as e:
        print(f"✗ Docker Hub API test failed: {e}")
        return False


def test_config_file_structure():
    """Test the structure of the config file."""
    print("\nTesting configuration file structure...")
    
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        
        required_keys = [
            "install_prerequisites",
            "install_docker_engine",
            "install_docker_compose",
            "password_file_path",
            "log_level"
        ]
        
        all_present = True
        for key in required_keys:
            if key in config:
                print(f"✓ Config contains '{key}': {config[key]}")
            else:
                print(f"✗ Config missing '{key}'")
                all_present = False
        
        return all_present
    except Exception as e:
        print(f"✗ Config file test failed: {e}")
        return False


def test_requirements():
    """Test that requirements can be parsed."""
    print("\nTesting requirements file...")
    
    try:
        with open("requirements.txt", "r") as f:
            requirements = f.read().strip().split("\n")
        
        print(f"✓ Requirements file found with {len(requirements)} packages")
        
        required_packages = ["textual", "requests", "docker"]
        for package in required_packages:
            found = any(package in req for req in requirements if req.strip())
            if found:
                print(f"✓ Required package '{package}' found in requirements")
            else:
                print(f"✗ Required package '{package}' missing from requirements")
        
        return True
    except Exception as e:
        print(f"✗ Requirements file test failed: {e}")
        return False


def summary_report(results):
    """Print a summary of test results."""
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r)
    
    print(f"Tests passed: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! The system is ready.")
        return True
    else:
        print("❌ Some tests failed. Please check the output above.")
        return False


def run_practical_tests():
    """Run all practical tests."""
    print("Running Practical Docker Installer TUI Tests...")
    print("="*60)
    
    tests = [
        ("Check Prerequisites", check_prerequisites),
        ("Check Files Exist", check_files_exist),
        ("Check Python Syntax", check_syntax),
        ("Test Config Loading", test_config_loading),
        ("Test API Integration", test_api_integration),
        ("Test AI Helper", test_ai_helper),
        ("Test Docker Hub API", test_docker_hub_api),
        ("Test Config File Structure", test_config_file_structure),
        ("Test Requirements", test_requirements),
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
    
    return summary_report(results)


if __name__ == "__main__":
    # Change to the script directory to ensure imports work
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    success = run_practical_tests()
    sys.exit(0 if success else 1)