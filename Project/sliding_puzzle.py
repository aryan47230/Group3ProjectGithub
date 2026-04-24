import pygame
import random


pygame.init()

# --- SETTINGS ---
GRID_SIZE   = 3
TILE_SIZE   = 160
PADDING     = 20
GAP         = 3
TOPBAR      = 45
WINDOW_W    = PADDING * 2 + GRID_SIZE * TILE_SIZE + (GRID_SIZE - 1) * GAP
WINDOW_H    = TOPBAR + PADDING * 2 + GRID_SIZE * TILE_SIZE + (GRID_SIZE - 1) * GAP + 10

IMG_SIZE    = GRID_SIZE * TILE_SIZE

# Colors
BG          = (15, 12, 20)
TOPBAR_BG   = (25, 20, 35)
EMPTY_COL   = (10, 8, 15)
TILE_BORDER = (80, 60, 100)
HOVER_GLOW  = (200, 100, 120)
WIN_COL     = (255, 80, 100)

FONT_UI     = pygame.font.SysFont("Courier", 20, bold=True)
FONT_WIN    = pygame.font.SysFont("Courier", 30, bold=True)
FONT_NUM = pygame.font.SysFont("Courier", 18, bold=True)

screen = None
clock  = None


# ---------------------------------------------------------
#   LOAD IMAGE AND GENERATE TILE IMAGES
# ---------------------------------------------------------

def generate_tile_images():
    full = pygame.image.load("crime_scene.png")                 # <-- change this to your image filename
    full = pygame.transform.scale(full, (IMG_SIZE, IMG_SIZE))  # scale to fit grid
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

def shuffle(board, n=300):
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
                if won:
                    screen.blit(tile_imgs[GRID_SIZE * GRID_SIZE], rect)
                else:
                    pygame.draw.rect(screen, EMPTY_COL, rect, border_radius=4)
                    pygame.draw.rect(screen, (40, 30, 55), rect, 1, border_radius=4)
            else:
                screen.blit(tile_imgs[val], rect)
                num_surf = FONT_NUM.render(str(val), True, (255, 255, 255))
                num_rect = num_surf.get_rect()
                box = pygame.Rect(rect.x + 3, rect.y + 3, num_rect.width + 6, num_rect.height + 2)
                pygame.draw.rect(screen, (0, 0, 0, 180), box, border_radius=3)
                pygame.draw.rect(screen, (80, 60, 100), box, 1, border_radius=3)
                screen.blit(num_surf, (rect.x + 6, rect.y + 4))
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

def draw_ui(won):
    pygame.draw.rect(screen, TOPBAR_BG, (0, 0, WINDOW_W, TOPBAR))
    pygame.draw.line(screen, (70, 50, 90), (0, TOPBAR), (WINDOW_W, TOPBAR), 1)

    title = FONT_UI.render("CRIME SCENE PUZZLE", True, (220, 80, 100))
    screen.blit(title, title.get_rect(center=(WINDOW_W // 2, TOPBAR // 2)))

    if won:
        bar = pygame.Surface((WINDOW_W, 40), pygame.SRCALPHA)
        bar.fill((140, 10, 20, 210))
        screen.blit(bar, (0, WINDOW_H - 40))
        msg = FONT_WIN.render("CASE SOLVED!", True, WIN_COL)
        screen.blit(msg, msg.get_rect(center=(WINDOW_W // 2 - 70, WINDOW_H - 20)))
        close_btn = pygame.Rect(WINDOW_W - 110, WINDOW_H - 34, 100, 26)
        mouse = pygame.mouse.get_pos()
        btn_col = (200, 60, 80) if close_btn.collidepoint(mouse) else (120, 30, 45)
        pygame.draw.rect(screen, btn_col, close_btn, border_radius=4)
        close_lbl = FONT_UI.render("Close", True, (255, 220, 220))
        screen.blit(close_lbl, close_lbl.get_rect(center=close_btn.center))


# ---------------------------------------------------------
#   RUN  (called from main.py or standalone)
# ---------------------------------------------------------

def run(ext_screen=None, ext_clock=None):
    """Run the puzzle. Returns 'menu' or 'quit'."""
    global screen, clock

    from pause import PauseScreen

    # Set up display for this puzzle
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption("Crime Scene Puzzle")
    clock = ext_clock if ext_clock else pygame.time.Clock()

    tile_imgs = generate_tile_images()
    board = solved_board()
    shuffle(board)
    won    = False
    paused = False
    pause_screen = PauseScreen(WINDOW_W, WINDOW_H)

    result  = "quit"
    running = True
    while running:
        dt    = clock.tick(60)
        mouse = pygame.mouse.get_pos()

        hover = None
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if tile_rect(r, c).collidepoint(mouse):
                    hover = (r, c)

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

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if won:
                    close_btn = pygame.Rect(WINDOW_W - 110, WINDOW_H - 34, 100, 26)
                    if close_btn.collidepoint(mouse):
                        running = False
                elif hover:
                    r, c = hover
                    if move(board, r, c):
                        if is_solved(board):
                            won = True

        screen.fill(BG)
        draw_board(board, tile_imgs, hover if not paused else None, won)
        draw_ui(won)

        if paused:
            pause_screen.update(dt)
            pause_screen.draw(screen)

        pygame.display.flip()

    if won:
        import os
        flag = os.path.join(os.path.dirname(os.path.abspath(__file__)), "puzzle1_complete.txt")
        with open(flag, "w") as f:
            f.write("complete")

    return result


def main():
    pygame.init()
    run()
    pygame.quit()


if __name__ == "__main__":
    main()