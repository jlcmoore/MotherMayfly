#!/bin/sh
ffmpeg -i $1 -ss 00:00:00.000 -vframes 1 $1.jpg
open -W $1.jpg
rm $1.jpg
