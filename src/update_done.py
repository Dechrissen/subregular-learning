"""
This script writes to src/langs_done.txt the languages for which neural
networks have been trained and evaluated.
"""

import os

rnn_types = ['gru', 'lstm', 'simple']
sizes = ['1k', '10k', '100k']

langs = set([model.split('_')[3] for model in os.listdir('models')])
print(langs)

with open('src/langs_done.txt', 'w') as f:
    for lang in langs:
        complete = True
        for model in ['_'.join(['Uni',rnn,'NoDrop',lang,size])
                      for rnn in rnn_types for size in sizes]:
            moddir = 'models/' + model
            if os.path.exists(moddir):
                complete = False if 'Test1_roc.png' not in os.listdir(moddir) else True
            else:
                complete = False
            if not complete:
                break
        if complete:
            f.write(lang + '\n')
        else:
            continue
