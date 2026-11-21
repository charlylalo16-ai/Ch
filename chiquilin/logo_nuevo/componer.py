"""Logo nuevo de El Chiquilín: solo el niño + el texto. uso: python3 -I componer.py  (necesita nino.png y texto.png de separar.py)"""
import cv2, numpy as np
from PIL import Image, ImageFilter
OUT = 'out'; import os; os.makedirs(OUT, exist_ok=True)
BROWN = np.array([62, 30, 12])

def disk(r): return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
def soft(m, s=1.2):  # máscara booleana -> alfa suave
    return cv2.GaussianBlur(m.astype(np.float32), (0, 0), s)

# ---- texto reconstruido: amarillo original + contorno café uniforme
t = np.array(Image.open('texto.png').convert('RGBA')).astype(np.float32)
P = 40; t = np.pad(t, ((P, P), (P, P), (0, 0)))
hsv = cv2.cvtColor(t[..., :3].astype(np.uint8), cv2.COLOR_RGB2HSV).astype(int)
yel = (hsv[..., 0] > 15) & (hsv[..., 0] < 40) & (hsv[..., 1] > 90) & (hsv[..., 2] > 150) & (t[..., 3] > 128)
yel = cv2.morphologyEx(yel.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
n, lab, st, _ = cv2.connectedComponentsWithStats(yel); yel = np.isin(lab, [i for i in range(1, n) if st[i, 4] > 300])
yel = cv2.morphologyEx(yel.astype(np.uint8), cv2.MORPH_CLOSE, disk(2)) > 0
out_m = cv2.dilate(yel.astype(np.uint8), disk(24)) > 0
ff = out_m.astype(np.uint8) * 255; pad = np.zeros((ff.shape[0] + 2, ff.shape[1] + 2), np.uint8); cv2.floodFill(ff, pad, (0, 0), 128); out_m = ff != 128
ya = soft(cv2.dilate(yel.astype(np.uint8), disk(1)) > 0, 1.0)[..., None]
YCOL = np.array([246, 205, 70], np.float32)    # amarillo parejo (como el original, sin manchas de compresión)
rgb = BROWN * (1 - ya) + YCOL * ya
txt = np.dstack([rgb, soft(out_m) * 255]).clip(0, 255).astype(np.uint8)
TXT = Image.fromarray(txt, 'RGBA'); TXT = TXT.crop(TXT.getbbox())
TXT.save(f'{OUT}/texto_el_chiquilin.png')

BOY = Image.open('nino.png').convert('RGBA')

def sticker(im, w=22, line=0):
    a = np.array(im)[..., 3] > 100
    r = cv2.dilate(a.astype(np.uint8), disk(w)) > 0
    ff = r.astype(np.uint8) * 255; pad = np.zeros((ff.shape[0] + 2, ff.shape[1] + 2), np.uint8); cv2.floodFill(ff, pad, (0, 0), 128); r = ff != 128
    base = np.zeros(a.shape + (4,), np.float32)
    if line:
        r2 = cv2.dilate(r.astype(np.uint8), disk(line)) > 0
        base[..., :3] = BROWN; base[..., 3] = soft(r2) * 255
    wa = soft(r)[..., None]
    base[..., :3] = base[..., :3] * (1 - wa) + 255 * wa; base[..., 3] = np.maximum(base[..., 3], wa[..., 0] * 255)
    b = Image.fromarray(base.clip(0, 255).astype(np.uint8), 'RGBA'); b.alpha_composite(im); return b

def vertical(circle=None, k=1.3):
    boy = BOY.resize((int(BOY.width * k), int(BOY.height * k)), Image.LANCZOS)
    M = 120; W = TXT.width + 2 * M
    oy = int(boy.height * 0.88)                      # el texto tapa el borde cortado de la camisa
    H = oy + TXT.height + 2 * M + (60 if circle else 0)
    c = Image.new('RGBA', (W, H), (0, 0, 0, 0)); y0 = M + (60 if circle else 0)
    bx = (W - boy.width) // 2 + int(TXT.width * 0.02)
    if circle:
        cr = int(boy.width * 0.62); cx, cy = W // 2, y0 + int(boy.height * 0.47)
        m = np.zeros((H, W), np.uint8); cv2.circle(m, (cx, cy), cr, 1, -1)
        ring = cv2.dilate(m, disk(16)); cm = np.zeros((H, W, 4), np.float32)
        cm[..., :3] = BROWN; cm[..., 3] = soft(ring > 0) * 255
        ia = soft(m > 0)[..., None]; cm[..., :3] = cm[..., :3] * (1 - ia) + np.array(circle) * ia
        c.alpha_composite(Image.fromarray(cm.astype(np.uint8), 'RGBA'))
        # rayitos suaves dentro del círculo
    c.alpha_composite(boy, (bx, y0))
    c.alpha_composite(TXT, (M, y0 + oy))
    c = sticker(c, 24, 6)
    return c.crop(c.getbbox())

def guardar(im, name):
    im.save(f'{OUT}/{name}.png')
    for bg, suf in (((255, 255, 255), 'fondo_blanco'), ((38, 18, 8), 'fondo_oscuro')):
        s = max(im.size) + 200; b = Image.new('RGB', (s, s), bg); b.paste(im, ((s - im.width) // 2, (s - im.height) // 2), im)
        b.resize((1600, 1600), Image.LANCZOS).save(f'{OUT}/{name}_{suf}.jpg', quality=95)
    print(name, im.size)

guardar(vertical(), 'logo_chiquilin_nuevo')
guardar(vertical(circle=(246, 160, 40)), 'logo_chiquilin_nuevo_circulo')
