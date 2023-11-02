#!/usr/bin/env python3
# Compute WER by comparing two given text; the first is a reference
# transcription, and the second is the hypothesis.
# Both input texts should be in the format of 'uttid' followed by sequence of words.
# 'pip install levenshtein' is required.

import argparse
import Levenshtein
import re

parser = argparse.ArgumentParser(
    description=__doc__, formatter_class=argparse.RawTextHelpFormatter
)
parser.add_argument(
    "ref", metavar="FILE", type=str, help="path to reference transcription"
)
parser.add_argument(
    "hyp", metavar="FILE", type=str, help="path to hypothesis transcription"
)
parser.add_argument(
    "--verbose", action="store_true", help="print WERs for each utterance"
)

args = parser.parse_args()

ref = {}
hyp = {}
for line in open(args.ref, "r"):
    key, *text = line.split()
    ref[key] = text

for line in open(args.hyp, "r"):
    key, *text = line.split()
    hyp[key] = text


N, S, D, I = 0, 0, 0, 0
false_sent = 0
total_sent = len(hyp)
for key in hyp:
    if key not in ref:
        raise Exception(f"no key '{key}' in ref file '{args.ref}'")

    # e = editdistance.eval(ref[key], hyp[key])
    ret = Levenshtein.editops(ref[key], hyp[key])
    i = sum(1 for x in ret if x[0] == "insert")
    d = sum(1 for x in ret if x[0] == "delete")
    s = sum(1 for x in ret if x[0] == "replace")
    n = len(ref[key])

    if i + d + s > 0:
        false_sent += 1
    if args.verbose:
        print(f"{key} {(s+d+i)/n*100:5.2f} {n} {s} {d} {i}")

    N += n
    S += s
    D += d
    I += i

print(f"%WER= {(S+D+I)/N*100:5.2f} [ {S+D+I} / {N}, {I} ins, {D} del, {S} sub ]")
print(f"%SER= {false_sent/len(hyp)*100:5.2f} [ {false_sent} / {len(hyp)} ]")
print(f"Scored {len(hyp)} sentences, {len(ref)-len(hyp)} not present in hyp.")
