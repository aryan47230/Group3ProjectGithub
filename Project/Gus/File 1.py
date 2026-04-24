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
    pygame.Rect(  0,   0, 800, 150),
    # left wall segment
    pygame.Rect(  0, 200,  50, 200),
    # custom collision box (50,225) -> (150,250)
    pygame.Rect( 50, 225, 100,  25),
    # custom collision box (600,225) -> (800,250)
    pygame.Rect(600, 225, 200,  25),
    # custom collision box (700,250) -> (800,325)
    pygame.Rect(700, 250, 100,  75),
    # left staircase passage (blocked until puzzle 2 complete)
    pygame.Rect(190, 150, 100, 150),
    # full-width row y=450 to y=500
    pygame.Rect(  0, 450, 800,  50),
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

    # Always start fresh — remove completion flags from any previous run
    for _flag in [
        "/Users/gus/Library/CloudStorage/OneDrive-UniversityofIllinois-Urbana/CS honor/Group3ProjectGithub/Project/puzzle1_complete.txt",
        "/Users/gus/Library/CloudStorage/OneDrive-UniversityofIllinois-Urbana/CS honor/Group3ProjectGithub/Project/puzzle2_complete.txt",
    ]:
        if os.path.exists(_flag):
            os.remove(_flag)

    _parent = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    sys.path.insert(0, _parent)
    from menu import Menu
    from main import LibrarianDialogue

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Grainger Mystery")
    clock = pygame.time.Clock()
    font  = pygame.font.SysFont("monospace", 16)

    # --- MENU ---
    menu = Menu(SCREEN_WIDTH, SCREEN_HEIGHT)
    in_menu = True
    while in_menu:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            action = menu.handle_event(event)
            if action == "start":
                in_menu = False
            elif action == "quit":
                pygame.quit(); sys.exit()
        if in_menu:
            menu.update(dt)
            menu.draw(screen)
            pygame.display.flip()

    # --- LIBRARIAN DIALOGUE ---
    librarian = LibrarianDialogue(SCREEN_WIDTH, SCREEN_HEIGHT)
    in_dialogue = True
    while in_dialogue:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            result = librarian.handle_event(event)
            if result == "menu":
                # restart menu
                menu = Menu(SCREEN_WIDTH, SCREEN_HEIGHT)
                in_menu = True
                while in_menu:
                    dt = clock.tick(60)
                    for ev in pygame.event.get():
                        if ev.type == pygame.QUIT:
                            pygame.quit(); sys.exit()
                        action = menu.handle_event(ev)
                        if action == "start":
                            in_menu = False
                        elif action == "quit":
                            pygame.quit(); sys.exit()
                    if in_menu:
                        menu.update(dt)
                        menu.draw(screen)
                        pygame.display.flip()
                librarian = LibrarianDialogue(SCREEN_WIDTH, SCREEN_HEIGHT)
            elif result == "done":
                in_dialogue = False
        if in_dialogue:
            librarian.update(dt)
            librarian.draw(screen)
            pygame.display.flip()

    background = pygame.image.load(
        "/Users/gus/Library/CloudStorage/OneDrive-UniversityofIllinois-Urbana/CS honor/Group3ProjectGithub/Project/Gus/library.png"
    ).convert()
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

    background_3rd = pygame.image.load(
        "/Users/gus/Library/CloudStorage/OneDrive-UniversityofIllinois-Urbana/CS honor/Group3ProjectGithub/Project/Gus/dark_3rd_floor.png"
    ).convert()
    background_3rd = pygame.transform.scale(background_3rd, (SCREEN_WIDTH, SCREEN_HEIGHT))

    background_2nd = pygame.image.load(
        "/Users/gus/Library/CloudStorage/OneDrive-UniversityofIllinois-Urbana/CS honor/Group3ProjectGithub/Project/Gus/2nd_floor_background_image.webp"
    ).convert()
    background_2nd = pygame.transform.scale(background_2nd, (SCREEN_WIDTH, SCREEN_HEIGHT))

    on_3rd_floor = False
    on_2nd_floor = False

    coffee_img = pygame.image.load(
        "/Users/gus/Library/CloudStorage/OneDrive-UniversityofIllinois-Urbana/CS honor/Group3ProjectGithub/Project/Gus/coffee.png"
    ).convert_alpha()
    coffee_img = pygame.transform.scale(coffee_img, (28, 28))
    coffee_rect = coffee_img.get_rect(topleft=(350, 410))

    camera_img = pygame.image.load(
        "/Users/gus/Library/CloudStorage/OneDrive-UniversityofIllinois-Urbana/CS honor/Group3ProjectGithub/Project/Gus/camera.png"
    ).convert_alpha()
    camera_img = pygame.transform.scale(camera_img, (20, 20))
    camera_rect = camera_img.get_rect(topleft=(24, 561))

    phone_img = pygame.image.load(
        "/Users/gus/Library/CloudStorage/OneDrive-UniversityofIllinois-Urbana/CS honor/Group3ProjectGithub/Project/Gus/phone.webp"
    ).convert_alpha()
    phone_img = pygame.transform.scale(phone_img, (20, 20))
    phone_rect = phone_img.get_rect(topleft=(560, 235))

    receipt_img = pygame.image.load(
        "/Users/gus/Library/CloudStorage/OneDrive-UniversityofIllinois-Urbana/CS honor/Group3ProjectGithub/Project/Gus/reciept.png"
    ).convert_alpha()
    receipt_img = pygame.transform.scale(receipt_img, (20, 20))
    receipt_rect = receipt_img.get_rect(topleft=(610, 295))

    clock_img = pygame.image.load(
        "/Users/gus/Library/CloudStorage/OneDrive-UniversityofIllinois-Urbana/CS honor/Group3ProjectGithub/Project/Gus/clock (1).webp"
    ).convert_alpha()
    clock_img = pygame.transform.scale(clock_img, (10, 10))
    clock_rect = clock_img.get_rect(topleft=(180, 245))

    # Collectible objects: name, image, rect
    collectibles = [
        {"name": "Coffee Cup", "img": coffee_img,  "rect": coffee_rect},
        {"name": "Camera",     "img": camera_img,  "rect": camera_rect},
        {"name": "Phone",      "img": phone_img,   "rect": phone_rect},
        {"name": "Receipt",    "img": receipt_img, "rect": receipt_rect},
        {"name": "Clock",      "img": clock_img,   "rect": clock_rect},
    ]
    collected = [False] * len(collectibles)
    COLLECT_RADIUS = 40   # pixels; how close the player must be to collect
    timeline_launched   = False
    timeline_proc       = None
    timeline_completed  = False
    all_collected_timer = 0   # frames to show "all collected" message

    TIMELINE_PATH = "/Users/gus/Library/CloudStorage/OneDrive-UniversityofIllinois-Urbana/CS honor/Group3ProjectGithub/Project/spras30/secondroom_timeline"

    RECONSTRUCTION_PATH = "/Users/gus/Library/CloudStorage/OneDrive-UniversityofIllinois-Urbana/CS honor/Group3ProjectGithub/Project/spras30/first_room_reconstruction"
    book_launched = False
    book_proc     = None

    BELL_TRIGGER      = pygame.Rect(380, 180, 40, 40)   # centred on (400, 200)
    MURDER_BOARD_PATH = "/Users/gus/Library/CloudStorage/OneDrive-UniversityofIllinois-Urbana/CS honor/Group3ProjectGithub/Project/rbenos2/murder_board.py"
    bell_launched = False
    bell_message_timer = 0

    puzzle_procs = []   # track all active puzzle subprocesses

    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    all_sprites = pygame.sprite.Group(player)
    debug = False

    PUZZLE1_TRIGGER = pygame.Rect(635, 330, 40, 40)   # centred on (655, 350)
    SLIDING_PUZZLE_PATH = "/Users/gus/Library/CloudStorage/OneDrive-UniversityofIllinois-Urbana/CS honor/Group3ProjectGithub/Project/sliding_puzzle.py"
    PUZZLE1_FLAG = "/Users/gus/Library/CloudStorage/OneDrive-UniversityofIllinois-Urbana/CS honor/Group3ProjectGithub/Project/puzzle1_complete.txt"

    PUZZLE2_TRIGGER = pygame.Rect(165, 330, 40, 40)   # centred on (185, 350)
    CYPHER_PATH = "/Users/gus/Library/CloudStorage/OneDrive-UniversityofIllinois-Urbana/CS honor/Group3ProjectGithub/Project/cypher.py"
    PUZZLE2_FLAG = "/Users/gus/Library/CloudStorage/OneDrive-UniversityofIllinois-Urbana/CS honor/Group3ProjectGithub/Project/puzzle2_complete.txt"

    LEFT_STAIRCASE_RECT = pygame.Rect(190, 150, 100, 150)
    FLOOR_UP_TRIGGER    = pygame.Rect(375, 210, 40, 40)   # centred on (395, 230)

    puzzle1_done     = os.path.exists(PUZZLE1_FLAG)
    puzzle2_done     = os.path.exists(PUZZLE2_FLAG)
    puzzle2_launched = puzzle2_done
    if puzzle2_done and LEFT_STAIRCASE_RECT in COLLISION_RECTS:
        COLLISION_RECTS.remove(LEFT_STAIRCASE_RECT)

    wellDone_timer = 0   # frames remaining to show completion message
    next_floor_timer = 0  # frames remaining to show "move onto next floor" message

    prompt_font = pygame.font.SysFont("monospace", 13, bold=True)

    while True:
        # Check puzzle completions from subprocesses
        if not puzzle1_done and os.path.exists(PUZZLE1_FLAG):
            puzzle1_done = True
            wellDone_timer = FPS * 6

        if not puzzle2_done and os.path.exists(PUZZLE2_FLAG):
            puzzle2_done = True
            wellDone_timer = FPS * 6
            next_floor_timer = FPS * 6
            if LEFT_STAIRCASE_RECT in COLLISION_RECTS:
                COLLISION_RECTS.remove(LEFT_STAIRCASE_RECT)

        on_library   = not on_3rd_floor and not on_2nd_floor
        near_puzzle1 = on_library and (not puzzle1_done) and PUZZLE1_TRIGGER.colliderect(player.rect)
        near_puzzle2 = on_library and puzzle1_done and (not puzzle2_launched) and PUZZLE2_TRIGGER.colliderect(player.rect)
        near_book    = timeline_completed and (not book_launched) and pygame.Rect(446, 381, 40, 40).colliderect(player.rect)
        near_floor_up = on_library and puzzle2_done and FLOOR_UP_TRIGGER.colliderect(player.rect)
        near_bell    = on_2nd_floor and (not bell_launched) and BELL_TRIGGER.colliderect(player.rect)

        # Remove any puzzle subprocesses that just ended
        just_ended = [p for p in puzzle_procs if p.poll() is not None]
        puzzle_procs[:] = [p for p in puzzle_procs if p.poll() is None]

        # Detect when timeline puzzle is closed
        if timeline_proc is not None and timeline_proc.poll() is not None:
            timeline_completed = True
            timeline_proc = None

        # Switch to 2nd floor background when book puzzle is closed
        if book_proc is not None and book_proc.poll() is not None:
            on_2nd_floor = True
            book_proc = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # On macOS, closing a puzzle subprocess window fires a QUIT
                # event in the parent.  Ignore it if a puzzle just closed.
                if just_ended:
                    just_ended.clear()
                    continue
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_d:
                    debug = not debug
                if event.key == pygame.K_e and near_floor_up:
                    on_3rd_floor = True
                    bottom_wall = pygame.Rect(0, 450, 800, 50)
                    if bottom_wall in COLLISION_RECTS:
                        COLLISION_RECTS.remove(bottom_wall)
                if event.key == pygame.K_e and near_puzzle1:
                    puzzle_procs.append(subprocess.Popen(
                        [sys.executable, SLIDING_PUZZLE_PATH],
                        cwd="/Users/gus/Library/CloudStorage/OneDrive-UniversityofIllinois-Urbana/CS honor/Group3ProjectGithub/Project"
                    ))
                if event.key == pygame.K_e and near_puzzle2:
                    puzzle2_launched = True
                    puzzle_procs.append(subprocess.Popen(
                        [sys.executable, CYPHER_PATH],
                        cwd="/Users/gus/Library/CloudStorage/OneDrive-UniversityofIllinois-Urbana/CS honor/Group3ProjectGithub/Project"
                    ))
                if event.key == pygame.K_e and near_bell:
                    bell_launched = True
                    bell_message_timer = FPS * 3
                    puzzle_procs.append(subprocess.Popen(
                        [sys.executable, MURDER_BOARD_PATH],
                        cwd="/Users/gus/Library/CloudStorage/OneDrive-UniversityofIllinois-Urbana/CS honor/Group3ProjectGithub/Project/rbenos2"
                    ))
                if event.key == pygame.K_e and near_book:
                    book_launched = True
                    book_proc = subprocess.Popen(
                        [sys.executable, RECONSTRUCTION_PATH],
                        cwd="/Users/gus/Library/CloudStorage/OneDrive-UniversityofIllinois-Urbana/CS honor/Group3ProjectGithub/Project/spras30"
                    )
                    puzzle_procs.append(book_proc)
                if event.key == pygame.K_e:
                    for idx, obj in enumerate(collectibles):
                        if not collected[idx]:
                            if obj["rect"].inflate(COLLECT_RADIUS * 2, COLLECT_RADIUS * 2).colliderect(player.rect):
                                collected[idx] = True
                                if all(collected) and not timeline_launched:
                                    timeline_launched = True
                                    all_collected_timer = FPS * 3
                                    timeline_proc = subprocess.Popen(
                                        [sys.executable, TIMELINE_PATH],
                                        cwd="/Users/gus/Library/CloudStorage/OneDrive-UniversityofIllinois-Urbana/CS honor/Group3ProjectGithub/Project/spras30"
                                    )
                                    puzzle_procs.append(timeline_proc)
                                break

        if wellDone_timer > 0:
            wellDone_timer -= 1
        if next_floor_timer > 0:
            next_floor_timer -= 1
        if all_collected_timer > 0:
            all_collected_timer -= 1
        if bell_message_timer > 0:
            bell_message_timer -= 1

        all_sprites.update()

        if on_2nd_floor:
            screen.blit(background_2nd, (0, 0))
        elif on_3rd_floor:
            screen.blit(background_3rd, (0, 0))
        else:
            screen.blit(background, (0, 0))


        # Draw collectibles and show "Press E" prompt when near (hidden on library floor)
        for idx, obj in enumerate(collectibles) if on_3rd_floor else []:
            if collected[idx]:
                continue
            screen.blit(obj["img"], obj["rect"])
            if obj["rect"].inflate(COLLECT_RADIUS * 2, COLLECT_RADIUS * 2).colliderect(player.rect):
                hint_surf = prompt_font.render(f"{obj['name']}  [Press E to collect]", True, WHITE)
                hint_bg = pygame.Surface((hint_surf.get_width() + 16, hint_surf.get_height() + 10), pygame.SRCALPHA)
                hint_bg.fill((0, 0, 0, 160))
                hx = max(0, min(obj["rect"].centerx - hint_bg.get_width() // 2, SCREEN_WIDTH - hint_bg.get_width()))
                hy = obj["rect"].top - hint_bg.get_height() - 6
                if hy < 0:
                    hy = obj["rect"].bottom + 6
                screen.blit(hint_bg, (hx, hy))
                screen.blit(hint_surf, (hx + 8, hy + 5))

        all_sprites.draw(screen)

        if near_puzzle1:
            label = prompt_font.render("Press E to open puzzle", True, WHITE)
            bg = pygame.Surface((label.get_width() + 16, label.get_height() + 10), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 160))
            bx = max(0, player.rect.centerx - bg.get_width() // 2)
            by = player.rect.top - bg.get_height() - 8
            if by < 0:
                by = player.rect.bottom + 8
            screen.blit(bg, (bx, by))
            screen.blit(label, (bx + 8, by + 5))

        if near_puzzle2:
            label = prompt_font.render("Press E to open puzzle", True, WHITE)
            bg = pygame.Surface((label.get_width() + 16, label.get_height() + 10), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 160))
            bx = max(0, player.rect.centerx - bg.get_width() // 2)
            by = player.rect.top - bg.get_height() - 8
            if by < 0:
                by = player.rect.bottom + 8
            screen.blit(bg, (bx, by))
            screen.blit(label, (bx + 8, by + 5))

        if near_bell:
            label = prompt_font.render("Ring Bell  [Press E]", True, WHITE)
            bg = pygame.Surface((label.get_width() + 16, label.get_height() + 10), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 160))
            bx = max(0, player.rect.centerx - bg.get_width() // 2)
            by = player.rect.top - bg.get_height() - 8
            if by < 0:
                by = player.rect.bottom + 8
            screen.blit(bg, (bx, by))
            screen.blit(label, (bx + 8, by + 5))

        if near_floor_up:
            label = prompt_font.render("Move onto next floor  [Press E]", True, WHITE)
            bg = pygame.Surface((label.get_width() + 16, label.get_height() + 10), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 160))
            bx = max(0, player.rect.centerx - bg.get_width() // 2)
            by = player.rect.top - bg.get_height() - 8
            if by < 0:
                by = player.rect.bottom + 8
            screen.blit(bg, (bx, by))
            screen.blit(label, (bx + 8, by + 5))

        if near_book:
            label = prompt_font.render("Read Book  [Press E]", True, WHITE)
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

        if next_floor_timer > 0 and on_library:
            msg = "Move onto the next floor!"
            msg_surf = prompt_font.render(msg, True, (100, 255, 160))
            msg_bg = pygame.Surface((msg_surf.get_width() + 20, msg_surf.get_height() + 14), pygame.SRCALPHA)
            msg_bg.fill((0, 0, 0, 190))
            nx = SCREEN_WIDTH // 2 - msg_bg.get_width() // 2
            ny = 30
            screen.blit(msg_bg, (nx, ny))
            screen.blit(msg_surf, (nx + 10, ny + 7))

        if all_collected_timer > 0:
            msg = "All clues collected! The timeline puzzle has opened."
            msg_surf = prompt_font.render(msg, True, (255, 220, 80))
            msg_bg = pygame.Surface((msg_surf.get_width() + 20, msg_surf.get_height() + 14), pygame.SRCALPHA)
            msg_bg.fill((0, 0, 0, 190))
            nx = SCREEN_WIDTH // 2 - msg_bg.get_width() // 2
            ny = 60
            screen.blit(msg_bg, (nx, ny))
            screen.blit(msg_surf, (nx + 10, ny + 7))

        if bell_message_timer > 0:
            msg = "You rang the bell! The Murder Board has opened."
            msg_surf = prompt_font.render(msg, True, (255, 180, 80))
            msg_bg = pygame.Surface((msg_surf.get_width() + 20, msg_surf.get_height() + 14), pygame.SRCALPHA)
            msg_bg.fill((0, 0, 0, 190))
            nx = SCREEN_WIDTH // 2 - msg_bg.get_width() // 2
            ny = 90
            screen.blit(msg_bg, (nx, ny))
            screen.blit(msg_surf, (nx + 10, ny + 7))

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