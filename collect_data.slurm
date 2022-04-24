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

bash src/collect_evals.sh
python src/evals2csv.py

