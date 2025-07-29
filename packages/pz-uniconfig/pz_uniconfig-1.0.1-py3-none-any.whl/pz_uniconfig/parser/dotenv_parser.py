from dotenv import dotenv_values
from ..utilities import flatten_dict, set_nested_key, serialize_config_value, parse_config_value
from ..exceptions import ConfigFormatError

def flatten_dotenv(config_dict, separator="."):
    """
    Flattens all keys in the config, no sections.
    Example: {'foo': {'bar': 1}, 'baz': 2} -> {'foo.bar': 1, 'baz': 2}
    """
    return flatten_dict(config_dict, separator)

def dotenv_parser(action, path, data=None):
    """
    Parse dotenv configuration files, providing functionality to load and save environment
    variables in a compatible format. This function relies on python-dotenv for loading and
    supports writing key-value pairs into dotenv files.

    :param action: A string indicating the action to perform. Supported actions are "load"
        to load environment variables from the specified file and "save" to save key-value
        pairs to the specified file.
    :param path: The file path of the dotenv file to read or write to.
    :param data: An optional dictionary of key-value pairs representing environment variables
        to save to the dotenv file when the action is "save".
    :return: When the action is "load", a dictionary containing the key-value pairs from the
        dotenv file is returned. No return value when the action is "save".
    :raises ConfigFormatError: If the provided action is not "load" or "save".
    """
    if action == "load":
        flat = dict(dotenv_values(dotenv_path=path, encoding="utf-8-sig"))
        nested = {}
        for k, v in flat.items():
            set_nested_key(nested, k, parse_config_value(v), sep='.')
        return nested
    elif action == "save":
        flat = flatten_dotenv(data)
        with open(path, "w", encoding="utf-8") as f:
            for k, v in flat.items():
                f.write(f"{k.upper()}={serialize_config_value(v)}\n")
        return None
    else:
        raise ConfigFormatError("Invalid dotenv parser action.")