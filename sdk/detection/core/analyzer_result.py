from pydantic import BaseModel, Field
from typing import Optional, Any

class AnalyzerResult(BaseModel):
    status: int = Field(description="Whether the analysis was unknown=-1, success=0, skipped=1")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    detail: Optional[Any] = Field(None, description="Additional analysis details")

    @classmethod
    def default(cls) -> "AnalyzerResult":
        """Returns a sample result for testing purposes."""
        return cls(
            status=-1,
            confidence=0.95,
            detail={}
        )

    @property
    def success(self):
        return self.status == 0
    
    @success.setter
    def success(self, value):
        self.status = 0 if value else -1
    
    @success.setter
    def skipped(self, value):
        self.status = 1 if value else -1