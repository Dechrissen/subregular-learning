"""
Performs one of three tasks:
    - writes language names to tags.txt for which an fst exists in src/fstlib/fst_format
      (supply neither --datagen nor --train)
    - writes language names to tags.txt for which data generation is not compelete
      (supply --datagen)
    - writes language names to tags.txt for which data generation is complete
      (supply --train)
The argument --avoid can be used to specify the path of a text file whose lines
indicate language names that should not be include in the output of this script.
"""

import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--datagen', dest='datagen', action='store_true')
parser.add_argument('--train', dest='train', action='store_true')
parser.add_argument('--avoid', type=str)
parser.set_defaults(datagen=False, train=False, avoid=None)
args = parser.parse_args()
dtgen = args.datagen
train = args.train
avoid = args.avoid

avoid = open(avoid, 'r').readlines() if avoid is not None else []
avoid = [l[:-1] for l in avoid]

lang_names = sorted([filename[:-4] for filename in os.listdir("src/fstlib/fst_format/")])
file_suffixes = ['Dev','Test1','Test2','Test3','Test4','Training']
sizes = {'1k':10**3, '10k':10**4, '100k':10**5}

if not (dtgen or train):
    with open('tags.txt', 'w') as f:
        out = [l + '\n' for l in lang_names if l not in avoid]
        f.writelines(out)
else:
    cwd = os.getcwd()
    with open('/dev/stdout', 'w') as f:
        langs_to_write = []
        for lang in lang_names:
            inc = False
            for suffix in file_suffixes:
                for size in sizes:
                    fname = 'data_gen/' + size + '/' + lang + '_' + suffix + '.txt'
                    if not os.path.exists(fname):
                        inc = True
                        break
                    nlines = len(open(fname, 'r').readlines())
                    if nlines != sizes[size]:
                        inc = True
                        break
                if inc:
                    break
            if (dtgen     and inc and lang not in avoid) or \
               (train and not inc and lang not in avoid):
                f.write(lang + '\n')
