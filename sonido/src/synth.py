"""
Sonido y Karaoke — cumbia sonidera original sintetizada con numpy (sin samples).
Cumbia sonidera, 96 BPM, La menor.
uso: python3 synth.py <menu|intro|cierre> out.wav
"""
import sys, wave
import numpy as np

SR = 48000
BPM = 96
BEAT = 60.0 / BPM
STEP = BEAT / 4
BAR = BEAT * 4

PIECES = {
    'sonido': (['build'] + ['g'] * 10 + ['final'], ['E', 'Am', 'Am', 'G', 'F', 'E', 'Am', 'G', 'F', 'E/Am', 'G/E', 'Am']),   # bar types and chords (one per bar; 'Bb/C' splits the bar)
    'menu':   (['build', 'g', 'g', 'g', 'g', 'g', 'g', 'final'], ['C', 'F', 'C', 'Dm', 'Bb', 'F', 'Bb/C', 'F']),
    'intro':  (['build', 'final'], ['C', 'F']),
    'cierre': (['g', 'final'], ['Bb/C', 'F']),
}
piece = sys.argv[1]
TYPES, CHORDS = PIECES[piece]
NB = len(TYPES)
DUR = NB * BAR
N = int(round(SR * DUR))
rng = np.random.default_rng(1234)

def T(bar, step=0.0): return bar * BAR + step * STEP
def mtof(m): return 440.0 * 2 ** ((m - 69) / 12.0)
def tt(n): return np.arange(n) / SR

class Bus:
    def __init__(self): self.L = np.zeros(N); self.R = np.zeros(N)
    def add(self, sig, t, gain=1.0, pan=0.0):
        i = int(round(t * SR))
        if sig.ndim == 1:
            a = (pan + 1) * np.pi / 4; sl, sr = sig * np.cos(a) * 1.4142, sig * np.sin(a) * 1.4142
        else: sl, sr = sig[0], sig[1]
        if i < 0: sl, sr = sl[-i:], sr[-i:]; i = 0
        if i >= N: return
        n = min(len(sl), N - i)
        self.L[i:i+n] += sl[:n] * gain; self.R[i:i+n] += sr[:n] * gain
    def st(self): return np.stack([self.L, self.R])

drums, perc, bass, keys, lead, fx, send = (Bus() for _ in range(7))

def biquad(x, kind, f, q=0.707):
    w = 2 * np.pi * f / SR; c, s = np.cos(w), np.sin(w); al = s / (2 * q)
    b = {'lp': [(1 - c) / 2, 1 - c, (1 - c) / 2], 'hp': [(1 + c) / 2, -(1 + c), (1 + c) / 2], 'bp': [al, 0, -al]}[kind]
    a = [1 + al, -2 * c, 1 - al]
    b0, b1, b2, a1, a2 = b[0] / a[0], b[1] / a[0], b[2] / a[0], a[1] / a[0], a[2] / a[0]
    y = np.zeros_like(x); x1 = x2 = y1 = y2 = 0.0
    for i in range(len(x)):
        xi = x[i]; yi = b0 * xi + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
        x2, x1, y2, y1 = x1, xi, y1, yi; y[i] = yi
    return y

def svf_lp(x, fc, q=0.8):
    y = np.zeros_like(x); low = band = 0.0; damp = 1.0 / q
    f = 2 * np.sin(np.pi * np.minimum(fc, SR / 6) / SR)
    for i in range(len(x)):
        low += f[i] * band; high = x[i] - low - damp * band; band += f[i] * high; y[i] = low
    return y

def fade(sig, fin=0.002, fout=0.01):
    n = len(sig); e = np.ones(n); a, b = int(fin * SR), int(fout * SR)
    if a: e[:a] = np.linspace(0, 1, a)
    if b: e[-b:] *= np.linspace(1, 0, b)
    return sig * e

def additive(freq, n, weight_fn, odd=False, phase=0.0):
    t = tt(n); out = np.zeros(n)
    for k in range(1, int(SR * 0.45 / freq) + 1, 2 if odd else 1):
        w = weight_fn(k * freq)
        if np.max(np.abs(w)) < 1e-3 / max(1, k): continue
        out += np.sin(2 * np.pi * k * freq * t + phase * k) * w / k
    return out

# ------------------------------------------------------------ instruments
def kick(punch=1.0, dur=0.38):
    n = int(dur * SR); t = tt(n)
    f = 48 + 160 * np.exp(-t * 32) + 50 * np.exp(-t * 300)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7.5) * (1 - np.exp(-t * 2000))
    click = biquad(rng.standard_normal(n), 'hp', 3000) * np.exp(-t * 450) * 0.3
    return fade(np.tanh((body + click) * 1.7 * punch) * 0.9, 0, 0.02)

def guiro(long=True):
    """scrape: ridged noise burst"""
    dur = 0.17 if long else 0.06
    n = int(dur * SR); t = tt(n)
    nz = biquad(biquad(rng.standard_normal(n), 'bp', 3800, 1.2), 'hp', 1800)
    ridge_rate = 70 if long else 95
    ridges = 0.35 + 0.65 * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * ridge_rate * t)))
    env = np.minimum(1, t / 0.01) * (np.exp(-np.maximum(0, t - dur * 0.75) * 60))
    return fade(nz * ridges * env * 0.9, 0.002, 0.008)

def conga(freq, slap=False):
    n = int(0.3 * SR); t = tt(n)
    f = freq * (1 + 0.25 * np.exp(-t * 60))
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * (18 if slap else 9))
    hit = biquad(rng.standard_normal(n), 'bp', 2200 if slap else 900, 0.8) * np.exp(-t * (90 if slap else 160))
    return fade(tone * 0.8 + hit * (0.9 if slap else 0.4), 0, 0.02)

def timbal(freq=520):
    n = int(0.25 * SR); t = tt(n)
    s = sum(np.sin(2 * np.pi * freq * r * t) * g for r, g in ((1, 1), (1.47, .5), (2.09, .3)))
    s = s * np.exp(-t * 14) + biquad(rng.standard_normal(n), 'hp', 4000) * np.exp(-t * 60) * 0.5
    return fade(s * 0.5, 0, 0.02)

def clap():
    n = int(0.3 * SR); t = tt(n); nz = biquad(rng.standard_normal(n), 'bp', 1400, 0.9); e = np.zeros(n)
    for off in (0, 0.008, 0.017, 0.024): e += np.where(t >= off, np.exp(-(t - off) * 190), 0)
    e += np.where(t >= 0.024, np.exp(-(t - 0.024) * 18) * 0.5, 0)
    return fade(nz * e * 1.5, 0, 0.03)

def shaker():
    n = int(0.06 * SR); t = tt(n)
    return fade(biquad(rng.standard_normal(n), 'hp', 6500) * np.sin(np.pi * t / 0.06) ** 2 * 0.4)

def accordion(m, dur, vel=1.0):
    """musette reeds: three detuned reeds, formant shaped, bellows envelope + tremolo"""
    n = int(dur * SR); t = tt(n); f = mtof(m)
    form = lambda fr: (1.0 / np.sqrt(1 + (fr / 3800) ** 4)) * (0.6 + 0.9 * np.exp(-((fr - 1300) / 700) ** 2))
    s = np.zeros(n)
    for det, g in ((1.0, 1.0), (1.0045, 0.8), (0.9962, 0.7)):
        s += additive(f * det, n, form, odd=False, phase=rng.uniform(0, 6)) * g
    # nasal odd-heavy reed underneath
    s += additive(f, n, form, odd=True) * 0.5
    env = np.minimum(1, t / 0.018) * np.clip((dur - t) / 0.03, 0, 1)
    env *= 1 + 0.08 * np.sin(2 * np.pi * 5.5 * t)
    return fade(np.tanh(s * 0.9) * env * 0.33 * vel, 0.002, 0.01)

def bass_note(m, dur):
    n = int(dur * SR); t = tt(n); f = mtof(m)
    cut = 250 + 1100 * np.exp(-t * 25)
    s = additive(f, n, lambda fr: 1 / np.sqrt(1 + (fr / cut) ** 6))
    s += np.sin(2 * np.pi * f / 2 * t) * 0.6 * 0  # (sub provided by fundamental already)
    s = np.tanh(s * 1.8) * np.exp(-t * 3) * np.clip((dur - t) / 0.02, 0, 1)
    return fade(s * 0.8, 0.002, 0.01)

def chord_pluck(notes, vel=1.0):
    """offbeat 'chucu' — bright pluck, like a palm-muted guitar/piano mix"""
    n = int(0.16 * SR); t = tt(n); s = np.zeros(n)
    for m in notes:
        f = mtof(m)
        cut = 900 + 3800 * np.exp(-t * 30)
        s += additive(f, n, lambda fr: 1 / np.sqrt(1 + (fr / cut) ** 4)) * np.exp(-t * 22)
    return fade(s * 0.22 * vel, 0.001, 0.02)

def pad(notes, dur):
    n = int(dur * SR); t = tt(n); L = np.zeros(n); R = np.zeros(n)
    for m in notes:
        for v in range(5):
            det = (v - 2) / 2; f = mtof(m) * 2 ** (det * 0.18 / 12)
            s = additive(f, n, lambda fr: 1 / np.sqrt(1 + (fr / 2200) ** 6), phase=rng.uniform(0, 6))
            a = (det * 0.8 + 1) * np.pi / 4; L += s * np.cos(a); R += s * np.sin(a)
    e = np.minimum(1, t / 0.3) * np.clip((dur - t) / 0.3, 0, 1)
    return np.stack([L, R]) * e * 0.035

def impact(size=1.0):
    n = int(2.2 * SR); t = tt(n); f = 30 + 70 * np.exp(-t * 7)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.4)
    nz = rng.standard_normal(n)
    crack = biquad(nz, 'lp', 4500) * np.exp(-t * 15) * 0.6
    return fade(np.tanh((sub * 1.3 + crack) * 1.4) * size, 0, 0.2)

def whoosh(dur=0.5):
    n = int(dur * SR); x = tt(n) / dur; nz = rng.standard_normal(n)
    fc = 500 * (8000 / 500) ** x
    y = svf_lp(nz, fc, 2.2) - svf_lp(nz, fc * 0.35, 0.7) * 0.6
    e = np.where(x < 0.7, (x / 0.7) ** 2, np.exp(-(x - 0.7) * 9))
    return fade(y * e * 0.6)

def riser(dur):
    n = int(dur * SR); x = tt(n) / dur; nz = rng.standard_normal(n)
    ns = svf_lp(nz, 300 * (10000 / 300) ** (x ** 1.5), 2.5) * x ** 2 * 0.4
    return fade(ns, 0.01, 0.01)

def bell(freq, dur=1.8):
    n = int(dur * SR); t = tt(n); idx = 2.5 * np.exp(-t * 4)
    s = np.sin(2 * np.pi * freq * t + np.sin(2 * np.pi * freq * 3.5 * t) * idx) * np.exp(-t * 2.8)
    return fade(s * 0.35, 0.001, 0.1)

def whistle(dur=0.5):
    """referee-style party whistle (two-tone pea whistle)"""
    n = int(dur * SR); t = tt(n)
    f = 2900 + 120 * np.sign(np.sin(2 * np.pi * 28 * t))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(1, t / 0.01) * np.clip((dur - t) / 0.05, 0, 1)
    s += biquad(rng.standard_normal(n), 'bp', 2900, 3) * 0.3
    return fade(s * 0.2)

def laser(dur=0.35):
    n = int(dur * SR); t = tt(n)
    f = 200 + 3200 * np.exp(-t * 14)
    s = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.5 + np.sin(2 * np.pi * np.cumsum(f * 1.01) / SR) * 0.5
    return fade(s * np.exp(-t * 7) * 0.3, 0.001, 0.02)

# ------------------------------------------------------------ harmony
CH = {'Am': [57, 60, 64], 'G': [55, 59, 62], 'F': [53, 57, 60], 'E': [52, 56, 59]}
ROOT = {'Am': 33, 'G': 31, 'F': 29, 'E': 28}
FIFTH = {'Am': 40, 'G': 38, 'F': 36, 'E': 35}
def chord_at(b, s):
    c = CHORDS[b]
    if '/' in c: a, b2 = c.split('/'); return a if s < 8 else b2
    return c

MEL = {   # (step, midi, length in steps) — A minor, accordion
    'Am': [(0, 76, 2), (2, 72, 1), (3, 76, 1), (4, 81, 3), (8, 79, 1), (9, 77, 1), (10, 76, 2), (12, 72, 2), (14, 71, 2)],
    'G':  [(0, 74, 2), (2, 71, 1), (3, 74, 1), (4, 79, 3), (8, 77, 1), (9, 76, 1), (10, 74, 2), (12, 71, 4)],
    'F':  [(0, 72, 2), (2, 69, 1), (3, 72, 1), (4, 77, 3), (8, 76, 1), (9, 74, 1), (10, 72, 2), (12, 69, 2), (14, 72, 2)],
    'E':  [(0, 71, 2), (2, 68, 1), (3, 71, 1), (4, 76, 3), (8, 74, 1), (9, 72, 1), (10, 71, 2), (12, 68, 4)],
    'E/Am': [(0, 71, 2), (2, 74, 2), (4, 76, 4), (8, 72, 2), (10, 76, 2), (12, 81, 4)],
    'G/E': [(0, 74, 2), (2, 79, 2), (4, 77, 2), (6, 76, 2), (8, 74, 2), (10, 71, 2), (12, 68, 2), (14, 71, 2)],
    'Am2': [(0, 76, 2), (2, 72, 1), (3, 76, 1), (4, 81, 2), (6, 83, 2), (8, 84, 2), (10, 83, 1), (11, 81, 1), (12, 79, 2), (14, 76, 2)],
}
RUN = [52, 53, 55, 57, 59, 60, 62, 64, 68]      # 9 × 16th pickup (steps 7..15) – one per letter of CHIQUILÍN

KICK, KBIG, CLAP = kick(), kick(1.35, 0.55), clap()
kick_times = []
groove_count = 0
for b, typ in enumerate(TYPES):
    if typ == 'build':
        fx.add(riser(BAR), T(b), 0.5)
        for s in range(0, 16, 2):
            perc.add(guiro(s % 4 == 0), T(b, s), 0.28 + 0.25 * s / 16, 0.3)
        for s in (0, 4):
            perc.add(timbal(520), T(b, s), 0.5, -0.3)
        for i, s in enumerate(range(7, 16)):
            lead.add(accordion(RUN[i], STEP * 0.95, 0.75 + 0.25 * i / 8), T(b, s), 0.9)
            send.add(accordion(RUN[i], STEP * 0.95), T(b, s), 0.15)
        for s in (12, 13, 14, 15):
            perc.add(timbal(560 + 30 * (s - 12)), T(b, s), 0.45, 0.25)
        keys.add(pad(CH['E'] + [64], BAR), T(b), 0.7)
        for s in (0, 6, 10): fx.add(laser(), T(b, s), 0.3, 0.6 if s == 6 else -0.6)
        fx.add(whistle(0.35), T(b, 1), 0.5, 0.4)
    elif typ == 'g':
        groove_count += 1
        for s in (0, 4, 8, 12):
            drums.add(KICK, T(b, s), 0.9 if s in (0, 8) else 0.5); kick_times.append(T(b, s))
        if b % 2 == 0:   # timbal fill closing each 2-bar phrase + sonidero laser
            for s in (13, 14, 15): perc.add(timbal(500 + 40 * (s - 13)), T(b, s), 0.4, 0.3)
            fx.add(laser(), T(b, 14), 0.22, -0.5)
        for s in (4, 12):
            drums.add(CLAP, T(b, s), 0.4, 0.05); send.add(CLAP, T(b, s), 0.2)
        # güiro: long-short-short each beat (classic cumbia)
        for beat in range(4):
            perc.add(guiro(True), T(b, beat * 4), 0.35, 0.35)
            perc.add(guiro(False), T(b, beat * 4 + 2), 0.3, 0.35)
            perc.add(guiro(False), T(b, beat * 4 + 3), 0.22, 0.35)
        for s in range(16):
            perc.add(shaker(), T(b, s + (0.15 if s % 2 else 0)), 0.18 if s % 2 else 0.1, -0.5)
        # congas
        for s, f, sl, g in ((3, 330, True, .35), (6, 210, False, .45), (7, 210, False, .35), (10, 330, True, .3), (11, 330, False, .25), (14, 180, False, .5), (15, 210, False, .35)):
            perc.add(conga(f, sl), T(b, s), g, -0.25 if f > 250 else 0.15)
        # bass: cumbia root–fifth
        for s, kind in ((0, 'r'), (3, 'f'), (6, 'f'), (8, 'r'), (11, 'f'), (14, 'r')):
            c = chord_at(b, s); m = ROOT[c] + 12 if kind == 'r' else FIFTH[c] + 12 - 12
            if kind == 'f': m = FIFTH[c]
            bass.add(bass_note(m, STEP * 1.6), T(b, s), 0.55)
        # offbeat chucu chords
        for s in (2, 6, 10, 14):
            c = chord_at(b, s); keys.add(chord_pluck([x + 12 for x in CH[c]]), T(b, s), 0.8, 0.2)
            send.add(chord_pluck([x + 12 for x in CH[c]]), T(b, s), 0.15)
        # accordion melody (alternate F phrase on second F bar)
        key = CHORDS[b]
        if key == 'Am' and groove_count > 2: key = 'Am2'
        for s, m, l in MEL[key]:
            a = accordion(m, STEP * l * 0.92)
            lead.add(a, T(b, s), 0.85, -0.1); send.add(a, T(b, s), 0.22)
            if groove_count >= 3: lead.add(accordion(m - 12, STEP * l * 0.92, 0.6), T(b, s), 0.35, 0.15)  # octave double
        keys.add(pad([x for x in CH[chord_at(b, 0)]], BAR + 0.1), T(b), 0.6)
        # transition whoosh into the next bar
        if b + 1 < NB:
            fx.add(whoosh(0.45), T(b + 1) - 0.45 * 0.7, 0.45)
    else:  # final
        drums.add(KBIG, T(b), 0.95); kick_times.append(T(b))
        fx.add(impact(), T(b), 0.8); send.add(impact(), T(b), 0.2)
        bass.add(bass_note(45, BAR * 0.8) * np.exp(-tt(int(BAR * 0.8 * SR)) * 1.0), T(b), 0.7)
        hit = accordion(81, BAR * 0.55); lead.add(hit, T(b), 0.8); send.add(hit, T(b), 0.35)
        for m in (72, 76): lead.add(accordion(m, BAR * 0.55, 0.7), T(b), 0.5)
        keys.add(chord_pluck([69, 72, 76, 81], 1.4), T(b), 1.0); send.add(chord_pluck([69, 72, 76, 81]), T(b), 0.5)
        # little accordion trill flourish + bells when the badge lands
        for i in range(6):
            m = 81 if i % 2 == 0 else 83
            lead.add(accordion(m, STEP * 0.45, 0.55), T(b, 8 + i * 0.5), 0.5, 0.2)
        lead.add(accordion(84, STEP * 3, 0.8), T(b, 11), 0.6); send.add(accordion(84, STEP * 3), T(b, 11), 0.4)
        for m, s in ((88, 4), (93, 6)):
            fx.add(bell(mtof(m)), T(b, s), 0.5, 0.2); send.add(bell(mtof(m)), T(b, s), 0.4)
        perc.add(guiro(True), T(b, 4), 0.3, 0.3); perc.add(guiro(True), T(b, 8), 0.3, 0.3)
        p = pad(CH['Am'] + [69], BAR); keys.add(p, T(b), 0.9); send.add(p, T(b), 0.4)
        fx.add(whistle(0.5), T(b, 1), 0.35, -0.4)
    if b > 0 and TYPES[b - 1] == 'build' and typ != 'final':
        fx.add(impact(0.7), T(b), 0.6)

# sonidero echo: dotted-8th feedback delay on the lead
d = int(STEP * 3 * SR); src = (lead.L + lead.R) * 0.5; el = np.zeros(N); er = np.zeros(N)
for k in range(1, 5):
    g = 0.38 ** k; sh = np.zeros(N); sh[d * k:] = src[:N - d * k] * g
    (er if k % 2 else el)[:] += sh
lead.L += el; lead.R += er

# sidechain
sc = np.ones(N)
for t0 in kick_times:
    i = int(t0 * SR); n = int(0.25 * SR)
    curve = 1 - 0.55 * np.exp(-tt(n) * 16) * (1 - np.exp(-tt(n) * 900)); j = min(N, i + n)
    sc[i:j] = np.minimum(sc[i:j], curve[:j - i])
for bus in (bass, keys, lead): bus.L *= sc; bus.R *= sc

# reverb (FFT convolution with synthetic IR)
def make_ir(dur=1.6):
    n = int(dur * SR); t = tt(n); out = []
    for _ in range(2):
        nz = rng.standard_normal(n); sm = np.convolve(nz, np.ones(20) / 20, mode='same') * 3
        mix = np.exp(-t * 2); ir = (nz * mix + sm * (1 - mix)) * np.exp(-t * 3.5); ir[:int(0.01 * SR)] = 0
        out.append(ir / np.sqrt(np.sum(ir ** 2)))
    return out
def conv(x, h):
    m = len(x) + len(h); nf = 1 << (m - 1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, nf) * np.fft.rfft(h, nf), nf)[:len(x)]
IR = make_ir(); s2 = send.st()
wet = np.stack([conv(biquad(s2[0], 'hp', 300), IR[0]), conv(biquad(s2[1], 'hp', 300), IR[1])])

mix = drums.st() + perc.st() * 0.9 + bass.st() * 0.9 + keys.st() * 0.8 + lead.st() * 0.85 + fx.st() * 0.8 + wet * 0.5
pk = np.max(np.abs(mix)); mix = mix / pk * 1.5; mix = np.tanh(mix) / np.tanh(1.5); mix *= 10 ** (-1 / 20)
fi = int(0.004 * SR); mix[:, :fi] *= np.linspace(0, 1, fi)
fo = int(0.45 * SR); mix[:, -fo:] *= np.linspace(1, 0, fo) ** 2

pcm = (np.clip(mix.T, -1, 1) * (2 ** 23 - 1)).astype('<i4')
arr = np.frombuffer(pcm.tobytes(), dtype=np.uint8).reshape(-1, 4)[:, :3]
with wave.open(sys.argv[2], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(3); w.setframerate(SR); w.writeframes(arr.tobytes())
print(piece, 'dur', DUR, 'rms dBFS', round(20 * np.log10(np.sqrt(np.mean(mix ** 2))), 1))
