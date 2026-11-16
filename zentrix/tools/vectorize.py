"""Reconstruye el logo ZENTRIX en vectores limpios (JSON):
Z, S y rayita como contornos; la órbita como línea central con grosor; ZENTRIX y STUDIO letra por letra."""
import json, sys, math
import numpy as np, cv2
from PIL import Image
src, out = sys.argv[1], sys.argv[2]
a = np.array(Image.open(src).convert('RGB')).astype(int); H, W = a.shape[:2]
r, g, b = a[..., 0], a[..., 1], a[..., 2]; mx = a.max(axis=2); mn = a.min(axis=2); sat = mx - mn
yy, xx = np.mgrid[0:H, 0:W]
blue = (b > r + 60) & (b > 120); silver = (sat < 45) & (mx > 110); emb = yy < 1045
U = 4

def trace(m, eps=0.7, minarea=50, mode=cv2.RETR_CCOMP):
    m = m.astype(np.uint8) * 255
    big = cv2.resize(m, (W * U, H * U), interpolation=cv2.INTER_LINEAR); big = cv2.GaussianBlur(big, (0, 0), U * 0.7)
    _, big = cv2.threshold(big, 127, 255, cv2.THRESH_BINARY)
    cs, _ = cv2.findContours(big, mode, cv2.CHAIN_APPROX_NONE); P = []
    for c in cs:
        if abs(cv2.contourArea(c)) < minarea * U * U: continue
        c = cv2.approxPolyDP(c, eps * U, True); P.append([[round(float(p[0][0]) / U, 2), round(float(p[0][1]) / U, 2)] for p in c])
    return P
def close(m, k, shape=cv2.MORPH_ELLIPSE):
    return cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, cv2.getStructuringElement(shape, k)) > 0
def biggest(m):
    n, lab, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8)); i = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA]); return lab == i

data = {'W': W, 'H': H}
# --- Z (plata): cerrar el hueco donde pasa la órbita
Z = biggest(close(silver & emb, (9, 61), cv2.MORPH_RECT)); data['Z'] = trace(Z, eps=0.8, minarea=5000, mode=cv2.RETR_EXTERNAL)
# --- S (azul): componente grande del azul, cerrando el cruce de la órbita
S_area = emb & (xx > 1140)
core = biggest(cv2.morphologyEx((blue & S_area).astype(np.uint8), cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (49, 49))) > 0)
S = core   # provisional (para encontrar la órbita); se rehace abajo
# --- rayita azul dentro de la Z
sl = blue & (xx > 950) & (xx < 1160) & (yy > 640) & (yy < 820); data['slash'] = trace(biggest(sl), eps=0.8, minarea=300, mode=cv2.RETR_EXTERNAL)
# --- órbita: elipse aproximada y luego línea central real con grosor
ringpx = blue & emb & ~S & ~(close(S, (25, 25)))
pts = np.column_stack(np.where(ringpx))[:, ::-1].astype(np.float32)
(ecx, ecy), (ew, eh), ang = cv2.fitEllipse(pts)
th = math.radians(ang); ca, sa = math.cos(th), math.sin(th); A, B = ew / 2, eh / 2
cl = []
for i in range(720):
    t = 2 * math.pi * i / 720; ex, ey = A * math.cos(t), B * math.sin(t)
    x0, y0 = ecx + ex * ca - ey * sa, ecy + ex * sa + ey * ca
    nx, ny = (ex / A ** 2) * ca - (ey / B ** 2) * sa, (ex / A ** 2) * sa + (ey / B ** 2) * ca; nl = math.hypot(nx, ny); nx, ny = nx / nl, ny / nl
    hits = [k for k in range(-60, 61) if 0 <= int(y0 + ny * k) < H and 0 <= int(x0 + nx * k) < W and ringpx[int(y0 + ny * k), int(x0 + nx * k)]]
    if hits:
        # segmento contiguo más cercano a la elipse
        segs, cur = [], [hits[0]]
        for k in hits[1:]:
            if k == cur[-1] + 1: cur.append(k)
            else: segs.append(cur); cur = [k]
        segs.append(cur); s = min(segs, key=lambda q: abs((q[0] + q[-1]) / 2))
        m = (s[0] + s[-1]) / 2; cl.append([x0 + nx * m, y0 + ny * m, len(s)])
    else: cl.append(None)
# rellenar huecos (donde la tapan Z/S) interpolando, y suavizar
n = len(cl); good = [i for i in range(n) if cl[i]]
arr = np.zeros((n, 3))
for i in range(n):
    if cl[i]: arr[i] = cl[i]; continue
    p = max([j for j in good if j < i], default=good[-1] - n); q = min([j for j in good if j > i], default=good[0] + n)
    f = (i - p) / (q - p); arr[i] = np.array(cl[p % n]) * (1 - f) + np.array(cl[q % n]) * f
k = np.ones(41) / 41
for c in range(3): arr[:, c] = np.convolve(np.concatenate([arr[-20:, c], arr[:, c], arr[:20, c]]), k, 'valid')
arr[:, 2] = np.clip(arr[:, 2], 12, 30)
data['ring'] = {'pts': np.round(arr, 2).tolist(), 'ellipse': [ecx, ecy, A, B, ang]}
# --- S final: azul menos la banda de la órbita fuera del núcleo de la S (esquinas intactas)
band = np.zeros((H, W), np.uint8)
for i in range(len(arr)):
    x, y, w = arr[i]; x2, y2, _ = arr[(i + 1) % len(arr)]; cv2.line(band, (int(x), int(y)), (int(x2), int(y2)), 255, int(w + 14))
coreD = cv2.dilate(core.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))) > 0
S = (blue | ((b > r + 30) & (mx > 90))) & S_area & ~((band > 0) & ~coreD)
S = biggest(close(S, (9, 9)))
data['S'] = trace(S, eps=0.7, minarea=5000, mode=cv2.RETR_EXTERNAL)
# --- textos: letra por letra con su color
def letters(region, ymin, ymax):
    m = region & (mx > 110); cs = trace(m, eps=0.5, minarea=20); groups = []
    for c in cs:
        xs = [p[0] for p in c]; ys = [p[1] for p in c]; bb = [min(xs), min(ys), max(xs), max(ys)]
        for gp in groups:
            if bb[0] >= gp['bb'][0] - 2 and bb[2] <= gp['bb'][2] + 2 and bb[1] >= gp['bb'][1] - 2: gp['c'].append(c); break
        else: groups.append({'bb': bb, 'c': [c]})
    groups.sort(key=lambda gp: gp['bb'][0])
    for gp in groups:
        x0, y0, x1, y1 = (int(v) for v in gp['bb']); sub = a[y0:y1 + 1, x0:x1 + 1].reshape(-1, 3); sub = sub[sub.max(axis=1) > 110]
        col = sub.mean(axis=0) if len(sub) else [255, 255, 255]; gp['col'] = [int(v) for v in col]
    return groups
data['zentrix'] = letters((yy >= 1045) & (yy < 1260), 1045, 1260)
data['studio'] = letters(yy >= 1260, 1260, H)
json.dump(data, open(out, 'w'))
print('Z', [len(c) for c in data['Z']], 'S', [len(c) for c in data['S']], 'slash', len(data['slash']), 'zentrix', len(data['zentrix']), 'studio', len(data['studio']), 'ellipse', [round(v) for v in data['ring']['ellipse']])
