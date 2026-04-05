# MIL: Character-Driven Hierarchical Composition

## A Mathematical Theory of Musical Identity Without Neural Networks
## Author :- Tasmai Keni

---

## Abstract

We present MIL (Melodic Intelligence Layer), a mathematical theory of algorithmic piano composition that solves the fundamental problem of **musical identity**: how to generate pieces that are not merely grammatically correct, but possess the distinctive character that separates a nocturne from a march, a waltz from a toccata, a ballade from an étude. The theory rests on the insight that musical grammar (scales, chord progressions, voice leading) is necessary but radically insufficient — it defines the ocean of *valid* music but provides no mechanism for navigating to *specific, memorable* regions within it.

The central innovation is the **Character Space** — a five-dimensional mathematical space where each point defines a complete, internally consistent set of generation constraints. The five dimensions (Energy, Darkness, Complexity, Lyricism, Volatility) jointly govern every parameter of the compositional process: tempo, metre, motif shape, harmonic vocabulary, rhythmic density, textural pattern, register, and dynamic range. Twenty named archetypes — spanning lyrical (Nocturne, Barcarolle, Lullaby, Berceuse, Arabesque), dance (Waltz, Polonaise, Tarantella, Mazurka), dramatic (Ballade, Scherzo, Elegy, Sonata), virtuosic (Étude, Toccata), free (Rhapsody, Fantasia), and structured (March, Prelude, Impromptu) families — are fixed points in this space, but any coordinate produces a unique piece with a coherent identity.

The Character Space is integrated with a **Performance Space** — a six-dimensional space defining pianist identity through rubato, attack profile, pedal technique, dynamic interpretation, voice highlighting, and ornamental impulse. The same composition performed by different pianists (Horowitz, Gould, Cortot, Chopin, Liszt, and others) produces audibly distinct interpretations.

The character trajectory evolves dynamically during piece generation via a continuous dynamical system with decay, allowing characters to drift and return in musically coherent ways. Harmonic vocabulary expands non-linearly with complexity. Micro-timing grooves provide rhythmic genre identity. Ornaments follow a context-free grammar. A composite tension field drives melodic climax and register expansion. Thematic memory implements recall pressure. A self-listening feedback loop closes the generation loop. The complete system is fully specified, deterministic given a random seed and character vector, and implementable without neural networks, training data, or external corpora.

---

## 1. The Grammar Trap: Why Correctness Is Not Enough

### 1.1 The Library of Babel for Piano Keys

Imagine an infinite library containing every possible sequence of piano notes. Most sequences are noise. If we filter by the rules of tonal music — notes must belong to a scale, chords must follow functional progressions, phrases must cadence — we eliminate the noise. What remains is grammatically correct music.

The problem is that this filtered library is still unimaginably vast, and almost everything in it sounds the same: pleasant, inoffensive, and utterly forgettable. It is music that obeys every rule and violates no constraint, yet possesses no identity. It is the musical equivalent of a paragraph where every word is valid English, every sentence is grammatically correct, and the whole thing says nothing.

Für Elise and the Turkish March both obey the same harmonic grammar. They both use diatonic scales, functional chord progressions, antecedent-consequent phrase pairs, and cadential resolution. Yet they are unmistakably different pieces. The difference is not in the grammar — it is in the **character**: the specific, correlated set of choices that makes every element of Für Elise serve wistful tenderness and every element of the Turkish March serve martial energy.

### 1.2 The Independence Problem

A generative system that samples each parameter independently — random motif, random rhythm cell, random chord walk, random accompaniment pattern — produces music where no element reinforces any other. The motif might suggest lyricism while the rhythm suggests a march and the accompaniment suggests a waltz. The result is not bad music; it is music without personality. It is a face where every feature is drawn from the space of valid features, but no feature relates to any other, producing something technically correct and deeply uncanny.

**Axiom 1.1 (The Identity Axiom).** Musical identity is an emergent property of **correlated constraint**: when tempo, metre, motif shape, harmonic vocabulary, rhythmic density, textural pattern, register, and dynamics are all drawn from distributions that share a common bias, the result has character. When they are drawn independently, the result is generic.

### 1.3 What Must Be Solved

A complete theory of algorithmic composition must provide:

1. **Grammatical correctness** — notes obey scales, chords follow functional logic, phrases cadence properly. (This is necessary but not sufficient.)
2. **Hierarchical coherence** — large-scale form constrains sections, sections constrain phrases, phrases constrain notes. (This prevents the "random walk" problem.)
3. **Musical identity** — a mechanism that makes all generative choices serve the same expressive intention, producing pieces that are distinct from each other in character. (This is the primary goal.)
4. **Performance variability** — the same piece performed by different pianists produces audibly distinct interpretations. (This reflects musical reality.)

---

## 2. Character Space: The Mathematical Foundation of Musical Identity

### 2.1 The Core Idea

We define a **Character Space** C = [0, 1]⁵, a five-dimensional unit hypercube. Each point **c** = (e, d, x, l, v) in this space defines a complete musical personality. The five dimensions are:

| Dimension | Symbol | Low (→ 0) | High (→ 1) |
|-----------|--------|-----------|------------|
| **Energy** | e | Slow, soft, sparse, legato, narrow range | Fast, loud, dense, staccato, wide range |
| **Darkness** | d | Major mode, bright register, simple harmony | Minor mode, low register, chromatic harmony |
| **Complexity** | x | Simple rhythms, stepwise motion, few harmonic changes | Elaborate rhythms, leaps, rich harmonic turns |
| **Lyricism** | l | Percussive, rhythmic, detached articulation | Singing, flowing, sustained, arpeggiated |
| **Volatility** | v | Steady, predictable, minimal contrast | Sudden dynamic shifts, surprising turns |

### 2.2 Archetype Points

Named archetypes are specific coordinates in Character Space. These are not arbitrary labels but mathematically defined points that correspond to recognisable musical traditions:

| Archetype | e | d | x | l | v | Character |
|-----------|------|------|------|------|------|-----------|
| **Lyrical / Gentle** | | | | | | |
| Nocturne | 0.20 | 0.40 | 0.30 | 0.92 | 0.18 | Night music — singing melody over gentle arpeggios |
| Barcarolle | 0.28 | 0.15 | 0.48 | 0.82 | 0.10 | Venetian boat song — rocking 6/8, ornamental, bright |
| Lullaby | 0.08 | 0.15 | 0.10 | 0.75 | 0.05 | Soothing, minimal, rocking — the sparsest archetype |
| Berceuse | 0.05 | 0.35 | 0.62 | 0.88 | 0.05 | Gentle variation-based cradle song — contemplative |
| Arabesque | 0.32 | 0.08 | 0.72 | 0.62 | 0.25 | Light ornamental Debussy-style — delicate, fast, free |
| **Dance** | | | | | | |
| Waltz | 0.45 | 0.28 | 0.30 | 0.70 | 0.20 | Graceful triple-metre dance, lilting, flowing |
| Polonaise | 0.70 | 0.48 | 0.52 | 0.22 | 0.30 | Stately, majestic Polish dance — powerful, dignified |
| Tarantella | 0.93 | 0.25 | 0.58 | 0.12 | 0.48 | Frantic Italian dance in 6/8 — wild, breathless |
| Mazurka | 0.60 | 0.25 | 0.38 | 0.32 | 0.40 | Polish dance with rhythmic accent — driving, syncopated |
| **Dramatic / Dark** | | | | | | |
| Ballade | 0.40 | 0.62 | 0.55 | 0.80 | 0.65 | Narrative, emotionally wide — dark but singing |
| Scherzo | 0.80 | 0.62 | 0.68 | 0.18 | 0.72 | Fast, dark, angular — demonic energy with sudden shifts |
| Elegy | 0.15 | 0.78 | 0.42 | 0.72 | 0.22 | Slow, mournful, deeply dark — singing through grief |
| Sonata | 0.62 | 0.55 | 0.72 | 0.48 | 0.60 | Dramatic two-theme form — development, conflict, resolution |
| **Virtuosic** | | | | | | |
| Étude | 0.75 | 0.35 | 0.88 | 0.45 | 0.30 | Technical study — relentless, complex, mechanical |
| Toccata | 0.95 | 0.48 | 0.82 | 0.05 | 0.42 | Perpetual motion — maximum density, minimum lyricism |
| **Free / Volatile** | | | | | | |
| Rhapsody | 0.65 | 0.45 | 0.60 | 0.62 | 0.85 | Improvisatory, unpredictable, passionate |
| Fantasia | 0.45 | 0.58 | 0.80 | 0.35 | 0.92 | Free-form, maximally unpredictable — cerebral, complex |
| **Structured** | | | | | | |
| March | 0.82 | 0.20 | 0.35 | 0.10 | 0.25 | Military/ceremonial — driving, rhythmic, bold, bright |
| Prelude | 0.42 | 0.45 | 0.45 | 0.52 | 0.38 | Concentrated musical idea — the most neutral archetype |
| Impromptu | 0.55 | 0.18 | 0.60 | 0.68 | 0.52 | Flowing, ornamental Chopin-style — spontaneous, lyrical |

These 20 archetypes are placed to guarantee a minimum Euclidean distance of 0.30 between any pair, ensuring that every archetype produces audibly distinct output. The mean pairwise distance is approximately 0.78. The system can also sample a random point in C to produce a piece with a unique, unnamed character, or interpolate between archetypes to produce hybrids.

### 2.3 The Character Mapping Function

**Definition 2.1.** The **character mapping** Φ: C → P maps a character vector to a complete parameter set P governing all generation decisions. We define Φ component by component:

**Tempo:**
```
BPM(c) = 58 + e × 120 + v × 20
```
This gives a range of ~58–198 BPM. Low energy → slow; high energy → fast; volatility adds unpredictability.

**Time Signature:**
```
if l > 0.65 and e < 0.45:    metre = 6/8    (compound, flowing)
elif l > 0.5 and e < 0.55:   metre = 3/4    (triple, dance-like)
else:                         metre = 4/4    (common time)
```

**Beats per bar** follows from the metre: 4 for 4/4, 3 for 3/4, and 3 compound beats (6 eighth notes) for 6/8.

**Motif Intervallic Bias:**
```
max_interval(c) = 2 + floor(x × 4 + e × 2)        range: 2–8 semitones
step_probability(c) = 0.85 - x × 0.35               range: 0.50–0.85
chromatic_probability(c) = d × 0.15 + x × 0.10      range: 0.00–0.25
```

**Motif Rhythmic Bias:**
```
short_note_probability(c) = 0.3 + e × 0.4 + x × 0.15
dotted_probability(c) = l × 0.25 + (1 - e) × 0.10
```

**Harmonic Vocabulary Width:**
```
secondary_dominant_prob(c) = x × 0.15 + d × 0.08
borrowed_chord_prob(c) = d × 0.12 + v × 0.08
suspension_prob(c) = l × 0.15 + x × 0.08
pedal_point_prob(c) = (1 - e) × 0.10 + l × 0.08
```

**Accompaniment Pattern Weights:**
The probability of each accompaniment pattern is a function of the character vector:
```
P(alberti)    = l × 0.6 + (1-e) × 0.2
P(arpeggiated)= l × 0.8 + (1-e) × 0.1
P(block)      = (1-l) × 0.5 + e × 0.3
P(waltz)      = f(metre=3/4) × 0.7 + l × 0.2
P(stride)     = e × 0.4 + (1-l) × 0.3
P(tremolo)    = v × 0.3 + d × 0.2 + e × 0.2
```
These are normalised to form a probability distribution from which the pattern is sampled per section.

**Dynamic Range:**
```
base_velocity(c) = 45 + e × 40
velocity_range(c) = 15 + v × 30 + e × 15
```

**Register Centre:**
```
melody_centre(c) = 72 - d × 8 + e × 4   (MIDI note, ~C5 area)
bass_depth(c) = 36 - d × 4               (MIDI note, ~C2-C3 area)
```

### 2.4 Causal Mechanism: Why This Works

The character mapping Φ is not a filter applied after generation. It is a **joint bias** applied during generation, making every stochastic choice throughout the entire pipeline favour the same expressive direction. This is the mechanism that produces identity:

- A Nocturne character biases toward slow tempo, triple or compound metre, flowing arpeggiated accompaniment, lyrical stepwise melody, simple harmony, soft dynamics — and these biases reinforce each other at every level.
- A Toccata character biases toward fast tempo, common time, percussive block or stride accompaniment, wide-leaping angular melody, complex harmony, forte dynamics — again, all mutually reinforcing.

No single bias is strong enough to make the piece sound "forced." But their cumulative effect, applied consistently across hundreds of generative decisions, produces unmistakable character. This is the Lollapalooza principle: multiple weak forces aligning in the same direction produce a strong emergent effect.

---

## 3. Performance Space: The Mathematical Foundation of Pianist Identity

### 3.1 The Six Dimensions of Pianist Identity

Beyond composition, the same notated piece sounds dramatically different when performed by different pianists. We model this variation using a **Performance Space** P = [0, 1]⁶, where each point **p** = (r, a, p_dim, d_p, h, o) represents a pianist's interpretive identity:

| Dimension | Symbol | Low (→ 0) | High (→ 1) |
|-----------|--------|-----------|------------|
| **Rubato Freedom** | r | Metronomic, mechanical timing | Expressive, flexible timing |
| **Attack Profile** | a | Rounded, gentle note onsets | Sharp, percussive, defined attacks |
| **Pedal Saturation** | p_dim | Minimal pedal use, clarity | Heavy pedal, resonant blur |
| **Dynamic Exaggeration** | d_p | Uniform dynamics, restrained | Extreme dynamics, dramatic swings |
| **Voice Highlighting** | h | Balanced texture, homogeneous | Soprano-biased, singing melody |
| **Ornamental Impulse** | o | Minimal ornamentation, literal | Maximum ornamentation, embellished |

### 3.2 Named Pianist Archetypes

Ten historically-inspired pianist profiles serve as reference points:

| Pianist | r | a | p_dim | d_p | h | o | Character |
|---------|------|------|------|------|------|------|-----------|
| **Horowitz** | 0.55 | 0.85 | 0.45 | 0.90 | 0.78 | 0.40 | Virtuosic, dramatic, crystalline attack |
| **Rubinstein** | 0.62 | 0.32 | 0.58 | 0.65 | 0.48 | 0.22 | Warm, lyrical, chamber-music-like |
| **Glenn Gould** | 0.12 | 0.72 | 0.08 | 0.55 | 0.62 | 0.08 | Analytical, spare, Bach-like clarity |
| **Rachmaninoff** | 0.68 | 0.48 | 0.62 | 0.85 | 0.30 | 0.28 | Sonorous, improvisatory, dark |
| **Argerich** | 0.42 | 0.75 | 0.30 | 0.92 | 0.55 | 0.18 | Explosive, vivid, mercurial |
| **Brendel** | 0.42 | 0.28 | 0.52 | 0.45 | 0.42 | 0.15 | Philosophical, controlled, Beethoven specialist |
| **Cortot** | 0.92 | 0.22 | 0.68 | 0.72 | 0.55 | 0.62 | Romantic, rubato-heavy, ornamental |
| **Richter** | 0.35 | 0.68 | 0.52 | 0.80 | 0.28 | 0.12 | Austere, powerful, intimate |
| **Liszt** | 0.72 | 0.82 | 0.55 | 0.95 | 0.72 | 0.78 | Virtuosic, flamboyant, transcendental |
| **Chopin** | 0.78 | 0.28 | 0.62 | 0.62 | 0.68 | 0.82 | Lyrical, elastic, ornament-rich |

### 3.3 Performance Mapping

**Definition 3.1.** The **performance mapping** Ψ: P → Q maps a performance vector to a set of interpreted performance parameters:

```
rubato_scale(p) = 0.5 + r × 1.5
```
Range: 0.5–2.0× applied to rubato magnitude. A rubato scale of 2.0 doubles all tempo deviations.

```
attack_sharpness(p) = a × 0.3
```
Duration reduction factor for note onsets: 0–30% of beat duration removed from preceding note, creating "early" attack. 0.0 = legato; 0.3 = crisp.

```
pedal_density(p) = 0.2 + p_dim × 0.6
```
Fraction of measures where sustain pedal is engaged. Range: 0.2–0.8.

```
dynamic_range_mult(p) = 0.6 + d_p × 0.8
```
Multiplier on dynamic variation magnitude. Range: 0.6–1.4×.

```
soprano_bias(p) = h × 15
```
Velocity boost applied to the highest voice (melody) in decibels. Range: 0–15 dB. This causes the melody to "sing" through the accompaniment.

```
ornament_probability(p) = o × 0.25
```
Additional probability mass added to ornament selection (turn, trill, grace note) beyond what character specifies. Range: 0–25% additional ornament probability.

### 3.4 Character × Performance Interaction

**Theorem 3.1 (Multiplicative Distinctiveness).** The perceptible difference between two performances of the same composition is the product of their differences in character space and performance space.

*Proof Sketch.* The performance mapping Ψ modulates parameters produced by the character mapping Φ. Variations in P produce distinct timing, articulation, and dynamic expression of the same underlying notated content. Variations in C produce different notated content, which is then modulated by P. When both C and P vary, both sources of difference are present and cumulative in their effect on perceived distinctiveness. ∎

Example: The same MIL-generated Nocturne composition, played by Horowitz (high attack, dynamic exaggeration, minimal rubato) versus Cortot (maximal rubato, heavy pedal, ornamental) produces dramatically different aesthetic experiences despite identical notation.

---

## 4. Hierarchical Generation: The Top-Down Principle

### 4.1 Why Local Optimisation Fails

A compelling paragraph requires a sentence plan, which requires a paragraph plan, which requires an essay plan. Even if every word is the optimal local choice given the preceding word, the result without higher-level planning is gibberish.

Music exhibits the identical structure. A sonata movement operates simultaneously at five timescales:

| Level | Span | Musical Unit | Function |
|-------|------|-------------|----------|
| 5 | 2–10 min | Piece | Dramatic arc, identity |
| 4 | 30–120 s | Section (A, B, A') | Thematic contrast/return |
| 3 | 8–16 s | Period (2 phrases) | Rhetorical statement |
| 2 | 4–8 s | Phrase (3–4 bars) | Single melodic gesture |
| 1 | 0.5–2 s | Bar / beat | Note-level content |

Generating music at Level 1 alone is structurally incapable of producing coherence at Levels 2–5, regardless of how sophisticated the note-selection heuristics become.

### 4.2 The Generation Sequence

**Axiom 4.1 (Top-Down Propagation).** Compositional decisions propagate downward. Higher levels are decided first and constrain all lower levels. The character vector propagates through every level.

```
0.  CHARACTER     →  Set character vector (archetype or custom)
1.  FORM          →  Choose section plan (Binary, Ternary, Rondo)
2.  KEY PLAN      →  Assign tonal centre and character offsets to each section
3.  SEED MOTIF    →  Generate rhythmic-intervallic DNA constrained by character
4.  PERIODS       →  Lay out antecedent–consequent pairs per section
5.  HARMONY       →  Generate functional progressions with character-appropriate vocabulary
6.  MELODY        →  Derive melody from motif transformations, guided by harmony
7.  TEXTURE       →  Generate accompaniment and bass with character-appropriate patterns
8.  EXPRESSION    →  Apply 1/f rubato, dynamics, and ornamentation scaled by character
```

Every later stage receives binding constraints from every earlier stage AND from the character vector. This dual constraint (hierarchical + character) produces both structural integrity and distinctive identity.

### 4.3 Inter-Section Character Modulation

**Definition 4.1.** Within each section, the effective character is a shifted version of the base character:

```
c_section(c, δ) = clamp(c + δ, 0, 1)
```

where δ is a section-specific offset vector. For instance, a B section in a Nocturne might have δ = (+0.15, +0.20, 0, -0.10, +0.15), creating a B section that is slightly brighter and more energetic than the A section.

| Section Role | Typical δ |
|--------------|-----------|
| A (home, first) | (0, 0, 0, 0, 0) |
| B (contrasting) | (+0.20, +0.10, +0.15, -0.10, +0.25) |
| C (further development) | (+0.30, 0, +0.20, -0.20, +0.30) |
| A' (return, modified) | (-0.10, 0, -0.10, +0.05, -0.10) |

---

## 5. Continuous Character Flow

### 5.1 Dynamic Character Evolution

Rather than treating character as constant within sections, we model it as a continuous trajectory evolving over the piece timeline. This allows natural drift, return, and climactic intensification.

**Definition 5.1.** Let **c**(t) = (e(t), d(t), x(t), l(t), v(t)) be the character vector as a continuous function of normalised time t ∈ [0, 1]. The character follows a first-order differential equation:

```
dc/dt = -μ · (c(t) - c_attractor) + perturbation(t)
```

where:
- **c_attractor** is the target character for the current section (fixed)
- **μ** is the viscosity/return rate (section-specific)
- **perturbation(t)** is a stochastic forcing term

### 5.2 Viscosity and Return Rate

The return rate governs how quickly the character "relaxes" back to the attractor:

```
μ(c) = 0.1 + (1 - volatility(c)) × 0.3
```

Range: 0.1–0.4. Low-volatility pieces (Lullaby, Nocturne) have high μ and return quickly to the attractor. High-volatility pieces (Rhapsody, Scherzo) have low μ and wander far before returning.

### 5.3 Section Boundaries and Perturbations

At section boundaries (e.g., A → B transition), an impulse perturbation is applied:

```
δ_section = c_section_offset(role)
c(t_boundary+) = c(t_boundary−) + δ_section
```

Between boundaries, the character evolves under the differential equation. This produces natural *drift* within sections and *contrast* between sections.

### 5.4 Effective Character at Bar Level

At each bar index i, compute the character as:

```
bars_since_section_start = i - i_section_start
t_into_section = bars_since_section_start / total_bars_in_section
c_eff(i) = c_attractor + (c_section_offset) × exp(-μ × bars_since_section_start)
           + pink_noise(t, scale=volatility)
```

The exponential term decays the section offset over time, naturally returning the character to the attractor. The pink noise term adds small, correlated micro-variations that maintain continuity.

### 5.5 Pink Noise for Micro-Variation

Within the continuous flow, small-scale character variation follows pink (1/f) statistics:

```
micro_variation(t) = pink_noise(t) × volatility(c)
```

Volatility scales the amplitude of micro-variations: high-volatility pieces exhibit larger character fluctuations; low-volatility pieces are steadier.

---

## 6. The Seed Motif: Rhythmic-Intervallic DNA

### 6.1 Motif as Development Foundation

**Definition 6.1.** The **seed motif** is a short sequence of 3–5 notes with fixed intervallic and rhythmic content. It is the atomic unit from which all melody is derived through transformation.

**Example (Nocturne-like):**
```
Intervals:  [0, +2, -3, +4]     (relative semitones)
Durations:  [1.0, 0.5, 0.5, 2.0] (beats)
```

### 6.2 Transformation Group

Melodic material is generated by applying transformations from the group T:

| Transform | Operation | Character Affinity |
|-----------|-----------|-------------------|
| **Identity** | Use motif as-is | All |
| **Inversion** | Negate intervals | High complexity, drama |
| **Retrograde** | Reverse interval order | High complexity, formal |
| **Augmentation** | Double all durations | Lyrical, slow |
| **Diminution** | Halve all durations | Energetic, technical |
| **Sequence** | Transpose and repeat | All, especially development |
| **Fragmentation** | Use subset of motif | Transitional, developmental |

### 6.3 Development Arc

Each phrase receives an assignment from T. Early phrases use Identity or Sequence. Middle phrases use Inversion, Retrograde, or Fragmentation. Late phrases return to Identity or modified Identity, providing closure.

---

## 7. Gravitational Harmony

### 7.1 The Functional Model

Chords arrange themselves around three functional poles in what we call **gravitational harmony**:

| Function | Symbol | Chord Example (C major) | Purpose |
|----------|--------|-------------------------|---------|
| **Tonic** | T | C major, A minor | Rest, resolution, stability |
| **Predominant** | P | F major, D minor | Tension build, preparation for dominant |
| **Dominant** | D | G major, G7 | Maximum tension, demands resolution |

### 7.2 Transition Matrix

Chords transition according to a weighted Markov chain:

```
Transition Probabilities (normalised):

        T    P    D
    T [ 0.1  0.6  0.3 ]
    P [ 0.3  0.2  0.5 ]
    D [ 0.8  0.1  0.1 ]
```

High probability of T → P and P → D (functional progression), D → T (authentic cadence), T → T (tonic stability). Transitions like T → D skip the predominant and create dramatic directness.

### 7.3 Harmonic Rhythm

The number of chords per bar depends on character:

```
harmonic_rhythm_rate(c) = 0.5 + x × 0.8 + e × 0.4
```

A low-complexity, low-energy piece might have 0.5–1 chord per bar (slow harmonic rhythm). A high-complexity, high-energy piece might have 1.5–2 chords per bar.

---

## 8. Harmonic Color Spectrum

### 8.1 Harmonic Color Index

**Definition 8.1.** The **Harmonic Color Index** is a composite measure governing harmonic vocabulary width:

```
H(c) = darkness(c) × 0.5 + complexity(c) × 0.5
```

Range: 0–1. This single scalar determines what chord types are available.

### 8.2 Vocabulary Strata

The harmonic vocabulary expands non-linearly with H:

```
H < 0.3:  Strictly diatonic
          Chords: I, ii, iii, IV, V, vi (major/minor borrowing at edges)
          Intervals: Perfect fourths, fifths, thirds, sixths

H ≥ 0.3:  + Secondary dominants (V/ii, V/iii, V/IV, V/V, V/vi)
          + Borrowed chords (iv, vi, bVII in major; VI, VII in minor)
          P(new chord) = max(0, (H − 0.3)) × 0.15

H ≥ 0.5:  + Neapolitan sixth (♭II6)
          + Tritone substitutions (vii°7 → I)
          P(new chord) = max(0, (H − 0.5)) × 0.12

H ≥ 0.65: + Augmented sixth chords (It6, Fr6, Ger6)
          P(new chord) = max(0, (H − 0.65)) × 0.10

H ≥ 0.75: + Chromatic mediants (iii → ♯iii, vi → ♯vi)
          P(new chord) = max(0, (H − 0.75)) × 0.08
```

### 8.3 Chord Type Specification

**Diatonic Triads (all levels):**
- I, vi: root–third–fifth (1–3–5 in pitch classes)
- IV, ii: root–third–fifth (4–6–1 and 2–4–7)
- V, iii: root–third–fifth (5–7–2 and 3–5–7)
- All voices fit within the active register envelope

**Secondary Dominants (H ≥ 0.3):**
- V/ii: 9–1–5 (one semitone above the II chord)
- V/IV: 0–4–7 functional equivalent
- Specified as major triads built on the fifth scale degree above each target chord

**Augmented Sixth Chords (H ≥ 0.65):**
- Italian (It6): I6 with raised 4th degree
- French (Fr6): I6 with raised 2nd and 4th degrees
- German (Ger6): I6 with raised 4th, duplicated root
- All specified in terms of semitone offsets from the home key

---

## 9. Rhythmic Identity

### 9.1 Time Signatures

The character vector selects the time signature (Definition 2.3). This is not cosmetic; it fundamentally alters the rhythmic feel:

- **4/4 (Common time):** 4 beats per bar. Strong beat on 1, secondary on 3. Default for marches, études, toccatas.
- **3/4 (Triple metre):** 3 beats per bar. Strong beat on 1. Natural for waltzes, minuets, mazurkas.
- **6/8 (Compound duple):** 6 eighth-note pulses grouped as 2 × 3. Flowing, lilting. Natural for nocturnes, barcarolles.

### 9.2 Character-Weighted Rhythm Cells

Rhythm cells are not sampled uniformly. Each cell has a character affinity score, and the sampling probability is weighted by how well the cell matches the current character:

**4/4 Cells (total = 4.0 beats):**
```
Cell                        Energy  Lyricism  Complexity
[1.0, 1.0, 1.0, 1.0]      0.3     0.3       0.1        (simple quarters)
[2.0, 2.0]                 0.2     0.7       0.1        (sustained halves)
[2.0, 1.0, 1.0]            0.4     0.5       0.2        (long-short-short)
[1.0, 1.0, 2.0]            0.3     0.5       0.2        (short-short-long)
[1.5, 0.5, 1.0, 1.0]       0.5     0.3       0.4        (dotted)
[0.5, 0.5, 0.5, 0.5, 2.0]  0.7     0.2       0.5        (running into long)
[0.5, 0.5, 1.0, 1.0, 1.0]  0.6     0.3       0.4        (eighth pickup)
[0.5, 0.5, 0.5, 0.5, 1.0, 1.0] 0.8  0.2      0.6        (running eighths)
```

**3/4 Cells (total = 3.0 beats):**
```
Cell                        Energy  Lyricism  Complexity
[1.0, 1.0, 1.0]            0.4     0.4       0.1        (simple waltz)
[2.0, 1.0]                 0.2     0.7       0.1        (sustained)
[1.0, 2.0]                 0.3     0.6       0.2        (pickup feel)
[1.5, 1.5]                 0.3     0.5       0.3        (hemiola hint)
[0.5, 0.5, 1.0, 1.0]       0.6     0.3       0.4        (running)
[1.0, 0.5, 0.5, 1.0]       0.5     0.3       0.4        (mixed)
```

**6/8 Cells (total = 3.0 compound beats = 6 eighth notes):**
```
Cell                        Energy  Lyricism  Complexity
[1.5, 1.5]                 0.2     0.8       0.1        (compound halves)
[1.0, 0.5, 1.0, 0.5]       0.3     0.7       0.2        (lilting)
[0.5, 0.5, 0.5, 0.5, 0.5, 0.5] 0.7 0.3      0.5        (full running)
[1.0, 0.5, 1.5]            0.3     0.6       0.3        (mixed compound)
```

The weight of each cell is computed as:
```
w(cell) = exp(-α × (|cell.energy - e|² + |cell.lyricism - l|² + |cell.complexity - x|²))
```
where α is a temperature parameter (~3.0). This ensures cells matching the character are strongly preferred.

---

## 10. Micro-Timing Groove

### 10.1 Groove Templates

Beyond character-level rhythm cells and rubato, **groove** provides systematic, beat-position-dependent micro-timing variation. Grooves are genre-specific and applied as an additional layer of timing modulation.

**Definition 10.1.** A **groove template** G is a vector of micro-offsets per beat position within a bar, measured in seconds:

```
groove = [offset_beat_0, offset_beat_1, ..., offset_beat_N-1]
```

### 10.2 Groove Template Library

Different archetypes have characteristic grooves:

**Waltz (3/4):**
```
groove = [0.0, -0.05, +0.03]
```
The second beat is slightly early (creates lilting feel), third beat slightly late.

**Mazurka (3/4):**
```
groove = [0.0, +0.08, +0.04]
```
Both weak beats are pushed forward (creates accent and drive).

**March (4/4):**
```
groove = [-0.02, 0.0, -0.02, 0.0]
```
Alternating beat patterns (even beats pushed back) create mechanical swagger.

**Nocturne (6/8):**
```
groove = [0.0, +0.03, +0.05, 0.0, -0.02, +0.01]
```
Gentle forward push on beats 2–3 and beats 5–6 (compound beats grouped).

**Toccata (4/4):**
```
groove = [-0.01, +0.01, -0.01, +0.01]
```
Tight alternation (machine-like precision).

### 10.3 Application

For each note event at beat position b within a bar at time t:

```
quantised_onset = t
groove_offset = groove[b mod len(groove)] × (60 / BPM)
actual_onset = quantised_onset + groove_offset
```

Groove offsets are **separate** from rubato. Rubato is stochastic and varies from bar to bar; groove is deterministic and repeats identically each bar.

---

## 11. Antecedent–Consequent Phrase Architecture

### 11.1 The Musical Period

**Definition 11.1.** A **period** is a pair of phrases where:

- The **antecedent** presents melodic material and ends on a Half Cadence (→ V), creating harmonic suspension.
- The **consequent** restates the material (often varied) and ends on a Perfect Authentic Cadence (→ I), providing closure.

This is the musical analogue of question and answer, statement and response.

### 11.2 Phrase Types

**Definition 11.2.** The **parallel period** uses the same opening motif in both phrases:
```
Antecedent:  [motif M] [continuation] → Half Cadence (V)
Consequent:  [motif M'] [new ending]  → Perfect Auth. Cadence (I)
```

**Definition 11.3.** The **contrasting period** uses different material:
```
Antecedent:  [motif M] [continuation]  → Half Cadence (V)
Consequent:  [motif N] [new ending]    → Perfect Auth. Cadence (I)
```

### 11.3 Phrase-Level Melodic Construction

Within each phrase, melody follows a contour arc:

1. **Presentation** (first half): the motif is stated, establishing pitch range and character.
2. **Continuation** (second half): the motif is developed (fragmented, sequenced, inverted), driving toward the cadence.

The cadential arrival is the most structurally important moment. The penultimate bar contains the highest tension (dominant preparation); the final bar resolves.

---

## 12. Hierarchical Form

### 12.1 Supported Forms

| Form | Structure | Character Affinity |
|------|-----------|-------------------|
| Binary | A – B | Short pieces, simple character |
| Rounded Binary | A – B – A' | Standard, most archetypes |
| Ternary | A – B – A | Clear contrast and return |
| Rondo | A – B – A – C – A | Longer pieces, high volatility |

The form is chosen based on piece length and character:
```
if num_bars ≤ 8:               Binary
elif num_bars ≤ 16:            Rounded Binary (ABA')
elif v > 0.6 and num_bars ≥ 24: Rondo (ABACA)
else:                          Ternary (ABA')
```

### 12.2 Section Properties

Each section carries:
- **Key centre** (may differ from home key for B/C sections)
- **Character offset δ** (Definition 4.1)
- **Thematic role** determining motif transform distribution
- **Dynamic base** from the macro arc

### 12.3 The A' Section (Modified Return)

The return of A material after contrast is never exact. A' sections:
1. Restate the opening motif in the home key.
2. May compress material (fewer bars).
3. End with a stronger cadence.
4. Often host the piece's dynamic climax in their penultimate phrase.

---

## 13. Ornamentation Algebra

### 13.1 Ornaments as Grammar Expansions

Ornamentation is not arbitrary decoration. Each ornament is a non-terminal in a context-free grammar, with expansion rules, probabilities, and structural constraints.

**Definition 13.1.** An **ornament** is a sequence of auxiliary notes that elaborates a main melodic note. Allowed ornament types are:

| Type | Example (on C4) | Character |
|------|-----------------|-----------|
| **Turn** | C–D–B–C | Lilting, flowing |
| **Trill** | C–B–C–B–C–B–C | Energetic, brilliant |
| **Mordent** | C–B–C | Sharp, incisive |
| **Grace Note** | B–C (fast) | Lyrical, sighing |
| **Appoggiatura** | D–C (tied) | Lyrical, expressive |

### 13.2 Expansion Rules and Probabilities

Each main melody note with duration ≥ 0.75 beats is a candidate for ornamentation. Expansion is non-terminal-specific:

```
P(turn)      = (lyricism × 0.3 + complexity × 0.2) × ornament_probability(p)
P(trill)     = (complexity × 0.3 + energy × 0.1) × ornament_probability(p)
P(mordent)   = (energy × 0.2 + complexity × 0.1) × ornament_probability(p)
P(grace)     = lyricism × 0.2 × ornament_probability(p)
P(appog)     = lyricism × 0.25 × ornament_probability(p)
P(none)      = 1 - sum of above
```

where `ornament_probability(p)` is the performance-space parameter from Definition 3.3.

### 13.3 Constraints

Ornaments obey strict structural rules:

1. **Duration constraint:** Only notes with duration ≥ 0.75 beats.
2. **No cadential ornamentation:** Penultimate and final phrase notes are never ornamented.
3. **Register constraint:** Ornaments must fit within the current register envelope (see §16).
4. **Harmonic constraint:** Ornament tones must be chord tones or diatonic passing tones; chromatic ornaments only when H(c) ≥ 0.5.

---

## 14. Tension Field

### 14.1 Composite Tension Scalar

A single scalar **T(t)** captures the current harmonic, melodic, and rhythmic tension:

```
T(t) = (w_h · T_harmonic(t) + w_m · T_melodic(t) +
        w_r · T_rhythmic(t) + w_reg · T_registral(t)) / (w_h + w_m + w_r + w_reg)
```

### 14.2 Tension Components

**Harmonic Tension:**
```
T_harmonic(t) = circle_of_fifths_distance(current_chord, I) / 12
```
Measured as steps on the circle of fifths from tonic (I). V = 1/5, IV = 4/5, vi = 2/5, ii = 3/5. Range: 0–1.

**Melodic Tension:**
```
T_melodic(t) = average(|pitch(i) - melody_centre(c)| / 12) +
               unresolved_leap_density(t) × 0.3
```
Combines distance from register centre and presence of unresolved large leaps. Range: 0–1.

**Rhythmic Tension:**
```
T_rhythmic(t) = syncopation_density(bar) × 0.5 +
                (1 - avg_note_duration(bar) / max_duration) × 0.5
```
High syncopation and short notes increase tension. Range: 0–1.

**Registral Tension:**
```
T_registral(t) = (current_register_width - base_width) / max_expansion
```
Difference between current melody spread and the baseline for the character. Range: 0–1.

### 14.3 Weights

Weights are computed from character:

```
w_h = 0.4
w_m = 0.2 + lyricism × 0.1       (melodic tension more important in lyrical pieces)
w_r = 0.2 + energy × 0.1          (rhythmic tension more important in energetic pieces)
w_reg = 0.2
```

### 14.4 Tension Gradient and Generation Feedback

The time derivative of tension provides feedback to the melody and harmony generator:

```
∇T = dT/dt
```

- If ∇T > 0, tension is rising → melody generator continues building climax, harmony sustains dominant preparation.
- If ∇T < 0, tension is falling → melody generator moves toward resolution, harmony shifts back to tonic.

This creates natural, tension-driven phrasing.

---

## 15. Register Geography

### 15.1 Register Envelope

**Definition 15.1.** The **register envelope** RE(t) = [low(t), high(t)] specifies the permissible melodic pitch range at time t:

```
melody_base_range = melody_centre(c) ± 7 semitones
melody_expansion(t) = tension(t) × expansion_factor + energy(c) × 3 semitones
melody_high(t) = melody_centre(c) + 7 + melody_expansion(t)
melody_low(t) = melody_centre(c) - 7
```

where `expansion_factor = 5` semitones per unit tension.

### 15.2 Climactic Expansion

At the piece climax (identified by peak of the macro dynamic arc), the register envelope snaps to maximum width:

```
at_climax:  melody_high = melody_centre + 24 semitones
            melody_low = melody_centre - 12 semitones
```

### 15.3 Register Breathing

Outside the climax, the envelope "breathes" — expanding and contracting with tension:

```
RE_actual(t) = RE_base + tension_gradient_direction × breathing_magnitude
```

This creates the audible effect of the piece "opening up" during development and "closing in" at resting points.

---

## 16. Thematic Memory and Recall

### 16.1 Familiarity Decay

**Definition 16.1.** The **familiarity** of a motif at time t after its last occurrence at t_last is:

```
F_m(t) = F_0 · exp(-λ · (t - t_last))
```

where F_0 = 1.0 (fully fresh at t_last) and λ is a decay rate.

### 16.2 Recall Pressure

**Definition 16.2.** The **recall pressure** R(t) measures how much the listener/generator expects to hear the motif again:

```
R(t) = max(0, θ - F_m(t))
```

where θ is a familiarity threshold:

```
θ(c) = 0.6 - volatility(c) × 0.3
```

Range: 0.3–0.6. Highly volatile pieces (Rhapsody, Fantasia) have low θ and tolerate longer periods without recall. Stable pieces (Lullaby, Waltz) have high θ and require frequent motif returns.

### 16.3 Adaptive Forgetting

The decay rate λ is not constant. Each time a motif is recalled, the decay slows (memory "strengthens"):

```
recall_number = how many times m has been recalled
λ_current = λ_base / (1 + recall_number × 0.3)
```

This creates the perceptual effect of a motif becoming increasingly "rooted" in the listener's mind.

### 16.4 Recall Bias in Phrase Planning

When R(t) > 0, the phrase planner biases toward generating phrases that are:
- **Identity** transforms of the motif (direct recall)
- **Fragment** transforms (partial recall, recognisable)

When R(t) ≤ 0, the planner is free to develop new material, defer recall, or introduce new themes.

---

## 17. Self-Listening Feedback Loop

### 17.1 Post-Phrase Analysis

After generating each phrase, the system measures what was actually generated:

```
actual_pitch_range = max_pitch - min_pitch (in the phrase)
actual_avg_velocity = mean(velocity values in phrase)
actual_rhythmic_density = count(notes) / phrase_duration
```

### 17.2 Target Parameters from Character

Compare against what the character specifies:

```
target_pitch_range(c) = (7 + energy(c) × 5) semitones
target_avg_velocity(c) = base_velocity(c) + velocity_range(c) / 2
target_rhythmic_density(c) = (1 + complexity(c) × 2) notes/beat
```

### 17.3 Error Correction

Compute error:

```
e_range = actual_pitch_range - target_pitch_range
e_velocity = actual_avg_velocity - target_avg_velocity
e_density = actual_rhythmic_density - target_rhythmic_density
```

Apply correction to the next phrase:

```
correction_bias = -α × [e_range, e_velocity, e_density]
```

where α = 0.3 (learning rate). This is applied by:
- Widening the register envelope if e_range was too narrow
- Adjusting target velocity for the next phrase
- Increasing/decreasing the tendency to select dense vs. sparse rhythm cells

### 17.4 Closed-Loop Benefit

This converts MIL from an open-loop (generate and hope) system to a closed-loop (generate, observe, correct) system. Over multiple phrases, actual output naturally converges toward character targets.

---

## 18. Voice Texture and Accompaniment

### 18.1 Voice Roles

| Voice | Register | Function |
|-------|----------|----------|
| Melody | C4–C6 (adjusted by character) | Primary thematic content |
| Accompaniment | G3–G5 | Harmonic support, rhythmic motion |
| Bass | C2–C4 | Harmonic foundation, root motion |

### 18.2 Character-Driven Accompaniment Patterns

The accompaniment pattern is selected per section by weighted sampling from the character-derived distribution (§2.3):

| Pattern | Description | Character Affinity |
|---------|------------|-------------------|
| Alberti | low–high–mid–high broken chord | Lyrical, classical |
| Arpeggiated | Root–3rd–5th–8va ascending | Flowing, expansive |
| Block | Simultaneous chord tones on beats | Bold, hymn-like |
| Waltz | Bass beat 1, chord beats 2–3 | Triple metre, dance |
| Stride | Bass octave beat 1, chord beat 2 | Rhythmic, propulsive |
| Tremolo | Rapid alternation of chord pairs | Dramatic, agitated |

### 18.3 Voice Independence

**Definition 18.1.** The **voice independence** scalar K governs how tightly the accompaniment and bass are locked to each other:

```
K(c) = (1 - lyricism(c)) × 0.5 + complexity(c) × 0.3 + volatility(c) × 0.2
```

Range: 0–1.

- **K < 0.3:** Homophonic lockstep. All voices move together on beats. Waltz, March.
- **K > 0.6:** Polyphonic independence. Each voice has its own rhythm. Étude, Toccata.
- **K ≈ 0.5:** Moderate independence. Movement partly synchronized, partly independent.

### 18.4 Cadential Unification

Regardless of K, at cadences (penultimate and final bars of phrases), all voices converge:

```
at_cadence: all voices synchronise to chord tones on strong beats
```

This ensures harmonic clarity at structurally critical moments.

---

## 19. 1/f Expressive Surface

### 19.1 The Pink Noise Model

Human musical expression follows a 1/f (pink noise) power spectral density. This means adjacent notes have correlated timing deviations (local smoothness), there are long-range correlations (gradual tempo arcs), and the deviations are neither periodic nor random.

### 19.2 Implementation via Voss–McCartney

```
state = [random() for each octave 0..N]
counter = 0

function step():
    counter += 1
    k = number of trailing zeros in binary(counter)
    state[min(k, N-1)] = random()
    return mean(state)
```

### 19.3 Character-Scaled Application

The magnitude of expressive variation is scaled by character:

**Tempo rubato:**
```
rubato_magnitude(c) = 0.04 + lyricism(c) × 0.06 + (1 - energy(c)) × 0.02
```
Range: ~4–12% BPM deviation. Lyrical, slow pieces get more rubato; fast, energetic pieces get less.

**Dynamic variation:**
```
dynamic_magnitude(c) = 10 + volatility(c) × 15 + energy(c) × 8
```
Range: ~10–33 MIDI velocity units. Volatile, energetic pieces get wider dynamic swings.

---

## 20. Macro Dynamic Arc

### 20.1 The Intensity Curve

**Definition 20.1.** The **macro dynamic arc** I(t) maps normalised position t ∈ [0, 1] to an intensity level I ∈ [0, 1].

| Arc Type | Shape | Character Affinity |
|----------|-------|-------------------|
| Arch | Rises to ~70%, descends | Low volatility (default) |
| Ramp | Gradual rise to climax near end | High energy |
| Double Arch | Two peaks | Long pieces, high volatility |

The arc type is selected by character:
```
if volatility > 0.6:    double_arch
elif energy > 0.65:     ramp
else:                   arch
```

### 20.2 Interaction with Form and Character

The macro arc modulates section dynamics: B sections sit at the arc's peak region, A' sections begin the descent. The arc's amplitude is scaled by the character's energy and volatility.

---

## 21. The Complete Generation Algorithm

```
function MIL_GENERATE(num_bars, key_root, scale_type, bpm_target, character, performance):

    # ── Level 0: Character and Performance ──
    params = CHARACTER_MAP(character)
    metre = params.time_signature
    beats_per_bar = params.beats_per_bar

    perf_params = PERFORMANCE_MAP(performance)
    rubato_scale = perf_params.rubato_scale
    attack_sharpness = perf_params.attack_sharpness
    soprano_bias = perf_params.soprano_bias

    # ── Level 5: Form ──
    form = SELECT_FORM(num_bars, character)
    sections = PLAN_SECTIONS(form, num_bars, key_root, scale_type, character)

    # ── Level 4: Seed Motif ──
    motif = GENERATE_SEED_MOTIF(character, beats_per_bar)

    # ── Level 3: Expression Surface ──
    expression = COMPUTE_EXPRESSION_MAP(num_bars, bpm_target, character, rubato_scale)
    macro_arc = COMPUTE_MACRO_ARC(num_bars, form, character)

    # ── Continuous Character Flow ──
    character_trajectory = COMPUTE_CHARACTER_FLOW(sections, character)

    # ── Tension Field and Register Geography ──
    tension_field = COMPUTE_TENSION_FIELD(sections, character)
    register_env = COMPUTE_REGISTER_ENVELOPE(character)

    # ── Thematic Memory ──
    memory_tracker = THEMATIC_MEMORY(motif)

    all_events = []
    feedback_accumulator = [0, 0, 0]  # range, velocity, density errors

    for section_idx, section in enumerate(sections):
        # Effective character from continuous flow
        c_eff = character_trajectory[section_idx]

        # Recall pressure from memory
        recall_pressure = memory_tracker.pressure(section_idx)

        section_key = section.key_root
        section_scale = section.scale_type

        # Choose accompaniment pattern weighted by character
        accomp_pattern = SAMPLE_ACCOMPANIMENT(c_eff)

        # Choose groove template from archetype
        groove = SELECT_GROOVE_TEMPLATE(c_eff)

        # ── Level 2: Periods and Phrases ──
        phrases = PLAN_PHRASES(section, motif, c_eff, recall_pressure,
                               feedback_accumulator)

        for phrase_idx, phrase in enumerate(phrases):
            # ── Harmony ──
            chords = GENERATE_PROGRESSION(
                section_key, section_scale,
                cadence_type = phrase.cadence_type,
                character = c_eff,
                tension = tension_field[section_idx][phrase_idx]
            )

            # ── Level 1: Note Content ──
            melody = GENERATE_MELODY(
                chords, motif, phrase, expression, macro_arc, c_eff,
                register_env, tension_field[section_idx][phrase_idx],
                character_trajectory[section_idx]
            )

            accomp = GENERATE_ACCOMPANIMENT(
                chords, accomp_pattern, phrase, expression, macro_arc,
                c_eff, metre, groove, attack_sharpness
            )

            bass = GENERATE_BASS(
                chords, phrase, expression, macro_arc, c_eff, groove
            )

            # ── Ornamentation ──
            melody = APPLY_ORNAMENTATION(melody, c_eff, performance.ornamental_impulse)

            all_events += melody + accomp + bass

            # ── Self-Listening Feedback ──
            actual_range = max(m.pitch for m in melody) - min(m.pitch for m in melody)
            actual_velocity = mean(m.velocity for m in melody)
            actual_density = len([m for m in melody if m.duration < 1.0]) / phrase.duration

            target_range = (7 + c_eff.energy × 5)
            target_velocity = params.base_velocity + params.velocity_range / 2
            target_density = (1 + c_eff.complexity × 2)

            feedback_accumulator[0] = actual_range - target_range
            feedback_accumulator[1] = actual_velocity - target_velocity
            feedback_accumulator[2] = actual_density - target_density

            # Update memory
            memory_tracker.recall(phrase_idx)

    # ── Apply Performance Mapping ──
    for event in all_events:
        # Soprano bias
        if event.is_melody:
            event.velocity += soprano_bias

        # Attack sharpness
        if event.duration > attack_sharpness:
            event.duration -= attack_sharpness * event.duration

    return all_events
```

---

## 22. Formal Properties

**Theorem 22.1 (Guaranteed Closure).** Every generated piece ends on a Perfect Authentic Cadence in the home key.

*Proof.* The final section is always an A or A' section in the home key. Its final phrase is a consequent phrase. By Definition 11.1, consequent phrases end with a PAC. ∎

**Theorem 22.2 (Thematic Unity).** Every melodic phrase is derivable from the seed motif via the transformation group T.

*Proof.* The melody generator receives a motif transformation assignment for each phrase (§6.2). All melodic material is generated by applying the assigned transformation and then fitting to the current harmony. ∎

**Theorem 22.3 (Harmonic Coherence).** Every chord progression satisfies the functional gravity law T → P → D → T.

*Proof.* Chords are generated by weighted walk on the transition matrix (§7.2), which assigns near-zero weight to non-functional transitions. Cadence patterns are predetermined by phrase type. ∎

**Theorem 22.4 (Character Consistency).** For any fixed character vector c, every stochastic choice in the generation pipeline is biased toward the same expressive direction defined by c.

*Proof.* By construction of the character mapping Φ (§2.3), every parameter governing tempo, motif, harmony, rhythm, accompaniment, dynamics, and register is a continuous function of c. Since all generative modules consume these parameters, and the parameters are jointly determined by the same c, every stochastic choice samples from a distribution shaped by the same expressive bias. ∎

**Theorem 22.5 (Distinctiveness).** For two character vectors c₁ and c₂ with ‖c₁ − c₂‖ > ε, the generated pieces differ in expected tempo, rhythmic profile, harmonic vocabulary, and textural pattern.

*Proof.* Each generation parameter is a continuous function of c with nonzero gradient in at least one dimension. When ‖c₁ − c₂‖ > ε, the parameter sets P₁ = Φ(c₁) and P₂ = Φ(c₂) differ, producing different sampling distributions at every level. ∎

**Theorem 22.6 (Performance Interaction).** The perceptual distinctiveness between two performances of the same piece is maximised when character and performance vectors are orthogonal in their influence.

*Proof Sketch.* Character space C controls composition; performance space P controls interpretation. When variations are independent (orthogonal), their effects on the final sound are multiplicative rather than cancelling. ∎

---

## 23. Implementation Specifications

### 23.1 Data Structures

```python
@dataclass
class Character:
    energy: float      # 0.0–1.0
    darkness: float    # 0.0–1.0
    complexity: float  # 0.0–1.0
    lyricism: float    # 0.0–1.0
    volatility: float  # 0.0–1.0

@dataclass
class Performance:
    rubato_freedom: float      # 0.0–1.0
    attack_profile: float      # 0.0–1.0
    pedal_saturation: float    # 0.0–1.0
    dynamic_exaggeration: float # 0.0–1.0
    voice_highlighting: float  # 0.0–1.0
    ornamental_impulse: float  # 0.0–1.0

@dataclass
class SeedMotif:
    intervals: list[int]        # signed semitone intervals
    durations: list[float]      # beat durations per note

@dataclass
class Section:
    key_root: int               # 0–11
    scale_type: str             # 'major' or 'minor'
    num_bars: int
    is_return: bool
    role: str                   # 'A', 'B', 'C', 'A_prime'
    dynamic_base: float         # 0.0–1.0
    char_offset: tuple[float]   # 5-tuple delta to character

@dataclass
class Phrase:
    start_bar: int
    num_bars: int
    cadence_type: str           # 'half' or 'authentic'
    motif_transform: str        # from T
    is_consequent: bool

@dataclass
class MILEvent:
    pitch: int
    duration_beats: float
    velocity: int
    beat_position: float
    time_seconds: float
    duration_seconds: float
    is_melody: bool
    is_bass: bool
    is_accompaniment: bool
    voice_id: int               # 0=melody, 1=accomp, 2=bass
```

### 23.2 Parameter Table

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Character dimensions | 5 | Minimal basis spanning musical identity |
| Performance dimensions | 6 | Comprehensive pianist identity model |
| Seed motif length | 3–5 notes | Long enough for identity, short enough for development |
| Phrase length | 3–4 bars | Standard classical phrase |
| Period length | 6–8 bars | Antecedent + consequent |
| Harmonic rhythm | 1 chord/bar (subdivided at cadences) | Standard |
| Melody range | C4–C6 (±character offset) | Comfortable piano treble |
| Bass range | C2–C4 (±character offset) | Comfortable piano bass |
| Rubato magnitude | 4–12% BPM (character-scaled) | Perceptible, not disorienting |
| Dynamic variation | 10–33 velocity units (character-scaled) | Expressive, not extreme |
| Leap resolution threshold | 5 semitones | Perfect fourth requires stepwise resolution |
| Character viscosity μ | 0.1–0.4 | Controls character drift during sections |
| Tension weight balance | h:m:r:reg = 0.4:0.2–0.3:0.2–0.3:0.2 | Harmonic tension dominates |
| Register expansion | 5 semitones per unit tension | Climactic breathing |
| Motif recall threshold θ | 0.3–0.6 | Volatility-dependent |
| Feedback learning rate α | 0.3 | Moderate correction per phrase |

---

*End of MIL Theory Document*
