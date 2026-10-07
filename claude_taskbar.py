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

# Win32 Shell API for non-intrusive fullscreen game detection (SHQueryUserNotificationState)
try:
    shell32 = ctypes.windll.shell32
    shell32.SHQueryUserNotificationState.argtypes = [ctypes.POINTER(wintypes.DWORD)]
    shell32.SHQueryUserNotificationState.restype = ctypes.c_long
except Exception:
    shell32 = None


class ClaudeTaskbarWidget(QWidget):
    def __init__(self):
        super().__init__()

        # --- Mascot Window Configuration ---
        # FramelessWindowHint: borderless transparent window
        # WindowStaysOnTopHint: OS-level persistent topmost without Z-order fighting
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
        self.snap_to_taskbar = True  # Magnetic snapping to bottom of taskbar
        self.idle_animations_enabled = True
        self.auto_hide_fullscreen = False

        # State
        self.current_anim_name = "idle"
        self.current_frame_idx = 0
        self.is_looping = False
        self.current_pixmap = None
        self.drag_start_pos = None
        self.window_start_pos = None
        self.is_dragging = False
        self.on_anim_finished = None

        # Fullscreen detection state
        self.hidden_by_fullscreen = False

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

        # Fullscreen detection timer: runs every 800ms only if enabled
        self.fullscreen_timer = QTimer(self)
        self.fullscreen_timer.timeout.connect(self._check_fullscreen)
        if self.auto_hide_fullscreen:
            self.fullscreen_timer.start(800)

        # Initial frame
        self.play_idle()

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

    # --- Screen Coordinates & Positioning ---

    def get_current_screen(self, pos=None):
        target = pos if pos is not None else self.pos()
        screen = QApplication.screenAt(target)
        if not screen:
            screen = QApplication.screenAt(QCursor.pos())
        if not screen:
            screen = QApplication.primaryScreen()
        return screen

    def get_taskbar_bottom_y(self, screen=None):
        """
        Calculates Y coordinate so Claude's feet rest at the very bottom edge of the taskbar/screen.
        In the 16x16 sprite, Claude's feet end at row 11 (12 pixels from top).
        Rows 12-15 are transparent padding.
        """
        if screen is None:
            screen = self.get_current_screen()
        geom = screen.geometry()
        feet_offset = 12 * self.scale_factor
        return geom.top() + geom.height() - feet_offset

    def get_default_position(self, screen=None):
        """Calculates default position: sitting at the bottom of the taskbar near the tray."""
        if screen is None:
            screen = self.get_current_screen()
        geom = screen.geometry()
        x = int(geom.left() + geom.width() * 0.8) - (self.width() // 2)
        y = self.get_taskbar_bottom_y(screen)
        return QPoint(x, y)

    def clamp_position(self, pos, screen=None):
        """
        Allows moving Claude to ANY location on the desktop while keeping him visible on screen.
        If snap_to_taskbar is enabled, magnetically snaps his feet to the bottom of the taskbar
        when within 35px of the bottom edge.
        """
        if screen is None:
            screen = self.get_current_screen(pos)
        geom = screen.geometry()

        # Clamping bounds to stay visible within screen
        min_x = geom.left()
        max_x = geom.left() + geom.width() - self.width()
        clamped_x = max(min_x, min(max_x, pos.x()))

        min_y = geom.top()
        bottom_y = self.get_taskbar_bottom_y(screen)
        max_y = bottom_y

        if self.snap_to_taskbar:
            # Magnetic snapping: if within 35px of the bottom of the taskbar, snap down!
            if abs(pos.y() - bottom_y) < 35 or pos.y() > bottom_y:
                clamped_y = bottom_y
            else:
                clamped_y = max(min_y, min(max_y, pos.y()))
        else:
            clamped_y = max(min_y, min(max_y, pos.y()))

        return QPoint(clamped_x, clamped_y)

    def load_config(self):
        self.saved_pos = None
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.scale_factor = data.get("scale_factor", 3)
                    self.snap_to_taskbar = data.get("snap_to_taskbar", True)
                    self.idle_animations_enabled = data.get("idle_animations_enabled", True)
                    self.auto_hide_fullscreen = data.get("auto_hide_fullscreen", False)
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
                "snap_to_taskbar": self.snap_to_taskbar,
                "idle_animations_enabled": self.idle_animations_enabled,
                "auto_hide_fullscreen": self.auto_hide_fullscreen
            }
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print("Failed to save config:", e)

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
        new_factor = max(2, min(8, factor))
        if new_factor == self.scale_factor:
            return

        screen = self.get_current_screen()
        geom = screen.geometry()
        old_bottom_y = geom.top() + geom.height() - (12 * self.scale_factor)
        was_at_bottom = abs(self.y() - old_bottom_y) < 6

        self.scale_factor = new_factor
        self.update_scaled_pixmaps()

        if was_at_bottom or self.snap_to_taskbar:
            new_y = self.get_taskbar_bottom_y(screen)
            self.move(self.clamp_position(QPoint(self.x(), new_y)))
        else:
            self.move(self.clamp_position(self.pos()))
        self.save_config()

    # --- Mouse Events: Free Dragging & Reactions ---

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
                self.move(self.clamp_position(target_pos))

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.is_dragging:
                self.move(self.clamp_position(self.pos()))
                self.save_config()
                self.play_idle()
            else:
                self.trigger_click_reaction()
            self.drag_start_pos = None
            self.is_dragging = False

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

        sit_act = menu.addAction("📍 Прижать к низу панели задач")
        sit_act.triggered.connect(self.sit_on_bottom_taskbar)

        snap_act = menu.addAction(f"{'✓ ' if self.snap_to_taskbar else '   '}🧲 Магнититься к низу панели")
        snap_act.triggered.connect(self.toggle_snap_taskbar)

        reset_pos_act = menu.addAction("📍 Сбросить позицию (по умолчанию)")
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
        self.save_config()

    def sit_on_bottom_taskbar(self):
        """Snaps Claude so his feet rest at the bottom of the taskbar."""
        bottom_y = self.get_taskbar_bottom_y()
        self.move(self.clamp_position(QPoint(self.x(), bottom_y)))
        self.save_config()

    def toggle_snap_taskbar(self):
        self.snap_to_taskbar = not self.snap_to_taskbar
        if self.snap_to_taskbar:
            self.move(self.clamp_position(self.pos()))
        self.save_config()

    def reset_to_default_pos(self):
        self.move(self.clamp_position(self.get_default_position()))
        self.save_config()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("ClaudeTaskbar")
    widget = ClaudeTaskbarWidget()
    widget.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
