import sys
import os
import glob
import json
import random
import ctypes
from ctypes import wintypes
from PyQt6.QtWidgets import QApplication, QWidget, QMenu
from PyQt6.QtGui import QImage, QPixmap, QPainter, QCursor
from PyQt6.QtCore import Qt, QTimer, QPoint

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
ANIM_DIR = os.path.join(BASE_DIR, "animations")
BASE_IMAGE_PATH = os.path.join(BASE_DIR, "base.png")
ARM_IMAGE_PATH = os.path.join(BASE_DIR, "right-arm-up.png")

# Win32 API Definitions
try:
    user32 = ctypes.windll.user32
    user32.SetWindowPos.argtypes = [
        wintypes.HWND, wintypes.HWND,
        ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
        ctypes.c_uint
    ]
    user32.SetWindowPos.restype = wintypes.BOOL

    SetWindowLongPtrW = getattr(user32, "SetWindowLongPtrW", user32.SetWindowLongW)
    SetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_void_p]
    SetWindowLongPtrW.restype = ctypes.c_void_p

    HWND_TOPMOST = -1
    SWP_NOMOVE = 0x0002
    SWP_NOSIZE = 0x0001
    SWP_NOACTIVATE = 0x0010
    SWP_NOOWNERZORDER = 0x0200
    GWLP_HWNDPARENT = -8
    GWL_EXSTYLE = -20
    WS_EX_TOOLWINDOW = 0x00000080
except Exception:
    user32 = None


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long)
    ]


class ClaudeTaskbarWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Use FramelessWindowHint and WindowStaysOnTopHint.
        # DO NOT use Qt.WindowType.Tool, as Qt adds CS_SAVEBITS which causes
        # Windows to restore desktop bits and make Claude blink or vanish when opening windows/Start Menu!
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Settings
        self.scale_factor = 3  # 3x scale: Claude body is 24px tall (50% of 48px taskbar)
        self.snap_to_bottom = True
        self.idle_animations_enabled = True

        # State
        self.current_anim_name = "idle"
        self.current_frame_idx = 0
        self.is_looping = False
        self.current_pixmap = None
        self.drag_start_pos = None
        self.window_start_pos = None
        self.is_dragging = False
        self.hidden_by_fullscreen = False

        # Load all sprites and animations
        self.load_all_sprites()

        # Load saved settings if any
        self.load_config()

        # Re-scale pixmaps to current scale_factor
        self.update_scaled_pixmaps()

        # Place at initial position with boundary clamping
        self.ensure_valid_position()

        # Animation playback timer
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._advance_anim_frame)

        # Idle behaviors timer (blinking, stretching, coffee, etc.)
        self.idle_timer = QTimer(self)
        self.idle_timer.timeout.connect(self._trigger_random_idle_action)
        self._schedule_next_idle(10000, 20000)

        # Fullscreen detection and topmost management timer (runs smoothly every 200ms)
        self.monitor_timer = QTimer(self)
        self.monitor_timer.timeout.connect(self._monitor_fullscreen_and_state)
        self.monitor_timer.start(200)

        # Initial frame
        self.play_idle()

    def showEvent(self, event):
        super().showEvent(event)
        self.apply_native_window_styles()

    def apply_native_window_styles(self):
        """Configures native Windows styles: hides from taskbar/Alt-Tab without CS_SAVEBITS, and attaches to taskbar."""
        if not user32:
            return
        try:
            hwnd = int(self.winId())
            # 1. Add WS_EX_TOOLWINDOW so Claude is not visible in Taskbar / Alt-Tab
            ex = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex | WS_EX_TOOLWINDOW)

            # 2. Set owner to Shell_TrayWnd so Claude stays above the Taskbar even when Start menu is open
            hwnd_tray = user32.FindWindowW("Shell_TrayWnd", None)
            if hwnd_tray:
                SetWindowLongPtrW(hwnd, GWLP_HWNDPARENT, hwnd_tray)

            # 3. Ensure topmost cleanly without SWP_SHOWWINDOW (no blinking/flicker)
            user32.SetWindowPos(
                hwnd,
                HWND_TOPMOST,
                0, 0, 0, 0,
                SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_NOOWNERZORDER
            )
        except Exception:
            pass

    def is_foreground_fullscreen(self, mon_rect):
        """Checks if the active foreground window is in fullscreen covering the monitor."""
        if not user32:
            return False
        try:
            fg = user32.GetForegroundWindow()
            if not fg:
                return False

            # If foreground window is Claude itself, not fullscreen
            if fg == int(self.winId()):
                return False

            # If window is minimized, not fullscreen
            if user32.IsIconic(fg):
                return False

            cls_buf = ctypes.create_unicode_buffer(256)
            user32.GetClassNameW(fg, cls_buf, 256)
            cls_name = cls_buf.value

            # Ignore desktop and shell elements
            ignore_classes = {
                "Progman", "WorkerW",
                "Shell_TrayWnd", "Shell_SecondaryTrayWnd",
                "Windows.UI.Core.CoreWindow", "StartMenuExperienceHost",
                "SearchHost", "Shell_InputSwitchTopLevelWindow"
            }
            if cls_name in ignore_classes:
                return False

            rect = RECT()
            user32.GetWindowRect(fg, ctypes.byref(rect))

            mon_l, mon_t, mon_r, mon_b = mon_rect
            # Fullscreen covers the whole monitor including taskbar
            covers = (
                rect.left <= mon_l and
                rect.top <= mon_t and
                rect.right >= mon_r and
                rect.bottom >= mon_b
            )
            return covers
        except Exception:
            return False

    def _monitor_fullscreen_and_state(self):
        """Handles auto-hiding during fullscreen apps, and maintains clean Z-order."""
        screen = self.get_current_screen()
        geom = screen.geometry()
        mon_rect = (
            geom.left(),
            geom.top(),
            geom.left() + geom.width(),
            geom.top() + geom.height()
        )

        fullscreen_active = self.is_foreground_fullscreen(mon_rect)

        if fullscreen_active:
            if not self.hidden_by_fullscreen:
                self.hidden_by_fullscreen = True
                self.hide()
        else:
            if self.hidden_by_fullscreen:
                self.hidden_by_fullscreen = False
                self.show()
                self.apply_native_window_styles()
            else:
                # Maintain gentle topmost without SWP_SHOWWINDOW (no blinking)
                if user32 and self.isVisible():
                    try:
                        hwnd = int(self.winId())
                        user32.SetWindowPos(
                            hwnd,
                            HWND_TOPMOST,
                            0, 0, 0, 0,
                            SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_NOOWNERZORDER
                        )
                    except Exception:
                        pass

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
                    anim_name, idx_str = basename.rsplit("_", 1)
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

        old_ground_y = self.y() + (12 * self.scale_factor)
        self.setFixedSize(w, h)

        if self.isVisible():
            # Keep feet pinned to ground level and clamp strictly inside screen
            new_y = old_ground_y - (12 * self.scale_factor)
            clamped = self.clamp_position(QPoint(self.x(), new_y))
            self.move(clamped)

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
        if not self.idle_animations_enabled or self.is_dragging or self.hidden_by_fullscreen:
            return
        if self.current_anim_name != "idle":
            self._schedule_next_idle(8000, 15000)
            return

        choices = [
            ("blink", 45),
            ("look_around", 20),
            ("coffee", 10),
            ("idea", 8),
            ("yawn", 8),
            ("typing", 5),
            ("peek", 4),
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

        self.play_animation(selected, loop=False, speed_ms=speed)

    def trigger_click_reaction(self):
        """Random playful reaction when user clicks on Claude."""
        reactions = [
            ("wave", 110),
            ("cheer", 120),
            ("jump", 100),
            ("heart", 130),
            ("dance", 120),
            ("cool", 130),
            ("idea", 120),
            ("spin", 90),
        ]
        name, speed = random.choice(reactions)
        self.play_animation(name, loop=False, speed_ms=speed)

    # --- Screen Boundary Clamping ---

    def get_current_screen(self, pos=None):
        target = pos if pos is not None else self.pos()
        screen = QApplication.screenAt(target)
        if not screen:
            screen = QApplication.screenAt(QCursor.pos())
        if not screen:
            screen = QApplication.primaryScreen()
        return screen

    def clamp_position(self, pos, screen=None):
        """Strictly restricts window coordinates inside screen boundaries."""
        if screen is None:
            screen = self.get_current_screen(pos)
        geom = screen.geometry()

        # Horizontal bounds: prevent going off-screen to the left or right
        min_x = geom.left()
        max_x = geom.left() + geom.width() - self.width()
        clamped_x = max(min_x, min(max_x, pos.x()))

        # Ground level is row 11 (the bottom of Claude's feet), so 12 units from top
        ground_offset = 12 * self.scale_factor
        ground_bottom_y = geom.top() + geom.height() - ground_offset

        if self.snap_to_bottom:
            clamped_y = ground_bottom_y
        else:
            min_y = geom.top()
            max_y = ground_bottom_y
            clamped_y = max(min_y, min(max_y, pos.y()))

        return QPoint(clamped_x, clamped_y)

    def load_config(self):
        self.saved_pos = None
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.scale_factor = data.get("scale_factor", 3)
                    self.snap_to_bottom = data.get("snap_to_bottom", True)
                    self.idle_animations_enabled = data.get("idle_animations_enabled", True)
                    if "x" in data and "y" in data:
                        self.saved_pos = QPoint(data["x"], data["y"])
            except Exception as e:
                print("Failed to load config:", e)

    def save_config(self):
        try:
            data = {
                "x": self.x(),
                "y": self.y(),
                "scale_factor": self.scale_factor,
                "snap_to_bottom": self.snap_to_bottom,
                "idle_animations_enabled": self.idle_animations_enabled
            }
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print("Failed to save config:", e)

    def get_default_position(self):
        screen = QApplication.primaryScreen().geometry()
        default_x = int(screen.width() * (1520 / 1920)) - (self.width() // 2)
        default_y = screen.height() - (12 * self.scale_factor)
        return QPoint(default_x, default_y)

    def ensure_valid_position(self):
        if self.saved_pos:
            self.move(self.clamp_position(self.saved_pos))
        else:
            self.move(self.clamp_position(self.get_default_position()))

    def paintEvent(self, event):
        if self.current_pixmap:
            painter = QPainter(self)
            painter.drawPixmap(0, 0, self.current_pixmap)

    def set_scale(self, factor):
        self.scale_factor = max(1, min(10, factor))
        self.update_scaled_pixmaps()
        self.move(self.clamp_position(self.pos()))
        self.save_config()

    # --- Mouse Events ---

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_pos = event.globalPosition().toPoint()
            self.window_start_pos = self.pos()
            self.is_dragging = False

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and self.drag_start_pos:
            delta = event.globalPosition().toPoint() - self.drag_start_pos
            if delta.manhattanLength() > 3:
                self.is_dragging = True
                target_pos = self.window_start_pos + delta

                screen = self.get_current_screen(target_pos)
                geom = screen.geometry()
                ground_y = geom.top() + geom.height() - (12 * self.scale_factor)

                if not self.snap_to_bottom and abs(target_pos.y() - ground_y) < 20:
                    target_pos.setY(ground_y)

                clamped_pos = self.clamp_position(target_pos, screen)
                self.move(clamped_pos)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.is_dragging:
                self.move(self.clamp_position(self.pos()))
                self.save_config()
                self.play_idle()
            else:
                self.trigger_click_reaction()
            self.drag_start_pos = None

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

        # Animations submenu
        anim_menu = menu.addMenu("🎭 Анимации")
        anim_list = [
            ("👋 Помахать рукой (Wave)", "wave", 110, False),
            ("🎉 Радость (Обе руки вверх)", "cheer", 120, False),
            ("🦘 Прыжок (Jump)", "jump", 100, False),
            ("💃 Весёлый танец (Dance)", "dance", 120, True),
            ("💖 Любовь и сердечко", "heart", 130, False),
            ("☕ Выпить чашку кофе", "coffee", 140, False),
            ("💡 Осенила идея (Лампочка)", "idea", 120, False),
            ("💻 Кодить за ноутбуком", "typing", 110, True),
            ("🕶️ Крутой в очках", "cool", 130, False),
            ("🔄 Покрутиться 360°", "spin", 90, False),
            ("🙈 Спрятаться за панель", "peek", 120, False),
            ("🥱 Зевнуть и потянуться", "yawn", 140, False),
            ("❓ Недоумение (Вопрос)", "question", 130, False),
            ("👀 Оглядеться по сторонам", "look_around", 130, False),
            ("😉 Моргнуть", "blink", 90, False),
            ("💤 Заснуть (Sleep)", "sleep", 200, True),
            ("🛑 Обычный вид (Idle)", "idle", 100, False),
        ]
        for title, anim_name, speed, loop in anim_list:
            act = anim_menu.addAction(title)
            act.triggered.connect(lambda checked=False, a=anim_name, s=speed, l=loop: self.play_animation(a, loop=l, speed_ms=s))

        menu.addSeparator()

        # Idle mode toggle
        idle_act = menu.addAction(f"{'✓ ' if self.idle_animations_enabled else '   '}Живой режим (авто-анимации)")
        idle_act.triggered.connect(self.toggle_idle_mode)

        # Scale submenu
        scale_menu = menu.addMenu("📐 Размер")
        scale_options = [
            ("Половина высоты панели (24px, 3x)", 3),
            ("Средний (32px, 4x)", 4),
            ("Большой (40px, 5x)", 5),
            ("Вся высота панели (48px, 6x)", 6),
            ("Крупный (64px, 8x)", 8),
            ("Мини (16px, 2x)", 2),
        ]
        for title, factor in scale_options:
            act = scale_menu.addAction(f"{'✓ ' if self.scale_factor == factor else '   '}{title}")
            act.triggered.connect(lambda checked=False, f=factor: self.set_scale(f))

        menu.addSeparator()

        reset_pos_act = menu.addAction("📍 Сбросить на позицию по умолчанию")
        reset_pos_act.triggered.connect(self.reset_to_default_pos)

        snap_act = menu.addAction(f"{'✓ ' if self.snap_to_bottom else '   '}Привязать к низу экрана")
        snap_act.triggered.connect(self.toggle_snap_bottom)

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

    def reset_to_default_pos(self):
        self.move(self.clamp_position(self.get_default_position()))
        self.save_config()

    def toggle_snap_bottom(self):
        self.snap_to_bottom = not self.snap_to_bottom
        self.move(self.clamp_position(self.pos()))
        self.save_config()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("ClaudeTaskbar")
    widget = ClaudeTaskbarWidget()
    widget.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
