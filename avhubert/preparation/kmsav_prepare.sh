#!/bin/bash -eu
CROP_DIR=$1 # Path to the directory where cropped videos are saved.
LIST=$2     # Path to the kmsav/data/list.txt file
OUTDIR=$3   # Directory designated for temporary files, extracted video,
            # and audio content.

mkdir -p $OUTDIR
for d in $CROP_DIR/*; do
    id=$(basename $d)
    if `cut -f 1 -d ' ' $LIST | grep -wq -- "$id" 2> /dev/null`; then
        find $d -name "*.mp4"
    fi
done | sed "s,\.mp4$,,;s,^$CROP_DIR/,," | sort | grep -v "_audio" > $OUTDIR/file.list


for f in `cat $OUTDIR/file.list`; do
    txt=$CROP_DIR/$f.txt
    tr -s '\n' ' ' < $txt
    echo ''
done > $OUTDIR/label.list

rev $OUTDIR/file.list | cut -f 2- -d/ | rev | sort -u | \
    sed "s,^,$OUTDIR/audio/," | xargs mkdir -p
for f in `cat $OUTDIR/file.list`; do
    cp $CROP_DIR/$f.wav $OUTDIR/audio/$f.wav
done



