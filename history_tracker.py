"""Runtime history tracking for statistics."""
import json
import logging
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Optional

from models import HistoryRecord

logger = logging.getLogger(__name__)

HISTORY_FILE = "history.json"


def get_history_path() -> Path:
    """Get the path to history.json."""
    import sys
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent / HISTORY_FILE
    return Path(__file__).parent / HISTORY_FILE


def load_history() -> list[HistoryRecord]:
    """Load history from file."""
    path = get_history_path()
    if not path.exists():
        return []

    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return [HistoryRecord.from_dict(r) for r in data]
    except Exception as e:
        logger.error(f"Failed to load history: {e}")
        return []


def save_history(records: list[HistoryRecord]) -> bool:
    """Save history to file."""
    path = get_history_path()
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump([r.to_dict() for r in records], f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Failed to save history: {e}")
        return False


def get_or_create_today_record(records: list[HistoryRecord]) -> tuple[HistoryRecord, bool]:
    """Get today's record or create a new one.

    Returns:
        Tuple of (record, was_created)
    """
    today = date.today().isoformat()
    for record in records:
        if record.date == today:
            return record, False

    new_record = HistoryRecord(date=today)
    return new_record, True


# Global session tracking
_session_start: Optional[datetime] = None
_is_preventing_sleep = False


def record_session_start():
    """Record the start of an active session."""
    global _session_start
    _session_start = datetime.now()
    logger.debug(f"Session started at {_session_start}")


def record_session_end():
    """Record the end of an active session and update history."""
    global _session_start

    if _session_start is None:
        return

    duration = datetime.now() - _session_start
    hours = duration.total_seconds() / 3600

    records = load_history()
    today_record, created = get_or_create_today_record(records)
    today_record.active_hours += hours

    if created:
        records.append(today_record)

    save_history(records)
    logger.info(f"Session ended. Added {hours:.2f} hours")

    _session_start = None


def record_prevent_sleep_activation():
    """Record a prevent sleep activation."""
    global _is_preventing_sleep
    _is_preventing_sleep = True

    records = load_history()
    today_record, created = get_or_create_today_record(records)
    today_record.prevent_sleep_count += 1

    if created:
        records.append(today_record)

    save_history(records)


def get_weekly_history() -> list[HistoryRecord]:
    """Get history for the last 7 days."""
    records = load_history()
    today = date.today()

    # Build a dict for quick lookup
    record_dict = {r.date: r for r in records}

    result = []
    for i in range(6, -1, -1):  # 6 days ago to today
        d = (today - timedelta(days=i)).isoformat()
        if d in record_dict:
            result.append(record_dict[d])
        else:
            result.append(HistoryRecord(date=d))

    return result


def get_total_active_hours() -> float:
    """Get total active hours across all history."""
    records = load_history()
    return sum(r.active_hours for r in records)


def get_online_rate() -> float:
    """Calculate online success rate (placeholder for now)."""
    # This would need actual tracking of connection events
    # For now, return a placeholder
    return 99.98