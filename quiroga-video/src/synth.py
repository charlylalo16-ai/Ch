"""
Quiroga Digital - musica original sintetizada con numpy (sin samples).
Pop institucional, 120 BPM, Sol mayor. Efectos de interfaz sincronizados con timeline.json.
uso: python3 synth.py out.wav
"""
import sys, wave, json, os
import numpy as np
SR = 48000
TL = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'timeline.json')))
BPM = TL['bpm']; BEAT = 60.0 / BPM; STEP = BEAT / 4; BAR = BEAT * 4
NB = TL['bars']; DUR = NB * BAR; N = int(round(SR * DUR))
rng = np.random.default_rng(2024)
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


# ============================================================ arrangement (Quiroga Digital)
def hat(open_=False):
    dur = 0.25 if open_ else 0.045
    n = int(dur * SR); t = tt(n)
    s = biquad(rng.standard_normal(n), 'hp', 8000) * np.exp(-t * (12 if open_ else 80))
    return fade(s * 0.45, 0, 0.01)

def tap_click():
    n = int(0.05 * SR); t = tt(n)
    s = np.sin(2 * np.pi * 1700 * t) * np.exp(-t * 140) * 0.5 + biquad(rng.standard_normal(n), 'hp', 3000) * np.exp(-t * 400) * 0.25
    return fade(s, 0, 0.005)

def key_tick():
    n = int(0.025 * SR); t = tt(n)
    return fade(biquad(rng.standard_normal(n), 'bp', 3500, 1.5) * np.exp(-t * 300) * 0.5, 0, 0.004)

def heartbeat():
    n = int(0.35 * SR); t = tt(n)
    f = 45 + 40 * np.exp(-t * 30)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 14)
    return fade(np.tanh(s * 1.6) * 0.9, 0, 0.02)

CH = {'G': [55, 59, 62], 'D': [54, 57, 62], 'Em': [52, 55, 59], 'C': [52, 55, 60]}
ROOT = {'G': 43, 'D': 38, 'Em': 40, 'C': 36}
OB = TL['sections'].index('outro')
CYC = ['G', 'D', 'Em', 'C']
PROG = [('Em', 'C', 'G', 'D')[b % 4] if TL['sections'][b] == 'alert' else CYC[b % 4] for b in range(NB)]
PROG[0] = PROG[1] = 'G'; PROG[OB - 1] = 'D'; PROG[OB] = 'C'
for b in range(OB + 1, NB): PROG[b] = 'G'
def sec(b): return TL['sections'][b]

KICK, KBIG, CLAP = kick(), kick(1.3, 0.5), clap()
HAT_C, HAT_O = hat(), hat(True)
kick_times = []
HOOK = [(0, 79, 2), (2, 81, 2), (4, 83, 3), (8, 81, 1), (9, 79, 1), (10, 78, 2), (12, 74, 4)]

for b in range(NB):
    c = PROG[b]; s_ = sec(b)
    # pad
    if s_ != 'outro' or b == OB:
        p = pad(CH[c] + [CH[c][0] + 12], BAR + 0.1)
        keys.add(p, T(b), 0.55 if s_ in ('intro', 'light') else 0.75); send.add(p, T(b), 0.3)
    # arpeggio plucks
    if s_ in ('light', 'alert', 'full') or b == 1:
        tones = [x + 12 for x in CH[c]] + [CH[c][0] + 24]
        order = [0, 1, 2, 3, 2, 1, 2, 3]
        for k in range(8):
            if b == 1 and k < 4: continue
            m = tones[order[k]]
            pl = chord_pluck([m], 0.9 if k % 2 == 0 else 0.6)
            keys.add(pl, T(b, k * 2), 0.9 if s_ != 'alert' else 0.7, 0.3 * (1 if k % 2 else -1)); send.add(pl, T(b, k * 2), 0.18)
    # bass
    if s_ in ('light', 'alert', 'full'):
        steps = [0, 4, 8, 12] if s_ == 'light' else [0, 2, 4, 6, 8, 10, 12, 14]
        for st in steps:
            bass.add(bass_note(ROOT[c] + 12, STEP * 1.7), T(b, st), 0.45 if s_ != 'light' else 0.5)
    # drums
    if s_ == 'light':
        for st in (0, 8): drums.add(KICK, T(b, st), 0.75); kick_times.append(T(b, st))
        for st in (4, 12): drums.add(CLAP, T(b, st), 0.4); send.add(CLAP, T(b, st), 0.15)
        for st in range(2, 16, 4): perc.add(shaker(), T(b, st), 0.25, 0.4)
    elif s_ == 'alert':
        for st in (0, 4, 8, 12): drums.add(KICK, T(b, st), 0.7); kick_times.append(T(b, st))
        for st in (4, 12): drums.add(CLAP, T(b, st), 0.35)
        for st in range(0, 16, 2): perc.add(HAT_C, T(b, st + 1), 0.25, 0.3)
    elif s_ == 'full':
        for st in (0, 4, 8, 12): drums.add(KBIG if (b == 12 and st == 0) else KICK, T(b, st), 0.85); kick_times.append(T(b, st))
        for st in (4, 12): drums.add(CLAP, T(b, st), 0.5); send.add(CLAP, T(b, st), 0.2)
        for st in range(16): perc.add(HAT_O if st % 4 == 2 else HAT_C, T(b, st), 0.22 if st % 2 else 0.32, 0.25 if st % 2 else -0.25)
        mel = HOOK if b % 2 == 0 else [(0, 78, 2), (2, 79, 2), (4, 81, 3), (8, 79, 1), (9, 78, 1), (10, 76, 2), (12, 79, 4)]
        for st, m, l in mel:
            bl = bell(mtof(m + 12), 0.9) * 0.55
            lead.add(bl, T(b, st), 0.55, 0.1); send.add(bl, T(b, st), 0.25)
            lead.add(chord_pluck([m]), T(b, st), 0.7, -0.1)

# intro: riser into the logo hit, bells on the logo
fx.add(riser(BAR) * 0.5, T(0), 0.4)
for m, st in ((83, 2), (86, 4), (91, 6)):
    fx.add(bell(mtof(m)), T(1, st), 0.35, 0.2); send.add(bell(mtof(m)), T(1, st), 0.35)
# outro: final chord + bell flourish
fin = pad(CH['G'] + [67, 71], BAR * 3); keys.add(fin * np.exp(-tt(fin.shape[1]) * 0.6), T(OB + 1) - 1.6, 0.9); send.add(fin, T(OB + 1) - 1.6, 0.4)
for i, m in enumerate((79, 83, 86, 91)):
    fx.add(bell(mtof(m)), T(OB, 4 + i * 3), 0.35, 0.3 * (i % 2 * 2 - 1)); send.add(bell(mtof(m)), T(OB, 4 + i * 3), 0.3)
bass.add(bass_note(43, BAR * 1.5) * np.exp(-tt(int(BAR * 1.5 * SR)) * 1.2), T(OB + 1) - 1.6, 0.6)
drums.add(KBIG, T(OB + 1) - 1.6, 0.9); kick_times.append(T(OB + 1) - 1.6)

# ---- interface sound design, synced to timeline.json ----
for tp in TL['taps']: fx.add(tap_click(), tp[0] if isinstance(tp, list) else tp, 0.35, 0.1)
r = np.random.default_rng(5)
for a, b2 in TL['typing']:
    t0 = a
    while t0 < b2: fx.add(key_tick(), t0, 0.18 + 0.08 * r.random(), (r.random() - 0.5) * 0.6); t0 += 0.06 + 0.04 * r.random()
for t0 in TL['whoosh']: w = whoosh(0.45); fx.add(w, t0 - 0.45 * 0.7, 0.35); send.add(w, t0 - 0.3, 0.1)
for t0 in TL['chime']:
    for m, d in ((88, 0), (95, 0.09)): fx.add(bell(mtof(m), 1.2), t0 + d, 0.3, 0.2); send.add(bell(mtof(m), 1.2), t0 + d, 0.3)
for t0 in TL['alarm']:
    for k in range(3):
        for m, d in ((84, 0), (91, 0.12)): fx.add(bell(mtof(m), 0.8), t0 + k * 0.32 + d, 0.32, 0.0); send.add(bell(mtof(m), 0.8), t0 + k * 0.32 + d, 0.2)
for t0 in TL['impact']: fx.add(impact(), t0, 0.6); send.add(impact(), t0, 0.15)
h0, h1 = TL['hold']
fx.add(riser(h1 - h0), h0, 0.45)
t0, gap = h0, 0.5
while t0 < h1 - 0.05:
    fx.add(heartbeat(), t0, 0.7); fx.add(heartbeat(), t0 + 0.16, 0.45); t0 += gap; gap = max(0.22, gap * 0.82)

# sidechain + reverb + master (same chain as the other pieces)
sc = np.ones(N)
for t0 in kick_times:
    i = int(t0 * SR); n = int(0.25 * SR)
    curve = 1 - 0.5 * np.exp(-tt(n) * 16) * (1 - np.exp(-tt(n) * 900)); j = min(N, i + n)
    sc[i:j] = np.minimum(sc[i:j], curve[:j - i])
for bus in (bass, keys, lead): bus.L *= sc; bus.R *= sc
def make_ir(dur=1.8):
    n = int(dur * SR); t = tt(n); out = []
    for _ in range(2):
        nz = rng.standard_normal(n); sm = np.convolve(nz, np.ones(20) / 20, mode='same') * 3
        mix = np.exp(-t * 2); ir = (nz * mix + sm * (1 - mix)) * np.exp(-t * 3.2); ir[:int(0.012 * SR)] = 0
        out.append(ir / np.sqrt(np.sum(ir ** 2)))
    return out
def conv(x, h):
    m = len(x) + len(h); nf = 1 << (m - 1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, nf) * np.fft.rfft(h, nf), nf)[:len(x)]
IR = make_ir(); s2 = send.st()
wet = np.stack([conv(biquad(s2[0], 'hp', 300), IR[0]), conv(biquad(s2[1], 'hp', 300), IR[1])])
mix = drums.st() + perc.st() * 0.9 + bass.st() * 0.85 + keys.st() * 0.8 + lead.st() * 0.7 + fx.st() * 0.9 + wet * 0.5
pk = np.max(np.abs(mix)); mix = mix / pk * 1.5; mix = np.tanh(mix) / np.tanh(1.5); mix *= 10 ** (-1 / 20)
fi = int(0.004 * SR); mix[:, :fi] *= np.linspace(0, 1, fi)
fo = int(1.5 * SR); mix[:, -fo:] *= np.linspace(1, 0, fo) ** 2
pcm = (np.clip(mix.T, -1, 1) * (2 ** 23 - 1)).astype('<i4')
arr = np.frombuffer(pcm.tobytes(), dtype=np.uint8).reshape(-1, 4)[:, :3]
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(3); w.setframerate(SR); w.writeframes(arr.tobytes())
print('dur', DUR, 'rms dBFS', round(20 * np.log10(np.sqrt(np.mean(mix ** 2))), 1))
