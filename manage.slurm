#!/bin/bash
#
#SBATCH --job-name=manage
#SBATCH --output=/dev/null
#SBATCH --ntasks-per-node=40
#SBATCH --nodes=2
#SBATCH --time=4:00:00
#SBATCH -p short-40core
#SBATCH --mail-type=BEGIN,END
#SBATCH --mail-user=sam.vanderpoel@stonybrook.edu

module load anaconda/3

python src/update_done.py
python src/manage_datagen.py --rmlangs
python src/lang_names.py --datagen > datagen_tags.txt
python src/lang_names.py --train --avoid src/langs_done.txt > train_tags.txt
python src/gen_trials.py

