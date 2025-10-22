# Docker Installer TUI

A comprehensive Terminal User Interface (TUI) application for Docker installation, management, and exploration with AI-powered assistance.

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Configuration](#configuration)
6. [API Integration](#api-integration)
7. [AI Assistant](#ai-assistant)
8. [Development](#development)
9. [Testing](#testing)
10. [Contributing](#contributing)
11. [License](#license)

## Overview

The Docker Installer TUI is a complete solution for Docker installation and management featuring:
- Interactive installation of Docker and related tools
- Docker Hub exploration and search capabilities
- Container management
- AI-powered Docker assistance
- Clean, user-friendly terminal interface

## Features

### Core Installation Features
- Step-by-step Docker installation
- Prerequisites installation
- Docker Engine installation
- Docker Compose installation
- Additional tools (Buildx, etc.)
- Service setup and user group management
- Installation verification

### Docker Hub Exploration
- Search Docker images on Docker Hub
- Browse popular containers
- View image details and statistics
- Image pull functionality

### Container Management
- View all containers (running and stopped)
- Start/stop containers
- Container information display
- Image management

### AI Assistant
- Local Ollama support
- OpenRouter API integration
- Docker best practices advice
- Configuration recommendations

### User Interface
- Terminal-based user interface using Textual
- Tabbed navigation
- Real-time progress updates
- Error handling and notifications
- Responsive design
- Animated 8-bit octopus mascot for assistance and fun!

### Octopus Mascot Features
- Animated banner with moving tentacles on startup
- Random Docker facts, greetings and tips
- Sidebar assistant in Docker Hub section
- Interactive messages throughout the application
- Fun ASCII art animations

#### Octopus Mascot Details
The 8-bit octopus mascot provides an engaging user experience with:
- **Animated Banner**: Appears on the main screen with moving tentacles
- **Random Greetings**: Displays different Docker-themed greetings each time
- **Docker Facts**: Shows interesting facts about Docker and octopuses
- **Pro Tips**: Provides Docker best practices and advice
- **Position Animation**: The octopus can move to different positions in the UI
- **Sidebar Assistant**: Appears in the Docker Hub section with helpful tips
- **Interactive Messages**: Responds with appropriate messages during operations

The octopus mascot is implemented in the `OctopusMascot.py` module with:
- `OctopusMascot` class for the animated widget
- `AnimatedOctopusContainer` for positioning
- Functions for random greetings, facts, and tips
- CSS styling in `docker_installer.tcss`

## Installation

### Prerequisites
- Python 3.8+
- Linux OS (Ubuntu/Debian recommended)
- Sudo access for Docker installation

### Quick Install

```bash
# Clone the repository
git clone https://github.com/cbwinslow/docker-installer-tui.git
cd docker-installer-tui

# Install dependencies
pip3 install -r requirements.txt

# Run the TUI
python3 DockerInstallerTUI.py
```

### Using the Makefile

The project includes a comprehensive Makefile for building and testing:

```bash
# Install dependencies
make install

# Run all tests
make test

# Run specific test suites
make test-unit      # Unit tests
make test-practical # Practical tests
make test-system    # System tests

# Build distribution packages
make dist

# Create PyPI packages
make pip

# Run the application
make run
```

### Using the Convenience Scripts

```bash
# Install Docker stack
./install_docker.sh

# Run the TUI
./run_tui.sh
```

## Usage

### Main Interface
The main interface provides:
- **Configure**: Adjust installation settings
- **Install**: Run Docker installation
- **Docker Hub**: Explore Docker Hub
- **Exit**: Exit the application

### Configuration Screen
- Toggle installation steps on/off
- Set log level (DEBUG, INFO, WARNING, ERROR)
- Specify password file location
- Adjust Docker repository URL
- Configure additional packages

### Installation Process
1. Select desired installation steps
2. Adjust configuration as needed
3. Click "Install" to begin
4. Monitor progress in the progress screen
5. Check results when complete

### Docker Hub Exploration
1. Navigate to "Docker Hub" from main menu
2. Use "Search" tab to find images
3. Use "Popular" tab to browse trending containers
4. Use "Containers" tab to manage local containers
5. Use "AI Assistant" tab for Docker advice

## Configuration

### Configuration File (config.json)
The application uses a JSON configuration file with the following options:

```json
{
  "install_prerequisites": true,
  "install_docker_engine": true,
  "install_docker_compose": true,
  "install_additional_tools": true,
  "setup_service": true,
  "add_user_to_group": true,
  "verify_installation": true,
  "password_file_path": "~/.ssh/.env",
  "log_level": "INFO",
  "docker_repo_url": "https://download.docker.com/linux/ubuntu",
  "additional_packages": [
    "docker-buildx-plugin",
    "docker-compose-plugin"
  ]
}
```

### Password File
The application reads the sudo password from a file specified in `password_file_path`. The file should contain only the password on the first line.

### Installation Steps
- `install_prerequisites`: Install required system packages
- `install_docker_engine`: Install Docker Engine
- `install_docker_compose`: Install Docker Compose
- `install_additional_tools`: Install additional Docker tools
- `setup_service`: Enable and start Docker service
- `add_user_to_group`: Add current user to docker group
- `verify_installation`: Verify the installation

## API Integration

### Docker Hub API
The application uses Docker Hub's v2 API to:
- Search for Docker images
- Retrieve popular images
- Get image details

### API Endpoints Used
- `GET /v2/search/repositories` - Search repositories
- `GET /v2/repositories` - Get popular repositories
- `GET /v2/repositories/{name}` - Get repository details

### Rate Limiting
The application respects Docker Hub rate limits. For heavy usage, consider implementing API keys or caching.

## AI Assistant

### Ollama Integration
To use the Ollama AI assistant:
1. Install Ollama from https://ollama.ai
2. Pull a model: `ollama pull llama2`
3. Start Ollama: `ollama serve`
4. Use the AI assistant in the application

### OpenRouter Integration
To use OpenRouter:
1. Get an API key from https://openrouter.ai
2. Set the API key in the application
3. Use the AI assistant in the application

### AI Capabilities
- Docker best practices
- Container configuration advice
- Troubleshooting help
- Security recommendations

## Development

### Project Structure
```
docker-installer-tui/
├── DockerInstaller.py          # Core Docker installation logic
├── DockerInstallerTUI.py       # TUI application
├── docker_installer.tcss       # Textual stylesheet
├── config.json                 # Default configuration
├── requirements.txt            # Python dependencies
├── install_docker.sh           # Installation script
├── run_tui.sh                  # TUI launch script
├── test_suite.py              # Unit tests
├── test_practical.py          # Practical tests
├── test_system.py             # System tests
├── test_comprehensive.py      # Comprehensive end-to-end tests
├── docs/                      # Documentation
├── examples/                  # Example configurations
└── README.md
```

### Extending Functionality
To extend the TUI with new features:
1. Create new screen classes inheriting from `Screen`
2. Add UI components using Textual widgets
3. Implement background operations with `@work(thread=True)`
4. Update the main application to include new screens

### Contributing Guidelines
1. Follow the existing code style
2. Write tests for new functionality
3. Update documentation for changes
4. Follow the SOLID principles
5. Ensure backward compatibility

## Testing

### Running Tests
```bash
# Run practical tests
python3 test_practical.py

# Run unit tests
python3 test_suite.py

# Run system integration tests
python3 test_system.py

# Run comprehensive end-to-end tests
python3 test_comprehensive.py

# Run comprehensive installer tests (hardware detection, version compatibility)
python3 test_installer_comprehensive.py

# Run installer integration tests (real system testing)
python3 test_installer_integration.py

# Run all tests
make test-all  # This runs all test suites

# Or run specific test categories:
make test            # Run core tests
make test-installation
make test-installer-comprehensive
make test-installer-integration
```

### Test Coverage
- Unit tests for all classes and methods (test_suite.py)
- Practical tests for system integration (test_practical.py)
- System tests for end-to-end functionality (test_system.py)
- Comprehensive end-to-end tests (test_comprehensive.py)
- Comprehensive installer tests (test_installer_comprehensive.py):
  - Hardware architecture detection (amd64, arm64, armhf, armel)
  - OS distribution detection (Ubuntu, Debian, etc.)
  - Configuration management
  - Installation step verification
  - Makefile validation
  - Version compatibility
- Integration tests (test_installer_integration.py):
  - Real system hardware detection
  - Docker availability verification
  - Configuration file validation
  - Installation prerequisites
- Mock-based testing for external dependencies
- Syntax and import validation
- Distribution package validation

### Hardware Support
The installer automatically detects:
- System architecture (amd64, arm64, armhf, armel)
- OS distribution and version (Ubuntu, Debian, etc.)
- Proper Docker repository URLs for your system

Supported architectures:
- x86_64 / amd64 (Intel/AMD 64-bit)
- aarch64 / arm64 (ARM 64-bit)
- armv7l / armhf (ARM 32-bit hard-float)
- armv6l / armel (ARM 32-bit soft-float)

### Continuous Integration
Tests should pass before merging new functionality.

## Contributing

### Reporting Issues
When reporting issues:
1. Provide detailed steps to reproduce
2. Include system information (OS, Python version)
3. Provide error messages and logs
4. Suggest possible solutions if known

### Pull Requests
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Update documentation as needed
5. Submit a pull request

### Development Setup
```bash
# Clone repository
git clone https://github.com/yourusername/docker-installer-tui.git
cd docker-installer-tui

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip3 install -r requirements.txt

# Run tests
python3 test_suite.py

# Start developing
python3 DockerInstallerTUI.py
```

## GitHub Repository

The project has been published to GitHub at: https://github.com/cbwinslow/docker-installer-tui

To set up the repository locally:

```bash
git clone https://github.com/cbwinslow/docker-installer-tui.git
cd docker-installer-tui
```

## Publishing Guide

This guide explains how to publish the Docker Installer TUI package to PyPI.

### Prerequisites

1. PyPI account with API token
2. `twine` installed: `pip3 install twine --break-system-packages`
3. `build` installed: `pip3 install build --break-system-packages`

### Steps to Publish

#### 1. Prepare the Release

```bash
# Update version in setup.py and pyproject.toml
# Run all tests
make test

# Create distribution packages
make dist
```

#### 2. Test the Package

```bash
# Check the package
python3 -m pip check

# Upload to TestPyPI first
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip3 install --index-url https://test.pypi.org/simple/ docker-installer-tui
```

#### 3. Upload to PyPI

```bash
# Upload to PyPI
twine upload dist/*
```

## License

MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.