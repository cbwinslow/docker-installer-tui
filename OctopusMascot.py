"""
Octopus Mascot Module for Docker Installer TUI
This module provides an animated 8-bit octopus mascot for the application.
"""
import time
import random
from datetime import datetime
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static, Label
from textual.containers import Container


class OctopusMascot(Widget):
    """An animated 8-bit octopus mascot widget."""
    
    # Reactive properties to control animation
    tentacle_state = reactive(0)  # For tentacle animation
    position_x = reactive(0)
    position_y = reactive(0)
    message = reactive("Ready to help!")
    is_waving = reactive(False)
    
    def __init__(self, initial_message: str = "Welcome to Docker Installer!", **kwargs):
        super().__init__(**kwargs)
        self.message = initial_message
        self.animation_speed = 0.5  # seconds between animation frames
        
    def compose(self) -> ComposeResult:
        """Compose the octopus widget."""
        yield Static(self.render_octopus(), id="octopus_display")
        if self.message:
            yield Label(self.message, id="octopus_message")
    
    def render_octopus(self) -> str:
        """Render the octopus with current animation state."""
        # Define different tentacle states for animation
        tentacle_sets = [
            ["\\", "|", "/"],  # State 0
            ["/", "|", "\\"],  # State 1
            ["|", "/", "|"],   # State 2
            ["|", "\\", "|"],  # State 3
        ]
        
        tentacles = tentacle_sets[self.tentacle_state % len(tentacle_sets)]
        
        # Create the octopus ASCII art with current tentacle state
        octopus = f"""    {tentacles[0]}   {tentacles[1]}   {tentacles[2]}
      \\|   |   |/
      `@._.@"@._.@'
        [   ] [   ]"""
        
        # Add position offset if needed
        if self.position_x > 0 or self.position_y > 0:
            lines = octopus.split("\n")
            # Add horizontal spacing
            if self.position_x > 0:
                lines = [" " * self.position_x + line for line in lines]
            # Add vertical spacing
            if self.position_y > 0:
                lines = ["\n"] * self.position_y + lines
            octopus = "\n".join(lines)
        
        return octopus
    
    def on_mount(self) -> None:
        """Start the animation once the widget is mounted."""
        self.set_interval(self.animation_speed, self.animate_octopus)
    
    def animate_octopus(self) -> None:
        """Animate the octopus by changing tentacle positions."""
        self.tentacle_state += 1
        # Randomly change position occasionally
        if random.random() < 0.15:  # 15% chance each frame
            # Change position with constraints to keep octopus visible
            self.position_x = random.randint(0, 40)
            self.position_y = random.randint(0, 8)
    
    def set_message(self, message: str, is_waving: bool = False) -> None:
        """Set a message for the octopus to display."""
        self.message = message
        self.is_waving = is_waving
        
        # Update the message label if it exists
        try:
            message_widget = self.query_one("#octopus_message", Label)
            message_widget.update(message)
        except:
            pass  # Widget might not be mounted yet
    
    def show_excited(self) -> None:
        """Show excited animation."""
        self.tentacle_state += 2
        self.set_message("Let's Docker this up! 🐙")
    
    def show_thinking(self) -> None:
        """Show thinking animation."""
        self.tentacle_state += 1
        self.set_message("Hmm, let me think about that...")
    
    def show_happy(self) -> None:
        """Show happy animation."""
        self.set_message("Everything looks great! 😊")
    
    def show_error(self) -> None:
        """Show error animation."""
        self.tentacle_state += 3
        self.set_message("Uh oh! Something went wrong! 🚨", is_waving=True)


class AnimatedOctopusContainer(Container):
    """A container that holds the octopus and allows it to move around the screen."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.border_title = "🐙 Octopus Assistant"
        
    def compose(self) -> ComposeResult:
        """Compose the animated octopus container."""
        yield OctopusMascot("Hello! I'm your Docker assistant! 🐙")


class BannerWithOctopus(Static):
    """A banner with animated octopus greeting."""
    
    def __init__(self, title: str = "Docker Installer TUI", **kwargs):
        super().__init__(**kwargs)
        self.title = title
    
    def compose(self) -> ComposeResult:
        """Compose the banner with octopus."""
        yield Static(self.render_banner(), id="banner_display")
    
    def render_banner(self) -> str:
        """Render the banner with octopus greeting."""
        # Get the octopus in greeting position
        greeting_octopus = self.render_greeting_octopus()
        
        # Create banner with title and octopus
        banner = f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║                           {self.title}                           ║
    ║                    The 8-bit Octopus Edition                   ║
    ║                                                              ║
    ║{greeting_octopus.center(60)}║
    ║                                                              ║
    ║         Welcome to the Docker Installation Wizard!           ║
    ║         The friendly octopus is here to help you out!        ║
    ╚══════════════════════════════════════════════════════════════╝
        """
        
        return banner
    
    def render_greeting_octopus(self) -> str:
        """Render a special greeting octopus animation."""
        # This is a special greeting animation with tentacles in a "wave" position
        return """  \\   |   /
    \\|   |   |/
    `@._.@"@._.@'
      [   ] [   ]"""


def get_octopus_fact() -> str:
    """Get a random Docker-related octopus fact."""
    facts = [
        "Fun fact: Octopuses have 3 hearts, just like Docker has 3 main components (Engine, Compose, Registry)!",
        "Did you know? An octopus has 8 arms, just like our 8-bit mascot has 8 tentacles!",
        "Octopuses are masters of adaptation - like Docker containers adapting to any environment!",
        "Octopuses can squeeze through tight spaces - like Docker containers optimizing space!",
        "Octopus intelligence rivals that of AI - just like our AI assistant feature!",
        "Octopuses are excellent at problem solving - just like Docker solves deployment problems!"
    ]
    return random.choice(facts)


def get_octopus_greeting() -> str:
    """Get a random octopus greeting."""
    greetings = [
        "Hello there, Docker fan! 🐙",
        "Ready to dive into Docker? 🏊‍♂️",
        "Welcome to the Docker depths! 🌊",
        "Let's make containers fun! 🎉",
        "Docker is better with friends! 👋",
        "Your friendly neighborhood octopus at your service! 🐙",
        "Time to Docker it up! ⏰",
        "Containers are cool, but octopuses are cooler! 🌟"
    ]
    return random.choice(greetings)


def get_octopus_tip() -> str:
    """Get a Docker tip from the octopus."""
    tips = [
        "Pro tip: Use Docker volumes for persistent data!",
        "Pro tip: Always tag your Docker images with version numbers!",
        "Pro tip: Use .dockerignore to exclude unnecessary files!",
        "Pro tip: Use docker-compose for multi-container applications!",
        "Pro tip: Keep your base images up to date for security!",
        "Pro tip: Use multi-stage builds to reduce image size!",
        "Pro tip: Use environment variables for configuration!",
        "Pro tip: Always run as non-root user in containers!"
    ]
    return random.choice(tips)