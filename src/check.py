
###########################################################
########### util functions to confirm file size ###########
###########################################################
# updated 29 May 2021
# goes with /data/ and tags.txt

# This script confirms that the
	# _Dev.txt
	# _Training.txt
	#_Test1.txt
	#_Test2.txt
	#_Test3.txt
# files in the data_3langs folder are of sizes
	# 100k
	# 10k
	# 1k
# for the languages listed in tags.txt (3 languages per class)

import pynini
import functools
import numpy as np
import random
import pathlib

def check(n):
    #check 1k, 10k, and 100k to see if all files of type n are of correct length
    lengths = ["1k", "10k", "100k"]
    #first 1k
    path_to_library = pathlib.Path(__file__).parent.absolute().parent
    beginning = path_to_library

    for x in lengths:

        try:
            dev = open("./data_gen/" + x + "/"+n+"_Dev.txt").readlines(),
        except:
            dev = 'missing'

        try:
            train = open("./data_gen/" + x + "/"+n+"_Training.txt").readlines(),
        except:
            train = 'missing'

        try:
            test1 = open("./data_gen/" + x + "/"+n+"_Test1.txt").readlines(),
        except:
            test1 = 'missing'

        try:
            test2 = open("./data_gen/" + x + "/"+n+"_Test2.txt").readlines(),
        except:
            test2 = 'missing'

        try:
            test3 = open("./data_gen/" + x + "/"+n+"_Test3.txt").readlines(),
        except:
            test3 = 'missing'

        files = [dev, train, test1, test2, test3]
        filetypes = ['_Dev', '_Training', '_Test1', '_Test2', '_Test3']


        if x == "1k":
            k = 1000
        elif x == "10k":
            k = 10000
        else:
            k = 100000


        for i in range(len(files)):
            if files[i] != 'missing':
                if len(files[i][0]) != k:
                    print(x + "/" + n + filetypes[i] + " incomplete:", str(len(files[i][0])))
                else:
                    print(x + "/" + n + filetypes[i] + " complete")
            else:
                 print(x + "/" + n + filetypes[i] + " missing")

    return True

def check_all():
    path_to_library = pathlib.Path(__file__).parent.absolute().parent
    #tags = open(str(path_to_library)+"/tags.txt").readlines()
    tags = open("./tags.txt").readlines()

    for x in tags:
        check(x)
        print()
    return True

check_all()
