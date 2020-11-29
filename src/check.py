
###########################################################
########### util functions to confirm file size ###########
###########################################################

import pynini
import functools
import numpy as np
import random

def check(n):
    #check 1k, 10k, and 100k to see if all files of type n are of correct length 
    lengths = ["1k", "10k", "100k"]
    #first 1k
    
    beginning = "/home/ekp/Documents/SBU_Fall2020/CSE538_NLP/Project/subregular_neural_models/src/data_gen/"
    
    for x in lengths:
        test = [open(beginning+"data/" + x + "/"+n+"_Dev.txt").readlines(),
                open(beginning+"data/" + x + "/"+n+"_Training.txt").readlines(),
                open(beginning+"data/" + x + "/"+n+"_Test1.txt").readlines(),
                open(beginning+"data/" + x + "/"+n+"_Test2.txt").readlines(),
                open(beginning+"data/" + x + "/"+n+"_Test3.txt").readlines()]
       
        if x == "1k":
            k = 1000
        elif x == "10k":
            k = 10000
        else:
            k = 100000
            
        if len(test[0]) < k:
            print(x + "/" + n + "_Dev incomplete:", str(len(test[0])))
        if len(test[1]) < k: 
            print(x + "/" + n + "_Training incomplete:", str(len(test[1])))
        if len(test[2]) < k:
            print(x + "/" + n + "_Test1 incomplete:", str(len(test[2])))
        if len(test[3]) < k:
            print(x + "/" + n + "_Test2 incomplete:", str(len(test[3])))
        if len(test[4]) < k:
            print(x + "/" + n + "_Test3 incomplete:", str(len(test[4])))
    
    return True

def check_all():
    tags = open("/home/ekp/Documents/SBU_Fall2020/CSE538_NLP/Project/subregular_neural_models/tags.txt").readlines()
    
    for x in tags:
        check(x[:-1])
    return True
    
check_all()
