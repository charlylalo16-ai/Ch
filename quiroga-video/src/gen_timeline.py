"""
Genera src/timeline.json y src/timeline.js: la ÚNICA fuente de tiempos.
La usan el video (index.html) y la música (synth.py), así todo queda sincronizado.
Ritmo pausado (v2): 96 BPM, 32 compases de 2.5 s = 80 s.
"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
META = json.load(open(os.path.join(HERE, '..', 'build', 'assets', 'screens', 'meta.json')))
SB = 28
BPM, BARS = 96, 32

screens, taps, typing, caps = [], [], [], []
sfx = {'whoosh': [], 'chime': [], 'alarm': [], 'impact': [], 'hold': []}

def at(t, name, tr='cut', **o): screens.append([round(t, 3), name, tr, o])
def rect(name, key, fallback=(206, 460)):
    r = META.get(name, {}).get('rects', {}).get(key)
    return [r[0], r[1] + SB] if r else [fallback[0], fallback[1] + SB]
def tap(t, xy, hold=None):
    taps.append([round(t, 3), xy[0], xy[1]] + ([hold] if hold else []))
def seq(prefix, t0, t1):
    import re
    ks = [k for k in META if re.fullmatch(re.escape(prefix) + r'\d+', k)]
    for i, k in enumerate(ks): at(t0 + (t1 - t0) * (i / max(1, len(ks) - 1)), k)
    typing.append([t0 - 0.05, t1 + 0.05]); return ks
def trans(t, name, tr): at(t, name, tr); sfx['whoosh'].append(t)

HOME_ICON = [34 + 2 * 92, 420 + 2 * 104]
# ---- 0–5 intro (sin teléfono) ----
# intro suave: sin golpe (las flores crecen)
# ---- 5–10 teléfono, inicio de Android, abrir la app ----
at(5.0, 'HOME', 'none'); sfx['whoosh'].append(4.7)
tap(6.9, [HOME_ICON[0] + 30, HOME_ICON[1] + 30])
trans(7.5, 'SPLASH', 'open')
# ---- 10–20 registro ----
trans(10.0, 'login', 'fade')
tap(10.9, rect('login', 'tabReg')); at(11.1, 'reg_empty')
tap(11.6, rect('reg_empty', 'name')); seq('reg_nombre_', 11.85, 13.2)
tap(13.5, rect('reg_pass_03', 'field')); seq('reg_pass_', 13.65, 14.15); seq('reg_pass2_', 14.3, 14.85)
tap(15.2, rect('reg_tel_02', 'field')); seq('reg_tel_', 15.35, 16.4)
tap(16.8, rect('reg_genero', 'field')); at(16.95, 'reg_genero')
tap(17.4, rect('reg_localidad', 'field')); at(17.55, 'reg_localidad')
tap(18.0, rect('reg_dir_04', 'field')); seq('reg_dir_', 18.15, 18.75)
tap(19.0, rect('reg_terminos', 'field')); at(19.05, 'reg_terminos')
tap(19.5, rect('reg_press', 'btn')); at(19.5, 'reg_press'); at(19.65, 'reg_creando')
# ---- 20–25 SMS ----
trans(20.0, 'sms_empty', 'fade')
tap(20.8, rect('sms_empty', 'field')); seq('sms_', 21.0, 22.5)
tap(23.0, rect('sms_empty', 'btn')); at(23.2, 'sms_ok'); sfx['chime'].append(23.25)
# ---- 25–30 inicio ----
trans(25.0, 'inicio_0', 'up')
at(26.8, 'inicio_220', 'scroll', dy=220); at(28.2, 'inicio_440', 'scroll', dy=220)
# ---- 30–45 ALERTA MUJER ----
trans(30.0, 'emerg', 'slide')
HOLD0, HOLD1 = 31.5, 33.5
tap(31.0, rect('emerg', 'sos'), HOLD1); sfx['hold'] = [HOLD0, HOLD1]
for i in range(1, 11): at(HOLD0 + (i - 1) * 0.2, 'hold_%02d' % i)
at(33.5, 'alerta_enviando', 'fade'); sfx['impact'].append(33.5)
at(35.0, 'alerta_enviada', 'fade'); sfx['alarm'].append(35.0)
tap(37.6, rect('alerta_enviada', 'chip')); at(37.8, 'alerta_recibida')
at(40.0, 'alerta_asignada'); sfx['chime'].append(40.1)
at(42.5, 'alerta_atencion'); sfx['chime'].append(42.6)
# ---- 45–50 widget / acceso directo ----
trans(45.0, 'HOME_W', 'fade')
tap(47.3, [HOME_ICON[0] + 30, HOME_ICON[1] + 30], 47.9)
# ---- 50–57.5 reportes ----
trans(50.0, 'rep_empty', 'slide')
tap(50.8, rect('rep_empty', 'area')); at(51.0, 'rep_area')
tap(51.6, rect('rep_titulo_04', 'field')); seq('rep_titulo_', 51.8, 53.0)
tap(53.3, rect('rep_desc_12', 'field')); seq('rep_desc_', 53.5, 54.8)
tap(55.1, rect('rep_ubic_07', 'field')); seq('rep_ubic_', 55.3, 56.0)
at(56.2, 'rep_listo', 'fade'); tap(56.45, rect('rep_listo', 'btn')); at(56.55, 'rep_enviando')
at(57.0, 'rep_ok', 'fade'); sfx['chime'].append(57.0)
# ---- 57.5–62.5 avisos ----
tap(57.35, [115, 858 + SB]); trans(57.5, 'avisos_0', 'slide'); at(60.0, 'avisos_260', 'scroll', dy=260)
# ---- 62.5–67.5 camión ----
tap(62.35, [294, 858 + SB]); trans(62.5, 'camion_0', 'slide')
at(63.8, 'camion_1', 'fade'); at(65.0, 'camion_2', 'fade'); at(66.2, 'camion_3', 'fade')
# ---- 67.5–72.5 mensajes ----
tap(67.35, [376, 858 + SB]); trans(67.5, 'mensajes', 'slide')
tap(69.6, [293, 238 + SB]); trans(69.8, 'chat', 'slide'); sfx['chime'].append(70.3)
# ---- 72.5–80 cierre ----
sfx['whoosh'].append(72.5); sfx['impact'].append(73.4)

caps = [
    [10.0, 20.0, '1', 'Regístrate en un minuto', [['Solo para gente de Quiroga y sus localidades', 10.0], ['Llenas tus datos una sola vez', 15.0]]],
    [20.0, 25.0, '1', 'Verificación segura', [['Te llega un código por SMS', 20.0]]],
    [25.0, 30.0, '2', 'Tu municipio en un solo lugar', [['Avisos, reportes, emergencias y más', 25.0]]],
    [30.0, 45.0, '3', 'ALERTA MUJER', [['Mantén presionado 2 segundos', 30.0], ['Tu ubicación se envía al instante', 33.5], ['Seguridad Pública recibe tu alerta', 37.8], ['Personal asignado, en camino', 40.0]]],
    [45.0, 50.0, '3', 'ALERTA MUJER', [['También desde el widget', 45.0], ['…o desde el acceso directo', 47.3]]],
    [50.0, 57.5, '4', 'Reporta en segundos', [['Baches, fugas, luminarias, basura…', 50.0], ['Con ubicación y foto', 54.0]]],
    [57.5, 62.5, '5', 'Avisos oficiales', [['Entérate primero de lo que pasa en Quiroga', 57.5]]],
    [62.5, 67.5, '6', 'Camión de basura', [['Ubicación en tiempo real', 62.5]]],
    [67.5, 72.5, '7', 'Habla con cada área', [['Mensajes directos con el Ayuntamiento', 67.5]]],
]
sos = rect('emerg', 'sos')
camera = [[29.9, 1, 206, 460], [30.9, 1, 206, 460], [31.6, 'Z1', sos[0], 0], [33.4, 'Z2', sos[0], 0],
          [33.9, 'Z3', 206, 0], [44.4, 'Z3', 206, 0], [45.0, 1, 206, 460]]
sections = ['intro'] * 2 + ['light'] * 10 + ['alert'] * 6 + ['full'] * 11 + ['outro'] * 3
TL = dict(bpm=BPM, bars=BARS, dur=BARS * 60 / BPM * 4, sections=sections, screens=sorted(screens, key=lambda s: s[0]),
          taps=taps, typing=typing, caps=caps, camera=camera, home_icon=HOME_ICON, **sfx)
json.dump(TL, open(os.path.join(HERE, 'timeline.json'), 'w'), indent=1, ensure_ascii=False)
open(os.path.join(HERE, 'timeline.js'), 'w').write('window.TLD = ' + json.dumps(TL, ensure_ascii=False) + ';')
print('ok', TL['dur'], 's,', len(screens), 'estados,', len(taps), 'toques')
