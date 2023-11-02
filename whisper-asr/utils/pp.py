#!/usr/bin/env python3
# Normalize text to compute WER, including
# removing pucutation marks(.,?!), special tags etc., and
# splitting words into characters.

import argparse
import sys
import re


def subline(
    line, remove_words=[], remove_char="", remove_string=[], remove_re=[], toupper=True
):
    for w in remove_string:
        line = line.replace(w, "")

    for w in remove_re:
        line = re.sub(w, "", line)

    if len(remove_char) > 0:
        line = re.sub(f"[{remove_char}]", " ", line)

    if len(remove_words) > 0:
        words = line.split()
        new_words = [word for word in words if word not in remove_words]
        line = " ".join(new_words)

    if toupper:
        line = line.upper()

    return line


parser = argparse.ArgumentParser(
    description=__doc__, formatter_class=argparse.RawTextHelpFormatter
)
parser.add_argument(
    "infile",
    metavar="FILE",
    nargs="?",
    type=argparse.FileType("r"),
    default=sys.stdin,
    help="input filename",
)
parser.add_argument("-s", "--split-char", action="store_true", help="split char")
parser.add_argument("--remove-string", type=str, default="", help="strings to remove")
parser.add_argument("--remove-word", type=str, default="", help="words to remove")
parser.add_argument(
    "--remove-re", type=str, default="\([^)]*\)", help="reg exp to remove"
)
parser.add_argument("--remove-char", type=str, default=".,?!", help="chars to remove")

args = parser.parse_args()

remove_word = args.remove_word.split(",")
remove_string = args.remove_string.split(",")
remove_re = args.remove_re.split(",")
for line in args.infile:
    line = line.strip()
    header, *nline = line.split(None, 1)
    if len(nline) == 0:
        print(header, file=args.outfile)
    else:
        line = subline(
            " ".join(nline), remove_word, args.remove_char, remove_string, remove_re
        )
        if args.split_char:
            print(header, " ".join(list("".join(line.split()))))
        else:
            print(header, " ".join(line.split()))
