#!/usr/bin/env python3
"""pathogen - generate data for a language by uniformly sampling paths

usage: pathogen [-b BASE] [-f FACTOR] id
where "id" is the basename of an fst file minus its extension. For example,
04.04.SL.2.1.0 refers to the file src/fstlib/fst_format/04.04.SL.2.1.0.fst

This script generates data for the given language,
placing its output into the data_gen directory.
Three subdirectories are used: Small, Mid, and Large.
Within each subdirectory, several files will be produced
whose prefix is the id and whose suffix is one of

_Train.txt  : training set
_Dev.txt    : development set
_TestSR.txt : short random test set
_TestLR.txt : long random test set
_TestSA.txt : short adversarial test set
_TestLA.txt : long adversarial test set

All sets are of the same size;
it is likely that subsets will be desired for practical use.
The random test sets are unique words that have no overlap with
the training or development sets.
The adversarial sets consist of TRUE/FALSE pairs
whose edit-distance is one, representing the border of the language.

Options:
[-b base] : default 1000.
base should be an even integer referring to the number of data points
desired in each Small data set.

[-f factor] : default 10.
factor is an integer detailing how many times larger the Mid and Large
data sets are compared against the next smaller size.
For example, with the defaults of base=1000 and factor=10,
the Small sets will be of size 1000, Mid of size 10000,
and Large of size 100000
"""

import argparse
import heapq
import math
import os
import pynini
import random

def main():
    # constants
    fstlib = os.path.join('src','fstlib','fst_format')

    # arguments
    parser = argparse.ArgumentParser(
        description='''Generate data by uniformly sampling paths.
        Output appears in the data_gen directory.
        Inputs are by tag;
        for example the file src/fstlib/fst_format/64.64.SL.2.1.0.fst
        has 64.64.SL.2.1.0 as its id.''')
    parser.add_argument('-b', type=int, dest='base',
                        default=1000,
                        help='number of elements in Small dataset')
    parser.add_argument('-f', type=int, dest='factor',
                        default=10,
                        help='growth factor for larger datasets')
    parser.add_argument('--lang', action='count', help='ignored')
    parser.add_argument('id', help='basename of FST minus extension')
    args = parser.parse_args()
    base = args.base
    factor = args.factor
    id = args.id

    to_gen = base * factor * factor
    short = range(20,30)
    long = range(31,51)

    fsa = pynini.Fst.read(os.path.join(fstlib, f'{id}.fst'))
    fsa.optimize()
    cofsa = pynini.difference(sigma(fsa).star,fsa)
    cofsa.optimize()
    border = fsa @ editExactly1(fsa) @ cofsa
    border.optimize()
    pos_dict = dict()
    neg_dict = dict()

    files = open_files('data_gen',id,'Train')
    n = to_gen // (2*len(short))
    for i in short:
        pos_dict[i], temp = create_data_with_duplicate(fsa, i, n)
        write_data(files, factor, temp, 'TRUE')
        neg_dict[i], temp = create_data_with_duplicate(cofsa, i, n)
        write_data(files, factor, temp, 'FALSE')
    close_files(files)

    files = open_files('data_gen',id,'Dev')
    n = to_gen // (2*len(short))
    for i in short:
        pos_dict[i], temp = create_data_no_duplicate(
            fsa, i, n, pos_dict[i])
        write_data(files, factor, temp, 'TRUE')
        neg_dict[i], temp = create_data_no_duplicate(
            cofsa, i, n, neg_dict[i])
        write_data(files, factor, temp, 'FALSE')
    close_files(files)

    files = open_files('data_gen',id,'TestSR')
    n = to_gen // (2*len(short))
    for i in short:
        _, temp = create_data_no_duplicate(fsa, i, n, pos_dict[i])
        write_data(files, factor, temp, 'TRUE')
        _, temp = create_data_no_duplicate(cofsa, i, n, neg_dict[i])
        write_data(files, factor, temp, 'FALSE')
    close_files(files)

    files = open_files('data_gen',id,'TestLR')
    n = to_gen // (2*len(long))
    for i in long:
        _, temp = create_data_no_duplicate(fsa, i, n, pynini.Fst())
        write_data(files, factor, temp, 'TRUE')
        _, temp = create_data_no_duplicate(cofsa, i, n, pynini.Fst())
        write_data(files, factor, temp, 'FALSE')
    close_files(files)

    del temp

    files = open_files('data_gen',id,'TestSA')
    n = to_gen // (2*len(short))
    for i in short:
        seen = pynini.union(neg_dict.get(i-1,pynini.Fst()),
                            neg_dict[i],
                            neg_dict.get(i+1,pynini.Fst()),
                            pos_dict[i])
        seen.optimize()
        pos, neg = create_adversarial_examples(border, i, n, seen)
        write_data(files, factor, pos, 'TRUE')
        write_data(files, factor, neg, 'FALSE')
    close_files(files)

    files = open_files('data_gen',id,'TestLA')
    n = to_gen // (2*len(long))
    for i in long:
        pos, neg = create_adversarial_examples(border, i, n, pynini.Fst())
        write_data(files, factor, pos, 'TRUE')
        write_data(files, factor, neg, 'FALSE')
    close_files(files)

def burdenedDAG(fsa):
    """Create a weighted machine with uniformly distributed paths.

    Arguments:
    fsa -- a finite-state machine. results unspecified if cyclic.
    """
    ofsa = pynini.Fst('log')
    ofsa.set_input_symbols(fsa.input_symbols())
    ofsa.set_output_symbols(fsa.output_symbols())
    fsa.topsort() # rename states such that edges always go small->large
    states = [-s for s in fsa.states()]
    heapq.heapify(states)
    if not states:
        return ofsa
    # FSTs come in with type 'standard'
    # there doesn't seem to be a way to change them afterward,
    # so we create an Ouput FST (ofsa) with 'log' weights
    # it needs to have the same number of states as the input;
    # so we'll make as many as we need and produce an input->output
    # map for consistent labeling
    i2o = dict()
    for s in fsa.states():
        t = ofsa.add_state()
        i2o[s] = t
        if fsa.final(s) == pynini.Weight.one(fsa.weight_type()):
            ofsa.set_final(t, pynini.Weight.one(ofsa.weight_type()))
        else:
            ofsa.set_final(t, pynini.Weight.zero(ofsa.weight_type()))
    ofsa.set_start(i2o[fsa.start()])

    npaths = dict()
    npaths[-heapq.heappop(states)] = 1
    # handle out-edges from each state in turn from a MaxHeap
    while states:
        q = -heapq.heappop(states)
        x = 0
        if fsa.final(q) == pynini.Weight.one(fsa.weight_type()):
            # final states have one extra path: stopping!
            x = 1
        for arc in fsa.arcs(q):
            x += npaths[arc.nextstate]
        npaths[q] = x
        for arc in fsa.arcs(q):
            v = math.log(x) - math.log(npaths[arc.nextstate])
            ofsa.add_arc(i2o[q],
                         pynini.Arc(arc.ilabel,
                                    arc.olabel,
                                    pynini.Weight('log',v),
                                    i2o[arc.nextstate]))
    # and when we run out of states, the machine has been weighted
    return ofsa

def sigma(fsa):
    ofsa = pynini.Fst()
    p = ofsa.add_state()
    q = ofsa.add_state()
    isyms = fsa.input_symbols()
    zero = pynini.Weight.zero(ofsa.weight_type())
    one = pynini.Weight.one(ofsa.weight_type())
    ofsa.set_start(p)
    ofsa.set_final(p, zero)
    ofsa.set_final(q, one)
    ofsa.set_input_symbols(isyms)
    ofsa.set_output_symbols(isyms)
    # don't generate an empty machine if we lack a symbol table!
    if isyms is None:
        isyms = set()
        for s in fsa.states():
            isyms.update([arc.ilabel for arc in fsa.arcs(s)])
    for sym in isyms:
        if not sym[0]:
            continue
        ofsa.add_arc(p,pynini.Arc(sym[0], sym[0], one, q))
    return ofsa

def create_data_with_duplicate(fsa, size, k):
    """Generate k words of the given size

    Arguments:
    fsa  : the base machine
    size : the desired length of words
    k    : (integer) number of words to generate

    Returns:
    * a dfa of words seen so far
    * a list of words seen so far
    """
    mach = sigma(fsa)**size
    mach.optimize() # doing this first makes for fewer states!
    mach = pynini.intersect(fsa, mach)
    mach.optimize()
    mach = burdenedDAG(mach)
    mach.set_input_symbols(fsa.input_symbols())
    mach.set_output_symbols(fsa.output_symbols())
    x = pynini.randgen(mach, npath=k, select='log_prob', weighted=False)
    s = list(x.paths(output_token_type=fsa.output_symbols()).ostrings())
    x.optimize()
    return unweight(x), [''.join(w.split(' ')) for w in s]

def create_data_no_duplicate(fsa, size, k, seen):
    """Generate k words of the given size

    Arguments:
    fsa  : the base machine
    size : the desired length of words
    k    : (integer) number of words to generate
    seen : words already seen

    Returns:
    * a dfa of words seen so far
    * a list of words seen so far
    """
    mach = sigma(fsa)**size
    mach.optimize() # doing this first makes for fewer states!
    mach = pynini.intersect(fsa, mach)
    mach = pynini.difference(mach,seen)
    mach.optimize()
    mach = burdenedDAG(mach)
    mach.set_input_symbols(fsa.input_symbols())
    mach.set_output_symbols(fsa.output_symbols())
    x = unique_paths(mach, k, select='log_prob', weighted=False)
    s = list(x.paths(output_token_type=fsa.output_symbols()).ostrings())
    x = unweight(x)|seen
    x.optimize()
    return x, [''.join(w.split(' ')) for w in s]

def create_adversarial_examples(border, size, k, seen):
    """Generate k words of the given size

    Arguments:
    border : the edit-distance-one positive-to-negative machine
    size   : the desired length of words
    k      : (integer) number of words to generate
    seen   : words already seen

    Returns:
    * a dfa of words seen so far
    * a list of words seen so far
    """
    mach = sigma(border)**size
    mach.optimize() # doing this first makes for fewer states!
    mach = pynini.difference(mach, seen)
    unseen = pynini.difference(sigma(border).star,seen)
    mach = mach @ border @ unseen
    del unseen
    mach.optimize()
    mach = burdenedDAG(mach)
    mach.set_input_symbols(border.input_symbols())
    mach.set_output_symbols(border.output_symbols())
    x = unique_paths(mach, k, select='log_prob', weighted=False)
    x = x.paths(input_token_type=border.input_symbols(),
                output_token_type=border.output_symbols())
    pos = []
    neg = []
    while not x.done():
        pos.append(''.join(x.istring().split(' ')))
        neg.append(''.join(x.ostring().split(' ')))
        x.next()
    return pos, neg


def editExactly1(fsa):
    syms = fsa.input_symbols()
    noneps = list(syms)[1:]
    deletions  = [T(x[1],"",token_type=syms) for x in noneps]
    insertions = [T("",x[1],token_type=syms) for x in noneps]
    subs = []
    for x in noneps:
        for y in noneps:
            if x == y:
                continue
            subs.append(T(x[1],y[1],token_type=syms))
    edits = pynini.union(*deletions,*insertions,*subs)
    edits.optimize()
    ss = sigma(fsa).star
    edit1transducer = ss + edits + ss
    # a transducer that produces all strings that are within
    # 1 edit of its input string
    return edit1transducer.optimize()

def unweight(fsa):
    """Return a new fsa with no weights."""
    ofsa = pynini.Fst()
    ofsa.set_input_symbols(fsa.input_symbols())
    ofsa.set_output_symbols(fsa.output_symbols())
    i2o = dict()
    for s in fsa.states():
        t = ofsa.add_state()
        i2o[s] = t
        if fsa.final(s) == pynini.Weight.one(fsa.weight_type()):
            ofsa.set_final(t, pynini.Weight.one(ofsa.weight_type()))
        else:
            ofsa.set_final(t, pynini.Weight.zero(ofsa.weight_type()))
    ofsa.set_start(i2o[fsa.start()])
    one = pynini.Weight.one(ofsa.weight_type())
    for s in fsa.states():
        for arc in fsa.arcs(s):
            ofsa.add_arc(
                i2o[s],
                pynini.Arc(arc.ilabel, arc.olabel,
                           one, i2o[arc.nextstate]))
    return ofsa

def unique_paths(fsa, n, seed=0, select='uniform',
                 max_length=2147483647,
                 weighted=False, remove_total_weight=False):
    aut = pynini.randgen(fsa, npath=n, seed=seed, select=select,
                         max_length=max_length, weighted=weighted,
                         remove_total_weight=remove_total_weight)
    aut.optimize()
    remain = n - len(set(aut.paths().ostrings()))
    while remain:
        aut = aut | pynini.randgen(
            fsa, npath=remain, seed=seed, select=select,
            max_length=max_length, weighted=weighted,
            remove_total_weight=remove_total_weight)
        aut.optimize()
        remain = n - len(set(aut.paths().ostrings()))
    return aut

def open_files(base_dir, id, tag):
    dirLarge = os.path.join(base_dir, 'Large')
    dirMid   = os.path.join(base_dir, 'Mid')
    dirSmall = os.path.join(base_dir, 'Small')
    dirs = [dirLarge, dirMid, dirSmall]
    file = f'{id}_{tag}.txt'
    for dir in dirs:
        if not os.path.exists(dir):
            os.makedirs(dir)
    return [open(os.path.join(dir, file),'w') for dir in dirs]

def write_data(files, factor, labels, tag):
    for count,x in enumerate(labels):
        for i in range(len(files)):
            if count % (factor**i) == 0:
                files[i].write(f'{x}\t{tag}\n')

def close_files(files):
    for f in files:
        f.close()

def A(s, token_type='utf8'):
    # the name of this function varies between pynini versions
    if hasattr(pynini, 'accep'):
        return pynini.accep(s, token_type=token_type)
    return pynini.acceptor(s, token_type=token_type)

def T(upper, lower, token_type='utf8'):
    return pynini.cross(A(upper, token_type=token_type),
                        A(lower, token_type=token_type))

if __name__ == '__main__':
    main()
