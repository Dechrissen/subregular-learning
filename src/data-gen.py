# For an input language name, this script generates a training
# set, dev set, and four test sets, for each size Large, Mid,
# Small where Small ⊂ Mid ⊂ Large.

import pynini
import argparse
import random
import pathlib
import os

################
# Helper Functions
################

def A(s, token_type='utf8'):
    # the name of this function varies between pynini versions
    if hasattr(pynini, 'accep'):
        return pynini.accep(s, token_type=token_type)
    return pynini.acceptor(s, token_type=token_type)

def T(upper, lower, token_type='utf8'):
    return pynini.cross(A(upper, token_type=token_type),
                        A(lower, token_type=token_type))

# FUNCTIONS that take an fsa and return its alphabet, sigma
# and sigmastar, respectively

def sigma(fsa):
    syms = fsa.input_symbols()
    one_letter = [A(x[1],token_type=syms) for x in syms][1:]
    s = pynini.union(*one_letter)
    s.set_input_symbols(fsa.input_symbols())
    s.set_output_symbols(fsa.output_symbols())
    return s.optimize()

def sigmastar(fsa):
    return (sigma(fsa).star).optimize()


def fill_bucket(fsa, length, n):
    isyms = fsa.input_symbols()
    osyms = fsa.output_symbols()
    a=pynini.intersect(fsa,sigma(fsa)**length)
    a.optimize()
    ps = a.paths(input_token_type=isyms,
                 output_token_type=osyms)
    return random.choices(list(ps.ostrings()), k=int(n))

# Create {n} random strings from fsa.
# No duplicates in the results.
# The output fsa is the difference between the original
# fsa and the delta fsa used to generate unique strings.

# create {num} random strings of positive/negative examples.
# This may be duplicates.
def create_data_with_duplicate(name, fsa, cofsa, min_len, max_len, num):
    threshold = 20 * num**2 # not ^ because ^ is xor
    test_files = [os.path.join(dirLarge, f"{x}{name}.txt"),
                  os.path.join(dirMid, f"{x}{name}.txt"),
                  os.path.join(dirSmall, f"{x}{name}.txt"),
                  os.path.join(dirLog, f"{x}.txt")]
    f = [open(x, "w+") for x in test_files]

    syms = fsa.input_symbols()
    noneps = list(syms)[1:]
    pos_dict = dict()
    neg_dict = dict()
    for i in range(min_len, max_len + 1):
        n_pos = 0
        n_neg = 0
        pos_strings = []
        neg_strings = []
        while len(pos_strings) < num or len(neg_strings) < num:
            s = random.choices(noneps, k=i)
            s = ' '.join([x[1] for x in s])
            if (A(s, token_type=syms) @ fsa).num_states() != 0:
                n_pos += 1
                if n_pos < num:
                    pos_strings.append(s.replace(' ',''))
                # if there are too many positive strings then
                # the negative strings are very rare
                # so we fill the neg bucket 
                elif n_pos >= threshold:
                    neg_strings = neg_strings + fill_bucket(cofsa, i, num-n_neg)
                    n_neg = num
            else:
                n_neg += 1
                if n_neg < num:
                    neg_strings.append(s.replace(' ',''))
                # if there are too many negative strings then
                # the positive strings are very rare
                # so we fill the pos bucket 
                elif n_neg >= threshold:
                    pos_strings = pos_strings + fill_bucket(fsa, i, num-n_pos)
                    n_pos = num
        pos_dict[i] = set(pos_strings)
        neg_dict[i] = set(neg_strings)
        count = 0
        for ele in pos_strings:
            f[0].write(ele + '\t' + 'TRUE\n')
            if count % factor == 0:
                f[1].write(ele + '\t' + 'TRUE\n')
                if count % (factor*factor) == 0:
                    f[2].write(ele + '\t' + 'TRUE\n')
            count = count + 1
        count = 0
        for ele in neg_strings:
            f[0].write(ele + '\t' + 'FALSE\n')
            if count % factor == 0:
                f[1].write(ele + '\t' + 'FALSE\n')
            if count % (factor*factor) == 0:
                f[2].write(ele + '\t' + 'FALSE\n')
            count = count + 1
        f[3].write('\t'.join([str(i),str(n_pos),str(n_neg)]) + '\n')

    for i in range(len(f)):
        f[i].close()
    return pos_dict, neg_dict

# Create {num} positive and negative examples from fsa.
# No duplicates in the dataset.
def create_data_no_duplicate(name, fsa, pos_dict, neg_dict, min_len, max_len, num):
    threshold = 20 * num**2 # not ^ because ^ is xor
    test_files = [os.path.join(dirLarge, f"{x}{name}.txt"),
                  os.path.join(dirMid, f"{x}{name}.txt"),
                  os.path.join(dirSmall, f"{x}{name}.txt")]
    f = [open(x, "w+") for x in test_files]

    syms = fsa.input_symbols()
    noneps = list(syms)[1:]
    opos_dict = dict()
    oneg_dict = dict()
    for i in range(min_len, max_len + 1):
        pos_strings = []
        neg_strings = []
        while len(pos_strings) < num or len(neg_strings) < num:
            s = random.choices(noneps, k=i)
            s = ' '.join([x[1] for x in s])
            sx = s.replace(' ','')
            if sx in pos_strings or sx in neg_strings:
                continue
            if i in pos_dict and (sx in pos_dict[i] or sx in neg_dict[i]):
                continue
            if (A(s, token_type=syms) @ fsa).num_states() != 0:
                if len(pos_strings) < num:
                    pos_strings.append(sx)
                elif len(pos_strings) >= threshold:
                    temp = set()
                    ndi = neg_dict.get(i, set())
                    while (len(temp) < num - len(neg_strings)):
                        to_gen = num - len(neg_strings) - len(temp)
                        new_strings = set(fill_bucket(cofsa, i, to_gen))
                        new_strings = new_strings.difference(ndi)
                        new_strings = new_strings.difference(neg_strings)
                        temp = temp.union(new_strings)
                    neg_strings = neg_strings + list(temp)
            else:
                if len(neg_strings) < num:
                    neg_strings.append(sx)
                elif len(neg_strings) >= threshold:
                    temp = set()
                    pdi = pos_dict.get(i, set())
                    while (len(temp) < num - len(pos_strings)):
                        to_gen = num - len(pos_strings) - len(temp)
                        new_strings = set(fill_bucket(fsa, i, to_gen))
                        new_strings = new_strings.difference(pdi)
                        new_strings = new_strings.difference(pos_strings)
                        temp = temp.union(new_strings)
                    pos_strings = pos_strings + list(temp)
        opos_dict[i] = pos_dict.get(i,set()).union(pos_strings)
        oneg_dict[i] = neg_dict.get(i,set()).union(neg_strings)

        # write positive results to file, stopping at stopping number
        count = 0
        for ele in pos_strings:
            f[0].write(ele + "\t" + "TRUE\n")
            if count % factor == 0:
                f[1].write(ele + "\t" + "TRUE\n")
            if count % (factor*factor) == 0:
                f[2].write(ele + "\t" + "TRUE\n")
            count = count + 1

        # write negative results to file, stopping at stopping number
        count = 0
        for ele in neg_strings:
            f[0].write(ele + "\t" + "FALSE\n")
            if count % factor == 0:
                f[1].write(ele + "\t" + "FALSE\n")
            if count % (factor*factor) == 0:
                f[2].write(ele + "\t" + "FALSE\n")
            count = count + 1

    for i in range(len(f)):
        f[i].close()
    return opos_dict, oneg_dict

################
# functions for determining the border and generating
# adversial pairs
################

# defining edit distance transducer given an alphabet
def editExactly1(fsa):
    syms = fsa.input_symbols()
    noneps = list(syms)[1:]
    deletions  = [T(x[1],"",token_type=syms) for x in noneps]
    insertions = [T("",x[1],token_type=syms) for x in noneps]
    subs = [T(x[1],y[1],token_type=syms) for x in noneps for y in noneps]
    edits = pynini.union(*deletions,*insertions,*subs)
    edits.optimize()
    ss = sigmastar(fsa)
    edit1transducer = ss + edits + ss
    # a transducer that produces all strings that are within
    # 1 edit of its input string
    return edit1transducer.optimize()

def create_adversarial_examples(
    pos_dict,
    neg_dict,
    border_fst,
    border_inv,
    min_len,
    max_len,
    length
):
    # the border_fst here is bpairs,
    # which relates strings x in the_fsa to
    # those strings y in the_cofsa such that
    # string edit distance (x,y) = 1
    isyms = border_fst.input_symbols()
    osyms = border_fst.output_symbols()
    noneps = list(isyms)[1:]

    tests = {'short':'SA', 'long':'LA'}
    test  = tests[length]
    test_files = [
        os.path.join(dirLarge, f"{x}_Test{test}.txt"),
        os.path.join(dirMid, f"{x}_Test{test}.txt"),
        os.path.join(dirSmall, f"{x}_Test{test}.txt")
    ]
    f = [open(x, "w+") for x in test_files]

    numtogen = {'short':largedata // num_ss , 'long':largedata // num_ls}
    for n in range(min_len,max_len+1):
        pos_strings = []
        neg_strings = []
        num = numtogen[length] // 2
        while len(pos_strings) < num:
            s = random.choices(noneps, k=n)
            s = ' '.join([x[1] for x in s])
            sx = s.replace(' ','')
            if sx in pos_strings or sx in pos_dict.get(n,set()):
                continue
            if sx in neg_strings or sx in neg_dict.get(n,set()):
                continue
            avail = A(s, token_type=isyms) @ border_fst
            if avail.num_states() != 0:
                ps = avail.paths(input_token_type=isyms,
                                 output_token_type=osyms)
                near = random.choice(list(ps.ostrings()))
                pos_strings.append(sx)
                neg_strings.append(near.replace(' ',''))
            else:
                avail = A(s, token_type=isyms) @ border_inv
                if avail.num_states() == 0:
                    continue
                ps = avail.paths(input_token_type=isyms,
                                 output_token_type=osyms)
                near = random.choice(list(ps.ostrings()))
                neg_strings.append(sx)
                pos_strings.append(near.replace(' ',''))
        count = 0
        for i in range(len(pos_strings)):
            istr = pos_strings[i]
            ostr = neg_strings[i]
            f[0].write(istr + "\tTRUE\n")
            f[0].write(ostr + "\tFALSE\n")
            if count % factor == 0:
                f[1].write(istr + "\tTRUE\n")
                f[1].write(ostr + "\tFALSE\n")
                if count % (factor*factor) == 0:
                    f[2].write(istr + "\tTRUE\n")
                    f[2].write(ostr + "\tFALSE\n")
            count=count+1
    for i in range(len(f)):
        f[i].close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--lang', type=str, required=True)
    args = parser.parse_args()
    x = args.lang # name of the language

    if not os.path.exists("data_gen"):
        os.mkdir("data_gen")
    if not os.path.exists("data_gen/Small"):
        os.mkdir("data_gen/Small")
    if not os.path.exists("data_gen/Mid"):
        os.mkdir("data_gen/Mid")
    if not os.path.exists("data_gen/Large"):
        os.mkdir("data_gen/Large")
    if not os.path.exists("data_gen/Log"):
        os.mkdir("data_gen/Log")

    mainDir = os.getcwd()
    dirLog = os.path.join(mainDir, "data_gen/Log")
    dirLarge = os.path.join(mainDir, "data_gen/Large")
    dirMid = os.path.join(mainDir, "data_gen/Mid")
    dirSmall = os.path.join(mainDir, "data_gen/Small")

    # lengths of short strings and long strings
    ss_min_len = 20
    ss_max_len = 29
    ls_min_len = 31
    ls_max_len = 50

    num_ss = ss_max_len - ss_min_len + 1  # 10 short string lengths
    num_ls = ls_max_len - ls_min_len + 1  # 20 long  string lengths

    base = 1000
    factor = 10 # 10

    smalldata = base               # 1000
    middddata = smalldata * factor # 10000
    largedata = middddata * factor # 100000

    # number of positive train and dev strings per length
    train_pos_num = largedata//(num_ss*2) # 5000
    dev_pos_num   = largedata//(num_ss*2) # 5000

    # test1 ~ testSR which means Short Random
    # test2 ~ testLR which means Long Random
    # test3 ~ testSA which means Short Adversarial
    # test4 ~ testLA which means Long Adversarial

    # number of positive strings by length for the test sets
    testSR_pos_num = largedata//(num_ss*2) # 5000
    testLR_pos_num = largedata//(num_ls*2) # 2500
    testSA_pos_num = largedata//(num_ss*2) # 5000
    testLA_pos_num = largedata//(num_ls*2) # 2500


    # The FSA we analyze and related FSAs

    fstfile = os.path.join(mainDir, "src/fstlib/fst_format", f"{x}.fst")
    the_fsa = pynini.Fst.read(fstfile)
    the_ss = sigmastar(the_fsa)
    editTransducer = editExactly1(the_fsa)
    the_cofsa = pynini.difference(the_ss,the_fsa)
    the_cofsa.optimize()

    # this gives entire border for the adversarial test sets
    bpairs = the_fsa @ editTransducer @ the_cofsa
    bpairs.optimize()
    bpairs_inv = bpairs.copy()
    bpairs_inv.invert()
    bpairs_inv.optimize()

    # Create training data, allowing duplicates,
    # from the short strings
    # start with a file that has 100k words.
    # From there, prune to have 10k and 1k from that file.

    pos_dict_after_train, neg_dict_after_train = create_data_with_duplicate(
        "_Train",
        the_fsa,
        the_cofsa,
        ss_min_len,
        ss_max_len,
        train_pos_num
    )

    # create dev and testSR (no duplicates, no overlap with train, dev, test data)
    pos_dict_after_dev, neg_dict_after_dev = create_data_no_duplicate(
        "_Dev",
        the_fsa,
        pos_dict_after_train,
        neg_dict_after_train,
        ss_min_len,
        ss_max_len,
        dev_pos_num
    )

    create_data_no_duplicate(
        "_TestSR",
        the_fsa,
        pos_dict_after_dev,
        neg_dict_after_dev,
        ss_min_len,
        ss_max_len,
        testSR_pos_num
    )

    # create testLR (no duplicates, no overlap in train,dev,test data)
    # no overlap with shorter data sets guaranteed by disjoint set of
    # string lengths
    create_data_no_duplicate(
        "_TestLR",
        the_fsa,
        dict(),
        dict(),
        ls_min_len,
        ls_max_len,
        testLR_pos_num
    )

    # create testSA (short adversarial examples, disjoint from train,dev data;
    # may overlap with testSR)
    create_adversarial_examples(
        pos_dict_after_dev,
        neg_dict_after_dev,
        bpairs,
        bpairs_inv,
        ss_min_len,
        ss_max_len,
        length='short'
    )

    # create testLA (long adversarial examples, may overlap with testLR)
    create_adversarial_examples(
        dict(),
        dict(),
        bpairs,
        bpairs_inv,
        ls_min_len,
        ls_max_len,
        length='long'
    )
