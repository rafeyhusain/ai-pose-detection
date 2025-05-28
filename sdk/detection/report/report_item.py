from pydantic import BaseModel, Field
from typing import Optional, Any

class ReportItem(BaseModel):
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    image: str = Field(..., description="Path to the saved image file")
    timestamp: float = Field(..., description="Timestamp of the detection in seconds")
    detail: Optional[Any] = Field(None, description="Additional detection details")

    @classmethod
    def default(cls) -> "ReportItem":
        """Returns a default ReportItem instance."""
        return cls(
            confidence=0.0,
            image="",
            timestamp=0.0,
            detail=None
        )
