#!/usr/bin/env python3

import argparse
import json
import os
import glob
import re

parser = argparse.ArgumentParser(
    description="Convert Whisper json output into Kaldi text file"
)
parser.add_argument("dir", metavar="result-dir", type=str, help="Whisper result dir")
parser.add_argument(
    "--remove-punc", choices=("True", "False"), help="remove puncutation marks",
    default="False",
)
args = parser.parse_args()

regexps = [
        (re.compile(r'[.,?"]', re.I|re.M), r''),
        ]

def normalize_text(script):
    for reg, rep in regexps:
        script = reg.sub(rep, script)
    return script

json_files = glob.glob(os.path.join(args.dir, "*.json"))
for f in json_files:
    rlt = json.load(open(f, "r"))

    uid = os.path.splitext(os.path.basename(f))[0]
    if args.remove_punc:
        print(uid, normalize_text(rlt["text"].strip()))
    else:
        print(uid, rlt["text"].strip())
