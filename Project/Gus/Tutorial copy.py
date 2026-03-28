import pygame
import sys
import math

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SCREEN_W, SCREEN_H = 900, 650
FPS = 60
TITLE = "Top-Down Angled Movement"

# In a 3/4 view, vertical movement appears "compressed"
SPEED_X = 4          # horizontal world speed
SPEED_Y = 2.5        # vertical world speed  (≈ half = foreshortening effect)

TILE_W  = 80         # tile width  in screen pixels
TILE_H  = 40         # tile height (half of width → foreshortened)
MAP_COLS = 22
MAP_ROWS = 28

# Colors (earthy RPG palette)
COL_BG        = ( 30,  28,  26)
COL_TILE_A    = ( 72,  90,  56)   # grass dark
COL_TILE_B    = ( 88, 108,  68)   # grass light
COL_TILE_PATH = (140, 120,  90)   # dirt path
COL_GRID      = ( 55,  70,  44)
COL_PLAYER    = (220, 180,  80)   # warm gold
COL_SHADOW    = (  0,   0,   0, 100)
COL_ACCENT    = (255, 100,  60)   # direction dot
COL_HUD_BG    = ( 20,  20,  20, 180)
COL_HUD_TEXT  = (220, 210, 180)

# ---------------------------------------------------------------------------
# Simple tile map  (0 = grass A, 1 = grass B, 2 = dirt path)
# ---------------------------------------------------------------------------
def build_map(cols: int, rows: int):
    tile_map = []
    for r in range(rows):
        row = []
        for c in range(cols):
            # Create a winding dirt path
            if abs((c - cols // 2) + math.sin(r * 0.4) * 3) < 1.6:
                row.append(2)
            elif (r + c) % 2 == 0:
                row.append(0)
            else:
                row.append(1)
        tile_map.append(row)
    return tile_map


TILE_COLORS = {
    0: COL_TILE_A,
    1: COL_TILE_B,
    2: COL_TILE_PATH,
}


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------
def world_to_screen(wx: float, wy: float, cam_x: float, cam_y: float):
    """Convert world pixel coords → screen pixel coords."""
    return wx - cam_x, wy - cam_y


def draw_tile(surface: pygame.Surface, col: int, row: int,
              color, cam_x: float, cam_y: float) -> None:
    """Draw a single foreshortened rectangular tile."""
    wx = col * TILE_W
    wy = row * TILE_H
    sx, sy = world_to_screen(wx, wy, cam_x, cam_y)
    rect = pygame.Rect(sx, sy, TILE_W, TILE_H)
    pygame.draw.rect(surface, color, rect)
    pygame.draw.rect(surface, COL_GRID, rect, 1)


def draw_player_shape(surface: pygame.Surface,
                      sx: float, sy: float, angle_deg: float) -> None:
    """Draw player body + directional indicator + drop shadow."""
    # Shadow (slightly below and to the right for angled lighting)
    shadow_surf = pygame.Surface((34, 18), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow_surf, COL_SHADOW, shadow_surf.get_rect())
    surface.blit(shadow_surf, (sx - 17 + 3, sy + 14))

    # Body circle
    pygame.draw.circle(surface, COL_PLAYER, (int(sx), int(sy)), 14)
    pygame.draw.circle(surface, (180, 140, 50), (int(sx), int(sy)), 14, 2)

    # Direction dot
    rad = math.radians(angle_deg)
    dot_x = sx + math.cos(rad) * 10
    dot_y = sy + math.sin(rad) * 10
    pygame.draw.circle(surface, COL_ACCENT, (int(dot_x), int(dot_y)), 4)


# ---------------------------------------------------------------------------
# Player
# ---------------------------------------------------------------------------
class Player:
    def __init__(self, wx: float, wy: float):
        self.wx   = wx    # world X (pixels)
        self.wy   = wy    # world Y (pixels)
        self.angle = 0.0  # degrees, 0 = right

    def handle_input(self, map_w: int, map_h: int) -> None:
        keys = pygame.key.get_pressed()

        dx = dy = 0.0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: dx -= SPEED_X
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += SPEED_X
        if keys[pygame.K_UP]    or keys[pygame.K_w]: dy -= SPEED_Y
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: dy += SPEED_Y
        if keys[pygame.K_SPACE]:
            self.wy -= 2
            pygame.time.delay(1000)
            self.wy += 2

        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            length = math.hypot(dx, dy)
            dx = dx / length * SPEED_X
            dy = dy / length * SPEED_Y

        # Update facing angle
        if dx != 0 or dy != 0:
            self.angle = math.degrees(math.atan2(dy, dx))

        self.wx = max(0, min(self.wx + dx, map_w - 1))
        self.wy = max(0, min(self.wy + dy, map_h - 1))

    def update(self, map_w: int, map_h: int) -> None:
        self.handle_input(map_w, map_h)

    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float) -> None:
        sx, sy = world_to_screen(self.wx, self.wy, cam_x, cam_y)
        draw_player_shape(surface, sx, sy, self.angle)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption(TITLE)
    clock  = pygame.time.Clock()
    font   = pygame.font.SysFont("monospace", 15)

    tile_map = build_map(MAP_COLS, MAP_ROWS)
    map_pixel_w = MAP_COLS * TILE_W
    map_pixel_h = MAP_ROWS * TILE_H

    # Start player in the middle of the map
    player = Player(map_pixel_w / 2, map_pixel_h / 2)

    while True:
        # ---- Events ----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()

        # ---- Update ----
        player.update(map_pixel_w, map_pixel_h)

        # Camera: center on player, clamp to map bounds
        cam_x = player.wx - SCREEN_W / 2
        cam_y = player.wy - SCREEN_H / 2
        cam_x = max(0, min(cam_x, map_pixel_w - SCREEN_W))
        cam_y = max(0, min(cam_y, map_pixel_h - SCREEN_H))

        # ---- Draw ----
        screen.fill(COL_BG)

        # Tiles (only draw those visible on screen)
        col_start = max(0, int(cam_x // TILE_W))
        col_end   = min(MAP_COLS, col_start + SCREEN_W // TILE_W + 2)
        row_start = max(0, int(cam_y // TILE_H))
        row_end   = min(MAP_ROWS, row_start + SCREEN_H // TILE_H + 2)

        for r in range(row_start, row_end):
            for c in range(col_start, col_end):
                draw_tile(screen, c, r, TILE_COLORS[tile_map[r][c]], cam_x, cam_y)

        # Player
        player.draw(screen, cam_x, cam_y)

        # HUD
        hud_lines = [
            f"World  X: {player.wx:6.1f}  Y: {player.wy:6.1f}",
            f"Facing : {player.angle:+.1f}°",
            f"[WASD / Arrows] move   [ESC] quit",
        ]
        hud_surf = pygame.Surface((290, 62), pygame.SRCALPHA)
        hud_surf.fill(COL_HUD_BG)
        screen.blit(hud_surf, (8, 8))
        for i, line in enumerate(hud_lines):
            txt = font.render(line, True, COL_HUD_TEXT)
            screen.blit(txt, (14, 12 + i * 18))

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()