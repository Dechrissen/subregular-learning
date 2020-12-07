#!/bin/bash

find models -name '*_eval.txt' | xargs -I {} grep -He '^F-score' {} | sort
