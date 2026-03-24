"""Windows power control via powercfg commands."""
import subprocess
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def prevent_sleep() -> bool:
    """Disable system sleep and hibernate.

    Returns:
        True if all commands executed successfully, False otherwise.
    """
    success = True

    # Disable standby (sleep)
    try:
        result = subprocess.run(
            ["powercfg", "/change", "standby-timeout-ac", "0"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            logger.info("Sleep timeout disabled")
        else:
            logger.error(f"Failed to disable sleep: {result.stderr}")
            success = False
    except Exception as e:
        logger.error(f"Failed to disable sleep: {e}")
        success = False

    # Disable hibernate timeout
    try:
        result = subprocess.run(
            ["powercfg", "/change", "hibernate-timeout-ac", "0"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            logger.info("Hibernate timeout disabled")
        else:
            logger.error(f"Failed to disable hibernate timeout: {result.stderr}")
            success = False
    except Exception as e:
        logger.error(f"Failed to disable hibernate timeout: {e}")
        success = False

    return success


def restore_sleep(minutes: int) -> bool:
    """Restore normal sleep and hibernate timeout.

    Args:
        minutes: Sleep timeout in minutes.

    Returns:
        True if all commands executed successfully, False otherwise.
    """
    success = True

    # Restore standby (sleep) timeout
    try:
        result = subprocess.run(
            ["powercfg", "/change", "standby-timeout-ac", str(minutes)],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            logger.info(f"Sleep timeout restored to {minutes} minutes")
        else:
            logger.error(f"Failed to restore sleep: {result.stderr}")
            success = False
    except Exception as e:
        logger.error(f"Failed to restore sleep: {e}")
        success = False

    # Restore hibernate timeout (default to never on restore, or same as sleep)
    try:
        result = subprocess.run(
            ["powercfg", "/change", "hibernate-timeout-ac", "0"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            logger.info("Hibernate timeout set to never")
        else:
            logger.error(f"Failed to set hibernate timeout: {result.stderr}")
            success = False
    except Exception as e:
        logger.error(f"Failed to set hibernate timeout: {e}")
        success = False

    return success


def get_current_sleep_timeout() -> Optional[int]:
    """Get current AC sleep timeout in minutes.

    Returns:
        Current timeout in minutes, or None if unable to determine.
    """
    try:
        result = subprocess.run(
            ["powercfg", "/query", "SCHEME_CURRENT", "SUB_SLEEP", "STANDBYIDLE"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                # Support both English and Chinese Windows
                if 'Current AC Power Setting Index:' in line or '当前交流电源设置索引:' in line:
                    hex_val = line.split(':')[-1].strip()
                    seconds = int(hex_val, 16)
                    return seconds // 60
        return None
    except Exception as e:
        logger.error(f"Failed to get sleep timeout: {e}")
        return None


def get_current_hibernate_timeout() -> Optional[int]:
    """Get current AC hibernate timeout in minutes.

    Returns:
        Current timeout in minutes, or None if unable to determine.
    """
    try:
        result = subprocess.run(
            ["powercfg", "/query", "SCHEME_CURRENT", "SUB_SLEEP", "HIBERNATEIDLE"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                # Support both English and Chinese Windows
                if 'Current AC Power Setting Index:' in line or '当前交流电源设置索引:' in line:
                    hex_val = line.split(':')[-1].strip()
                    seconds = int(hex_val, 16)
                    return seconds // 60
        return None
    except Exception as e:
        logger.error(f"Failed to get hibernate timeout: {e}")
        return None


def is_sleep_prevented() -> bool:
    """Check if sleep is currently prevented (timeout == 0)."""
    sleep_timeout = get_current_sleep_timeout()
    hibernate_timeout = get_current_hibernate_timeout()

    # Both must be 0 (disabled) to consider sleep prevented
    sleep_disabled = sleep_timeout == 0 if sleep_timeout is not None else False
    hibernate_disabled = hibernate_timeout == 0 if hibernate_timeout is not None else False

    return sleep_disabled and hibernate_disabled


def is_hibernate_enabled() -> bool:
    """Check if hibernate feature is enabled at system level."""
    try:
        result = subprocess.run(
            ["powercfg", "/a"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return "休眠" in result.stdout or "Hibernation" in result.stdout or "Hibernate" in result.stdout
        return False
    except Exception as e:
        logger.error(f"Failed to check hibernate status: {e}")
        return False