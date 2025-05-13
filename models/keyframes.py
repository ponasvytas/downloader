import uuid

from .model import (
    Drawings,
    DrawingLabelModel,
    KeyframeItem,
    DrawingStyleModel,
    FontSizeModel,
    ColorModel,
)
from .settings import VideoDetails


def create_keyframe(
    vid_time,
    short_text,
    full_text,
    video_details: VideoDetails,
    color="125;125;125",
    avg_time_stamps=3655,
):
    time_in_sec = vid_time * 60
    timestamp = video_details.frame_rate * avg_time_stamps * time_in_sec

    # try to center the text
    pos_x = video_details.width / 2 - len(full_text) * 5
    pos_y = video_details.height * 0.9

    drawing = Drawings(
        drawing_label=DrawingLabelModel(
            field_id=str(uuid.uuid4()),
            field_name=short_text,
            Text=full_text,
            Position=f"{pos_x:.2f};{pos_y:.2f}",
            DrawingStyle=DrawingStyleModel(
                Color=ColorModel(Value=color), FontSize=FontSizeModel(Value="16")
            ),
        ),
        drawing_rectangle=None,
    )

    k = KeyframeItem(
        field_id=str(uuid.uuid4()),
        Timestamp=str(int(timestamp)),
        Name=short_text,
        Color=color,
        Comment=rf"{{\rtf1\ansi\ansicpg1252\deff0\nouicompat\deflang1033{{\fonttbl{{\f0\fnil\fcharset0Arial;}}}}{full_text}}}",
        Drawings=drawing,
    )

    return k
