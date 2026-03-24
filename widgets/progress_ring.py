"""Circular progress indicator widget."""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QPen, QColor, QConicalGradient

from styles import COLORS


class ProgressRing(QWidget):
    """A circular progress ring widget."""

    def __init__(self, size: int = 120, parent=None):
        super().__init__(parent)
        self._progress = 0.0  # 0.0 to 1.0
        self._size = size
        self.setFixedSize(size, size)

    def setProgress(self, progress: float):
        """Set progress value (0.0 to 1.0)."""
        self._progress = max(0.0, min(1.0, progress))
        self.update()

    def getProgress(self) -> float:
        """Get current progress."""
        return self._progress

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Ring dimensions
        stroke_width = 6
        rect = QRectF(
            stroke_width / 2,
            stroke_width / 2,
            self._size - stroke_width,
            self._size - stroke_width
        )

        # Background ring - subtle
        bg_pen = QPen(QColor(COLORS.surface_container_high))
        bg_pen.setWidth(stroke_width)
        bg_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(bg_pen)
        painter.drawArc(rect, 0, 360 * 16)

        # Progress ring with success green gradient
        if self._progress > 0:
            gradient = QConicalGradient(
                self._size / 2,
                self._size / 2,
                90
            )
            gradient.setColorAt(0, QColor(COLORS.tertiary_fixed_dim))
            gradient.setColorAt(1, QColor("#6ffbbe"))

            progress_pen = QPen()
            progress_pen.setBrush(gradient)
            progress_pen.setWidth(stroke_width)
            progress_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(progress_pen)

            # Draw arc (Qt uses 1/16th degrees, start at top)
            span = int(360 * 16 * self._progress)
            painter.drawArc(rect, 90 * 16, -span)

        painter.end()