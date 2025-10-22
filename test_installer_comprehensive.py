#!/usr/bin/env python3
"""
Comprehensive Docker Installer Test Suite
Tests all installation functionality including hardware detection, version compatibility, 
and proper installation steps.
"""
import os
import sys
import unittest
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock, mock_open, call
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


class TestHardwareDetection(unittest.TestCase):
    """Test hardware and OS detection functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.logger = ConsoleLogger("ERROR")
        self.config = ConfigManager()
    
    @patch('subprocess.run')
    def test_detect_architecture_amd64(self, mock_run):
        """Test detecting amd64 architecture."""
        mock_run.return_value = Mock(
            stdout='amd64\n',
            returncode=0
        )
        
        installer = DockerInstaller(self.logger, self.config)
        
        self.assertEqual(installer.architecture, 'amd64')
        mock_run.assert_called()
    
    @patch('subprocess.run')
    def test_detect_architecture_arm64(self, mock_run):
        """Test detecting arm64 architecture."""
        mock_run.return_value = Mock(
            stdout='arm64\n',
            returncode=0
        )
        
        installer = DockerInstaller(self.logger, self.config)
        
        self.assertEqual(installer.architecture, 'arm64')
    
    @patch('subprocess.run')
    def test_detect_architecture_fallback(self, mock_run):
        """Test architecture detection fallback to uname."""
        # First call to dpkg fails
        # Second call to uname returns x86_64
        # Third call is for lsb_release in OS detection
        def side_effect(*args, **kwargs):
            cmd = args[0] if args else kwargs.get('cmd', [])
            if 'dpkg' in str(cmd):
                raise Exception("dpkg failed")
            elif 'uname' in str(cmd):
                return Mock(stdout='x86_64\n', returncode=0)
            elif 'lsb_release' in str(cmd):
                return Mock(stdout='focal\n', returncode=0)
            return Mock(stdout='', returncode=0)
        
        mock_run.side_effect = side_effect
        
        installer = DockerInstaller(self.logger, self.config)
        
        # Should map x86_64 to amd64
        self.assertEqual(installer.architecture, 'amd64')
    
    @patch('subprocess.run')
    def test_detect_architecture_armv7l(self, mock_run):
        """Test detecting ARMv7 architecture."""
        def side_effect(*args, **kwargs):
            cmd = args[0] if args else kwargs.get('cmd', [])
            if 'dpkg' in str(cmd):
                raise Exception("dpkg failed")
            elif 'uname' in str(cmd):
                return Mock(stdout='armv7l\n', returncode=0)
            elif 'lsb_release' in str(cmd):
                return Mock(stdout='focal\n', returncode=0)
            return Mock(stdout='', returncode=0)
        
        mock_run.side_effect = side_effect
        
        installer = DockerInstaller(self.logger, self.config)
        
        # Should map armv7l to armhf
        self.assertEqual(installer.architecture, 'armhf')
    
    @patch('builtins.open', new_callable=mock_open, read_data='ID=ubuntu\nVERSION_ID="24.04"\nVERSION_CODENAME=noble\n')
    @patch('os.path.exists')
    @patch('subprocess.run')
    def test_detect_os_ubuntu_24(self, mock_run, mock_exists, mock_file):
        """Test detecting Ubuntu 24.04."""
        mock_exists.return_value = True
        mock_run.return_value = Mock(stdout='noble\n', returncode=0)
        
        installer = DockerInstaller(self.logger, self.config)
        
        self.assertEqual(installer.os_info['id'], 'ubuntu')
        self.assertEqual(installer.os_info['version_id'], '24.04')
        self.assertEqual(installer.os_info['version_codename'], 'noble')
    
    @patch('builtins.open', new_callable=mock_open, read_data='ID=debian\nVERSION_ID="12"\nVERSION_CODENAME=bookworm\n')
    @patch('os.path.exists')
    @patch('subprocess.run')
    def test_detect_os_debian(self, mock_run, mock_exists, mock_file):
        """Test detecting Debian."""
        mock_exists.return_value = True
        mock_run.return_value = Mock(stdout='bookworm\n', returncode=0)
        
        installer = DockerInstaller(self.logger, self.config)
        
        self.assertEqual(installer.os_info['id'], 'debian')
        self.assertEqual(installer.os_info['version_codename'], 'bookworm')


class TestConfigManager(unittest.TestCase):
    """Test configuration management."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = ConfigManager()
        
        self.assertTrue(config.get_value("install_prerequisites"))
        self.assertTrue(config.get_value("install_docker_engine"))
        self.assertTrue(config.get_value("verify_installation"))
        self.assertEqual(config.get_value("log_level"), "INFO")
    
    def test_load_config_from_file(self):
        """Test loading configuration from JSON file."""
        test_config = {
            "install_prerequisites": False,
            "log_level": "DEBUG",
            "additional_packages": ["test-package"]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_config, f)
            config_path = f.name
        
        try:
            config = ConfigManager(config_path)
            
            self.assertFalse(config.get_value("install_prerequisites"))
            self.assertEqual(config.get_value("log_level"), "DEBUG")
            self.assertIn("test-package", config.get_value("additional_packages"))
        finally:
            os.unlink(config_path)
    
    def test_get_value_with_default(self):
        """Test getting configuration value with default."""
        config = ConfigManager()
        
        value = config.get_value("nonexistent_key", "default_value")
        self.assertEqual(value, "default_value")
    
    def test_invalid_config_file(self):
        """Test handling of invalid config file."""
        config = ConfigManager("/nonexistent/path/config.json")
        
        # Should fall back to defaults
        self.assertTrue(config.get_value("install_prerequisites"))


class TestDockerInstaller(unittest.TestCase):
    """Test Docker installer functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.logger = ConsoleLogger("ERROR")
        self.config = ConfigManager()
        
        # Create a temporary password file
        self.temp_password_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.temp_password_file.write("test_password\n")
        self.temp_password_file.close()
        
        self.config.config["password_file_path"] = self.temp_password_file.name
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_password_file.name):
            os.unlink(self.temp_password_file.name)
    
    @patch('subprocess.run')
    def test_read_sudo_password(self, mock_run):
        """Test reading sudo password from file."""
        mock_run.return_value = Mock(stdout='amd64\n', returncode=0)
        
        installer = DockerInstaller(self.logger, self.config)
        
        self.assertEqual(installer.sudo_password, "test_password")
    
    @patch('subprocess.run')
    def test_run_command_without_sudo(self, mock_run):
        """Test running command without sudo."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="success",
            stderr=""
        )
        
        installer = DockerInstaller(self.logger, self.config)
        result = installer._run_command(['echo', 'test'], use_sudo=False)
        
        self.assertTrue(result)
    
    @patch('subprocess.run')
    def test_run_command_with_sudo(self, mock_run):
        """Test running command with sudo."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="success",
            stderr=""
        )
        
        installer = DockerInstaller(self.logger, self.config)
        result = installer._run_command(['apt', 'update'], use_sudo=True)
        
        self.assertTrue(result)
    
    @patch('subprocess.run')
    def test_run_command_failure(self, mock_run):
        """Test handling command failure."""
        mock_run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="error message"
        )
        
        installer = DockerInstaller(self.logger, self.config)
        result = installer._run_command(['false'], use_sudo=False)
        
        self.assertFalse(result)
    
    @patch('subprocess.run')
    def test_install_prerequisites(self, mock_run):
        """Test installing prerequisites."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="success",
            stderr=""
        )
        
        installer = DockerInstaller(self.logger, self.config)
        result = installer.install_prerequisites()
        
        self.assertTrue(result)
        # Verify apt update was called
        self.assertTrue(any('apt' in str(call) for call in mock_run.call_args_list))
    
    @patch('subprocess.run')
    def test_install_docker_with_architecture(self, mock_run):
        """Test Docker installation uses detected architecture."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="success",
            stderr=""
        )
        
        installer = DockerInstaller(self.logger, self.config)
        
        # Mock the architecture to arm64
        installer.architecture = 'arm64'
        installer.os_info = {'id': 'ubuntu', 'version_codename': 'jammy'}
        
        result = installer.install_docker()
        
        # Check that the repository was added with correct architecture
        calls = [str(call) for call in mock_run.call_args_list]
        # Should contain arm64 in the repository line
        self.assertTrue(any('arm64' in call for call in calls))
    
    @patch('subprocess.run')
    def test_verify_installation(self, mock_run):
        """Test installation verification."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Docker version 24.0.0",
            stderr=""
        )
        
        installer = DockerInstaller(self.logger, self.config)
        result = installer.verify_installation()
        
        self.assertTrue(result)
    
    @patch('subprocess.run')
    @patch('os.getlogin')
    def test_add_user_to_docker_group(self, mock_getlogin, mock_run):
        """Test adding user to docker group."""
        mock_getlogin.return_value = 'testuser'
        mock_run.return_value = Mock(
            returncode=0,
            stdout="success",
            stderr=""
        )
        
        installer = DockerInstaller(self.logger, self.config)
        result = installer.add_user_to_docker_group()
        
        self.assertTrue(result)


class TestDockerInstallationOrchestrator(unittest.TestCase):
    """Test installation orchestration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.logger = ConsoleLogger("ERROR")
        self.mock_installer = Mock()
    
    def test_run_installation_all_steps(self):
        """Test running all installation steps."""
        self.mock_installer.install_prerequisites.return_value = True
        self.mock_installer.install_docker.return_value = True
        self.mock_installer.install_docker_compose.return_value = True
        self.mock_installer.install_additional_tools.return_value = True
        self.mock_installer.setup_docker_service.return_value = True
        self.mock_installer.add_user_to_docker_group.return_value = True
        self.mock_installer.verify_installation.return_value = True
        
        orchestrator = DockerInstallationOrchestrator(self.mock_installer, self.logger)
        
        steps = ['prerequisites', 'docker', 'compose', 'tools', 'service', 'group', 'verify']
        result = orchestrator.run_installation(steps)
        
        self.assertTrue(result)
        self.mock_installer.install_prerequisites.assert_called_once()
        self.mock_installer.install_docker.assert_called_once()
        self.mock_installer.verify_installation.assert_called_once()
    
    def test_run_installation_partial_steps(self):
        """Test running only specific installation steps."""
        self.mock_installer.install_prerequisites.return_value = True
        self.mock_installer.verify_installation.return_value = True
        
        orchestrator = DockerInstallationOrchestrator(self.mock_installer, self.logger)
        
        steps = ['prerequisites', 'verify']
        result = orchestrator.run_installation(steps)
        
        self.assertTrue(result)
        self.mock_installer.install_prerequisites.assert_called_once()
        self.mock_installer.verify_installation.assert_called_once()
        # These should not be called
        self.mock_installer.install_docker.assert_not_called()
        self.mock_installer.install_docker_compose.assert_not_called()
    
    def test_run_installation_step_failure(self):
        """Test handling of step failure."""
        self.mock_installer.install_prerequisites.return_value = True
        self.mock_installer.install_docker.return_value = False
        
        orchestrator = DockerInstallationOrchestrator(self.mock_installer, self.logger)
        
        steps = ['prerequisites', 'docker', 'verify']
        result = orchestrator.run_installation(steps)
        
        self.assertFalse(result)
        self.mock_installer.install_prerequisites.assert_called_once()
        self.mock_installer.install_docker.assert_called_once()
        # Should not proceed to verify after failure
        self.mock_installer.verify_installation.assert_not_called()


class TestMakefileTargets(unittest.TestCase):
    """Test Makefile functionality."""
    
    def test_makefile_exists(self):
        """Test that Makefile exists."""
        makefile_path = Path("Makefile")
        self.assertTrue(makefile_path.exists(), "Makefile should exist")
    
    def test_makefile_has_required_targets(self):
        """Test that Makefile has all required targets."""
        makefile_path = Path("Makefile")
        
        if not makefile_path.exists():
            self.skipTest("Makefile not found")
        
        content = makefile_path.read_text()
        
        required_targets = [
            'install',
            'test',
            'test-unit',
            'test-practical',
            'test-system',
            'clean',
            'dist',
            'run',
            'help'
        ]
        
        for target in required_targets:
            self.assertIn(f'{target}:', content, f"Makefile should have '{target}' target")
    
    def test_makefile_install_target(self):
        """Test that Makefile install target works."""
        # Note: We won't actually run the install to avoid side effects
        # Just verify the command is valid
        makefile_path = Path("Makefile")
        
        if not makefile_path.exists():
            self.skipTest("Makefile not found")
        
        content = makefile_path.read_text()
        
        # Verify install target uses pip3
        self.assertIn('pip3 install', content, "Install target should use pip3")
        self.assertIn('requirements.txt', content, "Install target should reference requirements.txt")


class TestInstallationScript(unittest.TestCase):
    """Test the installation shell script."""
    
    def test_install_script_exists(self):
        """Test that install_docker.sh exists."""
        script_path = Path("install_docker.sh")
        self.assertTrue(script_path.exists(), "install_docker.sh should exist")
    
    def test_install_script_is_executable(self):
        """Test that install_docker.sh is executable."""
        script_path = Path("install_docker.sh")
        
        if not script_path.exists():
            self.skipTest("install_docker.sh not found")
        
        self.assertTrue(os.access(script_path, os.X_OK), 
                       "install_docker.sh should be executable")
    
    def test_install_script_syntax(self):
        """Test that install_docker.sh has valid bash syntax."""
        script_path = Path("install_docker.sh")
        
        if not script_path.exists():
            self.skipTest("install_docker.sh not found")
        
        # Use bash -n to check syntax without executing
        import subprocess
        result = subprocess.run(
            ['bash', '-n', str(script_path)],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0, 
                        f"install_docker.sh should have valid syntax: {result.stderr}")


class TestVersionCompatibility(unittest.TestCase):
    """Test version compatibility and proper version installation."""
    
    @patch('subprocess.run')
    def test_docker_version_check(self, mock_run):
        """Test that Docker version can be checked."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Docker version 24.0.7, build afdd53b",
            stderr=""
        )
        
        logger = ConsoleLogger("ERROR")
        config = ConfigManager()
        
        # Create temp password file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test\n")
            temp_file = f.name
        
        try:
            config.config["password_file_path"] = temp_file
            installer = DockerInstaller(logger, config)
            
            result = installer.verify_installation()
            
            self.assertTrue(result)
            # Verify docker --version was called
            calls = [str(call) for call in mock_run.call_args_list]
            self.assertTrue(any('docker' in call and '--version' in call for call in calls))
        finally:
            os.unlink(temp_file)
    
    def test_docker_compose_plugin_in_packages(self):
        """Test that docker-compose-plugin is in default packages."""
        config = ConfigManager()
        packages = config.get_value("additional_packages", [])
        
        self.assertIn("docker-compose-plugin", packages,
                     "docker-compose-plugin should be in additional packages")


def run_tests():
    """Run all tests."""
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestHardwareDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigManager))
    suite.addTests(loader.loadTestsFromTestCase(TestDockerInstaller))
    suite.addTests(loader.loadTestsFromTestCase(TestDockerInstallationOrchestrator))
    suite.addTests(loader.loadTestsFromTestCase(TestMakefileTargets))
    suite.addTests(loader.loadTestsFromTestCase(TestInstallationScript))
    suite.addTests(loader.loadTestsFromTestCase(TestVersionCompatibility))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("COMPREHENSIVE INSTALLER TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
