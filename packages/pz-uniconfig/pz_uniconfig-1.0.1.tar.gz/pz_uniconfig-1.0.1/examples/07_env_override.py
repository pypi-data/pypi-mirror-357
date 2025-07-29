"""
Example 7: Overriding Configuration with Environment Variables

This example demonstrates how to override configuration values using environment variables.
It shows:
- Basic environment variable overrides
- Using a prefix for environment variables
- How environment variables are mapped to configuration keys
"""

import os
import tempfile
import shutil
from pz_uniconfig import Uniconfig

# Set the directory where the example config files are stored
CONFIG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "files"))

def main():
    print("UNICONFIG ENVIRONMENT VARIABLE OVERRIDE EXAMPLE")
    print("=============================================\n")
    
    # Create a temporary directory to avoid modifying the original files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Copy the YAML config to the temporary directory
        temp_yaml_path = os.path.join(temp_dir, "config.yaml")
        shutil.copy2(os.path.join(CONFIG_DIR, "config.yaml"), temp_yaml_path)
        
        # Load the configuration
        config = Uniconfig(config_filename="config.yaml", config_dir=temp_dir)
        
        # Display original values
        print("ORIGINAL VALUES")
        print("---------------")
        print(f"Project title: {config.get('project.title')}")
        print(f"Environment: {config.get('project.environment')}")
        print(f"API URL: {config.get('api.main_url')}")
        print(f"Maintenance mode: {config.get('maintenance_mode')}")
        print()
        
        # Set environment variables to override configuration
        print("SETTING ENVIRONMENT VARIABLES")
        print("----------------------------")
        os.environ["PROJECT_TITLE"] = "Environment Override Title"
        os.environ["PROJECT_ENVIRONMENT"] = "testing"
        os.environ["API_MAIN_URL"] = "https://test-api.example.com/v2/"
        os.environ["MAINTENANCE_MODE"] = "true"
        
        print("Environment variables set:")
        print("  PROJECT_TITLE=Environment Override Title")
        print("  PROJECT_ENVIRONMENT=testing")
        print("  API_MAIN_URL=https://test-api.example.com/v2/")
        print("  MAINTENANCE_MODE=true")
        print()
        
        # Apply environment variable overrides
        print("APPLYING ENVIRONMENT VARIABLE OVERRIDES")
        print("--------------------------------------")
        config.override_with_env()
        
        # Display overridden values
        print("Values after environment override:")
        print(f"Project title: {config.get('project.title')}")
        print(f"Environment: {config.get('project.environment')}")
        print(f"API URL: {config.get('api.main_url')}")
        print(f"Maintenance mode: {config.get('maintenance_mode')}")
        print()
        
        # Reset environment variables
        del os.environ["PROJECT_TITLE"]
        del os.environ["PROJECT_ENVIRONMENT"]
        del os.environ["API_MAIN_URL"]
        del os.environ["MAINTENANCE_MODE"]
        
        # Reload the configuration to reset values
        config.reload()
        
        # Using a prefix for environment variables
        print("USING A PREFIX FOR ENVIRONMENT VARIABLES")
        print("---------------------------------------")
        os.environ["MYAPP_PROJECT_TITLE"] = "Prefixed Override Title"
        os.environ["MYAPP_PROJECT_ENVIRONMENT"] = "staging"
        os.environ["MYAPP_API_MAIN_URL"] = "https://staging-api.example.com/v1/"
        
        print("Environment variables with prefix set:")
        print("  MYAPP_PROJECT_TITLE=Prefixed Override Title")
        print("  MYAPP_PROJECT_ENVIRONMENT=staging")
        print("  MYAPP_API_MAIN_URL=https://staging-api.example.com/v1/")
        print()
        
        # Apply environment variable overrides with prefix
        config.override_with_env(prefix="MYAPP_")
        
        # Display overridden values
        print("Values after prefixed environment override:")
        print(f"Project title: {config.get('project.title')}")
        print(f"Environment: {config.get('project.environment')}")
        print(f"API URL: {config.get('api.main_url')}")
        print()
        
        # Reset environment variables
        del os.environ["MYAPP_PROJECT_TITLE"]
        del os.environ["MYAPP_PROJECT_ENVIRONMENT"]
        del os.environ["MYAPP_API_MAIN_URL"]
        
        print("ENVIRONMENT VARIABLE MAPPING")
        print("--------------------------")
        print("Environment variables are mapped to configuration keys as follows:")
        print("1. Configuration key dots (.) are converted to underscores (_)")
        print("2. Keys are converted to uppercase")
        print("3. Optional prefix is added")
        print()
        print("Examples:")
        print("  project.title -> PROJECT_TITLE")
        print("  api.main_url -> API_MAIN_URL")
        print("  With prefix 'MYAPP_':")
        print("  project.title -> MYAPP_PROJECT_TITLE")
        print("  api.main_url -> MYAPP_API_MAIN_URL")

if __name__ == "__main__":
    main()