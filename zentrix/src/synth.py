"""ZENTRIX STUDIO · sonido de la intro (sintetizado con numpy, sin samples). 7 s, 48 kHz estéreo."""
import sys, wave
import numpy as np
SR, DUR = 48000, 12.0; N = int(SR * DUR); rng = np.random.default_rng(7)
T = dict(comet0=0.8, comet1=3.4, z0=2.6, s0=3.2, hit=4.9, word0=5.9, word1=7.5, stu0=7.5, end=11.2)
L = np.zeros(N); R = np.zeros(N); SL = np.zeros(N); SRv = np.zeros(N)
tt = lambda n: np.arange(n) / SR
def add(sig, t0, g=1.0, pan=0.0, send=0.0):
    i = int(t0 * SR); n = min(len(sig), N - i)
    if n <= 0: return
    a = (pan + 1) * np.pi / 4; l, r = sig[:n] * np.cos(a) * 1.414 * g, sig[:n] * np.sin(a) * 1.414 * g
    L[i:i + n] += l; R[i:i + n] += r; SL[i:i + n] += l * send; SRv[i:i + n] += r * send
def onepole(x, fc):   # paso-bajas de un polo con corte variable (vectorizado por bloques)
    y = np.zeros_like(x); s = 0.0; fc = np.broadcast_to(fc, x.shape)
    k = 1 - np.exp(-2 * np.pi * fc / SR)
    for i in range(len(x)): s += k[i] * (x[i] - s); y[i] = s
    return y
def fade(x, a=0.003, b=0.02):
    e = np.ones(len(x)); na, nb = int(a * SR), int(b * SR)
    if na: e[:na] = np.linspace(0, 1, na)
    if nb: e[-nb:] *= np.linspace(1, 0, nb)
    return x * e

# riser: ruido filtrado que se abre + tono que sube, hasta el golpe
n = int((T['hit'] - 0.05) * SR); x = tt(n) / (n / SR)
nz = rng.standard_normal(n); r1 = onepole(nz, 200 * (9000 / 200) ** (x ** 1.6)) - onepole(nz, 120) * 0.8
f = 110 * 2 ** (x * 2.5); tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25 + np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR) * 0.12
add(fade((r1 * 0.5 + tone) * x ** 2.2, 0.05, 0.01), 0.05, 0.55, 0, 0.3)
# cometa: barrido que viaja de izquierda a derecha
n = int((T['comet1'] - T['comet0']) * SR); x = tt(n) / (n / SR); nz = rng.standard_normal(n)
cm = (onepole(nz, 800 + 6000 * np.sin(np.pi * x)) - onepole(nz, 400)) * np.sin(np.pi * x) ** 1.5
for k, p in enumerate(np.linspace(-0.8, 0.8, 8)):   # paneo por tramos
    a, b = int(k * n / 8), int((k + 1) * n / 8); seg = fade(cm[a:b] * 0.6, 0.01, 0.01); add(seg, T['comet0'] + a / SR, 1.0, p, 0.25)
# contornos de Z y S dibujándose: brillo suave que sube
for t0, base in ((T['z0'], 660), (T['s0'], 880)):
    n = int(1.3 * SR); t = tt(n); x = t / 1.3
    f = base * 2 ** (x * 0.5); sh = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.6 + np.sin(2 * np.pi * np.cumsum(f * 2.01) / SR) * 0.3
    add(fade(sh * np.sin(np.pi * x) ** 2 * 0.12, 0.05, 0.1), t0, 1.0, -0.3 if base < 700 else 0.3, 0.6)
n = int(0.6 * SR); x = tt(n) / 0.6; nz = rng.standard_normal(n)
wz = (onepole(nz, 300 * (7000 / 300) ** x) - onepole(nz, 200)) * np.where(x < 0.8, (x / 0.8) ** 2, np.exp(-(x - 0.8) * 20))
add(fade(wz * 0.6), T['hit'] - 0.5, 0.6, 0, 0.2)
# golpe: sub + crack + cola metálica
n = int(2.6 * SR); t = tt(n); fsub = 32 + 80 * np.exp(-t * 8)
sub = np.sin(2 * np.pi * np.cumsum(fsub) / SR) * np.exp(-t * 1.8)
crack = (rng.standard_normal(n) - onepole(rng.standard_normal(n), 1500)) * np.exp(-t * 18) * 0.5
metal = sum(np.sin(2 * np.pi * fr * t) * np.exp(-t * d) for fr, d in ((523, 1.6), (784, 2.2), (1046, 2.6), (1568, 3.4))) * 0.08
add(fade(np.tanh((sub * 1.4 + crack + metal) * 1.3)), T['hit'], 0.95, 0, 0.35)
# shimmer al brillo
for k, fr in enumerate((1760, 2349, 2637, 3520)):
    n = int(1.5 * SR); t = tt(n); s = np.sin(2 * np.pi * fr * t + 2 * np.sin(2 * np.pi * fr * 2.01 * t) * np.exp(-t * 6)) * np.exp(-t * 3)
    add(fade(s * 0.12), T['hit'] + 0.25 + k * 0.07, 1.0, -0.5 + k * 0.33, 0.6)
# tecleo digital por letra de ZENTRIX
for k in range(7):
    n = int(0.08 * SR); t = tt(n); fr = 1400 + 160 * k
    add(fade(np.sign(np.sin(2 * np.pi * fr * t)) * np.exp(-t * 60) * 0.12), T['word0'] + k * (T['word1'] - T['word0']) / 8.5 + 0.12, 1.0, -0.6 + k * 0.2, 0.2)
# STUDIO: whoosh suave y abierto
n = int(0.7 * SR); x = tt(n) / 0.7; nz = rng.standard_normal(n)
add(fade((onepole(nz, 2000 + 4000 * x) - onepole(nz, 900)) * np.sin(np.pi * x) * 0.35), T['stu0'] - 0.1, 1.0, 0, 0.4)
# pad cinematográfico (Re menor 9) desde el golpe
n = int((DUR - T['hit']) * SR); t = tt(n); pad = np.zeros(n)
for m in (38, 45, 50, 53, 57, 64):
    fr = 440 * 2 ** ((m - 69) / 12)
    for det in (-0.08, 0, 0.08):
        ph = rng.uniform(0, 6); fd = fr * 2 ** (det / 12)
        pad += sum(np.sin(2 * np.pi * fd * h * t + ph * h) / h for h in range(1, 6)) * 0.5
env = np.minimum(1, t / 0.4) * np.clip((T['end'] + 0.5 - T['hit'] - t) / 0.9, 0, 1)
add(onepole(pad * env * 0.018, 1800.0), T['hit'], 1.0, 0, 0.5)
# reverb por convolución (IR sintética)
def ir(d=2.5):
    n = int(d * SR); t = tt(n); x = rng.standard_normal(n) * np.exp(-t * 2.2); x[:int(0.02 * SR)] = 0; return x / np.sqrt((x ** 2).sum())
def conv(x, h):
    m = len(x) + len(h); nf = 1 << (m - 1).bit_length(); return np.fft.irfft(np.fft.rfft(x, nf) * np.fft.rfft(h, nf), nf)[:len(x)]
L += conv(SL, ir()) * 0.6; R += conv(SRv, ir()) * 0.6
mix = np.stack([L, R]); mix = np.tanh(mix / np.abs(mix).max() * 1.4) / np.tanh(1.4) * 10 ** (-1 / 20)
fo = int(0.5 * SR); mix[:, -fo:] *= np.linspace(1, 0, fo) ** 2
pcm = (np.clip(mix.T, -1, 1) * 32767).astype('<i2')
with wave.open(sys.argv[1], 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('ok')
