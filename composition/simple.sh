#!/bin/bash
echo $1
python simple.py | tee output/tmp.ly
cd output
lilypond tmp.ly
timidity tmp.midi
cd -
