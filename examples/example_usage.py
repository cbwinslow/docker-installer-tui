#!/usr/bin/env python3
"""
Example script demonstrating Docker Installer TUI functionality.
This script shows how to use the various components of the Docker Installer TUI.
"""

import sys
import os
# Add current directory to path to import local modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from DockerInstallerTUI import DockerHubAPI, ContainerManager, AIHelper
from DockerInstaller import ConfigManager


def example_docker_hub_api():
    """Example of using the DockerHubAPI."""
    print("=== Docker Hub API Example ===")
    
    api = DockerHubAPI()
    
    # Search for nginx images
    print("Searching for 'nginx' images...")
    try:
        results = api.search_images("nginx", page_size=3)
        
        if 'results' in results and results['results']:
            for result in results['results'][:3]:  # Show first 3 results
                name = result.get('name', result.get('repo_name', 'N/A'))
                description = result.get('description', 'No description')
                stars = result.get('star_count', 0)
                print(f"  - {name}: {description} (★{stars})")
        else:
            print("  No results found")
    except Exception as e:
        print(f"  Error searching Docker Hub: {e}")
    
    print()


def example_container_manager():
    """Example of using the ContainerManager."""
    print("=== Container Manager Example ===")
    
    cm = ContainerManager()
    
    # Get all containers
    print("Getting all containers...")
    containers = cm.get_all_containers()
    
    if containers:
        for container in containers[:5]:  # Show first 5 containers
            name = container.get('name', 'N/A')
            image = container.get('image', 'N/A')
            status = container.get('status', 'N/A')
            print(f"  - {name}: {image} ({status})")
    else:
        print("  No containers found")
        print("  (This is expected if Docker isn't installed yet or no containers exist)")
    
    print()


def example_ai_helper():
    """Example of using the AIHelper."""
    print("=== AI Helper Example ===")
    
    ai = AIHelper()
    
    # Check Ollama availability
    print(f"Ollama available: {ai.ollama_available}")
    
    # Get Docker advice (will use fallback if no AI service is configured)
    question = "What is the best practice for Docker container security?"
    response = ai.get_docker_advice(question)
    print(f"Q: {question}")
    print(f"A: {response}")
    
    print()


def example_config_manager():
    """Example of using the ConfigManager."""
    print("=== Config Manager Example ===")
    
    # Load default config
    config = ConfigManager()
    
    # Display some configuration values
    print(f"Log level: {config.get_value('log_level')}")
    print(f"Install Docker Engine: {config.get_value('install_docker_engine')}")
    print(f"Password file path: {config.get_value('password_file_path')}")
    
    print()


def main():
    """Main function to run all examples."""
    print("Docker Installer TUI Examples")
    print("=" * 40)
    
    example_docker_hub_api()
    example_container_manager()
    example_ai_helper()
    example_config_manager()
    
    # Example of octopus mascot functionality
    print("=== Octopus Mascot Example ===")
    from OctopusMascot import get_octopus_greeting, get_octopus_fact, get_octopus_tip
    print(f"Greeting: {get_octopus_greeting()}")
    print(f"Fact: {get_octopus_fact()}")
    print(f"Tip: {get_octopus_tip()}")
    print()
    
    print("For more examples, see the examples/ directory.")


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()