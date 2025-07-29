import configparser
from ..utilities import flatten_dict, set_nested_key, serialize_config_value, parse_config_value
from ..exceptions import ConfigFormatError

def flatten_ini_sections(config_dict, separator="."):
    """
    Flattens nested dict for each section (top-level key).
    Returns {section: {dot_key: value}} for INI format.
    """
    result = {}
    for section, content in config_dict.items():
        if isinstance(content, dict):
            result[section] = flatten_dict(content, separator)
        elif isinstance(content, list):
            result[section] = flatten_dict({section: content}, separator)
        else:
            # Handle the rare case of a scalar at the section level
            result[section] = {section: content}
    return result

def ini_parser(action, path, data=None):
    """
    Handles loading and saving INI configuration files. It provides functionality to
    load INI files into a ConfigParser object and save ConfigParser or dictionary
    data as an INI file. The `load` action reads and parses the specified INI file,
    while the `save` action writes the provided configuration to the specified file.
    This function raises an error for unsupported actions.

    :param action: Defines the operation to perform. Either "load" to read the INI
        file or "save" to write data to the file.
    :param path: The file path pointing to the INI file to be loaded or saved.
    :param data: Optional. The Python dictionary or ConfigParser object containing
        data to be written to the file. Required only when `action="save"`.
    :return: When `action="load"`, it returns a ConfigParser object representing the
        loaded INI file. When `action="save"`, it returns None.
    :raises ConfigFormatError: If the given `action` is neither "load" nor "save".
    """
    config = configparser.ConfigParser()
    if action == "load":
        config.read(path, encoding="utf-8-sig")
        nested = {}
        for section in config.sections():
            for k, v in config.items(section):
                set_nested_key(nested.setdefault(section, {}), k, parse_config_value(v), sep='.')
        return nested
    elif action == "save":
        flat = flatten_ini_sections(data)
        for section, values in flat.items():
            if not config.has_section(section):
                config.add_section(section)
            for k, v in values.items():
                config.set(section, k, serialize_config_value(v))
        with open(path, "w", encoding="utf-8") as f:
            config.write(f)
            return None
    else:
        raise ConfigFormatError("Invalid INI parser action.")