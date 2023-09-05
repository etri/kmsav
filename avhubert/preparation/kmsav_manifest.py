# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import os
import glob
import shutil
import subprocess
from tqdm import tqdm
from pathlib import Path
from gen_subword import gen_vocab
from tempfile import NamedTemporaryFile
import argparse

def get_split_info(info_file_path):
    split_info = {"train":[], "test":[], "pretrain":[], "valid":[]}
    for line in open(info_file_path, "r"):
        line = line.strip()
        if line[0] == '#':
            continue
        w = line.split()
        split_info[w[-1]].append(w[0])
    return split_info

def main():
    parser = argparse.ArgumentParser(
        description="tsv preparation for KMSAV dataset",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--out-dir", type=str, help="output dir to store files for training"
    )
    parser.add_argument(
        "--data-dir", type=str, help="path to work dir storing file.list"
    )
    parser.add_argument(
        "--vocab-size", type=int, default=1000, help="a list of valid ids"
    )
    parser.add_argument(
        "--video_ext", type=str, default="mp4", help="video file extension"
    )
    parser.add_argument(
        "--kmsav-list", type=str, required=True, help="path to kmsav list.txt"
    )
    args = parser.parse_args()

    file_list, label_list = (
        f"{args.data_dir}/file.list",
        f"{args.data_dir}/label.list",
    )
    assert os.path.isfile(
        file_list
    ), f"{file_list} not exist -> run kmsav_prepare.sh first"
    assert os.path.isfile(
        label_list
    ), f"{label_list} not exist -> run kmsav_prepare.sh first"

    nframes_audio_file, nframes_video_file = (
        f"{args.data_dir}/nframes.audio",
        f"{args.data_dir}/nframes.video",
    )
    assert os.path.isfile(
        nframes_audio_file
    ), f"{nframes_audio_file} not exist -> run count_frames.py first"
    assert os.path.isfile(
        nframes_video_file
    ), f"{nframes_video_file} not exist -> run count_frames.py first"

    print(f"Generating sentencepiece units")
    vocab_size = args.vocab_size
    vocab_dir = (Path(f"{args.out_dir}") / f"spm{vocab_size}").absolute()
    # out_root = Path(vocab_dir).absolute()
    vocab_dir.mkdir(parents=True, exist_ok=True)
    spm_filename_prefix = f"spm_unigram{vocab_size}"
    with NamedTemporaryFile(mode="w", encoding="utf-8") as f:
        label_text = [
            ln.strip() for ln in open(label_list, "r", encoding="utf-8").readlines()
        ]
        for t in label_text:
            f.write(t.lower() + "\n")
        gen_vocab(
            Path(f.name), vocab_dir / spm_filename_prefix, "unigram", args.vocab_size
        )
    vocab_path = (vocab_dir / spm_filename_prefix).as_posix() + ".txt"

    audio_dir, video_dir = f"{args.data_dir}/audio", f"{args.data_dir}/video"

    def setup_target(target_dir, pretrain, train, valid, test):
        for name, data in zip(
            ["pretrain", "train", "valid", "test"], [pretrain, train, valid, test]
        ):
            with open(f"{target_dir}/{name}.tsv", "w") as fo:
                fo.write("/\n")
                for fid, _, nf_audio, nf_video in data:
                    fo.write(
                        "\t".join(
                            [
                                fid,
                                os.path.abspath(f"{video_dir}/{fid}.{args.video_ext}"),
                                os.path.abspath(f"{audio_dir}/{fid}.wav"),
                                str(nf_video),
                                str(nf_audio),
                            ]
                        )
                        + "\n"
                    )
            with open(f"{target_dir}/{name}.wrd", "w") as fo:
                for _, label, _, _ in data:
                    fo.write(f"{label}\n")
        shutil.copyfile(vocab_path, f"{target_dir}/dict.wrd.txt")
        return

    fids, labels = (
        [x.strip() for x in open(file_list, "r", encoding="utf-8").readlines()],
        [
            x.strip().lower()
            for x in open(label_list, "r", encoding="utf-8").readlines()
        ],
    )

    nfs_audio, nfs_video = [x.strip() for x in open(nframes_audio_file).readlines()], [
        x.strip() for x in open(nframes_video_file).readlines()
    ]
    #valid_fids = set([x.strip() for x in open(args.valid_ids).readlines()])

    split_info = get_split_info(args.kmsav_list)

    pretrain, train, valid, test = [], [], [], []
    for fid, label, nf_audio, nf_video in zip(fids, labels, nfs_audio, nfs_video):
        part = fid.split('/')[0]
        # print(part)
        if part in split_info['test']:
            test.append([fid, label, nf_audio, nf_video])
        elif part in split_info['valid']:
            valid.append([fid, label, nf_audio, nf_video])
        elif part in split_info['train']:
            train.append([fid, label, nf_audio, nf_video])
        else:
            pretrain.append([fid, label, nf_audio, nf_video])
    kmsav_preprocessed_dir = f"{args.out_dir}"
    print(f"Set up preprocessed kmsav data dir")
    os.makedirs(kmsav_preprocessed_dir, exist_ok=True)
    setup_target(kmsav_preprocessed_dir, pretrain, train, valid, test)
    return


if __name__ == '__main__':
    main()
