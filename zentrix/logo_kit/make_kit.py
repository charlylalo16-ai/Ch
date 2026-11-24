"""Kit de logo ZENTRIX SYSTEMS: variantes SVG (oscuro, claro, blanco, ícono) a partir del SVG por capas del cliente.
uso: python3 make_kit.py  -> dist/svg/*.svg ; luego node render.js -> dist/png/*.png"""
import os, re
SRC = open('../assets/zentrix-logo-por-capas.svg', encoding='utf-8').read()
os.makedirs('dist/svg', exist_ok=True)
def strip_size(s): return re.sub(r' width="[^"]+" height="[^"]+"', '', s, count=1)
def light(s):
    # para fondos claros: letras ZENTRIX en azul marino, Z plateada más oscura
    s = s.replace('<stop offset="0" stop-color="#FFFFFF"/><stop offset=".45" stop-color="#D3D7DC"/><stop offset=".72" stop-color="#8F959D"/><stop offset="1" stop-color="#E8EAED"/>',
                  '<stop offset="0" stop-color="#5A6472"/><stop offset=".45" stop-color="#2E3644"/><stop offset=".72" stop-color="#151B26"/><stop offset="1" stop-color="#3C4556"/>')
    i, j = s.index('id="06-ZENTRIX"'), s.index('id="07-SYSTEMS"')
    s = s[:i] + s[i:j].replace('#F2F3F5', '#0B1633').replace('#FFFFFF', '#0B1633') + s[j:]
    return s
def white(s):
    s = re.sub(r'(fill|stroke|stop-color)="#[0-9A-Fa-f]{6}"', r'\1="#FFFFFF"', s)
    s = s.replace('#cutL" ', '#cutL" ')
    # el corte entre Z y órbita sigue funcionando porque usa máscara/clip, no color
    return s
def mono_dark(s):
    s = re.sub(r'(fill|stroke|stop-color)="#[0-9A-Fa-f]{6}"', r'\1="#0B1633"', s)
    return s
def icon(s):
    # solo ZS + órbita (sin texto)
    for gid, nxt in (('06-ZENTRIX', '07-SYSTEMS'), ):
        pass
    s = re.sub(r'<g id="06-ZENTRIX".*?(?=<g id="07-SYSTEMS")', '', s, flags=re.S)
    s = re.sub(r'<g id="07-SYSTEMS".*?(?=<g id="08-lineas")', '', s, flags=re.S)
    s = re.sub(r'<g id="08-lineas".*?</g>(?=</svg>)', '', s, flags=re.S)
    return s
V = {
    'zentrix_logo_fondo_oscuro': SRC,
    'zentrix_logo_fondo_claro': light(SRC),
    'zentrix_logo_blanco': white(SRC),
    'zentrix_logo_una_tinta_azul_marino': mono_dark(SRC),
    'zentrix_icono_fondo_oscuro': icon(SRC),
    'zentrix_icono_fondo_claro': icon(light(SRC)),
    'zentrix_icono_blanco': icon(white(SRC)),
}
for k, s in V.items():
    open(f'dist/svg/{k}.svg', 'w', encoding='utf-8').write(strip_size(s))
print('\n'.join(V))
