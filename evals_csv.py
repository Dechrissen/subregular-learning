import csv

all_evals = './all_evals_lstm.txt'

with open(all_evals, 'r') as f:
    lines = f.readlines()
    
split_lines = [line.strip().split('/')[1:] for line in lines]

results = []

for line in split_lines:
    i=0
    pieces = line[i].split('_')
    model_type = pieces[0]
    if model_type[0] == 'B':
        direc = 'Bidirectional'
    elif model_type[0] == 'U':
        direc = 'Unidirectional'
    i_index = model_type.index('i')
    arch = model_type[i_index+1:]
    do = pieces[1]
    lang = pieces[2]
    lang_class = pieces[2].split('.')[0]
    set_size = pieces[3]
   
    i=1
    test_name = line[i].split('_')[0]
    score_type = line[i].split(':')[1]
    score = float(line[i].split(' ')[-1])
    new_result = [direc, arch, do, lang_class, lang, set_size, test_name, score_type, score]
    results.append(new_result)

with open('all_evals_lstm.csv', 'w', newline='\n') as f:
    writer = csv.writer(f)
    writer.writerows(results)
