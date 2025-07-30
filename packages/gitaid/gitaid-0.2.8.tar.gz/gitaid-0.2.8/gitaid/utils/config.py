# config.py

import os
import yaml

CONFIG_PATH = os.path.expanduser("~/.gitaid.yml")

def save_config(config: dict):
    """
    Save configuration to the YAML file.

    Args:
        config (dict): Configuration to save.
    """
    path = get_config_path()
    with open(path, "w") as f:
        yaml.dump(config, f)

def get_config_path():
    return CONFIG_PATH

def load_config():
    """
    Load configuration from the YAML file.

    Returns:
        dict: Configuration dictionary. Empty dict if file doesn't exist or is invalid.
    """
    path = get_config_path()
    if os.path.exists(path):
        with open(path, "r") as f:
            return yaml.safe_load(f) or {}
    return {}
