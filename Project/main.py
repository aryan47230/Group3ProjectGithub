"""
main.py  —  Entry point for Grainger Mystery
---------------------------------------------
Run with:  python main.py
"""

import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SCREEN_W = 900
SCREEN_H = 700

C_BG        = (18,  18,  24)
C_BORDER    = (180, 140,  60)
C_NAME_BG   = (30,  26,  18)
C_BOX_BG    = (22,  20,  30)
C_NAME_TEXT = (220, 170,  60)
C_BODY_TEXT = (230, 220, 200)
C_DIM       = (140, 130, 110)
C_PORTRAIT  = (40,  36,  50)
C_ACCENT    = (180, 140,  60)
C_BTN_BG    = (32,  28,  20)
C_BTN_HOV   = (50,  44,  28)

# ---------------------------------------------------------------------------
# Shared helper
# ---------------------------------------------------------------------------

def draw_button(screen, rect, label, font, hovered):
    bg = C_BTN_HOV if hovered else C_BTN_BG
    pygame.draw.rect(screen, bg,       rect, border_radius=5)
    pygame.draw.rect(screen, C_BORDER, rect, width=1, border_radius=5)
    surf = font.render(label, True, C_ACCENT if hovered else C_DIM)
    screen.blit(surf, surf.get_rect(center=rect.center))


# ---------------------------------------------------------------------------
# Librarian dialogue
# ---------------------------------------------------------------------------

LIBRARIAN_NAME  = "Mrs. Chen  —  Head Librarian"
LIBRARIAN_LINES = [
    "Oh, thank goodness you're here...",
    "I'm Mrs. Chen, the head librarian of Grainger Engineering Library.",
    "Something terrible has happened. Bob Grainger was found dead\n"
    "this morning on the third floor.",
    "The police are baffled. Someone tampered with the crime scene\n"
    "before they could secure it.",
    "I don't know who did it, or why... but I knew Bob for years.\n"
    "He didn't deserve this.",
    "Please, detective. Look around. Ask questions. Find the truth.",
    "I'll help however I can. Just... find out who did this to him.",
]

TYPEWRITER_SPEED = 0.03


class LibrarianDialogue:
    def __init__(self, screen_w, screen_h):
        self.W = screen_w
        self.H = screen_h

        pygame.font.init()
        self.font_name = pygame.font.SysFont("Georgia",     16, bold=True)
        self.font_body = pygame.font.SysFont("Georgia",     20)
        self.font_hint = pygame.font.SysFont("Courier New", 12)
        self.font_btn  = pygame.font.SysFont("Courier New", 13, bold=True)

        self._line_idx  = 0
        self._char_idx  = 0
        self._timer     = 0.0
        self._done      = False
        self._blink     = 0
        self._blink_vis = True

        self._box_w   = screen_w - 200
        self._wrapped = [self._wrap(ln) for ln in LIBRARIAN_LINES]

        # Back to menu button (top-left)
        self.btn_back = pygame.Rect(14, 14, 140, 28)

    def _wrap(self, text):
        lines, max_w = [], self._box_w - 40
        for segment in text.split("\n"):
            words, current = segment.split(), ""
            for word in words:
                test = (current + " " + word).strip()
                if self.font_body.size(test)[0] <= max_w:
                    current = test
                else:
                    if current:
                        lines.append(current)
                    current = word
            if current:
                lines.append(current)
        return lines

    def _full_text(self):
        return "\n".join(self._wrapped[self._line_idx])

    def update(self, dt_ms):
        if self._done:
            return
        self._timer += dt_ms / 1000.0
        full = self._full_text()
        while self._timer >= TYPEWRITER_SPEED and self._char_idx < len(full):
            self._char_idx += 1
            self._timer    -= TYPEWRITER_SPEED
        self._blink += dt_ms
        if self._blink >= 500:
            self._blink     = 0
            self._blink_vis = not self._blink_vis

    def _advance(self):
        full = self._full_text()
        if self._char_idx < len(full):
            self._char_idx = len(full)
        elif self._line_idx < len(LIBRARIAN_LINES) - 1:
            self._line_idx += 1
            self._char_idx  = 0
            self._timer     = 0.0
        else:
            self._done = True

    def handle_event(self, event):
        """Returns 'menu', 'done', or None."""
        mouse = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_back.collidepoint(mouse):
                return "menu"
            self._advance()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "menu"
            if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                self._advance()

        return "done" if self._done else None

    def draw(self, screen):
        screen.fill(C_BG)

        mouse = pygame.mouse.get_pos()

        # Back to menu button
        draw_button(screen, self.btn_back, "\u2190  BACK TO MENU",
                    self.font_btn, self.btn_back.collidepoint(mouse))
        pygame.mouse.set_cursor(
            pygame.SYSTEM_CURSOR_HAND
            if self.btn_back.collidepoint(mouse)
            else pygame.SYSTEM_CURSOR_ARROW
        )

        # Header
        label = self.font_hint.render(
            "[ GRAINGER ENGINEERING LIBRARY  \u2014  INTRODUCTION ]", True, C_DIM)
        screen.blit(label, (self.W // 2 - label.get_width() // 2, 18))
        pygame.draw.line(screen, C_BORDER, (60, 46), (self.W - 60, 46), 1)

        # Portrait
        portrait_rect = pygame.Rect(40, self.H - 280, 130, 220)
        pygame.draw.rect(screen, C_PORTRAIT, portrait_rect, border_radius=6)
        pygame.draw.rect(screen, C_ACCENT,   portrait_rect, width=2, border_radius=6)
        cx, cy = portrait_rect.centerx, portrait_rect.y + 60
        pygame.draw.circle(screen, C_DIM, (cx, cy), 28)
        pygame.draw.rect(screen, C_DIM,
                         pygame.Rect(cx - 30, cy + 28, 60, 80), border_radius=4)
        tag = self.font_hint.render("MRS. CHEN", True, C_ACCENT)
        screen.blit(tag, (portrait_rect.centerx - tag.get_width() // 2,
                          portrait_rect.bottom - 20))

        # Dialogue box
        box_x    = portrait_rect.right + 20
        box_y    = self.H - 290
        box_w    = self.W - box_x - 30
        box_h    = 240
        box_rect = pygame.Rect(box_x, box_y, box_w, box_h)
        pygame.draw.rect(screen, C_BOX_BG, box_rect, border_radius=8)
        pygame.draw.rect(screen, C_BORDER, box_rect, width=2, border_radius=8)

        # Name plate
        name_rect = pygame.Rect(box_x + 12, box_y - 18, 290, 28)
        pygame.draw.rect(screen, C_NAME_BG, name_rect, border_radius=4)
        pygame.draw.rect(screen, C_ACCENT,  name_rect, width=1, border_radius=4)
        screen.blit(self.font_name.render(LIBRARIAN_NAME, True, C_NAME_TEXT),
                    (name_rect.x + 10, name_rect.y + 5))

        # Typed text
        displayed  = self._full_text()[:self._char_idx]
        chars_left = len(displayed)
        ty = box_y + 18
        for ln in self._wrapped[self._line_idx]:
            if chars_left <= 0:
                break
            surf = self.font_body.render(ln[:chars_left], True, C_BODY_TEXT)
            screen.blit(surf, (box_x + 16, ty))
            chars_left -= len(ln)
            ty += self.font_body.get_linesize() + 2

        # Continue arrow
        if self._char_idx >= len(self._full_text()) and self._blink_vis:
            is_last = self._line_idx == len(LIBRARIAN_LINES) - 1
            arrow   = "\u25bc click to continue" if not is_last else "\u25bc click to proceed"
            a_surf  = self.font_hint.render(arrow, True, C_ACCENT)
            screen.blit(a_surf, (box_rect.right - a_surf.get_width() - 14,
                                  box_rect.bottom - a_surf.get_height() - 10))

        # Progress dots
        dot_y = box_rect.bottom + 10
        for i in range(len(LIBRARIAN_LINES)):
            col = C_ACCENT if i == self._line_idx else C_DIM
            pygame.draw.circle(screen, col,
                               (self.W // 2 - (len(LIBRARIAN_LINES) * 14) // 2 + i * 14,
                                dot_y), 4)


# ---------------------------------------------------------------------------
# Investigation hub  (shown after librarian dialogue)
# ---------------------------------------------------------------------------

C_CARD_BG    = (25,  22,  35)
C_CARD_HOV   = (35,  30,  48)
C_CARD_BORD  = (100,  80, 130)
C_SOON       = (160, 140, 100)
C_HUB_TITLE  = (200, 160,  60)


class InvestigationHub:
    """Simple hub screen with a puzzle card and a back-to-menu button."""

    def __init__(self, screen_w, screen_h):
        self.W = screen_w
        self.H = screen_h

        pygame.font.init()
        self.font_title  = pygame.font.SysFont("Georgia",     40, bold=True)
        self.font_card   = pygame.font.SysFont("Courier New", 16, bold=True)
        self.font_sub    = pygame.font.SysFont("Courier New", 12)
        self.font_btn    = pygame.font.SysFont("Courier New", 13, bold=True)

        # Puzzle card (centre of screen)
        card_w, card_h = 240, 300
        self.card_rect = pygame.Rect(
            screen_w // 2 - card_w // 2,
            screen_h // 2 - card_h // 2 - 20,
            card_w, card_h
        )

        # Back button (top-left)
        self.btn_back = pygame.Rect(14, 14, 140, 28)

        self._notify_timer = 0   # how long to show "coming soon" flash

    def handle_event(self, event):
        """Returns 'menu' or None."""
        mouse = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_back.collidepoint(mouse):
                return "menu"
            if self.card_rect.collidepoint(mouse):
                self._notify_timer = 2000   # show message for 2 s

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "menu"

        return None

    def update(self, dt_ms):
        if self._notify_timer > 0:
            self._notify_timer -= dt_ms

    def draw(self, screen):
        screen.fill(C_BG)

        mouse = pygame.mouse.get_pos()

        # Back button
        draw_button(screen, self.btn_back, "\u2190  BACK TO MENU",
                    self.font_btn, self.btn_back.collidepoint(mouse))

        # Title
        title = self.font_title.render("INVESTIGATION", True, C_HUB_TITLE)
        screen.blit(title, (self.W // 2 - title.get_width() // 2, 60))
        pygame.draw.line(screen, C_BORDER,
                         (self.W // 2 - 200, 112), (self.W // 2 + 200, 112), 1)

        # Puzzle card
        hovered = self.card_rect.collidepoint(mouse)
        card_bg = C_CARD_HOV if hovered else C_CARD_BG
        pygame.draw.rect(screen, card_bg,       self.card_rect, border_radius=10)
        pygame.draw.rect(screen, C_CARD_BORD,   self.card_rect, width=2, border_radius=10)

        # Card icon (simple file/folder shape)
        icon_x = self.card_rect.centerx
        icon_y = self.card_rect.y + 70
        pygame.draw.rect(screen, C_DIM,
                         pygame.Rect(icon_x - 35, icon_y - 45, 70, 85), border_radius=4)
        pygame.draw.rect(screen, C_CARD_BORD,
                         pygame.Rect(icon_x - 35, icon_y - 45, 70, 85), width=1, border_radius=4)
        pygame.draw.rect(screen, C_DIM,
                         pygame.Rect(icon_x - 35, icon_y - 55, 38, 14), border_radius=3)

        # Card label
        lbl  = self.font_card.render("CRIME SCENE",   True, C_BODY_TEXT)
        lbl2 = self.font_card.render("PUZZLE",        True, C_BODY_TEXT)
        screen.blit(lbl,  lbl.get_rect( centerx=self.card_rect.centerx, top=icon_y + 52))
        screen.blit(lbl2, lbl2.get_rect(centerx=self.card_rect.centerx, top=icon_y + 74))

        # "Click to play" hint inside card
        hint_col = C_ACCENT if hovered else C_DIM
        hint = self.font_sub.render("click to play", True, hint_col)
        screen.blit(hint, hint.get_rect(centerx=self.card_rect.centerx,
                                         bottom=self.card_rect.bottom - 16))

        # Coming-soon flash
        if self._notify_timer > 0:
            msg = self.font_card.render("Puzzle coming soon!", True, C_SOON)
            msg_rect = msg.get_rect(centerx=self.W // 2,
                                     top=self.card_rect.bottom + 20)
            screen.blit(msg, msg_rect)

        # Cursor
        clickable = self.btn_back.collidepoint(mouse) or self.card_rect.collidepoint(mouse)
        pygame.mouse.set_cursor(
            pygame.SYSTEM_CURSOR_HAND if clickable else pygame.SYSTEM_CURSOR_ARROW)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Grainger Mystery")
    clock = pygame.time.Clock()

    from menu import Menu
    menu      = Menu(SCREEN_W, SCREEN_H)
    librarian = LibrarianDialogue(SCREEN_W, SCREEN_H)
    hub       = InvestigationHub(SCREEN_W, SCREEN_H)

    state = "menu"

    while True:
        dt = clock.tick(60)

        # ----------------------------------------------------------------
        if state == "menu":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                action = menu.handle_event(event)
                if action == "start":
                    librarian = LibrarianDialogue(SCREEN_W, SCREEN_H)
                    state = "librarian"
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                elif action == "quit":
                    pygame.quit(); sys.exit()
            menu.update(dt)
            menu.draw(screen)
            pygame.display.flip()

        # ----------------------------------------------------------------
        elif state == "librarian":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                result = librarian.handle_event(event)
                if result == "menu":
                    state = "menu"
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                elif result == "done":
                    import subprocess
                    game_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                             "Gus", "File 1.py")
                    subprocess.Popen([sys.executable, game_path],
                                     cwd=os.path.dirname(game_path))
                    pygame.quit()
                    sys.exit()
            librarian.update(dt)
            librarian.draw(screen)
            pygame.display.flip()

        # ----------------------------------------------------------------
        elif state == "hub":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                result = hub.handle_event(event)
                if result == "menu":
                    state = "menu"
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            hub.update(dt)
            hub.draw(screen)
            pygame.display.flip()


if __name__ == "__main__":
    main()
