"""Etiquetas de salsas El Chiquilín (300 dpi, listas para hojas de stickers tamaño carta).
Formatos: redonda 2.5" (tapa de vasito) y rectangular 3.5"x2" (botella/frasco)."""
import math, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out'); os.makedirs(OUT, exist_ok=True)
DPI = 300; SS = 3                      # se dibuja a 3x y se reduce (bordes suaves)
F = os.path.join(HERE, '..', 'src', 'fonts')
FRED, FREDS, NUN = (os.path.join(F, n) for n in ('Fredoka-Bold.ttf', 'Fredoka-SemiBold.ttf', 'Nunito-Black.ttf'))
LOGO = Image.open(os.path.join(HERE, '..', 'src', 'brand', 'logo.png')).convert('RGBA')
CAFE, CREMA, AMA, ROJO = (26, 8, 0), (255, 249, 238), (245, 200, 0), (192, 19, 27)
TEL = '443 198 2156'
SALSAS = {
    'roja':     {'nombre': 'ROJA',     'col': (192, 19, 27),  'osc': (130, 10, 16), 'chile': (200, 25, 30),  'txt': CREMA},
    'verde':    {'nombre': 'VERDE',    'col': (26, 122, 58),  'osc': (14, 80, 36),  'chile': (40, 150, 60),  'txt': CREMA},
    'amarilla': {'nombre': 'AMARILLA', 'col': (245, 190, 0),  'osc': (200, 140, 0), 'chile': (250, 170, 0), 'txt': CAFE},
}

def font(path, px): return ImageFont.truetype(path, int(px))

def logo_outlined(h, ring=CREMA, r=None):
    """Logo con contorno tipo sticker (para que resalte sobre color)."""
    w = int(LOGO.width * h / LOGO.height); lg = LOGO.resize((w, h), Image.LANCZOS)
    r = r or max(4, h // 28); pad = r + 4
    out = Image.new('RGBA', (w + 2 * pad, h + 2 * pad))
    m = Image.new('L', out.size); m.paste(lg.getchannel('A'), (pad, pad)); m = m.filter(ImageFilter.MaxFilter(2 * r + 1)).filter(ImageFilter.GaussianBlur(1.5))
    o = Image.new('RGBA', out.size, ring + (255,)); o.putalpha(m); out.alpha_composite(o); out.alpha_composite(lg, (pad, pad))
    return out

def chile(d, cx, cy, s, col, rot=-25):
    """Chile dibujado (cuerpo curvo + rabito verde)."""
    pts = []
    for i in range(41):
        t = i / 40; x = (t - 0.5) * 2 * s; w = s * 0.62 * math.sin(math.pi * min(1, t * 1.1)) ** 0.7 * (1 - 0.45 * t)
        pts.append((x, -w + s * 0.25 * math.sin(t * math.pi) * 0.6))
    for i in range(40, -1, -1):
        t = i / 40; x = (t - 0.5) * 2 * s; w = s * 0.62 * math.sin(math.pi * min(1, t * 1.1)) ** 0.7 * (1 - 0.45 * t)
        pts.append((x, w * 0.9 + s * 0.25 * math.sin(t * math.pi) * 0.6))
    a = math.radians(rot); ca, sa = math.cos(a), math.sin(a)
    P = [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in pts]
    d.polygon(P, fill=col, outline=CAFE, width=max(2, int(s * 0.07)))
    sx, sy = cx - s * ca, cy - s * sa
    d.line([(sx, sy), (sx - s * 0.35 * ca + s * 0.12 * sa, sy - s * 0.35 * sa - s * 0.12 * ca)], fill=(46, 140, 60), width=max(4, int(s * 0.16)))
    d.ellipse([sx - s * 0.16, sy - s * 0.16, sx + s * 0.16, sy + s * 0.16], fill=(46, 140, 60), outline=CAFE, width=max(2, int(s * 0.05)))
    hl = [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in [(-s * 0.4, -s * 0.12), (s * 0.3, -s * 0.18)]]
    d.line(hl, fill=(255, 255, 255, 140), width=max(2, int(s * 0.08)))

def fit(d, txt, path, px, maxw, track=0):
    f = font(path, px)
    while d.textlength(txt, font=f) + track * (len(txt) - 1) > maxw and f.size > 8: f = font(path, f.size * 0.95)
    return f

def text_center(d, txt, cx, cy, f, fill, stroke=0, sfill=None, track=0):
    if not track:
        d.text((cx, cy), txt, font=f, fill=fill, anchor='mm', stroke_width=stroke, stroke_fill=sfill); return
    w = sum(d.textlength(ch, font=f) for ch in txt) + track * (len(txt) - 1); x = cx - w / 2
    for ch in txt:
        d.text((x, cy), ch, font=f, fill=fill, anchor='lm', stroke_width=stroke, stroke_fill=sfill); x += d.textlength(ch, font=f) + track

def arc_text(img, txt, cx, cy, r, f, fill, center_deg=90, spread=None):
    d0 = ImageDraw.Draw(img); widths = [d0.textlength(ch, font=f) for ch in txt]; total = sum(widths)
    spread = spread or math.degrees(total / r); bottom = 0 < center_deg < 180
    ang = center_deg + spread / 2 if bottom else center_deg - spread / 2
    for ch, w in zip(txt, widths):
        da = math.degrees(w / r); a = ang - da / 2 if bottom else ang + da / 2
        sz = int(f.size * 2.2); g = Image.new('RGBA', (sz, sz)); ImageDraw.Draw(g).text((sz / 2, sz / 2), ch, font=f, fill=fill, anchor='mm')
        g = g.rotate((90 - a) if bottom else (-90 - a), resample=Image.BICUBIC)
        x, y = cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))
        img.alpha_composite(g, (int(x - sz / 2), int(y - sz / 2)))
        ang = ang - da if bottom else ang + da

# ------------------------------------------------------------------ redonda 2.5"
def redonda(key):
    S = SALSAS[key]; D = int(2.5 * DPI * SS); c = D / 2; im = Image.new('RGBA', (D, D)); d = ImageDraw.Draw(im)
    d.ellipse([0, 0, D - 1, D - 1], fill=S['col'])
    d.ellipse([D * 0.035, D * 0.035, D * 0.965, D * 0.965], outline=CREMA, width=int(D * 0.008))
    r_in = D * 0.36; d.ellipse([c - r_in, c - r_in, c + r_in, c + r_in], fill=CREMA, outline=CAFE, width=int(D * 0.012))
    # texto curvo en el aro
    f_top = font(FRED, D * 0.072); f_bot = font(FREDS, D * 0.05)
    arc_text(im, 'SALSA ' + S['nombre'], c, c, D * 0.425, f_top, S['txt'], center_deg=270)
    arc_text(im, 'TACOS DE BIRRIA  •  ' + TEL, c, c, D * 0.43, f_bot, S['txt'], center_deg=90)
    # logo al centro
    lg = logo_outlined(int(D * 0.37)); im.alpha_composite(lg, (int(c - lg.width / 2), int(c - lg.height / 2 - D * 0.04)))
    # chiles a los lados + "hecha en casa"
    d = ImageDraw.Draw(im)
    chile(d, c - D * 0.215, c + D * 0.2, D * 0.045, S['chile'], rot=-35)
    chile(d, c + D * 0.215, c + D * 0.2, D * 0.045, S['chile'], rot=215)
    text_center(d, 'HECHA EN CASA', c, c + D * 0.24, fit(d, 'HECHA EN CASA', NUN, D * 0.04, D * 0.30), CAFE)
    for a in (180, 0):   # puntitos separadores en el aro
        x, y = c + D * 0.43 * math.cos(math.radians(a)), c + D * 0.43 * math.sin(math.radians(a))
        d.ellipse([x - D * 0.012, y - D * 0.012, x + D * 0.012, y + D * 0.012], fill=AMA if key != 'amarilla' else ROJO)
    return im.resize((D // SS, D // SS), Image.LANCZOS)

# ------------------------------------------------------------------ rectangular 3.5" x 2"
def rectangular(key):
    S = SALSAS[key]; W, H = int(3.5 * DPI * SS), int(2 * DPI * SS); im = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(im)
    R = int(H * 0.08)
    d.rounded_rectangle([0, 0, W - 1, H - 1], R, fill=S['col'])
    # panel crema con el logo (izquierda)
    px = int(W * 0.42); d.rounded_rectangle([int(H * 0.06), int(H * 0.06), px, H - int(H * 0.06)], int(R * 0.7), fill=CREMA, outline=CAFE, width=int(H * 0.012))
    lg = logo_outlined(int(H * 0.56)); lw = min(lg.width, px - int(H * 0.16))
    lg = lg.resize((lw, int(lg.height * lw / lg.width)), Image.LANCZOS)
    im.alpha_composite(lg, (int((H * 0.06 + px) / 2 - lg.width / 2), int(H * 0.40 - lg.height / 2)))
    text_center(d, 'TACOS DE BIRRIA', (H * 0.06 + px) / 2, H * 0.80, fit(d, 'TACOS DE BIRRIA', NUN, H * 0.07, (px - H * 0.06) * 0.86, H * 0.006), CAFE, track=H * 0.006)
    # derecha: nombre de la salsa
    rx = (px + W) / 2
    text_center(d, 'SALSA', rx, H * 0.24, font(FREDS, H * 0.13), S['txt'], track=H * 0.02)
    f = font(FRED, H * 0.25); name = S['nombre']
    while d.textlength(name, font=f) > (W - px) * 0.86: f = font(FRED, f.size * 0.94)
    text_center(d, name, rx, H * 0.46, f, S['txt'], stroke=int(H * 0.012), sfill=S['osc'])
    for i, dx in enumerate((-0.12, 0, 0.12)):
        chile(d, rx + dx * W * 0.9, H * 0.665, H * 0.065, S['chile'] if key != 'amarilla' else (250, 140, 0), rot=-25 + i * 10)
    d.line([(px + H * 0.12, H * 0.775), (W - H * 0.12, H * 0.775)], fill=S['txt'], width=int(H * 0.006))
    t1 = 'Hecha en casa · Consérvese en refrigeración'; text_center(d, t1, rx, H * 0.845, fit(d, t1, FREDS, H * 0.052, (W - px) * 0.88), S['txt'])
    text_center(d, 'Pedidos: ' + TEL, rx, H * 0.925, font(FRED, H * 0.062), S['txt'])
    return im.resize((W // SS, H // SS), Image.LANCZOS)

# ------------------------------------------------------------------ hojas carta para imprimir
def hoja(labels, size_in, cols, rows, shape, title):
    PW, PH = int(8.5 * DPI), int(11 * DPI); sheet = Image.new('RGB', (PW, PH), 'white'); d = ImageDraw.Draw(sheet)
    lw, lh = int(size_in[0] * DPI), int(size_in[1] * DPI)
    gx = (PW - cols * lw) / (cols + 1); gy = (PH - rows * lh) / (rows + 1); i = 0
    for r in range(rows):
        for c_ in range(cols):
            x, y = int(gx + c_ * (lw + gx)), int(gy + r * (lh + gy)); lab = labels[i % len(labels)]; i += 1
            sheet.paste(lab, (x, y), lab)
            # guía de corte punteada, 1.5 mm afuera
            o = int(DPI * 1.5 / 25.4)
            if shape == 'circle':
                for k in range(0, 360, 6): d.arc([x - o, y - o, x + lw + o, y + lh + o], k, k + 3, fill=(170, 170, 170), width=3)
            else:
                box = [x - o, y - o, x + lw + o, y + lh + o]
                for X in range(box[0], box[2], 24): d.line([(X, box[1]), (min(X + 12, box[2]), box[1])], fill=(170, 170, 170), width=3); d.line([(X, box[3]), (min(X + 12, box[2]), box[3])], fill=(170, 170, 170), width=3)
                for Y in range(box[1], box[3], 24): d.line([(box[0], Y), (box[0], min(Y + 12, box[3]))], fill=(170, 170, 170), width=3); d.line([(box[2], Y), (box[2], min(Y + 12, box[3]))], fill=(170, 170, 170), width=3)
    d.text((PW / 2, PH - 40), title + '  ·  Imprimir al 100% (tamaño real, sin "ajustar a la página")', font=font(FREDS, 34), fill=(150, 150, 150), anchor='mm')
    return sheet

if __name__ == '__main__':
    R = {k: redonda(k) for k in SALSAS}; Q = {k: rectangular(k) for k in SALSAS}
    for k in SALSAS:
        R[k].save(f'{OUT}/etiqueta_redonda_{k}.png', dpi=(DPI, DPI)); Q[k].save(f'{OUT}/etiqueta_rectangular_{k}.png', dpi=(DPI, DPI))
    pages = []
    for k in SALSAS:
        pages.append(hoja([R[k]], (2.5, 2.5), 3, 4, 'circle', f'Etiquetas redondas 2.5" · Salsa {SALSAS[k]["nombre"].lower()}'))
    pages.append(hoja([R[k] for k in SALSAS], (2.5, 2.5), 3, 4, 'circle', 'Etiquetas redondas 2.5" · Surtidas'))
    for k in SALSAS:
        pages.append(hoja([Q[k]], (3.5, 2), 2, 5, 'rect', f'Etiquetas rectangulares 3.5" x 2" · Salsa {SALSAS[k]["nombre"].lower()}'))
    pages.append(hoja([Q[k] for k in SALSAS], (3.5, 2), 2, 5, 'rect', 'Etiquetas rectangulares 3.5" x 2" · Surtidas'))
    pages[0].save(f'{OUT}/etiquetas_salsas_hojas_carta.pdf', save_all=True, append_images=pages[1:], resolution=DPI)
    for i, p in enumerate(pages): p.save(f'{OUT}/hoja_{i + 1:02d}.png', dpi=(DPI, DPI))
    print('ok', len(pages), 'hojas')
