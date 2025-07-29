"""
Example 3: Saving Configuration Changes

This example demonstrates how to save changes made to a configuration file.
It shows how to:
- Load a configuration
- Modify values
- Save changes to the original file
- Save changes to a new file
- Reload configuration from file
"""

import os
import tempfile
import shutil
from pz_uniconfig import Uniconfig

# Set the directory where the example config files are stored
CONFIG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "files"))

def main():
    print("UNICONFIG SAVE CHANGES EXAMPLE")
    print("==============================\n")
    
    # Create a temporary directory to avoid modifying the original files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Copy the YAML config to the temporary directory
        temp_yaml_path = os.path.join(temp_dir, "config.yaml")
        shutil.copy2(os.path.join(CONFIG_DIR, "config.yaml"), temp_yaml_path)
        
        print("Working with a temporary copy of config.yaml")
        print(f"Temporary file location: {temp_yaml_path}")
        print()
        
        # Load the configuration from the temporary file
        config = Uniconfig(config_filename="config.yaml", config_dir=temp_dir)
        
        # Display original values
        print("ORIGINAL VALUES")
        print("---------------")
        print(f"Project title: {config.get('project.title')}")
        print(f"Environment: {config.get('project.environment')}")
        print(f"Maintenance mode: {config.get('maintenance_mode')}")
        print()
        
        # Modify some values
        print("MODIFYING VALUES")
        print("----------------")
        config.set('project.title', "Modified Project Title")
        config.set('project.environment', "development")
        config.set('maintenance_mode', True)
        print("Values modified in memory")
        print()
        
        # Save changes to the original file
        print("SAVING CHANGES")
        print("--------------")
        config.save()
        print("Changes saved to the temporary file")
        print()
        
        # Reload the configuration to verify changes were saved
        print("RELOADING CONFIGURATION")
        print("----------------------")
        config.reload()
        print(f"Project title after reload: {config.get('project.title')}")
        print(f"Environment after reload: {config.get('project.environment')}")
        print(f"Maintenance mode after reload: {config.get('maintenance_mode')}")
        print()
        
        # Save to a different format
        print("SAVING TO A DIFFERENT FORMAT")
        print("---------------------------")
        temp_json_path = os.path.join(temp_dir, "config.json")
        json_config = config.clone(temp_json_path)
        print(f"Configuration cloned to JSON: {temp_json_path}")
        print(f"JSON config - Project title: {json_config.get('project.title')}")
        print(f"JSON config - Environment: {json_config.get('project.environment')}")
        print(f"JSON config - Maintenance mode: {json_config.get('maintenance_mode')}")
        print()
        
        # Modify the JSON config and save
        print("MODIFYING AND SAVING JSON CONFIG")
        print("-------------------------------")
        json_config.set('project.title', "JSON Project Title")
        json_config.save()
        print("Changes saved to the JSON file")
        
        # Reload to verify
        json_config.reload()
        print(f"JSON config after reload - Project title: {json_config.get('project.title')}")
        print()
        
        print("Note: All changes were made to temporary files that will be deleted.")
        print("In a real application, you would modify and save the actual configuration files.")

if __name__ == "__main__":
    main()