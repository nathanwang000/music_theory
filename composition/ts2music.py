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
    print(ts)
    return ((np.array(ts) - min(ts)) / (max(ts) - min(ts)) * n_notes).astype(int)

def number2note(n, n_notes):
    note, pitch = n % 7, n // 7
    notes = ['c', 'd', 'e', 'f', 'g', 'a', 'b']
    return "{}{}".format(notes[note], "'" * pitch)

def transpose(ts, notes, degree):
    return [notes[(notes.index(note) - degree) % len(notes)] for note in ts]

def main(args, span=4, time_signature=32, key='c', bass_degree=3):
    '''
    span: how many 7 notes span
    '''
    assert key == 'c', "only key of c supported for now"

    n_notes = span * 7
    n2note = partial(number2note, n_notes=n_notes)
    notes = list(map(n2note, np.arange(n_notes)))
    print(notes)
    
    ts = normalize(args.t, n_notes-1) # -1 for note using the n_notes note b/c 0 based
    ts = list(map(n2note, ts))
    logging.warning(ts)
    bass = transpose(ts, notes, bass_degree)

    staff = "\score{\n\\new PianoStaff << \n"
    staff += "  \\new Staff {" + " ".join(map(lambda x: x + str(time_signature),
                                              ts)) + "}\n"
    staff += "  \\new Staff {\clef bass "+" ".join(map(lambda x: x + str(time_signature),
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

    def stock(ticker, length):
        prices = yf.download(ticker)
        return np.array(prices['Close'])[-length:]
    
    # args.t = np.sin(ts)
    # args.t = np.exp(ts)
    # args.t = decimal(np.pi, len(ts))
    # args.t = decimal(np.e, len(ts))
    # args.t = decimal(np.sqrt(2), len(ts))
    args.t = stock('AAPL', len(ts))
    main(args, bass_degree=5)
