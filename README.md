# Unnamed Subregular Learning Library

## Sources
This repository is a fork and continuation of the work done by Emily Peterson, Cody St. Clair, and Joanne Chau [here](https://github.com/emkp/CSE538_FinalProject).  

The `data-gen` scripts were adapted from https://github.com/kkostyszyn/SBFST_2019. The use of `pynini` was updated for version 2.1.3. Function `rand_gen_no_duplicate()` was replaced with more efficient alternatives. Function `create_adversarial_examples()` was added. Bugs throughout code were fixed. `check.py` was updated. The model, training, and evaluation code are new contributions.

## Dependencies

-   Python >= 3.6
-   Tensorflow >= 2.4.0
-   Pynini >= 2.1.3

## Usage
### Prerequisite setup
The workflow of this codebase was tested using Conda, available through the Anaconda toolkit [here](https://www.anaconda.com/products/individual). First, install Conda. Next, download this repository with the green 'Code' button or via `git`:

```cmd
git clone https://github.com/Dechrissen/subregular.git
```

Open an Anaconda prompt, `cd` to the root of this project's directory, and attempt to install all of the dependencies:

```cmd
pip install -r requirements.txt
```

*Optional*: If `pynini` fails to install via `pip`, use this method to install it individually:

```cmd
conda install -c conda-forge pynini
```

### Data generation
Data (test strings) is generated according to FSAs (in the form of `.fst` files) of given subregular languages. The process of data generation is outlined in the below 3 steps:

#### 1 - `.att` files
Provide a file encoding the possible transitions in a given subregular language in the form of an `.att` file (example below). One file per language should be placed in the `/src/data_gen/lib` directory.
```
0	0	b	b
0	0	c	c
0	0	d	d
0	1	a	a
1	0	b	b
1	0	c	c
1	0	d	d
0
1
```
The `.att` files can be written by hand, but the process can be automated using `plebby`, which is included in The Language Toolkit [here](https://github.com/vvulpes0/Language-Toolkit-2). See [using plebby]().

#### 2 - `att2fst.sh` script

Once all the desired languages (as `.att` files) are placed in `/src/data_gen/lib`, run the `att2fst.sh` script from this directory:

```cmd
./att2fst.sh
```

This will create corresponding `.fst` files (which go in `/src/data_gen/lib/lib_fst`). These files are what `pynini` uses to generate strings in a given language.

#### 3 - `data-gen.py` script

After the `.fst` files are compiled, run `data-gen.py` which is in `/src/data_gen`:

```cmd
python data-gen.py
```

This will generate Training, Dev, Test 1, Test 2, and Test 3 sets for the languages listed in `/tags.txt` and store them in `/src/data_gen/data`. Check whether the data was generated successfully using `check.py`. If any of the files are missing strings, a "missing" or "incomplete" message will be printed to the terminal.  

In `/src/data_gen/data`, there are three subsets generated: `1k`, `10k`, and `100k`. Each one contains `_Training`, `_Dev.txt`, `_Test1.py`, `_Test2.py`, and `_Test3.py` for each language.

### Neural models
The currently supported RNN types are GRU and LSTM.  

#### Training
To train a single model, run `main.py` in `/src/neural_net/tensorflow`. Most of its arguments are self-expanatory, but note that the `--bidi` flag denotes whether the model's RNN is bidirectional. Valid values for `--rnn-type` are either "gru" or "lstm".

- list
- args
- here

#### Testing
To produce a set of predictions from a data file (test set) and a model, run `predict.py` in `/src/neural_net/tensorflow` with the model directory and test set file as arguments. This will output the model's predictions to a file consisting of the name of the test data file + `_pred.txt` in the model's directory. Example:

```cmd
python src/neural_net/tensorflow/predict.py --model-dir "models/BiGRU_NoDrop_SL.4.2.1_100k" --data-file "src/data_gen/data/10k/SL.4.2.0_Test1.txt"
```

To evaluate a model's predictions, run the script `eval.py` in `/src/neural_net/tensorflow`. This program takes a prediction file as produced by `predict.py` and writes to an equivalently-named `_eval.txt` file also in the model's directory. This file reports a number of statistics regarding the model's predictions. Example:

```cmd
python src/neural_net/tensorflow/eval.py --predict-file "models/BiGRU_NoDrop_SL.4.2.1_100k/Test1_pred.txt"
```

#### Batch-training scripts

The scripts `train_all.sh` and `train_all_lstm.sh` do not take any arguments and will produce all of the models examined in `report.pdf`. After they have been run, the scripts `collect_evals.sh` and `collect_evals_lstm.sh` or `evals_csv.py` can be run without arguments to collect all of the evaluation metrics we considered into a single csv file.
