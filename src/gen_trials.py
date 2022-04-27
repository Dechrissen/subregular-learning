import argparse
from itertools import product

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--langs_file", type=str, default="train_langs.txt")
    parser.add_argument("--fname_out", type=str, default="model_list.txt")
    langs_file = parser.parse_args().langs_file
    fname_out = parser.parse_args().fname_out

    langs = [
        lang.strip()
        for lang in open(langs_file, "r", encoding="utf8").readlines()
    ]
    sizes = ["Small", "Mid", "Large"]
    network_types = ["simple", "gru", "lstm", "stackedrnn", "transformer"]
    model_grid = product(langs, sizes, network_types)

    output_file = open(fname_out, "w+", encoding="utf8")

    for lang, size, network_type in model_grid:
        output_file.write(f"{lang} {size} {network_type}\n")
                
    output_file.close()
