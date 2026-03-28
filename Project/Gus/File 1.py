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


class Player(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int):
        super().__init__()
        self.image = pygame.Surface((40, 50), pygame.SRCALPHA)
        pygame.draw.rect(self.image, BLUE, (0, 0, 40, 50), border_radius=6)
        self.rect = self.image.get_rect(center=(x, y))

    def handle_input(self) -> None:
        keys = pygame.key.get_pressed()

        dx = dy = 0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: dx -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += PLAYER_SPEED
        if keys[pygame.K_UP]    or keys[pygame.K_w]: dy -= PLAYER_SPEED
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: dy += PLAYER_SPEED

        self.rect.x += dx
        self.rect.y += dy

        self.rect.clamp_ip(pygame.display.get_surface().get_rect())

    def update(self) -> None:
        self.handle_input()


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

    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    all_sprites = pygame.sprite.Group(player)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        all_sprites.update()

        screen.fill(WHITE)
        draw_grid(screen)
        all_sprites.draw(screen)

        pos_text = font.render(
            f"Position: ({player.rect.centerx}, {player.rect.centery})   "
            f"[WASD / Arrow Keys to move | ESC to quit]",
            True, BLACK
        )
        screen.blit(pos_text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()