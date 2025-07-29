"""
Example 1: Basic Configuration Loading

This example demonstrates how to load configuration files in different formats
using the Uniconfig library. It shows how to initialize the Uniconfig class
with different file types (YAML, TOML, JSON, INI, ENV) and access basic information.
"""

import os
from pz_uniconfig import Uniconfig

# Set the directory where the example config files are stored
CONFIG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "files"))

def main():
    print("UNICONFIG BASIC LOADING EXAMPLE")
    print("===============================\n")
    
    # Load YAML configuration
    print("Loading YAML configuration:")
    yaml_config = Uniconfig(config_filename="config.yaml", config_dir=CONFIG_DIR)
    print(f"Project title: {yaml_config.get('project.title')}")
    print(f"Environment: {yaml_config.get('project.environment')}")
    print(f"First owner: {yaml_config.get('project.owners[0].username')}")
    print()
    
    # Load TOML configuration
    print("Loading TOML configuration:")
    toml_config = Uniconfig(config_filename="config.toml", config_dir=CONFIG_DIR)
    print(f"App name: {toml_config.get('general.app_name')}")
    print(f"Mode: {toml_config.get('general.mode')}")
    print(f"Main developer: {toml_config.get('developer.main')}")
    print()
    
    # Load JSON configuration
    print("Loading JSON configuration:")
    json_config = Uniconfig(config_filename="config.json", config_dir=CONFIG_DIR)
    print(f"App name: {json_config.get('app.name')}")
    print(f"Version: {json_config.get('app.version')}")
    print(f"Debug mode: {json_config.get('app.debug')}")
    print()
    
    # Load INI configuration
    print("Loading INI configuration:")
    ini_config = Uniconfig(config_filename="config.ini", config_dir=CONFIG_DIR)
    print(f"App name: {ini_config.get('general.app_name')}")
    print(f"Debug: {ini_config.get('general.debug')}")
    print(f"Database host: {ini_config.get('database.host')}")
    print()
    
    # Load ENV configuration
    print("Loading ENV configuration:")
    env_config = Uniconfig(config_filename="config.env", config_dir=CONFIG_DIR)
    print(f"App name: {env_config.get('APP_NAME')}")
    print(f"Environment: {env_config.get('ENVIRONMENT')}")
    print(f"Debug: {env_config.get('DEBUG')}")
    print()
    
    print("All configurations loaded successfully!")

if __name__ == "__main__":
    main()