"""Tasks list page with responsive grid layout."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QGridLayout, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont
from typing import TYPE_CHECKING
from datetime import datetime

from models import Task
from styles import COLORS, ICONS
from widgets.task_card import TaskCardWrapper

if TYPE_CHECKING:
    from scheduler import TaskScheduler


class AddTaskPlaceholder(QWidget):
    """Dashed placeholder card for adding new tasks."""

    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        # Enable styled background for custom QWidget
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(f"""
            AddTaskPlaceholder {{
                background-color: #ffffff;
                border: 2px dashed {COLORS.outline};
                border-radius: 16px;
            }}
            AddTaskPlaceholder:hover {{
                border-color: {COLORS.primary};
            }}
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumWidth(280)
        self.setMinimumHeight(220)  # Match TaskCardWrapper minimum height
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)

        # Plus icon circle
        icon_container = QLabel(ICONS.ACTION_ADD)
        icon_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_container.setStyleSheet(f"""
            background-color: transparent;
            color: {COLORS.surface_container_highest};
            border: 1px solid {COLORS.surface_container_highest};
            border-radius: 24px;
            font-size: 24px;
            font-weight: 300;
        """)
        icon_container.setFixedSize(48, 48)
        layout.addWidget(icon_container, alignment=Qt.AlignmentFlag.AlignCenter)

        # Title
        title = QLabel("新建自动化策略")
        title.setStyleSheet(f"""
            color: {COLORS.on_surface_subtle};
            font-size: 14px;
            font-weight: 600;
        """)
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        # Subtitle
        subtitle = QLabel("点击定义新的时间规则")
        subtitle.setStyleSheet(f"""
            color: {COLORS.on_surface_subtle};
            font-size: 11px;
        """)
        layout.addWidget(subtitle, alignment=Qt.AlignmentFlag.AlignCenter)

        # Make clickable
        self.mousePressEvent = lambda e: self.clicked.emit()


class TasksPage(QWidget):
    """Page showing list of scheduled tasks with responsive grid."""

    # Signals
    add_task_clicked = pyqtSignal()
    edit_task_clicked = pyqtSignal(str)  # task_id
    delete_task_clicked = pyqtSignal(str)  # task_id
    task_toggled = pyqtSignal(str, bool)  # task_id, enabled

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tasks: list[Task] = []
        self._card_widgets = []  # Keep references to card widgets
        self._scheduler: "TaskScheduler | None" = None
        self._setup_ui()
        self._setup_timer()

    def _setup_ui(self):
        self.setStyleSheet(f"background-color: {COLORS.surface};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(48, 32, 48, 32)
        layout.setSpacing(24)

        # Header section
        header_section = QHBoxLayout()
        header_section.setSpacing(16)

        header_left = QVBoxLayout()
        header_left.setSpacing(8)

        title = QLabel("自动化任务列表")
        title.setFont(QFont("Inter", 28, QFont.Weight.ExtraBold))
        title.setStyleSheet(f"color: {COLORS.on_surface}; letter-spacing: -0.02em;")
        header_left.addWidget(title)

        subtitle = QLabel("管理您的桌面自动化策略与系统常驻任务")
        subtitle.setStyleSheet(f"color: {COLORS.on_surface_subtle}; font-size: 14px;")
        header_left.addWidget(subtitle)

        header_section.addLayout(header_left)
        header_section.addStretch()

        # Add task button
        add_btn = QPushButton("添加新任务")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet(f"""
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
        add_btn.clicked.connect(self.add_task_clicked.emit)
        header_section.addWidget(add_btn)

        layout.addLayout(header_section)

        # Scroll area for task grid
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("border: none; background: transparent;")

        # Task list container with light blue background for contrast
        task_list_container = QWidget()
        task_list_container.setObjectName("taskListContainer")
        task_list_container.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        task_list_container.setStyleSheet(f"""
            #taskListContainer {{
                background-color: {COLORS.surface_container};
                border-radius: 16px;
            }}
        """)
        task_list_layout = QVBoxLayout(task_list_container)
        task_list_layout.setContentsMargins(32, 32, 50, 32)  # Extra right margin for scrollbar (~17px)
        task_list_layout.setSpacing(0)

        # Set minimum width to ensure proper layout
        task_list_container.setMinimumWidth(600)

        # Task grid - will be updated on resize
        self.task_grid = QGridLayout()
        self.task_grid.setHorizontalSpacing(24)
        self.task_grid.setVerticalSpacing(16)  # Vertical spacing between rows
        self.task_grid.setContentsMargins(0, 8, 0, 8)
        self.task_grid.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        task_list_layout.addLayout(self.task_grid)

        # Empty state (inside container)
        self.empty_label = QLabel("暂无任务\n点击「添加新任务」创建您的第一个自动化策略")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet(f"color: {COLORS.on_surface_subtle}; font-size: 14px; background: transparent;")
        self.empty_label.hide()
        task_list_layout.addWidget(self.empty_label)

        scroll_area.setWidget(task_list_container)
        layout.addWidget(scroll_area)

        # Stats section
        self._create_stats_section(layout)

        layout.addStretch()

    def _create_stats_section(self, parent_layout):
        """Create statistics section at bottom."""
        stats_widget = QWidget()
        stats_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        stats_layout = QHBoxLayout(stats_widget)
        stats_layout.setContentsMargins(0, 16, 0, 0)
        stats_layout.setSpacing(24)

        # Active tasks stat
        active_stat = QWidget()
        active_stat.setMinimumWidth(180)
        active_stat.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS.surface_container_low};
                border-radius: 12px;
            }}
        """)
        active_layout = QVBoxLayout(active_stat)
        active_layout.setContentsMargins(24, 20, 24, 20)
        active_layout.setSpacing(4)
        active_title = QLabel("活跃任务")
        active_title.setStyleSheet(f"color: {COLORS.on_surface_subtle}; font-size: 11px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase;")
        active_layout.addWidget(active_title)
        active_count_row = QHBoxLayout()
        self.active_count = QLabel("02")
        self.active_count.setFont(QFont("Inter", 24, QFont.Weight.ExtraBold))
        self.active_count.setStyleSheet(f"color: {COLORS.on_surface}; letter-spacing: -0.02em;")
        active_count_row.addWidget(self.active_count)
        self.total_label = QLabel(" / 03")
        self.total_label.setStyleSheet(f"color: {COLORS.on_surface_subtle}; font-size: 12px; font-weight: 500;")
        active_count_row.addWidget(self.total_label)
        active_count_row.addStretch()
        active_layout.addLayout(active_count_row)
        stats_layout.addWidget(active_stat, 1)

        # Next execution stat
        next_stat = QWidget()
        next_stat.setMinimumWidth(200)
        next_stat.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS.surface_container_low};
                border-radius: 12px;
            }}
        """)
        next_layout = QVBoxLayout(next_stat)
        next_layout.setContentsMargins(24, 20, 24, 20)
        next_layout.setSpacing(4)
        next_title = QLabel("下次执行")
        next_title.setStyleSheet(f"color: {COLORS.on_surface_subtle}; font-size: 11px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase;")
        next_layout.addWidget(next_title)
        # Date row
        self.next_date = QLabel("--")
        self.next_date.setStyleSheet(f"color: {COLORS.on_surface_subtle}; font-size: 12px; font-weight: 500;")
        next_layout.addWidget(self.next_date)
        # Time row
        next_time_row = QHBoxLayout()
        self.next_time = QLabel("--:--")
        self.next_time.setFont(QFont("Inter", 24, QFont.Weight.ExtraBold))
        self.next_time.setStyleSheet(f"color: {COLORS.on_surface}; letter-spacing: -0.02em;")
        next_time_row.addWidget(self.next_time)
        next_time_row.addStretch()
        next_layout.addLayout(next_time_row)
        stats_layout.addWidget(next_stat, 1)

        # System status stat (spans 2 columns)
        system_stat = QWidget()
        system_stat.setMinimumWidth(300)
        system_stat.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #131b2e, stop:1 {COLORS.primary_container});
                border-radius: 12px;
            }}
        """)
        system_layout = QVBoxLayout(system_stat)
        system_layout.setContentsMargins(24, 20, 24, 20)
        system_layout.setSpacing(8)
        system_title = QLabel("系统状态")
        system_title.setStyleSheet(f"color: {COLORS.primary_fixed}; font-size: 11px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase;")
        system_layout.addWidget(system_title)
        status_row = QHBoxLayout()
        status_row.setSpacing(16)
        # Progress bar
        progress_bg = QLabel()
        progress_bg.setFixedSize(128, 8)
        progress_bg.setStyleSheet(f"""
            background-color: rgba(255,255,255,0.1);
            border-radius: 4px;
        """)
        status_row.addWidget(progress_bg)
        system_status = QLabel("运行稳定")
        system_status.setFont(QFont("Inter", 16, QFont.Weight.Bold))
        system_status.setStyleSheet("color: white; letter-spacing: -0.01em;")
        status_row.addWidget(system_status)
        status_row.addStretch()
        system_layout.addLayout(status_row)
        stats_layout.addWidget(system_stat, 2)

        parent_layout.addWidget(stats_widget)

    def set_tasks(self, tasks: list[Task]):
        """Set the task list."""
        self._tasks = tasks
        self._refresh_task_list()

    def set_scheduler(self, scheduler: "TaskScheduler"):
        """Set the scheduler reference for getting next run times."""
        self._scheduler = scheduler

    def _setup_timer(self):
        """Setup timer to periodically update next run time."""
        self._update_timer = QTimer(self)
        self._update_timer.timeout.connect(self._update_next_run_time)
        self._update_timer.start(60000)  # Update every minute

    def update_stats(self):
        """Update stats section (active count and next run time)."""
        active = sum(1 for t in self._tasks if t.enabled)
        self.active_count.setText(f"{active:02d}")
        self.total_label.setText(f" / {len(self._tasks):02d}")
        self._update_next_run_time()

    def _refresh_task_list(self):
        """Refresh the task list display."""
        # Clear existing cards from grid
        self._card_widgets.clear()
        while self.task_grid.count():
            item = self.task_grid.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        # Show/hide empty state
        self.empty_label.setVisible(len(self._tasks) == 0)

        # Add task cards
        for task in self._tasks:
            card = TaskCardWrapper(task)
            card.clicked.connect(self.edit_task_clicked.emit)
            card.delete_clicked.connect(self.delete_task_clicked.emit)
            card.toggle_clicked.connect(self.task_toggled.emit)
            self._card_widgets.append(card)

        # Add placeholder card
        self._placeholder = AddTaskPlaceholder()
        self._placeholder.clicked.connect(self.add_task_clicked.emit)

        # Layout cards
        self._layout_cards()

        # Update stats
        active = sum(1 for t in self._tasks if t.enabled)
        self.active_count.setText(f"{active:02d}")
        self.total_label.setText(f" / {len(self._tasks):02d}")

        # Update next execution time
        self._update_next_run_time()

    def _update_next_run_time(self):
        """Update the next run time display."""
        if not self._scheduler:
            self.next_date.setText("--")
            self.next_time.setText("--:--")
            return

        # Find the earliest next run time among enabled tasks
        earliest_time: datetime | None = None

        for task in self._tasks:
            if not task.enabled:
                continue
            next_run = self._scheduler.get_next_run_time(task.id)
            if next_run is not None:
                if earliest_time is None or next_run < earliest_time:
                    earliest_time = next_run

        if earliest_time:
            # Format date
            now = datetime.now()
            if earliest_time.date() == now.date():
                date_str = "今天"
            elif earliest_time.date().year == now.year:
                date_str = earliest_time.strftime("%m月%d日")
            else:
                date_str = earliest_time.strftime("%Y年%m月%d日")
            self.next_date.setText(date_str)
            self.next_time.setText(earliest_time.strftime("%H:%M"))
        else:
            self.next_date.setText("--")
            self.next_time.setText("--:--")

    def _layout_cards(self):
        """Layout cards in grid based on available width."""
        # Clear grid
        while self.task_grid.count():
            item = self.task_grid.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        # Calculate columns based on container width
        # self.width() is the page width, need to account for container padding (32*2=64) and grid margins (8*2=16)
        # Note: sidebar is already excluded from page width
        total_margins = 64 + 16
        available_width = self.width() - total_margins
        card_min_width = 300
        card_spacing = 24

        # Calculate how many cards fit
        cols = max(1, int((available_width + card_spacing) / (card_min_width + card_spacing)))

        # Limit to 4 columns max
        cols = min(cols, 4)

        # Debug: print column calculation
        print(f"DEBUG: width={self.width()}, available={available_width}, cols={cols}")

        # Reset column stretch factors
        for i in range(4):
            self.task_grid.setColumnStretch(i, 0)

        # Set equal stretch for used columns
        for i in range(cols):
            self.task_grid.setColumnStretch(i, 1)

        # Add task cards to grid
        row = 0
        col = 0
        for i, card in enumerate(self._card_widgets):
            self.task_grid.addWidget(card, row, col)
            col += 1
            if col >= cols:
                col = 0
                row += 1

        # Add placeholder
        self.task_grid.addWidget(self._placeholder, row, col)

    def resizeEvent(self, event):
        """Handle resize to re-layout cards."""
        super().resizeEvent(event)
        if hasattr(self, '_card_widgets') and self._card_widgets:
            self._layout_cards()