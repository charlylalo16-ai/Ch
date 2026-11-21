"""Logo nuevo de El Chiquilín (niño redibujado + texto), en alta resolución.
uso: python3 -I componer.py   (necesita nino_hd.png de redibujar.py y texto.png de separar.py)"""
import os, cv2, numpy as np
from PIL import Image
S = 4                                   # misma escala que redibujar.py
OUT = 'out'; os.makedirs(OUT, exist_ok=True)
BROWN = np.array([62, 28, 9], np.float32)
YCOL = np.array([246, 205, 70], np.float32)

def grow(m, r):        # dilatación por distancia (rápida para radios grandes)
    return cv2.distanceTransform((~m).astype(np.uint8), cv2.DIST_L2, 5) <= r
def fill_holes(m):
    ff = np.pad(m.astype(np.uint8) * 255, 1); pad = np.zeros((ff.shape[0] + 2, ff.shape[1] + 2), np.uint8)
    cv2.floodFill(ff, pad, (0, 0), 128); return ff[1:-1, 1:-1] != 128
def soft(m, s):
    return cv2.GaussianBlur(m.astype(np.float32), (0, 0), s)

# ---- texto: letras amarillas lisas + contorno café parejo, todo a escala S
t = np.array(Image.open('texto.png').convert('RGBA'))
P = 40; t = np.pad(t, ((P, P), (P, P), (0, 0)))
hsv = cv2.cvtColor(np.ascontiguousarray(t[..., :3]), cv2.COLOR_RGB2HSV).astype(int)
yel = (hsv[..., 0] > 15) & (hsv[..., 0] < 40) & (hsv[..., 1] > 90) & (hsv[..., 2] > 150) & (t[..., 3] > 128)
yel = cv2.morphologyEx(yel.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
n, lab, st, _ = cv2.connectedComponentsWithStats(yel); yel = np.isin(lab, [i for i in range(1, n) if st[i, 4] > 300])
h, w = yel.shape
yh = cv2.GaussianBlur(cv2.resize(yel.astype(np.float32), (w * S, h * S), interpolation=cv2.INTER_CUBIC), (0, 0), 1.2 * S)
ya = np.clip((yh - 0.5) * 3 + 0.5, 0, 1)                        # letra lisa con antialias
ym = yh > 0.5
om = fill_holes(grow(ym, 24 * S))
oa = np.clip(soft(om, 1.0 * S) * 1.6 - 0.3, 0, 1)
rgb = BROWN * (1 - ya[..., None]) + YCOL * ya[..., None]
TXT = Image.fromarray(np.dstack([rgb, oa * 255]).clip(0, 255).astype(np.uint8), 'RGBA'); TXT = TXT.crop(TXT.getbbox())
TXT.save(f'{OUT}/texto_el_chiquilin.png')

BOY = Image.open('nino_hd.png').convert('RGBA'); BOY = BOY.crop(BOY.getbbox())

def sticker(im, w=24, line=6):
    a = np.array(im)[..., 3] > 100
    r = fill_holes(grow(a, w * S)); r2 = grow(r, line * S)
    base = np.zeros(a.shape + (4,), np.float32)
    base[..., :3] = BROWN; base[..., 3] = np.clip(soft(r2, 0.8 * S) * 1.6 - 0.3, 0, 1) * 255
    wa = np.clip(soft(r, 0.8 * S) * 1.6 - 0.3, 0, 1)[..., None]
    base[..., :3] = base[..., :3] * (1 - wa) + 255 * wa
    b = Image.fromarray(base.clip(0, 255).astype(np.uint8), 'RGBA'); b.alpha_composite(im); return b

def vertical(circle=None, k=1.3):
    boy = BOY.resize((int(BOY.width * k), int(BOY.height * k)), Image.LANCZOS)
    M = 120 * S; W = TXT.width + 2 * M; top = (60 * S if circle else 0)
    oy = int(boy.height * 0.885)                     # el texto tapa el borde cortado de la camisa
    H = top + oy + TXT.height + 2 * M
    c = Image.new('RGBA', (W, H), (0, 0, 0, 0)); y0 = M + top
    bx = (W - boy.width) // 2 + int(TXT.width * 0.02)
    if circle:
        cr = int(boy.width * 0.62); cx, cy = W // 2, y0 + int(boy.height * 0.47)
        yy, xx = np.ogrid[:H, :W]; d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        cm = np.zeros((H, W, 4), np.float32)
        cm[..., :3] = BROWN; cm[..., 3] = np.clip(cr + 16 * S - d + 0.5, 0, 1) * 255
        ia = np.clip(cr - d + 0.5, 0, 1)[..., None]; cm[..., :3] = cm[..., :3] * (1 - ia) + np.array(circle) * ia
        c.alpha_composite(Image.fromarray(cm.astype(np.uint8), 'RGBA'))
    c.alpha_composite(boy, (bx, y0))
    c.alpha_composite(TXT, (M, y0 + oy))
    c = sticker(c)
    return c.crop(c.getbbox())

def guardar(im, name):
    im.save(f'{OUT}/{name}.png', optimize=True)
    for bg, suf in (((255, 255, 255), 'fondo_blanco'), ((38, 18, 8), 'fondo_oscuro')):
        s = max(im.size) + 200 * S; b = Image.new('RGB', (s, s), bg); b.paste(im, ((s - im.width) // 2, (s - im.height) // 2), im)
        b.resize((2000, 2000), Image.LANCZOS).save(f'{OUT}/{name}_{suf}.jpg', quality=95)
    print(name, im.size)

guardar(vertical(), 'logo_chiquilin_nuevo')
guardar(vertical(circle=(246, 160, 40)), 'logo_chiquilin_nuevo_circulo')
