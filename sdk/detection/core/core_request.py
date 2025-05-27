import shutil
from typing import Optional, Type
from pydantic import BaseModel
from sdk.app.json_file import JsonFile
from sdk.detection.core.types import T

class CoreRequest(BaseModel):
    def load(self, model_class: Type[T], json_path: str) -> Optional[T]:
        json_file = JsonFile()
        return json_file.load(model_class, json_path)
            
    def __str__(self):
        return "\n".join(
            f"{key.replace('_', ' ').title()}: {value}"
            for key, value in self.model_dump().items()
        )
