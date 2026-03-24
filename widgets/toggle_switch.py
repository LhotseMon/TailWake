"""Custom toggle switch widget."""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal, pyqtProperty, QPropertyAnimation, QRect, QEasingCurve
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush

from styles import COLORS


class ToggleSwitch(QWidget):
    """A custom toggle switch widget."""

    toggled = pyqtSignal(bool)

    def __init__(self, label: str = "", parent=None):
        super().__init__(parent)
        self._checked = False
        self._label = label
        self._anim_offset = 0
        self._animation = QPropertyAnimation(self, b"anim_offset", self)
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.setFixedHeight(24)
        self.setMinimumWidth(44)

        if label:
            self._setup_with_label()
        else:
            self.setCursor(Qt.CursorShape.PointingHandCursor)

    def _setup_with_label(self):
        """Setup with a label on the left."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        label_widget = QLabel(self._label)
        label_widget.setStyleSheet(f"color: {COLORS.on_surface};")
        layout.addWidget(label_widget)
        layout.addStretch()

        self._toggle_only = ToggleSwitch()
        self._toggle_only.toggled.connect(self.toggled.emit)
        layout.addWidget(self._toggle_only)

        self._setChecked = self._toggle_only._setChecked
        self.isChecked = self._toggle_only.isChecked
        self.setChecked = self._toggle_only.setChecked

    def get_anim_offset(self):
        return self._anim_offset

    def set_anim_offset(self, value):
        self._anim_offset = value
        self.update()

    anim_offset = pyqtProperty(int, get_anim_offset, set_anim_offset)

    def isChecked(self) -> bool:
        return self._checked

    def setChecked(self, checked: bool):
        if self._checked != checked:
            self._checked = checked
            self._start_animation()
            self.toggled.emit(checked)

    def _setChecked(self, checked: bool):
        """Internal setter without emitting signal."""
        if self._checked != checked:
            self._checked = checked
            self._start_animation()

    def _start_animation(self):
        """Start the toggle animation."""
        self._animation.stop()
        if self._checked:
            self._animation.setStartValue(0)
            self._animation.setEndValue(self.width() - 24)
        else:
            self._animation.setStartValue(self.width() - 24)
            self._animation.setEndValue(0)
        self._animation.start()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setChecked(not self._checked)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background track
        track_color = QColor(COLORS.primary) if self._checked else QColor(COLORS.outline_variant)
        track_color.setAlpha(80 if not self._checked else 255)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(track_color))
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 12, 12)

        # Knob
        knob_rect = QRect(
            int(2 + self._anim_offset),
            2,
            20,
            20
        )
        painter.setBrush(QBrush(QColor("#ffffff")))
        painter.drawEllipse(knob_rect)