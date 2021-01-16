# TODO

## Documentation

- [ ] add section to README detailing how to add new subregular languages

## Workflow

- [ ] write `plebby` scripts for each combination of parameters (*k* value and alphabet size): 9 total
  - k = {2,4,8}
  - alphabet size = {4,16,64}
- [ ] rewrite shell script template for model training
  - create directory `languages` to store languages (?)
  - shell script should have parameters that can be tweaked (NN types, languages to use)
- reorganize `/models` directory and separate into sub-folders for NN type. Other scripts like `predict.py` and `eval.py` might need to updated to use new paths for this

## Codebase

- [x] add check for possible positive string undergeneration in  `data-gen.py` > `create_data_no_duplicate` function
- [ ] add check for possible negative string undergeneration in  `data-gen.py` > `create_data_no_duplicate` function
