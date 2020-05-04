#!/bin/bash
echo $1
rm output/tmp.*
python simple.py | tee output/tmp.ly
cd output
lilypond tmp.ly
ps2pdf tmp.ps || { echo 'my_command failed' ; exit 1; }

timidity tmp.midi
cd -
