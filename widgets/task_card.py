"""Task display card widget."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QSizePolicy,
    QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from models import Task
from styles import COLORS, ICONS


class TaskCardWrapper(QWidget):
    """Wrapper widget that provides padding for shadow."""

    clicked = pyqtSignal(str)  # task_id
    delete_clicked = pyqtSignal(str)  # task_id
    toggle_clicked = pyqtSignal(str, bool)  # task_id, enabled

    def __init__(self, task: Task, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background: transparent;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 16)  # Bottom margin for spacing
        layout.setSpacing(0)

        self._card = TaskCard(task)
        self._card.clicked.connect(self.clicked.emit)
        self._card.delete_clicked.connect(self.delete_clicked.emit)
        self._card.toggle_clicked.connect(self.toggle_clicked.emit)
        layout.addWidget(self._card)

        # Use minimum height instead of fixed
        self.setMinimumWidth(300)
        self.setMinimumHeight(220)  # 200 card + 16 spacing + margin
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)


class TaskCard(QWidget):
    """A card widget for displaying a task."""

    # Signals
    clicked = pyqtSignal(str)  # task_id
    delete_clicked = pyqtSignal(str)  # task_id
    toggle_clicked = pyqtSignal(str, bool)  # task_id, enabled

    def __init__(self, task: Task, parent=None):
        super().__init__(parent)
        # Enable styled background for custom QWidget
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._task = task
        self._setup_ui()

    def _setup_ui(self):
        # Main container with white background and subtle border
        self.setStyleSheet(f"""
            TaskCard {{
                background-color: #ffffff;
                border-radius: 16px;
                border: 1px solid #e5e7eb;
            }}
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        # Use minimum size instead of fixed to allow auto-sizing
        self.setMinimumWidth(300)
        self.setMinimumHeight(200)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)
        # Ensure layout background is white
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Top row: Icon and Toggle
        top_row = QHBoxLayout()

        # Icon container
        icon_container = QLabel(ICONS.TASK_PREVENT_SLEEP if self._task.action == "prevent_sleep" else ICONS.TASK_RESTORE_SLEEP)
        icon_container.setStyleSheet(f"""
            background-color: {COLORS.surface_container_low};
            color: {COLORS.primary};
            border-radius: 12px;
            padding: 12px;
            font-size: 20px;
        """)
        icon_container.setFixedSize(48, 48)
        top_row.addWidget(icon_container)

        top_row.addStretch()

        # Toggle switch
        from widgets.toggle_switch import ToggleSwitch
        self.toggle = ToggleSwitch()
        self.toggle.setChecked(self._task.enabled)
        self.toggle.toggled.connect(lambda checked: self.toggle_clicked.emit(self._task.id, checked))
        top_row.addWidget(self.toggle)

        layout.addLayout(top_row)

        # Task name
        name_row = QHBoxLayout()
        name_label = QLabel(self._task.name)
        name_label.setFont(QFont("Inter", 15, QFont.Weight.Bold))
        name_label.setStyleSheet(f"color: {COLORS.on_surface}; background: transparent;")
        name_row.addWidget(name_label)

        if not self._task.enabled:
            disabled_tag = QLabel("已禁用")
            disabled_tag.setStyleSheet(f"""
                background-color: {COLORS.surface_container_highest};
                color: {COLORS.on_surface_subtle};
                font-size: 11px;
                font-weight: 600;
                border-radius: 4px;
                padding: 3px 8px;
            """)
            name_row.addWidget(disabled_tag)

        name_row.addStretch()
        layout.addLayout(name_row)

        # Schedule info
        schedule_text = self._get_schedule_text()
        schedule_label = QLabel(schedule_text)
        schedule_label.setStyleSheet(f"color: {COLORS.on_surface_subtle}; font-size: 12px; background: transparent;")
        layout.addWidget(schedule_label)

        # Action tag
        action_layout = QHBoxLayout()
        action_container = QLabel(f"动作: {self._get_action_text()}")
        action_container.setStyleSheet(f"""
            background-color: {COLORS.surface_container_low};
            color: {COLORS.on_surface_variant};
            font-size: 11px;
            border-radius: 6px;
            padding: 6px 12px;
        """)
        action_layout.addWidget(action_container)
        action_layout.addStretch()
        layout.addLayout(action_layout)

        layout.addStretch()

        # Bottom row: Edit/Delete buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        edit_btn = QPushButton("编辑")
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS.on_surface_subtle};
                border: 1px solid transparent;
                border-radius: 6px;
                padding: 6px 10px;
            }}
            QPushButton:hover {{
                background-color: {COLORS.surface_container_high};
                color: {COLORS.primary};
                border-color: {COLORS.surface_container_highest};
            }}
        """)
        edit_btn.clicked.connect(lambda: self.clicked.emit(self._task.id))
        btn_row.addWidget(edit_btn)

        delete_btn = QPushButton("删除")
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS.on_surface_subtle};
                border: 1px solid transparent;
                border-radius: 6px;
                padding: 6px 10px;
            }}
            QPushButton:hover {{
                background-color: {COLORS.error_container};
                color: {COLORS.error};
                border-color: {COLORS.error};
            }}
        """)
        delete_btn.clicked.connect(lambda: self.delete_clicked.emit(self._task.id))
        btn_row.addWidget(delete_btn)

        layout.addLayout(btn_row)

    def _get_schedule_text(self) -> str:
        """Get human-readable schedule text."""
        if self._task.task_type == "fixed":
            time_str = self._task.trigger_time or "00:00"
            if self._task.trigger_days:
                days = ["一", "二", "三", "四", "五", "六", "日"]
                day_names = [days[d] for d in self._task.trigger_days]
                return f"{ICONS.TASK_SCHEDULED} {time_str} | 周{', 周'.join(day_names)}"
            return f"{ICONS.TASK_SCHEDULED} {time_str} | 每日"
        else:
            mins = self._task.interval_minutes or 30
            return f"{ICONS.TASK_INTERVAL} 每 {mins} 分钟"

    def _get_action_text(self) -> str:
        """Get action text in Chinese."""
        if self._task.action == "prevent_sleep":
            return "防止休眠"
        return "恢复休眠"