#!/bin/bash
echo $1
python text2music.py -t "$1" > output/tmp.ly
cd output
lilypond tmp.ly
timidity tmp.midi
cd -
