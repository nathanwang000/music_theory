'''
todo: make main([Staff([])]) a ysnippet

Write music by writing degrees and rhythm
- rest can be written as 'r' in degrees
- list of staffed melodies can be play together by main

EXAMPLES:

##### easy way to directly use lilypond notation
# tuplet
>> main([Staff([r'\tuplet 3/2 {c d g}'])])

# tuplet: rhythm read as consume 3 notes but occupy 2 time units
>> main([Staff(melody([1, 2, 5], [(3, 2)]))])

##### appregio
# play appegio of c:7
>> play_notes(['c', 'e', 'g', 'bes'], unit=4)

# play appegio of c:7
>> main([Staff(melody([1,3,5,(7,-1)]), 'piano')])

# play appegio of c:7
>> main([Staff(['c4', 'e4', 'g4', 'bes4'])])

##### chord
# play chord of c:7
>> play_chord_mode(['c:7'])

# play chord of c:7
>> play_notes([chord(build_scale("c'",0), [1,3,5,(7,-1)])])

# play chord of c:7
>> main([Staff(melody([chord(build_scale("c'",0), [1,3,5,(7,-1)])]))])

# play appegio of c:7 each at different tempo
>> main([Staff(melody([1,3,5,(7,-1)], [3,1,3,1], unit=8), 'piano')])

##### drum
>> main([Staff(
         melody(['sn', 'hh', 'hh', 'r', 'sn', 'hh'],
                [4,    3,    1,    2,   2,    1], unit=8),
         'drum')
   ])

'''
import itertools, re
from functools import partial
import numpy as np

name2chord = {
    'I': [1, 3, 5],
    'II': [2, 4, 6],
    'III': [3, 5, 7],
    'IV': [4, 6, 8],
    'V': [5, 7, 9],
    'V7': [5, 7, 9, 11],
    'VI': [6, 8, 10],
    'VIIdim': [7, 9, 11]
}

name2staff = {
    'piano': '\\new PianoStaff',
    'drum': '\drums'
}

class Staff:
    ''' staff is just a bunch of note with instrument info'''
    def __init__(self, ts, instrument='piano', clef='treble'):
        self.instrument = instrument
        self.ts = ts
        self.clef = clef

def main(staffs, tempo='4=140', time_signature='4/4', key='c \major',
         heading='simple chord', add_metronome=False,
         metronome_measures=10):
    '''
    staffs: some lines of music
    '''
    assert type(staffs[0]) is Staff, 'melody should be list of staffs'

    if add_metronome:
        staffs.append(Staff(['hh4'] * 4 * metronome_measures, 'drum'))

    body = "\score{\n << \n"
    for staff in staffs:
        body += "%s { \\clef %s \\tempo %s \\time %s %s \n"\
                % (name2staff[staff.instrument], staff.clef,
                   tempo, time_signature,
                   '\key %s' % key if staff.instrument != 'drum' else '')
        body += " ".join(staff.ts)
        body += "}\n"
    body += ">>\n \layout {} \midi{} }\n"

    title = """\\version "2.18.2"
    \header {
    title = "%s"
    composer = "Jiaxuan Wang"
    tagline = "Copyright: MIT license"
    }""" % heading

    print(title + body)

def binarize(n):
    '''convert base 10 number "n" to list of binary digits'''
    binary_repr = []
    while n != 0:
        n, digit = n // 2, n % 2
        binary_repr.append(digit)
    binary_repr = binary_repr[::-1]
    return binary_repr

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
    main([Staff([scale(i) for i in range(1, 8)])])
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
        '''degree can be a number, or a tuple with offset, or r for rest'''
        if type(degree) in [tuple, list]:
            degree, offset = degree
        elif type(degree) is int:
            offset = 0
        else:
            return degree # handles cases like 'r', 'hihat' etc.
        idx, span  = (degree - 1) % 7, (degree - 1) // 7
        return number2note(n + span * 12 + diffs[idx] + offset)

    return scale

################## degrees manipulation ############
def invert(degrees, root=1):
    '''invert a series of degrees where each degree could be a
    int or a tuple of int, treat root as the invariant'''
    res = []
    for d in degrees:
        if d == 'r':
            res.append(d)
        elif type(d) is int:
            res.append(root - (d-1))
        else:
            res.append([root - (d[0]-1), -d[1]])
    return res

################## add flavors #############
def add_rhythm(notes, rhythm=None, unit=16):
    '''
    if rhythm is None, each note takes unit time
    if rhythm are more than notes, notes are repeated
    
    notes: notes to add rhythm to
    unit: the smallest granularity
    rhythm: [2, 3] means a 2 units note followed by a 3 units note,
            which is short hand for [(1, 2), (1, 3)]
            where (1, 2) means 1 note taking 2 unit times.
            This notation helps write triplets, e.g.,
            (3, 2) means 3 notes taking 2 unit times
    output: list of notes with rhythm
    '''
    if len(notes) == 0: return []
    
    if rhythm is None:
        rhythm = [1] * len(notes)

    def simplify(duration, note, unit=16):
        '''
        make the single note have duration amount of time
        it tries to simplify the note written
        notes are tied together by ties
        '''
        known_units = [1, 2, 4, 8, 16, 32, 64]
        assert unit in known_units, "unit must in {}".format(known_units)

        # binary representation: so I can simplify to how many 1, 2, etc.
        # with unit as the smallest granularity
        # pad so that the first entry is a note of unit 1
        binary_repr = binarize(duration)
        n_digits = known_units.index(unit) + 1
        binary_repr = [0] * (n_digits - len(binary_repr)) + binary_repr

        # further simplify by collecting nearby repr
        # for idx in range(1, len(binary_repr)): # front to back
        for idx in range(len(binary_repr)-1, 0, -1): # back to front
            if binary_repr[idx-1] == 1 and binary_repr[idx] == 1:
                binary_repr[idx-1] += 1
                binary_repr[idx] = 0

        # add ties
        notes = ['{}{}'.format(note, unit) + ("." if count > 1 else "")\
                 for unit, count in zip(known_units, binary_repr)\
                 if count != 0]

        if note != 'r': # rest has no tie
            for i in range(len(notes)-1):
                notes[i] += '~'

        return ' '.join(notes)

    def rhythm_to_noteconsumer(rhythm):
        '''
        Given a rhythm list, return a note consumer

        a note consumer is a function
        input: list of note
        output: list of notes embellished by rhythm
        '''
        def consumer(notes):
            orig_notes = notes
            out = []
            for duration in rhythm:
                if type(duration) in [tuple, list]: # tuplet
                    n_to_eat, duration = duration
                else: # regular
                    n_to_eat = 1

                # append more notes when notes run out
                if len(notes) < n_to_eat:
                    notes = notes + orig_notes
                
                consumed = notes[:n_to_eat]
                notes = notes[n_to_eat:]

                if n_to_eat == 1: # regular
                    out.append(simplify(duration, consumed[0], unit=unit))
                else: # tuplet
                    out.extend(
                        ['\\tuplet %d/%d {' % (n_to_eat, duration)] +
                        ['{}{}'.format(note, unit) for note in consumed] +
                        ['}']
                    )

            return out

        return consumer

    return rhythm_to_noteconsumer(rhythm)(notes)

def add_chord_names(chords):
    '''
    given list of chord, output an environment with chord names added
    '''
    return ['<< \n'] + \
        ['\\new ChordNames {'] + chords + ['}'] +\
        ['{'] + chords + ['}'] +\
        ['\n>>']

################## improvisation  #################
def tweleve_bar_blues(scale=build_scale('c', 'ionian')):
    # https://www.youtube.com/watch?v=BjhkClSUdYM
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

    main([Staff(ts)], tempo='4=160')

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

    measures = 5
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
                             unit=8) for _ in range(measures)]
        upper = list(itertools.chain(*pieces))

    lines = [Staff(upper),
             Staff(bass * measures)]
    main(lines, tempo='4=100')

################## chord progressions #############
'''standard chord progressions
and chord progressions that I picked up over the years
'''
def random_functional_chords(scale, M=None, m=None):
    '''build common functional chord progressions
    M is the maximum degree to match
    m is minimum degree to match
    '''
    home = [['I'], ['I', 'III'], ['I', 'VI'], ['I', 'III', 'VI'], ['I', 'VI', 'III']]
    bridge = [['IV'], ['II'], ['IV', 'II'], ['II', 'IV']]
    outside = [['V7'], ['V'], ['VIIdim']]
    names = np.random.choice(home) + np.random.choice(bridge) + \
        outside[np.random.choice(len(outside))] + ['I']
    # build the chords
    chords_deg = [name2chord[name] for name in names]

    # simplify chords by matching max and min
    def match_max_min(degrees, M=None, m=None): # M is max, m is min
        if M is None or m is None: return degrees
        new_degrees = []
        for deg in degrees:
            if deg > M and (deg-M) % 7 > 1:
                deg = M + (deg-M) % 7 - 7
            elif deg < m and (m-deg) % 7 > 1:
                deg = m - (m-deg) % 7 + 7
            new_degrees.append(deg)
        if min(new_degrees) > m + 1:
           new_degrees.append(max(new_degrees) - 7)
        if max(new_degrees) < M - 1:
           new_degrees.append(min(new_degrees) + 7)
        return new_degrees

    matched_chords_deg = []
    for degrees in chords_deg:
        degrees = match_max_min(degrees, M, m)
        matched_chords_deg.append(degrees)
        M, m = max(degrees), min(degrees)
    return [chord(scale, i) for i in matched_chords_deg], names

def chord_progression0():
    play_chord_mode(['b:m', 'g', 'd', 'a'], heading="D maj vi IV I V")

def chord_progression1():
    play_chord_mode(['e', 'gis', "cis':m", "a"], heading="")

def licks_between_chords(chords):
    '''assume were written in chord mode: eg. ["c:7", "b:6^5"]'''
    # https://www.youtube.com/watch?v=LP8ivrZFV-c&list=PLuDm3ueOL12yMH5K7uuFRKshZnVoDztZO&index=5&t=102s;
    # step 1: root
    # step 2: scale over 3 strings (not necessarily from root); shared
    # step 3: phrasing, play with the scale, share the phrase
    # step 4: share rhymic pattern in 3, but change phrase
    # step 5: full improvisation
    mel = []
    for chord in chords:
        mel += chord_mode([chord])
        # add scale

    main([Staff(mel)])

############ drum machine: deprecated, should use melody ######
def drum_machine(rhythm, unit=8, instrument='hihat'):
    '''
    refer to an online drum machine for an implementation of this
    negative rhythm is interpreted as rest
    this is DEPRECATED,
    please use Staff(melody(['hh','r','sn'], [1,2,3]), 'drum') instead
    '''
    beat = list(map(lambda r: (["{}{}".format(instrument, unit)]\
                               + ["r{}".format(unit)] * (r-1))\
                    if r > 0 else ['r{}'.format(unit)] * (-r),
                    rhythm))
    beat = list(itertools.chain(*beat))
    return beat

################# variation helpers ################
def melody(degrees, rhythm=None, scale=build_scale("c'"), unit=4,
           degree_transform=lambda x: x,
           rhythm_transform=lambda x: x):
    '''
    a piece of music is composed of
    degrees, rhythm, scale, unit
    This function takes the piece and transforms it with rhythm_transform
    and degree_transform
    returns a timeseries, ts, playable by main
    '''
    ts = add_rhythm([scale(i) for i in degree_transform(degrees)],
                    rhythm_transform(rhythm), unit=unit)
    return ts

################# specific variations #############
def variation_idea0(degrees, rhythm, scale, unit, tempo):
    '''
    uses melody and performs certain predefined
    variation on a given piece
    '''
    mels = []
    # original melody
    mels.append(melody(degrees, rhythm, scale, unit))
    # build other variations
    ### inversion
    for degree_transform in [partial(invert, root=5)]:
        mels.append(melody(degrees, rhythm, scale, unit,
                                     degree_transform))
    ### change scale
    for s in [build_scale("bes'", 'aeolian'),
              build_scale("b'", 'aeolian'),
              build_scale("c''", 'aeolian')]:
        mels.append(melody(degrees, rhythm, s, unit))
    ### ending
    mels.append(add_rhythm(up_scale(s), unit=unit))
    mels.append(add_rhythm(down_scale(s), unit=unit))
    mels.append(
        add_rhythm([chord(s, [1, 3, 5]),
                    chord(s, [0, 2, 4, (6, -1)]),
                    chord(s, [1-7, 3-7, 5-7])],
                   unit=2),
    )

    # output sound
    lines = [Staff(list(itertools.chain(*mels)))]
    main(lines, tempo=tempo)

def practice0():
    '''
    daily practice routinue with common chord progression
    '''
    def pattern(scale, degrees, unit=8):
        # change the pattern below to create different excercises
        # rhythm = [3,1,3,1,3,1,1,1,1,1]
        # new_degrees = [degrees[i] for i in np.random.choice(3, len(rhythm))]
        # return add_rhythm([scale(d) for d in new_degrees],
        #                   rhythm, unit=unit)
        ### idea 1
        new_degrees = [degrees[i] for i in [0,1,2,1,2,0,1,2]]
        # new_degrees = [degrees[i] for i in [0,1,2,2,1,0]]
        return add_rhythm([scale(d) for d in new_degrees], unit=unit)

    cmaj = build_scale("c'", 0)
    mel0, mel1 = [], []
    n_measures = 0
    for i in range(2):
        chords, names = random_functional_chords(cmaj)
        last_chord = chords[-1]
        chords, names = chords[:-1], names[:-1]
        mel0.extend(list(itertools.chain(*[pattern(cmaj, name2chord[name])\
                                           for name in names])))

        mel1.extend(add_rhythm(chords, unit=1))
        n_measures += len(chords)

    mel0.append('r1')
    mel1.append(last_chord)
    mel1 = add_chord_names(mel1) # add chord names

    repeat = n_measures
    beat1 = drum_machine([-4,4]*repeat, unit=8, instrument='sn') + ['r1']
    beat2 = drum_machine([-4,-1,1,1,1]*repeat, unit=8, instrument='hh') + ['r1']
    main([Staff(mel0),
          Staff(mel1),
          Staff(beat1, 'drum'),
          Staff(beat2, 'drum')
    ],
         heading=", ".join(names),
         tempo='4=80')

######## finger picking patterns practice #########
def finger_picking0(add_beats=False):
    '''
    finger picking pattern practice 2 in epic fingerpicking patterns
    tutorial
    '''
    scale = build_scale("d'", 0)
    unit = 8
    tempo = '4=100'
    degrees = [
        *([1, 3+7] * 4),
        *([5-7, 2+7] * 4),
        *([6-7, 1+7] * 4),
        *([4-7, 4+7] * 4),
        *([1, 5+7] * 4),
        *([5, 7+7] * 4),
        *([6, 1+14] * 4),
        *([4, 6+7] * 4),
    ]
    rhythm = [1] * len(degrees)
    mel = melody(degrees, rhythm, scale, unit)

    # final chord
    mel += add_rhythm([chord(scale, [1, 5, 1+7, 2+7, 3+7])], unit=4)
    staffs = [Staff(mel)]

    # add some beat
    if add_beats:
        repeat = 8
        beat = melody(['sn', 'hh', 'sn', 'sn', 'sn', 'hh', 'sn'],
                      [4, 3, 1, 2, 2, 2, 2], unit=16)
        staffs.append(Staff(beat * repeat + ['r1'], 'drum'))

    main(staffs, tempo=tempo, key='d \major')

def finger_picking1(add_beats=False):
    '''
    finger picking pattern practice 3 in epic fingerpicking patterns
    tutorial, thumb, index, and middle
    '''
    scale = build_scale("e'", 0)
    unit = 8
    tempo = '4=100'
    degrees = [
        1, 1+7, 5,
        3, 1+7, 5,
        5, 1+7,

        1, 1+7, 5,
        3, 1+7, 5,
        5, 1+7,

        4, 1+7, 5,
        (6,-1), 1+7, 5,
        5, 1+7,

        4, 1+7, 5,
        (3,-1), 1+7, 5,
        (2,-1), 1+7,

        # 4, 6, 5,
        # 4, 3, 2, 1
    ]
    rhythm = [1] * len(degrees)
    mel = melody(degrees, rhythm, scale, unit)

    mel += add_rhythm([chord(scale, [1, 3, 5, 8])], unit=4)
    main([Staff(mel)], tempo=tempo, add_metronome=add_beats,
         metronome_measures=5)

################# drum patterns ##################
def rhythm1(degrees=None, repeat=2, instrument='piano', tempo="4=120"):
    '''
    blues rhythm
    '''
    rhythm = [
        2, 1, 1, 2,
        2, 2, 2
    ] * repeat
    if degrees is None:
        degrees = ['hh']
        instrument = 'drum'
    mel = melody(degrees, rhythm, unit=16)
    staff = Staff(mel, instrument)
    main([staff], time_signature="3/4", tempo=tempo)

################# my own pieces ##################
def motive0():
    '''
    as sad and detached motive
    '''
    scale = build_scale("c'", 0)
    unit = 8
    tempo = '4=80'
    degrees = [
        'r', 7, 7, 5, 3, 2, 3, 6,
        4, 3, 4, 3, 4, 6, 5
    ]
    rhythm = [
        8, 3, 1, 1, 1, 1, 1, 8,
        3, 1, 1, 1, 1, 1, 8
    ]
    degrees2 = [
        'r', 1, 1, 'r', 4, 4, 2, 6-7,
        6, 'r', 'r', 3, 1
    ]
    rhythm2 = [
        6, 2, 4, 4, 1, 2, 2, 3,
        4, 4, 1, 2, 5
    ]
    mel = melody(degrees, rhythm, scale, unit)
    mel2 = melody(degrees2, rhythm2, scale, unit)
    main([Staff(mel), Staff(mel2)], tempo=tempo)

################# specific pieces ################
def pagnini24(mode='aeolian'):
    scale = build_scale("a'", mode)
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
    return {'degrees': degrees, 'rhythm': rhythm, 'scale': scale,
            'unit': unit, 'tempo': tempo}

def shengmusong(mode=0):
    ##### this is for shengmusong
    scale = build_scale("c''", mode=mode)
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
    return {'degrees': degrees, 'rhythm': rhythm, 'scale': scale,
            'unit': unit, 'tempo': tempo}

def changtingwai(mode=0):
    #### this is a chinese folk song changtingwai gudaobian
    tempo = '4=100'
    scale = build_scale("c''", mode=mode)
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
    return {'degrees': degrees, 'rhythm': rhythm, 'scale': scale,
            'unit': unit, 'tempo': tempo}

def suoluohe(mode=0):
    #### meilide suoluohe
    tempo = '4=140'
    scale = build_scale("c''", mode=mode)
    unit = 4
    degrees = [
        5, 5, 5, 6, 3, 5,
        1, 2, 3, 2, 1, 3,
        5, 3, 5, 3+7, 2+7, 7, 5, 6,
        7, 3+7, 5, 4, 5, 3,
    ]
    rhythm = [
        1, 1, 1, 2, 1, 6,
        1, 1, 1, 2, 1, 6,
        2, 1, 2, 1, 2, 1, 2, 1,
        1, 1, 1, 2, 1, 6
    ]
    return {'degrees': degrees, 'rhythm': rhythm, 'scale': scale,
            'unit': unit, 'tempo': tempo}

def nice_chord_c():
    '''a piece from nice chord on variation of C with D/C'''
    mel = chord_mode(["c/g", "d:m/a", "c", "d:m/a", "c/g", "f,:6^5",
                      "e,:m6-^5", "f,:6^5", "c/g"],
                     [2, 1, 2, 1, 2, 1, 2, 1, 3], unit=4)
    drum = melody("c, g, r g, c, g, r g,".split(" ") * 2 + ["c,"],
                  [7, 1, 3, 1] * 4 + [12], unit=16)
    main([Staff(mel),
          Staff(drum, clef='bass')], time_signature="3/4")

def play_notes(notes, unit=1, heading=""):
    '''use simple rhythm to play out specified notes or chords'''
    main([Staff(add_rhythm(notes, unit=unit))], heading=heading)

def chord_mode(chords, rhythm=None, unit=1):
    '''given a sequence of chords play the chords out'''
    def idx_end_note(note_str):
        '''given note str, e.g, "c'':m" return 3'''
        # idx = 1
        # while len(note_str) > idx and note_str[idx] in ["'", ","] :
        #     idx += 1
        # return idx
        return re.search("[a-z][es|is]*['|,]*", note_str).end()

    def add_modifiers(chords, modifiers):
        # return [(c if m == '' else c + ':' + m)
        #         for c, m in zip(chords, modifiers)]
        return [(c + m)
                for c, m in zip(chords, modifiers)]

    chords, modifiers = list(zip(*map(lambda c:
                                      #c.split(':') if ':' in c else [c,''],
                                      (c[:idx_end_note(c)],
                                       c[idx_end_note(c):]),
                                      chords)))
    chord_music = ['\chordmode {'] +\
        add_modifiers(add_rhythm(chords, rhythm, unit=unit),
                      modifiers) + ['}']

    return add_chord_names(chord_music)

def play_chord_mode(chords, rhythm=None, unit=1, heading=""):
    chords = chord_mode(chords, rhythm, unit)
    main([Staff(chords)], heading=heading)

if __name__ == '__main__':
    # dorian_improv()

    ## existing songs
    # variation_idea0(**pagnini24())
    # variation_idea0(**shengmusong())
    # variation_idea0(**changtingwai(0))
    # variation_idea0(**suoluohe(0))
    # nice_chord_c()

    ### playground of ideas
    # cmaj = build_scale("c'", 0)
    # chords = [
    #     chord(cmaj, [2,4+7,6,8]),
    #     chord(cmaj, [5,7+7,9,11]),
    #     chord(cmaj, [1,3+14,5,7]),
    # ]
    # names = ['2', '5', '1']
    # play_notes(chords, heading=" ".join(names))

    ### easy way to play chords
    # play_chord_mode(['c', 'd:7', 'g'])

    ####### guitar daily practice
    # practice0()
    # finger_picking0(add_beats=True)
    # finger_picking1(add_beats=True)
    # chord_progression0()
    # chord_progression1()
    # licks_between_chords(['b:m', 'g', 'd', 'a'])

    # motive0()
    rhythm1([1, 2, 3, 2, 4, 0, 1], repeat=2)
    # rhythm1()
