#!/bin/bash
# Genera los 6 videos de El Chiquilín: menu / intro / cierre × horizontal (16:9) y vertical (9:16)
set -e; cd "$(dirname "$0")"; mkdir -p build out
for p in menu intro cierre; do [ -f build/$p.wav ] || python3 src/synth.py $p build/$p.wav & done; wait
enc() { # piece fmt nseg
  local tag=$([ $2 = v ] && echo 9x16 || echo 16x9); [ -f out/chiquilin_$1_${tag}.mp4 ] && return 0
  local p=$1 f=$2 n=$3 frames=$4 per=$(( ($4 + $3 - 1) / $3 )); : > build/list_${p}_$f.txt
  for ((k=0;k<n;k++)); do node src/render.js segment $p $f build/${p}_${f}_$k.mkv $((k*per)) $(((k+1)*per)) & echo "file '${p}_${f}_$k.mkv'" >> build/list_${p}_$f.txt; done; wait
  ffmpeg -y -loglevel error -f concat -safe 0 -i build/list_${p}_$f.txt -i build/$p.wav -map 0:v -map 1:a \
    -vf "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p" -c:v libx264 -preset slow -crf 15 -profile:v high -r 60 \
    -colorspace bt709 -color_primaries bt709 -color_trc bt709 -c:a aac -b:a 320k -ar 48000 -movflags +faststart -shortest out/chiquilin_${p}_${tag}.mp4
}
enc menu h 4 900; enc menu v 4 900
enc intro h 2 225 & enc intro v 2 225 & wait
enc cierre h 2 225 & enc cierre v 2 225 & wait
