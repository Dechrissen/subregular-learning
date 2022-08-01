import argparse
from os.path import basename, dirname, join
import json

from model import MainModel
from data import *


def load_model_config(config_file):
    with open(config_file, "r") as f:
        config = json.load(f)
    return config


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", type=str, required=True)
    args = parser.parse_args()

    model_dir = dirname(args.model_dir)
    vocab_file = join(model_dir, "vocab.txt")
    vocabulary = load_vocab(vocab_file)

    config = load_model_config(f"{model_dir}/config.json")
    model = MainModel(**config)
    model.load_weights(f"{model_dir}/checkpoint.ckpt")

    model.build((None, 64))
    model.summary()
