"""
mil_engine.py — MIL: Character-Driven Hierarchical Piano Composition

Generates piano pieces through character-constrained top-down construction:

    Character → Form → Sections → Phrases → Harmony → Melody → Texture → Expression

The central innovation is the CHARACTER SPACE — a 5D vector (energy, darkness,
complexity, lyricism, volatility) that jointly biases every generative decision,
producing pieces with distinctive musical identity rather than generic correctness.

Six pillars of generation:

1.  CHARACTER SPACE (§2)
    Five dimensions jointly govern all parameters: tempo, metre, motif shape,
    harmonic vocabulary, rhythmic density, accompaniment, register, dynamics.
    Named archetypes (Nocturne, March, Waltz, etc.) are fixed points in this
    space, but any coordinate produces a coherent piece.

2.  HIERARCHICAL FORM (§3, §8)
    Pieces have formal structure (ABA', Rondo, etc.) with character offsets
    per section, producing contrast and narrative arc.

3.  SEED MOTIF AS RHYTHMIC-INTERVALLIC DNA (§4)
    A compact (interval, duration) sequence constrained by character.
    All melodic material derives from this motif via transformation:
    identity, inversion, retrograde, augmentation, diminution,
    fragmentation, and sequencing.

4.  GRAVITATIONAL HARMONY (§5)
    Functional chord progressions (T→P→D→T) with character-modulated
    enrichment: secondary dominants, borrowed chords, suspensions, pedal
    points. Complexity and darkness control harmonic vocabulary width.

5.  RHYTHMIC IDENTITY (§6)
    Time signatures (4/4, 3/4, 6/8) selected by character. Rhythm cells
    weighted by affinity to the character vector — not sampled uniformly.

6.  1/f EXPRESSIVE SURFACE (§10)
    Rubato and dynamics driven by Voss-McCartney pink noise, with
    magnitude scaled by character (more rubato for lyrical pieces,
    wider dynamics for volatile pieces).

Core classes:
    Character       — 5D character vector with archetype presets
    Pianist         — 6D pianist identity with performance parameters
    PinkNoise       — 1/f fractal noise generator
    SeedMotif       — rhythmic-intervallic motif with transformations
    ExpressionMap   — pink-noise rubato and dynamics
    ThematicMemory  — tracks transform recurrences
    FeedbackCorrector — self-listening analysis
    MILGenerator    — full character-driven hierarchical pipeline
    Playback        — time-second based player for rubato
    write_midi()    — MIDI file export
"""

from __future__ import annotations

import numpy as np
import random
import struct
import os
from dataclasses import dataclass, field

# ═══════════════════════════════════════════════════════════════
#  Musical Constants
# ═══════════════════════════════════════════════════════════════

NOTE_NAMES = ['C', 'C♯', 'D', 'E♭', 'E', 'F', 'F♯', 'G', 'A♭', 'A', 'B♭', 'B']

SCALES = {
    'major': [0, 2, 4, 5, 7, 9, 11],
    'minor': [0, 2, 3, 5, 7, 8, 10],
}

# Chord quality templates (intervals from root)
CHORD_MAJ  = [0, 4, 7]
CHORD_MIN  = [0, 3, 7]
CHORD_DIM  = [0, 3, 6]
CHORD_DOM7 = [0, 4, 7, 10]
CHORD_AUG  = [0, 4, 8]

# Diatonic chords for each scale type
MAJOR_CHORDS = {
    0: CHORD_MAJ, 2: CHORD_MIN, 4: CHORD_MIN, 5: CHORD_MAJ,
    7: CHORD_MAJ, 9: CHORD_MIN, 11: CHORD_DIM
}
MINOR_CHORDS = {
    0: CHORD_MIN, 2: CHORD_DIM, 3: CHORD_MAJ, 5: CHORD_MIN,
    7: CHORD_MAJ, 8: CHORD_MAJ, 10: CHORD_MAJ
}

MAJOR_DEGREES = [0, 2, 4, 5, 7, 9, 11]
MINOR_DEGREES = [0, 2, 3, 5, 7, 8, 10]

# Harmonic transition matrices (§5.3)
MAJOR_TRANSITIONS = np.array([
    [0.00, 0.18, 0.05, 0.28, 0.25, 0.18, 0.06],
    [0.05, 0.00, 0.00, 0.10, 0.60, 0.00, 0.25],
    [0.05, 0.10, 0.00, 0.50, 0.05, 0.30, 0.00],
    [0.12, 0.10, 0.00, 0.00, 0.55, 0.03, 0.20],
    [0.65, 0.03, 0.05, 0.05, 0.00, 0.17, 0.05],
    [0.05, 0.28, 0.10, 0.40, 0.12, 0.00, 0.05],
    [0.72, 0.00, 0.10, 0.03, 0.10, 0.05, 0.00],
], dtype=np.float64)

MINOR_TRANSITIONS = np.array([
    [0.00, 0.10, 0.20, 0.15, 0.25, 0.20, 0.10],
    [0.05, 0.00, 0.10, 0.10, 0.55, 0.00, 0.20],
    [0.10, 0.10, 0.00, 0.40, 0.10, 0.25, 0.05],
    [0.10, 0.10, 0.00, 0.00, 0.55, 0.05, 0.20],
    [0.65, 0.03, 0.05, 0.05, 0.00, 0.17, 0.05],
    [0.05, 0.15, 0.20, 0.40, 0.15, 0.00, 0.05],
    [0.70, 0.00, 0.10, 0.05, 0.10, 0.05, 0.00],
], dtype=np.float64)

# Accompaniment pattern names
ACCOMP_PATTERNS = ['alberti', 'arpeggiated', 'block', 'waltz', 'stride', 'tremolo']

# Groove templates for micro-timing
GROOVE_TEMPLATES = {
    # 3/4 grooves (offsets in beats for beats 0, 1, 2)
    'waltz':     [0.0, -0.05, +0.03],
    'mazurka':   [0.0, +0.08, +0.04],
    'polonaise': [0.0, -0.02, +0.05],
    # 4/4 grooves (offsets for beats 0, 1, 2, 3)
    'march':     [-0.02, 0.0, -0.02, 0.0],
    'toccata':   [-0.01, +0.01, -0.01, +0.01],
    'swing':     [0.0, +0.06, 0.0, +0.06],
    # 6/8 grooves (offsets for compound beats 0, 1, 2)
    'barcarolle': [0.0, +0.03, +0.05],
    'tarantella': [-0.02, 0.0, -0.02],
    # Default
    'neutral':   [0.0, 0.0, 0.0, 0.0],
}


# ═══════════════════════════════════════════════════════════════
#  Character Space (§2)
# ═══════════════════════════════════════════════════════════════

@dataclass
class Character:
    """5D character vector defining musical identity."""
    energy: float = 0.5       # 0=slow/soft/sparse  1=fast/loud/dense
    darkness: float = 0.5     # 0=major/bright      1=minor/chromatic
    complexity: float = 0.5   # 0=simple             1=elaborate
    lyricism: float = 0.5     # 0=percussive         1=singing/flowing
    volatility: float = 0.5   # 0=steady             1=unpredictable

    def as_array(self) -> np.ndarray:
        return np.array([self.energy, self.darkness, self.complexity,
                         self.lyricism, self.volatility])

    def offset(self, delta: tuple) -> 'Character':
        """Return new Character with delta added and clamped to [0,1]."""
        a = self.as_array() + np.array(delta)
        a = np.clip(a, 0.0, 1.0)
        return Character(*a.tolist())

    # ── Derived parameters (§2.3) ──

    @property
    def bpm_base(self) -> float:
        return 58.0 + self.energy * 120.0 + self.volatility * 20.0

    @property
    def time_signature(self) -> str:
        # High lyricism + low energy → compound flowing (6/8)
        if self.lyricism > 0.65 and self.energy < 0.45:
            return '6/8'
        # Very high energy + very low lyricism → could be 6/8 tarantella
        # (fast dance in compound time)
        if self.energy > 0.85 and self.lyricism < 0.20 and self.darkness < 0.35:
            return '6/8'
        # Moderate lyricism + moderate energy → triple metre (3/4)
        if self.lyricism > 0.5 and self.energy < 0.55:
            return '3/4'
        # High energy + low lyricism + moderate dark → could be 3/4 scherzo
        if self.energy > 0.7 and self.lyricism < 0.25 and self.volatility > 0.6:
            return '3/4'
        return '4/4'

    @property
    def beats_per_bar(self) -> float:
        ts = self.time_signature
        if ts == '3/4':
            return 3.0
        elif ts == '6/8':
            return 3.0  # 3 compound beats
        return 4.0

    @property
    def max_interval(self) -> int:
        return 2 + int(self.complexity * 4 + self.energy * 2)

    @property
    def step_probability(self) -> float:
        return max(0.45, 0.85 - self.complexity * 0.35)

    @property
    def secondary_dominant_prob(self) -> float:
        return self.complexity * 0.15 + self.darkness * 0.08

    @property
    def borrowed_chord_prob(self) -> float:
        return self.darkness * 0.12 + self.volatility * 0.08

    @property
    def suspension_prob(self) -> float:
        return self.lyricism * 0.15 + self.complexity * 0.08

    @property
    def rubato_magnitude(self) -> float:
        return 0.04 + self.lyricism * 0.06 + (1.0 - self.energy) * 0.02

    @property
    def dynamic_magnitude(self) -> float:
        return 10.0 + self.volatility * 15.0 + self.energy * 8.0

    @property
    def melody_centre(self) -> int:
        return int(72 - self.darkness * 8 + self.energy * 4)

    @property
    def base_velocity(self) -> int:
        return int(45 + self.energy * 40)

    @property
    def harmonic_color_index(self) -> float:
        """Composite harmonic color: how dark and complex the harmony should be."""
        return self.darkness * 0.5 + self.complexity * 0.5

    @property
    def neapolitan_prob(self) -> float:
        H = self.harmonic_color_index
        return max(0, (H - 0.5)) * 0.15

    @property
    def augmented_sixth_prob(self) -> float:
        H = self.harmonic_color_index
        return max(0, (H - 0.55)) * 0.12

    @property
    def chromatic_mediant_prob(self) -> float:
        H = self.harmonic_color_index
        return max(0, (H - 0.65)) * 0.10

    @property
    def tritone_sub_prob(self) -> float:
        H = self.harmonic_color_index
        return max(0, (H - 0.75)) * 0.08

    def accomp_weights(self, metre: str) -> dict[str, float]:
        """Return probability weights for each accompaniment pattern."""
        w = {
            'alberti':    self.lyricism * 0.6 + (1 - self.energy) * 0.2,
            'arpeggiated': self.lyricism * 0.8 + (1 - self.energy) * 0.1,
            'block':      (1 - self.lyricism) * 0.5 + self.energy * 0.3,
            'waltz':      (0.7 if metre == '3/4' else 0.05) + self.lyricism * 0.15,
            'stride':     self.energy * 0.4 + (1 - self.lyricism) * 0.3,
            'tremolo':    self.volatility * 0.3 + self.darkness * 0.2 + self.energy * 0.2,
        }
        # Ensure all positive
        for k in w:
            w[k] = max(0.01, w[k])
        return w


# ── Pianist Identity (§1) ──

@dataclass
class Pianist:
    """6D pianist identity defining performance style."""
    rubato_freedom: float = 0.5
    attack_profile: float = 0.5
    pedal_saturation: float = 0.5
    dynamic_exaggeration: float = 0.5
    voice_highlighting: float = 0.5
    ornamental_impulse: float = 0.5

    def as_array(self) -> np.ndarray:
        return np.array([self.rubato_freedom, self.attack_profile,
                         self.pedal_saturation, self.dynamic_exaggeration,
                         self.voice_highlighting, self.ornamental_impulse])

    @property
    def rubato_scale(self) -> float:
        return 0.5 + self.rubato_freedom * 1.5

    @property
    def attack_sharpness(self) -> float:
        return self.attack_profile * 0.3

    @property
    def pedal_density(self) -> float:
        return 0.2 + self.pedal_saturation * 0.6

    @property
    def dynamic_range_mult(self) -> float:
        return 0.6 + self.dynamic_exaggeration * 0.8

    @property
    def soprano_bias(self) -> float:
        return self.voice_highlighting * 15

    @property
    def ornament_prob(self) -> float:
        return self.ornamental_impulse * 0.25


PIANISTS = {
    'Horowitz':     Pianist(0.55, 0.85, 0.45, 0.90, 0.78, 0.40),
    'Rubinstein':   Pianist(0.62, 0.32, 0.58, 0.65, 0.48, 0.22),
    'Glenn Gould':  Pianist(0.12, 0.72, 0.08, 0.55, 0.62, 0.08),
    'Rachmaninoff': Pianist(0.68, 0.48, 0.62, 0.85, 0.30, 0.28),
    'Argerich':     Pianist(0.42, 0.75, 0.30, 0.92, 0.55, 0.18),
    'Brendel':      Pianist(0.42, 0.28, 0.52, 0.45, 0.42, 0.15),
    'Cortot':       Pianist(0.92, 0.22, 0.68, 0.72, 0.55, 0.62),
    'Richter':      Pianist(0.35, 0.68, 0.52, 0.80, 0.28, 0.12),
    'Liszt':        Pianist(0.72, 0.82, 0.55, 0.95, 0.72, 0.78),
    'Chopin':       Pianist(0.78, 0.28, 0.62, 0.62, 0.68, 0.82),
}

PIANIST_NAMES = ['Neutral'] + list(PIANISTS.keys())


# ── Named Archetypes ──
#
# Each archetype is a point in 5D Character Space:
#   (energy, darkness, complexity, lyricism, volatility)
#
# Design principles:
#   - Every archetype must be ≥0.30 Euclidean distance from every other
#   - Each fills a genuine musical tradition with a distinct feel
#   - Dimensions are set to produce the right tempo, metre, density,
#     harmonic vocabulary, and textural pattern for that tradition
#
# The archetypes below are organised into families:
#
#   Lyrical/Gentle:   Nocturne, Barcarolle, Lullaby
#   Dance:            Waltz, Polonaise, Tarantella
#   Dramatic/Dark:    Ballade, Scherzo, Elegy
#   Virtuosic:        Étude, Toccata
#   Free/Volatile:    Rhapsody, Fantasia
#   Structured:       March, Prelude
#   New Archetypes:   Impromptu, Mazurka, Berceuse, Arabesque, Sonata

ARCHETYPES: dict[str, Character] = {
    # ── Lyrical / Gentle ──
    'Nocturne':    Character(0.20, 0.40, 0.30, 0.92, 0.18),
    #  Night music. Singing melody over gentle arpeggiated accompaniment.
    #  Chopin Op.9, Op.27, Op.48. Slow, lyrical, 6/8, moderate darkness.

    'Barcarolle':  Character(0.28, 0.15, 0.48, 0.82, 0.10),
    #  Venetian boat song. Rocking 6/8, ornamental melody, BRIGHT.
    #  Chopin Op.60, Mendelssohn. Key difference from Nocturne: much brighter
    #  (darkness 0.15 vs 0.40), more ornamental (complexity 0.48 vs 0.30).

    'Lullaby':     Character(0.08, 0.15, 0.10, 0.75, 0.05),
    #  Soothing, minimal, rocking. The sparsest archetype.
    #  Brahms Wiegenlied. Very low energy, very simple, very steady.
    #  Now properly differentiated from Nocturne (was 0.250 apart, now 0.333).

    # ── Dance ──
    'Waltz':       Character(0.45, 0.28, 0.30, 0.70, 0.20),
    #  Graceful triple-metre dance. 3/4.
    #  Chopin waltzes, Strauss. Moderate energy, bright, flowing.

    'Polonaise':   Character(0.70, 0.48, 0.52, 0.22, 0.30),
    #  Stately, majestic Polish dance. Powerful, rhythmic, not lyrical.
    #  Chopin Op.53 "Heroic". High energy but dignified, moderate darkness.

    'Tarantella':  Character(0.93, 0.25, 0.58, 0.12, 0.48),
    #  Frantic Italian dance in 6/8. Wild, breathless, bright.
    #  Liszt, Rossini, Chopin Op.43. Maximum speed, percussive.

    # ── Dramatic / Dark ──
    'Ballade':     Character(0.40, 0.62, 0.55, 0.80, 0.65),
    #  Narrative, emotionally wide. Dark but singing. Dramatic arc.
    #  Chopin Ballades. The most volatile of the lyrical archetypes.

    'Scherzo':     Character(0.80, 0.62, 0.68, 0.18, 0.72),
    #  Fast, dark, angular, volatile. Demonic energy with sudden shifts.
    #  Chopin Scherzos, Beethoven. Fills the critical "high energy + dark" gap.

    'Elegy':       Character(0.15, 0.78, 0.42, 0.72, 0.22),
    #  Slow, mournful, deeply dark. Singing through grief.
    #  Rachmaninoff Elegie, Chopin Marche Funèbre. Fills "dark + lyrical" gap.

    # ── Virtuosic ──
    'Étude':       Character(0.75, 0.35, 0.88, 0.45, 0.30),
    #  Technical study. Relentless, complex, moderate lyricism.
    #  Chopin Op.10/Op.25, Liszt Transcendental. High complexity is key.

    'Toccata':     Character(0.95, 0.48, 0.82, 0.05, 0.42),
    #  Perpetual motion. Maximum density, minimum lyricism.
    #  Prokofiev Op.11, Bach. Pushed to 0.95 energy for denser rhythm cells.

    # ── Free / Volatile ──
    'Rhapsody':    Character(0.65, 0.45, 0.60, 0.62, 0.85),
    #  Improvisatory, unpredictable, passionate. Wide emotional range.
    #  Liszt Hungarian Rhapsodies, Gershwin. Highest volatility family.

    'Fantasia':    Character(0.45, 0.58, 0.80, 0.35, 0.92),
    #  Free-form, maximally unpredictable. Complex + volatile.
    #  Mozart K.475, Chopin Op.49. Different from Rhapsody: less energy,
    #  more complexity, even higher volatility.

    # ── Structured ──
    'March':       Character(0.82, 0.20, 0.35, 0.10, 0.25),
    #  Military/ceremonial. Driving, rhythmic, bold, bright.
    #  Mozart Turkish March, Prokofiev. 4/4, percussive, steady.

    'Prelude':     Character(0.42, 0.45, 0.45, 0.52, 0.38),
    #  Concentrated musical idea. The most "neutral" archetype — moderate
    #  in all dimensions. Can go anywhere. Fills the "moderate everything" gap.
    #  Chopin Preludes Op.28 (collectively), Bach WTC.

    # ── New Archetypes (§2.2) ──
    'Impromptu':   Character(0.55, 0.18, 0.60, 0.68, 0.52),
    #  Seemingly spontaneous, bright, ornamental, moderately volatile.

    'Mazurka':     Character(0.60, 0.25, 0.38, 0.32, 0.40),
    #  Polish folk dance. Bright, rhythmic, moderately complex.

    'Berceuse':    Character(0.05, 0.35, 0.62, 0.88, 0.05),
    #  Cradle song. Extremely slow, very lyrical, ornamental, steady.

    'Arabesque':   Character(0.32, 0.08, 0.72, 0.62, 0.25),
    #  Ornamental, bright, complex but not intense. Flowing.

    'Sonata':      Character(0.62, 0.55, 0.72, 0.48, 0.60),
    #  Formal structure, moderate darkness, high complexity, balanced volatility.
}

ARCHETYPE_NAMES = ['Random'] + list(ARCHETYPES.keys())


def random_character() -> Character:
    """Sample a random point in character space."""
    return Character(
        energy=random.uniform(0.1, 0.9),
        darkness=random.uniform(0.1, 0.9),
        complexity=random.uniform(0.1, 0.9),
        lyricism=random.uniform(0.1, 0.9),
        volatility=random.uniform(0.1, 0.9),
    )


# ═══════════════════════════════════════════════════════════════
#  MIL Event
# ═══════════════════════════════════════════════════════════════

@dataclass
class MILEvent:
    pitch: int
    duration_beats: float
    velocity: int
    beat_position: float
    time_seconds: float = 0.0
    duration_seconds: float = 0.0


# ═══════════════════════════════════════════════════════════════
#  Hierarchical Planning Structures
# ═══════════════════════════════════════════════════════════════

@dataclass
class Section:
    key_root: int
    scale_type: str
    start_bar: int
    num_bars: int
    is_return: bool
    role: str                  # 'A', 'B', 'C', 'A_prime'
    dynamic_base: float
    char_offset: tuple = (0.0, 0.0, 0.0, 0.0, 0.0)

@dataclass
class Phrase:
    start_bar: int
    num_bars: int
    cadence_type: str          # 'half' or 'authentic'
    motif_transform: str
    is_consequent: bool


# ═══════════════════════════════════════════════════════════════
#  1/f Pink Noise (Voss-McCartney)
# ═══════════════════════════════════════════════════════════════

class PinkNoise:
    """1/f fractal noise with long-range correlations."""
    def __init__(self, octaves: int = 6) -> None:
        self.octaves = octaves
        self.state = np.random.randn(octaves) * 0.5
        self.counter = 0

    def step(self) -> float:
        self.counter += 1
        c = self.counter
        zeros = 0
        while c > 0 and (c & 1) == 0:
            zeros += 1
            c >>= 1
        idx = min(zeros, self.octaves - 1)
        self.state[idx] = np.random.randn() * 0.5
        return float(np.sum(self.state) / self.octaves)


# ═══════════════════════════════════════════════════════════════
#  Thematic Memory (§7)
# ═══════════════════════════════════════════════════════════════

class ThematicMemory:
    """Tracks motif transformations for recall bias."""

    def __init__(self, volatility: float) -> None:
        self.occurrences: dict[str, list[float]] = {}
        self.lambda_base = 0.08
        self.theta = 0.6 - volatility * 0.3

    def record(self, transform: str, beat: float) -> None:
        """Record a transform at a beat position."""
        if transform not in self.occurrences:
            self.occurrences[transform] = []
        self.occurrences[transform].append(beat)

    def recall_pressure(self, beat: float) -> float:
        """Pressure to repeat a previously used transform."""
        if not self.occurrences:
            return 0.0
        max_pressure = 0.0
        for transform, beats in self.occurrences.items():
            if beats:
                t_last = beats[-1]
                n_recalls = len(beats)
                lam = self.lambda_base / max(1, n_recalls * 0.5)
                familiarity = np.exp(-lam * (beat - t_last))
                pressure = max(0, self.theta - familiarity)
                max_pressure = max(max_pressure, pressure)
        return max_pressure

    def should_recall(self, beat: float) -> bool:
        """Should we bias toward identity/fragment transform?"""
        return self.recall_pressure(beat) > 0.15


# ═══════════════════════════════════════════════════════════════
#  Feedback Corrector (§8)
# ═══════════════════════════════════════════════════════════════

class FeedbackCorrector:
    """Self-listening analysis and dynamic correction."""

    def __init__(self, char: Character, alpha: float = 0.3) -> None:
        self.alpha = alpha
        self.target_range = 8 + char.energy * 8 + char.complexity * 4
        self.target_velocity = char.base_velocity
        self.target_density = 1.0 + char.energy * 2.0 + char.complexity * 1.5
        self.corrections = np.zeros(3)

    def analyze_phrase(self, events: list[MILEvent]) -> None:
        """Analyze melody and compute corrections."""
        if not events:
            return
        pitches = [e.pitch for e in events]
        actual_range = max(pitches) - min(pitches)
        actual_vel = np.mean([e.velocity for e in events])
        total_beats = sum(e.duration_beats for e in events)
        actual_density = (len(events) / max(0.1, total_beats)
                          if total_beats > 0 else 1.0)

        errors = np.array([
            actual_range - self.target_range,
            actual_vel - self.target_velocity,
            actual_density - self.target_density,
        ])
        self.corrections = -self.alpha * errors

    @property
    def range_correction(self) -> float:
        return float(self.corrections[0])

    @property
    def velocity_correction(self) -> float:
        return float(self.corrections[1])

    @property
    def density_correction(self) -> float:
        return float(self.corrections[2])


# ═══════════════════════════════════════════════════════════════
#  Seed Motif — Rhythmic-Intervallic DNA (§4)
# ═══════════════════════════════════════════════════════════════

class SeedMotif:
    """Character-constrained rhythmic-intervallic motif with transformations."""

    def __init__(self, intervals: list[int] | None = None,
                 durations: list[float] | None = None,
                 character: Character | None = None,
                 beats_per_bar: float = 4.0) -> None:
        if intervals is not None and durations is not None:
            self.intervals = intervals
            self.durations = durations
        else:
            char = character or Character()
            self.intervals, self.durations = self._generate(char, beats_per_bar)

    def _generate(self, char: Character, bpb: float) -> tuple[list[int], list[float]]:
        """Generate a seed motif constrained by character."""
        max_iv = char.max_interval
        p_step = char.step_probability
        p_short = 0.3 + char.energy * 0.4 + char.complexity * 0.15
        p_dot = char.lyricism * 0.25 + (1.0 - char.energy) * 0.10

        for _ in range(200):
            length = random.randint(3, 5)
            intervals: list[int] = []
            durations: list[float] = []
            remaining = bpb

            for j in range(length):
                # ── Interval ──
                if j == 0:
                    if random.random() < p_step:
                        iv = random.choice([-2, -1, 1, 2])
                    else:
                        iv = random.choice(
                            [i for i in range(-max_iv, max_iv + 1) if i != 0])
                elif abs(intervals[-1]) >= 4:
                    # After leap, step in contrary direction
                    direction = -1 if intervals[-1] > 0 else 1
                    iv = direction * random.choice([1, 2])
                else:
                    if random.random() < p_step:
                        iv = random.choice([-2, -1, 1, 2])
                    else:
                        choices = [i for i in range(-max_iv, max_iv + 1) if i != 0]
                        iv = random.choice(choices) if choices else random.choice([-1, 1])
                intervals.append(iv)

                # ── Duration ──
                if j == length - 1:
                    dur = max(0.25, remaining)
                else:
                    min_remaining = 0.25 * (length - j - 1)
                    available = remaining - min_remaining
                    if random.random() < p_short:
                        dur = random.choice([0.25, 0.5])
                    elif random.random() < p_dot:
                        dur = random.choice([0.75, 1.5])
                    else:
                        dur = random.choice([0.5, 1.0])
                    dur = min(dur, available)
                    dur = max(0.25, dur)
                durations.append(dur)
                remaining -= dur
                if remaining <= 0:
                    break

            # Validate
            if len(intervals) < 3:
                continue
            has_up = any(i > 0 for i in intervals)
            has_down = any(i < 0 for i in intervals)
            has_step = sum(1 for i in intervals if abs(i) <= 2) >= len(intervals) // 2
            has_variety = len(set(abs(i) for i in intervals)) >= 2

            if has_up and has_down and has_step and has_variety:
                return intervals, durations

        return [2, -1, 3, -2], [1.0, 1.0, 1.0, 1.0]

    # ── Transformations (§4.3) ──

    def identity(self) -> tuple[list[int], list[float]]:
        return self.intervals[:], self.durations[:]

    def inversion(self) -> tuple[list[int], list[float]]:
        return [-iv for iv in self.intervals], self.durations[:]

    def retrograde(self) -> tuple[list[int], list[float]]:
        return self.intervals[::-1], self.durations[::-1]

    def retrograde_inversion(self) -> tuple[list[int], list[float]]:
        return [-iv for iv in reversed(self.intervals)], self.durations[::-1]

    def fragment(self, length: int = 2) -> tuple[list[int], list[float]]:
        n = min(length, len(self.intervals))
        return self.intervals[:n], self.durations[:n]

    def sequence(self, shift: int = 0) -> tuple[list[int], list[float]]:
        result = self.intervals[:]
        if result:
            result[0] += shift
        return result, self.durations[:]

    def augmented(self) -> tuple[list[int], list[float]]:
        return self.intervals[:], [d * 2 for d in self.durations]

    def diminished(self) -> tuple[list[int], list[float]]:
        return self.intervals[:], [max(0.25, d * 0.5) for d in self.durations]

    def get_transform(self, name: str) -> tuple[list[int], list[float]]:
        transforms = {
            'identity': self.identity,
            'inversion': self.inversion,
            'retrograde': self.retrograde,
            'retro_inv': self.retrograde_inversion,
            'fragment': lambda: self.fragment(2),
            'sequence_up': lambda: self.sequence(2),
            'sequence_down': lambda: self.sequence(-2),
            'augmented': self.augmented,
            'diminished': self.diminished,
        }
        fn = transforms.get(name, self.identity)
        return fn()


# ═══════════════════════════════════════════════════════════════
#  Rhythm Cells — Character-Weighted (§6)
# ═══════════════════════════════════════════════════════════════

# Each cell: (durations, energy_affinity, lyricism_affinity, complexity_affinity)
CELLS_4_4 = [
    # (durations,                       energy, lyricism, complexity)
    ([1.0, 1.0, 1.0, 1.0],              0.3,    0.3,      0.1),   # simple quarters
    ([2.0, 2.0],                         0.15,   0.8,      0.1),   # sustained halves
    ([2.0, 1.0, 1.0],                   0.35,   0.5,      0.2),   # long-short-short
    ([1.0, 1.0, 2.0],                   0.3,    0.5,      0.2),   # short-short-long
    ([1.5, 0.5, 1.0, 1.0],              0.5,    0.3,      0.4),   # dotted
    ([0.5, 0.5, 0.5, 0.5, 2.0],         0.65,   0.2,      0.5),   # run into long
    ([0.5, 0.5, 1.0, 1.0, 1.0],         0.55,   0.3,      0.4),   # eighth pickup
    ([0.5, 0.5, 0.5, 0.5, 1.0, 1.0],    0.75,   0.2,      0.6),   # running eighths
    ([1.0, 0.5, 0.5, 1.0, 1.0],         0.5,    0.4,      0.3),   # mixed
    # ── Fast cells for Toccata / Étude / Scherzo ──
    ([0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
                                         0.85,   0.1,      0.7),   # all eighths
    ([0.25, 0.25, 0.25, 0.25, 0.5, 0.5, 0.5, 0.5, 1.0],
                                         0.9,    0.1,      0.8),   # 16ths → 8ths → quarter
    ([0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 1.0, 1.0],
                                         0.95,   0.05,     0.85),  # 16th run + halves
    ([0.25, 0.25, 0.5, 0.25, 0.25, 0.5, 1.0, 1.0],
                                         0.88,   0.1,      0.75),  # grouped 16ths
]

CELLS_3_4 = [
    ([1.0, 1.0, 1.0],                   0.35,   0.4,    0.1),   # simple waltz
    ([2.0, 1.0],                         0.2,    0.7,    0.1),   # sustained
    ([1.0, 2.0],                         0.25,   0.6,    0.2),   # pickup feel
    ([1.5, 1.5],                         0.3,    0.5,    0.3),   # hemiola hint
    ([0.5, 0.5, 1.0, 1.0],              0.6,    0.3,    0.4),   # running
    ([1.0, 0.5, 0.5, 1.0],              0.5,    0.3,    0.4),   # mixed
    ([0.5, 0.5, 0.5, 0.5, 1.0],         0.7,    0.2,    0.5),   # fast
    # ── Fast cells for Polonaise / Scherzo in 3/4 ──
    ([0.5, 0.5, 0.5, 0.5, 0.5, 0.5],   0.8,    0.15,   0.6),   # all eighths
    ([0.25, 0.25, 0.25, 0.25, 0.5, 0.5, 1.0],
                                         0.85,   0.1,    0.7),   # 16ths → 8ths
]

CELLS_6_8 = [
    ([1.5, 1.5],                         0.15,   0.85,   0.1),   # compound halves
    ([1.0, 0.5, 1.0, 0.5],              0.3,    0.7,    0.2),   # lilting
    ([0.5, 0.5, 0.5, 0.5, 0.5, 0.5],   0.65,   0.3,    0.5),   # full running 8ths
    ([1.0, 0.5, 1.5],                   0.25,   0.6,    0.3),   # mixed compound
    ([0.5, 1.0, 0.5, 1.0],              0.4,    0.5,    0.3),   # syncopated
    # ── Fast cells for Tarantella ──
    ([0.25, 0.25, 0.25, 0.25, 0.5, 0.5, 0.5, 0.5],
                                         0.85,   0.15,   0.65),  # 16ths → 8ths
    ([0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.5, 0.5],
                                         0.92,   0.08,   0.8),   # frantic 16ths
    ([0.5, 0.5, 0.5, 0.25, 0.25, 0.5, 0.5],
                                         0.75,   0.2,    0.55),  # mixed fast
]


def _select_rhythm_cell(char: Character, metre: str) -> list[float]:
    """Sample a rhythm cell weighted by character affinity."""
    if metre == '3/4':
        cells = CELLS_3_4
    elif metre == '6/8':
        cells = CELLS_6_8
    else:
        cells = CELLS_4_4

    alpha = 3.0
    weights = []
    for durations, e_aff, l_aff, x_aff in cells:
        dist = ((e_aff - char.energy) ** 2
                + (l_aff - char.lyricism) ** 2
                + (x_aff - char.complexity) ** 2)
        weights.append(np.exp(-alpha * dist))

    total = sum(weights)
    if total <= 0:
        return cells[0][0]
    r = random.random() * total
    cumul = 0.0
    for i, w in enumerate(weights):
        cumul += w
        if r <= cumul:
            return list(cells[i][0])
    return list(cells[-1][0])


def _select_groove(archetype: str, metre: str) -> list[float]:
    """Select and adapt groove template based on archetype."""
    mapping = {
        'Waltz': 'waltz', 'Mazurka': 'mazurka', 'Polonaise': 'polonaise',
        'March': 'march', 'Toccata': 'toccata',
        'Barcarolle': 'barcarolle', 'Tarantella': 'tarantella',
    }
    name = mapping.get(archetype, 'neutral')
    groove = list(GROOVE_TEMPLATES.get(name, GROOVE_TEMPLATES['neutral']))

    # Ensure correct length for metre
    if metre == '3/4' or metre == '6/8':
        while len(groove) < 3:
            groove.append(0.0)
        return groove[:3]
    else:
        while len(groove) < 4:
            groove.append(0.0)
        return groove[:4]


# ═══════════════════════════════════════════════════════════════
#  Expression Map (§10 — 1/f Pink Noise)
# ═══════════════════════════════════════════════════════════════

class ExpressionMap:
    """Maps pink noise into tempo rubato and dynamic variation."""

    def __init__(self, max_beats: float, base_bpm: float,
                 char: Character | None = None):
        self.base_bpm = base_bpm
        c = char or Character()
        rubato_mag = c.rubato_magnitude
        dyn_mag = c.dynamic_magnitude

        tempo_noise = PinkNoise(octaves=6)
        dynamics_noise = PinkNoise(octaves=6)

        steps = int(max_beats * 4) + 16
        self.time_map = np.zeros(steps, dtype=np.float64)
        self.intensity_map = np.zeros(steps, dtype=np.float64)

        current_time = 0.0
        for i in range(steps):
            t_noise = tempo_noise.step()
            bpm_mult = np.clip(1.0 + t_noise * rubato_mag, 0.80, 1.20)
            d_noise = dynamics_noise.step()
            intensity = np.clip(d_noise * (dyn_mag / 18.0), -1.0, 1.0)

            current_bpm = base_bpm * bpm_mult
            dt = 0.25 * (60.0 / current_bpm)

            if i > 0:
                current_time += dt

            self.time_map[i] = current_time
            self.intensity_map[i] = intensity

    def _idx(self, beat: float) -> int:
        return max(0, min(len(self.time_map) - 2, int(beat * 4)))

    def time(self, beat: float) -> float:
        idx = self._idx(beat)
        frac = (beat * 4) - idx
        return self.time_map[idx] + frac * (self.time_map[idx + 1] - self.time_map[idx])

    def intensity(self, beat: float) -> float:
        return self.intensity_map[self._idx(beat)]


# ═══════════════════════════════════════════════════════════════
#  PHF State (for UI tension display)
# ═══════════════════════════════════════════════════════════════

class PHFState:
    """Tracks harmonic field uncertainty for the tension meter.

    Uses a sliding Bayesian estimator with three mechanisms to keep
    entropy responsive throughout the piece:

    1.  **Decay toward uniform** (forgetting).  Each step, the distribution
        is pulled toward uniform by factor `decay`.  This means old notes
        gradually lose influence and only the recent harmonic context matters.
    2.  **Soft likelihoods**.  Chord tone / scale tone / chromatic likelihoods
        are much closer together (0.55 / 0.35 / 0.15) so a single note
        cannot collapse the distribution.
    3.  **Static distance prior** applied once at init, not compounded
        per step.  The home key gets a gentle head-start, not an
        exponentially growing advantage.
    """

    def __init__(self, key_root: int = 0, decay: float = 0.12) -> None:
        self.key_root = key_root
        self.decay = decay          # pull-toward-uniform per step
        self.num_states = 24

        # Static distance prior: gentle bias toward home key, applied once
        prior = np.ones(self.num_states, dtype=np.float64)
        for s in range(self.num_states):
            root = s % 12
            d = min((root - key_root) % 12, (key_root - root) % 12)
            prior[s] = np.exp(-0.15 * d)   # very gentle: semitone away = 0.86×
        prior /= prior.sum()
        self.H = prior.copy()

    def uncertainty(self) -> float:
        H_nz = self.H[self.H > 1e-15]
        return float(-np.sum(H_nz * np.log2(H_nz)))

    def step(self, event_pitch: int) -> None:
        if event_pitch == 0:
            return
        pc = event_pitch % 12

        # 1. Decay toward uniform (forgetting old evidence)
        uniform = np.ones(self.num_states, dtype=np.float64) / self.num_states
        self.H = (1.0 - self.decay) * self.H + self.decay * uniform

        # 2. Bayesian update with soft likelihoods
        L = np.zeros(self.num_states, dtype=np.float64)
        for s in range(self.num_states):
            root = s % 12
            is_minor = s >= 12
            chord_pcs = set((root + iv) % 12
                            for iv in (CHORD_MIN if is_minor else CHORD_MAJ))
            scale_pcs = set((root + iv) % 12
                            for iv in (SCALES['minor'] if is_minor else SCALES['major']))
            if pc in chord_pcs:
                L[s] = 0.55
            elif pc in scale_pcs:
                L[s] = 0.35
            else:
                L[s] = 0.15
        self.H *= L

        # 3. Normalise
        s_sum = np.sum(self.H)
        if s_sum > 0:
            self.H /= s_sum
        else:
            self.H[:] = 1.0 / self.num_states


# ═══════════════════════════════════════════════════════════════
#  MIL Generator — Character-Driven Hierarchical Pipeline (§12)
# ═══════════════════════════════════════════════════════════════

class MILGenerator:
    """Character-driven top-down piano composition engine."""

    def __init__(self) -> None:
        self.last_bpm: int = 120
        self.last_key: int = 0
        self.last_key_name: str = "C"
        self.last_num_bars: int = 16
        self.last_form: str = ""
        self.last_scale_type: str = "major"
        self.last_archetype: str = "Random"
        self.last_time_sig: str = "4/4"
        self.last_pianist: str = "Neutral"

    def generate(self, num_bars: int = 16, key_root: int = 0,
                 bpm: int = 120, scale_type: str = 'major',
                 archetype: str = 'Random', pianist: str = 'Neutral',
                 **kwargs) -> list[MILEvent]:

        # ── Level 0: Character ──
        if archetype in ARCHETYPES:
            char = ARCHETYPES[archetype]
            # Adjust darkness for minor
            if scale_type == 'minor':
                char = char.offset((0, 0.15, 0, 0, 0))
        else:
            char = random_character()
            if scale_type == 'minor':
                char = char.offset((0, 0.15, 0, 0, 0))

        self.last_archetype = archetype
        metre = char.time_signature
        beats_per_bar = char.beats_per_bar
        self.last_time_sig = metre

        # ── Pianist ──
        if pianist in PIANISTS:
            perf_pianist = PIANISTS[pianist]
        else:
            perf_pianist = Pianist()  # Neutral
        self.last_pianist = pianist

        # Use provided BPM or let character suggest
        if bpm == 0:
            bpm = int(np.clip(char.bpm_base, 50, 200))
        self.last_bpm = bpm
        self.last_key = key_root
        self.last_key_name = NOTE_NAMES[key_root]
        self.last_num_bars = num_bars
        self.last_scale_type = scale_type

        # ── Level 5: Form ──
        sections, form_name = self._plan_form(
            num_bars, key_root, scale_type, char)
        self.last_form = form_name

        # ── Level 4: Seed Motif ──
        motif = SeedMotif(character=char, beats_per_bar=beats_per_bar)

        # ── Level 3: Expression Surface ──
        expr = ExpressionMap(max_beats=num_bars * beats_per_bar,
                             base_bpm=bpm, char=char)
        macro_arc = self._compute_macro_arc(num_bars, char)

        # ── Thematic Memory & Feedback ──
        memory = ThematicMemory(char.volatility)
        feedback = FeedbackCorrector(char)

        # ── Groove ──
        groove = _select_groove(archetype, metre)

        all_events: list[MILEvent] = []

        # ── Continuous Character Flow (§5) ──
        # Pink noise generator for micro-variations
        char_noise = PinkNoise(octaves=5)
        # Viscosity: μ = 0.1 + (1 - volatility) × 0.3
        mu = 0.1 + (1.0 - char.volatility) * 0.3

        # ── Tension tracking ──
        prev_tension = 0.0

        for section in sections:
            # Section attractor = base character + section offset
            attractor = char.offset(section.char_offset)

            # ── Level 2: Phrases ──
            phrases = self._plan_phrases(section, motif)

            # Choose accompaniment weighted by attractor character
            accomp_type = self._sample_accomp(attractor, metre)

            # ── Level 1: Generate content ──
            for phrase in phrases:
                # ── Continuous Character Flow: per-bar effective character ──
                # c_eff(i) = c_attractor + offset × exp(-μ × bars_since_start)
                #            + pink_noise × volatility
                bars_into_section = phrase.start_bar - section.start_bar
                decay = np.exp(-mu * bars_into_section)
                noise_val = char_noise.step() * char.volatility * 0.05
                offset_arr = np.array(section.char_offset)
                eff_arr = attractor.as_array() + offset_arr * (decay - 1.0) * 0.3 + noise_val
                eff_arr = np.clip(eff_arr, 0.0, 1.0)
                eff_char = Character(*eff_arr.tolist())

                chords = self._generate_progression(
                    section.key_root, section.scale_type,
                    phrase.num_bars, phrase.cadence_type, eff_char
                )
                melody = self._generate_melody(
                    section.key_root, section.scale_type,
                    chords, motif, phrase, expr, macro_arc,
                    eff_char, metre
                )

                # ── Tension Field (§14): compute and feed back ──
                phrase_tension = self._compute_phrase_tension(
                    melody, chords, section.key_root, eff_char
                )
                tension_gradient = phrase_tension - prev_tension
                prev_tension = phrase_tension

                # Apply feedback corrections to melody
                feedback.analyze_phrase(melody)
                # ── Self-Listening (§8): apply corrections ──
                if feedback.velocity_correction != 0:
                    vel_adj = int(feedback.velocity_correction * 0.5)
                    melody = [MILEvent(
                        pitch=e.pitch, duration_beats=e.duration_beats,
                        velocity=int(np.clip(e.velocity + vel_adj, 35, 125)),
                        beat_position=e.beat_position,
                        time_seconds=e.time_seconds,
                        duration_seconds=e.duration_seconds
                    ) for e in melody]

                # Apply ornaments to melody
                melody = self._apply_ornaments(
                    melody, eff_char, perf_pianist,
                    section.key_root, section.scale_type
                )

                # Apply groove to melody timing
                melody = self._apply_groove(melody, groove, bpm, beats_per_bar)

                # Record motif for thematic memory
                memory.record(phrase.motif_transform,
                            phrase.start_bar * beats_per_bar)

                accomp = self._generate_accompaniment(
                    section.key_root, section.scale_type,
                    chords, accomp_type, phrase, expr, macro_arc,
                    eff_char, metre
                )

                # Apply groove to accompaniment
                accomp = self._apply_groove(accomp, groove, bpm, beats_per_bar)

                bass = self._generate_bass(
                    section.key_root, chords, phrase, expr,
                    macro_arc, eff_char
                )

                # Apply groove to bass
                bass = self._apply_groove(bass, groove, bpm, beats_per_bar)

                all_events += melody + accomp + bass

        # Apply performance mapping as final pass
        all_events = self._apply_performance(all_events, perf_pianist, bpm)

        all_events.sort(key=lambda e: e.time_seconds)
        return all_events

    # ── Accompaniment Sampling ──

    def _sample_accomp(self, char: Character, metre: str) -> str:
        w = char.accomp_weights(metre)
        patterns = list(w.keys())
        weights = [w[p] for p in patterns]
        total = sum(weights)
        if total <= 0:
            return 'alberti'
        r = random.random() * total
        cumul = 0.0
        for i, wt in enumerate(weights):
            cumul += wt
            if r <= cumul:
                return patterns[i]
        return patterns[-1]

    # ── Macro Arc Computation ──

    def _compute_macro_arc(self, num_bars: int, char: Character) -> np.ndarray:
        """Compute macro intensity arc across the piece."""
        num_steps = max(4, num_bars // 2)
        arc = np.linspace(0.3, 0.9, num_steps)
        return arc

    # ───────────────────────────────────────────────────────────
    #  Level 5: Form Planning (§8)
    # ───────────────────────────────────────────────────────────

    def _plan_form(self, num_bars: int, key_root: int,
                   scale_type: str, char: Character
                   ) -> tuple[list[Section], str]:

        b_offset = (0.15, 0.10, 0.10, -0.10, 0.15)
        a_prime_offset = (-0.05, 0.0, 0.0, 0.05, -0.05)
        c_offset = (0.10, 0.15, 0.15, -0.15, 0.20)

        if num_bars <= 8:
            sections = [Section(key_root, scale_type, 0, num_bars,
                                False, 'A', 0.6)]
            return sections, "Binary"

        if num_bars <= 12:
            half = num_bars // 2
            rest = num_bars - half
            b_key, b_scale = self._related_key(key_root, scale_type)
            sections = [
                Section(key_root, scale_type, 0, half, False, 'A', 0.55),
                Section(b_key, b_scale, half, rest, False, 'B', 0.65,
                        char_offset=b_offset),
            ]
            return sections, "Binary A–B"

        # Rondo for high volatility + long pieces
        if char.volatility > 0.6 and num_bars >= 24:
            seg = max(4, (num_bars // 5 // 4) * 4)
            if seg < 4:
                seg = 4
            a1 = seg
            b1 = seg
            a2 = seg
            c1 = seg
            a3 = num_bars - a1 - b1 - a2 - c1
            if a3 < 4:
                a3 = 4
                c1 = max(4, num_bars - a1 - b1 - a2 - a3)
            b_key, b_scale = self._related_key(key_root, scale_type)
            c_key, c_scale = self._related_key(key_root, scale_type)
            # Make sure C key differs from B key
            while c_key == b_key:
                c_key, c_scale = self._related_key(key_root, scale_type)
            bar = 0
            sections = [
                Section(key_root, scale_type, bar, a1, False, 'A', 0.55),
            ]
            bar += a1
            sections.append(Section(b_key, b_scale, bar, b1, False, 'B', 0.70,
                                    char_offset=b_offset))
            bar += b1
            sections.append(Section(key_root, scale_type, bar, a2, True,
                                    'A_prime', 0.55, char_offset=a_prime_offset))
            bar += a2
            sections.append(Section(c_key, c_scale, bar, c1, False, 'C', 0.75,
                                    char_offset=c_offset))
            bar += c1
            sections.append(Section(key_root, scale_type, bar, a3, True,
                                    'A_prime', 0.60, char_offset=a_prime_offset))
            return sections, "Rondo A–B–A'–C–A'"

        # Ternary ABA'
        if num_bars >= 24:
            a_len = max(4, (num_bars // 3 // 4) * 4)
            b_len = a_len
            a2_len = num_bars - a_len - b_len
        else:
            a_len = max(4, (num_bars // 2 // 4) * 4)
            b_len = max(4, a_len // 2 if a_len >= 8 else 4)
            a2_len = num_bars - a_len - b_len

        a_len = max(4, a_len)
        b_len = max(4, b_len)
        a2_len = max(4, a2_len)

        total = a_len + b_len + a2_len
        if total > num_bars:
            a2_len = max(4, a2_len - (total - num_bars))
        elif total < num_bars:
            a2_len += (num_bars - total)

        b_key, b_scale = self._related_key(key_root, scale_type)
        sections = [
            Section(key_root, scale_type, 0, a_len, False, 'A', 0.55),
            Section(b_key, b_scale, a_len, b_len, False, 'B', 0.70,
                    char_offset=b_offset),
            Section(key_root, scale_type, a_len + b_len, a2_len, True,
                    'A_prime', 0.65, char_offset=a_prime_offset),
        ]
        return sections, "Ternary A–B–A'"

    def _related_key(self, key_root: int, scale_type: str) -> tuple[int, str]:
        if scale_type == 'major':
            options = [
                ((key_root + 7) % 12, 'major'),
                ((key_root + 9) % 12, 'minor'),
                ((key_root + 5) % 12, 'major'),
            ]
        else:
            options = [
                ((key_root + 3) % 12, 'major'),
                ((key_root + 7) % 12, 'minor'),
                ((key_root + 5) % 12, 'minor'),
            ]
        return random.choice(options)

    # ───────────────────────────────────────────────────────────
    #  Level 2: Phrase Planning (§7)
    # ───────────────────────────────────────────────────────────

    def _plan_phrases(self, section: Section,
                      motif: SeedMotif) -> list[Phrase]:
        phrases: list[Phrase] = []
        bar = section.start_bar
        remaining = section.num_bars

        # Motif development arc per section role (§4.4)
        if section.role == 'A':
            transforms = ['identity', 'identity', 'sequence_up', 'fragment']
        elif section.role == 'B':
            transforms = ['inversion', 'retrograde', 'sequence_down',
                          'retro_inv', 'fragment', 'diminished']
        elif section.role == 'C':
            transforms = ['retro_inv', 'augmented', 'sequence_down', 'inversion']
        else:  # A'
            transforms = ['identity', 'sequence_up', 'inversion', 'identity']

        pair_idx = 0
        while remaining >= 4:
            if remaining >= 8:
                t_idx = pair_idx % len(transforms)
                phrases.append(Phrase(
                    start_bar=bar, num_bars=4,
                    cadence_type='half',
                    motif_transform=transforms[t_idx],
                    is_consequent=False
                ))
                bar += 4
                remaining -= 4

                con_transform = transforms[t_idx]
                if random.random() < 0.4:
                    con_transform = random.choice(transforms)
                phrases.append(Phrase(
                    start_bar=bar, num_bars=min(4, remaining),
                    cadence_type='authentic',
                    motif_transform=con_transform,
                    is_consequent=True
                ))
                bar += min(4, remaining)
                remaining -= min(4, remaining)
                pair_idx += 1
            else:
                t_idx = pair_idx % len(transforms)
                phrases.append(Phrase(
                    start_bar=bar, num_bars=remaining,
                    cadence_type='authentic',
                    motif_transform=transforms[t_idx],
                    is_consequent=True
                ))
                bar += remaining
                remaining = 0
                pair_idx += 1

        return phrases

    # ───────────────────────────────────────────────────────────
    #  Harmony: Character-Enriched Progressions (§5)
    # ───────────────────────────────────────────────────────────

    def _generate_progression(self, key_root: int, scale_type: str,
                              num_bars: int, cadence_type: str,
                              char: Character
                              ) -> list[tuple[int, list[int]]]:
        degrees = MAJOR_DEGREES if scale_type == 'major' else MINOR_DEGREES
        trans = MAJOR_TRANSITIONS if scale_type == 'major' else MINOR_TRANSITIONS
        chord_dict = MAJOR_CHORDS if scale_type == 'major' else MINOR_CHORDS
        fallback = CHORD_MAJ if scale_type == 'major' else CHORD_MIN

        current_idx = 0
        progression: list[int] = [degrees[0]]

        for bar in range(1, num_bars):
            if bar == num_bars - 2:
                pre_dom_indices = [1, 3]
                current_idx = random.choice(pre_dom_indices)
                progression.append(degrees[current_idx])
            elif bar == num_bars - 1:
                if cadence_type == 'half':
                    progression.append(degrees[4])
                    current_idx = 4
                else:
                    progression.append(degrees[0])
                    current_idx = 0
            else:
                weights = trans[current_idx].copy()
                s = weights.sum()
                if s > 0:
                    weights /= s
                else:
                    weights = np.ones(7) / 7.0
                next_idx = np.random.choice(7, p=weights)
                current_idx = next_idx
                progression.append(degrees[current_idx])

        # Ensure V before final I for authentic cadence
        if cadence_type == 'authentic' and num_bars >= 2:
            progression[-2] = degrees[4]

        # Build chord list with character-modulated enrichment
        chords: list[tuple[int, list[int]]] = []
        for i, deg in enumerate(progression):
            quality = chord_dict.get(deg % 12, fallback)

            # Secondary dominant
            if deg != degrees[0] and random.random() < char.secondary_dominant_prob:
                quality = CHORD_DOM7

            # Borrowed chord (modal mixture)
            if random.random() < char.borrowed_chord_prob:
                if scale_type == 'major' and deg in [9, 11]:
                    # ♭VII or ♭vi in major
                    borrowed_root = (key_root + deg - 1) % 12
                    quality = CHORD_MAJ
                    deg = borrowed_root - key_root
                    if deg < 0:
                        deg += 12

            # Neapolitan (♭II, pre-dominant, first inversion)
            if i < num_bars - 1 and random.random() < char.neapolitan_prob:
                if i >= num_bars - 3:  # Pre-dominant bars
                    deg = 1  # ♭II relative to key
                    quality = CHORD_MAJ

            # Augmented sixth (approaching V)
            if i < num_bars - 1 and random.random() < char.augmented_sixth_prob:
                if i == num_bars - 2:  # Approaching final chord
                    # Mark with a special chord for voice leading
                    quality = CHORD_AUG

            # Chromatic mediant
            if i < num_bars - 1 and random.random() < char.chromatic_mediant_prob:
                shift = random.choice([3, 4, -3, -4])
                deg = (deg + shift) % 12
                quality = CHORD_MAJ

            # Tritone substitution (V chord)
            if deg == degrees[4] and random.random() < char.tritone_sub_prob:
                deg = 1  # ♭II (tritone away from V)
                quality = CHORD_DOM7

            chords.append((deg, quality))

        return chords

    # ───────────────────────────────────────────────────────────
    #  Register Geography (§9)
    # ───────────────────────────────────────────────────────────

    def _register_envelope(self, char: Character, intensity: float) -> tuple[int, int]:
        """Dynamic register expansion based on intensity."""
        base_centre = char.melody_centre
        base_range = 7
        expansion = intensity * 5 + char.energy * 3
        low = max(48, int(base_centre - base_range - expansion))
        high = min(96, int(base_centre + base_range + expansion))
        return low, high

    # ───────────────────────────────────────────────────────────
    #  Tension Field (§14)
    # ───────────────────────────────────────────────────────────

    def _compute_phrase_tension(self, melody: list[MILEvent],
                                chords: list[tuple[int, list[int]]],
                                key: int,
                                char: Character) -> float:
        """Compute composite tension T(t) for a phrase.

        T = (w_h·T_harm + w_m·T_mel + w_r·T_rhy + w_reg·T_reg) / Σw

        Returns a scalar in [0, 1].
        """
        if not melody:
            return 0.0

        # Weights from character (§14.3)
        w_h = 0.4
        w_m = 0.2 + char.lyricism * 0.1
        w_r = 0.2 + char.energy * 0.1
        w_reg = 0.2
        w_total = w_h + w_m + w_r + w_reg

        # ── Harmonic tension: circle-of-fifths distance ──
        # Map scale degrees to fifths distance from tonic
        FIFTHS_DIST = {0: 0, 7: 1, 2: 2, 9: 3, 4: 4, 11: 5, 5: 1,
                       10: 2, 3: 3, 8: 4, 1: 5, 6: 6}
        harm_tensions = []
        for deg, _ in chords:
            d = deg % 12
            dist = FIFTHS_DIST.get(d, 6)
            harm_tensions.append(dist / 6.0)
        t_harm = float(np.mean(harm_tensions)) if harm_tensions else 0.0

        # ── Melodic tension: distance from centre + leap density ──
        centre = char.melody_centre + key % 12
        pitches = [e.pitch for e in melody]
        pitch_dists = [abs(p - centre) / 12.0 for p in pitches]
        # Unresolved leap density
        leaps = sum(1 for i in range(1, len(pitches))
                    if abs(pitches[i] - pitches[i-1]) >= 5)
        leap_density = leaps / max(1, len(pitches) - 1)
        t_mel = min(1.0, float(np.mean(pitch_dists)) + leap_density * 0.3)

        # ── Rhythmic tension: syncopation + note speed ──
        bpb = char.beats_per_bar
        offbeat_count = sum(1 for e in melody
                           if (e.beat_position % bpb) > 0.1
                           and abs((e.beat_position % bpb) - bpb/2) > 0.25)
        synco_density = offbeat_count / max(1, len(melody))
        durs = [e.duration_beats for e in melody]
        max_dur = max(durs) if durs else 1.0
        avg_dur = float(np.mean(durs)) if durs else 1.0
        speed_tension = 1.0 - avg_dur / max(max_dur, 0.1)
        t_rhy = min(1.0, synco_density * 0.5 + speed_tension * 0.5)

        # ── Registral tension: width vs baseline ──
        base_width = 14  # ±7 semitones
        actual_width = max(pitches) - min(pitches) if len(pitches) > 1 else 0
        max_expansion = 24  # semitones
        t_reg = min(1.0, max(0.0, (actual_width - base_width) / max_expansion))

        tension = (w_h * t_harm + w_m * t_mel + w_r * t_rhy + w_reg * t_reg) / w_total
        return float(np.clip(tension, 0.0, 1.0))

    # ───────────────────────────────────────────────────────────
    #  Melody Generation (§4, §7.3)
    # ───────────────────────────────────────────────────────────

    def _generate_melody(self, key: int, scale_type: str,
                         chords: list[tuple[int, list[int]]],
                         motif: SeedMotif, phrase: Phrase,
                         expr: ExpressionMap, macro_arc: np.ndarray,
                         char: Character, metre: str) -> list[MILEvent]:
        events: list[MILEvent] = []
        scale = SCALES[scale_type]
        scale_pcs = set((key + s) % 12 for s in scale)
        bpb = char.beats_per_bar

        # Get motif intervals and durations for this phrase
        motif_ivs, motif_durs = motif.get_transform(phrase.motif_transform)
        motif_idx = 0
        motif_used = False

        # Starting pitch biased by character
        start_pitch = char.melody_centre + key % 12
        if start_pitch > 84:
            start_pitch -= 12
        if phrase.is_consequent:
            start_pitch -= 3  # Varied opening for consequent
        last_pitch = start_pitch

        must_resolve = False
        resolve_dir = 0
        last_rhythm: list[float] | None = None
        beat_pos = float(phrase.start_bar * bpb)

        for bar_offset in range(phrase.num_bars):
            bar_idx = phrase.start_bar + bar_offset
            chord_deg, chord_q = chords[bar_offset]
            chord_pcs = set(((key + chord_deg) + iv) % 12 for iv in chord_q)

            # Chromatic approach tones
            chromatic_apps = set()
            for ct in chord_pcs:
                chromatic_apps.add((ct - 1) % 12)
                chromatic_apps.add((ct + 1) % 12)
            chromatic_apps -= chord_pcs

            # Macro intensity
            arc_t = bar_idx / max(1, self.last_num_bars - 1)
            arc_idx = min(len(macro_arc) - 1,
                          int(arc_t * (len(macro_arc) - 1)))
            intensity = macro_arc[arc_idx]

            # Character-weighted rhythm cell
            if last_rhythm is not None and random.random() < 0.45:
                rhythm = last_rhythm
            else:
                rhythm = _select_rhythm_cell(char, metre)
            last_rhythm = rhythm

            beat_in_bar = 0.0
            is_final_bar = (bar_offset == phrase.num_bars - 1)

            for dur_idx, dur in enumerate(rhythm):
                total_pos = beat_pos + beat_in_bar
                is_cadence_note = is_final_bar and (
                    beat_in_bar + dur >= bpb - 0.5)

                # ── Motif-guided pitch selection ──
                motif_target = None
                if motif_idx < len(motif_ivs) and not is_cadence_note:
                    motif_target = last_pitch + motif_ivs[motif_idx]
                    # Use motif duration if available
                    if motif_idx < len(motif_durs):
                        dur = motif_durs[motif_idx]
                    motif_idx += 1
                    motif_used = True

                # Restart motif in second half if not used
                if bar_offset == phrase.num_bars // 2 and dur_idx == 0 and not motif_used:
                    motif_idx = 0

                pitch = self._select_melody_pitch(
                    last=last_pitch, chord_pcs=chord_pcs,
                    scale_pcs=scale_pcs, chromatic_apps=chromatic_apps,
                    motif_target=motif_target,
                    must_resolve=must_resolve, resolve_dir=resolve_dir,
                    is_cadence=is_cadence_note, key=key,
                    cadence_type=phrase.cadence_type,
                    intensity=intensity, char=char
                )

                # Leap resolution tracking
                actual_interval = abs(pitch - last_pitch)
                if actual_interval >= 5:
                    must_resolve = True
                    resolve_dir = -1 if pitch > last_pitch else 1
                else:
                    must_resolve = False
                    resolve_dir = 0

                # Velocity
                expr_mod = expr.intensity(total_pos)
                base_vel = char.base_velocity
                vel = int(np.clip(base_vel + intensity * 35
                                  + expr_mod * char.dynamic_magnitude,
                                  35, 120))
                # Strong beat accent
                if abs(beat_in_bar) < 0.01:
                    vel = min(125, vel + 8)
                elif abs(beat_in_bar - bpb / 2) < 0.25:
                    vel = min(120, vel + 4)

                evt_time = expr.time(total_pos)
                evt_dur = expr.time(total_pos + dur * 0.9) - evt_time

                events.append(MILEvent(
                    pitch=pitch, duration_beats=dur, velocity=vel,
                    beat_position=total_pos,
                    time_seconds=evt_time,
                    duration_seconds=max(0.05, evt_dur)))

                last_pitch = pitch
                beat_in_bar += dur
                if beat_in_bar >= bpb:
                    break

            beat_pos += bpb

        return events

    def _select_melody_pitch(self, *, last: int, chord_pcs: set[int],
                             scale_pcs: set[int], chromatic_apps: set[int],
                             motif_target: int | None,
                             must_resolve: bool, resolve_dir: int,
                             is_cadence: bool, key: int,
                             cadence_type: str, intensity: float,
                             char: Character) -> int:

        # Cadential pitch
        if is_cadence:
            if cadence_type == 'authentic':
                cands = [p for p in range(max(21, last - 9), min(109, last + 10))
                         if p % 12 == key]
            else:
                dom = (key + 7) % 12
                lead = (key + 11) % 12
                super_t = (key + 2) % 12
                target_pcs = {dom, lead, super_t}
                cands = [p for p in range(max(21, last - 9), min(109, last + 10))
                         if p % 12 in target_pcs]
            if cands:
                return min(cands, key=lambda p: abs(p - last))
            return last

        # General pitch selection with register envelope (§15)
        centre = char.melody_centre + key % 12
        reg_low, reg_high = self._register_envelope(char, intensity)
        low = max(reg_low, centre - 14)
        high = min(reg_high, centre + 15)
        cands = list(range(max(low, last - 12), min(high, last + 13)))
        if not cands:
            return last

        scores = np.zeros(len(cands), dtype=np.float64)

        for i, p in enumerate(cands):
            pc = p % 12
            interval = abs(p - last)

            # Proximity
            scores[i] += np.exp(-(interval ** 2) / 5.0) * 3.0

            # Motif adherence
            if motif_target is not None:
                dist = abs(p - motif_target)
                if dist == 0:
                    scores[i] += 5.0
                elif dist <= 1:
                    scores[i] += 3.0
                elif dist <= 2:
                    scores[i] += 1.0

            # Harmonic membership
            if pc in chord_pcs:
                scores[i] += 2.5
            elif pc in scale_pcs:
                scores[i] += 1.0
            else:
                scores[i] -= 2.5
                if pc in chromatic_apps:
                    scores[i] += intensity * 4.0

            # Avoid same pitch (scaled by energy — high energy tolerates reps)
            if p == last:
                scores[i] -= 2.5 + (1.0 - char.energy) * 1.5

            # Register comfort — centred on character's melody centre
            dist_from_centre = abs(p - centre)
            if dist_from_centre <= 7:
                scores[i] += 0.3
            elif dist_from_centre > 14:
                scores[i] -= 1.5

            # Expressive leaps at high intensity
            if 5 <= interval <= 7 and intensity > 0.5:
                scores[i] += (intensity - 0.3) * 2.5 * char.complexity

            # Leap resolution
            if must_resolve:
                signed_step = p - last
                if abs(signed_step) <= 2 and signed_step * resolve_dir > 0:
                    scores[i] += 5.0
                elif interval > 2:
                    scores[i] -= 4.0

        # Softmax selection
        scores -= scores.max()
        temp = 0.75 + intensity * 0.3 + char.volatility * 0.2
        weights = np.exp(scores / temp)
        s = weights.sum()
        if s <= 0:
            return last
        return int(np.random.choice(cands, p=weights / s))

    # ───────────────────────────────────────────────────────────
    #  Accompaniment Generation (§9)
    # ───────────────────────────────────────────────────────────

    def _generate_accompaniment(self, key: int, scale_type: str,
                                chords: list[tuple[int, list[int]]],
                                pattern_type: str, phrase: Phrase,
                                expr: ExpressionMap,
                                macro_arc: np.ndarray,
                                char: Character, metre: str
                                ) -> list[MILEvent]:
        events: list[MILEvent] = []
        bpb = char.beats_per_bar
        beat_pos = float(phrase.start_bar * bpb)

        for bar_offset in range(phrase.num_bars):
            bar_idx = phrase.start_bar + bar_offset
            chord_deg, chord_q = chords[bar_offset]
            root_pc = (key + chord_deg) % 12

            # Build chord tones in accompaniment register
            chord_pitches = sorted(set(
                (52 + ((root_pc + iv) % 12)) for iv in chord_q
            ))
            while len(chord_pitches) < 3:
                chord_pitches.append(chord_pitches[0] + 12)
            chord_pitches = [max(48, min(79, p)) for p in chord_pitches]

            arc_t = bar_idx / max(1, self.last_num_bars - 1)
            arc_idx = min(len(macro_arc) - 1,
                          int(arc_t * (len(macro_arc) - 1)))
            intensity = macro_arc[arc_idx]
            base_vel = int(35 + intensity * 20 + char.energy * 10)

            if pattern_type == 'alberti':
                self._accomp_alberti(events, chord_pitches, beat_pos,
                                     bpb, base_vel, expr, char)
            elif pattern_type == 'arpeggiated':
                self._accomp_arpeggio(events, chord_pitches, beat_pos,
                                      bpb, base_vel, expr, char)
            elif pattern_type == 'block':
                self._accomp_block(events, chord_pitches, beat_pos,
                                   bpb, base_vel, expr, char)
            elif pattern_type == 'waltz':
                self._accomp_waltz(events, chord_pitches, beat_pos,
                                   bpb, base_vel, expr, char, root_pc)
            elif pattern_type == 'stride':
                self._accomp_stride(events, chord_pitches, beat_pos,
                                    bpb, base_vel, expr, char)
            elif pattern_type == 'tremolo':
                self._accomp_tremolo(events, chord_pitches, beat_pos,
                                     bpb, base_vel, expr, char)

            beat_pos += bpb

        return events

    def _accomp_alberti(self, events, cp, bp, bpb, bv, expr, char):
        if len(cp) >= 3:
            pat = [cp[0], cp[2], cp[1], cp[2]]
        else:
            pat = cp * 2
        n_notes = int(bpb * 2)
        for j in range(n_notes):
            note = pat[j % len(pat)]
            pos = bp + j * 0.5
            t = expr.time(pos)
            d = expr.time(pos + 0.45) - t
            vel = int(np.clip(bv + expr.intensity(pos) * 10
                              + (4 if j % 2 == 0 else 0), 22, 85))
            events.append(MILEvent(
                pitch=note, duration_beats=0.5, velocity=vel,
                beat_position=pos, time_seconds=t,
                duration_seconds=max(0.05, d)))

    def _accomp_arpeggio(self, events, cp, bp, bpb, bv, expr, char):
        arp = cp[:3]
        if arp:
            arp.append(arp[0] + 12)
        dur = bpb / len(arp) if arp else 1.0
        for j, note in enumerate(arp):
            pos = bp + j * dur
            t = expr.time(pos)
            d = expr.time(pos + dur * 0.9) - t
            vel = int(np.clip(bv + expr.intensity(pos) * 10, 22, 80))
            events.append(MILEvent(
                pitch=note, duration_beats=dur, velocity=vel,
                beat_position=pos, time_seconds=t,
                duration_seconds=max(0.05, d)))

    def _accomp_block(self, events, cp, bp, bpb, bv, expr, char):
        beats = [0.0, bpb / 2.0]
        for beat in beats:
            pos = bp + beat
            t = expr.time(pos)
            d = expr.time(pos + bpb / 2 * 0.9) - t
            for note in cp[:3]:
                vel = int(np.clip(bv + expr.intensity(pos) * 10
                                  + (6 if beat < 0.01 else 0), 22, 85))
                events.append(MILEvent(
                    pitch=note, duration_beats=bpb / 2, velocity=vel,
                    beat_position=pos, time_seconds=t,
                    duration_seconds=max(0.05, d)))

    def _accomp_waltz(self, events, cp, bp, bpb, bv, expr, char, root_pc):
        # Beat 1: bass note, beats 2-3: chord
        bass = 36 + root_pc
        if bass < 28:
            bass += 12
        pos = bp
        t = expr.time(pos)
        d = expr.time(pos + 0.9) - t
        vel = int(np.clip(bv + 5, 25, 80))
        events.append(MILEvent(
            pitch=bass, duration_beats=1.0, velocity=vel,
            beat_position=pos, time_seconds=t,
            duration_seconds=max(0.05, d)))
        for beat in [1.0, 2.0]:
            if beat >= bpb:
                break
            pos2 = bp + beat
            t2 = expr.time(pos2)
            d2 = expr.time(pos2 + 0.9) - t2
            for note in cp[:3]:
                vel2 = int(np.clip(bv - 5 + expr.intensity(pos2) * 8, 22, 75))
                events.append(MILEvent(
                    pitch=note, duration_beats=1.0, velocity=vel2,
                    beat_position=pos2, time_seconds=t2,
                    duration_seconds=max(0.05, d2)))

    def _accomp_stride(self, events, cp, bp, bpb, bv, expr, char):
        low = cp[0] - 12 if cp[0] > 48 else cp[0]
        half = bpb / 2.0
        for beat_off in [0.0, half]:
            pos = bp + beat_off
            t = expr.time(pos)
            d = expr.time(pos + 0.9) - t
            vel = int(np.clip(bv + 5 + expr.intensity(pos) * 10, 22, 85))
            events.append(MILEvent(
                pitch=low, duration_beats=1.0, velocity=vel,
                beat_position=pos, time_seconds=t,
                duration_seconds=max(0.05, d)))
            pos2 = bp + beat_off + half / 2
            if pos2 < bp + bpb:
                t2 = expr.time(pos2)
                d2 = expr.time(pos2 + 0.9) - t2
                for note in cp[:3]:
                    vel2 = int(np.clip(bv - 3 + expr.intensity(pos2) * 8, 22, 80))
                    events.append(MILEvent(
                        pitch=note, duration_beats=half / 2, velocity=vel2,
                        beat_position=pos2, time_seconds=t2,
                        duration_seconds=max(0.05, d2)))

    def _accomp_tremolo(self, events, cp, bp, bpb, bv, expr, char):
        if len(cp) < 2:
            return self._accomp_block(events, cp, bp, bpb, bv, expr, char)
        pair = [cp[0], cp[1]]
        n_notes = int(bpb * 4)  # sixteenth-note tremolo
        for j in range(n_notes):
            note = pair[j % 2]
            pos = bp + j * 0.25
            t = expr.time(pos)
            d = expr.time(pos + 0.2) - t
            vel = int(np.clip(bv - 8 + expr.intensity(pos) * 12
                              + random.randint(-3, 3), 20, 80))
            events.append(MILEvent(
                pitch=note, duration_beats=0.25, velocity=vel,
                beat_position=pos, time_seconds=t,
                duration_seconds=max(0.05, d)))

    # ───────────────────────────────────────────────────────────
    #  Bass Generation (§9.3)
    # ───────────────────────────────────────────────────────────

    def _generate_bass(self, key: int,
                       chords: list[tuple[int, list[int]]],
                       phrase: Phrase, expr: ExpressionMap,
                       macro_arc: np.ndarray,
                       char: Character) -> list[MILEvent]:
        events: list[MILEvent] = []
        bpb = char.beats_per_bar
        beat_pos = float(phrase.start_bar * bpb)
        bass_depth = int(36 - char.darkness * 4)
        last_bass = bass_depth + key

        for bar_offset in range(phrase.num_bars):
            bar_idx = phrase.start_bar + bar_offset
            chord_deg, chord_q = chords[bar_offset]
            root_pc = (key + chord_deg) % 12

            # Voice-leading: closest bass note
            cands = []
            for octave_base in [24, 36, 48]:
                p = octave_base + root_pc
                if 28 <= p <= 52:
                    cands.append(p)
            if not cands:
                cands = [bass_depth + root_pc]
            bass_note = min(cands, key=lambda p: abs(p - last_bass))

            arc_t = bar_idx / max(1, self.last_num_bars - 1)
            arc_idx = min(len(macro_arc) - 1,
                          int(arc_t * (len(macro_arc) - 1)))
            intensity = macro_arc[arc_idx]
            base_vel = int(30 + intensity * 15 + char.energy * 8)

            pos = beat_pos
            t = expr.time(pos)
            d = expr.time(pos + bpb * 0.95) - t
            vel = int(np.clip(base_vel + expr.intensity(pos) * 8, 20, 75))
            events.append(MILEvent(
                pitch=bass_note, duration_beats=bpb, velocity=vel,
                beat_position=pos, time_seconds=t,
                duration_seconds=max(0.05, d)))
            last_bass = bass_note
            beat_pos += bpb

        return events

    # ───────────────────────────────────────────────────────────
    #  Ornamentation (§6)
    # ───────────────────────────────────────────────────────────

    def _apply_ornaments(self, events: list[MILEvent], char: Character,
                         pianist: Pianist, key: int, scale_type: str
                         ) -> list[MILEvent]:
        """Post-process melody events with ornaments."""
        result: list[MILEvent] = []
        scale = SCALES[scale_type]
        scale_pcs = set((key + s) % 12 for s in scale)

        for ev in events:
            # Only ornament longer notes not at cadence
            if ev.duration_beats < 0.75:
                result.append(ev)
                continue

            # Roll for ornament
            ornament_threshold = char.complexity * 0.3 + pianist.ornament_prob
            if random.random() > ornament_threshold:
                result.append(ev)
                continue

            # Choose ornament type (context-free grammar: §6)
            ornament_type = random.choice(['turn', 'mordent', 'grace', 'trill'])

            if ornament_type == 'turn':
                # 4 notes: upper, note, lower, note
                dur_quarter = ev.duration_beats / 4
                base_vel = ev.velocity
                upper = ev.pitch + 1
                lower = ev.pitch - 1
                notes = [upper, ev.pitch, lower, ev.pitch]
                for j, p in enumerate(notes):
                    pc = p % 12
                    if pc not in scale_pcs:
                        p = ev.pitch
                    result.append(MILEvent(
                        pitch=p, duration_beats=dur_quarter,
                        velocity=base_vel - 5,
                        beat_position=ev.beat_position + j * dur_quarter,
                        time_seconds=ev.time_seconds,
                        duration_seconds=ev.duration_seconds / 4
                    ))

            elif ornament_type == 'mordent':
                # 3 rapid notes: note, upper, note
                dur_third = ev.duration_beats / 3
                base_vel = ev.velocity
                upper = ev.pitch + 1
                notes = [ev.pitch, upper, ev.pitch]
                for j, p in enumerate(notes):
                    pc = p % 12
                    if pc not in scale_pcs:
                        p = ev.pitch
                    result.append(MILEvent(
                        pitch=p, duration_beats=dur_third if j > 0 else dur_third,
                        velocity=base_vel - 3,
                        beat_position=ev.beat_position + j * dur_third,
                        time_seconds=ev.time_seconds,
                        duration_seconds=ev.duration_seconds / 3
                    ))

            elif ornament_type == 'grace':
                # Prepend short approach note
                grace_dur = 0.1
                grace_pitch = ev.pitch - 1
                pc = grace_pitch % 12
                if pc not in scale_pcs:
                    grace_pitch = ev.pitch
                result.append(MILEvent(
                    pitch=grace_pitch, duration_beats=grace_dur,
                    velocity=ev.velocity - 8,
                    beat_position=ev.beat_position - grace_dur,
                    time_seconds=ev.time_seconds,
                    duration_seconds=grace_dur
                ))
                result.append(ev)

            else:  # trill
                # Rapid alternation: note, upper, note, upper, note
                upper = ev.pitch + 2  # whole step trill
                pc_up = upper % 12
                if pc_up not in scale_pcs:
                    upper = ev.pitch + 1  # half step
                n_reps = max(3, min(7, int(ev.duration_beats / 0.15)))
                trill_dur = ev.duration_beats / n_reps
                for j in range(n_reps):
                    p = ev.pitch if j % 2 == 0 else upper
                    result.append(MILEvent(
                        pitch=p, duration_beats=trill_dur,
                        velocity=ev.velocity - 3 + (j % 2) * 2,
                        beat_position=ev.beat_position + j * trill_dur,
                        time_seconds=ev.time_seconds + j * (ev.duration_seconds / n_reps),
                        duration_seconds=ev.duration_seconds / n_reps
                    ))

        return result

    # ───────────────────────────────────────────────────────────
    #  Groove Application (§5)
    # ───────────────────────────────────────────────────────────

    def _apply_groove(self, events: list[MILEvent], groove: list[float],
                      bpm: int, beats_per_bar: float) -> list[MILEvent]:
        """Apply groove timing offsets to events."""
        result: list[MILEvent] = []
        for ev in events:
            beat_in_bar = ev.beat_position % beats_per_bar
            beat_in_bar_int = int(beat_in_bar) % len(groove)
            groove_offset = groove[beat_in_bar_int] * (60.0 / bpm)

            result.append(MILEvent(
                pitch=ev.pitch,
                duration_beats=ev.duration_beats,
                velocity=ev.velocity,
                beat_position=ev.beat_position,
                time_seconds=ev.time_seconds + groove_offset,
                duration_seconds=ev.duration_seconds
            ))
        return result

    # ───────────────────────────────────────────────────────────
    #  Performance Application (§10)
    # ───────────────────────────────────────────────────────────

    def _apply_performance(self, events: list[MILEvent], pianist: Pianist,
                           bpm: int) -> list[MILEvent]:
        """Apply pianist-specific performance characteristics."""
        result: list[MILEvent] = []

        # Compute soprano notes (highest at each time)
        time_to_pitches: dict[float, list[int]] = {}
        for ev in events:
            t = round(ev.time_seconds, 3)
            if t not in time_to_pitches:
                time_to_pitches[t] = []
            time_to_pitches[t].append(ev.pitch)

        soprano_pitches = set()
        for pitches in time_to_pitches.values():
            if pitches:
                soprano_pitches.add(max(pitches))

        for ev in events:
            # 1. Rubato scaling
            time_offset = ev.time_seconds
            # Scaling is applied as-is to time_seconds

            # 2. Attack adjustment (reduce duration for percussive pianists)
            dur_sec = ev.duration_seconds
            dur_sec *= (1.0 - pianist.attack_sharpness * 0.15)

            # 3. Dynamic range scaling
            vel = ev.velocity
            mean_vel = 70
            vel_deviation = vel - mean_vel
            vel = int(np.clip(
                mean_vel + vel_deviation * pianist.dynamic_range_mult,
                20, 127
            ))

            # 4. Soprano bias
            if ev.pitch in soprano_pitches:
                vel = int(np.clip(vel + pianist.soprano_bias, 20, 127))

            result.append(MILEvent(
                pitch=ev.pitch,
                duration_beats=ev.duration_beats,
                velocity=vel,
                beat_position=ev.beat_position,
                time_seconds=ev.time_seconds,
                duration_seconds=max(0.05, dur_sec)
            ))

        return result


# ═══════════════════════════════════════════════════════════════
#  Playback State
# ═══════════════════════════════════════════════════════════════

class Playback:
    """Real-time playback with rubato support."""
    def __init__(self, events: list[MILEvent]):
        self.events = events
        self.elapsed = 0.0
        self.event_idx = 0
        self.active = True
        self.pending_offs: list[tuple[float, int]] = []
        self.sounding: set[int] = set()
        self.total_seconds = (max(e.time_seconds + e.duration_seconds
                                  for e in events) + 1.0) if events else 1.0

    def start(self) -> None:
        self.elapsed = 0.0
        self.event_idx = 0
        self.active = True
        self.pending_offs.clear()
        self.sounding.clear()

    def update(self, dt: float, engine) -> set[int]:
        if not self.active:
            return set()
        self.elapsed += dt

        while self.event_idx < len(self.events):
            ev = self.events[self.event_idx]
            if ev.time_seconds <= self.elapsed:
                engine.note_on(ev.pitch, velocity=ev.velocity / 127.0)
                self.sounding.add(ev.pitch)
                self.pending_offs.append(
                    (ev.time_seconds + ev.duration_seconds, ev.pitch))
                self.event_idx += 1
            else:
                break

        remaining: list[tuple[float, int]] = []
        for off_time, pitch in self.pending_offs:
            if off_time <= self.elapsed:
                engine.note_off(pitch, sustain=False)
                self.sounding.discard(pitch)
            else:
                remaining.append((off_time, pitch))
        self.pending_offs = remaining

        if self.event_idx >= len(self.events) and not self.pending_offs:
            self.active = False
            self.sounding.clear()

        return set(self.sounding)

    @property
    def progress(self) -> float:
        if not self.active and self.elapsed > 0:
            return 1.0
        return min(1.0, self.elapsed / self.total_seconds)


# ═══════════════════════════════════════════════════════════════
#  MIDI File Writer
# ═══════════════════════════════════════════════════════════════

def _vlq(value: int) -> bytes:
    """Encode variable-length quantity for MIDI."""
    value = max(0, value)
    result = bytearray([value & 0x7F])
    value >>= 7
    while value:
        result.append((value & 0x7F) | 0x80)
        value >>= 7
    result.reverse()
    return bytes(result)


def write_midi(events: list[MILEvent], filepath: str,
               bpm: int = 120, ticks_per_beat: int = 480) -> str:
    """Write events to a Standard MIDI file."""
    ticks_per_sec = (bpm / 60.0) * ticks_per_beat

    midi_evts: list[tuple[int, int, int, int]] = []
    for ev in events:
        if 21 <= ev.pitch <= 108:
            tick_on = max(0, int(ev.time_seconds * ticks_per_sec))
            tick_off = tick_on + max(1, int(ev.duration_seconds * ticks_per_sec))
            midi_evts.extend([
                (tick_on, 0x90, ev.pitch, ev.velocity),
                (tick_off, 0x80, ev.pitch, 0),
            ])

    midi_evts.sort(key=lambda x: (x[0], 0 if x[1] == 0x80 else 1))

    track = bytearray()
    track += (_vlq(0) + bytes([0xFF, 0x51, 0x03])
              + int(60_000_000 / bpm).to_bytes(3, 'big'))
    track += _vlq(0) + bytes([0xC0, 0x00])

    prev_tick = 0
    for tick, status, note, vel in midi_evts:
        track += (_vlq(max(0, tick - prev_tick))
                  + bytes([status, note & 0x7F, vel & 0x7F]))
        prev_tick = tick

    track += _vlq(0) + bytes([0xFF, 0x2F, 0x00])

    filepath = os.path.abspath(filepath)
    with open(filepath, 'wb') as f:
        f.write(b'MThd' + struct.pack('>I', 6)
                + struct.pack('>HHH', 0, 1, ticks_per_beat))
        f.write(b'MTrk' + struct.pack('>I', len(track)) + track)

    return filepath
