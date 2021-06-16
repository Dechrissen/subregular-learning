import pynini as pynini
import sys

fsa = pynini.Fst.read("src/fstlib/fst_format/SL.4.2.0.fst")

for line in sys.stdin:
    test_str = line.rstrip()   # have to remove the end of line character (so remove trailing whitespace) 
    compose = pynini.acceptor(test_str) @ fsa
    if compose.num_states() == 0:
        is_valid = False
    else:
        is_valid = True
    print(test_str + ", " + str(is_valid))
    
