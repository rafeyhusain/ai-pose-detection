import json
from pathlib import Path
import shutil
import cv2
from sdk.app.logger import Logger
from sdk.detection.core.core_request import CoreRequest

class CoreAnalyzer:
    def __init__(self):
        self.logger = Logger(__name__)
        self.output_folder = None

        self._request = None

    @property
    def request(self) -> CoreRequest:
        return self._request 

    @request.setter
    def request(self, value):
        self._request = value
        self.init_folder()
    
    @property
    def type(self):
        return None
    
    @property
    def type_title(self):
        return self.type.title()
    
    @property
    def report_json_path(self):
        return self.output_folder / f"report.json"
    
    def save_frame(self, frame, timestamp):
        timestamp = timestamp.replace(":", "-")
        image_filename = self.output_folder / f"{timestamp}.png"

        cv2.imwrite(str(image_filename), frame)

        return str(image_filename)
    
    def save_result(self, result):
        with open(self.report_json_path, "w") as f:
            json.dump(result, f, indent=4)

        self.logger.finished(f"{self.type_title} analysis report saved to {self.report_json_path}")
    
    def init_folder(self, clean=True):
        try:
            self.output_folder = self.create_output_folder(clean)
            self.logger.info(f"Output folder: {self.output_folder}")
        except Exception as e:
            self.logger.error(f"Failed to init output folder: {self.request.input}", e)
            raise

    def create_output_folder(self, clean=True):
        base_name = Path(self.request.input).stem
        folder = Path(self.request.input).parent / base_name / self.type

        if clean and folder.exists() and folder.is_dir():
            shutil.rmtree(folder) 

        folder.mkdir(exist_ok=True)
        
        return folder
