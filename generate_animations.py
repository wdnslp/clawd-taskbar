"""
Generates all pixel art animation frames for Claude Taskbar Mascot.
All sprites are strictly 16x16 RGBA PNGs, matching the exact terracotta palette and art style.
Strict character proportion rule: Claude's arms are strictly stubby (2x2 or 2x3 pixels),
never elongated or noodle-like.
Includes 22 high-concept animations.
"""

import os
from PIL import Image

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "animations")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Art Palette ---
T = (0, 0, 0, 0)             # Transparent
C = (218, 119, 88, 255)      # Claude Terracotta Base
CD = (186, 94, 66, 255)      # Claude Dark / Shading / Eyelids
E = (0, 0, 0, 255)           # Eye / Black
W = (255, 255, 255, 255)     # White
R = (235, 65, 65, 255)       # Red (heart)
P = (245, 140, 160, 255)     # Pink (blush)
Y = (255, 215, 0, 255)       # Yellow (gold, spark, cheese)
CY = (80, 220, 240, 255)     # Cyan (screen, cyber visor, energy)
BR = (120, 65, 30, 255)      # Brown / Coffee / Wood
GR = (170, 170, 175, 255)    # Grey (metal, laptop)
DG = (100, 100, 105, 255)    # Dark Grey
G = (40, 220, 60, 255)       # Neon Green (matrix)
GD = (20, 140, 30, 255)      # Dark Green
OR = (255, 120, 0, 255)      # Orange
BL = (60, 130, 245, 255)     # Water / Tears / Magic Blue
PU = (165, 80, 230, 255)     # Purple (wizard hat)
CH = (255, 210, 30, 255)     # Gold / Shield Glow

def make_empty_grid():
    return [[T for _ in range(16)] for _ in range(16)]

def save_frame(grid, anim_name, frame_idx):
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    for y in range(16):
        for x in range(16):
            img.putpixel((x, y), grid[y][x])
    filename = f"{anim_name}_{frame_idx:02d}.png"
    filepath = os.path.join(OUTPUT_DIR, filename)
    img.save(filepath)
    return filepath

def get_base_grid():
    g = make_empty_grid()
    # Row 4: head top
    for x in range(4, 12):
        g[4][x] = C
    # Row 5: eyes
    for x in range(4, 12):
        g[5][x] = C
    g[5][5] = E
    g[5][10] = E
    # Rows 6-7: shoulders & stubby arms down
    for y in (6, 7):
        for x in range(2, 14):
            g[y][x] = C
    # Rows 8-9: torso
    for y in (8, 9):
        for x in range(4, 12):
            g[y][x] = C
    # Rows 10-11: 4 stubby legs
    for y in (10, 11):
        g[y][4] = C
        g[y][6] = C
        g[y][9] = C
        g[y][11] = C
    return g

# ==========================================
# 1. Blink (Моргание)
# ==========================================
def gen_blink():
    f0 = get_base_grid()
    save_frame(f0, "blink", 0)

    f1 = get_base_grid()
    f1[5][5] = CD
    f1[5][10] = CD
    save_frame(f1, "blink", 1)

    f2 = get_base_grid()
    f2[5][5] = C; f2[5][10] = C
    f2[5][4] = CD; f2[5][5] = CD
    f2[5][9] = CD; f2[5][10] = CD
    save_frame(f2, "blink", 2)

    save_frame(f0, "blink", 3)

# ==========================================
# 2. Look Around (Оглядывается)
# ==========================================
def gen_look_around():
    f_base = get_base_grid()
    save_frame(f_base, "look_around", 0)

    f_left = get_base_grid()
    f_left[5][5] = C; f_left[5][10] = C
    f_left[5][4] = E; f_left[5][9] = E
    save_frame(f_left, "look_around", 1)
    save_frame(f_left, "look_around", 2)

    save_frame(f_base, "look_around", 3)

    f_right = get_base_grid()
    f_right[5][5] = C; f_right[5][10] = C
    f_right[5][6] = E; f_right[5][11] = E
    save_frame(f_right, "look_around", 4)
    save_frame(f_right, "look_around", 5)

    save_frame(f_base, "look_around", 6)

# ==========================================
# 3. Wave (Машет рукой — строго короткая лапка)
# ==========================================
def gen_wave():
    f0 = get_base_grid()
    save_frame(f0, "wave", 0)

    # Arm raised slightly (still stubby 2px, at row 5 col 12-13)
    f1 = get_base_grid()
    f1[7][12] = T; f1[7][13] = T
    f1[5][12] = C; f1[5][13] = C
    save_frame(f1, "wave", 1)

    # Wave up 1px (row 4 col 12-13, no stretching!)
    f2 = get_base_grid()
    f2[7][12] = T; f2[7][13] = T
    f2[6][12] = T; f2[6][13] = T
    f2[4][12] = C; f2[4][13] = C
    f2[5][12] = C; f2[5][13] = C
    save_frame(f2, "wave", 2)

    save_frame(f1, "wave", 3)
    save_frame(f2, "wave", 4)
    save_frame(f1, "wave", 5)
    save_frame(f0, "wave", 6)

# ==========================================
# 4. Cheer (Радость — короткие лапки вверх)
# ==========================================
def gen_cheer():
    f0 = get_base_grid()
    save_frame(f0, "cheer", 0)

    # Both stubby arms up (stay within cols 2-3 and 12-13, no elongation!)
    f1 = get_base_grid()
    f1[7][2] = T; f1[7][3] = T
    f1[5][2] = C; f1[5][3] = C
    f1[7][12] = T; f1[7][13] = T
    f1[5][12] = C; f1[5][13] = C
    save_frame(f1, "cheer", 1)

    # Hop up 1px, eyes happy ^ ^
    f2 = make_empty_grid()
    base = get_base_grid()
    for y in range(4, 12):
        for x in range(16):
            f2[y - 1][x] = base[y][x]
    f2[6][2] = T; f2[6][3] = T
    f2[6][12] = T; f2[6][13] = T
    f2[4][2] = C; f2[4][3] = C
    f2[4][12] = C; f2[4][13] = C
    f2[4][5] = CD; f2[4][10] = CD
    save_frame(f2, "cheer", 2)

    save_frame(f1, "cheer", 3)
    save_frame(f2, "cheer", 4)
    save_frame(f1, "cheer", 5)
    save_frame(f0, "cheer", 6)

# ==========================================
# 5. Jump (Радостный прыжок)
# ==========================================
def gen_jump():
    f0 = get_base_grid()
    save_frame(f0, "jump", 0)

    base = get_base_grid()
    f_squash = make_empty_grid()
    for y in range(4, 12):
        for x in range(16):
            if y < 11:
                f_squash[y + 1][x] = base[y][x]
    save_frame(f_squash, "jump", 1)

    f_up2 = make_empty_grid()
    for y in range(4, 12):
        for x in range(16):
            f_up2[y - 2][x] = base[y][x]
    save_frame(f_up2, "jump", 2)

    f_apex = make_empty_grid()
    for y in range(4, 12):
        for x in range(16):
            f_apex[y - 3][x] = base[y][x]
    save_frame(f_apex, "jump", 3)

    f_down1 = make_empty_grid()
    for y in range(4, 12):
        for x in range(16):
            f_down1[y - 1][x] = base[y][x]
    save_frame(f_down1, "jump", 4)

    save_frame(f_squash, "jump", 5)
    save_frame(f0, "jump", 6)

# ==========================================
# 6. Dance (Аккуратный танец — руки НЕ удлиняются)
# ==========================================
def gen_dance():
    base = get_base_grid()

    # Step left: body shifts 1px left, arms remain strictly compact 2px!
    f_left = make_empty_grid()
    for y in range(4, 12):
        for x in range(1, 15):
            f_left[y][x] = base[y][x + 1]
    # Legs bounce
    f_left[11][5] = T
    save_frame(f_left, "dance", 0)

    # Center bob
    save_frame(base, "dance", 1)

    # Step right: body shifts 1px right, arms strictly compact!
    f_right = make_empty_grid()
    for y in range(4, 12):
        for x in range(1, 15):
            f_right[y][x] = base[y][x - 1]
    f_right[11][10] = T
    save_frame(f_right, "dance", 2)

    # Center bob
    save_frame(base, "dance", 3)

# ==========================================
# 7. Sleep (Дремлет и храпит)
# ==========================================
def gen_sleep():
    f_sleep_base = get_base_grid()
    f_sleep_base[5][5] = C; f_sleep_base[5][10] = C
    f_sleep_base[5][4] = CD; f_sleep_base[5][5] = CD
    f_sleep_base[5][9] = CD; f_sleep_base[5][10] = CD

    save_frame(f_sleep_base, "sleep", 0)

    f1 = [row[:] for row in f_sleep_base]
    f1[2][12] = W; f1[2][13] = W
    f1[3][13] = W; f1[3][12] = W
    save_frame(f1, "sleep", 1)

    f2 = [row[:] for row in f_sleep_base]
    f2[1][13] = W; f2[1][14] = W
    f2[3][11] = CY; f2[3][12] = CY; f2[3][13] = CY
    f2[4][12] = CY; f2[4][11] = CY; f2[4][13] = CY
    save_frame(f2, "sleep", 2)

    f3 = [row[:] for row in f_sleep_base]
    f3[0][13] = W; f3[0][14] = W
    f3[1][10] = CY; f3[1][11] = CY; f3[1][12] = CY
    f3[2][11] = CY; f3[3][10] = CY; f3[3][11] = CY; f3[3][12] = CY
    save_frame(f3, "sleep", 3)

    save_frame(f_sleep_base, "sleep", 4)

# ==========================================
# 8. Heart (Любовь и сердечко)
# ==========================================
def gen_heart():
    base = get_base_grid()
    f_blush = [row[:] for row in base]
    f_blush[6][4] = P; f_blush[6][11] = P
    save_frame(f_blush, "heart", 0)

    f1 = [row[:] for row in f_blush]
    f1[2][7] = R; f1[2][8] = R
    f1[3][7] = R; f1[3][8] = R
    save_frame(f1, "heart", 1)

    f2 = [row[:] for row in f_blush]
    f2[0][6] = R; f2[0][7] = R; f2[0][8] = R; f2[0][9] = R
    f2[1][5] = R; f2[1][6] = W; f2[1][7] = R; f2[1][8] = R; f2[1][9] = R; f2[1][10] = R
    f2[2][6] = R; f2[2][7] = R; f2[2][8] = R; f2[2][9] = R
    f2[3][7] = R; f2[3][8] = R
    f2[5][5] = CD; f2[5][10] = CD
    save_frame(f2, "heart", 2)

    f3 = [row[:] for row in f2]
    f3[0][4] = Y; f3[2][11] = Y
    save_frame(f3, "heart", 3)

    save_frame(f1, "heart", 4)
    save_frame(base, "heart", 5)

# ==========================================
# 9. Coffee (Пьёт кофе)
# ==========================================
def gen_coffee():
    base = get_base_grid()
    f1 = [row[:] for row in base]
    f1[7][12] = W; f1[7][13] = BR; f1[7][14] = W
    f1[8][12] = W; f1[8][13] = W;  f1[8][14] = W
    save_frame(f1, "coffee", 0)

    f2 = [row[:] for row in f1]
    f2[6][13] = W; f2[5][14] = W
    save_frame(f2, "coffee", 1)

    f3 = [row[:] for row in base]
    f3[6][10] = W; f3[6][11] = BR; f3[6][12] = W
    f3[7][10] = W; f3[7][11] = W;  f3[7][12] = W
    f3[5][5] = CD; f3[5][10] = CD
    save_frame(f3, "coffee", 2)

    save_frame(f2, "coffee", 3)
    save_frame(base, "coffee", 4)

# ==========================================
# 10. Idea (Осенила идея / Лампочка)
# ==========================================
def gen_idea():
    base = get_base_grid()
    f_look = [row[:] for row in base]
    f_look[5][5] = C; f_look[5][10] = C
    f_look[4][5] = E; f_look[4][10] = E
    save_frame(f_look, "idea", 0)

    f1 = [row[:] for row in f_look]
    f1[2][7] = Y; f1[2][8] = Y
    save_frame(f1, "idea", 1)

    f2 = [row[:] for row in f_look]
    f2[0][7] = Y; f2[0][8] = Y
    f2[1][6] = Y; f2[1][7] = W; f2[1][8] = Y; f2[1][9] = Y
    f2[2][7] = Y; f2[2][8] = Y
    f2[3][7] = GR; f2[3][8] = GR
    save_frame(f2, "idea", 2)

    f3 = [row[:] for row in f2]
    f3[0][4] = Y; f3[0][11] = Y
    f3[2][4] = Y; f3[2][11] = Y
    f3[1][7] = W; f3[1][8] = W
    f3[4][5] = C; f3[4][10] = C
    f3[5][5] = E; f3[5][10] = E
    f3[5][4] = E; f3[5][11] = E
    save_frame(f3, "idea", 3)

    save_frame(f2, "idea", 4)
    save_frame(base, "idea", 5)

# ==========================================
# 11. Typing (Ноутбук — Длинная, богатая анимация)
# ==========================================
def gen_typing():
    base = get_base_grid()

    def get_laptop_base():
        f = [row[:] for row in base]
        # Laptop screen (cols 12-14, rows 7-8)
        f[7][13] = GR; f[7][14] = GR
        f[8][13] = CY; f[8][14] = GR
        # Laptop keyboard base (cols 10-13, row 9)
        f[9][11] = GR; f[9][12] = GR; f[9][13] = GR
        return f

    # 0: Opens laptop, screen powers on
    f0 = get_laptop_base()
    f0[8][13] = DG  # dark screen turning on
    save_frame(f0, "typing", 0)

    # 1: Screen glows cyan, ready to code
    f1 = get_laptop_base()
    save_frame(f1, "typing", 1)

    # 2: Left hand keystroke
    f2 = get_laptop_base()
    f2[8][11] = C   # short tap
    f2[8][13] = W   # cursor flash
    save_frame(f2, "typing", 2)

    # 3: Right hand keystroke
    f3 = get_laptop_base()
    f3[8][12] = C
    f3[7][13] = CY
    save_frame(f3, "typing", 3)

    # 4: Both hands active coding
    f4 = get_laptop_base()
    f4[8][11] = C; f4[8][12] = C
    f4[8][13] = CY; f4[7][13] = W
    save_frame(f4, "typing", 4)

    # 5: Code scrolling on screen
    f5 = get_laptop_base()
    f5[7][13] = G; f5[8][13] = CY
    save_frame(f5, "typing", 5)

    # 6: Thinking pause (hand on chin, eyes look at code)
    f6 = get_laptop_base()
    f6[7][10] = C  # short paw touches chin
    f6[5][5] = CD; f6[5][10] = E
    save_frame(f6, "typing", 6)

    # 7: Hacker burst 1!
    f7 = get_laptop_base()
    f7[8][11] = C
    f7[7][13] = W; f7[8][13] = W
    save_frame(f7, "typing", 7)

    # 8: Hacker burst 2!
    f8 = get_laptop_base()
    f8[8][12] = C
    f8[7][13] = CY; f8[8][13] = CY
    save_frame(f8, "typing", 8)

    # 9: Compiling... (yellow blink)
    f9 = get_laptop_base()
    f9[7][13] = Y; f9[8][13] = Y
    save_frame(f9, "typing", 9)

    # 10: BUILD SUCCESS! Screen bright green, happy eyes!
    f10 = get_laptop_base()
    f10[7][13] = G; f10[8][13] = G
    f10[5][5] = CD; f10[5][10] = CD  # happy eyes
    f10[6][4] = P; f10[6][11] = P    # blush
    save_frame(f10, "typing", 10)

    # 11: Satisfied completion
    save_frame(f1, "typing", 11)

# ==========================================
# 12. Spin (Крутится 360°)
# ==========================================
def gen_spin():
    base = get_base_grid()
    save_frame(base, "spin", 0)

    f_34r = make_empty_grid()
    for y in range(4, 12):
        for x in range(5, 12):
            f_34r[y][x] = C
    f_34r[5][9] = E
    f_34r[6][12] = C; f_34r[7][12] = C
    for y in (10, 11):
        f_34r[y][6] = C; f_34r[y][9] = C
    save_frame(f_34r, "spin", 1)

    f_side = make_empty_grid()
    for y in range(4, 10):
        for x in range(6, 10):
            f_side[y][x] = C
    f_side[5][8] = E
    for y in (10, 11):
        f_side[y][7] = C; f_side[y][8] = C
    save_frame(f_side, "spin", 2)

    f_back = make_empty_grid()
    for y in range(4, 10):
        for x in range(4, 12):
            f_back[y][x] = C
    for y in (6, 7):
        f_back[y][2] = C; f_back[y][3] = C
        f_back[y][12] = C; f_back[y][13] = C
    for y in (10, 11):
        f_back[y][4] = C; f_back[y][6] = C
        f_back[y][9] = C; f_back[y][11] = C
    save_frame(f_back, "spin", 3)

    f_side_l = make_empty_grid()
    for y in range(4, 10):
        for x in range(6, 10):
            f_side_l[y][x] = C
    f_side_l[5][7] = E
    for y in (10, 11):
        f_side_l[y][7] = C; f_side_l[y][8] = C
    save_frame(f_side_l, "spin", 4)

    f_34l = make_empty_grid()
    for y in range(4, 12):
        for x in range(4, 11):
            f_34l[y][x] = C
    f_34l[5][6] = E
    f_34l[6][3] = C; f_34l[7][3] = C
    for y in (10, 11):
        f_34l[y][6] = C; f_34l[y][9] = C
    save_frame(f_34l, "spin", 5)

    save_frame(base, "spin", 6)

# ==========================================
# 13. Peek (Прячется за панель)
# ==========================================
def gen_peek():
    base = get_base_grid()
    save_frame(base, "peek", 0)

    f_down2 = make_empty_grid()
    for y in range(4, 14):
        for x in range(16):
            if y + 2 < 16:
                f_down2[y + 2][x] = base[y][x]
    save_frame(f_down2, "peek", 1)

    f_down4 = make_empty_grid()
    for y in range(4, 12):
        for x in range(16):
            if y + 4 < 16:
                f_down4[y + 4][x] = base[y][x]
    save_frame(f_down4, "peek", 2)

    f_peek_l = [row[:] for row in f_down4]
    f_peek_l[9][5] = C; f_peek_l[9][10] = C
    f_peek_l[9][4] = E; f_peek_l[9][9] = E
    save_frame(f_peek_l, "peek", 3)

    f_peek_r = [row[:] for row in f_down4]
    f_peek_r[9][5] = C; f_peek_r[9][10] = C
    f_peek_r[9][6] = E; f_peek_r[9][11] = E
    save_frame(f_peek_r, "peek", 4)

    save_frame(f_down2, "peek", 5)
    save_frame(base, "peek", 6)

# ==========================================
# 14. Question (Знак вопроса)
# ==========================================
def gen_question():
    base = get_base_grid()
    f1 = [row[:] for row in base]
    f1[5][5] = E; f1[5][10] = CD
    save_frame(f1, "question", 0)

    f2 = [row[:] for row in f1]
    f2[0][8] = Y; f2[0][9] = Y
    f2[1][10] = Y; f2[2][9] = Y; f2[3][9] = Y
    save_frame(f2, "question", 1)

    f3 = [row[:] for row in f2]
    f3[0][8] = W; f3[0][9] = Y
    save_frame(f3, "question", 2)

    save_frame(f1, "question", 3)
    save_frame(base, "question", 4)

# ==========================================
# 15. Matrix (Хакер / Цифровой дождь)
# ==========================================
def gen_matrix():
    base = get_base_grid()
    f0 = [row[:] for row in base]
    f0[0][2] = G; f0[0][8] = G; f0[0][13] = G
    f0[1][8] = GD
    save_frame(f0, "matrix", 0)

    f1 = [row[:] for row in base]
    f1[1][2] = G; f1[2][2] = GD
    f1[2][8] = G; f1[3][8] = GD
    f1[1][13] = G; f1[2][13] = GD
    for x in range(4, 12):
        f1[5][x] = GD
    f1[5][5] = G; f1[5][10] = G
    save_frame(f1, "matrix", 1)

    f2 = [row[:] for row in base]
    f2[0][5] = G; f2[1][5] = GD
    f2[2][1] = G; f2[3][1] = GD
    f2[3][11] = G; f2[4][11] = GD
    f2[2][14] = G; f2[3][14] = GD
    for x in range(3, 13):
        f2[5][x] = G
    f2[5][5] = W; f2[5][10] = W
    save_frame(f2, "matrix", 2)

    f3 = [row[:] for row in base]
    f3[1][1] = GD; f3[3][5] = G; f3[4][5] = GD
    f3[0][9] = G; f3[1][9] = GD; f3[2][9] = G
    f3[4][14] = G; f3[5][14] = GD
    for x in range(3, 13):
        f3[5][x] = G
    f3[5][6] = W; f3[5][9] = W
    save_frame(f3, "matrix", 3)

    f4 = [row[:] for row in base]
    f4[5][2] = GD; f4[6][8] = GD; f4[7][13] = GD
    save_frame(f4, "matrix", 4)
    save_frame(base, "matrix", 5)

# ==========================================
# 16. Pizza (Кушает пиццу — аккуратная лапка)
# ==========================================
def gen_pizza():
    base = get_base_grid()
    f0 = [row[:] for row in base]
    f0[6][14] = BR; f0[7][14] = BR
    f0[7][12] = CH; f0[7][13] = CH; f0[8][11] = CH
    f0[7][13] = R
    save_frame(f0, "pizza", 0)

    f1 = [row[:] for row in base]
    f1[6][9] = CH; f1[6][10] = R; f1[7][8] = CH; f1[7][9] = CH; f1[6][11] = BR
    f1[7][6] = E; f1[7][7] = E
    save_frame(f1, "pizza", 1)

    f2 = [row[:] for row in base]
    f2[5][5] = CD; f2[5][10] = CD
    f2[7][7] = Y; f2[7][8] = Y; f2[7][9] = CH; f2[7][10] = CH; f2[6][11] = BR
    f2[6][6] = P; f2[6][9] = P
    save_frame(f2, "pizza", 2)

    f3 = [row[:] for row in base]
    f3[5][5] = CD; f3[5][10] = CD
    f3[6][4] = P; f3[6][11] = P
    f3[1][7] = R; f3[1][8] = R; f3[2][7] = R; f3[2][8] = R
    save_frame(f3, "pizza", 3)

    save_frame(base, "pizza", 4)

# ==========================================
# 17. Wizard (Волшебник)
# ==========================================
def gen_wizard():
    base = get_base_grid()
    f0 = [row[:] for row in base]
    f0[3][3] = PU; f0[3][4] = PU; f0[3][11] = PU; f0[3][12] = PU
    for x in range(4, 12):
        f0[3][x] = PU
    f0[2][5] = PU; f0[2][6] = Y; f0[2][7] = PU; f0[2][8] = PU; f0[2][9] = PU; f0[2][10] = PU
    f0[1][6] = PU; f0[1][7] = PU; f0[1][8] = PU
    f0[0][7] = PU; f0[0][8] = Y
    save_frame(f0, "wizard", 0)

    f1 = [row[:] for row in f0]
    f1[6][12] = BR; f1[5][12] = Y  # wand held neatly at shoulder
    save_frame(f1, "wizard", 1)

    f2 = [row[:] for row in f0]
    f2[5][11] = BR; f2[4][10] = Y
    f2[1][10] = CY; f2[2][12] = BL; f2[1][13] = Y; f2[0][11] = W
    save_frame(f2, "wizard", 2)

    f3 = [row[:] for row in f0]
    f3[1][3] = Y; f3[2][1] = PU; f3[3][2] = CY
    f3[1][12] = Y; f3[2][14] = BL; f3[3][13] = W
    f3[5][5] = CY; f3[5][10] = CY
    save_frame(f3, "wizard", 3)

    f4 = [row[:] for row in f0]
    f4[4][4] = Y; f4[6][1] = PU; f4[7][14] = CY
    save_frame(f4, "wizard", 4)
    save_frame(base, "wizard", 5)

# ==========================================
# 18. Workout (Качалка)
# ==========================================
def gen_workout():
    base = get_base_grid()
    f0 = [row[:] for row in base]
    for x in range(2, 14):
        f0[10][x] = GR
    f0[9][1] = DG; f0[10][1] = DG; f0[11][1] = DG
    f0[9][14] = DG; f0[10][14] = DG; f0[11][14] = DG
    save_frame(f0, "workout", 0)

    f1 = [row[:] for row in f0]
    f1[10][4] = C; f1[10][11] = C
    save_frame(f1, "workout", 1)

    f2 = [row[:] for row in base]
    for x in range(2, 14):
        f2[7][x] = GR
    f2[6][1] = DG; f2[7][1] = DG; f2[8][1] = DG
    f2[6][14] = DG; f2[7][14] = DG; f2[8][14] = DG
    f2[5][5] = CD; f2[5][10] = CD; f2[4][12] = CY
    save_frame(f2, "workout", 2)

    f3 = [row[:] for row in base]
    for x in range(2, 14):
        f3[1][x] = GR
    f3[0][1] = DG; f3[1][1] = DG; f3[2][1] = DG
    f3[0][14] = DG; f3[1][14] = DG; f3[2][14] = DG
    f3[3][3] = C; f3[2][3] = C; f3[3][12] = C; f3[2][12] = C
    f3[4][5] = CD; f3[4][10] = CD
    save_frame(f3, "workout", 3)

    f4 = [row[:] for row in f3]
    f4[4][5] = E; f4[4][10] = E
    f4[3][1] = Y; f4[3][14] = Y
    save_frame(f4, "workout", 4)
    save_frame(base, "workout", 5)

# ==========================================
# 19. Cry (Аниме-плач)
# ==========================================
def gen_cry():
    base = get_base_grid()
    f0 = [row[:] for row in base]
    f0[5][5] = CD; f0[5][10] = CD
    f0[7][7] = CD; f0[7][8] = CD
    save_frame(f0, "cry", 0)

    f1 = [row[:] for row in f0]
    f1[6][5] = BL; f1[6][10] = BL
    save_frame(f1, "cry", 1)

    f2 = [row[:] for row in f0]
    f2[5][4] = BL; f2[4][3] = BL; f2[4][2] = BL; f2[5][1] = BL
    f2[5][11] = BL; f2[4][12] = BL; f2[4][13] = BL; f2[5][14] = BL
    save_frame(f2, "cry", 2)

    f3 = [row[:] for row in f0]
    f3[5][3] = BL; f3[4][2] = BL; f3[5][1] = BL
    f3[5][12] = BL; f3[4][13] = BL; f3[5][14] = BL
    save_frame(f3, "cry", 3)

    save_frame(f0, "cry", 4)
    save_frame(base, "cry", 5)

# ==========================================
# 20. Spark (Фирменная искра Claude / AI Spark) - NEW
# ==========================================
def gen_spark():
    base = get_base_grid()
    # 0: Attentive look
    save_frame(base, "spark", 0)

    # 1: Eyes glint gold
    f1 = [row[:] for row in base]
    f1[5][5] = Y; f1[5][10] = Y
    save_frame(f1, "spark", 1)

    # 2: Tiny golden spark appears
    f2 = [row[:] for row in base]
    f2[6][13] = Y
    save_frame(f2, "spark", 2)

    # 3: Spark blooms into radiant 4-pointed Claude star
    f3 = [row[:] for row in base]
    f3[4][13] = Y
    f3[5][12] = Y; f3[5][13] = W; f3[5][14] = Y
    f3[6][13] = Y
    save_frame(f3, "spark", 3)

    # 4: Spark shines brightly with aura
    f4 = [row[:] for row in base]
    f4[3][13] = Y; f4[7][13] = Y
    f4[5][11] = Y; f4[5][15] = Y
    f4[4][13] = W; f4[6][13] = W; f4[5][12] = W; f4[5][14] = W
    f4[5][13] = W
    # Happy eyes ^ ^
    f4[5][5] = CD; f4[5][10] = CD
    save_frame(f4, "spark", 4)

    # 5: Spark ascends gently, golden particles
    f5 = [row[:] for row in base]
    f5[2][13] = W; f5[1][13] = Y; f5[3][13] = Y; f5[2][12] = Y; f5[2][14] = Y
    f5[4][12] = CH; f5[4][14] = CH
    save_frame(f5, "spark", 5)

    # 6: Warm fade
    f6 = [row[:] for row in base]
    f6[1][13] = Y
    save_frame(f6, "spark", 6)
    save_frame(base, "spark", 7)

# ==========================================
# 22. Chat (Генерация ответа `...` Bubble) - NEW
# ==========================================
def gen_chat():
    base = get_base_grid()
    # 0: Thought bubble begins
    f0 = [row[:] for row in base]
    f0[3][11] = W; f0[3][12] = W
    save_frame(f0, "chat", 0)

    # 1: Bubble with 1st dot
    f1 = [row[:] for row in base]
    # Bubble outline (rows 0-2, cols 8-14)
    for x in range(9, 14):
        f1[0][x] = W; f1[2][x] = W
    f1[1][8] = W; f1[1][14] = W; f1[3][11] = W
    f1[1][10] = DG  # dot 1
    save_frame(f1, "chat", 1)

    # 2: Bubble with 2 dots
    f2 = [row[:] for row in f1]
    f2[1][11] = DG  # dot 2
    f2[5][5] = E; f2[5][10] = CD  # thinking head tilt
    save_frame(f2, "chat", 2)

    # 3: Bubble with 3 dots (...)
    f3 = [row[:] for row in f2]
    f3[1][12] = DG  # dot 3
    save_frame(f3, "chat", 3)

    # 4: POP! Intelligent idea burst
    f4 = [row[:] for row in base]
    f4[1][11] = Y; f4[0][11] = W; f4[2][11] = W; f4[1][10] = Y; f4[1][12] = Y
    f4[5][5] = W; f4[5][10] = W  # bright eyes
    save_frame(f4, "chat", 4)

    # 5: Return to base with smile
    save_frame(base, "chat", 5)

# ==========================================
# 22. Shield (Защитный купол / AI Safety) - NEW
# ==========================================
def gen_shield():
    base = get_base_grid()
    # 0: Determined stance
    save_frame(base, "shield", 0)

    # 1: Hex shield activates around perimeter
    f1 = [row[:] for row in base]
    f1[3][7] = CY; f1[3][8] = CY
    f1[7][1] = CY; f1[7][14] = CY
    save_frame(f1, "shield", 1)

    # 2: Full glowing energy shield dome
    f2 = [row[:] for row in base]
    for x in range(5, 11):
        f2[2][x] = CY
    f2[3][4] = CY; f2[3][11] = CY
    f2[4][3] = CY; f2[4][12] = CY
    for y in range(5, 10):
        f2[y][1] = CY; f2[y][14] = CY
    f2[10][2] = CY; f2[10][13] = CY
    save_frame(f2, "shield", 2)

    # 3: Shield deflects rogue pixel with golden spark
    f3 = [row[:] for row in f2]
    f3[5][14] = W; f3[4][14] = Y; f3[6][14] = Y  # spark!
    f3[5][15] = R                                # rogue particle bounced
    save_frame(f3, "shield", 3)

    # 4: Soft protective pulse
    f4 = [row[:] for row in f2]
    f4[2][7] = W; f4[2][8] = W
    save_frame(f4, "shield", 4)

    # 5: Dissolves away
    save_frame(f1, "shield", 5)
    save_frame(base, "shield", 6)

# ==========================================
# Main: Run all generators (22 Animations)
# ==========================================
def main():
    print("Generating pixel art animation frames for 22 Claude animations...")
    # Classic & Core
    gen_blink()
    gen_look_around()
    gen_wave()
    gen_cheer()
    gen_jump()
    gen_dance()
    gen_sleep()
    gen_heart()
    gen_coffee()
    gen_idea()
    gen_typing()       # Long, rich 12-frame coding session!
    gen_spin()
    gen_peek()
    gen_question()
    gen_matrix()
    gen_pizza()
    gen_wizard()
    gen_workout()
    gen_cry()

    # Conceptual Claude Animations
    gen_spark()
    gen_chat()
    gen_shield()

    count = len([f for f in os.listdir(OUTPUT_DIR) if f.endswith(".png")])
    print(f"Successfully generated {count} animation frames across 22 animations in {OUTPUT_DIR}!")

if __name__ == "__main__":
    main()

