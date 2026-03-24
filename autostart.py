"""Windows autostart via Registry."""
import logging
import sys
from pathlib import Path

import winreg

logger = logging.getLogger(__name__)

REGISTRY_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "TailWake"


def get_app_path() -> str:
    """Get the application executable path."""
    if getattr(sys, 'frozen', False):
        return sys.executable
    # For development, use pythonw with the script path
    return f'pythonw "{Path(__file__).parent / "main.py"}"'


def enable_autostart() -> bool:
    """Enable autostart by adding to Registry.

    Returns:
        True if successful, False otherwise.
    """
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            REGISTRY_KEY,
            0,
            winreg.KEY_WRITE
        )
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, get_app_path())
        winreg.CloseKey(key)
        logger.info("Autostart enabled")
        return True
    except Exception as e:
        logger.error(f"Failed to enable autostart: {e}")
        return False


def disable_autostart() -> bool:
    """Disable autostart by removing from Registry.

    Returns:
        True if successful, False otherwise.
    """
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            REGISTRY_KEY,
            0,
            winreg.KEY_WRITE
        )
        try:
            winreg.DeleteValue(key, APP_NAME)
        except FileNotFoundError:
            pass  # Value doesn't exist, that's fine
        winreg.CloseKey(key)
        logger.info("Autostart disabled")
        return True
    except Exception as e:
        logger.error(f"Failed to disable autostart: {e}")
        return False


def is_autostart_enabled() -> bool:
    """Check if autostart is currently enabled.

    Returns:
        True if autostart entry exists, False otherwise.
    """
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            REGISTRY_KEY,
            0,
            winreg.KEY_READ
        )
        try:
            value, _ = winreg.QueryValueEx(key, APP_NAME)
            winreg.CloseKey(key)
            return bool(value)
        except FileNotFoundError:
            winreg.CloseKey(key)
            return False
    except Exception as e:
        logger.error(f"Failed to check autostart status: {e}")
        return False