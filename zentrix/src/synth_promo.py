"""Sonido de los videos 'Próximamente' de ZENTRIX (numpy, sin samples). uso: synth_promo.py teaser|carga out.wav"""
import sys, wave, json, os
import numpy as np
piece, outp = sys.argv[1], sys.argv[2]
D = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'promo_data.json')))[piece]
SR = 48000; DUR = D['dur']; N = int(SR * DUR); rng = np.random.default_rng(11)
L = np.zeros(N); R = np.zeros(N); SL = np.zeros(N); SRv = np.zeros(N)
tt = lambda n: np.arange(n) / SR
def add(sig, t0, g=1.0, pan=0.0, send=0.0):
    i = int(t0 * SR); n = min(len(sig), N - i)
    if n <= 0 or i < 0: return
    a = (pan + 1) * np.pi / 4; l, r = sig[:n] * np.cos(a) * 1.414 * g, sig[:n] * np.sin(a) * 1.414 * g
    L[i:i + n] += l; R[i:i + n] += r; SL[i:i + n] += l * send; SRv[i:i + n] += r * send
def lp(x, fc):
    y = np.zeros_like(x); s = 0.0; k = 1 - np.exp(-2 * np.pi * np.broadcast_to(fc, x.shape) / SR)
    for i in range(len(x)): s += k[i] * (x[i] - s); y[i] = s
    return y
def fade(x, a=0.003, b=0.02):
    e = np.ones(len(x)); na, nb = int(a * SR), int(b * SR)
    if na: e[:na] = np.linspace(0, 1, na)
    if nb: e[-nb:] *= np.linspace(1, 0, nb)
    return x * e
def saw(f, n):   # saw band-limited aditivo
    t = tt(n); return sum(np.sin(2 * np.pi * f * k * t) / k for k in range(1, int(8000 / f)))
def whoosh(dur=0.7, peak=0.7):
    n = int(dur * SR); x = tt(n) / dur; nz = rng.standard_normal(n)
    return fade((lp(nz, 300 * (8000 / 300) ** x) - lp(nz, 200)) * np.where(x < peak, (x / peak) ** 2, np.exp(-(x - peak) * 14)) * 0.6)
def boom():
    n = int(2.4 * SR); t = tt(n); f = 32 + 70 * np.exp(-t * 8)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2)
    crack = (rng.standard_normal(n) - lp(rng.standard_normal(n), 1500)) * np.exp(-t * 18) * 0.4
    return fade(np.tanh((sub * 1.3 + crack) * 1.2))
def bell(fr, d=1.6):
    n = int(d * SR); t = tt(n); return fade(np.sin(2 * np.pi * fr * t + 2 * np.sin(2 * np.pi * fr * 2.01 * t) * np.exp(-t * 6)) * np.exp(-t * 3) * 0.2)
def tick(fr=2200):
    n = int(0.03 * SR); t = tt(n); return fade(np.sin(2 * np.pi * fr * t) * np.exp(-t * 160) * 0.35 + rng.standard_normal(n) * np.exp(-t * 400) * 0.08, 0, 0.004)
def kick():
    n = int(0.35 * SR); t = tt(n); f = 45 + 120 * np.exp(-t * 35)
    return fade(np.tanh(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9) * 1.5))
def pad(notes, dur, cut=1500):
    n = int(dur * SR); t = tt(n); s = np.zeros(n)
    for m in notes:
        f0 = 440 * 2 ** ((m - 69) / 12)
        for d in (-0.07, 0, 0.07): s += sum(np.sin(2 * np.pi * f0 * 2 ** (d / 12) * h * t + rng.uniform(0, 6)) / h for h in range(1, 6))
    e = np.minimum(1, t / 1.0) * np.clip((dur - t) / 1.2, 0, 1)
    return lp(s * e * 0.012, float(cut))

BPM = 110; BEAT = 60 / BPM
if piece == 'teaser':
    add(pad([38, 45, 50, 53, 57], DUR), 0, 1.0, 0, 0.5)                       # fondo Re menor
    # pulso tecnológico suave mientras se construye
    t0 = D['type'][0]
    while t0 < D['close']['logo'][0] - 0.4:
        add(kick(), t0, 0.55); t0 += BEAT
    for s_ in D['whoosh']: add(whoosh(), s_ - 0.45, 0.6, 0, 0.3)
    # tecleo: un clic por carácter visible
    chars = sum(len(x) for line in D['code'] for _, x in line); a, b = D['type']
    for i in range(chars):
        x = i / chars; tt0 = a + (b - a) * (np.arccos(1 - 2 * x) / np.pi)        # inversa de la curva inOutS del video
        add(tick(1700 + 600 * rng.random()), tt0, 0.22 + 0.1 * rng.random(), (rng.random() - 0.5) * 0.6)
    # bocetos y color: brillos ascendentes
    for k, fr in enumerate((880, 1108, 1318, 1760)): add(bell(fr), D['build']['wire'][0] + k * 0.35, 0.8, -0.4 + k * 0.27, 0.6)
    for k, fr in enumerate((1318, 1568, 1760, 2093)): add(bell(fr), D['build']['color'][0] + k * 0.3, 0.9, 0.4 - k * 0.27, 0.6)
    # subida hacia el cierre + golpe con el logo
    n = int(1.6 * SR); x = tt(n) / 1.6; nz = rng.standard_normal(n)
    add(fade((lp(nz, 200 * (9000 / 200) ** (x ** 1.5)) - lp(nz, 150)) * x ** 2 * 0.5, 0.05, 0.01), D['close']['logo'][0] - 1.6, 0.6, 0, 0.3)
    add(boom(), D['close']['logo'][0], 0.9, 0, 0.3)
    for k, fr in enumerate((587, 880, 1175)): add(bell(fr, 2.5), D['close']['proximamente'][0] + k * 0.12, 0.8, -0.3 + k * 0.3, 0.7)
    add(pad([50, 57, 62, 65, 69], DUR - D['close']['logo'][0], 2500), D['close']['logo'][0], 1.2, 0, 0.6)
else:
    add(pad([38, 45, 50, 53], DUR), 0, 1.0, 0, 0.5)
    a, b = D['bar']; n = int((b - a) * SR); t = tt(n); x = t / (b - a)
    f = 220 * 2 ** (x * 1.2); tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.08 * np.minimum(1, x * 5)
    add(fade(lp(tone + saw(110, n) * 0.01, 1200.0), 0.05, 0.05), a, 1.0, 0, 0.3)          # tono que sube con la barra
    t0 = a
    while t0 < b: add(tick(2600), t0, 0.18, 0.3); t0 += BEAT / 2                            # pulso de carga
    g0, g1 = D['glitch']; n = int((g1 - g0) * SR); gl = rng.standard_normal(n) * (np.sign(np.sin(2 * np.pi * 23 * tt(n))) > 0) * 0.25
    add(fade(lp(gl, 3000.0)), g0, 0.8, 0, 0.2)
    for k in range(5): add(tick(400 + 300 * k), g0 + k * 0.1, 0.4, (k % 2) * 0.8 - 0.4)
    add(boom(), D['prox'][0], 0.85, 0, 0.3)
    for k, fr in enumerate((587, 880, 1175)): add(bell(fr, 2.2), D['prox'][0] + 0.05 + k * 0.12, 0.8, -0.3 + k * 0.3, 0.7)

def ir(d=2.4):
    n = int(d * SR); t = tt(n); x = rng.standard_normal(n) * np.exp(-t * 2.4); x[:int(0.02 * SR)] = 0; return x / np.sqrt((x ** 2).sum())
def conv(x, h):
    m = len(x) + len(h); nf = 1 << (m - 1).bit_length(); return np.fft.irfft(np.fft.rfft(x, nf) * np.fft.rfft(h, nf), nf)[:len(x)]
L += conv(SL, ir()) * 0.55; R += conv(SRv, ir()) * 0.55
mix = np.stack([L, R]); mix = np.tanh(mix / np.abs(mix).max() * 1.4) / np.tanh(1.4) * 10 ** (-1 / 20)
fo = int(0.6 * SR); mix[:, -fo:] *= np.linspace(1, 0, fo) ** 2
with wave.open(outp, 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(mix.T, -1, 1) * 32767).astype('<i2').tobytes())
print('ok', piece)
