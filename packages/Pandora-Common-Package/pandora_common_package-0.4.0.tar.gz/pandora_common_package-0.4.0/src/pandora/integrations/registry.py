import winreg
import re
from loguru import logger

HKEY_MAP = {
    "HKEY_CLASSES_ROOT": winreg.HKEY_CLASSES_ROOT,
    "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
    "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
    "HKEY_USERS": winreg.HKEY_USERS,
    "HKEY_CURRENT_CONFIG": winreg.HKEY_CURRENT_CONFIG
}

def handle_registry_path(path: str, auto_resolve=True):
    """
    Parse registry path into (root_key, sub_key)
    If no root key is given and auto_resolve=True, try common root keys.
    """
    path = path.strip().lstrip("\\")
    match = re.match(r'^(HKEY_[^\\]+)\\(.+)$', path, re.IGNORECASE)

    if match:
        root_key_str, sub_key = match.groups()
        root_key = HKEY_MAP.get(root_key_str.upper())
        if root_key:
            return root_key, sub_key
        else:
            logger.debug(f"Unknown root key {root_key_str}")
            return None, None
    if auto_resolve:
        for name, root_key in HKEY_MAP.items():
            try:
                with winreg.OpenKey(root_key, path, 0, winreg.KEY_READ):
                    return root_key, path
            except:
                continue
        logger.debug(f"[Error] Registry path not found: {path}")
        return None, None
    logger.debug(f"[Error] Invalid registry path: {path}")
    return None, None


def get_registry(path, value_name):
    """Read a specific registry value"""
    root_key, sub_key = handle_registry_path(path)
    if not root_key:
        return None, None
    try:
        with winreg.OpenKey(root_key, sub_key, 0, winreg.KEY_READ) as key:
            value, value_type = winreg.QueryValueEx(key, value_name)
            return value, value_type
    except:
        logger.debug(f"[Error] Failed to read value '{value_name}' from {path}")
        return None, None

def write_registry(path, values: dict):
    """
    Write or update multiple registry values.
    values: dict of {name: (value, type)}

    write_registry_values(
    r"HKEY_CURRENT_USER\Software\test",
    {
        "Setting1": ("Enabled", winreg.REG_SZ),
        "Count": (3, winreg.REG_DWORD)
        }
    )
    """
    root_key, sub_key = handle_registry_path(path)

    try:
        with winreg.CreateKeyEx(root_key, sub_key, 0, winreg.KEY_WRITE) as key:
            for name, (val, val_type) in values.items():
                try:
                    winreg.SetValueEx(key, name, 0, val_type, val)
                    logger.info(f"[Write] {name} = {val}")
                except OSError as e:
                    logger.error(f"[Error] Failed to write '{name}' = {val} ({val_type}): {e}")
    except Exception as e:
        logger.error(f"[Error] Failed to open or create registry key '{path}': {e}")

def delete_registry(path, value_names: list):
    """Delete multiple registry values
       delete_registry_values(
           r"HKEY_CURRENT_USER\Software\MyApp",
           ["Setting1", "NonExistentValue"]
    )
    """
    root_key, sub_key = handle_registry_path(path)
    if not root_key:
        return

    try:
        with winreg.OpenKey(root_key, sub_key, 0, winreg.KEY_SET_VALUE) as key:
            for name in value_names:
                try:
                    winreg.DeleteValue(key, name)
                    logger.error(f"[Deleted] Value: {name}")
                except:
                    logger.error(f"[Not Found] Value: {name}")
    except:
        logger.error(f"[Not Found] Key: {path}")

def list_registry_values(path, depth=1):
    """List all values and optionally recurse into subkeys"""
    root_key, sub_key = handle_registry_path(path)
    try:
        with winreg.OpenKey(root_key, sub_key, 0, winreg.KEY_READ) as key:
            logger.debug(f"[Listing] {path}")
            i = 0
            while True:
                try:
                    name, val, vtype = winreg.EnumValue(key, i)
                    logger.info(f"  Value: {name} = {val} ({vtype})")
                    i += 1
                except OSError:
                    break

            if depth > 0:
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        child_path = f"{path}\\{subkey_name}"
                        list_registry_values(child_path, depth - 1)
                        i += 1
                    except OSError:
                        break
    except FileNotFoundError:
        logger.error(f"[Not Found] {path}")
