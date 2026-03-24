"""Configuration file management."""
import json
import logging
from pathlib import Path
from typing import Optional

from models import AppConfig, Task

logger = logging.getLogger(__name__)

CONFIG_FILE = "config.json"


def get_config_path() -> Path:
    """Get the path to config.json (same directory as executable or script)."""
    # When running as exe, use exe directory
    # When running as script, use script directory
    import sys
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent / CONFIG_FILE
    return Path(__file__).parent / CONFIG_FILE


def load_config() -> AppConfig:
    """Load configuration from file, create default if not exists."""
    config_path = get_config_path()

    if not config_path.exists():
        logger.info("Config file not found, creating default")
        config = AppConfig()
        save_config(config)
        return config

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return AppConfig.from_dict(data)
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"Config file corrupted: {e}, using defaults")
        return AppConfig()


def save_config(config: AppConfig) -> bool:
    """Save configuration to file."""
    config_path = get_config_path()

    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config.to_dict(), f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Failed to save config: {e}")
        return False


def add_task(config: AppConfig, task: Task) -> bool:
    """Add a task to config and save."""
    config.tasks.append(task)
    return save_config(config)


def update_task(config: AppConfig, task: Task) -> bool:
    """Update an existing task and save."""
    for i, t in enumerate(config.tasks):
        if t.id == task.id:
            config.tasks[i] = task
            return save_config(config)
    return False


def remove_task(config: AppConfig, task_id: str) -> bool:
    """Remove a task and save."""
    config.tasks = [t for t in config.tasks if t.id != task_id]
    return save_config(config)