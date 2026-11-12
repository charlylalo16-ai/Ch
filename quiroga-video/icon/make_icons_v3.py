"""Íconos v3: diseños más elaborados (medallón, Q en 3D, celular). Flores salen de la Q."""
import math
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
S = 1024
QM = Image.open('q_white.png').getchannel('A'); FL = Image.open('flores_clean.png')
BASE = (490, 470)
NAVY, NAVY3, MAG, GOLD, WHITE = (0, 32, 104), (0, 14, 58), (226, 0, 124), (246, 178, 30), (255, 255, 255)
F_BLACK = '/usr/share/fonts/opentype/inter/InterDisplay-Black.otf'

def radial(c_in, c_out, cx=0.5, cy=0.45, r=0.8):
    g = Image.radial_gradient('L').resize((int(S * r * 2),) * 2)
    m = Image.new('L', (S, S), 255); m.paste(g, (int(S * cx - S * r), int(S * cy - S * r)))
    return Image.composite(Image.new('RGB', (S, S), c_out), Image.new('RGB', (S, S), c_in), m).convert('RGBA')

def vgrad(c1, c2, w, h):
    g = Image.linear_gradient('L').resize((w, h))
    return Image.composite(Image.new('RGB', (w, h), c2), Image.new('RGB', (w, h), c1), g).convert('RGBA')

def soft(base, mask, x, y, col, op, blur, off=(0, 0)):
    P = blur * 3; a = Image.new('L', (mask.width + 2 * P, mask.height + 2 * P)); a.paste(mask, (P, P))
    l = Image.new('RGBA', a.size, col + (0,)); l.putalpha(a.point(lambda v: int(v * op)).filter(ImageFilter.GaussianBlur(blur)))
    base.alpha_composite(l, (x + off[0] - P, y + off[1] - P))

def q3d(base, qw, cx, cy, face=(WHITE, (215, 222, 240)), side=(MAG, (120, 0, 70)), depth=34, outline=None):
    """Q con extrusión 3D (capas apiladas) + cara con degradado y brillo. Devuelve (x, y, qh)."""
    qh = int(QM.height * qw / QM.width); m = QM.resize((qw, qh), Image.LANCZOS)
    x, y = cx - qw // 2, cy - qh // 2
    soft(base, m, x + depth, y + depth, (0, 0, 0), 0.45, 26, (8, 20))
    for i in range(depth, 0, -1):
        t = i / depth; col = tuple(int(side[0][k] * (1 - t) + side[1][k] * t) for k in range(3))
        l = Image.new('RGBA', m.size, col + (255,)); l.putalpha(m); base.alpha_composite(l, (x + int(i * 0.55), y + i))
    if outline:
        P = 8; om = Image.new('L', (qw + 2 * P, qh + 2 * P)); om.paste(m, (P, P)); om = om.filter(ImageFilter.MaxFilter(13)).filter(ImageFilter.GaussianBlur(1))
        l = Image.new('RGBA', om.size, outline + (255,)); l.putalpha(om); base.alpha_composite(l, (x - P, y - P))
    f = vgrad(*face, qw, qh); f.putalpha(m); base.alpha_composite(f, (x, y))
    hl = Image.new('L', (qw, qh)); ImageDraw.Draw(hl).ellipse([-qw * 0.25, -qh * 0.6, qw * 0.85, qh * 0.32], fill=80)
    hl = ImageChops.multiply(hl.filter(ImageFilter.GaussianBlur(18)), m)
    base.alpha_composite(Image.merge('RGBA', (*[Image.new('L', (qw, qh), 255)] * 3, hl)), (x, y))
    return x, y, qh

def bouquet(base, ax, ay, fw, rot=-8, glow=None, behind=None):
    k = fw / FL.width; fl = FL.resize((fw, int(FL.height * k)), Image.LANCZOS)
    big = Image.new('RGBA', (fw * 2, fl.height * 2)); big.alpha_composite(fl, (int(fw - BASE[0] * k), int(fl.height - BASE[1] * k)))
    big = big.rotate(rot, resample=Image.BICUBIC, center=(fw, fl.height)); px, py = int(ax - fw), int(ay - fl.height)
    if glow: soft(base, big.getchannel('A'), px, py, glow, 0.6, 12)
    base.alpha_composite(big, (px, py))

def sparkle(d, x, y, r, col):
    d.polygon([(x, y - r), (x + r * 0.22, y - r * 0.22), (x + r, y), (x + r * 0.22, y + r * 0.22), (x, y + r), (x - r * 0.22, y + r * 0.22), (x - r, y), (x - r * 0.22, y - r * 0.22)], fill=col)

def text_c(base, txt, cx, y, size, fill, track=8, shadow=True):
    f = ImageFont.truetype(F_BLACK, size); d = ImageDraw.Draw(base)
    w = sum(d.textlength(c, font=f) for c in txt) + track * (len(txt) - 1); x = cx - w / 2
    for c in txt:
        if shadow: d.text((x + 3, y + 5), c, font=f, fill=(0, 0, 0, 90))
        d.text((x, y), c, font=f, fill=fill); x += d.textlength(c, font=f) + track
    return w

def arc_text(base, txt, cx, cy, r, size, fill, start=-90, spread=300):
    f = ImageFont.truetype(F_BLACK, size); n = len(txt)
    for i, ch in enumerate(txt):
        ad = start + spread / 2 - spread * (i + 0.5) / n; a = math.radians(ad)
        g = Image.new('RGBA', (size * 2, size * 2)); ImageDraw.Draw(g).text((size, size), ch, font=f, fill=fill, anchor='mm')
        g = g.rotate(90 - ad, resample=Image.BICUBIC)
        base.alpha_composite(g, (int(cx + r * math.cos(a) - size), int(cy + r * math.sin(a) - size)))

def pill(base, txt, cx, cy, size, bg, fg):
    f = ImageFont.truetype(F_BLACK, size); d = ImageDraw.Draw(base); tr = size * 0.12
    w = sum(d.textlength(c, font=f) for c in txt) + tr * (len(txt) - 1); pw, ph = w + size * 1.4, size * 1.65
    sh = Image.new('L', (int(pw), int(ph))); ImageDraw.Draw(sh).rounded_rectangle([0, 0, pw - 1, ph - 1], ph / 2, fill=255)
    soft(base, sh, int(cx - pw / 2), int(cy - ph / 2), (0, 0, 0), 0.4, 14, (0, 10))
    d.rounded_rectangle([cx - pw / 2, cy - ph / 2, cx + pw / 2, cy + ph / 2], ph / 2, fill=bg)
    d.rounded_rectangle([cx - pw / 2 + 6, cy - ph / 2 + 6, cx + pw / 2 - 6, cy + ph / 2 - 6], ph / 2 - 6, outline=WHITE + (110,), width=3)
    x = cx - w / 2
    for c in txt: d.text((x, cy), c, font=f, fill=fg, anchor='lm'); x += d.textlength(c, font=f) + tr

# ---------------------------------------------------------------- D · Medallón
def opcion_D():
    im = radial((18, 60, 170), NAVY3, r=0.85); d = ImageDraw.Draw(im)
    for k in range(24):   # rayos de luz suaves
        a = math.radians(k * 15); ray = Image.new('L', (S, S)); ImageDraw.Draw(ray).polygon([(512, 480), (512 + 900 * math.cos(a - 0.05), 480 + 900 * math.sin(a - 0.05)), (512 + 900 * math.cos(a + 0.05), 480 + 900 * math.sin(a + 0.05))], fill=18)
        im.alpha_composite(Image.merge('RGBA', (*[Image.new('L', (S, S), 255)] * 3, ray.filter(ImageFilter.GaussianBlur(8)))))
    cx, cy = 512, 540
    disc = Image.new('L', (S, S)); ImageDraw.Draw(disc).ellipse([cx - 360, cy - 360, cx + 360, cy + 360], fill=255)
    soft(im, disc, 0, 0, (0, 0, 0), 0.5, 30, (0, 24))
    d.ellipse([cx - 360, cy - 360, cx + 360, cy + 360], fill=MAG)
    d.ellipse([cx - 350, cy - 350, cx + 350, cy + 350], outline=(255, 120, 190), width=3)
    for k in range(48):
        a = math.radians(k * 7.5); rr = 336; d.ellipse([cx + rr * math.cos(a) - 4, cy + rr * math.sin(a) - 4, cx + rr * math.cos(a) + 4, cy + rr * math.sin(a) + 4], fill=GOLD)
    arc_text(im, 'QUIROGA DIGITAL', cx, cy, 300, 52, WHITE, start=90, spread=150)
    inner = vgrad(WHITE, (226, 232, 246), 500, 500); m = Image.new('L', (500, 500)); ImageDraw.Draw(m).ellipse([0, 0, 499, 499], fill=255); inner.putalpha(m)
    im.alpha_composite(inner, (cx - 250, cy - 250)); d.ellipse([cx - 250, cy - 250, cx + 250, cy + 250], outline=GOLD, width=8)
    x, y, qh = q3d(im, 280, cx, cy + 30, face=((20, 60, 160), NAVY3), side=(MAG, (110, 0, 60)), depth=22)
    bouquet(im, x + 0.66 * 280, y + 0.07 * qh, 520, glow=WHITE)
    for (sx, sy, r) in [(250, 230, 18), (800, 300, 14), (840, 760, 12), (190, 700, 10)]: sparkle(d, sx, sy, r, WHITE)
    return im

# ---------------------------------------------------------------- E · Q en 3D
def opcion_E():
    im = radial((96, 30, 160), (8, 10, 60), cx=0.5, cy=0.38, r=0.9)
    glow = Image.new('L', (S, S)); ImageDraw.Draw(glow).ellipse([212, 200, 812, 800], fill=120)
    im.alpha_composite(Image.merge('RGBA', (Image.new('L', (S, S), 255), Image.new('L', (S, S), 60), Image.new('L', (S, S), 170), glow.filter(ImageFilter.GaussianBlur(90)))))
    d = ImageDraw.Draw(im)
    for r_, a_ in ((380, 60), (440, 35)): d.ellipse([512 - r_, 520 - r_, 512 + r_, 520 + r_], outline=(255, 255, 255, a_), width=4)
    x, y, qh = q3d(im, 370, 495, 560, depth=40, outline=None)
    bouquet(im, x + 0.66 * 370, y + 0.07 * qh, 450, glow=(255, 220, 240))
    pill(im, 'DIGITAL', 512, 878, 68, MAG, WHITE)
    for (sx, sy, r) in [(210, 260, 20), (830, 220, 14), (860, 640, 16), (170, 620, 11), (760, 110, 9)]: sparkle(d, sx, sy, r, (255, 255, 255, 230))
    return im

# ---------------------------------------------------------------- F · Celular
def opcion_F():
    im = radial((230, 30, 140), (60, 0, 80), cx=0.3, cy=0.25, r=1.1)
    band = Image.new('L', (S, S)); ImageDraw.Draw(band).polygon([(0, 640), (S, 420), (S, S), (0, S)], fill=255)
    nv = vgrad((0, 51, 153), NAVY3, S, S); nv.putalpha(band); im.alpha_composite(nv)
    d = ImageDraw.Draw(im); px0, py0, pw, ph = 292, 250, 440, 700
    body = Image.new('L', (pw, ph)); ImageDraw.Draw(body).rounded_rectangle([0, 0, pw - 1, ph - 1], 70, fill=255)
    soft(im, body, px0, py0, (0, 0, 0), 0.55, 34, (18, 30))
    d.rounded_rectangle([px0, py0, px0 + pw, py0 + ph], 70, fill=(18, 18, 26))
    scr = vgrad((255, 255, 255), (222, 230, 248), pw - 44, ph - 44); m = Image.new('L', scr.size); ImageDraw.Draw(m).rounded_rectangle([0, 0, scr.width - 1, scr.height - 1], 50, fill=255); scr.putalpha(m)
    im.alpha_composite(scr, (px0 + 22, py0 + 22)); d.rounded_rectangle([px0 + pw / 2 - 50, py0 + 34, px0 + pw / 2 + 50, py0 + 50], 8, fill=(18, 18, 26))
    x, y, qh = q3d(im, 280, 512, 560, face=((20, 60, 160), NAVY3), side=(MAG, (110, 0, 60)), depth=20)
    bouquet(im, x + 0.66 * 280, y + 0.07 * qh, 500, glow=WHITE)
    pill(im, 'DIGITAL', 512, 830, 54, MAG, WHITE)
    for (sx, sy, r) in [(190, 300, 18), (850, 260, 14), (860, 760, 12)]: sparkle(d, sx, sy, r, WHITE)
    return im

if __name__ == '__main__':
    opts = {'D': opcion_D(), 'E': opcion_E(), 'F': opcion_F()}
    for k, im in opts.items():
        im.convert('RGB').save(f'v3_opcion_{k}_1024.png'); im.convert('RGB').resize((512, 512), Image.LANCZOS).save(f'v3_opcion_{k}_512.png')
    prev = Image.new('RGB', (3 * 420 + 40, 470), (235, 236, 240)); dp = ImageDraw.Draw(prev)
    for i, (k, im) in enumerate(opts.items()):
        big = im.resize((300, 300), Image.LANCZOS); m = Image.new('L', (300, 300), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, 299, 299], 70, fill=255)
        prev.paste(big, (40 + i * 420, 30), m)
        for j, sz in enumerate((96, 48)):
            sm = im.resize((sz, sz), Image.LANCZOS); m2 = Image.new('L', (sz, sz), 0); ImageDraw.Draw(m2).ellipse([0, 0, sz - 1, sz - 1], fill=255)
            prev.paste(sm, (40 + i * 420 + 60 + j * 130, 350 + (96 - sz) // 2), m2)
        dp.text((40 + i * 420 + 290, 390), k, fill=(0, 32, 104))
    prev.save('v3_propuestas.png')
