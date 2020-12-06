#!/bin/bash

find models -name '*_eval.txt' | grep -He '^F1'
