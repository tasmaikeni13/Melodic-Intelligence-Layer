"""
config.py — Central configuration for the Concert Grand Piano Simulator.

Contains all constants: tuning data, layout geometry, colours, audio
parameters, and window settings.  Every other module imports from here
so that tweaking a value in one place propagates everywhere.
"""

import numpy as np

# ═══════════════════════════════════════════════════════════════
#  Window / Display
# ═══════════════════════════════════════════════════════════════
SCREEN_WIDTH  = 1920
SCREEN_HEIGHT = 1080
FPS           = 60
TITLE         = "Concert Grand — 88 Keys"

# ═══════════════════════════════════════════════════════════════
#  Audio
# ═══════════════════════════════════════════════════════════════
SAMPLE_RATE    = 44100
BUFFER_SIZE    = 512          # frames per audio callback
AUDIO_CHANNELS = 2            # stereo
MAX_POLYPHONY  = 32
MASTER_VOLUME_DEFAULT = 0.55
VOLUME_STEP    = 0.05         # scroll‐wheel increment

# Reference pitch
A4_FREQ = 440.0

# ═══════════════════════════════════════════════════════════════
#  Keyboard geometry
# ═══════════════════════════════════════════════════════════════
NUM_KEYS       = 88
NUM_WHITE_KEYS = 52
FIRST_MIDI     = 21           # A0
LAST_MIDI      = 108          # C8

WHITE_KEY_WIDTH  = SCREEN_WIDTH / NUM_WHITE_KEYS    # ≈ 36.92 px
WHITE_KEY_HEIGHT = 255
BLACK_KEY_WIDTH  = WHITE_KEY_WIDTH * 0.60
BLACK_KEY_HEIGHT = WHITE_KEY_HEIGHT * 0.64

KEYBOARD_Y       = SCREEN_HEIGHT - WHITE_KEY_HEIGHT - 110
KEYBOARD_BOTTOM  = KEYBOARD_Y + WHITE_KEY_HEIGHT
REFLECTION_HEIGHT = 55
KEY_GAP          = 1           # px between white keys

# Animation
KEY_PRESS_DEPTH_WHITE = 5     # px downward shift on press
KEY_PRESS_DEPTH_BLACK = 4
KEY_ANIM_SPEED        = 18.0  # units/s  (1.0 = fully pressed)

# ═══════════════════════════════════════════════════════════════
#  Colours  (R, G, B)  or  (R, G, B, A)
# ═══════════════════════════════════════════════════════════════

# --- Background / stage ---
BG_TOP_COLOR    = (8, 6, 14)
BG_MID_COLOR    = (18, 14, 24)
BG_BOTTOM_COLOR = (10, 8, 16)
SPOTLIGHT_COLOR = (255, 225, 160)   # warm gold, used with low alpha

# --- White keys ---
WHITE_KEY_BASE       = (250, 247, 238)    # warm ivory
WHITE_KEY_PRESSED    = (230, 200, 120)    # amber highlight
WHITE_KEY_EDGE       = (210, 207, 198)    # subtle side shadow
WHITE_KEY_TOP_SHADE  = (235, 232, 224)    # darker at top (shadow from fallboard)

# --- Black keys ---
BLACK_KEY_BASE       = (18, 16, 14)       # deep ebony
BLACK_KEY_PRESSED    = (55, 45, 25)       # dark amber
BLACK_KEY_HIGHLIGHT  = (38, 35, 32)       # gloss streak
BLACK_KEY_BEVEL_LT   = (50, 47, 42)       # lighter bevel edge
BLACK_KEY_BEVEL_DK   = (8, 7, 6)          # darker bevel edge

# --- HUD ---
HUD_BG         = (12, 10, 18, 180)
HUD_TEXT       = (210, 205, 190)
HUD_TEXT_DIM   = (120, 115, 105)
PEDAL_ACTIVE   = (230, 190, 80)
PEDAL_INACTIVE = (55, 50, 45)
VOLUME_BAR_BG  = (40, 36, 50)
VOLUME_BAR_FG  = (200, 175, 100)

# --- Note labels ---
LABEL_COLOR        = (100, 95, 85)
LABEL_COLOR_C      = (180, 160, 100)     # C‐note markers
OCTAVE_LINE_COLOR  = (60, 55, 48, 120)

# ═══════════════════════════════════════════════════════════════
#  Note helpers
# ═══════════════════════════════════════════════════════════════
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
BLACK_PITCH_CLASSES = frozenset({1, 3, 6, 8, 10})   # C#, D#, F#, G#, A#


def is_black_key(midi_note: int) -> bool:
    """Return True if *midi_note* corresponds to a black key."""
    return (midi_note % 12) in BLACK_PITCH_CLASSES


def midi_to_note_name(midi_note: int) -> str:
    """Convert MIDI note number to human‑readable name, e.g. 'C#4'."""
    octave = (midi_note // 12) - 1
    return f"{NOTE_NAMES[midi_note % 12]}{octave}"


def midi_to_frequency(midi_note: int) -> float:
    """Equal‑temperament frequency for *midi_note* (A4 = 440 Hz)."""
    return A4_FREQ * (2.0 ** ((midi_note - 69) / 12.0))


# Pre‑computed lookup tables
FREQUENCIES = {m: midi_to_frequency(m) for m in range(FIRST_MIDI, LAST_MIDI + 1)}

# ═══════════════════════════════════════════════════════════════
#  Synthesis parameters (register‑dependent)
# ═══════════════════════════════════════════════════════════════
ATTACK_TIME  = 0.003       # seconds

RELEASE_TIME = 0.35        # seconds — note‑off fade

SOFT_PEDAL_VOLUME  = 0.70  # amplitude multiplier
SOFT_PEDAL_CUTOFF  = 0.6   # keep only this fraction of harmonics


def get_inharmonicity(midi_note: int) -> float:
    """Inharmonicity coefficient *B* — larger at extremes."""
    if midi_note < 40:
        return 0.00045 + (40 - midi_note) * 0.000035
    if midi_note > 80:
        return 0.00025 + (midi_note - 80) * 0.000025
    return 0.00012


def get_num_harmonics(midi_note: int) -> int:
    """How many partials to synthesise for a given note."""
    if midi_note < 48:
        return 22
    if midi_note < 72:
        return 16
    if midi_note < 90:
        return 10
    return 6


def get_decay_time(midi_note: int) -> float:
    """Decay‑time constant (seconds) — bass rings longer."""
    if midi_note < 36:
        return 10.0
    if midi_note < 52:
        return 7.0
    if midi_note < 68:
        return 4.5
    if midi_note < 84:
        return 2.8
    return 1.4


def get_harmonic_rolloff(midi_note: int) -> float:
    """Exponent *α* for 1/n^α harmonic amplitude scaling."""
    if midi_note < 48:
        return 0.70
    if midi_note < 84:
        return 1.00
    return 1.50


def get_stereo_pan(midi_note: int) -> float:
    """Return pan value in [‑1, 1].  Bass left, treble right."""
    return np.clip((midi_note - 64) / 50.0, -0.8, 0.8)


# ═══════════════════════════════════════════════════════════════
#  MIL — Generate Button & Playback UI
# ═══════════════════════════════════════════════════════════════

# --- Interactive UI Colors ---
UI_BG_INACTIVE   = (35, 30, 45)
UI_BG_ACTIVE     = (60, 55, 75)
UI_BORDER        = (80, 75, 95)
UI_BORDER_ACTIVE = (150, 140, 180)
UI_TEXT          = (210, 205, 190)
UI_TEXT_DIM      = (150, 145, 130)

# Generate button
BTN_WIDTH       = 260
BTN_HEIGHT      = 52
BTN_X           = SCREEN_WIDTH // 2 - BTN_WIDTH // 2
BTN_Y           = 300    # Moved down from 60 to the middle of the screen
BTN_COLOR       = (38, 32, 52)
BTN_HOVER_COLOR = (58, 48, 75)
BTN_PRESS_COLOR = (75, 62, 95)
BTN_TEXT_COLOR  = (230, 210, 150)
BTN_BORDER      = (110, 95, 65)

# Status / info text
STATUS_Y      = BTN_Y + BTN_HEIGHT + 50   # Increased spacing to fit the checkbox
STATUS_COLOR  = (190, 180, 145)
INFO_COLOR    = (140, 130, 110)

# Progress bar
PROG_Y  = STATUS_Y + 40   # Increased spacing from 28 to 40
PROG_W  = 360
PROG_H  = 5
PROG_X  = SCREEN_WIDTH // 2 - PROG_W // 2
PROG_BG = (35, 30, 45)
PROG_FG = (210, 185, 100)

# Tension meter (pH energy visualisation)
TENSION_X  = SCREEN_WIDTH // 2 - 180
TENSION_Y  = PROG_Y + 30  # Increased spacing from 20 to 30
TENSION_W  = 360
TENSION_H  = 4
TENSION_BG = (30, 25, 40)
TENSION_LO = (60, 130, 90)     # green = low tension
TENSION_HI = (200, 80, 60)     # red = high tension