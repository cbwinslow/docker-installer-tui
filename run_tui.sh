#!/bin/bash

# Script to run the Docker Installer TUI
# This script ensures requirements are installed before running the TUI

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TUI_SCRIPT="$SCRIPT_DIR/DockerInstallerTUI.py"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"

# Check if requirements are installed
if ! python3 -c "import textual" >/dev/null 2>&1; then
    echo "Textual library not found. Installing requirements..."
    if [ -f "$REQUIREMENTS_FILE" ]; then
        pip3 install -r "$REQUIREMENTS_FILE"
    else
        echo "Requirements file not found!"
        exit 1
    fi
else
    echo "Textual library is already installed."
fi

echo "Starting Docker Installer TUI..."
echo "Press Ctrl+C to exit at any time."
echo ""

# Run the TUI
python3 "$TUI_SCRIPT"