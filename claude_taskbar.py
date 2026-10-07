import sys
import os
import json
import ctypes
from ctypes import wintypes
from PyQt6.QtWidgets import QApplication, QWidget, QMenu
from PyQt6.QtGui import QImage, QPixmap, QPainter, QCursor
from PyQt6.QtCore import Qt, QTimer, QPoint

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
BASE_IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "base.png")
ARM_IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "right-arm-up.png")

# Setup Windows API for keeping topmost above taskbar
try:
    user32 = ctypes.windll.user32
    user32.SetWindowPos.argtypes = [
        wintypes.HWND, wintypes.HWND,
        ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
        ctypes.c_uint
    ]
    user32.SetWindowPos.restype = wintypes.BOOL
    HWND_TOPMOST = -1
    SWP_NOMOVE = 0x0002
    SWP_NOSIZE = 0x0001
    SWP_NOACTIVATE = 0x0010
    SWP_SHOWWINDOW = 0x0040
except Exception:
    user32 = None


class ClaudeTaskbarWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Frameless, Always on Top, Tool window (no taskbar icon)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Load and crop source images
        self.load_sprites()

        # State
        self.current_frame = "base"
        self.scale_factor = 3  # 3x scale: Claude is 24px tall (50% of 48px taskbar)
        self.snap_to_bottom = True
        self.drag_start_pos = None
        self.window_start_pos = None
        self.is_dragging = False

        # Load saved settings if any
        self.load_config()

        # Update pixmaps according to scale
        self.update_scaled_pixmaps()

        # Initial positioning (guaranteed within screen boundaries)
        self.ensure_valid_position()

        # Arm timer for resetting animation
        self.arm_timer = QTimer(self)
        self.arm_timer.setSingleShot(True)
        self.arm_timer.timeout.connect(self.reset_to_base)

        # Periodic timer to enforce topmost over Windows Taskbar
        self.topmost_timer = QTimer(self)
        self.topmost_timer.timeout.connect(self.enforce_topmost)
        self.topmost_timer.start(500)

    def load_sprites(self):
        """Loads base and arm-up sprites and crops them to the exact sprite boundary."""
        raw_base = QImage(BASE_IMAGE_PATH)
        raw_arm = QImage(ARM_IMAGE_PATH)

        # Claude sprite bounds in 16x16:
        # Col 2 to 14 (width 12), Row 4 to 12 (height 8)
        # Feet are exactly on row 11 (the bottom of this 12x8 slice).
        self.crop_rect = (2, 4, 12, 8)
        self.img_base_cropped = raw_base.copy(*self.crop_rect)
        self.img_arm_cropped = raw_arm.copy(*self.crop_rect)

    def get_current_screen(self, pos=None):
        """Returns the QScreen corresponding to the given position or cursor."""
        target = pos if pos is not None else self.pos()
        screen = QApplication.screenAt(target)
        if not screen:
            screen = QApplication.screenAt(QCursor.pos())
        if not screen:
            screen = QApplication.primaryScreen()
        return screen

    def clamp_position(self, pos, screen=None):
        """Restricts window coordinates strictly inside screen boundaries (left, right, top, bottom)."""
        if screen is None:
            screen = self.get_current_screen(pos)
        geom = screen.geometry()

        # Horizontal bounds: prevent going off-screen to the left or right
        min_x = geom.left()
        max_x = geom.left() + geom.width() - self.width()
        clamped_x = max(min_x, min(max_x, pos.x()))

        # Vertical bounds
        min_y = geom.top()
        max_y = geom.top() + geom.height() - self.height()

        if self.snap_to_bottom:
            clamped_y = max_y
        else:
            clamped_y = max(min_y, min(max_y, pos.y()))

        return QPoint(clamped_x, clamped_y)

    def update_scaled_pixmaps(self):
        """Recreates pixmaps with crisp nearest-neighbor scaling."""
        w = self.crop_rect[2] * self.scale_factor
        h = self.crop_rect[3] * self.scale_factor

        self.pm_base = QPixmap.fromImage(self.img_base_cropped).scaled(
            w, h, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.FastTransformation
        )
        self.pm_arm = QPixmap.fromImage(self.img_arm_cropped).scaled(
            w, h, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.FastTransformation
        )

        old_bottom = self.y() + self.height()
        self.setFixedSize(w, h)

        if self.isVisible():
            # Keep feet pinned to previous bottom and clamp inside screen
            new_y = old_bottom - h
            clamped = self.clamp_position(QPoint(self.x(), new_y))
            self.move(clamped)

    def load_config(self):
        self.saved_pos = None
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.scale_factor = data.get("scale_factor", 3)
                    self.snap_to_bottom = data.get("snap_to_bottom", True)
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
                "snap_to_bottom": self.snap_to_bottom
            }
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print("Failed to save config:", e)

    def get_default_position(self):
        """Calculates default position marked in user screenshot (~1520 X on 1920x1080, bottom of screen)."""
        screen = QApplication.primaryScreen().geometry()
        # Default X is ~79% of screen width (1520/1920 on full HD)
        default_x = int(screen.width() * (1520 / 1920)) - (self.width() // 2)
        # Default Y is sitting on the very bottom edge of the screen
        default_y = screen.height() - self.height()
        return QPoint(default_x, default_y)

    def ensure_valid_position(self):
        if self.saved_pos:
            self.move(self.clamp_position(self.saved_pos))
        else:
            self.move(self.clamp_position(self.get_default_position()))

    def enforce_topmost(self):
        if user32:
            try:
                hwnd = int(self.winId())
                user32.SetWindowPos(
                    hwnd,
                    HWND_TOPMOST,
                    0, 0, 0, 0,
                    SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW
                )
            except Exception:
                pass

    def paintEvent(self, event):
        painter = QPainter(self)
        pixmap = self.pm_arm if self.current_frame == "arm_up" else self.pm_base
        painter.drawPixmap(0, 0, pixmap)

    def trigger_wave_animation(self, duration_ms=700):
        """Raises arm up and starts timer to reset."""
        self.current_frame = "arm_up"
        self.update()
        self.arm_timer.stop()
        self.arm_timer.start(duration_ms)

    def reset_to_base(self):
        self.current_frame = "base"
        self.update()

    def set_scale(self, factor):
        self.scale_factor = max(1, min(10, factor))
        self.update_scaled_pixmaps()
        self.move(self.clamp_position(self.pos()))
        self.save_config()
        self.update()

    # --- Mouse Events ---

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_pos = event.globalPosition().toPoint()
            self.window_start_pos = self.pos()
            self.is_dragging = False
            # Instantly raise arm when clicked
            self.trigger_wave_animation(1000)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and self.drag_start_pos:
            delta = event.globalPosition().toPoint() - self.drag_start_pos
            if delta.manhattanLength() > 3:
                self.is_dragging = True
                target_pos = self.window_start_pos + delta

                screen = self.get_current_screen(target_pos)
                geom = screen.geometry()
                target_bottom_y = geom.top() + geom.height() - self.height()

                # Snap to bottom if close to bottom (within 20 pixels)
                if not self.snap_to_bottom and abs(target_pos.y() - target_bottom_y) < 20:
                    target_pos.setY(target_bottom_y)

                # Clamp strictly within screen boundaries
                clamped_pos = self.clamp_position(target_pos, screen)
                self.move(clamped_pos)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.is_dragging:
                # Finished dragging, save clamped position
                self.move(self.clamp_position(self.pos()))
                self.save_config()
                # Lower arm 400ms after release
                self.arm_timer.start(400)
            else:
                # Single click: raise arm and wave!
                self.trigger_wave_animation(700)
            self.drag_start_pos = None

    def wheelEvent(self, event):
        """Allows fast resizing with mouse wheel while hovering."""
        delta = event.angleDelta().y()
        if delta > 0:
            self.set_scale(self.scale_factor + 1)
        elif delta < 0:
            self.set_scale(self.scale_factor - 1)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 6px;
                padding: 4px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
            }
            QMenu::item {
                padding: 6px 20px 6px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #DA7758;
                color: #ffffff;
            }
            QMenu::separator {
                height: 1px;
                background-color: #444444;
                margin: 4px 10px;
            }
        """)

        anim_act = menu.addAction("👋 Поднять руку")
        anim_act.triggered.connect(lambda: self.trigger_wave_animation(800))

        scale_menu = menu.addMenu("📐 Размер")
        scale_options = [
            ("Половина высоты панели (24px, 3x)", 3),
            ("Средний (32px, 4x)", 4),
            ("Большой (40px, 5x)", 5),
            ("Высота всей панели (48px, 6x)", 6),
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
