import json
import os

CONFIG_DIR = "configs/"
DEFAULT_MODEL = "bitaxe_gamma"
DEFAULT_CONFIG_FILE = os.path.join(CONFIG_DIR, f"{DEFAULT_MODEL}.json")

def load_config(model=DEFAULT_MODEL):
    """Load configuration settings for a specific Bitaxe model."""
    config_file = os.path.join(CONFIG_DIR, f"{model}.json")

    if not os.path.exists(config_file):
        print(f"Config file {config_file} not found!")

    try:
        with open(config_file, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        print(f"Config file {config_file} is corrupted!")
        return()

def save_config(config, model=DEFAULT_MODEL):
    """Save configuration settings for a specific Bitaxe model."""
    config_file = os.path.join(CONFIG_DIR, f"{model}.json")
    with open(config_file, "w") as file:
        json.dump(config, file, indent=4)

