class ConfigFormatError(Exception):
    """
    Represents an error related to configuration formatting.

    This exception is intended to be raised when a configuration file, format,
    or related data does not conform to the expected structure or requirements.
    It allows for distinguishing configuration format errors from other types of
    exceptions in an application.
    """
    pass