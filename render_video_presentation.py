"""
Renders a broadcast-quality Full HD (1920x1080 @ 30 FPS) MP4 video presentation
showcasing all 32 animations of the Claude Taskbar Mascot with titles,
categories, statistics, magnified hero previews, and real-time taskbar simulation.
"""

import os
import glob
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ANIM_DIR = os.path.join(BASE_DIR, "animations")
OUTPUT_VIDEO = os.path.join(BASE_DIR, "claude_showcase.mp4")

# Font configuration
FONT_TITLE = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 46)
FONT_SUBTITLE = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 28)
FONT_BODY = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 24)
FONT_BADGE = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 18)
FONT_MONO = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 22)
FONT_HERO = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 64)
FONT_HERO_SUB = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 30)

WIDTH, HEIGHT = 1920, 1080
FPS = 30

ANIMATIONS_META = [
    # 1. Classic & Emotions
    {"name": "wave", "title": "Помахать рукой (Wave)", "cat": "Эмоции и жесты", "desc": "Дружелюбный привет пользователю правой рукой", "speed_ms": 110, "tag": "EMOTION"},
    {"name": "cheer", "title": "Радость (Cheer)", "cat": "Эмоции и жесты", "desc": "Победный восторг с обеими поднятыми руками", "speed_ms": 120, "tag": "EMOTION"},
    {"name": "jump", "title": "Прыжок (Jump)", "cat": "Эмоции и жесты", "desc": "Пружинистый прыжок с плавной деформацией тела", "speed_ms": 100, "tag": "EMOTION"},
    {"name": "dance", "title": "Весёлый танец (Dance)", "cat": "Эмоции и жесты", "desc": "Ритмичный шаг влево и вправо в такт музыке", "speed_ms": 120, "tag": "EMOTION"},
    {"name": "heart", "title": "Любовь и сердечко (Heart)", "cat": "Эмоции и жесты", "desc": "Смущенный румянец на щечках и бьющееся сердце", "speed_ms": 130, "tag": "EMOTION"},
    {"name": "cool", "title": "Крутой в очках (Cool)", "cat": "Эмоции и жесты", "desc": "Черные солнцезащитные очки падают с блеском", "speed_ms": 130, "tag": "EMOTION"},
    {"name": "applause", "title": "Аплодисменты (Applause)", "cat": "Эмоции и жесты", "desc": "Бурные овации в ладоши и палец вверх автору", "speed_ms": 110, "tag": "EMOTION"},
    {"name": "dab", "title": "Победный дэб (Dab)", "cat": "Эмоции и жесты", "desc": "Стильный победный дэб с наклоном головы в локоть", "speed_ms": 110, "tag": "EMOTION"},
    {"name": "cry", "title": "Аниме-плач (Cry)", "cat": "Эмоции и жесты", "desc": "Драматичные фонтаны слез в обе стороны", "speed_ms": 110, "tag": "EMOTION"},
    {"name": "yawn", "title": "Зевнуть и потянуться (Yawn)", "cat": "Эмоции и жесты", "desc": "Усталый зевок с открытым ртом и потягиванием", "speed_ms": 140, "tag": "EMOTION"},
    {"name": "question", "title": "Недоумение (Question)", "cat": "Эмоции и жесты", "desc": "Наклон головы и вопросительный знак над головой", "speed_ms": 130, "tag": "EMOTION"},
    {"name": "look_around", "title": "Оглядеться по сторонам", "cat": "Эмоции и жесты", "desc": "Любопытный взгляд влево, вправо и по центру", "speed_ms": 130, "tag": "EMOTION"},
    {"name": "blink", "title": "Моргание (Blink)", "cat": "Эмоции и жесты", "desc": "Естественное моргание глазками в фоновом режиме", "speed_ms": 90, "tag": "EMOTION"},
    # 2. Tech & Work
    {"name": "typing", "title": "Кодить за ноутбуком (Typing)", "cat": "Работа и код", "desc": "Быстрый набор кода на светящемся кибер-ноуте", "speed_ms": 110, "tag": "TECH"},
    {"name": "matrix", "title": "Матрица / Хакер (Matrix)", "cat": "Работа и код", "desc": "Зеленый цифровой дождь кода и неоновый визор", "speed_ms": 120, "tag": "TECH"},
    {"name": "idea", "title": "Осенила идея (Idea)", "cat": "Работа и код", "desc": "Яркая вспышка лампочки с лучами вдохновения", "speed_ms": 120, "tag": "TECH"},
    {"name": "read", "title": "Чтение документации (Read)", "cat": "Работа и код", "desc": "Изучает мануал и аккуратно листает страницу", "speed_ms": 130, "tag": "TECH"},
    {"name": "coffee", "title": "Выпить чашку кофе (Coffee)", "cat": "Работа и код", "desc": "Горячая кружка кофе с ароматным паром", "speed_ms": 140, "tag": "TECH"},
    # 3. Memes & Fun
    {"name": "pizza", "title": "Кушать пиццу (Pizza)", "cat": "Мемы и юмор", "desc": "Аппетитный горячий ломтик с тянущимся сыром", "speed_ms": 120, "tag": "MEME"},
    {"name": "rage", "title": "Рейдж / Переворот стола (Rage)", "cat": "Мемы и юмор", "desc": "Классический (╯°□°)╯︵ ┻━┻ после бага в коде", "speed_ms": 100, "tag": "MEME"},
    {"name": "rock", "title": "Рок-концерт (Rock)", "cat": "Мемы и юмор", "desc": "Забойное соло на электрогитаре с хедбэнгингом", "speed_ms": 100, "tag": "MEME"},
    {"name": "fire", "title": "This is Fine (В огне)", "cat": "Мемы и юмор", "desc": "Вокруг бушует пламя, а Клод спокоен с чашкой", "speed_ms": 130, "tag": "MEME"},
    {"name": "cat", "title": "Котик на голове (Cat)", "cat": "Мемы и юмор", "desc": "Мурчащий рыжий котенок с виляющим хвостиком", "speed_ms": 130, "tag": "MEME"},
    {"name": "money", "title": "Денежный дождь (Money)", "cat": "Мемы и юмор", "desc": "Дождь из золотых монет и хрустящих банкнот", "speed_ms": 120, "tag": "MEME"},
    {"name": "disco", "title": "Диско-вечеринка (Disco)", "cat": "Мемы и юмор", "desc": "Позы Траволты под сверкающим диско-шаром", "speed_ms": 120, "tag": "MEME"},
    # 4. Action & Magic
    {"name": "wizard", "title": "Волшебник (Wizard)", "cat": "Магия и экшен", "desc": "Шляпа мага, взмах палочки и сноп волшебных звезд", "speed_ms": 120, "tag": "MAGIC"},
    {"name": "superhero", "title": "Супермен / Полёт (Superhero)", "cat": "Магия и экшен", "desc": "Развевающийся красный плащ и взлет в небо", "speed_ms": 100, "tag": "MAGIC"},
    {"name": "ghost", "title": "Привидение / Бу! (Ghost)", "cat": "Магия и экшен", "desc": "Превращение в милое привидение с криком Бу!", "speed_ms": 110, "tag": "MAGIC"},
    {"name": "workout", "title": "Качалка / Штанга (Workout)", "cat": "Магия и экшен", "desc": "Рывок тяжелой штанги над головой и флекс мышц", "speed_ms": 120, "tag": "MAGIC"},
    {"name": "spin", "title": "Крутиться на 360° (Spin)", "cat": "Магия и экшен", "desc": "Стремительный полный оборот вокруг своей оси", "speed_ms": 90, "tag": "MAGIC"},
    {"name": "peek", "title": "Прятаться за панель (Peek)", "cat": "Магия и экшен", "desc": "Опускается за край панели и высматривает", "speed_ms": 120, "tag": "MAGIC"},
    # 5. Modes
    {"name": "sleep", "title": "Заснуть (Sleep Zzz)", "cat": "Режимы", "desc": "Глубокий уютный сон с улетающими буквами Zzz", "speed_ms": 200, "tag": "MODE"},
]

CATEGORY_COLORS = {
    "EMOTION": ((235, 90, 130), (255, 230, 240)),  # Pink
    "TECH":    ((40, 190, 230), (220, 250, 255)),  # Cyan
    "MEME":    ((245, 140, 40), (255, 245, 220)),  # Orange
    "MAGIC":   ((160, 90, 240), (245, 230, 255)),  # Purple
    "MODE":    ((90, 170, 240), (230, 245, 255)),  # Blue
}

def load_frames(anim_name):
    pattern = os.path.join(ANIM_DIR, f"{anim_name}_*.png")
    files = sorted(glob.glob(pattern))
    frames = []
    for f in files:
        img = Image.open(f).convert("RGBA")
        frames.append(img)
    return frames

def create_background():
    # Base dark gradient
    bg = Image.new("RGBA", (WIDTH, HEIGHT), (14, 16, 22, 255))
    draw = ImageDraw.Draw(bg)

    # Subtle grid lines
    grid_color = (255, 255, 255, 8)
    for x in range(0, WIDTH, 60):
        draw.line([(x, 0), (x, HEIGHT)], fill=grid_color, width=1)
    for y in range(0, HEIGHT, 60):
        draw.line([(0, y), (WIDTH, y)], fill=grid_color, width=1)

    # Terracotta ambient glow at center-right
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    cx, cy = 1350, 480
    for r in range(450, 0, -20):
        alpha = int(28 * (1.0 - r / 450.0))
        glow_draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(218, 119, 88, alpha))
    bg = Image.alpha_composite(bg, glow)
    return bg

def render_taskbar_strip(current_frame, width=WIDTH, height=72):
    """Draws a replica of Windows 11 Taskbar with Claude sitting on it."""
    bar = Image.new("RGBA", (width, height), (28, 30, 36, 250))
    draw = ImageDraw.Draw(bar)

    # Top border line
    draw.line([(0, 0), (width, 0)], fill=(60, 64, 75, 255), width=1)

    # Centered taskbar icons (Windows 11 style)
    cx = width // 2
    # Start button (blue 4 squares)
    draw.rectangle([cx - 130, 24, cx - 108, 46], fill=(0, 120, 215, 255))
    draw.line([(cx - 119, 24), (cx - 119, 46)], fill=(28, 30, 36, 255), width=2)
    draw.line([(cx - 130, 35), (cx - 108, 35)], fill=(28, 30, 36, 255), width=2)

    # Search bar (pill)
    draw.rounded_rectangle([cx - 95, 20, cx + 20, 50], radius=15, fill=(42, 45, 54, 255))
    draw.ellipse([cx - 80, 28, cx - 68, 40], outline=(150, 155, 170, 255), width=2)
    draw.line([(cx - 70, 38), (cx - 65, 43)], fill=(150, 155, 170, 255), width=2)

    # App icons
    icons = [
        ((250, 160, 40), cx + 40),   # Explorer / folder
        ((30, 160, 240), cx + 75),   # Edge / Browser
        ((60, 100, 240), cx + 110),  # VS Code / IDE
        ((80, 200, 120), cx + 145),  # Terminal
    ]
    for color, ix in icons:
        draw.rounded_rectangle([ix, 22, ix + 24, 46], radius=6, fill=color)

    # Place real-sized Claude at X = 1500 (inside tray area)
    claude_3x = current_frame.resize((48, 48), Image.Resampling.NEAREST)
    bar.paste(claude_3x, (1500, height - 48), claude_3x)

    # Tray clock & network placeholder
    draw.text((width - 120, 24), "12:00", fill=(200, 205, 220, 255), font=FONT_BADGE)
    draw.text((width - 120, 42), "10.08.2026", fill=(130, 135, 150, 255), font=ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 13))

    return bar

def render_slide(meta, frame_idx, frame_img, anim_idx, total_anims, base_bg):
    img = base_bg.copy()
    draw = ImageDraw.Draw(img)

    # Top Header Banner
    draw.text((90, 55), "CLAUDE PIXEL TASKBAR MASCOT", fill=(218, 119, 88, 255), font=FONT_BADGE)
    draw.text((380, 55), "|   ПОЛНАЯ ПРЕЗЕНТАЦИЯ ВСЕХ АНИМАЦИЙ", fill=(140, 145, 160, 255), font=FONT_BADGE)

    # Category Pill Badge
    tag = meta.get("tag", "EMOTION")
    border_col, text_col = CATEGORY_COLORS.get(tag, ((218, 119, 88), (255, 255, 255)))
    badge_text = f"★  {meta['cat'].upper()}"
    draw.rounded_rectangle([90, 120, 320, 156], radius=18, fill=(30, 33, 42, 230), outline=border_col, width=2)
    draw.text((115, 127), badge_text, fill=text_col, font=FONT_BADGE)

    # Counter (e.g. 05 / 32)
    counter_str = f"#{anim_idx + 1:02d} / {total_anims:02d}"
    draw.text((340, 126), counter_str, fill=(180, 185, 200, 255), font=FONT_SUBTITLE)

    # Animation Title
    draw.text((90, 180), meta["title"], fill=(255, 255, 255, 255), font=FONT_TITLE)

    # Internal animation identifier
    id_str = f"claude.play_animation(\"{meta['name']}\")"
    draw.text((90, 250), id_str, fill=(218, 119, 88, 255), font=FONT_MONO)

    # Description
    draw.text((90, 310), meta["desc"], fill=(195, 200, 215, 255), font=FONT_BODY)

    # Specs Box (Glassmorphic info card)
    box_x, box_y, box_w, box_h = 90, 390, 520, 250
    draw.rounded_rectangle([box_x, box_y, box_x + box_w, box_y + box_h], radius=16, fill=(24, 27, 36, 210), outline=(55, 60, 75, 255), width=2)

    specs = [
        ("Кадров в цикле:", f"{len(load_frames(meta['name']))} кадров"),
        ("Скорость тика:", f"{meta['speed_ms']} мс / кадр"),
        ("Пиксельная сетка:", "16x16 (Pixel Perfect)"),
        ("Цветовая палитра:", "Terracotta Anthropic"),
        ("Текущий кадр:", f"Кадр #{frame_idx + 1} из {len(load_frames(meta['name']))}"),
    ]
    for i, (label, val) in enumerate(specs):
        sy = box_y + 24 + i * 42
        draw.text((box_x + 30, sy), label, fill=(130, 135, 150, 255), font=FONT_BODY)
        draw.text((box_x + 280, sy), val, fill=(255, 255, 255, 255), font=FONT_BODY)

    # --- HERO STAGE (Center-Right) ---
    stage_cx, stage_cy = 1350, 500

    # Stage Pedestal / Neon Platform
    draw.ellipse([stage_cx - 240, stage_cy + 160, stage_cx + 240, stage_cy + 240], fill=(20, 22, 28, 255), outline=(218, 119, 88, 160), width=3)
    draw.ellipse([stage_cx - 180, stage_cy + 180, stage_cx + 180, stage_cy + 225], fill=(218, 119, 88, 25))

    # Large 22x scale Claude Sprite (352x352)
    hero_size = 352
    hero_frame = frame_img.resize((hero_size, hero_size), Image.Resampling.NEAREST)
    hero_x = stage_cx - (hero_size // 2)
    hero_y = stage_cy - (hero_size // 2) + 20
    img.paste(hero_frame, (hero_x, hero_y), hero_frame)

    # Hero caption badge
    draw.rounded_rectangle([stage_cx - 140, stage_cy + 260, stage_cx + 140, stage_cy + 295], radius=12, fill=(20, 22, 28, 220), outline=(50, 55, 68, 255), width=1)
    draw.text((stage_cx - 120, stage_cy + 268), "УВЕЛИЧЕНО В 22 РАЗА (352px)", fill=(170, 175, 190, 255), font=FONT_BADGE)

    # --- SIMULATED TASKBAR AT BOTTOM ---
    taskbar = render_taskbar_strip(frame_img, width=WIDTH, height=76)
    img.paste(taskbar, (0, HEIGHT - 76), taskbar)

    # Taskbar hint text
    draw.text((1200, HEIGHT - 105), "▲ Реальный вид на панели задач (масштаб 3x, 48px)", fill=(160, 165, 180, 255), font=FONT_BADGE)

    # Global Progress Bar (very bottom)
    progress = (anim_idx + 1) / total_anims
    bar_w = int(WIDTH * progress)
    draw.line([(0, HEIGHT - 3), (bar_w, HEIGHT - 3)], fill=(218, 119, 88, 255), width=3)

    return img

def render_intro_slide(base_bg):
    img = base_bg.copy()
    draw = ImageDraw.Draw(img)

    # Huge Centered Title Card
    cx, cy = WIDTH // 2, HEIGHT // 2 - 50

    # Glow badge
    draw.rounded_rectangle([cx - 200, cy - 180, cx + 200, cy - 130], radius=25, fill=(218, 119, 88, 40), outline=(218, 119, 88, 255), width=2)
    draw.text((cx - 165, cy - 168), "★  OFFICIAL MASCOT SHOWCASE", fill=(255, 230, 220, 255), font=FONT_BADGE)

    draw.text((cx - 520, cy - 90), "CLAUDE PIXEL TASKBAR", fill=(255, 255, 255, 255), font=FONT_HERO)
    draw.text((cx - 410, cy), "32 УНИКАЛЬНЫХ АНИМАЦИИ & РЕАКЦИИ", fill=(218, 119, 88, 255), font=FONT_HERO_SUB)

    sub = "Пиксельный маскот для панели задач Windows 11 с нулевой задержкой и 0% CPU"
    draw.text((cx - 440, cy + 80), sub, fill=(180, 185, 200, 255), font=FONT_BODY)

    # Four feature pills
    pills = ["195 Спрайтов", "16x16 Pixel Art", "1 мс Реакция", "Windows 11 Ready"]
    for i, p in enumerate(pills):
        px = cx - 380 + i * 200
        py = cy + 160
        draw.rounded_rectangle([px, py, px + 170, py + 46], radius=14, fill=(28, 32, 42, 230), outline=(60, 65, 80, 255), width=1)
        draw.text((px + 20, py + 12), p, fill=(220, 225, 240, 255), font=FONT_BADGE)

    return img

def render_outro_slide(base_bg):
    img = base_bg.copy()
    draw = ImageDraw.Draw(img)

    cx, cy = WIDTH // 2, HEIGHT // 2 - 40
    draw.text((cx - 430, cy - 100), "ВСЕ 32 АНИМАЦИИ ГОТОВЫ!", fill=(255, 255, 255, 255), font=FONT_HERO)
    draw.text((cx - 380, cy), "Нажмите правой кнопкой мыши по Клоду,", fill=(218, 119, 88, 255), font=FONT_HERO_SUB)
    draw.text((cx - 350, cy + 50), "чтобы запустить любую анимацию в меню!", fill=(218, 119, 88, 255), font=FONT_HERO_SUB)

    draw.text((cx - 310, cy + 150), "Или просто кликайте левой кнопкой мыши для случайных реакций ✨", fill=(170, 175, 190, 255), font=FONT_BODY)
    return img

def main():
    print("Preparing 1080p 60 FPS video renderer for 32 Claude animations...")
    base_bg = create_background()

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(OUTPUT_VIDEO, fourcc, FPS, (WIDTH, HEIGHT))
    if not out.isOpened():
        print("Error: Could not open VideoWriter!")
        return

    # 1. Intro sequence (2 seconds = 60 frames)
    intro_img = render_intro_slide(base_bg)
    intro_cv = cv2.cvtColor(np.array(intro_img), cv2.COLOR_RGBA2BGR)
    print("Rendering Intro Card...")
    for _ in range(60):
        out.write(intro_cv)

    # 2. Render each of the 32 animations
    total_anims = len(ANIMATIONS_META)
    for anim_idx, meta in enumerate(ANIMATIONS_META):
        anim_name = meta["name"]
        frames = load_frames(anim_name)
        if not frames:
            print(f"Warning: No frames for {anim_name}")
            continue

        print(f"[{anim_idx + 1:02d}/{total_anims:02d}] Rendering '{anim_name}' ({len(frames)} frames)...")

        # We display each animation for approximately 2.2 seconds (66 video frames)
        # Cycling through the animation frames according to their speed_ms
        target_video_frames = 66
        ms_per_video_frame = 1000.0 / FPS
        speed_ms = meta["speed_ms"]

        current_time_ms = 0.0
        for _ in range(target_video_frames):
            frame_idx = int(current_time_ms / speed_ms) % len(frames)
            current_frame = frames[frame_idx]

            slide_img = render_slide(meta, frame_idx, current_frame, anim_idx, total_anims, base_bg)
            slide_cv = cv2.cvtColor(np.array(slide_img), cv2.COLOR_RGBA2BGR)
            out.write(slide_cv)

            current_time_ms += ms_per_video_frame

    # 3. Outro sequence (2 seconds = 60 frames)
    print("Rendering Outro Card...")
    outro_img = render_outro_slide(base_bg)
    outro_cv = cv2.cvtColor(np.array(outro_img), cv2.COLOR_RGBA2BGR)
    for _ in range(60):
        out.write(outro_cv)

    out.release()
    file_size_mb = os.path.getsize(OUTPUT_VIDEO) / (1024 * 1024)
    print(f"\nSUCCESS! Video presentation saved to {OUTPUT_VIDEO} ({file_size_mb:.2f} MB)")

if __name__ == "__main__":
    main()
