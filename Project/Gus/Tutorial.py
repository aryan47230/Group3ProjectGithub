"""
2D Top-Down Angled (3/4 Perspective) Movement — RPG Sprite Sheet Edition
-------------------------------------------------------------------------
Sprite sheet layout  (RPG_assets.png  →  128×128px, 8×8 grid of 16×16 tiles):

  Col:   0    1       2       3       4       5       6      7
  Row 0: ---  (empty head row) ---
  Row 1: ---  [dn-A] [dn-B]  [dn-A] [dn-B]  [dn-A] [dn-B]  ---   ← facing DOWN
  Row 2: ---  [lt-A] [lt-B]  [lt-A] [lt-B]  [lt-A] [lt-B]  ---   ← facing LEFT
  Row 3: ---  [rt-A] [rt-B]  [rt-A] [rt-B]  [rt-A] [rt-B]  ---   ← facing RIGHT
  Row 4: ---  [dn-A] [dn-B]  [dn-A] [dn-B]  ...ghost...    ---   ← facing DOWN (blue outfit)
  Row 5: ---  [lt-A] [lt-B]  ...                            ---   ← facing LEFT  (blue outfit)
  Row 6: ---  [rt-A] [rt-B]  ...                            ---   ← facing RIGHT (blue outfit)

  Each character pair of columns = one character variant (3 hair colours per outfit).
  UP has no dedicated row — we mirror the LEFT frames horizontally.

Character select (CHAR_SET):
  0 = brown hair / green outfit   (cols 1-2, rows 1-3)
  1 = red hair   / green outfit   (cols 3-4, rows 1-3)
  2 = purple hair / green outfit  (cols 5-6, rows 1-3)
  3 = purple hair / blue outfit   (cols 1-2, rows 4-6)

Controls:
  WASD / Arrow Keys — 8-directional movement
  1 / 2 / 3 / 4    — switch character variant
  ESC               — quit
"""

import pygame
import sys
import math

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SCREEN_W, SCREEN_H = 900, 650
FPS         = 60
TITLE       = "Top-Down Angled — Sprite Movement"

SPEED_X     = 4       # horizontal world speed
SPEED_Y     = 2.5     # vertical   world speed  (foreshortening ≈ ½)

TILE_W      = 80      # map tile width  (screen pixels)
TILE_H      = 40      # map tile height (half = angled view)
MAP_COLS    = 22
MAP_ROWS    = 28

SPRITE_SRC  = 16      # source tile size in sheet (px)
SPRITE_SCALE = 3      # render at 3× → 48×48 px
SPRITE_SIZE  = SPRITE_SRC * SPRITE_SCALE   # 48

ANIM_SPEED  = 10      # game-frames between walk-frame swaps

# Sprite-sheet character definitions
# Each entry: (col_offset, row_offset) — top-left tile of the 2-col × 3-row block
CHAR_SETS = {
    0: (1, 1),   # brown hair, green outfit
    1: (3, 1),   # red hair,   green outfit
    2: (5, 1),   # purple hair, green outfit
    3: (1, 4),   # purple hair, blue outfit
}
CHAR_SET = 0   # default

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
COL_BG        = ( 30,  28,  26)
COL_TILE_A    = ( 72,  90,  56)
COL_TILE_B    = ( 88, 108,  68)
COL_TILE_PATH = (140, 120,  90)
COL_GRID      = ( 55,  70,  44)
COL_SHADOW    = (  0,   0,   0, 100)
COL_HUD_BG    = ( 20,  20,  20, 180)
COL_HUD_TEXT  = (220, 210, 180)
COL_HUD_KEY   = (255, 200,  80)


# ---------------------------------------------------------------------------
# Map generation
# ---------------------------------------------------------------------------
def build_map(cols: int, rows: int) -> list:
    tile_map = []
    for r in range(rows):
        row = []
        for c in range(cols):
            if abs((c - cols // 2) + math.sin(r * 0.4) * 3) < 1.6:
                row.append(2)   # dirt path
            elif (r + c) % 2 == 0:
                row.append(0)   # grass A
            else:
                row.append(1)   # grass B
        tile_map.append(row)
    return tile_map


TILE_COLORS = {0: COL_TILE_A, 1: COL_TILE_B, 2: COL_TILE_PATH}


# ---------------------------------------------------------------------------
# Sprite-sheet loader
# ---------------------------------------------------------------------------
def load_character_frames(sheet: pygame.Surface, char_set: int) -> dict:
    """
    Slice 2-walk-frames for each of the 4 directions from the sprite sheet.
    Returns: { 'down': [surf, surf], 'left': [...], 'right': [...], 'up': [...] }
    The UP direction is synthesised by mirroring the LEFT frames.
    """
    col0, row0 = CHAR_SETS[char_set]
    # direction_row_offset: down=0, left=1, right=2  (relative to row0)
    dir_row = {"down": 0, "left": 1, "right": 2}

    frames: dict = {}
    for direction, dr in dir_row.items():
        row = row0 + dr
        dir_frames = []
        for frame_idx in range(2):
            col = col0 + frame_idx
            src_rect = pygame.Rect(col * SPRITE_SRC, row * SPRITE_SRC,
                                   SPRITE_SRC, SPRITE_SRC)
            raw  = sheet.subsurface(src_rect).copy()
            big  = pygame.transform.scale(raw, (SPRITE_SIZE, SPRITE_SIZE))
            dir_frames.append(big)
        frames[direction] = dir_frames

    # UP = horizontally flipped LEFT frames (no dedicated up sprites in this sheet)
    frames["up"] = [pygame.transform.flip(f, True, False)
                    for f in frames["left"]]
    return frames


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------
def world_to_screen(wx: float, wy: float,
                    cam_x: float, cam_y: float) -> tuple:
    return wx - cam_x, wy - cam_y


def draw_tile(surface: pygame.Surface, col: int, row: int,
              color, cam_x: float, cam_y: float) -> None:
    wx = col * TILE_W
    wy = row * TILE_H
    sx, sy = world_to_screen(wx, wy, cam_x, cam_y)
    rect = pygame.Rect(int(sx), int(sy), TILE_W, TILE_H)
    pygame.draw.rect(surface, color, rect)
    pygame.draw.rect(surface, COL_GRID, rect, 1)


# ---------------------------------------------------------------------------
# Player
# ---------------------------------------------------------------------------
class Player:
    def __init__(self, wx: float, wy: float, frames: dict):
        self.wx          = wx
        self.wy          = wy
        self.frames      = frames
        self.direction   = "down"
        self.frame_idx   = 0
        self.anim_timer  = 0
        self.moving      = False

    def load_new_frames(self, frames: dict) -> None:
        self.frames = frames

    def handle_input(self, map_w: float, map_h: float) -> None:
        keys = pygame.key.get_pressed()
        dx = dy = 0.0

        if keys[pygame.K_LEFT]  or keys[pygame.K_a]:
            dx -= SPEED_X
            self.direction = "left"
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += SPEED_X
            self.direction = "right"
        if keys[pygame.K_UP]    or keys[pygame.K_w]:
            dy -= SPEED_Y
            self.direction = "up"
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]:
            dy += SPEED_Y
            self.direction = "down"

        # Diagonal normalisation
        if dx != 0 and dy != 0:
            length = math.hypot(dx, dy)
            dx = dx / length * SPEED_X
            dy = dy / length * SPEED_Y

        self.moving = (dx != 0 or dy != 0)
        self.wx = max(0.0, min(self.wx + dx, map_w - 1))
        self.wy = max(0.0, min(self.wy + dy, map_h - 1))

    def update(self, map_w: float, map_h: float) -> None:
        self.handle_input(map_w, map_h)

        if self.moving:
            self.anim_timer += 1
            if self.anim_timer >= ANIM_SPEED:
                self.anim_timer = 0
                self.frame_idx  = (self.frame_idx + 1) % 2
        else:
            self.frame_idx  = 0   # idle pose
            self.anim_timer = 0

    def draw(self, surface: pygame.Surface,
             cam_x: float, cam_y: float) -> None:
        sx, sy = world_to_screen(self.wx, self.wy, cam_x, cam_y)

        # Drop shadow
        shadow = pygame.Surface((40, 14), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, COL_SHADOW, shadow.get_rect())
        surface.blit(shadow, (int(sx) - 20 + 4, int(sy) + SPRITE_SIZE // 2 - 4))

        # Sprite (centred on world position)
        sprite = self.frames[self.direction][self.frame_idx]
        rect   = sprite.get_rect(center=(int(sx), int(sy)))
        surface.blit(sprite, rect)


# ---------------------------------------------------------------------------
# HUD
# ---------------------------------------------------------------------------
def draw_hud(surface: pygame.Surface, font: pygame.font.Font,
             player: Player, char_set: int, fps: float) -> None:
    lines = [
        ("WASD / ↑↓←→  move", COL_HUD_TEXT),
        ("1 2 3 4  switch character", COL_HUD_TEXT),
        ("ESC  quit", COL_HUD_TEXT),
        ("", None),
        (f"Character  : {char_set + 1}", COL_HUD_KEY),
        (f"Direction  : {player.direction}", COL_HUD_KEY),
        (f"World pos  : ({player.wx:.0f}, {player.wy:.0f})", COL_HUD_KEY),
        (f"FPS        : {fps:.0f}", COL_HUD_KEY),
    ]
    pad   = 8
    lh    = 18
    w     = 230
    h     = pad * 2 + lh * len(lines)

    hud = pygame.Surface((w, h), pygame.SRCALPHA)
    hud.fill(COL_HUD_BG)
    surface.blit(hud, (8, 8))

    for i, (text, color) in enumerate(lines):
        if not text:
            continue
        txt_surf = font.render(text, True, color)
        surface.blit(txt_surf, (8 + pad, 8 + pad + i * lh))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption(TITLE)
    clock  = pygame.time.Clock()
    font   = pygame.font.SysFont("monospace", 14)

    # ---- Load sprite sheet ----
    sheet_raw = pygame.image.load("RPG_assets.png").convert()
    bg_color  = sheet_raw.get_at((0, 0))   # top-left pixel = cyan background
    sheet_raw.set_colorkey(bg_color)

    # ---- Build map ----
    tile_map    = build_map(MAP_COLS, MAP_ROWS)
    map_pixel_w = MAP_COLS * TILE_W
    map_pixel_h = MAP_ROWS * TILE_H

    # ---- Player ----
    char_set = CHAR_SET
    frames   = load_character_frames(sheet_raw, char_set)
    player   = Player(map_pixel_w / 2, map_pixel_h / 2, frames)

    # ---- Main loop ----
    while True:
        dt = clock.tick(FPS)

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                # Character switching
                for key, idx in [(pygame.K_1, 0), (pygame.K_2, 1),
                                  (pygame.K_3, 2), (pygame.K_4, 3)]:
                    if event.key == key and idx in CHAR_SETS:
                        char_set = idx
                        player.load_new_frames(
                            load_character_frames(sheet_raw, char_set))

        # Update
        player.update(map_pixel_w, map_pixel_h)

        # Camera: centre on player, clamp to map
        cam_x = max(0, min(player.wx - SCREEN_W / 2, map_pixel_w - SCREEN_W))
        cam_y = max(0, min(player.wy - SCREEN_H / 2, map_pixel_h - SCREEN_H))

        # Draw — tiles
        screen.fill(COL_BG)
        col_start = max(0, int(cam_x // TILE_W))
        col_end   = min(MAP_COLS, col_start + SCREEN_W // TILE_W + 2)
        row_start = max(0, int(cam_y // TILE_H))
        row_end   = min(MAP_ROWS, row_start + SCREEN_H // TILE_H + 2)

        for r in range(row_start, row_end):
            for c in range(col_start, col_end):
                draw_tile(screen, c, r,
                          TILE_COLORS[tile_map[r][c]], cam_x, cam_y)

        # Draw — player
        player.draw(screen, cam_x, cam_y)

        # Draw — HUD
        draw_hud(screen, font, player, char_set, clock.get_fps())

        pygame.display.flip()


if __name__ == "__main__":
    main()