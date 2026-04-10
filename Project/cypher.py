import pygame
import string
import time
import math
import random as _rnd

pygame.init()

# =============================================================
#  CONFIG
# =============================================================

CIPHER_TEXT = "V GBBX CEBSRFFBE TENVATREF PYNFF ORPNHFR V URNEQ VG JNF NA RNFL N UR TNIR ZR N FVKGL SVIR CREPRAG BA ZL SVANY N FVKGL SVIR CREPRAG"

CIPHER_KEY = {
    "A": "N", "B": "O", "C": "P", "D": "Q", "E": "R",
    "F": "S", "G": "T", "H": "U", "I": "V", "J": "W",
    "K": "X", "L": "Y", "M": "Z", "N": "A", "O": "B",
    "P": "C", "Q": "D", "R": "E", "S": "F", "T": "G",
    "U": "H", "V": "I", "W": "J", "X": "K", "Y": "L",
    "Z": "M",
}

# =============================================================
#  WINDOW & STYLE
# =============================================================

W, H   = 900, 700
screen = None
clock  = None

BG          = (13, 13, 20)
PANEL       = (22, 22, 35)
BORDER      = (60, 55, 85)
ACCENT      = (180, 80, 100)
ACCENT2     = (80, 160, 200)
TEXT_MAIN   = (220, 215, 240)
TEXT_DIM    = (120, 110, 140)
TEXT_CIPHER = (240, 200, 80)
CORRECT     = (80, 200, 120)
WRONG       = (200, 80, 80)
NEUTRAL     = (60, 58, 80)
BTN_CHECK   = (100, 40, 60)
BTN_CHECK_H = (140, 55, 80)
INPUT_BG    = (28, 26, 40)
INPUT_ACT   = (38, 36, 60)
KEY_BG      = (18, 16, 28)
HINT_BG     = (30, 28, 15)
HINT_BORDER = (160, 140, 40)
HINT_TEXT   = (240, 210, 80)
WAVEFORM    = (80, 160, 200)
WAVEFORM2   = (180, 80, 100)
KEY_FILLED  = (60, 180, 120)
CONFLICT    = (220, 120, 40)

FONT_TITLE  = pygame.font.SysFont("Courier", 22, bold=True)
FONT_MED    = pygame.font.SysFont("Courier", 16, bold=True)
FONT_SM     = pygame.font.SysFont("Courier", 13)
FONT_CIPHER = pygame.font.SysFont("Courier", 17, bold=True)
FONT_INPUT  = pygame.font.SysFont("Courier", 16, bold=True)
FONT_KEY    = pygame.font.SysFont("Courier", 12)
FONT_HINT   = pygame.font.SysFont("Courier", 13, bold=True)
FONT_TYPEWR = pygame.font.SysFont("Courier", 20, bold=True)

# =============================================================
#  CIPHER LOGIC
# =============================================================

def split_into_blocks(text, n):
    words = text.split(" ")
    blocks = []
    size = max(1, len(words) // n)
    for i in range(n):
        start = i * size
        end = start + size if i < n - 1 else len(words)
        blocks.append(" ".join(words[start:end]))
    return blocks

def decode_with_key(text, key):
    result = ""
    for ch in text:
        if ch.upper() in key:
            decoded = key[ch.upper()]
            result += decoded if ch.isupper() else decoded.lower()
        else:
            result += ch
    return result

BLOCKS       = split_into_blocks(CIPHER_TEXT, 5)
ANSWERS      = [decode_with_key(b, CIPHER_KEY) for b in BLOCKS]
FULL_DECODED = FULL_DECODED = "I took Professor Grainger's class because I heard it was an easy A. He gave me a sixty five percent on my final, a sixty five percent!"

# =============================================================
#  STATE
# =============================================================

player_inputs = [[""] * len(b) for b in BLOCKS]
active_cell   = None
check_results = [None] * 5
player_key    = {}

def rebuild_player_key():
    global player_key
    player_key = {}
    for bi, block in enumerate(BLOCKS):
        char_idx = 0
        for ch in block:
            if ch != " " and ch in string.ascii_uppercase:
                typed = player_inputs[bi][char_idx] if char_idx < len(player_inputs[bi]) else ""
                if typed:
                    player_key[ch] = typed
            char_idx += 1

def has_conflict(cipher_letter, plain_letter):
    for k, v in player_key.items():
        if v == plain_letter and k != cipher_letter:
            return True
    return False

won            = False
win_phase      = 0
block_positions= []
block_targets  = []
typewriter_idx = 0
typewriter_text= ""
last_char_time = 0.0
TYPEWRITER_SPEED = 0.045

# =============================================================
#  LAYOUT
# =============================================================

BLOCK_PANEL_TOP = 60
BLOCK_PANEL_H   = 82
BLOCK_PANEL_GAP = 6
KEY_PANEL_TOP   = BLOCK_PANEL_TOP + 5 * (BLOCK_PANEL_H + BLOCK_PANEL_GAP) + 10
KEY_PANEL_H     = 100
HINT_TOP        = KEY_PANEL_TOP + KEY_PANEL_H + 8
HINT_H          = 28

CHECK_BTN_W, CHECK_BTN_H = 70, 28
CELL_W, CELL_H            = 16, 24
WAVE_W                    = 80

def block_panel_y(i):
    return BLOCK_PANEL_TOP + i * (BLOCK_PANEL_H + BLOCK_PANEL_GAP)

def block_panel_rect(i, override_y=None):
    y = override_y if override_y is not None else block_panel_y(i)
    return pygame.Rect(10, y, W - 20, BLOCK_PANEL_H)

def wave_rect(i, override_y=None):
    pr = block_panel_rect(i, override_y)
    return pygame.Rect(pr.x + 8, pr.y + (BLOCK_PANEL_H - 38) // 2, WAVE_W, 38)

def check_btn_rect(i, override_y=None):
    pr = block_panel_rect(i, override_y)
    return pygame.Rect(pr.right - CHECK_BTN_W - 8,
                       pr.y + (BLOCK_PANEL_H - CHECK_BTN_H) // 2,
                       CHECK_BTN_W, CHECK_BTN_H)

def cells_start_x(i):
    return wave_rect(i).right + 12

def cell_rect(block_i, char_i, override_y=None):
    bx = cells_start_x(block_i)
    pr = block_panel_rect(block_i, override_y)
    return pygame.Rect(bx + char_i * (CELL_W + 1), pr.y + 30, CELL_W, CELL_H)

# =============================================================
#  WAVEFORM
# =============================================================

_rnd.seed(42)
WAVE_HEIGHTS = [[_rnd.randint(4, 18) for _ in range(18)] for _ in range(5)]

def draw_waveform(rect, block_i, t, solved):
    n    = len(WAVE_HEIGHTS[block_i])
    bw   = max(2, (rect.width - (n - 1) * 2) // n)
    col  = CORRECT if solved else WAVEFORM
    col2 = CORRECT if solved else WAVEFORM2
    for j, h_base in enumerate(WAVE_HEIGHTS[block_i]):
        h = int(h_base + 5 * math.sin(t * 3 + j * 0.6))
        h = max(3, min(rect.height - 2, h))
        x = rect.x + j * (bw + 2)
        y = rect.centery - h // 2
        c = col if j % 2 == 0 else col2
        pygame.draw.rect(screen, c, (x, y, bw, h), border_radius=2)

# =============================================================
#  DRAWING
# =============================================================

def draw_button(rect, label, base_col, hover_col, mouse_pos):
    col = hover_col if rect.collidepoint(mouse_pos) else base_col
    pygame.draw.rect(screen, col, rect, border_radius=5)
    pygame.draw.rect(screen, BORDER, rect, 1, border_radius=5)
    s = FONT_SM.render(label, True, TEXT_MAIN)
    screen.blit(s, s.get_rect(center=rect.center))

def draw_blocks(mouse_pos, t):
    for i, block in enumerate(BLOCKS):
        pr = block_panel_rect(i)
        pygame.draw.rect(screen, PANEL, pr, border_radius=6)
        pygame.draw.rect(screen, BORDER, pr, 1, border_radius=6)

        screen.blit(FONT_SM.render(f"BLOCK {i+1}", True, TEXT_DIM),
                    (pr.x + WAVE_W + 18, pr.y + 4))

        solved_block = check_results[i] is not None and all(check_results[i])
        draw_waveform(wave_rect(i), i, t, solved_block)
        draw_button(check_btn_rect(i), "CHECK", BTN_CHECK, BTN_CHECK_H, mouse_pos)

        bx     = cells_start_x(i)
        max_x  = check_btn_rect(i).x - 10
        cy_cip = pr.y + 12
        cy_inp = pr.y + 30
        x_cur  = bx
        char_idx = 0

        for ch in block:
            if x_cur + CELL_W > max_x:
                break
            if ch == " ":
                x_cur    += CELL_W // 2 + 2
                char_idx += 1
                continue

            screen.blit(FONT_CIPHER.render(ch, True, TEXT_CIPHER), (x_cur + 1, cy_cip))

            cr        = pygame.Rect(x_cur, cy_inp, CELL_W, CELL_H)
            is_active = (active_cell == (i, char_idx))
            result    = check_results[i]

            if result is not None and char_idx < len(result):
                cell_col   = CORRECT if result[char_idx] else WRONG
                border_col = CORRECT if result[char_idx] else WRONG
            elif is_active:
                cell_col   = INPUT_ACT
                border_col = ACCENT2
            else:
                cell_col   = INPUT_BG
                border_col = NEUTRAL

            pygame.draw.rect(screen, cell_col, cr, border_radius=2)
            pygame.draw.rect(screen, border_col, cr, 1, border_radius=2)

            typed = player_inputs[i][char_idx] if char_idx < len(player_inputs[i]) else ""
            if typed:
                ts = FONT_INPUT.render(typed, True, TEXT_MAIN)
                screen.blit(ts, ts.get_rect(center=cr.center))

            x_cur    += CELL_W + 1
            char_idx += 1

def draw_key_panel():
    kr = pygame.Rect(10, KEY_PANEL_TOP, W - 20, KEY_PANEL_H)
    pygame.draw.rect(screen, KEY_BG, kr, border_radius=6)
    pygame.draw.rect(screen, BORDER, kr, 1, border_radius=6)
    screen.blit(FONT_MED.render("SUBSTITUTION KEY  (fills as you type)", True, ACCENT),
                (kr.x + 10, kr.y + 7))

    for idx, letter in enumerate(string.ascii_uppercase):
        col        = idx % 13
        row_offset = (idx // 13) * 38
        x          = kr.x + 10 + col * 30
        y1         = kr.y + 26 + row_offset
        y2         = kr.y + 44 + row_offset

        screen.blit(FONT_KEY.render(letter, True, TEXT_CIPHER), (x, y1))

        filled = player_key.get(letter, "")
        if filled:
            conflict  = has_conflict(letter, filled)
            col_plain = CONFLICT if conflict else KEY_FILLED
            screen.blit(FONT_KEY.render(filled, True, col_plain), (x, y2))
        else:
            screen.blit(FONT_KEY.render("_", True, NEUTRAL), (x, y2))

        pygame.draw.line(screen, BORDER, (x - 2, y1 - 2), (x - 2, y2 + 12), 1)

def draw_hint():
    hr = pygame.Rect(10, HINT_TOP, W - 20, HINT_H)
    pygame.draw.rect(screen, HINT_BG, hr, border_radius=5)
    pygame.draw.rect(screen, HINT_BORDER, hr, 1, border_radius=5)
    hint = FONT_HINT.render("Hint:  TENVATREF  =  GRAINGERS", True, HINT_TEXT)
    screen.blit(hint, hint.get_rect(midleft=(hr.x + 14, hr.centery)))

def draw_title():
    pygame.draw.rect(screen, PANEL, (0, 0, W, 52))
    pygame.draw.line(screen, ACCENT, (0, 52), (W, 52), 1)
    t = FONT_TITLE.render("[ VOICE DESCRAMBLER ]  —  ARISTOCRAT CIPHER", True, ACCENT)
    screen.blit(t, (W // 2 - t.get_width() // 2, 15))

# =============================================================
#  WIN ANIMATION
# =============================================================

def start_win_animation():
    global win_phase, block_positions, block_targets
    global typewriter_idx, typewriter_text, last_char_time

    win_phase       = 1
    typewriter_idx  = 0
    typewriter_text = ""
    last_char_time  = 0.0

    block_positions = [float(block_panel_y(i)) for i in range(5)]
    stack_total_h   = 5 * BLOCK_PANEL_H + 4 * BLOCK_PANEL_GAP
    stack_top       = (H - stack_total_h) // 2 - 40
    block_targets   = [float(stack_top + i * (BLOCK_PANEL_H + BLOCK_PANEL_GAP))
                       for i in range(5)]

def draw_win_animation(t):
    global win_phase, block_positions, typewriter_idx, typewriter_text, last_char_time

    now   = time.time()
    dt    = clock.get_time() / 1000.0
    SPEED = 6.0

    if win_phase == 1:
        all_arrived = True
        for i in range(5):
            diff = block_targets[i] - block_positions[i]
            if abs(diff) > 0.5:
                block_positions[i] += diff * SPEED * dt
                all_arrived = False
            else:
                block_positions[i] = block_targets[i]

        for i in range(5):
            y  = int(block_positions[i])
            pr = block_panel_rect(i, y)
            pygame.draw.rect(screen, PANEL, pr, border_radius=6)
            pygame.draw.rect(screen, CORRECT, pr, 2, border_radius=6)
            draw_waveform(wave_rect(i, y), i, t, True)
            ans_surf = FONT_MED.render(ANSWERS[i], True, CORRECT)
            screen.blit(ans_surf, (pr.x + WAVE_W + 18,
                                   pr.centery - ans_surf.get_height() // 2))

        if all_arrived:
            win_phase      = 2
            last_char_time = now

    elif win_phase == 2:
        for i in range(5):
            y  = int(block_positions[i])
            pr = block_panel_rect(i, y)
            pygame.draw.rect(screen, PANEL, pr, border_radius=6)
            pygame.draw.rect(screen, CORRECT, pr, 2, border_radius=6)
            draw_waveform(wave_rect(i, y), i, t, True)
            ans_surf = FONT_MED.render(ANSWERS[i], True, CORRECT)
            screen.blit(ans_surf, (pr.x + WAVE_W + 18,
                                   pr.centery - ans_surf.get_height() // 2))

        if typewriter_idx < len(FULL_DECODED):
            if now - last_char_time >= TYPEWRITER_SPEED:
                typewriter_idx += 1
                last_char_time  = now
        typewriter_text = FULL_DECODED[:typewriter_idx]

        tw_rect = pygame.Rect(10, H - 130, W - 20, 115)
        pygame.draw.rect(screen, KEY_BG, tw_rect, border_radius=6)
        pygame.draw.rect(screen, CORRECT, tw_rect, 2, border_radius=6)
        screen.blit(FONT_SM.render("DECODED TRANSMISSION:", True, TEXT_DIM),
                    (tw_rect.x + 12, tw_rect.y + 8))

        cursor  = "|" if int(now * 2) % 2 == 0 else ""
        display = typewriter_text + cursor

        # wrap text across multiple lines
        words   = display.split(" ")
        lines   = []
        current = ""
        for word in words:
            test = current + (" " if current else "") + word
            if FONT_TYPEWR.size(test)[0] < tw_rect.width - 24:
                current = test
            else:
                lines.append(current)
                current = word
        lines.append(current)

        for li, line in enumerate(lines):
            screen.blit(FONT_TYPEWR.render(line, True, CORRECT),
                        (tw_rect.x + 12, tw_rect.y + 28 + li * 26))

        if typewriter_idx >= len(FULL_DECODED):
            hdr = FONT_TITLE.render("[ TRANSMISSION DECODED ]", True, CORRECT)
            screen.blit(hdr, hdr.get_rect(center=(W // 2, 30)))

# =============================================================
#  GAME LOGIC
# =============================================================

def check_block(i):
    answer   = ANSWERS[i]
    block    = BLOCKS[i]
    full     = []
    char_idx = 0
    for ch in block:
        if ch == " ":
            full.append(True)
        else:
            typed   = player_inputs[i][char_idx] if char_idx < len(player_inputs[i]) else ""
            correct = answer[char_idx] if char_idx < len(answer) else ""
            full.append(typed.upper() == correct.upper())
        char_idx += 1
    check_results[i] = full

def all_solved():
    return all(
        check_results[i] is not None and all(check_results[i])
        for i in range(5)
    )

def next_input_cell(block_i, char_i, direction=1):
    block = BLOCKS[block_i]
    idx   = char_i + direction
    while 0 <= idx < len(block):
        if block[idx] != " ":
            return (block_i, idx)
        idx += direction
    return None

def click_cell(mouse_pos):
    global active_cell
    for i, block in enumerate(BLOCKS):
        for char_idx, ch in enumerate(block):
            if ch != " ":
                if cell_rect(i, char_idx).collidepoint(mouse_pos):
                    active_cell = (i, char_idx)
                    return
    active_cell = None

# =============================================================
#  RUN  (called from main.py or standalone)
# =============================================================

def run(ext_screen=None, ext_clock=None):
    """Run the puzzle. Returns 'menu' or 'quit'."""
    global screen, clock
    global player_inputs, active_cell, check_results, player_key
    global won, win_phase, block_positions, block_targets
    global typewriter_idx, typewriter_text, last_char_time

    from pause import PauseScreen

    # Set up display
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Voice Descrambler")
    clock = ext_clock if ext_clock else pygame.time.Clock()

    # Reset all game state
    player_inputs  = [[""] * len(b) for b in BLOCKS]
    active_cell    = None
    check_results  = [None] * 5
    player_key     = {}
    won            = False
    win_phase      = 0
    block_positions= []
    block_targets  = []
    typewriter_idx = 0
    typewriter_text= ""
    last_char_time = 0.0

    paused       = False
    pause_screen = PauseScreen(W, H)
    result       = "quit"
    running      = True
    start_t      = time.time()

    while running:
        clock.tick(60)
        t     = time.time() - start_t
        mouse = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                paused = not paused
                if not paused:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

            elif paused:
                action = pause_screen.handle_event(event)
                if action == "resume":
                    paused = False
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                elif action == "quit":
                    result  = "menu"
                    running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not won:
                for i in range(5):
                    if check_btn_rect(i).collidepoint(mouse):
                        check_block(i)
                click_cell(mouse)

            elif event.type == pygame.KEYDOWN and active_cell and not won:
                bi, ci = active_cell

                if event.key == pygame.K_BACKSPACE:
                    player_inputs[bi][ci] = ""
                    check_results[bi]     = None
                    rebuild_player_key()
                    prev = next_input_cell(bi, ci, -1)
                    if prev:
                        active_cell = prev

                elif event.key in (pygame.K_LEFT, pygame.K_UP):
                    prev = next_input_cell(bi, ci, -1)
                    if prev:
                        active_cell = prev

                elif event.key in (pygame.K_RIGHT, pygame.K_DOWN, pygame.K_RETURN):
                    nxt = next_input_cell(bi, ci, 1)
                    if nxt:
                        active_cell = nxt

                elif event.unicode.upper() in string.ascii_uppercase:
                    player_inputs[bi][ci] = event.unicode.upper()
                    check_results[bi]     = None
                    rebuild_player_key()
                    nxt = next_input_cell(bi, ci, 1)
                    if nxt:
                        active_cell = nxt

        screen.fill(BG)

        if not won:
            draw_title()
            draw_blocks(mouse, t)
            draw_key_panel()
            draw_hint()
            if all_solved():
                won = True
                start_win_animation()
        else:
            draw_win_animation(t)

        if paused:
            pause_screen.update(clock.get_time())
            pause_screen.draw(screen)

        pygame.display.flip()

    return result


def main():
    pygame.init()
    run()
    pygame.quit()


if __name__ == "__main__":
    main()