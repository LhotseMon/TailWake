"""Task editor page."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QSpinBox, QComboBox, QCheckBox, QFrame,
    QScrollArea, QSizePolicy, QBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from models import Task
from styles import COLORS, ICONS


class DayButton(QPushButton):
    """Circular day toggle button."""

    def __init__(self, text: str, checked: bool = False, parent=None):
        super().__init__(text, parent)
        self._checked = checked
        self.setFixedSize(56, 56)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._update_style()
        self.clicked.connect(self._toggle)

    def _toggle(self):
        self._checked = not self._checked
        self._update_style()

    def isChecked(self) -> bool:
        return self._checked

    def setChecked(self, checked: bool):
        self._checked = checked
        self._update_style()

    def _update_style(self):
        if self._checked:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS.primary};
                    color: white;
                    border-radius: 28px;
                    font-weight: 600;
                    font-size: 14px;
                    font-family: 'Segoe UI', 'Microsoft YaHei', 'PingFang SC', sans-serif;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS.surface_container_high};
                    color: {COLORS.on_surface_variant};
                    border-radius: 28px;
                    font-weight: 600;
                    font-size: 14px;
                    font-family: 'Segoe UI', 'Microsoft YaHei', 'PingFang SC', sans-serif;
                }}
                QPushButton:hover {{
                    background-color: {COLORS.surface_container_highest};
                }}
            """)


class TaskEditPage(QWidget):
    """Page for creating/editing tasks."""

    # Signals
    saved = pyqtSignal(Task)
    cancelled = pyqtSignal()

    # Responsive breakpoint - switch to vertical layout below this width
    RESPONSIVE_BREAKPOINT = 900

    def __init__(self, parent=None):
        super().__init__(parent)
        self._task: Task | None = None
        self._is_edit = False
        self._content_layout = None
        self._form_card = None
        self._info_layout = None
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(f"background-color: {COLORS.surface};")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Scroll area for responsive layout
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: {COLORS.surface};
                border: none;
            }}
        """)

        # Content widget
        content = QWidget()
        content.setStyleSheet(f"background-color: {COLORS.surface};")
        content.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(48, 32, 48, 32)
        layout.setSpacing(32)

        # Page header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(8)

        self.title_label = QLabel("编辑任务详情")
        self.title_label.setFont(QFont("Inter", 32, QFont.Weight.ExtraBold))
        self.title_label.setStyleSheet(f"color: {COLORS.on_surface}; letter-spacing: -0.02em;")
        header_layout.addWidget(self.title_label)

        subtitle = QLabel("配置您的桌面自动化策略与系统常驻任务")
        subtitle.setStyleSheet(f"color: {COLORS.on_surface_subtle}; font-size: 16px;")
        header_layout.addWidget(subtitle)

        layout.addLayout(header_layout)

        # Main content - two columns (responsive)
        self._content_layout = QHBoxLayout()
        self._content_layout.setSpacing(24)

        # Left: Form
        self._form_card = QFrame()
        self._form_card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS.surface_container_low};
                border-radius: 12px;
                border: 1px solid {COLORS.surface_container};
            }}
        """)
        form_layout = QVBoxLayout(self._form_card)
        form_layout.setContentsMargins(32, 32, 32, 32)
        form_layout.setSpacing(24)

        # Section header
        section_header = QLabel(f"{ICONS.SECTION_CONFIG} 基本配置")
        section_header.setFont(QFont("Inter", 15, QFont.Weight.Bold))
        section_header.setStyleSheet(f"color: {COLORS.primary}; letter-spacing: -0.01em;")
        form_layout.addWidget(section_header)

        # Task name
        name_label = QLabel("任务名称")
        name_label.setStyleSheet(f"color: {COLORS.on_surface_subtle}; font-size: 12px; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase;")
        form_layout.addWidget(name_label)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("例如：深夜系统维护脚本")
        self.name_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS.surface_container_highest};
                border: none;
                border-radius: 8px;
                padding: 14px 16px;
                font-size: 14px;
                font-family: 'Inter';
            }}
            QLineEdit:focus {{
                background-color: {COLORS.primary_fixed};
            }}
        """)
        form_layout.addWidget(self.name_input)

        # Time and action row
        time_action_layout = QHBoxLayout()
        time_action_layout.setSpacing(32)

        # Trigger time - using separate hour, minute, AM/PM selectors
        time_container = QVBoxLayout()
        time_label = QLabel("触发时间")
        time_label.setStyleSheet(f"color: {COLORS.on_surface_subtle}; font-size: 12px; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase;")
        time_container.addWidget(time_label)

        # Horizontal layout for hour : minute : AM/PM
        time_input_layout = QHBoxLayout()
        time_input_layout.setSpacing(8)

        self.hour_spin = QSpinBox()
        self.hour_spin.setRange(1, 12)
        self.hour_spin.setValue(2)
        self.hour_spin.setWrapping(True)
        self.hour_spin.setFixedWidth(80)
        self.hour_spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hour_spin.setStyleSheet(f"""
            QSpinBox {{
                background-color: {COLORS.surface_container_highest};
                border: none;
                border-radius: 8px;
                padding: 12px 8px;
                font-size: 18px;
                font-weight: 600;
                font-family: 'Inter';
            }}
            QSpinBox:focus {{
                background-color: {COLORS.primary_fixed};
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                background-color: {COLORS.surface_container};
                border-radius: 4px;
                width: 24px;
                margin: 2px;
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background-color: {COLORS.primary};
            }}
            QSpinBox::up-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-bottom: 6px solid {COLORS.on_surface_variant};
                subcontrol-position: center;
            }}
            QSpinBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {COLORS.on_surface_variant};
                subcontrol-position: center;
            }}
        """)
        time_input_layout.addWidget(self.hour_spin)

        colon1 = QLabel(":")
        colon1.setStyleSheet(f"color: {COLORS.on_surface_variant}; font-size: 24px; font-weight: 300;")
        time_input_layout.addWidget(colon1)

        self.minute_spin = QSpinBox()
        self.minute_spin.setRange(0, 59)
        self.minute_spin.setValue(30)
        self.minute_spin.setWrapping(True)
        self.minute_spin.setFixedWidth(80)
        self.minute_spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.minute_spin.setStyleSheet(f"""
            QSpinBox {{
                background-color: {COLORS.surface_container_highest};
                border: none;
                border-radius: 8px;
                padding: 12px 8px;
                font-size: 18px;
                font-weight: 600;
                font-family: 'Inter';
            }}
            QSpinBox:focus {{
                background-color: {COLORS.primary_fixed};
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                background-color: {COLORS.surface_container};
                border-radius: 4px;
                width: 24px;
                margin: 2px;
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background-color: {COLORS.primary};
            }}
            QSpinBox::up-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-bottom: 6px solid {COLORS.on_surface_variant};
                subcontrol-position: center;
            }}
            QSpinBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {COLORS.on_surface_variant};
                subcontrol-position: center;
            }}
        """)
        time_input_layout.addWidget(self.minute_spin)

        self.am_pm_combo = QComboBox()
        self.am_pm_combo.addItems(["AM", "PM"])
        self.am_pm_combo.setCurrentIndex(0)
        self.am_pm_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS.surface_container_highest};
                border: none;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 16px;
                font-weight: 600;
                font-family: 'Inter';
                min-width: 80px;
            }}
            QComboBox:focus {{
                background-color: {COLORS.primary_fixed};
            }}
            QComboBox::drop-down {{
                border: none;
                padding-right: 12px;
            }}
            QComboBox::down-arrow {{
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {COLORS.on_surface_variant};
            }}
        """)
        time_input_layout.addWidget(self.am_pm_combo)

        time_input_layout.addStretch()
        time_container.addLayout(time_input_layout)
        time_action_layout.addLayout(time_container)

        # Power action
        action_container = QVBoxLayout()
        action_label = QLabel("电源动作 (POWER ACTION)")
        action_label.setStyleSheet(f"color: {COLORS.on_surface_subtle}; font-size: 12px; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase;")
        action_container.addWidget(action_label)

        self.action_combo = QComboBox()
        self.action_combo.addItems(["防止休眠 (Prevent Sleep)", "恢复休眠 (Normal Sleep)"])
        self.action_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS.surface_container_highest};
                border: none;
                border-radius: 8px;
                padding: 14px 16px;
                font-size: 14px;
                font-family: 'Inter';
                font-weight: 500;
            }}
            QComboBox:focus {{
                background-color: {COLORS.primary_fixed};
            }}
            QComboBox::drop-down {{
                border: none;
                padding-right: 12px;
            }}
            QComboBox::down-arrow {{
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {COLORS.on_surface_variant};
                margin-right: 12px;
            }}
        """)
        action_container.addWidget(self.action_combo)
        time_action_layout.addLayout(action_container)

        form_layout.addLayout(time_action_layout)

        # Task type
        type_label = QLabel("触发类型")
        type_label.setStyleSheet(f"color: {COLORS.on_surface_subtle}; font-size: 12px; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase;")
        form_layout.addWidget(type_label)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["固定时间", "间隔循环"])
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        self.type_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS.surface_container_highest};
                border: none;
                border-radius: 6px;
                padding: 16px;
                font-size: 14px;
            }}
        """)
        form_layout.addWidget(self.type_combo)

        # Fixed time settings - Days
        self.days_label = QLabel("重复周期 (REPEAT CYCLE)")
        self.days_label.setStyleSheet(f"color: {COLORS.on_surface_subtle}; font-size: 12px; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase;")
        form_layout.addWidget(self.days_label)

        days_layout = QHBoxLayout()
        days_layout.setSpacing(8)
        self.day_buttons = []
        days = ["一", "二", "三", "四", "五", "六", "日"]
        for day in days:
            btn = DayButton(day, checked=True)
            self.day_buttons.append(btn)
            days_layout.addWidget(btn)
        days_layout.addStretch()
        form_layout.addLayout(days_layout)

        # Interval settings
        self.interval_frame = QFrame()
        interval_layout = QHBoxLayout(self.interval_frame)
        interval_layout.setContentsMargins(0, 0, 0, 0)

        interval_label = QLabel("间隔时间")
        interval_label.setStyleSheet(f"color: {COLORS.on_surface_subtle}; font-size: 12px; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase;")
        interval_layout.addWidget(interval_label)

        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 1440)
        self.interval_spin.setValue(30)
        self.interval_spin.setSuffix(" 分钟")
        self.interval_spin.setFixedWidth(120)
        self.interval_spin.setStyleSheet(f"""
            QSpinBox {{
                background-color: {COLORS.surface_container_highest};
                border: none;
                border-radius: 8px;
                padding: 12px 8px;
                font-size: 14px;
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                background-color: {COLORS.surface_container};
                border-radius: 4px;
                width: 20px;
                margin: 2px;
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background-color: {COLORS.primary};
            }}
            QSpinBox::up-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-bottom: 5px solid {COLORS.on_surface_variant};
                subcontrol-position: center;
            }}
            QSpinBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid {COLORS.on_surface_variant};
                subcontrol-position: center;
            }}
        """)
        interval_layout.addWidget(self.interval_spin)
        interval_layout.addStretch()

        self.interval_frame.hide()
        form_layout.addWidget(self.interval_frame)

        form_layout.addStretch()
        self._content_layout.addWidget(self._form_card, 2)

        # Right: Info sidebar
        self._info_layout = QVBoxLayout()
        self._info_layout.setSpacing(20)

        # Device info card
        device_card = QFrame()
        device_card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS.surface_container_low};
                border-radius: 12px;
                border: 1px solid {COLORS.surface_container};
            }}
        """)
        device_layout = QVBoxLayout(device_card)
        device_layout.setContentsMargins(24, 24, 24, 24)
        device_layout.setSpacing(16)

        device_header = QLabel("目标设备信息")
        device_header.setFont(QFont("Inter", 13, QFont.Weight.Bold))
        device_header.setStyleSheet(f"color: {COLORS.on_surface}; letter-spacing: -0.01em;")
        device_layout.addWidget(device_header)

        device_layout.addSpacing(8)

        ip_label = QLabel("NODE IP ADDRESS")
        ip_label.setStyleSheet(f"color: {COLORS.on_surface_subtle}; font-size: 10px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase;")
        device_layout.addWidget(ip_label)

        ip_value = QLabel("192.168.1.104")
        ip_value.setFont(QFont("Inter", 16, QFont.Weight.Bold))
        ip_value.setStyleSheet(f"color: {COLORS.on_surface}; font-family: monospace;")
        device_layout.addWidget(ip_value)

        device_layout.addSpacing(8)

        status_label = QLabel("DEVICE STATUS")
        status_label.setStyleSheet(f"color: {COLORS.on_surface_subtle}; font-size: 10px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase;")
        device_layout.addWidget(status_label)

        status_value = QLabel("Active & Connected")
        status_value.setFont(QFont("Inter", 14, QFont.Weight.Bold))
        status_value.setStyleSheet(f"color: {COLORS.tertiary_fixed_dim};")
        device_layout.addWidget(status_value)

        device_layout.addSpacing(12)

        # Security badge
        security_badge = QLabel(f"{ICONS.STATUS_SUCCESS} 此节点已通过 Tailscale 安全验证，支持所有高级自动化命令。")
        security_badge.setStyleSheet(f"color: {COLORS.on_surface_subtle}; font-size: 11px; background-color: {COLORS.surface_container_highest}; border-radius: 8px; padding: 12px;")
        security_badge.setWordWrap(True)
        device_layout.addWidget(security_badge)

        self._info_layout.addWidget(device_card)

        # Tip card
        tip_card = QFrame()
        tip_card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {COLORS.primary}, stop:1 {COLORS.primary_container});
                border-radius: 12px;
            }}
        """)
        tip_layout = QVBoxLayout(tip_card)
        tip_layout.setContentsMargins(24, 24, 24, 24)
        tip_layout.setSpacing(12)

        tip_title = QLabel(f"{ICONS.SECTION_TIPS} 专业提示")
        tip_title.setFont(QFont("Inter", 14, QFont.Weight.Bold))
        tip_title.setStyleSheet("color: white; letter-spacing: -0.01em;")
        tip_layout.addWidget(tip_title)

        tip_text = QLabel("启用「防止休眠」可以确保您的远程渲染或大规模数据下载任务不会因系统进入待机而中断。")
        tip_text.setStyleSheet("color: rgba(255,255,255,0.85); font-size: 12px; line-height: 1.5;")
        tip_text.setWordWrap(True)
        tip_layout.addWidget(tip_text)

        self._info_layout.addWidget(tip_card)
        self._info_layout.addStretch()

        self._content_layout.addLayout(self._info_layout, 1)
        layout.addLayout(self._content_layout)

        # Footer buttons
        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(16)
        footer_layout.addStretch()

        cancel_btn = QPushButton("取消")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS.surface_container_lowest};
                color: {COLORS.on_surface_subtle};
                border: 1px solid {COLORS.surface_container_high};
                border-radius: 10px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 14px;
                font-family: 'Inter', 'Segoe UI', 'Microsoft YaHei', 'PingFang SC', sans-serif;
            }}
            QPushButton:hover {{
                background-color: {COLORS.surface_container_high};
                border-color: {COLORS.surface_container_highest};
            }}
        """)
        cancel_btn.clicked.connect(self.cancelled.emit)
        footer_layout.addWidget(cancel_btn)

        save_btn = QPushButton("保存任务")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {COLORS.primary}, stop:1 {COLORS.primary_container});
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px 32px;
                font-weight: 600;
                font-size: 14px;
                font-family: 'Inter', 'Segoe UI', 'Microsoft YaHei', 'PingFang SC', sans-serif;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {COLORS.primary_container}, stop:1 {COLORS.primary});
            }}
        """)
        save_btn.clicked.connect(self._on_save)
        footer_layout.addWidget(save_btn)

        layout.addLayout(footer_layout)

        scroll_area.setWidget(content)
        main_layout.addWidget(scroll_area)

    def _on_type_changed(self, index: int):
        """Handle task type change."""
        is_fixed = index == 0
        self.days_label.setVisible(is_fixed)
        for btn in self.day_buttons:
            btn.setVisible(is_fixed)
        self.interval_frame.setVisible(not is_fixed)

    def set_task(self, task: Task | None):
        """Set task for editing, or None for new task."""
        self._task = task
        self._is_edit = task is not None

        if self._is_edit:
            self.title_label.setText("编辑任务详情")
        else:
            self.title_label.setText("新建任务")

        if task:
            self.name_input.setText(task.name)
            self.type_combo.setCurrentIndex(0 if task.task_type == "fixed" else 1)

            # Parse trigger time for new hour/minute/am_pm selectors
            if task.trigger_time:
                parts = task.trigger_time.replace(':', ' ').split()
                if len(parts) >= 2:
                    hour = int(parts[0])
                    minute = int(parts[1])
                    am_pm = "AM" if hour < 12 else "PM"
                    display_hour = hour if hour <= 12 else hour - 12
                    if display_hour == 0:
                        display_hour = 12
                    self.hour_spin.setValue(display_hour)
                    self.minute_spin.setValue(minute)
                    self.am_pm_combo.setCurrentIndex(0 if am_pm == "AM" else 1)
            else:
                self.hour_spin.setValue(2)
                self.minute_spin.setValue(30)
                self.am_pm_combo.setCurrentIndex(0)

            for i, btn in enumerate(self.day_buttons):
                btn.setChecked(
                    task.trigger_days is None or
                    i in (task.trigger_days or [])
                )

            self.interval_spin.setValue(task.interval_minutes or 30)
            self.action_combo.setCurrentIndex(
                0 if task.action == "prevent_sleep" else 1
            )
        else:
            # Reset to defaults
            self.name_input.clear()
            self.type_combo.setCurrentIndex(0)
            self.hour_spin.setValue(2)
            self.minute_spin.setValue(30)
            self.am_pm_combo.setCurrentIndex(0)
            for btn in self.day_buttons:
                btn.setChecked(True)
            self.interval_spin.setValue(30)
            self.action_combo.setCurrentIndex(0)

    def _on_save(self):
        """Handle save button click."""
        name = self.name_input.text().strip()
        if not name:
            return

        is_fixed = self.type_combo.currentIndex() == 0

        # Build trigger time from hour/minute/am_pm
        hour = self.hour_spin.value()
        minute = self.minute_spin.value()
        am_pm = self.am_pm_combo.currentText()

        if am_pm == "PM" and hour != 12:
            hour += 12
        elif am_pm == "AM" and hour == 12:
            hour = 0

        trigger_time = f"{hour:02d}:{minute:02d}"

        trigger_days = [
            i for i, btn in enumerate(self.day_buttons)
            if btn.isChecked()
        ] if is_fixed else None

        if trigger_days and len(trigger_days) == 7:
            trigger_days = None

        if self._task:
            task = Task(
                id=self._task.id,
                name=name,
                task_type="fixed" if is_fixed else "interval",
                trigger_time=trigger_time if is_fixed else None,
                trigger_days=trigger_days,
                interval_minutes=self.interval_spin.value() if not is_fixed else None,
                action="prevent_sleep" if self.action_combo.currentIndex() == 0 else "restore_sleep",
                enabled=self._task.enabled
            )
        else:
            task = Task(
                name=name,
                task_type="fixed" if is_fixed else "interval",
                trigger_time=trigger_time if is_fixed else None,
                trigger_days=trigger_days,
                interval_minutes=self.interval_spin.value() if not is_fixed else None,
                action="prevent_sleep" if self.action_combo.currentIndex() == 0 else "restore_sleep"
            )

        self.saved.emit(task)

    def resizeEvent(self, event):
        """Handle resize event to switch between horizontal and vertical layout."""
        super().resizeEvent(event)
        if not self._content_layout or not self._form_card or not self._info_layout:
            return

        width = event.size().width()
        current_direction = self._content_layout.direction()
        is_horizontal = current_direction == QBoxLayout.Direction.LeftToRight

        if width < self.RESPONSIVE_BREAKPOINT and is_horizontal:
            # Switch to vertical layout
            self._content_layout.removeWidget(self._form_card)
            self._content_layout.removeItem(self._info_layout)
            self._content_layout.setDirection(QBoxLayout.Direction.TopToBottom)
            self._content_layout.addWidget(self._form_card, 2)
            self._content_layout.addLayout(self._info_layout, 1)
        elif width >= self.RESPONSIVE_BREAKPOINT and not is_horizontal:
            # Switch to horizontal layout
            self._content_layout.removeWidget(self._form_card)
            self._content_layout.removeItem(self._info_layout)
            self._content_layout.setDirection(QBoxLayout.Direction.LeftToRight)
            self._content_layout.addWidget(self._form_card, 2)
            self._content_layout.addLayout(self._info_layout, 1)