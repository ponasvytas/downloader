from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class Segment(BaseModel):
    A: str
    B: str


class CalibrationLine(BaseModel):
    Length: str
    Segment: Segment
    Origin: str
    Axis: str


class Unit(BaseModel):
    field_Abbreviation: str = Field(..., alias="@Abbreviation")
    text: str = Field(..., alias="#text")


class Calibration(BaseModel):
    CalibrationLine: CalibrationLine
    CalibrationDrawingId: str
    Unit: Unit


class ColorModel(BaseModel):
    field_Key: str = Field("back color", alias="@Key")
    Value: str = "255;0;0;0"


class FontSizeModel(BaseModel):
    field_Key: str = Field("font size", alias="@Key")
    Value: str = "12"


class DrawingStyleModel(BaseModel):
    Color: ColorModel = ColorModel()
    FontSize: FontSizeModel = FontSizeModel()


class InfosFadingModel(BaseModel):
    Enabled: str = "true"
    UseDefault: str = "true"
    AlwaysVisible: str = "false"
    MasterFactor: str = "1"
    OpaqueFrames: str = "1"
    Frames: str = "20"


class DrawingLabelModel(BaseModel):
    field_id: str = Field(..., alias="@id")
    field_name: str = Field(..., alias="@name")
    Text: str
    Position: str
    ArrowVisible: str = "false"
    ArrowEnd: str = "1646.89;1332.651"
    DrawingStyle: DrawingStyleModel = DrawingStyleModel()
    InfosFading: InfosFadingModel = InfosFadingModel()

    model_config = ConfigDict(populate_by_name=True)


class LineSize(BaseModel):
    field_Key: str = Field(..., alias="@Key")
    Value: str


class PenShape(BaseModel):
    field_Key: str = Field(..., alias="@Key")
    Value: str


class DrawingStyle1(BaseModel):
    Color: ColorModel
    LineSize: LineSize
    PenShape: PenShape


class DrawingRectangle(BaseModel):
    field_id: str = Field(..., alias="@id")
    field_name: str = Field(..., alias="@name")
    PointUpperLeft: str
    PointUpperRight: str
    PointLowerRight: str
    PointLowerLeft: str
    DrawingStyle: DrawingStyle1
    InfosFading: InfosFadingModel


class Drawings(BaseModel):
    drawing_label: Optional[DrawingLabelModel] = Field(None, alias="Label")
    drawing_rectangle: Optional[DrawingRectangle] = Field(None, alias="Rectangle")
    model_config = ConfigDict(populate_by_name=True)


class KeyframeItem(BaseModel):
    field_id: str = Field(..., alias="@id")
    Timestamp: str
    Name: str
    Color: str
    Comment: str
    Drawings: Drawings

    model_config = ConfigDict(populate_by_name=True)


class KeyframesItems(BaseModel):
    Keyframe: List[KeyframeItem] = Field(default_factory=list)


class DrawingStyle2(BaseModel):
    Color: ColorModel


class CoordinateSystem(BaseModel):
    field_id: str = Field(..., alias="@id")
    field_name: str = Field(..., alias="@name")
    Position: str
    Visible: str
    ShowGrid: str
    ShowGraduations: str
    DrawingStyle: DrawingStyle2


class DrawingStyle3(BaseModel):
    Color: ColorModel


class TestGrid(BaseModel):
    field_id: str = Field(..., alias="@id")
    field_name: str = Field(..., alias="@name")
    Visible: str
    ShowHorizontalAxis: str
    ShowVerticalAxis: str
    ShowFraming: str
    ShowThirds: str
    DrawingStyle: DrawingStyle3


class CropPositions(BaseModel):
    CropPosition: List[str]


class Kinogram(BaseModel):
    TileCount: str
    Rows: str
    CropSize: str
    CropPositions: CropPositions
    AutoInterpolate: str
    LeftToRight: str
    BorderColor: str
    BorderVisible: str
    MeasureLabelType: str


class VideoFilters(BaseModel):
    Kinogram: Kinogram


class KinoveaVideoAnalysisItem(BaseModel):
    FormatVersion: str = "2.0"
    AverageTimeStampsPerFrame: int = 1000
    Keyframes: KeyframesItems = KeyframesItems()


class Annotation(BaseModel):
    KinoveaVideoAnalysis: Optional[KinoveaVideoAnalysisItem] = (
        KinoveaVideoAnalysisItem()
    )
