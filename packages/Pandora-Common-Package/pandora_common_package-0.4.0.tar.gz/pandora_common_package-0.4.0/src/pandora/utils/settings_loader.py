import json
import configparser
import os
import yaml  # pip install PyYAML
from jsonschema import validate, ValidationError  # pip install jsonschema


class ConfigLoader:
    @staticmethod
    def load_config(file_path, schema=None):
        """
        Load a configuration file (JSON, YAML, or INI). Optionally validate with a JSON Schema.

        Args:
            file_path: str, path to the configuration file.
            schema: dict, optional. JSON schema for validating JSON/YAML configs.

        Returns:
            dict for JSON/YAML, ConfigParser for INI, or None if loading fails.
        """
        if not os.path.exists(file_path):
            return None

        ext = os.path.splitext(file_path)[1].lower()

        try:
            if ext == ".json":
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            elif ext in [".yaml", ".yml"]:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
            elif ext == ".ini":
                parser = configparser.ConfigParser()
                parser.read(file_path, encoding="utf-8")
                return parser
            else:
                raise ValueError(f"Unsupported config file type: {ext}")

            if schema and isinstance(data, dict):
                validate(instance=data, schema=schema)

            return data
        except (json.JSONDecodeError, yaml.YAMLError, configparser.Error, ValidationError, OSError) as e:
            print(f"[ConfigLoader] Failed to load config: {e}")
            return None

    @staticmethod
    def get_value(config, key, section=None):
        """
        Retrieve a value from a config dict (supports nested keys with dot notation) or from a ConfigParser.

        Args:
            config: dict or ConfigParser. The loaded configuration object.
            key: str. For dict, use dot notation for nested keys; for INI, the option name.
            section: str, optional. Section name for INI files.

        Returns:
            The value if found, otherwise None.
        """
        if isinstance(config, dict):
            keys = key.split('.')
            value = config
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return None
            return value
        elif isinstance(config, configparser.ConfigParser):
            if section and config.has_section(section) and config.has_option(section, key):
                return config.get(section, key)
            return None
        else:
            return None
