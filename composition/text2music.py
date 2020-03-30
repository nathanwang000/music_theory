import argparse

parser = argparse.ArgumentParser(description="txt2score")
parser.add_argument('-t', type=str, default="I love you, babe")
args = parser.parse_args()

char2notes = { 
    'a':("<c e g b>4 ", "c''32 c'' g' g' e' e' c' c' "),
    'b':("<d f a c'>4 ", "d'32 d' e' e' f' f' d' d' "),
    'c':("<e g b d'> ", r"g' \trill "),
    'd':("e2 ", "e'4 a' "),
    'e':("<c g>2 ", "a'4 <a' c'> "),
    'f':("a2 ", "<g' a'>4 c'' "),
    'g':("a2 ", "<g' a'>4 a' "),
    'h':("r4 g ", " r4 g' "),
    'i':("<c e>2 ", "d'4 g' "),
    'j':("a4 a ", "g'4 g' "),
    'k':("a2 ", "<g' a'>4 g' "),
    'l':("e4 g ", "a'4 a' "),
    'm':("c4 e ", "a'4 g' "),
    'n':("e4 c ", "a'4 g' "),
    'o':("<c a g>2  ", "a'2 "),
    'p':("a2 ", "e'4 <e' g'> "),
    'q':("a2 ", "a'4 a' "),
    'r':("g4 e ", "a'4 a' "),
    's':("a2 ", "g'4 a' "),
    't':("g2 ", "e'4 c' "),
    'u':("<c e g>2  ", "<a' g'>2"),
    'v':("e4 e ", "a'4 c' "),
    'w':("e4 a ", "a'4 c' "),
    'x':("r4 <c d> ", "g' a' "),
    'y':("<c g>2  ", "<a' g'>2"),
    'z':("<e a>2 ", "g'4 a' "),
    '\n':("r1 r1 ", "r1 r1 "),
    ',':("r2 ", "r2"),
    '.':("<c e a>2 ", "<a c' e'>2"),
    ' ':("<a c e g>", "r2 "),    
}

txt = args.t
upper_staff = ""
lower_staff = "" 
for i in txt.lower():
    (l,u) = char2notes[i]
    upper_staff += u + " "
    lower_staff += l + " "

staff = "\score{\n\\new PianoStaff << \n"
staff += "  \\new Staff {" + upper_staff + "}\n"  
staff += "  \\new Staff { \clef bass " + lower_staff + "}\n"  
staff += ">>\n \layout {} \midi{} }\n"

title = """\header {
  title = \"""" + args.t + """\"
  composer = "Jiaxuan Wang"
  tagline = "Copyright: MIT license"
}"""

print(title + staff)
