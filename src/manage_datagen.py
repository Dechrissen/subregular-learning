#  no arg    : report languages for which datagen is not complete
#  --repall  : for all languages in fst_format, report how much of
#              datagen is complete
#  --rmlangs : remove data files of langs that are not complete

import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('--repall', dest='repall', action='store_true')
parser.add_argument('--rmlangs', dest='rmlangs', action='store_true')
parser.set_defaults(repall=False, rmlangs=False)
args = parser.parse_args()
repall = args.repall
rmlangs = args.rmlangs

lang_names = sorted([filename[:-4] for filename in os.listdir("src/fstlib/fst_format/")])
file_suffixes = ['Dev','Test1','Test2','Test3','Test4','Training']
sizes = {'1k':10**3, '10k':10**4, '100k':10**5}

print('LANG' + 20*' ' + '\t'.join(file_suffixes))

for lang in lang_names:
    ind = {suf:'' for suf in file_suffixes}
    for suffix in file_suffixes:
        for size in sizes:
            fname = 'data_gen/' + size + '/' + lang + '_' + suffix + '.txt'
            if not os.path.exists(fname):
                ind[suffix] += '0'
                continue
            nlines = len(open(fname, 'r').readlines())
            ind[suffix] += '1' if nlines == sizes[size] else '0'
    if repall or any([ind[suf] != '111' for suf in file_suffixes]):
        print(lang + (24-len(lang))*' ' + '\t'.join([ind[suf] for suf in file_suffixes]))
    if rmlangs and any([ind[suf] != '111' for suf in file_suffixes]):
        fnames = ['data_gen/' + size + '/' + lang + '_' + suffix + '.txt' \
                  for size in sizes for suffix in file_suffixes]
        for f in fnames:
            try:
                os.remove(f)
            except:
                continue
