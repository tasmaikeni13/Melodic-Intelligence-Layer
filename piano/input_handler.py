"""
input_handler.py — Mouse‑click detection and key‑to‑note mapping.

Builds click‑region rectangles for every key at startup, then provides
a fast lookup from any (x, y) screen position to the MIDI note under
the cursor.  Black keys are tested first because they visually overlap
white keys.
"""

from __future__ import annotations

import pygame
from config import (
    FIRST_MIDI, LAST_MIDI,
    KEYBOARD_Y, WHITE_KEY_WIDTH, WHITE_KEY_HEIGHT,
    BLACK_KEY_WIDTH, BLACK_KEY_HEIGHT, KEY_GAP,
    is_black_key,
)


# ═══════════════════════════════════════════════════════════════
#  Key‑layout data structure
# ═══════════════════════════════════════════════════════════════

class KeyInfo:
    """Geometry and identity of a single piano key."""
    __slots__ = ("midi_note", "is_black", "rect", "x", "y", "w", "h")

    def __init__(self, midi_note: int, is_blk: bool,
                 x: float, y: float, w: float, h: float) -> None:
        self.midi_note = midi_note
        self.is_black  = is_blk
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.rect = pygame.Rect(int(x), int(y), int(w), int(h))


def build_key_layout() -> tuple[list[KeyInfo], list[KeyInfo], list[KeyInfo]]:
    """Compute pixel rectangles for every key.

    Returns
    -------
    all_keys   – every KeyInfo, MIDI‑ordered
    white_keys – only white KeyInfo objects
    black_keys – only black KeyInfo objects
    """
    all_keys: list[KeyInfo]   = []
    white_keys: list[KeyInfo] = []
    black_keys: list[KeyInfo] = []

    wkw = WHITE_KEY_WIDTH
    wkh = WHITE_KEY_HEIGHT
    bkw = BLACK_KEY_WIDTH
    bkh = BLACK_KEY_HEIGHT

    white_index = 0

    for midi in range(FIRST_MIDI, LAST_MIDI + 1):
        if is_black_key(midi):
            # Black key centred on the boundary between its two neighbours
            cx = white_index * wkw
            x  = cx - bkw / 2.0
            ki = KeyInfo(midi, True, x, KEYBOARD_Y, bkw, bkh)
            all_keys.append(ki)
            black_keys.append(ki)
        else:
            x  = white_index * wkw
            ki = KeyInfo(midi, False, x, KEYBOARD_Y, wkw - KEY_GAP, wkh)
            all_keys.append(ki)
            white_keys.append(ki)
            white_index += 1

    return all_keys, white_keys, black_keys


# ═══════════════════════════════════════════════════════════════
#  InputHandler
# ═══════════════════════════════════════════════════════════════

class InputHandler:
    """Translates mouse events into MIDI note on/off messages."""

    def __init__(self) -> None:
        self.all_keys, self.white_keys, self.black_keys = build_key_layout()
        self._pressed_note: int | None = None   # currently held by mouse

    # ── public ──────────────────────────────────────────────────
    def key_at(self, pos: tuple[int, int]) -> int | None:
        """Return the MIDI note at screen position *pos*, or None."""
        # Check black keys first (they sit on top of white keys)
        for ki in self.black_keys:
            if ki.rect.collidepoint(pos):
                return ki.midi_note
        for ki in self.white_keys:
            if ki.rect.collidepoint(pos):
                return ki.midi_note
        return None

    def key_info_for(self, midi_note: int) -> KeyInfo | None:
        """Return the KeyInfo for a given MIDI note."""
        idx = midi_note - FIRST_MIDI
        if 0 <= idx < len(self.all_keys):
            return self.all_keys[idx]
        return None

    # ── mouse state tracking ────────────────────────────────────
    @property
    def currently_pressed(self) -> int | None:
        return self._pressed_note

    def on_mouse_down(self, pos: tuple[int, int]) -> int | None:
        """Returns MIDI note if a key was pressed, else None."""
        note = self.key_at(pos)
        self._pressed_note = note
        return note

    def on_mouse_up(self) -> int | None:
        """Returns the MIDI note that was released, then clears it."""
        note = self._pressed_note
        self._pressed_note = None
        return note

    def on_mouse_motion(self, pos: tuple[int, int],
                        buttons: tuple[int, ...]) -> tuple[int | None, int | None]:
        """Handle drag across keys.

        Returns (new_note, old_note) — *new_note* to trigger,
        *old_note* to release.  Either may be None.
        """
        if buttons[0]:  # left‑button held
            note = self.key_at(pos)
            if note != self._pressed_note:
                old = self._pressed_note
                self._pressed_note = note
                return note, old
        return None, None
