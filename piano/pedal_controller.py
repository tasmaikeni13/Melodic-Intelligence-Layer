"""
pedal_controller.py — Sustain, soft‑pedal, and sostenuto pedal logic.

Three pedals, modelled after a real concert grand:
    • Sustain  (right pedal / Spacebar)  — lifts all dampers; held notes
      continue ringing after key release.
    • Sostenuto (middle pedal / Right‑Ctrl) — captures notes currently
      sounding at the moment the pedal is pressed and sustains only those.
    • Soft / una‑corda (left pedal / Left‑Shift) — reduces volume and
      softens timbre by cutting higher harmonics.
"""

from __future__ import annotations
import pygame


class PedalController:
    """Track the state of the three piano pedals."""

    def __init__(self) -> None:
        self.sustain: bool   = False
        self.soft: bool      = False
        self.sostenuto: bool = False

        # Notes captured by the sostenuto pedal (frozen when pedal pressed)
        self.sostenuto_notes: set[int] = set()

    # ── public API ──────────────────────────────────────────────
    def update(self, keys_pressed: pygame.key.ScancodeWrapper,
               active_midi_notes: set[int]) -> None:
        """Called once per frame with the current keyboard state."""

        # --- Sustain (Spacebar) ---
        self.sustain = keys_pressed[pygame.K_SPACE]

        # --- Soft / una‑corda (Left Shift) ---
        self.soft = keys_pressed[pygame.K_LSHIFT]

        # --- Sostenuto (Right Ctrl) ---
        new_sost = keys_pressed[pygame.K_RCTRL]
        if new_sost and not self.sostenuto:
            # Capture currently sounding notes
            self.sostenuto_notes = set(active_midi_notes)
        if not new_sost:
            self.sostenuto_notes.clear()
        self.sostenuto = new_sost

    def should_sustain_note(self, midi_note: int) -> bool:
        """Return True if *midi_note* should keep ringing after release."""
        if self.sustain:
            return True
        if self.sostenuto and midi_note in self.sostenuto_notes:
            return True
        return False

    # ── for HUD display ─────────────────────────────────────────
    @property
    def states(self) -> list[tuple[str, bool]]:
        """Return pedal names and their on/off state for the HUD."""
        return [
            ("UNA CORDA",  self.soft),
            ("SOSTENUTO",  self.sostenuto),
            ("SUSTAIN",    self.sustain),
        ]
