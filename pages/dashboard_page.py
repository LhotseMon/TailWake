"""Main dashboard page."""
from datetime import date
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QFrame, QPushButton,
    QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont

from styles import COLORS, ICONS
from widgets.progress_ring import ProgressRing
from tailscale_status import get_tailscale_status, TailscaleInfo
from history_tracker import get_weekly_history, get_total_active_hours, get_online_rate
from power_control import is_sleep_prevented


class StatCard(QWidget):
    """A small statistic card."""

    def __init__(self, title: str, value: str, subtitle: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self._setup_ui(title, value, subtitle)

    def _setup_ui(self, title: str, value: str, subtitle: str):
        self.setStyleSheet(f"""
            QWidget#card {{
                background-color: {COLORS.surface_container_low};
                border-radius: 16px;
                border: 1px solid {COLORS.surface_container};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(12)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            font-size: 12px;
            font-weight: 600;
            color: {COLORS.on_surface_subtle};
            text-transform: uppercase;
            letter-spacing: 0.08em;
        """)
        layout.addWidget(title_label)

        value_label = QLabel(value)
        value_label.setFont(QFont("Inter", 36, QFont.Weight.ExtraBold))
        value_label.setStyleSheet(f"color: {COLORS.on_surface}; letter-spacing: -0.02em;")
        layout.addWidget(value_label)

        if subtitle:
            sub_label = QLabel(subtitle)
            sub_label.setStyleSheet(f"color: {COLORS.secondary}; font-size: 12px;")
            layout.addWidget(sub_label)


class QuickActionCard(QWidget):
    """Quick action card for dashboard."""

    clicked = pyqtSignal()

    def __init__(self, icon_text: str, title: str, description: str, parent=None):
        super().__init__(parent)
        self._setup_ui(icon_text, title, description)

    def _setup_ui(self, icon_text: str, title: str, description: str):
        self.setStyleSheet(f"""
            QuickActionCard {{
                background-color: {COLORS.surface_container_low};
                border-radius: 12px;
                border: 1px solid {COLORS.surface_container};
            }}
            QuickActionCard:hover {{
                background-color: {COLORS.surface_container};
            }}
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(140)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)

        # Icon placeholder
        icon_label = QLabel(icon_text)
        icon_label.setStyleSheet(f"""
            background-color: {COLORS.surface_container_lowest};
            color: {COLORS.primary};
            border-radius: 10px;
            padding: 14px;
            font-size: 22px;
        """)
        icon_label.setFixedSize(52, 52)
        layout.addWidget(icon_label)

        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Inter", 14, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {COLORS.on_surface}; letter-spacing: -0.01em;")
        layout.addWidget(title_label)

        # Description
        desc_label = QLabel(description)
        desc_label.setStyleSheet(f"color: {COLORS.on_surface_variant}; font-size: 13px; line-height: 1.5;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

    def mousePressEvent(self, event):
        """Handle mouse press to emit clicked signal."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class DashboardPage(QWidget):
    """Main dashboard showing status and statistics."""

    # Signals for navigation and actions
    navigate_to_tasks = pyqtSignal()
    navigate_to_settings = pyqtSignal()
    toggle_sleep_prevention = pyqtSignal(bool)  # True = prevent, False = restore

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dashboardPage")
        self._setup_ui()
        self._start_status_refresh()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create scroll area for responsive layout
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: {COLORS.surface};
                border: none;
            }}
            QScrollArea > QWidget > QWidget {{
                background-color: {COLORS.surface};
            }}
        """)

        # Content widget inside scroll area
        content = QWidget()
        content.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        layout = QVBoxLayout(content)
        layout.setContentsMargins(48, 32, 48, 48)
        layout.setSpacing(24)

        # Page header with status indicator
        header_section = QVBoxLayout()
        header_section.setSpacing(12)

        # Status indicator row
        status_header = QHBoxLayout()
        self.status_dot = QLabel()
        self.status_dot.setFixedSize(10, 10)
        self.status_dot.setStyleSheet(f"""
            background-color: {COLORS.tertiary_fixed_dim};
            border-radius: 5px;
        """)
        status_header.addWidget(self.status_dot)

        status_tag = QLabel("系统当前运行状态")
        status_tag.setStyleSheet(f"""
            color: {COLORS.on_surface_subtle};
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-left: 8px;
        """)
        status_header.addWidget(status_tag)
        status_header.addStretch()
        header_section.addLayout(status_header)

        # Main title
        self.status_label = QLabel("保持唤醒状态：开启")
        self.status_label.setFont(QFont("Inter", 44, QFont.Weight.ExtraBold))
        self.status_label.setStyleSheet(f"color: {COLORS.on_surface}; letter-spacing: -0.02em;")
        header_section.addWidget(self.status_label)

        # Description
        self.desc_label = QLabel("自动睡眠已禁用。该设备将持续响应 Tailscale 网络请求并保持节点活跃。")
        self.desc_label.setStyleSheet(f"color: {COLORS.on_surface_variant}; font-size: 14px; line-height: 1.5;")
        self.desc_label.setWordWrap(True)
        header_section.addWidget(self.desc_label)

        # Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(16)

        self.disable_btn = QPushButton("立即禁用")
        self.disable_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.disable_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {COLORS.primary}, stop:1 {COLORS.primary_container});
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 14px;
                font-family: 'Inter', 'Segoe UI', 'Microsoft YaHei', 'PingFang SC', sans-serif;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {COLORS.primary_container}, stop:1 {COLORS.primary});
            }}
        """)
        self.disable_btn.clicked.connect(self._on_toggle_btn_clicked)
        btn_layout.addWidget(self.disable_btn)

        self.settings_btn = QPushButton("运行计划设置")
        self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS.surface_container_high};
                color: {COLORS.primary};
                border: 1px solid {COLORS.surface_container_high};
                border-radius: 10px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 14px;
                font-family: 'Inter', 'Segoe UI', 'Microsoft YaHei', 'PingFang SC', sans-serif;
            }}
            QPushButton:hover {{
                background-color: {COLORS.surface_container_highest};
                border-color: {COLORS.outline};
            }}
        """)
        self.settings_btn.clicked.connect(lambda: self.navigate_to_tasks.emit())
        btn_layout.addWidget(self.settings_btn)
        btn_layout.addStretch()
        header_section.addLayout(btn_layout)

        layout.addLayout(header_section)

        # Hero section - Network card and Stats sidebar
        hero_layout = QHBoxLayout()
        hero_layout.setSpacing(24)

        # Left: Network info card
        self._create_network_card(hero_layout)

        # Right: Stats sidebar
        stats_sidebar = self._create_stats_sidebar()
        hero_layout.addWidget(stats_sidebar, 1)

        layout.addLayout(hero_layout)

        # Quick Actions section
        actions_label = QLabel("快速操作")
        actions_label.setFont(QFont("Inter", 18, QFont.Weight.Bold))
        actions_label.setStyleSheet(f"color: {COLORS.on_surface};")
        layout.addWidget(actions_label)

        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(20)

        # Quick action cards with better icons
        prevent_card = QuickActionCard(
            "⏻", "立即保持唤醒",
            "一键覆盖系统设置，防止任何形式的休眠进入。"
        )
        prevent_card.clicked.connect(lambda: self._on_quick_action("prevent"))

        restore_card = QuickActionCard(
            "◐", "正常睡眠模式",
            "恢复系统默认电源策略，允许设备在空闲时进入低功耗。"
        )
        restore_card.clicked.connect(lambda: self._on_quick_action("restore"))

        schedule_card = QuickActionCard(
            "◷", "定时任务设置",
            "配置基于时间的自动唤醒逻辑，如工作时间保持活跃。"
        )
        schedule_card.clicked.connect(lambda: self.navigate_to_tasks.emit())

        config_card = QuickActionCard(
            "⚙", "节点配置",
            "管理当前设备的 Tailscale 鉴权密钥与子网路由设置。"
        )
        config_card.clicked.connect(lambda: self.navigate_to_settings.emit())

        actions_layout.addWidget(prevent_card)
        actions_layout.addWidget(restore_card)
        actions_layout.addWidget(schedule_card)
        actions_layout.addWidget(config_card)

        layout.addLayout(actions_layout)

        # Running history section - horizontal layout with history chart and node config
        history_section = QHBoxLayout()
        history_section.setSpacing(24)

        # Left: History chart card
        history_card = self._create_history_card()
        history_section.addWidget(history_card, 2)

        # Right: Node config card
        config_card = self._create_node_config_card()
        history_section.addWidget(config_card, 1)

        layout.addLayout(history_section)

        layout.addStretch()

        # Set scroll area content
        scroll_area.setWidget(content)
        main_layout.addWidget(scroll_area)

    def _create_network_card(self, parent_layout):
        """Create network info card."""
        network_frame = QFrame()
        network_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1f3a, stop:1 {COLORS.primary_container});
                border-radius: 16px;
            }}
        """)
        network_frame.setMinimumHeight(260)
        network_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        network_layout = QVBoxLayout(network_frame)
        network_layout.setContentsMargins(28, 28, 28, 28)
        network_layout.setSpacing(18)

        # Header
        header = QLabel(f"{ICONS.SECTION_NETWORK} 网络节点信息")
        header.setStyleSheet(f"color: {COLORS.primary_fixed}; font-weight: 700; font-size: 12px; letter-spacing: 0.05em; text-transform: uppercase;")
        network_layout.addWidget(header)

        # IP Address
        ip_label = QLabel("Tailscale IPv4")
        ip_label.setStyleSheet(f"color: rgba(255,255,255,0.5); font-size: 10px; font-weight: 500; letter-spacing: 0.05em;")
        network_layout.addWidget(ip_label)

        self.ip_value = QLabel("100.82.145.21")
        self.ip_value.setFont(QFont("Inter", 26, QFont.Weight.Bold))
        self.ip_value.setStyleSheet("color: white; font-family: monospace; letter-spacing: -0.02em;")
        network_layout.addWidget(self.ip_value)

        network_layout.addSpacing(20)

        # Tunnel status
        tunnel_label = QLabel("加密隧道状态")
        tunnel_label.setStyleSheet(f"color: rgba(255,255,255,0.5); font-size: 10px; font-weight: 500; letter-spacing: 0.05em;")
        network_layout.addWidget(tunnel_label)

        self.tunnel_status = QLabel(f"{ICONS.STATUS_SUCCESS} WireGuard 活跃")
        self.tunnel_status.setStyleSheet("color: white; font-size: 16px; font-weight: 500;")
        network_layout.addWidget(self.tunnel_status)

        network_layout.addStretch()

        # Footer
        footer = QLabel("最后握手: 2分钟前    内网在线")
        footer.setStyleSheet(f"color: rgba(255,255,255,0.5); font-size: 11px;")
        network_layout.addWidget(footer)

        parent_layout.addWidget(network_frame, 2)

    def _create_history_card(self) -> QWidget:
        """Create running history chart card."""
        card = QWidget()
        card.setStyleSheet(f"background-color: {COLORS.surface_container_low}; border-radius: 16px;")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("运行时间历史")
        title.setFont(QFont("Inter", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS.on_surface}; letter-spacing: -0.01em;")
        header_layout.addWidget(title)

        subtitle = QLabel("过去 7 天的活跃小时统计")
        subtitle.setStyleSheet(f"color: {COLORS.on_surface_subtle}; font-size: 13px;")
        header_layout.addWidget(subtitle)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Bar chart placeholder
        bars_widget = QWidget()
        bars_widget.setFixedHeight(140)
        bars_layout = QHBoxLayout(bars_widget)
        bars_layout.setSpacing(12)

        days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        heights = [40, 65, 55, 90, 70, 85, 80]

        for i, (day, height) in enumerate(zip(days, heights)):
            bar_container = QVBoxLayout()
            bar_container.setSpacing(8)

            bar = QLabel()
            bar.setFixedHeight(int(height * 1.2))
            bar.setStyleSheet(f"""
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS.primary_fixed}, stop:1 {COLORS.primary_container});
                border-radius: 4px;
            """)
            bar_container.addWidget(bar, alignment=Qt.AlignmentFlag.AlignBottom)

            day_label = QLabel(day)
            day_label.setStyleSheet(f"color: {COLORS.on_surface_subtle}; font-size: 12px; font-weight: 500;")
            day_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            bar_container.addWidget(day_label)

            bars_layout.addLayout(bar_container)

        layout.addWidget(bars_widget)
        return card

    def _create_node_config_card(self) -> QWidget:
        """Create node configuration card."""
        card = QWidget()
        card.setStyleSheet(f"background-color: {COLORS.surface_container_low}; border-radius: 16px;")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)

        # Header
        title = QLabel("节点配置")
        title.setFont(QFont("Inter", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS.on_surface}; letter-spacing: -0.01em;")
        layout.addWidget(title)

        # Config items
        configs = [
            ("鉴权密钥", "已配置", True),
            ("子网路由", "未启用", False),
            ("出口节点", "未设置", False),
            ("DNS 配置", "自动", True),
        ]

        for name, value, is_active in configs:
            item = QWidget()
            item_layout = QHBoxLayout(item)
            item_layout.setContentsMargins(0, 8, 0, 8)
            item_layout.setSpacing(12)

            # Status dot
            dot = QLabel()
            dot.setFixedSize(8, 8)
            dot.setStyleSheet(f"""
                background-color: {COLORS.tertiary_fixed_dim if is_active else COLORS.outline_variant};
                border-radius: 4px;
            """)
            item_layout.addWidget(dot)

            # Name
            name_label = QLabel(name)
            name_label.setStyleSheet(f"color: {COLORS.on_surface_subtle}; font-size: 13px;")
            item_layout.addWidget(name_label)

            item_layout.addStretch()

            # Value
            value_label = QLabel(value)
            value_label.setStyleSheet(f"""
                color: {COLORS.tertiary_fixed_dim if is_active else COLORS.on_surface_variant};
                font-size: 13px;
                font-weight: 600;
            """)
            item_layout.addWidget(value_label)

            layout.addWidget(item)

        layout.addStretch()

        # Configure button
        self.config_btn = QPushButton("配置节点")
        self.config_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.config_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS.surface_container_lowest};
                color: {COLORS.primary};
                border: 1px solid {COLORS.surface_container_high};
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {COLORS.surface_container_high};
                border-color: {COLORS.outline};
            }}
        """)
        self.config_btn.clicked.connect(lambda: self.navigate_to_settings.emit())
        layout.addWidget(self.config_btn)

        return card

    def _create_stats_sidebar(self) -> QWidget:
        """Create statistics sidebar."""
        sidebar = QWidget()
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(20)

        # Total hours card
        hours_card = QWidget()
        hours_card.setStyleSheet(f"background-color: {COLORS.surface_container_low}; border-radius: 16px;")
        hours_layout = QVBoxLayout(hours_card)
        hours_layout.setContentsMargins(28, 28, 28, 28)
        hours_layout.setSpacing(12)

        hours_title = QLabel(f"{ICONS.SECTION_TIME} 唤醒总时长")
        hours_title.setStyleSheet(f"color: {COLORS.on_surface_subtle}; font-size: 12px; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase;")
        hours_layout.addWidget(hours_title)

        weekly = get_weekly_history()
        weekly_hours = sum(r.active_hours for r in weekly)
        hours_value = QLabel(f"{weekly_hours:.0f}h")
        hours_value.setFont(QFont("Inter", 36, QFont.Weight.ExtraBold))
        hours_value.setStyleSheet(f"color: {COLORS.on_surface}; letter-spacing: -0.02em;")
        hours_layout.addWidget(hours_value)

        hours_layout.addWidget(self._create_progress_bar(0.75))
        sidebar_layout.addWidget(hours_card)

        # Online rate card
        online_card = QWidget()
        online_card.setStyleSheet(f"background-color: {COLORS.surface_container_low}; border-radius: 16px;")
        online_layout = QVBoxLayout(online_card)
        online_layout.setContentsMargins(28, 28, 28, 28)
        online_layout.setSpacing(12)

        online_title = QLabel(f"{ICONS.SECTION_CLOUD} 网络在线率")
        online_title.setStyleSheet(f"color: {COLORS.on_surface_subtle}; font-size: 12px; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase;")
        online_layout.addWidget(online_title)

        online_value = QLabel(f"{get_online_rate():.2f}%")
        online_value.setFont(QFont("Inter", 36, QFont.Weight.ExtraBold))
        online_value.setStyleSheet(f"color: {COLORS.on_surface}; letter-spacing: -0.02em;")
        online_layout.addWidget(online_value)

        online_note = QLabel("自系统部署以来无断线记录")
        online_note.setStyleSheet(f"color: {COLORS.tertiary_fixed_dim}; font-size: 12px; font-weight: 600;")
        online_layout.addWidget(online_note)

        sidebar_layout.addWidget(online_card)

        return sidebar

    def _create_progress_bar(self, progress: float) -> QWidget:
        """Create a progress bar."""
        bar = QWidget()
        bar.setFixedHeight(4)
        bar.setStyleSheet(f"""
            background-color: {COLORS.surface_container_high};
            border-radius: 2px;
        """)

        # This is a simplified version - in production you'd use custom paint
        return bar

    def _start_status_refresh(self):
        """Start periodic status refresh."""
        self._refresh_status()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh_status)
        self._timer.start(30000)  # 30 seconds

    def _refresh_status(self):
        """Refresh Tailscale and sleep status."""
        # Get Tailscale status
        ts_info = get_tailscale_status()

        if ts_info.online:
            self.ip_value.setText(ts_info.ip or "No IP")
            self.tunnel_status.setText(f"{ICONS.STATUS_SUCCESS} WireGuard 活跃")
        else:
            self.ip_value.setText("--")
            self.tunnel_status.setText("✗ 未连接")

        # Get sleep status
        if is_sleep_prevented():
            self.status_label.setText("保持唤醒状态：开启")
            self.desc_label.setText("自动睡眠已禁用。该设备将持续响应 Tailscale 网络请求并保持节点活跃。")
            self.disable_btn.setText("立即禁用")
            self.status_dot.setStyleSheet(f"""
                background-color: {COLORS.tertiary_fixed_dim};
                border-radius: 5px;
            """)
        else:
            self.status_label.setText("保持唤醒状态：关闭")
            self.desc_label.setText("系统将按照默认电源策略运行。设备可能在空闲时进入睡眠模式。")
            self.disable_btn.setText("立即启用")
            self.status_dot.setStyleSheet(f"""
                background-color: {COLORS.outline_variant};
                border-radius: 5px;
            """)

    def _on_toggle_btn_clicked(self):
        """Handle toggle button click."""
        if is_sleep_prevented():
            self.toggle_sleep_prevention.emit(False)
        else:
            self.toggle_sleep_prevention.emit(True)
        # Refresh status after a short delay
        QTimer.singleShot(500, self._refresh_status)

    def _on_quick_action(self, action: str):
        """Handle quick action card click."""
        if action == "prevent":
            self.toggle_sleep_prevention.emit(True)
        elif action == "restore":
            self.toggle_sleep_prevention.emit(False)
        # Refresh status after a short delay
        QTimer.singleShot(500, self._refresh_status)