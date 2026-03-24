# TailWake 设计规格

## 项目概述

TailWake 是一个轻量级 Windows 绿色工具，用于防止 Tailscale 连接的笔记本电脑因休眠而断网失联。通过定时任务动态切换系统休眠策略，确保远程访问的可靠性。

## 技术选型

| 项目 | 选择 | 理由 |
|------|------|------|
| GUI 框架 | PyQt6 | 最新版本，LGPL 协议，社区活跃 |
| 调度器 | APScheduler (BackgroundScheduler) | 灵活的内存调度，支持固定时间和间隔任务 |
| 开机自启 | 注册表 HKCU\Run | 无需管理员权限，绿色便携 |
| 配置存储 | 程序目录 config.json | 绿色便携，换电脑直接复制 |
| 打包工具 | PyInstaller | 单文件 exe，便于分发 |

## 项目结构

```
TailWake/
├── main.py                    # 程序入口，初始化应用
├── config.py                  # 配置文件读写、默认配置
├── models.py                  # 数据模型（Task, HistoryRecord）
├── power_control.py           # 电源策略控制（powercfg 调用）
├── tailscale_status.py        # Tailscale 状态获取
├── scheduler.py               # APScheduler 封装，任务调度逻辑
├── history_tracker.py         # 运行时间历史记录
├── autostart.py               # 开机自启（注册表方式）
├── styles.py                  # 样式定义（颜色、字体、QSS）
├── widgets/                   # 自定义控件
│   ├── sidebar.py             # 侧边栏导航
│   ├── toggle_switch.py       # 开关控件
│   ├── task_card.py           # 任务卡片
│   ├── countdown_dialog.py    # 倒计时确认弹窗
│   └── progress_ring.py       # 圆形进度环
├── pages/                     # 页面
│   ├── dashboard_page.py      # Dashboard 主页面
│   ├── tasks_page.py          # 任务列表页面
│   ├── task_edit_page.py      # 任务编辑页面
│   └── settings_page.py       # 设置页面
├── main_window.py             # 主窗口（侧边栏 + 内容区）
├── tray.py                    # 系统托盘图标与菜单
├── config.json                # 运行时配置文件
├── history.json               # 运行时间历史记录
└── requirements.txt           # 依赖列表
```

## 设计系统

### 设计理念

"The Digital Architect" - 将工具视为精密仪器，权威、冷静、有层次感。

**核心原则：**
- **无分割线规则**：通过背景色变化区分区域，禁止使用 1px 实线边框
- **色调分层**：UI 像堆叠的纸张，通过不同深浅的背景色创造层次
- **渐变主色调**：主操作按钮使用 `primary` 到 `primary_container` 的 135° 渐变

### 颜色系统

```
Surface Hierarchy (背景层次):
├── surface (#faf8ff)                    - Level 0 基础背景
├── surface_container_low (#f2f3ff)      - Level 1 区域背景
├── surface_container (#eaedff)          - Level 1.5
├── surface_container_high (#e2e7ff)     - Level 2 悬停状态
├── surface_container_highest (#dae2fd)  - Level 3 输入框默认
└── surface_container_lowest (#ffffff)   - Level 2 卡片/交互元素

Primary Colors (主色调):
├── primary (#141779)                    - 主色，深蓝
├── primary_container (#2d328f)          - 主色容器
├── primary_fixed (#e0e0ff)              - 固定主色
└── primary_fixed_dim (#bfc2ff)          - 固定主色暗

Status Colors (状态色):
├── tertiary_fixed_dim (#4edea3)         - 成功/活跃状态（绿色）
├── error (#ba1a1a)                      - 错误状态
└── error_container (#ffdad6)            - 错误容器

Text Colors (文字色):
├── on_surface (#131b2e)                 - 主文字
├── on_surface_variant (#464652)         - 次要文字
├── secondary (#515f74)                  - 辅助文字
└── outline_variant (#c7c5d4)            - 边框/分割线（仅 15% 不透明度）
```

### 字体系统

使用 **Inter** 字体：

| 用途 | 大小 | 字重 | 行高 | 字间距 |
|------|------|------|------|--------|
| Display (大数字/倒计时) | 44px | 800 | 1.0 | -0.02em |
| Title Large | 22px | 700 | 1.2 | -0.01em |
| Title Medium | 16px | 600 | 1.3 | 0 |
| Body Medium | 14px | 500 | 1.5 | 0 |
| Body Small | 12px | 400 | 1.5 | 0 |
| Label Small | 11px | 700 | 1.4 | +0.05em (大写) |

### 圆角系统

```
rounded-md:  6px   (按钮)
rounded-lg:  12px  (卡片)
rounded-xl:  16px  (大卡片)
rounded-full: 9999px (开关、圆形按钮)
```

### 阴影系统

```css
/* 卡片阴影 */
box-shadow: 0 4px 20px rgba(19, 27, 46, 0.02);

/* 悬浮元素阴影 */
box-shadow: 0 12px 40px rgba(19, 27, 46, 0.06);

/* 主按钮阴影 */
box-shadow: 0 8px 24px rgba(45, 50, 143, 0.3);
```

## 数据模型

### Task 数据模型

```python
@dataclass
class Task:
    id: str                          # 唯一标识（UUID）
    name: str                        # 任务名称
    icon: str                        # 图标名称（Material Symbols）
    task_type: str                   # "fixed" 固定时间 / "interval" 间隔重复
    trigger_time: str | None         # 固定时间：如 "09:00"
    trigger_days: list[int] | None   # 固定时间：[0-6] 星期几（0=周一, 6=周日），None 表示每天
    interval_minutes: int | None     # 间隔模式：分钟数
    action: str                      # "prevent_sleep" / "restore_sleep"
    enabled: bool                    # 是否启用
```

### HistoryRecord 数据模型

```python
@dataclass
class HistoryRecord:
    date: str              # 日期 "YYYY-MM-DD"
    active_hours: float    # 活跃小时数
    prevent_sleep_count: int  # 防休眠次数
```

### config.json 结构

```json
{
    "countdown_seconds": 60,
    "restore_sleep_minutes": 20,
    "autostart": true,
    "track_history": true,
    "tasks": [
        {
            "id": "uuid-string",
            "name": "工作时间",
            "icon": "visibility",
            "task_type": "fixed",
            "trigger_time": "09:00",
            "trigger_days": [0, 1, 2, 3, 4],
            "interval_minutes": null,
            "action": "prevent_sleep",
            "enabled": true
        }
    ]
}
```

## 核心模块

### power_control.py - 电源控制

```python
def prevent_sleep() -> bool:
    """执行 powercfg /change standby-timeout-ac 0，返回是否成功"""

def restore_sleep(minutes: int) -> bool:
    """执行 powercfg /change standby-timeout-ac {minutes}，返回是否成功"""

def get_current_sleep_timeout() -> int | None:
    """获取当前休眠超时设置（用于状态显示）"""
```

### tailscale_status.py - Tailscale 状态

```python
def get_tailscale_ip() -> str | None:
    """执行 tailscale ip -4 获取 IPv4 地址"""

def get_tailscale_status() -> dict:
    """执行 tailscale status --json 获取完整状态"""
    # 返回: {"online": bool, "ip": str, "hostname": str, "last_handshake": str}
```

### scheduler.py - 调度引擎

- 使用 `APScheduler` 的 `BackgroundScheduler`
- 启动时从 config 加载所有启用的任务
- 提供 `add_task(task)`、`remove_task(task_id)`、`update_task(task)` 接口
- **休眠唤醒补偿**：使用 `win32api` 监听 `WM_POWERBROADCAST` 消息（`PBT_APMRESUMEAUTOMATIC` 事件），唤醒后检查是否有错过的任务并触发确认弹窗

### history_tracker.py - 历史记录

```python
def record_session_start():
    """记录会话开始时间"""

def record_session_end():
    """记录会话结束，计算活跃时长"""

def get_weekly_history() -> list[HistoryRecord]:
    """获取最近7天的历史记录"""

def get_total_active_hours() -> float:
    """获取总活跃时长"""
```

### autostart.py - 开机自启

```python
def enable_autostart() -> bool:
    """向 HKCU\Software\Microsoft\Windows\CurrentVersion\Run 写入程序路径"""

def disable_autostart() -> bool:
    """移除注册表项"""

def is_autostart_enabled() -> bool:
    """检查是否已设置自启"""
```

## UI 页面设计

### 应用行为

- **启动时**：最小化到系统托盘
- **关闭窗口**：最小化到托盘（不退出程序）
- **托盘双击**：显示主窗口
- **托盘退出**：需确认后退出程序

### 主窗口布局

```
┌────────────────────────────────────────────────────────────┐
│ ┌──────────┐ ┌────────────────────────────────────────────┐ │
│ │          │ │ 顶部导航栏 (h: 48px)                        │ │
│ │  侧边栏   │ │ [网络状态] [同步] [账户]                    │ │
│ │  w: 256px│ ├────────────────────────────────────────────┤ │
│ │          │ │                                            │ │
│ │ [Logo]   │ │                                            │ │
│ │          │ │              内容区                         │ │
│ │ Dashboard│ │                                            │ │
│ │ Tasks    │ │         (根据侧边栏选择切换)                │ │
│ │ Settings │ │                                            │ │
│ │          │ │                                            │ │
│ │          │ │                                            │ │
│ │ [用户信息]│ │                                            │ │
│ └──────────┘ └────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

### Dashboard 页面

**区域 1: 核心状态卡片 (左侧 8列, 高度 320px)**
- 状态指示点 + 标签 "系统当前运行状态"
- 大标题: "保持唤醒状态：开启/关闭"
- 描述文字
- 操作按钮: "立即禁用/启用" + "运行计划设置"
- 背景装饰: 渐变圆形

**区域 2: 网络节点信息 (右侧 4列)**
- 深色背景 (primary_container)
- Tailscale IPv4 地址
- 加密隧道状态 (WireGuard 活跃)
- 最后握手时间

**区域 3: 快速操作 (4个卡片网格)**
- 立即保持唤醒
- 正常睡眠模式
- 定时任务设置
- 节点配置

**区域 4: 运行时间历史 (左侧 8列)**
- 柱状图显示最近7天活跃时长
- 时间范围选择器

**区域 5: 统计卡片 (右侧 4列)**
- 唤醒总时长
- 网络在线率

**底部状态栏:**
- 核心守护进程状态
- 下一次自动休眠检查时间

### Tasks 页面 (任务列表)

**页面头部:**
- 标题: "自动化任务列表"
- 描述: "管理您的桌面自动化策略与系统常驻任务"
- 添加新任务按钮 (渐变背景)

**任务卡片网格 (响应式 1/2/3 列):**

每个卡片包含:
- 图标 (左上角，圆角方形背景)
- 开关 (右上角)
- 任务名称
- 时间信息 (图标 + 文字)
- 动作标签
- 悬停显示: 编辑/删除按钮

**底部统计栏:**
- 活跃任务数
- 下次执行时间
- 系统状态进度条

### Task Edit 页面 (任务编辑)

**左侧主表单 (8列):**
- 任务名称输入框
- **任务类型选择**: 单选按钮组 "固定时间" / "间隔重复"
- **固定时间模式** (当选择"固定时间"时显示):
  - 触发时间选择器 (时:分)
  - 重复周期选择 (星期按钮组: 一二三四五六日，支持多选)
  - 快捷选项: "每天"、"工作日"、"周末"
- **间隔重复模式** (当选择"间隔重复"时显示):
  - 间隔分钟数输入框 (数字输入，最小值 1)
  - 显示说明: "每隔 X 分钟执行一次"
- 电源动作下拉选择:
  - "防止休眠" (prevent_sleep)
  - "恢复休眠" (restore_sleep)
- 启用开关

**右侧信息卡片 (4列):**
- 目标设备信息 (IP, 状态, 系统版本)
- 专业提示卡片 (渐变背景)

**底部操作栏:**
- 取消按钮
- 保存任务按钮 (渐变背景)

### Settings 页面

**设置项:**
- 倒计时秒数 (滑块/输入框)
- 恢复休眠分钟数 (输入框)
- 开机自启 (开关)
- 记录运行历史 (开关)
- 关于信息

### Confirmation Dialog (确认弹窗)

**触发条件:**
- **定时任务到达时**: 所有启用的定时任务触发时都会弹出确认窗口
- **休眠唤醒补偿**: 电脑从休眠唤醒后，如果有错过的任务，也会弹出确认窗口

**布局:**
- 模态遮罩层 (backdrop-blur)
- 居中卡片 (max-width: 480px)
- 始终置顶，确保用户能看到

**内容:**
- 警告图标 + 标题: "确认操作：[动作名称]？"
- 圆形进度环 (倒计时数字居中)
- 提示文字: "如果未进行任何操作，任务将在倒计时结束后自动执行。"
- 任务信息标签: 显示任务名称和动作类型
- 双按钮: 立即确认 / 取消

**圆形进度环:**
- 外圈: Ghost Border (outline_variant 15%)
- 进度: tertiary_fixed_dim 填充
- 中心: 大号倒计时数字 (从配置秒数递减到 0)
- 倒计时结束: 自动执行动作（兜底机制）

**交互逻辑:**
- 点击"立即确认": 立即执行动作，关闭弹窗
- 点击"取消": 放弃操作，关闭弹窗
- 倒计时结束未操作: 自动执行动作，关闭弹窗

## 系统托盘

**图标:**
- 默认: TailWake logo
- 防休眠激活时: 添加绿色指示点

**右键菜单:**
```
├─ 打开主界面
├─ ───────────
├─ 立即开启防休眠
├─ 立即恢复正常休眠
├─ ───────────
├─ 开机自启 ✓
├─ ───────────
└─ 退出
```

## 错误处理

### 电源命令执行

- 捕获 `powercfg` 命令执行失败，在托盘显示错误提示
- 记录日志到文件 `tailwake.log`

### Tailscale 状态获取

- tailscale CLI 未安装: 显示 "未安装 Tailscale"
- 未连接: 显示 "未连接"
- 获取失败: 显示离线状态，不阻塞其他功能

### 配置文件

- 首次启动：创建默认配置文件
- 配置损坏：使用默认配置，提示用户
- 配置保存：每次修改后立即写入，避免丢失

### 调度器异常

- 任务执行失败：记录日志，托盘提示
- 休眠唤醒后：检查系统时间与上次记录时间，如果差距超过阈值且期间有错过的任务，立即触发确认弹窗

### UI 异常

- 弹窗显示时程序被最小化：确保弹窗始终置顶
- 多个任务同时触发：弹窗队列化处理

### 应用退出行为

- 关闭窗口：最小化到托盘
- 托盘退出：确认对话框后退出，不自动恢复休眠设置

## 用户配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| countdown_seconds | 60 | 确认弹窗倒计时秒数 |
| restore_sleep_minutes | 20 | 恢复休眠时的超时分钟数 |
| autostart | true | 是否开机自启 |
| track_history | true | 是否记录运行历史 |

## 打包要求

- 使用 PyInstaller 打包为单文件 exe
- 目标平台：Windows 10/11
- 无需管理员权限运行
- 包含 Inter 字体文件