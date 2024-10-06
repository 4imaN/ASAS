#!/bin/bash

# Set the name for the virtual environment
VENV_NAME="venv"

# Create a virtual environment if it doesn't exist
if [ ! -d "$VENV_NAME" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_NAME"
fi

# Activate the virtual environment
source "$VENV_NAME/bin/activate"

# Create a simple Flask app if it doesn't exist
APP_FILE="api/v1/app"


# Start the Flask server
echo "Starting the Flask server..."
python3 -m "$APP_FILE"
