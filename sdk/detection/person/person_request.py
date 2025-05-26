from argparse import Namespace
from pydantic import Field, field_validator, model_validator
from typing import Optional
from sdk.detection.core.core_request import CoreRequest

class PersonRequest(CoreRequest):
    input: Optional[str] = Field(None, description="Input file or folder path (for 'file' mode)")
    model_name: str = Field("yolov8n.pt", description="Path to the YOLO model file (.pt)")
    confidence: float = Field(0.5, ge=0.0, le=1.0, description="Confidence threshold between 0.0 and 1.0")
    frame_skip: int = Field(5, ge=0, description="Number of frames to skip between detections")

    @classmethod
    def sample(cls) -> "PersonRequest":
        """Returns a sample request for testing purposes."""
        return cls(
            input="data/videos/video2.mp4",
            model_name="yolov8n.pt",
            confidence=0.5,
            frame_skip=5
        )

    @model_validator(mode='before')
    def check_dependencies(cls, values):
        model_name = values.get("model_name")
        input_path = values.get("input")

        if not input_path:
            raise ValueError("Input path is required")
        
        if not model_name.endswith(".pt"):
            raise ValueError("model_name must end with .pt")
        
        return values
    
    def from_args(self, args: Namespace) -> Optional["PersonRequest"]:
        self.input = args.input
        self.model_name = args.model_name
        self.confidence = args.confidence
        self.frame_skip = args.frame_skip
        
        return self