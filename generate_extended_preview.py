"""
Generates extended frames for Coffee and Wizard animations (Original, 3x, 5x)
specifically for HTML presentation and user review.
Does not overwrite base app animations until approved.
"""

import os
from PIL import Image

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preview_extended")
os.makedirs(OUTPUT_DIR, exist_ok=True)

T = (0, 0, 0, 0)
C = (218, 119, 88, 255)
CD = (186, 94, 66, 255)
E = (0, 0, 0, 255)
W = (255, 255, 255, 255)
R = (235, 65, 65, 255)
P = (245, 140, 160, 255)
Y = (255, 215, 0, 255)
CY = (80, 220, 240, 255)
BR = (120, 65, 30, 255)
GR = (170, 170, 175, 255)
DG = (100, 100, 105, 255)
BL = (60, 130, 245, 255)
PU = (165, 80, 230, 255)

def make_empty():
    return [[T for _ in range(16)] for _ in range(16)]

def get_base():
    g = make_empty()
    for x in range(4, 12): g[4][x] = C
    for x in range(4, 12): g[5][x] = C
    g[5][5] = E; g[5][10] = E
    for y in (6, 7):
        for x in range(2, 14): g[y][x] = C
    for y in (8, 9):
        for x in range(4, 12): g[y][x] = C
    for y in (10, 11):
        g[y][4] = C; g[y][6] = C; g[y][9] = C; g[y][11] = C
    return g

def save(grid, name, idx):
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    for y in range(16):
        for x in range(16):
            img.putpixel((x, y), grid[y][x])
    filepath = os.path.join(OUTPUT_DIR, f"{name}_{idx:02d}.png")
    img.save(filepath)
    return filepath

# --- Coffee Mug Drawing Helpers ---
def draw_mug_desk(grid, x=13, y=8):
    grid[y][x] = W; grid[y][x+1] = BR; grid[y+1][x] = W; grid[y+1][x+1] = W

def draw_mug_hand(grid, x=11, y=7):
    # Held in paw
    grid[y][x] = W; grid[y][x+1] = BR; grid[y][x+2] = W
    grid[y+1][x] = W; grid[y+1][x+1] = W; grid[y+1][x+2] = W
    grid[y][x-1] = C; grid[y+1][x-1] = C

def draw_mug_sip(grid, x=10, y=6):
    # At mouth level
    grid[y][x] = W; grid[y][x+1] = BR; grid[y][x+2] = W
    grid[y+1][x] = W; grid[y+1][x+1] = W; grid[y+1][x+2] = W
    grid[y][x-1] = C; grid[y+1][x-1] = C

# ==============================================================
# COFFEE: Original (5 frames)
# ==============================================================
def gen_coffee_orig():
    base = get_base()
    f0 = [row[:] for row in base]
    f0[7][12] = W; f0[7][13] = BR; f0[7][14] = W
    f0[8][12] = W; f0[8][13] = W;  f0[8][14] = W
    save(f0, "coffee_orig", 0)

    f1 = [row[:] for row in f0]
    f1[6][13] = W; f1[5][14] = W
    save(f1, "coffee_orig", 1)

    f2 = [row[:] for row in base]
    f2[6][10] = W; f2[6][11] = BR; f2[6][12] = W
    f2[7][10] = W; f2[7][11] = W;  f2[7][12] = W
    f2[5][5] = CD; f2[5][10] = CD
    save(f2, "coffee_orig", 2)

    save(f1, "coffee_orig", 3)
    save(base, "coffee_orig", 4)

# ==============================================================
# COFFEE: 3x Extended (15 frames)
# ==============================================================
def gen_coffee_3x():
    base = get_base()

    # 0: Mug rests on desk
    f0 = [row[:] for row in base]
    draw_mug_desk(f0, 13, 8)
    save(f0, "coffee_3x", 0)

    # 1: Paw reaches toward mug
    f1 = [row[:] for row in f0]
    f1[7][12] = C; f1[8][12] = C
    save(f1, "coffee_3x", 1)

    # 2: Lifts mug off desk
    f2 = [row[:] for row in base]
    draw_mug_hand(f2, 12, 7)
    save(f2, "coffee_3x", 2)

    # 3: First wisp of steam rising
    f3 = [row[:] for row in f2]
    f3[5][13] = W
    save(f3, "coffee_3x", 3)

    # 4: Curling aroma steam
    f4 = [row[:] for row in f2]
    f4[4][13] = W; f4[5][14] = W; f4[3][14] = W
    save(f4, "coffee_3x", 4)

    # 5: Bringing mug up to face
    f5 = [row[:] for row in base]
    draw_mug_sip(f5, 10, 6)
    f5[4][11] = W; f5[3][12] = W
    save(f5, "coffee_3x", 5)

    # 6: First warm sip, eyes gently close in delight
    f6 = [row[:] for row in base]
    draw_mug_sip(f6, 10, 6)
    f6[5][5] = CD; f6[5][10] = CD
    save(f6, "coffee_3x", 6)

    # 7: Savoring taste, gentle cheek blush
    f7 = [row[:] for row in f6]
    f7[6][4] = P
    save(f7, "coffee_3x", 7)

    # 8: Lowers mug to chest, eyes open happily
    f8 = [row[:] for row in base]
    draw_mug_hand(f8, 11, 7)
    f8[6][4] = P; f8[6][11] = P
    save(f8, "coffee_3x", 8)

    # 9: Cozy steam curling from cup
    f9 = [row[:] for row in f8]
    f9[5][12] = W; f9[4][13] = W
    save(f9, "coffee_3x", 9)

    # 10: Second smaller sip
    f10 = [row[:] for row in base]
    draw_mug_sip(f10, 10, 6)
    f10[5][5] = CD; f10[5][10] = CD
    save(f10, "coffee_3x", 10)

    # 11: Warm cozy exhale puff (steam dissipates)
    f11 = [row[:] for row in base]
    draw_mug_hand(f11, 11, 7)
    f11[4][8] = W; f11[3][9] = W  # breath puff
    save(f11, "coffee_3x", 11)

    # 12: Lowers mug back down towards desk
    f12 = [row[:] for row in base]
    draw_mug_hand(f12, 12, 8)
    save(f12, "coffee_3x", 12)

    # 13: Sets mug gently on desk
    f13 = [row[:] for row in base]
    draw_mug_desk(f13, 13, 8)
    f13[7][12] = C
    save(f13, "coffee_3x", 13)

    # 14: Paw returns to side, cozy idle
    save(base, "coffee_3x", 14)

# ==============================================================
# COFFEE: 5x Extended (25 frames)
# ==============================================================
def gen_coffee_5x():
    base = get_base()

    # 0: Notices mug on desk
    f0 = [row[:] for row in base]
    draw_mug_desk(f0, 13, 8)
    f0[5][5] = C; f0[5][10] = C; f0[5][6] = E; f0[5][11] = E # glances right
    save(f0, "coffee_5x", 0)

    # 1: Paw starts reaching
    f1 = [row[:] for row in f0]
    f1[7][12] = C
    save(f1, "coffee_5x", 1)

    # 2: Grasps mug handle
    f2 = [row[:] for row in base]
    f2[7][12] = C; f2[8][12] = C
    draw_mug_desk(f2, 13, 8)
    save(f2, "coffee_5x", 2)

    # 3: Lifts mug slightly
    f3 = [row[:] for row in base]
    draw_mug_hand(f3, 12, 8)
    save(f3, "coffee_5x", 3)

    # 4: Raises to mid-chest
    f4 = [row[:] for row in base]
    draw_mug_hand(f4, 11, 7)
    save(f4, "coffee_5x", 4)

    # 5: First steam wisp rises
    f5 = [row[:] for row in f4]
    f5[5][12] = W
    save(f5, "coffee_5x", 5)

    # 6: Aroma curling high
    f6 = [row[:] for row in f4]
    f6[4][12] = W; f6[3][13] = W; f6[5][13] = W
    save(f6, "coffee_5x", 6)

    # 7: Sniffs aroma (eyes blink gently)
    f7 = [row[:] for row in f4]
    f7[4][13] = W; f7[3][12] = W
    f7[5][5] = CD; f7[5][10] = CD
    save(f7, "coffee_5x", 7)

    # 8: Brings mug closer to face
    f8 = [row[:] for row in base]
    draw_mug_sip(f8, 10, 6)
    f8[4][11] = W
    save(f8, "coffee_5x", 8)

    # 9: Careful testing sip (first touch)
    f9 = [row[:] for row in base]
    draw_mug_sip(f9, 10, 6)
    f9[5][5] = CD; f9[5][10] = CD
    save(f9, "coffee_5x", 9)

    # 10: Holds sip, pleasant realization
    f10 = [row[:] for row in f9]
    f10[6][4] = P
    save(f10, "coffee_5x", 10)

    # 11: Lowers slightly, happy cheeks
    f11 = [row[:] for row in base]
    draw_mug_hand(f11, 11, 7)
    f11[6][4] = P; f11[6][11] = P
    save(f11, "coffee_5x", 11)

    # 12: Steam dances again
    f12 = [row[:] for row in f11]
    f12[5][12] = W; f12[4][13] = W
    save(f12, "coffee_5x", 12)

    # 13: Ready for a deep, hearty sip!
    f13 = [row[:] for row in base]
    draw_mug_sip(f13, 10, 6)
    save(f13, "coffee_5x", 13)

    # 14: Deep sip — bliss state
    f14 = [row[:] for row in base]
    draw_mug_sip(f14, 10, 6)
    f14[5][5] = CD; f14[5][10] = CD
    f14[6][4] = P; f14[6][11] = P
    save(f14, "coffee_5x", 14)

    # 15: Savoring the coffee notes
    f15 = [row[:] for row in f14]
    f15[4][11] = W
    save(f15, "coffee_5x", 15)

    # 16: Still savoring
    save(f14, "coffee_5x", 16)

    # 17: Mug lowers to chest
    f17 = [row[:] for row in base]
    draw_mug_hand(f17, 11, 7)
    f17[5][5] = CD; f17[5][10] = CD
    save(f17, "coffee_5x", 17)

    # 18: Warm breath exhale puff (peaceful)
    f18 = [row[:] for row in base]
    draw_mug_hand(f18, 11, 7)
    f18[4][7] = W; f18[3][8] = W
    save(f18, "coffee_5x", 18)

    # 19: Exhale floats away
    f19 = [row[:] for row in base]
    draw_mug_hand(f19, 11, 7)
    f19[2][8] = W; f19[1][9] = W
    save(f19, "coffee_5x", 19)

    # 20: Glances down at remaining coffee
    f20 = [row[:] for row in base]
    draw_mug_hand(f20, 11, 7)
    f20[5][5] = C; f20[5][10] = C; f20[6][5] = E; f20[6][10] = E # looking down
    save(f20, "coffee_5x", 20)

    # 21: Starts putting mug back on desk
    f21 = [row[:] for row in base]
    draw_mug_hand(f21, 12, 8)
    save(f21, "coffee_5x", 21)

    # 22: Mug safely on desk
    f22 = [row[:] for row in base]
    draw_mug_desk(f22, 13, 8)
    f22[7][12] = C
    save(f22, "coffee_5x", 22)

    # 23: Releases handle
    f23 = [row[:] for row in base]
    draw_mug_desk(f23, 13, 8)
    save(f23, "coffee_5x", 23)

    # 24: Happy full belly / returns to serene idle
    save(base, "coffee_5x", 24)

# ==============================================================
# WIZARD: Helper hat & wand drawers
# ==============================================================
def draw_wizard_hat(grid, star_color=Y):
    # Purple wizard cone hat
    for x in range(3, 13): grid[3][x] = PU
    for x in range(5, 11): grid[2][x] = PU
    for x in range(6, 9): grid[1][x] = PU
    grid[0][7] = PU; grid[0][8] = star_color
    grid[2][6] = star_color

def draw_wand(grid, wx=12, wy=6, glow=Y):
    # Wand: brown shaft + glowing tip
    grid[wy][wx] = BR
    grid[wy-1][wx] = glow

# ==============================================================
# WIZARD: Original (6 frames)
# ==============================================================
def gen_wizard_orig():
    base = get_base()
    f0 = [row[:] for row in base]
    draw_wizard_hat(f0)
    save(f0, "wizard_orig", 0)

    f1 = [row[:] for row in f0]
    draw_wand(f1, 12, 6, Y)
    save(f1, "wizard_orig", 1)

    f2 = [row[:] for row in f0]
    f2[5][11] = BR; f2[4][10] = Y
    f2[1][10] = CY; f2[2][12] = BL; f2[1][13] = Y; f2[0][11] = W
    save(f2, "wizard_orig", 2)

    f3 = [row[:] for row in f0]
    f3[1][3] = Y; f3[2][1] = PU; f3[3][2] = CY
    f3[1][12] = Y; f3[2][14] = BL; f3[3][13] = W
    f3[5][5] = CY; f3[5][10] = CY
    save(f3, "wizard_orig", 3)

    f4 = [row[:] for row in f0]
    f4[4][4] = Y; f4[6][1] = PU; f4[7][14] = CY
    save(f4, "wizard_orig", 4)
    save(base, "wizard_orig", 5)

# ==============================================================
# WIZARD: 3x Extended (18 frames)
# ==============================================================
def gen_wizard_3x():
    base = get_base()

    # 0: Magic eyes glint (anticipation)
    f0 = [row[:] for row in base]
    f0[5][5] = CY; f0[5][10] = CY
    save(f0, "wizard_3x", 0)

    # 1: Hat begins to materialize (translucent purple brim)
    f1 = [row[:] for row in base]
    for x in range(4, 12): f1[3][x] = PU
    f1[2][7] = PU; f1[2][8] = PU
    save(f1, "wizard_3x", 1)

    # 2: Full wizard hat forms, star shines
    f2 = [row[:] for row in base]
    draw_wizard_hat(f2, W)
    save(f2, "wizard_3x", 2)

    # 3: Hat star turns gold
    f3 = [row[:] for row in base]
    draw_wizard_hat(f3, Y)
    save(f3, "wizard_3x", 3)

    # 4: Reaches paw into cloak
    f4 = [row[:] for row in f3]
    f4[7][12] = C
    save(f4, "wizard_3x", 4)

    # 5: Pulls out wand
    f5 = [row[:] for row in f3]
    draw_wand(f5, 12, 6, Y)
    save(f5, "wizard_3x", 5)

    # 6: Wand tip starts charging (cyan spark)
    f6 = [row[:] for row in f3]
    draw_wand(f6, 12, 6, CY)
    f6[4][13] = W
    save(f6, "wizard_3x", 6)

    # 7: Magic charge builds (swirling particles around wand)
    f7 = [row[:] for row in f3]
    draw_wand(f7, 12, 6, W)
    f7[4][11] = CY; f7[3][13] = Y; f7[6][13] = BL
    save(f7, "wizard_3x", 7)

    # 8: Wand raises up high to cast
    f8 = [row[:] for row in f3]
    f8[4][11] = BR; f8[3][11] = W
    f8[2][11] = Y; f8[2][12] = CY
    save(f8, "wizard_3x", 8)

    # 9: The Cast! Magic arc sweeps across top
    f9 = [row[:] for row in f3]
    f9[4][11] = BR; f9[3][11] = CY
    f9[1][6] = Y; f9[1][8] = W; f9[1][11] = CY; f9[0][9] = Y
    save(f9, "wizard_3x", 9)

    # 10: Constellation rune appears overhead
    f10 = [row[:] for row in f3]
    draw_wand(f10, 12, 6, Y)
    f10[0][4] = Y; f10[1][3] = W; f10[0][11] = CY; f10[1][12] = Y
    f10[5][5] = CY; f10[5][10] = CY
    save(f10, "wizard_3x", 10)

    # 11: Big burst: magical particles shower down
    f11 = [row[:] for row in f3]
    f11[2][1] = PU; f11[3][2] = CY; f11[2][14] = BL; f11[3][13] = W
    f11[0][6] = Y; f11[1][9] = W
    f11[5][5] = W; f11[5][10] = W
    save(f11, "wizard_3x", 11)

    # 12: Falling star sparkle cascade
    f12 = [row[:] for row in f3]
    f12[4][1] = Y; f12[6][2] = CY; f12[4][14] = Y; f12[6][13] = PU
    f12[1][7] = W
    save(f12, "wizard_3x", 12)

    # 13: Sparks drift to the ground
    f13 = [row[:] for row in f3]
    draw_wand(f13, 12, 7, GR)
    f13[8][2] = CY; f13[8][13] = Y
    save(f13, "wizard_3x", 13)

    # 14: Wand lowers, Claude tips hat with paw
    f14 = [row[:] for row in f3]
    f14[2][4] = C  # paw tips brim
    save(f14, "wizard_3x", 14)

    # 15: Proud blush
    f15 = [row[:] for row in f3]
    f15[6][4] = P; f15[6][11] = P
    save(f15, "wizard_3x", 15)

    # 16: Hat star gives final sparkle
    f16 = [row[:] for row in f3]
    draw_wizard_hat(f16, W)
    save(f16, "wizard_3x", 16)

    # 17: Hat vanishes in tiny puff of purple stardust, back to base
    f17 = [row[:] for row in base]
    f17[3][6] = PU; f17[2][8] = Y
    save(f17, "wizard_3x", 17)

# ==============================================================
# WIZARD: 5x Extended (30 frames)
# ==============================================================
def gen_wizard_5x():
    base = get_base()

    # 00: Calm focus
    save(base, "wizard_5x", 0)

    # 01: Eyes ignite cyan magic
    f1 = [row[:] for row in base]
    f1[5][5] = CY; f1[5][10] = CY
    save(f1, "wizard_5x", 1)

    # 02: Magic circle starts forming around feet
    f2 = [row[:] for row in f1]
    f2[11][2] = PU; f2[11][13] = PU
    save(f2, "wizard_5x", 2)

    # 03: Wizard hat begins to materialize (sparkle rim)
    f3 = [row[:] for row in f1]
    for x in range(4, 12): f3[3][x] = PU
    f3[2][7] = PU; f3[2][8] = W
    save(f3, "wizard_5x", 3)

    # 04: Full wizard hat manifests, star glints
    f4 = [row[:] for row in f1]
    draw_wizard_hat(f4, W)
    save(f4, "wizard_5x", 4)

    # 05: Star glows warm yellow
    f5 = [row[:] for row in base]
    draw_wizard_hat(f5, Y)
    save(f5, "wizard_5x", 5)

    # 06: Paw reaches into robe
    f6 = [row[:] for row in f5]
    f6[7][12] = C
    save(f6, "wizard_5x", 6)

    # 07: Draws out magic wand
    f7 = [row[:] for row in f5]
    draw_wand(f7, 12, 6, Y)
    save(f7, "wizard_5x", 7)

    # 08: Examines wand, tip is quiet
    f8 = [row[:] for row in f5]
    draw_wand(f8, 12, 6, GR)
    save(f8, "wizard_5x", 8)

    # 09: Chanting begins: eyes shut in concentration
    f9 = [row[:] for row in f5]
    draw_wand(f9, 12, 6, GR)
    f9[5][5] = CD; f9[5][10] = CD
    save(f9, "wizard_5x", 9)

    # 10: Wand tip ignites with blue spark
    f10 = [row[:] for row in f5]
    draw_wand(f10, 12, 6, BL)
    f10[5][5] = CD; f10[5][10] = CD
    save(f10, "wizard_5x", 10)

    # 11: Energy increases to cyan
    f11 = [row[:] for row in f5]
    draw_wand(f11, 12, 6, CY)
    f11[4][13] = W
    save(f11, "wizard_5x", 11)

    # 12: Golden mana rings start orbiting wand
    f12 = [row[:] for row in f5]
    draw_wand(f12, 12, 6, W)
    f12[3][13] = Y; f12[5][13] = Y; f12[4][11] = CY
    save(f12, "wizard_5x", 12)

    # 13: Full mana charge — eyes open blazing cyan!
    f13 = [row[:] for row in f5]
    draw_wand(f13, 12, 6, W)
    f13[5][5] = CY; f13[5][10] = CY
    f13[2][12] = Y; f13[4][14] = CY
    save(f13, "wizard_5x", 13)

    # 14: Wand winds up backward
    f14 = [row[:] for row in f5]
    f14[5][13] = BR; f14[4][14] = W
    f14[5][5] = CY; f14[5][10] = CY
    save(f14, "wizard_5x", 14)

    # 15: Strike forward — arc of energy!
    f15 = [row[:] for row in f5]
    f15[4][11] = BR; f15[3][10] = W
    f15[2][9] = CY; f15[1][8] = Y
    save(f15, "wizard_5x", 15)

    # 16: Magic crest / rune draws across sky
    f16 = [row[:] for row in f5]
    f16[4][10] = BR; f16[3][9] = CY
    f16[0][7] = W; f16[0][8] = Y; f16[1][5] = CY; f16[1][10] = CY
    save(f16, "wizard_5x", 16)

    # 17: Secondary wand flourish
    f17 = [row[:] for row in f5]
    draw_wand(f17, 11, 5, W)
    f17[0][4] = Y; f17[0][11] = Y; f17[2][3] = BL; f17[2][12] = BL
    save(f17, "wizard_5x", 17)

    # 18: THE GRAND CONJURATION: Supernova burst overhead!
    f18 = [row[:] for row in f5]
    draw_wand(f18, 11, 5, Y)
    f18[0][5] = W; f18[0][6] = Y; f18[0][9] = Y; f18[0][10] = W
    f18[1][3] = CY; f18[1][12] = CY; f18[2][2] = PU; f18[2][13] = PU
    f18[5][5] = W; f18[5][10] = W
    save(f18, "wizard_5x", 18)

    # 19: Particle shockwave expands outward
    f19 = [row[:] for row in f5]
    draw_wand(f19, 12, 6, Y)
    f19[1][1] = Y; f19[2][14] = Y; f19[3][0] = CY; f19[3][15] = CY
    f19[0][7] = W; f19[0][8] = W
    save(f19, "wizard_5x", 19)

    # 20: Stardust starts raining down gently
    f20 = [row[:] for row in f5]
    draw_wand(f20, 12, 6, Y)
    f20[2][3] = Y; f20[3][5] = CY; f20[2][11] = Y; f20[3][13] = CY
    f20[4][2] = W; f20[4][14] = W
    save(f20, "wizard_5x", 20)

    # 21: Stardust particles cascade past shoulders
    f21 = [row[:] for row in f5]
    draw_wand(f21, 12, 6, Y)
    f21[6][2] = Y; f21[7][4] = CY; f21[6][13] = Y; f21[7][11] = CY
    save(f21, "wizard_5x", 21)

    # 22: Tiny star falls right into left paw!
    f22 = [row[:] for row in f5]
    draw_wand(f22, 12, 6, Y)
    f22[7][3] = Y  # star in left paw
    save(f22, "wizard_5x", 22)

    # 23: Claude looks at star in paw, delighted
    f23 = [row[:] for row in f5]
    draw_wand(f23, 12, 7, GR)
    f23[7][3] = W
    f23[5][5] = C; f23[5][10] = C; f23[6][4] = E; f23[5][9] = E # look down-left
    save(f23, "wizard_5x", 23)

    # 24: Star in paw sparkles gold then twinkles away
    f24 = [row[:] for row in f5]
    draw_wand(f24, 12, 7, GR)
    f24[6][3] = Y
    save(f24, "wizard_5x", 24)

    # 25: Claude lowers wand, tips wizard hat
    f25 = [row[:] for row in f5]
    f25[2][4] = C  # paw tips hat brim
    f25[6][11] = P
    save(f25, "wizard_5x", 25)

    # 26: Happy warm smile & blush
    f26 = [row[:] for row in f5]
    f26[6][4] = P; f26[6][11] = P
    save(f26, "wizard_5x", 26)

    # 27: Wand dissolves into stardust
    f27 = [row[:] for row in f5]
    f27[7][12] = Y; f27[6][13] = CY
    save(f27, "wizard_5x", 27)

    # 28: Hat star gives one final bright twinkle
    f28 = [row[:] for row in f5]
    draw_wizard_hat(f28, W)
    save(f28, "wizard_5x", 28)

    # 29: Hat dissolves into gentle purple spark, returns to idle
    f29 = [row[:] for row in base]
    f29[3][7] = PU; f29[2][8] = Y
    save(f29, "wizard_5x", 29)

def main():
    print("Generating extended preview animations...")
    gen_coffee_orig()
    gen_coffee_3x()
    gen_coffee_5x()
    gen_wizard_orig()
    gen_wizard_3x()
    gen_wizard_5x()
    print("Done! Frames saved to preview_extended/")

if __name__ == "__main__":
    main()
