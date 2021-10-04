"""
Performs one of three tasks:
    - writes language names to tags.txt for which an fst exists in src/fstlib/fst_format
      (supply no argument)
    - writes language names to tags.txt for which data generation is not compelete
      (supply argument --datagen)
    - writes language names to tags.txt for which data generation is complete
      (supply argument --train)
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

with open('tags.txt', 'w') as f:
    lang_names = sorted([filename[:-4] for filename in os.listdir("src/fstlib/fst_format/")])
    out = [l + '\n' for l in lang_names]
    f.writelines(out)
cwd = os.getcwd()
with open('tags.txt', 'r+') as f:
    langs = [l[:-1] for l in f.readlines()]
    data1   = [s.split('_')[0] for s in os.listdir(os.path.join(cwd, 'data_gen/1k'))]
    data10  = [s.split('_')[0] for s in os.listdir(os.path.join(cwd, 'data_gen/10k'))]
    data100 = [s.split('_')[0] for s in os.listdir(os.path.join(cwd, 'data_gen/100k'))]
    langs_to_write = []
    for l in langs:
        if datagen and (data1.count(l) != 6 or data10.count(l) != 6 or data100.count(l) != 6):
                langs_to_write.append(l)
        elif train and data1.count(l) == 6 and data10.count(l) == 6 and data100.count(l) == 6:
                langs_to_write.append(l)
    out = [l + '\n' for l in langs_to_write]
    f.seek(0)
    f.writelines(out)
    f.truncate()
