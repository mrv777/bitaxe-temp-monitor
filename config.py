import json
import os

CONFIG_DIR = "configs/"
# DEFAULT_MODEL = "bitaxe_gamma"
# DEFAULT_CONFIG_FILE = os.path.join(CONFIG_DIR, f"{DEFAULT_MODEL}.json")

def load_config(board_version):
    """Load configuration settings for a specific Bitaxe model."""
    config_file = os.path.join(CONFIG_DIR, f"{board_version}.json")

    if not os.path.exists(config_file):
        print(f"Config file {config_file} not found!")

    try:
        with open(config_file, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        print(f"Config file {config_file} is corrupted!")
        return()

def save_config(config, board_version):
    """Save configuration settings for a specific Bitaxe model."""
    config_file = os.path.join(CONFIG_DIR, f"{board_version}.json")
    with open(config_file, "w") as file:
        json.dump(config, file, indent=4)

