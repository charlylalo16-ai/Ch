"""
Showreel score — synthesized from scratch with numpy. No samples.
128 BPM, F minor, 8 bars = exactly 15.000 s.
Output: 48 kHz / 24-bit stereo WAV.
"""
import sys, wave
import numpy as np

SR = 48000
BPM = 128
BEAT = 60.0 / BPM          # 0.46875 s
STEP = BEAT / 4            # 16th note
BAR = BEAT * 4             # 1.875 s
DUR = 15.0
N = int(SR * DUR)
rng = np.random.default_rng(20261104)

def T(bar, step=0.0):
    return bar * BAR + step * STEP

def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)

def tt(n):
    return np.arange(n) / SR

# ----------------------------------------------------------------- buses
class Bus:
    def __init__(self):
        self.L = np.zeros(N); self.R = np.zeros(N)
    def add(self, sig, t, gain=1.0, pan=0.0):
        """sig mono (n,) or stereo (2,n). pan -1..1 (equal power)."""
        i = int(round(t * SR))
        if sig.ndim == 1:
            a = (pan + 1) * np.pi / 4
            sl, sr = sig * np.cos(a) * 1.4142, sig * np.sin(a) * 1.4142
        else:
            sl, sr = sig[0], sig[1]
        if i < 0:
            sl, sr = sl[-i:], sr[-i:]; i = 0
        if i >= N: return
        n = min(len(sl), N - i)
        self.L[i:i+n] += sl[:n] * gain
        self.R[i:i+n] += sr[:n] * gain
    def st(self):
        return np.stack([self.L, self.R])

drums, bass, pads, arps, fx, verb_send = Bus(), Bus(), Bus(), Bus(), Bus(), Bus()

# ----------------------------------------------------------------- dsp
def biquad(x, kind, f, q=0.707):
    w = 2 * np.pi * f / SR
    c, s = np.cos(w), np.sin(w)
    al = s / (2 * q)
    if kind == 'lp':
        b = [(1 - c) / 2, 1 - c, (1 - c) / 2]
    elif kind == 'hp':
        b = [(1 + c) / 2, -(1 + c), (1 + c) / 2]
    else:  # band-pass, 0 dB peak
        b = [al, 0, -al]
    a = [1 + al, -2 * c, 1 - al]
    b0, b1, b2 = b[0] / a[0], b[1] / a[0], b[2] / a[0]
    a1, a2 = a[1] / a[0], a[2] / a[0]
    y = np.zeros_like(x)
    x1 = x2 = y1 = y2 = 0.0
    for i in range(len(x)):
        xi = x[i]
        yi = b0 * xi + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
        x2, x1, y2, y1 = x1, xi, y1, yi
        y[i] = yi
    return y

def svf_lp(x, fc, q=0.8):
    """Time-varying state-variable low-pass (fc array)."""
    y = np.zeros_like(x)
    low = band = 0.0
    damp = 1.0 / q
    f = 2 * np.sin(np.pi * np.minimum(fc, SR / 6) / SR)
    for i in range(len(x)):
        fi = f[i]
        low += fi * band
        high = x[i] - low - damp * band
        band += fi * high
        y[i] = low
    return y

def saw_additive(freq, n, cutoff, phase0=0.0, maxh=None):
    """Band-limited saw with a 4-pole-ish spectral roll-off at `cutoff` (array or scalar)."""
    t = tt(n)
    out = np.zeros(n)
    hmax = int(min(SR * 0.45 / freq, maxh or 200))
    cutoff = np.broadcast_to(cutoff, (n,))
    for k in range(1, hmax + 1):
        w = 1.0 / np.sqrt(1.0 + (k * freq / cutoff) ** 8)
        if np.max(w) < 1e-3: break
        out += np.sin(2 * np.pi * k * freq * t + phase0 * k) * w / k
    return out

def square_additive(freq, n, cutoff):
    t = tt(n); out = np.zeros(n)
    cutoff = np.broadcast_to(cutoff, (n,))
    for k in range(1, int(SR * 0.45 / freq) + 1, 2):
        w = 1.0 / np.sqrt(1.0 + (k * freq / cutoff) ** 6)
        if np.max(w) < 1e-3: break
        out += np.sin(2 * np.pi * k * freq * t) * w / k
    return out

def env_adsr(n, a=0.005, d=0.1, s=0.7, r=0.1):
    t = tt(n); dur = n / SR
    e = np.where(t < a, t / a, s + (1 - s) * np.exp(-(t - a) / max(d, 1e-4)))
    rel = np.clip((dur - t) / r, 0, 1)
    return e * rel

def fade(sig, fin=0.002, fout=0.01):
    n = len(sig)
    e = np.ones(n)
    a, b = int(fin * SR), int(fout * SR)
    if a: e[:a] = np.linspace(0, 1, a)
    if b: e[-b:] *= np.linspace(1, 0, b)
    return sig * e

# ----------------------------------------------------------------- instruments
def kick(punch=1.0, dur=0.42):
    n = int(dur * SR); t = tt(n)
    f = 44 + 170 * np.exp(-t * 30) + 60 * np.exp(-t * 300)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t * 6.5) * (1 - np.exp(-t * 2000))
    click = biquad(rng.standard_normal(n), 'hp', 3000) * np.exp(-t * 400) * 0.35
    s = np.tanh((body + click) * 1.8 * punch) * 0.9
    return fade(s, 0, 0.02)

def clap():
    n = int(0.35 * SR); t = tt(n)
    nz = biquad(rng.standard_normal(n), 'bp', 1300, 0.9)
    e = np.zeros(n)
    for off in (0.0, 0.009, 0.018, 0.026):
        e += np.where(t >= off, np.exp(-(t - off) * 180), 0)
    e += np.where(t >= 0.026, np.exp(-(t - 0.026) * 16) * 0.55, 0)
    return fade(nz * e * 1.6, 0, 0.03)

def snare(vel=1.0):
    n = int(0.22 * SR); t = tt(n)
    tone = np.sin(2 * np.pi * (185 + 40 * np.exp(-t * 60)) * t) * np.exp(-t * 30)
    nz = biquad(rng.standard_normal(n), 'hp', 1500) * np.exp(-t * 22)
    return fade((tone * 0.5 + nz * 0.7) * vel, 0, 0.02)

HAT_NOISE = rng.standard_normal(int(0.5 * SR))
HAT_HP = biquad(biquad(HAT_NOISE, 'hp', 7000), 'hp', 7000)
def hat(open_=False):
    dur = 0.32 if open_ else 0.05
    n = int(dur * SR); t = tt(n)
    # metallic: noise + inharmonic square partials
    metal = np.zeros(n)
    for f in (3200, 4690, 5870, 7420, 8340, 9910):
        metal += np.sign(np.sin(2 * np.pi * f * t))
    metal = biquad(metal, 'hp', 7500) * 0.08
    s = (HAT_HP[:n] + metal) * np.exp(-t * (9 if open_ else 75))
    return fade(s * 0.5, 0, 0.01)

def tick(freq=2400):
    n = int(0.03 * SR); t = tt(n)
    return np.sin(2 * np.pi * freq * t) * np.exp(-t * 260)

def impact(size=1.0):
    n = int(2.4 * SR); t = tt(n)
    f = 28 + 70 * np.exp(-t * 7)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2)
    nz = rng.standard_normal(n)
    crack = biquad(nz, 'lp', 4000) * np.exp(-t * 14) * 0.6
    air = biquad(nz, 'hp', 6000) * np.exp(-t * 4) * 0.12
    s = np.tanh((sub * 1.3 + crack + air) * 1.4) * size
    return fade(s, 0, 0.2)

def whoosh(dur=0.6, f0=300, f1=6000, peak=0.6):
    n = int(dur * SR); t = tt(n) / dur
    fc = f0 * (f1 / f0) ** t
    nz = rng.standard_normal(n)
    y = svf_lp(nz, fc, 2.5) - svf_lp(nz, fc * 0.35, 0.7) * 0.6
    e = np.where(t < peak, (t / peak) ** 2, np.exp(-(t - peak) * 9))
    return fade(y * e * 0.7)

def riser(dur):
    n = int(dur * SR); x = tt(n) / dur
    nz = rng.standard_normal(n)
    fc = 200 * (12000 / 200) ** (x ** 1.6)
    ns = svf_lp(nz, fc, 3.0) * (x ** 1.8) * 0.5
    f = 180 * 2 ** (x * 3.0)  # three-octave pitch rise
    vib = 1 + 0.01 * np.sin(2 * np.pi * (5 + 20 * x) * tt(n))
    tone = np.sin(2 * np.pi * np.cumsum(f * vib) / SR) * (x ** 2) * 0.18
    tone += np.sin(2 * np.pi * np.cumsum(f * 1.5 * vib) / SR) * (x ** 3) * 0.09
    return fade(ns + tone, 0.01, 0.004)

def reverse_swell(dur):
    n = int(dur * SR); t = tt(n)
    nz = biquad(rng.standard_normal(n), 'bp', 2500, 0.6)
    e = np.exp(-(dur - t) * 6)
    return fade(nz * e * 0.6, 0.01, 0.003)

def bell(freq, dur=2.5):
    n = int(dur * SR); t = tt(n)
    idx = 3.0 * np.exp(-t * 3)
    mod = np.sin(2 * np.pi * freq * 3.5 * t) * idx
    s = np.sin(2 * np.pi * freq * t + mod) * np.exp(-t * 2.2)
    s += 0.3 * np.sin(2 * np.pi * freq * 2.01 * t) * np.exp(-t * 4)
    return fade(s * 0.4, 0.001, 0.1)

def bass_note(m, dur, drop=False):
    n = int(dur * SR); t = tt(n)
    f = mtof(m)
    cut = (180 + (1400 if drop else 700) * np.exp(-t * 18))
    s = saw_additive(f, n, cut) * 0.9
    s += np.sin(2 * np.pi * f / 2 * t) * (0.55 if drop else 0.35)   # sub
    s = np.tanh(s * 1.5)
    return fade(s * env_adsr(n, 0.003, 0.08, 0.6, 0.02), 0.002, 0.01)

def pluck(m, vel=1.0):
    n = int(0.32 * SR); t = tt(n)
    f = mtof(m)
    cut = 500 + 5200 * np.exp(-t * 22) * vel
    s = square_additive(f, n, cut) * 0.6 + saw_additive(f * 1.005, n, cut) * 0.4
    return fade(s * np.exp(-t * 9) * vel, 0.001, 0.02)

def supersaw_chord(notes, dur, cutoff, voices=7, spread=0.22):
    n = int(dur * SR)
    L, R = np.zeros(n), np.zeros(n)
    for m in notes:
        f = mtof(m)
        for v in range(voices):
            det = (v - (voices - 1) / 2) / ((voices - 1) / 2)  # -1..1
            fv = f * 2 ** (det * spread / 12)
            s = saw_additive(fv, n, cutoff, phase0=rng.uniform(0, 6.28), maxh=60)
            pan = det * 0.8
            a = (pan + 1) * np.pi / 4
            L += s * np.cos(a); R += s * np.sin(a)
    g = 0.12 / np.sqrt(len(notes) * voices / 7)
    return np.stack([L, R]) * g

# ----------------------------------------------------------------- arrangement
CH = {   # chord voicings (MIDI)
    'Fm':  [53, 56, 60, 63],
    'Db':  [49, 53, 56, 60],
    'Eb':  [51, 55, 58, 65],
    'Ab':  [56, 60, 63, 67],
    'Fm9': [41, 53, 56, 60, 63, 67],
}
ROOT = {'Fm': 41, 'Db': 37, 'Eb': 39, 'Ab': 44, 'Fm9': 41}
PROG = ['Fm', 'Fm', 'Db', 'Eb', 'Fm', 'Db', 'Ab', 'Fm9']   # per bar
def chord_at(bar, step):
    if bar == 6 and step >= 8: return 'Eb'
    return PROG[bar]

KICK = kick(); KICK_BIG = kick(1.4, 0.6); CLAP = clap()
HAT_C, HAT_O = hat(False), hat(True)
kick_times = []

# --- drums
drums.add(kick(0.7), T(0, 0), 0.6); kick_times.append(T(0, 0))
for b in range(1, 7):
    for s in (0, 4, 8, 12):
        k = KICK_BIG if (b == 4 and s == 0) else KICK
        drums.add(k, T(b, s), 0.9); kick_times.append(T(b, s))
    if b == 5:
        drums.add(KICK, T(b, 14), 0.6); kick_times.append(T(b, 14))
    if b != 3:
        for s in (4, 12):
            drums.add(CLAP, T(b, s), 0.55, 0.05); verb_send.add(CLAP, T(b, s), 0.25)
    else:
        drums.add(CLAP, T(b, 4), 0.55); verb_send.add(CLAP, T(b, 4), 0.25)
    # hats
    for s in range(16):
        sw = 0.12 if s % 2 else 0.0       # 16th swing
        if b <= 3:
            if s % 4 == 2:
                drums.add(HAT_C, T(b, s + sw), 0.55, 0.3)
            elif b >= 2 and s % 2 == 1:
                drums.add(HAT_C, T(b, s + sw), 0.18, -0.3)
        else:
            if s % 4 == 2:
                drums.add(HAT_O, T(b, s), 0.35, 0.25)
            else:
                acc = 0.32 if s % 2 == 0 else 0.16
                drums.add(HAT_C, T(b, s + sw), acc, -0.25 if s % 2 else 0.2)
# snare roll build (bar 3): 8ths -> 16ths -> 32nds, rising velocity
roll = []
roll += [T(3, s) for s in range(0, 8, 2)]
roll += [T(3, s) for s in range(8, 12)]
roll += [T(3, 12 + i * 0.5) for i in range(6)]
for i, t0 in enumerate(roll):
    v = 0.25 + 0.75 * (i / len(roll)) ** 1.3
    drums.add(snare(v), t0, 0.55, 0.0); verb_send.add(snare(v), t0, 0.15)

# intro ticks (bar 0) – synced to the dial ticks on screen (8ths)
for s in range(0, 16, 2):
    fx.add(tick(2400 if s % 8 == 0 else 1800), T(0, s), 0.22, 0.4 if (s // 2) % 2 else -0.4)
fx.add(reverse_swell(BEAT * 1.5), T(0, 16) - BEAT * 1.5, 0.6)

# impacts + whooshes on every transition
for t0, g in ((T(1), 0.8), (T(4), 1.0), (T(7), 1.0)):
    fx.add(impact(), t0, g); verb_send.add(impact(), t0, 0.25 * g)
for t0 in (T(2), T(3), T(5), T(6)):
    w = whoosh(0.55, 400, 7000, 0.7)
    fx.add(w, t0 - 0.55 * 0.7, 0.5, 0.0)
    verb_send.add(w, t0 - 0.55 * 0.7, 0.2)
fx.add(riser(BAR - STEP), T(3), 0.65)
verb_send.add(riser(BAR - STEP), T(3), 0.25)

# --- bass
for b in range(1, 7):
    drop = b >= 4
    steps = [s for s in range(16) if s % 4 != 0] if drop else [2, 6, 10, 14]
    if b == 3:
        steps = [2, 6, 10, 11, 13, 14]   # build: busier, ends before the gap
    for s in steps:
        c = chord_at(b, s)
        m = ROOT[c] + 12
        if drop and s % 4 == 3: m += 12   # octave pop on the last 16th of each beat
        dur = STEP * (0.95 if drop else 1.7)
        bass.add(bass_note(m, dur, drop), T(b, s), 0.42 if drop else 0.5)
# final bass
bass.add(bass_note(29 + 12, BAR * 0.9, True) * np.exp(-tt(int(BAR * 0.9 * SR)) * 1.5), T(7), 0.55)

# --- pads (one per bar, cut-off automation tells the story)
for b in range(8):
    c = PROG[b]
    dur = BAR + 0.25
    n = int(dur * SR); x = tt(n) / dur
    if b == 0:   cut = 300 + 900 * x ** 2
    elif b < 3:  cut = np.full(n, 1400.0)
    elif b == 3: cut = 1400 + 4000 * x ** 2
    elif b < 7:  cut = np.full(n, 3800.0)
    else:        cut = 5200 * np.exp(-tt(n) * 1.2) + 500
    if b == 6:   # Ab -> Eb split
        half = int(BAR / 2 * SR)
        p1 = supersaw_chord(CH['Ab'], BAR / 2 + 0.05, cut[:int((BAR/2+0.05)*SR)])
        p2 = supersaw_chord(CH['Eb'], BAR / 2 + 0.25, cut[:int((BAR/2+0.25)*SR)])
        for p, t0 in ((p1, T(6)), (p2, T(6, 8))):
            e = env_adsr(p.shape[1], 0.01, 0.4, 0.8, 0.08)
            pads.add(p * e, t0, 1.0); verb_send.add(p * e, t0, 0.35)
        continue
    if b == 7:
        dur = 15.0 - T(7)
        n = int(dur * SR)
        cut = 5200 * np.exp(-tt(n) * 1.4) + 400
    p = supersaw_chord(CH[c], dur, cut)
    e = env_adsr(p.shape[1], 0.08 if b == 0 else 0.01, 0.6, 0.8 if b < 7 else 0.5, 0.12 if b < 7 else 1.2)
    if b == 7:
        e *= np.exp(-tt(p.shape[1]) * 1.1)
    g = 0.75 if b == 0 else 1.0
    pads.add(p * e, T(b), g); verb_send.add(p * e, T(b), 0.4)

# --- arp (filtered tease in bar 3, full in the drop)
for b in (3, 4, 5, 6):
    for s in range(16):
        if b == 3 and s >= 15: continue
        c = chord_at(b, s)
        tones = CH[c] + [x + 12 for x in CH[c]]
        order = [0, 2, 4, 1, 3, 5, 7, 4, 6, 2, 5, 3, 7, 1, 6, 4]
        m = tones[order[s] % len(tones)] + 12
        vel = (0.5 + 0.5 * (s / 16)) if b == 3 else (1.0 if s % 4 == 0 else 0.75)
        p = pluck(m, vel)
        pan = 0.35 * np.sin(s * 1.3)
        arps.add(p, T(b, s), 0.22 if b == 3 else 0.32, pan)
# ping-pong delay on arps (3/16)
d = int(STEP * 3 * SR)
dl = np.zeros_like(arps.L); dr = np.zeros_like(arps.R)
src = (arps.L + arps.R) * 0.5
for k in range(1, 6):
    g = 0.42 ** k
    sh = np.zeros(N); sh[d * k:] = src[:N - d * k] * g
    if k % 2: dr += sh
    else: dl += sh
arps.L += dl; arps.R += dr
verb_send.L += arps.L * 0.3; verb_send.R += arps.R * 0.3

# --- logo bell (lands with the logo dot on screen)
for m, t0, g in ((77, T(7, 4), 0.5), (84, T(7, 6), 0.35), (72, T(7, 8), 0.3)):
    bl = bell(mtof(m))
    fx.add(bl, t0, g, 0.2 if m == 84 else -0.15); verb_send.add(bl, t0, 0.5 * g)

# ----------------------------------------------------------------- sidechain
sc = np.ones(N)
for t0 in kick_times:
    i = int(t0 * SR)
    n = int(0.3 * SR)
    curve = 1 - 0.75 * np.exp(-tt(n) * 14) * (1 - np.exp(-tt(n) * 900))
    j = min(N, i + n)
    sc[i:j] = np.minimum(sc[i:j], curve[:j - i])
for bus in (bass, pads, arps):
    bus.L *= sc; bus.R *= sc

# ----------------------------------------------------------------- reverb (FFT convolution, synthetic IR)
def make_ir(dur=2.4):
    n = int(dur * SR); t = tt(n)
    irs = []
    for ch in range(2):
        nz = rng.standard_normal(n)
        # progressively darker: blend white and smoothed noise over time
        k = 24
        sm = np.convolve(nz, np.ones(k) / k, mode='same') * 3
        mix = np.exp(-t * 1.5)
        ir = (nz * mix + sm * (1 - mix)) * np.exp(-t * 2.6)
        ir[:int(0.012 * SR)] = 0   # predelay
        irs.append(ir / np.sqrt(np.sum(ir ** 2)))
    return irs
IR = make_ir()
def convolve(x, h):
    m = len(x) + len(h)
    nfft = 1 << (m - 1).bit_length()
    y = np.fft.irfft(np.fft.rfft(x, nfft) * np.fft.rfft(h, nfft), nfft)
    return y[:len(x)]
send = verb_send.st()
send[0] = biquad(send[0], 'hp', 250); send[1] = biquad(send[1], 'hp', 250)
wet = np.stack([convolve(send[0], IR[0]), convolve(send[1], IR[1])]) * 0.9

# ----------------------------------------------------------------- mix bus
music = drums.st() * 1.0 + bass.st() * 0.9 + pads.st() * 0.85 + arps.st() * 0.8
# pre-drop gap: last 16th of bar 3 – everything but the riser/fx drops out
g0, g1 = int(T(3, 15) * SR), int(T(4) * SR)
music[:, g0:g1] *= np.linspace(1, 0, g1 - g0) ** 3

# glitch stutter: last beat of bar 6 retriggers slices of itself
def stutter(x, t_start, t_end):
    i0, i1 = int(t_start * SR), int(t_end * SR)
    out = x.copy()
    pos = i0
    lens = [STEP] * 2 + [STEP / 2] * 2 + [STEP / 4] * 4
    src0 = int(T(6, 8) * SR)   # grab a slice from the Eb half
    for k, l in enumerate(lens):
        n = int(l * SR)
        if pos >= i1: break
        sl = x[:, src0:src0 + n].copy()
        rate = 1 + k * 0.08            # pitch climbs
        idx = np.clip((np.arange(n) * rate).astype(int), 0, n - 1)
        sl = sl[:, idx]
        w = np.ones(n); f = min(64, n // 4); w[:f] = np.linspace(0, 1, f); w[-f:] = np.linspace(1, 0, f)
        m = min(n, i1 - pos)
        out[:, pos:pos + m] = (sl * w)[:, :m]
        pos += n
    return out
music = stutter(music, T(6, 12), T(7))

mix = music + fx.st() * 0.9 + wet * 0.55

# gentle low-end tidy + soft clip + normalise
mix[0] = mix[0] - biquad(mix[0], 'lp', 25) ; mix[1] = mix[1] - biquad(mix[1], 'lp', 25)
pk = np.max(np.abs(mix))
mix = mix / pk * 1.6
mix = np.tanh(mix) / np.tanh(1.6)
mix *= 10 ** (-1.0 / 20)   # -1 dBFS ceiling
# edges
fi = int(0.004 * SR); mix[:, :fi] *= np.linspace(0, 1, fi)
fo = int(0.6 * SR); mix[:, -fo:] *= np.linspace(1, 0, fo) ** 2

out = sys.argv[1] if len(sys.argv) > 1 else 'score.wav'
pcm = (np.clip(mix.T, -1, 1) * (2 ** 23 - 1)).astype(np.int32)
b = pcm.astype('<i4').tobytes()
b24 = bytearray()
arr = np.frombuffer(b, dtype=np.uint8).reshape(-1, 4)[:, :3]
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(3); w.setframerate(SR)
    w.writeframes(arr.tobytes())
rms = np.sqrt(np.mean(mix ** 2))
print('wrote', out, 'peak', np.max(np.abs(mix)), 'rms dBFS', 20 * np.log10(rms))
