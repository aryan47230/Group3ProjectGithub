"""
ui/menu.py  —  Main Menu screen for Grainger Mystery
-----------------------------------------------------
Standalone pygame menu — no game_states or state_manager required.

Usage:
    menu = Menu(screen_w, screen_h)
    ...
    action = menu.handle_event(event)   # returns "start", "quit", or None
    menu.update(dt)
    menu.draw(screen)
"""

import pygame

# ---------------------------------------------------------------------------
# Colours
# ---------------------------------------------------------------------------
C_BG         = (18,  18,  24)
C_BORDER     = (180, 140,  60)
C_TITLE      = (200, 160,  60)
C_SUBTITLE   = (230, 220, 200)
C_DIM        = (140, 130, 110)
C_HIGHLIGHT  = (255, 200,  60)
C_SELECTED   = (255, 200,  60)
C_UNSELECTED = (180, 170, 150)

# ---------------------------------------------------------------------------
# Menu options
# ---------------------------------------------------------------------------
OPTION_START = 0
OPTION_QUIT  = 1
OPTIONS = ["START GAME", "QUIT"]


class Menu:
    """Full menu screen. handle_event() returns 'start', 'quit', or None."""

    def __init__(self, screen_w, screen_h):
        self.W = screen_w
        self.H = screen_h

        pygame.font.init()
        self.font_title    = pygame.font.SysFont("Georgia",     64, bold=True)
        self.font_subtitle = pygame.font.SysFont("Georgia",     26, bold=False)
        self.font_tagline  = pygame.font.SysFont("Courier New", 15)
        self.font_option   = pygame.font.SysFont("Courier New", 22, bold=True)
        self.font_hint     = pygame.font.SysFont("Courier New", 13)

        self.selected = OPTION_START

        self._blink_timer   = 0
        self._blink_visible = True

        self._alpha     = 0
        self._fading_in = True
        self._fade_surf = pygame.Surface((screen_w, screen_h))
        self._fade_surf.fill((0, 0, 0))

        self._surf_title    = self.font_title.render("GRAINGER", True, C_TITLE)
        self._surf_subtitle = self.font_subtitle.render("A Murder Mystery", True, C_SUBTITLE)
        self._surf_tagline  = self.font_tagline.render(
            "Grainger Engineering Library  \u2022  Five Floors  \u2022  One Killer",
            True, C_DIM
        )
        self._surf_hint = self.font_hint.render(
            "W / S  or  \u2191 \u2193  to navigate     ENTER / Click to confirm",
            True, C_DIM
        )

        # Mouse state
        self._option_rects = []  # filled each draw()
        self._surf_version = self.font_hint.render("v0.1.0", True, C_DIM)

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, dt):
        if self._fading_in:
            self._alpha = max(0, self._alpha - int(dt * 3))
            if self._alpha == 0:
                self._fading_in = False

        self._blink_timer += dt
        if self._blink_timer >= 500:
            self._blink_timer   = 0
            self._blink_visible = not self._blink_visible

    # ------------------------------------------------------------------
    # Input — returns "start", "quit", or None
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
            return "quit"

        return None

    def _confirm(self):
        if self.selected == OPTION_START:
            self._fading_in = True
            self._alpha     = 0
            return "start"
        elif self.selected == OPTION_QUIT:
            return "quit"

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def draw(self, screen):
        screen.fill(C_BG)

        pygame.draw.rect(screen, C_BORDER, (0, 0, self.W, 5))
        pygame.draw.rect(screen, C_BORDER, (0, self.H - 5, self.W, 5))

        cx = self.W // 2

        title_y = self.H // 5
        screen.blit(self._surf_title,
                    (cx - self._surf_title.get_width() // 2, title_y))
        screen.blit(self._surf_subtitle,
                    (cx - self._surf_subtitle.get_width() // 2,
                     title_y + self._surf_title.get_height() + 8))
        screen.blit(self._surf_tagline,
                    (cx - self._surf_tagline.get_width() // 2,
                     title_y + self._surf_title.get_height() + 44))

        div_y = title_y + self._surf_title.get_height() + 74
        pygame.draw.line(screen, C_BORDER,
                         (cx - 200, div_y), (cx + 200, div_y), 1)

        option_start_y = self.H // 2 - 10
        option_gap     = 52

        mouse_pos = pygame.mouse.get_pos()
        self._option_rects = []
        hovering_any = False

        for i, label in enumerate(OPTIONS):
            is_sel = i == self.selected
            colour = C_SELECTED if is_sel else C_UNSELECTED
            text   = self.font_option.render(label, True, colour)
            text_x = cx - text.get_width() // 2
            text_y = option_start_y + i * option_gap

            bar_rect = pygame.Rect(cx - 160, text_y - 6, 320, text.get_height() + 12)
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

        screen.blit(self._surf_hint,
                    (cx - self._surf_hint.get_width() // 2, self.H - 50))
        screen.blit(self._surf_version,
                    (self.W - self._surf_version.get_width() - 10, self.H - 22))

        if self._fading_in:
            self._fade_surf.set_alpha(self._alpha)
            screen.blit(self._fade_surf, (0, 0))


# ---------------------------------------------------------------------------
# Standalone runner — python -m ui.menu  or  python ui/menu.py
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import main
    main.main()
