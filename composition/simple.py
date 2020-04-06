import argparse
import logging
import numpy as np
from functools import partial
import yfinance as yf
import pandas as pd
import itertools

parser = argparse.ArgumentParser(description="simple composition tool try")
parser.add_argument('-t', type=str, nargs='+', default=['c', 'e', 'g'])
args = parser.parse_args()

def main(lines, tempo='4=140', time_signature='4/4'):
    '''
    lines: list of time serieses to play
    '''
    body = "\score{\n \\new PianoStaff << \n"
    for ts in lines:
        body += "  \\new Staff { \\clef treble \\tempo %s \\time %s "\
                % (tempo, time_signature)
        body += " ".join(ts)
        body += "}\n"
    body += ">>\n \layout {} \midi{} }\n"

    title = """\\version "2.18.2"
    \header {
    title = "simple chords"
    composer = "Jiaxuan Wang"
    tagline = "Copyright: MIT license"
    }"""

    print(title + body)

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

def abs_note2number(note):
    '''
    calculate the absolute number from note to number
    ex: "c" -> 0
    ex: "fis''" -> 12 * 2 + 6 = 30
    ex: "c," -> -12
    '''
    notes = ['c', 'd', 'e', 'f', 'g', 'a', 'b']
    degrees = [0, 2, 4, 5, 7, 9, 11]
    n = degrees[notes.index(note[0])]
    c = ""
    for p in range(1, len(note)):
        c = c + note[p]
        if c == 'is':
            n += 1
            c = ""
        elif c == 'es':
            n -= 1
            c = ""
        elif c == "'":
            n += 12
            c = ""            
        elif c == ',':
            n -= 12
            c = ""
    assert c == "", "have unparsed note {}".format(c)
    return n
            
def abs_number2note(n, scale=None):
    '''
    the inverse of abs_note2number
    but this is still ambiguous: e.g., fes = e = disis,
    need to be given scale to determine what is
    '''
    if scale is None:
        scale = ['c', 'cis', 'd', 'ees', 'e', 'f', 'fis', 'g', 'gis', 'a', 'bes', 'b']
    note, pitch = scale[n % 12], n // 12
    return note + ("," if pitch < 0 else "'") * abs(pitch)

def build_scale(root, mode='Ionian'):
    '''
    build scale from the root
    example usage:
    scale = build_scale('c', 'dorian')
    main(scale)
    '''
    modes = ['ionian', 'dorian', 'phrygian', 'lydian', 'mixolydian',
             'aeolian', 'locrian']
    # convert mode to number
    if type(mode) is str:
        mode = dict((a, b) for a, b in zip(modes, range(len(modes))))[mode.lower()]

    diffs = [2, 2, 1, 2, 2, 2, 1] # diff between nodes in 'ionian'
    diffs = np.cumsum([0] + diffs[mode:] + diffs[:mode])
    n = abs_note2number(root)
    return [abs_number2note(n+diff) for diff in diffs]

################## rhythm notations #############
def add_rhythm(notes, rhythm_pattern=None, unit=16, assert_equal=True):
    '''
    unit: the smallest granularity
    rhythm_pattern: [2, 3] means 2 continuous unit followed by a 3 continuous unit
    '''
    if rhythm_pattern is None:
        rhythm_pattern = [1] * len(notes)

    if assert_equal:
        assert len(rhythm_pattern) == len(notes), 'rhythm and notes length differ'
    else:
        # repeat notes if rhythm has more
        if len(notes) < len(rhythm_pattern):
            if len(notes) == 0:
                notes = ["a'"]
            notes = notes + [notes[-1]] * (len(rhythm_pattern) - len(notes))
        notes = notes[:len(rhythm_pattern)]
    
    def simplify(rythm, note, unit=16):
        '''
        now is just a dumb slur; should simplfy later
        '''
        notes = ['{}{}'.format(note, unit) for _ in range(rythm)]
        for i in range(len(notes)-1):
            notes[i] += '~'
        if len(notes) > 1:
            notes[0] = notes[0] + '('
            notes[-1] = notes[-1] + ')'        
        return ' '.join(notes)
    
    return [simplify(r, n, unit=unit) for r, n in zip(rhythm_pattern, notes)]

################## improvisation  #################
def tweleve_bar_blues(scale):
    # todo: https://www.youtube.com/watch?v=BjhkClSUdYM
    '''
    12 bar blues 
    example usage:
    scale = build_scale('c', 'dorian')
    tweleve_bar_blues(scale)
    '''
    chords5 = [swing(chord(scale, [i,i+4])) for i in range(8)]
    chords6 = [swing(chord(scale, [i,i+5])) for i in range(8)]
    finish = [swing(chord(scale, [i,i+5]),
                    chord(scale, [i,i+4])) + r"\fermata" for i in range(8)]
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

################## improvisation for 1 bar ########
def random_notes(scale):
    '''
    random for 1 bar
    '''
    choose_from = scale + ['r']
    # return [scale[i-1] for i in np.random.choice(range(1,8), 7)] + ['r']    
    return np.random.choice(choose_from, 8)

def up_scale(scale):
    '''
    for 1 bar
    '''
    return [scale[i-1] for i in list(range(1,8))] + ['r']

def down_scale(scale):
    '''
    for 1 bar
    '''
    return [scale[i-1] for i in list(range(8,1,-1))] + ['r']

def random_rhythm(unit=8):
    res = []
    curr = 0
    while curr < unit:
        cand = np.random.choice(range(1, unit+1))
        res.append(min(cand, unit-curr))
        curr += res[-1]
    return res
    
if __name__ == '__main__':
    # for improvisation: https://www.youtube.com/watch?v=o7dGlZAMKi0
    mode = 'dorian'
    root = 'd'
    scale = build_scale(root, mode)
    rhythm = [1,1,1,5]
    notes = [scale[i-1] for i in [1, 3, 5, 6]]
    bass = add_rhythm(notes, rhythm, unit=8)

    debug = False
    scale = build_scale(root + "'", mode)
    if debug:
        mel = [scale[i-1] for i in [1, 3, 5, 7, 7, 8, 6, 6]]
        pieces = [mel, ['r'],
                  down_scale(scale),
                  random_notes(scale),
                  random_notes(scale),
                  random_notes(scale),              
                  up_scale(scale)]
        upper = add_rhythm(list(itertools.chain(*pieces)), unit=8)

    else:
        pieces = [add_rhythm(random_notes(scale), random_rhythm(),
                             assert_equal=False, unit=8) for _ in range(5)]
        upper = list(itertools.chain(*pieces))

    lines = [upper, bass * 5] 
    main(lines, tempo='4=100')
    

    
