"""
Example 2: Getting and Setting Configuration Values

This example demonstrates how to get and set configuration values using the Uniconfig library.
It shows different ways to access configuration data, including:
- Basic key access with dot notation
- Accessing nested values
- Accessing array elements
- Setting new values
- Checking if keys exist
- Using default values
"""

import os
from pz_uniconfig import Uniconfig

# Set the directory where the example config files are stored
CONFIG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "files"))

def main():
    print("UNICONFIG GET/SET VALUES EXAMPLE")
    print("================================\n")
    
    # Create a temporary copy of the YAML config to modify
    yaml_config = Uniconfig(config_filename="config.yaml", config_dir=CONFIG_DIR)
    
    print("GETTING VALUES")
    print("--------------")
    
    # Basic key access with dot notation
    print(f"Project title: {yaml_config.get('project.title')}")
    
    # Accessing nested values
    print(f"SMTP server: {yaml_config.get('notifications.email.smtp_server')}")
    
    # Accessing array elements
    print(f"First owner: {yaml_config.get('project.owners[0].username')}")
    print(f"Second owner: {yaml_config.get('project.owners[1].username')}")
    
    # Accessing array elements with nested properties
    print(f"First owner's roles: {yaml_config.get('project.owners[0].roles')}")
    print(f"First owner's first role: {yaml_config.get('project.owners[0].roles[0]')}")
    
    # Using default values for non-existent keys
    print(f"Non-existent key: {yaml_config.get('does.not.exist', 'Default Value')}")
    
    # Checking if keys exist
    print(f"Does 'project.title' exist? {yaml_config.has('project.title')}")
    print(f"Does 'does.not.exist' exist? {yaml_config.has('does.not.exist')}")
    
    # Using try_get for safe access
    found, value = yaml_config.try_get('project.title')
    print(f"try_get 'project.title': Found={found}, Value={value}")
    
    found, value = yaml_config.try_get('does.not.exist')
    print(f"try_get 'does.not.exist': Found={found}, Value={value}")
    
    print("\nSETTING VALUES")
    print("--------------")
    
    # Setting values
    print("Original maintenance mode:", yaml_config.get('maintenance_mode'))
    yaml_config.set('maintenance_mode', True)
    print("After setting maintenance mode:", yaml_config.get('maintenance_mode'))
    
    # Setting nested values
    print("Original SMTP port:", yaml_config.get('notifications.email.port'))
    yaml_config.set('notifications.email.port', 587)
    print("After setting SMTP port:", yaml_config.get('notifications.email.port'))
    
    # Creating new nested values
    yaml_config.set('new.nested.value', "This is a new nested value")
    print("New nested value:", yaml_config.get('new.nested.value'))
    
    # Setting array values
    yaml_config.set('metrics.providers[0]', "newrelic")
    print("Updated metrics providers:", yaml_config.get('metrics.providers'))
    
    print("\nNote: Changes made in this example are not saved to the original file.")
    print("To save changes, use the save() method as shown in the saving example.")

if __name__ == "__main__":
    main()