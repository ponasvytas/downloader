from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel
from typing import List, Optional
from datetime import date, time


class VideoDetails(BaseModel):
    frame_rate: float = Field(24.62)
    height: int = 1080
    width: int = 1920
    length: float = 3600
    avg_time_stamps_per_frame: int = 3620

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)


class GameInfo(BaseModel):
    video_name: str = ""
    rink_code: int = Field(0)
    rink_name: str = Field("")
    video_start_date: Optional[date] = None
    video_start_time: Optional[time] = None
    video_length: float = Field(1.0, description="Length of the video in hours")
    download_urls: List[str] = Field(default_factory=list)
    video_urls: List[str] = Field(default_factory=list)
    video_details: VideoDetails = Field(default_factory=VideoDetails)

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)
