import re

def flatten_dict(d, separator='.', prefix=''):
    """
    Flattens a nested dictionary or a mix of dictionaries and lists into a single-level dictionary. Keys of the
    flattened dictionary include the path from the root to the associated value, concatenated with a separator
    or indexed for lists.

    :param d: The dictionary or list to be flattened, which may contain nested dictionaries and/or lists.
    :param prefix: An optional string used to prefix keys in the flattened dictionary. Defaults to ''.
    :param separator: A string used as a separator between levels of keys. Defaults to '.'.
    :return: A dictionary with flattened keys representing paths, mapping to their corresponding values.
    """
    items = {}
    if isinstance(d, dict):
        for k, v in d.items():
            new_key = f"{prefix}{separator}{k}" if prefix else k
            items.update(flatten_dict(v, separator, new_key))
    elif isinstance(d, list):
        if any(isinstance(item, (dict, list)) for item in d):
            for idx, item in enumerate(d):
                new_key = f"{prefix}[{idx}]"
                items.update(flatten_dict(item, separator, new_key))
        else:
            items[prefix] = ','.join(str(x) for x in d)
    else:
        items[prefix] = d
    return items

def unflatten_dict(flat_dict, sep='.'):
    """
    Unflattens a dictionary where keys are flattened representations of a nested structure. The
    flattened keys use a defined separator to indicate levels in the structure. Handles keys with
    list-like indexing (e.g., "key[0]") to support lists within the nested structure. The function
    reconstructs the original nested structure of the input dictionary.

    :param flat_dict: A flat dictionary where keys are encoded to imply nesting using a separator or
        list-like indexing.
    :param sep: A string separator that is used to indicate the hierarchy in flattened keys.
    :return: A nested dictionary reconstructed from the input flat dictionary.
    """
    root = {}
    bracket_re = re.compile(r'([^\[]+)\[(\d+)\]')

    for flat_key, value in flat_dict.items():
        parts = flat_key.split(sep)
        curr = root
        for i, part in enumerate(parts):
            m = bracket_re.match(part)
            if m:
                name, idx = m.group(1), int(m.group(2))
                if name not in curr or not isinstance(curr[name], list):
                    curr[name] = []
                while len(curr[name]) <= idx:
                    curr[name].append({})
                if i == len(parts) - 1:
                    curr[name][idx] = value
                else:
                    curr = curr[name][idx]
            else:
                if i == len(parts) - 1:
                    curr[part] = value
                else:
                    if part not in curr or not isinstance(curr[part], dict):
                        curr[part] = {}
                    curr = curr[part]
    return root

def parse_config_value(val: str) -> str | list[str]:
    """
    Parses a configuration value string, which might include quoted strings or comma-separated lists,
    and returns either a cleaned string or a list of strings, depending on the delimiters present.

    This function processes the input by stripping whitespace, removing surrounding quotes if present,
    and splitting comma-separated lists while recursively parsing each list element to handle potential
    quotes around list values.

    :param val: Configuration value as a string.

    :return: Parsed configuration value as a string or a list of strings. If the input is a single
        quoted/unquoted string, it returns the stripped value. If the input is a comma-separated list,
        it returns a list of strings with each element properly parsed and stripped.
    """
    val = val.strip()
    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
        val = val[1:-1]
    if ',' in val:
        return [parse_config_value(v) for v in val.split(',')]
    return val

def set_nested_key(d, key_path, value, sep='.'):
    """
    Sets a value in a nested dictionary at the specified key path. If any of the
    keys in the path do not exist in the dictionary, they will be created.

    :param d: Dictionary in which the value is to be set.
    :param key_path: Dot-separated string or path specifying the location of the
        value in the nested dictionary
    :param value: Value to set at the specified key path
    :param sep: Separator used in the key_path string to denote nested levels
    :return: None
    """
    keys = [k.strip() for k in key_path.split(sep)]
    current = d
    for k in keys[:-1]:
        current = current.setdefault(k, {})
    current[keys[-1]] = value

def serialize_config_value(val):
    """
    Serializes a configuration value into a string format. This function converts lists into
    comma-separated strings and other values into their string representation. It is useful
    for preparing configuration parameters for storage or transmission.

    :param val: The configuration value to serialize. It may be a list or any other data type.
    :return: The serialized string representation of the configuration value.
    """
    if isinstance(val, list):
        return ','.join(str(x) for x in val)
    return str(val)