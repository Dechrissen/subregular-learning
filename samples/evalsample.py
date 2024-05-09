import pynini
import sys
import matplotlib.pyplot as plt

with open('tags.txt', 'r') as f:
    langs = [lang.rstrip() for lang in f.readlines()]
#print('\n'.join(langs))

for lang in langs:
    alph = lang.split('.')[1]
    smpl_file = "samples/alph" + alph + "_sample.txt"
    fsa = pynini.Fst.read("src/fstlib/fst_format/" + lang + ".fst")
    valid_cnts = {} #tracks num of valid strs for each string length
    total_cnts = {} #tracks total num of strs for each string length
    with open(smpl_file, 'r') as file:
        for total, l in enumerate(file):
            pass
        file.seek(0)
        count = 0
        for line in file:
            count += 1
            sys.stdout.write("\rChecking well-formedness of line " + str(count) + \
                             " of " + str(total+1) + " for lang " + lang + ' ')
            sys.stdout.flush()
            test_str = line.rstrip()   # remove eol char
            if len(test_str) not in total_cnts:
                total_cnts[len(test_str)] = 1
                valid_cnts[len(test_str)] = 0
            else:
                total_cnts[len(test_str)] += 1
            compose = pynini.acceptor(test_str) @ fsa
            if compose.num_states() != 0:
                valid_cnts[len(test_str)] += 1
                #is_valid = True
            #else:
                #is_valid = False
            #print(test_str + ", " + str(is_valid))
        print('')

    fig, ax = plt.subplots()
    for i in [key for key in valid_cnts]:
        if i % 5 == 0:
            ax.axvline(i, linestyle='--', color='k', alpha=0.4, linewidth=0.5)
    for i in [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]:
        ax.axhline(i, linestyle='--', color='k', alpha=0.4, linewidth=0.5)
    ax.set_xlim(min(valid_cnts)-1, max(valid_cnts)+1)
    ax.set_ylim(-0.05, 1.05)
    valid_cnts_sort = {key:valid_cnts[key] for key in sorted(valid_cnts.keys())}
    total_cnts_sort = {key:total_cnts[key] for key in sorted(total_cnts.keys())}
    ax.plot(valid_cnts_sort.keys(),
            [val/tot for (val, tot) in zip(valid_cnts_sort.values(), total_cnts_sort.values())],
            'r', alpha=1)
    ax.set(xlabel='String Length', ylabel='Proportion Valid',
           title='Prop. Valid Strings for Lang ' + lang)
    fig.savefig('samples/plots/' + lang + '.png', dpi=500)
