\version "2.18.2" % 3 4 5 3
\score {

       \relative c' {
         <<
           \new Staff {
	       \clef "treble"
               \time 4/4
               \key aes \major
	       \tempo 4=120
	       
               r8 aes c f' ees4. ees8 | c4. des8 f,4 ees |
               r4 ees8 ees c'4. bes16 c | bes4 aes r2 \bar "|."
	       }
	   \new Staff {
               \key aes \major
	       
	       <aes, c ees>2 <g bes ees> | <aes c ees> <bes des f> | % 1512 or 1514
	       <aes c ees> <aes c ees> | <bes des g>4 <aes c ees> % 1171
	       
	       }
	 >>
	 }
       \layout {}
       \midi {}
}




