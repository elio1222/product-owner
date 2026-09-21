from pathlib import Path
import json

def get_config() -> dict:
    config_path = Path(".po/config.json")

    with open(config_path, "r") as file:
        config = json.load(file)

    return config