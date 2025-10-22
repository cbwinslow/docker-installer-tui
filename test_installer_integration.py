#!/usr/bin/env python3
"""
Integration Test Suite for Docker Installer
Tests the installer with realistic scenarios and verifies proper behavior
on the actual system.
"""
import os
import sys
import unittest
import tempfile
import json
import subprocess
from pathlib import Path

# Import the modules to test
try:
    from DockerInstaller import (
        ConsoleLogger,
        ConfigManager,
        DockerInstaller,
        DockerInstallationOrchestrator
    )
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)


class TestRealSystemDetection(unittest.TestCase):
    """Test hardware detection on the actual system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.logger = ConsoleLogger("INFO")
        self.config = ConfigManager()
        
        # Create a temporary password file
        self.temp_password_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.temp_password_file.write("dummy_password\n")
        self.temp_password_file.close()
        
        self.config.config["password_file_path"] = self.temp_password_file.name
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_password_file.name):
            os.unlink(self.temp_password_file.name)
    
    def test_real_architecture_detection(self):
        """Test that architecture detection works on real system."""
        installer = DockerInstaller(self.logger, self.config)
        
        # Verify architecture is detected
        self.assertIsNotNone(installer.architecture)
        self.assertIn(installer.architecture, ['amd64', 'arm64', 'armhf', 'armel'])
        
        print(f"Detected architecture: {installer.architecture}")
    
    def test_real_os_detection(self):
        """Test that OS detection works on real system."""
        installer = DockerInstaller(self.logger, self.config)
        
        # Verify OS info is detected
        self.assertIsNotNone(installer.os_info)
        self.assertIn('id', installer.os_info)
        self.assertIn('version_codename', installer.os_info)
        
        print(f"Detected OS: {installer.os_info}")
    
    def test_architecture_matches_dpkg(self):
        """Test that detected architecture matches dpkg output."""
        try:
            result = subprocess.run(['dpkg', '--print-architecture'], 
                                  capture_output=True, text=True, check=True)
            dpkg_arch = result.stdout.strip()
            
            installer = DockerInstaller(self.logger, self.config)
            
            self.assertEqual(installer.architecture, dpkg_arch)
        except subprocess.CalledProcessError:
            self.skipTest("dpkg not available on this system")
    
    def test_os_matches_lsb_release(self):
        """Test that detected OS matches lsb_release output."""
        try:
            result = subprocess.run(['lsb_release', '-cs'], 
                                  capture_output=True, text=True, check=True)
            lsb_codename = result.stdout.strip()
            
            installer = DockerInstaller(self.logger, self.config)
            
            self.assertEqual(installer.os_info['version_codename'], lsb_codename)
        except subprocess.CalledProcessError:
            self.skipTest("lsb_release not available on this system")


class TestDockerAvailability(unittest.TestCase):
    """Test that Docker is available and working (if installed)."""
    
    def test_docker_installed(self):
        """Test if Docker is installed on the system."""
        try:
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True, check=True)
            print(f"Docker version: {result.stdout.strip()}")
            self.assertTrue(True)  # Docker is installed
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.skipTest("Docker is not installed on this system")
    
    def test_docker_compose_installed(self):
        """Test if Docker Compose is installed on the system."""
        try:
            result = subprocess.run(['docker', 'compose', 'version'], 
                                  capture_output=True, text=True, check=True)
            print(f"Docker Compose version: {result.stdout.strip()}")
            self.assertTrue(True)  # Docker Compose is installed
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.skipTest("Docker Compose is not installed on this system")
    
    def test_docker_running(self):
        """Test if Docker daemon is running."""
        try:
            result = subprocess.run(['docker', 'ps'], 
                                  capture_output=True, text=True, check=True)
            print("Docker daemon is running")
            self.assertTrue(True)  # Docker is running
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.skipTest("Docker is not running or not available")


class TestConfigurationFiles(unittest.TestCase):
    """Test configuration file handling."""
    
    def test_default_config_file_exists(self):
        """Test that default config.json exists."""
        config_path = Path("config.json")
        self.assertTrue(config_path.exists(), "config.json should exist")
    
    def test_default_config_valid_json(self):
        """Test that default config.json is valid JSON."""
        config_path = Path("config.json")
        
        if not config_path.exists():
            self.skipTest("config.json not found")
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Verify essential keys
            self.assertIn("install_prerequisites", config)
            self.assertIn("install_docker_engine", config)
            self.assertIn("log_level", config)
            
            print(f"Config keys: {list(config.keys())}")
        except json.JSONDecodeError as e:
            self.fail(f"config.json is not valid JSON: {e}")
    
    def test_custom_config_loading(self):
        """Test loading a custom configuration file."""
        custom_config = {
            "install_prerequisites": False,
            "install_docker_engine": True,
            "log_level": "DEBUG",
            "custom_key": "custom_value"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(custom_config, f)
            temp_config = f.name
        
        try:
            config = ConfigManager(temp_config)
            
            self.assertFalse(config.get_value("install_prerequisites"))
            self.assertEqual(config.get_value("log_level"), "DEBUG")
            self.assertEqual(config.get_value("custom_key"), "custom_value")
        finally:
            os.unlink(temp_config)


class TestDockerRepositoryURLs(unittest.TestCase):
    """Test Docker repository URL generation for different distributions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.logger = ConsoleLogger("ERROR")
        self.config = ConfigManager()
        
        # Create a temporary password file
        self.temp_password_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.temp_password_file.write("dummy\n")
        self.temp_password_file.close()
        
        self.config.config["password_file_path"] = self.temp_password_file.name
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_password_file.name):
            os.unlink(self.temp_password_file.name)
    
    def test_ubuntu_repository_url(self):
        """Test that Ubuntu uses correct Docker repository URL."""
        installer = DockerInstaller(self.logger, self.config)
        
        if installer.os_info['id'] == 'ubuntu':
            # Should use ubuntu URL
            expected_base = "https://download.docker.com/linux/ubuntu"
            
            # We can't easily test the full install_docker method
            # but we can verify the OS detection
            self.assertEqual(installer.os_info['id'], 'ubuntu')
    
    def test_architecture_in_repo_line(self):
        """Test that architecture is properly included in repository line."""
        installer = DockerInstaller(self.logger, self.config)
        
        # The repository line should include the detected architecture
        # Format: deb [arch=<arch>] <url> <codename> stable
        arch = installer.architecture
        
        self.assertIn(arch, ['amd64', 'arm64', 'armhf', 'armel'])


class TestInstallationPrerequisites(unittest.TestCase):
    """Test installation prerequisite checks."""
    
    def test_apt_available(self):
        """Test that apt package manager is available."""
        try:
            result = subprocess.run(['which', 'apt'], 
                                  capture_output=True, text=True, check=True)
            self.assertTrue(result.returncode == 0)
        except subprocess.CalledProcessError:
            self.skipTest("apt not available on this system")
    
    def test_curl_available(self):
        """Test that curl is available."""
        try:
            result = subprocess.run(['which', 'curl'], 
                                  capture_output=True, text=True, check=True)
            self.assertTrue(result.returncode == 0)
        except subprocess.CalledProcessError:
            self.skipTest("curl not available on this system")
    
    def test_systemctl_available(self):
        """Test that systemctl is available."""
        try:
            result = subprocess.run(['which', 'systemctl'], 
                                  capture_output=True, text=True, check=True)
            self.assertTrue(result.returncode == 0)
        except subprocess.CalledProcessError:
            self.skipTest("systemctl not available on this system")


class TestScriptHelp(unittest.TestCase):
    """Test that scripts provide help information."""
    
    def test_docker_installer_help(self):
        """Test that DockerInstaller.py provides help."""
        result = subprocess.run(
            [sys.executable, 'DockerInstaller.py', '--help'],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0)
        self.assertIn('usage:', result.stdout.lower())
    
    def test_install_script_help(self):
        """Test that install_docker.sh provides help."""
        result = subprocess.run(
            ['bash', 'install_docker.sh', '--help'],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0)
        self.assertIn('usage:', result.stdout.lower())


def run_tests():
    """Run all integration tests."""
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestRealSystemDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestDockerAvailability))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigurationFiles))
    suite.addTests(loader.loadTestsFromTestCase(TestDockerRepositoryURLs))
    suite.addTests(loader.loadTestsFromTestCase(TestInstallationPrerequisites))
    suite.addTests(loader.loadTestsFromTestCase(TestScriptHelp))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("INTEGRATION TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("="*70)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
