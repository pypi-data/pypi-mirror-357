import json
import os
import configparser
import re
from types import SimpleNamespace
from .parser import ini_parser, json_parser, toml_parser, yaml_parser, dotenv_parser
from .exceptions import ConfigFormatError
from .utilities import flatten_dict

class Uniconfig:
    """
    Handles application configuration management, loading, saving, and
    manipulating configuration files, and their data. This class supports
    varied configuration file formats such as YAML, INI, and dotenv, among
    others. It also facilitates hierarchical access to data and seamless
    conversion between different storage formats.

    :ivar config_path: Full path to the configuration file.
    :ivar _parser: Internal function or callable is used to load and save the
        configuration file based on its format.
    :ivar _config: The in-memory representation of the loaded configuration
        data (e.g., dictionary or ConfigParser object).
    """
    def __init__(self, config_filename="config.yaml", config_dir=None):
        """
        Initialize an instance of the configuration handler capable of loading,
        parsing, and managing configuration from a specified configuration
        file. The initialization sets up file paths, creates a parser, and
        loads configuration data, ensuring the provided file is accessible
        and in the correct format.

        :param config_filename: Name of the configuration file. Defaults to "config.yaml".
        :param config_dir: Directory path where the configuration file is located.
            If not provided, defaults to the parent directory of the script's location.
        """
        if config_dir is None:
            config_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        self.config_path = os.path.join(config_dir, config_filename)

        if not os.path.isfile(self.config_path):
            raise FileNotFoundError(f"No config file found at '{self.config_path}'")

        self._parser = self._get_parser(self.config_path)
        self._config = self._load_config()

    def _load_config(self):
        """
        Loads the configuration using the specified parser and configuration path.

        This method uses a private parser method to load the configuration
        details from the defined configuration path. It abstracts the logic for
        parsing and returns the configuration object.

        :return: The loaded configuration object returned by the parser.
        """
        return self._parser("load", self.config_path)

    def reload(self):
        """
        Reloads the configuration by fetching the updated configuration
        data, replacing any previously loaded configuration. This ensures
        that any modifications to the configuration source are correctly
        reflected in the application's runtime.

        :return: None
        """
        self._config = self._load_config()

    def has(self, key):
        """
        Checks whether a nested key or configuration path exists in the provided
        configuration instance. The method navigates through a nested dictionary
        or configparser.ConfigParser representation using the dot-separated or
        colon-separated key paths provided.

        :param key: The dot-separated or colon-separated key path to check for
            existence in the configuration.
        :return: A boolean indicating whether the key exists or not in the
            configuration.
        """
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                if k not in value:
                    return False
                value = value[k]
            elif isinstance(value, configparser.ConfigParser):
                section, option = (k.split(":", 1) if ":" in k else (k, None))
                if option and value.has_option(section, option):
                    return True
                elif value.has_section(k):
                    return True
                else:
                    return False
            else:
                return False
        return True

    def get(self, key, default=None):
        """
        Retrieve a value from a nested configuration structure using a specified key. The key
        is parsed into its hierarchical components, and each part is used to access the
        corresponding level in the configuration data. If any level does not exist, the default
        value is returned. The function supports navigating both dictionaries and lists while
        ensuring type safety and handling exceptions gracefully.

        :param key: The hierarchical key used to retrieve the value from the configuration.
        :param default: The value to be returned if the hierarchical key cannot be resolved or
            if the configuration structure is invalid. Defaults to None.
        :return: The value corresponding to the hierarchical key in the configuration, or the
            specified default value if the key cannot be resolved.
        """
        parts = self._parse_path(key)
        value = self._config
        for part in parts:
            try:
                if isinstance(value, dict) and isinstance(part, str):
                    value = value.get(part, default)
                elif isinstance(value, list) and isinstance(part, int):
                    value = value[part]
                else:
                    return default
            except (KeyError, IndexError, TypeError):
                return default
            if value is None:
                return default
        return value

    def try_get(self, key):
        """
        Attempts to retrieve the value corresponding to the provided key from the
        dictionary. If the key exists and its associated value is not None, the method
        returns a tuple with a boolean value of True and the corresponding value.
        Otherwise, it returns a tuple with a boolean value of False and None.

        :param key: The key to be searched in the dictionary.
        :return: A tuple containing a boolean indicating the presence of a valid
            value and the corresponding value or None.
        """
        val = self.get(key, default=None)
        if val is not None:
            return True, val
        return False, None

    def set(self, key, value):
        """
        Sets a value in the internal configuration storage. Allows setting values in a nested
        structure using dot-separated keys. For INI-based configurations, the key should follow
        the 'section:option' format, where the value is placed under the specified section and
        option. If the specified section does not exist, it will be created. For non-INI
        configurations, dot-separated keys will traverse the nested dictionaries, automatically
        creating intermediate dictionaries as needed.

        :param key: The key under which the value should be stored. For INI configurations,
            it should follow the 'section:option' format. For other configurations, it can
            be a dot-separated string representing nested keys.
        :param value: The value to store in the configuration under the specified key.
        :return: None
        """
        keys = key.split(".")
        cfg = self._config
        if isinstance(cfg, configparser.ConfigParser):
            # Format: section:option
            if ":" in keys[0]:
                section, option = keys[0].split(":", 1)
                if not cfg.has_section(section):
                    cfg.add_section(section)
                cfg.set(section, option, str(value))
            else:
                raise ValueError("INI keys should be in 'section:option' format")
        else:
            for k in keys[:-1]:
                cfg = cfg.setdefault(k, dict())
            cfg[keys[-1]] = value

    def delete(self, key):
        """
        Delete a configuration value based on the provided key. The key can reference
        nested configuration sections or options in configparser-like format. For
        configparser, keys must follow the 'section:option' format; otherwise, for
        other configurations, the key can reference nested dictionaries.

        :param key: The key specifying the configuration value to delete. For
                    configparser, it must be in the form 'section:option'.
        :raises ValueError: If the key for configparser is not in 'section:option' format.
        :return: None
        """
        keys = key.split(".")
        cfg = self._config
        if isinstance(cfg, configparser.ConfigParser):
            if ":" in keys[0]:
                section, option = keys[0].split(":", 1)
                if cfg.has_section(section):
                    cfg.remove_option(section, option)
            else:
                raise ValueError("INI keys should be in 'section:option' format")
        else:
            for k in keys[:-1]:
                if k not in cfg or not isinstance(cfg[k], dict):
                    return  # Nothing to delete
                cfg = cfg[k]
            cfg.pop(keys[-1], None)

    def save(self):
        """
        Parses and saves the current configuration data to the designated file path.

        This method uses an internal parser to handle the saving process. It ensures
        that the current state of the configuration is written to the specified file path
        accurately. The process includes invoking the parser with the appropriate arguments.

        :return: None
        """
        self._parser("save", self.config_path, self._config)

    def clone(self, new_path):
        """
        Clone the current instance to a new file path. This method creates a new instance
        of the same class at the specified path by saving the current instance's data
        to the new location.

        :param new_path: The file path where the cloned instance should be saved.
        :return: A new instance of the current class, initialized with the new file path.
        """
        parser = self._get_parser(new_path)
        data = self.to_dict() if hasattr(self, "to_dict") else self.data
        parser("save", new_path, data)
        new_dir, new_filename = os.path.split(new_path)
        return self.__class__(config_filename=new_filename, config_dir=new_dir)

    def as_namespace(self):
        """
        Converts a complex data structure (dictionaries and lists) to a namespace
        representation. This allows attribute-style access to keys of dictionaries
        contained in the data. Nested dictionaries and lists are also recursively
        converted to namespaces and lists of namespaces respectively.

        :raises TypeError: If `self.data` is not a list or dictionary.

        :return: The namespace representation of the data in `self.data`, where all
            dictionaries are converted to namespaces, and nested dictionaries or
            lists are recursively processed.
        """
        def to_ns(obj):
            if isinstance(obj, dict):
                return SimpleNamespace(**{k: to_ns(v) for k, v in obj.items()})
            elif isinstance(obj, list):
                return [to_ns(v) for v in obj]
            return obj

        return to_ns(self.data)

    def diff(self, other):
        """
        Compute the difference between the data of the current instance and another object.
        The method compares the nested dictionary structures of two objects and identifies
        differences.

        The comparison is done recursively for nested dictionaries. If the dictionary keys
        or their values differ between the two objects, the differences are recorded. For
        non-dictionary values, mismatches are directly recorded.

        :param other: The object to compare against. It can be either another Uniconfig
            object or a dictionary. If it is a Uniconfig object, its `data` attribute is
            used for comparison.
        :return: A dictionary capturing the differences between `self.data` and `other`.
            Each key in the returned dictionary refers to a path where differences were
            found, and the values describe the different entries in `self` and `other`.
        """
        def _diff(a, b):
            diffs = {}
            a_dict = a.data if isinstance(a, Uniconfig) else a
            b_dict = b.data if isinstance(b, Uniconfig) else b
            keys = set(a_dict.keys()).union(b_dict.keys())
            for k in keys:
                va = a_dict.get(k)
                vb = b_dict.get(k)
                if isinstance(va, dict) and isinstance(vb, dict):
                    sub_diff = _diff(va, vb)
                    if sub_diff:
                        diffs[k] = sub_diff
                elif va != vb:
                    diffs[k] = {'self': va, 'other': vb}
            return diffs

        return _diff(self.data, other)

    def update_from_dict(self, d):
        """
        Updates the internal configuration by merging it with the provided dictionary.

        This method updates the internal dictionary-based configuration by recursively
        merging the elements of the provided dictionary with the current configuration.
        If both the existing and the input values for a specific key are dictionaries,
        they will be merged recursively. For all other cases, the value from the input
        dictionary will overwrite the existing value. This method only supports
        configurations stored as dictionaries and raises a TypeError otherwise.

        :param d: A dictionary whose content is to be merged with the current
            configuration.
        :raises TypeError: Raised if the internal configuration is not
            backed by a dictionary.
        """
        def merge(a, b):
            for k, v in b.items():
                if isinstance(v, dict) and isinstance(a.get(k), dict):
                    merge(a[k], v)
                else:
                    a[k] = v

        if isinstance(self._config, dict):
            merge(self._config, d)
        else:
            raise TypeError("update_from_dict only works for dict-backed configs.")

    def as_flat_dict(self, separator="."):
        """
        Converts the nested dictionary `self.data` into a flattened dictionary. The keys in the
        returned dictionary are constructed by combining the keys from each level of the nested
        dictionary, separated by a specified separator.

        :param separator: Optional; defines the string used to separate concatenated keys in the
            flattened dictionary. Defaults to '.' if not provided.
        :type separator: str
        :return: A flattened version of `self.data` as a dictionary where nested keys are
            concatenated using the specified separator.
        :rtype: dict
        """
        return flatten_dict(self.data, separator=separator)

    def override_with_env(self, prefix=None):
        """
        Overrides the current configuration values with environment variables if they exist.

        This method traverses through all the configuration settings in a flat dictionary
        form, constructs corresponding environment variable names, and checks if they exist
        in the environment. If a matching environment variable is found, its value is
        used to override the current configuration setting. Optionally, a prefix can
        be added to the environment variable names.

        :param prefix: Optional prefix to prepend to the environment variable names.
                       Defaults to None.
        :return: None
        """
        flat = self.as_flat_dict()
        for key in flat:
            env_key = key.upper().replace('.', '_')
            if prefix:
                env_key = prefix.upper() + env_key
            if env_key in os.environ:
                self.set(key, os.environ[env_key])

    def print(self) -> None:
        """
        Prints the stored data in a formatted JSON string representation to the console.

        The method converts the `data` attribute of the class instance into a JSON string
        with an indentation of 4 spaces, making the output human-readable. It then prints
        the resulting JSON string to the standard output.

        :raises TypeError: If the object contains non-serializable data.
        :return: None
        """
        json_str = json.dumps(self.data, indent=4, ensure_ascii=False, default=str)
        print(json_str)

    @property
    def data(self):
        """
        Provides access to the data managed by the `_config` attribute. This property
        dynamically processes the `_config` attribute to return it as a dictionary
        when it is an instance of `configparser.ConfigParser`. If `_config` is not
        an instance of `configparser.ConfigParser`, it directly returns the `_config`
        attribute.

        :raises TypeError: If the `_config` object cannot be processed for some reason.

        :return: If `_config` is a `configparser.ConfigParser` instance, it returns a
            dictionary with sections as keys and their corresponding key-value pairs
            as a nested dictionary. Otherwise, it directly returns whatever value
            `_config` holds.
        """
        #if isinstance(self._config, configparser.ConfigParser):
         #   return {section: dict(self._config.items(section)) for section in self._config.sections()}
        return self._config

    @staticmethod
    def _get_parser(path):
        """
        Returns the appropriate parser based on the file extension of the provided
        file path. The function determines the file type and selects the suitable
        parser to handle its configuration format. Supported formats include YAML,
        JSON, TOML, .env, and INI. Throws a ConfigFormatError if the file format
        is unsupported.

        :param path: The file path of the configuration file.
        :return: A parser corresponding to the file extension found in the path.
        :raises ConfigFormatError: If the configuration file format is unsupported.
        """
        ext = os.path.splitext(path)[1].lower()
        if ext in (".yaml", ".yml"):
            return yaml_parser
        elif ext == ".json":
            return json_parser
        elif ext == ".toml":
            return toml_parser
        elif ext == ".env":
            return dotenv_parser
        elif ext == ".ini":
            return ini_parser
        else:
            raise ConfigFormatError(f"Unsupported config format: {ext}")

    @staticmethod
    def _parse_path(key):
        """
        Parses a given key string into a list of subkeys or indices representing the path.

        This method takes a string representation of a path to access elements in a
        nested dictionary or list structure. It splits the path into smaller components,
        identifying dictionary keys and list indices as appropriate, and returns them in
        order within a list.

        :param key: The string representation of the path. The key can include
            dictionary keys separated by dots or list indices represented in square brackets.
        :return: A list of path components extracted from the key. Dictionary keys
            remain as strings, and list indices are returned as integers.
        """
        pattern = re.compile(r'''
            ([^.[]+)      # Dict key (no dots or brackets)
            |             # OR
            \[(\d+)\]     # List index, e.g. [0]
        ''', re.VERBOSE)
        parts = []
        for segment in key.split('.'):
            matches = pattern.findall(segment)
            for m in matches:
                if m[0]:
                    parts.append(m[0])
                elif m[1]:
                    parts.append(int(m[1]))
        return parts