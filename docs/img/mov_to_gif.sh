#!/bin/sh
mkdir frames
# crop=out_w:out_h:x:y for video 
ffmpeg -i $1 -vf crop=$2:$3:$4:$5 -r 4 'frames/frame-%03d.jpg'
echo "here"
convert -delay 20 -loop 0 frames/*.jpg $1.gif
rm -rf frames
