#!/bin/sh
mkdir frames
# crop=out_w:out_h:x:y for video 
ffmpeg -i $1 -vf crop=$2:$3:$4:$5 -r 12 'frames/frame-%03d.jpg'
convert -delay $6 -loop 0 frames/*.jpg $1.gif
rm -rf frames
