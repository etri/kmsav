# Data Preparation

## Download youtube video
At first download video files from youtube.com using file id in
[data/list.txt](data/list.txt) file. If file id is `AlLW83LkQ4M` then video
link would be `https://youtube.com/watch?v=AlLW83LkQ4M` and the tool like
[yt-dlp](https://github.com/yt-dlp/yt-dlp) can be used. For example,

    yt-dlp --no-simulate -f mp4 -o '/path/to/downloaded/data/%(id)s.%(ext)s' \
       'https://youtube.com/watch?v=AlLW83LkQ4M'

## Download ASR and ASD info files
Download [ASD info file](https://github.com/etri/kmsav/releases/download/v0.2.0/kmsav_asd_v0.2.zip)
from repository, and unzip them. You will get `kmsav_asd_v0.2` directory.

## Crop utterances from video file
It's necessary to extract from the entire video, sentence by sentence as spoken
by the speaker. And among those, we need to select only the facial area to save
as a new video. This is done as following for each video file (`opencv-python`
is required.)

    python3 utils/crop_video.py \
        --asdinfo-dir ./kmsav_asd_v0.2 \
        --save-root ./cropped \
        /path/to/downloaded/data/zuSLzH7rPb0.mp4

This will generate files in `./cropped` dir as:

    ./cropped/
    └── zuSLzH7rPb0
        ├── frames
        │   ├── 000001.jpg
        │   ├── 000002.jpg
        │   ├── 000003.jpg
        ...
        │   ├── 053577.jpg
        │   └── 053578.jpg
        └── utts
            ├── 000003.mp4
            ├── 000003.txt
            ├── 000003.wav
            ├── 000003_audio.mp4
            ├── 000004.mp4
            ├── 000004.txt
            ├── 000004.wav
            ├── 000004_audio.mp4
            ...
            ├── 000231.mp4
            ├── 000231.txt
            ├── 000231.wav
            └── 000231_audio.mp4

`frames` dir contains images of each frame of video file for internal use.
`utts` dir contains video, audio and trasncription of each utterance. The
number is utterance index as defined in ASD info files.

Repeat running `crop_vide.py` for all other videos in train/valid/test set in `list.txt` file
