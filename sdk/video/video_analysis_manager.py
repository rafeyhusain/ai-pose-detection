from glob import glob
import os
import time
from sdk.app.logger import Logger
from sdk.video.video_analysis_request import VideoAnalysisRequest
from sdk.video.video_file_analyzer import VideoFileAnalyzer
from sdk.video.video_splitter import VideoSplitter
from sdk.detection.head.head_file_analyzer import HeadFileAnalyzer
from sdk.detection.head.head_request import HeadRequest
from sdk.detection.person.person_file_analyzer import PersonFileAnalyzer
from sdk.detection.person.person_request import PersonRequest

class VideoAnalysisManager:
    def __init__(self, request: VideoAnalysisRequest):
        self.request = request
        self.logger = Logger(__name__)
    
    def analyze(self):
        start_time = time.time()

        report = None

        self.logger.started(f"Started analyzing video")

        try:
            folder_path = self.split()

            if folder_path:
                report = self.analyze_folder(folder_path)

            elif os.path.isfile(self.request.input):
                report = self.analyze_file(self.request.input)

            elif os.path.isdir(self.request.input):
                report = self.analyze_folder(self.request.input)

            else:
                self.logger.error(f"Invalid 'input' path in request {self.request}")
        except Exception as e:
            self.logger.error(f"Failed to analyze", e)
            raise

        self.logger.finished(f"Finished analyzing video", start_time)

        return report

    def split(self):
        MAX_SIZE = 50 # MB

        if os.path.isfile(self.request.input):
            if os.path.getsize(self.request.input) > MAX_SIZE * 1024 * 1024:
                self.logger.info(f"File is larger than {MAX_SIZE}MB")
            else:
                self.logger.info("File is within the limit")
                return None
        else:
            return None
        
        splitter = VideoSplitter(self.request.input)
        splitter.split()

        return splitter.output_folder

    def analyze_folder(self, folder_path):
        report = None

        self.logger.started(f"Analyzing all mp4 files in folder: {folder_path}")

        for file_path in glob(os.path.join(folder_path, "*.mp4")):
            report = self.analyze_file(file_path)

        return report
    
    def analyze_file(self, file_path):
        request = self.request.clone()
        request.input = file_path
        analyzer = VideoFileAnalyzer(request)
        report = analyzer.analyze()
        return report
    