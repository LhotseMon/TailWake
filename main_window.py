"""Main application window."""
import logging
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QStackedWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject

from models import Task, AppConfig
from config import load_config, save_config, add_task, update_task, remove_task
from scheduler import TaskScheduler
from styles import get_app_stylesheet
from widgets.sidebar import Sidebar
from widgets.countdown_dialog import CountdownDialog
from pages.dashboard_page import DashboardPage
from pages.tasks_page import TasksPage
from pages.task_edit_page import TaskEditPage
from pages.settings_page import SettingsPage
import power_control
import history_tracker

logger = logging.getLogger(__name__)


class TaskTriggerSignaler(QObject):
    """Signal emitter for thread-safe task triggering."""
    task_triggered = pyqtSignal(object)  # Emits Task object


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TailWake")
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)

        # Load config
        self._config = load_config()

        # Create signal emitter for thread-safe task triggering
        self._task_signaler = TaskTriggerSignaler()
        self._task_signaler.task_triggered.connect(self._show_task_dialog)

        # Initialize scheduler
        self._scheduler = TaskScheduler()
        self._scheduler.start()

        self._setup_ui()
        self._load_tasks_to_scheduler()

    def _setup_ui(self):
        # Apply stylesheet
        self.setStyleSheet(get_app_stylesheet())

        # Central widget
        central = QWidget()
        central.setObjectName("mainContent")
        self.setCentralWidget(central)

        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar()
        self.sidebar.dashboard_clicked.connect(lambda: self._show_page("dashboard"))
        self.sidebar.tasks_clicked.connect(lambda: self._show_page("tasks"))
        self.sidebar.settings_clicked.connect(lambda: self._show_page("settings"))
        layout.addWidget(self.sidebar)

        # Main content area
        self.stack = QStackedWidget()

        # Pages
        self.dashboard_page = DashboardPage()
        self.dashboard_page.navigate_to_tasks.connect(lambda: self._show_page("tasks"))
        self.dashboard_page.navigate_to_settings.connect(lambda: self._show_page("settings"))
        self.dashboard_page.toggle_sleep_prevention.connect(self._toggle_sleep_prevention)
        self.stack.addWidget(self.dashboard_page)

        self.tasks_page = TasksPage()
        self.tasks_page.set_scheduler(self._scheduler)
        self.tasks_page.set_tasks(self._config.tasks)
        self.tasks_page.add_task_clicked.connect(self._show_new_task_page)
        self.tasks_page.edit_task_clicked.connect(self._show_edit_task_page)
        self.tasks_page.delete_task_clicked.connect(self._delete_task)
        self.tasks_page.task_toggled.connect(self._toggle_task)
        self.stack.addWidget(self.tasks_page)

        self.task_edit_page = TaskEditPage()
        self.task_edit_page.saved.connect(self._save_task)
        self.task_edit_page.cancelled.connect(lambda: self._show_page("tasks"))
        self.stack.addWidget(self.task_edit_page)

        self.settings_page = SettingsPage()
        self.settings_page.set_config(self._config)
        self.settings_page.settings_changed.connect(self._save_settings)
        self.stack.addWidget(self.settings_page)

        layout.addWidget(self.stack, 1)

    def _show_page(self, page: str):
        """Show a specific page."""
        if page == "dashboard":
            self.stack.setCurrentWidget(self.dashboard_page)
            self.sidebar.set_active_page("dashboard")
        elif page == "tasks":
            self.tasks_page.set_tasks(self._config.tasks)
            self.stack.setCurrentWidget(self.tasks_page)
            self.sidebar.set_active_page("tasks")
        elif page == "settings":
            self.stack.setCurrentWidget(self.settings_page)
            self.sidebar.set_active_page("settings")

    def _show_new_task_page(self):
        """Show page for creating new task."""
        self.task_edit_page.set_task(None)
        self.stack.setCurrentWidget(self.task_edit_page)

    def _show_edit_task_page(self, task_id: str):
        """Show page for editing task."""
        task = next((t for t in self._config.tasks if t.id == task_id), None)
        if task:
            self.task_edit_page.set_task(task)
            self.stack.setCurrentWidget(self.task_edit_page)

    def _save_task(self, task: Task):
        """Save a task (create or update)."""
        existing = next((t for t in self._config.tasks if t.id == task.id), None)

        if existing:
            update_task(self._config, task)
            self._scheduler.update_task(task, self._on_task_trigger)
        else:
            add_task(self._config, task)
            self._scheduler.add_task(task, self._on_task_trigger)

        self._show_page("tasks")

    def _delete_task(self, task_id: str):
        """Delete a task."""
        remove_task(self._config, task_id)
        self._scheduler.remove_task(task_id)
        self.tasks_page.set_tasks(self._config.tasks)

    def _toggle_task(self, task_id: str, enabled: bool):
        """Toggle task enabled state."""
        task = next((t for t in self._config.tasks if t.id == task_id), None)
        if task:
            task.enabled = enabled
            update_task(self._config, task)

            if enabled:
                self._scheduler.add_task(task, self._on_task_trigger)
            else:
                self._scheduler.remove_task(task_id)

            # Update stats display
            self.tasks_page.update_stats()

    def _load_tasks_to_scheduler(self):
        """Load all tasks to scheduler."""
        for task in self._config.tasks:
            self._scheduler.add_task(task, self._on_task_trigger)

    def _on_task_trigger(self, task: Task):
        """Handle task trigger from scheduler (called from background thread)."""
        logger.info(f"Task triggered: {task.name}")
        # Emit signal to show dialog in main thread
        self._task_signaler.task_triggered.emit(task)

    def _show_task_dialog(self, task: Task):
        """Show task confirmation dialog (called in main thread via signal)."""
        dialog = CountdownDialog(
            task_name=task.name,
            action=task.action,
            countdown_seconds=self._config.countdown_seconds,
            parent=self
        )
        dialog.confirmed.connect(lambda: self._execute_task(task))
        dialog.start_countdown()

    def _execute_task(self, task: Task):
        """Execute a task action."""
        if task.action == "prevent_sleep":
            power_control.prevent_sleep()
            history_tracker.record_prevent_sleep_activation()
            history_tracker.record_session_start()
        else:
            power_control.restore_sleep(self._config.restore_sleep_minutes)
            history_tracker.record_session_end()

    def _toggle_sleep_prevention(self, prevent: bool):
        """Toggle sleep prevention state from dashboard."""
        if prevent:
            power_control.prevent_sleep()
            history_tracker.record_prevent_sleep_activation()
            history_tracker.record_session_start()
        else:
            power_control.restore_sleep(self._config.restore_sleep_minutes)
            history_tracker.record_session_end()

    def _save_settings(self):
        """Save settings to config file."""
        save_config(self._config)

    def closeEvent(self, event):
        """Handle window close."""
        self._scheduler.stop()
        event.accept()