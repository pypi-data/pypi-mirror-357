import time

from src.pandora.drivers import web_browser


def test_get_value_from_local_storage():
    option = web_browser.EdgeOptions()
    option.add_argument("--start-maximized")

    test_driver = web_browser.WebBrowser.get_driver("edge", option)
    test_driver.get("https://www.doc.com/")

    common_web_function = web_browser.WebBrowser(test_driver)

    local_storage_actual_value = common_web_function.get_value_from_local_storage(
        "lastExternalReferrer"
    )
    local_storage_expect_value = "empty"

    assert (
        local_storage_actual_value == local_storage_expect_value
    ), "The except value is incorrect in local storage"
    test_driver.quit()


# test web_browser.py switch_to_tab_by_title method
def test_switch_to_tab_by_title():
    option = web_browser.EdgeOptions()
    option.add_argument("--start-maximized")

    test_driver = web_browser.WebBrowser.get_driver("edge", option)
    test_driver.get("https://www.google.com/")
    test_driver.execute_script("window.open('https://www.bing.com');")
    test_driver.execute_script("window.open('https://www.youtube.com');")

    web_browser.WebBrowser.switch_to_tab_by_title(test_driver, "Search - Microsoft Bing", 10)
    assert (test_driver.current_url == "https://www.bing.com/"),\
        "The except value is incorrect in local storage"
    web_browser.WebBrowser.switch_to_tab_by_title(test_driver, "Google", 10)
    assert (test_driver.current_url == "https://www.google.com.hk/"),\
        "The except value is incorrect in local storage"
    web_browser.WebBrowser.switch_to_tab_by_title(test_driver, "YouTube", 10)
    assert (test_driver.current_url == "https://www.youtube.com/"),\
        "The except value is incorrect in local storage"
    test_driver.quit()
