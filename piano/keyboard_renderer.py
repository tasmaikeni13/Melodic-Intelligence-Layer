"""
keyboard_renderer.py — All rendering: keyboard, textures, lighting,
reflections, labels, HUD.

Pre‑renders ivory/ebony key textures and the concert‑hall background at
startup.  Each frame only blits the cached surfaces and draws dynamic
elements (pressed‑key highlights, HUD text, pedal indicators).
"""

from __future__ import annotations

import math
import numpy as np
import pygame

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE,
    KEYBOARD_Y, KEYBOARD_BOTTOM, REFLECTION_HEIGHT,
    WHITE_KEY_WIDTH, WHITE_KEY_HEIGHT,
    BLACK_KEY_WIDTH, BLACK_KEY_HEIGHT, KEY_GAP,
    KEY_PRESS_DEPTH_WHITE, KEY_PRESS_DEPTH_BLACK, KEY_ANIM_SPEED,
    FIRST_MIDI, LAST_MIDI,
    # colours
    BG_TOP_COLOR, BG_MID_COLOR, BG_BOTTOM_COLOR, SPOTLIGHT_COLOR,
    WHITE_KEY_BASE, WHITE_KEY_PRESSED, WHITE_KEY_EDGE, WHITE_KEY_TOP_SHADE,
    BLACK_KEY_BASE, BLACK_KEY_PRESSED, BLACK_KEY_HIGHLIGHT,
    BLACK_KEY_BEVEL_LT, BLACK_KEY_BEVEL_DK,
    HUD_BG, HUD_TEXT, HUD_TEXT_DIM,
    PEDAL_ACTIVE, PEDAL_INACTIVE,
    VOLUME_BAR_BG, VOLUME_BAR_FG,
    LABEL_COLOR, LABEL_COLOR_C, OCTAVE_LINE_COLOR,
    # helpers
    is_black_key, midi_to_note_name,
)


# ═══════════════════════════════════════════════════════════════
#  KeyboardRenderer
# ═══════════════════════════════════════════════════════════════

class KeyboardRenderer:
    """Handles every pixel that reaches the screen."""

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.clock  = pygame.time.Clock()

        # Key animation state: midi → float in [0, 1]
        self.press_amounts: dict[int, float] = {
            m: 0.0 for m in range(FIRST_MIDI, LAST_MIDI + 1)
        }

        # Toggle flags
        self.show_labels   = False
        self.show_octaves  = True    # C‑markers always on by default

        # Fonts
        pygame.font.init()
        self._load_fonts()

        # Pre‑render static assets
        self._bg_surface        = self._create_background()
        self._white_key_surface = self._create_white_key_texture()
        self._black_key_surface = self._create_black_key_texture()
        self._white_key_pressed_surface = self._create_white_key_pressed_texture()
        self._black_key_pressed_surface = self._create_black_key_pressed_texture()

    # ── font loading ────────────────────────────────────────────
    def _load_fonts(self) -> None:
        # Try to find a nice serif / display font
        preferred = ["Georgia", "Palatino Linotype", "Book Antiqua",
                     "Times New Roman", "DejaVu Serif"]
        available = pygame.font.get_fonts()
        chosen = None
        for name in preferred:
            low = name.lower().replace(" ", "")
            if low in available:
                chosen = pygame.font.match_font(low)
                break

        if chosen:
            self.font_title = pygame.font.Font(chosen, 22)
            self.font_hud   = pygame.font.Font(chosen, 16)
            self.font_label = pygame.font.Font(chosen, 11)
            self.font_pedal = pygame.font.Font(chosen, 12)
        else:
            self.font_title = pygame.font.SysFont(None, 24)
            self.font_hud   = pygame.font.SysFont(None, 18)
            self.font_label = pygame.font.SysFont(None, 13)
            self.font_pedal = pygame.font.SysFont(None, 14)

    # ── pre‑rendered textures ───────────────────────────────────
    def _create_background(self) -> pygame.Surface:
        """Dark concert‑hall stage with warm spotlight."""
        bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        # Vertical gradient for the upper area
        for y in range(KEYBOARD_Y):
            t = y / max(1, KEYBOARD_Y)
            r = int(BG_TOP_COLOR[0] + (BG_MID_COLOR[0] - BG_TOP_COLOR[0]) * t)
            g = int(BG_TOP_COLOR[1] + (BG_MID_COLOR[1] - BG_TOP_COLOR[1]) * t)
            b = int(BG_TOP_COLOR[2] + (BG_MID_COLOR[2] - BG_TOP_COLOR[2]) * t)
            pygame.draw.line(bg, (r, g, b), (0, y), (SCREEN_WIDTH, y))

        # Below the keyboard
        for y in range(KEYBOARD_BOTTOM, SCREEN_HEIGHT):
            t = (y - KEYBOARD_BOTTOM) / max(1, SCREEN_HEIGHT - KEYBOARD_BOTTOM)
            r = int(BG_MID_COLOR[0] + (BG_BOTTOM_COLOR[0] - BG_MID_COLOR[0]) * t)
            g = int(BG_MID_COLOR[1] + (BG_BOTTOM_COLOR[1] - BG_MID_COLOR[1]) * t)
            b = int(BG_MID_COLOR[2] + (BG_BOTTOM_COLOR[2] - BG_MID_COLOR[2]) * t)
            pygame.draw.line(bg, (r, g, b), (0, y), (SCREEN_WIDTH, y))

        # Warm spotlight overlay
        spot = pygame.Surface((SCREEN_WIDTH, KEYBOARD_Y), pygame.SRCALPHA)
        cx, cy = SCREEN_WIDTH // 2, KEYBOARD_Y - 180
        max_r  = 700
        for r in range(max_r, 0, -3):
            frac  = r / max_r
            alpha = int(18 * (1.0 - frac * frac))
            alpha = max(0, min(255, alpha))
            color = (SPOTLIGHT_COLOR[0], SPOTLIGHT_COLOR[1],
                     SPOTLIGHT_COLOR[2], alpha)
            pygame.draw.circle(spot, color, (cx, cy), r)
        bg.blit(spot, (0, 0))

        # Two softer side lights
        for sx in [SCREEN_WIDTH // 4, 3 * SCREEN_WIDTH // 4]:
            side = pygame.Surface((SCREEN_WIDTH, KEYBOARD_Y), pygame.SRCALPHA)
            for r in range(400, 0, -4):
                frac  = r / 400
                alpha = int(8 * (1.0 - frac * frac))
                color = (SPOTLIGHT_COLOR[0], SPOTLIGHT_COLOR[1],
                         SPOTLIGHT_COLOR[2], max(0, alpha))
                pygame.draw.circle(side, color, (sx, cy + 50), r)
            bg.blit(side, (0, 0))

        # Subtle horizontal line across the top of the keyboard (fallboard edge)
        for i in range(3):
            c = 30 - i * 8
            pygame.draw.line(bg, (c, c, c),
                             (0, KEYBOARD_Y - 3 + i),
                             (SCREEN_WIDTH, KEYBOARD_Y - 3 + i))

        return bg

    def _create_white_key_texture(self) -> pygame.Surface:
        """Ivory‑textured white key (single key, later tiled)."""
        w = int(WHITE_KEY_WIDTH - KEY_GAP)
        h = int(WHITE_KEY_HEIGHT)
        surf = pygame.Surface((w, h))

        # Vertical gradient: subtle darker at top (shadow), lighter toward bottom
        for y in range(h):
            t = y / max(1, h)
            r = int(WHITE_KEY_TOP_SHADE[0]
                    + (WHITE_KEY_BASE[0] - WHITE_KEY_TOP_SHADE[0]) * t)
            g = int(WHITE_KEY_TOP_SHADE[1]
                    + (WHITE_KEY_BASE[1] - WHITE_KEY_TOP_SHADE[1]) * t)
            b = int(WHITE_KEY_TOP_SHADE[2]
                    + (WHITE_KEY_BASE[2] - WHITE_KEY_TOP_SHADE[2]) * t)
            pygame.draw.line(surf, (r, g, b), (0, y), (w, y))

        # Subtle grain texture (numpy noise)
        arr = pygame.surfarray.pixels3d(surf)
        noise = np.random.randint(-3, 4, arr.shape, dtype=np.int16)
        np.clip(arr.astype(np.int16) + noise, 0, 255, out=noise)
        arr[:] = noise.astype(np.uint8)
        del arr  # release pixel lock

        # Side edges (slightly darker vertical lines)
        pygame.draw.line(surf, WHITE_KEY_EDGE, (0, 0), (0, h - 1))
        pygame.draw.line(surf, WHITE_KEY_EDGE, (w - 1, 0), (w - 1, h - 1))

        # Rounded bottom corners (paint two small arcs)
        radius = 4
        pygame.draw.rect(surf, WHITE_KEY_BASE,
                         pygame.Rect(0, h - radius, w, radius))
        pygame.draw.ellipse(surf, WHITE_KEY_BASE,
                            pygame.Rect(0, h - radius * 2, radius * 2, radius * 2))
        pygame.draw.ellipse(surf, WHITE_KEY_BASE,
                            pygame.Rect(w - radius * 2, h - radius * 2,
                                        radius * 2, radius * 2))

        return surf

    def _create_white_key_pressed_texture(self) -> pygame.Surface:
        """Warm amber tinted pressed white key."""
        base = self._white_key_surface.copy()
        tint = pygame.Surface(base.get_size(), pygame.SRCALPHA)
        tint.fill((*WHITE_KEY_PRESSED, 110))
        base.blit(tint, (0, 0))
        return base

    def _create_black_key_texture(self) -> pygame.Surface:
        """Ebony‑textured black key with 3D bevel."""
        w = int(BLACK_KEY_WIDTH)
        h = int(BLACK_KEY_HEIGHT)
        surf = pygame.Surface((w, h))
        surf.fill(BLACK_KEY_BASE)

        # Glossy highlight strip down the centre
        strip_x = int(w * 0.28)
        strip_w = int(w * 0.44)
        for y in range(int(h * 0.08), int(h * 0.75)):
            t = (y - h * 0.08) / max(1, h * 0.67)
            brightness = int(10 + 18 * math.sin(t * math.pi))
            color = tuple(min(255, BLACK_KEY_BASE[i] + brightness) for i in range(3))
            pygame.draw.line(surf, color, (strip_x, y), (strip_x + strip_w, y))

        # Bevel edges
        pygame.draw.line(surf, BLACK_KEY_BEVEL_LT, (0, 0), (0, h - 1))
        pygame.draw.line(surf, BLACK_KEY_BEVEL_LT, (0, 0), (w - 1, 0))
        pygame.draw.line(surf, BLACK_KEY_BEVEL_DK, (w - 1, 0), (w - 1, h - 1))
        pygame.draw.line(surf, BLACK_KEY_BEVEL_DK, (0, h - 1), (w - 1, h - 1))

        # 3D bottom face
        bottom_h = 6
        for y in range(bottom_h):
            t = y / bottom_h
            c = int(12 + 20 * t)
            pygame.draw.line(surf, (c, c - 1, c - 2),
                             (2, h - bottom_h + y), (w - 2, h - bottom_h + y))

        return surf

    def _create_black_key_pressed_texture(self) -> pygame.Surface:
        """Pressed (lowered) black key with amber tint."""
        base = self._black_key_surface.copy()
        tint = pygame.Surface(base.get_size(), pygame.SRCALPHA)
        tint.fill((*BLACK_KEY_PRESSED, 100))
        base.blit(tint, (0, 0))
        return base

    # ── per‑frame update ────────────────────────────────────────
    def update_animations(self, pressed_notes: set[int], dt: float) -> None:
        """Ease key‑press animations toward target state."""
        for midi in range(FIRST_MIDI, LAST_MIDI + 1):
            target = 1.0 if midi in pressed_notes else 0.0
            current = self.press_amounts[midi]
            if current < target:
                self.press_amounts[midi] = min(
                    target, current + KEY_ANIM_SPEED * dt)
            elif current > target:
                self.press_amounts[midi] = max(
                    target, current - KEY_ANIM_SPEED * dt)

    # ── main draw ───────────────────────────────────────────────
    def draw(self, white_keys, black_keys,
             pedal_states: list[tuple[str, bool]],
             master_volume: float,
             active_note_name: str,
             cursor_octave: str) -> None:
        """Render one complete frame."""

        # 1. Background
        self.screen.blit(self._bg_surface, (0, 0))

        # 2. White keys
        for ki in white_keys:
            amt = self.press_amounts.get(ki.midi_note, 0.0)
            offset = int(amt * KEY_PRESS_DEPTH_WHITE)
            tex = (self._white_key_pressed_surface if amt > 0.3
                   else self._white_key_surface)
            self.screen.blit(tex, (int(ki.x), int(ki.y) + offset))

            # Shadow cast by adjacent black keys (subtle darkening strip)
            self._draw_black_key_shadow(ki)

        # 3. Black keys (on top)
        for ki in black_keys:
            amt = self.press_amounts.get(ki.midi_note, 0.0)
            offset = int(amt * KEY_PRESS_DEPTH_BLACK)
            tex = (self._black_key_pressed_surface if amt > 0.3
                   else self._black_key_surface)
            self.screen.blit(tex, (int(ki.x), int(ki.y) + offset))

        # 4. Key outlines / borders between white keys
        for ki in white_keys:
            x_right = int(ki.x + ki.w)
            pygame.draw.line(self.screen, (45, 40, 35),
                             (x_right, KEYBOARD_Y),
                             (x_right, KEYBOARD_BOTTOM - 1))

        # 5. C‑note octave markers
        if self.show_octaves:
            self._draw_octave_markers(white_keys)

        # 6. Note labels
        if self.show_labels:
            self._draw_note_labels(white_keys)

        # 7. Reflection below keyboard
        self._draw_reflection()

        # 8. HUD
        self._draw_hud(pedal_states, master_volume,
                       active_note_name, cursor_octave)

    # ── sub‑draws ───────────────────────────────────────────────
    def _draw_black_key_shadow(self, wk) -> None:
        """Paint a faint shadow strip on a white key below an adjacent black key."""
        shadow = pygame.Surface((int(BLACK_KEY_WIDTH // 2), int(BLACK_KEY_HEIGHT)),
                                pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 22))
        # Left neighbour shadow
        sx = int(wk.x + wk.w - BLACK_KEY_WIDTH // 4)
        if sx > 0:
            self.screen.blit(shadow, (sx, KEYBOARD_Y))

    def _draw_octave_markers(self, white_keys) -> None:
        """Small 'C' label at the base of each C key."""
        for ki in white_keys:
            if ki.midi_note % 12 == 0:  # It's a C
                name = midi_to_note_name(ki.midi_note)
                txt  = self.font_label.render(name, True, LABEL_COLOR_C)
                tx   = int(ki.x + ki.w / 2 - txt.get_width() / 2)
                ty   = KEYBOARD_BOTTOM - 20
                self.screen.blit(txt, (tx, ty))

                # Faint vertical line at octave boundary
                line_surf = pygame.Surface((1, int(WHITE_KEY_HEIGHT)), pygame.SRCALPHA)
                line_surf.fill((*OCTAVE_LINE_COLOR[:3], 45))
                self.screen.blit(line_surf, (int(ki.x), KEYBOARD_Y))

    def _draw_note_labels(self, white_keys) -> None:
        """Render note name on every white key."""
        for ki in white_keys:
            name = midi_to_note_name(ki.midi_note)
            txt  = self.font_label.render(name, True, LABEL_COLOR)
            tx   = int(ki.x + ki.w / 2 - txt.get_width() / 2)
            ty   = KEYBOARD_BOTTOM - 36
            self.screen.blit(txt, (tx, ty))

    def _draw_reflection(self) -> None:
        """Faint mirrored reflection below the keyboard."""
        strip_h = min(REFLECTION_HEIGHT, SCREEN_HEIGHT - KEYBOARD_BOTTOM)
        if strip_h <= 0:
            return

        # Grab the bottom slice of the keyboard area
        kb_rect = pygame.Rect(0, KEYBOARD_BOTTOM - strip_h,
                              SCREEN_WIDTH, strip_h)
        try:
            strip = self.screen.subsurface(kb_rect).copy()
        except ValueError:
            return
        strip = pygame.transform.flip(strip, False, True)

        # Apply fading alpha
        fade = pygame.Surface(strip.get_size(), pygame.SRCALPHA)
        for y in range(strip_h):
            alpha = int(35 * (1.0 - y / strip_h))
            pygame.draw.line(fade, (255, 255, 255, alpha),
                             (0, y), (SCREEN_WIDTH, y))
        strip.blit(fade, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        self.screen.blit(strip, (0, KEYBOARD_BOTTOM))

    def _draw_hud(self, pedal_states, master_volume,
                  active_note, cursor_octave) -> None:
        """Top bar, pedal indicators, and volume bar."""

        # --- Top bar ---
        bar = pygame.Surface((SCREEN_WIDTH, 44), pygame.SRCALPHA)
        bar.fill(HUD_BG)
        self.screen.blit(bar, (0, 0))

        # Title
        title_surf = self.font_title.render(TITLE, True, HUD_TEXT)
        self.screen.blit(title_surf, (20, 10))

        # Active note
        if active_note:
            note_txt = self.font_hud.render(
                f"Playing: {active_note}", True, WHITE_KEY_PRESSED)
            self.screen.blit(note_txt, (SCREEN_WIDTH // 2 - note_txt.get_width() // 2,
                                         13))

        # Cursor octave
        if cursor_octave:
            oct_txt = self.font_hud.render(
                f"Octave: {cursor_octave}", True, HUD_TEXT_DIM)
            self.screen.blit(oct_txt, (SCREEN_WIDTH - 200, 13))

        # --- Pedal indicators ---
        px, py = 30, SCREEN_HEIGHT - 50
        for label, active in pedal_states:
            color = PEDAL_ACTIVE if active else PEDAL_INACTIVE
            # Outer circle
            pygame.draw.circle(self.screen, color, (px, py), 10)
            if active:
                # Glow ring
                glow = pygame.Surface((30, 30), pygame.SRCALPHA)
                pygame.draw.circle(glow, (*PEDAL_ACTIVE, 50), (15, 15), 15)
                self.screen.blit(glow, (px - 15, py - 15))
            # Label
            lbl = self.font_pedal.render(label, True,
                                          HUD_TEXT if active else HUD_TEXT_DIM)
            self.screen.blit(lbl, (px + 16, py - 7))
            px += lbl.get_width() + 50

        # --- Volume bar ---
        vx = SCREEN_WIDTH - 40
        vy_top = SCREEN_HEIGHT - 160
        bar_h  = 120
        bar_w  = 8

        # Background track
        pygame.draw.rect(self.screen, VOLUME_BAR_BG,
                         (vx, vy_top, bar_w, bar_h), border_radius=4)
        # Filled portion
        fill_h = int(bar_h * master_volume)
        fill_y = vy_top + bar_h - fill_h
        if fill_h > 0:
            pygame.draw.rect(self.screen, VOLUME_BAR_FG,
                             (vx, fill_y, bar_w, fill_h), border_radius=4)
        # Percentage text
        vol_txt = self.font_label.render(f"{int(master_volume * 100)}%",
                                          True, HUD_TEXT_DIM)
        self.screen.blit(vol_txt, (vx - 4, vy_top + bar_h + 6))

        # --- FPS counter (subtle) ---
        fps_val  = self.clock.get_fps()
        fps_surf = self.font_label.render(f"{fps_val:.0f} fps", True, HUD_TEXT_DIM)
        self.screen.blit(fps_surf, (SCREEN_WIDTH - 70, 14))

    # ── public toggles ──────────────────────────────────────────
    def toggle_labels(self) -> None:
        self.show_labels = not self.show_labels

    def toggle_octaves(self) -> None:
        self.show_octaves = not self.show_octaves

    def tick(self) -> float:
        """Advance the frame clock and return dt in seconds."""
        return self.clock.tick(FPS) / 1000.0
