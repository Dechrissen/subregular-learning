"""Split the lines of a file evenly over n new files."""

import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("--fname", type=str, default="model_list.txt")
parser.add_argument("--n_files", type=int, default=3)
fname = parser.parse_args().fname
n_files = parser.parse_args().n_files

lines = [line.strip() for line in open(fname, "r").readlines()]
n_lines = len(lines)

lines_per_file, rem = divmod(n_lines, n_files)
lines_list = n_files*[lines_per_file]
lines_list[-1] += rem
print(lines_list)

fname_base = "".join(fname.split(".")[:-1])
for idx in range(n_files):
    with open(f"{fname_base}_{idx}.txt", "w") as f:
        start, end = sum(lines_list[:idx]), sum(lines_list[:idx+1])
        lines_out = lines[start:end]
        f.write("\n".join(lines_out))


