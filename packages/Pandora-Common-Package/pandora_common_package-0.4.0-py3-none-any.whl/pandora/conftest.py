import configparser
import os
import sys
import time

from selenium.common import WebDriverException

from drivers import web_browser
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "integrations"))
pytest_plugins = ["pytest_html_reporter.plugin"]




def pytest_addoption(parser):
    parser.addoption("--stack", action="store", default="prod", help="stack name")
    parser.addoption("--browser", action="store", default="chrome", help="browser name")
    parser.addoption("--fuzzy-mark", action="store", default="",
                     help="Run tests with marks that fuzzy match this string")


@pytest.fixture(autouse=True)
def get_parser_config(request):
    # metric_str = request.config.getoption("--m")
    #   metric_list = [x for x in metric_str.split(',')]
    config_data = {
        # "metrics": metric_list,
        # "sample": int(request.config.getoption("--sample")),
        "stack": request.config.getoption("--stack")
    }
    return config_data


@pytest.fixture(scope="function", autouse=True)
def load_config(get_parser_config):
    config = configparser.ConfigParser()
    stack = get_parser_config.get("stack")
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", f"{stack}.ini")
    config.read(config_path)
    return {"stack": stack, "web_url": config["UI"]["web_url"]}


@pytest.fixture()
def driver(request):
    """
    Fixture that provides a WebDriver instance based on the specified browser.

    Args:
        request: pytest request object containing configuration and options.
    Yields:
        WebDriver: Instance of the WebDriver for the specified browser.

    Raises:
        ValueError: If an unsupported browser is specified.
        WebDriverException: If there is an issue initializing the WebDriver.
    """
    browser_name = request.config.getoption("browser")
    browser_name = browser_name.lower().strip()
    browser_option = None
    url = "https://www.amazon.com/"

    if browser_name == "chrome":
        browser_option = web_browser.ChromeOptions()
        browser_option.add_argument("--start-maximized")
    elif browser_name == "firefox":
        browser_option = web_browser.FirefoxOptions()
        browser_option.add_argument("--start-maximized")
    elif browser_name == "edge":
        browser_option = web_browser.EdgeOptions()
        browser_option.add_argument("--start-maximized")
    try:
        # Initialize WebDriver based on browser name
        driver = web_browser.WebBrowser.get_driver(browser_name, browser_option)
        driver.get(url)
        yield driver
        driver.quit()
    except ValueError as e:
        pytest.fail(f"Unsupported browser: {browser_name}. Error: {str(e)}")
    except WebDriverException as e:
        pytest.fail(f"Failed to initialize WebDriver: {str(e)}")

		
# This hook modifies the collected test items if --fuzzy-mark is used.
# It will only keep tests that have at least one mark containing the given substring.
def pytest_collection_modifyitems(config, items):
    fuzzy_mark = config.getoption("--fuzzy-mark")
    if fuzzy_mark:
        selected = []
        for item in items:
            for mark in item.iter_markers():
                if fuzzy_mark in mark.name:
                    selected.append(item)
                    break
        items[:] = selected

"""
Notes:
- This file enables fuzzy filtering of test marks via the --fuzzy-mark option.
- Example: pytest --fuzzy-mark=smoke will run all tests with any mark containing 'smoke'.
- This is useful if you want to run a group of similarly-named marks without listing each one.
- Standard pytest -m <mark> only supports exact or boolean-combined matches.
"""
