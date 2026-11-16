#!/bin/bash
# ZENTRIX STUDIO · intro de logo (7 s) en 16:9 y 9:16, 60 fps
set -e; cd "$(dirname "$0")"; mkdir -p build out
[ -f build/intro.wav ] || python3 src/synth.py build/intro.wav
for f in h v; do
  tag=$([ $f = v ] && echo 9x16 || echo 16x9); [ -f out/zentrix_intro_$tag.mp4 ] && continue
  : > build/list_$f.txt
  for k in 0 1 2 3; do node src/render.js segment i $f build/seg_${f}_$k.mkv $((k*105)) $(((k+1)*105)) & echo "file 'seg_${f}_$k.mkv'" >> build/list_$f.txt; done; wait
  ffmpeg -y -loglevel error -f concat -safe 0 -i build/list_$f.txt -i build/intro.wav -map 0:v -map 1:a \
    -vf "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p" -c:v libx264 -preset slow -crf 14 -profile:v high -r 60 \
    -colorspace bt709 -color_primaries bt709 -color_trc bt709 -c:a aac -b:a 320k -ar 48000 -movflags +faststart -shortest out/zentrix_intro_$tag.mp4
done
