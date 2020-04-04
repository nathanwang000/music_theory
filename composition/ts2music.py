import argparse
import logging
import numpy as np
from functools import partial
import yfinance as yf
import pandas as pd

parser = argparse.ArgumentParser(description="time series to music")
parser.add_argument('-t', type=float, nargs='+', default=[1,2,3,2,1])
args = parser.parse_args()

def normalize(ts, n_notes):
    '''
    return a np array of size of len(ts), quantized as n_notes
    round down
    '''
    return ((np.array(ts) - min(ts)) / (max(ts) - min(ts)) * n_notes).astype(int)

def number2note(n, n_notes):
    note, pitch = n % 7, n // 7
    notes = ['c', 'd', 'e', 'f', 'g', 'a', 'b']
    return "{}{}".format(notes[note], "'" * (pitch+1))

def transpose(ts, notes, degree):
    return [notes[(notes.index(note) - degree) % len(notes)] for note in ts]

def main(args, span=4, time_signature='3/4', tempo='4=210', time_unit=4,
         key='c', bass_degree=3, bass_ts=None):
    '''
    span: how many 7 notes span
    '''
    assert key == 'c', "only key of c supported for now"

    n_notes = span * 7
    n2note = partial(number2note, n_notes=n_notes)
    notes = list(map(n2note, np.arange(n_notes)))
    
    ts = normalize(args.t, n_notes-1) # -1 for note using the n_notes note b/c 0 based
    ts = list(map(n2note, ts))
    logging.warning(ts)

    if bass_ts is None:
        bass = transpose(ts, notes, bass_degree)
    else:
        bass = normalize(bass_ts, n_notes-1)
        bass = list(map(n2note, bass))
        logging.warning(bass)        

    staff = "\score{\n\\new PianoStaff << \n"
    staff += "  \\new Staff { \\clef treble \\tempo %s \\time %s " \
             % (tempo, time_signature) +\
             " ".join(map(lambda x: x + str(time_unit), ts)) + "}\n"
    staff += "  \\new Staff {"+" ".join(map(lambda x: x + str(time_unit),
                                                      bass)) + "}\n"  
    
    
    staff += ">>\n \layout {} \midi{} }\n"

    title = """\header {
    title = \"""" + " ".join(map(str, args.t)) + """\"
    composer = "Jiaxuan Wang"
    tagline = "Copyright: MIT license"
    }"""

    print(title + staff)
    
if __name__ == '__main__':
    ts = np.linspace(0, 4*np.pi, 40) 
    bass_ts = None
    
    def fib(length):
        ret = [1,1]
        while length > len(ret):
            ret.append(ret[-1] + ret[-2])
        return ret[:length]

    def decimal(n, length):
        ret = []
        while length > len(ret):
            ret.append(int(n) % 10)
            n *= 10
        return ret[:length]

    def stock(ticker, length, interval='1d'):
        prices = yf.download(ticker, interval=interval, progress=False)
        return np.array(prices['Close'])[-length:]
    
    args.t = np.sin(ts)
    # args.t = np.exp(ts)
    # args.t = decimal(np.pi, len(ts))
    # args.t = decimal(np.e, len(ts))
    # args.t = decimal(np.sqrt(2), len(ts))
    # args.t = stock('MSFT', len(ts), interval='1d')
    # args.t = stock('GOOGL', len(ts)) # variations F
    # bass_ts = stock('GOOGL', len(ts))

    # ideas to try: bass note try to use 12 bar blues or things of that sort
    main(args, span=2, bass_degree=5, bass_ts=bass_ts)
