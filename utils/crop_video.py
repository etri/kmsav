import os
import glob
import argparse
import subprocess
import sys
import cv2
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s (%(module)s:%(lineno)d) %(levelname)s: %(message)s",
)


def init_save_root(args):
    fileid = os.path.splitext(os.path.basename(args.video_path))[0]
    frames_dir = os.path.join(args.save_root, fileid, "frames")
    utt_dir = os.path.join(args.save_root, fileid, "utts")

    if not args.dry_run:
        os.makedirs(args.save_root, exist_ok=True)
        os.makedirs(utt_dir, exist_ok=True)
        os.makedirs(frames_dir, exist_ok=True)

    return frames_dir, utt_dir


def avi2images(video_path, frames_path, fps):
    # convert every frames in avi to jpg files
    # enforcing fps to given fps
    imgfile = os.path.join(frames_path, f"{1:06}.jpg")
    if os.path.exists(imgfile):
        logging.info(f"{imgfile} exists. re-using it.")
        return
    try:
        output_path = os.path.join(frames_path, "%06d.jpg")
        command = (
            f"ffmpeg -y -i {video_path} -qscale:v 2 -vf fps={fps}"
            f" -f image2 {output_path} -loglevel quiet",
        )
        output = subprocess.check_call(command, shell=True, stdout=None)
    except subprocess.CalledProcessError as e:
        logging.error(f"ffmpeg failed with error message: {e.stderr}")
        sys.exit(-1)


def adjust_av_index(fstart_a, fend_a, frame_list):
    fstart_v = int(frame_list[0][0])
    fend_v = int(frame_list[-1][0])

    header = []
    footer = []
    if fstart_a < fstart_v:
        for frame in range(fstart_a, fstart_v):
            header.append([frame, *frame_list[0][1:]])
    else:
        frame_list[: fstart_a - fstart_v] = []

    if fend_a > fend_v:
        for frame in range(fend_v + 1, fend_a + 1):
            footer.append([frame, *frame_list[-1][1:]])
    else:
        frame_list[-(fend_v - fend_a) :] = []

    return header + frame_list + footer


def crop_video(utt_index, point_list, flist, outdir):
    # calculate the maximum length of the part to crop
    width_list, height_list = list(zip(*point_list))[3:]
    max_width = max(list(map(int, width_list)))
    max_height = max(list(map(int, height_list)))

    video_path = os.path.join(outdir, utt_index + ".mp4")
    vOut = cv2.VideoWriter(
        video_path,
        cv2.VideoWriter_fourcc(*"mp4v"),
        25,
        (224, 224),
    )

    try:
        for index, frame in enumerate(point_list):
            iframe = [max(0, int(x)) for x in frame]
            image = cv2.imread(flist[max(0, min(len(flist) - 1, iframe[0] - 1))])
            crop_area = image[
                iframe[2] : iframe[2] + max_height, iframe[1] : iframe[1] + max_width
            ]

            vOut.write(cv2.resize(crop_area, (224, 224)))
    except:
        logging.error(f"ERROR while processing {video_path}")
        raise
    vOut.release()

    return video_path


def combine_audio(video_path, audio_path, audio_start, audio_end):
    video_out, ext = os.path.splitext(video_path)
    audio_out = video_out + ".wav"
    video_out = video_out + "_audio" + ext
    command = (
        f"ffmpeg -y -i {audio_path} -async 1 -ac 1 -vn -acodec pcm_s16le"
        f" -ar 16000 -ss {audio_start} -to {audio_end} {audio_out}"
        f" -loglevel panic"
    )
    print(command)
    output = subprocess.check_call(command, shell=True, stdout=None)  # Crop audio file

    command = (
        f"ffmpeg -y -i {video_path} -i {audio_out} -c:v copy -c:a aac"
        f" {video_out} -loglevel panic"
    )
    output = subprocess.check_call(command, shell=True, stdout=None)
    return audio_out


def crop_all_utts(args, frames_dir, utt_dir):
    # get vidio and audio name
    audio_path = os.path.splitext(args.video_path)[0] + ".wav"
    fileid = os.path.basename(audio_path)[:-4]

    # get a list of txt files in script files
    txt_dir = os.path.join(args.asdinfo_dir, fileid)
    txt_list = glob.glob(os.path.join(txt_dir, "??????.txt"))
    if len(txt_list) == 0:
        logging.error(f"No ASD info found for '{fileid}'. Exit.")
        sys.exit(-1)
    else:
        txt_list.sort()

    flist = glob.glob(os.path.join(frames_dir, "??????.jpg"))
    flist.sort()

    # crop video based on the data of txt
    for txt_path in txt_list:
        utt_index = os.path.splitext(os.path.split(txt_path)[-1])[0]
        utt_id = f"{fileid}:{utt_index:06}"
        lines = open(txt_path).readlines()

        lineno = 0
        while lines[lineno][0] == "#" or lines[lineno].strip() == "":
            w = lines[lineno].split(":")
            if w[0] == "# Script":
                script = " ".join(w[1].split())
            elif w[0] == "# ImageSize":
                image_size_x, image_size_y = [int(x) for x in w[1].split()]
            elif w[0] == "# FPS":
                fps = int(w[1])
            elif w[0] == "# Audio Duration(ms)":
                audio_start, audio_end = [int(x) for x in w[1].split()]
            lineno += 1

        audio_start_frame = int(audio_start / 1000 * fps) + 1
        audio_end_frame = int(audio_end / 1000 * fps) + 1
        audio_start_sec = (audio_start_frame - 1) / fps
        audio_end_sec = (audio_end_frame - 1) / fps

        if audio_start < 0:
            raise ValueError("The audio start frame cannot be negative.")

        # face coordinates per frame, width & height data
        frame_list = [data.split(" ") for data in lines[lineno:]]

        # adjust frame length according to audio start and end info
        crop_regions = adjust_av_index(audio_start_frame, audio_end_frame, frame_list)

        # crop facial area from images and generate avi
        crop_path = crop_video(utt_index, crop_regions, flist, utt_dir)

        # combine audio
        audio_path_out = combine_audio(
            crop_path, audio_path, audio_start_sec, audio_end_sec
        )

        with open(crop_path[:-4] + ".txt", "w") as ofp:
            ofp.write(f"{script}\n")

        print(
            f"{utt_id}\t"
            f"{crop_path}\t"
            f"{audio_path_out}\t"
            f"{audio_end_frame-audio_start_frame+1}\t"
            f"{int((audio_end_sec-audio_start_sec)*16000)}\t"
            f"{script}"
        )

    return


def write_utt_info(args, utt_dir):
    # get vidio and audio name
    audio_path = os.path.splitext(args.video_path)[0] + ".wav"
    fileid = os.path.basename(audio_path)[:-4]

    # get a list of txt files in script files
    txt_dir = os.path.join(args.asdinfo_dir, fileid)
    txt_list = glob.glob(os.path.join(txt_dir, "??????.txt"))
    if len(txt_list) == 0:
        logging.error(f"No ASD info found for '{fileid}'. Exit.")
        sys.exit(-1)
    else:
        txt_list.sort()

    for txt_path in txt_list:
        utt_index = os.path.splitext(os.path.split(txt_path)[-1])[0]
        utt_id = f"{fileid}:{utt_index:06}"
        lines = open(txt_path).readlines()

        lineno = 0
        while lines[lineno][0] == "#":
            w = lines[lineno].split(":")
            if w[0] == "# Script":
                script = " ".join(w[1].split())
            elif w[0] == "# ImageSize":
                image_size_x, image_size_y = [int(x) for x in w[1].split()]
            elif w[0] == "# FPS":
                fps = int(w[1])
            elif w[0] == "# Audio Duration(ms)":
                audio_start, audio_end = [int(x) for x in w[1].split()]
            lineno += 1

        audio_start_frame = int(audio_start / 1000 * fps) + 1
        audio_end_frame = int(audio_end / 1000 * fps) + 1
        audio_start_sec = (audio_start_frame - 1) / fps
        audio_end_sec = (audio_end_frame - 1) / fps

        if audio_start < 0:
            raise ValueError("The audio start frame cannot be negative.")

        crop_path = os.path.join(utt_dir, utt_index + ".avi")
        audio_path = os.path.splitext(crop_path)[0] + ".wav"
        print(
            f"{utt_id}\t"
            f"{crop_path}\t"
            f"{audio_path}\t"
            f"{audio_end_frame-audio_start_frame+1}\t"
            f"{int((audio_end_sec-audio_start_sec)*16000)}\t"
            f"{script}"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crop KMSAV video data")
    parser.add_argument(
        "--asdinfo-dir", type=str, required=True, help="Script root dir"
    )
    parser.add_argument(
        "--save-root", type=str, required=True, help="Path to save cropped video"
    )
    parser.add_argument(
        "--start-margin", type=int, help="video start margin(sec)", default=0
    )
    parser.add_argument(
        "--end-margin", type=int, help="video end margin(sec)", default=0
    )
    parser.add_argument("--dry-run", action="store_true", help="create meta files only")
    parser.add_argument("--fps", type=int, help="video fps", default=25)
    parser.add_argument("video_path", type=str, help="video id")
    args = parser.parse_args()

    # create directories to store output files
    # the directory structure is as follows:
    # output/
    # └── fileid/
    #     ├── frames/
    #     └── utts/
    frames_dir, utt_dir = init_save_root(args)

    # convert all frames into output/fileid/frames/ directory.
    # if there exists '000001.jpg' file already, conversion is skipped.
    if not args.dry_run:
        avi2images(args.video_path, frames_dir, args.fps)

    # For given fileid, video files are extracted corresponding to
    # all utterances described in the script file.
    if args.dry_run:
        write_utt_info(args, utt_dir)
    else:
        crop_all_utts(args, frames_dir, utt_dir)
