from pathlib import Path
# ...existing imports...

# Replace any hardcoded config paths with dynamic ones
DEFAULT_CONFIG_DIR = Path.home() / "dravik" / "config"
# ...existing code...

def get_config_path():
    """Get the path to the configuration file"""
    # Use Path.home() instead of hardcoded paths
    return Path.home() / "dravik" / "config" / "settings.yaml"
    
# ...existing code...