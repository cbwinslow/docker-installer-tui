#!/bin/bash

# Docker Installation Script Wrapper
# This script provides a convenient way to run the Docker installer

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/DockerInstaller.py"
CONFIG_FILE="$SCRIPT_DIR/config.json"

# Default values
STEPS=("prerequisites" "docker" "compose" "tools" "service" "group" "verify")
PASSWORD_FILE=""
LOG_LEVEL=""
HELP=false

# Function to display help
show_help() {
    echo "Docker Installation Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --steps <step1> [step2] ...    Specify installation steps to run"
    echo "                                  Available steps: prerequisites, docker, compose, tools, service, group, verify"
    echo "  --password-file <path>         Path to sudo password file (overrides config)"
    echo "  --log-level <LEVEL>            Logging level: DEBUG, INFO, WARNING, ERROR (overrides config)"
    echo "  --config <path>                Path to config file (default: config.json)"
    echo "  --help                         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                          # Install everything"
    echo "  $0 --steps prerequisites docker service     # Install only specific steps"
    echo "  $0 --log-level DEBUG                        # Install with debug logging"
    echo "  $0 --config myconfig.json                   # Use custom config file"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --steps)
            STEPS=()
            shift
            while [[ $# -gt 0 && ! "$1" =~ ^-- ]]; do
                STEPS+=("$1")
                shift
            done
            ;;
        --password-file)
            PASSWORD_FILE="$2"
            shift 2
            ;;
        --log-level)
            LOG_LEVEL="$2"
            shift 2
            ;;
        --config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        --help)
            HELP=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Show help if requested
if [ "$HELP" = true ]; then
    show_help
    exit 0
fi

# Check if Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Error: Python script not found at $PYTHON_SCRIPT"
    exit 1
fi

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Config file not found at $CONFIG_FILE"
    exit 1
fi

# If password file was provided, check if it exists
if [ -n "$PASSWORD_FILE" ] && [ ! -f "$PASSWORD_FILE" ]; then
    echo "Error: Password file not found at $PASSWORD_FILE"
    exit 1
fi

# Make sure the Python script is executable
chmod +x "$PYTHON_SCRIPT"

echo "Starting Docker installation..."
echo "Configuration file: $CONFIG_FILE"
echo "Steps to be executed: ${STEPS[*]}"

# Build command with conditional arguments
CMD_ARGS="--config $CONFIG_FILE --steps ${STEPS[*]}"

if [ -n "$PASSWORD_FILE" ]; then
    CMD_ARGS="$CMD_ARGS --password-file $PASSWORD_FILE"
    echo "Password file: $PASSWORD_FILE"
fi

if [ -n "$LOG_LEVEL" ]; then
    CMD_ARGS="$CMD_ARGS --log-level $LOG_LEVEL"
    echo "Log level: $LOG_LEVEL"
fi

echo ""

# Run the Python script with the constructed arguments
python3 "$PYTHON_SCRIPT" $CMD_ARGS

echo ""
echo "Docker installation script completed!"
echo "Note: You may need to log out and back in for group changes to take effect."