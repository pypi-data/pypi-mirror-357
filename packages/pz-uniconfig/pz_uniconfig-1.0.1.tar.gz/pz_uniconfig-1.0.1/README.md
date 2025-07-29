# Uniconfig

A flexible Python library for loading, editing, and saving configuration files in multiple formats—including YAML, JSON, TOML, dotenv (.env), and INI. Uniconfig provides a unified interface for working with configuration files, making it easy to manage your application's settings regardless of the underlying file format.

## Features

- **Multiple Format Support**: Works with YAML, JSON, TOML, dotenv (.env), and INI files
- **Unified API**: Read, write, and modify configuration with a single consistent API
- **Intuitive Access**: Access nested configuration values using simple dot notation
- **Type Preservation**: Maintains data types (strings, numbers, booleans, lists, dictionaries)
- **Hot Reload**: Reload configuration changes at runtime
- **Format Conversion**: Easily convert between different configuration formats
- **Environment Variable Override**: Override configuration values with environment variables
- **Advanced Features**: Compare configurations, convert to namespaces, flatten nested structures

## Installation

```bash
pip install pz-uniconfig
```

## Quick Start

```python
from pz_uniconfig import Uniconfig

# Load a configuration file
config = Uniconfig("config.yaml")

# Get values (with optional default)
database_host = config.get("database.host", "localhost")
is_debug = config.get("app.debug", False)

# Check if a key exists
if config.has("logging.level"):
    print(f"Log level: {config.get('logging.level')}")

# Set values (creates nested structures as needed)
config.set("app.version", "1.2.3")
config.set("database.credentials.username", "admin")

# Save changes
config.save()
```

## Detailed Usage

### Loading Configuration Files

Uniconfig automatically detects the file format based on the file extension:

```python
# Load different file formats
yaml_config = Uniconfig("config.yaml")
json_config = Uniconfig("config.json")
toml_config = Uniconfig("config.toml")
ini_config = Uniconfig("config.ini")
env_config = Uniconfig("config.env")

# Specify a different directory
config = Uniconfig(config_filename="config.yaml", config_dir="/path/to/config/dir")
```

### Accessing Configuration Values

```python
# Basic key access with dot notation
project_title = config.get("project.title")

# Accessing nested values
smtp_server = config.get("notifications.email.smtp_server")

# Accessing array elements
first_owner = config.get("project.owners[0].username")
first_role = config.get("project.owners[0].roles[0]")

# Using default values for non-existent keys
value = config.get("does.not.exist", "Default Value")

# Checking if keys exist
if config.has("project.title"):
    print("Project title is defined")

# Using try_get for safe access
found, value = config.try_get("project.title")
if found:
    print(f"Found value: {value}")
```

### Modifying Configuration

```python
# Setting values
config.set("maintenance_mode", True)

# Setting nested values
config.set("notifications.email.port", 587)

# Creating new nested values
config.set("new.nested.value", "This is a new nested value")

# Setting array values
config.set("metrics.providers[0]", "newrelic")

# Delete a key
config.delete("temporary.setting")
```

### Saving Changes

```python
# Save changes to the original file
config.save()

# Clone to a different file or format
json_config = config.clone("/path/to/new/config.json")
```

### Advanced Features

#### Updating from Dictionary

```python
update_dict = {
    "project": {
        "title": "Updated Project",
        "version": "2.0.0"
    },
    "api": {
        "url": "https://api.example.com/v2/"
    }
}
config.update_from_dict(update_dict)
```

#### Converting to Namespace

```python
# Convert to namespace for attribute-style access
ns = config.as_namespace()
print(ns.project.title)
print(ns.api.url)
```

#### Flattening Nested Structure

```python
# Convert nested structure to flat dictionary
flat_dict = config.as_flat_dict()
# Result: {"project.title": "My Project", "project.version": "1.0", ...}
```

#### Environment Variable Override

```python
# Override config values with environment variables
# For example, PROJECT_TITLE env var will override project.title
config.override_with_env(prefix="APP_")
```

#### Comparing Configurations

```python
# Compare two configurations
other_config = Uniconfig("other_config.yaml")
differences = config.diff(other_config)
```

#### Reloading Configuration

```python
# Reload configuration from file
config.reload()
```

## Method Reference

| Method | Description |
|--------|-------------|
| `__init__(config_filename, config_dir=None)` | Initialize with a configuration file |
| `get(key, default=None)` | Get a value by key with optional default |
| `set(key, value)` | Set a value by key (creates nested structure if needed) |
| `has(key)` | Check if a key exists |
| `try_get(key)` | Safely try to get a value, returns (found, value) |
| `delete(key)` | Delete a key from the configuration |
| `save()` | Save changes to the configuration file |
| `reload()` | Reload the configuration from the file |
| `clone(new_path)` | Clone the configuration to a new file |
| `as_namespace()` | Convert configuration to a namespace for attribute access |
| `diff(other)` | Compare with another configuration |
| `update_from_dict(d)` | Update configuration from a dictionary |
| `as_flat_dict(separator=".")` | Convert to a flat dictionary with keys separated by dots |
| `override_with_env(prefix=None)` | Override configuration with environment variables |
| `print()` | Print the configuration as formatted JSON |

## Supported File Formats

| Format | File Extensions | Description |
|--------|----------------|-------------|
| YAML | .yaml, .yml | Human-readable format with support for complex data structures |
| JSON | .json | JavaScript Object Notation, widely used for data interchange |
| TOML | .toml | Tom's Obvious, Minimal Language, designed to be easy to read |
| INI | .ini | Simple configuration format with sections and key-value pairs |
| dotenv | .env | Environment variable file format with KEY=VALUE pairs |

## Why Use Uniconfig?

Uniconfig simplifies configuration management in Python applications by providing:

1. **Format Flexibility**: Switch between configuration formats without changing your code
2. **Simplified Access**: No need to remember different APIs for different formats
3. **Nested Configuration**: Easily work with complex, nested configuration structures
4. **Type Safety**: Preserve data types across different formats
5. **Developer Experience**: Intuitive API with helpful methods for common tasks
6. **Extensibility**: Easy to add support for additional formats if needed

Whether you're building a small script or a large application, Uniconfig helps you manage your configuration in a clean, consistent way.