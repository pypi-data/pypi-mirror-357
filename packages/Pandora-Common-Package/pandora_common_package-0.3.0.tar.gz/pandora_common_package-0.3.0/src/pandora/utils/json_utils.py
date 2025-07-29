# utility/json_utils.py

import json
import os
from typing import Any, Dict, Optional


class JsonUtils:
    """Utility functions for reading, writing, updating, and validating JSON data."""

    @staticmethod
    def read_json_file(file_path, log_error=False):
        """
        Read JSON data from a file.

        Args:
            file_path: str, path to the JSON file.
            log_error: bool, print error message if reading fails.

        Returns:
            dict or list if successful, None otherwise.
        """
        if not os.path.exists(file_path):
            if log_error:
                print(f"[JsonUtils] File not found: {file_path}")
            return None
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            if log_error:
                print(f"[JsonUtils] Failed to read JSON from {file_path}: {e}")
            return None

    @staticmethod
    def write_json_file(file_path, data, indent=4):
        """
        Write a dictionary or list to a JSON file.

        Args:
            file_path: str, path to the JSON file.
            data: dict or list, data to write.
            indent: int, number of spaces for indentation.

        Returns:
            None
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)

    @staticmethod
    def update_json_file_keys(file_path, updates):
        """
        Update top-level keys in a JSON file.

        Args:
            file_path: str, path to the JSON file.
            updates: dict, key-value pairs to update at the top level.

        Returns:
            None
        """
        data = JsonUtils.read_json_file(file_path)
        if not isinstance(data, dict):
            raise ValueError("JSON root must be a dictionary for update.")
        data.update(updates)
        JsonUtils.write_json_file(file_path, data)

    @staticmethod
    def set_json_nested_key(data, key_path, value):
        """
        Set the value of a nested key in a dictionary using a dotted key path.

        Args:
            data: dict, dictionary to update.
            key_path: str, dotted path to the nested key (e.g., 'a.b.c').
            value: any, value to set at the nested key.

        Returns:
            dict, the updated dictionary.
        """
        keys = key_path.split('.')
        d = data
        for k in keys[:-1]:
            d = d.setdefault(k, {})
        d[keys[-1]] = value
        return data

    @staticmethod
    def update_json_file_nested_key(file_path, key_path, value):
        """
        Update a nested key in a JSON file using a dotted key path.

        Args:
            file_path: str, path to the JSON file.
            key_path: str, dotted path to the nested key (e.g., 'a.b.c').
            value: any, value to set at the nested key.

        Returns:
            None
        """
        data = JsonUtils.read_json_file(file_path)
        if not isinstance(data, dict):
            raise ValueError("JSON root must be a dictionary for nested update.")
        JsonUtils.set_json_nested_key(data, key_path, value)
        JsonUtils.write_json_file(file_path, data)

    @staticmethod
    def json_string_to_dict(json_str):
        """
        Convert a JSON string to a Python dictionary.

        Args:
            json_str: str, JSON string to convert.

        Returns:
            dict, parsed dictionary from the JSON string.
        """
        return json.loads(json_str)

    @staticmethod
    def dict_to_json_string(data, indent=2):
        """
        Convert a dictionary or list to a JSON string.

        Args:
            data: dict or list, data to convert.
            indent: int, number of spaces for indentation.

        Returns:
            str, JSON string representation of the data.
        """
        return json.dumps(data, indent=indent, ensure_ascii=False)

    @staticmethod
    def has_json_nested_key(data, key_path):
        """
        Check if a nested key exists in a dictionary.

        Args:
            data: dict, dictionary to check.
            key_path: str, dotted path to the nested key (e.g., 'a.b.c').

        Returns:
            bool, True if the nested key exists, False otherwise.
        """
        keys = key_path.split('.')
        for k in keys:
            if isinstance(data, dict) and k in data:
                data = data[k]
            else:
                return False
        return True

