# Docker Installer TUI Examples

This directory contains examples for using the Docker Installer TUI in various scenarios.

## Basic Usage

### Example 1: Full Installation
```bash
# Run the TUI and perform a full Docker installation
python3 DockerInstallerTUI.py

# Or use the convenience script
./run_tui.sh
```

### Example 2: Command Line Installation
```bash
# Install with default settings
python3 DockerInstaller.py

# Install with debug logging
python3 DockerInstaller.py --log-level DEBUG

# Install only specific steps
python3 DockerInstaller.py --steps prerequisites docker service
```

### Example 3: Using Configuration File
```bash
# Create custom config
cp config.json myconfig.json

# Modify myconfig.json as needed
# Then run with custom config
python3 DockerInstaller.py --config myconfig.json
```

## Docker Hub Exploration

### Example 4: Search for Images
```python
from DockerInstallerTUI import DockerHubAPI

api = DockerHubAPI()
results = api.search_images("nginx")
for result in results.get('results', []):
    print(f"{result.get('name')}: {result.get('description')}")
```

### Example 5: Get Popular Images
```python
from DockerInstallerTUI import DockerHubAPI

api = DockerHubAPI()
results = api.get_popular_images()
for result in results.get('results', []):
    print(f"{result.get('name')}: {result.get('pull_count')} pulls")
```

## Container Management

### Example 6: List Containers
```python
from DockerInstallerTUI import ContainerManager

cm = ContainerManager()
containers = cm.get_all_containers()
for container in containers:
    print(f"{container['name']} - {container['status']}")
```

### Example 7: Pull an Image
```python
from DockerInstallerTUI import ContainerManager

cm = ContainerManager()
success = cm.pull_image("nginx:latest")
if success:
    print("Image pulled successfully!")
else:
    print("Failed to pull image")
```

## AI Assistant

### Example 8: Get Docker Advice
```python
from DockerInstallerTUI import AIHelper

ai = AIHelper()
# Make sure Ollama is running or OpenRouter API key is set
response = ai.get_docker_advice("How do I run a nginx container with port 8080?")
print(response)
```

## Configuration

### Example 9: Custom Configuration
```json
{
  "install_prerequisites": true,
  "install_docker_engine": true,
  "install_docker_compose": true,
  "install_additional_tools": true,
  "setup_service": true,
  "add_user_to_group": true,
  "verify_installation": true,
  "password_file_path": "/path/to/password/file",
  "log_level": "DEBUG",
  "docker_repo_url": "https://download.docker.com/linux/ubuntu",
  "additional_packages": [
    "docker-buildx-plugin",
    "docker-compose-plugin"
  ]
}
```

## Advanced Usage

### Example 10: Using with Different Password Files
```bash
# Use a custom password file
./install_docker.sh --password-file /custom/path/password.txt
```

### Example 11: Custom Installation Steps
```bash
# Install only prerequisites and docker engine
./install_docker.sh --steps prerequisites docker
```

### Example 12: Using with Custom Log Level
```bash
# Run with debug logging
./install_docker.sh --log-level DEBUG
```

## Troubleshooting

### Example 13: Common Issues
```bash
# If getting permission errors:
# Make sure your password file has correct permissions
chmod 600 ~/.ssh/.env

# If Docker commands fail after installation:
# Add user to docker group or log out and back in
sudo usermod -aG docker $USER
```

## Automation

### Example 14: Using in Scripts
```bash
#!/bin/bash
# automation_example.sh

# Set up Docker installer
cd /path/to/docker-installer-tui

# Install dependencies
pip3 install -r requirements.txt --break-system-packages

# Run installation with specific config
python3 DockerInstaller.py --config my_production_config.json --log-level INFO
```

### Example 15: CI/CD Integration
```yaml
# Example GitHub Actions workflow
name: Test Docker Installer TUI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: |
        python test_suite.py
        python test_practical.py
```

## Octopus Mascot Examples

### Example 16: Using the Octopus Mascot Functions
```python
from OctopusMascot import (
    get_octopus_greeting,
    get_octopus_fact, 
    get_octopus_tip,
    OctopusMascot
)

# Get random octopus greeting
print(get_octopus_greeting())

# Get random Docker fact from octopus
print(get_octopus_fact())

# Get Docker tip from octopus
print(get_octopus_tip())

# Create and use animated octopus widget
octopus_widget = OctopusMascot("Welcome to Docker!")
# The octopus will animate its tentacles and can move around the terminal
```

These examples demonstrate the various ways to use the Docker Installer TUI in different scenarios.