"""
Generates all pixel art animation frames for Claude Taskbar Mascot.
All sprites are strictly 16x16 RGBA PNGs, matching the exact terracotta palette and art style.
"""

import os
from PIL import Image

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "animations")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Colors
T = (0, 0, 0, 0)             # Transparent
C = (218, 119, 88, 255)      # Claude Terracotta
CD = (186, 94, 66, 255)      # Claude Dark / Shading
E = (0, 0, 0, 255)           # Eye / Black
W = (255, 255, 255, 255)     # White
R = (235, 65, 65, 255)       # Red (heart)
P = (245, 140, 160, 255)     # Pink (blush)
Y = (255, 215, 0, 255)       # Yellow (lightbulb, sparkles)
CY = (80, 220, 240, 255)     # Cyan (screen / tech)
BR = (120, 65, 30, 255)      # Coffee / Wood
GR = (170, 170, 175, 255)    # Grey (metal / laptop)
DG = (100, 100, 105, 255)    # Dark grey

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

# --- 1. Blink (Моргание) ---
def gen_blink():
    # 0: open
    f0 = get_base_grid()
    save_frame(f0, "blink", 0)

    # 1: squint / half closed (eyes are CD)
    f1 = get_base_grid()
    f1[5][5] = CD
    f1[5][10] = CD
    save_frame(f1, "blink", 1)

    # 2: fully closed (eyes are horizontal line CD)
    f2 = get_base_grid()
    f2[5][5] = C
    f2[5][10] = C
    f2[5][4] = CD
    f2[5][5] = CD
    f2[5][9] = CD
    f2[5][10] = CD
    save_frame(f2, "blink", 2)

    # 3: open again
    save_frame(f0, "blink", 3)

# --- 2. Look Around (Оглядывается) ---
def gen_look_around():
    f_base = get_base_grid()
    save_frame(f_base, "look_around", 0)

    # Look Left (eyes shifted col 4 & 9)
    f_left = get_base_grid()
    f_left[5][5] = C
    f_left[5][10] = C
    f_left[5][4] = E
    f_left[5][9] = E
    save_frame(f_left, "look_around", 1)
    save_frame(f_left, "look_around", 2)

    save_frame(f_base, "look_around", 3)

    # Look Right (eyes shifted col 6 & 11)
    f_right = get_base_grid()
    f_right[5][5] = C
    f_right[5][10] = C
    f_right[5][6] = E
    f_right[5][11] = E
    save_frame(f_right, "look_around", 4)
    save_frame(f_right, "look_around", 5)

    save_frame(f_base, "look_around", 6)

# --- 3. Wave (Машет правой рукой) ---
def gen_wave():
    f0 = get_base_grid()
    save_frame(f0, "wave", 0)

    # Arm up 1 (standard right-arm-up)
    f1 = get_base_grid()
    f1[7][12] = T
    f1[7][13] = T
    f1[5][12] = C
    f1[5][13] = C
    save_frame(f1, "wave", 1)

    # Arm waving high / out
    f2 = get_base_grid()
    f2[7][12] = T
    f2[7][13] = T
    f2[6][12] = T
    f2[6][13] = T
    f2[4][13] = C
    f2[4][14] = C
    f2[5][12] = C
    f2[5][13] = C
    save_frame(f2, "wave", 2)

    # Arm wave in
    save_frame(f1, "wave", 3)
    save_frame(f2, "wave", 4)
    save_frame(f1, "wave", 5)
    save_frame(f0, "wave", 6)

# --- 4. Cheer / Double Wave (Радость / Обе руки вверх) ---
def gen_cheer():
    f0 = get_base_grid()
    save_frame(f0, "cheer", 0)

    # Both arms up
    f1 = get_base_grid()
    # Left arm up
    f1[7][2] = T
    f1[7][3] = T
    f1[5][2] = C
    f1[5][3] = C
    # Right arm up
    f1[7][12] = T
    f1[7][13] = T
    f1[5][12] = C
    f1[5][13] = C
    save_frame(f1, "cheer", 1)

    # Both arms high + tiny bounce 1px up
    f2 = make_empty_grid()
    # Shift base up 1 pixel
    base = get_base_grid()
    for y in range(4, 12):
        for x in range(16):
            f2[y - 1][x] = base[y][x]
    # Arms high
    f2[6][2] = T
    f2[6][3] = T
    f2[6][12] = T
    f2[6][13] = T
    f2[3][1] = C
    f2[3][2] = C
    f2[4][2] = C
    f2[4][3] = C
    f2[3][13] = C
    f2[3][14] = C
    f2[4][12] = C
    f2[4][13] = C
    # Happy eyes ^ ^
    f2[4][5] = CD
    f2[4][10] = CD
    save_frame(f2, "cheer", 2)

    save_frame(f1, "cheer", 3)
    save_frame(f2, "cheer", 4)
    save_frame(f1, "cheer", 5)
    save_frame(f0, "cheer", 6)

# --- 5. Jump (Радостный прыжок) ---
def gen_jump():
    f0 = get_base_grid()
    save_frame(f0, "jump", 0)

    # Squash down 1px
    f_squash = make_empty_grid()
    base = get_base_grid()
    for y in range(4, 12):
        for x in range(16):
            if y < 11:
                f_squash[y + 1][x] = base[y][x]
    # Widen body 1px on sides
    f_squash[7][1] = C
    f_squash[7][14] = C
    save_frame(f_squash, "jump", 1)

    # Launch up 2px
    f_up2 = make_empty_grid()
    for y in range(4, 12):
        for x in range(16):
            f_up2[y - 2][x] = base[y][x]
    save_frame(f_up2, "jump", 2)

    # Apex up 3px (highest point)
    f_apex = make_empty_grid()
    for y in range(4, 12):
        for x in range(16):
            f_apex[y - 3][x] = base[y][x]
    # Arms lifted slightly
    f_apex[4][2] = T
    f_apex[4][13] = T
    f_apex[2][2] = C
    f_apex[2][13] = C
    save_frame(f_apex, "jump", 3)

    # Coming down 1px
    f_down1 = make_empty_grid()
    for y in range(4, 12):
        for x in range(16):
            f_down1[y - 1][x] = base[y][x]
    save_frame(f_down1, "jump", 4)

    # Landing squash
    save_frame(f_squash, "jump", 5)
    save_frame(f0, "jump", 6)

# --- 6. Dance / Bounce (Весёлый танец) ---
def gen_dance():
    base = get_base_grid()

    # Step left: body tilted/shifted 1px left, right arm raised
    f_left = make_empty_grid()
    for y in range(4, 12):
        for x in range(1, 15):
            f_left[y][x] = base[y][x + 1]
    f_left[5][12] = C
    f_left[5][13] = C
    f_left[7][12] = T
    save_frame(f_left, "dance", 0)

    # Center bob
    save_frame(base, "dance", 1)

    # Step right: body shifted 1px right, left arm raised
    f_right = make_empty_grid()
    for y in range(4, 12):
        for x in range(1, 15):
            f_right[y][x] = base[y][x - 1]
    f_right[5][2] = C
    f_right[5][3] = C
    f_right[7][3] = T
    save_frame(f_right, "dance", 2)

    # Center bob
    save_frame(base, "dance", 3)

# --- 7. Sleep / Zzz (Дремлет и храпит) ---
def gen_sleep():
    # Base sleeping body: eyes closed, head lowered 1px
    f_sleep_base = get_base_grid()
    f_sleep_base[5][5] = C
    f_sleep_base[5][10] = C
    f_sleep_base[5][4] = CD
    f_sleep_base[5][5] = CD
    f_sleep_base[5][9] = CD
    f_sleep_base[5][10] = CD

    # 0: just falling asleep
    save_frame(f_sleep_base, "sleep", 0)

    # 1: small 'z'
    f1 = [row[:] for row in f_sleep_base]
    # z at (col 12..13, row 2..3)
    f1[2][12] = W; f1[2][13] = W
    f1[3][13] = W
    f1[3][12] = W
    save_frame(f1, "sleep", 1)

    # 2: z floats up, second bigger Z starts
    f2 = [row[:] for row in f_sleep_base]
    # small z at row 1
    f2[1][13] = W; f2[1][14] = W
    # med z at row 2-3
    f2[3][11] = CY; f2[3][12] = CY; f2[3][13] = CY
    f2[4][12] = CY
    f2[4][11] = CY; f2[4][12] = CY; f2[4][13] = CY
    save_frame(f2, "sleep", 2)

    # 3: big Z at row 0-2
    f3 = [row[:] for row in f_sleep_base]
    f3[0][13] = W; f3[0][14] = W
    f3[1][10] = CY; f3[1][11] = CY; f3[1][12] = CY
    f3[2][11] = CY
    f3[3][10] = CY; f3[3][11] = CY; f3[3][12] = CY
    save_frame(f3, "sleep", 3)

    # 4: exhale
    save_frame(f_sleep_base, "sleep", 4)

# --- 8. Heart / Love (Любовь и сердечко) ---
def gen_heart():
    base = get_base_grid()
    # Add blush
    f_blush = [row[:] for row in base]
    f_blush[6][4] = P
    f_blush[6][11] = P
    save_frame(f_blush, "heart", 0)

    # Small heart appears
    f1 = [row[:] for row in f_blush]
    # heart at row 2
    f1[2][7] = R; f1[2][8] = R
    f1[3][7] = R; f1[3][8] = R
    save_frame(f1, "heart", 1)

    # Full beating heart
    f2 = [row[:] for row in f_blush]
    # rows 0-3
    f2[0][6] = R; f2[0][7] = R; f2[0][8] = R; f2[0][9] = R
    f2[1][5] = R; f2[1][6] = W; f2[1][7] = R; f2[1][8] = R; f2[1][9] = R; f2[1][10] = R
    f2[2][6] = R; f2[2][7] = R; f2[2][8] = R; f2[2][9] = R
    f2[3][7] = R; f2[3][8] = R
    # Happy eyes ^ ^
    f2[5][5] = CD; f2[5][10] = CD
    save_frame(f2, "heart", 2)

    # Heart pulse
    f3 = [row[:] for row in f2]
    # sparkles
    f3[0][4] = Y; f3[2][11] = Y
    save_frame(f3, "heart", 3)

    save_frame(f1, "heart", 4)
    save_frame(base, "heart", 5)

# --- 9. Coffee / Tea (Пьёт кофе) ---
def gen_coffee():
    base = get_base_grid()

    # Holding mug in right hand
    f1 = [row[:] for row in base]
    # Mug at cols 12-14, rows 7-8
    f1[7][12] = W; f1[7][13] = BR; f1[7][14] = W
    f1[8][12] = W; f1[8][13] = W;  f1[8][14] = W
    save_frame(f1, "coffee", 0)

    # Steam rising
    f2 = [row[:] for row in f1]
    f2[6][13] = W
    f2[5][14] = W
    save_frame(f2, "coffee", 1)

    # Sipping (mug brought closer to face, eyes closed happily)
    f3 = [row[:] for row in base]
    f3[6][10] = W; f3[6][11] = BR; f3[6][12] = W
    f3[7][10] = W; f3[7][11] = W;  f3[7][12] = W
    # Closed eyes
    f3[5][5] = CD; f3[5][10] = CD
    save_frame(f3, "coffee", 2)

    # Satisfied lower mug
    save_frame(f2, "coffee", 3)
    save_frame(base, "coffee", 4)

# --- 10. Idea / Lightbulb (Идея / Лампочка) ---
def gen_idea():
    base = get_base_grid()

    # Looking up (eyes on row 4)
    f_look = [row[:] for row in base]
    f_look[5][5] = C; f_look[5][10] = C
    f_look[4][5] = E; f_look[4][10] = E
    save_frame(f_look, "idea", 0)

    # Spark!
    f1 = [row[:] for row in f_look]
    f1[2][7] = Y; f1[2][8] = Y
    save_frame(f1, "idea", 1)

    # Lightbulb appears
    f2 = [row[:] for row in f_look]
    # Bulb top (row 0-1)
    f2[0][7] = Y; f2[0][8] = Y
    f2[1][6] = Y; f2[1][7] = W; f2[1][8] = Y; f2[1][9] = Y
    f2[2][7] = Y; f2[2][8] = Y
    # Base of bulb (row 3)
    f2[3][7] = GR; f2[3][8] = GR
    save_frame(f2, "idea", 2)

    # Bulb flashes with rays!
    f3 = [row[:] for row in f2]
    # Rays
    f3[0][4] = Y; f3[0][11] = Y
    f3[2][4] = Y; f3[2][11] = Y
    f3[1][7] = W; f3[1][8] = W
    # Big excited eyes O O
    f3[4][5] = C; f3[4][10] = C
    f3[5][5] = E; f3[5][10] = E
    f3[5][4] = E; f3[5][11] = E
    save_frame(f3, "idea", 3)

    save_frame(f2, "idea", 4)
    save_frame(base, "idea", 5)

# --- 11. Typing / Laptop (Кодит / Работает за ноутом) ---
def gen_typing():
    base = get_base_grid()

    # Laptop on table in front: cols 10-14
    # Frame 0: laptop open, screen glowing cyan
    f0 = [row[:] for row in base]
    # Screen (rows 7-9)
    f0[7][13] = GR; f0[7][14] = GR
    f0[8][13] = CY; f0[8][14] = GR
    # Keyboard base (row 9-10)
    f0[9][11] = GR; f0[9][12] = GR; f0[9][13] = GR
    f0[10][11] = DG; f0[10][12] = DG
    save_frame(f0, "typing", 0)

    # Frame 1: tapping key (hand reaches down, screen flicker)
    f1 = [row[:] for row in f0]
    f1[8][11] = C   # left arm tapping
    f1[8][13] = W   # screen line flickers white
    save_frame(f1, "typing", 1)

    # Frame 2: alternate hand tap
    f2 = [row[:] for row in f0]
    f2[8][12] = C   # right arm tapping
    f2[7][13] = CY
    save_frame(f2, "typing", 2)

    # Frame 3: fast combo tap
    f3 = [row[:] for row in f0]
    f3[8][11] = C
    f3[8][12] = C
    f3[8][13] = CY; f3[7][13] = W
    save_frame(f3, "typing", 3)

    save_frame(f1, "typing", 4)
    save_frame(f2, "typing", 5)

# --- 12. Spin 360 (Крутится вокруг своей оси) ---
def gen_spin():
    base = get_base_grid()
    save_frame(base, "spin", 0)

    # 3/4 turn right (narrower body, one eye)
    f_34r = make_empty_grid()
    for y in range(4, 12):
        for x in range(5, 12):
            f_34r[y][x] = C
    f_34r[5][9] = E  # only right eye visible
    f_34r[6][12] = C; f_34r[7][12] = C
    # legs
    for y in (10, 11):
        f_34r[y][6] = C; f_34r[y][9] = C
    save_frame(f_34r, "spin", 1)

    # Side profile (thin body cols 6-9)
    f_side = make_empty_grid()
    for y in range(4, 10):
        for x in range(6, 10):
            f_side[y][x] = C
    f_side[5][8] = E  # eye on side
    for y in (10, 11):
        f_side[y][7] = C; f_side[y][8] = C
    save_frame(f_side, "spin", 2)

    # Back view (no eyes at all!)
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

    # Other side profile
    f_side_l = make_empty_grid()
    for y in range(4, 10):
        for x in range(6, 10):
            f_side_l[y][x] = C
    f_side_l[5][7] = E
    for y in (10, 11):
        f_side_l[y][7] = C; f_side_l[y][8] = C
    save_frame(f_side_l, "spin", 4)

    # 3/4 turn left
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

# --- 13. Peek / Hide (Прячется за панель задач) ---
def gen_peek():
    base = get_base_grid()
    save_frame(base, "peek", 0)

    # Sink down 2px (legs go under taskbar)
    f_down2 = make_empty_grid()
    for y in range(4, 14):
        for x in range(16):
            if y + 2 < 16:
                f_down2[y + 2][x] = base[y][x]
    save_frame(f_down2, "peek", 1)

    # Sink down 4px (only head and eyes peek out!)
    f_down4 = make_empty_grid()
    for y in range(4, 12):
        for x in range(16):
            if y + 4 < 16:
                f_down4[y + 4][x] = base[y][x]
    save_frame(f_down4, "peek", 2)

    # Eyes shift left and right while peeking
    f_peek_l = [row[:] for row in f_down4]
    f_peek_l[9][5] = C; f_peek_l[9][10] = C
    f_peek_l[9][4] = E; f_peek_l[9][9] = E
    save_frame(f_peek_l, "peek", 3)

    f_peek_r = [row[:] for row in f_down4]
    f_peek_r[9][5] = C; f_peek_r[9][10] = C
    f_peek_r[9][6] = E; f_peek_r[9][11] = E
    save_frame(f_peek_r, "peek", 4)

    # Pop back up!
    save_frame(f_down2, "peek", 5)
    save_frame(base, "peek", 6)

# --- 14. Yawn (Зевает) ---
def gen_yawn():
    base = get_base_grid()
    save_frame(base, "yawn", 0)

    # Squinting eyes, small open mouth
    f1 = [row[:] for row in base]
    f1[5][5] = CD; f1[5][10] = CD
    f1[7][7] = E; f1[7][8] = E
    save_frame(f1, "yawn", 1)

    # Big yawn! Hands stretched
    f2 = [row[:] for row in base]
    f2[5][5] = CD; f2[5][10] = CD
    # bigger mouth
    f2[7][7] = E; f2[7][8] = E
    f2[8][7] = E; f2[8][8] = E
    # hands stretch out
    f2[6][1] = C; f2[6][14] = C
    save_frame(f2, "yawn", 2)

    save_frame(f1, "yawn", 3)
    save_frame(base, "yawn", 4)

# --- 15. Sunglasses / Cool (Крутой в очках) ---
def gen_cool():
    base = get_base_grid()
    save_frame(base, "cool", 0)

    # Sunglasses drop from above (row 2-3)
    f1 = [row[:] for row in base]
    for x in range(4, 12):
        f1[2][x] = E
    f1[2][6] = W; f1[2][10] = W
    save_frame(f1, "cool", 1)

    # Sunglasses land on eyes (row 5)
    f2 = [row[:] for row in base]
    for x in range(3, 13):
        f2[5][x] = E
    # White glint
    f2[5][5] = W; f2[5][10] = W
    save_frame(f2, "cool", 2)

    # Sparkle on sunglasses
    f3 = [row[:] for row in f2]
    f3[4][12] = Y; f3[5][12] = Y
    save_frame(f3, "cool", 3)

    save_frame(f2, "cool", 4)
    save_frame(base, "cool", 5)

# --- 16. Confused / Question (Знак вопроса) ---
def gen_question():
    base = get_base_grid()

    # Head tilt, eyes puzzled
    f1 = [row[:] for row in base]
    f1[5][5] = E; f1[5][10] = CD  # one eye raised, one squinting
    save_frame(f1, "question", 0)

    # Question mark appears above head
    f2 = [row[:] for row in f1]
    # ? mark at row 0-3, col 8-10
    f2[0][8] = Y; f2[0][9] = Y
    f2[1][10] = Y
    f2[2][9] = Y
    f2[3][9] = Y
    save_frame(f2, "question", 1)

    # Sparkle question mark
    f3 = [row[:] for row in f2]
    f3[0][8] = W; f3[0][9] = Y
    save_frame(f3, "question", 2)

    save_frame(f1, "question", 3)
    save_frame(base, "question", 4)


def main():
    print("Generating pixel art animation frames...")
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
    
    count = len([f for f in os.listdir(OUTPUT_DIR) if f.endswith(".png")])
    print(f"Successfully generated {count} animation frames in {OUTPUT_DIR}!")

if __name__ == "__main__":
    main()
