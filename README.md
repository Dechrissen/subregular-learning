# Unnamed Subregular Learning Library

## Sources
This repository is a fork and continuation of the work done by Emily Peterson, Cody St. Clair, and Joanne Chau [here](https://github.com/emkp/CSE538_FinalProject). A summary of the results from their work is in `/docs/2020_report.pdf`.

The `data-gen` scripts were adapted from https://github.com/kkostyszyn/SBFST_2019. The use of `pynini` was updated for version 2.1.3. Function `rand_gen_no_duplicate` was replaced with more efficient alternatives (`alternate_rand_gen_no_duplicate`). Function `create_adversarial_examples` was added. Bugs throughout code were fixed. `check.py` was updated. The model, training, and evaluation code are new contributions.

## Dependencies

-   Python >= 3.6
-   Tensorflow >= 2.4.0
-   Pynini >= 2.1.3

## Usage
1. [Prerequisite setup](#prerequisite-setup)
2. [Data generation](#data-generation)
3. [Neural models](#neural-models)
4. [Collecting evaluations](#collecting-evaluations)
5. [Adding new languages](#adding-new-languages)

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
Data for each language (sets of strings) is generated according to FSAs (in the form of `.fst` files) of given subregular languages. The process of data generation is outlined in the below 3 steps:

#### 1 - `.att` files
Provide a file encoding the possible transitions in a given subregular language in the form of an `.att` file (example below). One file per language should be placed in the `/src/data_gen/lib/` directory.
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
The `.att` files can be written by hand, but the process can be automated using `plebby`, which is included in The Language Toolkit [here](https://github.com/vvulpes0/Language-Toolkit-2). (See [Adding new languages](#adding-new-languages))

#### 2 - `att2fst.sh` script

Once all the desired languages (as `.att` files) are placed in `/src/data_gen/lib/`, run the `att2fst.sh` script from this directory:

```cmd
./att2fst.sh
```

This will create corresponding `.fst` files (which go in `/src/data_gen/lib/lib_fst/`). These files are what `pynini` uses to generate strings in a given language.

#### 3 - `data-gen.py` script

After the `.fst` files are compiled, run `data-gen.py` which is in `/src/data_gen/`:

```cmd
python /src/data_gen/data-gen.py
```

This will generate Training, Dev, Test 1, Test 2, and Test 3 sets for the languages listed in `/tags.txt` and store them in `/src/data_gen/data/`. Check whether the data was generated successfully using `check.py`. If any of the files are missing strings, a "missing" or "incomplete" message will be printed to the terminal.  

In `/src/data_gen/data/`, there are three subsets generated: `1k`, `10k`, and `100k`. Each one contains `_Training.txt`, `_Dev.txt`, `_Test1.txt`, `_Test2.txt`, and `_Test3.txt` for each language.

#### `check.py` script

The script `check.py` in `/src/data_gen/` will check the `data` directory for the generated data. For each file size subset (1k, 10k, 100k) the 5 datasets for each language will be checked to determine if they exist/have sufficient strings. For each dataset, `missing` will be output if it doesn't exist, or `incomplete` will be output if the dataset hasn't achieved its designated file size (along with the amount it stopped at).

### Neural models
The currently supported RNN types are s-RNN, GRU and LSTM.  

#### Training
To train a single model, run `main.py` in `/src/neural_net/tensorflow/`. Most of its arguments are self-expanatory, but note that the `--bidi` flag denotes whether the model's RNN is bidirectional. Example:

```cmd
python src/neural_net/tensorflow/main.py --batch-size 64 --epochs 30 --embed-dim 100 --rnn-type gru --dropout 0 --bidi False --train-data "/src/data_gen/data/100k/SL.4.2.0_Training.txt" --val-data "/src/data_gen/data/100k/SL.4.2.0_Dev.txt" --output-dir "/src/models"
```

Possible arguments for `main.py` are below (along with indications of whether they are required):

- `'--train-data', type=str, required=True`
- `'--val-data', type=str, required=True`
- `'--output-dir', type=str, required=True`
- `'--batch-size', type=int, default=64`
- `'--epochs', type=int, default=10`
- `'--embed-dim', type=int, default=100`
- `'--dropout', type=float, default=0.2`
- `'--rnn-type', type=str, default="simple"` (valid values: "simple", "gru" or "lstm")
- `'--bidi', type=bool, default=False`

#### Testing
To produce a set of predictions from a data file (test set) and a trained model, run `predict.py` in `/src/neural_net/tensorflow/` with the model directory and test set file as arguments. This will output the model's predictions to a file consisting of the name of the test data file + `_pred.txt` in the model's directory. Example:

```cmd
python src/neural_net/tensorflow/predict.py --model-dir "models/Bi_lstm_NoDrop_SL.4.2.1_100k" --data-file "src/data_gen/data/10k/SL.4.2.0_Test1.txt"
```

To evaluate a model's predictions, run the script `eval.py` in `/src/neural_net/tensorflow/`. This program takes a prediction file as produced by `predict.py` and writes to an equivalently-named `_eval.txt` file also in the model's directory. This file reports a number of statistics regarding the model's predictions. Example:

```cmd
python src/neural_net/tensorflow/eval.py --predict-file "models/BiGRU_NoDrop_SL.4.2.1_100k/Test1_pred.txt"
```

#### Batch-training script
The script `batch_train.sh` will train multiple models according to the parameters at the top of the file under the heading 'PARAMETERS TO EDIT' (shown below). This script depends on the languages listed in `/tags.txt` (one language per line) which must also have a corresponding `.fst` file in `/src/data_gen/lib/lib_fst/`.
```{bash}
UNIVERSAL_ARGS=( --batch-size 64 --epochs 30 --embed-dim 100 )
rnn_type="simple" # simple / gru / lstm
```
These default values can be tweaked as needed. The `UNIVERSAL_ARGS` list can be edited to vary the batch size, epochs, and embedding layers. The `rnn_type` value can be changed to any of the 3 supported neural network types. With the configuration above, the script will train s-RNN models for all the languages listed in `/tags.txt`, one for each data size.  

For each model, the script will also run `predict.py` for each test set to generate three `_pred.txt` files. Then, it will run `eval.py` on each prediction file. These files are all generated in the corresponding model's directory.

### Collecting evaluations

After models have been trained and evaluated (i.e. `_eval.txt` files exist in `/models/`), run the script `collect_evals.sh`. This will collect all of the `_eval.txt` files present in `/models/` and output their evaluation metrics (currently F score and accuracy) into `/all_evals.txt`.  

To organize these results nicely into a `.csv` file, run `/evals2csv.py`. This will generate a file `/all_evals.csv`.

### Adding new languages

(Need to add info here to explain how to add languages and describe the `subreglib` directory.)
