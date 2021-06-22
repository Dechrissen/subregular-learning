#!/bin/bash

output=all_evals.txt

find models -name '*_eval.txt' | xargs -I {} grep -He '^F-score' {} | sort | tee $output

find models -name '*_eval.txt' | xargs -I {} grep -He '^Accuracy' {} | sort | tee -a $output

find models -name '*_eval.txt' | xargs -I {} grep -He '^AUC' {} | sort | tee -a $output
