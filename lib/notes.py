name2number = {
    'C': 0, 'Db': 1, 'C#': 1, 'D': 2, 'Eb': 3, 'D#': 3, 'E': 4, 'F': 5,
    'Gb': 6, 'F#': 6, 'G': 7, 'Ab': 8, 'G#': 8, 'A': 9, 'Bb': 10, 'A#': 10, 'B': 11
}
number2name = dict((val, n) for n, val in name2number.items())

NOTES = list(number2name.values())

class Note:

    def __init__(self, name):
        if type(name) == int:
            self.rep = name % 12
        else:
            allowed = 'ABCDEFG'
            assert name[0] in allowed, 'Not valid name, need in {}'.format(allowed)
            number_rep = name2number[name[0]]
            if len(name) > 1:
                for i in range(1, len(name)):
                    assert name[i] in '#b', "# or b needed"
                    if name[i] == '#':
                        number_rep += 1
                    else:
                        number_rep -= 1
            self.rep = number_rep % 12 # todo: think about whether wrap around

        self.name = number2name[self.rep]

    def __repr__(self):
        return self.name

    def __add__(self, other_interval):
        assert type(other_interval) is Interval
        return Note(other_interval.rep + self.rep)

    def __sub__(self, other):
        assert type(other) is Note
        # todo: think about whether wrap around
        return Interval((self.rep - other.rep) % 12) 

class Interval:
    '''
    distance measure for music
    
    eg. Interval('m2') == Interval(1) == 1 == 'm2'
    '''
    def __init__(self, name):
        named_interval = ['m2', 'M2', 'm3', 'M3', 'P4', 'tritone',
                          'P5', 'm6', 'M6', 'm7', 'M7']
        self.name2rep = lambda x: 1 + named_interval.index(x)
        self.rep2name = lambda n: str(n) if (n<=0 or n>=12) else named_interval[n-1]
        
        if type(name) == int:
            number_rep = name
        else:
            assert name in named_interval,\
                "not valide name, need in {}".format(named_interval)
            number_rep = self.name2rep(name)

        self.rep = number_rep
        self.name = name
        
    def __repr__(self):
        return self.rep2name(self.rep)
    
    def __add__(self, other):
        if type(other) == Interval:
            return Interval(other.rep + self.rep)
        elif type(other) == Note:
            return Note(other.rep + self.rep)
        else:
            raise Error("not implemented")

    def __eq__(self, other):
        if type(other) != Interval:
            other = Interval(other)
        return self.rep == other.rep
        
class Scale:

    def __init__(self, root_note, major=True, minor_mode='natural'):

        '''
        minor mode:
        natural: just plain
        harmonic: #7
        melodic: #6 and #7 up, down is natural
        '''

        assert minor_mode in ['harmonic', 'melodic', 'natural'],\
            "minor mode must be in ['harmonic', 'melodic', 'natural']"

        if type(root_note) is not Note:
            root_note = Note(root_note)
        self.root_note = root_note

        self.major = major
        self.minor_mode = minor_mode

        if self.major:
            pattern = [0, 2, 2, 1, 2, 2, 2, 1]
            notes = self.fill_pattern_(pattern)
        else:
            if minor_mode == 'natural':
                pattern = [0, 2, 1, 2, 2, 1, 2, 2]
                notes = self.fill_pattern_(pattern)
            elif minor_mode == 'harmonic':
                pattern = [0, 2, 1, 2, 2, 1, 3, 1]
                notes = self.fill_pattern_(pattern)
            else: # melodic
                pattern = [0, 2, 1, 2, 2, 2, 2, 1, # up
                           -2, -2, -1, -2, -2, -1, -2]
                notes = self.fill_pattern_(pattern)
                
        self.notes = notes

    def fill_pattern_(self, pattern):
        notes = []
        cumsum = 0
        for p in pattern:
            cumsum += p
            notes.append(self.root_note + Interval(cumsum))
        return notes

    def __repr__(self):
        res = ""
        if self.major: res += 'major: '
        else: res += '{} minor: '.format(self.minor_mode)
        return res + ','.join(map(str, self.notes))

    def chord(self, chord_number):
        assert chord_number < 8 and chord_number > 0, "chord number in [1,7]"
        pattern = [0, 2, 4] 
        pattern = map(lambda x: (x + chord_number - 1) % 7, pattern)
        notes = [self.notes[i] for i in pattern]
        return Chord(notes)

class Chord:
    '''
    chords are just more than 3 notes together
    assume no inversion applied (sorted)
    
    current modes support:
    M: major (1, 3, 5), occur in 1 4 5 major scale or 3 6 7 minor scale
    m: minor (1, 3b, 5), 
    o: diminished (1, 3b, 5b)
    +: augmented (1, 3, 5#)
    '''

    def __init__(self, notes):
        assert len(notes) >= 3, "chord need 3 or more notes"
        self.notes = []
        for note in notes:
            if type(note) != Note:
                note = Note(note)
            self.notes.append(note)

        # determine chord type
        self.mode = ""        
        notes = self.notes
        if notes[1] - notes[0] == 'M3': # M3
            if notes[2] - notes[0] == 'P5': # P5
                self.mode = 'M' # major
            elif notes[2] - notes[0] == 'm6':
                self.mode = '+' # augmented
        elif notes[1] - notes[0] == 'm3': # m3
            if notes[2] - notes[0] == 'P5': # P5
                self.mode = 'm' # minor
            elif notes[2] - notes[0] == 'tritone': # tritone
                self.mode = 'o' # diminished
        elif notes[1] - notes[0] == 'P4': # P4
            if notes[2] - notes[0] == 'P5': # P5
                self.mode = 'sus4' # sus4 cord
        elif notes[1] - notes[0] == 'M2': # M2
            if notes[2] - notes[0] == 'P5': # P5
                self.mode = 'sus2' # sus2 cord

    def __repr__(self):
        res = self.mode
        return res + self.notes.__repr__()
            

    
