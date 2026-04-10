"""
pause.py  —  Pause screen overlay for Grainger Mystery
-------------------------------------------------------
Usage inside any puzzle's game loop:

    from pause import PauseScreen
    pause_screen = PauseScreen(screen_w, screen_h)
    paused = False

    # inside event loop:
    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        paused = not paused

    # inside main loop (before pygame.display.flip()):
    if paused:
        action = pause_screen.handle_event(event)   # "resume", "quit", or None
        pause_screen.draw(screen)
        if action == "resume":
            paused = False
        elif action == "quit":
            running = False
"""

import pygame

# ---------------------------------------------------------------------------
# Colours
# ---------------------------------------------------------------------------
C_OVERLAY    = (0,   0,   0)
C_PANEL_BG   = (18,  18,  24)
C_BORDER     = (180, 140,  60)
C_TITLE      = (200, 160,  60)
C_SELECTED   = (255, 200,  60)
C_UNSELECTED = (180, 170, 150)
C_HIGHLIGHT  = (255, 200,  60)
C_DIM        = (140, 130, 110)

OPTION_RESUME = 0
OPTION_QUIT   = 1
OPTIONS = ["RESUME GAME", "BACK TO MENU"]

OVERLAY_ALPHA = 160
PANEL_W = 360
PANEL_H = 260


class PauseScreen:
    """Semi-transparent pause overlay. handle_event() returns 'resume', 'quit', or None."""

    def __init__(self, screen_w, screen_h):
        self.W = screen_w
        self.H = screen_h

        pygame.font.init()
        self.font_title  = pygame.font.SysFont("Georgia",     42, bold=True)
        self.font_option = pygame.font.SysFont("Courier New", 22, bold=True)
        self.font_hint   = pygame.font.SysFont("Courier New", 13)

        self.selected = OPTION_RESUME

        self._blink_timer   = 0
        self._blink_visible = True

        self._overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        self._overlay.fill((*C_OVERLAY, OVERLAY_ALPHA))

        self._option_rects = []  # filled each draw()

    # ------------------------------------------------------------------
    # Update (call every frame while paused, passing dt in ms)
    # ------------------------------------------------------------------

    def update(self, dt):
        self._blink_timer += dt
        if self._blink_timer >= 500:
            self._blink_timer   = 0
            self._blink_visible = not self._blink_visible

    # ------------------------------------------------------------------
    # Input — returns "resume", "quit", or None
    # ------------------------------------------------------------------

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            for i, rect in enumerate(self._option_rects):
                if rect and rect.collidepoint(event.pos):
                    if self.selected != i:
                        self.selected       = i
                        self._blink_visible = True
                        self._blink_timer   = 0
            return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(self._option_rects):
                if rect and rect.collidepoint(event.pos):
                    self.selected = i
                    return self._confirm()
            return None

        if event.type != pygame.KEYDOWN:
            return None

        if event.key in (pygame.K_w, pygame.K_UP):
            self.selected = (self.selected - 1) % len(OPTIONS)
            self._blink_visible = True
            self._blink_timer   = 0

        elif event.key in (pygame.K_s, pygame.K_DOWN):
            self.selected = (self.selected + 1) % len(OPTIONS)
            self._blink_visible = True
            self._blink_timer   = 0

        elif event.key == pygame.K_RETURN:
            return self._confirm()

        elif event.key == pygame.K_ESCAPE:
            return "resume"

        return None

    def _confirm(self):
        if self.selected == OPTION_RESUME:
            return "resume"
        elif self.selected == OPTION_QUIT:
            return "quit"

    # ------------------------------------------------------------------
    # Draw — call after your puzzle draws itself, before display.flip()
    # ------------------------------------------------------------------

    def draw(self, screen):
        # Dim the background
        screen.blit(self._overlay, (0, 0))

        cx = self.W // 2
        cy = self.H // 2

        # Panel
        panel_rect = pygame.Rect(cx - PANEL_W // 2, cy - PANEL_H // 2, PANEL_W, PANEL_H)
        pygame.draw.rect(screen, C_PANEL_BG, panel_rect, border_radius=8)
        pygame.draw.rect(screen, C_BORDER,   panel_rect, width=2, border_radius=8)

        # Title
        title_surf = self.font_title.render("PAUSED", True, C_TITLE)
        screen.blit(title_surf, (cx - title_surf.get_width() // 2,
                                  panel_rect.y + 24))

        # Divider
        div_y = panel_rect.y + 24 + title_surf.get_height() + 12
        pygame.draw.line(screen, C_BORDER,
                         (cx - 120, div_y), (cx + 120, div_y), 1)

        # Options
        option_start_y = div_y + 24
        option_gap     = 52
        mouse_pos      = pygame.mouse.get_pos()
        self._option_rects = []
        hovering_any   = False

        for i, label in enumerate(OPTIONS):
            is_sel = i == self.selected
            colour = C_SELECTED if is_sel else C_UNSELECTED
            text   = self.font_option.render(label, True, colour)
            text_x = cx - text.get_width() // 2
            text_y = option_start_y + i * option_gap

            bar_rect = pygame.Rect(cx - 140, text_y - 6, 280, text.get_height() + 12)
            self._option_rects.append(bar_rect)

            if bar_rect.collidepoint(mouse_pos):
                hovering_any = True

            if is_sel:
                pygame.draw.rect(screen, (32, 30, 20), bar_rect, border_radius=4)
                pygame.draw.rect(screen, C_BORDER, bar_rect, width=1, border_radius=4)

            screen.blit(text, (text_x, text_y))

            if is_sel and self._blink_visible:
                arrow = self.font_option.render(">", True, C_HIGHLIGHT)
                screen.blit(arrow, (text_x - arrow.get_width() - 12, text_y))

        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if hovering_any else pygame.SYSTEM_CURSOR_ARROW)

        # Hint
        hint_surf = self.font_hint.render(
            "ESC  or  W/S + ENTER  \u2022  Click to select", True, C_DIM
        )
        screen.blit(hint_surf, (cx - hint_surf.get_width() // 2,
                                 panel_rect.bottom - hint_surf.get_height() - 12))
