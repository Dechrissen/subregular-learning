# TODO

## Documentation

- [ ] add section to README detailing how to add new subregular languages
- [x] add section to README detailing how to run the evaluation-collection scripts / `csv` creation

## Workflow

- [ ] write `plebby` scripts for each combination of parameters (*k* value and alphabet size): 9 total
  - [x] k = 2 / alph = 4
  - [ ] k = 2 / alph = 16
  - [ ] k = 2 / alph = 64
  - [ ] k = 4 / alph = 4
  - [ ] k = 4 / alph = 16
  - [ ] k = 4 / alph = 64
  - [ ] k = 8 / alph = 4
  - [ ] k = 8 / alph = 16
  - [ ] k = 8 / alph = 64
- [ ] write Python script to automate generation of `plebby` scripts according to some user-specified values
- [x] rewrite shell script template for model training
  - ~~create directory `languages` to store languages (?)~~ this is actually just `/tags.txt`
  - shell script should have parameters that can be tweaked (NN types, languages to use)
- [ ] reorganize `/models` directory and separate into sub-folders for NN type. Other scripts like `predict.py` and `eval.py` might need to updated to use new paths for this

## Codebase

- [x] add check for possible positive string undergeneration in  `data-gen.py` > `create_data_no_duplicate` function
- [ ] add check for possible negative string undergeneration in  `data-gen.py` > `create_data_no_duplicate` function
