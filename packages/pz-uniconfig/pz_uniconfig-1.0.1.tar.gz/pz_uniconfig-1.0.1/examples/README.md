# Uniconfig Examples

This directory contains example scripts that demonstrate how to use the Uniconfig library for configuration management. Each example focuses on specific features of the library and provides clear, documented code to help you understand how to use Uniconfig in your own projects.

## Running the Examples

To run any example, make sure you have the Uniconfig library installed, then execute the Python script from the command line:

```bash
python examples/01_basic_loading.py
```

## Example Scripts

Here's an overview of the example scripts provided:

### 1. Basic Configuration Loading (`01_basic_loading.py`)

Demonstrates how to load configuration files in different formats (YAML, TOML, JSON, INI, ENV) and access basic information.

### 2. Getting and Setting Values (`02_get_set_values.py`)

Shows different ways to access and modify configuration data, including:
- Basic key access with dot notation
- Accessing nested values
- Accessing array elements
- Setting new values
- Checking if keys exist
- Using default values

### 3. Saving Configuration Changes (`03_save_changes.py`)

Demonstrates how to save changes made to a configuration file, including:
- Loading a configuration
- Modifying values
- Saving changes to the original file
- Saving changes to a new file
- Reloading configuration from file

### 4. Deleting Configuration Keys (`04_delete_keys.py`)

Shows how to delete keys from a configuration, including:
- Deleting top-level keys
- Deleting nested keys
- Deleting array elements
- Checking if keys exist before and after deletion

### 5. Format Conversion (`05_format_conversion.py`)

Demonstrates how to convert configuration data to different formats:
- Converting to a namespace for attribute-style access
- Converting to a flat dictionary with dot notation keys
- Printing configuration as formatted JSON

### 6. Comparing Configurations (`06_comparing_configs.py`)

Shows how to compare two different configurations and identify the differences between them using the diff() method.

### 7. Environment Variable Override (`07_env_override.py`)

Demonstrates how to override configuration values using environment variables, including:
- Basic environment variable overrides
- Using a prefix for environment variables
- How environment variables are mapped to configuration keys

### 8. Advanced Features (`08_advanced_features.py`)

Covers some advanced features of the Uniconfig library:
- Updating configuration from a dictionary
- Cloning configurations to different formats
- Creating and working with new configuration files
- Handling different data types

## Example Configuration Files

The `files` directory contains example configuration files in different formats (YAML, TOML, JSON, INI, ENV) that are used by the example scripts.

## Next Steps

After exploring these examples, you should have a good understanding of how to use the Uniconfig library in your own projects. For more detailed information, refer to the library's documentation.