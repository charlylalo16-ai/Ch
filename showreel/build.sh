#!/bin/bash
# Reproduce showreel.mp4 from source: music (numpy) + 900 frames (headless Chromium, 4 workers) + encode.
set -e; cd "$(dirname "$0")"; mkdir -p build
python3 src/synth.py build/score.wav
for k in 0 1 2 3; do node src/render.js segment build/seg$k.mkv $((k*225)) $(((k+1)*225)) & done; wait
printf "file 'seg0.mkv'\nfile 'seg1.mkv'\nfile 'seg2.mkv'\nfile 'seg3.mkv'\n" > build/list.txt
ffmpeg -y -loglevel error -f concat -safe 0 -i build/list.txt -i build/score.wav -map 0:v -map 1:a \
  -vf "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p" -c:v libx264 -preset slow -crf 14 \
  -profile:v high -tune film -r 60 -colorspace bt709 -color_primaries bt709 -color_trc bt709 \
  -c:a aac -b:a 320k -ar 48000 -movflags +faststart -t 15 showreel.mp4
