"""Íconos v4: base del v2 (Q + flores + DIGITAL) con acabado institucional: doble aro, cinta, sin efectos llamativos."""
import math
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import make_icons_v2 as V2
S = 1024; W = (255, 255, 255)
NAVY, NAVY2, NAVY3, MAG, GOLD = (0, 32, 104), (0, 51, 153), (0, 16, 64), (226, 0, 124), (198, 160, 82)
F = '/usr/share/fonts/opentype/inter/InterDisplay-Black.otf'

GAP = (222, 318)   # hueco del aro detrás de las flores (grados PIL: 0 = derecha, 270 = arriba)
K = 4              # sobremuestreo: líneas, aros y cinta se dibujan a 4x y se reducen (bordes suaves)
def _aa(im, draw_fn):
    big = Image.new('RGBA', (S * K, S * K), (0, 0, 0, 0)); draw_fn(ImageDraw.Draw(big))
    im.alpha_composite(big.resize((S, S), Image.LANCZOS))

def seal(im, cx, cy, r, outer, inner, dots=None):
    g0, g1 = GAP
    def fn(d):
        c, R = cx * K, r * K
        def arc(rr, w, col): d.arc([c - rr, cy * K - rr, c + rr, cy * K + rr], g1, g0 + 360, fill=col, width=w * K)
        arc(R, 18, outer); arc(R - 30 * K, 4, inner)
        for ang in (g0, g1):
            a = math.radians(ang); rr = R - 9 * K; x, y = c + rr * math.cos(a), cy * K + rr * math.sin(a)
            d.ellipse([x - 9 * K, y - 9 * K, x + 9 * K, y + 9 * K], fill=outer)
        if dots:
            for k in range(72):
                ang = k * 5
                if g0 - 4 < ang < g1 + 4: continue
                a = math.radians(ang); rr = R - 15 * K; x, y = c + rr * math.cos(a), cy * K + rr * math.sin(a)
                d.ellipse([x - 3 * K, y - 3 * K, x + 3 * K, y + 3 * K], fill=dots)
    _aa(im, fn)

def ribbon(im, txt, cx, cy, size, bg, fg, edge):
    f = ImageFont.truetype(F, size * K); tr = size * 0.18 * K
    def fn(d):
        c, y = cx * K, cy * K
        w = sum(d.textlength(ch, font=f) for ch in txt) + tr * (len(txt) - 1); pw, ph = w + size * 1.6 * K, size * 1.55 * K
        x0, x1, y0, y1 = c - pw / 2, c + pw / 2, y - ph / 2, y + ph / 2; n = ph * 0.35; o = 16 * K
        for s_ in (-1, 1):
            xa = x0 if s_ < 0 else x1; xt = xa + s_ * ph * 0.75
            d.polygon([(xa, y0 + o), (xt, y0 + o), (xt - s_ * n, y + 8 * K), (xt, y1 + o), (xa, y1 + o)], fill=edge)
        d.rectangle([x0, y0, x1, y1], fill=bg)
        d.line([(x0 + 10 * K, y0 + 9 * K), (x1 - 10 * K, y0 + 9 * K)], fill=GOLD, width=3 * K); d.line([(x0 + 10 * K, y1 - 9 * K), (x1 - 10 * K, y1 - 9 * K)], fill=GOLD, width=3 * K)
        x = c - w / 2
        for ch in txt: d.text((x, y + 2 * K), ch, font=f, fill=fg, anchor='lm'); x += d.textlength(ch, font=f) + tr
    _aa(im, fn)

def build(bg, qfill, outline, ring_o, ring_i, dots, rib_bg, rib_fg, rib_edge, glow):
    im = bg; cx, cy = 512, 470
    seal(im, cx, cy + 20, 400, ring_o, ring_i, dots)
    q, pad, qh = V2.q_layer(330, *qfill, outline=outline, ow=10 if outline else 0)
    qx, qy = cx - q.width // 2, cy + 25 - q.height // 2
    V2.bouquet(im, qx + pad + 0.66 * 330, qy + pad + 0.07 * qh, 400, glow=glow)
    V2.drop(im, q, qx, qy, op=0.35); im.alpha_composite(q, (qx, qy))
    ribbon(im, 'DIGITAL', 512, 860, 74, rib_bg, rib_fg, rib_edge)
    return im

def G(): return build(V2.radial((20, 70, 190), NAVY3, cy=0.42, r=0.85), (W, (220, 226, 242)), None, MAG, GOLD, GOLD, MAG, W, (150, 0, 82), W)
def H(): return build(V2.radial((255, 255, 255), (228, 233, 245), cy=0.42, r=0.85), ((25, 65, 165), NAVY3), None, NAVY, MAG, MAG, NAVY, W, NAVY3, None)
def I():
    bg = V2.radial((20, 70, 190), NAVY3, cy=0.42, r=0.85); d = ImageDraw.Draw(bg)
    d.rectangle([0, 0, S, 26], fill=MAG); d.rectangle([0, S - 26, S, S], fill=MAG)
    return build(bg, (W, (220, 226, 242)), None, W, GOLD, None, W, NAVY, (190, 196, 214), W)

if __name__ == '__main__':
    opts = {'G': G(), 'H': H(), 'I': I()}
    for k, im in opts.items():
        im.convert('RGB').save(f'v4_opcion_{k}_1024.png'); im.convert('RGB').resize((512, 512), Image.LANCZOS).save(f'v4_opcion_{k}_512.png')
    prev = Image.new('RGB', (3 * 420 + 40, 470), (235, 236, 240)); dp = ImageDraw.Draw(prev)
    for i, (k, im) in enumerate(opts.items()):
        big = im.resize((300, 300), Image.LANCZOS); m = Image.new('L', (300, 300), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, 299, 299], 70, fill=255)
        prev.paste(big, (40 + i * 420, 30), m)
        for j, sz in enumerate((96, 48)):
            sm = im.resize((sz, sz), Image.LANCZOS); m2 = Image.new('L', (sz, sz), 0); ImageDraw.Draw(m2).ellipse([0, 0, sz - 1, sz - 1], fill=255)
            prev.paste(sm, (40 + i * 420 + 60 + j * 130, 350 + (96 - sz) // 2), m2)
        dp.text((40 + i * 420 + 290, 390), k, fill=(0, 32, 104))
    prev.save('v4_propuestas.png')
