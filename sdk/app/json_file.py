import json
import time
from typing import Optional, Type
from sdk.app.logger import Logger
from sdk.detection.core.types import T

class JsonFile:
    def __init__(self, logger: Optional[Logger] = None):
        self.logger = logger or Logger(__name__)

    def load(self, model_class: Type[T], json_path: str) -> Optional[T]:
        start_time = time.time()
        try:
            with open(json_path, 'r') as file:
                data = json.load(file)

            instance = model_class(**data)
            self.logger.finished(f"Loaded {model_class.__name__} from {json_path}", start_time)
            return instance

        except FileNotFoundError as e:
            self.logger.error(f"JSON file not found: {json_path}", e)
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON format in file: {json_path}", e)
        except (TypeError, ValueError) as e:
            self.logger.error(f"Invalid value in {model_class.__name__}", e)
        except Exception as e:
            self.logger.error("Unexpected error while loading JSON config", e)

        return None
