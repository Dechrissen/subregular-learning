#!/bin/bash

<<<<<<< HEAD
output=all_evals.txt

find models -name '*_eval.txt' | xargs -I {} grep -He '^F-score' {} | sort | tee $output

find models -name '*_eval.txt' | xargs -I {} grep -He '^Accuracy' {} | sort | tee -a $output
=======
find models -name '*_eval.txt' | xargs -I {} grep -He '^F-score' {} | sort | ./format_evals.awk
>>>>>>> 39eacea25cf20194192926b2243a2b5ed41ec735
