"""Etiquetas v2 · moderno minimalista con detalle. 300 dpi, hojas carta (reutiliza hoja() de v1)."""
import math, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import make_etiquetas as V1

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'out_v2'); os.makedirs(OUT, exist_ok=True)
DPI, SS = 300, 3
IB, IBK, IM, ISB = ('/usr/share/fonts/opentype/inter/' + n for n in ('InterDisplay-Bold.otf', 'InterDisplay-Black.otf', 'Inter-Medium.otf', 'Inter-SemiBold.otf'))
INK, PAPER, GRIS = (34, 30, 28), (252, 250, 246), (120, 112, 106)
TEL = V1.TEL
SAL = {   # colores más sobrios / elegantes
    'roja':     {'n': 'ROJA',     'c': (168, 32, 38),  't': (246, 226, 222), 'tag': 'Receta de la casa'},
    'verde':    {'n': 'VERDE',    'c': (52, 104, 60),  't': (226, 238, 224), 'tag': 'Receta de la casa'},
    'amarilla': {'n': 'AMARILLA', 'c': (214, 150, 0),  't': (250, 240, 212), 'tag': 'Receta de la casa'},
}
def F(p, px): return ImageFont.truetype(p, int(px))
def fit(d, s, p, px, maxw, tr=0):
    f = F(p, px)
    while d.textlength(s, font=f) + tr * (len(s) - 1) > maxw and f.size > 8: f = F(p, f.size * 0.95)
    return f
def tc(d, s, x, y, f, fill, tr=0, anchor='mm'):
    if not tr: d.text((x, y), s, font=f, fill=fill, anchor=anchor); return
    w = sum(d.textlength(ch, font=f) for ch in s) + tr * (len(s) - 1); xx = x - w / 2 if anchor[0] == 'm' else x
    for ch in s: d.text((xx, y), ch, font=f, fill=fill, anchor='l' + anchor[1]); xx += d.textlength(ch, font=f) + tr

def chile_line(d, cx, cy, s, col, w, rot=-30):
    """Chile en línea fina (estilo ícono moderno)."""
    pts = []
    for i in range(61):
        t = i / 60; x = (t - 0.5) * 2 * s; hw = s * 0.36 * math.sin(math.pi * min(1, t * 1.08)) ** 0.75 * (1 - 0.4 * t)
        pts.append((x, -hw + s * 0.18 * math.sin(t * math.pi)))
    for i in range(60, -1, -1):
        t = i / 60; x = (t - 0.5) * 2 * s; hw = s * 0.36 * math.sin(math.pi * min(1, t * 1.08)) ** 0.75 * (1 - 0.4 * t)
        pts.append((x, hw + s * 0.18 * math.sin(t * math.pi)))
    a = math.radians(rot); ca, sa = math.cos(a), math.sin(a); R = lambda x, y: (cx + x * ca - y * sa, cy + x * sa + y * ca)
    d.line([R(*p) for p in pts] + [R(*pts[0])], fill=col, width=w, joint='curve')
    x0 = -s; d.line([R(x0, 0), R(x0 - s * 0.22, -s * 0.05), R(x0 - s * 0.32, -s * 0.28)], fill=col, width=w, joint='curve')
    d.line([R(x0 - s * 0.05, -s * 0.18), R(x0 + s * 0.12, -s * 0.3), R(x0 + s * 0.3, -s * 0.2)], fill=col, width=w, joint='curve')

def tile_pattern(size, col, step, s, w):
    im = Image.new('RGBA', size); d = ImageDraw.Draw(im)
    for j, y in enumerate(range(-step, size[1] + step, step)):
        for i, x in enumerate(range(-step, size[0] + step, step)):
            chile_line(d, x + (step / 2 if j % 2 else 0), y, s, col, w, rot=-30 + 60 * ((i + j) % 2))
    return im

def logo_badge(h):
    return V1.logo_outlined(h, ring=(255, 255, 255), r=max(4, h // 30))

# ---------------------------------------------------------------- rectangular 3.5 x 2
def rect(k):
    S = SAL[k]; W, H = int(3.5 * DPI * SS), int(2 * DPI * SS); im = Image.new('RGBA', (W, H), PAPER + (255,)); d = ImageDraw.Draw(im)
    # panel izquierdo de color con patrón de chiles tono sobre tono
    pw = int(W * 0.40); panel = Image.new('RGBA', (pw, H), S['c'] + (255,))
    pat = tile_pattern((pw, H), tuple(min(255, v + 28) for v in S['c']) + (255,), int(H * 0.26), H * 0.075, int(H * 0.008)); panel.alpha_composite(pat)
    im.alpha_composite(panel)
    # logo en círculo blanco
    cr = int(min(H * 0.33, pw * 0.42)); cx, cy = pw // 2, int(H * 0.45)
    sh = Image.new('L', (W, H)); ImageDraw.Draw(sh).ellipse([cx - cr, cy - cr + 14, cx + cr, cy + cr + 14], fill=90); im.alpha_composite(Image.merge('RGBA', (*[Image.new('L', (W, H), 0)] * 3, sh.filter(ImageFilter.GaussianBlur(20)))))
    d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(255, 255, 255)); d.ellipse([cx - cr + 16, cy - cr + 16, cx + cr - 16, cy + cr - 16], outline=S['c'], width=6)
    lg = V1.LOGO.resize((int(cr * 1.62), int(cr * 1.62 * V1.LOGO.height / V1.LOGO.width)), Image.LANCZOS); im.alpha_composite(lg, (cx - lg.width // 2, cy - lg.height // 2))
    tc(d, 'TACOS DE BIRRIA', cx, H * 0.91, fit(d, 'TACOS DE BIRRIA', ISB, H * 0.055, pw * 0.8, H * 0.012), (255, 255, 255), tr=H * 0.012)
    # derecha
    x0, x1 = pw + H * 0.11, W - H * 0.09; mx = (x0 + x1) / 2
    tc(d, 'SALSA', x0, H * 0.20, F(ISB, H * 0.075), GRIS, tr=H * 0.03, anchor='lm')
    f = fit(d, S['n'], IBK, H * 0.30, x1 - x0); d.text((x0 - 4, H * 0.40), S['n'], font=f, fill=S['c'], anchor='lm')
    d.rectangle([x0, H * 0.555, x0 + H * 0.16, H * 0.565], fill=S['c'])
    tc(d, S['tag'].upper() + '  ·  HECHA EN CASA', x0, H * 0.635, fit(d, S['tag'].upper() + '  ·  HECHA EN CASA', IM, H * 0.052, x1 - x0, H * 0.006), INK, tr=H * 0.006, anchor='lm')
    tc(d, 'Consérvese en refrigeración', x0, H * 0.715, F(IM, H * 0.048), GRIS, anchor='lm')
    d.line([(x0, H * 0.80), (x1, H * 0.80)], fill=(220, 214, 206), width=4)
    tc(d, 'Pedidos  ' + TEL, x0, H * 0.885, F(IB, H * 0.06), INK, anchor='lm')
    chile_line(d, x1 - H * 0.07, H * 0.885, H * 0.055, S['c'], int(H * 0.009))
    # marco fino
    d.rounded_rectangle([10, 10, W - 11, H - 11], int(H * 0.06), outline=S['c'], width=8)
    m = Image.new('L', (W, H)); ImageDraw.Draw(m).rounded_rectangle([0, 0, W - 1, H - 1], int(H * 0.07), fill=255); im.putalpha(m)
    return im.resize((W // SS, H // SS), Image.LANCZOS)

# ---------------------------------------------------------------- redonda 2.5
def redonda(k):
    S = SAL[k]; D = int(2.5 * DPI * SS); c = D / 2; im = Image.new('RGBA', (D, D)); d = ImageDraw.Draw(im)
    d.ellipse([0, 0, D - 1, D - 1], fill=PAPER)
    # media luna inferior de color con patrón
    low = Image.new('RGBA', (D, D), S['c'] + (255,)); low.alpha_composite(tile_pattern((D, D), tuple(min(255, v + 28) for v in S['c']) + (255,), int(D * 0.15), D * 0.04, int(D * 0.005)))
    m = Image.new('L', (D, D)); dm = ImageDraw.Draw(m); dm.ellipse([0, 0, D - 1, D - 1], fill=255); dm.rectangle([0, 0, D, int(D * 0.66)], fill=0); low.putalpha(m); im.alpha_composite(low)
    d = ImageDraw.Draw(im)
    d.ellipse([D * 0.03, D * 0.03, D * 0.97, D * 0.97], outline=S['c'], width=int(D * 0.006))
    lg = V1.LOGO.resize((int(D * 0.46), int(D * 0.46 * V1.LOGO.height / V1.LOGO.width)), Image.LANCZOS); im.alpha_composite(lg, (int(c - lg.width / 2), int(D * 0.08)))
    tc(d, 'SALSA', c, D * 0.47, F(ISB, D * 0.045), GRIS, tr=D * 0.018)
    f = fit(d, S['n'], IBK, D * 0.15, D * 0.72); d.text((c, D * 0.565), S['n'], font=f, fill=S['c'], anchor='mm')
    tc(d, 'HECHA EN CASA', c, D * 0.735, F(ISB, D * 0.036), (255, 255, 255), tr=D * 0.008)
    tc(d, TEL, c, D * 0.81, F(IB, D * 0.05), (255, 255, 255))
    tc(d, 'TACOS DE BIRRIA', c, D * 0.875, F(ISB, D * 0.03), (255, 255, 255), tr=D * 0.008)
    m = Image.new('L', (D, D)); ImageDraw.Draw(m).ellipse([0, 0, D - 1, D - 1], fill=255); im.putalpha(m)
    return im.resize((D // SS, D // SS), Image.LANCZOS)

if __name__ == '__main__':
    R = {k: redonda(k) for k in SAL}; Q = {k: rect(k) for k in SAL}
    for k in SAL: R[k].save(f'{OUT}/etiqueta_redonda_{k}.png', dpi=(DPI, DPI)); Q[k].save(f'{OUT}/etiqueta_rectangular_{k}.png', dpi=(DPI, DPI))
    pages = [V1.hoja([R[k]], (2.5, 2.5), 3, 4, 'circle', f'Etiquetas redondas 2.5" · Salsa {SAL[k]["n"].lower()}') for k in SAL]
    pages.append(V1.hoja([R[k] for k in SAL], (2.5, 2.5), 3, 4, 'circle', 'Etiquetas redondas 2.5" · Surtidas'))
    pages += [V1.hoja([Q[k]], (3.5, 2), 2, 5, 'rect', f'Etiquetas rectangulares 3.5" x 2" · Salsa {SAL[k]["n"].lower()}') for k in SAL]
    pages.append(V1.hoja([Q[k] for k in SAL], (3.5, 2), 2, 5, 'rect', 'Etiquetas rectangulares 3.5" x 2" · Surtidas'))
    pages[0].save(f'{OUT}/etiquetas_salsas_hojas_carta.pdf', save_all=True, append_images=pages[1:], resolution=DPI)
    print('ok')
