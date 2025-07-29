import os
import json
import yaml
from utils.settings_loader import ConfigLoader

def test_load_config_json():
    test_file = "test_config.json"
    data = {"a": {"b": 123}, "x": 1}
    with open(test_file, "w", encoding="utf-8") as f:
        json.dump(data, f)
    config = ConfigLoader.load_config(test_file)
    assert isinstance(config, dict)
    assert config["a"]["b"] == 123
    os.remove(test_file)

def test_load_config_yaml():
    test_file = "test_config.yaml"
    data = {"foo": {"bar": "baz"}}
    with open(test_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)
    config = ConfigLoader.load_config(test_file)
    assert isinstance(config, dict)
    assert config["foo"]["bar"] == "baz"
    os.remove(test_file)

def test_get_value_dict():
    config = {"outer": {"inner": "value"}}
    assert ConfigLoader.get_value(config, "outer.inner") == "value"
    assert ConfigLoader.get_value(config, "outer.not_exist") is None  

def test_load_config_ini_and_get_value():
    test_file = "test_config.ini"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("[section1]\nkey1=value1\n")
    config = ConfigLoader.load_config(test_file)
    assert ConfigLoader.get_value(config, "key1", section="section1") == "value1"
    assert ConfigLoader.get_value(config, "not_exist", section="section1") is None 
    os.remove(test_file)