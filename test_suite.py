#!/usr/bin/env python3
"""
Comprehensive Test Suite for Docker Installer TUI
This test suite verifies all functionality of the Docker Installer TUI.
"""
import asyncio
import sys
import os
import subprocess
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import unittest

# Import the modules we need to test
try:
    from DockerInstallerTUI import (
        DockerHubAPI,
        ContainerManager,
        AIHelper,
        DockerHubScreen,
        InstallationApp,
        ConfigScreen,
        ProgressScreen
    )
    from DockerInstaller import ConfigManager
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running this from the docker-installer directory")
    sys.exit(1)


class TestDockerHubAPI(unittest.TestCase):
    """Test Docker Hub API client."""
    
    def setUp(self):
        self.api = DockerHubAPI()
    
    @patch('requests.Session.get')
    def test_search_images(self, mock_get):
        """Test Docker Hub search functionality."""
        mock_response = {
            'results': [
                {
                    'name': 'nginx',
                    'description': 'Official build of Nginx',
                    'star_count': 10000
                }
            ]
        }
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status.return_value = None
        
        result = self.api.search_images('nginx')
        
        self.assertEqual(result, mock_response)
        mock_get.assert_called_once()
    
    @patch('requests.Session.get')
    def test_get_popular_images(self, mock_get):
        """Test getting popular images."""
        mock_response = {
            'results': [
                {
                    'name': 'alpine',
                    'description': 'A minimal Docker image',
                    'pull_count': 50000000
                }
            ]
        }
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status.return_value = None
        
        result = self.api.get_popular_images()
        
        self.assertEqual(result, mock_response)
        mock_get.assert_called_once()
    
    @patch('requests.Session.get')
    def test_get_image_details(self, mock_get):
        """Test getting image details."""
        mock_response = {
            'name': 'nginx',
            'description': 'Official build of Nginx',
            'star_count': 10000
        }
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status.return_value = None
        
        result = self.api.get_image_details('nginx')
        
        self.assertEqual(result, mock_response)
        mock_get.assert_called_once()


class TestContainerManager(unittest.TestCase):
    """Test Container Manager functionality."""
    
    def setUp(self):
        # Mock docker client to avoid requiring Docker to be installed
        with patch('docker.from_env') as mock_docker:
            self.container_manager = ContainerManager()
            self.container_manager.client = Mock()
    
    def test_get_running_containers(self):
        """Test getting running containers."""
        # Mock a container
        mock_container = Mock()
        mock_container.short_id = 'abc123'
        mock_container.name = 'test_container'
        mock_container.image = Mock()
        mock_container.image.tags = ['nginx:latest']
        mock_container.status = 'running'
        mock_container.ports = {}
        
        self.container_manager.client.containers.list.return_value = [mock_container]
        
        containers = self.container_manager.get_running_containers()
        
        self.assertEqual(len(containers), 1)
        self.assertEqual(containers[0]['name'], 'test_container')
    
    def test_get_all_containers(self):
        """Test getting all containers."""
        # Mock a container
        mock_container = Mock()
        mock_container.short_id = 'def456'
        mock_container.name = 'test_container2'
        mock_container.image = Mock()
        mock_container.image.tags = ['alpine:latest']
        mock_container.status = 'exited'
        mock_container.ports = {}
        
        self.container_manager.client.containers.list.return_value = [mock_container]
        
        containers = self.container_manager.get_all_containers()
        
        self.assertEqual(len(containers), 1)
        self.assertEqual(containers[0]['name'], 'test_container2')
    
    def test_pull_image(self):
        """Test pulling an image."""
        self.container_manager.client.images.pull.return_value = Mock()
        
        result = self.container_manager.pull_image('nginx:latest')
        
        self.assertTrue(result)
        self.container_manager.client.images.pull.assert_called_once_with('nginx:latest')
    
    def test_start_container(self):
        """Test starting a container."""
        mock_container = Mock()
        self.container_manager.client.containers.get.return_value = mock_container
        
        result = self.container_manager.start_container('test_container')
        
        self.assertTrue(result)
        mock_container.start.assert_called_once()


class TestAIHelper(unittest.TestCase):
    """Test AI Helper functionality."""
    
    def setUp(self):
        self.ai_helper = AIHelper()
    
    @patch('requests.get')
    def test_check_ollama(self, mock_get):
        """Test checking if Ollama is available."""
        # Simulate Ollama being available
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = self.ai_helper._check_ollama()
        
        self.assertTrue(result)
    
    @patch('requests.get')
    def test_check_ollama_unavailable(self, mock_get):
        """Test checking if Ollama is unavailable."""
        # Simulate Ollama being unavailable
        mock_get.side_effect = Exception("Connection failed")
        
        result = self.ai_helper._check_ollama()
        
        self.assertFalse(result)
    
    def test_set_openrouter_api_key(self):
        """Test setting OpenRouter API key."""
        api_key = "test_key_123"
        self.ai_helper.set_openrouter_api_key(api_key)
        
        self.assertEqual(self.ai_helper.openrouter_api_key, api_key)
    
    def test_get_docker_advice_no_service(self):
        """Test getting advice when no AI service is configured."""
        with patch.object(self.ai_helper, '_check_ollama', return_value=False):
            response = self.ai_helper.get_docker_advice("How do I use nginx?")
        
        self.assertIn("AI features are not configured", response)


class TestConfigManager(unittest.TestCase):
    """Test Configuration Manager."""
    
    def test_config_loading(self):
        """Test loading configuration."""
        config = ConfigManager()
        
        self.assertIsNotNone(config.get_value("install_prerequisites"))
        self.assertIsNotNone(config.get_value("password_file_path"))
        self.assertEqual(config.get_value("log_level"), "INFO")
    
    def test_config_from_file(self):
        """Test loading configuration from file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            import json
            json.dump({
                "log_level": "DEBUG",
                "install_docker_engine": False
            }, f)
            temp_path = f.name
        
        try:
            config = ConfigManager(temp_path)
            self.assertEqual(config.get_value("log_level"), "DEBUG")
            self.assertFalse(config.get_value("install_docker_engine"))
        finally:
            os.unlink(temp_path)


class TestTUIScreens(unittest.TestCase):
    """Test TUI screens."""
    
    def test_config_screen_creation(self):
        """Test ConfigScreen creation."""
        config_manager = ConfigManager()
        screen = ConfigScreen(config_manager)
        
        self.assertIsNotNone(screen)
        self.assertEqual(screen.config_manager, config_manager)
    
    def test_docker_hub_screen_creation(self):
        """Test DockerHubScreen creation."""
        screen = DockerHubScreen()
        
        self.assertIsNotNone(screen)
        self.assertIsNotNone(screen.docker_hub_api)
        self.assertIsNotNone(screen.container_manager)
        self.assertIsNotNone(screen.ai_helper)


class TestIntegration(unittest.TestCase):
    """Integration tests."""
    
    def test_app_creation(self):
        """Test that the main app can be created."""
        app = InstallationApp()
        
        self.assertIsNotNone(app)
        self.assertIsNotNone(app.config_manager)
        self.assertIsNotNone(app.logger)
    
    def test_config_flow(self):
        """Test the configuration flow."""
        config_manager = ConfigManager()
        
        # Modify some config values
        config_manager.config["log_level"] = "DEBUG"
        config_manager.config["install_prerequisites"] = False
        
        # Verify the changes
        self.assertEqual(config_manager.get_value("log_level"), "DEBUG")
        self.assertFalse(config_manager.get_value("install_prerequisites"))


def run_tests():
    """Run all tests."""
    print("Running Docker Installer TUI Test Suite...")
    print("="*60)
    
    # Create a test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    # Change to the script directory to ensure imports work
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    success = run_tests()
    sys.exit(0 if success else 1)