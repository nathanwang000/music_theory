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

    def __repr__(self):
        return "{}".format(number2name[self.rep])

    def __add__(self, other_interval):
        assert type(other_interval) is Interval
        return Note(other_interval.rep + self.rep)

    def __sub__(self, other):
        assert type(other) is Note
        return Interval(self.rep - other.rep)
    

class Interval:
    '''
    distance measure for music
    '''
    def __init__(self, name):
        named_interval = ['m2', 'M2', 'm3', 'M3', 'P4', 'tritone',
                          'P5', 'm6', 'M6']
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

    def __sub__(self, other):
        assert type(other) is Interval, "interval can only substract interval"
        return Interval(self.rep - other.rep)
        
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
            notes = self.fill_pattern(pattern)
        else:
            if minor_mode == 'natural':
                pattern = [0, 2, 1, 2, 2, 1, 2, 2]
                notes = self.fill_pattern(pattern)
            elif minor_mode == 'harmonic':
                pattern = [0, 2, 1, 2, 2, 1, 3, 1]
                notes = self.fill_pattern(pattern)
            else: # melodic
                pattern = [0, 2, 1, 2, 2, 2, 2, 1, # up
                           -2, -2, -1, -2, -2, -1, -2]
                notes = self.fill_pattern(pattern)
                
        self.notes = notes

    def fill_pattern(self, pattern):
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
        
