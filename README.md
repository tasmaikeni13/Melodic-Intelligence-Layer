# MIL — Melodic Intelligence Layer

### A Mathematical Theory of Algorithmic Piano Composition with Musical Identity, Without Neural Networks

---

## Abstract

MIL (Melodic Intelligence Layer) is a complete mathematical framework for algorithmic piano composition that solves the fundamental problem of **musical identity** — generating pieces that possess the distinctive character separating a nocturne from a march, a waltz from a toccata, a ballade from an etude. The system rests on the insight that musical grammar (scales, chord progressions, voice leading) is necessary but radically insufficient: it defines the ocean of *valid* music but provides no mechanism for navigating to *specific, memorable* regions within it.

The core innovation is the **Character Space** — a five-dimensional unit hypercube C = [0, 1]^5 where each point defines a complete, internally consistent set of generation constraints. The five dimensions (Energy, Darkness, Complexity, Lyricism, Volatility) jointly govern every parameter of the compositional process: tempo, metre, motif shape, harmonic vocabulary, rhythmic density, textural pattern, register, and dynamic range. Twenty named archetypes — spanning lyrical, dance, dramatic, virtuosic, free, and structured families — are fixed points in this space, but any coordinate produces a unique piece with coherent identity.

The Character Space is integrated with a six-dimensional **Performance Space** modelling pianist identity. The character trajectory evolves dynamically via a continuous dynamical system with viscosity-dependent decay. Harmonic vocabulary expands non-linearly through a gated color spectrum. Micro-timing grooves provide rhythmic genre identity. Ornaments follow a context-free grammar. A composite tension field drives melodic climax and register expansion. Thematic memory implements recall pressure. A self-listening feedback loop closes the generation loop.

The complete system is fully specified, deterministic given a random seed and character vector, and implemented without neural networks, training data, or external corpora. The codebase totals ~3,900 lines of Python (2,225-line generation engine + 1,650-line UI/audio layer) with only `numpy`, `pygame`, and `sounddevice` as dependencies.

---

## Table of Contents

1. [Motivation: The Grammar Trap](#1-motivation-the-grammar-trap)
2. [Theoretical Framework](#2-theoretical-framework)
   - 2.1 [Character Space](#21-character-space-c--01⁵)
   - 2.2 [Performance Space](#22-performance-space-p--01⁶)
   - 2.3 [Continuous Character Flow](#23-continuous-character-flow)
   - 2.4 [Harmonic Color Spectrum](#24-harmonic-color-spectrum)
   - 2.5 [Micro-Timing Groove](#25-micro-timing-groove)
   - 2.6 [Ornamentation Algebra](#26-ornamentation-algebra)
   - 2.7 [Tension Field](#27-tension-field)
   - 2.8 [Register Geography](#28-register-geography)
   - 2.9 [Thematic Memory](#29-thematic-memory)
   - 2.10 [Self-Listening Feedback Loop](#210-self-listening-feedback-loop)
3. [Generation Pipeline](#3-generation-pipeline)
4. [Formal Properties](#4-formal-properties)
5. [Repository Structure](#5-repository-structure)
6. [Installation](#6-installation)
7. [Usage](#7-usage)
8. [Programmatic API](#8-programmatic-api)
9. [MIDI Export](#9-midi-export)
10. [Parameter Reference](#10-parameter-reference)
11. [Design Philosophy](#11-design-philosophy)
12. [License](#12-license)
13. [Citation](#13-citation)

---

## 1. Motivation: The Grammar Trap

Imagine an infinite library containing every possible sequence of piano notes. Most sequences are noise. If we filter by the rules of tonal music — notes must belong to a scale, chords must follow functional progressions, phrases must cadence — we eliminate the noise. What remains is grammatically correct music.

The problem is that this filtered library is still unimaginably vast, and almost everything in it sounds *the same*: pleasant, inoffensive, and utterly forgettable. It is music that obeys every rule and violates no constraint, yet possesses no identity.

Fur Elise and the Turkish March both obey the same harmonic grammar. They both use diatonic scales, functional chord progressions, antecedent-consequent phrase pairs, and cadential resolution. Yet they are unmistakably different pieces. The difference is not in the grammar — it is in the **character**: the specific, correlated set of choices that makes every element of Fur Elise serve wistful tenderness and every element of the Turkish March serve martial energy.

A generative system that samples each parameter independently — random motif, random rhythm cell, random chord walk, random accompaniment pattern — produces music where no element reinforces any other. The motif might suggest lyricism while the rhythm suggests a march and the accompaniment suggests a waltz. The result is not bad music; it is music without personality.

**The Identity Axiom.** Musical identity is an emergent property of *correlated constraint*: when tempo, metre, motif shape, harmonic vocabulary, rhythmic density, textural pattern, register, and dynamics are all drawn from distributions that share a common bias, the result has character. When they are drawn independently, the result is generic.

MIL formalises this axiom as a mathematical object — the Character Space — and derives the entire generation system from it.

---

## 2. Theoretical Framework

The full mathematical theory is documented in [`mil.md`](mil.md) (1,262 lines, 23 sections). Below is a condensed treatment of each major component.

### 2.1 Character Space (C = [0,1]^5)

The Character Space is a five-dimensional unit hypercube. Each point **c** = (e, d, x, l, v) defines a complete musical personality:

| Dimension | Symbol | 0 | 1 |
|---|---|---|---|
| **Energy** | e | Slow, soft, sparse, legato, narrow range | Fast, loud, dense, staccato, wide range |
| **Darkness** | d | Major mode, bright register, simple harmony | Minor mode, low register, chromatic harmony |
| **Complexity** | x | Simple rhythms, stepwise motion, few changes | Elaborate rhythms, leaps, rich harmonic turns |
| **Lyricism** | l | Percussive, rhythmic, detached articulation | Singing, flowing, sustained, arpeggiated |
| **Volatility** | v | Steady, predictable, minimal contrast | Sudden dynamic shifts, surprising turns |

The **character mapping** Phi: C -> P maps each vector to a complete parameter set governing all generation decisions. Every derived parameter is a continuous function of c, ensuring smooth interpolation between characters:

```
BPM(c)                    = 58 + e * 120 + v * 20                    (range: 58-198)
max_interval(c)           = 2 + floor(x * 4 + e * 2)                 (range: 2-8 semitones)
step_probability(c)       = 0.85 - x * 0.35                          (range: 0.50-0.85)
secondary_dominant_prob(c) = x * 0.15 + d * 0.08                     (range: 0.00-0.23)
borrowed_chord_prob(c)    = d * 0.12 + v * 0.08                      (range: 0.00-0.20)
suspension_prob(c)        = l * 0.15 + x * 0.08                      (range: 0.00-0.23)
rubato_magnitude(c)       = 0.04 + l * 0.06 + (1-e) * 0.02          (range: 4-12% BPM)
dynamic_magnitude(c)      = 10 + v * 15 + e * 8                      (range: 10-33 velocity)
melody_centre(c)          = 72 - d * 8 + e * 4                       (MIDI note, range: 64-76)
base_velocity(c)          = 45 + e * 40                               (range: 45-85)
```

Time signature selection is governed by a decision tree over lyricism and energy, producing 4/4, 3/4, or 6/8 metre. Accompaniment patterns (Alberti bass, arpeggiated, block chords, waltz, stride, tremolo) are selected by weighted sampling where the weights are continuous functions of the character vector and current metre.

#### Named Archetypes

Twenty archetypes serve as fixed reference points in Character Space. They are placed to guarantee a **minimum Euclidean distance of 0.30** between any pair (verified computationally over all 190 pairs), ensuring every archetype produces audibly distinct output. The mean pairwise distance is approximately 0.78.

| Family | Archetypes | Character Summary |
|---|---|---|
| **Lyrical** | Nocturne, Barcarolle, Lullaby, Berceuse, Arabesque | Singing melody, gentle accompaniment, low energy, high lyricism |
| **Dance** | Waltz, Polonaise, Tarantella, Mazurka | Rhythmic drive, characteristic metres and accents |
| **Dramatic** | Ballade, Scherzo, Elegy, Sonata | Emotional range, dark harmony, narrative structure |
| **Virtuosic** | Etude, Toccata | Technical density, maximum complexity and energy |
| **Free** | Rhapsody, Fantasia | High volatility, unpredictable character evolution |
| **Structured** | March, Prelude, Impromptu | Clear rhythmic identity, moderate complexity |

The system also accepts random points in C (producing pieces with unique unnamed characters) and supports interpolation between archetypes for hybrid characters.

### 2.2 Performance Space (P = [0,1]^6)

Beyond composition, the same notated piece sounds dramatically different when performed by different pianists. MIL models this variation using a six-dimensional Performance Space:

| Dimension | Symbol | 0 | 1 |
|---|---|---|---|
| **Rubato Freedom** | r | Metronomic timing | Elastic, expressive timing |
| **Attack Profile** | a | Rounded, gentle onsets | Sharp, percussive, crystalline |
| **Pedal Saturation** | p | Minimal pedal, maximal clarity | Heavy pedal, resonant blur |
| **Dynamic Exaggeration** | d_p | Uniform, restrained dynamics | Extreme dynamic swings |
| **Voice Highlighting** | h | Balanced, homogeneous texture | Soprano-biased, singing melody |
| **Ornamental Impulse** | o | Minimal ornamentation, literal | Maximum embellishment |

Ten historically-inspired pianist profiles serve as reference points (minimum pairwise distance >= 0.30 in 6D, verified over all 45 pairs):

| Pianist | r | a | p | d_p | h | o | Signature |
|---|---|---|---|---|---|---|---|
| **Horowitz** | 0.55 | 0.85 | 0.45 | 0.90 | 0.78 | 0.40 | Virtuosic, dramatic, crystalline attack |
| **Rubinstein** | 0.62 | 0.32 | 0.58 | 0.65 | 0.48 | 0.22 | Warm, lyrical, chamber-like |
| **Glenn Gould** | 0.12 | 0.72 | 0.08 | 0.55 | 0.62 | 0.08 | Analytical, sparse, Bach-like clarity |
| **Rachmaninoff** | 0.68 | 0.48 | 0.62 | 0.85 | 0.30 | 0.28 | Sonorous, improvisatory, dark |
| **Argerich** | 0.42 | 0.75 | 0.30 | 0.92 | 0.55 | 0.18 | Explosive, vivid, mercurial |
| **Brendel** | 0.42 | 0.28 | 0.52 | 0.45 | 0.42 | 0.15 | Philosophical, controlled, intellectual |
| **Cortot** | 0.92 | 0.22 | 0.68 | 0.72 | 0.55 | 0.62 | Romantic, rubato-heavy, ornamental |
| **Richter** | 0.35 | 0.68 | 0.52 | 0.80 | 0.28 | 0.12 | Austere, powerful, intimate |
| **Liszt** | 0.72 | 0.82 | 0.55 | 0.95 | 0.72 | 0.78 | Flamboyant, transcendental virtuosity |
| **Chopin** | 0.78 | 0.28 | 0.62 | 0.62 | 0.68 | 0.82 | Lyrical, elastic, ornament-rich |

The **performance mapping** Psi: P -> Q converts each vector into concrete interpretation parameters:

```
rubato_scale(p)      = 0.5 + r * 1.5       (range: 0.5x - 2.0x tempo deviation multiplier)
attack_sharpness(p)  = a * 0.3             (range: 0-30% note-onset duration reduction)
pedal_density(p)     = 0.2 + p * 0.6       (range: 20-80% measures with sustain pedal)
dynamic_range_mult(p)= 0.6 + d_p * 0.8     (range: 0.6x - 1.4x dynamic variation)
soprano_bias(p)      = h * 15              (range: 0-15 velocity boost to highest voice)
ornament_prob(p)     = o * 0.25            (range: 0-25% additional ornament probability)
```

**Multiplicative Distinctiveness.** The perceptible difference between two performances of the same composition is the product of character-space and performance-space differences. The same Nocturne performed by Horowitz (high attack, dynamic exaggeration) versus Cortot (maximal rubato, heavy pedal, ornamental) produces dramatically different aesthetic experiences despite identical note sequences.

### 2.3 Continuous Character Flow

Character is not static within sections. It evolves via a first-order ODE:

```
dc/dt = -mu * (c(t) - c_attractor) + perturbation(t)
```

where **c_attractor** is the target character for the current section, **mu** is a viscosity parameter, and the perturbation term adds stochastic 1/f micro-variation.

The viscosity governs how quickly character relaxes back to the attractor:

```
mu(c) = 0.1 + (1 - volatility) * 0.3       (range: 0.1-0.4)
```

Low-volatility pieces (Lullaby, mu ~ 0.35) return to their attractor within ~6 bars. High-volatility pieces (Rhapsody, mu ~ 0.15) wander freely for ~18 bars before returning. At section boundaries, an impulse perturbation is applied (the section's character offset), which then decays exponentially:

```
c_eff(bar_i) = c_attractor + offset * exp(-mu * bars_since_section_start)
               + pink_noise(t) * volatility
```

This produces natural drift within sections and sharp contrast between them, replacing the unrealistic assumption of constant character per section.

### 2.4 Harmonic Color Spectrum

A composite **Harmonic Color Index** gates access to chromatic harmonic devices:

```
H(c) = darkness * 0.5 + complexity * 0.5       (range: 0.0-1.0)
```

As H increases, progressively richer harmonic vocabulary becomes available:

| H Threshold | Device | Probability Formula |
|---|---|---|
| H > 0.50 | Neapolitan chords (bII) | (H - 0.50) * 0.15 |
| H > 0.55 | Augmented sixth chords (It6, Fr6, Ger6) | (H - 0.55) * 0.12 |
| H > 0.65 | Chromatic mediants (bIII, bVI) | (H - 0.65) * 0.10 |
| H > 0.75 | Tritone substitutions | (H - 0.75) * 0.08 |

This means a bright simple piece (Lullaby, H ~ 0.13) uses only diatonic harmony, while a dark complex piece (Scherzo, H ~ 0.65) freely employs Neapolitans and augmented sixths. The vocabulary expands continuously and non-linearly with the character vector, mirroring how real composers employ chromatic devices.

### 2.5 Micro-Timing Groove

Nine genre-specific beat-position offset templates shift events by fractions of a beat to create rhythmic *feel* that is audible but never notated:

| Template | Description | Example Offsets |
|---|---|---|
| **Swing** | Triplet-ised offbeat | [0.00, +0.04, -0.02, +0.04] |
| **Viennese Waltz** | Anticipated beat 2 | [0.00, -0.03, +0.02] |
| **Bossa Nova** | Syncopated 2+3+2+3 feel | [0.00, +0.02, -0.03, +0.02, -0.01, +0.03, -0.02, +0.01] |
| **Habanera** | Dotted eighth + sixteenth anticipation | [0.00, +0.05, -0.02, +0.03] |
| **Tango** | Marcato downbeat, legato continuation | [0.00, +0.02, -0.04, +0.02] |
| **Mazurka** | Delayed beat 2 or 3 | [0.00, +0.04, -0.02] |
| **March** | Slightly early offbeats | [0.00, -0.01, +0.01, -0.01] |
| **Tarantella** | Compound 6/8 push | [0.00, +0.02, -0.03, +0.02, -0.01, +0.02] |
| **Nocturne** | Lazy rubato feel | [0.00, +0.03, -0.01, +0.02] |

All templates are verified to have near-zero mean shift (< 0.1 beats) so they don't cause cumulative drift. Groove selection is automatic based on archetype and metre.

### 2.6 Ornamentation Algebra

Melody notes are expanded into ornamental figures via a context-free grammar with four production rules:

| Ornament | Expansion | Condition |
|---|---|---|
| **Turn** | note -> upper, note, lower, note | Long notes, moderate complexity |
| **Mordent** | note -> note, upper, note | Medium notes, all complexity levels |
| **Trill** | note -> (note, upper) x n | Long notes, high complexity/pianist impulse |
| **Grace Note** | note -> approach, note | Any duration, scales with ornamental impulse |

Ornament probability is gated by: `P(ornament) = complexity * 0.3 + pianist.ornamental_impulse`. This means a Toccata performed by Gould (low ornamental impulse) is nearly bare, while a Nocturne by Chopin (high impulse) is richly embellished. All auxiliary notes are constrained to the current scale.

### 2.7 Tension Field

A composite scalar T(t) in [0, 1] captures the instantaneous musical tension from four weighted sources:

```
T(t) = (w_h * T_harm + w_m * T_mel + w_r * T_rhy + w_reg * T_reg) / (w_h + w_m + w_r + w_reg)
```

**Components:**

| Component | Formula | Captures |
|---|---|---|
| **Harmonic** | circle_of_fifths_distance(chord, I) / 6 | Distance from tonic on the circle of fifths |
| **Melodic** | mean(abs(pitch - centre) / 12) + leap_density * 0.3 | Register deviation + unresolved leaps |
| **Rhythmic** | syncopation_density * 0.5 + (1 - avg_duration / max_duration) * 0.5 | Rhythmic instability |
| **Registral** | (actual_width - base_width) / max_expansion | Pitch spread vs. baseline |

**Character-dependent weights:**

```
w_h   = 0.40                                  (harmonic tension always dominates)
w_m   = 0.20 + lyricism * 0.10               (melodic tension higher in lyrical pieces)
w_r   = 0.20 + energy * 0.10                 (rhythmic tension higher in energetic pieces)
w_reg = 0.20                                  (registral tension constant)
```

The tension gradient dT/dt feeds back into the generator: rising tension sustains climactic building; falling tension triggers resolution. This creates natural phrase-level dramatic arcs without explicit programming of "climax" or "resolution."

### 2.8 Register Geography

The register envelope RE(t) = [low(t), high(t)] specifies the permissible melodic pitch range, expanding dynamically with tension and energy:

```
base_range  = melody_centre(c) +/- 7 semitones
expansion   = tension * 5 + energy * 3 semitones
high(t)     = melody_centre + 7 + expansion
low(t)      = melody_centre - 7 - expansion
```

At rest, the melody occupies a ~14-semitone window centred on the character's preferred register. At full tension, this expands to ~25 semitones, allowing climactic passages to reach into extreme registers while quiet passages remain centred. The expansion factor of 5 semitones per unit tension was calibrated to produce perceptible but not disorienting register shifts.

### 2.9 Thematic Memory

Motif transformations are tracked with exponential familiarity decay:

```
F_m(t) = F_0 * exp(-lambda * (t - t_last))
```

where lambda_decay = lambda_base / max(1, n_recalls * 0.5), reducing decay rate for frequently-recalled motifs (they become "more memorable"). When familiarity drops below a threshold theta:

```
R(t) = max(0, theta - F_m(t))            (recall pressure)
theta = 0.6 - volatility * 0.3           (range: 0.30-0.60)
```

High recall pressure biases the generator toward identity or fragmentation transforms, creating the sense that the music "remembers" its themes. High-volatility pieces have lower theta (more tolerant of novelty); low-volatility pieces insistently recall familiar material.

### 2.10 Self-Listening Feedback Loop

After each phrase, a feedback corrector compares actual output against character-derived targets:

```
error = [actual_range - target_range,
         actual_velocity - target_velocity,
         actual_density - target_density]

correction = -alpha * error               (alpha = 0.3)
```

Target values are derived from the character vector (e.g., target_range = 8 + energy * 8 + complexity * 4). Corrections are applied to subsequent phrases, preventing drift away from character intentions over long pieces. This is a classical proportional control loop — no neural networks, just error feedback.

---

## 3. Generation Pipeline

The complete pipeline follows a strict top-down hierarchy:

```
MIL_GENERATE(num_bars, key_root, scale_type, bpm, character, pianist):

    Level 0: Character + Performance
    ├── Derive all parameters from character vector via Phi
    ├── Derive performance parameters from pianist vector via Psi
    ├── Compute viscosity mu for character flow
    │
    Level 5: Form
    ├── Select form type (Binary, Ternary ABA', Rondo ABACA)
    ├── Plan sections with key relations and character offsets
    │
    Level 4: Seed Motif
    ├── Generate 3-5 note motif constrained by character
    ├── Define transformation group: identity, inversion, retrograde,
    │   augmentation, diminution, fragmentation, sequence
    │
    Level 3: Expression Surface
    ├── Compute 1/f pink noise rubato and dynamics map
    ├── Compute macro intensity arc across piece
    │
    For each section:
    │   Compute effective character via continuous flow ODE
    │   Select accompaniment pattern (Alberti, arpeggiated, block, etc.)
    │   Select micro-timing groove template
    │
    │   Level 2: Phrases
    │   ├── Plan antecedent-consequent pairs
    │   ├── Assign motif transformations (biased by thematic memory)
    │   │
    │   For each phrase:
    │   │   Level 1: Content Generation
    │   │   ├── Generate chord progression (functional harmony)
    │   │   ├── Generate melody (motif-guided, harmony-constrained)
    │   │   ├── Compute tension field for phrase
    │   │   ├── Apply self-listening feedback corrections
    │   │   ├── Apply ornamentation grammar
    │   │   ├── Apply micro-timing groove
    │   │   ├── Generate accompaniment
    │   │   ├── Generate bass line
    │   │   └── Record motif transforms in thematic memory
    │
    Level 0: Performance Pass
    ├── Apply soprano voice highlighting
    ├── Apply attack profile (note-onset sharpening)
    ├── Apply dynamic range multiplication
    └── Apply rubato scaling

    Return: list of timed MILEvent objects
```

---

## 4. Formal Properties

The theory paper proves six formal theorems about MIL's output:

**Theorem 1 (Guaranteed Closure).** Every generated piece ends on a Perfect Authentic Cadence in the home key. The final section is always an A or A' in the home key; its final phrase is a consequent phrase; consequent phrases end with PAC by construction.

**Theorem 2 (Thematic Unity).** Every melodic phrase is derivable from the seed motif via the transformation group T = {identity, inversion, retrograde, augmentation, diminution, fragmentation, sequence}. The melody generator receives a transformation assignment for each phrase.

**Theorem 3 (Harmonic Coherence).** Every chord progression satisfies the functional gravity law T -> PD -> D -> T. Chords are generated by weighted random walk on a transition matrix that assigns near-zero weight to non-functional transitions.

**Theorem 4 (Character Consistency).** For any fixed character vector c, every stochastic choice in the pipeline is biased toward the same expressive direction. Every parameter is a continuous function of c; all modules consume these parameters; therefore all sampling distributions share the same bias.

**Theorem 5 (Distinctiveness).** For two character vectors c1 and c2 with ||c1 - c2|| > epsilon, the generated pieces differ in expected tempo, rhythmic profile, harmonic vocabulary, and textural pattern. Each parameter has nonzero gradient in at least one dimension; sufficient separation in C implies separation in parameter space.

**Theorem 6 (Performance Interaction).** Character space controls composition; performance space controls interpretation. When both vary, their effects are multiplicative, maximising perceptual distinctiveness.

---

## 5. Repository Structure

```
mil/
├── README.md                       # This document
├── mil.md                          # Full mathematical theory (1,262 lines, 23 sections)
│
└── piano/                          # Implementation
    ├── mil_engine.py               # Core generation engine (2,225 lines)
    │   ├── Character               #   5D character vector + derived parameters
    │   ├── Pianist                  #   6D performance vector + derived parameters
    │   ├── SeedMotif               #   Motif generation + 7 transformations
    │   ├── ExpressionMap           #   1/f pink noise rubato + dynamics
    │   ├── PinkNoise               #   Voss-McCartney fractal noise generator
    │   ├── ThematicMemory          #   Familiarity decay + recall pressure
    │   ├── FeedbackCorrector       #   Self-listening error correction
    │   ├── PHFState                #   Bayesian harmonic uncertainty tracker
    │   ├── MILGenerator            #   Complete hierarchical pipeline
    │   ├── Playback                #   Real-time rubato-aware playback
    │   └── write_midi()            #   Standard MIDI file export
    │
    ├── main.py                     # Pygame UI application (508 lines)
    │   ├── Key / Mode / BPM / Bars selectors
    │   ├── Archetype selector (20 archetypes + Random)
    │   ├── Pianist selector (10 pianists + Neutral)
    │   ├── 88-key concert grand visualisation
    │   ├── Real-time tension meter
    │   └── MIDI export toggle
    │
    ├── piano_engine.py             # Audio synthesis via sounddevice (283 lines)
    ├── keyboard_renderer.py        # 88-key visual rendering (436 lines)
    ├── config.py                   # UI constants and layout (218 lines)
    ├── input_handler.py            # Keyboard/mouse input (138 lines)
    ├── pedal_controller.py         # Sustain pedal logic (64 lines)
    └── requirements.txt            # Python dependencies
```

The engine (`mil_engine.py`) is entirely self-contained — it depends only on `numpy` and Python's standard library. It takes a character vector and optional pianist vector and returns a list of timed, velocity-marked note events. The UI layer (`main.py` + supporting modules) handles rendering and audio.

---

## 6. Installation

**Requirements:** Python 3.10 or higher. Tested on Windows 10/11, macOS 13+, and Ubuntu 22.04.

```bash
git clone https://github.com/yourusername/mil.git
cd mil/piano
pip install -r requirements.txt
```

**Dependencies** (all pip-installable):

| Package | Version | Purpose |
|---|---|---|
| `numpy` | >= 1.24.0 | Linear algebra, probability, noise generation |
| `pygame` | >= 2.5.0 | UI rendering, event handling, audio mixer |
| `sounddevice` | >= 0.4.6 | Low-latency audio output |
| `scipy` | >= 1.10.0 | Signal processing utilities |

No GPU required. No CUDA. No model weights. No downloads beyond the pip packages.

---

## 7. Usage

### Interactive UI

```bash
cd piano
python main.py
```

The application opens a concert grand piano visualisation with controls arranged in three rows:

**Row 1 — Composition Parameters:**
- **Key** — click to cycle through all 12 keys (C, C#, D, Eb, E, F, F#, G, Ab, A, Bb, B)
- **Mode** — Major or Minor (click to toggle)
- **BPM** — click to type a tempo value (40-240, default 120)
- **Bars** — click to type piece length (4-128, default 16)

**Row 2 — Character Selection:**
- Click to cycle through 20 named archetypes + "Random" (which samples a random point in Character Space each time)

**Row 3 — Pianist Selection:**
- Click to cycle through 10 named pianist profiles + "Neutral" (the centroid of Performance Space)

**Controls:**
- **Generate & Play** — compose a new piece and begin playback with real-time piano animation
- **Save to MIDI** — checkbox; when enabled, each generation exports a timestamped .mid file

**Keyboard Shortcuts:**
- `L` — toggle note name labels on keys
- `O` — toggle octave markers
- `Scroll` — adjust master volume
- `Escape` — quit

The status bar displays the active key, mode, BPM, time signature, bar count, archetype, pianist, and formal structure (Binary, Ternary ABA', Rondo ABACA, etc.). A progress bar and real-time tension meter (harmonic field uncertainty) provide visual feedback during playback.

---

## 8. Programmatic API

The engine can be used directly without the UI:

```python
from mil_engine import MILGenerator, write_midi, ARCHETYPE_NAMES, PIANIST_NAMES

gen = MILGenerator()

# Generate a Nocturne in D minor performed by Horowitz
events = gen.generate(
    num_bars=32,
    key_root=2,              # D (0=C, 1=C#, 2=D, ... 11=B)
    bpm=72,
    scale_type='minor',      # 'major' or 'minor'
    archetype='Nocturne',    # any of ARCHETYPE_NAMES, or 'Random'
    pianist='Horowitz'        # any of PIANIST_NAMES, or 'Neutral'
)

# Each event is a MILEvent with:
#   .pitch            (MIDI note number, 21-108)
#   .duration_beats   (duration in beats)
#   .velocity         (MIDI velocity, 0-127)
#   .beat_position    (absolute beat position in piece)
#   .time_seconds     (absolute time with rubato applied)
#   .duration_seconds (duration with rubato applied)

# Export to standard MIDI
write_midi(events, 'nocturne_d_minor.mid', bpm=72)

# Access generation metadata
print(gen.last_key_name)     # 'D'
print(gen.last_form)         # e.g. 'Ternary ABA'
print(gen.last_time_sig)     # e.g. '6/8'
print(gen.last_archetype)    # 'Nocturne'
print(gen.last_pianist)      # 'Horowitz'
```

**Custom Characters:**

```python
from mil_engine import Character, MILGenerator

# A brooding, complex, volatile character with no named archetype
custom = Character(
    energy=0.35,
    darkness=0.82,
    complexity=0.75,
    lyricism=0.60,
    volatility=0.70
)

# Inspect derived parameters
print(custom.bpm_base)              # ~117 BPM
print(custom.harmonic_color_index)  # 0.785 (rich chromatic vocabulary)
print(custom.neapolitan_prob)       # ~0.043
print(custom.time_signature)        # '4/4'
```

**Available Archetypes:**

```python
from mil_engine import ARCHETYPE_NAMES
# ['Random', 'Nocturne', 'Barcarolle', 'Lullaby', 'Berceuse', 'Arabesque',
#  'Waltz', 'Polonaise', 'Tarantella', 'Mazurka', 'Ballade', 'Scherzo',
#  'Elegy', 'Sonata', 'Etude', 'Toccata', 'Rhapsody', 'Fantasia',
#  'March', 'Prelude', 'Impromptu']
```

**Available Pianists:**

```python
from mil_engine import PIANIST_NAMES
# ['Neutral', 'Horowitz', 'Rubinstein', 'Glenn Gould', 'Rachmaninoff',
#  'Argerich', 'Brendel', 'Cortot', 'Richter', 'Liszt', 'Chopin']
```

---

## 9. MIDI Export

Every generated piece can be exported as a standard MIDI file (Format 0, single track) by enabling the "Save to MIDI" checkbox before generating. Files are written to the working directory with descriptive names:

```
mil_Dmin_72bpm_Nocturne_143052.mid
mil_CMaj_120bpm_Waltz_143105.mid
mil_Fmin_88bpm_Scherzo_143118.mid
```

These files can be opened in any DAW (Ableton, Logic, FL Studio, Reaper), notation software (MuseScore, Finale, Sibelius), or MIDI player. The MIDI events preserve the exact timing (including rubato deviations from grid), velocity (including performance-modified dynamics), and duration produced by the engine.

Programmatic export is also available:

```python
from mil_engine import MILGenerator, write_midi

gen = MILGenerator()
events = gen.generate(num_bars=64, archetype='Ballade', pianist='Rachmaninoff')
path = write_midi(events, 'ballade.mid', bpm=gen.last_bpm)
print(f'Written to: {path}')
```

---

## 10. Parameter Reference

| Parameter | Value | Rationale |
|---|---|---|
| Character dimensions | 5 | Minimal basis spanning musical identity |
| Performance dimensions | 6 | Comprehensive pianist identity model |
| Named archetypes | 20 | Coverage of major Western piano traditions |
| Named pianists | 10 | Historically grounded, perceptually distinct |
| Min archetype distance | 0.30 (Euclidean, 5D) | Guarantees audible distinctiveness |
| Min pianist distance | 0.30 (Euclidean, 6D) | Guarantees perceptible performance difference |
| Seed motif length | 3-5 notes | Long enough for identity, short enough for development |
| Phrase length | 3-4 bars | Standard classical phrase length |
| Harmonic rhythm | 1 chord/bar | Standard, subdivided at cadences |
| Melody range | MIDI 48-96 (±character offset) | Comfortable piano treble |
| Bass range | MIDI 36-60 (±character offset) | Comfortable piano bass |
| Rubato magnitude | 4-12% BPM | Perceptible, not disorienting |
| Dynamic variation | 10-33 velocity units | Expressive, not extreme |
| Leap resolution threshold | 5 semitones | Perfect fourth requires stepwise resolution |
| Character viscosity mu | 0.1-0.4 | Controls character drift rate |
| Tension weights | h:m:r:reg = 0.4:0.2-0.3:0.2-0.3:0.2 | Harmonic tension dominates |
| Register expansion factor | 5 semitones per unit tension | Climactic register breathing |
| Motif recall threshold theta | 0.3-0.6 | Volatility-dependent |
| Feedback learning rate alpha | 0.3 | Moderate correction per phrase |
| Groove templates | 9 genre-specific | Near-zero mean shift, perceptible feel |
| Form types | Binary, Ternary ABA', Rondo ABACA | Piece length and character dependent |
| Ornament types | 4 (turn, mordent, trill, grace) | Context-free grammar expansion |
| Pink noise octaves | 6 | Adequate long-range correlation depth |

---

## 11. Design Philosophy

MIL is not a neural network. It does not learn from data. It does not use transformers, diffusion models, RNNs, VAEs, or any form of machine learning. It is a hand-crafted mathematical system — a generative grammar for piano music where every rule, probability, and constraint is explicitly specified and musically motivated.

This is a deliberate design choice, rooted in three convictions:

**Transparency.** Every note in a MIL-generated piece can be traced back through the pipeline to the character vector that caused it. There are no hidden representations, no latent spaces, no black-box activations. The system is fully inspectable: you can ask "why did it play that note?" and get a complete causal chain from character vector through form, section, phrase, harmony, and pitch selection.

**Sufficiency of mathematics.** Musical identity — the quality that makes a nocturne sound like a nocturne — can be formalised as pure mathematics: geometry (character space), dynamical systems (character flow), information theory (tension field), probability (weighted sampling), and algebra (motif transformations). The hypothesis is that identity emerges from *correlated constraint*, and correlation can be engineered without learning it.

**Reproducibility.** Given the same random seed and character vector, MIL produces the same piece every time. There are no stochastic training runs, no model checkpoints, no hyperparameter sensitivity across training epochs. The system's behaviour is determined entirely by the code and the mathematics documented in the theory paper.

The limitation is equally clear: MIL cannot produce pieces with the long-range narrative architecture of human masterworks. It generates music that is *stylistically coherent* and *locally intelligent* but lacks the goal-directed revision, cultural context, and emotional intentionality of human composition. It maps the space of *plausible* piano music, not the space of *great* piano music. This is an honest boundary, and the system does not pretend otherwise.

---

## 12. License

MIT License. See [LICENSE](LICENSE) for details.

---

## 13. Citation

If you use MIL in research, creative work, or derivative projects:

```bibtex
@software{mil2026,
  title     = {MIL: Character-Driven Hierarchical Piano Composition},
  subtitle  = {A Mathematical Theory of Musical Identity Without Neural Networks},
  year      = {2026},
  url       = {https://github.com/yourusername/mil},
  note      = {5D Character Space, 6D Performance Space, 20 archetypes, 10 pianist profiles,
               continuous character flow, harmonic color spectrum, tension field,
               thematic memory, self-listening feedback. Pure mathematics, no neural networks.}
}
```
