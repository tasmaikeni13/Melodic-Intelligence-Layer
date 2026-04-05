"""
main.py — MIL Concert Grand: Character-Driven Hierarchical Piano Composition

Generates coherent piano pieces using the MIL character-driven hierarchical
theory, plays them back with full visual animation on the 88-key concert grand,
and optionally exports each piece as a standard MIDI file.

The archetype selector lets the user choose a musical character (Nocturne,
March, Waltz, Étude, Ballade, Toccata, Rhapsody, Lullaby, etc.) or Random
for a unique unnamed character each time.  The pianist selector chooses a
performance personality (Horowitz, Gould, Argerich, Rubinstein, etc.) that
colours dynamics, rubato, pedalling, and ornamentation.
"""

from __future__ import annotations

import sys
import os
import time as _time

import pygame

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE,
    VOLUME_STEP, FIRST_MIDI, LAST_MIDI,
    midi_to_note_name,
    BTN_WIDTH, BTN_HEIGHT,
    BTN_COLOR, BTN_HOVER_COLOR, BTN_PRESS_COLOR,
    BTN_TEXT_COLOR, BTN_BORDER,
    STATUS_COLOR, INFO_COLOR,
    PROG_X, PROG_W, PROG_H, PROG_BG, PROG_FG,
    TENSION_X, TENSION_W, TENSION_H,
    TENSION_BG, TENSION_LO, TENSION_HI,
    HUD_BG, HUD_TEXT, HUD_TEXT_DIM,
)
from piano_engine import PianoEngine
from keyboard_renderer import KeyboardRenderer
from input_handler import InputHandler
from mil_engine import (
    MILGenerator, Playback, write_midi, PHFState,
    ARCHETYPE_NAMES, PIANIST_NAMES,
)

# --- UI Layout ---
CENTER_X = SCREEN_WIDTH // 2
BASE_Y   = 220
ROW2_Y   = BASE_Y + 45
ROW3_Y   = ROW2_Y + 42
BTN_Y_NEW = ROW3_Y + 50
CHK_Y_NEW = BTN_Y_NEW + BTN_HEIGHT + 15
STATUS_Y_NEW = CHK_Y_NEW + 35
PROG_Y_NEW = STATUS_Y_NEW + 40
TENSION_Y_NEW = PROG_Y_NEW + 20


def main() -> None:
    """Application entry point."""

    pygame.init()
    screen = pygame.display.set_mode(
        (SCREEN_WIDTH, SCREEN_HEIGHT),
        pygame.DOUBLEBUF | pygame.HWSURFACE,
    )
    pygame.display.set_caption("MIL Concert Grand — Character-Driven Composition")
    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

    engine   = PianoEngine()
    renderer = KeyboardRenderer(screen)
    handler  = InputHandler()

    engine.start()

    # Fonts
    pygame.font.init()
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
        font_btn    = pygame.font.Font(chosen, 18)
        font_status = pygame.font.Font(chosen, 15)
        font_info   = pygame.font.Font(chosen, 13)
        font_ui     = pygame.font.Font(chosen, 14)
        font_title_sm = pygame.font.Font(chosen, 11)
    else:
        font_btn    = pygame.font.SysFont(None, 20)
        font_status = pygame.font.SysFont(None, 17)
        font_info   = pygame.font.SysFont(None, 15)
        font_ui     = pygame.font.SysFont(None, 16)
        font_title_sm = pygame.font.SysFont(None, 13)

    # MIL state
    generator = MILGenerator()
    playback: Playback | None = None
    phf_tracker: PHFState | None = None

    status_text = "Select an archetype and click Generate & Play"
    info_text   = ""

    # --- UI State ---
    keys_list = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
    modes_list = ['Major', 'Minor']

    key_idx = 0
    mode_idx = 0
    bpm_text = "120"
    bars_text = "16"
    save_midi = False
    active_input = None
    archetype_idx = 0  # index into ARCHETYPE_NAMES
    pianist_idx = 0    # index into PIANIST_NAMES

    # --- UI Rectangles ---
    # Row 1: Key, Mode, BPM, Bars
    btn_key_rect  = pygame.Rect(CENTER_X - 220, BASE_Y, 90, 36)
    btn_mode_rect = pygame.Rect(CENTER_X - 110, BASE_Y, 100, 36)
    inp_bpm_rect  = pygame.Rect(CENTER_X + 10, BASE_Y, 90, 36)
    inp_bars_rect = pygame.Rect(CENTER_X + 120, BASE_Y, 90, 36)

    # Row 2: Archetype selector (wide)
    archetype_rect = pygame.Rect(CENTER_X - 160, ROW2_Y, 320, 36)

    # Row 3: Pianist selector (wide)
    pianist_rect = pygame.Rect(CENTER_X - 160, ROW3_Y, 320, 36)

    # Generate button
    btn_generate_rect = pygame.Rect(CENTER_X - BTN_WIDTH // 2,
                                    BTN_Y_NEW, BTN_WIDTH, BTN_HEIGHT)
    # MIDI checkbox
    chk_midi_rect = pygame.Rect(CENTER_X - 60, CHK_Y_NEW, 20, 20)

    running = True
    while running:
        dt = renderer.tick()

        mouse_pos = pygame.mouse.get_pos()
        btn_hovered = btn_generate_rect.collidepoint(mouse_pos)
        btn_clicking = False

        # --- Events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_l:
                    renderer.toggle_labels()
                elif event.key == pygame.K_o:
                    renderer.toggle_octaves()

                # Text input handling
                if active_input:
                    if event.key == pygame.K_BACKSPACE:
                        if active_input == 'bpm':
                            bpm_text = bpm_text[:-1]
                        elif active_input == 'bars':
                            bars_text = bars_text[:-1]
                    elif event.unicode.isdigit():
                        if active_input == 'bpm' and len(bpm_text) < 3:
                            bpm_text += event.unicode
                        elif active_input == 'bars' and len(bars_text) < 3:
                            bars_text += event.unicode

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if btn_key_rect.collidepoint(mouse_pos):
                    key_idx = (key_idx + 1) % len(keys_list)
                    active_input = None
                elif btn_mode_rect.collidepoint(mouse_pos):
                    mode_idx = (mode_idx + 1) % len(modes_list)
                    active_input = None
                elif inp_bpm_rect.collidepoint(mouse_pos):
                    active_input = 'bpm'
                elif inp_bars_rect.collidepoint(mouse_pos):
                    active_input = 'bars'
                elif archetype_rect.collidepoint(mouse_pos):
                    archetype_idx = (archetype_idx + 1) % len(ARCHETYPE_NAMES)
                    active_input = None
                elif pianist_rect.collidepoint(mouse_pos):
                    pianist_idx = (pianist_idx + 1) % len(PIANIST_NAMES)
                    active_input = None
                elif chk_midi_rect.collidepoint(mouse_pos):
                    save_midi = not save_midi
                    active_input = None
                elif event.button == 1 and btn_hovered:
                    active_input = None
                    btn_clicking = True

                    # Stop current playback
                    if playback and playback.active:
                        playback.active = False
                        engine.release_all_sustained()

                    status_text = "Composing..."
                    pygame.display.set_caption(
                        "MIL Concert Grand — Composing...")

                    # Parse inputs
                    bpm_val = max(40, min(240, int(bpm_text))) if bpm_text else 120
                    bars_val = max(4, min(128, int(bars_text))) if bars_text else 16
                    selected_mode = modes_list[mode_idx].lower()
                    selected_archetype = ARCHETYPE_NAMES[archetype_idx]
                    selected_pianist = PIANIST_NAMES[pianist_idx]

                    events = generator.generate(
                        num_bars=bars_val, key_root=key_idx,
                        bpm=bpm_val, scale_type=selected_mode,
                        archetype=selected_archetype,
                        pianist=selected_pianist,
                    )

                    # MIDI export
                    if save_midi:
                        timestamp = _time.strftime("%H%M%S")
                        key_name = (generator.last_key_name
                                    .replace("♯", "s").replace("♭", "b"))
                        filename = (f"mil_{key_name}_{generator.last_bpm}bpm"
                                    f"_{selected_archetype}_{timestamp}.mid")
                        midi_path = write_midi(events, filename,
                                               bpm=generator.last_bpm)
                        info_text = f"Saved → {os.path.basename(midi_path)}"
                    else:
                        info_text = ""

                    playback = Playback(events)
                    playback.start()

                    phf_tracker = PHFState(key_root=generator.last_key)

                    ts_label = generator.last_time_sig
                    status_text = (
                        f"Playing: {generator.last_key_name} {selected_mode}  "
                        f"| {generator.last_bpm} BPM  "
                        f"| {ts_label}  "
                        f"| {generator.last_num_bars} bars  "
                        f"| {selected_archetype}  "
                        f"| {selected_pianist}  "
                        f"| Form: {generator.last_form}"
                    )
                    pygame.display.set_caption(
                        f"MIL — {selected_archetype}: "
                        f"{generator.last_key_name} {selected_mode} "
                        f"@ {generator.last_bpm} BPM")

                elif event.button == 4:
                    engine.adjust_volume(VOLUME_STEP)
                elif event.button == 5:
                    engine.adjust_volume(-VOLUME_STEP)
                else:
                    active_input = None

        # --- Update playback ---
        display_pressed: set[int] = set()
        current_note_name = ""

        if playback and playback.active:
            display_pressed = playback.update(dt, engine)
            if display_pressed:
                highest = max(display_pressed)
                current_note_name = midi_to_note_name(highest)

            if phf_tracker and playback.event_idx > 0:
                idx = min(playback.event_idx - 1,
                          len(playback.events) - 1)
                ev = playback.events[idx]
                phf_tracker.step(ev.pitch)

        elif playback and not playback.active:
            selected_mode = modes_list[mode_idx].lower()
            status_text = (
                f"Done: {generator.last_key_name} {selected_mode}  "
                f"| {generator.last_bpm} BPM  "
                f"| {generator.last_num_bars} bars  "
                f"| {generator.last_archetype}"
            )

        # --- Render piano ---
        renderer.update_animations(display_pressed, dt)
        renderer.draw(
            white_keys=handler.white_keys,
            black_keys=handler.black_keys,
            pedal_states=[],
            master_volume=engine.master_volume,
            active_note_name=current_note_name,
            cursor_octave="",
        )

        # --- Draw UI Overlay ---
        # Row 1
        _draw_toggle(screen, btn_key_rect, font_ui,
                     f"Key: {keys_list[key_idx]}")
        _draw_toggle(screen, btn_mode_rect, font_ui,
                     f"Mode: {modes_list[mode_idx]}")
        _draw_text_input(screen, inp_bpm_rect, font_ui, "BPM:",
                         bpm_text, active_input == 'bpm')
        _draw_text_input(screen, inp_bars_rect, font_ui, "Bars:",
                         bars_text, active_input == 'bars')

        # Row 2: Archetype
        _draw_archetype(screen, archetype_rect, font_ui, font_title_sm,
                        ARCHETYPE_NAMES[archetype_idx])

        # Row 3: Pianist
        _draw_pianist(screen, pianist_rect, font_ui, font_title_sm,
                      PIANIST_NAMES[pianist_idx])

        # Generate button
        _draw_button(screen, btn_generate_rect, font_btn, btn_hovered,
                     btn_clicking,
                     is_playing=(playback is not None and playback.active))

        # MIDI checkbox
        _draw_checkbox(screen, chk_midi_rect, font_ui, save_midi,
                       "Save to MIDI")

        # Status
        _draw_status(screen, font_status, font_info, status_text, info_text)

        # Progress
        if playback:
            _draw_progress(screen, playback.progress)

        # Tension meter
        if phf_tracker and playback and playback.active:
            _draw_tension(screen, font_info, phf_tracker.uncertainty())

        pygame.display.flip()

    engine.stop()
    pygame.quit()
    sys.exit(0)


# ═══════════════════════════════════════════════════════════════
#  UI Drawing Helpers
# ═══════════════════════════════════════════════════════════════

def _draw_toggle(screen: pygame.Surface, rect: pygame.Rect,
                 font: pygame.font.Font, text: str) -> None:
    pygame.draw.rect(screen, (45, 40, 55), rect, border_radius=6)
    pygame.draw.rect(screen, (80, 75, 95), rect, 1, border_radius=6)
    txt_surf = font.render(text, True, (210, 205, 190))
    screen.blit(txt_surf, (rect.centerx - txt_surf.get_width() // 2,
                            rect.centery - txt_surf.get_height() // 2))


def _draw_text_input(screen: pygame.Surface, rect: pygame.Rect,
                     font: pygame.font.Font, label: str, val: str,
                     is_active: bool) -> None:
    bg_color = (60, 55, 75) if is_active else (35, 30, 45)
    border_color = (150, 140, 180) if is_active else (80, 75, 95)
    pygame.draw.rect(screen, bg_color, rect, border_radius=6)
    pygame.draw.rect(screen, border_color, rect, 1, border_radius=6)

    lbl_surf = font.render(label, True, (150, 145, 130))
    val_surf = font.render(val + ("_" if is_active else ""), True,
                           (230, 225, 210))
    screen.blit(lbl_surf, (rect.x + 8,
                            rect.centery - lbl_surf.get_height() // 2))
    screen.blit(val_surf, (rect.x + lbl_surf.get_width() + 14,
                            rect.centery - val_surf.get_height() // 2))


def _draw_archetype(screen: pygame.Surface, rect: pygame.Rect,
                    font: pygame.font.Font,
                    font_small: pygame.font.Font,
                    archetype: str) -> None:
    """Draw the archetype selector with character indicator."""
    # Background
    col = (48, 38, 62)
    border = (130, 110, 80)
    pygame.draw.rect(screen, col, rect, border_radius=8)
    pygame.draw.rect(screen, border, rect, 2, border_radius=8)

    # Label
    lbl = font_small.render("CHARACTER:", True, (150, 140, 120))
    screen.blit(lbl, (rect.x + 10, rect.centery - lbl.get_height() // 2))

    # Archetype name
    name_surf = font.render(archetype, True, (230, 210, 150))
    screen.blit(name_surf, (rect.x + lbl.get_width() + 20,
                             rect.centery - name_surf.get_height() // 2))

    # Click hint arrows
    arrow_l = font_small.render("◀", True, (100, 95, 80))
    arrow_r = font_small.render("▶", True, (100, 95, 80))
    screen.blit(arrow_r, (rect.right - 20,
                           rect.centery - arrow_r.get_height() // 2))


def _draw_pianist(screen: pygame.Surface, rect: pygame.Rect,
                  font: pygame.font.Font,
                  font_small: pygame.font.Font,
                  pianist: str) -> None:
    """Draw the pianist selector with performer indicator."""
    col = (38, 45, 62)
    border = (80, 120, 140)
    pygame.draw.rect(screen, col, rect, border_radius=8)
    pygame.draw.rect(screen, border, rect, 2, border_radius=8)

    lbl = font_small.render("PIANIST:", True, (120, 140, 155))
    screen.blit(lbl, (rect.x + 10, rect.centery - lbl.get_height() // 2))

    name_surf = font.render(pianist, True, (150, 210, 230))
    screen.blit(name_surf, (rect.x + lbl.get_width() + 20,
                             rect.centery - name_surf.get_height() // 2))

    arrow_r = font_small.render("▶", True, (100, 95, 80))
    screen.blit(arrow_r, (rect.right - 20,
                           rect.centery - arrow_r.get_height() // 2))


def _draw_checkbox(screen: pygame.Surface, rect: pygame.Rect,
                   font: pygame.font.Font, is_checked: bool,
                   label: str) -> None:
    pygame.draw.rect(screen, (35, 30, 45), rect, border_radius=4)
    pygame.draw.rect(screen, (80, 75, 95), rect, 2, border_radius=4)
    if is_checked:
        pygame.draw.line(screen, (200, 175, 100),
                         (rect.x + 4, rect.centery),
                         (rect.centerx - 1, rect.bottom - 4), 3)
        pygame.draw.line(screen, (200, 175, 100),
                         (rect.centerx - 1, rect.bottom - 4),
                         (rect.right - 4, rect.y + 4), 3)
    lbl_surf = font.render(label, True, (190, 185, 170))
    screen.blit(lbl_surf, (rect.right + 10,
                            rect.centery - lbl_surf.get_height() // 2))


def _draw_button(screen: pygame.Surface, rect: pygame.Rect,
                 font: pygame.font.Font, hovered: bool,
                 clicking: bool, is_playing: bool) -> None:
    color = (BTN_PRESS_COLOR if clicking
             else (BTN_HOVER_COLOR if hovered else BTN_COLOR))
    shadow = pygame.Rect(rect.x + 2, rect.y + 2, rect.w, rect.h)
    pygame.draw.rect(screen, (5, 4, 8), shadow, border_radius=10)
    pygame.draw.rect(screen, color, rect, border_radius=10)
    pygame.draw.rect(screen, BTN_BORDER, rect, 2, border_radius=10)

    if hovered:
        glow = pygame.Surface((rect.w + 8, rect.h + 8), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*BTN_BORDER, 30),
                         (0, 0, rect.w + 8, rect.h + 8), border_radius=12)
        screen.blit(glow, (rect.x - 4, rect.y - 4))

    label = "Generate New" if is_playing else "Generate & Play"
    txt = font.render(label, True, BTN_TEXT_COLOR)
    screen.blit(txt, (rect.centerx - txt.get_width() // 2,
                       rect.centery - txt.get_height() // 2))


def _draw_status(screen: pygame.Surface, font_main: pygame.font.Font,
                 font_sub: pygame.font.Font,
                 status: str, info: str) -> None:
    if status:
        txt = font_main.render(status, True, STATUS_COLOR)
        screen.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2,
                          STATUS_Y_NEW))
    if info:
        txt = font_sub.render(info, True, INFO_COLOR)
        screen.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2,
                          STATUS_Y_NEW + 22))


def _draw_progress(screen: pygame.Surface, progress: float) -> None:
    pygame.draw.rect(screen, PROG_BG,
                     (PROG_X, PROG_Y_NEW, PROG_W, PROG_H),
                     border_radius=2)
    fill_w = int(PROG_W * min(1.0, max(0.0, progress)))
    if fill_w > 0:
        pygame.draw.rect(screen, PROG_FG,
                         (PROG_X, PROG_Y_NEW, fill_w, PROG_H),
                         border_radius=2)


def _draw_tension(screen: pygame.Surface, font: pygame.font.Font,
                  energy: float) -> None:
    t = min(1.0, energy / 4.0)
    pygame.draw.rect(screen, TENSION_BG,
                     (TENSION_X, TENSION_Y_NEW, TENSION_W, TENSION_H),
                     border_radius=2)

    r = int(TENSION_LO[0] + (TENSION_HI[0] - TENSION_LO[0]) * t)
    g = int(TENSION_LO[1] + (TENSION_HI[1] - TENSION_LO[1]) * t)
    b = int(TENSION_LO[2] + (TENSION_HI[2] - TENSION_LO[2]) * t)

    fill_w = max(2, int(TENSION_W * t))
    pygame.draw.rect(screen, (r, g, b),
                     (TENSION_X, TENSION_Y_NEW, fill_w, TENSION_H),
                     border_radius=2)

    lbl = font.render("PHF Uncertainty", True, HUD_TEXT_DIM)
    screen.blit(lbl, (TENSION_X, TENSION_Y_NEW + TENSION_H + 3))

    val = font.render(f"{energy:.2f}", True, HUD_TEXT_DIM)
    screen.blit(val, (TENSION_X + TENSION_W - val.get_width(),
                       TENSION_Y_NEW + TENSION_H + 3))


if __name__ == "__main__":
    main()
