import os
import shutil
import tempfile
import json
import glob
from io import StringIO
from unittest.mock import patch
import pytest
from pz_uniconfig import Uniconfig
from pz_uniconfig.exceptions import ConfigFormatError

EXAMPLES_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../examples/files"))

# Dynamically discover all config files in the examples/files directory
CONFIG_FILES_PATHS = glob.glob(os.path.join(EXAMPLES_PATH, "config.*"))
CONFIG_FILE_NAMES = [os.path.basename(path) for path in CONFIG_FILES_PATHS]

# Mapping of file types to their key paths and expected values
CONFIG_FILE_MAPPING = {
    "config.yaml": {"key": "project.title", "expected": "YAMLConfigTest", "set_key": "project.title", "set_value": "TestTitleYAML"},
    "config.json": {"key": "app.name", "expected": "ConfigManagerDemo", "set_key": "app.name", "set_value": "TestNameJSON"},
    "config.ini": {"key": "general.app_name", "expected": "INIDemoApp", "set_key": "general.app_name", "set_value": "TestNameINI"},
    "config.toml": {"key": "general.app_name", "expected": "TOMLTestSuite", "set_key": "general.app_name", "set_value": "TestNameTOML"},
    "config.env": {"key": "APP_NAME", "expected": "dotenv-demo", "set_key": "APP_NAME", "set_value": "TestNameENV"},
}

# Generate CONFIG_FILES list from the mapping
CONFIG_FILES = [
    (filename, mapping["key"], mapping["expected"], mapping["set_key"], mapping["set_value"])
    for filename, mapping in CONFIG_FILE_MAPPING.items()
]

# Generate all possible format conversion combinations
FORMAT_CONVERSIONS = []
for src_file in CONFIG_FILE_NAMES:
    src_ext = os.path.splitext(src_file)[1]
    for tgt_file in CONFIG_FILE_NAMES:
        tgt_ext = os.path.splitext(tgt_file)[1]
        if src_ext != tgt_ext:
            FORMAT_CONVERSIONS.append((src_file, f"converted{tgt_ext}"))

@pytest.fixture
def temp_copy(request):
    """Fixture to create a temp copy of a file and yield its path."""
    def _make_temp_copy(filename):
        orig = os.path.join(EXAMPLES_PATH, filename)
        tmp_dir = tempfile.mkdtemp()
        tmp_file = os.path.join(tmp_dir, filename)
        shutil.copy2(orig, tmp_file)
        return tmp_dir, tmp_file, filename
    yield _make_temp_copy

@pytest.mark.parametrize("config_file", CONFIG_FILE_NAMES)
def test_get_operation(config_file):
    """Test the get operation for retrieving configuration values."""
    uc = Uniconfig(config_filename=config_file, config_dir=EXAMPLES_PATH)
    key = CONFIG_FILE_MAPPING[config_file]["key"]
    expected = CONFIG_FILE_MAPPING[config_file]["expected"]
    assert uc.get(key) == expected

def test_get_with_default():
    """Test get operation with the default value for nonexistent keys."""
    uc = Uniconfig(config_filename="config.toml", config_dir=EXAMPLES_PATH)
    assert uc.get("does_not.exist", default="fallback") == "fallback"

def test_data_property():
    """Test the data property returns the correct dictionary."""
    uc = Uniconfig(config_filename="config.yaml", config_dir=EXAMPLES_PATH)
    data = uc.data
    assert isinstance(data, dict)
    assert "project" in data

@pytest.mark.parametrize("config_file", CONFIG_FILE_NAMES)
def test_has_method(temp_copy, config_file):
    """Test the has method for checking if a key exists."""
    tmp_dir, tmp_file, tmp_name = temp_copy(config_file)
    try:
        cfg = Uniconfig(config_filename=tmp_name, config_dir=tmp_dir)
        key = CONFIG_FILE_MAPPING[config_file]["key"]
        assert cfg.has(key)
        assert not cfg.has("not_a_key")
    finally:
        shutil.rmtree(tmp_dir)

@pytest.mark.parametrize("config_file", CONFIG_FILE_NAMES)
def test_try_get_method(temp_copy, config_file):
    """Test the try_get method for safely retrieving values."""
    tmp_dir, tmp_file, tmp_name = temp_copy(config_file)
    try:
        cfg = Uniconfig(config_filename=tmp_name, config_dir=tmp_dir)
        key = CONFIG_FILE_MAPPING[config_file]["key"]
        expected = CONFIG_FILE_MAPPING[config_file]["expected"]

        # Test existing key
        found, val = cfg.try_get(key)
        assert found
        assert val == expected

        # Test the non-existing key
        found, val = cfg.try_get("not_a_key")
        assert not found
        assert val is None
    finally:
        shutil.rmtree(tmp_dir)

@pytest.mark.parametrize("config_file", CONFIG_FILE_NAMES)
def test_delete_method(temp_copy, config_file):
    """Test the delete method for removing keys."""
    tmp_dir, tmp_file, tmp_name = temp_copy(config_file)
    try:
        cfg = Uniconfig(config_filename=tmp_name, config_dir=tmp_dir)
        key = CONFIG_FILE_MAPPING[config_file]["key"]

        # Verify key exists before deletion
        assert cfg.has(key)

        # Delete the key
        cfg.delete(key)

        # Verify key no longer exists
        assert not cfg.has(key)
    finally:
        shutil.rmtree(tmp_dir)

@pytest.mark.parametrize("config_file", CONFIG_FILE_NAMES)
def test_set_method(temp_copy, config_file):
    """Test the set method for setting key values."""
    tmp_dir, tmp_file, tmp_name = temp_copy(config_file)
    try:
        cfg = Uniconfig(config_filename=tmp_name, config_dir=tmp_dir)
        set_key = CONFIG_FILE_MAPPING[config_file]["set_key"]
        set_value = CONFIG_FILE_MAPPING[config_file]["set_value"]

        # Save the original value
        orig_value = cfg.get(set_key)

        # Set the new value
        cfg.set(set_key, set_value)

        # Verify new value
        assert cfg.get(set_key) == set_value

        # Restore original value
        cfg.set(set_key, orig_value)

        # Verify restoration
        assert cfg.get(set_key) == orig_value
    finally:
        shutil.rmtree(tmp_dir)

@pytest.mark.parametrize("src_fmt,tgt_fmt", [
    ("config.yaml", "config.json"),
    ("config.json", "config.toml"),
    ("config.toml", "config.env"),
    ("config.env", "config.ini")
])
def test_diff_between_configs(temp_copy, src_fmt, tgt_fmt):
    """Test the diff method to compare two config objects."""
    # Skip tests with INI files for diff operations
    if src_fmt.endswith(".ini") or tgt_fmt.endswith(".ini"):
        pytest.skip("INI format doesn't support full diff operations")

    tmp_dir, tmp_file, tmp_name = temp_copy(src_fmt)
    try:
        src_cfg = Uniconfig(config_filename=tmp_name, config_dir=tmp_dir)

        # Clone to the target format
        new_path = os.path.join(tmp_dir, tgt_fmt)
        clone_cfg = src_cfg.clone(new_path)

        # Make a change to the clone
        set_key = CONFIG_FILE_MAPPING[src_fmt]["set_key"]
        set_value = CONFIG_FILE_MAPPING[src_fmt]["set_value"]

        if tgt_fmt.endswith(".env"):
            set_key = set_key.upper().replace(".", "_")

        clone_cfg.set(set_key, set_value)

        # Get diff
        diff = src_cfg.diff(clone_cfg)
        assert diff  # Ensure the diff is not empty
    finally:
        shutil.rmtree(tmp_dir)

@pytest.mark.parametrize("config_file", [
    "config.yaml", 
    "config.json", 
    "config.toml", 
    "config.env"
])
def test_update_from_dict(temp_copy, config_file):
    """Test updating config from a dictionary."""
    # Skip INI files for update_from_dict operations
    if config_file.endswith(".ini"):
        pytest.skip("INI format doesn't support update_from_dict")

    tmp_dir, tmp_file, tmp_name = temp_copy(config_file)
    try:
        cfg = Uniconfig(config_filename=tmp_name, config_dir=tmp_dir)
        set_key = CONFIG_FILE_MAPPING[config_file]["set_key"]
        set_value = CONFIG_FILE_MAPPING[config_file]["set_value"]

        # Create the update dictionary
        if config_file.endswith(".env"):
            # For .env, we need to create a flat dict
            update_dict = {set_key: set_value}
        else:
            # Create the nested dict from dot notation
            parts = set_key.split(".")
            update_dict = {}
            current = update_dict
            for i, part in enumerate(parts):
                if i == len(parts) - 1:
                    current[part] = set_value
                else:
                    current[part] = {}
                    current = current[part]

        # Update from dict
        cfg.update_from_dict(update_dict)

        # Verify update
        assert cfg.get(set_key) == set_value
    finally:
        shutil.rmtree(tmp_dir)

@pytest.mark.parametrize("config_file", CONFIG_FILE_NAMES)
def test_as_namespace(temp_copy, config_file):
    """Test the as_namespace method for object-like access to config data."""
    tmp_dir, tmp_file, tmp_name = temp_copy(config_file)
    try:
        cfg = Uniconfig(config_filename=tmp_name, config_dir=tmp_dir)
        ns = cfg.as_namespace()

        # Test that the namespace has expected attributes
        if config_file.endswith(".yaml"):
            assert hasattr(ns, "project")
            assert hasattr(ns.project, "title")
        elif config_file.endswith(".json"):
            assert hasattr(ns, "app")
            assert hasattr(ns.app, "name")
        elif config_file.endswith(".toml") or config_file.endswith(".ini"):
            assert hasattr(ns, "general")
            assert hasattr(ns.general, "app_name")
    finally:
        shutil.rmtree(tmp_dir)

@pytest.mark.parametrize("config_file", CONFIG_FILE_NAMES)
def test_as_flat_dict_default_separator(temp_copy, config_file):
    """Test the as_flat_dict method with the default separator."""
    tmp_dir, tmp_file, tmp_name = temp_copy(config_file)
    try:
        cfg = Uniconfig(config_filename=tmp_name, config_dir=tmp_dir)
        flat = cfg.as_flat_dict()

        # Test that flat dict contains expected keys
        key = CONFIG_FILE_MAPPING[config_file]["key"]
        if not config_file.endswith(".env"):  # .env files are already flat
            assert key in flat
        else:
            assert key in flat  # For .env, the key is already in flat format
    finally:
        shutil.rmtree(tmp_dir)

@pytest.mark.parametrize("config_file", CONFIG_FILE_NAMES)
def test_as_flat_dict_custom_separator(temp_copy, config_file):
    """Test the as_flat_dict method with the custom separator."""
    tmp_dir, tmp_file, tmp_name = temp_copy(config_file)
    try:
        cfg = Uniconfig(config_filename=tmp_name, config_dir=tmp_dir)

        # Test with the custom separator (_)
        flat_underscore = cfg.as_flat_dict(separator="_")

        # Test that flat dict contains expected keys with the custom separator
        key = CONFIG_FILE_MAPPING[config_file]["key"]
        if not config_file.endswith(".env"):  # .env files are already flat
            modified_key = key.replace(".", "_")
            assert modified_key in flat_underscore
        else:
            assert key in flat_underscore  # For .env, the key is already in flat format
    finally:
        shutil.rmtree(tmp_dir)

@pytest.mark.parametrize("config_file", CONFIG_FILE_NAMES)
def test_print_method(temp_copy, config_file):
    """Test the print method for displaying config data."""
    tmp_dir, tmp_file, tmp_name = temp_copy(config_file)
    try:
        cfg = Uniconfig(config_filename=tmp_name, config_dir=tmp_dir)

        # Test print method (ensure it doesn't crash)
        with patch('sys.stdout', new=StringIO()) as fake_out:
            cfg.print()
            output = fake_out.getvalue()

            # Verify output is valid JSON and contains expected data
            output_data = json.loads(output)

            # Check for expected keys in the output
            if config_file.endswith(".yaml") or config_file.endswith(".json"):
                assert "project" in output_data or "app" in output_data
            elif config_file.endswith(".toml") or config_file.endswith(".ini"):
                assert "general" in output_data
            elif config_file.endswith(".env"):
                assert "APP_NAME" in output_data
    finally:
        shutil.rmtree(tmp_dir)

@pytest.mark.parametrize("config_file", CONFIG_FILE_NAMES)
def test_basic_environment_override(monkeypatch, temp_copy, config_file):
    """Test basic environment variable override functionality."""
    tmp_dir, tmp_file, tmp_name = temp_copy(config_file)
    try:
        cfg = Uniconfig(config_filename=tmp_name, config_dir=tmp_dir)
        key = CONFIG_FILE_MAPPING[config_file]["key"]

        # Create the environment variable name from the key
        env_var = key.upper().replace(".", "_")

        # Set environment variable
        monkeypatch.setenv(env_var, "EnvOverride")

        # Apply override
        cfg.override_with_env()

        # Verify override was applied
        assert cfg.get(key) == "EnvOverride"
    finally:
        shutil.rmtree(tmp_dir)

@pytest.mark.parametrize("config_file", CONFIG_FILE_NAMES)
def test_environment_override_with_prefix(monkeypatch, temp_copy, config_file):
    """Test environment variable override with prefix."""
    tmp_dir, tmp_file, tmp_name = temp_copy(config_file)
    try:
        cfg = Uniconfig(config_filename=tmp_name, config_dir=tmp_dir)
        key = CONFIG_FILE_MAPPING[config_file]["key"]

        # Create the environment variable name from the key with a prefix
        env_var = "MYAPP_" + key.upper().replace(".", "_")

        # Set environment variable
        monkeypatch.setenv(env_var, "PrefixOverride")

        # Apply override with prefix
        cfg.override_with_env(prefix="MYAPP_")

        # Verify override was applied
        assert cfg.get(key) == "PrefixOverride"
    finally:
        shutil.rmtree(tmp_dir)

def test_unsupported_file_format():
    """Test error handling for unsupported file formats."""
    tmp_dir = tempfile.mkdtemp()
    try:
        # Create an unsupported format file
        unsupported_path = os.path.join(tmp_dir, "config.xyz")
        with open(unsupported_path, 'w') as f:
            f.write("invalid_format: true")

        # Verify ConfigFormatError is raised
        with pytest.raises(ConfigFormatError):
            Uniconfig(config_filename="config.xyz", config_dir=tmp_dir)
    finally:
        shutil.rmtree(tmp_dir)

def test_parse_path_simple_dot_notation():
    """Test parsing simple dot notation paths."""
    uc = Uniconfig(config_filename="config.yaml", config_dir=EXAMPLES_PATH)
    assert uc._parse_path("project.title") == ["project", "title"]

def test_parse_path_array_index_notation():
    """Test parsing paths with array index notation."""
    uc = Uniconfig(config_filename="config.yaml", config_dir=EXAMPLES_PATH)
    assert uc._parse_path("project.owners[0].username") == ["project", "owners", 0, "username"]

def test_parse_path_multiple_array_indices():
    """Test parsing paths with multiple array indices."""
    uc = Uniconfig(config_filename="config.yaml", config_dir=EXAMPLES_PATH)
    assert uc._parse_path("features[0].allowed_types[1]") == ["features", 0, "allowed_types", 1]

def test_parse_path_mixed_notation():
    """Test parsing paths with mixed notation."""
    uc = Uniconfig(config_filename="config.yaml", config_dir=EXAMPLES_PATH)
    assert uc._parse_path("servers.eu-west.status") == ["servers", "eu-west", "status"]

def test_get_with_array_indices():
    """Test getting values using array indices."""
    uc = Uniconfig(config_filename="config.yaml", config_dir=EXAMPLES_PATH)
    assert uc.get("project.owners[0].username") == "poziel"
    assert uc.get("project.owners[1].username") == "bob"
    assert uc.get("project.owners[0].roles[0]") == "admin"

def test_get_with_nonexistent_array_index():
    """Test getting values with nonexistent array indices."""
    uc = Uniconfig(config_filename="config.yaml", config_dir=EXAMPLES_PATH)
    assert uc.get("project.owners[99]") is None
    assert uc.get("project.owners[99]", default="not found") == "not found"

def test_empty_config_handling():
    """Test handling of empty configuration files."""
    tmp_dir = tempfile.mkdtemp()
    try:
        # Create an empty YAML file
        empty_yaml_path = os.path.join(tmp_dir, "empty.yaml")
        with open(empty_yaml_path, 'w') as f:
            f.write("")

        # Create a Uniconfig instance with the empty file
        cfg = Uniconfig(config_filename="empty.yaml", config_dir=tmp_dir)

        # Verify data is empty but not None
        assert cfg.data == {}

        # Test setting and getting values in an initially empty config
        cfg.set("new.key", "value")
        assert cfg.get("new.key") == "value"

        # Save and reload to verify persistence
        cfg.save()
        cfg.reload()
        assert cfg.get("new.key") == "value"
    finally:
        shutil.rmtree(tmp_dir)

def test_nonexistent_file_handling():
    """Ensure Uniconfig raises FileNotFoundError for missing config files."""
    tmp_dir = tempfile.mkdtemp()
    try:
        with pytest.raises(FileNotFoundError):
            Uniconfig(config_filename="does_not_exist.yaml", config_dir=tmp_dir)
    finally:
        shutil.rmtree(tmp_dir)

def test_get_nested_structures():
    """Test accessing nested structures in config."""
    cfg = Uniconfig(config_filename="config.yaml", config_dir=EXAMPLES_PATH)
    assert cfg.get("api.retry.exceptions[0]") == "TimeoutError"

def test_set_deeply_nested_values(temp_copy):
    """Test setting deeply nested values in config."""
    tmp_dir, tmp_file, tmp_name = temp_copy("config.yaml")
    try:
        cfg = Uniconfig(config_filename=tmp_name, config_dir=tmp_dir)

        # Set a deeply nested value
        cfg.set("api.retry.new_setting.sub_setting.deep_value", "test")

        # Verify the value was set
        assert cfg.get("api.retry.new_setting.sub_setting.deep_value") == "test"

        # Save and reload to verify persistence
        cfg.save()
        cfg.reload()
        assert cfg.get("api.retry.new_setting.sub_setting.deep_value") == "test"
    finally:
        shutil.rmtree(tmp_dir)

def test_data_types_preservation_in_get():
    """Test that different data types are preserved when getting values."""
    # Create a temporary YAML file
    tmp_dir = tempfile.mkdtemp()
    try:
        # Create a YAML file with various data types
        yaml_path = os.path.join(tmp_dir, "types.yaml")
        with open(yaml_path, 'w') as f:
            f.write("string_value: test\n")
            f.write("integer_value: 42\n")
            f.write("float_value: 3.14\n")
            f.write("boolean_value: true\n")
            f.write("null_value: null\n")
            f.write("list_value: [1, 2, 3]\n")
            f.write("dict_value:\n  key: value\n")

        # Create a Uniconfig instance
        cfg = Uniconfig(config_filename="types.yaml", config_dir=tmp_dir)

        # Verify data types are preserved
        assert isinstance(cfg.get("string_value"), str)
        assert isinstance(cfg.get("integer_value"), int)
        assert isinstance(cfg.get("float_value"), float)
        assert isinstance(cfg.get("boolean_value"), bool)
        assert cfg.get("null_value") is None
        assert isinstance(cfg.get("list_value"), list)
        assert isinstance(cfg.get("dict_value"), dict)
    finally:
        shutil.rmtree(tmp_dir)

def test_data_types_preservation_in_clone():
    """Test that different data types are preserved when cloning to another format."""
    # Create a temporary YAML file
    tmp_dir = tempfile.mkdtemp()
    try:
        # Create a YAML file with various data types
        yaml_path = os.path.join(tmp_dir, "types.yaml")
        with open(yaml_path, 'w') as f:
            f.write("string_value: test\n")
            f.write("integer_value: 42\n")
            f.write("float_value: 3.14\n")
            f.write("boolean_value: true\n")
            f.write("null_value: null\n")
            f.write("list_value: [1, 2, 3]\n")
            f.write("dict_value:\n  key: value\n")

        # Create a Uniconfig instance
        cfg = Uniconfig(config_filename="types.yaml", config_dir=tmp_dir)

        # Test cloning preserves data types
        json_path = os.path.join(tmp_dir, "types.json")
        json_cfg = cfg.clone(json_path)

        assert isinstance(json_cfg.get("string_value"), str)
        assert isinstance(json_cfg.get("integer_value"), int)
        assert isinstance(json_cfg.get("float_value"), float)
        assert isinstance(json_cfg.get("boolean_value"), bool)
        assert json_cfg.get("null_value") is None
        assert isinstance(json_cfg.get("list_value"), list)
        assert isinstance(json_cfg.get("dict_value"), dict)
    finally:
        shutil.rmtree(tmp_dir)

@pytest.mark.parametrize("config_file", CONFIG_FILE_NAMES)
def test_save_and_reload(temp_copy, config_file):
    """Test saving and reloading configuration."""
    # Get the test parameters for this file type
    file_params = CONFIG_FILE_MAPPING[config_file]
    set_key = file_params["set_key"]
    set_value = file_params["set_value"]

    # Create a temporary copy of the config file
    tmp_dir, tmp_file, tmp_name = temp_copy(config_file)

    try:
        # Create config instance
        cfg = Uniconfig(config_filename=tmp_name, config_dir=tmp_dir)

        # Save the original value
        original_value = cfg.get(set_key)

        # Set the new value
        cfg.set(set_key, set_value)

        # Save and reload
        cfg.save()
        cfg.reload()

        # Verify value persists after reload
        assert cfg.get(set_key) == set_value

        # Restore original value
        cfg.set(set_key, original_value)
        cfg.save()
    finally:
        shutil.rmtree(tmp_dir)

@pytest.mark.parametrize("config_file", CONFIG_FILE_NAMES)
def test_clone_to_other_format(temp_copy, config_file):
    """Test cloning to a different format."""
    # Get the test parameters for this file type
    file_params = CONFIG_FILE_MAPPING[config_file]
    key = file_params["key"]

    # Create a temporary copy of the config file
    tmp_dir, tmp_file, tmp_name = temp_copy(config_file)

    try:
        # Create config instance
        cfg = Uniconfig(config_filename=tmp_name, config_dir=tmp_dir)

        # Find a different format for cloning
        for target_ext in [".yaml", ".json", ".toml", ".ini", ".env"]:
            if not config_file.endswith(target_ext):
                clone_path = os.path.join(tmp_dir, f"cloned{target_ext}")
                clone_cfg = cfg.clone(clone_path)

                # Verify the file was created
                assert os.path.exists(clone_path)

                # For .env target files, keys are uppercase and flattened with underscores
                if target_ext == ".env":
                    env_key = key.upper().replace(".", "_")
                    assert clone_cfg.get(env_key) is not None
                else:
                    # For other formats, the key should be preserved
                    assert clone_cfg.get(key) is not None
                break
    finally:
        shutil.rmtree(tmp_dir)