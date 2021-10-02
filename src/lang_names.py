"""
Performs one of two tasks:
    - writes language names to tags.txt for which an fst exists in src/fstlib/fst_format
      (supply argument --allfst)
    - writes language names to tags.txt for which data generation is not compelete
      (supply argument --datagen)
"""

import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--allfst', dest='allfst', action='store_true')
parser.add_argument('--datagen', dest='datagen', action='store_true')
parser.set_defaults(allfst=False, datagen=False)
args = parser.parse_args()
allfst = args.allfst
datagen = args.datagen

if allfst:
    with open('tags.txt', 'w') as f:
        lang_names = sorted([filename[:-4] for filename in os.listdir("src/fstlib/fst_format/")])
        f.write('\n'.join(lang_names))
        f.write('\n')
elif datagen:
    cwd = os.getcwd()
    with open('tags.txt', 'r+') as f:
        langs = [l[:-1] for l in f.readlines()]
        data1   = [s.split('_')[0] for s in os.listdir(os.path.join(cwd, 'data_gen/1k'))]
        data10  = [s.split('_')[0] for s in os.listdir(os.path.join(cwd, 'data_gen/10k'))]
        data100 = [s.split('_')[0] for s in os.listdir(os.path.join(cwd, 'data_gen/100k'))]
        langs_not_done = []
        for l in langs:
            if data1.count(l) != 4 or data10.count(l) != 4 or data100.count(l) != 4:
                langs_not_done.append(l)
        out = [l + '\n' for l in langs_not_done]
        f.seek(0)
        f.writelines(out)
        f.truncate()
else:
    Warning('No argument supplied.')
