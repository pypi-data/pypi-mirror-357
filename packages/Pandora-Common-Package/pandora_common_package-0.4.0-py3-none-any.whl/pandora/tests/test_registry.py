import winreg
from pandora.integrations.registry import list_registry_values, write_registry, get_registry, delete_registry
from loguru import logger
import sys


def test_get_registry():
    value, value_type = get_registry(r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "AppsUseLightTheme")
    assert value == 1
    assert value_type == winreg.REG_DWORD
    value, value_type = get_registry(r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "ColorPrevalence")
    assert value == 0
    assert value_type == winreg.REG_DWORD
    value, value_type = get_registry(r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "EnableTransparency")
    assert value == 1
    assert value_type == winreg.REG_DWORD
    value, value_type = get_registry(r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "SystemUsesLightTheme")
    assert value == 1
    assert value_type == winreg.REG_DWORD

def test_write_registry():
    new_values = {
        "NewString": ("Test Value", winreg.REG_SZ),
        "NewInt": (100, winreg.REG_DWORD),
    }
    write_registry(r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", new_values)
    value, value_type = get_registry(r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "NewString")
    assert value == "Test Value"
    assert value_type == winreg.REG_SZ
    value, value_type = get_registry(r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "NewInt")
    assert value == 100
    assert value_type == winreg.REG_DWORD


def test_delete_registry():
    delete_registry(r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", ["NewInt", "NewString"])

    value, _ = get_registry(r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "NewInt")
    assert value is None
    value, _ = get_registry(r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "NewString")
    assert value is None



def test_list_registry_values(capsys):
    logger.add(sys.stdout)
    subkey_path = r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
    list_registry_values(subkey_path, depth=1)

    captured = capsys.readouterr()
    output = captured.out
    assert f"[Listing] {subkey_path}" in output

    expected_values = [
        "AppsUseLightTheme",
        "SystemUsesLightTheme",
        "ColorPrevalence",
        "EnableTransparency"
    ]
    assert any(val in output for val in expected_values)
    assert "Value:" in output