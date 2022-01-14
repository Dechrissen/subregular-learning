#!/bin/bash
#
#SBATCH --job-name=collect
#SBATCH --output=/dev/null
#SBATCH --ntasks-per-node=40
#SBATCH --nodes=2
#SBATCH --time=4:00:00
#SBATCH -p short-40core
#SBATCH --mail-type=BEGIN,END
#SBATCH --mail-user=sam.vanderpoel@stonybrook.edu

module load anaconda/3

output=all_evals.txt
find models -name '*_eval.txt' | xargs -I {} grep -He '^F-score' {} | sort | tee $output
find models -name '*_eval.txt' | xargs -I {} grep -He '^Accuracy' {} | sort | tee -a $output
find models -name '*_eval.txt' | xargs -I {} grep -He '^AUC' {} | sort | tee -a $output

python src/evals2csv.py

