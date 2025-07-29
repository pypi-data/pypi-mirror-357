import json
from ..exceptions import ConfigFormatError

def json_parser(action, path, data=None):
    """
    Handles JSON file operations for loading or saving data based on the specified action.

    This function provides a utility to either load data from a JSON file
    or save data to a JSON file, determined by the `action` parameter.
    If the specified action is "load", the function reads and parses JSON
    data from the file at the given path. If the action is "save", it
    writes the provided data to a JSON file at the given path.

    :param action: The action to be performed. Must be either "load" or "save".
    :param path: The file path to the JSON file.
    :param data: The data to be saved to a JSON file when the action is "save".
        Optional; defaults to None.
    :return: For the "load" action, returns the parsed JSON content.
        For the "save" action, returns None.
    :raises ConfigFormatError: If the `action` parameter is not "load" or "save".
    """
    if action == "load":
        with open(path, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    elif action == "save":
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            return None
    else:
        raise ConfigFormatError("Invalid JSON parser action.")