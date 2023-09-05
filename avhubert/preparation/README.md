# Prerequisites

## Video Cropping from YouTube Data

1. Download YouTube data using the `kmsav` list file.
2. Process the data to extract and crop the face area from the YouTube videos.
3. For detailed instructions, refer to the document at [kmsav/DataPrepare](../../DataPrepare.md).

# Steps to Prepare Data

## Set up the avhubert Environment

1. Visit the [avhubert GitHub page](https://github.com/facebookresearch/av_hubert).
2. Follow the provided instructions to download and install `avhubert`.

## Data Preparation for avhubert

Before you run the script, adjust the configuration based on your setup:

- `CROP_DIR`: Path to the directory where cropped videos are saved.
- `KMSAV_LIST`: Path to the `kmsav/data/list.txt` file.
- `WORKDIR`: Directory designated for temporary files, extracted video, and
  audio content.
- `OUTDIR`: Directory where the `train`, `valid`, and `test` data for
  `avhubert` will be stored.
- `NJ`: Number of jobs you want to run simultaneously.
- `NGPU`: Number of GPUs to utilize.

Once you've set the configurations, run the provided scripts, which are based
on the [Preparation Guidelines from the avhubert GitHub
repository](https://github.com/facebookresearch/av_hubert/tree/main/avhubert/preparation).

```
CROP_DIR=../../cropped
KMSAV_LIST=/path/to/dir/kmsav/data/list.txt
WORKDIR=./work
OUTDIR=./kmsav
NJ=32

conda activate avhubert

bash kmsav_prepare.sh $CROP_DIR $KMSAV_LIST $WORKDIR

run.pl JOB=1:$NJ dl.JOB.log \
    CUDA_VISIBLE_DEVICES=$\(\(JOB%\$NGPU\)\) python detect_landmark.py \
        --landmark $WORKDIR/landmark --manifest $WORKDIR/file.list \
        --cnn_detector ./mmod_human_face_detector.dat \
        --face_predictor ./shape_predictor_68_face_landmarks.dat \
        --ffmpeg /usr/bin/ffmpeg \
        --root $CROP_DIR \
        --rank $\(\(JOB-1\)\) \
        --nshard $NJ

run.pl JOB=1:$NJ am.JOB.log \
    CUDA_VISIBLE_DEVICES=$\(\(JOB%\$NGPU\)\) python align_mouth.py \
        --video-direc $CROP_DIR \
        --landmark $WORKDIR/landmark \
        --filename-path $WORKDIR/file.list \
        --save-direc $WORKDIR/video \
        --mean-face ./20words_mean_face.npy \
        --ffmpeg /usr/bin/ffmpeg \
        --rank $\(\(JOB-1\)\) \
        --nshard $NJ

run.pl JOB=1:$NJ cf.JOB.log \
   python count_frames.py \
       --root $WORKDIR \
       --manifest $WORKDIR/file.list \
       --rank $\(\(JOB-1\)\) \
       --nshard $NJ

for rank in $(seq 0 $((NJ - 1))); do
    cat $WORKDIR/nframes.audio.${rank}
done > $WORKDIR/nframes.audio
for rank in $(seq 0 $((NJ - 1))); do
    cat $WORKDIR/nframes.video.${rank}
done > $WORKDIR/nframes.video

python kmsav_manifest.py  \
    --data-dir $WORKDIR \
    --vocab-size 5000 \
    --out-dir $OUTDIR \
    --kmsav-list $KMSAV_LIST
```

After executing the script, the contents of `$OUTDIR` will appear as follows:

    kmsav
    ├── dict.wrd.txt
    ├── pretrain.tsv
    ├── pretrain.wrd
    ├── spm5000
    │   ├── spm_unigram5000.model
    │   ├── spm_unigram5000.txt
    │   └── spm_unigram5000.vocab
    ├── test.tsv
    ├── test.wrd
    ├── train.tsv
    ├── train.wrd
    ├── valid.tsv
    └── valid.wrd
