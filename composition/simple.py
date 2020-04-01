import argparse
import logging
import numpy as np
from functools import partial
import yfinance as yf
import pandas as pd

parser = argparse.ArgumentParser(description="simple composition tool try")
parser.add_argument('-t', type=str, nargs='+', default=['c', 'e', 'g'])
args = parser.parse_args()

def main(ts, tempo='4=140', time_signature='4/4'):
    '''
    ts is time series to play
    '''
    staff = "\score{  \n\\new PianoStaff << \n"
    staff += "  \\new Staff { \\clef treble \\tempo %s \\time %s " \
             % (tempo, time_signature) +\
             " ".join(ts) + "}\n"
    staff += ">>\n \layout {} \midi{} }\n"

    title = """\\version "2.18.2"
    \header {
    title = "simple chords"
    composer = "Jiaxuan Wang"
    tagline = "Copyright: MIT license"
    }"""

    print(title + staff)

def number2note(n, scale, use_pitch=True):
    note, pitch = n % len(scale), n // len(scale) if use_pitch else 0
    return "{}{}".format(scale[note], "'" * (pitch))

def chord(scale, degrees):
    # degree is 1 above
    n2note = partial(number2note, scale=scale)
    return '<' + " ".join([n2note(d-1) for d in degrees]) + ">"

def swing(chord1, chord2=None):
    chord2 = chord2 if chord2 else chord1
    return r"\tuplet 3/2 %s8~ %s %s " % (chord1, chord1, chord2)

if __name__ == '__main__':
    # todo develop a small language for myself to write simple chord
    cmaj = [chr(ord("a") + i) for i in range(7)]
    cmaj = cmaj[2:] + cmaj[:2]

    chords5 = [swing(chord(cmaj, [i,i+4])) for i in range(8)]
    chords6 = [swing(chord(cmaj, [i,i+5])) for i in range(8)]
    finish = [swing(chord(cmaj, [i,i+5]),
                    chord(cmaj, [i,i+4])) + r"\fermata" for i in range(8)]
    # 12 bar blues
    ts = [chords5[1], chords6[1], chords5[1], chords6[1],
          chords5[1], chords6[1], chords5[1], chords6[1],
          chords5[1], chords6[1], chords5[1], chords6[1],
          chords5[1], chords6[1], chords5[1], chords6[1],          
          chords5[4], chords6[4], chords5[4], chords6[4],
          chords5[4], chords6[4], chords5[4], chords6[4],          
          chords5[1], chords6[1], chords5[1], chords6[1],          
          chords5[1], chords6[1], chords5[1], chords6[1],
          chords5[5], chords6[5], chords5[5], chords6[5],
          chords5[4], chords6[4], chords5[4], chords6[4],                    
          chords5[1], chords6[1], chords5[1], chords6[1],
          chords5[1], chords6[1], chords5[1], finish[1]]
    
    main(ts, tempo='4=160')
