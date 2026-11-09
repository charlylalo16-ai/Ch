#!/bin/bash
# Quiroga Digital — video promocional (40 s) en vertical 9:16 y horizontal 16:9. Reanudable.
# Requiere: build/assets (capturas de la app hechas con lab/record.js) y python3+numpy, node+playwright, ffmpeg.
set -e; cd "$(dirname "$0")"; mkdir -p build out
[ -f build/quiroga.wav ] || python3 src/synth.py build/quiroga.wav
enc() {
  local f=$1 tag=$([ $1 = v ] && echo 9x16 || echo 16x9) n=4 per=1200; [ -f out/quiroga_digital_${tag}.mp4 ] && return 0
  : > build/list_$f.txt
  for ((k=0;k<n;k++)); do
    seg=build/seg_${f}_$k.mkv; echo "file 'seg_${f}_$k.mkv'" >> build/list_$f.txt
    if [ -f $seg ] && [ "$(ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 $seg 2>/dev/null)" = "$per" ]; then continue; fi
    node src/render.js segment q $f $seg $((k*per)) $(((k+1)*per)) &
  done; wait
  ffmpeg -y -loglevel error -f concat -safe 0 -i build/list_$f.txt -i build/quiroga.wav -map 0:v -map 1:a \
    -vf "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p" -c:v libx264 -preset slow -crf 17 -profile:v high -r 60 \
    -colorspace bt709 -color_primaries bt709 -color_trc bt709 -c:a aac -b:a 320k -ar 48000 -movflags +faststart -shortest out/tmp_${tag}.mp4
  mv out/tmp_${tag}.mp4 out/quiroga_digital_${tag}.mp4
}
enc v; enc h
