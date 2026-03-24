"""Task scheduler using APScheduler."""
import logging
from typing import Callable, Optional
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from models import Task

logger = logging.getLogger(__name__)


class TaskScheduler:
    """Manages scheduled tasks using APScheduler."""

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self._jobs: dict[str, str] = {}  # task_id -> job_id

    def start(self):
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started")

    def stop(self):
        """Stop the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")

    def add_task(
        self,
        task: Task,
        callback: Callable[[Task], None]
    ) -> bool:
        """Add a task to the scheduler.

        Args:
            task: Task to schedule.
            callback: Function to call when task triggers.

        Returns:
            True if task was added successfully.
        """
        if not task.enabled:
            logger.info(f"Task {task.name} is disabled, skipping")
            return False

        try:
            if task.task_type == "fixed":
                job = self._add_fixed_task(task, callback)
            else:
                job = self._add_interval_task(task, callback)

            if job:
                self._jobs[task.id] = job.id
                logger.info(f"Added task: {task.name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to add task {task.name}: {e}")
            return False

    def _add_fixed_task(
        self,
        task: Task,
        callback: Callable[[Task], None]
    ):
        """Add a fixed-time task."""
        if not task.trigger_time:
            logger.error(f"Fixed task {task.name} has no trigger time")
            return None

        # Parse time (HH:MM format)
        hour, minute = task.trigger_time.split(":")

        # Build cron expression
        if task.trigger_days:
            # Days: 0=Monday, 6=Sunday -> cron: 0=Sunday, 6=Saturday
            # Convert: our 0=Monday -> cron 1=Monday
            day_of_week = ",".join(str((d + 1) % 7) for d in task.trigger_days)
        else:
            day_of_week = "*"

        trigger = CronTrigger(
            hour=int(hour),
            minute=int(minute),
            day_of_week=day_of_week
        )

        return self.scheduler.add_job(
            callback,
            trigger=trigger,
            args=[task],
            id=f"task_{task.id}",
            replace_existing=True
        )

    def _add_interval_task(
        self,
        task: Task,
        callback: Callable[[Task], None]
    ):
        """Add an interval task."""
        if not task.interval_minutes:
            logger.error(f"Interval task {task.name} has no interval")
            return None

        trigger = IntervalTrigger(minutes=task.interval_minutes)

        return self.scheduler.add_job(
            callback,
            trigger=trigger,
            args=[task],
            id=f"task_{task.id}",
            replace_existing=True
        )

    def remove_task(self, task_id: str) -> bool:
        """Remove a task from the scheduler.

        Args:
            task_id: ID of task to remove.

        Returns:
            True if task was removed.
        """
        if task_id not in self._jobs:
            return False

        try:
            job_id = self._jobs[task_id]
            self.scheduler.remove_job(job_id)
            del self._jobs[task_id]
            logger.info(f"Removed task: {task_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove task {task_id}: {e}")
            return False

    def update_task(
        self,
        task: Task,
        callback: Callable[[Task], None]
    ) -> bool:
        """Update an existing task.

        Args:
            task: Updated task.
            callback: Callback function.

        Returns:
            True if update successful.
        """
        self.remove_task(task.id)
        return self.add_task(task, callback)

    def get_next_run_time(self, task_id: str) -> Optional[datetime]:
        """Get the next run time for a task.

        Args:
            task_id: Task ID.

        Returns:
            Next run time or None.
        """
        if task_id not in self._jobs:
            return None

        try:
            job_id = self._jobs[task_id]
            job = self.scheduler.get_job(job_id)
            return job.next_run_time if job else None
        except Exception:
            return None

    def load_tasks(
        self,
        tasks: list[Task],
        callback: Callable[[Task], None]
    ):
        """Load all tasks from config.

        Args:
            tasks: List of tasks to load.
            callback: Callback function for each task.
        """
        for task in tasks:
            self.add_task(task, callback)