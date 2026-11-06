#!/bin/bash
# Genera el video de Sonido y Karaoke (30 s) en horizontal 16:9 y vertical 9:16. Reanudable.
set -e; cd "$(dirname "$0")"; mkdir -p build out
[ -f build/sonido.wav ] || python3 src/synth.py sonido build/sonido.wav
enc() { # fmt
  local f=$1 tag=$([ $1 = v ] && echo 9x16 || echo 16x9) n=4 per=450; [ -f out/sonido_karaoke_${tag}.mp4 ] && return 0
  : > build/list_$f.txt
  for ((k=0;k<n;k++)); do
    seg=build/seg_${f}_$k.mkv; echo "file 'seg_${f}_$k.mkv'" >> build/list_$f.txt
    if [ -f $seg ] && [ "$(ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 $seg 2>/dev/null)" = "$per" ]; then continue; fi
    node src/render.js segment sonido $f $seg $((k*per)) $(((k+1)*per)) &
  done; wait
  ffmpeg -y -loglevel error -f concat -safe 0 -i build/list_$f.txt -i build/sonido.wav -map 0:v -map 1:a \
    -vf "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p" -c:v libx264 -preset slow -crf 16 -profile:v high -r 60 \
    -colorspace bt709 -color_primaries bt709 -color_trc bt709 -c:a aac -b:a 320k -ar 48000 -movflags +faststart -shortest out/sonido_karaoke_${tag}.mp4.tmp.mp4
  mv out/sonido_karaoke_${tag}.mp4.tmp.mp4 out/sonido_karaoke_${tag}.mp4
}
enc h; enc v
