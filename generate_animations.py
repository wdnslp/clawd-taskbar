"""
Generates all pixel art animation frames for Claude Taskbar Mascot.
All sprites are strictly 16x16 RGBA PNGs, matching the exact terracotta palette and art style.
Includes 32 unique animations: classic actions, emotions, gaming, tech, and meme reactions!
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
R = (235, 65, 65, 255)       # Red (heart, cape, guitar)
P = (245, 140, 160, 255)     # Pink (blush, cat ears)
Y = (255, 215, 0, 255)       # Yellow (gold, stars, cheese, lightbulb)
CY = (80, 220, 240, 255)     # Cyan (screen, sweat, tech, magic)
BR = (120, 65, 30, 255)      # Brown / Coffee / Wood / Leather
GR = (170, 170, 175, 255)    # Grey (metal, laptop, weights)
DG = (100, 100, 105, 255)    # Dark Grey
G = (40, 220, 60, 255)       # Matrix Neon Green
GD = (20, 140, 30, 255)      # Matrix Dark Green
OR = (255, 120, 0, 255)      # Fire / Crust Orange / Cat Fur
BL = (60, 130, 245, 255)     # Water / Tears / Magic Blue
PU = (165, 80, 230, 255)     # Wizard Purple
CH = (255, 210, 30, 255)     # Cheese Yellow

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
    # Rows 6-7: shoulders & arms down
    for y in (6, 7):
        for x in range(2, 14):
            g[y][x] = C
    # Rows 8-9: torso
    for y in (8, 9):
        for x in range(4, 12):
            g[y][x] = C
    # Rows 10-11: 4 legs
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
    f2[5][5] = C
    f2[5][10] = C
    f2[5][4] = CD
    f2[5][5] = CD
    f2[5][9] = CD
    f2[5][10] = CD
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
# 3. Wave (Машет правой рукой)
# ==========================================
def gen_wave():
    f0 = get_base_grid()
    save_frame(f0, "wave", 0)

    f1 = get_base_grid()
    f1[7][12] = T; f1[7][13] = T
    f1[5][12] = C; f1[5][13] = C
    save_frame(f1, "wave", 1)

    f2 = get_base_grid()
    f2[7][12] = T; f2[7][13] = T
    f2[6][12] = T; f2[6][13] = T
    f2[4][13] = C; f2[4][14] = C
    f2[5][12] = C; f2[5][13] = C
    save_frame(f2, "wave", 2)

    save_frame(f1, "wave", 3)
    save_frame(f2, "wave", 4)
    save_frame(f1, "wave", 5)
    save_frame(f0, "wave", 6)

# ==========================================
# 4. Cheer (Радость / Обе руки вверх)
# ==========================================
def gen_cheer():
    f0 = get_base_grid()
    save_frame(f0, "cheer", 0)

    f1 = get_base_grid()
    f1[7][2] = T; f1[7][3] = T
    f1[5][2] = C; f1[5][3] = C
    f1[7][12] = T; f1[7][13] = T
    f1[5][12] = C; f1[5][13] = C
    save_frame(f1, "cheer", 1)

    f2 = make_empty_grid()
    base = get_base_grid()
    for y in range(4, 12):
        for x in range(16):
            f2[y - 1][x] = base[y][x]
    f2[6][2] = T; f2[6][3] = T
    f2[6][12] = T; f2[6][13] = T
    f2[3][1] = C; f2[3][2] = C; f2[4][2] = C; f2[4][3] = C
    f2[3][13] = C; f2[3][14] = C; f2[4][12] = C; f2[4][13] = C
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
    f_squash[7][1] = C; f_squash[7][14] = C
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
    f_apex[4][2] = T; f_apex[4][13] = T
    f_apex[2][2] = C; f_apex[2][13] = C
    save_frame(f_apex, "jump", 3)

    f_down1 = make_empty_grid()
    for y in range(4, 12):
        for x in range(16):
            f_down1[y - 1][x] = base[y][x]
    save_frame(f_down1, "jump", 4)

    save_frame(f_squash, "jump", 5)
    save_frame(f0, "jump", 6)

# ==========================================
# 6. Dance (Весёлый танец)
# ==========================================
def gen_dance():
    base = get_base_grid()

    f_left = make_empty_grid()
    for y in range(4, 12):
        for x in range(1, 15):
            f_left[y][x] = base[y][x + 1]
    f_left[5][12] = C; f_left[5][13] = C
    f_left[7][12] = T
    save_frame(f_left, "dance", 0)

    save_frame(base, "dance", 1)

    f_right = make_empty_grid()
    for y in range(4, 12):
        for x in range(1, 15):
            f_right[y][x] = base[y][x - 1]
    f_right[5][2] = C; f_right[5][3] = C
    f_right[7][3] = T
    save_frame(f_right, "dance", 2)

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
# 11. Typing (Кодит за ноутом)
# ==========================================
def gen_typing():
    base = get_base_grid()
    f0 = [row[:] for row in base]
    f0[7][13] = GR; f0[7][14] = GR
    f0[8][13] = CY; f0[8][14] = GR
    f0[9][11] = GR; f0[9][12] = GR; f0[9][13] = GR
    f0[10][11] = DG; f0[10][12] = DG
    save_frame(f0, "typing", 0)

    f1 = [row[:] for row in f0]
    f1[8][11] = C; f1[8][13] = W
    save_frame(f1, "typing", 1)

    f2 = [row[:] for row in f0]
    f2[8][12] = C; f2[7][13] = CY
    save_frame(f2, "typing", 2)

    f3 = [row[:] for row in f0]
    f3[8][11] = C; f3[8][12] = C
    f3[8][13] = CY; f3[7][13] = W
    save_frame(f3, "typing", 3)

    save_frame(f1, "typing", 4)
    save_frame(f2, "typing", 5)

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
# 14. Yawn (Зевает)
# ==========================================
def gen_yawn():
    base = get_base_grid()
    save_frame(base, "yawn", 0)

    f1 = [row[:] for row in base]
    f1[5][5] = CD; f1[5][10] = CD
    f1[7][7] = E; f1[7][8] = E
    save_frame(f1, "yawn", 1)

    f2 = [row[:] for row in base]
    f2[5][5] = CD; f2[5][10] = CD
    f2[7][7] = E; f2[7][8] = E
    f2[8][7] = E; f2[8][8] = E
    f2[6][1] = C; f2[6][14] = C
    save_frame(f2, "yawn", 2)

    save_frame(f1, "yawn", 3)
    save_frame(base, "yawn", 4)

# ==========================================
# 15. Cool (Крутой в очках)
# ==========================================
def gen_cool():
    base = get_base_grid()
    save_frame(base, "cool", 0)

    f1 = [row[:] for row in base]
    for x in range(4, 12):
        f1[2][x] = E
    f1[2][6] = W; f1[2][10] = W
    save_frame(f1, "cool", 1)

    f2 = [row[:] for row in base]
    for x in range(3, 13):
        f2[5][x] = E
    f2[5][5] = W; f2[5][10] = W
    save_frame(f2, "cool", 2)

    f3 = [row[:] for row in f2]
    f3[4][12] = Y; f3[5][12] = Y
    save_frame(f3, "cool", 3)

    save_frame(f2, "cool", 4)
    save_frame(base, "cool", 5)

# ==========================================
# 16. Question (Знак вопроса)
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
# 17. Matrix (Хакер / Цифровой дождь)
# ==========================================
def gen_matrix():
    base = get_base_grid()
    # 0: Code rain drops begin
    f0 = [row[:] for row in base]
    f0[0][2] = G; f0[0][8] = G; f0[0][13] = G
    f0[1][8] = GD
    save_frame(f0, "matrix", 0)

    # 1: Code falls, cyber visor on eyes
    f1 = [row[:] for row in base]
    f1[1][2] = G; f1[2][2] = GD
    f1[2][8] = G; f1[3][8] = GD
    f1[1][13] = G; f1[2][13] = GD
    # Green matrix reflection across eyes
    for x in range(4, 12):
        f1[5][x] = GD
    f1[5][5] = G; f1[5][10] = G
    save_frame(f1, "matrix", 1)

    # 2: Dense digital rain, visor glow
    f2 = [row[:] for row in base]
    f2[0][5] = G; f2[1][5] = GD
    f2[2][1] = G; f2[3][1] = GD
    f2[3][11] = G; f2[4][11] = GD
    f2[2][14] = G; f2[3][14] = GD
    for x in range(3, 13):
        f2[5][x] = G
    f2[5][5] = W; f2[5][10] = W  # glowing visor eyes
    save_frame(f2, "matrix", 2)

    # 3: Stream cascade
    f3 = [row[:] for row in base]
    f3[1][1] = GD; f3[3][5] = G; f3[4][5] = GD
    f3[0][9] = G; f3[1][9] = GD; f3[2][9] = G
    f3[4][14] = G; f3[5][14] = GD
    for x in range(3, 13):
        f3[5][x] = G
    f3[5][6] = W; f3[5][9] = W
    save_frame(f3, "matrix", 3)

    # 4: Fading rain
    f4 = [row[:] for row in base]
    f4[5][2] = GD; f4[6][8] = GD; f4[7][13] = GD
    save_frame(f4, "matrix", 4)
    save_frame(base, "matrix", 5)

# ==========================================
# 18. Rock (Рок-гитарист)
# ==========================================
def gen_rock():
    base = get_base_grid()
    # 0: Pulls out red electric guitar
    f0 = [row[:] for row in base]
    # Red guitar body cols 10-14, rows 7-9
    f0[7][12] = R; f0[7][13] = R; f0[8][11] = R; f0[8][12] = W; f0[8][13] = R; f0[9][12] = R
    # Guitar neck cols 8-10, row 6
    f0[6][9] = GR; f0[5][8] = W
    save_frame(f0, "rock", 0)

    # 1: Strum down, yellow music note
    f1 = [row[:] for row in f0]
    f1[7][11] = C   # right arm strumming
    f1[1][12] = Y; f1[2][12] = Y; f1[1][13] = Y; f1[2][14] = Y
    save_frame(f1, "rock", 1)

    # 2: Power jump & rock horns!
    f2 = make_empty_grid()
    for y in range(4, 12):
        for x in range(16):
            f2[y - 1][x] = base[y][x]
    # Guitar tilted up
    f2[6][12] = R; f2[6][13] = R; f2[7][11] = R; f2[7][12] = W; f2[7][13] = R
    f2[5][9] = GR; f2[4][8] = W
    # Left arm rock horns (col 1-2, row 4)
    f2[4][1] = C; f2[4][3] = C; f2[5][2] = C
    # Happy eyes ^ ^
    f2[4][5] = CD; f2[4][10] = CD
    f2[0][11] = CY; f2[1][11] = CY; f2[0][12] = CY
    save_frame(f2, "rock", 2)

    # 3: Strum back with star glint
    f3 = [row[:] for row in f0]
    f3[7][13] = W  # sparkle on guitar
    f3[0][7] = Y; f3[1][7] = Y
    save_frame(f3, "rock", 3)

    save_frame(f1, "rock", 4)
    save_frame(base, "rock", 5)

# ==========================================
# 19. Pizza (Кушает пиццу)
# ==========================================
def gen_pizza():
    base = get_base_grid()
    # 0: Holding a slice of pizza on the right
    f0 = [row[:] for row in base]
    # Pizza slice (cols 11-15, rows 6-8)
    f0[6][14] = BR; f0[7][14] = BR   # crust
    f0[7][12] = CH; f0[7][13] = CH; f0[8][11] = CH
    f0[7][13] = R                   # pepperoni
    save_frame(f0, "pizza", 0)

    # 1: Pizza brought to mouth, mouth opens
    f1 = [row[:] for row in base]
    f1[6][9] = CH; f1[6][10] = R; f1[7][8] = CH; f1[7][9] = CH; f1[6][11] = BR
    # open mouth
    f1[7][6] = E; f1[7][7] = E
    save_frame(f1, "pizza", 1)

    # 2: Big bite! Cheese stretch!
    f2 = [row[:] for row in base]
    f2[5][5] = CD; f2[5][10] = CD  # happy squinting eyes
    # cheese string from hand to mouth
    f2[7][7] = Y; f2[7][8] = Y; f2[7][9] = CH; f2[7][10] = CH; f2[6][11] = BR
    f2[6][6] = P; f2[6][9] = P     # blushing cheeks
    save_frame(f2, "pizza", 2)

    # 3: Chewing happily, heart above head
    f3 = [row[:] for row in base]
    f3[5][5] = CD; f3[5][10] = CD
    f3[6][4] = P; f3[6][11] = P
    f3[1][7] = R; f3[1][8] = R; f3[2][7] = R; f3[2][8] = R  # small heart
    save_frame(f3, "pizza", 3)

    # 4: Wipes mouth with arm
    f4 = [row[:] for row in base]
    f4[6][5] = C; f4[6][6] = C
    save_frame(f4, "pizza", 4)
    save_frame(base, "pizza", 5)

# ==========================================
# 20. Rage (Рейдж / Переворот стола)
# ==========================================
def gen_rage():
    base = get_base_grid()
    # 0: Peaceful computer table in front
    f0 = [row[:] for row in base]
    f0[8][11] = GR; f0[8][12] = GR; f0[8][13] = GR
    f0[9][11] = DG; f0[9][13] = DG
    save_frame(f0, "rage", 0)

    # 1: Bug detected! Angry red face
    f1 = [row[:] for row in f0]
    f1[6][4] = R; f1[6][11] = R
    # Angry eyes (slanting in)
    f1[5][4] = E; f1[5][5] = R; f1[5][10] = R; f1[5][11] = E
    save_frame(f1, "rage", 1)

    # 2: Grabbing underneath table
    f2 = [row[:] for row in f1]
    f2[8][11] = C; f2[9][11] = C
    save_frame(f2, "rage", 2)

    # 3: TABLE FLIP! (╯°□°)╯︵ ┻━┻
    f3 = [row[:] for row in base]
    # Arms thrust high
    f3[5][2] = C; f3[4][2] = C; f3[5][13] = C; f3[4][13] = C
    f3[7][2] = T; f3[7][13] = T
    # Table flying upside down in air (rows 2-4, cols 10-14)
    f3[3][10] = DG; f3[3][12] = DG
    f3[2][10] = GR; f3[2][11] = GR; f3[2][12] = GR
    # Angry wide eyes
    f3[5][5] = W; f3[5][10] = W; f3[5][4] = E; f3[5][11] = E
    save_frame(f3, "rage", 3)

    # 4: Table crashes, dust puff
    f4 = [row[:] for row in base]
    f4[9][13] = GR; f4[9][14] = GR; f4[8][14] = DG
    f4[8][12] = W; f4[9][11] = W  # dust
    save_frame(f4, "rage", 4)

    # 5: Heavy exhale, calming down
    f5 = [row[:] for row in base]
    f5[5][5] = CD; f5[5][10] = CD
    save_frame(f5, "rage", 5)
    save_frame(base, "rage", 6)

# ==========================================
# 21. Disco (Диско-шар / Вечеринка)
# ==========================================
def gen_disco():
    base = get_base_grid()
    # 0: Disco ball drops from ceiling
    f0 = [row[:] for row in base]
    f0[0][7] = GR; f0[0][8] = GR; f0[1][6] = GR; f0[1][7] = W; f0[1][8] = CY; f0[1][9] = GR
    f0[2][7] = GR; f0[2][8] = W
    save_frame(f0, "disco", 0)

    # 1: Travolta pose! Right arm pointing up-right at 45°
    f1 = [row[:] for row in f0]
    f1[7][13] = T; f1[6][13] = T
    f1[5][12] = C; f1[4][13] = C; f1[3][14] = C; f1[2][15] = C
    # Lights shooting
    f1[3][3] = Y; f1[4][2] = PU; f1[6][1] = CY
    save_frame(f1, "disco", 1)

    # 2: Hip switch, left arm pointing down
    f2 = [row[:] for row in f0]
    f2[7][2] = T; f2[8][1] = C
    # Disco ball glint
    f2[1][7] = Y; f2[1][8] = W
    f2[5][5] = W; f2[5][10] = W  # excited eyes
    save_frame(f2, "disco", 2)

    # 3: Switch! Left arm shoots up-left at 45°
    f3 = [row[:] for row in f0]
    f3[7][2] = T; f3[6][2] = T
    f3[5][3] = C; f3[4][2] = C; f3[3][1] = C; f3[2][0] = C
    f3[3][12] = PU; f3[4][13] = Y; f3[6][14] = CY
    save_frame(f3, "disco", 3)

    # 4: Spin with cool glasses
    f4 = [row[:] for row in f0]
    for x in range(3, 13):
        f4[5][x] = E
    f4[5][5] = W; f4[5][10] = W
    save_frame(f4, "disco", 4)
    save_frame(base, "disco", 5)

# ==========================================
# 22. Wizard (Волшебник / Магия)
# ==========================================
def gen_wizard():
    base = get_base_grid()
    # 0: Purple wizard hat on head
    f0 = [row[:] for row in base]
    f0[3][3] = PU; f0[3][4] = PU; f0[3][11] = PU; f0[3][12] = PU  # brim
    for x in range(4, 12):
        f0[3][x] = PU
    f0[2][5] = PU; f0[2][6] = Y; f0[2][7] = PU; f0[2][8] = PU; f0[2][9] = PU; f0[2][10] = PU
    f0[1][6] = PU; f0[1][7] = PU; f0[1][8] = PU
    f0[0][7] = PU; f0[0][8] = Y  # tip with gold star
    save_frame(f0, "wizard", 0)

    # 1: Draws glowing magic wand in right hand
    f1 = [row[:] for row in f0]
    f1[7][13] = T; f1[6][13] = T
    f1[5][12] = C; f1[4][13] = BR; f1[3][14] = Y
    save_frame(f1, "wizard", 1)

    # 2: Waves wand, magic arc of stars
    f2 = [row[:] for row in f0]
    f2[4][12] = BR; f2[3][11] = Y
    # Arc of sparkles
    f2[1][11] = CY; f2[2][13] = BL; f2[1][14] = Y; f2[0][12] = W
    save_frame(f2, "wizard", 2)

    # 3: MAGIC BURST!
    f3 = [row[:] for row in f0]
    f3[1][3] = Y; f3[2][1] = PU; f3[3][2] = CY
    f3[1][12] = Y; f3[2][14] = BL; f3[3][13] = W
    f3[7][0] = Y; f3[7][15] = CY
    # Eyes glow cyan with power
    f3[5][5] = CY; f3[5][10] = CY
    save_frame(f3, "wizard", 3)

    # 4: Glitter floats down
    f4 = [row[:] for row in f0]
    f4[4][4] = Y; f4[6][1] = PU; f4[7][14] = CY
    save_frame(f4, "wizard", 4)
    save_frame(base, "wizard", 5)

# ==========================================
# 23. Workout (Качалка / Штанга)
# ==========================================
def gen_workout():
    base = get_base_grid()
    # 0: Heavy barbell on floor
    f0 = [row[:] for row in base]
    for x in range(2, 14):
        f0[10][x] = GR
    # Weights at ends
    f0[9][1] = DG; f0[10][1] = DG; f0[11][1] = DG
    f0[9][14] = DG; f0[10][14] = DG; f0[11][14] = DG
    save_frame(f0, "workout", 0)

    # 1: Grips the barbell
    f1 = [row[:] for row in f0]
    f1[10][4] = C; f1[10][11] = C
    f1[5][5] = E; f1[5][10] = E
    save_frame(f1, "workout", 1)

    # 2: Lifts to chest (Clean)
    f2 = [row[:] for row in base]
    for x in range(2, 14):
        f2[7][x] = GR
    f2[6][1] = DG; f2[7][1] = DG; f2[8][1] = DG
    f2[6][14] = DG; f2[7][14] = DG; f2[8][14] = DG
    # Straining face
    f2[5][5] = CD; f2[5][10] = CD; f2[4][12] = CY  # sweat drop
    save_frame(f2, "workout", 2)

    # 3: OVERHEAD PRESS! (Jerk)
    f3 = [row[:] for row in base]
    for x in range(2, 14):
        f3[1][x] = GR
    f3[0][1] = DG; f3[1][1] = DG; f3[2][1] = DG
    f3[0][14] = DG; f3[1][14] = DG; f3[2][14] = DG
    # Arms extending straight up
    f3[3][3] = C; f3[2][3] = C; f3[3][12] = C; f3[2][12] = C
    f3[4][5] = CD; f3[4][10] = CD
    save_frame(f3, "workout", 3)

    # 4: Holds overhead triumphantly
    f4 = [row[:] for row in f3]
    f4[4][5] = E; f4[4][10] = E
    f4[3][1] = Y; f4[3][14] = Y  # power sparkles
    save_frame(f4, "workout", 4)

    # 5: Drops barbell with flex!
    f5 = [row[:] for row in base]
    f5[6][1] = C; f5[5][2] = C; f5[6][14] = C; f5[5][13] = C  # flex biceps
    save_frame(f5, "workout", 5)
    save_frame(base, "workout", 6)

# ==========================================
# 24. Cry (Драматичный аниме-плач)
# ==========================================
def gen_cry():
    base = get_base_grid()
    # 0: Sad droopy face
    f0 = [row[:] for row in base]
    f0[5][5] = CD; f0[5][10] = CD
    f0[7][7] = CD; f0[7][8] = CD
    save_frame(f0, "cry", 0)

    # 1: Tears welling up
    f1 = [row[:] for row in f0]
    f1[6][5] = BL; f1[6][10] = BL
    save_frame(f1, "cry", 1)

    # 2: FOUNTAINS OF TEARS! High-pressure streams shooting out
    f2 = [row[:] for row in f0]
    # Left stream
    f2[5][4] = BL; f2[4][3] = BL; f2[4][2] = BL; f2[5][1] = BL; f2[6][0] = BL
    # Right stream
    f2[5][11] = BL; f2[4][12] = BL; f2[4][13] = BL; f2[5][14] = BL; f2[6][15] = BL
    # Hands rubbing eyes
    f2[6][4] = C; f2[6][11] = C
    save_frame(f2, "cry", 2)

    # 3: Stream pulses with splash
    f3 = [row[:] for row in f0]
    f3[5][3] = BL; f3[4][2] = BL; f3[5][0] = BL; f3[7][0] = BL
    f3[5][12] = BL; f3[4][13] = BL; f3[5][15] = BL; f3[7][15] = BL
    f3[6][5] = C; f3[6][10] = C
    save_frame(f3, "cry", 3)

    # 4: Sniffling with handkerchief
    f4 = [row[:] for row in f0]
    f4[6][6] = W; f4[7][6] = W; f4[6][7] = C
    save_frame(f4, "cry", 4)
    save_frame(base, "cry", 5)

# ==========================================
# 25. Read (Читает книгу / документацию)
# ==========================================
def gen_read():
    base = get_base_grid()
    # 0: Opens leather book in hands
    f0 = [row[:] for row in base]
    # Book (cols 4-11, rows 7-9)
    for x in range(4, 12):
        f0[8][x] = W; f0[9][x] = BR
    f0[8][4] = BR; f0[8][11] = BR; f0[8][7] = BL  # spine & ribbon
    save_frame(f0, "read", 0)

    # 1: Eyes reading left side
    f1 = [row[:] for row in f0]
    f1[5][5] = E; f1[5][10] = E
    f1[5][4] = E; f1[5][9] = E
    save_frame(f1, "read", 1)

    # 2: Eyes reading right side
    f2 = [row[:] for row in f0]
    f2[5][4] = C; f2[5][9] = C
    f2[5][6] = E; f2[5][11] = E
    save_frame(f2, "read", 2)

    # 3: Page turn curl!
    f3 = [row[:] for row in f0]
    f3[7][8] = W; f3[7][9] = GR; f3[7][10] = C  # hand turning
    save_frame(f3, "read", 3)

    # 4: 'Aha!' spark above head
    f4 = [row[:] for row in f0]
    f4[1][7] = Y; f4[1][8] = Y; f4[2][7] = W
    f4[5][5] = E; f4[5][10] = E
    save_frame(f4, "read", 4)
    save_frame(base, "read", 5)

# ==========================================
# 26. Cat (Котик на голове)
# ==========================================
def gen_cat():
    base = get_base_grid()
    # 0: Looks up curiously
    f0 = [row[:] for row in base]
    f0[5][5] = C; f0[5][10] = C; f0[4][5] = E; f0[4][10] = E
    save_frame(f0, "cat", 0)

    # 1: Kitty appears on head
    f1 = [row[:] for row in base]
    # Orange kitty (cols 5-10, rows 2-3)
    f1[2][5] = OR; f1[2][6] = OR; f1[2][7] = OR; f1[2][8] = OR; f1[2][9] = OR; f1[2][10] = OR
    f1[3][5] = W; f1[3][6] = OR; f1[3][7] = OR; f1[3][8] = OR; f1[3][9] = OR; f1[3][10] = W
    # Ears
    f1[1][5] = P; f1[1][10] = P
    save_frame(f1, "cat", 1)

    # 2: Kitty wags tail, purrs
    f2 = [row[:] for row in f1]
    f2[1][4] = OR; f2[0][4] = OR  # tail curled
    f2[5][5] = CD; f2[5][10] = CD  # Claude closes eyes happily
    f2[6][4] = P; f2[6][11] = P    # Claude blushing
    f2[1][12] = P                  # heart
    save_frame(f2, "cat", 2)

    # 3: Claude pets kitty's ears
    f3 = [row[:] for row in f2]
    f3[7][13] = T; f3[6][13] = T
    f3[3][11] = C; f3[2][11] = C  # hand scratching kitty
    f3[0][12] = P; f3[1][13] = P  # bigger heart
    save_frame(f3, "cat", 3)

    # 4: Kitty takes cozy nap, purring
    f4 = [row[:] for row in f2]
    f4[2][6] = CD; f4[2][9] = CD  # kitty eyes closed
    save_frame(f4, "cat", 4)
    save_frame(base, "cat", 5)

# ==========================================
# 27. Money (Дождь из монет и купюр)
# ==========================================
def gen_money():
    base = get_base_grid()
    # 0: Gold coin drops from sky
    f0 = [row[:] for row in base]
    f0[0][8] = Y; f0[0][9] = Y; f0[1][8] = Y; f0[1][9] = CH
    save_frame(f0, "money", 0)

    # 1: Coins and green cash fall
    f1 = [row[:] for row in base]
    f1[2][8] = Y; f1[2][9] = CH
    f1[0][3] = G; f1[0][4] = G; f1[1][3] = GD; f1[1][4] = G   # $ bill
    f1[1][13] = Y; f1[1][14] = CH                             # coin
    save_frame(f1, "money", 1)

    # 2: Dollar eyes & money shower!
    f2 = [row[:] for row in base]
    f2[5][5] = G; f2[5][10] = G
    # falling coins
    f2[3][2] = G; f2[4][8] = Y; f2[4][9] = CH; f2[3][14] = Y
    # arms catching money
    f2[7][2] = T; f2[6][2] = T; f2[5][1] = C
    f2[7][13] = T; f2[6][13] = T; f2[5][14] = C
    save_frame(f2, "money", 2)

    # 3: Tossing coins in air
    f3 = [row[:] for row in f2]
    f3[2][6] = Y; f3[2][7] = W; f3[2][9] = Y; f3[2][10] = W
    save_frame(f3, "money", 3)

    # 4: Glitz and sparkles
    f4 = [row[:] for row in base]
    f4[3][4] = Y; f4[3][11] = Y; f4[7][1] = Y; f4[7][14] = G
    f4[5][5] = W; f4[5][10] = W  # glittering eyes
    save_frame(f4, "money", 4)
    save_frame(base, "money", 5)

# ==========================================
# 28. Fire (Мем "This is Fine")
# ==========================================
def gen_fire():
    base = get_base_grid()
    # 0: Floor sparks
    f0 = [row[:] for row in base]
    f0[10][1] = OR; f0[11][1] = R; f0[10][14] = OR; f0[11][14] = R
    save_frame(f0, "fire", 0)

    # 1: Flames rise, Claude pulls coffee mug
    f1 = [row[:] for row in base]
    # Flames on sides
    f1[8][1] = Y; f1[9][1] = OR; f1[10][1] = R; f1[11][0] = R
    f1[8][14] = Y; f1[9][14] = OR; f1[10][14] = R; f1[11][15] = R
    # Mug in hand
    f1[7][11] = W; f1[7][12] = BR; f1[8][11] = W
    save_frame(f1, "fire", 1)

    # 2: Big blazing fire all around!
    f2 = [row[:] for row in base]
    for y in range(4, 12):
        f2[y][0] = R if y % 2 == 0 else OR
        f2[y][1] = OR if y % 2 == 0 else Y
        f2[y][14] = OR if y % 2 == 0 else Y
        f2[y][15] = R if y % 2 == 0 else OR
    # Calm sip
    f2[6][9] = W; f2[6][10] = BR
    f2[5][5] = CD; f2[5][10] = CD
    save_frame(f2, "fire", 2)

    # 3: Intense fire, serene stare: "This is fine"
    f3 = [row[:] for row in f2]
    f3[3][1] = Y; f3[3][14] = Y
    f3[5][5] = E; f3[5][10] = E  # unblinking eye contact
    save_frame(f3, "fire", 3)

    # 4: Exhale blows out fire with smoke
    f4 = [row[:] for row in base]
    f4[6][1] = GR; f4[7][2] = W; f4[6][14] = GR; f4[7][13] = W
    save_frame(f4, "fire", 4)
    save_frame(base, "fire", 5)

# ==========================================
# 29. Ghost (Привидение / Бу!)
# ==========================================
def gen_ghost():
    base = get_base_grid()
    save_frame(base, "ghost", 0)

    # 1: Shifts into white ghost
    f1 = make_empty_grid()
    # Ghost head
    for x in range(4, 12):
        f1[4][x] = W
    for x in range(4, 12):
        f1[5][x] = W
    f1[5][5] = E; f1[5][10] = E
    # Ghost body & wavy hem
    for y in range(6, 11):
        for x in range(3, 13):
            f1[y][x] = W
    f1[11][3] = W; f1[11][5] = W; f1[11][7] = W; f1[11][9] = W; f1[11][11] = W
    save_frame(f1, "ghost", 1)

    # 2: Ghost floats up 2px
    f2 = make_empty_grid()
    for y in range(4, 12):
        for x in range(16):
            if y - 2 >= 0:
                f2[y - 2][x] = f1[y][x]
    # Floaty arms
    f2[5][1] = W; f2[6][2] = W; f2[5][14] = W; f2[6][13] = W
    save_frame(f2, "ghost", 2)

    # 3: "BOO!" Open mouth & wiggle arms
    f3 = [row[:] for row in f2]
    f3[5][7] = E; f3[5][8] = E  # open spooky mouth
    f3[4][1] = W; f3[5][1] = T; f3[4][14] = W; f3[5][14] = T
    save_frame(f3, "ghost", 3)

    # 4: Giggles and lowers
    save_frame(f2, "ghost", 4)
    save_frame(f1, "ghost", 5)
    save_frame(base, "ghost", 6)

# ==========================================
# 30. Superhero (Супермен / Полет)
# ==========================================
def gen_superhero():
    base = get_base_grid()
    # 0: Red cape appears behind back
    f0 = [row[:] for row in base]
    f0[6][1] = R; f0[7][1] = R; f0[8][2] = R; f0[9][2] = R
    f0[6][14] = R; f0[7][14] = R; f0[8][13] = R; f0[9][13] = R
    save_frame(f0, "superhero", 0)

    # 1: Hero pose: hand on hip, cape billowing
    f1 = [row[:] for row in f0]
    f1[7][3] = C; f1[7][2] = T  # hand on hip
    f1[8][0] = R; f1[9][1] = R  # cape waving wide
    save_frame(f1, "superhero", 1)

    # 2: Spring crouch
    f2 = make_empty_grid()
    for y in range(4, 12):
        for x in range(16):
            if y + 1 < 16:
                f2[y + 1][x] = f0[y][x]
    save_frame(f2, "superhero", 2)

    # 3: TAKEOFF! Right fist pointed straight up, body hovering 3px
    f3 = make_empty_grid()
    for y in range(4, 12):
        for x in range(16):
            if y - 3 >= 0:
                f3[y - 3][x] = base[y][x]
    # Right fist pointed to sky
    f3[0][12] = C; f3[1][12] = C; f3[2][12] = C
    # Billowing cape
    f3[4][2] = R; f3[5][1] = R; f3[6][1] = R; f3[7][0] = R
    # Yellow speed lines at feet
    f3[10][5] = Y; f3[11][5] = Y; f3[10][10] = Y; f3[11][10] = Y
    save_frame(f3, "superhero", 3)

    # 4: Hovering at peak
    f4 = [row[:] for row in f3]
    f4[10][5] = T; f4[11][5] = T; f4[10][10] = T; f4[11][10] = T
    save_frame(f4, "superhero", 4)

    # 5: Superhero landing
    save_frame(f2, "superhero", 5)
    save_frame(base, "superhero", 6)

# ==========================================
# 31. Applause (Аплодисменты / Хлопает)
# ==========================================
def gen_applause():
    base = get_base_grid()
    # 0: Hands come forward together
    f0 = [row[:] for row in base]
    f0[7][2] = T; f0[7][13] = T
    f0[7][6] = C; f0[7][9] = C
    save_frame(f0, "applause", 0)

    # 1: CLAP! Hands meet with spark
    f1 = [row[:] for row in base]
    f1[7][2] = T; f1[7][13] = T
    f1[7][7] = C; f1[7][8] = C
    # Sparkle between hands
    f1[6][7] = Y; f1[6][8] = W
    f1[5][5] = CD; f1[5][10] = CD  # happy eyes
    save_frame(f1, "applause", 1)

    # 2: Hands separate
    f2 = [row[:] for row in f0]
    f2[5][5] = E; f2[5][10] = E
    save_frame(f2, "applause", 2)

    # 3: CLAP! Second enthusiastic clap
    save_frame(f1, "applause", 3)
    save_frame(f2, "applause", 4)

    # 5: Thumbs up with right hand!
    f5 = [row[:] for row in base]
    f5[7][13] = T; f5[6][13] = T
    f5[5][13] = C; f5[4][13] = C  # thumb up
    save_frame(f5, "applause", 5)
    save_frame(base, "applause", 6)

# ==========================================
# 32. Dab (Дэб)
# ==========================================
def gen_dab():
    base = get_base_grid()
    save_frame(base, "dab", 0)

    # 1: Wind-up, leaning back
    f1 = [row[:] for row in base]
    f1[6][3] = C; f1[7][3] = C
    save_frame(f1, "dab", 1)

    # 2: HIT THE DAB!
    # Head tucked into right elbow, left arm extended straight up-left at 45°
    f2 = make_empty_grid()
    # Body
    for y in range(4, 12):
        for x in range(3, 13):
            f2[y][x] = base[y][x]
    # Head buried into right arm (tucked)
    f2[5][5] = CD; f2[5][10] = CD
    f2[5][9] = C; f2[5][10] = C; f2[6][11] = C; f2[6][12] = C  # right arm across face
    # Left arm pointing straight up-left at 45°
    f2[5][3] = C; f2[4][2] = C; f2[3][1] = C; f2[2][0] = C
    f2[7][2] = T; f2[7][13] = T
    save_frame(f2, "dab", 2)

    # 3: Hold with sparkle at fingertip!
    f3 = [row[:] for row in f2]
    f3[1][0] = Y; f3[2][1] = W
    save_frame(f3, "dab", 3)

    # 4: Pop up & brush dust off shoulder
    f4 = [row[:] for row in base]
    f4[6][4] = C; f4[5][3] = C
    save_frame(f4, "dab", 4)
    save_frame(base, "dab", 5)

# ==========================================
# Main: Run all generators
# ==========================================
def main():
    print("Generating pixel art animation frames for ALL 32 animations...")
    # Original 16
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
    gen_typing()
    gen_spin()
    gen_peek()
    gen_yawn()
    gen_cool()
    gen_question()

    # New 16
    gen_matrix()
    gen_rock()
    gen_pizza()
    gen_rage()
    gen_disco()
    gen_wizard()
    gen_workout()
    gen_cry()
    gen_read()
    gen_cat()
    gen_money()
    gen_fire()
    gen_ghost()
    gen_superhero()
    gen_applause()
    gen_dab()
    
    count = len([f for f in os.listdir(OUTPUT_DIR) if f.endswith(".png")])
    print(f"Successfully generated {count} animation frames across 32 animations in {OUTPUT_DIR}!")

if __name__ == "__main__":
    main()
