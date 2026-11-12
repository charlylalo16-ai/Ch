"""Íconos v2 (más ricos): luz, profundidad, aro, Q con volumen y palabra QUIROGA. Flores salen de la Q."""
import math
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
S = 1024
Qw, FL = Image.open('q_white.png'), Image.open('flores_clean.png')
QM = Qw.getchannel('A')
BASE = (490, 470)
WORD = 'DIGITAL'
NAVY, NAVY2, NAVY3, MAG, MAG2, GOLD = (0, 32, 104), (0, 51, 153), (0, 16, 64), (226, 0, 124), (181, 0, 98), (246, 168, 0)
F_BLACK = '/usr/share/fonts/opentype/inter/InterDisplay-Black.otf'

def radial(c_in, c_out, cx=0.5, cy=0.42, r=0.75):
    g = Image.radial_gradient('L').resize((int(S * r * 2), int(S * r * 2)))
    m = Image.new('L', (S, S), 255); m.paste(g, (int(S * cx - S * r), int(S * cy - S * r)))
    return Image.composite(Image.new('RGB', (S, S), c_out), Image.new('RGB', (S, S), c_in), m).convert('RGBA')

def lin(c1, c2, w, h, angle=90):
    g = Image.linear_gradient('L').resize((w, h))
    if angle != 90: g = g.rotate(angle - 90, expand=False, fillcolor=128)
    return Image.composite(Image.new('RGB', (w, h), c2), Image.new('RGB', (w, h), c1), g).convert('RGBA')

def q_layer(qw, fill_top, fill_bot, outline=None, ow=0):
    """Q con relleno en degradado, contorno opcional, brillo superior."""
    qh = int(QM.height * qw / QM.width); m = QM.resize((qw, qh), Image.LANCZOS)
    pad = ow + 4; W, H = qw + pad * 2, qh + pad * 2
    out = Image.new('RGBA', (W, H))
    if outline:
        om = Image.new('L', (W, H)); om.paste(m, (pad, pad)); om = om.filter(ImageFilter.MaxFilter(ow * 2 + 1)).filter(ImageFilter.GaussianBlur(1))
        ol = Image.new('RGBA', (W, H), outline); ol.putalpha(om); out.alpha_composite(ol)
    body = lin(fill_top, fill_bot, qw, qh); body.putalpha(m); out.alpha_composite(body, (pad, pad))
    # brillo (highlight) en la parte superior izquierda
    hl = Image.new('L', (qw, qh)); ImageDraw.Draw(hl).ellipse([-qw * 0.3, -qh * 0.55, qw * 0.9, qh * 0.35], fill=70)
    hl = ImageChops.multiply(hl.filter(ImageFilter.GaussianBlur(20)), m); out.alpha_composite(Image.merge('RGBA', (*[Image.new('L', (qw, qh), 255)] * 3, hl)), (pad, pad))
    return out, pad, qh

def drop(base, layer, x, y, blur=22, off=(0, 22), op=0.45, col=(0, 0, 0)):
    P = blur * 3; a = Image.new('L', (layer.width + 2 * P, layer.height + 2 * P)); a.paste(layer.getchannel('A'), (P, P))
    sh = Image.new('RGBA', a.size, col + (0,)); sh.putalpha(a.point(lambda v: int(v * op)).filter(ImageFilter.GaussianBlur(blur)))
    base.alpha_composite(sh, (x + off[0] - P, y + off[1] - P))

def long_shadow(base, layer, x, y, length=180, col=(0, 0, 0), op=0.22):
    a = layer.getchannel('A'); acc = Image.new('L', (S, S))
    for i in range(0, length, 3):
        tmp = Image.new('L', (S, S)); tmp.paste(a, (x + i, y + i)); acc = ImageChops.lighter(acc, tmp)
    sh = Image.new('RGBA', (S, S), col + (0,)); sh.putalpha(acc.point(lambda v: int(v * op)).filter(ImageFilter.GaussianBlur(6)))
    base.alpha_composite(sh)

def bouquet(base, ax, ay, fw, rot=-8, glow=None):
    k = fw / FL.width; fl = FL.resize((fw, int(FL.height * k)), Image.LANCZOS)
    big = Image.new('RGBA', (fw * 2, fl.height * 2)); bx, by = int(fw - BASE[0] * k), int(fl.height - BASE[1] * k)
    big.alpha_composite(fl, (bx, by)); big = big.rotate(rot, resample=Image.BICUBIC, center=(fw, fl.height))
    px, py = int(ax - fw), int(ay - fl.height)
    if glow:
        g = Image.new('RGBA', big.size, glow + (0,)); g.putalpha(big.getchannel('A').point(lambda v: int(v * 0.55)).filter(ImageFilter.GaussianBlur(10)))
        base.alpha_composite(g, (px, py))
    base.alpha_composite(big, (px, py))

def word(base, text, cx, y, size, fill, track=6, shadow=None):
    f = ImageFont.truetype(F_BLACK, size); d = ImageDraw.Draw(base)
    w = sum(d.textlength(ch, font=f) for ch in text) + track * (len(text) - 1); x = cx - w / 2
    for ch in text:
        if shadow: d.text((x + 3, y + 5), ch, font=f, fill=shadow)
        d.text((x, y), ch, font=f, fill=fill); x += d.textlength(ch, font=f) + track

def ring(base, cx, cy, r, w, col, a0=200, a1=520):
    d = ImageDraw.Draw(base); d.arc([cx - r, cy - r, cx + r, cy + r], a0, a1, fill=col, width=w)

def compose(bg, qcol, outline, ringcol, wordcol, glowcol, qw=360, qcy=530, wy=868, fw=430, sop=0.22, rr_=300, ws=84):
    im = bg
    ring(im, 512, qcy - 5, rr_, 16, ringcol)
    q, pad, qh = q_layer(qw, *qcol, outline=outline, ow=10 if outline else 0)
    qx, qy = 512 - q.width // 2, qcy - q.height // 2
    long_shadow(im, q, qx, qy, col=(0, 0, 0), op=sop)
    ax, ay = qx + pad + 0.66 * qw, qy + pad + 0.07 * qh
    bouquet(im, ax, ay, fw, glow=glowcol)
    drop(im, q, qx, qy); im.alpha_composite(q, (qx, qy))
    word(im, WORD, 512, wy, ws, wordcol, shadow=(0, 0, 0, 70))
    return im

def opcion_A():
    bg = radial((20, 70, 190), NAVY3, cy=0.40, r=0.85)
    return compose(bg, ((255, 255, 255), (214, 222, 240)), None, MAG + (230,), (255, 255, 255), (255, 255, 255))

def opcion_B():
    bg = radial((236, 40, 150), (70, 10, 90), cy=0.38, r=0.9)
    return compose(bg, ((255, 255, 255), (230, 225, 240)), NAVY + (255,), GOLD + (230,), (255, 255, 255), (255, 255, 255))

def opcion_C():
    bg = radial((255, 255, 255), (232, 236, 246), cy=0.40, r=0.85); d = ImageDraw.Draw(bg)
    d.polygon([(0, 955)] + [(x, 955 + 22 * math.sin(x / S * math.pi * 1.6)) for x in range(0, S + 1, 16)] + [(S, S), (0, S)], fill=MAG)
    d.polygon([(0, 985)] + [(x, 985 + 18 * math.sin(x / S * math.pi * 1.6 + 1)) for x in range(0, S + 1, 16)] + [(S, S), (0, S)], fill=NAVY)
    return compose(bg, ((20, 60, 160), NAVY3), None, MAG + (200,), NAVY, None, qw=340, qcy=515, wy=840, sop=0.10, rr_=290)

if __name__ == '__main__':
    opts = {'A': opcion_A(), 'B': opcion_B(), 'C': opcion_C()}
    for k, im in opts.items():
        im.convert('RGB').save(f'v2_opcion_{k}_1024.png'); im.convert('RGB').resize((512, 512), Image.LANCZOS).save(f'v2_opcion_{k}_512.png')
    prev = Image.new('RGB', (3 * 420 + 40, 470), (235, 236, 240)); dp = ImageDraw.Draw(prev)
    for i, (k, im) in enumerate(opts.items()):
        big = im.resize((300, 300), Image.LANCZOS); m = Image.new('L', (300, 300), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, 299, 299], 70, fill=255)
        prev.paste(big, (40 + i * 420, 30), m)
        for j, sz in enumerate((96, 48)):
            sm = im.resize((sz, sz), Image.LANCZOS); m2 = Image.new('L', (sz, sz), 0); ImageDraw.Draw(m2).ellipse([0, 0, sz - 1, sz - 1], fill=255)
            prev.paste(sm, (40 + i * 420 + 60 + j * 130, 350 + (96 - sz) // 2), m2)
        dp.text((40 + i * 420 + 290, 390), k, fill=(0, 32, 104))
    prev.save('v2_propuestas.png')
