#
# A script to generate train/dev/test set
# goes with /data_gen/ and tags.txt

# This script has 3 versions of the rand_gen_no_duplicate function:
	# cody_rand_gen_no_duplicate
	# alternate_rand_gen_no_duplicate
	# rand_gen_no_duplicate (the original) (inefficient)
# Right now it's using alternate_rand_gen_no_duplicate
# It puts files of sizes 100k, 10k, and 1k strings into a data folder

# updated 3 December 2020
#
import pynini
import functools
import numpy as np
import random
import pathlib


def A(s):
    return pynini.acceptor(s, token_type="utf8")

def T(upper, lower):
    return pynini.cross(A(upper), A(lower))

a = A("a")
zero = a-a
zero.optimize()

# Defining alphabet

# alpha = "abcd"
# sigma = zero
# for x in list(alpha):
#     sigma = A(x) | sigma
# sigma.optimize()

# # sigmaStar accepts all strings made of the characters in alpha
# sigmaStar = (sigma.star).optimize()


# FUNCTIONS that take an fsa and return its alphabet, sigma and sigmastar, respectively

def alph(fsa):
    symtable = fsa.input_symbols()
    i = iter(symtable)
    next(i) # this skips over epsilon which is always
            # the first entry in the symbol table
    temp = ''
    for sympair in i:  # the table entries are pairs of the form (num,symbol)
        temp = temp + sympair[1]
    return temp

def sigma(fsa):
    chars = alph(fsa)
    s = zero
    for c in chars:
        s = A(c) | s
    return s.optimize()

def sigmastar(fsa):
    return (sigma(fsa).star).optimize()

# Utility function that outputs all strings of an fsa

def list_string_set(acceptor):
    my_list = []
    paths = acceptor.paths(input_token_type="utf8", output_token_type="utf8")
    for s in paths.ostrings():
        my_list.append(s)
    my_list.sort(key=len)
    return my_list

################
# functions for determining the border and generating adversial pairs
################

# defining edit distance transducer given an alphabet
def editExactly1(fsa):
    chars = alph(fsa)
    ss = sigmastar(fsa)
    edits = zero
    for x in chars: edits = T(x,"") | edits  # deletion
    for x in chars: edits = T("",x) | edits  # insertion
    for x in chars:
        for y in chars:
            if x != y:
                edits = T(x,y) | edits       # substitution
    edits.optimize()
    edit1transducer = ss + edits + ss
    # a transducer that produces all strings that are within 1 edit of its input string
    return edit1transducer.optimize()

def border(fsa,n):
    '''
    A function that takes an fsa and produces an fst;
    the fst converts strings of length n in the language to "border" strings,
    which are 1 edit off from being in the language
    '''
    chars = alph(fsa)
    s = sigma(fsa)
    ss = sigmastar(fsa)
    editTransducer = editExactly1(fsa)
    cofsa = pynini.difference(ss,fsa)
    cofsa.optimize()
    bpairs = fsa @ editTransducer @ cofsa     # this is the key insight which gives entire border
    bpairs.optimize()
    sigmaN = pynini.closure(s,n,n)
    sigmaN.optimize()
    bpairsN = sigmaN @ bpairs               # here we limit the border to input words of length=n
    bpairsN.optimize()
    return bpairsN


def build (border, lang, lang_name, n, length):
    '''
    A function that creates the adv_data files that are in /data_gen/ ;
    It gets the set of "border" strings from `border()`
    and writes them to adv_data files using the function `by_len()`

    Inputs:
    -------
    border : fst
        the fsa that recognizes border strings
    lang : fst
        the fsa that recognizes the language in question
    n : int
        length of the strings used to generate the border strings
    '''
    tests = {'short':'3', 'long':'4'}
    test  = tests[length]
    path_to_library = str(pathlib.Path(__file__).parent.absolute().parent)
    test3_files = [path_to_library+"/data_gen/100k/"+lang_name+"_Test" + test + ".txt",
                   path_to_library+"/data_gen/10k/"+lang_name+"_Test" + test + ".txt",
                   path_to_library+"/data_gen/1k/"+lang_name+"_Test" + test + ".txt"]
    f = [open(test3_files[0], "w+"),
         open(test3_files[1], "w+"),
         open(test3_files[2], "w+")]

    count = 0

    # 5 times:
    for i in range(5):
        # writes 2*xk/10 random strings to the files in f
        # border(lang, n) creates border pairs for length n
        by_len(border(lang, n), f, count)

    for i in range(3):
        f[i].close()

    return count

def create_adversarial_examples(pos_dict, fsa, lang_name, min_len, max_len, length):
    for i in range(min_len,max_len+1):
        c = build(border,fsa,lang_name, i, length=length)
    return c

def by_len(ex, f, count):
    random_examples=pynini.randgen(ex,10000)
    ps = random_examples.paths(input_token_type="utf8", output_token_type="utf8")

    while not ps.done():
        if ps.istring() and ps.ostring():
            f[0].write(ps.istring() + "\tTRUE\n")
            f[0].write(ps.ostring() + "\tFALSE\n")
            if count % 10 ==0:
                f[1].write(ps.istring() + "\tTRUE\n")
                f[1].write(ps.ostring() + "\tFALSE\n")
                if count %100 ==0:
                    f[2].write(ps.istring() + "\tTRUE\n")
                    f[2].write(ps.ostring() + "\tFALSE\n")
        ps.next()
        count=count+1


# Utility function that gets the strings of an fsa
# with length from min_len to max_len

def get_pos_string(fsa, min_len, max_len):
    s = sigma(fsa)
    fsa_dict = {}
    for i in range(min_len, max_len + 1):
        fsa_dict[i] = pynini.intersect(fsa, pynini.closure(s, i, i))
        # print(list_string_set(fsa_dict[i]))
    return fsa_dict


# Utility function that gets the strings of the complement
# of an fsa with length from min_len to max_len

def get_neg_string(fsa, min_len, max_len):
    s = sigma(fsa)
    fsa_dict = {}
    for i in range(min_len, max_len + 1):
        fsa_dict[i] = pynini.difference(pynini.closure(s, i, i), fsa)
        # print(list_string_set(fsa_dict[i]))
    return fsa_dict


# Create {n} random strings from fsa.
# No duplicates in the results.
# The output fsa is the difference between the original
# fsa and the delta fsa used to generate unique strings.


def rand_gen_no_duplicate(acceptor, n):
    loop = 100000
    for i in range(loop):
        print('trying to generate random strings ('+str(i)+')')
        num = int(n + n*i*0.1)
        temp = pynini.randgen(acceptor, npath=num, seed=0, select="uniform", max_length=2147483647, weighted=False)
        rand_list = list_string_set(temp)
        rand_list = list(set(rand_list))
        uniq_len = len(rand_list)
        if uniq_len < n and i < loop - 1:
            #print('insufficient random strings\n')
            continue
        else:
            random.shuffle(rand_list)
            rand_list = rand_list[:n]
            rand_list.sort()
            acceptor = pynini.difference(acceptor, temp)
            return acceptor, rand_list

def alternate_rand_gen_no_duplicate(acceptor, n):
    rand_list = []
    loop = 10
    seed = 0
    for i in range(loop):
        print('(alternate) trying to generate random strings ('+str(i)+')')
        num = int(n + n*i*.01)
        temp = pynini.randgen(acceptor, npath=num, seed=seed, select='uniform', max_length=2147483647, weighted=False)
        print('made new `temp`')
        temp_list = list_string_set(temp)
        print('temp got '+str(len(temp_list))+' random strings')
        temp_list = list(set(temp_list))
        new_strings = [t for t in temp_list if t not in rand_list]
        print('got '+str(len(new_strings))+' new strings')
        for t in temp_list:
            if t not in rand_list:
                rand_list.append(t)
                if len(rand_list)==n:
                    print('rand_list now has '+str(len(rand_list))+' strings')
                    print('finally got enough strings in rand_list; i='+str(i))
                    return acceptor, rand_list
        acceptor = pynini.difference(acceptor, temp)
        seed += 1
        print('rand_list now has '+str(len(rand_list))+' strings')
        print('need to add strings to rand_list ('+str(i)+')')
    print('finished loop; returning incomplete set')
    return acceptor, rand_list

def cody_rand_gen_no_duplicate(acceptor, n):
    loop = 50000
    result_set = set()
    seed = 0
    for i in range(loop):
        print('started loop '+str(i))
        num = int(n + n*i*0.1)
        temp = pynini.randgen(acceptor, npath=num, seed=seed, select='uniform', max_length=2147483647, weighted=False)
        rand_list = list_string_set(temp)
        result_set = result_set.union(set(rand_list))
        uniq_len = len(result_set)
        if uniq_len < n and i < loop - 1:
            print('insufficient random strings')
            seed += 1
            continue
        else:
            rand_list = list(result_set)
            random.shuffle(rand_list)
            rand_list = rand_list[:n]
            rand_list.sort()
            acceptor = pynini.difference(acceptor, temp)
            print('returning')
            if len(rand_list) >= n:
                print('got full rand_list\n')
            return acceptor, rand_list

# Create {num} positive and negative examples from fsa.
# No duplicates in the dataset.


def create_data_no_duplicate(filename, pos_dict, neg_dict, min_len, max_len, num):
    with open(filename, "w+") as f:
        for i in range(min_len, max_len + 1):
            print('\nworking on length '+str(i))

            # generate positive strings
            print('getting positive strings for length '+str(i))
            acceptor, pos_results = alternate_rand_gen_no_duplicate(pos_dict[i], num)
            amount_pos = len(pos_results)
            if amount_pos < num:
                print('WARNING: Only', str(amount_pos), 'positive strings generated for length', str(i))
            pos_dict[i] = acceptor

            # generate negative strings
            print('getting negative strings for length '+str(i))
            acceptor, neg_results = alternate_rand_gen_no_duplicate(neg_dict[i], num)
            amount_neg = len(neg_results)
            if amount_neg < num:
                print('WARNING: Only', str(amount_neg), 'negative strings generated for length', str(i))
            neg_dict[i] = acceptor

            # check which of the pos results or neg results is smaller, and set that to the stopping number
            if amount_pos > amount_neg:
                stop = amount_neg
            else:
                stop = amount_pos

            # write positive results to file, stopping at stopping number
            counter = 0
            for ele in pos_results:
                f.write(ele + "\t" + "TRUE\n")
                counter+=1
                if counter == stop:
                    break

            # write negative results to file, stopping at stopping number
            counter = 0
            for ele in neg_results:
                f.write(ele + "\t" + "FALSE\n")
                counter+=1
                if counter == stop:
                    break

    return pos_dict, neg_dict


# create {num} random strings of positive/negative examples.
# This may be duplicates.
def create_data_with_duplicate(filename, pos_dict, neg_dict, min_len, max_len, num, get_difference):
    with open(filename, "w+") as f:
        for i in range(min_len, max_len + 1):
            pos_fsa = \
                pynini.randgen(pos_dict[i], npath=num, seed=0, select="uniform", max_length=2147483647, weighted=False)
            if get_difference == 1:
                pos_dict[i] = pynini.difference(pos_dict[i], pos_fsa)
            for ele in list_string_set(pos_fsa):
                f.write(ele + "\t" + "TRUE\n")
            neg_fsa = \
                pynini.randgen(neg_dict[i], npath=num, seed=0, select="uniform", max_length=2147483647, weighted=False)
            if get_difference == 1:
                neg_dict[i] = pynini.difference(neg_dict[i], neg_fsa)
            for ele in list_string_set(neg_fsa):
                f.write(ele + "\t" + "FALSE\n")
    return pos_dict, neg_dict


# function that will take the 100k word list and create 10k and 1k from that list
def prune(f, name):
    path_to_library = str(pathlib.Path(__file__).parent.absolute().parent)

    data = open(name).readlines()

    small = [open(path_to_library+"/data_gen/10k/" + f, "w+"),
                open(path_to_library+"/data_gen/1k/" + f, "w+")]

    tr = []
    fl = []
    count = 0

    for line in data:
        if count % 2 == 0:
            tr.append(line)
        else:
            fl.append(line)
        count += 1
    count = 0

    for x in range(len(tr)):
        if count % 10 == 0:
            small[0].write(tr[x] + fl[x])
            if count %100 ==0:
                small[1].write(tr[x] + fl[x])
        count=count+1

    return True

###########################################################
## util functions to generate data and confirm file size ##
###########################################################
## moved this to a separate file


# have not made use of this yet
'''def construct_data(n):
    return True

def construct_all():
    tags = open("tags.txt").readlines()

    for x in tags:
        construct_data(x[:-1])
    return True'''


# ############################################
# ####main body (util functions finished)#####
# ############################################


path_to_library = pathlib.Path(__file__).parent.absolute().parent
#print(path_to_library)
tags = open(path_to_library / pathlib.Path("tags.txt"))
tags = tags.readlines()

# define hyper-parameters
for x in tags:
    print('\nStarting on', x)
    my_fsa = pynini.Fst.read(str(path_to_library) + "/src/fstlib/fst_format/" + x[:-1] + ".fst")
    x = x[:-1]
    ss_min_len = 10
    ss_max_len = 19
    train_pos_num = 5000
    dev_pos_num = 5000

    test1_pos_num = 5000
    test2_pos_num = 2500
    test3_pos_num = 5000

    ls_min_len = 31
    ls_max_len = 50

    dir_name = str(path_to_library)+"/data_gen/100k/" + x


    #FIRST - set up dictionary
    pos_dict = get_pos_string(my_fsa, ss_min_len, ss_max_len)
    neg_dict = get_neg_string(my_fsa, ss_min_len, ss_max_len)


    # create training data with duplicates
    # start with a file that has 100k words. from there, prune to have 10k and 1k from that file.
    pos_dict, neg_dict = \
    create_data_with_duplicate(dir_name + "_Training.txt", pos_dict, neg_dict, ss_min_len, ss_max_len, train_pos_num, 1)
    prune(x + "_Training.txt", dir_name + "_Training.txt")

    # create dev and test_1 (no duplicates, no overlap in train/dev/test data)
    pos_dict, neg_dict = create_data_no_duplicate(dir_name + "_Dev.txt", pos_dict, neg_dict, ss_min_len, ss_max_len, dev_pos_num)
    prune(x + "_Dev.txt", dir_name + "_Dev.txt")

    pos_dict, neg_dict = create_data_no_duplicate(dir_name + "_Test1.txt", pos_dict, neg_dict, ss_min_len, ss_max_len, test1_pos_num)
    prune(x + "_Test1.txt", dir_name + "_Test1.txt")

    # creat test_3 (short adversarial examples)
    create_adversarial_examples(pos_dict, my_fsa, x, ss_min_len, ss_max_len, length='short')

    # generate long strings
    pos_dict = get_pos_string(my_fsa, ls_min_len, ls_max_len)
    neg_dict = get_neg_string(my_fsa, ls_min_len, ls_max_len)

    # create test_2 (no duplicates)
    create_data_no_duplicate(dir_name + "_Test2.txt", pos_dict, neg_dict, ls_min_len, ls_max_len, test2_pos_num)
    prune(x + "_Test2.txt", dir_name + "_Test2.txt")

    # create test_4 (long adversarial examples)
    create_adversarial_examples(pos_dict, my_fsa, x, ls_min_len, ls_max_len, length='long')

    print("Finished", x)

print("Finished!")


