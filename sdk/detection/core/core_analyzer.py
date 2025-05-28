import json
from pathlib import Path
import shutil
import cv2
from sdk.app.logger import Logger
from sdk.detection.core.analyzer_result import AnalyzerResult
from sdk.detection.core.core_request import CoreRequest

class CoreAnalyzer:
    def __init__(self):
        self.logger = Logger(__name__)
        self._request = None
        self.model = None

    @property
    def request(self) -> CoreRequest:
        return self._request 

    @request.setter
    def request(self, value):
        self._request = value
        self.init_folder()
    
    @property
    def output_folder(self):
        base_name = Path(self._request.input).stem
        folder = Path(self._request.input).parent / base_name / self.type
        return folder
    
    @property
    def type(self):
        return None
    
    @property
    def type_title(self):
        return self.type.title()
    
    @property
    def report_json_path(self):
        return self.output_folder / f"report.json"
        
    @property
    def reports_json_path(self):
        return self.output_folder / f"reports.json"
    
    def set_file(self, file_path):
        self.request.input = file_path
        self.init_folder()

    def to_timestamp(self, seconds):
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"
    
    def save_frame(self, frame, timestamp):
        timestamp = timestamp.replace(":", "-")
        image_filename = self.output_folder / f"{timestamp}.png"

        cv2.imwrite(str(image_filename), frame)

        return str(image_filename)
    
    def save_result(self, result):
        self.save_result_json(self.report_json_path, result)

    def save_results(self, results):
        self.save_result_json(self.reports_json_path, results)
        
    def save_result_json(self, file_path, result):
        with open(file_path, "w") as f:
            json.dump(result, f, indent=4)

        self.logger.finished(f"{self.type_title} analysis report saved to {file_path}")
    
    def init_folder(self, clean=True):
        try:
            self.create_output_folder(clean)
            self.logger.info(f"Output folder: {self.output_folder}")
        except Exception as e:
            self.logger.error(f"Failed to init output folder: {self._request.input}", e)
            raise

    def create_output_folder(self, clean=True):
        folder = self.output_folder

        if clean and folder.exists() and folder.is_dir():
            shutil.rmtree(folder)

        folder.mkdir(parents=True, exist_ok=True)
        
        return folder
    
    def analyze_frame(self, frame_index, frame) -> AnalyzerResult:
        return None
