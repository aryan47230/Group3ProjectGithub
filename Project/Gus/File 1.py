import pygame
import sys
import subprocess
import os

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PLAYER_SPEED = 5

WHITE  = (255, 255, 255)
BLACK  = (  0,   0,   0)
BLUE   = ( 50, 120, 220)
GRAY   = (200, 200, 200)
RED    = (220,  50,  50)

# Collision rectangles (x, y, w, h) in 800x600 screen space.
# Press D in-game to show/hide them for tuning.
COLLISION_RECTS = [
    # top wall
    pygame.Rect(  0,   0, 800, 200),
    # left wall segment
    pygame.Rect(  0, 200,  50, 200),
    # central back staircase
    pygame.Rect(275,  75, 250, 195),
]


FRAME_W = 16
FRAME_H = 17
# Sheet layout: 4 cols (down, left, right, up) × 3 rows (anim frames)
DIRECTION_COL = {"down": 0, "left": 3, "up": 2, "right": 1}
ANIM_FRAMES   = 3   # rows in the sprite sheet
ANIM_SPEED    = 8   # game ticks per frame


class Player(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int):
        super().__init__()
        sheet = pygame.image.load("/Users/gus/Library/CloudStorage/OneDrive-UniversityofIllinois-Urbana/CS honor/Group3ProjectGithub/Project/Gus/Sprites/Males/M_03.png").convert()
        sheet.set_colorkey(sheet.get_at((0, 0)))
        self.sheet = sheet

        self.direction  = "down"
        self.anim_index = 0        # standing frame
        self.anim_timer = 0
        self.moving     = False

        self.image = self._get_frame()
        self.rect  = self.image.get_rect(center=(x, y))

    def _get_frame(self) -> pygame.Surface:
        col   = DIRECTION_COL[self.direction]
        row   = self.anim_index
        frame = self.sheet.subsurface(pygame.Rect(col * FRAME_W, row * FRAME_H, FRAME_W, FRAME_H))
        return pygame.transform.scale(frame, (48, 48))

    def handle_input(self) -> None:
        keys = pygame.key.get_pressed()

        dx = dy = 0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: dx -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += PLAYER_SPEED
        if keys[pygame.K_UP]    or keys[pygame.K_w]: dy -= PLAYER_SPEED
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: dy += PLAYER_SPEED

        self.moving = dx != 0 or dy != 0

        # Update facing direction (prefer horizontal when diagonal)
        if dx < 0:
            self.direction = "left"
        elif dx > 0:
            self.direction = "right"
        elif dy < 0:
            self.direction = "up"
        elif dy > 0:
            self.direction = "down"

        # Move X, check collisions, revert if blocked
        self.rect.x += dx
        if any(self.rect.colliderect(r) for r in COLLISION_RECTS):
            self.rect.x -= dx

        # Move Y, check collisions, revert if blocked
        self.rect.y += dy
        if any(self.rect.colliderect(r) for r in COLLISION_RECTS):
            self.rect.y -= dy

        self.rect.clamp_ip(pygame.display.get_surface().get_rect())

    def update(self) -> None:
        self.handle_input()

        if self.moving:
            self.anim_timer += 1
            if self.anim_timer >= ANIM_SPEED:
                self.anim_timer  = 0
                self.anim_index  = (self.anim_index + 1) % ANIM_FRAMES
        else:
            self.anim_index = 0   # reset to standing frame
            self.anim_timer = 0

        self.image = self._get_frame()


def draw_grid(surface: pygame.Surface, cell: int = 50) -> None:
    for x in range(0, SCREEN_WIDTH, cell):
        pygame.draw.line(surface, GRAY, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, cell):
        pygame.draw.line(surface, GRAY, (0, y), (SCREEN_WIDTH, y))


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Basic Player Movement")
    clock = pygame.time.Clock()
    font  = pygame.font.SysFont("monospace", 16)

    background = pygame.image.load(
        "/Users/gus/Library/CloudStorage/OneDrive-UniversityofIllinois-Urbana/CS honor/Group3ProjectGithub/Project/Gus/library.png"
    ).convert()
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

    background_3rd = pygame.image.load(
        "/Users/gus/Library/CloudStorage/OneDrive-UniversityofIllinois-Urbana/CS honor/Group3ProjectGithub/Project/Gus/dark_3rd_floor.png"
    ).convert()
    background_3rd = pygame.transform.scale(background_3rd, (SCREEN_WIDTH, SCREEN_HEIGHT))

    FLOOR_TRIGGER = pygame.Rect(350, 200, 100, 100)   # near x=400, y=250
    on_3rd_floor = False

    coffee_img = pygame.image.load(
        "/Users/gus/Library/CloudStorage/OneDrive-UniversityofIllinois-Urbana/CS honor/Group3ProjectGithub/Project/Gus/coffee.png"
    ).convert_alpha()
    coffee_img = pygame.transform.scale(coffee_img, (38, 38))
    coffee_rect = coffee_img.get_rect(topleft=(350, 410))

    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    all_sprites = pygame.sprite.Group(player)
    debug = False

    PUZZLE1_TRIGGER = pygame.Rect(700, 350, 260, 65)
    SLIDING_PUZZLE_PATH = "/Users/gus/Library/CloudStorage/OneDrive-UniversityofIllinois-Urbana/CS honor/Group3ProjectGithub/Project/sliding_puzzle.py"
    PUZZLE1_FLAG = "/Users/gus/Library/CloudStorage/OneDrive-UniversityofIllinois-Urbana/CS honor/Group3ProjectGithub/Project/puzzle1_complete.txt"

    PUZZLE2_TRIGGER = pygame.Rect(170, 320, 100, 80)   # near x=200, y=350
    CYPHER_PATH = "/Users/gus/Library/CloudStorage/OneDrive-UniversityofIllinois-Urbana/CS honor/Group3ProjectGithub/Project/cypher.py"
    PUZZLE2_FLAG = "/Users/gus/Library/CloudStorage/OneDrive-UniversityofIllinois-Urbana/CS honor/Group3ProjectGithub/Project/puzzle2_complete.txt"

    STAIRCASE_RECT = pygame.Rect(275, 75, 250, 195)

    puzzle1_done = os.path.exists(PUZZLE1_FLAG)
    puzzle2_done = os.path.exists(PUZZLE2_FLAG)
    if puzzle2_done and STAIRCASE_RECT in COLLISION_RECTS:
        COLLISION_RECTS.remove(STAIRCASE_RECT)

    wellDone_timer = 0   # frames remaining to show completion message

    prompt_font = pygame.font.SysFont("monospace", 13, bold=True)

    while True:
        # Check puzzle completions from subprocesses
        if not puzzle1_done and os.path.exists(PUZZLE1_FLAG):
            puzzle1_done = True
            wellDone_timer = FPS * 6

        if not puzzle2_done and os.path.exists(PUZZLE2_FLAG):
            puzzle2_done = True
            wellDone_timer = FPS * 6
            if STAIRCASE_RECT in COLLISION_RECTS:
                COLLISION_RECTS.remove(STAIRCASE_RECT)

        near_puzzle1 = (not puzzle1_done) and PUZZLE1_TRIGGER.colliderect(player.rect)
        near_puzzle2 = puzzle1_done and (not puzzle2_done) and PUZZLE2_TRIGGER.colliderect(player.rect)

        if FLOOR_TRIGGER.colliderect(player.rect):
            on_3rd_floor = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_d:
                    debug = not debug
                if event.key == pygame.K_e and near_puzzle1:
                    subprocess.Popen(
                        [sys.executable, SLIDING_PUZZLE_PATH],
                        cwd="/Users/gus/Library/CloudStorage/OneDrive-UniversityofIllinois-Urbana/CS honor/Group3ProjectGithub/Project"
                    )
                if event.key == pygame.K_e and near_puzzle2:
                    subprocess.Popen(
                        [sys.executable, CYPHER_PATH],
                        cwd="/Users/gus/Library/CloudStorage/OneDrive-UniversityofIllinois-Urbana/CS honor/Group3ProjectGithub/Project"
                    )

        if wellDone_timer > 0:
            wellDone_timer -= 1

        all_sprites.update()

        screen.blit(background_3rd if on_3rd_floor else background, (0, 0))
        draw_grid(screen)
        screen.blit(coffee_img, coffee_rect)
        all_sprites.draw(screen)

        if near_puzzle1:
            label = prompt_font.render("Puzzle 1  [Press E to open]", True, WHITE)
            bg = pygame.Surface((label.get_width() + 16, label.get_height() + 10), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 160))
            bx = max(0, player.rect.centerx - bg.get_width() // 2)
            by = player.rect.top - bg.get_height() - 8
            if by < 0:
                by = player.rect.bottom + 8
            screen.blit(bg, (bx, by))
            screen.blit(label, (bx + 8, by + 5))

        if near_puzzle2:
            label = prompt_font.render("Puzzle 2  [Press E to open]", True, WHITE)
            bg = pygame.Surface((label.get_width() + 16, label.get_height() + 10), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 160))
            bx = max(0, player.rect.centerx - bg.get_width() // 2)
            by = player.rect.top - bg.get_height() - 8
            if by < 0:
                by = player.rect.bottom + 8
            screen.blit(bg, (bx, by))
            screen.blit(label, (bx + 8, by + 5))

        if wellDone_timer > 0:
            msg = "Well done! You have completed Puzzle 1, more puzzles awaits you" if not puzzle2_done else "Well done! You have completed Puzzle 2, more puzzles awaits you"
            msg_surf = prompt_font.render(msg, True, WHITE)
            msg_bg = pygame.Surface((msg_surf.get_width() + 20, msg_surf.get_height() + 14), pygame.SRCALPHA)
            msg_bg.fill((0, 0, 0, 180))
            mx = SCREEN_WIDTH // 2 - msg_bg.get_width() // 2
            my = SCREEN_HEIGHT // 2 - msg_bg.get_height() // 2
            screen.blit(msg_bg, (mx, my))
            screen.blit(msg_surf, (mx + 10, my + 7))

        if debug:
            for r in COLLISION_RECTS:
                surf = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
                surf.fill((220, 50, 50, 100))
                screen.blit(surf, r.topleft)
                pygame.draw.rect(screen, RED, r, 2)

        pos_text = font.render(
            f"Position: ({player.rect.centerx}, {player.rect.centery})   "
            f"[WASD / Arrow Keys | D = debug | ESC to quit]",
            True, BLACK
        )
        screen.blit(pos_text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()