import pynini as pynini
import sys

with open('tags.txt', 'r') as f:
    langs = [lang.rstrip() for lang in f.readlines()]
#print('\n'.join(langs))

fractions = {}
for lang in langs:
    print("Working on lang " + lang)
    alph = lang.split('.')[1]
    smpl_file = "samples/alph" + alph + "_sample.txt"
    fsa = pynini.Fst.read("src/fstlib/fst_format/" + lang + ".fst")
    with open(smpl_file, 'r') as file:
        count = 0
        valid = 0
        for line in file:
            count += 1
            test_str = line.rstrip()   # remove eol char
            compose = pynini.acceptor(test_str) @ fsa
            if compose.num_states() != 0:
                valid += 1
                #is_valid = True
            #else:
                #is_valid = False
            #print(test_str + ", " + str(is_valid))
        prop_valid = valid/count
        fractions[lang] = prop_valid

with open("samples/smpl_results.txt", 'w') as f:
    f.write('lang,proportion_valid\n')
    for lang in langs:
        f.write(lang + ',' + str(round(fractions[lang], 4)) + '\n')
