import os
from typing import Any, get_type_hints, get_args, get_origin

__all__ = ["EnvironmentClass"]

class EnvironmentClass:
    def __init__(self):
        """
        Initialize environment variables for the class by loading values from the environment.

        If a corresponding environment variable is found, it assigns it to the class attribute
        after converting its type based on the provided type hints.
        If `python-dotenv` is installed, `.env` files are also supported for environment variable loading.

        Attributes that do not have type hints specified or do not match with available
        class variables are ignored.
        """
        try:
            from dotenv import load_dotenv

            load_dotenv()
        except ImportError:
            pass

        class_vars = {attr: getattr(self, attr) for attr in vars(self.__class__) if not attr.startswith("_")}

        type_hints = get_type_hints(self.__class__)

        for var_name, _ in class_vars.items():
            if value := os.environ.get(var_name):
                setattr(self, var_name, self._convert_type(value, type_hints[var_name]))

    @staticmethod
    def _convert_type(value: str, target_type: Any) -> Any:
        """
        Converts a string value to a specified target type.

        Supports basic types like bool, list, and dict, and can handle generic types for lists
        by parsing based on semicolons and converting elements to their respective types.
        Raises a `ValueError` if conversion fails due to incompatible types or unexpected formats.

        :param value: The string value to be converted.
        :type value: str
        :param target_type: The target type to which the value should be converted. Can be a primitive
            type, a list with generic type, or a dictionary with key-value string pairs.
        :type target_type: Any
        :return: The converted value in the specified target type.
        :rtype: Any
        :raises ValueError: If the value cannot be converted to the specified target type due to
            formatting issues or incompatible conversion rules.
        """
        try:
            if get_origin(target_type) is list:
                element_type = get_args(target_type)[0]
                return [element_type(item.strip()) for item in value.split(";") if item.strip()]

            if target_type == bool:
                return value.lower() in ("true", "1", "yes", "y", "on")
            elif target_type == list:
                return value.split(";") if value else []
            elif target_type == dict:
                return dict(item.split(":") for item in value.split(";") if ":" in item)
            else:
                return target_type(value)

        except (ValueError, TypeError) as e:
            raise ValueError(f"Could not convert '{value}' to type {target_type.__name__}: {str(e)}")