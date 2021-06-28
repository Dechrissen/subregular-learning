# Writes all languages in fst_format to tags.txt for convenience

import os

with open('tags.txt', 'w') as f:
    lang_names = sorted([filename[:-4] for filename in os.listdir("src/fstlib/fst_format/")])
    f.write('\n'.join(lang_names))
    f.write('\n')
