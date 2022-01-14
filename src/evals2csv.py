import csv

all_evals = './all_evals.txt'

with open(all_evals, 'r') as f:
    lines = f.readlines()

num_rows_out = 0
for line in lines:
    if 'F-score' in line:
        num_rows_out += 1

split_lines = [line.strip().split('/')[1:] for line in lines]

results = [['class', 'alph', 'k', 'lang_id', 'direction',
            'netwrk_type', 'drop', 'size', 'test', 'fscore', 'accuracy', 'auc']]

for i in range(0,num_rows_out):
    model = split_lines[i][0]
    print(model)

    pieces = model.split('_')
    model_type = pieces[0]
    if model_type[0] == 'B':
        direc = 'Bidirectional'
    elif model_type[0] == 'U':
        direc = 'Unidirectional'
    #i_index = model_type.index('i')
    #arch = model_type[i_index+1:]
    ntwrk_type = pieces[1]
    drop = pieces[2]
    lang_class = pieces[3].split('.')[0]
    alph = pieces[3].split('.')[1]
    k = pieces[3].split('.')[2]
    lang_id = pieces[3].split('.')[3]
    set_size = pieces[4]
    test_name = split_lines[i][1].split('_')[0]

    for line in split_lines:
        if line[0] == model and 'F-score' in line[1] and test_name in line[1]:
            fscore = line[1].split()[1]
            print(model, fscore)
        elif line[0] == model and 'Accuracy' in line[1] and test_name in line[1]:
            accuracy = line[1].split()[1]
            print(model, accuracy)
        elif line[0] == model and 'AUC' in line[1] and test_name in line[1]:
            auc = line[1].split()[1]
            print(model, auc)

    
    new_result = [lang_class, alph, k, lang_id, direc, ntwrk_type,
                  drop, set_size, test_name, fscore, accuracy, auc]
    results.append(new_result)

with open('all_evals.csv', 'w', newline='\n') as f:
    writer = csv.writer(f)
    writer.writerows(results)
