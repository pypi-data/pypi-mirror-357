import pytest

# define some simple functions to test
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def get_api_status():
    # Simulate an API call that returns a status
    return "success"

@pytest.mark.smoke
def test_add_smoke():
    assert add(1, 1) == 2

@pytest.mark.smokedemo
def test_add_demo():
    assert add(2, 2) == 4

@pytest.mark.regression
def test_subtract_regression():
    assert subtract(5, 3) == 2

@pytest.mark.api
def test_api_status():
    status = get_api_status()
    assert status == "success"

@pytest.mark.group("demo")
def test_demo_group():
    assert add(10, 5) == 15

# trigger pytest to run this file with the following command:
# pytest -m smoke         # only run smoke marked tests
# pytest -m regression    # only run regression marked tests
# pytest -m "smoke or regression"  # run both smoke and regression
# pytest -m group         # run group marked tests