"""
[Web Browser Driver]

Author: [kane.huang@hp.com]
Last Modified: [kane.huang@hp.com]
TODO: [OPTIONAL todo description]
"""

import logging
import re

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class WebBrowser:
    """
    Factory class for creating WebDriver instances based on specified browser types.
    Supports Chrome, Firefox, and Edge browsers with automatic driver management using webdriver-manager.
    """

    def __init__(self, driver):
        self.driver = driver

    @staticmethod
    def get_driver(browser_name="chrome", browser_options=None):
        """
        Args:
            browser_name (str): Name of the target browser.
                Supported values: "chrome", "firefox", "edge"
            browser_options (Options): Browser-specific options/configurations.

        Return:
            WebDriver instance for the specified browser.
        """
        # Validate and normalize browser name
        if not isinstance(browser_name, str):
            raise TypeError("browser_name must be a string")

        browser_key = browser_name.lower().strip()

        # Validate supported browsers
        supported_browsers = {"chrome", "firefox", "edge"}
        if browser_key not in supported_browsers:
            raise ValueError(
                f"Unsupported browser: '{browser_name}'. "
                f"Supported values: {', '.join(supported_browsers)}"
            )

        # Create WebDriver instance with specified options
        if browser_key == "chrome":
            if (
                not isinstance(browser_options, ChromeOptions)
                and browser_options is not None
            ):
                raise TypeError("browser_options must be an instance of ChromeOptions")

            return webdriver.Chrome(
                service=ChromeService(ChromeDriverManager().install()),
                options=browser_options,
            )

        elif browser_key == "firefox":
            if (
                not isinstance(browser_options, FirefoxOptions)
                and browser_options is not None
            ):
                raise TypeError("browser_options must be an instance of FirefoxOptions")

            return webdriver.Firefox(
                service=FirefoxService(GeckoDriverManager().install()),
                options=browser_options,
            )

        elif browser_key == "edge":
            if (
                not isinstance(browser_options, EdgeOptions)
                and browser_options is not None
            ):
                raise TypeError("browser_options must be an instance of EdgeOptions")

            return webdriver.Edge(
                service=EdgeService(EdgeChromiumDriverManager().install()),
                options=browser_options,
            )

    def get_value_from_local_storage(self, key, is_exact_match: bool = True):
        """
        Retrieves a value from localStorage using the provided key.

        Args:
            key: The key to search for in localStorage.
            is_exact_match: If True, performs an exact match. If False,
                            treats the key as a regular expression pattern.
                            Defaults to True.

        Returns:
            The value associated with the key if found, otherwise None.
        """
        # Prepare key matcher based on exact match flag
        key_matcher = re.compile(key) if not is_exact_match else None

        try:
            # Retrieve all keys from localStorage
            keys_js = "return Object.keys(window.localStorage);"
            all_keys = self.driver.execute_script(keys_js)

            # Iterate through keys to find a match
            for stored_key in all_keys:
                if (key_matcher and key_matcher.fullmatch(stored_key)) or (
                    is_exact_match and stored_key == key
                ):
                    value_js = f"return window.localStorage.getItem('{stored_key}');"
                    return self.driver.execute_script(value_js)

            # No match found
            return None

        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {str(e)}") from e
        except Exception as e:
            # Handle unexpected errors (e.g., WebDriver issues)
            logging.error(f"Error accessing localStorage: {str(e)}")
            return None

    @staticmethod
    def switch_to_tab_by_title(driver, title, timeout=10):
        """
        Switch to a specific tab based on its title (with wait mechanism)

        :param driver: Selenium WebDriver instance
        :param title: The title of the tab to switch to
        :param timeout: Maximum waiting time for the title to update, in seconds
        :return: True if successfully switched, False if no matching tab title is found
        """
        # Get all window handles
        window_handles = driver.window_handles

        # Iterate through all window handles
        for handle in window_handles:
            # Switch to the current window
            driver.switch_to.window(handle)

            try:
                # Wait for the title to update (up to timeout seconds)
                WebDriverWait(driver, timeout, 1).until(
                    EC.title_is(title)  # Wait for the current window title to match exactly
                )
                print(f"Successfully switched to tab: {title}")
                return True
            except Exception as e:
                # If the title does not match, continue checking the next handle
                pass

                # If no matching title is found among all window handles
        print(f"No tab found with title '{title}'")
        return False
