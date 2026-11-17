#!/bin/bash
# ZENTRIX · videos "Próximamente": teaser (18 s) y barra de carga (8 s), en 16:9 y 9:16
set -e; cd "$(dirname "$0")"; mkdir -p build out
python3 -c "import json; d=json.load(open('src/promo_data.json')); open('build/promo_data.js','w').write('window.PD='+json.dumps(d,ensure_ascii=False)+';')"
for p in teaser carga portafolio; do
  [ -f build/$p.wav ] || python3 src/synth_promo.py $p build/$p.wav
  frames=$(python3 -c "import json; print(int(json.load(open('src/promo_data.json'))['$p']['dur']*60))"); per=$(( (frames + 3) / 4 ))
  for f in h v; do
    tag=$([ $f = v ] && echo 9x16 || echo 16x9); o=out/zentrix_systems_${p}_$tag.mp4; [ -f $o ] && continue
    : > build/list_${p}_$f.txt
    for k in 0 1 2 3; do PAGE=$([ $p = portafolio ] && echo portfolio.html || echo promo.html) node src/render_promo.js segment $p $f build/pseg_${p}_${f}_$k.mkv $((k*per)) $(((k+1)*per)) & echo "file 'pseg_${p}_${f}_$k.mkv'" >> build/list_${p}_$f.txt; done; wait
    ffmpeg -y -loglevel error -f concat -safe 0 -i build/list_${p}_$f.txt -i build/$p.wav -map 0:v -map 1:a \
      -vf "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p" -c:v libx264 -preset slow -crf 15 -profile:v high -r 60 \
      -colorspace bt709 -color_primaries bt709 -color_trc bt709 -c:a aac -b:a 320k -ar 48000 -movflags +faststart -shortest $o
  done
done
