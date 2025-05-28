import time
import cv2
from sdk.app.logger import Logger  
from sdk.detection.core.core_analyzer import CoreAnalyzer
from sdk.detection.person.person_request import PersonRequest
from sdk.detection.report.report import Report
from sdk.detection.report.report_item import ReportItem
from sdk.video.video_analysis_request import VideoAnalysisRequest
from sdk.detection.head.head_file_analyzer import HeadFileAnalyzer
from sdk.detection.person.person_file_analyzer import PersonFileAnalyzer

class VideoFileAnalyzer:
    def __init__(self, request: VideoAnalysisRequest):
        self.request = request
        self.logger = Logger(__name__)
        self._analyzers = None
        self.cap = None

        self.add_sample_analyzer()

    @property
    def analyzers(self) -> list[CoreAnalyzer]:
        return self._analyzers 

    @analyzers.setter
    def analyzers(self, value):
        self._analyzers = value

    def open_video(self, file_path):
        self.cap = cv2.VideoCapture(file_path)

        if not self.cap.isOpened():
            self.logger.failed(f"Cannot open video file: {file_path}")
            return None
        
        self.logger.success(f"Video opened: {file_path}")

        return self.cap

    def add_sample_analyzer(self):
        self._analyzers = [
                PersonFileAnalyzer(PersonRequest.default(self.request.input)),
                HeadFileAnalyzer(PersonRequest.default(self.request.input))
              ]
        
    def analyze(self) -> Report:
        self.logger.started(f"Started analyzing video")

        start_time = time.time()

        try:
            report = Report()

            self.cap = self.open_video(self.request.input)
            if self.cap is None:
                return

            frame_index = 0

            while True:
                ret, frame = self.cap.read()

                if not ret:
                    break

                frame_index += 1
                
                report = self.run_analyzers(frame_index, frame)
                
            self.cap.release()

            if report.items.count == 0:
                self.logger.failed("No detection found in the video")

            self.logger.finished("Video analysis complete", start_time)
        except Exception as e:
            self.logger.error("Error during video analysis.", e)
        
        return report

    def run_analyzers(self, frame_index, frame) -> Report:
        report = Report()

        for analyzer in self.analyzers:
            item = self.run_analyzer(analyzer, frame_index, frame)

            if item:
                report.items.append(item)

        return report
    
    def run_analyzer(self, analyzer: CoreAnalyzer, frame_index, frame) -> Report:
        start_time = time.time()

        item = None

        try:
            result = analyzer.analyze_frame(frame_index, frame)

            if not result:
                return item;
        
            if result.success:
                item = ReportItem.default()
                item.confidence = result.confidence
                item.timestamp = analyzer.to_timestamp(self.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0)
                item.image = analyzer.save_frame(frame, item.timestamp)
                item.detail = result.detail
                
                self.logger.finished(f"Frame [{frame_index}]: Analysis completed by [{analyzer.type_title}] analyzer", start_time)

        except Exception as e:
            self.logger.error(f"Error in Frame [{frame_index}]: [{analyzer.type_title}] analyzer.", e)
        
        return item