"""Design system: colors, fonts, and QSS stylesheets."""
from dataclasses import dataclass


@dataclass
class Colors:
    """Color palette for the Digital Architect design system."""
    # Surface hierarchy
    surface: str = "#faf8ff"
    surface_container_low: str = "#f2f3ff"
    surface_container: str = "#eaedff"
    surface_container_high: str = "#e2e7ff"
    surface_container_highest: str = "#dae2fd"
    surface_container_lowest: str = "#ffffff"

    # Primary colors
    primary: str = "#141779"
    primary_container: str = "#2d328f"
    primary_fixed: str = "#e0e0ff"
    primary_fixed_dim: str = "#bfc2ff"

    # Status colors
    tertiary: str = "#002f1e"
    tertiary_fixed_dim: str = "#22c087"  # Success/active green - brighter for better contrast
    tertiary_fixed: str = "#6ffbbe"
    tertiary_container: str = "#e8f5e9"  # Light green background
    error: str = "#dc2626"  # Darker red for better contrast
    error_container: str = "#fee2e2"
    warning: str = "#f59e0b"  # Add warning color
    info: str = "#3b82f6"     # Add info color

    # Text colors - enhanced contrast
    on_surface: str = "#1a1a2e"          # Darker for better readability
    on_surface_variant: str = "#4a4a5c"  # Darker gray
    on_surface_subtle: str = "#6b6b7b"   # New: for secondary text
    on_primary: str = "#ffffff"
    on_primary_container: str = "#9ba1ff"
    on_tertiary: str = "#ffffff"
    on_tertiary_container: str = "#145636"
    on_tertiary_fixed_variant: str = "#145636"
    secondary: str = "#515f74"
    on_secondary_container: str = "#57657a"
    outline: str = "#9ca3af"             # New: darker outline for visibility
    outline_variant: str = "#a1a1aa"     # Darker than before
    surface_tint: str = "#4f54b1"

    # Gradients (for QLinearGradient)
    @property
    def primary_gradient(self) -> tuple[str, str]:
        return (self.primary, self.primary_container)


COLORS = Colors()


@dataclass(frozen=True)
class Icons:
    """Icon system - unified emoji-based icons for consistent UI."""
    # Task type icons
    TASK_PREVENT_SLEEP: str = "👁"      # Keep awake / prevent sleep
    TASK_RESTORE_SLEEP: str = "🔄"     # Restore sleep
    TASK_INTERVAL: str = "⏱"          # Interval/recurring task
    TASK_SCHEDULED: str = "🕐"         # Scheduled time task

    # Status icons
    STATUS_SUCCESS: str = "✓"          # Success / verified / active
    STATUS_ERROR: str = "✕"            # Error / failed / cancelled
    STATUS_WARNING: str = "⚠️"         # Warning / caution
    STATUS_INFO: str = "ℹ️"            # Information
    STATUS_DISABLED: str = "⊘"         # Disabled / blocked

    # Action icons
    ACTION_ADD: str = "+"              # Add new item
    ACTION_EDIT: str = "✎"             # Edit item
    ACTION_DELETE: str = "🗑"          # Delete item
    ACTION_CONFIRM: str = "✓"          # Confirm action
    ACTION_CANCEL: str = "✕"           # Cancel action
    ACTION_SETTINGS: str = "⚙️"        # Settings
    ACTION_REFRESH: str = "↻"          # Refresh / reload

    # Section/Category icons
    SECTION_CONFIG: str = "📝"         # Configuration
    SECTION_NETWORK: str = "🌐"        # Network / connectivity
    SECTION_SECURITY: str = "🔒"       # Security
    SECTION_TIME: str = "⏱"            # Time / duration
    SECTION_CLOUD: str = "☁️"          # Cloud / online
    SECTION_TIPS: str = "💡"           # Tips / hints
    SECTION_DEVICE: str = "💻"         # Device / computer

    # Navigation icons
    NAV_DASHBOARD: str = "◉"           # Dashboard / overview
    NAV_TASKS: str = "☰"               # Tasks / list
    NAV_SETTINGS: str = "⚙️"           # Settings


ICONS = Icons()


def get_app_stylesheet() -> str:
    """Get the main application stylesheet."""
    return f"""
    /* Global font - Inter with fallbacks */
    QWidget {{
        font-family: 'Inter', 'Segoe UI', 'Microsoft YaHei', 'PingFang SC', 'Hiragino Sans GB', sans-serif;
        font-size: 14px;
        color: {COLORS.on_surface};
    }}

    /* Typography scale */
    QLabel#display {{
        font-size: 44px;
        font-weight: 700;
        color: {COLORS.on_surface};
        letter-spacing: -0.02em;
    }}

    QLabel#headline {{
        font-size: 24px;
        font-weight: 600;
        color: {COLORS.on_surface};
        letter-spacing: -0.01em;
    }}

    QLabel#title {{
        font-size: 18px;
        font-weight: 600;
        color: {COLORS.on_surface};
    }}

    QLabel#body {{
        font-size: 14px;
        color: {COLORS.on_surface};
    }}

    QLabel#labelSmall {{
        font-size: 12px;
        font-weight: 600;
        color: {COLORS.on_surface_variant};
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}

    /* Main window background */
    QMainWindow, QWidget#mainContent {{
        background-color: {COLORS.surface};
    }}

    /* Sidebar */
    QWidget#sidebar {{
        background-color: {COLORS.surface};
        border-right: none;
    }}

    /* Page title */
    QLabel#titleLabel {{
        font-size: 36px;
        font-weight: 700;
        color: {COLORS.on_surface};
        letter-spacing: -0.02em;
    }}

    /* Buttons */
    QPushButton {{
        background-color: {COLORS.surface_container_lowest};
        border: 1px solid {COLORS.surface_container_high};
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        color: {COLORS.on_surface};
    }}

    QPushButton:hover {{
        background-color: {COLORS.surface_container_high};
        border-color: {COLORS.surface_container_highest};
    }}

    QPushButton:pressed {{
        background-color: {COLORS.surface_container_highest};
    }}

    QPushButton#primaryButton {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 {COLORS.primary}, stop:1 {COLORS.primary_container});
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 600;
    }}

    QPushButton#primaryButton:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 {COLORS.primary_container}, stop:1 {COLORS.primary});
    }}

    /* Cards */
    QWidget#card {{
        background-color: {COLORS.surface_container_lowest};
        border-radius: 16px;
        border: 1px solid {COLORS.surface_container_high};
    }}

    QWidget#card:hover {{
        background-color: {COLORS.surface_container_high};
        border-color: {COLORS.surface_container_highest};
    }}

    /* Input fields */
    QLineEdit, QSpinBox, QComboBox {{
        background-color: {COLORS.surface_container_highest};
        border: 1px solid transparent;
        border-radius: 8px;
        padding: 14px;
        color: {COLORS.on_surface};
        font-family: 'Inter', 'Segoe UI', 'Microsoft YaHei', 'PingFang SC', sans-serif;
    }}

    QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
        background-color: {COLORS.primary_fixed};
        border: 2px solid {COLORS.primary};
    }}

    /* Labels */
    QLabel#subtitleLabel {{
        font-size: 14px;
        color: {COLORS.secondary};
    }}

    QLabel#labelSmall {{
        font-size: 12px;
        font-weight: 600;
        color: {COLORS.on_surface_variant};
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}

    /* Scrollbar */
    QScrollBar:vertical {{
        background: transparent;
        width: 6px;
        margin: 0;
    }}

    QScrollBar::handle:vertical {{
        background: {COLORS.surface_container_highest};
        border-radius: 3px;
        min-height: 20px;
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}

    /* ComboBox dropdown */
    QComboBox::drop-down {{
        border: none;
        padding-right: 12px;
    }}

    QComboBox::down-arrow {{
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 6px solid {COLORS.on_surface_variant};
        margin-right: 8px;
    }}

    QComboBox QAbstractItemView {{
        background-color: {COLORS.surface_container_lowest};
        border: none;
        border-radius: 6px;
        selection-background-color: {COLORS.surface_container_high};
    }}
    """


def get_sidebar_button_style(active: bool = False) -> str:
    """Get style for sidebar navigation button."""
    if active:
        return f"""
            QPushButton {{
                background-color: {COLORS.surface_container_lowest};
                color: {COLORS.primary_container};
                border-radius: 10px;
                padding: 12px 16px;
                text-align: left;
                font-weight: 600;
                border-left: 3px solid {COLORS.primary_container};
            }}
        """
    return f"""
        QPushButton {{
            background-color: transparent;
            color: {COLORS.on_surface_variant};
            border-radius: 10px;
            padding: 12px 16px;
            text-align: left;
            border-left: 3px solid transparent;
        }}
        QPushButton:hover {{
            background-color: {COLORS.surface_container_high};
            color: {COLORS.primary_container};
        }}
    """