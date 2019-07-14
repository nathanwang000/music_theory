from lib.notes import Note, Interval, Scale, NOTES
import numpy as np

# note = Note('A')
# print(Scale(note, major=False, minor_mode='harmonic'))

def random_scale(root_notes=NOTES, majors=[True, False],
                 minor_modes=['natural', 'harmonic', 'melodic']):
    root_note = np.random.choice(root_notes)
    major = np.random.choice(majors)
    minor_mode = np.random.choice(minor_modes)
    return Scale(root_note, major=major, minor_mode=minor_mode)

print(random_scale())
print(Note('G') - Note('C'))
