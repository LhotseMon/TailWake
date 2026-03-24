"""System tray icon and menu."""
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction, QPixmap, QPainter, QColor
from PyQt6.QtCore import pyqtSignal, QObject, Qt

from styles import COLORS


def create_tray_icon() -> QIcon:
    """Create tray icon with multiple sizes."""
    icon = QIcon()
    sizes = [16, 32, 48, 64]

    for size in sizes:
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        margin = size // 8
        radius = size // 4

        painter.setBrush(QColor(COLORS.primary))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(margin, margin, size - 2*margin, size - 2*margin, radius, radius)

        painter.setPen(QColor(255, 255, 255))
        from PyQt6.QtGui import QFont
        font_size = int(size * 0.5)
        font = QFont("Inter", font_size, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "T")

        painter.end()

        icon.addPixmap(pixmap)

    return icon


class TrayIcon(QObject):
    """System tray icon manager."""

    # Signals
    show_window = pyqtSignal()
    quit_app = pyqtSignal()
    prevent_sleep = pyqtSignal()
    restore_sleep = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tray: QSystemTrayIcon | None = None
        self._menu: QMenu | None = None

    def create(self, icon_path: str = None):
        """Create the tray icon."""
        self._tray = QSystemTrayIcon()

        # Use provided icon path or create default icon
        if icon_path:
            self._tray.setIcon(QIcon(icon_path))
        else:
            self._tray.setIcon(create_tray_icon())

        self._tray.setToolTip("TailWake")

        # Create menu
        self._menu = QMenu()

        show_action = QAction("Open TailWake", self._menu)
        show_action.triggered.connect(self.show_window.emit)
        self._menu.addAction(show_action)

        self._menu.addSeparator()

        prevent_action = QAction("Prevent Sleep Now", self._menu)
        prevent_action.triggered.connect(self.prevent_sleep.emit)
        self._menu.addAction(prevent_action)

        restore_action = QAction("Restore Sleep", self._menu)
        restore_action.triggered.connect(self.restore_sleep.emit)
        self._menu.addAction(restore_action)

        self._menu.addSeparator()

        quit_action = QAction("Quit", self._menu)
        quit_action.triggered.connect(self.quit_app.emit)
        self._menu.addAction(quit_action)

        self._tray.setContextMenu(self._menu)
        self._tray.activated.connect(self._on_activated)

    def show(self):
        """Show the tray icon."""
        if self._tray:
            self._tray.show()

    def hide(self):
        """Hide the tray icon."""
        if self._tray:
            self._tray.hide()

    def set_tooltip(self, text: str):
        """Set tray tooltip text."""
        if self._tray:
            self._tray.setToolTip(text)

    def show_message(self, title: str, message: str):
        """Show a notification message."""
        if self._tray:
            self._tray.showMessage(title, message)

    def _on_activated(self, reason):
        """Handle tray icon activation."""
        from PyQt6.QtWidgets import QSystemTrayIcon
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_window.emit()