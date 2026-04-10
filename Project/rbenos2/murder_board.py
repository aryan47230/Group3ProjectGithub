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
# =============================================================
ALIBI_BLURBS = [
    # Veronica Mitchell (Author)
    "I was just trying to finish writing my book so I went to get some coffee and I saw a little vile with red liquid. The barista said it was fruit punch flavoring.",

    # John John (Student)
    "I WASN'T VAPING I SWEAR, the smoke came from this random gun I found on the dumpster. The CBTF proctor was trying to get me in trouble but I got a call from a number a didn't regonize saying to meet outside.",

    # Richard Hedricks (Janitor)
    "I was cleaning late because I picked up the closing shift, doing my job ya know, and I hear this girl crying saying she saw Grainger Bob get murdered with something that looked like a mini sword. Sounded like she had been in there a while, she wouldn't come out of the stall.",

    # Ross Bob (Artist)
    "I was ... measureing the magnetic field of the bell with an iOLab! Don't make fun of me, I am an artist. This knife was just sitting in the planter here next to this magnificant work of craftmenship.",

    # Claudia VanHelsing (Librarian)
    "I was proctering an exam in my big comfy hoodie when I saw smoke coming in through the window so I left to yell at a kid for vaping, the same kid that brought candlestick holders in the testing room because he thought they were 'cool cups for fruit punch'.",
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

TIME_PILL   = ( 80,  60, 130)
TIME_PILL_H = (110,  85, 170)
TIME_TEXT   = (220, 210, 255)

BTN_COL     = (120,  30,  30)
BTN_HOVER   = (160,  45,  45)
BTN_TEXT    = (255, 220, 200)

ALIBI_BTN   = ( 55,  80,  45)
ALIBI_HOV   = ( 80, 115,  60)
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
FONT_HAND   = pygame.font.SysFont("Courier", 9)
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
    "time":     "8:23 PM",
}

SLOT_KINDS = ["time", "location", "weapon"]

TIMES = ["7:45 PM", "8:23 PM", "9:47 PM", "3:55 AM", "12:31 AM"]

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
CARD_HEADER_H = 105
CARD_GAP      = 22
CARDS_Y       = 55
CARDS_START_X = (W - (5 * CARD_W + 4 * CARD_GAP)) // 2
PHOTO_PAD     = 5
SLOT_PADDING  = 6
SLOT_MARGIN   = 8
SLOT_H        = 134
TIME_SLOT_H   = 30
CLUE_ZONE_Y = 570

def card_x(i):                                          
    return CARDS_START_X + i * (CARD_W + CARD_GAP)

def slot_height(slot_i):
    return TIME_SLOT_H if SLOT_KINDS[slot_i] == "time" else SLOT_H

def card_total_height(i):
    return CARD_HEADER_H + sum(slot_height(si) + SLOT_PADDING for si in range(len(SLOT_KINDS))) + SLOT_PADDING + 8

def slot_top_y(card_i, slot_i):
    y = CARDS_Y + CARD_HEADER_H + SLOT_PADDING
    for si in range(slot_i):
        y += slot_height(si) + SLOT_PADDING
    return y

def slot_rect(card_i, slot_i):
    return pygame.Rect(card_x(card_i) + SLOT_MARGIN,
                       slot_top_y(card_i, slot_i),
                       CARD_W - SLOT_MARGIN * 2, slot_height(slot_i))

def card_rect(i):
    return pygame.Rect(card_x(i), CARDS_Y, CARD_W, card_total_height(i))

def alibi_btn_rect(i):
    cr = card_rect(i)
    return pygame.Rect(cr.x + 8, cr.y + CARD_HEADER_H - 20, cr.w - 16, 18)

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
        ("loc_cbtf.png",     "CBTF Testing Center",    164,  82),
        ("loc_espresso.png", "Espresso Royal",          146, 108),
        ("loc_restroom.png", "Womens Restroom",         164,  97),
        ("loc_bell.png",     "By the Bell",             135, 108),
        ("loc_smoking.png",  "Unofficial Smoking Area", 164, 108),
    ]
    wpn_data = [
        ("wpn_knife.png",       "Knife",       108, 108),
        ("wpn_gun.png",         "Gun",         108, 108),
        ("wpn_poison.png",      "Poison",      108, 108),
        ("wpn_candlestick.png", "Candlestick", 164, 100),
        ("wpn_sword.png",       "Sword",        69, 108),
    ]
    rng = random.Random(7)
    for filename, label, iw, ih in loc_data + wpn_data:
        kind         = "location" if filename.startswith("loc") else "weapon"
        surf, pw, ph = load_clue(filename, label, kind, iw, ih)
        clues.append({
            "label":  label, "kind":   kind,
            "surf":   surf,
            "w":      pw,    "h":      ph,
            "pw":     pw,    "ph":     ph,
            "angle":  rng.uniform(-10, 10),
            "placed": False, "slot":   None,
            "rect":   None,  "home":   None,
        })

    for t in TIMES:
        clues.append({
            "label":  t,    "kind":   "time",
            "surf":   None,
            "w":      90,   "h":      28,
            "pw":     90,   "ph":     28,
            "angle":  0,
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

    tim_c = [c for c in ALL_CLUES if c["kind"] == "time"]
    x = W // 2 - (len(tim_c) * 96) // 2
    for c in tim_c:
        y = CLUE_ZONE_Y - 38
        c["home"] = pygame.Rect(x, y, c["w"], c["h"])
        c["rect"] = pygame.Rect(x, y, c["w"], c["h"])
        x += c["w"] + 6

assign_clue_positions()

# =============================================================
#  SLOTS STATE
# =============================================================
slots = [{k: None for k in SLOT_KINDS} for _ in range(5)]

# =============================================================
#  ALIBI STATE
# =============================================================
alibi_state  = None   # None or {"suspect": i, "start": t, "text": str}
ALIBI_SPEED  = 0.03
WAVE_BARS    = 12
_wrng        = random.Random(55)
WAVE_BASE_H  = [_wrng.randint(4, 16) for _ in range(WAVE_BARS)]

def start_alibi(i):
    global alibi_state
    alibi_state = {"suspect": i, "start": time.time(), "text": ALIBI_BLURBS[i]}

def close_alibi():
    global alibi_state
    alibi_state = None

def wrap_text(text, font, max_w):
    words, lines, line = text.split(), [], ""
    for w in words:
        test = line + (" " if line else "") + w
        if font.size(test)[0] <= max_w:
            line = test
        else:
            if line: lines.append(line)
            line = w
    if line: lines.append(line)
    return lines

def get_alibi_close_rect():
    """Returns close button rect for current alibi popup, or None."""
    if alibi_state is None:
        return None
    si    = alibi_state["suspect"]
    cr    = card_rect(si)
    pop_w = 320
    pop_x = max(10, min(cr.centerx - pop_w//2, W - pop_w - 10))
    pop_y = cr.bottom + 6
    lines = wrap_text(alibi_state["text"], FONT_ALIBI, pop_w - 20)
    pop_h = 30 + 14 + len(lines) * 16 + 14
    if pop_y + pop_h > H - 10:
        pop_y = cr.y - pop_h - 6
    return pygame.Rect(pop_x + pop_w - 22, pop_y + 3, 18, 14)

def draw_alibi_popup():
    if alibi_state is None:
        return
    now     = time.time()
    t       = now - alibi_state["start"]
    full    = alibi_state["text"]
    chars   = min(len(full), int(t / ALIBI_SPEED))
    visible = full[:chars]
    cursor  = "|" if int(now * 2) % 2 == 0 else " "

    si      = alibi_state["suspect"]
    cr      = card_rect(si)
    pop_w   = 320
    pop_x   = max(10, min(cr.centerx - pop_w//2, W - pop_w - 10))
    pop_y   = cr.bottom + 6
    wave_h  = 30
    lines   = wrap_text(visible + cursor, FONT_ALIBI, pop_w - 20)
    pop_h   = wave_h + 14 + len(lines) * 16 + 14

    if pop_y + pop_h > H - 10:
        pop_y = cr.y - pop_h - 6

    # shadow
    pygame.draw.rect(screen, (20,12,5), (pop_x+3, pop_y+3, pop_w, pop_h), border_radius=5)
    # body
    pygame.draw.rect(screen, CARD_BG,     (pop_x, pop_y, pop_w, pop_h), border_radius=5)
    pygame.draw.rect(screen, CARD_BORDER, (pop_x, pop_y, pop_w, pop_h), 1, border_radius=5)
    # tape
    tape = pygame.Surface((pop_w, 10), pygame.SRCALPHA)
    tape.fill((220, 215, 150, 140))
    screen.blit(tape, (pop_x, pop_y))

    # waveform
    bw = (pop_w - 20) // WAVE_BARS
    for bi in range(WAVE_BARS):
        bh  = int(WAVE_BASE_H[bi] + 8 * math.sin(t * 5 + bi * 0.8))
        bh  = max(3, min(wave_h - 2, bh))
        col = (80,160,100) if bi % 2 == 0 else (60,130,80)
        pygame.draw.rect(screen, col,
                         (pop_x + 10 + bi*bw + 2,
                          pop_y + 10 + (wave_h-bh)//2,
                          max(2, bw-4), bh), border_radius=2)

    # REC dot
    rec_col = (220,50,50) if int(t*2) % 2 == 0 else (150,30,30)
    pygame.draw.circle(screen, rec_col, (pop_x + pop_w - 16, pop_y + 24), 5)
    screen.blit(FONT_XS.render("REC", True, (180,40,40)), (pop_x+pop_w-38, pop_y+18))

    # divider
    pygame.draw.line(screen, CARD_LINES,
                     (pop_x+8, pop_y+wave_h+12),
                     (pop_x+pop_w-8, pop_y+wave_h+12), 1)

    # text
    ty = pop_y + wave_h + 18
    for line in lines:
        screen.blit(FONT_ALIBI.render(line, True, TEXT_CARD), (pop_x+10, ty))
        ty += 16

    # close button
    cr2 = pygame.Rect(pop_x+pop_w-22, pop_y+3, 18, 14)
    pygame.draw.rect(screen, CARD_BORDER, cr2, border_radius=3)
    screen.blit(FONT_XS.render("x", True, TEXT_CARD),
                FONT_XS.render("x", True, TEXT_CARD).get_rect(center=cr2.center))

# =============================================================
#  ROSS BOB PIXEL ART SPRITE
# =============================================================
def draw_ross_bob(cx, cy, scale=3):
    def r(x, y, w, h, col):
        pygame.draw.rect(screen, col,
                         (int(cx+x*scale), int(cy+y*scale),
                          max(1,int(w*scale)), max(1,int(h*scale))))
    SKIN=(210,170,130); SHIRT=(80,110,160); PANTS=(55,50,70)
    HAIR=(60,45,30);    BERET=(140,40,40);  SHOES=(30,25,18)
    BEARD=(80,60,40)
    r(-12,44,12,6,SHOES);  r(2,44,12,6,SHOES)
    r(-12,26,10,20,PANTS); r(2,26,10,20,PANTS)
    r(-14,4,28,24,SHIRT)
    r(-4,4,8,6,(200,195,180))
    r(-22,6,10,18,SHIRT);  r(12,6,10,18,SHIRT)
    r(-22,22,9,8,SKIN);    r(12,22,9,8,SKIN)
    r(20,18,3,14,(160,120,70))
    r(21,30,2,4,(80,140,200))
    r(-12,-18,24,24,SKIN)
    r(-12,-18,24,8,HAIR)
    r(-14,-22,28,8,BERET)
    r(-6,-26,16,6,BERET)
    r(6,-28,4,4,BERET)
    r(-8,-8,5,5,(40,35,50));  r(4,-8,5,5,(40,35,50))
    r(-9,-11,6,2,HAIR);       r(3,-11,6,2,HAIR)
    r(-10,2,20,6,BEARD)
    r(-5,-2,10,3,(160,100,80))
    r(2,-2,5,2,(180,120,90))

# =============================================================
#  PRISON BARS ANIMATION
# =============================================================
BAR_COUNT = 7

def draw_prison_scene(now, arrest_start_t):
    elapsed = now - arrest_start_t
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((10,5,2,220))
    screen.blit(overlay, (0,0))

    fw, fh = 280, 320
    fx     = W//2 - fw//2
    fy     = H//2 - fh//2 - 20

    # cell background
    pygame.draw.rect(screen, (35,28,20), (fx,fy,fw,fh))
    pygame.draw.rect(screen, (80,65,40), (fx,fy,fw,fh), 3)

    # bricks
    for row in range(0, fh, 16):
        offset = 20 if (row//16)%2 else 0
        for col in range(-offset, fw, 40):
            br = pygame.Rect(fx+col+1, fy+row+1, 38, 14)
            pygame.draw.rect(screen, (45,35,25), br)
            pygame.draw.rect(screen, (60,48,32), br, 1)

    # floor
    pygame.draw.rect(screen, (55,42,28), (fx, fy+fh-40, fw, 40))

    # Ross Bob sprite
    draw_ross_bob(W//2, H//2+50, scale=3)

    # bars dropping
    bar_w   = fw // BAR_COUNT
    all_done = True
    for bi in range(BAR_COUNT):
        delay    = bi * 0.06
        if elapsed > delay:
            progress = min(1.0, (elapsed-delay)*120.0/fh)
        else:
            progress = 0.0
        bar_h = int(fh * progress)
        if bar_h < fh:
            all_done = False
        bx  = fx + bi*bar_w
        pygame.draw.rect(screen, (15,10,5),  (bx+3, fy, bar_w-8, bar_h))
        col = BAR_COL1 if bi%2==0 else BAR_COL2
        pygame.draw.rect(screen, col,        (bx+1, fy, bar_w-6, bar_h))
        pygame.draw.rect(screen, BAR_SHINE,  (bx+2, fy, 3,       bar_h))
        if bar_h > 10:
            pygame.draw.circle(screen, (120,100,60), (bx+bar_w//2, fy+8), 4)

    # top bar
    if elapsed > 0.3:
        pygame.draw.rect(screen, (60,50,30), (fx, fy, fw, 12))
        pygame.draw.rect(screen, BAR_SHINE,  (fx, fy, fw,  3))

    if elapsed > 0.8:
        lbl = FONT_WIN.render("ARRESTED!", True, (220,50,50))
        screen.blit(lbl, lbl.get_rect(center=(W//2, fy-42)))
        sub = FONT_MED.render(f"{CORRECT['suspect']} has been taken into custody.",
                               True, CARD_BG)
        screen.blit(sub, sub.get_rect(center=(W//2, fy+fh+22)))
        clue = FONT_SM.render(
            f"Weapon: {CORRECT['weapon']}   Location: {CORRECT['location']}",
            True, (180,160,120))
        screen.blit(clue, clue.get_rect(center=(W//2, fy+fh+46)))

    return all_done and elapsed > 2.5

# =============================================================
#  DRAW HELPERS
# =============================================================
def draw_pin(x, y):
    pygame.draw.circle(screen, PIN_DARK,  (x,y), 7)
    pygame.draw.circle(screen, PIN_RED,   (x,y), 6)
    pygame.draw.circle(screen, PIN_SHINE, (x-2,y-2), 2)

def draw_tape(rect):
    tape = pygame.Surface((rect.w, 14), pygame.SRCALPHA)
    tape.fill((220,215,150,130))
    screen.blit(tape, (rect.x, rect.y-3))

def draw_red_strings():
    for i in range(5):
        cr = card_rect(i)
        for si, kind in enumerate(SLOT_KINDS):
            if slots[i][kind]:
                sr  = slot_rect(i, si)
                p1  = (cr.centerx, cr.y + CARD_HEADER_H//2)
                p2  = (sr.centerx, sr.top)
                mid = ((p1[0]+p2[0])//2, (p1[1]+p2[1])//2+15)
                pts = []
                for t2 in range(11):
                    tt = t2/10
                    pts.append((
                        int((1-tt)**2*p1[0]+2*(1-tt)*tt*mid[0]+tt**2*p2[0]),
                        int((1-tt)**2*p1[1]+2*(1-tt)*tt*mid[1]+tt**2*p2[1])
                    ))
                if len(pts) >= 2:
                    pygame.draw.lines(screen, RED_STRING, False, pts, 2)

def draw_suspect_card(i, mouse_pos):
    s  = SUSPECTS[i]
    cr = card_rect(i)
    is_hov = (phase == "select_suspect" and
              cr.collidepoint(mouse_pos) and not dragging)

    # shadow
    pygame.draw.rect(screen, CARD_SHADOW,
                     pygame.Rect(cr.x+4,cr.y+4,cr.w,cr.h), border_radius=3)
    if is_hov:
        pygame.draw.rect(screen, (200,180,80),
                         pygame.Rect(cr.x-2,cr.y-2,cr.w+4,cr.h+4), border_radius=5)

    pygame.draw.rect(screen, CARD_BG, cr, border_radius=3)
    for ly in range(cr.y+28, cr.y+CARD_HEADER_H-24, 12):
        pygame.draw.line(screen, CARD_LINES, (cr.x+8,ly), (cr.right-8,ly), 1)
    pygame.draw.line(screen, (200,150,150),
                     (cr.x+22,cr.y+4),(cr.x+22,cr.y+CARD_HEADER_H-4),1)
    pygame.draw.rect(screen, CARD_BORDER, cr, 1, border_radius=3)
    draw_tape(cr)
    draw_pin(cr.centerx, cr.y-2)

    y_off = cr.y+10
    for part in s["name"].split():
        ns = FONT_MED.render(part, True, TEXT_CARD)
        screen.blit(ns, ns.get_rect(centerx=cr.centerx, y=y_off))
        y_off += 16
    rs = FONT_XS.render(f"— {s['role']} —", True, TEXT_DIM)
    screen.blit(rs, rs.get_rect(centerx=cr.centerx, y=y_off+2))

    # alibi button — right under the name
    ab     = alibi_btn_rect(i)
    active = alibi_state is not None and alibi_state["suspect"] == i
    ab_col = ALIBI_HOV if (ab.collidepoint(mouse_pos) or active) else ALIBI_BTN
    pygame.draw.rect(screen, ab_col, ab, border_radius=3)
    screen.blit(FONT_XS.render("▶ ALIBI", True, ALIBI_TEXT),
                FONT_XS.render("▶ ALIBI", True, ALIBI_TEXT).get_rect(center=ab.center))

    # slots — fixed size, image centered inside
    for si, kind in enumerate(SLOT_KINDS):
        sr   = slot_rect(i, si)
        clue = slots[i][kind]
        pygame.draw.rect(screen, (155, 130, 95), sr, border_radius=3)
        if clue:
            if clue["kind"] == "time":
                pygame.draw.rect(screen, TIME_PILL, sr, border_radius=5)
                lbl = FONT_SM.render(clue["label"], True, TIME_TEXT)
                screen.blit(lbl, lbl.get_rect(center=sr.center))
            else:
                scale = min((sr.w - 8) / clue["pw"], (sr.h - 8) / clue["ph"])
                dw    = int(clue["pw"] * scale)
                dh    = int(clue["ph"] * scale)
                scaled= pygame.transform.scale(clue["surf"], (dw, dh))
                bx    = sr.x + (sr.w - dw) // 2
                by    = sr.y + (sr.h - dh) // 2
                screen.blit(scaled, (bx, by))
                pygame.draw.rect(screen, CARD_BORDER, sr, 1, border_radius=3)
        else:
            for dx in range(sr.x+4, sr.right-4, 8):
                pygame.draw.line(screen, SLOT_DASHED, (dx, sr.y+2),    (dx+4, sr.y+2),    1)
                pygame.draw.line(screen, SLOT_DASHED, (dx, sr.bottom-3),(dx+4, sr.bottom-3),1)
            lbl = FONT_XS.render(kind.upper(), True, TEXT_DIM)
            screen.blit(lbl, lbl.get_rect(center=sr.center))

def draw_time_pill(c, hovered=False, alpha=255):
    col  = TIME_PILL_H if hovered else TIME_PILL
    surf = pygame.Surface((c["w"], c["h"]), pygame.SRCALPHA)
    pygame.draw.rect(surf, (*col, alpha), (0, 0, c["w"], c["h"]), border_radius=6)
    pygame.draw.rect(surf, (255, 255, 255, 60), (0, 0, c["w"], c["h"]), 1, border_radius=6)
    lbl = FONT_SM.render(c["label"], True, TIME_TEXT)
    surf.blit(lbl, lbl.get_rect(center=(c["w"]//2, c["h"]//2)))
    screen.blit(surf, (c["rect"].x, c["rect"].y))

def draw_clue_photo(c, hovered=False, alpha=255, use_angle=True):
    if c["kind"] == "time":
        draw_time_pill(c, hovered=hovered, alpha=alpha)
        return
    surf  = c["surf"].copy()
    if alpha < 255:
        surf.set_alpha(alpha)
    angle = c["angle"] if use_angle else 0
    if hovered:
        pygame.draw.rect(surf,(255,200,50),(0,0,surf.get_width(),surf.get_height()),3)
    if angle != 0:
        rot = pygame.transform.rotate(surf, angle)
        cx  = c["rect"].x + c["w"]//2
        cy  = c["rect"].y + c["h"]//2
        screen.blit(rot, (cx-rot.get_width()//2, cy-rot.get_height()//2))
    else:
        screen.blit(surf, (c["rect"].x, c["rect"].y))

def draw_clue_zone_divider():
    tape = pygame.Surface((W,16), pygame.SRCALPHA)
    tape.fill((200,195,130,140))
    screen.blit(tape, (0, CLUE_ZONE_Y-8))
    screen.blit(FONT_HAND.render("LOCATIONS ▼",True,(80,55,25)),(25,CLUE_ZONE_Y-22))
    screen.blit(FONT_HAND.render("WEAPONS ▼",  True,(80,55,25)),(W//2+10,CLUE_ZONE_Y-22))
    screen.blit(FONT_HAND.render("TIMES ▼",    True,(80,55,25)),(W//2-30, CLUE_ZONE_Y-58))

def draw_title_card():
    tr = pygame.Rect(W//2-230,8,460,36)
    pygame.draw.rect(screen, CARD_BG,     tr, border_radius=3)
    pygame.draw.rect(screen, CARD_BORDER, tr, 1, border_radius=3)
    draw_tape(tr)
    screen.blit(FONT_TITLE.render("MURDER BOARD  —  FIND THE KILLER",True,(140,30,30)),
                FONT_TITLE.render("MURDER BOARD  —  FIND THE KILLER",True,(140,30,30))
                .get_rect(center=tr.center))
    draw_pin(tr.centerx-90, tr.y-2)
    draw_pin(tr.centerx+90, tr.y-2)
def draw_evidence_button(mouse_pos):
    br  = pygame.Rect(W - 160, 8, 150, 36)
    col = (80, 55, 110) if br.collidepoint(mouse_pos) else (55, 35, 85)
    pygame.draw.rect(screen, CARD_BG, br, border_radius=5)
    pygame.draw.rect(screen, col,     br, border_radius=5)
    pygame.draw.rect(screen, (180, 140, 220), br, 2, border_radius=5)
    s = FONT_SM.render("📁 EVIDENCE", True, (220, 200, 255))
    screen.blit(s, s.get_rect(center=br.center))
    return br

def draw_evidence_panel():
    if not evidence_open:
        return

    # ── Panel background ──
    pw, ph = 780, 380
    px     = W // 2 - pw // 2
    py     = H // 2 - ph // 2
    pygame.draw.rect(screen, (143, 105, 60), (px+4, py+4, pw, ph), border_radius=8)
    pygame.draw.rect(screen, (176, 141, 100),      (px, py, pw, ph),      border_radius=8)
    pygame.draw.rect(screen, (61, 39, 13), (px, py, pw, ph),   2, border_radius=8)
    draw_tape(pygame.Rect(px, py, pw, 14))

    # Title
    t = FONT_MED.render("EVIDENCE FROM THE SCENE", True, (140, 30, 30))
    screen.blit(t, t.get_rect(centerx=px + pw // 2, y=py + 14))

    # ── Five photo slots ──────────────────────────────────────
    # Replace None with pygame.image.load("your_photo.png") for each slot
    EVIDENCE_PHOTOS = [
        pygame.image.load("coffee_cup.png"),   # <-- slot 1: replace with pygame.image.load("evidence1.png")
        pygame.image.load("iOLab_reciept.png"),   # <-- slot 2: replace with pygame.image.load("evidence2.png")
        pygame.image.load("security_cam.png"),   # <-- slot 3: replace with pygame.image.load("evidence3.png")
        pygame.image.load("broken_watch.png"),   # <-- slot 4: replace with pygame.image.load("evidence4.png")
        pygame.image.load("call_log.png"),   # <-- slot 5: replace with pygame.image.load("evidence5.png")
    ]

    slot_w, slot_h = 140, 140
    sy      = py + 60
    # Staggered y positions — alternates high/low
    stagger = [sy, sy + 60, sy, sy + 60, sy]

    for idx, photo in enumerate(EVIDENCE_PHOTOS):
        total_w = 5 * slot_w + 4 * 16
        sx      = px + (pw - total_w) // 2
        x       = sx + idx * (slot_w + 16)
        y       = stagger[idx]
        sr      = pygame.Rect(x, y, slot_w, slot_h)

        # polaroid-style white border
        pygame.draw.rect(screen, PHOTO_BG,    sr, border_radius=4)
        pygame.draw.rect(screen, CARD_BORDER, sr, 1, border_radius=4)
        if photo:
            scaled = pygame.transform.scale(photo, (slot_w - 8, slot_h - 24))
            screen.blit(scaled, (sr.x + 4, sr.y + 4))
        else:
            lbl = FONT_XS.render(f"PHOTO {idx+1}", True, TEXT_DIM)
            screen.blit(lbl, lbl.get_rect(center=(sr.centerx, sr.centery - 8)))

    # ── Close button ──
    close_r = pygame.Rect(px + pw - 26, py + 6, 20, 16)
    pygame.draw.rect(screen, CARD_BORDER, close_r, border_radius=3)
    screen.blit(FONT_XS.render("x", True, TEXT_CARD),
                FONT_XS.render("x", True, TEXT_CARD).get_rect(center=close_r.center))
    return close_r
def draw_arrest_button(mouse_pos):
    """Big arrest button at bottom center — only shown in select_suspect phase."""
    if phase != "select_suspect":
        return None
    br  = pygame.Rect(W//2-120, H-52, 240, 40)
    col = BTN_HOVER if br.collidepoint(mouse_pos) else BTN_COL
    pygame.draw.rect(screen, CARD_BG,          br, border_radius=5)
    pygame.draw.rect(screen, col,              br, border_radius=5)
    pygame.draw.rect(screen, (255,100,100),    br, 2, border_radius=5)
    screen.blit(FONT_MED.render("★  MAKE ARREST  ★", True, BTN_TEXT),
                FONT_MED.render("★  MAKE ARREST  ★", True, BTN_TEXT)
                .get_rect(center=br.center))
    return br

def draw_status_banner():
    if phase == "board":
        msg = ("All clues placed! Now click MAKE ARREST to choose the killer."
               if any_card_full() else
               "Drag location and weapon photos onto a suspect card.")
    elif phase == "select_suspect":
        msg = "Click a suspect card to select them, then press MAKE ARREST."
    else:
        return
    bar = pygame.Surface((W,28), pygame.SRCALPHA)
    bar.fill((20,10,5,180))
    screen.blit(bar, (0, H-28))
    screen.blit(FONT_SM.render(msg,True,(220,200,160)),
                FONT_SM.render(msg,True,(220,200,160)).get_rect(center=(W//2,H-14)))

# =============================================================
#  HELPERS
# =============================================================
def any_card_full():
    return any(all(slots[i][k] is not None for k in SLOT_KINDS) for i in range(5))

def clue_hit(c, mouse):
    cx = c["rect"].x + c["w"]//2
    cy = c["rect"].y + c["h"]//2
    return pygame.Rect(cx-c["w"]//2, cy-c["h"]//2, c["w"], c["h"]).collidepoint(mouse)

def check_suspect(i):
    s      = SUSPECTS[i]
    loc_ok = (slots[i]["location"] and
              slots[i]["location"]["label"].lower() == CORRECT["location"].lower())
    wpn_ok = (slots[i]["weapon"] and
              slots[i]["weapon"]["label"].lower()   == CORRECT["weapon"].lower())
    tim_ok = (slots[i]["time"] and
              slots[i]["time"]["label"].lower()     == CORRECT["time"].lower())
    return "correct" if (s["name"]==CORRECT["suspect"] and loc_ok and wpn_ok and tim_ok) else "wrong"

# =============================================================
#  GAME STATE
# =============================================================
dragging       = None
drag_offset    = (0, 0)
phase          = "board"
selected_suspect = None
wrong_timer    = 0.0
arrest_start   = 0.0
win_start      = 0.0
evidence_open    = False

# =============================================================
#  WIN SCREEN
# =============================================================
# Load grainger image once so we don't reload every frame
_grainger_img   = pygame.image.load("grainger_bob.png")
_g_w, _g_h      = _grainger_img.get_size()
_g_scale        = min((W * 0.65) / _g_w, (H - 180) / _g_h)
_g_dw           = int(_g_w * _g_scale)
_g_dh           = int(_g_h * _g_scale)
GRAINGER_SURF   = pygame.transform.scale(_grainger_img, (_g_dw, _g_dh))
GRAINGER_IX     = W // 2 - _g_dw // 2
GRAINGER_IY     = 170

def draw_win_screen():
    screen.fill((10,8,12))

    # fade in over 2 seconds
    elapsed = now - win_start
    alpha   = min(255, int(255 * elapsed / 2.0))
    faded   = GRAINGER_SURF.copy()
    faded.set_alpha(alpha)
    screen.blit(faded, (GRAINGER_IX, GRAINGER_IY))

    title = FONT_WIN.render("JUSTICE FOR GRAINGER BOB", True, (240,200,80))
    screen.blit(title, title.get_rect(center=(W//2, 65)))
    sub1 = FONT_MED.render("The killer has been brought to justice.", True, CORRECT_COL)
    screen.blit(sub1, sub1.get_rect(center=(W//2, 115)))
    sub2 = FONT_SM.render("Ross Bob  —  Knife  —  By the Bell  —  8:23 PM", True, (160,140,110))
    screen.blit(sub2, sub2.get_rect(center=(W//2, 145)))
    plaque = pygame.Rect(W//2-600, H-82, 1200, 52)
    pygame.draw.rect(screen, (80,65,20), plaque, border_radius=6)
    pygame.draw.rect(screen, (180,150,50), plaque, 2, border_radius=6)
    pt = FONT_MED.render('"In memory of Professor Grainger — A true educator. We build this statue in his honor, may be sit here, resting, at his favorite spot for eternity"', True, (240,210,100))
    screen.blit(pt, pt.get_rect(center=plaque.center))

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

            # --- alibi close button ---
            close_r = get_alibi_close_rect()
            if close_r and close_r.collidepoint(mouse):
                close_alibi()
                continue
            # --- evidence panel close ---
            if evidence_open:
                cr = draw_evidence_panel()
                if cr and cr.collidepoint(mouse):
                    evidence_open = False
                continue

            # --- evidence button ---
            ev_btn = pygame.Rect(W - 160, 8, 150, 36)
            if ev_btn.collidepoint(mouse):
                evidence_open = not evidence_open
                continue

            # --- alibi buttons ---
            clicked_alibi = False
            for i in range(5):
                if alibi_btn_rect(i).collidepoint(mouse):
                    if alibi_state and alibi_state["suspect"] == i:
                        close_alibi()
                    else:
                        start_alibi(i)
                    clicked_alibi = True
                    break
            if clicked_alibi:
                continue

            # --- drag clues ---
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
                        break

            # --- arrest button ---
            if dragging is None and phase == "select_suspect":
                br = pygame.Rect(W//2-120, H-52, 240, 40)
                if br.collidepoint(mouse) and selected_suspect is not None:
                    result = check_suspect(selected_suspect)
                    if result == "correct":
                        phase        = "arrest"
                        arrest_start = now
                    else:
                        phase      = "wrong"
                        wrong_timer= now

            # --- select suspect ---
            if dragging is None and phase == "select_suspect":
                for i in range(5):
                    cr = card_rect(i)
                    ab = alibi_btn_rect(i)
                    if cr.collidepoint(mouse) and not ab.collidepoint(mouse):
                        selected_suspect = i
                        break

            # --- enter select mode ---
            if dragging is None and phase == "board" and any_card_full():
                for i in range(5):
                    cr = card_rect(i)
                    ab = alibi_btn_rect(i)
                    if (cr.collidepoint(mouse) and not ab.collidepoint(mouse) and
                            not any(clue_hit(c,mouse) for c in ALL_CLUES if not c["placed"])):
                        phase            = "select_suspect"
                        selected_suspect = None
                        break

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if dragging:
                dropped = False
                for ci in range(5):
                    for si2, kind in enumerate(SLOT_KINDS):
                        if dragging["kind"] == kind:
                            drop_zone = slot_rect(ci, si2)
                            if drop_zone.collidepoint(mouse):
                                existing = slots[ci][kind]
                                if existing:
                                    existing["placed"] = False
                                    existing["slot"]   = None
                                    existing["rect"]   = pygame.Rect(
                                        existing["home"].x,existing["home"].y,
                                        existing["w"],existing["h"])
                                    existing["angle"]  = random.uniform(-10,10)
                                slots[ci][kind]    = dragging
                                dragging["placed"] = True
                                dragging["slot"]   = (ci, si2)
                                dragging["rect"]   = pygame.Rect(
                                    drop_zone.x, drop_zone.y,
                                    drop_zone.w, drop_zone.h)
                                dragging["angle"]  = 0
                                dropped = True
                                break
                    if dropped:
                        break
                if not dropped:
                    dragging["rect"]  = pygame.Rect(
                        dragging["home"].x,dragging["home"].y,
                        dragging["w"],dragging["h"])
                    dragging["angle"] = random.uniform(-10,10)
                dragging = None
                if any_card_full() and phase == "board":
                    phase = "select_suspect"
                    selected_suspect = None

        elif event.type == pygame.MOUSEMOTION and dragging:
            dragging["rect"].x = mouse[0]-drag_offset[0]
            dragging["rect"].y = mouse[1]-drag_offset[1]

    # ── DRAW ─────────────────────────────────────────────────

    if phase == "win":
        draw_win_screen()

    elif phase == "arrest":
        draw_red_strings()
        for i in range(5):
            draw_suspect_card(i, mouse)
        done = draw_prison_scene(now, arrest_start)
        if done:
            phase     = "win"
            win_start = now

    else:
        draw_clue_zone_divider()
        draw_red_strings()
        for i in range(5):
            draw_suspect_card(i, mouse)

        # highlight selected suspect
        if selected_suspect is not None and phase == "select_suspect":
            cr   = card_rect(selected_suspect)
            glow = pygame.Rect(cr.x-4, cr.y-4, cr.w+8, cr.h+8)
            pygame.draw.rect(screen, SELECTED_GLOW, glow, 3, border_radius=6)

        for c in ALL_CLUES:
            if not c["placed"] and c is not dragging:
                draw_clue_photo(c, hovered=clue_hit(c,mouse), use_angle=True)

        draw_arrest_button(mouse)
        draw_title_card()
        draw_status_banner()

        if phase == "wrong":
            if now - wrong_timer < 2.0:
                a     = int(110*abs(math.sin((now-wrong_timer)*6)))
                flash = pygame.Surface((W,H),pygame.SRCALPHA)
                flash.fill((180,20,20,a))
                screen.blit(flash,(0,0))
                msg = FONT_WIN.render("WRONG — TRY AGAIN",True,(255,80,80))
                screen.blit(msg,msg.get_rect(center=(W//2,H//2)))
            else:
                phase = "select_suspect"

        if dragging:
            draw_clue_photo(dragging, hovered=True, use_angle=False)

        draw_evidence_button(mouse)
        draw_evidence_panel()
        # alibi popup always on top
        draw_alibi_popup()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()