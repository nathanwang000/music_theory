#!/bin/bash
echo $1
# python ts2music.py -t $1 > tmp.ly
python ts2music.py > tmp.ly
lilypond tmp.ly
timidity tmp.midi

# rm tmp.pdf
# rm tmp.pdf
# rm tmp.midi
# rm tmp.ly
