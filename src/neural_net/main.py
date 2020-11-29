import copy
import numpy as np
import glob
import os
import torch
import torch.optim as optim
import torch.nn as nn
from model import Predictor
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

language_class_name = "Data/sigma4/LT2"
data ={'tr':{}, 'dev':{}, 'te1':{}, 'te2':{}, 'te3':{}}
label ={'tr':{}, 'dev':{}, 'te1':{}, 'te2':{}, 'te3':{}}
pat_name = {'tr':'Train','dev':'Dev', 'te1':'Test1', 'te2':'Test2', 'te3':'Test3'}
datasets = glob.glob(language_class_name+'/*')
print(datasets)

np.random.seed(0)
torch.manual_seed(0)

for dataset_name in datasets:
    for key in pat_name.keys():
        for filename in glob.glob(dataset_name+'/*'):
            if os.path.basename(filename).find(pat_name[key]) >=0:
                print('"%s"'%filename, "is read as the", key, "set.")
                pd = np.array([ l.strip().split() for l in open(filename)])
                data[key][dataset_name] = pd[:,0]
                label[key][dataset_name] = np.array(
                    [1 if temp_label == 'TRUE' else 0 for temp_label in pd[:,1]])


def get_dataset(dataset_name):
    global data, label, pat_name
    _d_tr = data['tr'][dataset_name]
    Sigma = sorted(set([a for l in _d_tr for a in l] ))
    to_int = { a: i+1 for i,a in enumerate(Sigma) }
    _d_ret = {}
    _l_ret = {}
    for key in pat_name.keys():
        _d = data[key][dataset_name]
        _d = [ np.int32([to_int[a] for a in l]) for l in _d ]
        _d = np.array(_d)
        _l = np.int32(label[key][dataset_name])
        _d_ret[key] = _d
        _l_ret[key] = _l
    return Sigma, _d_ret, _l_ret


def get_shuffled_ids(data, bsize):
    sorted_ids = np.argsort([len(l)+np.random.uniform(-1.0,1.0) for l in data])
    blocked_sorted_ids = [sorted_ids[i:i+bsize] for i in range(0, len(data), bsize)]
    np.random.shuffle(blocked_sorted_ids)
    return blocked_sorted_ids

Sigma, _data, _label = get_dataset('Data/sigma4/LT2/100k')


def make_batch(data, label, blocked_sorted_ids):
    batch_input = data[blocked_sorted_ids]
    batch_label = label[blocked_sorted_ids]
    sorted_ids = np.argsort([-len(l) for l in batch_input])
    batch_input = batch_input[sorted_ids]
    batch_len = [len(l) for l in batch_input]
    batch_label = batch_label[sorted_ids]
    max_length = max([len(l) for l in batch_input])
    batch_input = [np.append(l, [0] * (max_length - len(l))) for l in batch_input]
    batch_input = torch.tensor(batch_input, dtype=torch.long)
    batch_label = torch.tensor(batch_label, dtype=torch.long)
    return batch_input, batch_len, batch_label


def eval(model, data, label):
    with torch.no_grad():
        id_list = [i for i in range(0,data.shape[0])]
        b_i, b_len, b_label = make_batch(data, label, id_list)
        h0 = torch.zeros(1, data.shape[0], lstm_dim)
        c0 = torch.zeros(1, data.shape[0], lstm_dim)
        out = model(b_i, b_len, h0, c0)
        _, indx = torch.topk(out,1)
        indx = indx.numpy()
        correct = 0
        for e1,e2 in zip(indx, b_label.numpy()):
            if e1[0] == e2:
                correct += 1
        acc = 1.0*correct/data.shape[0]
        return acc


voc_size = len(Sigma)
lstm_dim = 10
batch_size = 128
num_of_layers = 1
num_of_directions = 1
num_epochs = 300
clip = 1.0

predictor = Predictor(voc_size,lstm_dim)
optimizer = optim.Adam(predictor.parameters())
criterion = nn.NLLLoss()


best_dev_acc = 0.0
best_model_wts = copy.deepcopy(predictor.state_dict())
best_test1_acc = 0.0
best_test2_acc = 0.0
best_test3_acc = 0.0
best_epoch_num = 0

total_epoch_num = 0
all_losses = []
all_acc_1 = []
all_acc_2 = []
all_acc_3 = []

for epoch in range(1,num_epochs):
    total_epoch_num += 1
    shuffled_id_blocks = get_shuffled_ids(_data['tr'], batch_size)
    running_loss = 0.0
    predictor.train()
    for id_block in shuffled_id_blocks:
        predictor.zero_grad()

        h0 = torch.zeros(num_of_layers * num_of_directions, id_block.shape[0], lstm_dim)
        c0 = torch.zeros(num_of_layers * num_of_directions, id_block.shape[0], lstm_dim)

        batch_input, batch_len, batch_label = make_batch(_data['tr'], _label['tr'], id_block)
        output = predictor(batch_input, batch_len, h0, c0)
        loss = criterion(output, batch_label)
        running_loss += loss.item()*batch_input.size(0)
        loss.backward()
        _ = torch.nn.utils.clip_grad_norm_(predictor.parameters(), clip)
        optimizer.step()
    running_loss = running_loss/_data['tr'].shape[0]
    predictor.eval()
    dev_acc = eval(predictor, _data['dev'], _label['dev'])
    acc_1 = eval(predictor, _data['te1'], _label['te1'])
    acc_2 = eval(predictor, _data['te2'], _label['te2'])
    acc_3 = eval(predictor, _data['te3'], _label['te3'])
    if dev_acc > best_dev_acc:
        best_dev_acc = dev_acc
        best_model_wts = copy.deepcopy(predictor.state_dict())
        best_test1_acc = acc_1
        best_test2_acc = acc_2
        best_test3_acc = acc_3
        best_epoch_num = epoch
    print('epoc', epoch, '\t', running_loss, '\t', dev_acc, '\t', acc_1, '\t', acc_2, '\t', acc_3)
    all_losses.append(running_loss)
    all_acc_1.append(acc_1)
    all_acc_2.append(acc_2)
    all_acc_3.append(acc_3)
    if best_dev_acc > 0.99999:
        break
    if epoch - best_epoch_num > 50:
        break


torch.save(best_model_wts, 'best_model.pt')

print('best dev acc', dev_acc)
print('best test1 acc', best_test1_acc)
print('best test2 acc', best_test2_acc)
print('best test3 acc', best_test3_acc)


plt.figure()
epoch_list = [i for i in range(1,total_epoch_num + 1)]
plt.plot(epoch_list, all_losses, 'r', label = 'train')
plt.plot(epoch_list, all_acc_1, 'y', label = 'test1')
plt.plot(epoch_list, all_acc_2, 'g', label = 'test2')
plt.plot(epoch_list, all_acc_3, 'b', label = 'test3')
plt.legend()
plt.show()
