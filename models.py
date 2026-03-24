"""Data models for TailWake application."""
from dataclasses import dataclass, field, asdict
from typing import Optional
import uuid
import json


@dataclass
class Task:
    """Represents a scheduled task."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    icon: str = "schedule"
    task_type: str = "fixed"  # "fixed" or "interval"
    trigger_time: Optional[str] = None  # "HH:MM" format
    trigger_days: Optional[list[int]] = None  # 0=Monday, 6=Sunday, None=every day
    interval_minutes: Optional[int] = None
    action: str = "prevent_sleep"  # "prevent_sleep" or "restore_sleep"
    enabled: bool = True

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(**data)


@dataclass
class HistoryRecord:
    """Represents a single day's history."""
    date: str  # "YYYY-MM-DD"
    active_hours: float = 0.0
    prevent_sleep_count: int = 0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "HistoryRecord":
        return cls(**data)


@dataclass
class AppConfig:
    """Application configuration."""
    countdown_seconds: int = 60
    restore_sleep_minutes: int = 20
    autostart: bool = True
    track_history: bool = True
    tasks: list[Task] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "countdown_seconds": self.countdown_seconds,
            "restore_sleep_minutes": self.restore_sleep_minutes,
            "autostart": self.autostart,
            "track_history": self.track_history,
            "tasks": [t.to_dict() for t in self.tasks]
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AppConfig":
        tasks = [Task.from_dict(t) for t in data.get("tasks", [])]
        return cls(
            countdown_seconds=data.get("countdown_seconds", 60),
            restore_sleep_minutes=data.get("restore_sleep_minutes", 20),
            autostart=data.get("autostart", True),
            track_history=data.get("track_history", True),
            tasks=tasks
        )