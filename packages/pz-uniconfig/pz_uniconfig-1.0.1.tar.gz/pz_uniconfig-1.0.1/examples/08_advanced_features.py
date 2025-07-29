"""
Example 8: Advanced Features

This example demonstrates some advanced features of the Uniconfig library:
- Updating configuration from a dictionary
- Cloning configurations to different formats
- Creating and working with new configuration files
- Handling non-existent files
"""

import os
import tempfile
import shutil
from pz_uniconfig import Uniconfig

# Set the directory where the example config files are stored
CONFIG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "files"))

def main():
    print("UNICONFIG ADVANCED FEATURES EXAMPLE")
    print("==================================\n")
    
    # Create a temporary directory for our examples
    with tempfile.TemporaryDirectory() as temp_dir:
        # UPDATING FROM DICTIONARY
        print("UPDATING CONFIGURATION FROM DICTIONARY")
        print("-------------------------------------")
        
        # Copy the YAML config to the temporary directory
        temp_yaml_path = os.path.join(temp_dir, "config.yaml")
        shutil.copy2(os.path.join(CONFIG_DIR, "config.yaml"), temp_yaml_path)
        
        # Load the configuration
        config = Uniconfig(config_filename="config.yaml", config_dir=temp_dir)
        
        # Display original values
        print("Original values:")
        print(f"Project title: {config.get('project.title')}")
        print(f"API URL: {config.get('api.main_url')}")
        print(f"Has custom_section: {config.has('custom_section')}")
        print()
        
        # Create a dictionary with updates
        update_dict = {
            "project": {
                "title": "Updated from Dictionary",
                "version": "2.0.0"  # Add a new nested value
            },
            "api": {
                "main_url": "https://updated-api.example.com/v2/"
            },
            "custom_section": {  # Add a completely new section
                "enabled": True,
                "options": ["option1", "option2"],
                "settings": {
                    "timeout": 30,
                    "retries": 3
                }
            }
        }
        
        # Update the configuration from the dictionary
        config.update_from_dict(update_dict)
        
        # Display updated values
        print("Values after update_from_dict:")
        print(f"Project title: {config.get('project.title')}")
        print(f"Project version: {config.get('project.version')}")
        print(f"API URL: {config.get('api.main_url')}")
        print(f"Has custom_section: {config.has('custom_section')}")
        print(f"Custom section enabled: {config.get('custom_section.enabled')}")
        print(f"Custom section options: {config.get('custom_section.options')}")
        print(f"Custom section timeout: {config.get('custom_section.settings.timeout')}")
        print()
        
        # CLONING CONFIGURATIONS
        print("CLONING CONFIGURATIONS TO DIFFERENT FORMATS")
        print("-----------------------------------------")
        
        # Clone to JSON format
        json_path = os.path.join(temp_dir, "cloned.json")
        json_config = config.clone(json_path)
        
        print(f"Configuration cloned to JSON: {json_path}")
        print(f"JSON config - Project title: {json_config.get('project.title')}")
        
        # Clone to TOML format
        toml_path = os.path.join(temp_dir, "cloned.toml")
        toml_config = config.clone(toml_path)
        
        print(f"Configuration cloned to TOML: {toml_path}")
        print(f"TOML config - Project title: {toml_config.get('project.title')}")
        
        # Clone to YAML format
        yaml_path = os.path.join(temp_dir, "cloned.yaml")
        yaml_config = config.clone(yaml_path)
        
        print(f"Configuration cloned to YAML: {yaml_path}")
        print(f"YAML config - Project title: {yaml_config.get('project.title')}")
        print()
        
        # CREATING NEW CONFIGURATION FILES
        print("CREATING NEW CONFIGURATION FILES")
        print("-------------------------------")
        
        # Create a new configuration file that doesn't exist yet
        new_config_path = os.path.join(temp_dir, "new_config.yaml")
        open(new_config_path, 'w').close()
        new_config = Uniconfig(config_filename="new_config.yaml", config_dir=temp_dir)
        
        # Set some values in the new configuration
        new_config.set('app.name', "New Application")
        new_config.set('app.version', "1.0.0")
        new_config.set('app.debug', True)
        new_config.set('database.host', "localhost")
        new_config.set('database.port', 5432)
        new_config.set('database.username', "admin")
        
        # Save the new configuration
        new_config.save()
        
        print(f"New configuration created: {new_config_path}")
        print(f"App name: {new_config.get('app.name')}")
        print(f"App version: {new_config.get('app.version')}")
        print(f"Database host: {new_config.get('database.host')}")
        print()
        
        # Reload to verify the file was created correctly
        new_config.reload()
        print("Configuration reloaded from file:")
        print(f"App name: {new_config.get('app.name')}")
        print(f"App version: {new_config.get('app.version')}")
        print(f"Database host: {new_config.get('database.host')}")
        print()
        
        # HANDLING DIFFERENT DATA TYPES
        print("HANDLING DIFFERENT DATA TYPES")
        print("---------------------------")
        
        # Set values of different types
        new_config.set('types.string', "This is a string")
        new_config.set('types.integer', 42)
        new_config.set('types.float', 3.14159)
        new_config.set('types.boolean', True)
        new_config.set('types.list', [1, 2, 3, 4, 5])
        new_config.set('types.dict', {"key1": "value1", "key2": "value2"})
        
        # Save and reload
        new_config.save()
        new_config.reload()
        
        # Display values with their types
        print("Values with different data types:")
        print(f"String: {new_config.get('types.string')} (type: {type(new_config.get('types.string')).__name__})")
        print(f"Integer: {new_config.get('types.integer')} (type: {type(new_config.get('types.integer')).__name__})")
        print(f"Float: {new_config.get('types.float')} (type: {type(new_config.get('types.float')).__name__})")
        print(f"Boolean: {new_config.get('types.boolean')} (type: {type(new_config.get('types.boolean')).__name__})")
        print(f"List: {new_config.get('types.list')} (type: {type(new_config.get('types.list')).__name__})")
        print(f"Dict: {new_config.get('types.dict')} (type: {type(new_config.get('types.dict')).__name__})")

if __name__ == "__main__":
    main()