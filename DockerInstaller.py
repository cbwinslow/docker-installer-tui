#!/usr/bin/env python3
"""
Docker Installation Script
This script installs Docker and related tools following OOP principles.
"""
import os
import sys
import subprocess
import argparse
import logging
import json
from abc import ABC, abstractmethod
from typing import List, Optional


class ILogger(ABC):
    """Abstract interface for logging."""
    
    @abstractmethod
    def info(self, message: str) -> None:
        pass
    
    @abstractmethod
    def error(self, message: str) -> None:
        pass
    
    @abstractmethod
    def warning(self, message: str) -> None:
        pass


class ConsoleLogger(ILogger):
    """Concrete implementation of ILogger for console output."""
    
    def __init__(self, level: str = "INFO"):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        if not self.logger.handlers:
            self.logger.addHandler(handler)
    
    def info(self, message: str) -> None:
        self.logger.info(message)
    
    def error(self, message: str) -> None:
        self.logger.error(message)
    
    def warning(self, message: str) -> None:
        self.logger.warning(message)


class IConfiguration:
    """Interface for configuration management."""
    
    @abstractmethod
    def load_config(self, config_path: str) -> dict:
        pass
    
    @abstractmethod
    def get_value(self, key: str, default=None):
        pass


class ConfigManager(IConfiguration):
    """Configuration management for Docker installer."""
    
    def __init__(self, config_path: str = None):
        self.config = {
            "install_prerequisites": True,
            "install_docker_engine": True,
            "install_docker_compose": True,
            "install_additional_tools": True,
            "setup_service": True,
            "add_user_to_group": True,
            "verify_installation": True,
            "password_file_path": "~/.ssh/.env",
            "log_level": "INFO",
            "docker_repo_url": "https://download.docker.com/linux/ubuntu",
            "additional_packages": [
                "docker-buildx-plugin",
                "docker-compose-plugin"
            ]
        }
        
        if config_path and os.path.exists(config_path):
            self.load_config(config_path)
    
    def load_config(self, config_path: str) -> dict:
        """Load configuration from a JSON file."""
        try:
            with open(config_path, 'r') as f:
                file_config = json.load(f)
                self.config.update(file_config)
            return self.config
        except Exception as e:
            print(f"Error loading config file {config_path}: {str(e)}")
            return self.config
    
    def get_value(self, key: str, default=None):
        """Get a configuration value."""
        return self.config.get(key, default)


class IDockerInstaller(ABC):
    """Interface for Docker installation operations."""
    
    @abstractmethod
    def install_prerequisites(self) -> bool:
        pass
    
    @abstractmethod
    def install_docker(self) -> bool:
        pass
    
    @abstractmethod
    def install_docker_compose(self) -> bool:
        pass
    
    @abstractmethod
    def install_additional_tools(self) -> bool:
        pass
    
    @abstractmethod
    def setup_docker_service(self) -> bool:
        pass
    
    @abstractmethod
    def add_user_to_docker_group(self) -> bool:
        pass


class DockerInstaller(IDockerInstaller):
    """Concrete implementation of Docker installation."""
    
    def __init__(self, logger: ILogger, config: IConfiguration):
        self.logger = logger
        self.config = config
        self.sudo_password_path = os.path.expanduser(self.config.get_value("password_file_path", "~/.ssh/.env"))
        self.sudo_password = self._read_sudo_password()
        
    def _read_sudo_password(self) -> Optional[str]:
        """Read sudo password from file."""
        try:
            with open(self.sudo_password_path, 'r') as f:
                # Assume the password is the first line
                return f.readline().strip()
        except FileNotFoundError:
            self.logger.error(f"Password file not found at {self.sudo_password_path}")
            return None
        except Exception as e:
            self.logger.error(f"Error reading password file: {str(e)}")
            return None
    
    def _run_command(self, cmd: List[str], use_sudo: bool = False) -> bool:
        """Execute a command with optional sudo."""
        try:
            if use_sudo and self.sudo_password:
                # Use echo to pipe password to sudo
                full_cmd = ['echo', self.sudo_password, '|', 'sudo', '-S'] + cmd
                # Join and split again for proper shell execution
                process_cmd = ' '.join(full_cmd)
                result = subprocess.run(
                    process_cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            else:
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            
            if result.returncode == 0:
                self.logger.info(f"Command succeeded: {' '.join(cmd)}")
                return True
            else:
                self.logger.error(f"Command failed: {' '.join(cmd)}")
                self.logger.error(f"Error: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Exception running command {' '.join(cmd)}: {str(e)}")
            return False
    
    def install_prerequisites(self) -> bool:
        """Install prerequisite packages."""
        self.logger.info("Installing prerequisites...")
        
        # Update package lists
        if not self._run_command(['apt', 'update'], use_sudo=True):
            return False
        
        prereqs = [
            'apt-transport-https',
            'ca-certificates',
            'curl',
            'software-properties-common',
            'gnupg',
            'lsb-release'
        ]
        
        for pkg in prereqs:
            self.logger.info(f"Installing {pkg}...")
            if not self._run_command(['apt', 'install', '-y', pkg], use_sudo=True):
                self.logger.error(f"Failed to install {pkg}")
                return False
        
        return True
    
    def install_docker(self) -> bool:
        """Install Docker Engine."""
        self.logger.info("Installing Docker Engine...")
        
        # Add Docker's official GPG key
        docker_repo_url = self.config.get_value("docker_repo_url", "https://download.docker.com/linux/ubuntu")
        if not self._run_command([
            'curl', '-fsSL', f'{docker_repo_url}/gpg'
        ], use_sudo=True):
            self.logger.error("Failed to download Docker GPG key")
            return False
        
        # Add Docker repository
        release = subprocess.run(['lsb_release', '-cs'], capture_output=True, text=True).stdout.strip()
        if not self._run_command([
            'add-apt-repository', 
            f'deb [arch=amd64] {docker_repo_url} {release} stable'
        ], use_sudo=True):
            self.logger.error("Failed to add Docker repository")
            return False
        
        # Update package lists again
        if not self._run_command(['apt', 'update'], use_sudo=True):
            return False
        
        # Install Docker Engine
        if not self._run_command([
            'apt', 'install', '-y', 
            'docker-ce', 
            'docker-ce-cli', 
            'containerd.io',
            'docker-buildx-plugin',
            'docker-compose-plugin'
        ], use_sudo=True):
            self.logger.error("Failed to install Docker")
            return False
        
        return True
    
    def install_docker_compose(self) -> bool:
        """Install Docker Compose."""
        self.logger.info("Installing Docker Compose...")
        
        # Install Docker Compose v2 (already included in recent Docker installations)
        # But we'll also install legacy v1 as a fallback if needed
        compose_install_cmd = [
            'curl', '-L', 
            'https://github.com/docker/compose/releases/latest/download/docker-compose-'
            f'$(uname -s)-$(uname -m)',
            '-o', '/usr/local/bin/docker-compose'
        ]
        
        if not self._run_command(['chmod', '+x', '/usr/local/bin/docker-compose'], use_sudo=True):
            self.logger.warning("Could not set Docker Compose executable permissions")
        
        return True
    
    def install_additional_tools(self) -> bool:
        """Install additional Docker-related tools."""
        self.logger.info("Installing additional Docker tools...")
        
        additional_tools = self.config.get_value("additional_packages", [
            'docker-buildx-plugin',    # Build multi-arch images
            'docker-compose-plugin',   # Docker Compose plugin
        ])
        
        for tool in additional_tools:
            if not self._run_command(['apt', 'install', '-y', tool], use_sudo=True):
                self.logger.error(f"Failed to install {tool}")
                return False
        
        return True
    
    def setup_docker_service(self) -> bool:
        """Enable and start Docker service."""
        self.logger.info("Setting up Docker service...")
        
        # Enable Docker service to start at boot
        if not self._run_command(['systemctl', 'enable', 'docker'], use_sudo=True):
            self.logger.error("Failed to enable Docker service")
            return False
        
        # Start Docker service
        if not self._run_command(['systemctl', 'start', 'docker'], use_sudo=True):
            self.logger.error("Failed to start Docker service")
            return False
        
        return True
    
    def add_user_to_docker_group(self) -> bool:
        """Add current user to docker group to avoid using sudo."""
        self.logger.info("Adding current user to docker group...")
        
        username = os.getlogin()
        if not self._run_command(['usermod', '-aG', 'docker', username], use_sudo=True):
            self.logger.warning("Failed to add user to docker group. Docker will require sudo.")
            return False
        
        self.logger.info(f"Added user {username} to docker group. Log out and back in to take effect.")
        return True
    
    def verify_installation(self) -> bool:
        """Verify Docker installation."""
        self.logger.info("Verifying Docker installation...")
        
        # Check Docker version
        if not self._run_command(['docker', '--version']):
            self.logger.error("Docker not found after installation")
            return False
        
        # Run a test container
        if not self._run_command(['docker', 'run', 'hello-world']):
            self.logger.warning("Could not run test container, but Docker is installed")
        
        # Check Docker Compose
        if not self._run_command(['docker', 'compose', 'version']):
            self.logger.info("Docker Compose not available")
        
        return True


class DockerInstallationOrchestrator:
    """Orchestrates the entire Docker installation process."""
    
    def __init__(self, installer: IDockerInstaller, logger: ILogger):
        self.installer = installer
        self.logger = logger
    
    def run_installation(self, steps: List[str]) -> bool:
        """Execute Docker installation based on specified steps."""
        try:
            success = True
            
            for step in steps:
                if step == "prerequisites":
                    success = self.installer.install_prerequisites()
                elif step == "docker":
                    success = self.installer.install_docker()
                elif step == "compose":
                    success = self.installer.install_docker_compose()
                elif step == "tools":
                    success = self.installer.install_additional_tools()
                elif step == "service":
                    success = self.installer.setup_docker_service()
                elif step == "group":
                    success = self.installer.add_user_to_docker_group()
                elif step == "verify":
                    success = self.installer.verify_installation()
                
                if not success:
                    self.logger.error(f"Installation failed at step: {step}")
                    return False
            
            self.logger.info("Docker installation completed successfully!")
            self.logger.info("Note: You may need to log out and back in for group changes to take effect.")
            return True
            
        except Exception as e:
            self.logger.error(f"Installation failed with exception: {str(e)}")
            return False


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Install Docker and related tools.')
    parser.add_argument(
        '--steps', 
        nargs='+',
        default=['prerequisites', 'docker', 'compose', 'tools', 'service', 'group', 'verify'],
        help='List of installation steps to execute (default: all steps)'
    )
    parser.add_argument(
        '--password-file',
        help='Path to sudo password file (overrides config file)'
    )
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level (overrides config file)'
    )
    parser.add_argument(
        '--config',
        default='config.json',
        help='Path to configuration file (default: config.json)'
    )
    
    return parser.parse_args()


def main():
    """Main function."""
    args = parse_arguments()
    
    # Load configuration
    config = ConfigManager(args.config)
    
    # Override config values with command-line arguments if provided
    if args.log_level:
        config.config["log_level"] = args.log_level
    if args.password_file:
        config.config["password_file_path"] = args.password_file
    
    # Initialize logger
    logger = ConsoleLogger(config.get_value("log_level", "INFO"))
    
    # Initialize installer
    try:
        installer = DockerInstaller(logger, config)
    except Exception as e:
        logger.error(f"Failed to initialize DockerInstaller: {str(e)}")
        sys.exit(1)
    
    # Initialize orchestrator
    orchestrator = DockerInstallationOrchestrator(installer, logger)
    
    # Run installation
    success = orchestrator.run_installation(args.steps)
    
    if success:
        logger.info("Docker stack installation completed successfully!")
        sys.exit(0)
    else:
        logger.error("Docker stack installation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()