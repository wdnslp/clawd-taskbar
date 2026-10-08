"""
Minimalist Anthropic-Style GitHub Banner Generator for Clawd Taskbar Mascot.

Design Philosophy:
- Pure monotone dark background (#141413 - Anthropic's signature charcoal)
- Anthropic editorial serif typography (Georgia) + clean humanist sans (Segoe UI)
- Zero badges, zero pills, zero glass, zero glow blobs - pure minimalist elegance
- Highlighting Claude Code active reaction (typing on laptop) and head petting
"""

import os
import math
import glob
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
ANIM_DIR = os.path.join(BASE_DIR, "animations")
BASE_PNG = os.path.join(BASE_DIR, "base.png")

os.makedirs(ASSETS_DIR, exist_ok=True)

# Anthropic Design System Colors
BG_COLOR = (20, 20, 19, 255)         # #141413 Flat monotone dark charcoal
TEXT_PRIMARY = (236, 235, 236, 255)  # Warm ivory / off-white
TEXT_SECONDARY = (180, 178, 175, 255)# Warm taupe gray
TEXT_MUTED = (115, 114, 110, 255)    # Subtle warm slate
ACCENT_CLAY = (217, 119, 87, 255)    # #d97757 Anthropic terracotta
GREEN_ACTIVE = (74, 222, 128, 255)   # #4ade80 Clean active status
PINK_BLUSH = (255, 50, 130, 255)     # Vibrant high-contrast blush pink
PINK_SUB_BLUSH = (255, 85, 155, 255) # Secondary blush pink
BORDER_SUBTLE = (45, 45, 43, 255)    # Barely visible dark separator line

# Fonts
def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

FONT_TITLE = get_font("C:/Windows/Fonts/georgia.ttf", 46)
FONT_TITLE_ITALIC = get_font("C:/Windows/Fonts/georgiai.ttf", 17)
FONT_HEAD = get_font("C:/Windows/Fonts/georgia.ttf", 18)
FONT_SANS = get_font("C:/Windows/Fonts/segoeui.ttf", 14)
FONT_SANS_BOLD = get_font("C:/Windows/Fonts/segoeuib.ttf", 12)
FONT_LABEL = get_font("C:/Windows/Fonts/segoeui.ttf", 12)
FONT_SMALL = get_font("C:/Windows/Fonts/segoeui.ttf", 11)
FONT_CODE = get_font("C:/Windows/Fonts/consola.ttf", 12)

# Load animation frames
base_img = Image.open(BASE_PNG)

def load_frames(prefix):
    files = sorted(glob.glob(os.path.join(ANIM_DIR, f"{prefix}_*.png")))
    return [Image.open(f) for f in files] if files else [base_img]

laptop_frames = load_frames("laptop_classic")
cheer_frames = load_frames("cheer")
blink_frames = load_frames("blink")


def render_clawd_sprite(frame_img, blush_alpha=0.0, scale=8):
    """Upscales Clawd frame crisply, adding high-contrast pink blush if in idle state."""
    frame = frame_img.convert("RGBA").copy()
    if blush_alpha > 0.01:
        # High-contrast vibrant pink blush on cheeks (4,6) and (11,6)
        r, g, b = 255, 50, 130
        for cx in (4, 11):
            if 0 <= cx < frame.width and 0 <= 6 < frame.height:
                if frame.getpixel((cx, 6))[3] > 0:
                    frame.putpixel((cx, 6), (r, g, b, 255))
        if blush_alpha > 0.25:
            for cx in (3, 12):
                if 0 <= cx < frame.width and 0 <= 6 < frame.height:
                    if frame.getpixel((cx, 6))[3] > 0:
                        frame.putpixel((cx, 6), (255, 85, 155, 255))
    return frame.resize((frame.width * scale, frame.height * scale), Image.Resampling.NEAREST)


def create_pixel_cursor(scale=3):
    grid = [
        "X       ",
        "XX      ",
        "X.X     ",
        "X..X    ",
        "X...X   ",
        "X....X  ",
        "X.....X ",
        "X...XXXX",
        "X.X.X   ",
        "XX XX   ",
        "X   X   "
    ]
    w = len(grid[0])
    h = len(grid)
    cur = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for y in range(h):
        for x in range(w):
            c = grid[y][x]
            if c == 'X':
                cur.putpixel((x, y), (20, 20, 19, 255))
            elif c == '.':
                cur.putpixel((x, y), (245, 245, 245, 255))
    return cur.resize((w * scale, h * scale), Image.Resampling.NEAREST)


def create_pixel_heart(scale=3, alpha=255):
    grid = [
        " .X. .X. ",
        "XXXX XXXX",
        "XXXXXXXXX",
        " XXXXXXX ",
        "  XXXXX  ",
        "   XXX   ",
        "    X    "
    ]
    w = len(grid[0])
    h = len(grid)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for y in range(h):
        for x in range(w):
            c = grid[y][x]
            if c == 'X':
                im.putpixel((x, y), (255, 50, 130, alpha))
            elif c == '.':
                im.putpixel((x, y), (255, 120, 175, alpha))
    return im.resize((w * scale, h * scale), Image.Resampling.NEAREST)


# =========================================================================
# 1. GENERATE MAIN ANIMATED GITHUB BANNER (assets/banner_animated.gif)
# =========================================================================
print("Generating Minimalist Anthropic-Style Animated Banner (assets/banner_animated.gif)...")

BANNER_W, BANNER_H = 920, 320
cursor_sprite = create_pixel_cursor(scale=3)

# 38 frames loop (~4.1 seconds at 110ms)
frames = []
TOTAL_FRAMES = 38

for f_idx in range(TOTAL_FRAMES):
    canvas = Image.new("RGBA", (BANNER_W, BANNER_H), BG_COLOR)
    draw = ImageDraw.Draw(canvas)
    
    # Left Column: Editorial Typography & Dynamic Live Status
    # Header: Title in Georgia serif
    draw.text((54, 42), "Clawd", font=FONT_TITLE, fill=TEXT_PRIMARY)
    
    # Elegant terracotta period or subtle brand subtitle
    draw.text((188, 54), "—", font=FONT_SANS, fill=TEXT_MUTED)
    draw.text((206, 52), "Pixel mascot for Windows taskbar", font=FONT_TITLE_ITALIC, fill=TEXT_SECONDARY)
    
    # Subtle separator line
    draw.line([(54, 106), (560, 106)], fill=BORDER_SUBTLE, width=1)
    
    # Dynamic Status & Feature description depending on phase:
    # Phase 1 (f: 0..7): Idle / Calm
    # Phase 2 (f: 8..21): Claude Code is Working! (Clawd types on laptop)
    # Phase 3 (f: 22..30): Petting on crown of head (Rosy cheeks bloom)
    # Phase 4 (f: 31..37): Animation starts -> Cheeks instantly clear! (Clawd cheers)
    
    cur_frame = base_img
    blush = 0.0
    cursor_pos = None
    heart_info = None
    stage_x, stage_y = 690, 85
    
    if 0 <= f_idx < 8:
        # State: Idle
        status_dot_col = TEXT_MUTED
        status_title = "Standby  •  Living quietly on taskbar"
        status_desc = "Clawd rests on your Windows taskbar with living animations."
        if f_idx in (3, 4):
            cur_frame = blink_frames[min(1, len(blink_frames)-1)]
        else:
            cur_frame = base_img
            
    elif 8 <= f_idx < 22:
        # State: Claude Code Active! (REACTS WHEN CLAUDE IS WORKING)
        status_dot_col = GREEN_ACTIVE
        status_title = "Claude Code Active  •  Typing in real-time"
        status_desc = "Detects Claude Code CLI & IDE terminal processes.\nClawd opens his laptop and types alongside you while coding."
        laptop_idx = (f_idx - 8) % len(laptop_frames)
        cur_frame = laptop_frames[laptop_idx]
        
    elif 22 <= f_idx < 31:
        # State: Petting strictly above head
        status_dot_col = PINK_BLUSH
        status_title = "Head Petting  •  Rosy cheeks blooming"
        status_desc = "Stroke the crown of his head with the mouse cursor.\nVibrant pink cheeks appear as you pet him."
        cur_frame = base_img
        
        # Petting progress
        pet_p = (f_idx - 22) / 8.0
        blush = min(1.0, pet_p * 1.3)
        
        # Cursor strictly moving ABOVE head (y <= 5*scale)
        head_cx = stage_x + 64
        head_top_y = stage_y + 18
        sway_x = math.sin((f_idx - 22) * 1.6) * 18
        cursor_pos = (int(head_cx + sway_x - 12), int(head_top_y - 10))
        
        if f_idx >= 26:
            hp = (f_idx - 26) / 5.0
            hx = int(head_cx + 26)
            hy = int(head_top_y - 20 - hp * 22)
            ha = int(255 * (1.0 - hp * 0.5))
            heart_info = (hx, hy, ha)
            
    else:
        # State: Animation starts -> Cheeks INSTANTLY CLEARED!
        status_dot_col = ACCENT_CLAY
        status_title = "Action Triggered  •  Cheeks instantly clear"
        status_desc = "Cheeks immediately vanish when any animation plays\nor when Clawd moves or reacts."
        cheer_idx = (f_idx - 31) % len(cheer_frames)
        cur_frame = cheer_frames[cheer_idx]
        blush = 0.0  # INSTANTLY 0.0!
        
    # Draw status dot and title
    draw.ellipse([54, 128, 62, 136], fill=status_dot_col)
    draw.text((72, 124), status_title, font=FONT_SANS_BOLD, fill=TEXT_PRIMARY)
    
    # Draw status description
    draw.text((54, 150), status_desc, font=FONT_SANS, fill=TEXT_SECONDARY)
    
    # Feature checklist (clean Anthropic editorial bullets)
    bullets = [
        "Reacts automatically to Claude Code terminal activity",
        "Pet the crown of his head for blushing cheeks",
        "Draggable Wander Zone interval directly on taskbar",
        "AFK sleep mode, coffee breaks, and 15+ animations"
    ]
    by = 210
    for b in bullets:
        draw.text((54, by), "•", font=FONT_SANS, fill=ACCENT_CLAY)
        draw.text((72, by), b, font=FONT_LABEL, fill=TEXT_SECONDARY)
        by += 21
        
    # Footer metadata line
    draw.text((54, 290), "Windows 10 / 11   •   PyQt6 & Win32 API   •   Open Source (MIT)", font=FONT_SMALL, fill=TEXT_MUTED)
    
    # Right Column: Mascot Stage (Pure Minimalist, Flat Charcoal)
    # Subtle floor guideline
    floor_y = stage_y + 128
    draw.line([(stage_x - 20, floor_y), (stage_x + 148, floor_y)], fill=BORDER_SUBTLE, width=1)
    
    # Render sprite at scale 8x
    sprite = render_clawd_sprite(cur_frame, blush_alpha=blush, scale=8)
    sp_x = stage_x
    sp_y = floor_y - sprite.height
    canvas.alpha_composite(sprite, (sp_x, sp_y))
    
    if heart_info:
        hx, hy, ha = heart_info
        canvas.alpha_composite(create_pixel_heart(scale=3, alpha=ha), (hx, hy))
        
    if cursor_pos:
        canvas.alpha_composite(cursor_sprite, cursor_pos)
        
    # Save a preview frame at frame 14 (Claude Code coding) and 28 (blushing)
    if f_idx == 14:
        canvas.save(os.path.join(ASSETS_DIR, "preview_coding.png"), format="PNG")
    if f_idx == 28:
        canvas.save(os.path.join(ASSETS_DIR, "preview_blush.png"), format="PNG")
        
    frames.append(canvas.convert("RGB"))

out_gif = os.path.join(ASSETS_DIR, "banner_animated.gif")
print(f"Saving Minimalist Animated Banner to {out_gif}...")
frames[0].save(
    out_gif,
    save_all=True,
    append_images=frames[1:],
    duration=110,
    loop=0,
    optimize=True
)
print(f"Created {out_gif} ({os.path.getsize(out_gif)} bytes)")


# =========================================================================
# 2. GENERATE FOCUSED PETTING DEMO GIF (assets/petting_demo.gif)
# =========================================================================
print("Generating Minimalist Petting Demo GIF (assets/petting_demo.gif)...")

DEMO_W, DEMO_H = 640, 240
demo_frames = []
DEMO_TOTAL_FRAMES = 32

for f_idx in range(DEMO_TOTAL_FRAMES):
    d_canvas = Image.new("RGBA", (DEMO_W, DEMO_H), BG_COLOR)
    dd = ImageDraw.Draw(d_canvas)
    
    # Header: Anthropic editorial serif
    dd.text((36, 24), "Interactive Petting", font=FONT_HEAD, fill=TEXT_PRIMARY)
    dd.text((195, 26), "—", font=FONT_SANS, fill=TEXT_MUTED)
    dd.text((212, 26), "Stroke above head  •  Instantly clears on animation", font=FONT_SANS, fill=TEXT_SECONDARY)
    
    # Clean separator line
    dd.line([(36, 56), (604, 56)], fill=BORDER_SUBTLE, width=1)
    
    # Taskbar ledge representation (clean minimal flat bar)
    tb_y = 180
    dd.line([(36, tb_y), (604, tb_y)], fill=(60, 60, 58, 255), width=2)
    dd.text((36, tb_y + 8), "Windows Taskbar", font=FONT_SMALL, fill=TEXT_MUTED)
    
    clawd_cx = 320
    clawd_feet_y = tb_y
    
    # Phases:
    # 0..4: Idle
    # 5..18: Petting strictly above head -> cheeks bloom
    # 19..25: Cursor stops -> cheeks start lingering
    # 26..31: Animation triggers -> CHEEKS INSTANTLY DISAPPEAR!
    
    cur_frame = base_img
    blush = 0.0
    cursor_xy = None
    heart_xy = None
    status_msg = "Standby  (waiting for petting above head)"
    status_col = TEXT_MUTED
    
    if f_idx < 5:
        blush = 0.0
        cur_frame = base_img
        status_msg = "Idle on taskbar"
        status_col = TEXT_MUTED
    elif 5 <= f_idx < 19:
        # Petting strictly above head
        p = (f_idx - 5) / 13.0
        blush = min(1.0, p * 1.3)
        cur_frame = base_img
        sway = math.sin((f_idx - 5) * 1.6) * 18
        # Cursor position strictly ABOVE head
        cursor_xy = (int(clawd_cx + sway - 10), int(clawd_feet_y - 75 + math.cos((f_idx-5)*1.6)*4))
        status_msg = f"Stroking crown of head  •  Cheeks blooming ({int(blush*100)}%)"
        status_col = PINK_BLUSH
        if f_idx >= 12:
            hp = (f_idx - 12) / 7.0
            hx = int(clawd_cx + 26)
            hy = int(clawd_feet_y - 85 - hp * 22)
            heart_xy = (hx, hy, int(255 * (1.0 - hp * 0.5)))
    elif 19 <= f_idx < 26:
        # Lingering blush before animation
        blush = 0.9
        cur_frame = base_img
        status_msg = "Petting finished  •  Blush active"
        status_col = PINK_BLUSH
    else:
        # Animation starts: CHEEKS INSTANTLY CLEARED!
        blush = 0.0  # Instant clear!
        cur_frame = cheer_frames[(f_idx - 26) % len(cheer_frames)]
        status_msg = "Animation starts  ->  Cheeks INSTANTLY disappear"
        status_col = GREEN_ACTIVE
        
    # Draw status message
    dd.text((36, 68), status_msg, font=FONT_LABEL, fill=status_col)
    
    # Render sprite at scale 7x
    sp = render_clawd_sprite(cur_frame, blush_alpha=blush, scale=7)
    sx = clawd_cx - (sp.width // 2)
    sy = clawd_feet_y - sp.height
    d_canvas.alpha_composite(sp, (sx, sy))
    
    if heart_xy:
        hx, hy, ha = heart_xy
        d_canvas.alpha_composite(create_pixel_heart(scale=2, alpha=ha), (hx, hy))
        
    if cursor_xy:
        d_canvas.alpha_composite(cursor_sprite, cursor_xy)
        
    demo_frames.append(d_canvas.convert("RGB"))

out_demo = os.path.join(ASSETS_DIR, "petting_demo.gif")
print(f"Saving Minimalist Petting Demo to {out_demo}...")
demo_frames[0].save(
    out_demo,
    save_all=True,
    append_images=demo_frames[1:],
    duration=115,
    loop=0,
    optimize=True
)
print(f"Created {out_demo} ({os.path.getsize(out_demo)} bytes)")


# =========================================================================
# 3. GENERATE ULTRA-MINIMALIST STATIC BANNER (assets/banner.png)
# =========================================================================
print("Generating Minimalist Anthropic-Style Static Banner (assets/banner.png)...")

STATIC_W, STATIC_H = 1200, 360
s_canvas = Image.new("RGBA", (STATIC_W, STATIC_H), BG_COLOR)
sd = ImageDraw.Draw(s_canvas)

# Left Section: Brand & Description (Anthropic Editorial Style)
sd.text((64, 46), "Clawd", font=FONT_TITLE, fill=TEXT_PRIMARY)
sd.text((200, 58), "—", font=FONT_SANS, fill=TEXT_MUTED)
sd.text((220, 56), "Pixel Taskbar Mascot for Windows", font=FONT_TITLE_ITALIC, fill=TEXT_SECONDARY)

sd.line([(64, 110), (580, 110)], fill=BORDER_SUBTLE, width=1)

sd.text((64, 126), "An interactive desktop companion built with PyQt6 and Win32 API.", font=FONT_SANS, fill=TEXT_PRIMARY)
sd.text((64, 150), "Living directly on your taskbar with real-time process awareness,\nwandering zones, head petting reactions, and 15+ living animations.", font=FONT_LABEL, fill=TEXT_SECONDARY)

# Features summary list
features = [
    ("Claude Code Reaction", "Clawd opens his laptop and types in real time during code generation"),
    ("Head Petting & Blush", "Stroke the crown of his head to see pink cheeks; instantly clears on action"),
    ("Wander Zone Interval", "Configurable taskbar zone for gentle roaming without obstructing icons"),
    ("AFK Sleep & Living AI", "Auto-curls up to sleep when idle; wakes up and greets upon mouse return")
]

fy = 196
for f_title, f_desc in features:
    sd.text((64, fy), "•", font=FONT_SANS, fill=ACCENT_CLAY)
    sd.text((80, fy), f_title, font=FONT_SANS_BOLD, fill=TEXT_PRIMARY)
    sd.text((230, fy), f"—  {f_desc}", font=FONT_SMALL, fill=TEXT_SECONDARY)
    fy += 24

sd.text((64, 314), "Windows 10 / 11   •   Python 3.10+   •   0% CPU Usage   •   MIT License", font=FONT_SMALL, fill=TEXT_MUTED)

# Right Section: Two Minimalist Showcases Side-by-Side
# Vertical divider
sd.line([(630, 46), (630, 314)], fill=BORDER_SUBTLE, width=1)

# Showcase 1: Claude Code Active (Laptop Coding)
sh1_cx = 760
sh_floor_y = 205
sd.line([(660, sh_floor_y), (860, sh_floor_y)], fill=(50, 50, 48, 255), width=1)

sp_coding = render_clawd_sprite(laptop_frames[2], blush_alpha=0.0, scale=7)
s_canvas.alpha_composite(sp_coding, (sh1_cx - sp_coding.width // 2, sh_floor_y - sp_coding.height))

# Label for Showcase 1
sd.ellipse([sh1_cx - 50, 224, sh1_cx - 42, 232], fill=GREEN_ACTIVE)
sd.text((sh1_cx - 36, 221), "Claude Code Active", font=FONT_SANS_BOLD, fill=TEXT_PRIMARY)
sd.text((sh1_cx - 65, 240), "Types at laptop during", font=FONT_SMALL, fill=TEXT_SECONDARY)
sd.text((sh1_cx - 65, 254), "code generation & tasks", font=FONT_SMALL, fill=TEXT_MUTED)


# Showcase 2: Head Petting (Blush Cheeks + Cursor Above Head)
sh2_cx = 1010
sd.line([(910, sh_floor_y), (1110, sh_floor_y)], fill=(50, 50, 48, 255), width=1)

sp_pet = render_clawd_sprite(base_img, blush_alpha=1.0, scale=7)
sp_pet_x = sh2_cx - sp_pet.width // 2
sp_pet_y = sh_floor_y - sp_pet.height
s_canvas.alpha_composite(sp_pet, (sp_pet_x, sp_pet_y))

# Cursor strictly above head
s_canvas.alpha_composite(create_pixel_cursor(scale=3), (sh2_cx - 10, sp_pet_y - 12))
s_canvas.alpha_composite(create_pixel_heart(scale=2, alpha=230), (sh2_cx + 24, sp_pet_y - 22))

# Label for Showcase 2
sd.ellipse([sh2_cx - 45, 224, sh2_cx - 37, 232], fill=PINK_BLUSH)
sd.text((sh2_cx - 31, 221), "Head Petting", font=FONT_SANS_BOLD, fill=TEXT_PRIMARY)
sd.text((sh2_cx - 65, 240), "Stroke crown of head", font=FONT_SMALL, fill=TEXT_SECONDARY)
sd.text((sh2_cx - 65, 254), "Instant clear on action", font=FONT_SMALL, fill=TEXT_MUTED)

out_png = os.path.join(ASSETS_DIR, "banner.png")
print(f"Saving Minimalist Static Banner to {out_png}...")
s_canvas.save(out_png, format="PNG")
print(f"Created {out_png} ({os.path.getsize(out_png)} bytes)")


# =========================================================================
# 4. GENERATE ANIMATIONS SHOWCASE GIF (assets/animations_showcase.gif)
# =========================================================================
print("Generating Minimalist Animations Showcase GIF (assets/animations_showcase.gif)...")

SHOW_W, SHOW_H = 880, 240
show_frames = []
SHOW_TOTAL_FRAMES = 32

coffee_frames = load_frames("coffee")
wizard_frames = load_frames("wizard")
sleep_frames = load_frames("sleep")

showcases = [
    ("Coding", laptop_frames, "Claude Code active", False),
    ("Coffee", coffee_frames, "Coffee break", False),
    ("Wizard", wizard_frames, "Magic sparkle", False),
    ("Petting", [base_img], "Blush cheeks", True),
    ("AFK Sleep", sleep_frames, "Auto-sleep", False)
]

col_w = SHOW_W // len(showcases)

for f_idx in range(SHOW_TOTAL_FRAMES):
    c_canvas = Image.new("RGBA", (SHOW_W, SHOW_H), BG_COLOR)
    cd = ImageDraw.Draw(c_canvas)

    # Header
    cd.text((44, 20), "Living Expressions & Behaviors", font=FONT_HEAD, fill=TEXT_PRIMARY)
    cd.text((310, 22), "—", font=FONT_SANS, fill=TEXT_MUTED)
    cd.text((328, 22), "Responsive desktop companions with 15+ animations", font=FONT_SANS, fill=TEXT_SECONDARY)
    cd.line([(44, 50), (SHOW_W - 44, 50)], fill=BORDER_SUBTLE, width=1)

    # Floor guideline
    floor_y = 175
    cd.line([(44, floor_y), (SHOW_W - 44, floor_y)], fill=(50, 50, 48, 255), width=1)

    for i, (title, f_list, subtitle, is_pet) in enumerate(showcases):
        cx = col_w * i + (col_w // 2)

        # Determine frame
        if is_pet:
            frame_img = base_img
            # Petting blush cycle
            blush_lvl = 0.5 + 0.5 * math.sin(f_idx * 0.25)
        else:
            frame_img = f_list[f_idx % len(f_list)]
            blush_lvl = 0.0

        sp = render_clawd_sprite(frame_img, blush_alpha=blush_lvl, scale=6)
        sp_x = cx - sp.width // 2
        sp_y = floor_y - sp.height
        c_canvas.alpha_composite(sp, (sp_x, sp_y))

        if is_pet and blush_lvl > 0.5:
            # Heart float
            ha = int((blush_lvl - 0.5) * 2 * 230)
            c_canvas.alpha_composite(create_pixel_heart(scale=2, alpha=ha), (cx + 18, sp_y - 12))

        # Text labels below floor
        cd.text((cx - 24, floor_y + 10), title, font=FONT_SANS_BOLD, fill=TEXT_PRIMARY)
        cd.text((cx - 36, floor_y + 26), subtitle, font=FONT_SMALL, fill=TEXT_MUTED)

    show_frames.append(c_canvas.convert("RGB"))

out_showcase = os.path.join(ASSETS_DIR, "animations_showcase.gif")
print(f"Saving Animations Showcase GIF to {out_showcase}...")
show_frames[0].save(
    out_showcase,
    save_all=True,
    append_images=show_frames[1:],
    duration=115,
    loop=0,
    optimize=True
)
print(f"Created {out_showcase} ({os.path.getsize(out_showcase)} bytes)")

print("\nAll minimalist Anthropic-style banners generated successfully!")
