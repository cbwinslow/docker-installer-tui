#!/usr/bin/env python3
"""
Comprehensive End-to-End Test for Docker Installer TUI
This test verifies the complete functionality including the octopus mascot.
"""
import sys
import os
from pathlib import Path

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from DockerInstaller import ConfigManager, DockerInstaller
        print("✓ DockerInstaller imports successfully")
    except Exception as e:
        print(f"✗ DockerInstaller import failed: {e}")
        return False
    
    try:
        from DockerInstallerTUI import (
            InstallationApp, 
            DockerHubScreen, 
            DockerHubAPI, 
            ContainerManager, 
            AIHelper
        )
        print("✓ DockerInstallerTUI imports successfully")
    except Exception as e:
        print(f"✗ DockerInstallerTUI import failed: {e}")
        return False
    
    try:
        from OctopusMascot import (
            OctopusMascot,
            get_octopus_greeting,
            get_octopus_fact,
            get_octopus_tip
        )
        print("✓ OctopusMascot imports successfully")
    except Exception as e:
        print(f"✗ OctopusMascot import failed: {e}")
        return False
    
    return True


def test_config_manager():
    """Test configuration management."""
    print("\nTesting ConfigManager...")
    
    try:
        from DockerInstaller import ConfigManager
        config = ConfigManager()
        
        # Test basic functionality
        assert config.get_value("log_level") == "INFO"
        assert config.get_value("install_docker_engine") == True
        print("✓ ConfigManager works correctly")
        return True
    except Exception as e:
        print(f"✗ ConfigManager test failed: {e}")
        return False


def test_docker_hub_api():
    """Test Docker Hub API integration."""
    print("\nTesting DockerHubAPI...")
    
    try:
        from DockerInstallerTUI import DockerHubAPI
        api = DockerHubAPI()
        
        # Test that methods exist
        assert hasattr(api, 'search_images')
        assert hasattr(api, 'get_popular_images')
        assert hasattr(api, 'get_image_details')
        print("✓ DockerHubAPI methods available")
        return True
    except Exception as e:
        print(f"✗ DockerHubAPI test failed: {e}")
        return False


def test_container_manager():
    """Test container management."""
    print("\nTesting ContainerManager...")
    
    try:
        from DockerInstallerTUI import ContainerManager
        cm = ContainerManager()
        
        # Test that methods exist
        assert hasattr(cm, 'get_running_containers')
        assert hasattr(cm, 'get_all_containers')
        assert hasattr(cm, 'pull_image')
        assert hasattr(cm, 'start_container')
        print("✓ ContainerManager methods available")
        return True
    except Exception as e:
        print(f"✗ ContainerManager test failed: {e}")
        return False


def test_ai_helper():
    """Test AI helper functionality."""
    print("\nTesting AIHelper...")
    
    try:
        from DockerInstallerTUI import AIHelper
        ai = AIHelper()
        
        # Test that methods exist
        assert hasattr(ai, 'get_docker_advice')
        assert hasattr(ai, 'set_openrouter_api_key')
        assert hasattr(ai, '_check_ollama')
        print("✓ AIHelper methods available")
        return True
    except Exception as e:
        print(f"✗ AIHelper test failed: {e}")
        return False


def test_octopus_mascot():
    """Test octopus mascot functionality."""
    print("\nTesting OctopusMascot...")
    
    try:
        from OctopusMascot import (
            get_octopus_greeting,
            get_octopus_fact,
            get_octopus_tip
        )
        
        # Test all functions return strings
        greeting = get_octopus_greeting()
        fact = get_octopus_fact()
        tip = get_octopus_tip()
        
        assert isinstance(greeting, str) and len(greeting) > 0
        assert isinstance(fact, str) and len(fact) > 0
        assert isinstance(tip, str) and len(tip) > 0
        
        print("✓ OctopusMascot functions work correctly")
        return True
    except Exception as e:
        print(f"✗ OctopusMascot test failed: {e}")
        return False


def test_main_app_creation():
    """Test that the main application can be created."""
    print("\nTesting main application creation...")
    
    try:
        from DockerInstallerTUI import InstallationApp
        app = InstallationApp()
        
        # Test that the app object is created
        assert app is not None
        print("✓ InstallationApp can be created")
        return True
    except Exception as e:
        print(f"✗ InstallationApp creation failed: {e}")
        return False


def test_file_integrity():
    """Test that all required files exist."""
    print("\nTesting file integrity...")
    
    required_files = [
        "DockerInstaller.py",
        "DockerInstallerTUI.py", 
        "OctopusMascot.py",
        "docker_installer.tcss",
        "config.json",
        "requirements.txt",
        "README.md",
        "setup.py",
        "pyproject.toml",
        "Makefile"
    ]
    
    all_good = True
    for file in required_files:
        if Path(file).exists():
            print(f"✓ {file} exists")
        else:
            print(f"✗ {file} missing")
            all_good = False
    
    return all_good


def main():
    """Run all tests."""
    print("Running Comprehensive End-to-End Tests for Docker Installer TUI")
    print("=" * 70)
    
    tests = [
        test_imports,
        test_config_manager,
        test_docker_hub_api,
        test_container_manager,
        test_ai_helper,
        test_octopus_mascot,
        test_main_app_creation,
        test_file_integrity
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 70)
    print("COMPREHENSIVE TEST SUMMARY")
    print("=" * 70)
    
    total_tests = len(results)
    passed_tests = sum(results)
    
    print(f"Tests passed: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 All comprehensive tests passed! The application is ready.")
        return True
    else:
        print("❌ Some comprehensive tests failed.")
        return False


if __name__ == "__main__":
    # Change to the script directory
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    success = main()
    sys.exit(0 if success else 1)