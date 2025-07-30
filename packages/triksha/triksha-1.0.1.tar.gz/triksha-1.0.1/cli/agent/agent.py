#!/usr/bin/env python3
"""
Dravik Agent Launcher
This script launches the Dravik Agent Streamlit app
"""
import os
import sys
import json
import subprocess
import traceback
from pathlib import Path

def load_config():
    """Load configuration from .dravik/config.json in user's home directory"""
    config_dir = Path.home() / ".dravik"
    config_file = config_dir / "config.json"
    
    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                config = json.load(f)
                
                # Set API keys from config if not already in environment
                if "gemini" in config and config["gemini"] and not os.environ.get("GOOGLE_API_KEY"):
                    os.environ["GOOGLE_API_KEY"] = config["gemini"]
                    print("Loaded Gemini API key from config")
                    
                if "openai" in config and config["openai"] and not os.environ.get("OPENAI_API_KEY"):
                    os.environ["OPENAI_API_KEY"] = config["openai"]
                    print("Loaded OpenAI API key from config")
                    
                return config
        except Exception as e:
            print(f"Error loading config: {e}")
    
    return {}

def main():
    """Launch the Dravik Agent Streamlit app"""
    # Load configuration
    load_config()
    
    # Get the directory of this script
    script_dir = Path(__file__).parent.absolute()
    
    # Streamlit app file path
    app_file = script_dir / "streamlit_app.py"
    
    if not app_file.exists():
        print(f"Error: Streamlit app file not found at {app_file}")
        sys.exit(1)
    
    # Check and install required packages
    try:
        # Check if streamlit is installed
        import streamlit
        print("Streamlit is already installed.")
    except ImportError:
        print("Streamlit not found. Installing streamlit...")
        subprocess.run([sys.executable, "-m", "pip", "install", "streamlit"])
    
    try:
        # Check if google-generativeai is installed
        import google.generativeai
        print("Google Generative AI library is already installed.")
    except ImportError:
        print("Google Generative AI library not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "google-generativeai"])
    
    # Launch the Streamlit app
    print(f"Launching Dravik Agent at http://localhost:8501")
    try:
        # Find an available port starting from 8501
        port = find_available_port()
        subprocess.run(["streamlit", "run", str(app_file), "--server.port", str(port)])
    except Exception as e:
        print(f"Error running Streamlit app: {str(e)}")
        traceback.print_exc()
        print("\nTrying with Python module invocation...")
        try:
            # Alternative launch method
            subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_file)])
        except Exception as e2:
            print(f"Error with alternative launch method: {str(e2)}")
            traceback.print_exc()

def find_available_port(start_port=8501, max_attempts=10):
    """Find an available port starting from the given port"""
    import socket
    current_port = start_port
    for _ in range(max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', current_port)) != 0:
                print(f"Using port: {current_port}")
                return current_port
            current_port += 1
    print(f"No available ports found, defaulting to {start_port}")
    return start_port  # Default fallback

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Unhandled error: {str(e)}")
        traceback.print_exc()