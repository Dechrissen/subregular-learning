# TODO

## Documentation

- [x] add section to README detailing how to add new subregular languages
- [x] add section to README detailing how to run the evaluation-collection scripts / `csv` creation
- [ ] add section to README explaining `ins.txt` and `outs.txt`

## Workflow

- [ ] write `plebby` scripts for each combination of parameters (*k* value and alphabet size): 9 total
  - [x] k = 2 / alph = 4
  - [x] k = 2 / alph = 16
  - [x] k = 2 / alph = 64
  - [ ] k = 4 / alph = 4
  - [ ] k = 4 / alph = 16
  - [ ] k = 4 / alph = 64
  - [ ] k = 8 / alph = 4
  - [ ] k = 8 / alph = 16
  - [ ] k = 8 / alph = 64
- [ ] ~~write Python script to automate generation of `plebby` scripts according to some user-specified values~~
- [x] rewrite shell script template for model training
  - ~~create directory `languages` to store languages (?)~~ this is actually just `/tags.txt`
  - shell script should have parameters that can be tweaked (NN types, languages to use)
- [ ] reorganize `/models` directory and separate into sub-folders for NN type. Other scripts like `predict.py` and `eval.py` might need to updated to use new paths for this
- [x] reorganize repo structure
- [x] automate the generation of `.fst` files into their specified directory, instead of being generated in the same directory as the corresponding `.att` files (update `att2fst.sh`)

## Codebase

- [x] add check for possible positive string undergeneration in  `data-gen.py` > `create_data_no_duplicate` function
- [x] add check for possible negative string undergeneration in  `data-gen.py` > `create_data_no_duplicate` function
- [x] change paths (`path_to_fsa`, `my_fsa`, `dir_name`) in `data-gen.py`
