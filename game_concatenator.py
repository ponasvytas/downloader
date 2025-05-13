from pathlib import Path
import json

import os
from typing import Optional
import cv2


import ffmpeg


from models.settings import GameInfo, VideoDetails


def concatenate_files(directory: Path, game_name: str, delete_parts: bool = False):
    os.chdir(directory)

    mp4_files = list(directory.glob("part*.mp4"))
    filepaths = [f"file '{filepath.name}'\n" for filepath in directory.glob("*.mp4")]
    part_file = directory.joinpath("file_parts.txt")

    with open(part_file, "w") as f:
        f.writelines(filepaths)

    stream = ffmpeg.input("file_parts.txt", f="concat")

    output_stream = ffmpeg.output(
        stream,
        f"{game_name}.mp4",
        **{"c": "copy"},
    )

    ffmpeg.run(output_stream)

    if delete_parts:
        for filepath in mp4_files:
            filepath.unlink()

        part_file.unlink()

    return directory.joinpath(f"{game_name}.mp4")


def read_video_details(path_to_video: Path) -> VideoDetails:
    cap = cv2.VideoCapture(str(path_to_video))

    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    length = cap.get(cv2.CAP_PROP_FRAME_COUNT) / frame_rate  # in seconds

    return VideoDetails(frame_rate=frame_rate, height=height, width=width, length=length)


def update_details(path_to_details: Path, details: VideoDetails):
    with open(path_to_details, "r") as f:
        vid_info = GameInfo(**json.load(f))

    vid_info.video_details = details

    with open(path_to_details, "w") as f:
        f.write(vid_info.model_dump_json(by_alias=True, indent=2))


def trim_video_files(directory: Path, trim_start_time, trim_end_time):
    os.chdir(directory)

    mp4_files = sorted(list(directory.glob("part*.mp4")))

    if trim_start_time and trim_start_time !="00:00:00":
        print("WILL TRIM THIS FILE", mp4_files[0])
        ffmpeg.input(mp4_files[0], ss=trim_start_time).output(f"{mp4_files[0].stem}_trim.mp4", c="copy").run()
        # remove input file
        mp4_files[0].unlink()

    if trim_end_time and trim_end_time !="00:00:00":
        print("WILL TRIM THIS FILE", mp4_files[-1])
        ffmpeg.input(mp4_files[-1], t=trim_end_time).output(f"{mp4_files[-1].stem}_trim.mp4", c="copy").run()
        # remove input file
        mp4_files[-1].unlink()


def concatenate_game(
    game_folder: Path,
    trim_start_time: Optional[str] = None,  # timestamp in HH:MM:SS format of the first part file
    trim_end_time: Optional[str] = None,  # timestamp in HH:MM:SS format of the last part file
    delete_parts: bool = False,
):
    trim_video_files(game_folder, trim_start_time, trim_end_time)

    game_name = game_folder.name
    video_path = concatenate_files(game_folder, game_name=game_name, delete_parts=delete_parts)

    vid_details = read_video_details(video_path)

    update_details(game_folder.joinpath("video_info.json"), vid_details)

    print("All done")
