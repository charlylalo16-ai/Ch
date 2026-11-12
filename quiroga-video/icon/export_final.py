"""Exporta el ícono elegido (v4 opción H: blanco con azul) en todos los tamaños: Play, Android (legado, redondo, adaptativo) e iOS."""
import os, shutil
from PIL import Image, ImageDraw
import make_icons_v4 as V4, make_icons_v2 as V2
OUT = 'final'; shutil.rmtree(OUT, ignore_errors=True)
S = 1024
full = V4.H().convert('RGB')                       # ícono completo
# capas separadas para el ícono adaptativo de Android
bgl = V2.radial((255, 255, 255), (228, 233, 245), cy=0.42, r=0.85)
fgl = V4.build(Image.new('RGBA', (S, S), (0, 0, 0, 0)), ((25, 65, 165), V4.NAVY3), None, V4.NAVY, V4.MAG, V4.MAG, V4.NAVY, V4.W, V4.NAVY3, None)
def save(im, path, size):
    os.makedirs(os.path.dirname(path), exist_ok=True); im.resize((size, size), Image.LANCZOS).save(path, optimize=True)
# foreground: contenido recortado y ajustado a la zona segura (círculo de 66dp dentro de 108dp)
bb = fgl.getbbox(); cont = fgl.crop(bb); fit = int(S * 60 / 108); sc = fit / max(cont.size)
cont = cont.resize((int(cont.width * sc), int(cont.height * sc)), Image.LANCZOS)
FG = Image.new('RGBA', (S, S)); FG.alpha_composite(cont, ((S - cont.width) // 2, (S - cont.height) // 2))
save(full, f'{OUT}/google-play/icono-512x512.png', 512)
save(full, f'{OUT}/ios/AppIcon-1024.png', 1024)                     # sin transparencia (requisito de Apple)
dens = {'mdpi': 1, 'hdpi': 1.5, 'xhdpi': 2, 'xxhdpi': 3, 'xxxhdpi': 4}
for d, k in dens.items():
    base = f'{OUT}/android/res/mipmap-{d}'
    save(full, f'{base}/ic_launcher.png', int(48 * k))
    r = full.resize((int(48 * k),) * 2, Image.LANCZOS).convert('RGBA'); m = Image.new('L', r.size, 0); ImageDraw.Draw(m).ellipse([0, 0, r.width - 1, r.height - 1], fill=255); r.putalpha(m)
    r.save(f'{base}/ic_launcher_round.png', optimize=True)
    # adaptativo 108dp: el diseño va dentro de la zona segura (72dp de 108dp)
    n = int(108 * k); fg = FG.resize((n, n), Image.LANCZOS)
    fg.save(f'{base}/ic_launcher_foreground.png', optimize=True)
    bgl.convert('RGB').resize((n, n), Image.LANCZOS).save(f'{base}/ic_launcher_background.png', optimize=True)
os.makedirs(f'{OUT}/android/res/mipmap-anydpi-v26', exist_ok=True)
xml = '''<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@mipmap/ic_launcher_background"/>
    <foreground android:drawable="@mipmap/ic_launcher_foreground"/>
</adaptive-icon>
'''
for n in ('ic_launcher.xml', 'ic_launcher_round.xml'): open(f'{OUT}/android/res/mipmap-anydpi-v26/{n}', 'w').write(xml)
save(full, f'{OUT}/web/logo-icono-512.png', 512); save(full, f'{OUT}/web/logo-icono-192.png', 192)
# vista previa: máscaras de Android (círculo, squircle) y iOS
pv = Image.new('RGB', (1000, 300), (235, 236, 240))
ad = bgl.copy(); ad.alpha_composite(FG); c0 = int(S * 18 / 108); ad = ad.crop((c0, c0, S - c0, S - c0))   # lo que realmente se ve (72dp)
for i, (im, shape) in enumerate([(ad, 'circle'), (ad, 'squircle'), (full.convert('RGBA'), 'ios')]):
    t = im.resize((220, 220), Image.LANCZOS); m = Image.new('L', (220, 220), 0); dm = ImageDraw.Draw(m)
    if shape == 'circle': dm.ellipse([0, 0, 219, 219], fill=255)
    else: dm.rounded_rectangle([0, 0, 219, 219], 70 if shape == 'squircle' else 50, fill=255)
    pv.paste(t, (60 + i * 320, 40), m)
pv.save(f'{OUT}/vista_previa_mascaras.png')
print('ok')
