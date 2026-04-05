"""
piano_engine.py — Real‑time additive‑synthesis piano audio engine.

Each note is built from a fundamental frequency plus up to ~22 harmonics
whose amplitudes follow a 1/n^α roll‑off that varies by register.  The
harmonics are slightly stretched by an inharmonicity coefficient *B* to
mimic real piano‑string physics.

Per‑harmonic decay (higher partials fade faster) produces the natural
"brightness → warmth" evolution of a decaying piano tone.  A short
filtered‑noise burst at attack simulates hammer impact.

Audio is rendered in a sounddevice OutputStream callback and mixed in
stereo with gentle position‑dependent panning.
"""

from __future__ import annotations

import threading
import numpy as np
import sounddevice as sd

from config import (
    SAMPLE_RATE, BUFFER_SIZE, AUDIO_CHANNELS, MAX_POLYPHONY,
    MASTER_VOLUME_DEFAULT, FIRST_MIDI, LAST_MIDI,
    ATTACK_TIME, RELEASE_TIME,
    SOFT_PEDAL_VOLUME, SOFT_PEDAL_CUTOFF,
    midi_to_frequency, get_inharmonicity, get_num_harmonics,
    get_decay_time, get_harmonic_rolloff, get_stereo_pan,
)


# ═══════════════════════════════════════════════════════════════
#  NoteState — per‑voice state
# ═══════════════════════════════════════════════════════════════

class NoteState:
    """Represents a single sounding piano note."""

    __slots__ = (
        "midi_note", "velocity", "pan",
        "frequencies", "base_amplitudes", "current_amplitudes",
        "harmonic_decay_rates", "phases",
        "envelope_level", "attacking", "releasing", "finished",
        "attack_rate", "release_rate",
        "soft_active",
        "hammer_samples_left",
    )

    def __init__(self, midi_note: int, velocity: float = 1.0,
                 soft: bool = False) -> None:
        self.midi_note = midi_note
        self.velocity  = velocity
        self.soft_active = soft
        self.pan = get_stereo_pan(midi_note)

        f0        = midi_to_frequency(midi_note)
        B         = get_inharmonicity(midi_note)
        n_harm    = get_num_harmonics(midi_note)
        alpha     = get_harmonic_rolloff(midi_note)
        decay_t   = get_decay_time(midi_note)

        if soft:
            n_harm = max(3, int(n_harm * SOFT_PEDAL_CUTOFF))

        ns = np.arange(1, n_harm + 1, dtype=np.float64)

        # Stretched partial frequencies  f_n = n·f0·sqrt(1 + B·n²)
        self.frequencies = ns * f0 * np.sqrt(1.0 + B * ns * ns)

        # Ensure no partials above Nyquist
        valid = self.frequencies < (SAMPLE_RATE / 2.0)
        self.frequencies     = self.frequencies[valid]
        ns                   = ns[: len(self.frequencies)]
        n_harm               = len(self.frequencies)

        # Amplitudes: 1/n^alpha, with subtle per‑note random detuning
        self.base_amplitudes    = 1.0 / (ns ** alpha)
        self.current_amplitudes = self.base_amplitudes.copy()

        # Per‑harmonic decay  (higher harmonics die faster)
        base_rate = 1.0 / decay_t
        self.harmonic_decay_rates = base_rate * (1.0 + 0.35 * (ns - 1))

        # Phase accumulators
        self.phases = np.random.uniform(0, 2 * np.pi, n_harm)

        # Envelope
        self.envelope_level = 0.0
        self.attacking      = True
        self.releasing       = False
        self.finished        = False
        self.attack_rate     = 1.0 / max(1, int(ATTACK_TIME * SAMPLE_RATE))
        self.release_rate    = np.exp(-1.0 / (RELEASE_TIME * SAMPLE_RATE))

        # Hammer noise duration (samples)
        self.hammer_samples_left = int(0.008 * SAMPLE_RATE)   # 8 ms

    # ── render one buffer ───────────────────────────────────────
    def render(self, frames: int) -> np.ndarray:
        """Return *frames* mono samples for this note."""

        if self.finished or len(self.frequencies) == 0:
            return np.zeros(frames, dtype=np.float64)

        # --- waveform (vectorised over harmonics) ---
        t  = np.arange(frames, dtype=np.float64) / SAMPLE_RATE          # (F,)
        fr = self.frequencies[:, np.newaxis]                              # (H,1)
        ph = self.phases[:, np.newaxis]                                   # (H,1)
        am = self.current_amplitudes[:, np.newaxis]                       # (H,1)

        sines  = am * np.sin(2.0 * np.pi * fr * t + ph)                  # (H,F)
        signal = sines.sum(axis=0)                                        # (F,)

        # Update phases (wrap to avoid float‐precision loss)
        self.phases += 2.0 * np.pi * self.frequencies * frames / SAMPLE_RATE
        self.phases %= (2.0 * np.pi)

        # --- per‑harmonic amplitude decay ---
        decay_factors = np.exp(-self.harmonic_decay_rates * frames / SAMPLE_RATE)
        self.current_amplitudes *= decay_factors

        # --- hammer noise (first few ms) ---
        if self.hammer_samples_left > 0:
            n_noise = min(frames, self.hammer_samples_left)
            noise   = np.random.randn(n_noise) * 0.12
            # Simple 5‑tap moving‑average lowpass
            kernel  = np.ones(5) / 5.0
            noise   = np.convolve(noise, kernel, mode="same")
            env     = np.exp(-np.arange(n_noise, dtype=np.float64)
                             / (0.003 * SAMPLE_RATE))
            signal[:n_noise] += noise * env
            self.hammer_samples_left -= n_noise

        # --- envelope (sample‑by‑sample for state transitions) ---
        envelope = np.empty(frames, dtype=np.float64)
        lvl = self.envelope_level
        for i in range(frames):
            if self.attacking:
                lvl += self.attack_rate
                if lvl >= 1.0:
                    lvl = 1.0
                    self.attacking = False
            elif self.releasing:
                lvl *= self.release_rate
                if lvl < 0.0003:
                    lvl = 0.0
                    self.finished = True
            # Sustain / natural‑decay: envelope stays at current level;
            # amplitude decrease is handled by per‑harmonic decay above.
            envelope[i] = lvl
        self.envelope_level = lvl

        # --- apply envelope & velocity ---
        vel_mod = self.velocity * (SOFT_PEDAL_VOLUME if self.soft_active else 1.0)
        signal *= envelope * vel_mod

        # Silence check (entire note has essentially died)
        if np.max(self.current_amplitudes) < 0.0001 and not self.attacking:
            self.finished = True

        return signal

    def start_release(self) -> None:
        if not self.releasing:
            self.releasing = True


# ═══════════════════════════════════════════════════════════════
#  PianoEngine — manages voices and the audio stream
# ═══════════════════════════════════════════════════════════════

class PianoEngine:
    """Additive‑synthesis piano with real‑time audio output."""

    def __init__(self) -> None:
        self.lock          = threading.Lock()
        self.active_notes: dict[int, NoteState] = {}   # midi → NoteState
        self.master_volume = MASTER_VOLUME_DEFAULT
        self.stream: sd.OutputStream | None = None

    # ── lifecycle ───────────────────────────────────────────────
    def start(self) -> None:
        """Open the audio output stream."""
        self.stream = sd.OutputStream(
            samplerate=SAMPLE_RATE,
            blocksize=BUFFER_SIZE,
            channels=AUDIO_CHANNELS,
            dtype="float32",
            callback=self._audio_callback,
            latency="low",
        )
        self.stream.start()

    def stop(self) -> None:
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None

    # ── note control ────────────────────────────────────────────
    def note_on(self, midi_note: int, velocity: float = 1.0,
                soft: bool = False) -> None:
        with self.lock:
            # Retrigger: release old voice, start new
            if midi_note in self.active_notes:
                self.active_notes[midi_note].start_release()
            self.active_notes[midi_note] = NoteState(midi_note, velocity, soft)
            self._enforce_polyphony()

    def note_off(self, midi_note: int, sustain: bool = False) -> None:
        with self.lock:
            note = self.active_notes.get(midi_note)
            if note and not sustain:
                note.start_release()

    def release_all_sustained(self) -> None:
        """Release every note that isn't already releasing (pedal lift)."""
        with self.lock:
            for note in self.active_notes.values():
                if not note.releasing:
                    note.start_release()

    def get_active_midi_notes(self) -> set[int]:
        with self.lock:
            return set(self.active_notes.keys())

    # ── volume ──────────────────────────────────────────────────
    def adjust_volume(self, delta: float) -> None:
        self.master_volume = max(0.0, min(1.0, self.master_volume + delta))

    # ── internal ────────────────────────────────────────────────
    def _enforce_polyphony(self) -> None:
        """Drop the quietest voices when exceeding MAX_POLYPHONY."""
        while len(self.active_notes) > MAX_POLYPHONY:
            quietest = min(self.active_notes,
                           key=lambda m: self.active_notes[m].envelope_level)
            del self.active_notes[quietest]

    def _audio_callback(self, outdata: np.ndarray, frames: int,
                         time_info, status) -> None:
        """sounddevice callback — runs in a dedicated audio thread."""
        if status:
            pass  # under‑run / over‑run; keep going

        left  = np.zeros(frames, dtype=np.float64)
        right = np.zeros(frames, dtype=np.float64)

        with self.lock:
            dead: list[int] = []
            for midi, note in self.active_notes.items():
                mono = note.render(frames)
                # Stereo pan (constant‑power)
                pan = note.pan
                l_gain = np.sqrt(0.5 * (1.0 - pan))
                r_gain = np.sqrt(0.5 * (1.0 + pan))
                left  += mono * l_gain
                right += mono * r_gain
                if note.finished:
                    dead.append(midi)
            for midi in dead:
                del self.active_notes[midi]

        # Master volume
        left  *= self.master_volume
        right *= self.master_volume

        # Soft limiter — prevents harsh digital clipping
        _soft_limit(left)
        _soft_limit(right)

        outdata[:, 0] = left.astype(np.float32)
        outdata[:, 1] = right.astype(np.float32)


def _soft_limit(buf: np.ndarray, threshold: float = 0.85) -> None:
    """In‑place soft‑clip: gentle tanh saturation above *threshold*."""
    mask = np.abs(buf) > threshold
    if mask.any():
        sign = np.sign(buf[mask])
        excess = np.abs(buf[mask]) - threshold
        buf[mask] = sign * (threshold + (1.0 - threshold)
                            * np.tanh(excess / (1.0 - threshold)))
