"""
Example 4: Deleting Configuration Keys

This example demonstrates how to delete keys from a configuration.
It shows how to:
- Delete top-level keys
- Delete nested keys
- Delete array elements
- Check if keys exist before and after deletion
"""

import os
import tempfile
import shutil
from pz_uniconfig import Uniconfig

# Set the directory where the example config files are stored
CONFIG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "files"))

def main():
    print("UNICONFIG DELETE KEYS EXAMPLE")
    print("============================\n")
    
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
        
        # Check if keys exist before deletion
        print("CHECKING KEYS BEFORE DELETION")
        print("----------------------------")
        print(f"Does 'maintenance_mode' exist? {config.has('maintenance_mode')}")
        print(f"Does 'notifications.email.smtp_server' exist? {config.has('notifications.email.smtp_server')}")
        print(f"Does 'metrics.providers' exist? {config.has('metrics.providers')}")
        print()
        
        # Delete a top-level key
        print("DELETING TOP-LEVEL KEY")
        print("---------------------")
        print(f"Original maintenance_mode: {config.get('maintenance_mode')}")
        config.delete('maintenance_mode')
        print(f"After deletion - Does 'maintenance_mode' exist? {config.has('maintenance_mode')}")
        print(f"After deletion - maintenance_mode value: {config.get('maintenance_mode', 'Key was deleted')}")
        print()
        
        # Delete a nested key
        print("DELETING NESTED KEY")
        print("------------------")
        print(f"Original SMTP server: {config.get('notifications.email.smtp_server')}")
        config.delete('notifications.email.smtp_server')
        print(f"After deletion - Does 'notifications.email.smtp_server' exist? {config.has('notifications.email.smtp_server')}")
        print(f"After deletion - SMTP server value: {config.get('notifications.email.smtp_server', 'Key was deleted')}")
        print(f"Parent key 'notifications.email' still exists: {config.has('notifications.email')}")
        print()
        
        # Delete a nested structure
        print("DELETING NESTED STRUCTURE")
        print("------------------------")
        print(f"Original email section exists: {config.has('notifications.email')}")
        config.delete('notifications.email')
        print(f"After deletion - Does 'notifications.email' exist? {config.has('notifications.email')}")
        print(f"Parent key 'notifications' still exists: {config.has('notifications')}")
        print()
        
        # Save changes to verify persistence
        print("SAVING AND RELOADING")
        print("-------------------")
        config.save()
        config.reload()
        print(f"After reload - Does 'maintenance_mode' exist? {config.has('maintenance_mode')}")
        print(f"After reload - Does 'notifications.email' exist? {config.has('notifications.email')}")
        print()
        
        # Working with INI files (special format)
        print("WORKING WITH INI FILES")
        print("---------------------")
        # Copy the INI config to the temporary directory
        temp_ini_path = os.path.join(temp_dir, "config.ini")
        shutil.copy2(os.path.join(CONFIG_DIR, "config.ini"), temp_ini_path)
        
        ini_config = Uniconfig(config_filename="config.ini", config_dir=temp_dir)
        print(f"Original database host: {ini_config.get('database.host')}")
        
        # For INI files, keys must be in 'section:option' format
        ini_config.delete('database:host')
        print(f"After deletion - database host: {ini_config.get('database.host', 'Key was deleted')}")
        
        print("\nNote: All changes were made to temporary files that will be deleted.")
        print("In a real application, you would modify and save the actual configuration files.")

if __name__ == "__main__":
    main()