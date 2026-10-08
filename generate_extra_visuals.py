"""
Generates additional visual graphics and banners for Clawd Taskbar GitHub repository.
Aesthetic: Anthropic editorial minimalism (#141413 dark background, Georgia + Segoe UI, no glass/pills).
"""

import os
import math
import glob
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
ANIM_DIR = os.path.join(BASE_DIR, "animations")
BASE_PNG = os.path.join(BASE_DIR, "base.png")

# Palette
BG_COLOR = (20, 20, 19, 255)         # #141413
TEXT_PRIMARY = (236, 235, 236, 255)  # Ivory / white
TEXT_SECONDARY = (180, 178, 175, 255)# Taupe gray
TEXT_MUTED = (115, 114, 110, 255)    # Subtle slate
ACCENT_CLAY = (217, 119, 87, 255)    # #d97757 Terracotta
GREEN_ACTIVE = (74, 222, 128, 255)   # #4ade80
PINK_BLUSH = (255, 50, 130, 255)     # Saturated pink
BORDER_SUBTLE = (45, 45, 43, 255)    # Subtle separator
BOX_BG = (28, 28, 27, 255)           # Very subtle surface

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

FONT_TITLE = get_font("C:/Windows/Fonts/georgia.ttf", 32)
FONT_HEAD = get_font("C:/Windows/Fonts/georgia.ttf", 20)
FONT_SUB = get_font("C:/Windows/Fonts/georgiai.ttf", 15)
FONT_SANS = get_font("C:/Windows/Fonts/segoeui.ttf", 14)
FONT_SANS_BOLD = get_font("C:/Windows/Fonts/segoeuib.ttf", 13)
FONT_SMALL = get_font("C:/Windows/Fonts/segoeui.ttf", 11)
FONT_CODE = get_font("C:/Windows/Fonts/consola.ttf", 12)

base_img = Image.open(BASE_PNG)

def load_frames(prefix):
    files = sorted(glob.glob(os.path.join(ANIM_DIR, f"{prefix}_*.png")))
    return [Image.open(f) for f in files] if files else [base_img]

walk_frames = load_frames("walk")
laptop_frames = load_frames("laptop_classic")
cheer_frames = load_frames("cheer")

def render_clawd(frame_img, blush=False, flip_x=False, scale=6):
    f = frame_img.convert("RGBA").copy()
    if blush:
        for cx in (4, 11):
            if 0 <= cx < f.width and 0 <= 6 < f.height and f.getpixel((cx, 6))[3] > 0:
                f.putpixel((cx, 6), (255, 50, 130, 255))
        for cx in (3, 12):
            if 0 <= cx < f.width and 0 <= 6 < f.height and f.getpixel((cx, 6))[3] > 0:
                f.putpixel((cx, 6), (255, 85, 155, 255))
    if flip_x:
        f = f.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    return f.resize((f.width * scale, f.height * scale), Image.Resampling.NEAREST)

# -------------------------------------------------------------
# 1. WANDER ZONE ANIMATED GIF (assets/wander_demo.gif)
# -------------------------------------------------------------
print("Generating Wander Demo GIF (assets/wander_demo.gif)...")
WANDER_W, WANDER_H = 880, 230
wander_gif_frames = []
TOTAL_W_FRAMES = 36

# Clawd walks back and forth between x=280 and x=600
min_x, max_x = 290, 590
walk_range = max_x - min_x
floor_y = 155

for f_idx in range(TOTAL_W_FRAMES):
    canvas = Image.new("RGBA", (WANDER_W, WANDER_H), BG_COLOR)
    draw = ImageDraw.Draw(canvas)
    
    # Title & description
    draw.text((44, 20), "Draggable Wander Zone", font=FONT_HEAD, fill=TEXT_PRIMARY)
    draw.text((276, 23), "—", font=FONT_SANS, fill=TEXT_MUTED)
    draw.text((294, 23), "Configurable taskbar roaming interval to never obstruct active apps", font=FONT_SANS, fill=TEXT_SECONDARY)
    draw.line([(44, 50), (WANDER_W - 44, 50)], fill=BORDER_SUBTLE, width=1)
    
    # Taskbar floor line
    draw.line([(44, floor_y), (WANDER_W - 44, floor_y)], fill=(55, 55, 52, 255), width=1)
    
    # Mock taskbar elements
    # Left: Start & pinned apps
    draw.rectangle([(54, floor_y - 28), (74, floor_y - 8)], outline=BORDER_SUBTLE, width=1) # Start
    draw.rectangle([(84, floor_y - 28), (104, floor_y - 8)], outline=BORDER_SUBTLE, width=1) # App 1
    draw.rectangle([(114, floor_y - 28), (134, floor_y - 8)], outline=BORDER_SUBTLE, width=1) # App 2
    draw.rectangle([(144, floor_y - 28), (164, floor_y - 8)], outline=BORDER_SUBTLE, width=1) # App 3
    draw.text((54, floor_y + 12), "Pinned Taskbar Apps", font=FONT_SMALL, fill=TEXT_MUTED)
    
    # Right: Tray
    draw.text((WANDER_W - 145, floor_y - 22), "18:42  ENG", font=FONT_CODE, fill=TEXT_MUTED)
    draw.text((WANDER_W - 145, floor_y + 12), "System Tray", font=FONT_SMALL, fill=TEXT_MUTED)
    
    # Wander Zone visual brackets
    bracket_h = 52
    b_top = floor_y - bracket_h
    b_bot = floor_y + 6
    
    # Dotted interval floor
    for dot_x in range(min_x + 10, max_x - 10, 16):
        draw.ellipse([(dot_x - 1, floor_y - 1), (dot_x + 1, floor_y + 1)], fill=(90, 85, 80, 255))
        
    # Left bracket
    draw.line([(min_x, b_top), (min_x, b_bot)], fill=ACCENT_CLAY, width=2)
    draw.line([(min_x, b_top), (min_x + 8, b_top)], fill=ACCENT_CLAY, width=2)
    draw.line([(min_x, b_bot), (min_x + 8, b_bot)], fill=ACCENT_CLAY, width=2)
    
    # Right bracket
    draw.line([(max_x, b_top), (max_x, b_bot)], fill=ACCENT_CLAY, width=2)
    draw.line([(max_x, b_top), (max_x - 8, b_top)], fill=ACCENT_CLAY, width=2)
    draw.line([(max_x, b_bot), (max_x - 8, b_bot)], fill=ACCENT_CLAY, width=2)
    
    # Zone label & range
    zone_mid_x = (min_x + max_x) // 2
    draw.text((zone_mid_x - 62, b_top - 18), "←  300px Safe Roam Zone  →", font=FONT_SMALL, fill=ACCENT_CLAY)
    draw.text((zone_mid_x - 56, floor_y + 12), "Interactive Boundary Interval", font=FONT_SMALL, fill=TEXT_MUTED)
    
    # Position calculation (keep Clawd comfortably inside bounds)
    t = (f_idx / TOTAL_W_FRAMES) * 2 * math.pi
    pos_factor = (math.sin(t) + 1) / 2  # 0 to 1
    safe_margin = 40
    curr_x = int((min_x + safe_margin) + pos_factor * (walk_range - 2 * safe_margin))
    is_facing_left = math.cos(t) < 0
    
    # Select walk frame
    wf = walk_frames[f_idx % len(walk_frames)]
    sp = render_clawd(wf, blush=False, flip_x=is_facing_left, scale=5)
    
    canvas.alpha_composite(sp, (curr_x - sp.width // 2, floor_y - sp.height))
    
    wander_gif_frames.append(canvas.convert("RGB"))

out_wander = os.path.join(ASSETS_DIR, "wander_demo.gif")
wander_gif_frames[0].save(
    out_wander,
    save_all=True,
    append_images=wander_gif_frames[1:],
    duration=110,
    loop=0,
    optimize=True
)
print(f"Created {out_wander} ({os.path.getsize(out_wander)} bytes)")

# -------------------------------------------------------------
# 2. ARCHITECTURE / SYSTEM OVERVIEW (assets/architecture.png)
# -------------------------------------------------------------
print("Generating Architecture Overview (assets/architecture.png)...")
ARCH_W, ARCH_H = 880, 280
a_canvas = Image.new("RGBA", (ARCH_W, ARCH_H), BG_COLOR)
ad = ImageDraw.Draw(a_canvas)

# Title
ad.text((44, 24), "Architecture & Runtime Overview", font=FONT_HEAD, fill=TEXT_PRIMARY)
ad.text((375, 27), "—", font=FONT_SANS, fill=TEXT_MUTED)
ad.text((395, 27), "Lightweight Win32 integration with zero idle CPU overhead", font=FONT_SANS, fill=TEXT_SECONDARY)
ad.line([(44, 56), (ARCH_W - 44, 56)], fill=BORDER_SUBTLE, width=1)

# 3 Columns
cols = [
    ("Process & System Watcher", [
        ("Claude Code Monitor", "Background process scan (claude, ide)"),
        ("Active Shell Hook", "Tracks Windows Shell_TrayWnd taskbar"),
        ("AFK Inactivity Timer", "Detects user idle states after 5 minutes")
    ]),
    ("Behavior & Emotion Engine", [
        ("Smart Context", "Spawns laptop & types during generation"),
        ("Crown Petting Logic", "Upper-bound cursor detection + bloom"),
        ("Wander Pathing", "Clamped step algorithms within user zone")
    ]),
    ("Native Win32 Display Layer", [
        ("Frameless Transparent Window", "Qt.WindowStaysOnTopHint + layered canvas"),
        ("Crisp Nearest-Neighbor", "Subpixel integer scaling (16x16 to high DPI)"),
        ("0.0% CPU Footprint", "Event-driven updates, no active busy loops")
    ])
]

col_w = (ARCH_W - 88 - 32) // 3
for i, (col_title, items) in enumerate(cols):
    cx = 44 + i * (col_w + 16)
    # Box background
    ad.rectangle([(cx, 74), (cx + col_w, ARCH_H - 28)], fill=BOX_BG, outline=BORDER_SUBTLE, width=1)
    
    # Column Header
    ad.text((cx + 16, 88), col_title, font=FONT_SANS_BOLD, fill=ACCENT_CLAY)
    ad.line([(cx + 16, 112), (cx + col_w - 16, 112)], fill=BORDER_SUBTLE, width=1)
    
    iy = 126
    for item_title, item_sub in items:
        ad.text((cx + 16, iy), item_title, font=FONT_SANS_BOLD, fill=TEXT_PRIMARY)
        ad.text((cx + 16, iy + 18), item_sub, font=FONT_SMALL, fill=TEXT_MUTED)
        iy += 42

out_arch = os.path.join(ASSETS_DIR, "architecture.png")
a_canvas.save(out_arch, format="PNG")
print(f"Created {out_arch} ({os.path.getsize(out_arch)} bytes)")


# -------------------------------------------------------------
# 3. INTERACTION & CONTROLS GUIDE (assets/controls_guide.png)
# -------------------------------------------------------------
print("Generating Interaction Guide (assets/controls_guide.png)...")
CTRL_W, CTRL_H = 880, 220
c_canvas = Image.new("RGBA", (CTRL_W, CTRL_H), BG_COLOR)
cd = ImageDraw.Draw(c_canvas)

cd.text((44, 22), "Mouse Controls & Interactions", font=FONT_HEAD, fill=TEXT_PRIMARY)
cd.text((340, 25), "—", font=FONT_SANS, fill=TEXT_MUTED)
cd.text((358, 25), "Four direct ways to engage with your taskbar mascot", font=FONT_SANS, fill=TEXT_SECONDARY)
cd.line([(44, 52), (CTRL_W - 44, 52)], fill=BORDER_SUBTLE, width=1)

controls = [
    ("Pet Crown", "Hover above head", "Vibrant pink cheeks bloom;\nclears instantly on click"),
    ("Quick Play", "Left Click", "Triggers random reaction:\nwave, cheer, crystal magic"),
    ("Relocate", "Drag Upwards", "Lifts off the taskbar floor;\nreposition anywhere horizontally"),
    ("Preferences", "Right Click", "Configure wander zone, autostart,\nlanguage, or quit")
]

card_w = (CTRL_W - 88 - 36) // 4
for i, (act_title, act_input, act_desc) in enumerate(controls):
    cx = 44 + i * (card_w + 12)
    cd.rectangle([(cx, 70), (cx + card_w, CTRL_H - 24)], fill=BOX_BG, outline=BORDER_SUBTLE, width=1)
    
    cd.text((cx + 14, 84), act_title, font=FONT_SANS_BOLD, fill=TEXT_PRIMARY)
    cd.text((cx + 14, 104), act_input, font=FONT_CODE, fill=ACCENT_CLAY)
    cd.line([(cx + 14, 126), (cx + card_w - 14, 126)], fill=BORDER_SUBTLE, width=1)
    
    cd.text((cx + 14, 138), act_desc, font=FONT_SMALL, fill=TEXT_SECONDARY)

out_ctrl = os.path.join(ASSETS_DIR, "controls_guide.png")
c_canvas.save(out_ctrl, format="PNG")
print(f"Created {out_ctrl} ({os.path.getsize(out_ctrl)} bytes)")

print("\nAll extra visuals generated successfully!")
