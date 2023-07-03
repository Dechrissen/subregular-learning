# For an input language name, this script generates a training
# set, dev set, and four test sets, for each size Large, Mid,
# Small where Small ⊂ Mid ⊂ Large.

import pynini
import argparse
import functools
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

a = A("a")
zero = a-a
zero.optimize()

# FUNCTIONS that take an fsa and return its alphabet, sigma
# and sigmastar, respectively

def alph(fsa):
    symtable = fsa.input_symbols()
    i = iter(symtable)
    next(i) # skip over epsilon, ie first entry in symbol table
    temp = ''
    for sympair in i:  # table entries are pairs of form (num,symbol)
        temp = temp + sympair[1]
    return temp

def sigma(fsa):
    syms = fsa.input_symbols()
    one_letter = [A(x[1],token_type=syms) for x in syms][1:]
    s = pynini.union(*one_letter)
    s.set_input_symbols(fsa.input_symbols())
    s.set_output_symbols(fsa.output_symbols())
    return s.optimize()

def sigmastar(fsa):
    return (sigma(fsa).star).optimize()

# Utility function that outputs all strings of an fsa
# the fsa must recognize a finite language

def list_string_set(fsa):
    isyms=fsa.input_symbols()
    osyms=fsa.output_symbols()
    my_list = []
    paths = fsa.paths(input_token_type=isyms, output_token_type=osyms)
    for s in paths.ostrings():
        my_list.append(s)
    my_list.sort(key=len)
    return my_list


# Utility function that gets the strings of an fsa
# with length from min_len to max_len

def make_string_dict(fsa, min_len, max_len, sigma):
    fsa_dict = {}
    for i in range(min_len, max_len + 1):
        fsa_dict[i] = pynini.intersect(fsa, pynini.closure(sigma, i, i))
        # print(list_string_set(fsa_dict[i]))
    return fsa_dict

# Create {n} random strings from fsa.
# No duplicates in the results.
# The output fsa is the difference between the original
# fsa and the delta fsa used to generate unique strings.

# create {num} random strings of positive/negative examples.
# This may be duplicates.
def create_data_with_duplicate(name, pos_dict, neg_dict, min_len, max_len, num):

    test_files = [os.path.join(dirLarge, f"{x}{name}.txt"),
                  os.path.join(dirMid, f"{x}{name}.txt"),
                  os.path.join(dirSmall, f"{x}{name}.txt")]
    f = [open(test_files[0], "w+"),
         open(test_files[1], "w+"),
         open(test_files[2], "w+")]

    for i in range(min_len, max_len + 1):
        
        # get num strings of length i from the pos_dict
        pos_fsa = pynini.randgen(
            pos_dict[i],
            npath=num,
            seed=0,
            select="uniform",
            max_length=2147483647,
            weighted=False
        )

        # write them into the files
        count = 0
        for ele in list_string_set(pos_fsa):
            f[0].write(ele + "\t" + "TRUE\n")
            if count % factor == 0:
                f[1].write(ele + "\t" + "TRUE\n")
            if count % (factor*factor) == 0:
                f[2].write(ele + "\t" + "TRUE\n")
            count = count +1

        # update the pos_dict by subtracting the strings in pos_fsa
        pos_dict[i] = pynini.difference(pos_dict[i], pos_fsa)

        # get num strings of length i from the neg_dict
        neg_fsa = pynini.randgen(
            neg_dict[i],
            npath=num,
            seed=0,
            select="uniform",
            max_length=2147483647,
            weighted=False
        )

        # write them into the files
        count = 0
        for ele in list_string_set(neg_fsa):
            f[0].write(ele + "\t" + "FALSE\n")
            if count % factor == 0:
                f[1].write(ele + "\t" + "FALSE\n")
            if count % (factor*factor) == 0:
                f[2].write(ele + "\t" + "FALSE\n")
            count = count + 1

        # update the neg_dict by subtracting the strings in neg_fsa
        neg_dict[i] = pynini.difference(neg_dict[i], neg_fsa)

    for i in range(3):
        f[i].close()            
    return pos_dict, neg_dict


def rand_gen_no_duplicate(acceptor, n):
    rand_list = []
    loop = 10
    seed = 0
    for i in range(loop):
        #print('(alternate) trying to generate random strings ('+str(i)+')')
        num = int(n + n*i*.01)
        temp = pynini.randgen(
            acceptor,
            npath=num,
            seed=seed,
            select='uniform',
            max_length=2147483647,
            weighted=False
        )
        #print('made new `temp`')
        temp_list = list_string_set(temp)
        #print('temp got '+str(len(temp_list))+' random strings')
        temp_list = list(set(temp_list))
        #new_strings = [t for t in temp_list if t not in rand_list]
        #print('got '+str(len(new_strings))+' new strings')
        for t in temp_list:
            if t not in rand_list:
                rand_list.append(t)
                if len(rand_list)==n:
                    #print('rand_list now has '+str(len(rand_list))+' strings')
                    #print('finally got enough strings in rand_list; i='+str(i))
                    return acceptor, rand_list
        acceptor = pynini.difference(acceptor, temp)
        seed += 1
        #print('rand_list now has '+str(len(rand_list))+' strings')
        #print('need to add strings to rand_list ('+str(i)+')')
    #print('finished loop; returning incomplete set')
    return acceptor, rand_list

# Create {num} positive and negative examples from fsa.
# No duplicates in the dataset.


def create_data_no_duplicate(name, pos_dict, neg_dict, min_len, max_len, num):

    test_files = [os.path.join(dirLarge, f"{x}{name}.txt"),
                  os.path.join(dirMid, f"{x}{name}.txt"),
                  os.path.join(dirSmall, f"{x}{name}.txt")]
    f = [open(test_files[0], "w+"),
         open(test_files[1], "w+"),
         open(test_files[2], "w+")]
    
    for i in range(min_len, max_len + 1):
        #print('\nworking on length '+str(i))
        
        # generate positive strings
        #print('getting positive strings for length '+str(i))
        acceptor, pos_results = rand_gen_no_duplicate(pos_dict[i], num)
        amount_pos = len(pos_results)
        if amount_pos < num:
            print(
                f'WARNING: Only {amount_pos}'
                f'positive strings generated for length {i}'
            )
            pos_dict[i] = acceptor
            
        # generate negative strings
        #print('getting negative strings for length '+str(i))
        acceptor, neg_results = rand_gen_no_duplicate(neg_dict[i], num)
        amount_neg = len(neg_results)
        if amount_neg < num:
            print(
                f'WARNING: Only {amount_neg}'
                f'negative strings generated for length {i}'
            )
            neg_dict[i] = acceptor
            
        # check which of the pos results or neg results is smaller,
        # and set that to the stopping number
        if amount_pos > amount_neg:
            stop = amount_neg
        else:
            stop = amount_pos

        # write positive results to file, stopping at stopping number
        count = 0
        for ele in pos_results:
            f[0].write(ele + "\t" + "TRUE\n")
            if count % factor == 0:
                f[1].write(ele + "\t" + "TRUE\n")
            if count % (factor*factor) == 0:
                f[2].write(ele + "\t" + "TRUE\n")
            count = count +1
            if count == stop:
                break

        # write negative results to file, stopping at stopping number
        count = 0
        for ele in neg_results:
            f[0].write(ele + "\t" + "FALSE\n")
            if count % factor == 0:
                f[1].write(ele + "\t" + "FALSE\n")
            if count % (factor*factor) == 0:
                f[2].write(ele + "\t" + "FALSE\n")
            count = count +1
            if count == stop:
                break

    for i in range(3):
        f[i].close()        
    return pos_dict, neg_dict



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


def border(borderfsa, pos_dict, neg_dict, n):
    '''
    A function that takes an fsa and produces an fst;
    the fst converts strings of length n in the language to "border" strings,
    which are 1 edit off from being in the language
    '''
    neg_dicts = neg_dict[n] | neg_dict[n-1] | neg_dict[n+1]
    # limit the border to input words of length=n
    bpairsN = pos_dict[n] @ borderfsa @ neg_dicts
    bpairsN.optimize()
    return bpairsN


def create_adversarial_examples(
    pos_dict,
    neg_dict,
    border_fst,
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
    
    tests = {'short':'SA', 'long':'LA'}
    test  = tests[length]
    test_files = [
        os.path.join(dirLarge, f"{x}_Test{test}.txt"),
        os.path.join(dirMid, f"{x}_Test{test}.txt"),
        os.path.join(dirSmall, f"{x}_Test{test}.txt")
    ]
    f = [
        open(test_files[0], "w+"),
        open(test_files[1], "w+"),
        open(test_files[2], "w+")
    ]

    numtogen = {'short':largedata / num_ss , 'long':largedata / num_ls}
    for n in range(min_len,max_len+1):
        bpairsN = border(border_fst, pos_dict, neg_dict, n)
        random_examples=pynini.randgen(
            bpairsN,
            npath=numtogen[length]/2,
            seed=0,
            select="uniform",
            max_length=2147483647,
            weighted=False
        )
        ps = random_examples.paths(
            input_token_type=isyms,
            output_token_type=osyms
        )

        # CONCERN: These test items could contain duplicates because
        # random_examples may contain duplicates... maybe a better
        # approach is to generate positive strings with create_data_no_duplicate
        # and then find a negative string which is 1 away (then each pair is
        # distinct even if some negative strings occur twice)
        
        count = 0
        while not ps.done():
            if ps.istring() and ps.ostring():
                f[0].write(ps.istring() + "\tTRUE\n")
                f[0].write(ps.ostring() + "\tFALSE\n")
                if count % factor == 0:
                    f[1].write(ps.istring() + "\tTRUE\n")
                    f[1].write(ps.ostring() + "\tFALSE\n")
                    if count % (factor*factor) == 0:
                        f[2].write(ps.istring() + "\tTRUE\n")
                        f[2].write(ps.ostring() + "\tFALSE\n")
            ps.next()
            count=count+1
        
    for i in range(3):
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

    mainDir = os.getcwd()
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
    train_pos_num = largedata/(num_ss*2) # 5000
    dev_pos_num   = largedata/(num_ss*2) # 5000

    # test1 ~ testSR which means Short Random
    # test2 ~ testLR which means Long Random
    # test3 ~ testSA which means Short Adversarial
    # test4 ~ testLA which means Long Adversarial

    # number of positive strings by length for the test sets
    testSR_pos_num = largedata/(num_ss*2) # 5000
    testLR_pos_num = largedata/(num_ls*2) # 2500
    testSA_pos_num = largedata/(num_ss*2) # 5000
    testLA_pos_num = largedata/(num_ls*2) # 2500


    # The FSA we analyze and related FSAs

    fstfile = os.path.join(mainDir, "src/fstlib/fst_format", f"{x}.fst")
    the_fsa = pynini.Fst.read(fstfile)
    the_chars = alph(the_fsa)
    the_s = sigma(the_fsa)
    the_ss = sigmastar(the_fsa)
    editTransducer = editExactly1(the_fsa)
    the_cofsa = pynini.difference(the_ss,the_fsa)
    the_cofsa.optimize()

    # this gives entire border for the adversarial test sets
    bpairs = the_fsa @ editTransducer @ the_cofsa
    bpairs.optimize()


    # set up dictionary for short strings
    pos_dict_ss = make_string_dict(the_fsa, ss_min_len-1, ss_max_len+1, the_s)
    neg_dict_ss = make_string_dict(the_cofsa, ss_min_len-1, ss_max_len+1, the_s)


    # set up dictionary for long strings
    pos_dict_ls = make_string_dict(the_fsa, ls_min_len-1, ls_max_len+1, the_s)
    neg_dict_ls = make_string_dict(the_cofsa, ls_min_len-1, ls_max_len+1, the_s)

    # Create training data with duplicates
    # from the short strings
    # start with a file that has 100k words.
    # From there, prune to have 10k and 1k from that file.

    pos_dict_after_train, neg_dict_after_train = create_data_with_duplicate(
        "_Train",
        pos_dict_ss,
        neg_dict_ss,
        ss_min_len,
        ss_max_len,
        train_pos_num
    )

    # create dev and testSR (no duplicates, no overlap with train, dev, test data)
    pos_dict_after_dev, neg_dict_after_dev = create_data_no_duplicate(
        "_Dev",
        pos_dict_after_train,
        neg_dict_after_train,
        ss_min_len,
        ss_max_len,
        dev_pos_num
    )

    create_data_no_duplicate(
        "_TestSR",
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
        pos_dict_ls,
        neg_dict_ls,
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
        ss_min_len,
        ss_max_len,
        length='short'
    )

    # create testLA (long adversarial examples, may overlap with testLR)
    create_adversarial_examples(
        pos_dict_ls,
        neg_dict_ls,
        bpairs,
        ls_min_len,
        ls_max_len,
        length='long'
    )
