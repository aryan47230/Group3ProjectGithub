import pygame
import sys
import time
import math
import random

pygame.init()

# =============================================================
#  WINDOW
# =============================================================
W, H = 1280, 860
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Murder Board — Find the Killer")
clock = pygame.time.Clock()

# =============================================================
#  ALIBI BLURBS — WRITE YOUR TEXT HERE
#  Each entry matches the order of SUSPECTS below.
#  Keep each blurb to 2-3 sentences for best display.
# =============================================================
ALIBI_BLURBS = [
    # Veronica Mitchell (Author)
    "Write Veronica's alibi here. Add as much detail as you like.",

    # John John (Student)
    "Write John John's alibi here. Add as much detail as you like.",

    # Richard Hedricks (Janitor)
    "Write Richard's alibi here. Add as much detail as you like.",

    # Ross Bob (Artist)
    "Write Ross Bob's alibi here. Add as much detail as you like.",

    # Claudia VanHelsing (Librarian)
    "Write Claudia's alibi here. Add as much detail as you like.",
]

# =============================================================
#  COLORS
# =============================================================
CORK_BASE   = (139, 101,  63)
CORK_LIGHT  = (158, 118,  75)
CORK_DARK   = (112,  79,  46)
CORK_GRAIN  = (125,  90,  54)

PHOTO_BG    = (245, 240, 228)
PHOTO_SHADE = (210, 205, 190)

RED_STRING  = (180,  30,  30)
PIN_RED     = (220,  40,  40)
PIN_SHINE   = (255, 120, 120)
PIN_DARK    = (140,  20,  20)

CARD_BG     = (245, 238, 220)
CARD_LINES  = (200, 190, 170)
CARD_BORDER = (180, 160, 130)
CARD_SHADOW = ( 80,  55,  30)

TEXT_CARD   = ( 40,  30,  20)
TEXT_DIM    = (120, 100,  70)
TEXT_LABEL  = ( 60,  40,  20)

SLOT_DASHED = (160, 120,  72)
CORRECT_COL = ( 60, 160,  80)
WRONG_COL   = (180,  50,  50)

BTN_COL     = (120,  30,  30)
BTN_HOVER   = (160,  45,  45)
BTN_TEXT    = (255, 220, 200)

ALIBI_BTN   = ( 60,  80,  50)
ALIBI_HOV   = ( 85, 115,  65)
ALIBI_TEXT  = (220, 240, 200)

SELECTED_GLOW = (255, 200,  50)

BAR_COL1    = ( 28,  22,  18)
BAR_COL2    = ( 48,  40,  28)
BAR_SHINE   = ( 95,  82,  55)

# =============================================================
#  FONTS
# =============================================================
FONT_TITLE  = pygame.font.SysFont("Courier", 20, bold=True)
FONT_MED    = pygame.font.SysFont("Courier", 14, bold=True)
FONT_SM     = pygame.font.SysFont("Courier", 11)
FONT_XS     = pygame.font.SysFont("Courier", 10)
FONT_WIN    = pygame.font.SysFont("Courier", 36, bold=True)
FONT_HAND   = pygame.font.SysFont("Courier", 11)
FONT_ALIBI  = pygame.font.SysFont("Courier", 12)

# =============================================================
#  DATA
# =============================================================
SUSPECTS = [
    {"name": "Veronica Mitchell", "role": "Author"},
    {"name": "John John",         "role": "Student"},
    {"name": "Richard Hedricks",  "role": "Janitor"},
    {"name": "Ross Bob",          "role": "Artist"},
    {"name": "Claudia VanHelsing","role": "Librarian"},
]

CORRECT = {
    "suspect":  "Ross Bob",
    "location": "By the Bell",
    "weapon":   "Knife",
}

SLOT_KINDS = ["location", "weapon"]

WIN_IDX = next(i for i, s in enumerate(SUSPECTS)
               if s["name"] == CORRECT["suspect"])

# =============================================================
#  CORK BOARD — pre-render
# =============================================================
def make_cork_surface():
    surf = pygame.Surface((W, H))
    surf.fill(CORK_BASE)
    rng = random.Random(42)
    for _ in range(700):
        x1  = rng.randint(0, W)
        y1  = rng.randint(0, H)
        x2  = x1 + rng.randint(-70, 70)
        y2  = y1 + rng.randint(-10, 10)
        col = rng.choice([CORK_LIGHT, CORK_DARK, CORK_GRAIN])
        pygame.draw.line(surf, col, (x1, y1), (x2, y2), 1)
    vig = pygame.Surface((W, H), pygame.SRCALPHA)
    for r in range(0, max(W, H) // 2, 6):
        a = max(0, 75 - r // 5)
        pygame.draw.ellipse(vig, (40, 20, 5, a),
                            (W//2-r, H//2-r, r*2, r*2), 6)
    surf.blit(vig, (0, 0))
    return surf

CORK_SURF = make_cork_surface()

def draw_cork():
    screen.blit(CORK_SURF, (0, 0))

# =============================================================
#  LAYOUT
# =============================================================
CARD_W        = 165
CARD_HEADER_H = 95
CARD_GAP      = 22
CARDS_Y       = 55
CARDS_START_X = (W - (5 * CARD_W + 4 * CARD_GAP)) // 2
PHOTO_PAD     = 5
SLOT_PADDING  = 6
SLOT_MARGIN   = 8
CLUE_ZONE_Y   = 570

def card_x(i):
    return CARDS_START_X + i * (CARD_W + CARD_GAP)

def card_total_height(i):
    h = CARD_HEADER_H
    for kind in SLOT_KINDS:
        clue = slots[i][kind]
        h += (clue["ph"] if clue else 44) + SLOT_PADDING * 2
    h += 26   # room for alibi button
    return h

def slot_top_y(card_i, slot_i):
    y = CARDS_Y + CARD_HEADER_H + SLOT_PADDING
    for si in range(slot_i):
        kind = SLOT_KINDS[si]
        clue = slots[card_i][kind]
        y += (clue["ph"] if clue else 44) + SLOT_PADDING * 2
    return y

def slot_rect(card_i, slot_i):
    clue = slots[card_i][SLOT_KINDS[slot_i]]
    sw   = CARD_W - SLOT_MARGIN * 2
    sh   = clue["ph"] if clue else 44
    return pygame.Rect(card_x(card_i) + SLOT_MARGIN,
                       slot_top_y(card_i, slot_i), sw, sh)

def card_rect(i):
    return pygame.Rect(card_x(i), CARDS_Y, CARD_W, card_total_height(i))

def alibi_btn_rect(i):
    cr = card_rect(i)
    return pygame.Rect(cr.x + 8, cr.bottom - 22, cr.w - 16, 18)

# =============================================================
#  CLUE LOADING
# =============================================================
def load_clue(filename, label, kind, img_w, img_h):
    img  = pygame.transform.scale(pygame.image.load(filename), (img_w, img_h))
    pw   = img_w + PHOTO_PAD * 2
    ph   = img_h + PHOTO_PAD * 2 + 16
    surf = pygame.Surface((pw, ph))
    surf.fill(PHOTO_BG)
    pygame.draw.rect(surf, PHOTO_SHADE, (0, 0, pw, ph), 1)
    surf.blit(img, (PHOTO_PAD, PHOTO_PAD))
    lbl  = FONT_HAND.render(label, True, TEXT_LABEL)
    surf.blit(lbl, lbl.get_rect(centerx=pw//2, y=img_h + PHOTO_PAD + 2))
    return surf, pw, ph

def make_clues():
    clues = []
    loc_data = [
        ("loc_cbtf.png",     "CBTF Testing Center",    128, 64),
        ("loc_espresso.png", "Espresso Royal",           92, 68),
        ("loc_restroom.png", "Womens Restroom",          64, 64),
        ("loc_bell.png",     "By the Bell",              64, 64),
        ("loc_smoking.png",  "Unofficial Smoking Area",  76, 108),
    ]
    wpn_data = [
        ("wpn_knife.png",       "Knife",        64,  64),
        ("wpn_gun.png",         "Gun",          64,  64),
        ("wpn_poison.png",      "Poison",       64,  64),
        ("wpn_candlestick.png", "Candlestick",  104, 64),
        ("wpn_sword.png",       "Sword",        64,  100),
    ]
    rng = random.Random(7)
    for filename, label, iw, ih in loc_data + wpn_data:
        kind         = "location" if filename.startswith("loc") else "weapon"
        surf, pw, ph = load_clue(filename, label, kind, iw, ih)
        clues.append({
            "label":  label, "kind":   kind,
            "surf":   surf,  "w":      pw,   "h":      ph,
            "pw":     pw,    "ph":     ph,
            "angle":  rng.uniform(-10, 10),
            "placed": False, "slot":   None,
            "rect":   None,  "home":   None,
        })
    return clues

ALL_CLUES = make_clues()

def assign_clue_positions():
    rng   = random.Random(99)
    loc_c = [c for c in ALL_CLUES if c["kind"] == "location"]
    wpn_c = [c for c in ALL_CLUES if c["kind"] == "weapon"]
    x = 25
    for c in loc_c:
        y = CLUE_ZONE_Y + rng.randint(8, max(8, H - CLUE_ZONE_Y - c["h"] - 50))
        c["home"] = pygame.Rect(x, y, c["w"], c["h"])
        c["rect"] = pygame.Rect(x, y, c["w"], c["h"])
        x += c["w"] + rng.randint(6, 18)
    x = W // 2 + 10
    for c in wpn_c:
        y = CLUE_ZONE_Y + rng.randint(8, max(8, H - CLUE_ZONE_Y - c["h"] - 50))
        c["home"] = pygame.Rect(x, y, c["w"], c["h"])
        c["rect"] = pygame.Rect(x, y, c["w"], c["h"])
        x += c["w"] + rng.randint(6, 18)

assign_clue_positions()

# =============================================================
#  SLOTS STATE
# =============================================================
slots = [{k: None for k in SLOT_KINDS} for _ in range(5)]

# =============================================================
#  ALIBI STATE
# =============================================================
# alibi_state: None | {"suspect": i, "start": t, "text": str, "chars": n}
alibi_state    = None
ALIBI_SPEED    = 0.03   # seconds per character
WAVE_BARS      = 12
_wave_rng      = random.Random(55)
WAVE_BASE_H    = [_wave_rng.randint(4, 16) for _ in range(WAVE_BARS)]

def start_alibi(i):
    global alibi_state
    alibi_state = {
        "suspect": i,
        "start":   time.time(),
        "text":    ALIBI_BLURBS[i],
        "chars":   0,
    }

def close_alibi():
    global alibi_state
    alibi_state = None

def wrap_text(text, font, max_width):
    words  = text.split()
    lines  = []
    line   = ""
    for w in words:
        test = line + (" " if line else "") + w
        if font.size(test)[0] <= max_width:
            line = test
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines

def draw_alibi_popup():
    if alibi_state is None:
        return
    now   = time.time()
    t     = now - alibi_state["start"]
    full  = alibi_state["text"]
    chars = min(len(full), int(t / ALIBI_SPEED))
    alibi_state["chars"] = chars
    visible = full[:chars]
    cursor  = "|" if int(now * 2) % 2 == 0 else " "

    si      = alibi_state["suspect"]
    cr      = card_rect(si)
    pop_w   = 320
    pop_x   = min(cr.centerx - pop_w // 2, W - pop_w - 10)
    pop_x   = max(pop_x, 10)
    pop_y   = cr.bottom + 6

    # waveform animation height
    wave_h  = 30
    lines   = wrap_text(visible + cursor, FONT_ALIBI, pop_w - 20)
    pop_h   = wave_h + 14 + len(lines) * 16 + 14

    # clamp to screen
    if pop_y + pop_h > H - 10:
        pop_y = cr.y - pop_h - 6

    # shadow
    pygame.draw.rect(screen, (20, 12, 5),
                     (pop_x + 3, pop_y + 3, pop_w, pop_h), border_radius=5)
    # body — manila card
    pygame.draw.rect(screen, CARD_BG,
                     (pop_x, pop_y, pop_w, pop_h), border_radius=5)
    pygame.draw.rect(screen, CARD_BORDER,
                     (pop_x, pop_y, pop_w, pop_h), 1, border_radius=5)

    # tape at top
    tape = pygame.Surface((pop_w, 10), pygame.SRCALPHA)
    tape.fill((220, 215, 150, 140))
    screen.blit(tape, (pop_x, pop_y))

    # waveform bars
    bw    = (pop_w - 20) // WAVE_BARS
    bar_x = pop_x + 10
    for bi in range(WAVE_BARS):
        bh = int(WAVE_BASE_H[bi] + 8 * math.sin(t * 5 + bi * 0.8))
        bh = max(3, min(wave_h - 2, bh))
        col = (80, 160, 100) if bi % 2 == 0 else (60, 130, 80)
        pygame.draw.rect(screen, col,
                         (bar_x + bi * bw + 2,
                          pop_y + 10 + (wave_h - bh) // 2,
                          max(2, bw - 4), bh), border_radius=2)

    # "REC" dot
    rec_col = (220, 50, 50) if int(t * 2) % 2 == 0 else (150, 30, 30)
    pygame.draw.circle(screen, rec_col, (pop_x + pop_w - 16, pop_y + 24), 5)
    rec_lbl = FONT_XS.render("REC", True, (180, 40, 40))
    screen.blit(rec_lbl, (pop_x + pop_w - 38, pop_y + 18))

    # divider
    pygame.draw.line(screen, CARD_LINES,
                     (pop_x + 8, pop_y + wave_h + 12),
                     (pop_x + pop_w - 8, pop_y + wave_h + 12), 1)

    # transcribed text
    ty = pop_y + wave_h + 18
    for line in lines:
        ls = FONT_ALIBI.render(line, True, TEXT_CARD)
        screen.blit(ls, (pop_x + 10, ty))
        ty += 16

    # close button
    close_r = pygame.Rect(pop_x + pop_w - 22, pop_y + 3, 18, 14)
    pygame.draw.rect(screen, CARD_BORDER, close_r, border_radius=3)
    cx_s = FONT_XS.render("✕", True, TEXT_CARD)
    screen.blit(cx_s, cx_s.get_rect(center=close_r.center))
    return close_r   # return so main loop can check click

# =============================================================
#  ROSS BOB PIXEL ART SPRITE
# =============================================================
def draw_ross_bob(cx, cy, scale=1):
    """Pixel art of Ross Bob (artist) at center cx, cy."""
    def r(x, y, w, h, col):
        pygame.draw.rect(screen, col,
                         (int(cx + x*scale), int(cy + y*scale),
                          max(1, int(w*scale)), max(1, int(h*scale))))

    SKIN  = (210, 170, 130)
    SHIRT = (80,  110, 160)   # blue artist shirt
    PANTS = (55,   50,  70)
    HAIR  = (60,   45,  30)
    BERET = (140,  40,  40)   # red beret — he's an artist
    SHOES = (30,   25,  18)
    BEARD = (80,   60,  40)

    # shoes
    r(-12, 44, 12, 6, SHOES)
    r(  2, 44, 12, 6, SHOES)
    # legs
    r(-12, 26, 10, 20, PANTS)
    r(  2, 26, 10, 20, PANTS)
    # torso
    r(-14, 4, 28, 24, SHIRT)
    # collar
    r( -4, 4,  8,  6, (200, 195, 180))
    # arms
    r(-22, 6, 10, 18, SHIRT)
    r( 12, 6, 10, 18, SHIRT)
    # hands
    r(-22, 22,  9,  8, SKIN)
    r( 12, 22,  9,  8, SKIN)
    # paintbrush in right hand
    r( 20, 18,  3, 14, (160, 120, 70))
    r( 21, 30,  2,  4, (80, 140, 200))
    # head
    r(-12, -18, 24, 24, SKIN)
    # hair
    r(-12, -18, 24,  8, HAIR)
    # beret
    r(-14, -22, 28,  8, BERET)
    r( -6, -26, 16,  6, BERET)
    r(  6, -28,  4,  4, BERET)   # pompom
    # eyes
    r( -8,  -8,  5,  5, (40, 35, 50))
    r(  4,  -8,  5,  5, (40, 35, 50))
    # eyebrows
    r( -9, -11,  6,  2, HAIR)
    r(  3, -11,  6,  2, HAIR)
    # beard / stubble
    r(-10,   2, 20,  6, BEARD)
    # mouth
    r( -5,  -2,  10,  3, (160, 100, 80))
    # smug smirk
    r(  2,  -2,   5,  2, (180, 120, 90))

# =============================================================
#  PRISON BARS ANIMATION
# =============================================================
BAR_COUNT = 7

def draw_prison_scene(t, arrest_start_t):
    """Full arrest scene: Ross Bob sprite + bars dropping."""
    elapsed = t - arrest_start_t

    # dark backdrop
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((10, 5, 2, 220))
    screen.blit(overlay, (0, 0))

    # scene frame
    fw, fh  = 280, 320
    fx      = W // 2 - fw // 2
    fy      = H // 2 - fh // 2 - 20

    # cell background
    pygame.draw.rect(screen, (35, 28, 20), (fx, fy, fw, fh))
    pygame.draw.rect(screen, (80, 65, 40), (fx, fy, fw, fh), 3)

    # brick wall pattern
    for row in range(0, fh, 16):
        offset = 20 if (row // 16) % 2 else 0
        for col in range(-offset, fw, 40):
            br = pygame.Rect(fx + col + 1, fy + row + 1, 38, 14)
            pygame.draw.rect(screen, (45, 35, 25), br)
            pygame.draw.rect(screen, (60, 48, 32), br, 1)

    # floor
    pygame.draw.rect(screen, (55, 42, 28), (fx, fy + fh - 40, fw, 40))

    # draw Ross Bob in center of cell
    draw_ross_bob(W // 2, H // 2 + 50, scale=3)

    # prison bars — animate dropping from top
    bar_w   = fw // BAR_COUNT
    bar_speed = 400.0
    all_done  = True
    for bi in range(BAR_COUNT):
        delay    = bi * 0.06
        if elapsed > delay:
            progress = min(1.0, (elapsed - delay) * bar_speed / fh)
        else:
            progress = 0.0
        bar_h = int(fh * progress)
        if bar_h < fh:
            all_done = False
        bx = fx + bi * bar_w
        # bar shadow
        pygame.draw.rect(screen, (15, 10, 5),
                         (bx + 3, fy, bar_w - 8, bar_h))
        # bar body
        col = BAR_COL1 if bi % 2 == 0 else BAR_COL2
        pygame.draw.rect(screen, col, (bx + 1, fy, bar_w - 6, bar_h))
        # shine
        pygame.draw.rect(screen, BAR_SHINE, (bx + 2, fy, 3, bar_h))
        # rivet at top
        if bar_h > 10:
            pygame.draw.circle(screen, (120, 100, 60),
                                (bx + bar_w // 2, fy + 8), 4)

    # horizontal bar across top
    if elapsed > 0.3:
        pygame.draw.rect(screen, (60, 50, 30), (fx, fy, fw, 12))
        pygame.draw.rect(screen, BAR_SHINE,    (fx, fy,  fw,  3))

    # label
    if elapsed > 0.8:
        lbl = FONT_WIN.render("ARRESTED!", True, (220, 50, 50))
        screen.blit(lbl, lbl.get_rect(center=(W // 2, fy - 40)))
        name = FONT_MED.render(f"{CORRECT['suspect']} has been taken into custody.",
                                True, CARD_BG)
        screen.blit(name, name.get_rect(center=(W // 2, fy + fh + 22)))
        clue = FONT_SM.render(
            f"Weapon: {CORRECT['weapon']}   Location: {CORRECT['location']}",
            True, (180, 160, 120))
        screen.blit(clue, clue.get_rect(center=(W // 2, fy + fh + 46)))

    return all_done and elapsed > 2.5

# =============================================================
#  DRAW HELPERS
# =============================================================
def draw_pin(x, y):
    pygame.draw.circle(screen, PIN_DARK,  (x, y), 7)
    pygame.draw.circle(screen, PIN_RED,   (x, y), 6)
    pygame.draw.circle(screen, PIN_SHINE, (x-2, y-2), 2)

def draw_tape(rect):
    tape = pygame.Surface((rect.w, 14), pygame.SRCALPHA)
    tape.fill((220, 215, 150, 130))
    screen.blit(tape, (rect.x, rect.y - 3))

def draw_red_strings():
    for i in range(5):
        cr = card_rect(i)
        for si, kind in enumerate(SLOT_KINDS):
            if slots[i][kind]:
                sr  = slot_rect(i, si)
                p1  = (cr.centerx, cr.y + CARD_HEADER_H // 2)
                p2  = (sr.centerx, sr.top)
                mid = ((p1[0]+p2[0])//2, (p1[1]+p2[1])//2 + 15)
                pts = []
                for t2 in range(11):
                    tt = t2 / 10
                    x  = int((1-tt)**2*p1[0] + 2*(1-tt)*tt*mid[0] + tt**2*p2[0])
                    y  = int((1-tt)**2*p1[1] + 2*(1-tt)*tt*mid[1] + tt**2*p2[1])
                    pts.append((x, y))
                if len(pts) >= 2:
                    pygame.draw.lines(screen, RED_STRING, False, pts, 2)

def draw_suspect_card(i, mouse_pos):
    s      = SUSPECTS[i]
    cr     = card_rect(i)
    is_hov = (phase == "select_suspect" and
              cr.collidepoint(mouse_pos) and not dragging)

    # shadow
    pygame.draw.rect(screen, CARD_SHADOW,
                     pygame.Rect(cr.x+4, cr.y+4, cr.w, cr.h), border_radius=3)

    # hover glow
    if is_hov:
        pygame.draw.rect(screen, (200, 180, 80),
                         pygame.Rect(cr.x-2, cr.y-2, cr.w+4, cr.h+4),
                         border_radius=5)

    # card body
    pygame.draw.rect(screen, CARD_BG, cr, border_radius=3)

    # ruled lines
    for ly in range(cr.y + 28, cr.y + CARD_HEADER_H - 4, 12):
        pygame.draw.line(screen, CARD_LINES, (cr.x+8, ly), (cr.right-8, ly), 1)
    pygame.draw.line(screen, (200, 150, 150),
                     (cr.x+22, cr.y+4), (cr.x+22, cr.y+CARD_HEADER_H-4), 1)

    pygame.draw.rect(screen, CARD_BORDER, cr, 1, border_radius=3)
    draw_tape(cr)
    draw_pin(cr.centerx, cr.y - 2)

    # name
    y_off = cr.y + 10
    for part in s["name"].split():
        ns = FONT_MED.render(part, True, TEXT_CARD)
        screen.blit(ns, ns.get_rect(centerx=cr.centerx, y=y_off))
        y_off += 16
    rs = FONT_XS.render(f"— {s['role']} —", True, TEXT_DIM)
    screen.blit(rs, rs.get_rect(centerx=cr.centerx, y=y_off+2))

    # slots
    for si, kind in enumerate(SLOT_KINDS):
        sr   = slot_rect(i, si)
        clue = slots[i][kind]
        if clue:
            scale  = (sr.w - 4) / clue["pw"]
            dw     = int(clue["pw"] * scale)
            dh     = int(clue["ph"] * scale)
            scaled = pygame.transform.scale(clue["surf"], (dw, dh))
            screen.blit(scaled, (sr.x + (sr.w-dw)//2, sr.y))
            pygame.draw.rect(screen, CARD_BORDER,
                             pygame.Rect(sr.x, sr.y, sr.w, dh), 1, border_radius=2)
        else:
            dr = pygame.Rect(card_x(i)+SLOT_MARGIN, slot_top_y(i, si),
                             CARD_W-SLOT_MARGIN*2, 44)
            pygame.draw.rect(screen, (155, 130, 95), dr, border_radius=3)
            for dx in range(dr.x+4, dr.right-4, 8):
                pygame.draw.line(screen, SLOT_DASHED, (dx, dr.y+2), (dx+4, dr.y+2), 1)
                pygame.draw.line(screen, SLOT_DASHED,
                                 (dx, dr.bottom-3), (dx+4, dr.bottom-3), 1)
            lbl = FONT_XS.render(kind.upper(), True, TEXT_DIM)
            screen.blit(lbl, lbl.get_rect(center=dr.center))

    # alibi button
    ab  = alibi_btn_rect(i)
    is_alibi_active = alibi_state is not None and alibi_state["suspect"] == i
    ab_col = ALIBI_HOV if ab.collidepoint(mouse_pos) or is_alibi_active else ALIBI_BTN
    pygame.draw.rect(screen, ab_col, ab, border_radius=3)
    ab_lbl = FONT_XS.render("▶ ALIBI", True, ALIBI_TEXT)
    screen.blit(ab_lbl, ab_lbl.get_rect(center=ab.center))

    # "CLICK TO ARREST" hint
    if phase == "select_suspect":
        al = FONT_XS.render("CLICK TO ARREST", True, (160, 30, 30))
        screen.blit(al, al.get_rect(centerx=cr.centerx, y=cr.bottom + 3))

def draw_clue_photo(c, hovered=False, alpha=255, use_angle=True):
    surf  = c["surf"].copy()
    if alpha < 255:
        surf.set_alpha(alpha)
    angle = c["angle"] if use_angle else 0
    if hovered:
        pygame.draw.rect(surf, (255, 200, 50),
                         (0, 0, surf.get_width(), surf.get_height()), 3)
    if angle != 0:
        rot = pygame.transform.rotate(surf, angle)
        cx  = c["rect"].x + c["w"] // 2
        cy  = c["rect"].y + c["h"] // 2
        screen.blit(rot, (cx - rot.get_width()//2, cy - rot.get_height()//2))
    else:
        screen.blit(surf, (c["rect"].x, c["rect"].y))

def draw_clue_zone_divider():
    tape = pygame.Surface((W, 16), pygame.SRCALPHA)
    tape.fill((200, 195, 130, 140))
    screen.blit(tape, (0, CLUE_ZONE_Y - 8))
    screen.blit(FONT_HAND.render("LOCATIONS ▼", True, (80,55,25)), (25, CLUE_ZONE_Y-22))
    screen.blit(FONT_HAND.render("WEAPONS ▼",   True, (80,55,25)), (W//2+10, CLUE_ZONE_Y-22))

def draw_title_card():
    tr = pygame.Rect(W//2-230, 8, 460, 36)
    pygame.draw.rect(screen, CARD_BG, tr, border_radius=3)
    pygame.draw.rect(screen, CARD_BORDER, tr, 1, border_radius=3)
    draw_tape(tr)
    t = FONT_TITLE.render("MURDER BOARD  —  FIND THE KILLER", True, (140,30,30))
    screen.blit(t, t.get_rect(center=tr.center))
    draw_pin(tr.centerx - 90, tr.y - 2)
    draw_pin(tr.centerx + 90, tr.y - 2)

def draw_status_banner():
    if phase == "board":
        msg = ("All clues placed! Click a suspect card to make your arrest."
               if any_card_full() else
               "Drag location and weapon photos onto a suspect card.")
    elif phase == "select_suspect":
        msg = "Click the suspect you think is the murderer."
    else:
        return
    bar = pygame.Surface((W, 28), pygame.SRCALPHA)
    bar.fill((20, 10, 5, 180))
    screen.blit(bar, (0, H - 28))
    s = FONT_SM.render(msg, True, (220, 200, 160))
    screen.blit(s, s.get_rect(center=(W//2, H - 14)))

# =============================================================
#  HELPERS
# =============================================================
def any_card_full():
    return any(all(slots[i][k] is not None for k in SLOT_KINDS) for i in range(5))

def clue_hit(c, mouse):
    cx = c["rect"].x + c["w"] // 2
    cy = c["rect"].y + c["h"] // 2
    return pygame.Rect(cx-c["w"]//2, cy-c["h"]//2, c["w"], c["h"]).collidepoint(mouse)

def check_suspect(i):
    s      = SUSPECTS[i]
    loc_ok = slots[i]["location"] and \
             slots[i]["location"]["label"].lower() == CORRECT["location"].lower()
    wpn_ok = slots[i]["weapon"] and \
             slots[i]["weapon"]["label"].lower()   == CORRECT["weapon"].lower()
    return "correct" if (s["name"] == CORRECT["suspect"] and loc_ok and wpn_ok) else "wrong"

# =============================================================
#  GAME STATE
# =============================================================
dragging      = None
drag_offset   = (0, 0)
phase         = "board"
wrong_timer   = 0.0
arrest_start  = 0.0

# =============================================================
#  MAIN LOOP
# =============================================================
running = True

while running:
    draw_cork()
    mouse = pygame.mouse.get_pos()
    now   = time.time()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            # close alibi popup if clicking X
            if alibi_state is not None:
                # check close button (drawn last frame — approximate position)
                si  = alibi_state["suspect"]
                cr  = card_rect(si)
                pop_w = 320
                pop_x = min(cr.centerx - pop_w//2, W - pop_w - 10)
                pop_x = max(pop_x, 10)
                pop_y = cr.bottom + 6
                close_r = pygame.Rect(pop_x + pop_w - 22, pop_y + 3, 18, 14)
                if close_r.collidepoint(mouse):
                    close_alibi()
                    continue

            # alibi buttons
            clicked_alibi = False
            for i in range(5):
                ab = alibi_btn_rect(i)
                if ab.collidepoint(mouse):
                    if alibi_state and alibi_state["suspect"] == i:
                        close_alibi()
                    else:
                        start_alibi(i)
                    clicked_alibi = True
                    break
            if clicked_alibi:
                continue

            # drag clues
            if phase in ("board", "select_suspect"):
                for c in reversed(ALL_CLUES):
                    if clue_hit(c, mouse):
                        if c["placed"]:
                            ci, si = c["slot"]
                            slots[ci][SLOT_KINDS[si]] = None
                            c["placed"] = False
                            c["slot"]   = None
                        dragging    = c
                        drag_offset = (mouse[0]-c["rect"].x, mouse[1]-c["rect"].y)
                        c["angle"]  = 0
                        if phase == "select_suspect":
                            phase = "board"
                        break

            # suspect selection
            if dragging is None and phase == "select_suspect":
                for i in range(5):
                    cr = card_rect(i)
                    if cr.collidepoint(mouse) and not alibi_btn_rect(i).collidepoint(mouse):
                        result = check_suspect(i)
                        if result == "correct":
                            phase        = "arrest"
                            arrest_start = now
                        else:
                            phase      = "wrong"
                            wrong_timer= now
                        break

            # enter select mode on card click when board is ready
            if dragging is None and phase == "board" and any_card_full():
                for i in range(5):
                    cr = card_rect(i)
                    if (cr.collidepoint(mouse) and
                            not alibi_btn_rect(i).collidepoint(mouse) and
                            not any(clue_hit(c, mouse) for c in ALL_CLUES if not c["placed"])):
                        phase = "select_suspect"
                        break

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if dragging:
                dropped = False
                for ci in range(5):
                    for si2, kind in enumerate(SLOT_KINDS):
                        if dragging["kind"] == kind:
                            approx = pygame.Rect(
                                card_x(ci)+SLOT_MARGIN,
                                slot_top_y(ci, si2),
                                CARD_W-SLOT_MARGIN*2, 80)
                            if approx.collidepoint(mouse):
                                existing = slots[ci][kind]
                                if existing:
                                    existing["placed"] = False
                                    existing["slot"]   = None
                                    existing["rect"]   = pygame.Rect(
                                        existing["home"].x, existing["home"].y,
                                        existing["w"], existing["h"])
                                    existing["angle"]  = random.uniform(-10, 10)
                                slots[ci][kind]    = dragging
                                dragging["placed"] = True
                                dragging["slot"]   = (ci, si2)
                                dragging["rect"]   = pygame.Rect(
                                    approx.x, approx.y, approx.w, approx.h)
                                dragging["angle"]  = 0
                                dropped = True
                                break
                    if dropped:
                        break
                if not dropped:
                    dragging["rect"]  = pygame.Rect(
                        dragging["home"].x, dragging["home"].y,
                        dragging["w"], dragging["h"])
                    dragging["angle"] = random.uniform(-10, 10)
                dragging = None
                if any_card_full() and phase == "board":
                    phase = "select_suspect"

        elif event.type == pygame.MOUSEMOTION and dragging:
            dragging["rect"].x = mouse[0] - drag_offset[0]
            dragging["rect"].y = mouse[1] - drag_offset[1]

    # ── DRAW ─────────────────────────────────────────────────

    if phase == "win":
        # win screen
        screen.fill((10, 8, 12))
        # draw grainger statue
        cx, cy = W//2, 420
        SKIN=(210,170,130); SUIT=(50,60,90); SHIRT=(220,215,200)
        pygame.draw.rect(screen,(130,110,80),(cx-80,cy+120,160,40))
        pygame.draw.rect(screen,(160,140,100),(cx-70,cy+110,140,15))
        pygame.draw.rect(screen,(100,85,60),(cx-80,cy+120,160,40),2)
        pygame.draw.rect(screen,(100,70,40),(cx-70,cy+85,140,12))
        pygame.draw.rect(screen,(80,55,30),(cx-65,cy+97,10,25))
        pygame.draw.rect(screen,(80,55,30),(cx+55,cy+97,10,25))
        pygame.draw.rect(screen,SUIT,(cx-30,cy+60,25,30))
        pygame.draw.rect(screen,SUIT,(cx+5,cy+60,25,30))
        pygame.draw.rect(screen,(30,25,20),(cx-35,cy+85,30,10))
        pygame.draw.rect(screen,(30,25,20),(cx+5,cy+85,30,10))
        pygame.draw.rect(screen,SUIT,(cx-28,cy+20,56,42))
        pygame.draw.rect(screen,SHIRT,(cx-10,cy+22,20,38))
        pygame.draw.rect(screen,SUIT,(cx-46,cy+22,20,35))
        pygame.draw.rect(screen,SUIT,(cx+26,cy+22,20,35))
        pygame.draw.rect(screen,SKIN,(cx-44,cy+54,16,12))
        pygame.draw.rect(screen,SKIN,(cx+28,cy+54,16,12))
        pygame.draw.rect(screen,(180,60,60),(cx-20,cy+52,40,18))
        pygame.draw.rect(screen,(220,80,80),(cx-18,cy+53,36,4))
        pygame.draw.rect(screen,SKIN,(cx-20,cy-10,40,38))
        pygame.draw.rect(screen,(180,175,180),(cx-20,cy-10,40,10))
        pygame.draw.rect(screen,(160,155,160),(cx-22,cy-4,6,20))
        pygame.draw.rect(screen,(160,155,160),(cx+16,cy-4,6,20))
        pygame.draw.rect(screen,(60,55,70),(cx-18,cy+12,14,9))
        pygame.draw.rect(screen,(60,55,70),(cx+4,cy+12,14,9))
        pygame.draw.rect(screen,(60,55,70),(cx-4,cy+15,8,3))
        pygame.draw.rect(screen,(40,35,50),(cx-14,cy+14,6,5))
        pygame.draw.rect(screen,(40,35,50),(cx+8,cy+14,6,5))
        pygame.draw.rect(screen,(170,110,90),(cx-8,cy+26,16,4))
        pygame.draw.rect(screen,(140,130,120),(cx-10,cy+22,20,5))
        pygame.draw.rect(screen,(60,45,30),(cx-180,cy-80,120,80))
        pygame.draw.rect(screen,(80,62,42),(cx-178,cy-78,116,76))
        pygame.draw.rect(screen,(200,175,120),(cx-178,cy-78,116,76),2)
        for txt,dy in [("UNIVERSITY",cy-52),("LIBRARY",cy-36)]:
            s=FONT_XS.render(txt,True,(220,195,140))
            screen.blit(s,s.get_rect(center=(cx-120,dy)))
        plq=FONT_XS.render("PROF. GRAINGER BOB",True,(200,175,100))
        screen.blit(plq,plq.get_rect(center=(cx,cy+138)))
        title=FONT_WIN.render("JUSTICE FOR GRAINGER BOB",True,(240,200,80))
        screen.blit(title,title.get_rect(center=(W//2,65)))
        sub1=FONT_MED.render("The killer has been brought to justice.",True,CORRECT_COL)
        screen.blit(sub1,sub1.get_rect(center=(W//2,115)))
        sub2=FONT_SM.render("Ross Bob  —  Knife  —  By the Bell  —  8:23 PM",True,(160,140,110))
        screen.blit(sub2,sub2.get_rect(center=(W//2,145)))
        plaque=pygame.Rect(W//2-270,H-82,540,52)
        pygame.draw.rect(screen,(80,65,20),plaque,border_radius=6)
        pygame.draw.rect(screen,(180,150,50),plaque,2,border_radius=6)
        pt=FONT_MED.render('"In memory of Professor Grainger — A true educator"',True,(240,210,100))
        screen.blit(pt,pt.get_rect(center=plaque.center))

    elif phase == "arrest":
        draw_red_strings()
        for i in range(5):
            draw_suspect_card(i, mouse)
        done = draw_prison_scene(now, arrest_start)
        if done:
            phase = "win"

    else:
        draw_clue_zone_divider()
        draw_red_strings()
        for i in range(5):
            draw_suspect_card(i, mouse)
        for c in ALL_CLUES:
            if not c["placed"] and c is not dragging:
                draw_clue_photo(c, hovered=clue_hit(c, mouse), use_angle=True)
        draw_title_card()
        draw_status_banner()

        if phase == "wrong":
            if now - wrong_timer < 2.0:
                a     = int(110 * abs(math.sin((now-wrong_timer)*6)))
                flash = pygame.Surface((W, H), pygame.SRCALPHA)
                flash.fill((180, 20, 20, a))
                screen.blit(flash, (0, 0))
                msg = FONT_WIN.render("WRONG — TRY AGAIN", True, (255,80,80))
                screen.blit(msg, msg.get_rect(center=(W//2, H//2)))
            else:
                phase = "select_suspect"

        if dragging:
            draw_clue_photo(dragging, hovered=True, use_angle=False)

        # alibi popup always on top
        draw_alibi_popup()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()