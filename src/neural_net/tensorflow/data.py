def save_vocab(fname, vocabulary):
    with open(fname, 'w') as f:
        for key in vocabulary:
            f.write(key + '\t' + str(vocabulary[key]) + '\n')

def load_vocab(fname):
    vocabulary = {}
    with open(fname, 'r') as f:
        for line in f.readlines():
            word, index = line.strip().split('\t')
            vocabulary[word] = int(index)
    return vocabulary

def parse_dataset(fname, vocabulary={'pad': 0}):
    x_items = []
    y_items = []
    with open(fname, 'r') as f:
        for line in f.readlines():
            x, y = line.strip().split('\t')
            x_indices = []
            for c in x:
                if c not in vocabulary:
                    vocabulary[c] = len(vocabulary)
                x_indices.append(vocabulary[c])
            y_numeric = [1.0, 0.0] if y == "TRUE" else [0.0, 1.0]
            x_items.append(x_indices)
            y_items.append(y_numeric)
    return vocabulary, x_items, y_items

def pad_data(dataset, vocabulary):
    max_length = max([len(item) for item in dataset])
    padded_dataset = []
    for item in dataset:
        padded_dataset.append(item + [vocabulary['pad']]*(max_length - len(item)))
    return padded_dataset
