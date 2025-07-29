import os
from utils.json_utils import JsonUtils

def test_write_and_read_json_file():
    test_file = "test.json"
    data = {"a": 1, "b": {"c": 2}}
    JsonUtils.write_json_file(test_file, data)
    loaded = JsonUtils.read_json_file(test_file)
    assert loaded == data
    os.remove(test_file)

def test_update_json_file_keys():
    test_file = "test.json"
    data = {"a": 1, "b": 2}
    JsonUtils.write_json_file(test_file, data)
    JsonUtils.update_json_file_keys(test_file, {"b": 3, "c": 4})
    loaded = JsonUtils.read_json_file(test_file)
    assert loaded["b"] == 3 and loaded["c"] == 4
    os.remove(test_file)

def test_update_json_file_nested_key():
    test_file = "test.json"
    data = {"a": {"b": {"c": 1}}}
    JsonUtils.write_json_file(test_file, data)
    JsonUtils.update_json_file_nested_key(test_file, "a.b.c", 100)
    loaded = JsonUtils.read_json_file(test_file)
    assert loaded["a"]["b"]["c"] == 100
    os.remove(test_file)

def test_dict_to_json_string_and_json_string_to_dict():
    data = {"x": 1}
    json_str = JsonUtils.dict_to_json_string(data)
    parsed = JsonUtils.json_string_to_dict(json_str)
    assert parsed == data

def test_has_json_nested_key():
    data = {"a": {"b": {"c": 1}}}
    assert JsonUtils.has_json_nested_key(data, "a.b.c") is True
    assert JsonUtils.has_json_nested_key(data, "a.b.x") is False

def test_set_json_nested_key():
    data = {"a": {"b": 1}}
    updated = JsonUtils.set_json_nested_key(data, "a.c", 2)
    assert updated["a"]["c"] == 2