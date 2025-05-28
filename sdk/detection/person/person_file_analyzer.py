import time
import cv2
from ultralytics import YOLO
from sdk.app.logger import Logger  
from sdk.detection.core.analyzer_result import AnalyzerResult
from sdk.detection.core.core_analyzer import CoreAnalyzer
from sdk.detection.person.person_request import PersonRequest

class PersonFileAnalyzer(CoreAnalyzer):
    def __init__(self, request: PersonRequest):
        self.logger = Logger(__name__)
        self.request = request
        self.model = None
        self.init()
    @property
    def type(self):
        return "person"
    
    def init(self):
        try:
            self.model = YOLO(self.request.model_name)
            self.logger.info(f"Model loaded: {self.request.model_name}")
        except Exception as e:
            self.logger.error(f"Failed to load model: {self.request.model_name}", e)
            raise

    def analyze_frame(self, frame_index, frame) -> AnalyzerResult:
        result = AnalyzerResult.default()

        try:
            if frame_index % self.request.frame_skip != 0:
                result.skipped = True
                return result

            results = self.model(frame, verbose=False)[0]

            people = [det for det in results.boxes.data if int(det[5]) == 0 and det[4] > self.request.confidence]
            total_people = len(people)
            result.success = total_people > 1

            if result.success:
                for det in people:
                    x1, y1, x2, y2 = map(int, det[:4])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # green box

                result.confidence = round(float(max(det[4] for det in people)), 2)
                result.detail = dict({"count": total_people})
        except Exception as e:
            self.logger.error(f"Model inference failed at frame {frame_index}", e)
        
        return result
        

    def analyze123(self):
        start_time = time.time()
        try:
            cap = self.open_video(self.request.input)
            if cap is None:
                return {"detected": False, "confidence": 0.0, "detected_timestamps": []}

            timestamps = []
            total_frames = 0
            detected_frames = 0
            frame_index = 0

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_index % self.request.frame_skip != 0:
                    frame_index += 1
                    continue

                total_frames += 1
                results = self.analyze_frame(frame, frame_index)
                if results is None:
                    frame_index += 1
                    continue

                people = [det for det in results.boxes.data if int(det[5]) == 0 and det[4] > self.request.confidence]
                total_people = len(people)

                if total_people > 1:
                    for det in people:
                        x1, y1, x2, y2 = map(int, det[:4])
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # green box

                    confidence = round(float(max(det[4] for det in people)), 2)
                    timestamp = self.to_timestamp(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0)
                    image_path = self.save_frame(frame, timestamp)

                    self.logger.info(f"At [{timestamp}], detected [{total_people}] people. Confidence [{confidence}]")

                    timestamps.append({
                        "timestamp": timestamp,
                        "detected_people": total_people,
                        "confidence": confidence,
                        "image": image_path
                    })

                    detected_frames += 1

                frame_index += 1

            cap.release()

            confidence_score = round(detected_frames / total_frames, 2) if total_frames else 0
            self.logger.info("Video analysis complete", start_time)

            if detected_frames == 0:
                self.logger.info("Not detected more than 1 person in the video")

            result = {
                "detected": detected_frames > 0,
                "confidence": confidence_score,
                "detected_timestamps": timestamps
            }

            self.save_result(result)

            return result

        except Exception as e:
            self.logger.error("Unexpected error during video analysis.", e)
            return {"detected": False, "confidence": 0.0, "detected_timestamps": []}
