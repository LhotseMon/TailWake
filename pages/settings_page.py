"""Settings page."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSlider,
    QSizePolicy, QScrollArea
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont

from models import AppConfig
from styles import COLORS
from widgets.toggle_switch import ToggleSwitch


class TimeSlider(QWidget):
    """A slider with label for time-based settings."""

    valueChanged = pyqtSignal(int)

    def __init__(self, min_val: int, max_val: int, default_val: int, suffix: str, parent=None):
        super().__init__(parent)
        self._suffix = suffix
        self._min = min_val
        self._max = max_val
        self._setup_ui(default_val)

    def _setup_ui(self, default_val: int):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Value label
        self.value_label = QLabel(f"{default_val}{self._suffix}")
        self.value_label.setFixedWidth(70)
        self.value_label.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS.surface_container_lowest};
                border: 1px solid {COLORS.outline};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                font-weight: 600;
                color: {COLORS.primary};
            }}
        """)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.value_label)

        # Slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(self._min)
        self.slider.setMaximum(self._max)
        self.slider.setValue(default_val)
        self.slider.setFixedWidth(150)
        self.slider.setCursor(Qt.CursorShape.PointingHandCursor)
        self.slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                background: {COLORS.surface_container_high};
                height: 6px;
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: {COLORS.primary};
                width: 18px;
                height: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }}
            QSlider::handle:horizontal:hover {{
                background: {COLORS.primary_container};
            }}
            QSlider::sub-page:horizontal {{
                background: {COLORS.primary};
                border-radius: 3px;
            }}
        """)
        self.slider.valueChanged.connect(self._on_slider_changed)
        layout.addWidget(self.slider)

    def _on_slider_changed(self, value: int):
        self.value_label.setText(f"{value}{self._suffix}")
        self.valueChanged.emit(value)

    def setValue(self, value: int):
        self.slider.setValue(value)

    def value(self) -> int:
        return self.slider.value()


class SettingsPage(QWidget):
    """Application settings page."""

    # Signals
    settings_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._config: AppConfig | None = None
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
        layout.setSpacing(24)

        # Title section
        header = QVBoxLayout()
        header.setSpacing(8)

        title = QLabel("设置")
        title.setFont(QFont("Inter", 28, QFont.Weight.ExtraBold))
        title.setStyleSheet(f"color: {COLORS.on_surface}; letter-spacing: -0.02em;")
        header.addWidget(title)

        subtitle = QLabel("自定义应用程序行为与系统偏好")
        subtitle.setStyleSheet(f"color: {COLORS.on_surface_subtle}; font-size: 14px;")
        header.addWidget(subtitle)

        layout.addLayout(header)

        # Settings sections
        layout.addWidget(self._create_section("通用", [
            ("启动时自动运行", "应用启动后自动开始保持唤醒功能", self._create_autostart_toggle),
        ]))

        layout.addWidget(self._create_section("任务行为", [
            ("倒计时时间", "自动确认前的等待时间", self._create_countdown_setting),
            ("恢复休眠时间", "任务结束后恢复休眠的等待时间", self._create_restore_setting),
        ]))

        layout.addWidget(self._create_section("隐私", [
            ("使用历史记录", "记录应用运行历史以便统计分析", self._create_history_toggle),
        ]))

        layout.addStretch()

        scroll_area.setWidget(content)
        main_layout.addWidget(scroll_area)

    def _create_section(
        self,
        title: str,
        items: list[tuple[str, str, callable]]
    ) -> QFrame:
        """Create a settings section."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS.surface_container_low};
                border-radius: 12px;
            }}
        """)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(0)

        # Section title
        section_title = QLabel(title)
        section_title.setFont(QFont("Inter", 12, QFont.Weight.Bold))
        section_title.setStyleSheet(f"""
            color: {COLORS.on_surface_subtle};
            letter-spacing: 0.05em;
            text-transform: uppercase;
        """)
        layout.addWidget(section_title)

        # Add spacing after section title
        layout.addSpacing(20)

        # Items with spacing
        for i, (label, description, creator) in enumerate(items):
            if i > 0:
                layout.addSpacing(16)

            item_widget = creator(label, description)
            layout.addWidget(item_widget)
            if i < len(items) - 1:
                layout.addSpacing(16)

        return frame

    def _create_setting_row(self, label: str, description: str, control: QWidget) -> QWidget:
        """Create a setting row with label, description and control."""
        widget = QWidget()
        widget.setStyleSheet(f"background: transparent;")

        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Left side: label and description
        left_layout = QVBoxLayout()
        left_layout.setSpacing(4)

        label_widget = QLabel(label)
        label_widget.setStyleSheet(f"""
            color: {COLORS.on_surface};
            font-size: 14px;
            font-weight: 600;
        """)
        left_layout.addWidget(label_widget)

        desc_widget = QLabel(description)
        desc_widget.setStyleSheet(f"""
            color: {COLORS.on_surface_subtle};
            font-size: 12px;
        """)
        left_layout.addWidget(desc_widget)

        layout.addLayout(left_layout, 1)
        layout.addWidget(control, 0, Qt.AlignmentFlag.AlignVCenter)

        return widget

    def _create_autostart_toggle(self, label: str, description: str) -> QWidget:
        """Create autostart toggle setting."""
        self.autostart_toggle = ToggleSwitch()
        self.autostart_toggle.toggled.connect(self._on_autostart_changed)
        return self._create_setting_row(label, description, self.autostart_toggle)

    def _create_countdown_setting(self, label: str, description: str) -> QWidget:
        """Create countdown duration setting."""
        self.countdown_slider = TimeSlider(10, 300, 60, "秒")
        self.countdown_slider.valueChanged.connect(self._on_setting_changed)
        return self._create_setting_row(label, description, self.countdown_slider)

    def _create_restore_setting(self, label: str, description: str) -> QWidget:
        """Create restore sleep setting."""
        self.restore_slider = TimeSlider(5, 120, 20, "分钟")
        self.restore_slider.valueChanged.connect(self._on_setting_changed)
        return self._create_setting_row(label, description, self.restore_slider)

    def _create_history_toggle(self, label: str, description: str) -> QWidget:
        """Create history tracking toggle."""
        self.history_toggle = ToggleSwitch()
        self.history_toggle.toggled.connect(self._on_setting_changed)
        return self._create_setting_row(label, description, self.history_toggle)

    def set_config(self, config: AppConfig):
        """Set the current configuration."""
        self._config = config
        self.autostart_toggle.setChecked(config.autostart)
        self.countdown_slider.setValue(config.countdown_seconds)
        self.restore_slider.setValue(config.restore_sleep_minutes)
        self.history_toggle.setChecked(config.track_history)

    def _on_autostart_changed(self, enabled: bool):
        """Handle autostart toggle."""
        import autostart
        if enabled:
            autostart.enable_autostart()
        else:
            autostart.disable_autostart()
        self._on_setting_changed()

    def _on_setting_changed(self):
        """Handle setting change."""
        if self._config:
            self._config.autostart = self.autostart_toggle.isChecked()
            self._config.countdown_seconds = self.countdown_slider.value()
            self._config.restore_sleep_minutes = self.restore_slider.value()
            self._config.track_history = self.history_toggle.isChecked()
            self.settings_changed.emit()