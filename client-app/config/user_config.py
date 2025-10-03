import os
import json

# Load the config and read its values into a dict
def load_config():
    try:
        with open("config/config.json", "r") as config_json:
            config = json.load(config_json)
            return config
    except FileNotFoundError:
        config_starter = {
            "server_ip": None,
            "target_dirs": [],
            "backup_frequency": None
        }    
        with open("config/config.json", "w") as config_json:
            json.dump(config_starter, config_json, indent=2)
            return config_starter

def update_config(config):
    with open("config/config.json", "w") as config_json:
        json.dump(config, config_json, indent=2)
    

