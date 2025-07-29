import os

import pytest
import responses
from utils.assertion import SoftAssert
import requests

from utils.testdata_handler import TestDataHandler, assert_all_assertions

def setup_mock_resp(status=200):
    # Setup mock response
    mock_response = {
      "foo": {
          "bar": {"name": "one"},
          "baz": {"name": "two"}
      },
      "items": [
        "item_a",
        "item_c"
      ],
      "json_list": [
        {"name": "item_1"},
        {"name": "item_2"}
      ],
      "list_with_order": [
          {"test": "aaa"},
          {"test": 111},
          {"test": "ccc"}
      ],
      "env_var": "test123"
    }

    if status == 200:
        # use responses to mock the API call
        responses.add(
            responses.GET,
            'https://api.example.com/data',
            json=mock_response,
            status=200
        )
    if status == 201:
        # use responses to mock the API call
        responses.add(
            responses.GET,
            'https://api.example.com/data',
            json={"status": "ok"},
            status=201
        )
    elif status == 400:
        responses.add(
            responses.GET,
            'https://api.example.com/data',
            json={"error": "Bad Request"},
            status=400
        )

os.environ["EXAMPLE_PARAM"]= "test123"
testcases = TestDataHandler.load_test_data("testdata/test_data_sample.yaml", "TestDataSample")

@pytest.mark.parametrize(
    "case", testcases, ids=[case["Case_Name"] for case in testcases]
)
@responses.activate
def test_data_format(case):
    setup_mock_resp(case["Status_Code"])
    resp = requests.get('https://api.example.com/data')

    result, error_msg = assert_all_assertions(case, resp)
    if case["Case_Name"] == "TestListWithOrder":
        assert not result, error_msg
    else:
        assert result, error_msg




def test_case1():
    SoftAssert.expect(1 == 2, "1 != 2")  # will fail
    assert 1 == 1
    print("1=1")
    SoftAssert.expect("a" in "b", "'a' not in 'b'")  # will fail
    SoftAssert.verify_assert()


def test_case2():
    SoftAssert.expect(True, "should be true")  # pass
    assert 1 == 1
    SoftAssert.verify_assert()
