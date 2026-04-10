import pygame
import sys

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
    pygame.Rect(  0,   0, 800,  75),
    # central back staircase
    pygame.Rect(275,  75, 250, 195),
    # back-left table & chairs cluster
    pygame.Rect(  0, 210, 250, 130),
    # back-right counter
    pygame.Rect(490, 195, 310, 135),
    # front center sofa group
    pygame.Rect(  0, 457, 800, 83),
    # bottom wall
    pygame.Rect(  0, 555, 800,  45),
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

    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    all_sprites = pygame.sprite.Group(player)
    debug = False

    while True:
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

        all_sprites.update()

        screen.blit(background, (0, 0))
        all_sprites.draw(screen)

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