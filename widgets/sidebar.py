"""Navigation sidebar widget."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont

from styles import COLORS, get_sidebar_button_style


class Sidebar(QWidget):
    """Left navigation sidebar."""

    # Signals
    dashboard_clicked = pyqtSignal()
    tasks_clicked = pyqtSignal()
    settings_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(256)
        self._active_page = "dashboard"
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 24, 16, 20)
        layout.setSpacing(4)

        # App title area at top
        title_widget = QWidget()
        title_layout = QVBoxLayout(title_widget)
        title_layout.setContentsMargins(16, 0, 0, 0)
        title_layout.setSpacing(2)

        title = QLabel("TailWake")
        title.setFont(QFont("Inter", 20, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS.primary_container}; letter-spacing: -0.02em;")
        title_layout.addWidget(title)

        subtitle = QLabel("WINDOWS DESKTOP")
        subtitle.setStyleSheet(f"""
            color: {COLORS.on_surface_subtle};
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.08em;
        """)
        title_layout.addWidget(subtitle)

        layout.addWidget(title_widget)

        # Smaller spacer between title and nav
        layout.addSpacerItem(QSpacerItem(0, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

        # Navigation buttons - grouped at top
        self.dashboard_btn = self._create_nav_button(
            "仪表盘",
            "dashboard",
            self.dashboard_clicked
        )
        layout.addWidget(self.dashboard_btn)

        self.tasks_btn = self._create_nav_button(
            "任务",
            "tasks",
            self.tasks_clicked
        )
        layout.addWidget(self.tasks_btn)

        self.settings_btn = self._create_nav_button(
            "设置",
            "settings",
            self.settings_clicked
        )
        layout.addWidget(self.settings_btn)

        # Push remaining space to bottom
        layout.addStretch()

        # Set initial active state
        self.set_active_page("dashboard")

    def _create_nav_button(
        self,
        text: str,
        page_id: str,
        signal: pyqtSignal
    ) -> QPushButton:
        """Create a navigation button."""
        btn = QPushButton(text)
        btn.setProperty("page_id", page_id)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(lambda: self._on_nav_click(page_id, signal))
        return btn

    def _on_nav_click(self, page_id: str, signal: pyqtSignal):
        """Handle navigation button click."""
        self.set_active_page(page_id)
        signal.emit()

    def set_active_page(self, page_id: str):
        """Set the active page indicator."""
        self._active_page = page_id

        for btn in [self.dashboard_btn, self.tasks_btn, self.settings_btn]:
            is_active = btn.property("page_id") == page_id
            btn.setStyleSheet(get_sidebar_button_style(is_active))