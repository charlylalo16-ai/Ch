#!/usr/bin/env bash
# Arma dist/zentrix-intro.js metiendo el SVG por capas del cliente, más el sonido en mp3 y la página de ejemplo.
set -e; cd "$(dirname "$0")"; mkdir -p dist
python3 - <<'PY'
import json, re
svg = open('../assets/zentrix-logo-por-capas.svg', encoding='utf-8').read()
svg = re.sub(r'<\?xml[^>]*\?>', '', svg).strip()
src = open('zentrix-intro.src.js', encoding='utf-8').read().replace('__SVG__', json.dumps(svg, ensure_ascii=False))
open('dist/zentrix-intro.js', 'w', encoding='utf-8').write(src)
PY
python3 ../src/synth.py dist/_intro.wav >/dev/null 2>&1 || cp ../build/intro.wav dist/_intro.wav
ffmpeg -loglevel error -y -i dist/_intro.wav -codec:a libmp3lame -b:a 160k dist/zentrix-intro.mp3 && rm -f dist/_intro.wav
cp ejemplo.html dist/index.html; cp LEEME.txt dist/
echo listo; ls -la dist
