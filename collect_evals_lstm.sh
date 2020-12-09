#!/bin/bash

output=all_evals_lstm.txt

find models_lstm -name '*_eval.txt' | xargs -I {} grep -He '^F-score' {} | sort | tee $output

find models_lstm -name '*_eval.txt' | xargs -I {} grep -He '^Accuracy' {} | sort | tee -a $output
