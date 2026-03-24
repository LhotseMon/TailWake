"""Countdown confirmation dialog."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPainter, QColor, QPen

from styles import COLORS, ICONS
from widgets.progress_ring import ProgressRing


class CountdownDialog(QDialog):
    """A dialog with countdown timer for task confirmation."""

    # Signals
    confirmed = pyqtSignal()
    cancelled = pyqtSignal()

    def __init__(
        self,
        task_name: str,
        action: str,
        countdown_seconds: int = 60,
        parent=None
    ):
        super().__init__(parent)
        self._countdown = countdown_seconds
        self._initial_countdown = countdown_seconds
        self._task_name = task_name
        self._action = action
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)

        self.setWindowTitle("执行确认")
        self.setFixedSize(560, 560)
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        self._setup_ui()

    def _setup_ui(self):
        # Main container with rounded corners
        container = QWidget(self)
        container.setObjectName("dialogContainer")
        container.setStyleSheet(f"""
            #dialogContainer {{
                background-color: {COLORS.surface_container_lowest};
                border-radius: 20px;
            }}
        """)
        container.setGeometry(0, 0, 560, 560)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(32)

        # Header with icon and title
        header_layout = QHBoxLayout()

        icon_label = QLabel(ICONS.STATUS_WARNING)
        icon_label.setStyleSheet(f"""
            background-color: rgba(232, 79, 79, 0.1);
            border-radius: 12px;
            padding: 12px;
            font-size: 24px;
        """)
        icon_label.setFixedSize(48, 48)
        header_layout.addWidget(icon_label)

        header_text = QVBoxLayout()
        title = QLabel(f"确认操作：{'开启防止休眠' if self._action == 'prevent_sleep' else '恢复休眠'}？")
        title.setFont(QFont("Inter", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS.on_surface}; letter-spacing: -0.02em;")
        header_text.addWidget(title)

        subtitle = QLabel("EXECUTION CONFIRMATION")
        subtitle.setStyleSheet(f"color: {COLORS.on_surface_subtle}; font-size: 11px; font-weight: 600; letter-spacing: 0.1em;")
        header_text.addWidget(subtitle)

        header_layout.addLayout(header_text)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Countdown circle
        countdown_container = QWidget()
        countdown_container.setFixedHeight(220)
        countdown_layout = QVBoxLayout(countdown_container)
        countdown_layout.setContentsMargins(0, 0, 0, 0)
        countdown_layout.setSpacing(0)

        self.progress_ring = ProgressRing(180)
        self.progress_ring.setProgress(1.0)
        countdown_layout.addWidget(self.progress_ring, alignment=Qt.AlignmentFlag.AlignCenter)

        # Spacer to position countdown text over progress ring
        countdown_layout.addSpacing(-100)

        self.countdown_label = QLabel(str(self._countdown))
        self.countdown_label.setFont(QFont("Inter", 64, QFont.Weight.Bold))
        self.countdown_label.setStyleSheet(f"color: {COLORS.on_surface}; letter-spacing: -0.02em;")
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        countdown_layout.addWidget(self.countdown_label)

        remaining_label = QLabel("SECONDS REMAINING")
        remaining_label.setStyleSheet(f"color: {COLORS.on_surface_subtle}; font-size: 11px; font-weight: 600; letter-spacing: 0.2em;")
        remaining_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        countdown_layout.addWidget(remaining_label)

        layout.addWidget(countdown_container)

        # Warning text
        warning_card = QWidget()
        warning_card.setStyleSheet(f"""
            background-color: {COLORS.surface_container_low};
            border-radius: 8px;
        """)
        warning_layout = QVBoxLayout(warning_card)
        warning_layout.setContentsMargins(20, 16, 20, 16)

        warning_text = QLabel("如果未进行任何操作，任务将在倒计时结束后自动执行。这可以防止系统在当前过程中进入休眠模式。")
        warning_text.setStyleSheet(f"color: {COLORS.on_surface_variant}; font-size: 13px; line-height: 1.5;")
        warning_text.setWordWrap(True)
        warning_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warning_layout.addWidget(warning_text)

        layout.addWidget(warning_card)

        # Task details
        details_layout = QHBoxLayout()
        details_layout.setContentsMargins(0, 0, 0, 8)
        target_label = QLabel("TARGET PROCESS")
        target_label.setStyleSheet(f"color: {COLORS.on_surface_subtle}; font-size: 11px; font-weight: 600; letter-spacing: 0.1em;")
        details_layout.addWidget(target_label)

        process_label = QLabel("sys_pwr_keep_alive")
        process_label.setStyleSheet(f"""
            background-color: {COLORS.surface_container_highest};
            color: {COLORS.primary};
            font-family: monospace;
            font-weight: 600;
            border-radius: 4px;
            padding: 4px 10px;
            font-size: 11px;
        """)
        details_layout.addWidget(process_label)
        details_layout.addStretch()
        layout.addLayout(details_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(16)

        confirm_btn = QPushButton(f"{ICONS.STATUS_SUCCESS} 立即确认")
        confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        confirm_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {COLORS.primary}, stop:1 {COLORS.primary_container});
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {COLORS.primary_container}, stop:1 {COLORS.primary});
            }}
        """)
        confirm_btn.clicked.connect(self._on_confirm)
        btn_layout.addWidget(confirm_btn)

        cancel_btn = QPushButton(f"{ICONS.STATUS_ERROR} 取消")
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
            }}
            QPushButton:hover {{
                background-color: {COLORS.surface_container_high};
                border-color: {COLORS.surface_container_highest};
            }}
        """)
        cancel_btn.clicked.connect(self._on_cancel)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def start_countdown(self):
        """Start the countdown timer."""
        self._timer.start(1000)
        self.raise_()
        self.activateWindow()
        self.show()

    def _tick(self):
        """Handle countdown tick."""
        self._countdown -= 1
        self.countdown_label.setText(str(self._countdown))

        # Update progress ring
        progress = self._countdown / self._initial_countdown
        self.progress_ring.setProgress(progress)

        if self._countdown <= 0:
            self._on_confirm()

    def _on_confirm(self):
        """Handle confirm action."""
        self._timer.stop()
        self.confirmed.emit()
        self.accept()

    def _on_cancel(self):
        """Handle cancel action."""
        self._timer.stop()
        self.cancelled.emit()
        self.reject()

    def closeEvent(self, event):
        """Handle close event."""
        self._timer.stop()
        event.accept()