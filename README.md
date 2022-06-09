# Subregular Language Library for Machine Learning

This repository provides many regular languages from distinct well-understood subregular language classes, instantiating a benchmark for machine learning models. The desired outcome is to better understand the kinds of sequential patterns neural networks in particular are able to learn successfuly and under what conditions. Some motivation is provided in [Avcu et al. (2017) paper "Subregular Complexity and Deep Learning"](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&ved=2ahUKEwjggda6gaTuAhVRElkFHcpJD4kQFjACegQIBhAC&url=http%3A%2F%2Fprojects.illc.uva.nl%2FLaCo%2Fclclab%2Fmedia%2Fpdfs%2F2017%2Fvelhoen2017.pdf&usg=AOvVaw3YNi86XUzp5U_I1sKb6u_I).
The regular languages themselves are based on logical and algebraic structure, forming the subregular language hierarchy (see [Rogers and Pullum 2011](https://link.springer.com/article/10.1007/s10849-011-9140-2) and [Rogers et al. 2013](https://link.springer.com/chapter/10.1007%2F978-3-642-39998-5_6)).

## Contents
1. [Setup](#setup)
2. [Data generation](#data-generation)
3. [Neural networks](#neural-networks)
4. [Managing language names](#managing-language-names)
5. [Collecting evaluations](#collecting-evaluations)
6. [Adding new languages](#adding-new-languages)

# Setup
This codebase was tested on Linux using [Conda](https://www.anaconda.com/products/individual). Clone and cd into this repository:

```cmd
git clone https://github.com/heinz-jeffrey/subregular-learning.git
cd subregular-learning
```

Requirements include Python >= 3.6, Tensorflow >= 2.4.0, and Pynini == 2.1.2. To create a conda environment with all necessary libraries, run

```
conda env create -f subreg_env.yml
conda activate subreg
```

or

```
conda create --name subreg python=3.9 numpy tensorflow scikit-learn matplotlib
conda activate subreg
conda install -c conda-forge pynini=2.1.2
```

# Data generation
Data for each language is generated according to an FSA (in the form of an `.fst` file) of a given subregular language. The process of data generation is outlined in the following three steps.

## 1 - `.att` files
Provide a file encoding the possible transitions in a given subregular language in the form of an `.att` file (example below). One file per language should be placed in the `/src/fstlib/att_format` directory.
```
0   0   b   b
0   0   c   c
0   0   d   d
0   1   a   a
1   0   b   b
1   0   c   c
1   0   d   d
0
1
```
The `.att` files can be written by hand, but this is time-consuming and error-prone. We recommend writing automata with software such as [openfst](http://www.openfst.org/twiki/bin/view/FST/WebHome) currently maintained by researchers at Google, or `plebby`, which is included in [The Language Toolkit](https://github.com/vvulpes0/Language-Toolkit-2) by Dakotah Lambert. We have used `plebby` for specifying the acceptors and `openfst` for data generation through its Python wrapper [Pynini](http://www.openfst.org/twiki/bin/view/GRM/Pynini). (See [Adding new languages](#adding-new-languages))

## 2 - `att2fst.sh` script

This script has 3 dependencies: (1) `.att` files, (2) `ins.txt` (input symbols) and (3) `outs.txt` (output symbols), all of which should go in `/src/fstlib/att_format`. The `ins.txt` and `outs.txt` files currently in the repo are set up for a max of 64 universe symbols and their UTF-8 encodings. Should you want to support more than 64 symbols, you should modify the script `/src/fstlib/att_format/make-ins-and-outs.py`and run it (the `ins.txt` and `outs.txt` generated should also be copied into `/src/subreglib`).

Once all the desired languages (as `.att` files) and `ins.txt` & `outs.txt` are in `/src/fstlib/att_format`, run the `att2fst.sh` script from the `fstlib` directory:

```cmd
./att2fst.sh
```

This will create corresponding `.fst` files (which are output to `src/fstlib/fst_format`). These are binary files which can be processed by `openfst` and are what `pynini` uses to generate strings in a given language.

## 3 - `data-gen.py` script

After the `.fst` files are compiled, `src/data-gen.py` is used to generate data for regular languages, taking one argument specifying the language name. For example, to generate data for 16.04.TLTT.4.2.4 we run

```cmd
python src/data-gen.py --lang 16.04.TLTT.4.2.4
```

This will generate a training set, a validation set, and four test sets for each of three sizes (Small: 1k lines, Mid: 10k lines, Large: 100k lines) stored in `data_gen`.

The command `src/lang_names.py --action data_gen_done` prints language names for which data generation is complete. (See more on `src/lang_names.py` in the section [Managing language names](#managing-language-names).)

## About the training, dev, and test data

- **Training** data contains equal numbers of positive and negative strings between the lengths of 20 and 29.
- **Dev** (validation) data contains equal numbers of positive and negative strings between the lengths of 20 and 29 which are disjoint from Training.
- **TestSR** (short random test) data contains equal numbers of positive and negative strings between the lengths of 20 and 29 which are disjoint from both Training and Dev.
- **TestSA** data contains equal numbers of positive and negative strings between the lengths of 20 and 29; in particular, each positive string *x* is paired with a negative string *y* such that the string edit distance of *(x,y)* is 1.
- **TestLR** (long random test) data contains equal numbers of positive and negative strings between the lengths of 31 and 50 which are disjoint from both Training and Dev.
- **TestLA** data contains equal numbers of positive and negative strings between the lengths of 31 and 50; in particular, each positive string *x* is paired with a negative string *y* such that the string edit distance of *(x,y)* is 1.

Equal numbers of strings of each length in the selected length range are chosen. Under these constraints, the strings themselves are randomly selected uniformly.

# Neural networks
The currently supported neural network types are simple RNNs, GRUs, LSTMs, stacked LSTMs, and multi-head attention models.

## Training
To train a single model, run `main.py` in `src/neural_net/tensorflow`. Most of its arguments are self-expanatory, but note that the `--bidi` flag denotes whether an RNN is bidirectional. Example:

```cmd
python3 src/neural_net/tensorflow/main.py --rnn-type gru --train-data data_gen/Small/16.04.TLTT.4.2.4_Train.txt --val-data data_gen/Small/16.04.TLTT.4.2.4_Dev.txt --output-dir models/Uni_gru_NoDrop_16.04.TLTT.4.2.4_Small/
```

Possible arguments for `main.py` are below (along with indications of whether they are required):

- `'--train-data', type=str, required=True`
- `'--val-data', type=str, required=True`
- `'--output-dir', type=str, required=True`
- `'--batch-size', type=int, default=64`
- `'--epochs', type=int, default=30`
- `'--embed-dim', type=int, default=100`
- `'--dropout', type=float, default=0.2`
- `'--rnn-type', type=str, required=True` (valid values: "simple", "gru", "lstm", "stackedrnn", "transformer")
- `'--bidi', type=bool, default=False`

## Testing
Neural networks are automatically tested on all four test sets (SR, SA, LR, LA) in `main.py` after training completes. To run additional tests individually, use `src/neural_net/tensorflow/predict.py`, for example:

```
python src/neural_net/tensorflow/predict.py --model-dir models/Uni_gru_NoDrop_16.04.TLTT.4.2.4_Small/ --data-file data_gen/Small/16.04.TLTT.4.2.4_TestLA.txt
```

The predictions resulting from the above command can be evaluated as follows:

```cmd
python src/neural_net/tensorflow/eval.py --predict-file models/Uni_gru_NoDrop_16.04.TLTT.4.2.4_Small/TestLA_pred.txt
```

which produces an evaluation file recording various test metrics including accuracy, F-score, precision, and Brier score, among others.

# Managing language names
With support for 1980 regular languages and thousands of neural models, tracking the progress of languages and models throughout the data generation, training, and evaluation process in an organized way is crucial. The script `src/lang_names.py` accomplishes this by printing to stdout those language names satisfying a certain condition. The condition under which to print language names is specified with the argument `--action`, which has the following options:
- `--action all_fst`: print language names having an associated .fst file in `src/fstlib/fst_format`
- `--action all_langs`: print language names having an associated .fst file as well as any langauges with data in `data_gen` (this includes completmentary languages e.g. coSL, coSP, etc.)
- `--action data_gen_done`: prints languages names for which data generation is complete
- `--action train_done`: prints language names for which training and evaluation of all neural models is complete

If the argument `--avoid filename` is passed to `src/lang_names.py`, then the lines of `filename` (consisting of language names) will not be printed by `src/lang_names.py`.

Typical use cases of `src/lang_names.py` include the following.
- Writing to file those languages whose data generation is not complete:
```
python src/lang_names.py --action data_gen_done > data_gen_done.txt
python src/lang_names.py --action all_langs --avoid data_gen_done.txt > data_gen_not_done.txt
```
- Writing to file those languages whose data generation is complete but whose model training and evaluation is not complete:
```
python src/lang_names.py --action train_done > train_done.txt
python src/lang_names.py --action data_gen_done --avoid train_done.txt > train_langs.txt
```

The script `src/gen_trials.py` converts a file of language names into a file of neural model specifications. It accepts a file name via the argument `--langs_file` (e.g. a file output by `src/lang_names.py`) and writes by default to `model_list.txt`, the lines of which are model specifications.

# Collecting evaluations

After models have been trained and evaluated, the following commands parse all model evaluation files and collect them in a comprehensive table stored in `all_evals.csv`:

```
bash src/collect_evals.sh
python src/evals2csv.py
```

# Adding new languages

`src/subreglib` contains `.plebby` files that can be used with `plebby`, included in [The Language Toolkit](https://github.com/vvulpes0/Language-Toolkit-2) by Dakotah Lambert. Each file specifies the acceptors for various languages and, after being run via `plebby`, outputs `.att` files for each language. A usage guide for `plebby` is [here](https://github.com/vvulpes0/Language-Toolkit-2/blob/master/docs/plebbyGuide.txt). For more info about the organization of `.plebby` files for use in this library, refer to the README in `src/subreglib` .

# Acknowledgements

This repository is a continuation of work reported by [Avcu et al. (2017)](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&ved=2ahUKEwjggda6gaTuAhVRElkFHcpJD4kQFjACegQIBhAC&url=http%3A%2F%2Fprojects.illc.uva.nl%2FLaCo%2Fclclab%2Fmedia%2Fpdfs%2F2017%2Fvelhoen2017.pdf&usg=AOvVaw3YNi86XUzp5U_I1sKb6u_I). The code here evolved from Andersen's [repository](https://github.com/Dechrissen/subregular-learning), which in turn inherited from Peterson, St. Clair, and Chau's work [here](https://github.com/emkp/CSE538_FinalProject) as well as Kostyszyn's [repository](https://github.com/kkostyszyn/SBFST_2019).

The latest installment of this work is supervised by Jeffrey Heinz, with primary contributions from Kalina Kostyszyn, Dakotah Lambert, and Sam van der Poel.

The following researchers have all contributed to the development of this project.

- [Derek Andersen (CompLing MA 2021)](https://github.com/Dechrissen)
- [Joanne Chau (CompLing MA 2020)](https://github.com/joannechau)
- Paul Fodor (Professor of Instruction, CS)
- Tiantian Gao (CS, PhD 2019)
- [Jeffrey Heinz (Professor, Linguistics & IACS)](http://jeffreyheinz.net/)
- [Dakotah Lambert (Ling, current PhD)](https://github.com/vvulpes0)
- [Kalina Kostyszyn (Ling, current PhD)](https://github.com/kkostyszyn)
- [Emily Peterson (Ling, CompLing MA 2020)](https://github.com/emkp)
- Chihiro Shibata (Professor, Hosei University)
- [Cody St. Clair (Ling MA 2020)](https://github.com/cody-stclair)
- [Sam van der Poel (Georgia Tech PhD student)](https://github.com/samvanderpoel)
- Rahul Verma (CS, MS 2018)
