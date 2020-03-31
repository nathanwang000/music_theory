#!/bin/bash
echo $1
# python ts2music.py -t $1 > tmp.ly
python ts2music.py > output/tmp.ly
cd output
lilypond tmp.ly
timidity tmp.midi
cd -
