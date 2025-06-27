# Anova WiFi Device Controller

Interactive Python terminal for controlling Anova WiFi devices including Precision Cookers (APC) and Precision Ovens (APO).

## Features

- Control both Anova Precision Cookers (sous vide) and Precision Ovens
- Real-time message streaming from devices
- Interactive command menu
- Support for cooking operations, temperature control, and telemetry export
- Clean terminal interface with background message collection

## Requirements

- Python 3.7 or higher
- Personal Access Token from Anova app

## Installation

### 1. Install Python

**macOS:**

```bash
# Using Homebrew (recommended)
brew install python

# Or download from python.org
# macOS usually comes with Python 3, check with:
python3 --version
```

**Windows:**

```bash
# Download from python.org and install
# Make sure to check "Add Python to PATH" during installation
```

**Linux (Ubuntu/Debian):**

```bash
sudo apt update
sudo apt install python3 python3-pip
```

### 2. Install Required Packages

**macOS (with modern Python/Homebrew):**

```bash
# Create a virtual environment (recommended)
python3 -m venv anova_env
source anova_env/bin/activate
pip install websockets

# Alternative: Install with --user flag
# python3 -m pip install --user websockets
```

**Windows/Linux:**

```bash
pip install websockets
```

### 3. Get Your Personal Access Token

1. Download the **Anova Oven app** (even if you only have a sous vide cooker)
2. Open the app and go to: **More → Developer → Personal Access Tokens**
3. Create a new token - it will start with `anova-`
4. Copy this token for use with the script

## Usage

### Running the Script

```bash
# Navigate to the script directory
cd /path/to/developer-docs

# If using virtual environment, activate it first:
source anova_env/bin/activate

# Run the script
python3 anova_interactive.py

# When done, deactivate virtual environment:
deactivate
```

### First Time Setup

1. The script will prompt for your Personal Access Token
2. Enter the token that starts with `anova-`
3. The script will discover your devices automatically
4. Select your device from the list
5. Use the interactive menu to control your device

### Menu Options

**For Precision Cookers (APC):**

1. Show message stream - View real-time device communications
2. Start sous vide cook - Begin cooking with temperature and timer
3. Stop cooking - Stop current cooking session
4. Set temperature unit - Change between Celsius/Fahrenheit
5. Export telemetry data - Download cooking data (returns an array of urls)
6. Exit

**For Precision Ovens (APO):**

1. Show message stream - View real-time device communications
2. Start sous vide cook (wet bulb) - Sous vide mode in oven
3. Start roasting (dry bulb) - Traditional roasting
4. Start steam cooking - Steam cooking with humidity control
5. Stop cooking - Stop current cooking session
6. Set temperature unit - Change between Celsius/Fahrenheit
7. Export telemetry data - Download cooking data (returns an array of urls)
8. Exit

## Troubleshooting

**"websockets module not found" (macOS):**

```bash
# Try these commands in order:
pip3 install websockets
# or
python3 -m pip install websockets
# or
python3 -m pip install --user websockets
```

**"Invalid token format":**

- Make sure your token starts with `anova-`
- Get a new token from the Anova Oven app

**"No devices found":**

- Ensure your devices are connected to WiFi
- Make sure devices are paired with your Anova account
- Try refreshing the app and generating a new token

**Connection issues:**

- Check your internet connection
- Verify your devices are online in the Anova app
- Try restarting the script

## Notes

- Keep the script running to maintain connection with your devices
- The message stream shows real-time updates from your device (temperature, status, etc.)
- All websocket communications are logged and can be viewed via option 1
- Press Ctrl+C to exit the script safely
