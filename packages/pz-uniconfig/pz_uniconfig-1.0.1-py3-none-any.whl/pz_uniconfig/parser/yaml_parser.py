import yaml
from collections.abc import Mapping
from ..exceptions import ConfigFormatError

def convert_to_serializable(obj):
    """Convert non-serializable objects to serializable types."""
    if isinstance(obj, Mapping):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(item) for item in obj]
    elif hasattr(obj, "__dict__"):  # Handle custom objects
        return convert_to_serializable(obj.__dict__)
    return obj  # Assume basic types like int, str, etc.


def yaml_parser(action, path, data=None):
    """
    Parses YAML files based on the specified action. This function provides the ability to load
    data from a YAML file or save data to a YAML file. It ensures proper handling of file operations
    with encoding support and safety mechanisms for YAML processing. The function supports two specific
    actions: 'load' for reading from a YAML file and 'save' for writing data onto a YAML file.

    :param action: The operation to perform, either 'load' or 'save'.
    :param path: The file path to read from or write to.
    :param data: The data to save to the YAML file. Required only for the 'save' action.
    :return: For the 'load' action, it returns the parsed YAML content as a dictionary. For the 'save'
             action, it returns None.
    :raises ConfigFormatError: If an invalid action is provided.
    """
    if action == "load":
        with open(path, "r", encoding="utf-8-sig") as f:
            return yaml.load(f, Loader=yaml.FullLoader) or {}
    elif action == "save":
        with open(path, "w", encoding="utf-8") as f:
            serializable_data = convert_to_serializable(data)
            yaml.safe_dump(serializable_data, f, allow_unicode=True)
            return None
    else:
        raise ConfigFormatError("Invalid YAML parser action.")