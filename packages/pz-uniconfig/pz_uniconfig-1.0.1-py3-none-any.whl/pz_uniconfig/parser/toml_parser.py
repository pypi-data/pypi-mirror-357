import toml
from ..exceptions import ConfigFormatError

def toml_parser(action, path, data=None):
    """
    Parses and processes TOML configuration files based on the specified action. This
    function can either load contents from a TOML file or save data into a TOML file.
    The desired behavior is determined by the `action` parameter. If a load action is
    requested, it reads and parses the TOML file at the specified `path`. For a save
    action, it writes the provided `data` object into a file at the designated `path`.

    :param action: The action to perform, either "load" to read and parse a TOML file,
        or "save" to write data into a TOML file.
    :param path: The file path of the TOML file to either read from or save to.
    :param data: The data to be saved into the TOML file, applicable only for the
        "save" action. Defaults to None.
    :return: If the `action` is "load", returns the parsed data from the TOML file.
        If the `action` is "save", returns None.
    :raises ConfigFormatError: If the provided `action` is neither "load" nor "save".
    """
    if action == "load":
        with open(path, "r", encoding="utf-8-sig") as f:
            return toml.load(f)
    elif action == "save":
        with open(path, "w", encoding="utf-8") as f:
            toml.dump(data, f)
            return None
    else:
        raise ConfigFormatError("Invalid TOML parser action.")