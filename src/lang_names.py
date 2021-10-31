"""
Performs one of three tasks:
    - writes language names to tags.txt for which an fst exists in src/fstlib/fst_format
      (supply no argument)
    - writes language names to tags.txt for which data generation is not compelete
      (supply --datagen)
    - writes language names to tags.txt for which data generation is complete
      (supply --train)
"""

import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--datagen', dest='datagen', action='store_true')
parser.add_argument('--train', dest='train', action='store_true')
parser.set_defaults(datagen=False, train=False)
args = parser.parse_args()
datagen = args.datagen
train = args.train

lang_names = sorted([filename[:-4] for filename in os.listdir("src/fstlib/fst_format/")])
file_suffixes = ['Dev','Test1','Test2','Test3','Test4','Training']
sizes = {'1k':10**3, '10k':10**4, '100k':10**5}

if not (datagen or train):
    with open('tags.txt', 'w') as f:
        out = [l + '\n' for l in lang_names]
        f.writelines(out)
else:
    cwd = os.getcwd()
    with open('tags.txt', 'r+') as f:
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
            if datagen and inc:
                langs_to_write += [lang]
            elif train and not inc:
                langs_to_write += [lang]
        out = [l + '\n' for l in langs_to_write]
        f.seek(0)
        f.writelines(out)
        f.truncate()
