#!/usr/bin/env python3

def main():
    """This program reads a DFA from the JSON format output by
    FlexFringe as well as one or more input data files.
    It then writes output files describing the DFA's predictions
    for the input words.

    Run "testaut.py -h" for full usage information.
    """
    parser = argparse.ArgumentParser(description='Test a learned model.')
    parser.add_argument('-d', '--outdir',
                        help='directory in which to place predictions',
                        default="")
    parser.add_argument('-m', '--model',
                        help='path to the JSON-formatted model data',
                        required=True)
    parser.add_argument('inputs',
                        nargs='*',
                        help='tagged test data files')
    args = parser.parse_args()
    dfa = read_model(args.model)
    outdir = os.path.expanduser(args.outdir)
    real_out = sys.stdout
    if outdir:
        os.makedirs(outdir, exist_ok=True)
    for test in args.inputs:
        name = test.split("_")[-1]
        name = name.split(".")[0]
        sys.stdout = open(f"{os.path.join(outdir,name)}_pred.txt","w")
        evaluate(dfa,test)
    sys.stdout = real_out

import argparse
import json
import os
import sys


def read_model(model_file):
    """Load and interpret the model found in a given JSON file.

    arguments
    =========
    model_file: path to the JSON-formatted model file
    """

    with open(model_file,"r") as f:
        json_data = f.read()

    model = json.loads(json_data)
    dfa = dict()
    for edge in model["edges"]:
        source = str(edge["source"])
        sym = str(edge["name"])
        target = str(edge["target"])
        if source not in dfa:
            dfa[source] = dict()
        dfa[source][sym] = target

    for node in model["nodes"]:
        id = str(node["id"])
        parity = "1" == (node["trace"].split(" "))[0]
        if id not in dfa:
            dfa[id] = dict()
        dfa[id]["accepting?"] = parity
    return dfa


def traverse(dfa, word):
    """Determine whether the given word is accepted by the given DFA.

    arguments
    =========
    dfa:  a dictionary representing the model
    word: the string to test
    """

    state = "0"
    for symbol in word:
        state = dfa.get(state,dict()).get(symbol)
        if type(state) == type(None):
            return False
    return dfa.get(state,dict()).get("accepting?")


def evaluate(dfa, test_file=None):
    """Read a word-list and determine how the given DFA performs.

    arguments
    =========
    dfa:       a dictionary representing the model
    test_file: a file containing tab-separated lines
               containing a word followed by a BOOL
    """
    if type(test_file) == type(None):
        samples = sys.stdin.readlines()
    else:
        with open(test_file,"r") as f:
            samples = f.readlines()
    for sample in samples:
        word, expected, *_ = sample.rstrip().split("\t")
        print(word,str(expected).upper(),
              str(traverse(dfa,word)).upper(),sep="\t")


if __name__ == "__main__":
    main()
