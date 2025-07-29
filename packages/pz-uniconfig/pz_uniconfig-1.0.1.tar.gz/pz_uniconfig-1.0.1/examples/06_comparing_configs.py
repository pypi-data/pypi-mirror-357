"""
Example 6: Comparing Configurations

This example demonstrates how to compare two different configurations
and identify the differences between them using the diff() method.
It shows:
- Comparing two configurations with minor differences
- Comparing configurations from different file formats
- Understanding the structure of the diff output
"""

import os
import tempfile
import shutil
from pz_uniconfig import Uniconfig

# Set the directory where the example config files are stored
CONFIG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "files"))

def main():
    print("UNICONFIG COMPARING CONFIGURATIONS EXAMPLE")
    print("========================================\n")
    
    # Create a temporary directory to avoid modifying the original files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Copy the YAML config to the temporary directory
        temp_yaml_path = os.path.join(temp_dir, "config.yaml")
        shutil.copy2(os.path.join(CONFIG_DIR, "config.yaml"), temp_yaml_path)
        
        # Load the original configuration
        original_config = Uniconfig(config_filename="config.yaml", config_dir=CONFIG_DIR)
        
        # Create a modified version of the configuration
        modified_config = Uniconfig(config_filename="config.yaml", config_dir=temp_dir)
        
        # Make some changes to the modified configuration
        modified_config.set('project.title', "Modified Project Title")
        modified_config.set('project.environment', "development")
        modified_config.set('maintenance_mode', True)
        modified_config.set('api.retry.max_attempts', 10)
        modified_config.set('new.section.value', "This is a new section")
        
        # Save the modified configuration
        modified_config.save()
        
        # Compare the original and modified configurations
        print("COMPARING ORIGINAL AND MODIFIED CONFIGURATIONS")
        print("---------------------------------------------")
        diff = original_config.diff(modified_config)
        
        # Print the differences
        print("Differences between original and modified configurations:")
        if diff:
            print_diff(diff)
        else:
            print("No differences found.")
        
        print("\nCOMPARING CONFIGURATIONS FROM DIFFERENT FILE FORMATS")
        print("--------------------------------------------------")
        
        # Load a configuration from a different format
        toml_config = Uniconfig(config_filename="config.toml", config_dir=CONFIG_DIR)
        
        # Create a modified version of the TOML configuration
        temp_toml_path = os.path.join(temp_dir, "config.toml")
        shutil.copy2(os.path.join(CONFIG_DIR, "config.toml"), temp_toml_path)
        modified_toml = Uniconfig(config_filename="config.toml", config_dir=temp_dir)
        
        # Make some changes to the modified TOML configuration
        modified_toml.set('general.app_name', "Modified App Name")
        modified_toml.set('general.mode', "development")
        modified_toml.set('service.rate_limit_per_minute', 500)
        
        # Save the modified TOML configuration
        modified_toml.save()
        
        # Compare the original and modified TOML configurations
        diff_toml = toml_config.diff(modified_toml)
        
        # Print the differences
        print("Differences between original and modified TOML configurations:")
        if diff_toml:
            print_diff(diff_toml)
        else:
            print("No differences found.")
        
        print("\nCOMPARING CONFIGURATIONS FROM COMPLETELY DIFFERENT FORMATS")
        print("--------------------------------------------------------")
        
        # Compare YAML and TOML configurations
        # Note: This will show many differences since they have different structures
        diff_formats = original_config.diff(toml_config)
        
        # Print a summary of the differences
        print("Summary of differences between YAML and TOML configurations:")
        print(f"Number of top-level keys with differences: {len(diff_formats)}")
        print("Top-level keys with differences:")
        for key in diff_formats.keys():
            print(f"  - {key}")

def print_diff(diff, prefix=""):
    """Helper function to print the diff structure in a readable format"""
    for key, value in diff.items():
        if isinstance(value, dict) and 'self' in value and 'other' in value:
            print(f"{prefix}- {key}: '{value['self']}' -> '{value['other']}'")
        elif isinstance(value, dict):
            print(f"{prefix}- {key}:")
            print_diff(value, prefix + "  ")
        else:
            print(f"{prefix}- {key}: {value}")

if __name__ == "__main__":
    main()