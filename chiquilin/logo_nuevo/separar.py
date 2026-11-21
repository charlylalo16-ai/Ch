"""Separa del logo original: el niño y el texto EL CHIQUILÍN (quita círculo rojo, 'TACOS DE BIRRIA' y comida)."""
import numpy as np, cv2, sys
from PIL import Image, ImageDraw
src = sys.argv[1]; out = sys.argv[2]
im = Image.open(src).convert('RGBA'); a = np.array(im).astype(int); H, W = a.shape[:2]
r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
hsv = cv2.cvtColor(a[..., :3].astype(np.uint8), cv2.COLOR_RGB2HSV).astype(int); hh, ss, vv = hsv[..., 0], hsv[..., 1], hsv[..., 2]
red = ((hh < 8) | (hh > 168)) & (ss > 80) & (vv > 45)
# ---- niño: polígono que sigue su contorno izquierdo (deja fuera tazón, tacos y plato)
poly = [(1000, 60), (919, 330), (919, 400), (919, 440), (920, 480), (924, 520), (935, 560), (950, 585), (960, 597), (978, 612), (984, 624), (960, 655), (920, 705), (880, 760), (880, 776), (1300, 776), (1300, 745), (1298, 600), (1290, 510), (1318, 470), (1325, 380), (1326, 100)]
pm = Image.new('L', (W, H)); ImageDraw.Draw(pm).polygon(poly, fill=255); pm = np.array(pm) > 0
cream = (ss < 70) & (vv > 160)
xx = np.arange(W)[None, :].repeat(H, 0)
boy = pm & (al > 20) & ~red & ~(cream & (xx < 962) & (np.arange(H)[:, None] > 525) & (np.arange(H)[:, None] < 615)) & ~((hh > 15) & (hh < 40) & (ss > 90) & (vv > 150) & (np.arange(H)[:, None] > 740))
boy = cv2.morphologyEx(boy.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)) > 0
n, lab, st, _ = cv2.connectedComponentsWithStats(boy.astype(np.uint8)); boy = lab == (1 + np.argmax(st[1:, cv2.CC_STAT_AREA]))
boy = cv2.morphologyEx(boy.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)) > 0
# ---- texto: letras amarillas + su contorno café (todo lo que esté a <= 30 px del amarillo), sin rojo
yellow = (hh > 15) & (hh < 40) & (ss > 90) & (vv > 150) & (np.arange(H)[:, None] > 745)
yellow = cv2.morphologyEx(yellow.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
n, lab, st, _ = cv2.connectedComponentsWithStats(yellow); big = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > 300])
reach = cv2.dilate(big.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (61, 61))) > 0
brightred = ((hh < 8) | (hh > 168)) & (ss > 110) & (vv > 110)
orange = (hh >= 5) & (hh <= 17) & (ss > 110) & (vv > 120)
txt = reach & (al > 20) & ~brightred & ~orange & (np.arange(H)[:, None] > 740)
txt = cv2.morphologyEx(txt.astype(np.uint8), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
ff = txt.copy() * 255; pad = np.zeros((H + 2, W + 2), np.uint8); inv = (255 - ff).astype(np.uint8); cv2.floodFill(inv, pad, (0, 0), 0); txt = (txt > 0) | (inv > 0)
n, lab, st, _ = cv2.connectedComponentsWithStats(txt.astype(np.uint8)); txt = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > 5000])
# el relleno de huecos también tapó el área encerrada por el borde del plato: limitar a <= 27 px del amarillo
txt &= cv2.dilate(big.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (55, 55))) > 0
txt = cv2.morphologyEx(txt.astype(np.uint8), cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))) > 0
# borde superior parejo: las letras empiezan en y=784; solo el acento de la Í sube más
top = np.where((np.arange(W) > 1295) & (np.arange(W) < 1395), 736, 761)
txt &= np.arange(H)[:, None] >= top[None, :]
# niño: quitar lo que toca el texto y las líneas delgadas sueltas (contorno del círculo detrás)
boy = boy & ~(cv2.dilate(txt.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0)
core = cv2.morphologyEx(boy.astype(np.uint8), cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31)))
boy = boy & (cv2.dilate(core, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))) > 0)
n, lab, st, _ = cv2.connectedComponentsWithStats(boy.astype(np.uint8)); boy = lab == (1 + np.argmax(st[1:, cv2.CC_STAT_AREA]))
bf = boy.astype(np.uint8) * 255; pad = np.zeros((H + 2, W + 2), np.uint8); cv2.floodFill(bf, pad, (0, 0), 128); boy = bf != 128   # rellenar huecos internos
# pelo: en el original la parte de arriba/izquierda la tapaba el círculo rojo -> se reconstruye un domo liso
pts = np.array([(921, 352), (909, 310), (903, 255), (909, 200), (930, 148), (965, 108), (1005, 84), (1065, 68), (1145, 64), (1220, 80), (1270, 108)], np.float64)
tt_ = np.linspace(0, 1, len(pts)); ts = np.linspace(0, 1, 200)
curve = np.stack([np.interp(ts, tt_, pts[:, 0]), np.interp(ts, tt_, pts[:, 1])], 1)
curve = cv2.GaussianBlur(curve.reshape(-1, 1, 2).astype(np.float32), (1, 31), 0).reshape(-1, 2); curve[0], curve[-1] = pts[0], pts[-1]
dome = np.zeros((H, W), np.uint8); cv2.fillPoly(dome, [np.vstack([curve, [(1270, 300), (960, 360)]]).astype(np.int32)], 1)
hairpx = boy & (vv < 90) & (np.arange(H)[:, None] < 300)
hair_col = np.median(a[hairpx][:, :3], 0).astype(np.uint8)
add = (dome > 0) & ~boy
a[add, :3] = hair_col; a[add, 3] = 255; al = a[..., 3]
boy = boy | (dome > 0)
bf = boy.astype(np.uint8) * 255; pad = np.zeros((H + 2, W + 2), np.uint8); cv2.floodFill(bf, pad, (0, 0), 128); boy = bf != 128
# cuña beige (borde del plato) entre la quijada y el contorno, a la izquierda de la barbilla
ys_, xs_ = np.where(boy); bx0, by0 = xs_.min(), ys_.min()
yy_ = np.arange(H)[:, None]; xx_ = np.arange(W)[None, :]
wedge = boy & (ss < 90) & (vv > 150) & (xx_ < bx0 + 100) & (yy_ > by0 + 465) & (yy_ < by0 + 570)
boy = boy & ~wedge
boy = cv2.morphologyEx(boy.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)) > 0
n, lab, st, _ = cv2.connectedComponentsWithStats(boy.astype(np.uint8)); boy = lab == (1 + np.argmax(st[1:, cv2.CC_STAT_AREA]))
print('cuña px', int(wedge.sum()))
boy = cv2.morphologyEx(boy.astype(np.uint8), cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13))) > 0   # silueta lisa
# contorno café parejo alrededor de toda la silueta del niño (los bordes recortados quedan delineados como el resto)
ring = (cv2.dilate(boy.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))) > 0) & ~boy
a[ring, :3] = hair_col; a[ring, 3] = 255; al = a[..., 3]; boy = boy | ring
for name, m in (('nino', boy), ('texto', txt)):
    o = a.copy().astype(np.uint8); o[..., 3] = np.where(m, al, 0); img = Image.fromarray(o, 'RGBA'); img = img.crop(img.getbbox()); img.save(f'{out}/{name}.png'); print(name, img.size)
