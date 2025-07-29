# This is a sample Python script.
from config.config import c_config
from conftest import load_config


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(load_config):
    # Use a breakpoint in the code line below to debug your script.
    print(f"Hi, {load_config['stack']}")  # Press Ctrl+F8 to toggle the breakpoint.
    print(f"Hi, {load_config['web_url']}")


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    print_hi(load_config)


def test_getconfiginfo(load_config):
    print("test")
    print_hi(load_config)
    print(c_config.user_name_1)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
