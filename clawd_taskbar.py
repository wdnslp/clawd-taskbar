import sys
import os
import glob
import json
import time
import random
import ctypes
from ctypes import wintypes
from PyQt6.QtWidgets import QApplication, QWidget, QMenu, QSystemTrayIcon
from PyQt6.QtGui import QImage, QPixmap, QPainter, QCursor, QColor, QPen, QIcon
from PyQt6.QtCore import Qt, QTimer, QPoint, QRect, QRectF
from PyQt6.QtSvg import QSvgRenderer
import winreg

try:
    import psutil
except ImportError:
    psutil = None

# Configure high-DPI scaling policy before QApplication creation for pixel-perfect rendering
try:
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
ANIM_DIR = os.path.join(BASE_DIR, "animations")
BASE_IMAGE_PATH = os.path.join(BASE_DIR, "base.png")
ARM_IMAGE_PATH = os.path.join(BASE_DIR, "right-arm-up.png")

# Win32 APIs for taskbar ownership, region clipping & non-flickering topmost assertion
try:
    user32 = ctypes.windll.user32
    gdi32 = ctypes.windll.gdi32
    shell32 = ctypes.windll.shell32
    kernel32 = ctypes.windll.kernel32

    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

    if hasattr(user32, "SetWindowLongPtrW"):
        SetWindowLongPtr = user32.SetWindowLongPtrW
    else:
        SetWindowLongPtr = user32.SetWindowLongW

    SetWindowLongPtr.argtypes = [wintypes.HWND, ctypes.c_int, wintypes.LPARAM]
    SetWindowLongPtr.restype = wintypes.LPARAM

    user32.SetWindowPos.argtypes = [
        wintypes.HWND, wintypes.HWND,
        ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
        ctypes.c_uint
    ]
    user32.SetWindowPos.restype = wintypes.BOOL

    user32.GetWindow.argtypes = [wintypes.HWND, ctypes.c_uint]
    user32.GetWindow.restype = wintypes.HWND

    user32.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
    user32.FindWindowW.restype = wintypes.HWND

    user32.IsWindowVisible.argtypes = [wintypes.HWND]
    user32.IsWindowVisible.restype = wintypes.BOOL

    user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
    user32.GetWindowThreadProcessId.restype = wintypes.DWORD

    user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
    user32.GetWindowRect.restype = wintypes.BOOL

    user32.SetWindowRgn.argtypes = [wintypes.HWND, wintypes.HRGN, wintypes.BOOL]
    user32.SetWindowRgn.restype = ctypes.c_int

    user32.SetParent.argtypes = [wintypes.HWND, wintypes.HWND]
    user32.SetParent.restype = wintypes.HWND

    user32.GetParent.argtypes = [wintypes.HWND]
    user32.GetParent.restype = wintypes.HWND

    user32.GetAncestor.argtypes = [wintypes.HWND, ctypes.c_uint]
    user32.GetAncestor.restype = wintypes.HWND

    user32.BringWindowToTop.argtypes = [wintypes.HWND]
    user32.BringWindowToTop.restype = wintypes.BOOL

    user32.GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]
    user32.GetWindowLongW.restype = ctypes.c_long

    user32.GetDC.argtypes = [wintypes.HWND]
    user32.GetDC.restype = wintypes.HDC

    user32.ReleaseDC.argtypes = [wintypes.HWND, wintypes.HDC]
    user32.ReleaseDC.restype = ctypes.c_int

    gdi32.CreateRectRgn.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
    gdi32.CreateRectRgn.restype = wintypes.HRGN

    gdi32.CombineRgn.argtypes = [wintypes.HRGN, wintypes.HRGN, wintypes.HRGN, ctypes.c_int]
    gdi32.CombineRgn.restype = ctypes.c_int

    gdi32.DeleteObject.argtypes = [wintypes.HGDIOBJ]
    gdi32.DeleteObject.restype = wintypes.BOOL

    gdi32.GetPixel.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int]
    gdi32.GetPixel.restype = ctypes.c_uint

    if shell32:
        shell32.SHQueryUserNotificationState.argtypes = [ctypes.POINTER(wintypes.DWORD)]
        shell32.SHQueryUserNotificationState.restype = ctypes.c_long

    GWLP_HWNDPARENT = -8
    GW_OWNER = 4
    GW_HWNDPREV = 3
    HWND_TOPMOST = wintypes.HWND(-1)

    # 0x071B: SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_NOOWNERZORDER | SWP_NOCOPYBITS | SWP_NOSENDCHANGING | SWP_NOREDRAW
    # This flags combination instructs Windows to adjust Z-order without sending WM_WINDOWPOSCHANGING,
    # without performing internal BitBlt screen copying, and without triggering redraws.
    SWP_FLAGS_SILENT = 0x0002 | 0x0001 | 0x0010 | 0x0200 | 0x0100 | 0x0400 | 0x0008

    def to_lparam(val):
        if val >= (1 << 31):
            return val - (1 << 32)
        return val
except Exception:
    user32 = None
    gdi32 = None
    shell32 = None
    SetWindowLongPtr = None
    def to_lparam(val):
        return val



# --- Windows Autostart Management ---
RUN_REG_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_REG_NAME = "ClawdTaskbar"

def is_autostart_configured() -> bool:
    """Checks if autostart at Windows boot is configured in HKCU Run registry."""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_REG_KEY, 0, winreg.KEY_READ)
        try:
            val, _ = winreg.QueryValueEx(key, APP_REG_NAME)
        except Exception:
            val, _ = winreg.QueryValueEx(key, "ClaudeTaskbar")
        winreg.CloseKey(key)
        return bool(val)
    except Exception:
        return False

def get_system_uptime_ms() -> int:
    """Returns system uptime in milliseconds via Win32 GetTickCount64."""
    try:
        if kernel32 and hasattr(kernel32, "GetTickCount64"):
            kernel32.GetTickCount64.restype = ctypes.c_uint64
            return int(kernel32.GetTickCount64())
    except Exception:
        pass
    return 99999999


def set_autostart_configured(enabled: bool) -> bool:
    """Enables or disables autostart at Windows login."""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_REG_KEY, 0, winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE)
        if enabled:
            py_exe = sys.executable
            pyw_exe = os.path.join(os.path.dirname(py_exe), "pythonw.exe")
            runner = pyw_exe if os.path.exists(pyw_exe) else py_exe
            script_path = os.path.abspath(os.path.join(BASE_DIR, "clawd_taskbar.py"))
            if not os.path.exists(script_path):
                script_path = os.path.abspath(os.path.join(BASE_DIR, "claude_taskbar.py"))
            cmd = f'"{runner}" "{script_path}"'
            winreg.SetValueEx(key, APP_REG_NAME, 0, winreg.REG_SZ, cmd)
        else:
            for k in (APP_REG_NAME, "ClaudeTaskbar"):
                try:
                    winreg.DeleteValue(key, k)
                except FileNotFoundError:
                    pass
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print("Failed to set autostart in registry:", e)
        return False


ICONS_DIR = os.path.join(BASE_DIR, "assets", "icons")

def get_material_icon(name: str) -> QIcon:
    """Returns a crisp QIcon for a Google Material Symbol."""
    png_path = os.path.join(ICONS_DIR, f"{name}.png")
    if os.path.exists(png_path):
        return QIcon(png_path)
    svg_path = os.path.join(ICONS_DIR, f"{name}.svg")
    if os.path.exists(svg_path):
        return QIcon(svg_path)
    return QIcon()

# --- Localization (English & System Detection) ---
TRANSLATIONS = {
    "ru": {
        "roam_zone": "Зона прогулки",
        "roam_allow_slow": "Разрешить медленные шаги",
        "roam_tune": "Настроить зону на панели...",
        "roam_reset": "Сбросить зону по умолчанию",
        "autostart": "Запускать при старте Windows",
        "placement": "Позиция на панели",
        "placement_bottom": "Внутри панели (снизу экрана)",
        "placement_top": "Сверху панели (на бордюре)",
        "language": "Язык",
        "lang_system": "🌐 Системный",
        "lang_en": "🇺🇸 English",
        "lang_ru": "🇷🇺 Русский",
        "lang_uk": "🇺🇦 Українська",
        "snap_taskbar": "Магнититься к панели",
        "reset_pos": "Сбросить позицию Clawd",
        "quit": "Закрыть",
        "tooltip_default": "Clawd Mascot",
        "tooltip_coding": "Clawd Mascot — Пишет код",
        "tooltip_coding_done": "Clawd Mascot — Код готов",
        "tooltip_afk": "Clawd Mascot — Спит (AFK)",
    },
    "en": {
        "roam_zone": "Wander Zone",
        "roam_allow_slow": "Allow slow steps",
        "roam_tune": "Configure zone on taskbar...",
        "roam_reset": "Reset zone to default",
        "autostart": "Run on Windows startup",
        "placement": "Taskbar Position",
        "placement_bottom": "Inside taskbar (screen bottom)",
        "placement_top": "Above taskbar (on border)",
        "language": "Language",
        "lang_system": "🌐 System",
        "lang_en": "🇺🇸 English",
        "lang_ru": "🇷🇺 Russian",
        "lang_uk": "🇺🇦 Ukrainian",
        "snap_taskbar": "Snap to taskbar",
        "reset_pos": "Reset Clawd position",
        "quit": "Quit",
        "tooltip_default": "Clawd Mascot",
        "tooltip_coding": "Clawd Mascot — Writing code",
        "tooltip_coding_done": "Clawd Mascot — Code ready",
        "tooltip_afk": "Clawd Mascot — Sleeping (AFK)",
    },
    "uk": {
        "roam_zone": "Зона прогулянки",
        "roam_allow_slow": "Дозволити повільні кроки",
        "roam_tune": "Налаштувати зону на панелі...",
        "roam_reset": "Скинути зону за замовчуванням",
        "autostart": "Запускати під час старту Windows",
        "placement": "Позиція на панелі",
        "placement_bottom": "Усередині панелі (знизу екрана)",
        "placement_top": "Зверху панелі (на бордюрі)",
        "language": "Мова",
        "lang_system": "🌐 Системна",
        "lang_en": "🇺🇸 English",
        "lang_ru": "🇷🇺 Русский",
        "lang_uk": "🇺🇦 Українська",
        "snap_taskbar": "Прилипати до панелі",
        "reset_pos": "Скинути позицію Clawd",
        "quit": "Закрити",
        "tooltip_default": "Clawd Mascot",
        "tooltip_coding": "Clawd Mascot — Пише код",
        "tooltip_coding_done": "Clawd Mascot — Код готовий",
        "tooltip_afk": "Clawd Mascot — Спить (AFK)",
    }
}

def get_system_language() -> str:
    """Detects Windows system UI language; returns 'uk' for Ukrainian, 'ru' for Russian/Belarusian, else 'en'."""
    try:
        if kernel32:
            lang_id = kernel32.GetUserDefaultUILanguage() & 0x3FF
            if lang_id == 0x22:
                return "uk"
            if lang_id in (0x19, 0x23):
                return "ru"
    except Exception:
        pass
    return "en"


# --- Taskbar Roaming Zone Overlay (Draggable & Resizable Blue Interval) ---
class RoamZoneOverlayWidget(QWidget):
    """
    Clean, minimal semi-transparent blue interval overlay directly on the taskbar.
    Color matches user screenshot: rgba(35, 116, 222, 0.38) with side handles.
    Uses official Material Symbols Outlined 'close' icon.
    No obstructive text or walking icons in the middle.
    """
    def __init__(self, clawd_widget):
        super().__init__()
        self.clawd_widget = clawd_widget
        self.clawd_widget = clawd_widget  # backwards compatibility alias
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setMouseTracking(True)

        self.drag_mode = None  # None, "move", "left", "right"
        self.drag_start_global_x = 0
        self.drag_start_geo = None
        self._hover_close = False

        # Load Google Material Symbols Outlined 'close' icon
        close_svg = os.path.join(ICONS_DIR, "close.svg")
        if not os.path.exists(close_svg):
            close_svg = os.path.join(BASE_DIR, "assets", "close.svg")
        if os.path.exists(close_svg):
            self.close_renderer = QSvgRenderer(close_svg)
        else:
            self.close_renderer = None

        self.sync_geometry()

    def sync_geometry(self):
        tray_r = self.clawd_widget.get_tray_rect()
        if tray_r:
            tray_top = tray_r.top
            tray_h = tray_r.bottom - tray_r.top
            tray_left = tray_r.left
            tray_w = tray_r.right - tray_r.left
        else:
            screen = self.clawd_widget.get_current_screen()
            geom = screen.geometry()
            tray_top = geom.bottom() - 48
            tray_h = 48
            tray_left = geom.left()
            tray_w = geom.width()

        self.clawd_widget.ensure_roam_bounds()
        min_x = max(tray_left, self.clawd_widget.roam_screen_min_x)
        max_x = min(tray_left + tray_w, self.clawd_widget.roam_screen_max_x)
        self.zone_w = max(120, max_x - min_x)
        self.zone_h = tray_h

        # Window covers blue zone on taskbar plus top/right offsets for the badge
        offset_top = 10
        offset_right = 12
        self.setGeometry(min_x, tray_top - offset_top, self.zone_w + offset_right, self.zone_h + offset_top)

    def close_btn_rect(self):
        # Square badge in the top-right corner with fly-out
        badge_size = 20
        offset_top = 10
        zone_w = getattr(self, "zone_w", self.width() - 12)
        bx = zone_w - badge_size // 2 - 1
        by = max(1, offset_top - badge_size // 2 - 1)
        return QRect(bx, by, badge_size, badge_size)

    def is_over_close_btn(self, pt):
        return self.close_btn_rect().contains(pt)

    def leaveEvent(self, event):
        if self._hover_close:
            self._hover_close = False
            self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.pos()
            if self.is_over_close_btn(pos):
                self.hide()
                return

            # Cancel any ongoing slow roaming step on Clawd immediately
            if hasattr(self.clawd_widget, "_roam_step_timer") and self.clawd_widget._roam_step_timer.isActive():
                self.clawd_widget._roam_step_timer.stop()
                self.clawd_widget._roam_steps_remaining = 0

            self.drag_start_global_x = event.globalPosition().toPoint().x()
            self.drag_start_geo = self.geometry()
            self.drag_start_zone_w = getattr(self, "zone_w", self.width() - 12)

            if pos.x() <= 14:
                self.drag_mode = "left"
            elif pos.x() >= self.drag_start_zone_w - 14:
                self.drag_mode = "right"
            else:
                self.drag_mode = "move"

    def mouseMoveEvent(self, event):
        pos = event.pos()
        offset_top = 10
        offset_right = 12
        zone_w = getattr(self, "zone_w", self.width() - offset_right)
        zone_h = getattr(self, "zone_h", self.height() - offset_top)

        if self.drag_mode is None:
            was_hover = self._hover_close
            now_hover = self.is_over_close_btn(pos)
            if was_hover != now_hover:
                self._hover_close = now_hover
                self.update()

            if now_hover:
                self.setCursor(Qt.CursorShape.PointingHandCursor)
            elif pos.x() <= 14 or pos.x() >= zone_w - 14:
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            else:
                self.setCursor(Qt.CursorShape.SizeAllCursor)
            return

        delta_x = event.globalPosition().toPoint().x() - self.drag_start_global_x
        tray_r = self.clawd_widget.get_tray_rect()
        tray_left = tray_r.left if tray_r else 0
        tray_right = tray_r.right if tray_r else 1920

        if self.drag_mode == "move":
            new_x = self.drag_start_geo.x() + delta_x
            new_x = max(tray_left, min(tray_right - zone_w, new_x))
            self.move(new_x, self.y())

        elif self.drag_mode == "left":
            new_x = self.drag_start_geo.x() + delta_x
            new_w = self.drag_start_zone_w - delta_x
            if new_w >= 120 and new_x >= tray_left:
                self.zone_w = new_w
                self.setGeometry(new_x, self.y(), new_w + offset_right, zone_h + offset_top)

        elif self.drag_mode == "right":
            new_w = self.drag_start_zone_w + delta_x
            if new_w >= 120 and (self.x() + new_w <= tray_right):
                self.zone_w = new_w
                self.resize(new_w + offset_right, zone_h + offset_top)

        self.clawd_widget.roam_screen_min_x = self.x()
        self.clawd_widget.roam_screen_max_x = self.x() + getattr(self, "zone_w", self.width() - offset_right)
        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_mode = None
            offset_right = 12
            self.clawd_widget.roam_screen_min_x = self.x()
            self.clawd_widget.roam_screen_max_x = self.x() + getattr(self, "zone_w", self.width() - offset_right)
            self.clawd_widget.save_config()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        offset_top = 10
        offset_right = 12
        corner_radius = 4

        zone_w = getattr(self, "zone_w", self.width() - offset_right)
        zone_h = getattr(self, "zone_h", self.height() - offset_top)

        zone_x = 1
        zone_y = offset_top + 1
        draw_w = zone_w - 2
        draw_h = zone_h - 2

        # Exact sampled blue from screenshot: (35, 116, 222)
        fill_color = QColor(35, 116, 222, 95)
        border_color = QColor(109, 167, 236, 230)
        handle_color = QColor(52, 135, 236, 240)

        # Background fill and outline (clean, uncluttered box)
        painter.setBrush(fill_color)
        painter.setPen(QPen(border_color, 2))
        painter.drawRoundedRect(zone_x, zone_y, draw_w, draw_h, corner_radius, corner_radius)

        # Left Handle Grip
        painter.setBrush(handle_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(zone_x + 2, zone_y + 3, 10, draw_h - 6, 3, 3)
        painter.setBrush(QColor(255, 255, 255, 200))
        for dot_y in (zone_y + draw_h // 2 - 6, zone_y + draw_h // 2, zone_y + draw_h // 2 + 6):
            painter.drawEllipse(zone_x + 6, dot_y, 2, 2)

        # Right Handle Grip
        painter.setBrush(handle_color)
        painter.drawRoundedRect(zone_x + draw_w - 12, zone_y + 3, 10, draw_h - 6, 3, 3)
        painter.setBrush(QColor(255, 255, 255, 200))
        for dot_y in (zone_y + draw_h // 2 - 6, zone_y + draw_h // 2, zone_y + draw_h // 2 + 6):
            painter.drawEllipse(zone_x + draw_w - 8, dot_y, 2, 2)

        # Material Symbols Outlined Close Badge (Square with rounded corners, fly-out top-right)
        cr = self.close_btn_rect()

        # Shadow
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 0, 0, 80))
        painter.drawRoundedRect(cr.translated(0, 1), corner_radius, corner_radius)

        # Badge Body
        if self._hover_close:
            badge_bg = QColor(218, 119, 88, 245)      # Clawd brand orange on hover
            badge_border = QColor(255, 255, 255, 230)
        else:
            badge_bg = QColor(26, 32, 44, 240)        # Dark theme badge
            badge_border = QColor(109, 167, 236, 240)  # Accent blue border

        painter.setBrush(badge_bg)
        painter.setPen(QPen(badge_border, 1.5))
        painter.drawRoundedRect(cr, corner_radius, corner_radius)

        icon_size = 12
        icon_x = cr.x() + (cr.width() - icon_size) / 2.0
        icon_y = cr.y() + (cr.height() - icon_size) / 2.0
        icon_r = QRectF(icon_x, icon_y, icon_size, icon_size)

        if getattr(self, "close_renderer", None) and self.close_renderer.isValid():
            self.close_renderer.render(painter, icon_r)
        else:
            close_png = os.path.join(ICONS_DIR, "close.png")
            if os.path.exists(close_png):
                painter.drawPixmap(int(icon_x), int(icon_y), icon_size, icon_size, QPixmap(close_png))

class ClawdTaskbarWidget(QWidget):
    def __init__(self):
        super().__init__()

        # --- Mascot Window Configuration ---
        # FramelessWindowHint: borderless transparent window
        # WindowStaysOnTopHint: OS-level persistent topmost
        # Tool: no taskbar icon, no Alt+Tab entry, desktop accessory style
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Petting interaction state (blush cheeks appear when petted / hovered over)
        self.setMouseTracking(True)
        self.pet_blush_level = 0.0  # 0.0 (no blush) to 1.0 (full blushing cheeks)
        self._last_pet_mouse_pos = None
        self._last_pet_time = 0.0
        self._pet_timer = QTimer(self)
        self._pet_timer.timeout.connect(self._update_pet_blush_decay)
        self._pet_timer.setInterval(35)

        # Language setting ('system', 'en', 'ru')
        self.language = "system"

        # Settings (Living mode & Fullscreen hiding are ALWAYS permanently active)
        self.scale_factor = 3
        self.placement_mode = "bottom"  # "bottom" (inside taskbar) or "top" (on top of taskbar ledge)
        self.auto_peek_on_shell = False
        self.is_peeked_up = False
        self.snap_to_taskbar = True
        self.idle_animations_enabled = True  # Always permanently active
        self.auto_hide_fullscreen = True     # Always permanently active

        # Smart Context state (Claude Code live coding, AFK sleep, IDE focus)
        self.smart_context_enabled = True   # Always permanently active
        self.is_claude_coding = False
        self.is_sleeping_afk = False
        self._last_coding_time = 0.0
        self._current_coding_project = ""
        self._recent_idle_history = []
        self.idle_frequency_mode = "normal"

        # Roam Zone (Slow occasional wandering within semi-transparent blue interval)
        self.roam_enabled = True
        self.roam_screen_min_x = None
        self.roam_screen_max_x = None
        self.roam_overlay = None
        self.roam_timer = QTimer(self)
        self.roam_timer.timeout.connect(self._trigger_slow_roam)
        self._roam_step_timer = QTimer(self)
        self._roam_step_timer.timeout.connect(self._execute_roam_step)
        self._roam_steps_remaining = 0
        self._roam_direction = 0
        self._roam_walk_frame = 0

        # State
        self.current_anim_name = "peek_entrance"
        self.current_frame_idx = 0
        self.is_looping = False
        self.current_pixmap = None
        self.drag_start_pos = None
        self.window_start_pos = None
        self.window_start_screen_x = None
        self.is_dragging = False
        self.is_lifted = False
        self.on_anim_finished = None

        # Startup entrance state (peek entrance from below taskbar)
        self._startup_animated = False
        self._startup_entrance_scheduled = False
        uptime_ms = get_system_uptime_ms()
        self._is_system_boot = (uptime_ms < 180000)  # within 3 minutes of Windows boot

        # Fullscreen & Taskbar Embedding state
        self.hidden_by_fullscreen = False
        self._is_embedded = False

        # Load all sprites and animations
        self.load_all_sprites()

        # Load saved settings if any
        self.load_config()

        # Re-scale pixmaps to current scale_factor
        self.update_scaled_pixmaps()

        # Place at saved or initial position
        self.ensure_valid_position()

        # Animation playback timer
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._advance_anim_frame)

        # Idle behaviors timer (blinking, stretching, coffee, etc.)
        self.idle_timer = QTimer(self)
        self.idle_timer.timeout.connect(self._trigger_random_idle_action)
        self._schedule_next_idle(10000, 20000)

        # Shell & Z-order safety monitor (runs smoothly every 60ms with 0.0% CPU)
        self._cached_trays = set()
        self._last_topmost_assert_time = 0.0
        self.zorder_monitor_timer = QTimer(self)
        self.zorder_monitor_timer.timeout.connect(self._check_zorder_safety)
        self.zorder_monitor_timer.start(60)

        # Fullscreen detection timer: runs every 800ms only if enabled
        self.fullscreen_timer = QTimer(self)
        self.fullscreen_timer.timeout.connect(self._check_fullscreen)
        if self.auto_hide_fullscreen:
            self.fullscreen_timer.start(800)

        # Smart Context monitor timer (polls Claude Code & input every 1 second)
        self.context_timer = QTimer(self)
        self.context_timer.timeout.connect(self._check_contextual_state)
        self.context_timer.start(1000)

        # Automatically ensure Windows Autostart on boot is active
        if not is_autostart_configured():
            set_autostart_configured(True)

        # Roam Zone overlay widget instance
        self.roam_overlay = RoamZoneOverlayWidget(self)

        # Setup System Tray Icon & Context Menu (with base icon)
        self.setup_tray_icon()

        # Start wandering timer (runs every 2.5 to 5 minutes)
        self._schedule_next_roam(150, 300)

        # Initial stance: start transparent so Claude cleanly emerges from below upon entrance
        w = 16 * self.scale_factor
        h = 16 * self.scale_factor
        self.current_pixmap = QPixmap(w, h)
        self.current_pixmap.fill(Qt.GlobalColor.transparent)

    # --- Windows Taskbar Embedding & Topmost Maintenance ---

    def get_tray_rect(self):
        """Returns the screen RECT of Shell_TrayWnd."""
        if not user32:
            return None
        try:
            tray = user32.FindWindowW("Shell_TrayWnd", None)
            if not tray:
                return None
            r = wintypes.RECT()
            if user32.GetWindowRect(tray, ctypes.byref(r)):
                return r
        except Exception:
            pass
        return None

    def embed_in_taskbar(self, target_screen_x=None):
        """
        Embeds Clawd's window as a genuine WS_CHILD of Shell_TrayWnd.
        This seamlessly places Claude inside the taskbar:
        - Clawd is rendered as part of the taskbar's visual hierarchy by DWM.
        - Clawd NEVER disappears when Start Menu, Action Center, or Windows panels open.
        - NO hole is carved in the taskbar, so the taskbar's native acrylic background
          is preserved behind Clawd with zero black boxes or black borders.
        """
        if not user32:
            return
        try:
            tray = user32.FindWindowW("Shell_TrayWnd", None)
            if not tray:
                return
            hwnd = int(self.winId())
            if not hwnd:
                return

            # Make sure tray has normal region (no leftover holes)
            user32.SetWindowRgn(tray, None, True)

            user32.SetParent(hwnd, tray)
            style = user32.GetWindowLongW(hwnd, -16)  # GWL_STYLE
            # Remove WS_POPUP (0x80000000), add WS_CHILD (0x40000000) and WS_VISIBLE (0x10000000)
            new_style = (style & ~0x80000000) | 0x40000000 | 0x10000000
            SetWindowLongPtr(hwnd, -16, to_lparam(new_style))
            self._is_embedded = True

            tray_r = self.get_tray_rect()
            if tray_r:
                tray_w = tray_r.right - tray_r.left
                tray_h = tray_r.bottom - tray_r.top
                target_y = tray_h - (12 * self.scale_factor)
                if target_screen_x is not None:
                    local_x = max(0, min(tray_w - self.width(), target_screen_x - tray_r.left))
                    self.saved_pos = QPoint(target_screen_x, target_y)
                elif self.saved_pos:
                    local_x = max(0, min(tray_w - self.width(), self.saved_pos.x() - tray_r.left))
                else:
                    local_x = int(tray_w * 0.8) - (self.width() // 2)
                user32.SetWindowPos(hwnd, 0, local_x, target_y, self.width(), self.height(), 0x0040)
                user32.BringWindowToTop(hwnd)
                if not getattr(self, "_startup_animated", False):
                    self.schedule_startup_entrance()
        except Exception as e:
            print("embed_in_taskbar error:", e)

    def unembed_from_taskbar(self):
        """
        Restores Clawd as a top-level topmost window when in 'top' placement mode.
        """
        if not user32 or not self._is_embedded:
            return
        try:
            hwnd = int(self.winId())
            if not hwnd:
                return

            tray_r = self.get_tray_rect()
            screen_x = (tray_r.left if tray_r else 0) + self.x()
            screen = self.get_current_screen()
            screen_y = self.get_taskbar_top_y(screen)

            user32.SetParent(hwnd, 0)
            style = user32.GetWindowLongW(hwnd, -16)  # GWL_STYLE
            # Remove WS_CHILD (0x40000000), restore WS_POPUP (0x80000000) | WS_VISIBLE
            top_style = (style & ~0x40000000) | 0x80000000 | 0x10000000
            SetWindowLongPtr(hwnd, -16, to_lparam(top_style))
            self._is_embedded = False

            user32.SetWindowPos(hwnd, HWND_TOPMOST, screen_x, screen_y, self.width(), self.height(), 0x0040)
            self.move(screen_x, screen_y)
            self.attach_tray_ownership()
            self.assert_topmost()
        except Exception as e:
            print("unembed_from_taskbar error:", e)

    def restore_taskbar_hole(self):
        """Ensures the Windows taskbar region is normal (no hole)."""
        if not user32:
            return
        try:
            tray = user32.FindWindowW("Shell_TrayWnd", None)
            if tray:
                user32.SetWindowRgn(tray, None, True)
        except Exception:
            pass

    def attach_tray_ownership(self):
        """
        Sets the Windows taskbar (Shell_TrayWnd) as the owner of Clawd's window
        when running as a top-level window.
        """
        if not user32 or not SetWindowLongPtr or not self.isVisible() or self.hidden_by_fullscreen or self._is_embedded:
            return
        try:
            hwnd = int(self.winId())
            if not hwnd:
                return

            tray = user32.FindWindowW("Shell_TrayWnd", None)
            if not tray:
                return

            current_owner = user32.GetWindow(hwnd, GW_OWNER)
            if current_owner != tray:
                SetWindowLongPtr(hwnd, GWLP_HWNDPARENT, tray)
                user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_FLAGS_SILENT)
        except Exception:
            pass

    def showEvent(self, event):
        super().showEvent(event)
        if self.placement_mode == "bottom":
            if not self._is_embedded:
                self.embed_in_taskbar()
        else:
            self.attach_tray_ownership()
            self.assert_topmost()
        if not getattr(self, "_startup_animated", False):
            self.schedule_startup_entrance()

    def closeEvent(self, event):
        if self._is_embedded:
            self.unembed_from_taskbar()
        self.restore_taskbar_hole()
        super().closeEvent(event)

    def moveEvent(self, event):
        super().moveEvent(event)

    def get_trays(self):
        """Returns cached HWNDs for primary and secondary Windows taskbars."""
        if not self._cached_trays and user32:
            hwnd_tray = user32.FindWindowW("Shell_TrayWnd", None)
            hwnd_tray2 = user32.FindWindowW("Shell_SecondaryTrayWnd", None)
            self._cached_trays = {h for h in (hwnd_tray, hwnd_tray2) if h}
        return self._cached_trays

    def is_shell_active(self):
        """Detects if the Windows taskbar, Start Menu, or action center is currently active."""
        if not user32:
            return False
        try:
            fg = user32.GetForegroundWindow()
            if not fg:
                return False
            cls = ctypes.create_unicode_buffer(256)
            user32.GetClassNameW(fg, cls, 256)
            shell_classes = {
                "Shell_TrayWnd", "Shell_SecondaryTrayWnd",
                "Windows.UI.Core.CoreWindow", "XamlExplorerHostIslandWindow",
                "DV2ControlHost", "ControlCenterWindow"
            }
            return cls.value in shell_classes
        except Exception:
            return False

    def assert_topmost(self):
        """Silently asserts topmost Z-order and taskbar ownership without redrawing."""
        if not user32 or not self.isVisible() or self.hidden_by_fullscreen or self._is_embedded:
            return
        try:
            self.attach_tray_ownership()
            hwnd = int(self.winId())
            user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_FLAGS_SILENT)
        except Exception:
            pass

    def is_occluded(self):
        """
        Checks if Clawd's visible pixels are physically occluded in the Z-order
        by any overlapping external application window (only relevant in top mode).
        """
        if not user32 or not self.isVisible() or self.hidden_by_fullscreen or self._is_embedded:
            return False
        try:
            hwnd = int(self.winId())
            clawd_vis_rect = (
                self.x(),
                self.y() + (4 * self.scale_factor),
                self.x() + self.width(),
                self.y() + (12 * self.scale_factor)
            )
            my_pid = os.getpid()

            curr = hwnd
            for _ in range(50):
                curr = user32.GetWindow(curr, GW_HWNDPREV)
                if not curr:
                    break

                if not user32.IsWindowVisible(curr):
                    continue

                pid = wintypes.DWORD()
                user32.GetWindowThreadProcessId(curr, ctypes.byref(pid))
                if pid.value == my_pid:
                    continue

                r = wintypes.RECT()
                if user32.GetWindowRect(curr, ctypes.byref(r)):
                    if not (r.right <= clawd_vis_rect[0] or r.left >= clawd_vis_rect[2] or
                            r.bottom <= clawd_vis_rect[1] or r.top >= clawd_vis_rect[3]):
                        return True

            return False
        except Exception:
            return False

    def _check_zorder_safety(self):
        """
        Runs smoothly every 60ms with zero CPU overhead:
        1. When embedded in taskbar ('bottom' mode): maintains WS_CHILD hierarchy inside Shell_TrayWnd
           so Clawd is rendered by DWM directly as part of the taskbar and never occluded by Windows panels.
        2. When top-level ('top' mode): maintains Shell_TrayWnd ownership and asserts topmost Z-order.
        """
        if not user32 or not self.isVisible() or self.hidden_by_fullscreen or getattr(self, "is_lifted", False) or self.is_dragging:
            return

        if self.placement_mode == "bottom":
            if not self._is_embedded:
                self.embed_in_taskbar()
                return
            try:
                hwnd = int(self.winId())
                tray = user32.FindWindowW("Shell_TrayWnd", None)
                if tray:
                    parent = user32.GetAncestor(hwnd, 1)  # GA_PARENT = 1
                    if parent != tray:
                        self.embed_in_taskbar()
                    else:
                        user32.BringWindowToTop(hwnd)
            except Exception:
                pass
            return

        # Top mode handling
        try:
            hwnd = int(self.winId())
            tray = user32.FindWindowW("Shell_TrayWnd", None)
            if tray:
                current_owner = user32.GetWindow(hwnd, GW_OWNER)
                if current_owner != tray:
                    SetWindowLongPtr(hwnd, GWLP_HWNDPARENT, tray)
                    user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_FLAGS_SILENT)
        except Exception:
            pass

        # Topmost safety against external overlapping windows
        if self.is_occluded():
            now = time.monotonic()
            if now - self._last_topmost_assert_time > 0.3:
                self.assert_topmost()
                self._last_topmost_assert_time = now
        else:
            self._last_topmost_assert_time = 0.0

    def enterEvent(self, event):
        """Hovering over Clawd ensures he is always at the top of the stack for clicks/drag."""
        super().enterEvent(event)
        if self.placement_mode == "bottom" and self._is_embedded:
            hwnd = int(self.winId())
            if user32 and hwnd:
                user32.BringWindowToTop(hwnd)
        else:
            self.assert_topmost()

    def leaveEvent(self, event):
        """When mouse leaves Clawd, reset petting position and smoothly fade blush."""
        self._last_pet_mouse_pos = None
        if self.pet_blush_level > 0.0 and not self._pet_timer.isActive():
            self._pet_timer.start(35)
        super().leaveEvent(event)

    def get_current_cheek_y(self) -> int:
        """Determines the row Y for cheeks in the current animation frame."""
        if self.current_anim_name == "jump":
            jump_offsets = {0: 6, 1: 7, 2: 4, 3: 3, 4: 5, 5: 7, 6: 6}
            return jump_offsets.get(self.current_frame_idx, 6)
        return 6

    def _update_pet_blush_decay(self):
        """Gradually decays cheek blush over time when cursor stops moving or leaves."""
        now = time.monotonic()
        # Start decaying 0.4s after the last petting stroke
        if now - self._last_pet_time >= 0.4:
            self.pet_blush_level = max(0.0, self.pet_blush_level - 0.02)
            self.update()
            if self.pet_blush_level <= 0.0:
                self._pet_timer.stop()

    # --- Sprite & Animation Loading ---

    def load_all_sprites(self):
        """Loads and organizes all raw 16x16 frames."""
        self.raw_animations = {}

        # 1. Base / Idle
        base_img = QImage(BASE_IMAGE_PATH)
        if base_img.isNull():
            base_img = QImage(16, 16, QImage.Format.Format_ARGB32)
            base_img.fill(0)
        self.raw_animations["idle"] = [base_img]

        # 2. Right arm up fallback
        arm_img = QImage(ARM_IMAGE_PATH)
        if not arm_img.isNull():
            self.raw_animations["right_arm_up"] = [arm_img]

        # 3. Load all generated animations from animations/ directory
        if os.path.exists(ANIM_DIR):
            png_files = sorted(glob.glob(os.path.join(ANIM_DIR, "*.png")))
            for filepath in png_files:
                basename = os.path.splitext(os.path.basename(filepath))[0]
                if "_" in basename:
                    anim_name, _ = basename.rsplit("_", 1)
                    if anim_name not in self.raw_animations:
                        self.raw_animations[anim_name] = []
                    img = QImage(filepath)
                    if not img.isNull():
                        self.raw_animations[anim_name].append(img)

        # 4. Generate startup peek entrance animation (emerging from below)
        if "peek" in self.raw_animations and len(self.raw_animations["peek"]) >= 7:
            p = self.raw_animations["peek"]
            # p[2]: eyes peeking out center
            # p[3]: glance left
            # p[4]: glance right
            # p[5]: climb up halfway
            # p[6]: stand tall
            self.raw_animations["peek_entrance"] = [
                p[2],  # Initial peek out center
                p[2],  # Hold initial glance
                p[3],  # Glance left
                p[2],  # Glance center
                p[4],  # Glance right
                p[5],  # Climb up onto taskbar
                p[6],  # Stand tall
            ]

    def update_scaled_pixmaps(self):
        """Generates crisp scaled QPixmaps for all animation frames."""
        w = 16 * self.scale_factor
        h = 16 * self.scale_factor

        self.scaled_animations = {}
        for anim_name, img_list in self.raw_animations.items():
            self.scaled_animations[anim_name] = [
                QPixmap.fromImage(img).scaled(
                    w, h,
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.FastTransformation
                )
                for img in img_list
            ]

        self.setFixedSize(w, h)
        self._update_current_pixmap()

    def _update_current_pixmap(self):
        frames = self.scaled_animations.get(self.current_anim_name, self.scaled_animations.get("idle", []))
        if frames:
            idx = min(self.current_frame_idx, len(frames) - 1)
            self.current_pixmap = frames[idx]
        else:
            self.current_pixmap = None
        self.update()

    def play_animation(self, name, loop=False, speed_ms=120, on_finished=None):
        """Plays animation by name."""
        if name not in self.scaled_animations:
            name = "idle"

        # Instantly remove cheeks when any animation is triggered
        if name != "idle":
            self.pet_blush_level = 0.0
            self._last_pet_mouse_pos = None
            if hasattr(self, "_pet_timer") and self._pet_timer.isActive():
                self._pet_timer.stop()

        self.current_anim_name = name
        self.current_frame_idx = 0
        self.is_looping = loop
        self.on_anim_finished = on_finished
        self._update_current_pixmap()

        self.anim_timer.stop()
        if len(self.scaled_animations.get(name, [])) > 1 or loop:
            self.anim_timer.start(speed_ms)

    def play_idle(self):
        self.play_animation("idle", loop=False)

    def schedule_startup_entrance(self):
        """Schedules the cute peek-out entrance animation upon first appearance."""
        if self._startup_animated or getattr(self, "_startup_entrance_scheduled", False):
            return
        self._startup_entrance_scheduled = True
        # If launched right during Windows boot, wait for taskbar & DWM to settle (1.4s)
        # Otherwise for normal app launches, brief 250ms delay for smooth initial painting
        delay = 1400 if getattr(self, "_is_system_boot", False) else 250
        QTimer.singleShot(delay, self.play_startup_entrance)

    def play_startup_entrance(self):
        """Plays the entrance animation where Clawd emerges and peeks out from below."""
        if self._startup_animated:
            return
        self._startup_animated = True

        if "peek_entrance" in self.scaled_animations:
            self.play_animation("peek_entrance", loop=False, speed_ms=125, on_finished=self.play_idle)
        elif "peek" in self.scaled_animations:
            self.play_animation("peek", loop=False, speed_ms=120, on_finished=self.play_idle)
        else:
            self.play_idle()

    def _advance_anim_frame(self):
        frames = self.scaled_animations.get(self.current_anim_name, [])
        if not frames:
            self.anim_timer.stop()
            return

        if self.current_frame_idx + 1 < len(frames):
            self.current_frame_idx += 1
            self._update_current_pixmap()
        else:
            if self.is_looping:
                self.current_frame_idx = 0
                self._update_current_pixmap()
            else:
                self.anim_timer.stop()
                if self.on_anim_finished:
                    cb = self.on_anim_finished
                    self.on_anim_finished = None
                    cb()
                else:
                    if self.smart_context_enabled and self.is_claude_coding:
                        self.play_animation("typing", loop=True, speed_ms=110)
                    elif self.smart_context_enabled and self.is_sleeping_afk:
                        self.play_animation("sleep", loop=True, speed_ms=200)
                    else:
                        self.play_idle()
                        self._schedule_next_idle(10000, 25000)

    def _schedule_next_idle(self, min_ms=None, max_ms=None):
        if not self.idle_animations_enabled:
            return
        if min_ms is None or max_ms is None:
            if self.idle_frequency_mode == "active":
                min_ms, max_ms = 6000, 12000
            elif self.idle_frequency_mode == "relaxed":
                min_ms, max_ms = 25000, 50000
            else:  # normal
                min_ms, max_ms = 12000, 22000
        interval = random.randint(min_ms, max_ms)
        self.idle_timer.stop()
        self.idle_timer.start(interval)

    def _trigger_random_idle_action(self):
        if not self.idle_animations_enabled or self.is_dragging or getattr(self, "is_lifted", False) or self.hidden_by_fullscreen:
            return
        if self.smart_context_enabled and (self.is_claude_coding or self.is_sleeping_afk):
            return
        if self.current_anim_name != "idle":
            self._schedule_next_idle()
            return

        # Rich, balanced pool with ALL animations!
        # Notice: Laptop coding animations (typing, laptop_*) are excluded from random pool:
        # they strictly trigger when real Claude Code is coding!
        is_dev = self.smart_context_enabled and self._is_dev_window_active()
        if is_dev:
            # Active in IDE/Terminal: mostly everyday cute defaults, with occasional developer flashes
            all_choices = [
                ("blink", 28),
                ("look_around", 20),
                ("dance", 18),
                ("wave", 12),
                ("coffee", 8),
                ("spark", 8),
                ("matrix", 6),
                ("wizard", 5),
                ("idea", 5),
                ("workout", 3),
                ("shield", 2),
            ]
        else:
            # Cozy desktop: primarily default everyday movements (blink, look_around, dance, wave)
            # Rare easter eggs have tiny 2-3% chance each!
            all_choices = [
                ("blink", 35),        # Default: natural cute blinking
                ("look_around", 24),  # Default: curious looking around
                ("dance", 20),        # Default: cheerful little mascot dance
                ("wave", 14),         # Default: friendly paw wave
                ("coffee", 8),        # Cozy sip of coffee
                ("spark", 8),         # Cute spark
                # Rare easter eggs (occasional rare surprise):
                ("matrix", 3),        # Rare cyber matrix stream
                ("idea", 3),          # Rare idea bulb
                ("peek", 3),          # Rare peek under taskbar
                ("jump", 3),          # Rare bounce jump
                ("heart", 3),         # Rare love heart
                ("chat", 3),          # Rare thought bubble
                ("wizard", 2),        # Rare wizard hat magic
                ("workout", 2),       # Rare barbell workout
                ("shield", 2),        # Rare energy shield
                ("question", 2),      # Rare question mark
                ("spin", 2),          # Rare 360 spin
            ]

        # Anti-repeat filter: exclude animations played in the last 4 rounds for maximum fresh variety!
        eligible = [(name, w) for name, w in all_choices if name not in self._recent_idle_history]
        if not eligible:
            eligible = all_choices

        total = sum(w for _, w in eligible)
        r = random.randint(1, total)
        accum = 0
        selected = eligible[0][0]
        for name, weight in eligible:
            accum += weight
            if r <= accum:
                selected = name
                break

        # Update recent history
        self._recent_idle_history.append(selected)
        if len(self._recent_idle_history) > 4:
            self._recent_idle_history.pop(0)

        # Precise speed per animation
        speeds = {
            "blink": 90,
            "wave": 110,
            "matrix": 110,
            "wizard": 120,
            "workout": 110,
            "dance": 120,
            "jump": 100,
            "heart": 130,
            "coffee": 130,
            "idea": 120,
            "spark": 110,
            "chat": 120,
            "peek": 120,
            "shield": 120,
            "look_around": 130,
            "question": 130,
        }
        speed = speeds.get(selected, 120)
        self.play_animation(selected, loop=False, speed_ms=speed)

    def trigger_click_reaction(self):
        """Random playful reaction when user clicks on Clawd."""
        if self.is_sleeping_afk:
            self.is_sleeping_afk = False
            self.setToolTip(self.t("tooltip_default"))
            self.play_animation("wave", loop=False, speed_ms=110, on_finished=self.play_idle)
            return
        reactions = [
            ("wave", 110),
            ("cheer", 120),
            ("jump", 100),
            ("heart", 130),
            ("dance", 120),
            ("spark", 110),
            ("chat", 120),
            ("shield", 120),
            ("coffee", 140),
            ("wizard", 120),
            ("workout", 120),
            ("idea", 120),
            ("spin", 90),
        ]
        name, speed = random.choice(reactions)
        self.play_animation(name, loop=False, speed_ms=speed)

    # --- Screen Coordinates & Positioning ---

    def get_current_screen(self, pos=None):
        target = pos if pos is not None else self.pos()
        screen = QApplication.screenAt(target)
        if not screen:
            screen = QApplication.screenAt(QCursor.pos())
        if not screen:
            screen = QApplication.primaryScreen()
        return screen

    def get_taskbar_surface_y(self, screen=None):
        """Returns the Y coordinate of the top surface/ledge of the taskbar."""
        if screen is None:
            screen = self.get_current_screen()
        avail = screen.availableGeometry()
        geom = screen.geometry()
        if avail.height() < geom.height() and avail.top() == geom.top():
            return avail.bottom() + 1
        return geom.bottom() + 1

    def get_taskbar_top_y(self, screen=None):
        """
        Calculates Y coordinate so Clawd's feet rest perfectly on top of the taskbar ledge.
        Clawd is completely outside the taskbar rect and NEVER gets occluded by Start menu/taskbar.
        """
        surface_y = self.get_taskbar_surface_y(screen)
        feet_offset = 12 * self.scale_factor
        return surface_y - feet_offset

    def get_taskbar_bottom_y(self, screen=None):
        """Calculates Y coordinate so Clawd's feet rest at the bottom of the screen (inside taskbar)."""
        if screen is None:
            screen = self.get_current_screen()
        geom = screen.geometry()
        feet_offset = 12 * self.scale_factor
        return geom.top() + geom.height() - feet_offset

    def get_target_taskbar_y(self, screen=None):
        if self.placement_mode == "top":
            return self.get_taskbar_top_y(screen)
        else:
            if self._is_embedded:
                tray_r = self.get_tray_rect()
                tray_h = (tray_r.bottom - tray_r.top) if tray_r else 48
                return tray_h - (12 * self.scale_factor)
            else:
                return self.get_taskbar_bottom_y(screen)

    def get_default_position(self, screen=None):
        """Calculates default position based on current placement mode near the tray."""
        if self.placement_mode == "bottom" and self._is_embedded:
            tray_r = self.get_tray_rect()
            tray_w = (tray_r.right - tray_r.left) if tray_r else 1920
            tray_h = (tray_r.bottom - tray_r.top) if tray_r else 48
            x = int(tray_w * 0.8) - (self.width() // 2)
            y = tray_h - (12 * self.scale_factor)
            return QPoint(x, y)
        if screen is None:
            screen = self.get_current_screen()
        geom = screen.geometry()
        x = int(geom.left() + geom.width() * 0.8) - (self.width() // 2)
        y = self.get_target_taskbar_y(screen)
        return QPoint(x, y)

    def clamp_position(self, pos, screen=None):
        """
        Keeps Clawd on screen or within taskbar. If snap_to_taskbar is enabled,
        magnetically snaps him to his designated position.
        """
        if self.placement_mode == "bottom" and self._is_embedded:
            tray_r = self.get_tray_rect()
            tray_w = (tray_r.right - tray_r.left) if tray_r else 1920
            tray_h = (tray_r.bottom - tray_r.top) if tray_r else 48

            min_x = 0
            max_x = tray_w - self.width()
            clamped_x = max(min_x, min(max_x, pos.x()))

            target_y = tray_h - (12 * self.scale_factor)
            if self.snap_to_taskbar:
                clamped_y = target_y
            else:
                clamped_y = max(0, min(tray_h - self.height(), pos.y()))
            return QPoint(clamped_x, clamped_y)

        if screen is None:
            screen = self.get_current_screen(pos)
        geom = screen.geometry()

        min_x = geom.left()
        max_x = geom.left() + geom.width() - self.width()
        clamped_x = max(min_x, min(max_x, pos.x()))

        min_y = geom.top()
        bottom_limit = self.get_taskbar_bottom_y(screen)
        target_tb_y = self.get_target_taskbar_y(screen)

        if self.snap_to_taskbar:
            if abs(pos.y() - target_tb_y) < 35 or pos.y() > target_tb_y:
                clamped_y = target_tb_y
            else:
                clamped_y = max(min_y, min(bottom_limit, pos.y()))
        else:
            clamped_y = max(min_y, min(bottom_limit, pos.y()))

        return QPoint(clamped_x, clamped_y)

    def load_config(self):
        self.saved_pos = None
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.scale_factor = 3
                    self.placement_mode = "bottom"
                    self.auto_peek_on_shell = data.get("auto_peek_on_shell", False)
                    self.snap_to_taskbar = data.get("snap_to_taskbar", True)
                    self.idle_animations_enabled = data.get("idle_animations_enabled", True)
                    self.auto_hide_fullscreen = data.get("auto_hide_fullscreen", False)
                    self.smart_context_enabled = True
                    self.idle_animations_enabled = True
                    self.auto_hide_fullscreen = True
                    self.idle_frequency_mode = "normal"
                    self.language = data.get("language", "system")
                    self.roam_enabled = data.get("roam_enabled", True)
                    self.roam_screen_min_x = data.get("roam_screen_min_x", None)
                    self.roam_screen_max_x = data.get("roam_screen_max_x", None)
                    if "x" in data and "y" in data:
                        self.saved_pos = QPoint(data["x"], data["y"])
            except Exception as e:
                print("Failed to load config:", e)

    def save_config(self):
        try:
            if self.placement_mode == "bottom" and self._is_embedded:
                tray_r = self.get_tray_rect()
                hwnd = int(self.winId()) if user32 else None
                if hwnd and user32:
                    wr = wintypes.RECT()
                    if user32.GetWindowRect(hwnd, ctypes.byref(wr)):
                        screen_x = wr.left
                        screen_y = wr.top
                    else:
                        screen_x = self.saved_pos.x() if self.saved_pos else 1451
                        screen_y = (tray_r.top if tray_r else 1032) + 12
                else:
                    screen_x = self.saved_pos.x() if self.saved_pos else 1451
                    screen_y = (tray_r.top if tray_r else 1032) + 12
            else:
                screen_x = self.x()
                screen_y = self.y()
                if self.is_peeked_up:
                    screen_y = self.get_taskbar_bottom_y()

            data = {
                "x": screen_x,
                "y": screen_y,
                "scale_factor": self.scale_factor,
                "placement_mode": self.placement_mode,
                "auto_peek_on_shell": self.auto_peek_on_shell,
                "snap_to_taskbar": self.snap_to_taskbar,
                "idle_animations_enabled": self.idle_animations_enabled,
                "auto_hide_fullscreen": self.auto_hide_fullscreen,
                "smart_context_enabled": True,
                "idle_frequency_mode": self.idle_frequency_mode,
                "language": getattr(self, "language", "system"),
                "roam_enabled": self.roam_enabled,
                "roam_screen_min_x": self.roam_screen_min_x,
                "roam_screen_max_x": self.roam_screen_max_x
            }
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print("Failed to save config:", e)

    def ensure_valid_position(self):
        if self.placement_mode == "bottom":
            return
        else:
            if self.saved_pos:
                self.move(self.clamp_position(self.saved_pos))
            else:
                self.move(self.clamp_position(self.get_default_position()))

    def paintEvent(self, event):
        if self.current_pixmap:
            painter = QPainter(self)
            painter.drawPixmap(0, 0, self.current_pixmap)

            # Sweet blushing cheeks when petted (strictly in idle state, instantly hidden during animations)
            if self.current_anim_name == "idle" and self.pet_blush_level > 0.01:
                s = self.scale_factor
                cy = self.get_current_cheek_y()

                # High-contrast vibrant anime-style rosy pink blush
                alpha = int(self.pet_blush_level * 255)
                blush_color = QColor(255, 50, 130, alpha)
                painter.fillRect(4 * s, cy * s, s, s, blush_color)
                painter.fillRect(11 * s, cy * s, s, s, blush_color)

                # Expansion to (3, cy) and (12, cy) when stroked warmly
                if self.pet_blush_level > 0.25:
                    sub_alpha = int((self.pet_blush_level - 0.25) / 0.75 * 240)
                    sub_color = QColor(255, 85, 155, sub_alpha)
                    painter.fillRect(3 * s, cy * s, s, s, sub_color)
                    painter.fillRect(12 * s, cy * s, s, s, sub_color)

    def set_scale(self, factor):
        new_factor = max(2, min(8, factor))
        if new_factor == self.scale_factor:
            return

        self.scale_factor = new_factor
        self.update_scaled_pixmaps()

        if self.placement_mode == "bottom" and self._is_embedded:
            tray_r = self.get_tray_rect()
            if tray_r:
                tray_w = tray_r.right - tray_r.left
                tray_h = tray_r.bottom - tray_r.top
                target_y = tray_h - (12 * self.scale_factor)
                hwnd = int(self.winId())
                if user32 and hwnd:
                    wr = wintypes.RECT()
                    user32.GetWindowRect(hwnd, ctypes.byref(wr))
                    local_x = max(0, min(tray_w - self.width(), wr.left - tray_r.left))
                    user32.SetWindowPos(hwnd, 0, local_x, target_y, self.width(), self.height(), 0x0040)
        else:
            screen = self.get_current_screen()
            new_y = self.get_target_taskbar_y(screen)
            self.move(self.clamp_position(QPoint(self.x(), new_y)))
            self.assert_topmost()

        self.save_config()
        self.rebuild_tray_menu()


    # --- Smart Context Logic (Claude Code, AFK Sleep, IDE Focus) ---



    def _poll_claude_code(self):
        """
        Polls for active coding in Claude Code.
        Returns: (is_coding: bool, project_name: str)
        """
        claude_dir = os.path.expanduser("~/.claude")
        sessions_dir = os.path.join(claude_dir, "sessions")
        if not os.path.exists(sessions_dir):
            return False, ""

        active_project = ""
        now = time.time()

        # 1. Primary signal: Active session status in ~/.claude/sessions/*.json
        try:
            for fname in os.listdir(sessions_dir):
                if not fname.endswith(".json"):
                    continue
                fpath = os.path.join(sessions_dir, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    pid = data.get("pid")
                    status = data.get("status")
                    cwd = data.get("cwd", "")

                    is_alive = False
                    if pid:
                        if psutil:
                            is_alive = psutil.pid_exists(pid)
                        elif user32:
                            h_proc = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
                            if h_proc:
                                ctypes.windll.kernel32.CloseHandle(h_proc)
                                is_alive = True

                    if is_alive:
                        proj = os.path.basename(cwd) if cwd else ""
                        if proj:
                            active_project = proj
                        if status == "busy":
                            return True, proj
                except Exception:
                    continue
        except Exception:
            pass

        # 2. Secondary signal: recent writes to project .jsonl transcripts (last 3.5s)
        projects_dir = os.path.join(claude_dir, "projects")
        try:
            if os.path.exists(projects_dir):
                for proj in os.listdir(projects_dir):
                    proj_path = os.path.join(projects_dir, proj)
                    if not os.path.isdir(proj_path):
                        continue
                    for item in os.listdir(proj_path):
                        if item.endswith(".jsonl"):
                            p = os.path.join(proj_path, item)
                            try:
                                if (now - os.path.getmtime(p)) < 3.5:
                                    clean_proj = proj.replace("U--", "").replace("C--", "").split("--")[-1]
                                    return True, clean_proj or active_project
                            except OSError:
                                pass
        except Exception:
            pass

        return False, active_project

    def _get_user_idle_seconds(self) -> float:
        """Returns number of seconds since last user input (mouse/keyboard)."""
        if not user32 or not kernel32:
            return 0.0
        try:
            lii = LASTINPUTINFO()
            lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
            if user32.GetLastInputInfo(ctypes.byref(lii)):
                tick_now = kernel32.GetTickCount()
                diff = tick_now - lii.dwTime
                if diff >= 0:
                    return diff / 1000.0
        except Exception:
            pass
        return 0.0

    def _is_dev_window_active(self) -> bool:
        """Checks if the user currently has an IDE, editor, or terminal active in foreground."""
        if not user32:
            return False
        try:
            hwnd = user32.GetForegroundWindow()
            if not hwnd:
                return False

            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buff, length + 1)
                title = buff.value.lower()
                dev_keywords = (
                    "visual studio", "cursor", "pycharm", "intellij", "webstorm",
                    "terminal", "powershell", "cmd.exe", "bash", "sublime", "neovim",
                    "antigravity", "claude code", "workspace"
                )
                if any(kw in title for kw in dev_keywords):
                    return True

            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            if pid.value and psutil:
                try:
                    proc_name = psutil.Process(pid.value).name().lower()
                    dev_procs = (
                        "code.exe", "cursor.exe", "pycharm64.exe", "idea64.exe",
                        "windowsterminal.exe", "powershell.exe", "cmd.exe", "devenv.exe",
                        "antigravity.exe", "webstorm64.exe", "wt.exe", "claude.exe"
                    )
                    if proc_name in dev_procs:
                        return True
                except Exception:
                    pass
        except Exception:
            pass
        return False

    def _check_contextual_state(self):
        """Called every 1 second by context_timer to check Claude Code, AFK sleep, etc."""
        if not self.smart_context_enabled:
            return
        if self.is_dragging or getattr(self, "is_lifted", False) or self.hidden_by_fullscreen:
            return

        now = time.time()

        # --- 1. Claude Code Detection (Highest Priority) ---
        raw_coding, project_name = self._poll_claude_code()
        if raw_coding:
            self._last_coding_time = now
            if project_name:
                self._current_coding_project = project_name

        # Hold coding state for 2.5s between rapid tool calls to prevent flapping
        is_coding = raw_coding or (self.is_claude_coding and (now - self._last_coding_time < 2.5))

        if is_coding and not self.is_claude_coding:
            # Transition: Claude Code started generating/writing code!
            self.is_claude_coding = True
            self.is_sleeping_afk = False
            self.idle_timer.stop()
            if self._roam_step_timer.isActive():
                self._roam_step_timer.stop()
            self.roam_timer.stop()
            proj_label = f" ({self._current_coding_project})" if self._current_coding_project else ""
            self.setToolTip(f"{self.t('tooltip_coding')}{proj_label}")
            # Classic laptop animation (typing) as originally was!
            self.play_animation("typing", loop=True, speed_ms=110)
            return

        elif not is_coding and self.is_claude_coding:
            # Transition: Claude Code finished coding!
            self.is_claude_coding = False
            self.setToolTip(self.t("tooltip_coding_done"))
            celebration = random.choice(["cheer", "spark"])
            def on_celebration_done():
                self.setToolTip(self.t("tooltip_default"))
                self.play_idle()
                self._schedule_next_idle(8000, 20000)
                self._schedule_next_roam(120, 240)
            self.play_animation(celebration, loop=False, speed_ms=120, on_finished=on_celebration_done)
            return

        if self.is_claude_coding:
            return

        # --- 2. AFK Inactivity Check (5 minutes = 300 seconds) ---
        afk_seconds = self._get_user_idle_seconds()
        AFK_THRESHOLD = 300  # 5 minutes

        if afk_seconds >= AFK_THRESHOLD and not self.is_sleeping_afk:
            # User has stepped away: Clawd curls up to sleep
            self.is_sleeping_afk = True
            self.idle_timer.stop()
            self.setToolTip(self.t("tooltip_afk"))
            self.play_animation("sleep", loop=True, speed_ms=200)
            return

        elif afk_seconds < 2.0 and self.is_sleeping_afk:
            # User returned to PC: Clawd wakes up and greets!
            self.is_sleeping_afk = False
            self.setToolTip(self.t("tooltip_default"))
            wake_reaction = random.choice(["wave", "look_around"])
            def on_wake_done():
                self.play_idle()
                self._schedule_next_idle(6000, 18000)
            self.play_animation(wake_reaction, loop=False, speed_ms=120, on_finished=on_wake_done)
            return

        if self.is_sleeping_afk:
            return

    # --- Mouse Events: Free Dragging & Reactions ---

    def mousePressEvent(self, event):
        # Instantly remove cheeks when clicked
        self.pet_blush_level = 0.0
        self._last_pet_mouse_pos = None
        if hasattr(self, "_pet_timer") and self._pet_timer.isActive():
            self._pet_timer.stop()
        self.update()

        if event.button() == Qt.MouseButton.LeftButton:
            # Cancel any ongoing slow roaming step immediately
            if self._roam_step_timer.isActive():
                self._roam_step_timer.stop()
                self._roam_steps_remaining = 0
            self.drag_start_pos = event.globalPosition().toPoint()
            self.is_dragging = False
            self.is_lifted = False

            if self.placement_mode == "bottom" and self._is_embedded and user32:
                hwnd = int(self.winId())
                wr = wintypes.RECT()
                user32.GetWindowRect(hwnd, ctypes.byref(wr))
                self.window_start_screen_x = wr.left
                self.window_start_pos = self.pos()
            else:
                self.window_start_pos = self.pos()
                self.window_start_screen_x = self.x()

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.MouseButton.LeftButton) and self.drag_start_pos:
            delta = event.globalPosition().toPoint() - self.drag_start_pos

            # Rule: Cannot drag horizontally directly on the taskbar.
            # Must first pull UPWARDS by at least 8px (negative Y) to lift Clawd off the floor!
            LIFT_THRESHOLD = 8

            if not self.is_lifted:
                if delta.y() <= -LIFT_THRESHOLD:
                    self.is_lifted = True
                    self.is_dragging = True
                    # Play looping drag animation with chosen variant (no mouth, minimalist paws)
                    self.play_animation("drag", loop=True, speed_ms=90)
                else:
                    # User only moved horizontally or downwards:
                    # Clawd resists and stays planted on the floor!
                    return

            if self.is_lifted:
                if self.placement_mode == "bottom" and self._is_embedded and user32:
                    tray_r = self.get_tray_rect()
                    if tray_r:
                        tray_w = tray_r.right - tray_r.left
                        tray_h = tray_r.bottom - tray_r.top
                        start_x = self.window_start_screen_x if self.window_start_screen_x is not None else (tray_r.left + self.x())
                        target_screen_x = start_x + delta.x()
                        local_x = max(0, min(tray_w - self.width(), target_screen_x - tray_r.left))

                        # Lifted off the floor: move up from floor (12) towards top of taskbar (0)
                        floor_y = tray_h - (12 * self.scale_factor)
                        lift_offset = min(floor_y, max(8, -delta.y()))
                        lifted_y = max(0, floor_y - lift_offset)

                        hwnd = int(self.winId())
                        user32.SetWindowPos(hwnd, 0, local_x, lifted_y, self.width(), self.height(), 0x0040)
                        user32.BringWindowToTop(hwnd)
                else:
                    # Top placement mode:
                    start_pos = self.window_start_pos if self.window_start_pos else self.pos()
                    target_pos = start_pos + delta
                    self.move(self.clamp_position(target_pos))
                    self.assert_topmost()
        else:
            # Petting interaction (strictly on top of Clawd's head in idle stance)
            if self.current_anim_name != "idle":
                if self.pet_blush_level > 0.0:
                    self.pet_blush_level = 0.0
                    self.update()
                self._last_pet_mouse_pos = None
                return

            curr_pos = event.pos()
            s = self.scale_factor
            # "гладить его нужно сверху головы, а не на самом кловде"
            # Crown of the head zone: upper area of widget (rows 0-5), horizontal head span (x: 2..14)
            is_above_head = (curr_pos.y() <= 5 * s) and (2 * s <= curr_pos.x() <= 14 * s)

            if is_above_head:
                if self._last_pet_mouse_pos is not None:
                    dist = (curr_pos - self._last_pet_mouse_pos).manhattanLength()
                    if dist >= 1:
                        # Stroke detected on crown of head: increase blush smoothly
                        step = min(0.08, max(0.02, dist * 0.008))
                        self.pet_blush_level = min(1.0, self.pet_blush_level + step)
                        self._last_pet_time = time.monotonic()
                        if not self._pet_timer.isActive():
                            self._pet_timer.start(35)
                        self.update()
                self._last_pet_mouse_pos = curr_pos
            else:
                self._last_pet_mouse_pos = None

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.is_lifted:
                if self.placement_mode == "bottom" and self._is_embedded and user32:
                    tray_r = self.get_tray_rect()
                    if tray_r:
                        tray_w = tray_r.right - tray_r.left
                        tray_h = tray_r.bottom - tray_r.top
                        delta = event.globalPosition().toPoint() - self.drag_start_pos if self.drag_start_pos else QPoint(0, 0)
                        start_x = self.window_start_screen_x if self.window_start_screen_x is not None else (tray_r.left + self.x())
                        target_screen_x = start_x + delta.x()
                        local_x = max(0, min(tray_w - self.width(), target_screen_x - tray_r.left))
                        floor_y = tray_h - (12 * self.scale_factor)
                        hwnd = int(self.winId())
                        user32.SetWindowPos(hwnd, 0, local_x, floor_y, self.width(), self.height(), 0x0040)
                        user32.BringWindowToTop(hwnd)
                        self.saved_pos = QPoint(tray_r.left + local_x, tray_r.top + floor_y)
                else:
                    screen = self.get_current_screen()
                    target_y = self.get_taskbar_top_y(screen) if self.placement_mode == "top" else self.get_taskbar_bottom_y(screen)
                    self.move(self.clamp_position(QPoint(self.x(), target_y)))
                    self.assert_topmost()

                self.save_config()

                # Squish landing upon touchdown, then transition smoothly to idle!
                self.play_animation("land", loop=False, speed_ms=100)
                def on_after_land():
                    if self.smart_context_enabled and self.is_claude_coding:
                        self.play_animation("typing", loop=True, speed_ms=110)
                    else:
                        self.play_idle()
                QTimer.singleShot(220, on_after_land)
            else:
                delta = event.globalPosition().toPoint() - self.drag_start_pos if self.drag_start_pos else QPoint(0, 0)
                if delta.manhattanLength() < 6:
                    self.trigger_click_reaction()
                else:
                    self.play_idle()

            self.drag_start_pos = None
            self.window_start_pos = None
            self.window_start_screen_x = None
            self.is_dragging = False
            self.is_lifted = False

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            hype = random.choice(["jump", "cheer", "spin"])
            self.play_animation(hype, loop=False, speed_ms=100)

    def wheelEvent(self, event):
        pass

    # --- Fullscreen Game Auto-Hide (Clean) ---

    def _check_fullscreen(self):
        if not self.auto_hide_fullscreen:
            if self.hidden_by_fullscreen:
                self.hidden_by_fullscreen = False
                self.show()
                if self.placement_mode == "bottom":
                    if not self._is_embedded:
                        self.embed_in_taskbar()
                else:
                    self.assert_topmost()
            return

        if not shell32:
            return

        try:
            state = wintypes.DWORD()
            res = shell32.SHQueryUserNotificationState(ctypes.byref(state))
            if res == 0:
                # 2 = QUNS_BUSY (exclusive fullscreen game/presentation)
                # 3 = QUNS_RUNNING_D3D_FULL_SCREEN (DirectX exclusive fullscreen)
                is_game = state.value in (2, 3)
                if is_game and not self.hidden_by_fullscreen:
                    self.hidden_by_fullscreen = True
                    self.hide()
                elif not is_game and self.hidden_by_fullscreen:
                    self.hidden_by_fullscreen = False
                    self.show()
                    if self.placement_mode == "bottom":
                        if not self._is_embedded:
                            self.embed_in_taskbar()
                    else:
                        self.assert_topmost()
        except Exception:
            pass

    # --- Roam & Wander Zone Logic ---

    def ensure_roam_bounds(self):
        """Ensures valid roaming screen bounds are configured."""
        tray_r = self.get_tray_rect()
        if tray_r:
            tray_left = tray_r.left
            tray_w = tray_r.right - tray_r.left
        else:
            screen = self.get_current_screen()
            geom = screen.geometry()
            tray_left = geom.left()
            tray_w = geom.width()

        if self.roam_screen_min_x is None or self.roam_screen_max_x is None or self.roam_screen_max_x <= self.roam_screen_min_x:
            # Default zone: right-center portion of the taskbar
            self.roam_screen_min_x = int(tray_left + tray_w * 0.40)
            self.roam_screen_max_x = int(tray_left + tray_w * 0.85)

    def _schedule_next_roam(self, min_s=150, max_s=300):
        """Schedules the next slow, occasional wandering step in 2.5 to 5 minutes."""
        if not getattr(self, "roam_enabled", True):
            self.roam_timer.stop()
            return
        delay_ms = random.randint(min_s, max_s) * 1000
        self.roam_timer.stop()
        self.roam_timer.start(delay_ms)

    def _trigger_slow_roam(self):
        """Triggers a sequence of slow, gentle steps within the blue roam interval."""
        if not getattr(self, "roam_enabled", True) or self.is_dragging or getattr(self, "is_lifted", False):
            self._schedule_next_roam()
            return
        if self.is_claude_coding or self.is_sleeping_afk or self.hidden_by_fullscreen:
            self._schedule_next_roam()
            return
        if self.current_anim_name != "idle":
            self._schedule_next_roam(60, 120)
            return

        self.ensure_roam_bounds()

        tray_r = self.get_tray_rect()
        tray_left = tray_r.left if tray_r else 0
        tray_w = (tray_r.right - tray_r.left) if tray_r else 1920

        if self.placement_mode == "bottom" and self._is_embedded:
            curr_x = self.x()
            min_local_x = max(0, self.roam_screen_min_x - tray_left)
            max_local_x = min(tray_w - self.width(), self.roam_screen_max_x - tray_left - self.width())
        else:
            curr_x = self.x()
            min_local_x = self.roam_screen_min_x
            max_local_x = self.roam_screen_max_x - self.width()

        if max_local_x <= min_local_x:
            self._schedule_next_roam()
            return

        # Choose direction: bias away from the boundaries
        if curr_x <= min_local_x + 16:
            direction = 1
        elif curr_x >= max_local_x - 16:
            direction = -1
        else:
            direction = random.choice([-1, 1])

        # Step count: 3 to 6 steps
        self._roam_steps_remaining = random.randint(3, 6)
        self._roam_direction = direction
        self._roam_min_x = min_local_x
        self._roam_max_x = max_local_x
        self._roam_walk_frame = 0

        # Execute steps slowly every 240ms
        self._roam_step_timer.start(240)

    def _execute_roam_step(self):
        """Executes a single slow step (4px per step) with cute walking animation."""
        if self.is_dragging or getattr(self, "is_lifted", False) or self.is_claude_coding or self.is_sleeping_afk:
            self._roam_step_timer.stop()
            self.play_idle()
            self._schedule_next_roam()
            return

        if self._roam_steps_remaining <= 0:
            self._roam_step_timer.stop()
            self.play_idle()
            if random.random() < 0.6:
                self.play_animation("look_around", loop=False, speed_ms=130, on_finished=self.play_idle)
            self.save_config()
            self._schedule_next_roam()
            return

        self._roam_steps_remaining -= 1

        curr_x = self.x()
        step_dx = self._roam_direction * 4
        new_x = max(self._roam_min_x, min(self._roam_max_x, curr_x + step_dx))

        if self.placement_mode == "bottom" and self._is_embedded and user32:
            tray_r = self.get_tray_rect()
            tray_h = (tray_r.bottom - tray_r.top) if tray_r else 48
            floor_y = tray_h - (12 * self.scale_factor)
            hwnd = int(self.winId())
            user32.SetWindowPos(hwnd, 0, new_x, floor_y, self.width(), self.height(), 0x0040)
            user32.BringWindowToTop(hwnd)
        else:
            self.move(new_x, self.y())
            self.assert_topmost()

        # Alternate walking frames
        self._roam_walk_frame = (self._roam_walk_frame + 1) % 4
        self.play_animation("walk", loop=False)
        self.current_frame_idx = self._roam_walk_frame
        self._update_current_pixmap()

    def toggle_roam_enabled(self):
        self.roam_enabled = not self.roam_enabled
        if self.roam_enabled:
            self._schedule_next_roam(60, 180)
        else:
            self.roam_timer.stop()
            self._roam_step_timer.stop()
        self.save_config()
        self.rebuild_tray_menu()

    def toggle_roam_overlay(self):
        if not self.roam_overlay:
            self.roam_overlay = RoamZoneOverlayWidget(self)

        if self.roam_overlay.isVisible():
            self.roam_overlay.hide()
        else:
            self.roam_overlay.sync_geometry()
            self.roam_overlay.show()
            self.roam_overlay.raise_()

    def reset_roam_bounds(self):
        self.roam_screen_min_x = None
        self.roam_screen_max_x = None
        self.ensure_roam_bounds()
        if self.roam_overlay and self.roam_overlay.isVisible():
            self.roam_overlay.sync_geometry()
            self.roam_overlay.update()
        self.save_config()

    def toggle_autostart(self):
        new_state = not is_autostart_configured()
        set_autostart_configured(new_state)
        self.rebuild_tray_menu()

    # --- System Tray & Context Menu ---

    def get_active_language(self) -> str:
        if getattr(self, "language", "system") == "system":
            return get_system_language()
        return self.language if self.language in TRANSLATIONS else "ru"

    def t(self, key: str) -> str:
        lang = self.get_active_language()
        return TRANSLATIONS.get(lang, TRANSLATIONS["ru"]).get(key, key)

    def set_language(self, lang: str):
        if getattr(self, "language", "system") == lang:
            return
        self.language = lang
        self.save_config()
        self.rebuild_tray_menu()
        if hasattr(self, "tray_icon") and self.tray_icon:
            self.tray_icon.setToolTip(self.t("tooltip_default"))
        if not self.is_claude_coding:
            self.setToolTip(self.t("tooltip_default"))

    def setup_tray_icon(self):
        """Initializes the System Tray Icon with base.png and context menu."""
        self.tray_icon = QSystemTrayIcon(self)

        # Crop excessive empty padding (mascot is 12x8 in 16x16) and scale up by another 1.4x
        # so that Clawd is prominent and clearly visible in the Windows tray slot
        base_img = QImage(BASE_IMAGE_PATH)
        mascot_crop = base_img.copy(2, 4, 12, 8)

        # 48 * 1.4 = 67.2 -> 68x68 canvas
        tray_pix = QPixmap(68, 68)
        tray_pix.fill(Qt.GlobalColor.transparent)
        painter = QPainter(tray_pix)
        # 44 * 1.4 = 61.6 -> 62x41
        mascot_scaled = mascot_crop.scaled(
            62, 41,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation
        )
        ox = (68 - mascot_scaled.width()) // 2
        oy = (68 - mascot_scaled.height()) // 2
        painter.drawImage(ox, oy, mascot_scaled)
        painter.end()

        self.tray_icon.setIcon(QIcon(tray_pix))
        self.tray_icon.setToolTip(self.t("tooltip_default"))
        self.rebuild_tray_menu()
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()

    def rebuild_tray_menu(self):
        """Constructs a clean, modern dark menu without clutter."""
        self.tray_menu = QMenu(self)
        menu_style = """
            QMenu {
                background-color: #1e1e1e;
                color: #f0f0f0;
                border: 1px solid #383838;
                border-radius: 8px;
                padding: 6px 8px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
            }
            QMenu::item {
                padding: 6px 24px 6px 8px;
                border-radius: 4px;
                margin: 2px 4px;
            }
            QMenu::item:selected {
                background-color: #DA7758;
                color: #ffffff;
            }
            QMenu::separator {
                height: 1px;
                background-color: #333333;
                margin: 4px 8px;
            }
            QMenu::icon {
                margin-left: 10px;
            }
        """
        self.tray_menu.setStyleSheet(menu_style)

        # 1. Roam Zone Controls (with Material Symbols)
        roam_menu = self.tray_menu.addMenu(self.t("roam_zone"))
        roam_menu.setStyleSheet(menu_style)
        roam_menu.setIcon(get_material_icon("zone"))

        roam_act = roam_menu.addAction(get_material_icon("check" if self.roam_enabled else "blank"), self.t("roam_allow_slow"))
        roam_act.triggered.connect(self.toggle_roam_enabled)

        show_zone_act = roam_menu.addAction(get_material_icon("tune"), self.t("roam_tune"))
        show_zone_act.triggered.connect(self.toggle_roam_overlay)

        reset_zone_act = roam_menu.addAction(get_material_icon("refresh"), self.t("roam_reset"))
        reset_zone_act.triggered.connect(self.reset_roam_bounds)

        self.tray_menu.addSeparator()

        # 2. Windows Autostart on boot
        autostart_on = is_autostart_configured()
        auto_act = self.tray_menu.addAction(get_material_icon("check" if autostart_on else "blank"), self.t("autostart"))
        auto_act.triggered.connect(self.toggle_autostart)

        self.tray_menu.addSeparator()

        # 3. Language Submenu (Google Material 'language' icon + flag emojis)
        lang_menu = self.tray_menu.addMenu(self.t("language"))
        lang_menu.setStyleSheet(menu_style)
        lang_menu.setIcon(get_material_icon("language"))

        sys_act = lang_menu.addAction(get_material_icon("check" if self.language == "system" else "blank"), self.t("lang_system"))
        sys_act.triggered.connect(lambda: self.set_language("system"))

        en_act = lang_menu.addAction(get_material_icon("check" if self.language == "en" else "blank"), self.t("lang_en"))
        en_act.triggered.connect(lambda: self.set_language("en"))

        ru_act = lang_menu.addAction(get_material_icon("check" if self.language == "ru" else "blank"), self.t("lang_ru"))
        ru_act.triggered.connect(lambda: self.set_language("ru"))

        uk_act = lang_menu.addAction(get_material_icon("check" if self.language == "uk" else "blank"), self.t("lang_uk"))
        uk_act.triggered.connect(lambda: self.set_language("uk"))

        # 5. Snapping and Reset
        snap_act = self.tray_menu.addAction(get_material_icon("check" if self.snap_to_taskbar else "blank"), self.t("snap_taskbar"))
        snap_act.triggered.connect(self.toggle_snap_taskbar)

        reset_pos_act = self.tray_menu.addAction(get_material_icon("refresh"), self.t("reset_pos"))
        reset_pos_act.triggered.connect(self.reset_to_default_pos)

        self.tray_menu.addSeparator()

        # 6. Exit
        quit_act = self.tray_menu.addAction(get_material_icon("close"), self.t("quit"))
        quit_act.triggered.connect(QApplication.instance().quit)

        if hasattr(self, "tray_icon") and self.tray_icon:
            self.tray_icon.setContextMenu(self.tray_menu)

    def contextMenuEvent(self, event):
        """Right-clicking Clawd directly on the taskbar also pops up the tray menu."""
        if hasattr(self, "tray_menu"):
            self.tray_menu.exec(event.globalPos())

    def set_placement_mode(self, mode):
        if self.placement_mode == mode:
            return
        self.placement_mode = mode
        self.is_peeked_up = False

        if mode == "bottom":
            self.embed_in_taskbar()
        else:
            self.unembed_from_taskbar()

        self.save_config()
        self.rebuild_tray_menu()

    def toggle_snap_taskbar(self):
        self.snap_to_taskbar = not self.snap_to_taskbar
        if self.snap_to_taskbar:
            self.move(self.clamp_position(self.pos()))
        self.save_config()
        self.rebuild_tray_menu()

    def reset_to_default_pos(self):
        if self.placement_mode == "bottom" and self._is_embedded:
            tray_r = self.get_tray_rect()
            tray_w = (tray_r.right - tray_r.left) if tray_r else 1920
            tray_h = (tray_r.bottom - tray_r.top) if tray_r else 48
            local_x = int(tray_w * 0.8) - (self.width() // 2)
            local_y = tray_h - (12 * self.scale_factor)
            self.move(local_x, local_y)
            hwnd = int(self.winId())
            if user32 and hwnd:
                user32.SetWindowPos(hwnd, 0, local_x, local_y, self.width(), self.height(), 0x0040)
        else:
            self.move(self.clamp_position(self.get_default_position()))
            self.assert_topmost()
        self.save_config()
        if "peek_entrance" in self.scaled_animations:
            self.play_animation("peek_entrance", loop=False, speed_ms=125, on_finished=self.play_idle)
        else:
            self.play_idle()


def main():
    if user32:
        try:
            hdesk = user32.OpenDesktopW("Default", 0, False, 0x01FF)
            if hdesk:
                user32.SetThreadDesktop(hdesk)
        except Exception:
            pass

        # Make sure Shell_TrayWnd has no leftover region hole from older versions
        try:
            tray = user32.FindWindowW("Shell_TrayWnd", None)
            if tray:
                user32.SetWindowRgn(tray, None, True)
        except Exception:
            pass

    app = QApplication(sys.argv)
    app.setApplicationName("ClawdTaskbar")
    widget = ClawdTaskbarWidget()
    app.aboutToQuit.connect(widget.restore_taskbar_hole)
    widget.show()
    sys.exit(app.exec())


# Backwards compatibility alias
ClaudeTaskbarWidget = ClawdTaskbarWidget


if __name__ == "__main__":
    main()
