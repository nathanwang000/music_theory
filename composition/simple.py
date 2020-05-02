import argparse
import itertools
from functools import partial
import numpy as np

parser = argparse.ArgumentParser(description="simple composition tool try")
parser.add_argument('-t', type=str, nargs='+', default=['c', 'e', 'g'])
args = parser.parse_args()

def main(lines, tempo='4=140', time_signature='4/4'):
    '''
    lines: list of time serieses to play
    '''
    assert type(lines[0]) in [tuple, list], "melodic lines should be list of list"
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

def chord(scale, degrees):
    '''a chord'''
    return '<' + " ".join([scale(d) for d in degrees]) + ">"

def swing(chord1, chord2=None):
    '''swing rhythm emphasizes the first beat more than the second'''
    chord2 = chord2 if chord2 else chord1
    return r"\tuplet 3/2 %s8~ %s %s " % (chord1, chord1, chord2)

def note2number(note):
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
            
def number2note(n):
    '''
    the inverse of note2number
    but this is still ambiguous: e.g., fes = e = disis,
    need to be given scale to determine what is, now not supported
    '''
    notes = ['c', 'cis', 'd', 'ees', 'e', 'f', 'fis', 'g', 'gis', 'a', 'bes', 'b']
    note, pitch = notes[n % 12], n // 12
    return note + ("," if pitch < 0 else "'") * abs(pitch)

def build_scale(root, mode='Ionian'):
    '''
    build scale from the root
    example usage:
    scale = build_scale('c', 'dorian')
    or
    scale = build_scale('c', 1)    
    main([scale(i) for i in range(1, 8)])
    '''
    modes = ['ionian', 'dorian', 'phrygian', 'lydian', 'mixolydian',
             'aeolian', 'locrian']
    # convert mode to number
    if type(mode) is str:
        mode = dict((a, b) for a, b in zip(modes, range(len(modes))))[mode.lower()]

    diffs = [2, 2, 1, 2, 2, 2, 1] # diff between nodes in 'ionian'
    diffs = np.cumsum([0] + diffs[mode:] + diffs[:mode])
    n = note2number(root)
    
    def scale(degree):
        '''degree can be a number, or a tuple with offset'''
        if type(degree) is not int:
            degree, offset = degree
        else:
            offset = 0
        idx, span  = (degree - 1) % 7, (degree - 1) // 7
        return number2note(n + span * 12 + diffs[idx] + offset)
    
    return scale

################## note manipulation ############
def invert(degrees, root=1):
    '''invert a series of degrees where each degree could be a
    int or a tuple of int, treat root as the invariant'''
    res = []
    for d in degrees:
        if type(d) is int:
            res.append(root - (d-1))
        else:
            res.append([root - (d[0]-1), -d[1]])
    return res

################## rhythm notations #############
def add_rhythm(notes, rhythm_pattern=None, unit=16, assert_equal=True):
    '''
    unit: the smallest granularity
    rhythm_pattern: [2, 3] means 2 continuous unit followed by a 3 continuous unit
    output: list of nodes with rhythm
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
def tweleve_bar_blues(scale=build_scale('c', 'ionian')):
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
    
    main([ts], tempo='4=160')

################## improvisation for 1 bar ########
def random_notes(scale):
    '''
    random for 1 bar, choose from a scale and the rest bar
    '''
    choose_from = [scale(i) for i in range(1,8)] + ['r']
    # return [scale(i) for i in np.random.choice(range(1,8), 7)] + ['r']    
    return np.random.choice(choose_from, 8)

def up_scale(scale):
    '''
    for 1 bar
    '''
    return [scale(i) for i in list(range(1,8))] + ['r']

def down_scale(scale):
    '''
    for 1 bar
    '''
    return [scale(i) for i in list(range(8,1,-1))] + ['r']

def random_rhythm(unit=8):
    '''random rhythm for unit beats'''
    res = []
    curr = 0
    while curr < unit:
        cand = np.random.choice(range(1, unit+1))
        res.append(min(cand, unit-curr))
        curr += res[-1]
    return res

def dorian_improv():
    '''for improvisation: https://www.youtube.com/watch?v=o7dGlZAMKi0'''
    mode = 'dorian'
    root = 'd'
    scale = build_scale(root, mode)
    rhythm = [1, 1, 1, 5]
    notes = [scale(i) for i in [1, 3, 5, 6]]
    bass = add_rhythm(notes, rhythm, unit=8)

    debug = False
    scale = build_scale(root + "'", mode)
    if debug:
        mel = [scale(i) for i in [1, 3, 5, 7, 7, 8, 6, 6]]
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

################# variation helpers ################
def melody_variation(degrees, rhythm, scale, unit,
                     degree_transform=lambda x: x,
                     rhythm_transform=lambda x: x):
    '''
    a piece of music is composed of
    degrees, rhythm, scale, unit
    This function takes the piece and transforms it with rhythm_transform
    and degree_transform
    returns a timeseries, ts, playable by main([ts], tempo=tempo)
    '''
    ts = add_rhythm([scale(i) for i in degree_transform(degrees)],
                    rhythm_transform(rhythm), unit=unit)
    return ts

################# specific variations #############
def variation_idea0(degrees, rhythm, scale, unit, tempo):
    '''
    uses melody_variation and performs certain predefined 
    variation on a given piece
    '''
    mels = []    
    # original melody
    mels.append(melody_variation(degrees, rhythm, scale, unit))
    # build other variations
    ### inversion
    for degree_transform in [partial(invert, root=5)]:
        mels.append(melody_variation(degrees, rhythm, scale, unit,
                                     degree_transform))
    ### change scale
    for s in [build_scale("bes'", 'aeolian'),
              build_scale("b'", 'aeolian'),
              build_scale("c''", 'aeolian')]:
        mels.append(melody_variation(degrees, rhythm, s, unit))
    ### ending
    mels.append(add_rhythm(up_scale(s), unit=unit))
    mels.append(add_rhythm(down_scale(s), unit=unit))
    mels.append(
        add_rhythm([chord(s, [1, 3, 5]), 
                    chord(s, [0, 2, 4, (6, -1)]), 
                    chord(s, [1-7, 3-7, 5-7])],
                   unit=1),
    )
    
    # output sound
    lines = [list(itertools.chain(*mels))]
    main(lines, tempo=tempo)
    
################# specific pieces ################
def pagnini24():
    scale = build_scale("a'", 'aeolian')
    unit = 16
    tempo = '4=140'    
    degrees = [1, 1,
               1, 3, 2, 1,
               5, 5-7,
               5-7, (7-7, 1), (6-7, 1), 5-7,
               1, 1,
               1, 3, 2, 1,
               5,
               5-7]
    rhythm = [3, 1,
              1, 1, 1, 1,
              3, 1,
              1, 1, 1, 1,
              3, 1,
              1, 1, 1, 1,
              4,
              4]
    return degrees, rhythm, scale, unit, tempo

def shengmusong():
    ##### this is for 圣母颂 todo:
    scale = build_scale("c''")
    tempo = '4=140'        
    unit = 4
    degrees = [
        3, 4, 5, 2, 3,
        6, 6-7, 7-7, 1, 2, 3, 2,
        5, 5-7, 6-7, 7-7, 1, 2, 1,
        1+7, 1, 2, 3, (4, 1), 3, 2, 6-7, 7-7,
    ]

    rhythm = [
        4, 4, 3, 1, 4,
        5, 1, 1, 1, 3, 1, 4,
        5, 1, 1, 1, 3, 1, 4,
        5, 1, 1, 1, 3, 1, 2, 2, 4
    ]
    return degrees, rhythm, scale, unit, tempo

def changtingwai():
    #### this is a chinese folk song 长亭外 古道边
    tempo = '4=100'
    scale = build_scale("c''", 5)
    unit = 8
    degrees = [
        5, 3, 5, 1+7, 7, 6, 1+7, 5,
        5, 1, 2, 3, 2, 1, 2,
        5, 3, 5, 1+7, 7, 6, 1+7, 5,
        5, 2, 3, 4, 7-7, 1
    ]
    rhythm = [
        2, 1, 1, 3, 1, 2, 2, 4,
        2, 1, 1, 2, 1, 1, 8,
        2, 1, 1, 3, 1, 2, 2, 4,
        2, 1, 1, 2, 2, 8
    ]    
    return degrees, rhythm, scale, unit, tempo

if __name__ == '__main__':
    # dorian_improv()

    # variation_idea0(*pagnini24())
    # variation_idea0(*shengmusong())
    variation_idea0(*changtingwai())    

    ## playground of ideas
    # cmaj = build_scale("c'", 0)
    # dmaj = build_scale("d'", 0)
    # main([
    #     add_rhythm([chord(cmaj, [1, 3, 5]), # c7
    #                 chord(dmaj, [1, 3, 5, (7, -1)]), # d7
    #                 chord(cmaj, [5-7, 2-7, 7])],
    #                unit=2),
    # ])
