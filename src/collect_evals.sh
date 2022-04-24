#!/bin/bash

output=all_evals.txt

if test -f $output; then
    rm $output
fi

find models -name '*_eval.txt' | xargs -I {} grep -He '^TP' {} | sort >> $output
find models -name '*_eval.txt' | xargs -I {} grep -He '^FP' {} | sort >> $output
find models -name '*_eval.txt' | xargs -I {} grep -He '^TN' {} | sort >> $output
find models -name '*_eval.txt' | xargs -I {} grep -He '^FN' {} | sort >> $output
find models -name '*_eval.txt' | xargs -I {} grep -He '^TPR' {} | sort >> $output
find models -name '*_eval.txt' | xargs -I {} grep -He '^FPR' {} | sort >> $output
find models -name '*_eval.txt' | xargs -I {} grep -He '^Precision' {} | sort >> $output
find models -name '*_eval.txt' | xargs -I {} grep -He '^F-score' {} | sort >> $output
find models -name '*_eval.txt' | xargs -I {} grep -He '^Accuracy' {} | sort >> $output
find models -name '*_eval.txt' | xargs -I {} grep -He '^AUC' {} | sort >> $output
find models -name '*_eval.txt' | xargs -I {} grep -He '^Brier' {} | sort >> $output
