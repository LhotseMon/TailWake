"""TailWake application entry point."""
import sys
import logging
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFontDatabase, QFont, QIcon, QPixmap, QPainter, QColor

from main_window import MainWindow
from tray import TrayIcon
from styles import COLORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_fonts():
    """Load Inter font if available."""
    font_path = Path(__file__).parent / "resources" / "fonts" / "Inter-VariableFont.ttf"
    if font_path.exists():
        QFontDatabase.addApplicationFont(str(font_path))
        logger.info("Inter font loaded")
    else:
        logger.warning("Inter font not found, using system font")


def create_app_icon() -> QIcon:
    """Create application icon."""
    icon = QIcon()

    # Create multiple sizes for different contexts
    sizes = [16, 32, 48, 64, 128, 256]

    for size in sizes:
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw rounded rectangle background
        margin = size // 8
        radius = size // 4

        painter.setBrush(QColor(COLORS.primary))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(margin, margin, size - 2*margin, size - 2*margin, radius, radius)

        # Draw "T" letter or wake symbol
        painter.setPen(QColor(255, 255, 255))
        font_size = int(size * 0.5)
        font = QFont("Inter", font_size, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "T")

        painter.end()

        icon.addPixmap(pixmap)

    return icon


def main():
    """Main entry point."""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("TailWake")
    app.setApplicationVersion("1.0.0")
    app.setQuitOnLastWindowClosed(False)  # Keep running in tray

    # Set application icon
    app_icon = create_app_icon()
    app.setWindowIcon(app_icon)

    # Load fonts
    load_fonts()

    # Set application font with Chinese fallback
    font = QFont("Inter")
    font.setStyleHint(QFont.StyleHint.SansSerif)
    font.setFamilies(["Inter", "Segoe UI", "Microsoft YaHei", "PingFang SC", "SimHei", "sans-serif"])
    app.setFont(font)

    # Create main window
    window = MainWindow()
    window.setWindowIcon(app_icon)

    # Create tray icon
    tray = TrayIcon()
    tray.create()
    tray.show()
    tray.show_window.connect(window.show)
    tray.show_window.connect(window.activateWindow)
    tray.quit_app.connect(app.quit)

    # Handle window close
    def on_close(event):
        # Minimize to tray instead of closing
        window.hide()
        tray.show_message("TailWake", "Running in background")

    window.closeEvent = on_close

    # Show window on first launch
    window.show()

    logger.info("TailWake started")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()