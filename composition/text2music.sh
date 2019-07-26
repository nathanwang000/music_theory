#!/bin/bash
echo $1
python text2music.py -t "$1" > tmp.ly
lilypond tmp.ly
timidity tmp.midi

rm tmp.pdf
rm tmp.midi
rm tmp.ly
