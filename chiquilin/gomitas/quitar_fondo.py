"""Quita el fondo blanco del logo de gomitas (relleno desde las orillas) -> src/brand/logo_gomitas.png (RGBA)."""
import cv2, numpy as np
from PIL import Image
a = np.array(Image.open('src/brand/logo_gomitas_original.png').convert('RGB'))
H, W = a.shape[:2]
white = (a.min(-1) > 225).astype(np.uint8)
# fondo = blanco conectado a las orillas
n, lab = cv2.connectedComponents(white, connectivity=4)
edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
bg = np.isin(lab, list(edge))
fg = ~bg
fg = cv2.morphologyEx(fg.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)) > 0
n, lab, st, _ = cv2.connectedComponentsWithStats(fg.astype(np.uint8)); fg = np.isin(lab, [i for i in range(1, n) if st[i, 4] > 150])
# alfa suave: el borde se mezcla en vez de quedar dentado
al = cv2.GaussianBlur(fg.astype(np.float32), (0, 0), 0.8)
# des-mezclar el blanco del antialias en el borde
out = np.dstack([a, (al * 255).astype(np.uint8)])
Image.fromarray(out, 'RGBA').save('src/brand/logo_gomitas.png'); print('ok', fg.mean())
