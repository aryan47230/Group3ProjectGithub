import pygame
import random
import time

pygame.init()

# --- SETTINGS ---
GRID_SIZE   = 3
TILE_SIZE   = 120
PADDING     = 20
GAP         = 3
TOPBAR      = 60
WINDOW_W    = PADDING * 2 + GRID_SIZE * TILE_SIZE + (GRID_SIZE - 1) * GAP
WINDOW_H    = TOPBAR + PADDING * 2 + GRID_SIZE * TILE_SIZE + (GRID_SIZE - 1) * GAP + 50

IMG_SIZE    = GRID_SIZE * TILE_SIZE  # 480x480 pixel art canvas

# Colors
BG          = (15, 12, 20)
TOPBAR_BG   = (25, 20, 35)
EMPTY_COL   = (10, 8, 15)
TILE_BORDER = (80, 60, 100)
HOVER_GLOW  = (200, 100, 120)
TEXT_COL    = (220, 200, 240)
WIN_COL     = (255, 80, 100)
BTN_COL     = (80, 40, 60)
BTN_HOVER   = (120, 60, 80)
BTN_TEXT    = (255, 200, 220)

FONT_TILE   = pygame.font.SysFont("Courier", 18, bold=True)
FONT_UI     = pygame.font.SysFont("Courier", 20, bold=True)
FONT_WIN    = pygame.font.SysFont("Courier", 30, bold=True)
FONT_SMALL  = pygame.font.SysFont("Courier", 13)

screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
pygame.display.set_caption("Crime Scene Puzzle")
clock = pygame.time.Clock()


# ---------------------------------------------------------
#   PIXEL ART MURDER SCENE  (drawn entirely in code)
# ---------------------------------------------------------

def draw_pixel_art(surface):
    """
    Draws a gritty pixel-art murder scene onto a 480x480 surface.
    P=10 means each 'fat pixel' is a 10x10 block.
    """
    W, H = IMG_SIZE, IMG_SIZE
    P = 10  # base pixel size

    def px(x, y, w, h, color):
        pygame.draw.rect(surface, color, (x * P, y * P, w * P, h * P))

    # -- Floor --------------------------------------------------
    surface.fill((28, 22, 18))
    for row in range(0, H // P, 4):
        shade = (35, 27, 21) if (row // 4) % 2 == 0 else (22, 17, 13)
        pygame.draw.rect(surface, shade, (0, row * P, W, 3 * P))
        pygame.draw.rect(surface, (18, 13, 10), (0, (row + 3) * P, W, P))

    # -- Wall ---------------------------------------------------
    WALL = (45, 38, 55)
    px(0, 0, 48, 16, WALL)
    for col in range(0, 48, 6):
        stripe = (50, 42, 60) if (col // 6) % 2 == 0 else WALL
        px(col, 0, 6, 16, stripe)
    px(0, 16, 48, 1, (60, 50, 70))

    # -- Window (cracked) ---------------------------------------
    px(30, 1, 12, 12, (30, 55, 80))
    px(30, 1, 12, 1, (100, 80, 60))
    px(30, 12, 12, 1, (100, 80, 60))
    px(30, 1, 1, 12, (100, 80, 60))
    px(41, 1, 1, 12, (100, 80, 60))
    px(35, 1, 1, 12, (90, 72, 55))
    px(30, 6, 12, 1, (90, 72, 55))
    pygame.draw.line(surface, (200, 220, 255), (330, 25), (370, 60), 1)
    pygame.draw.line(surface, (200, 220, 255), (355, 35), (385, 58), 1)

    # moonlight beam
    beam_surf = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.polygon(beam_surf, (40, 60, 90, 35),
                        [(310, 120), (410, 120), (460, 300), (260, 300)])
    surface.blit(beam_surf, (0, 0))

    # -- Bookshelf ----------------------------------------------
    px(0, 1, 8, 14, (55, 42, 30))
    BOOKS = [(200,50,50),(50,120,80),(80,80,160),(180,140,40),
             (140,60,140),(60,130,130),(200,100,60),(50,80,180)]
    for i, bc in enumerate(BOOKS):
        bx = i % 4
        by = i // 4
        px(1 + bx * 2, 2 + by * 6, 2, 5, bc)
    px(0, 7, 8, 1, (70, 55, 38))
    px(0, 14, 8, 1, (70, 55, 38))

    # -- Overturned chair ---------------------------------------
    CHAIR  = (90, 60, 35)
    CHAIRD = (65, 42, 22)
    px(10, 28, 1, 5, CHAIRD)
    px(16, 30, 5, 1, CHAIRD)
    px(13, 35, 1, 4, CHAIRD)
    px(18, 29, 1, 5, CHAIRD)
    px(9, 26, 10, 3, CHAIR)
    px(9, 25, 10, 1, (110, 75, 42))

    # -- Desk ---------------------------------------------------
    DESK = (100, 72, 45)
    px(20, 22, 22, 4, DESK)
    px(20, 22, 22, 1, (120, 88, 55))
    px(20, 26, 2, 6, DESK)
    px(40, 26, 2, 6, DESK)

    # papers on desk
    px(22, 20, 5, 2, (235, 230, 215))
    px(26, 19, 6, 2, (220, 215, 200))
    px(30, 21, 4, 2, (230, 225, 210))

    # knocked-over mug + coffee spill
    px(34, 22, 2, 2, (200, 190, 180))
    px(34, 24, 4, 1, (30, 20, 15))
    px(35, 25, 6, 1, (25, 15, 10))
    px(36, 26, 3, 1, (20, 12, 8))

    # candlestick (weapon hint)
    px(38, 20, 2, 3, (210, 190, 100))
    px(37, 23, 4, 1, (180, 160, 80))
    px(38, 18, 1, 2, (255, 230, 150))
    px(39, 17, 1, 1, (255, 180, 50))

    # -- Body ---------------------------------------------------
    SKIN  = (200, 160, 130)
    SHIRT = (60, 80, 120)
    PANTS = (40, 55, 85)
    px(14, 36, 8, 5, SHIRT)
    px(22, 34, 5, 5, SKIN)
    px(23, 33, 3, 2, (160, 120, 90))
    px(12, 36, 3, 2, SKIN)
    px(10, 37, 3, 1, SKIN)
    px(8,  38, 3, 1, SKIN)
    px(22, 40, 3, 2, SKIN)
    px(14, 41, 4, 4, PANTS)
    px(18, 41, 4, 4, PANTS)
    px(14, 45, 4, 2, (80, 60, 45))
    px(18, 45, 4, 2, (70, 52, 38))

    # -- Blood --------------------------------------------------
    BLOOD  = (140, 15, 20)
    BLOOD2 = (100, 10, 15)
    px(20, 38, 8, 4, BLOOD)
    px(18, 39, 12, 3, BLOOD)
    px(19, 37, 6, 2, BLOOD2)
    px(28, 37, 2, 1, BLOOD2)
    px(30, 36, 1, 2, BLOOD2)
    px(17, 42, 2, 1, BLOOD2)
    px(29, 41, 1, 2, BLOOD2)
    px(32, 39, 2, 1, BLOOD2)
    px(25, 43, 1, 1, BLOOD2)
    px(24, 26, 1, 2, BLOOD2)
    px(26, 26, 2, 1, BLOOD2)

    # -- Knife on floor -----------------------------------------
    pygame.draw.polygon(surface, (190, 200, 210),
                        [(350, 430), (420, 400), (425, 410), (358, 442)])
    pygame.draw.polygon(surface, (90, 60, 35),
                        [(330, 440), (352, 430), (358, 442), (336, 452)])
    pygame.draw.ellipse(surface, BLOOD, (355, 432, 30, 8))

    # -- Footprints in blood ------------------------------------
    px(33, 44, 2, 1, BLOOD2)
    px(34, 45, 3, 1, BLOOD2)
    px(37, 44, 2, 1, BLOOD2)
    px(38, 45, 3, 1, BLOOD2)
    px(33, 42, 1, 1, BLOOD2)
    px(35, 42, 1, 1, BLOOD2)
    px(37, 42, 1, 1, BLOOD2)

    # -- Chalk outline ------------------------------------------
    chalk_surf = pygame.Surface((W, H), pygame.SRCALPHA)
    points = [(145,360),(220,340),(270,340),(280,380),
              (230,420),(200,430),(140,420),(130,390)]
    pygame.draw.lines(chalk_surf, (200, 200, 210, 180), True, points, 2)
    surface.blit(chalk_surf, (0, 0))

    # -- Vignette -----------------------------------------------
    vig = pygame.Surface((W, H), pygame.SRCALPHA)
    for r in range(0, max(W, H) // 2, 4):
        alpha = max(0, 110 - r // 2)
        pygame.draw.circle(vig, (0, 0, 0, alpha),
                           (W // 2, H // 2), max(W, H) // 2 - r, 4)
    surface.blit(vig, (0, 0))


# ---------------------------------------------------------
#   GENERATE TILE IMAGES
# ---------------------------------------------------------

def generate_tile_images():
    """Renders full scene then slices into GRID_SIZE x GRID_SIZE tiles."""
    full = pygame.Surface((IMG_SIZE, IMG_SIZE))
    draw_pixel_art(full)
    tiles = {}
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            idx = r * GRID_SIZE + c + 1
            sub = pygame.Surface((TILE_SIZE, TILE_SIZE))
            sub.blit(full, (0, 0),
                     (c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            tiles[idx] = sub
    return tiles


# ---------------------------------------------------------
#   PUZZLE LOGIC
# ---------------------------------------------------------

def solved_board():
    nums = list(range(1, GRID_SIZE * GRID_SIZE)) + [0]
    return [nums[i * GRID_SIZE:(i + 1) * GRID_SIZE] for i in range(GRID_SIZE)]

def find_empty(board):
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if board[r][c] == 0:
                return r, c

def movable_tiles(board):
    er, ec = find_empty(board)
    result = []
    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
        nr, nc = er+dr, ec+dc
        if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
            result.append((nr, nc))
    return result

def move(board, r, c):
    er, ec = find_empty(board)
    if (r, c) in movable_tiles(board):
        board[er][ec], board[r][c] = board[r][c], board[er][ec]
        return True
    return False

def shuffle(board, n=400):
    for _ in range(n):
        r, c = random.choice(movable_tiles(board))
        move(board, r, c)

def is_solved(board):
    return board == solved_board()


# ---------------------------------------------------------
#   DRAWING
# ---------------------------------------------------------

def tile_rect(r, c):
    x = PADDING + c * (TILE_SIZE + GAP)
    y = TOPBAR + PADDING + r * (TILE_SIZE + GAP)
    return pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

def draw_board(board, tile_imgs, hover, won):
    movable = movable_tiles(board)
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            rect = tile_rect(r, c)
            val  = board[r][c]
            if val == 0:
                pygame.draw.rect(screen, EMPTY_COL, rect, border_radius=4)
                pygame.draw.rect(screen, (40, 30, 55), rect, 1, border_radius=4)
            else:
                screen.blit(tile_imgs[val], rect)
                is_hover   = (r, c) == hover
                is_movable = (r, c) in movable
                if is_hover and is_movable:
                    pygame.draw.rect(screen, HOVER_GLOW, rect, 3, border_radius=2)
                else:
                    pygame.draw.rect(screen, TILE_BORDER, rect, 1, border_radius=2)
                if not is_movable and not won:
                    dim = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                    dim.fill((0, 0, 0, 60))
                    screen.blit(dim, rect)
                num_surf = FONT_SMALL.render(str(val), True, (255, 255, 255))
                screen.blit(num_surf, (rect.x + 4, rect.y + 3))

def draw_ui(moves, elapsed, btn_rect, btn_hovered, won):
    pygame.draw.rect(screen, TOPBAR_BG, (0, 0, WINDOW_W, TOPBAR))
    pygame.draw.line(screen, (70, 50, 90), (0, TOPBAR), (WINDOW_W, TOPBAR), 1)

    title = FONT_UI.render("CRIME SCENE PUZZLE", True, (220, 80, 100))
    screen.blit(title, (PADDING, 10))

    stats = FONT_SMALL.render(f"moves: {moves}   time: {int(elapsed)}s", True, (160, 140, 180))
    screen.blit(stats, (PADDING, 36))

    color = BTN_HOVER if btn_hovered else BTN_COL
    pygame.draw.rect(screen, color, btn_rect, border_radius=6)
    pygame.draw.rect(screen, (120, 80, 100), btn_rect, 1, border_radius=6)
    btn_label = FONT_SMALL.render("NEW CASE", True, BTN_TEXT)
    screen.blit(btn_label, btn_label.get_rect(center=btn_rect.center))

    if won:
        bar = pygame.Surface((WINDOW_W, 50), pygame.SRCALPHA)
        bar.fill((140, 10, 20, 210))
        screen.blit(bar, (0, WINDOW_H - 50))
        msg = FONT_WIN.render(f"CASE SOLVED  -  {moves} moves, {int(elapsed)}s", True, WIN_COL)
        screen.blit(msg, msg.get_rect(center=(WINDOW_W // 2, WINDOW_H - 25)))


# ---------------------------------------------------------
#   MAIN
# ---------------------------------------------------------

def main():
    tile_imgs = generate_tile_images()

    board   = solved_board()
    shuffle(board)
    moves   = 0
    won     = False
    start   = time.time()
    elapsed = 0

    btn_rect = pygame.Rect(WINDOW_W - 110, 12, 95, 32)

    running = True
    while running:
        screen.fill(BG)
        mouse = pygame.mouse.get_pos()

        hover = None
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if tile_rect(r, c).collidepoint(mouse):
                    hover = (r, c)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_rect.collidepoint(mouse):
                    board   = solved_board()
                    shuffle(board)
                    moves   = 0
                    won     = False
                    start   = time.time()
                    elapsed = 0
                elif not won and hover:
                    r, c = hover
                    if move(board, r, c):
                        moves += 1
                        if is_solved(board):
                            won     = True
                            elapsed = time.time() - start

        if not won:
            elapsed = time.time() - start

        draw_board(board, tile_imgs, hover, won)
        draw_ui(moves, elapsed, btn_rect, btn_rect.collidepoint(mouse), won)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
