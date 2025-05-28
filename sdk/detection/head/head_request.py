from argparse import Namespace
from typing import Optional, Literal
from pydantic import Field, model_validator

from sdk.detection.core.core_request import CoreRequest

class HeadRequest(CoreRequest):
    mode: Literal["file", "live"] = Field(..., description="Mode of operation: 'file' or 'live'")
    input: Optional[str] = Field(None, description="Input file or folder path (for 'file' mode)")
    look_mode: Literal["yaw", "yaw_pitch", "gaze"] = Field("yaw_pitch", description="Look direction analysis mode")
    frame_skip: int = Field(5, ge=0, description="Number of frames to skip between detections")
    look_away_threshold: float = Field(0.6, ge=0.0, le=1.0, description="Threshold to detect looking away (0.0 to 1.0)")
    threshold_look_away_duration: int = Field(5, ge=0, description="Threshold to detect looking away duration in seconds")
    
    @classmethod
    def default(cls, input) -> "HeadRequest":
        """Returns a sample request for testing purposes."""
        return cls(
            mode="file",
            input=input,
            look_mode="yaw_pitch",
            frame_skip=5,
            look_away_threshold=0.01,
            threshold_look_away_duration = 5
        )

    @model_validator(mode='before')
    def check_dependencies(cls, values):
        mode = values.get("mode")
        input_path = values.get("input")

        if mode == "file" and not input_path:
            raise ValueError("Input path is required in 'file' mode")
        return values

    def from_json(self, json_path: str) -> Optional["HeadRequest"]:
        return super().load(HeadRequest, json_path)

    def from_args(self, args: Namespace) -> Optional["HeadRequest"]:
        self.mode = args.mode
        self.input = args.input
        self.look_mode = args.look_mode
        self.frame_skip = args.frame_skip
        self.look_away_threshold = args.look_away_threshold
        
        return self
