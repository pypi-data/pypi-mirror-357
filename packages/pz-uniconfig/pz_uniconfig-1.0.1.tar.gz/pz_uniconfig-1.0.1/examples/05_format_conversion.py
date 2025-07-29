"""
Example 5: Converting Configuration to Different Formats

This example demonstrates how to convert configuration data to different formats:
- Converting to a namespace for attribute-style access
- Converting to a flat dictionary with dot notation keys
- Printing configuration as formatted JSON
"""

import os
from pz_uniconfig import Uniconfig

# Set the directory where the example config files are stored
CONFIG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "files"))

def main():
    print("UNICONFIG FORMAT CONVERSION EXAMPLE")
    print("==================================\n")
    
    # Load the YAML configuration
    config = Uniconfig(config_filename="config.yaml", config_dir=CONFIG_DIR)
    
    # Convert to namespace
    print("CONVERTING TO NAMESPACE")
    print("----------------------")
    print("Namespaces allow attribute-style access to configuration values")
    
    # Convert the configuration to a namespace
    ns = config.as_namespace()
    
    # Access values using attribute notation
    print(f"Project title (attribute access): {ns.project.title}")
    print(f"Environment (attribute access): {ns.project.environment}")
    print(f"First owner (attribute access): {ns.project.owners[0].username}")
    print(f"First owner's roles (attribute access): {ns.project.owners[0].roles}")
    
    # Demonstrate nested attribute access
    print("\nAccessing nested attributes:")
    print(f"API URL: {ns.api.main_url}")
    print(f"SMTP Server: {ns.notifications.email.smtp_server}")
    print(f"First feature name: {ns.features[0].name}")
    print()
    
    # Convert to flat dictionary
    print("CONVERTING TO FLAT DICTIONARY")
    print("----------------------------")
    print("Flat dictionaries represent nested structures with dot notation keys")
    
    # Convert the configuration to a flat dictionary with default separator (.)
    flat_dict = config.as_flat_dict()
    
    # Display some keys from the flat dictionary
    print("\nFlat dictionary with default separator (.):")
    for key in sorted(list(flat_dict.keys())[:10]):  # Show first 10 keys
        print(f"  {key}: {flat_dict[key]}")
    
    # Convert to flat dictionary with custom separator
    flat_dict_underscore = config.as_flat_dict(separator="_")
    
    # Display some keys from the flat dictionary with custom separator
    print("\nFlat dictionary with custom separator (_):")
    for key in sorted(list(flat_dict_underscore.keys())[:10]):  # Show first 10 keys
        print(f"  {key}: {flat_dict_underscore[key]}")
    
    # Demonstrate accessing values from flat dictionaries
    print("\nAccessing values from flat dictionaries:")
    print(f"Project title (flat dict): {flat_dict['project.title']}")
    print(f"First owner (flat dict): {flat_dict['project.owners[0].username']}")
    print(f"Project title (flat dict with underscore): {flat_dict_underscore['project_title']}")
    print()
    
    # Print configuration as JSON
    print("PRINTING CONFIGURATION AS JSON")
    print("-----------------------------")
    print("The print() method outputs the configuration as formatted JSON:")
    config.print()
    
    # Load different format and demonstrate conversion
    print("\nCONVERTING BETWEEN DIFFERENT FORMATS")
    print("-----------------------------------")
    
    # Load TOML configuration
    toml_config = Uniconfig(config_filename="config.toml", config_dir=CONFIG_DIR)
    
    # Convert to namespace
    toml_ns = toml_config.as_namespace()
    print("\nTOML config as namespace:")
    print(f"App name: {toml_ns.general.app_name}")
    print(f"Mode: {toml_ns.general.mode}")
    
    # Convert to flat dictionary
    toml_flat = toml_config.as_flat_dict()
    print("\nTOML config as flat dictionary:")
    for key in sorted(list(toml_flat.keys())[:10]):  # Show first 10 keys
        print(f"  {key}: {toml_flat[key]}")

if __name__ == "__main__":
    main()