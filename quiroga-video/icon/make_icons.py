"""Propuestas de ícono para Quiroga Digital (1024 px -> exporta 512 Play y 432 adaptativo)."""
import math
from PIL import Image, ImageDraw, ImageFilter
S = 1024
Qw, Qn, FL = Image.open('q_white.png'), Image.open('q_navy.png'), Image.open('flores_clean.png')

def grad(c1, c2, diag=False):
    g = Image.linear_gradient('L').resize((S, S))
    if diag:
        h = Image.linear_gradient('L').resize((S, S)).rotate(90)
        g = Image.blend(g, h.transpose(Image.FLIP_LEFT_RIGHT), 0.5)
    a, b = Image.new('RGB', (S, S), c1), Image.new('RGB', (S, S), c2)
    return Image.composite(b, a, g).convert('RGBA')

def place(base, img, w, cx, cy, shadow=0.0):
    h = int(img.height * w / img.width); im = img.resize((w, h), Image.LANCZOS)
    if shadow:
        sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); sh.putalpha(im.getchannel('A').point(lambda v: int(v * shadow)))
        base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)), (cx - w // 2 + 6, cy - h // 2 + 16))
    base.alpha_composite(im, (cx - w // 2, cy - h // 2))

BASE = (490, 470)   # where the bouquet's stems meet (flower image coords)
def sprout(base, q, qw, qcx, qcy, fw, rel=(0.70, 0.06), rot=0):
    # bouquet whose stems come out of the Q: stem base anchored at a point on the Q's top-right
    qh = int(q.height * qw / q.width); ax = qcx - qw // 2 + rel[0] * qw; ay = qcy - qh // 2 + rel[1] * qh
    k = fw / FL.width; fl = FL.resize((fw, int(FL.height * k)), Image.LANCZOS)
    if rot: fl = fl.rotate(rot, resample=Image.BICUBIC, expand=False, center=(BASE[0] * k, BASE[1] * k))
    base.alpha_composite(fl, (int(ax - BASE[0] * k), int(ay - BASE[1] * k)))

def opcion_A():   # azul institucional, Q blanca con el ramillete del logo
    im = grad((0, 51, 153), (0, 22, 80)); sprout(im, Qw, 380, 470, 640, 470); place(im, Qw, 380, 470, 640, 0.35); return im

def opcion_B():   # ubicación: pin blanco con Q azul, degradado rosa→azul
    im = grad((226, 0, 124), (0, 32, 104), diag=True)
    pin = Image.new('RGBA', (S, S)); d = ImageDraw.Draw(pin); cx, cy, r = 512, 480, 235
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill='white'); d.polygon([(cx - 160, cy + 170), (cx + 160, cy + 170), (cx, cy + 385)], fill='white')
    sh = Image.new('RGBA', (S, S)); sh.putalpha(pin.getchannel('A').point(lambda v: int(v * 0.3)))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)), (8, 18)); im.alpha_composite(pin)
    sprout(im, Qn, 235, 500, 520, 300); place(im, Qn, 235, 500, 520); return im

def opcion_C():   # blanco con Q azul, ramillete y onda rosa
    im = Image.new('RGBA', (S, S), 'white'); d = ImageDraw.Draw(im)
    d.polygon([(0, 830)] + [(x, 830 + 38 * math.sin(x / S * math.pi * 1.5)) for x in range(0, S + 1, 16)] + [(S, S), (0, S)], fill=(226, 0, 124))
    sprout(im, Qn, 370, 470, 600, 460); place(im, Qn, 370, 470, 600); return im

if __name__ == '__main__':
    opts = {'A': opcion_A(), 'B': opcion_B(), 'C': opcion_C()}
    for k, im in opts.items(): im.convert('RGB').save(f'opcion_{k}_1024.png')
    prev = Image.new('RGB', (3 * 420 + 40, 470), (235, 236, 240)); dp = ImageDraw.Draw(prev)
    for i, (k, im) in enumerate(opts.items()):
        big = im.resize((300, 300), Image.LANCZOS); m = Image.new('L', (300, 300), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, 299, 299], 70, fill=255)
        prev.paste(big, (40 + i * 420, 30), m)
        for j, sz in enumerate((96, 48)):
            sm = im.resize((sz, sz), Image.LANCZOS); m2 = Image.new('L', (sz, sz), 0); ImageDraw.Draw(m2).ellipse([0, 0, sz - 1, sz - 1], fill=255)
            prev.paste(sm, (40 + i * 420 + 60 + j * 130, 350 + (96 - sz) // 2), m2)
        dp.text((40 + i * 420 + 290, 390), k, fill=(0, 32, 104))
    prev.save('propuestas.png')
