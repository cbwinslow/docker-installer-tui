#!/usr/bin/env python3
"""
Docker Installation TUI
A Textual-based terminal user interface for the Docker installer.
"""
import os
import json
import asyncio
import requests
import docker
from typing import List, Dict, Any, Optional
from pathlib import Path

from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import (
    Button, 
    Checkbox, 
    Footer, 
    Header, 
    Label, 
    Select, 
    Static, 
    Switch,
    TextArea,
    Input,
    OptionList,
    TabbedContent,
    TabPane,
    Collapsible
)
from textual.screen import Screen
from textual.validation import Function
from textual.message import Message
from textual.reactive import reactive

from DockerInstaller import DockerInstaller, ConsoleLogger, ConfigManager
from OctopusMascot import OctopusMascot, BannerWithOctopus, get_octopus_greeting, get_octopus_fact, get_octopus_tip


class DockerHubAPI:
    """API client for Docker Hub."""
    
    BASE_URL = "https://hub.docker.com/v2"
    
    def __init__(self):
        self.session = requests.Session()
        
    def search_images(self, query: str, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """Search for Docker images."""
        try:
            url = f"{self.BASE_URL}/search/repositories"
            params = {
                'query': query,
                'page': page,
                'page_size': page_size
            }
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error searching Docker Hub: {e}")
            return {}
    
    def get_popular_images(self, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """Get popular Docker images."""
        try:
            url = f"{self.BASE_URL}/repositories"
            params = {
                'page': page,
                'page_size': page_size,
                'ordering': 'pull_count'
            }
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting popular images: {e}")
            return {}
    
    def get_image_details(self, image_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific image."""
        try:
            url = f"{self.BASE_URL}/repositories/{image_name}"
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting image details: {e}")
            return {}


class ContainerManager:
    """Class to manage Docker containers."""
    
    def __init__(self):
        try:
            self.client = docker.from_env()
        except:
            self.client = None
    
    def get_running_containers(self) -> List[Dict[str, Any]]:
        """Get list of running containers."""
        if not self.client:
            return []
        
        try:
            containers = self.client.containers.list()
            result = []
            for container in containers:
                result.append({
                    'id': container.short_id,
                    'name': container.name,
                    'image': container.image.tags[0] if container.image.tags else 'N/A',
                    'status': container.status,
                    'ports': container.ports
                })
            return result
        except Exception as e:
            print(f"Error getting running containers: {e}")
            return []
    
    def get_all_containers(self) -> List[Dict[str, Any]]:
        """Get list of all containers (running and stopped)."""
        if not self.client:
            return []
        
        try:
            containers = self.client.containers.list(all=True)
            result = []
            for container in containers:
                result.append({
                    'id': container.short_id,
                    'name': container.name,
                    'image': container.image.tags[0] if container.image.tags else 'N/A',
                    'status': container.status,
                    'ports': container.ports
                })
            return result
        except Exception as e:
            print(f"Error getting all containers: {e}")
            return []
    
    def pull_image(self, image_name: str) -> bool:
        """Pull a Docker image."""
        if not self.client:
            return False
        
        try:
            self.client.images.pull(image_name)
            return True
        except Exception as e:
            print(f"Error pulling image {image_name}: {e}")
            return False
    
    def start_container(self, container_name: str) -> bool:
        """Start a Docker container."""
        if not self.client:
            return False
        
        try:
            container = self.client.containers.get(container_name)
            container.start()
            return True
        except Exception as e:
            print(f"Error starting container {container_name}: {e}")
            return False


class AIHelper:
    """AI assistant for Docker-related queries."""
    
    def __init__(self):
        self.ollama_available = self._check_ollama()
        self.openrouter_api_key = None
        
    def _check_ollama(self) -> bool:
        """Check if Ollama is available."""
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags")
            return response.status_code == 200
        except:
            return False
    
    def set_openrouter_api_key(self, api_key: str):
        """Set OpenRouter API key."""
        self.openrouter_api_key = api_key
    
    def get_docker_advice(self, query: str) -> str:
        """Get Docker-related advice from AI."""
        if self.ollama_available:
            return self._get_ollama_response(query)
        elif self.openrouter_api_key:
            return self._get_openrouter_response(query)
        else:
            return "AI features are not configured. Install Ollama locally or provide an OpenRouter API key."
    
    def _get_ollama_response(self, query: str) -> str:
        """Get response from local Ollama."""
        try:
            import requests
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama2",
                    "prompt": f"You are a Docker expert. Provide concise, accurate advice about: {query}",
                    "stream": False
                }
            )
            if response.status_code == 200:
                result = response.json()
                return result.get('response', 'No response received')
            else:
                return f"Error getting Ollama response: {response.status_code}"
        except Exception as e:
            return f"Error getting Ollama response: {str(e)}"
    
    def _get_openrouter_response(self, query: str) -> str:
        """Get response from OpenRouter API."""
        if not self.openrouter_api_key:
            return "No OpenRouter API key provided"
        
        try:
            import requests
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openrouter_api_key}"
                },
                json={
                    "model": "openchat/openchat-7b",
                    "messages": [
                        {"role": "system", "content": "You are an expert in Docker and containerization technology. Provide concise, accurate advice."},
                        {"role": "user", "content": query}
                    ]
                }
            )
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"Error getting OpenRouter response: {response.status_code}"
        except Exception as e:
            return f"Error getting OpenRouter response: {str(e)}"


class ConfigScreen(Screen):
    """Screen for configuration settings."""
    
    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.config_manager = config_manager
        
    def compose(self) -> ComposeResult:
        config = self.config_manager.config
        
        yield Header()
        yield Vertical(
            Label("Docker Installation Configuration", classes="title"),
            
            Vertical(
                Label("Installation Steps", classes="section-title"),
                
                Horizontal(
                    Checkbox("Install Prerequisites", value=config.get("install_prerequisites", True), id="install_prerequisites"),
                    Checkbox("Install Docker Engine", value=config.get("install_docker_engine", True), id="install_docker_engine"),
                ),
                
                Horizontal(
                    Checkbox("Install Docker Compose", value=config.get("install_docker_compose", True), id="install_docker_compose"),
                    Checkbox("Install Additional Tools", value=config.get("install_additional_tools", True), id="install_additional_tools"),
                ),
                
                Horizontal(
                    Checkbox("Setup Docker Service", value=config.get("setup_service", True), id="setup_service"),
                    Checkbox("Add User to Docker Group", value=config.get("add_user_to_group", True), id="add_user_to_docker_group"),
                ),
                
                Checkbox("Verify Installation", value=config.get("verify_installation", True), id="verify_installation"),
            ),
            
            Vertical(
                Label("Settings", classes="section-title"),
                
                Label("Password File Path:"),
                Static(config.get("password_file_path", "~/.ssh/.env"), id="password_path_display"),
                Button("Change Password File", variant="default", id="change_password_file"),
                
                Label("Log Level:"),
                Select(
                    options=[("DEBUG", "DEBUG"), ("INFO", "INFO"), ("WARNING", "WARNING"), ("ERROR", "ERROR")],
                    value=config.get("log_level", "INFO"),
                    id="log_level_select"
                ),
                
                Label("Docker Repository URL:"),
                Static(config.get("docker_repo_url", "https://download.docker.com/linux/ubuntu"), id="repo_url_display"),
                Button("Change Repo URL", variant="default", id="change_repo_url"),
            ),
            
            Horizontal(
                Button("Back", variant="primary", id="back"),
                Button("Save", variant="success", id="save"),
            ),
            id="config_form"
        )
        yield Footer()
    
    @on(Button.Pressed, "#change_password_file")
    def change_password_file(self):
        """Open a dialog to change the password file path."""
        current_path = self.config_manager.get_value("password_file_path", "~/.ssh/.env")
        # For now, we'll just show a simple input in the log - in a real app we'd have a proper dialog
        self.notify(f"Current password file path: {current_path}")
        # In a more advanced implementation, we would use a modal dialog here
    
    @on(Button.Pressed, "#change_repo_url")
    def change_repo_url(self):
        """Open a dialog to change the repository URL."""
        current_url = self.config_manager.get_value("docker_repo_url", "https://download.docker.com/linux/ubuntu")
        self.notify(f"Current repo URL: {current_url}")
        # In a more advanced implementation, we would use a modal dialog here
    
    @on(Button.Pressed, "#back")
    def go_back(self):
        """Return to the main screen."""
        self.app.pop_screen()
    
    @on(Button.Pressed, "#save")
    def save_config(self):
        """Save the current configuration."""
        # Update config from the form
        self.config_manager.config["install_prerequisites"] = self.query_one("#install_prerequisites").value
        self.config_manager.config["install_docker_engine"] = self.query_one("#install_docker_engine").value
        self.config_manager.config["install_docker_compose"] = self.query_one("#install_docker_compose").value
        self.config_manager.config["install_additional_tools"] = self.query_one("#install_additional_tools").value
        self.config_manager.config["setup_service"] = self.query_one("#setup_service").value
        self.config_manager.config["add_user_to_docker_group"] = self.query_one("#add_user_to_docker_group").value
        self.config_manager.config["verify_installation"] = self.query_one("#verify_installation").value
        self.config_manager.config["log_level"] = self.query_one("#log_level_select").value
        
        # Save to config file
        config_path = Path("config.json")
        with open(config_path, 'w') as f:
            json.dump(self.config_manager.config, f, indent=2)
        
        self.notify("Configuration saved successfully!")
        self.app.pop_screen()


class ProgressScreen(Screen):
    """Screen to show installation progress."""
    
    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.config_manager = config_manager
        self.log_content = []
        
    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Label("Docker Installation Progress", classes="title"),
            Static("Starting installation...", id="status"),
            VerticalScroll(
                Static("", id="log_display", classes="log"),
                id="log_container"
            ),
            Horizontal(
                Button("Cancel", variant="error", id="cancel"),
                id="progress_controls"
            ),
            id="progress_layout"
        )
        yield Footer()
    
    @on(Button.Pressed, "#cancel")
    def cancel_installation(self):
        """Cancel the installation process."""
        self.notify("Installation cancelled by user.")
        self.app.pop_screen()
    
    def update_log(self, message: str):
        """Update the log display with a new message."""
        self.log_content.append(message)
        log_widget = self.query_one("#log_display", Static)
        log_widget.update("\n".join(self.log_content))
        
        # Auto-scroll to bottom
        log_container = self.query_one("#log_container")
        log_container.scroll_end(animate=False)
    
    def update_status(self, message: str):
        """Update the status message."""
        status_widget = self.query_one("#status", Static)
        status_widget.update(message)


class DockerHubScreen(Screen):
    """Screen for Docker Hub exploration."""
    
    BINDINGS = [
        ("escape", "app.pop_screen", "Go Back"),
    ]
    
    def __init__(self):
        super().__init__()
        self.docker_hub_api = DockerHubAPI()
        self.container_manager = ContainerManager()
        self.ai_helper = AIHelper()
        
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Horizontal(
                Vertical(
                    Label("Docker Hub Explorer", classes="title"),
                    Horizontal(
                        Button("Search", variant="default", id="search_tab_btn"),
                        Button("Popular", variant="default", id="popular_tab_btn"),
                        Button("Containers", variant="default", id="containers_tab_btn"),
                        Button("AI Assistant", variant="default", id="ai_tab_btn"),
                        id="tab_buttons"
                    ),
                    Container(
                        Vertical(
                            Horizontal(
                                Input(placeholder="Search Docker images...", id="search_input"),
                                Button("Search", variant="primary", id="search_button"),
                                id="search_controls"
                            ),
                            OptionList(id="search_results"),
                            id="search_content"
                        ),
                        Vertical(
                            Label("Popular Docker Images", classes="section-title"),
                            OptionList(id="popular_results"),
                            Horizontal(
                                Button("Refresh", variant="default", id="refresh_popular"),
                                id="popular_controls"
                            ),
                            id="popular_content", classes="hidden"
                        ),
                        Vertical(
                            Label("My Containers", classes="section-title"),
                            OptionList(id="containers_list"),
                            Horizontal(
                                Button("Refresh", variant="default", id="refresh_containers"),
                                Button("Pull Image", variant="primary", id="pull_image"),
                                id="container_controls"
                            ),
                            id="containers_content", classes="hidden"
                        ),
                        Vertical(
                            Label("Docker AI Assistant", classes="section-title"),
                            Input(placeholder="Ask about Docker...", id="ai_query_input"),
                            Button("Ask AI", variant="primary", id="ask_ai_button"),
                            Static("", id="ai_response", classes="ai-response"),
                            Label("AI Configuration", classes="section-title"),
                            Horizontal(
                                Button("Use Ollama", variant="default", id="use_ollama"),
                                Button("Set OpenRouter Key", variant="default", id="set_openrouter_key"),
                                id="ai_config_controls"
                            ),
                            id="ai_content", classes="hidden"
                        ),
                        id="content_area"
                    ),
                    id="docker_hub_main_content"
                ),
                # Add octopus sidebar
                Vertical(
                    Static("🐙\n  Docker\n  Helper", classes="octopus-sidebar"),
                    Label(get_octopus_tip(), classes="octopus-tip", id="octopus_tip"),
                    id="octopus_sidebar"
                ),
                id="docker_hub_layout"
            ),
            id="docker_hub_container"
        )
        yield Footer()
    
    def on_mount(self):
        """Called when the screen is mounted."""
        # Show search content by default
        self.show_content("search")
        # Load popular images by default
        self.load_popular_images()
    
    @on(Button.Pressed, "#search_tab_btn")
    def on_search_tab(self):
        """Show search content."""
        self.show_content("search")
    
    @on(Button.Pressed, "#popular_tab_btn")
    def on_popular_tab(self):
        """Show popular content."""
        self.show_content("popular")
    
    @on(Button.Pressed, "#containers_tab_btn")
    def on_containers_tab(self):
        """Show containers content."""
        self.show_content("containers")
        self.load_containers()
    
    @on(Button.Pressed, "#ai_tab_btn")
    def on_ai_tab(self):
        """Show AI content."""
        self.show_content("ai")
    
    def show_content(self, content_type: str):
        """Show the specified content area and hide others."""
        content_areas = ["search", "popular", "containers", "ai"]
        for area in content_areas:
            element = self.query_one(f"#{area}_content")
            if area == content_type:
                element.remove_class("hidden")
            else:
                element.add_class("hidden")
    
    @on(Button.Pressed, "#search_button")
    def on_search_button(self):
        """Handle search button press."""
        query = self.query_one("#search_input", Input).value
        if query:
            self.search_docker_images(query)
    
    @on(Button.Pressed, "#refresh_popular")
    def on_refresh_popular(self):
        """Refresh popular images."""
        self.load_popular_images()
    
    @on(Button.Pressed, "#refresh_containers")
    def on_refresh_containers(self):
        """Refresh container list."""
        self.load_containers()
    
    @on(Button.Pressed, "#pull_image")
    def on_pull_image(self):
        """Pull selected image."""
        self.pull_selected_image()
    
    @on(Button.Pressed, "#ask_ai_button")
    def on_ask_ai_button(self):
        """Handle AI query."""
        query = self.query_one("#ai_query_input", Input).value
        if query:
            self.get_ai_response(query)
    
    @on(Button.Pressed, "#use_ollama")
    def on_use_ollama(self):
        """Configure to use Ollama."""
        if self.ai_helper._check_ollama():
            self.notify("Ollama is available and will be used for AI features", timeout=3)
        else:
            self.notify("Ollama is not available. Please install Ollama locally.", severity="warning", timeout=5)
    
    @on(Button.Pressed, "#set_openrouter_key")
    def on_set_openrouter_key(self):
        """Set OpenRouter API key."""
        # In a real implementation, this would open a dialog
        self.notify("In a full implementation, this would open an API key dialog", timeout=3)
    
    @work(thread=True)
    def search_docker_images(self, query: str):
        """Search Docker images in a background thread."""
        try:
            results = self.docker_hub_api.search_images(query)
            self.call_from_thread(self.display_search_results, results)
        except Exception as e:
            self.call_from_thread(self.notify, f"Error searching images: {str(e)}", severity="error")
    
    @work(thread=True)
    def load_popular_images(self):
        """Load popular Docker images in a background thread."""
        try:
            results = self.docker_hub_api.get_popular_images()
            self.call_from_thread(self.display_popular_results, results)
        except Exception as e:
            self.call_from_thread(self.notify, f"Error loading popular images: {str(e)}", severity="error")
    
    @work(thread=True)
    def load_containers(self):
        """Load containers in a background thread."""
        try:
            containers = self.container_manager.get_all_containers()
            self.call_from_thread(self.display_containers, containers)
        except Exception as e:
            self.call_from_thread(self.notify, f"Error loading containers: {str(e)}", severity="error")
    
    @work(thread=True)
    def pull_selected_image(self):
        """Pull selected image in a background thread."""
        # Get selected item from search or popular results
        try:
            # In a real implementation, we'd get the selected image
            # For now just show a message
            self.call_from_thread(self.notify, "Pulling selected image...", timeout=2)
        except Exception as e:
            self.call_from_thread(self.notify, f"Error pulling image: {str(e)}", severity="error")
    
    @work(thread=True)
    def get_ai_response(self, query: str):
        """Get AI response in a background thread."""
        try:
            response = self.ai_helper.get_docker_advice(query)
            self.call_from_thread(self.display_ai_response, response)
        except Exception as e:
            self.call_from_thread(self.display_ai_response, f"Error getting AI response: {str(e)}")
    
    def display_search_results(self, results: Dict[str, Any]):
        """Display search results in the UI."""
        option_list = self.query_one("#search_results", OptionList)
        option_list.clear_options()
        
        if 'results' in results and results['results']:
            for item in results['results']:
                name = item.get('name', 'N/A')
                description = item.get('description', 'No description')
                stars = item.get('star_count', 0)
                option_list.add_option(f"{name} - {description} (★{stars})")
        else:
            option_list.add_option("No results found")
    
    def display_popular_results(self, results: Dict[str, Any]):
        """Display popular image results in the UI."""
        option_list = self.query_one("#popular_results", OptionList)
        option_list.clear_options()
        
        if 'results' in results and results['results']:
            for item in results['results']:
                name = item.get('name', 'N/A')
                description = item.get('description', 'No description')
                pulls = item.get('pull_count', 0)
                option_list.add_option(f"{name} - {description} ({pulls:,} pulls)")
        else:
            option_list.add_option("No results found")
    
    def display_containers(self, containers: List[Dict[str, Any]]):
        """Display containers in the UI."""
        option_list = self.query_one("#containers_list", OptionList)
        option_list.clear_options()
        
        if containers:
            for container in containers:
                name = container.get('name', 'N/A')
                image = container.get('image', 'N/A')
                status = container.get('status', 'N/A')
                option_list.add_option(f"{name} - {image} ({status})")
        else:
            option_list.add_option("No containers found")
    
    def display_ai_response(self, response: str):
        """Display AI response in the UI."""
        response_widget = self.query_one("#ai_response", Static)
        response_widget.update(response)
    
    def on_mount(self):
        """Called when the screen is mounted."""
        # Load popular images by default
        self.load_popular_images()
    
    def compose_search_tab(self) -> ComposeResult:
        """Compose the search tab content."""
        yield Vertical(
            Horizontal(
                Input(placeholder="Search Docker images...", id="search_input"),
                Button("Search", variant="primary", id="search_button"),
                id="search_controls"
            ),
            OptionList(id="search_results"),
            id="search_tab_content"
        )
    
    def compose_popular_tab(self) -> ComposeResult:
        """Compose the popular tab content."""
        yield Vertical(
            Label("Popular Docker Images", classes="section-title"),
            OptionList(id="popular_results"),
            Horizontal(
                Button("Refresh", variant="default", id="refresh_popular"),
                id="popular_controls"
            ),
            id="popular_tab_content"
        )
    
    def compose_containers_tab(self) -> ComposeResult:
        """Compose the containers tab content."""
        yield Vertical(
            Label("My Containers", classes="section-title"),
            OptionList(id="containers_list"),
            Horizontal(
                Button("Refresh", variant="default", id="refresh_containers"),
                Button("Pull Image", variant="primary", id="pull_image"),
                id="container_controls"
            ),
            id="containers_tab_content"
        )
    
    def compose_ai_tab(self) -> ComposeResult:
        """Compose the AI assistant tab content."""
        yield Vertical(
            Label("Docker AI Assistant", classes="section-title"),
            Input(placeholder="Ask about Docker...", id="ai_query_input"),
            Button("Ask AI", variant="primary", id="ask_ai_button"),
            Static("", id="ai_response", classes="ai-response"),
            Label("AI Configuration", classes="section-title"),
            Horizontal(
                Button("Use Ollama", variant="default", id="use_ollama"),
                Button("Set OpenRouter Key", variant="default", id="set_openrouter_key"),
                id="ai_config_controls"
            ),
            id="ai_tab_content"
        )
    
    @on(Button.Pressed, "#search_button")
    def on_search_button(self):
        """Handle search button press."""
        query = self.query_one("#search_input", Input).value
        if query:
            self.search_docker_images(query)
    
    @on(Button.Pressed, "#refresh_popular")
    def on_refresh_popular(self):
        """Refresh popular images."""
        self.load_popular_images()
    
    @on(Button.Pressed, "#refresh_containers")
    def on_refresh_containers(self):
        """Refresh container list."""
        self.load_containers()
    
    @on(Button.Pressed, "#pull_image")
    def on_pull_image(self):
        """Pull selected image."""
        self.pull_selected_image()
    
    @on(Button.Pressed, "#ask_ai_button")
    def on_ask_ai_button(self):
        """Handle AI query."""
        query = self.query_one("#ai_query_input", Input).value
        if query:
            self.get_ai_response(query)
    
    @on(Button.Pressed, "#use_ollama")
    def on_use_ollama(self):
        """Configure to use Ollama."""
        if self.ai_helper._check_ollama():
            self.notify("Ollama is available and will be used for AI features", timeout=3)
        else:
            self.notify("Ollama is not available. Please install Ollama locally.", severity="warning", timeout=5)
    
    @on(Button.Pressed, "#set_openrouter_key")
    def on_set_openrouter_key(self):
        """Set OpenRouter API key."""
        # In a real implementation, this would open a dialog
        self.notify("In a full implementation, this would open an API key dialog", timeout=3)
    
    @work(thread=True)
    def search_docker_images(self, query: str):
        """Search Docker images in a background thread."""
        try:
            results = self.docker_hub_api.search_images(query)
            self.call_from_thread(self.display_search_results, results)
        except Exception as e:
            self.call_from_thread(self.notify, f"Error searching images: {str(e)}", severity="error")
    
    @work(thread=True)
    def load_popular_images(self):
        """Load popular Docker images in a background thread."""
        try:
            results = self.docker_hub_api.get_popular_images()
            self.call_from_thread(self.display_popular_results, results)
        except Exception as e:
            self.call_from_thread(self.notify, f"Error loading popular images: {str(e)}", severity="error")
    
    @work(thread=True)
    def load_containers(self):
        """Load containers in a background thread."""
        try:
            containers = self.container_manager.get_all_containers()
            self.call_from_thread(self.display_containers, containers)
        except Exception as e:
            self.call_from_thread(self.notify, f"Error loading containers: {str(e)}", severity="error")
    
    @work(thread=True)
    def pull_selected_image(self):
        """Pull selected image in a background thread."""
        # Get selected item from search or popular results
        try:
            # In a real implementation, we'd get the selected image
            # For now just show a message
            self.call_from_thread(self.notify, "Pulling selected image...", timeout=2)
        except Exception as e:
            self.call_from_thread(self.notify, f"Error pulling image: {str(e)}", severity="error")
    
    @work(thread=True)
    def get_ai_response(self, query: str):
        """Get AI response in a background thread."""
        try:
            response = self.ai_helper.get_docker_advice(query)
            self.call_from_thread(self.display_ai_response, response)
        except Exception as e:
            self.call_from_thread(self.display_ai_response, f"Error getting AI response: {str(e)}")
    
    def display_search_results(self, results: Dict[str, Any]):
        """Display search results in the UI."""
        option_list = self.query_one("#search_results", OptionList)
        option_list.clear_options()
        
        if 'results' in results and results['results']:
            for item in results['results']:
                name = item.get('name', 'N/A')
                description = item.get('description', 'No description')
                stars = item.get('star_count', 0)
                option_list.add_option(f"{name} - {description} (★{stars})")
        else:
            option_list.add_option("No results found")
    
    def display_popular_results(self, results: Dict[str, Any]):
        """Display popular image results in the UI."""
        option_list = self.query_one("#popular_results", OptionList)
        option_list.clear_options()
        
        if 'results' in results and results['results']:
            for item in results['results']:
                name = item.get('name', 'N/A')
                description = item.get('description', 'No description')
                pulls = item.get('pull_count', 0)
                option_list.add_option(f"{name} - {description} ({pulls:,} pulls)")
        else:
            option_list.add_option("No results found")
    
    def display_containers(self, containers: List[Dict[str, Any]]):
        """Display containers in the UI."""
        option_list = self.query_one("#containers_list", OptionList)
        option_list.clear_options()
        
        if containers:
            for container in containers:
                name = container.get('name', 'N/A')
                image = container.get('image', 'N/A')
                status = container.get('status', 'N/A')
                option_list.add_option(f"{name} - {image} ({status})")
        else:
            option_list.add_option("No containers found")
    
    def display_ai_response(self, response: str):
        """Display AI response in the UI."""
        response_widget = self.query_one("#ai_response", Static)
        response_widget.update(response)


class InstallationApp(App):
    """Docker Installation TUI Application."""
    
    CSS_PATH = "docker_installer.tcss"
    
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager("config.json")
        self.logger = ConsoleLogger(self.config_manager.get_value("log_level", "INFO"))
        
    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Vertical(
            # Banner with octopus mascot
            Static(
                f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║                    Docker Installation Wizard                  ║
    ║                    The 8-bit Octopus Edition                   ║
    ║                                                              ║
    ║                       \\   |   /                             ║
    ║                       \\|   |   |/                           ║
    ║                       `@._.@"@._.@'                         ║
    ║                         [   ] [   ]                         ║
    ║                                                              ║
    ║           Welcome to the Docker Installation Wizard!         ║
    ║           The friendly octopus is here to help you out!      ║
    ╚══════════════════════════════════════════════════════════════╝
                """,
                classes="banner"
            ),
            
            # Octopus fact or tip
            Static(get_octopus_greeting(), classes="greeting"),
            Static(get_octopus_fact(), classes="fact"),
            
            Vertical(
                Label("Installation Steps", classes="section-title"),
                Checkbox("Install Prerequisites", value=self.config_manager.get_value("install_prerequisites", True), id="step_prerequisites"),
                Checkbox("Install Docker Engine", value=self.config_manager.get_value("install_docker_engine", True), id="step_docker_engine"),
                Checkbox("Install Docker Compose", value=self.config_manager.get_value("install_docker_compose", True), id="step_docker_compose"),
                Checkbox("Install Additional Tools", value=self.config_manager.get_value("install_additional_tools", True), id="step_additional_tools"),
                Checkbox("Setup Docker Service", value=self.config_manager.get_value("setup_service", True), id="step_service"),
                Checkbox("Add User to Docker Group", value=self.config_manager.get_value("add_user_to_docker_group", True), id="step_group"),
                Checkbox("Verify Installation", value=self.config_manager.get_value("verify_installation", True), id="step_verify"),
            ),
            
            Horizontal(
                Button("Configure", variant="default", id="configure"),
                Button("Install", variant="success", id="install"),
                Button("Docker Hub", variant="primary", id="docker_hub"),
                Button("Exit", variant="error", id="exit"),
                id="main_buttons"
            ),
            
            id="main_layout"
        )
        yield Footer()
    
    @on(Button.Pressed, "#configure")
    def configure_settings(self):
        """Open the configuration screen."""
        self.push_screen(ConfigScreen(self.config_manager))
    
    @on(Button.Pressed, "#install")
    def on_install_pressed(self):
        """Begin the installation process."""
        # Determine which steps to run based on checkboxes
        steps = []
        if self.query_one("#step_prerequisites").value:
            steps.append("prerequisites")
        if self.query_one("#step_docker_engine").value:
            steps.append("docker")
        if self.query_one("#step_docker_compose").value:
            steps.append("compose")
        if self.query_one("#step_additional_tools").value:
            steps.append("tools")
        if self.query_one("#step_service").value:
            steps.append("service")
        if self.query_one("#step_group").value:
            steps.append("group")
        if self.query_one("#step_verify").value:
            steps.append("verify")
        
        if not steps:
            self.notify("Please select at least one installation step.", severity="warning")
            return
        
        # Start installation in a separate thread
        self.push_screen(ProgressScreen(self.config_manager))
        
        # Run the actual installation
        self.start_installation(steps)
    
    @work(thread=True)
    def run_installation(self, steps: List[str]):
        """Run the actual installation in a background thread."""
        progress_screen = self.query_one(ProgressScreen)
        
        # Create a custom logger that updates the UI
        class TuiLogger:
            def __init__(self, update_func):
                self.update_func = update_func
            
            def info(self, message: str) -> None:
                self.update_func(f"[INFO] {message}")
            
            def error(self, message: str) -> None:
                self.update_func(f"[ERROR] {message}")
            
            def warning(self, message: str) -> None:
                self.update_func(f"[WARNING] {message}")
        
        def update_log(message: str):
            # Use call_from_thread to safely update the UI from the worker thread
            self.call_from_thread(progress_screen.update_log, message)
        
        tui_logger = TuiLogger(update_log)
        
        try:
            # Create the Docker installer with the current configuration
            installer = DockerInstaller(tui_logger, self.config_manager)
            
            # Import the orchestrator and run the installation
            from DockerInstaller import DockerInstallationOrchestrator
            orchestrator = DockerInstallationOrchestrator(installer, tui_logger)
            
            # Run the installation
            success = orchestrator.run_installation(steps)
            
            # Update UI with final status
            if success:
                self.call_from_thread(self.notify, "Docker installation completed successfully!", timeout=10)
                self.call_from_thread(lambda: self.query_one(ProgressScreen).update_log("Docker installation completed successfully!"))
                self.call_from_thread(lambda: self.query_one(ProgressScreen).update_status("Installation completed successfully!"))
            else:
                self.call_from_thread(self.notify, "Docker installation failed!", severity="error", timeout=10)
                self.call_from_thread(lambda: self.query_one(ProgressScreen).update_log("Docker installation failed!"))
                self.call_from_thread(lambda: self.query_one(ProgressScreen).update_status("Installation failed!"))
                
        except Exception as e:
            self.call_from_thread(self.notify, f"Installation failed: {str(e)}", severity="error", timeout=10)
            self.call_from_thread(lambda: self.query_one(ProgressScreen).update_log(f"Error during installation: {str(e)}"))
            self.call_from_thread(lambda: self.query_one(ProgressScreen).update_status("Installation failed!"))
    
    def start_installation(self, steps: List[str]):
        """Start the installation process."""
        progress_screen = self.query_one(ProgressScreen)
        progress_screen.update_log("Starting Docker installation...")
        
        # Run the installation in the background
        self.run_installation(steps)
    
    @on(Button.Pressed, "#docker_hub")
    def open_docker_hub(self):
        """Open the Docker Hub exploration screen."""
        self.push_screen(DockerHubScreen())
    
    @on(Button.Pressed, "#exit")
    def exit_app(self):
        """Exit the application."""
        self.exit()


def main():
    """Main entry point for the application."""
    app = InstallationApp()
    app.run()


if __name__ == "__main__":
    # Run the application
    main()
