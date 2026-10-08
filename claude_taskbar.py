import sys
import os
import glob
import json
import time
import random
import ctypes
from ctypes import wintypes
from PyQt6.QtWidgets import QApplication, QWidget, QMenu
from PyQt6.QtGui import QImage, QPixmap, QPainter, QCursor, QColor
from PyQt6.QtCore import Qt, QTimer, QPoint

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


class ClaudeTaskbarWidget(QWidget):
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

        # Settings
        self.scale_factor = 3
        self.placement_mode = "bottom"  # "bottom" (inside taskbar) or "top" (on top of taskbar ledge)
        self.auto_peek_on_shell = False  # Not needed: tray ownership keeps Claude 100% visible inside taskbar
        self.is_peeked_up = False
        self.snap_to_taskbar = True  # Magnetic snapping to taskbar
        self.idle_animations_enabled = True
        self.auto_hide_fullscreen = False

        # State
        self.current_anim_name = "idle"
        self.current_frame_idx = 0
        self.is_looping = False
        self.current_pixmap = None
        self.drag_start_pos = None
        self.window_start_pos = None
        self.window_start_screen_pos = None
        self.is_dragging = False
        self.is_lifted = False
        self.was_embedded_before_lift = False
        self.on_anim_finished = None

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

        # Initial frame
        self.play_idle()

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
        Embeds Claude's window as a genuine WS_CHILD of Shell_TrayWnd.
        This seamlessly places Claude inside the taskbar:
        - Claude is rendered as part of the taskbar's visual hierarchy by DWM.
        - Claude NEVER disappears when Start Menu, Action Center, or Windows panels open.
        - NO hole is carved in the taskbar, so the taskbar's native acrylic background
          is preserved behind Claude with zero black boxes or black borders.
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
        except Exception as e:
            print("embed_in_taskbar error:", e)

    def unembed_from_taskbar(self, pos=None):
        """
        Restores Claude as a top-level topmost window when in 'top' placement mode
        or when lifted off the taskbar during drag.
        """
        if not user32 or not self._is_embedded:
            return
        try:
            hwnd = int(self.winId())
            if not hwnd:
                return

            if pos is not None:
                screen_x, screen_y = pos.x(), pos.y()
            else:
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
        Sets the Windows taskbar (Shell_TrayWnd) as the owner of Claude's window
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
        Checks if Claude's visible pixels are physically occluded in the Z-order
        by any overlapping external application window (only relevant in top mode).
        """
        if not user32 or not self.isVisible() or self.hidden_by_fullscreen or self._is_embedded:
            return False
        try:
            hwnd = int(self.winId())
            claude_vis_rect = (
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
                    if not (r.right <= claude_vis_rect[0] or r.left >= claude_vis_rect[2] or
                            r.bottom <= claude_vis_rect[1] or r.top >= claude_vis_rect[3]):
                        return True

            return False
        except Exception:
            return False

    def _check_zorder_safety(self):
        """
        Runs smoothly every 60ms with zero CPU overhead:
        1. When embedded in taskbar ('bottom' mode): maintains WS_CHILD hierarchy inside Shell_TrayWnd
           so Claude is rendered by DWM directly as part of the taskbar and never occluded by Windows panels.
        2. When top-level ('top' mode): maintains Shell_TrayWnd ownership and asserts topmost Z-order.
        """
        if not user32 or not self.isVisible() or self.hidden_by_fullscreen or getattr(self, "is_lifted", False):
            return

        if self.placement_mode == "bottom" and self._is_embedded:
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
        """Hovering over Claude ensures he is always at the top of the stack for clicks/drag."""
        super().enterEvent(event)
        if self.placement_mode == "bottom" and self._is_embedded:
            hwnd = int(self.winId())
            if user32 and hwnd:
                user32.BringWindowToTop(hwnd)
        else:
            self.assert_topmost()

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
                    self.play_idle()
                    self._schedule_next_idle(10000, 25000)

    def _schedule_next_idle(self, min_ms=10000, max_ms=25000):
        if self.idle_animations_enabled:
            interval = random.randint(min_ms, max_ms)
            self.idle_timer.stop()
            self.idle_timer.start(interval)

    def _trigger_random_idle_action(self):
        if not self.idle_animations_enabled or self.is_dragging or getattr(self, "is_lifted", False) or self.hidden_by_fullscreen:
            return
        if self.current_anim_name != "idle":
            self._schedule_next_idle(8000, 15000)
            return

        choices = [
            ("blink", 30),
            ("look_around", 15),
            ("coffee", 8),
            ("spark", 8),
            ("chat", 7),
            ("idea", 6),
            ("typing", 6),
            ("pizza", 4),
            ("peek", 4),
            ("matrix", 4),
            ("shield", 3),
        ]
        total = sum(w for _, w in choices)
        r = random.randint(1, total)
        accum = 0
        selected = "blink"
        for name, weight in choices:
            accum += weight
            if r <= accum:
                selected = name
                break

        speed = 130
        if selected == "blink":
            speed = 90
        elif selected == "typing":
            speed = 110
        elif selected == "matrix":
            speed = 120

        self.play_animation(selected, loop=False, speed_ms=speed)

    def trigger_click_reaction(self):
        """Random playful reaction when user clicks on Claude."""
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
            ("pizza", 120),
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
        Calculates Y coordinate so Claude's feet rest perfectly on top of the taskbar ledge.
        Claude is completely outside the taskbar rect and NEVER gets occluded by Start menu/taskbar.
        """
        surface_y = self.get_taskbar_surface_y(screen)
        feet_offset = 12 * self.scale_factor
        return surface_y - feet_offset

    def get_taskbar_bottom_y(self, screen=None):
        """Calculates Y coordinate so Claude's feet rest at the bottom of the screen (inside taskbar)."""
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
        Keeps Claude on screen or within taskbar. If snap_to_taskbar is enabled,
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
                    self.scale_factor = data.get("scale_factor", 3)
                    self.placement_mode = data.get("placement_mode", "bottom")
                    self.auto_peek_on_shell = data.get("auto_peek_on_shell", False)
                    self.snap_to_taskbar = data.get("snap_to_taskbar", True)
                    self.idle_animations_enabled = data.get("idle_animations_enabled", True)
                    self.auto_hide_fullscreen = data.get("auto_hide_fullscreen", False)
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
                "auto_hide_fullscreen": self.auto_hide_fullscreen
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

    # --- Mouse Events: Free Dragging & Reactions ---

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_pos = event.globalPosition().toPoint()
            self.is_dragging = False
            self.is_lifted = False
            self.was_embedded_before_lift = bool(self.placement_mode == "bottom" and self._is_embedded)

            if user32:
                hwnd = int(self.winId())
                wr = wintypes.RECT()
                user32.GetWindowRect(hwnd, ctypes.byref(wr))
                self.window_start_screen_pos = QPoint(wr.left, wr.top)
            else:
                self.window_start_screen_pos = self.pos()

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.MouseButton.LeftButton) and self.drag_start_pos and self.window_start_screen_pos:
            delta = event.globalPosition().toPoint() - self.drag_start_pos

            # Rule: Cannot drag horizontally directly on the taskbar.
            # Must first pull UPWARDS by at least 12px (negative Y) to lift Claude off the floor!
            LIFT_THRESHOLD = 12

            if not self.is_lifted:
                if delta.y() <= -LIFT_THRESHOLD:
                    self.is_lifted = True
                    self.is_dragging = True

                    target_pos = self.window_start_screen_pos + delta
                    if self._is_embedded:
                        self.unembed_from_taskbar(target_pos)
                    else:
                        self.move(target_pos)

                    # Play looping drag animation: flailing little paws and bicycling feet!
                    self.play_animation("drag", loop=True, speed_ms=85)
                    self.assert_topmost()
                else:
                    # User only moved horizontally or downwards:
                    # Claude resists and stays planted on the floor!
                    return

            if self.is_lifted:
                target_pos = self.window_start_screen_pos + delta
                self.move(target_pos)
                self.assert_topmost()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.is_lifted:
                # Claude lands back down on the taskbar floor at his new horizontal position!
                drop_screen_x = self.x()
                screen = self.get_current_screen()

                if self.placement_mode == "bottom" and self.was_embedded_before_lift:
                    self.embed_in_taskbar(target_screen_x=drop_screen_x)
                else:
                    target_y = self.get_taskbar_top_y(screen) if self.placement_mode == "top" else self.get_taskbar_bottom_y(screen)
                    self.move(self.clamp_position(QPoint(drop_screen_x, target_y)))
                    self.assert_topmost()

                self.save_config()

                # Squish landing upon touchdown, then transition smoothly to idle!
                self.play_animation("land", loop=False, speed_ms=100)
                QTimer.singleShot(220, self.play_idle)
            else:
                delta = event.globalPosition().toPoint() - self.drag_start_pos if self.drag_start_pos else QPoint(0, 0)
                if delta.manhattanLength() < 6:
                    self.trigger_click_reaction()
                else:
                    self.play_idle()

            self.drag_start_pos = None
            self.window_start_screen_pos = None
            self.is_dragging = False
            self.is_lifted = False

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            hype = random.choice(["jump", "cheer", "spin"])
            self.play_animation(hype, loop=False, speed_ms=100)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta > 0:
            self.set_scale(self.scale_factor + 1)
        elif delta < 0:
            self.set_scale(self.scale_factor - 1)

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

    # --- Context Menu ---

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #242424;
                color: #f0f0f0;
                border: 1px solid #444444;
                border-radius: 8px;
                padding: 6px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
            }
            QMenu::item {
                padding: 6px 24px 6px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #DA7758;
                color: #ffffff;
            }
            QMenu::separator {
                height: 1px;
                background-color: #3d3d3d;
                margin: 4px 8px;
            }
        """)

        # Animations submenu with 24 animations categorized
        anim_menu = menu.addMenu("🎭 Анимации (24)")

        categories = [
            ("✨ Фирменный Claude & AI", [
                ("✨ Искра Claude (Spark)", "spark", 110, False),
                ("💬 Ответ Claude (Chat ...)", "chat", 120, False),
                ("🛡️ Защитный купол (Shield)", "shield", 120, False),
                ("🟢 Матрица / Хакер (Matrix)", "matrix", 120, True),
            ]),
            ("💻 Работа и отдых", [
                ("💻 Кодить за ноутбуком (Typing)", "typing", 110, True),
                ("💡 Осенила идея (Idea)", "idea", 120, False),
                ("☕ Чашка кофе (Coffee)", "coffee", 140, False),
                ("🍕 Кушать пиццу (Pizza)", "pizza", 120, False),
            ]),
            ("😊 Эмоции и жесты", [
                ("👋 Помахать рукой (Wave)", "wave", 110, False),
                ("🎉 Радость (Cheer)", "cheer", 120, False),
                ("🦘 Прыжок (Jump)", "jump", 100, False),
                ("💃 Весёлый танец (Dance)", "dance", 120, True),
                ("💖 Любовь и сердечко (Heart)", "heart", 130, False),
                ("😭 Аниме-плач (Cry)", "cry", 110, False),
                ("❓ Недоумение (Question)", "question", 130, False),
                ("👀 Оглядеться по сторонам", "look_around", 130, False),
                ("😉 Моргнуть (Blink)", "blink", 90, False),
                ("🏃 Поднят в воздух (Drag)", "drag", 85, True),
                ("🛬 Приземление (Land)", "land", 100, False),
            ]),
            ("🧙 Экшен и магия", [
                ("🧙 Волшебник (Wizard)", "wizard", 120, False),
                ("🏋️ Качалка / Штанга (Workout)", "workout", 120, False),
                ("🔄 Крутиться 360° (Spin)", "spin", 90, False),
                ("🙈 Прятаться за панель (Peek)", "peek", 120, False),
            ]),
            ("💤 Режимы", [
                ("💤 Заснуть (Sleep)", "sleep", 200, True),
                ("🛑 Обычный вид (Idle)", "idle", 100, False),
            ])
        ]

        for cat_title, items in categories:
            sub = anim_menu.addMenu(cat_title)
            for title, anim_name, speed, loop in items:
                act = sub.addAction(title)
                act.triggered.connect(lambda checked=False, a=anim_name, s=speed, l=loop: self.play_animation(a, loop=l, speed_ms=s))

        menu.addSeparator()

        # Idle mode toggle
        idle_act = menu.addAction(f"{'✓ ' if self.idle_animations_enabled else '   '}Живой режим (авто-анимации)")
        idle_act.triggered.connect(self.toggle_idle_mode)

        # Fullscreen auto-hide toggle
        fs_act = menu.addAction(f"{'✓ ' if self.auto_hide_fullscreen else '   '}Скрывать в полноэкранных играх")
        fs_act.triggered.connect(self.toggle_fullscreen_mode)

        # Scale submenu
        scale_menu = menu.addMenu("📐 Размер")
        scale_options = [
            ("Мини (16px, 2x)", 2),
            ("Половина высоты панели (24px, 3x)", 3),
            ("Средний (32px, 4x)", 4),
            ("Большой (40px, 5x)", 5),
            ("Вся высота панели (48px, 6x)", 6),
            ("Гигантский (64px, 8x)", 8),
        ]
        for title, factor in scale_options:
            act = scale_menu.addAction(f"{'✓ ' if self.scale_factor == factor else '   '}{title}")
            act.triggered.connect(lambda checked=False, f=factor: self.set_scale(f))

        menu.addSeparator()

        place_menu = menu.addMenu("📍 Позиция на панели")
        bot_act = place_menu.addAction(f"{'✓ ' if self.placement_mode == 'bottom' else '   '}Внутри панели (снизу экрана)")
        bot_act.triggered.connect(lambda: self.set_placement_mode("bottom"))

        top_act = place_menu.addAction(f"{'✓ ' if self.placement_mode == 'top' else '   '}Сверху панели (на бордюре)")
        top_act.triggered.connect(lambda: self.set_placement_mode("top"))

        snap_act = menu.addAction(f"{'✓ ' if self.snap_to_taskbar else '   '}🧲 Магнититься к панели")
        snap_act.triggered.connect(self.toggle_snap_taskbar)

        reset_pos_act = menu.addAction("🔄 Сбросить позицию (по умолчанию)")
        reset_pos_act.triggered.connect(self.reset_to_default_pos)

        menu.addSeparator()

        quit_act = menu.addAction("❌ Закрыть")
        quit_act.triggered.connect(QApplication.instance().quit)

        menu.exec(event.globalPos())

    def toggle_idle_mode(self):
        self.idle_animations_enabled = not self.idle_animations_enabled
        if self.idle_animations_enabled:
            self._schedule_next_idle(5000, 15000)
        else:
            self.idle_timer.stop()
        self.save_config()

    def toggle_fullscreen_mode(self):
        self.auto_hide_fullscreen = not self.auto_hide_fullscreen
        if self.auto_hide_fullscreen:
            self.fullscreen_timer.start(800)
        else:
            self.fullscreen_timer.stop()
            if self.hidden_by_fullscreen:
                self.hidden_by_fullscreen = False
                self.show()
                if self.placement_mode == "bottom":
                    if not self._is_embedded:
                        self.embed_in_taskbar()
                else:
                    self.assert_topmost()
        self.save_config()

    def sit_on_taskbar_top(self):
        """Switches placement to sitting on top of the taskbar (recommended: never occluded)."""
        self.set_placement_mode("top")

    def sit_on_bottom_taskbar(self):
        """Switches placement to sitting inside the taskbar (at the bottom of the screen)."""
        self.set_placement_mode("bottom")

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

    def toggle_auto_peek(self):
        self.auto_peek_on_shell = not self.auto_peek_on_shell
        self.save_config()

    def toggle_snap_taskbar(self):
        self.snap_to_taskbar = not self.snap_to_taskbar
        if self.snap_to_taskbar:
            self.move(self.clamp_position(self.pos()))
        self.save_config()

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
    app.setApplicationName("ClaudeTaskbar")
    widget = ClaudeTaskbarWidget()
    app.aboutToQuit.connect(widget.restore_taskbar_hole)
    widget.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
