"""Redibuja al niño en limpio y en alta resolución (colores planos + curvas lisas, sin manchas de compresión).
uso: python3 -I redibujar.py [escala]   lee nino.png (de separar.py) -> nino_hd.png"""
import sys, cv2, numpy as np
from PIL import Image
S = int(sys.argv[1]) if len(sys.argv) > 1 else 4
PAL = np.array([
    (234, 159, 97),   # 0 piel
    (210, 134, 73),   # 1 sombra de piel
    (150, 80, 36),    # 2 mandil / lengua
    (252, 250, 245),  # 3 blanco
    (233, 194, 145),  # 4 piel clara / reflejos
    (232, 220, 204),  # 5 sombra de la camisa
    (110, 60, 28),    # 6 brillo café
    (62, 28, 9),      # 7 línea (contorno y pelo)
], np.float32)
NF = 7; LN = 7
a = np.pad(np.array(Image.open('nino.png').convert('RGBA')), ((24, 24), (24, 24), (0, 0))); H, W = a.shape[:2]
OY = 24   # desplazamiento por el margen
alpha = a[..., 3] > 128
ff = alpha.astype(np.uint8) * 255; ff = np.pad(ff, 1); pad = np.zeros((H + 4, W + 4), np.uint8); cv2.floodFill(ff, pad, (0, 0), 128)
holes = (ff[1:-1, 1:-1] == 0); alpha |= holes
# silueta lisa: rellena muescas y suaviza escalones
sm = cv2.morphologyEx(alpha.astype(np.uint8), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
sm = cv2.GaussianBlur(sm.astype(np.float32), (0, 0), 2.0) > 0.5
holes |= sm & ~alpha; alpha = sm                   # huecos internos (rendijas semitransparentes del original)
a[holes, :3] = (62, 28, 9)
src = cv2.bilateralFilter(a[..., :3], 5, 30, 3)
toLab = lambda c: cv2.cvtColor(np.asarray(c, np.uint8).reshape(-1, 1, 3), cv2.COLOR_RGB2LAB).reshape(-1, 3).astype(np.float32)
lab = cv2.cvtColor(src, cv2.COLOR_RGB2LAB).astype(np.float32)
d = np.sqrt(((lab[:, :, None] - toLab(PAL)[None, None]) ** 2).sum(-1))
line = (d[..., :NF].min(-1) - d[..., LN] + 8) > 0
lbl = np.where(line, LN, d[..., :NF].argmin(-1))
# borde blanco del círculo viejo pegado al pelo/cabeza: todo lo claro a <=7 px de la silueta (arriba de la barbilla) es pelo
dist = cv2.distanceTransform(alpha.astype(np.uint8), cv2.DIST_L2, 5)
yy = np.arange(H)[:, None]
rim = alpha & ~line & (((dist <= 7) & (yy < 470 + OY)) | ((dist <= 15) & (yy < 330 + OY)) | ((dist <= 16) & (yy > 430 + OY) & (yy < 600 + OY) & (np.arange(W)[None, :] < 140 + OY)))
rim |= alpha & (yy < 168 + OY)          # arriba de la frente todo es pelo
line |= rim; lbl[rim] = LN
# franjas delgadas de color intermedio (halos) -> se marcan como dudosas
bad = np.zeros((H, W), bool)
for k in (0, 1, 2, 4, 5, 6):
    m = lbl == k
    r = 9 if k == 6 else 5
    keep = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (r, r))) > 0
    bad |= m & ~keep
# lo dudoso toma el relleno que más abunde a su alrededor (sin contar la línea), creciendo de afuera hacia adentro
for it in range(12):
    if not bad.any(): break
    ok = ~bad & ~line & alpha
    v = np.stack([cv2.blur(((lbl == k) & ok).astype(np.float32), (5, 5)) for k in range(NF)], -1)
    have = v.max(-1) > 0
    upd = bad & have
    lbl[upd] = v.argmax(-1)[upd]; bad &= ~upd
lbl[bad] = 0
# brillos de los ojos: islas chicas rodeadas de línea -> blanco
HL = []
n_, cc, st_, _ = cv2.connectedComponentsWithStats((~line & alpha).astype(np.uint8), connectivity=4)
for c_ in range(1, n_):
    x_, y_ = st_[c_, 0] + st_[c_, 2] / 2, st_[c_, 1] + st_[c_, 3] / 2
    if st_[c_, 4] < 70:
        if 60 + OY < x_ < 300 + OY and 290 + OY < y_ < 390 + OY:
            ys_, xs_ = np.where(cc == c_); r_ = max(2.5, np.sqrt(len(ys_) / np.pi) * 1.1)
            lbl[cc == c_] = LN; HL.append((xs_.mean(), ys_.mean(), r_))
        else: lbl[cc == c_] = LN
lbl[~alpha] = LN
# subir de escala: cada capa se agranda y suaviza; en cada pixel gana la más fuerte
up = lambda x, s: cv2.GaussianBlur(cv2.resize(x.astype(np.float32), (W * S, H * S), interpolation=cv2.INTER_CUBIC), (0, 0), s)
LH = np.argmax(np.stack([up(lbl == k, 0.8 * S) for k in range(len(PAL))], -1), -1)
rgb = PAL[LH]
fe = cv2.dilate((cv2.Canny(LH.astype(np.uint8) * 30, 1, 1) > 0).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
b = cv2.GaussianBlur(rgb, (0, 0), 1.1); rgb[fe] = b[fe]
for x_, y_, r_ in HL:                     # brillos redondos en las pupilas
    cv2.circle(rgb, (int(x_ * S + S / 2), int(y_ * S + S / 2)), int(r_ * S), (252, 250, 245), -1, cv2.LINE_AA)
# ojos redibujados como vectores (en el original son muy chicos y la compresión los deforma)
# (centro del ojo, radios, ángulo, centro de pupila, radios pupila, brillo) en coordenadas de nino.png
EYES = [((95, 330), (28, 37), 10, (107, 338), (16, 25), (103, 330), 5.0),
        (( 244, 336), (35, 42), 8, (256, 350), (21, 29), (249, 341), 6.0)]
def P(x, y): return (int(round((x + 24) * S)), int(round((y + 24) * S)))
def R(r): return int(round(r * S))
SKIN = tuple(int(v) for v in PAL[0]); LC = tuple(int(v) for v in PAL[7]); WH = tuple(int(v) for v in PAL[3])
for c, (rx, ry), ang, pc, (px, py), hl, hr in EYES:
    cv2.ellipse(rgb, P(*c), (R(rx + 7), R(ry + 5)), ang, 0, 360, SKIN, -1, cv2.LINE_AA)
    cv2.ellipse(rgb, P(*c), (R(rx + 3.6), R(ry + 3.6)), ang, 0, 360, LC, -1, cv2.LINE_AA)
    wm = np.zeros(rgb.shape[:2], np.uint8); cv2.ellipse(wm, P(*c), (R(rx), R(ry)), ang, 0, 360, 255, -1, cv2.LINE_AA)
    pm = np.zeros_like(wm); cv2.ellipse(pm, P(*pc), (R(px), R(py)), ang, 0, 360, 255, -1, cv2.LINE_AA)
    w_ = (wm / 255.0)[..., None]; p_ = (pm / 255.0)[..., None] * w_
    rgb[:] = rgb * (1 - w_) + np.array(WH) * w_
    rgb[:] = rgb * (1 - p_) + np.array(LC) * p_
    cv2.circle(rgb, P(*hl), R(hr), WH, -1, cv2.LINE_AA)
al = up(alpha, 0.6 * S); al = np.clip((al - 0.5) * 2.5 + 0.5, 0, 1)
out = np.dstack([rgb, al * 255]).clip(0, 255).astype(np.uint8)
Image.fromarray(out, 'RGBA').save('nino_hd.png'); print('nino_hd', out.shape[1], out.shape[0])
