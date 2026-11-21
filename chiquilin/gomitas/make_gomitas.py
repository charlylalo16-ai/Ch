"""Gomitas El Chiquilín: etiquetas (redonda 2.5" y rectangular 3.5x2", 300 dpi, hojas carta) + publicación/historia.
Dos sabores: ENCHILADAS (chamoy y chile) y ACUÁTICAS. Gomitas dibujadas con código."""
import math, os, sys, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'etiquetas'))
import make_etiquetas as V1
OUT = os.path.join(HERE, 'out'); os.makedirs(OUT, exist_ok=True)
DPI, SS = 300, 3
FD = os.path.join(HERE, '..', 'src', 'fonts'); FRED, FREDS, NUN = (os.path.join(FD, n) for n in ('Fredoka-Bold.ttf', 'Fredoka-SemiBold.ttf', 'Nunito-Black.ttf'))
LOGO = V1.LOGO; INK = (40, 16, 8); WHITE = (255, 255, 255)
F = lambda p, px: ImageFont.truetype(p, max(8, int(px)))
TEL = V1.TEL
SAB = {
    'enchiladas': {'nombre': 'ENCHILADAS', 'tag': 'CON CHAMOY Y CHILE', 'bg1': (255, 92, 40), 'bg2': (214, 20, 60), 'acc': (255, 214, 0), 'txt': WHITE,
                   'gum': [(255, 70, 70), (255, 150, 30), (255, 200, 40), (210, 30, 80), (250, 100, 160)], 'kind': 'ench'},
    'acuaticas':  {'nombre': 'ACUÁTICAS', 'tag': '¡SÚPER DIVERTIDAS!', 'bg1': (40, 200, 255), 'bg2': (20, 90, 220), 'acc': (255, 230, 60), 'txt': WHITE,
                   'gum': [(60, 230, 200), (80, 160, 255), (160, 110, 255), (40, 220, 120), (255, 120, 200)], 'kind': 'agua'},
}

# ------------------------------------------------------------------ gomitas
def shade(c, k): return tuple(max(0, min(255, int(v * k))) for v in c)
def glossy(layer, mask_draw_fn, col, box):
    """Rellena con color translúcido + borde + brillo."""
    w, h = layer.size; m = Image.new('L', (w, h)); mask_draw_fn(ImageDraw.Draw(m))
    body = Image.new('RGBA', (w, h), col + (235,)); body.putalpha(m.point(lambda v: v * 235 // 255))
    inner = Image.new('RGBA', (w, h), shade(col, 1.25) + (0,)); inner.putalpha(m.filter(ImageFilter.MinFilter(int(box * 0.18) | 1)).filter(ImageFilter.GaussianBlur(box * 0.08)).point(lambda v: v * 150 // 255))
    edge = m.filter(ImageFilter.MaxFilter(5)); ed = Image.new('RGBA', (w, h), shade(col, 0.6) + (0,)); ed.putalpha(Image.eval(Image.merge('L', [edge]), lambda v: v).point(lambda v: v) if False else ImageChopsSub(edge, m))
    layer.alpha_composite(ed); layer.alpha_composite(body); layer.alpha_composite(inner)
    hl = Image.new('L', (w, h)); dh = ImageDraw.Draw(hl); dh.ellipse([w * 0.18, h * 0.12, w * 0.45, h * 0.32], fill=200)
    hl = Image.composite(hl, Image.new('L', (w, h)), m).filter(ImageFilter.GaussianBlur(box * 0.03))
    layer.alpha_composite(Image.merge('RGBA', (Image.new('L', (w, h), 255),) * 3 + (hl.point(lambda v: v * 170 // 255),)))
def ImageChopsSub(a, b):
    from PIL import ImageChops
    return ImageChops.subtract(a, b)

def bear(s, col):
    w, h = int(s), int(s * 1.25); L = Image.new('RGBA', (w, h))
    def m(d):
        d.ellipse([w * .22, h * .02, w * .42, h * .2], fill=255); d.ellipse([w * .58, h * .02, w * .78, h * .2], fill=255)
        d.ellipse([w * .2, h * .06, w * .8, h * .5], fill=255); d.ellipse([w * .16, h * .38, w * .84, h * .96], fill=255)
        d.ellipse([w * .02, h * .45, w * .32, h * .66], fill=255); d.ellipse([w * .68, h * .45, w * .98, h * .66], fill=255)
        d.ellipse([w * .14, h * .78, w * .44, h * .99], fill=255); d.ellipse([w * .56, h * .78, w * .86, h * .99], fill=255)
    glossy(L, m, col, s); d = ImageDraw.Draw(L)
    for ex in (.38, .62): d.ellipse([w * ex - w * .035, h * .24, w * ex + w * .035, h * .3], fill=shade(col, .45))
    d.arc([w * .4, h * .28, w * .6, h * .4], 20, 160, fill=shade(col, .45), width=max(2, int(s * .03)))
    return L
def worm(s, c1, c2):
    w, h = int(s * 1.6), int(s * 0.7); L = Image.new('RGBA', (w, h)); th = s * 0.26
    pts = [(w * .08 + i * (w * .84) / 30, h * .5 + math.sin(i / 30 * math.pi * 2) * h * .22) for i in range(31)]
    for k, col in ((0, c1), (1, c2)):
        def m(d, k=k):
            seg = pts[:16] if k == 0 else pts[15:]
            d.line(seg, fill=255, width=int(th), joint='curve'); [d.ellipse([p[0] - th / 2, p[1] - th / 2, p[0] + th / 2, p[1] + th / 2], fill=255) for p in (seg[0], seg[-1])]
        glossy(L, m, col, s * 0.5)
    return L
def fish(s, col, shark=False):
    w, h = int(s * 1.5), int(s * 0.9); L = Image.new('RGBA', (w, h))
    def m(d):
        d.ellipse([w * .12, h * .2, w * .8, h * .8], fill=255); d.polygon([(w * .74, h * .5), (w * .98, h * .18), (w * .98, h * .82)], fill=255)
        if shark: d.polygon([(w * .38, h * .26), (w * .5, h * .0), (w * .58, h * .26)], fill=255)
        else: d.polygon([(w * .4, h * .22), (w * .5, h * .06), (w * .6, h * .22)], fill=255)
    glossy(L, m, col, s * 0.6); d = ImageDraw.Draw(L)
    d.ellipse([w * .24, h * .4, w * .31, h * .5], fill=(30, 20, 40)); d.ellipse([w * .255, h * .41, w * .275, h * .44], fill=WHITE)
    if shark:
        for i in range(4): d.polygon([(w * (.18 + i * .045), h * .6), (w * (.2 + i * .045), h * .68), (w * (.22 + i * .045), h * .6)], fill=WHITE)
    return L
def chile_powder(L, n, rnd):
    d = ImageDraw.Draw(L); w, h = L.size; a = L.getchannel('A')
    for _ in range(n):
        x, y = rnd.random() * w, rnd.random() * h
        if a.getpixel((int(x), int(y))) > 100: r = rnd.choice((1.5, 2, 2.5)) * w / 220; d.ellipse([x - r, y - r, x + r, y + r], fill=rnd.choice([(150, 20, 10), (190, 40, 20), (120, 10, 10)]))
    return L
def gummy(kind, i, s, col, rnd):
    if kind == 'ench':
        g = [lambda: bear(s, col), lambda: worm(s, col, SAB['enchiladas']['gum'][(i + 2) % 5])][i % 2]()
        return chile_powder(g, int(s * 0.7), rnd)
    return [lambda: fish(s, col), lambda: fish(s, col, True), lambda: worm(s, col, SAB['acuaticas']['gum'][(i + 2) % 5]), lambda: bear(s, col)][i % 4]()

def scatter(canvas, kind, cols, n, box, smin, smax, seed, avoid=None):
    rnd = random.Random(seed); x0, y0, x1, y1 = box; placed = []
    for i in range(n):
        for _ in range(60):
            s = rnd.uniform(smin, smax); x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
            if avoid and any(ax0 < x < ax1 and ay0 < y < ay1 for ax0, ay0, ax1, ay1 in avoid): continue
            if all(math.hypot(x - px, y - py) > (s + ps) * 0.55 for px, py, ps in placed): break
        placed.append((x, y, s)); g = gummy(kind, i, s, cols[i % len(cols)], rnd).rotate(rnd.uniform(-40, 40), expand=True, resample=Image.BICUBIC)
        sh = Image.new('RGBA', g.size, (0, 0, 0, 0)); sh.putalpha(g.getchannel('A').point(lambda v: v * 70 // 255)); sh = sh.filter(ImageFilter.GaussianBlur(s * 0.05))
        canvas.alpha_composite(sh, (int(x - g.width / 2 + s * .04), int(y - g.height / 2 + s * .07))); canvas.alpha_composite(g, (int(x - g.width / 2), int(y - g.height / 2)))

# ------------------------------------------------------------------ fondos y texto
def gradient(w, h, c1, c2):
    g = Image.linear_gradient('L').resize((w, h)); return Image.composite(Image.new('RGBA', (w, h), c2 + (255,)), Image.new('RGBA', (w, h), c1 + (255,)), g)
def confetti(im, n, seed, cols):
    rnd = random.Random(seed); d = ImageDraw.Draw(im); w, h = im.size
    for _ in range(n):
        x, y, r = rnd.random() * w, rnd.random() * h, rnd.uniform(.004, .012) * w; col = rnd.choice(cols) + (140,)
        if rnd.random() < .5: d.ellipse([x - r, y - r, x + r, y + r], fill=col)
        else: d.polygon([(x, y - r * 1.6), (x + r * .5, y - r * .5), (x + r * 1.6, y), (x + r * .5, y + r * .5), (x, y + r * 1.6), (x - r * .5, y + r * .5), (x - r * 1.6, y), (x - r * .5, y - r * .5)], fill=col)
def bubbles(im, n, seed):
    rnd = random.Random(seed); d = ImageDraw.Draw(im); w, h = im.size
    for _ in range(n):
        x, y, r = rnd.random() * w, rnd.random() * h, rnd.uniform(.006, .025) * w
        d.ellipse([x - r, y - r, x + r, y + r], outline=(255, 255, 255, 120), width=max(2, int(r * .18))); d.ellipse([x - r * .45, y - r * .55, x - r * .1, y - r * .25], fill=(255, 255, 255, 150))
def fun_text(im, txt, cx, cy, size, fill, outline=INK, depth=None, maxw=None):
    d = ImageDraw.Draw(im); f = F(FRED, size)
    while maxw and d.textlength(txt, font=f) > maxw: f = F(FRED, f.size * 0.95)
    depth = depth if depth is not None else int(f.size * 0.08); sw = max(3, int(f.size * 0.09))
    for k in range(depth, 0, -1): d.text((cx + k * .5, cy + k), txt, font=f, fill=outline, anchor='mm', stroke_width=sw, stroke_fill=outline)
    d.text((cx, cy), txt, font=f, fill=fill, anchor='mm', stroke_width=sw, stroke_fill=outline)
def pill(im, txt, cx, cy, size, bg, fg):
    d = ImageDraw.Draw(im); f = F(NUN, size); tw = d.textlength(txt, font=f); w, h = tw + size * 1.4, size * 1.7
    d.rounded_rectangle([cx - w / 2 + size * .12, cy - h / 2 + size * .18, cx + w / 2 + size * .12, cy + h / 2 + size * .18], h / 2, fill=INK)
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], h / 2, fill=bg, outline=INK, width=max(3, int(size * .1)))
    d.text((cx, cy + size * .04), txt, font=f, fill=fg, anchor='mm')
def logo(im, cx, cy, h):
    lg = V1.logo_outlined(int(h), ring=WHITE, r=max(5, int(h / 26))); im.alpha_composite(lg, (int(cx - lg.width / 2), int(cy - lg.height / 2)))

# ------------------------------------------------------------------ etiquetas
def redonda(k):
    S = SAB[k]; D = int(2.5 * DPI * SS); c = D / 2
    im = gradient(D, D, S['bg1'], S['bg2'])
    (bubbles if S['kind'] == 'agua' else lambda a, b, s: confetti(a, b, s, [S['acc'], WHITE]))(im, 26, 3)
    scatter(im, S['kind'], S['gum'], 9, (D * .05, D * .05, D * .95, D * .95), D * .1, D * .15, 7, avoid=[(D * .2, D * .1, D * .8, D * .9)])
    logo(im, c, D * .33, D * .36)
    fun_text(im, 'GOMITAS', c, D * .6, D * .1, S['acc'])
    fun_text(im, S['nombre'], c, D * .72, D * .135, WHITE, maxw=D * .74)
    pill(im, S['tag'], c, D * .85, D * .038, S['acc'], INK)
    d = ImageDraw.Draw(im); d.ellipse([D * .02, D * .02, D * .98, D * .98], outline=WHITE, width=int(D * .012))
    m = Image.new('L', (D, D)); ImageDraw.Draw(m).ellipse([0, 0, D - 1, D - 1], fill=255); im.putalpha(m)
    return im.resize((D // SS, D // SS), Image.LANCZOS)
def rect(k):
    S = SAB[k]; W, H = int(3.5 * DPI * SS), int(2 * DPI * SS)
    im = gradient(W, H, S['bg1'], S['bg2'])
    (bubbles if S['kind'] == 'agua' else lambda a, b, s: confetti(a, b, s, [S['acc'], WHITE]))(im, 30, 5)
    scatter(im, S['kind'], S['gum'], 6, (W * .8, H * .12, W * .95, H * .88), H * .17, H * .22, 11)
    logo(im, W * .165, H * .5, H * .37)
    fun_text(im, 'GOMITAS', W * .555, H * .24, H * .13, S['acc'])
    fun_text(im, S['nombre'], W * .555, H * .45, H * .19, WHITE, maxw=W * .36)
    pill(im, S['tag'], W * .555, H * .67, H * .055, S['acc'], INK)
    ImageDraw.Draw(im).text((W * .555, H * .85), 'El Chiquilín · ' + TEL, font=F(FREDS, H * .06), fill=WHITE, anchor='mm', stroke_width=int(H * .008), stroke_fill=INK)
    d = ImageDraw.Draw(im); d.rounded_rectangle([12, 12, W - 13, H - 13], int(H * .07), outline=WHITE, width=int(H * .016))
    m = Image.new('L', (W, H)); ImageDraw.Draw(m).rounded_rectangle([0, 0, W - 1, H - 1], int(H * .08), fill=255); im.putalpha(m)
    return im.resize((W // SS, H // SS), Image.LANCZOS)

# ------------------------------------------------------------------ redes
def social(w, h, story):
    im = gradient(w, h, (255, 90, 160), (110, 40, 220)); confetti(im, 70, 21, [(255, 230, 60), WHITE, (60, 230, 200)])
    # mitad izq enchiladas, der acuáticas (fondos en burbuja)
    d = ImageDraw.Draw(im); cy = h * (.56 if story else .58)
    if story: scatter(im, 'ench', SAB['enchiladas']['gum'][:3], 4, (w * .05, h * .69, w * .45, h * .8), w * .07, w * .1, 51); scatter(im, 'agua', SAB['acuaticas']['gum'][:3], 4, (w * .55, h * .69, w * .95, h * .8), w * .07, w * .1, 52)
    for side, k in ((0, 'enchiladas'), (1, 'acuaticas')):
        S = SAB[k]; cx = w * (.27 if side == 0 else .73); r = w * .25
        blob = gradient(int(r * 2), int(r * 2), S['bg1'], S['bg2']); m = Image.new('L', blob.size); ImageDraw.Draw(m).ellipse([0, 0, r * 2 - 1, r * 2 - 1], fill=255); blob.putalpha(m)
        sh = Image.new('RGBA', blob.size, INK + (0,)); sh.putalpha(m.point(lambda v: v * 120 // 255)); im.alpha_composite(sh, (int(cx - r + 10), int(cy - r + 16)))
        im.alpha_composite(blob, (int(cx - r), int(cy - r))); ImageDraw.Draw(im).ellipse([cx - r, cy - r, cx + r, cy + r], outline=WHITE, width=10)
        scatter(im, S['kind'], S['gum'], 7, (cx - r * .78, cy - r * .7, cx + r * .78, cy + r * .45), r * .26, r * .36, 31 + side)
        pill(im, S['nombre'], cx, cy + r * .78, w * .04, S['acc'], INK)
    logo(im, w / 2, h * (.13 if story else .12), h * (.17 if story else .17))
    fun_text(im, '¡NUEVAS!', w / 2, h * (.27 if story else .27), w * .1, (255, 230, 60))
    fun_text(im, 'GOMITAS', w / 2, h * (.36 if story else .37), w * .14, WHITE)
    fun_text(im, 'Enchiladas y acuáticas', w / 2, h * (.86 if story else .87), w * .055, WHITE, depth=4)
    fun_text(im, 'Pídelas al ' + TEL, w / 2, h * (.92 if story else .945), w * .045, (255, 230, 60), depth=3)
    return im.convert('RGB')

if __name__ == '__main__':
    R = {k: redonda(k) for k in SAB}; Q = {k: rect(k) for k in SAB}
    for k in SAB: R[k].save(f'{OUT}/etiqueta_redonda_{k}.png', dpi=(DPI, DPI)); Q[k].save(f'{OUT}/etiqueta_rectangular_{k}.png', dpi=(DPI, DPI))
    pages = [V1.hoja([R[k]], (2.5, 2.5), 3, 4, 'circle', f'Gomitas {SAB[k]["nombre"].lower()} · etiquetas redondas 2.5"') for k in SAB]
    pages.append(V1.hoja([R[k] for k in SAB], (2.5, 2.5), 3, 4, 'circle', 'Gomitas · etiquetas redondas 2.5" · surtidas'))
    pages += [V1.hoja([Q[k]], (3.5, 2), 2, 5, 'rect', f'Gomitas {SAB[k]["nombre"].lower()} · etiquetas 3.5" x 2"') for k in SAB]
    pages.append(V1.hoja([Q[k] for k in SAB], (3.5, 2), 2, 5, 'rect', 'Gomitas · etiquetas 3.5" x 2" · surtidas'))
    pages[0].save(f'{OUT}/gomitas_etiquetas_hojas_carta.pdf', save_all=True, append_images=pages[1:], resolution=DPI)
    social(1080, 1350, False).save(f'{OUT}/gomitas_publicacion_1080x1350.png'); social(1080, 1920, True).save(f'{OUT}/gomitas_historia_1080x1920.png')
    print('ok')
