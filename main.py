from lib.notes import Note, Interval, Scale, NOTES, Chord
from lib.fret import get_fret
import numpy as np

def random_scale(root_notes=NOTES, majors=[True, False],
                 minor_modes=['natural', 'harmonic', 'melodic']):
    root_note = np.random.choice(root_notes)
    major = np.random.choice(majors)
    minor_mode = np.random.choice(minor_modes)
    return Scale(root_note, major=major, minor_mode=minor_mode)

def random_diatonic_harmony(scale):
    '''
    - method 1
    [[https://www.artofcomposing.com/08-diatonic-harmony][art of composing]]
    tonic pre-dominant dominant
    (1 6) (4 2) (7 5)

    rules, can go to the right, but must follow arrows when moving left
    left edges: (6, 1), (5, 6), (5, 1), (7, 1), (5, 4)

    - method 2
    https://www.youtube.com/watch?v=fXIEmMDwc7E
    (1, any), (2, 5), (3, 6), (4, 1), (4, 5), (5, 1), (6, 2)
    different from method 1 in (3, 6) and (4, 1) and (1, 3)

    sample from 1 until hit 1 again
    '''

    edges = {
        1: [2, 3, 4, 5, 6], # (1,3) may not work
        2: [7, 5],
        3: [6], # 6 may not work
        4: [2, 7, 5, 1], # 1 may not work
        5: [6, 1, 4],
        6: [4, 2, 7, 5, 1],
        7: [5, 1]
    }

    chord_num = 1
    chord = scale.chord(chord_num)
    print('chord {}:'.format(chord_num), chord, get_fret(chord))        
    chord_num = np.random.choice(edges[chord_num])

    while chord_num != 1:
        chord = scale.chord(chord_num)
        print('chord {}:'.format(chord_num), chord, get_fret(chord))
        chord_num = np.random.choice(edges[chord_num])        
    
    chord = scale.chord(chord_num)
    print('chord {}:'.format(chord_num), chord, get_fret(chord))
    

scale = random_scale(root_notes=['C'], majors=[True])
print(scale)
random_diatonic_harmony(scale)
    

