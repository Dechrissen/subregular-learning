# A script for generating `.plebby` files 
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    ref_k = parser.add_argument('--k', type=int, required=True)
    ref_alph = parser.add_argument('--alph-size', type=int, required=True)

    args = parser.parse_args()

    # argument validitation
    if args.k not in [2,4,8]:
        raise argparse.ArgumentError(ref_k, "k must be 2, 4, or 8")
    if args.alph_size not in [4,16,64]:
        raise argparse.ArgumentError(ref_alph, "alph size must be 4, 16, or 64")

    full_alphabet = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l',
        'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A',
        'B', 'C', 'etc...')

    sub_alphabet = [i for i in full_alphabet[:args.alph_size]]
    universe = ""
    uni = ""
    for i in sub_alphabet:
        uni += "/" + i + " "
    universe = "=universe { " + uni + "}"

    filename = 'test.plebby'
    f = open(filename, 'w')
    f.write(universe)
    f.close()
    print('plebby script successfully generated!')
