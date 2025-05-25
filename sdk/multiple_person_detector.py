import shutil
import time
import cv2
from pathlib import Path
from ultralytics import YOLO
from sdk.logger import Logger  


class MultiplePersonDetector:
    def __init__(self, model_name="yolov8n.pt", confidence=0.5, frame_skip=10):
        self.logger = Logger()
        self.confidence = confidence
        self.frame_skip = frame_skip
        self.model = None
        self.init_model(model_name)

    def init_model(self, model_name):
        try:
            self.model = YOLO(model_name)
            self.logger.log(f"Model loaded: {model_name}")
        except Exception as e:
            self.logger.error("Failed to load YOLO model.", e)
            raise

    def to_timestamp(self, seconds):
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}-{secs:02d}"

    def open_video(self, video_path):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            self.logger.error(f"Cannot open video file: {video_path}")
            return None
        self.logger.log(f"Video opened: {video_path}")
        return cap

    def save_frame(self, frame, output_folder, timestamp):
        image_filename = output_folder / f"{timestamp}.png"
        cv2.imwrite(str(image_filename), frame)
        return str(image_filename)

    def analyze_frame(self, frame, frame_index):
        try:
            results = self.model(frame, verbose=False)[0]
            return results
        except Exception as e:
            self.logger.error(f"Model inference failed at frame {frame_index}", e)
            return None

    def analyze_video(self, video_path):
        start_time = time.time()
        try:
            cap = self.open_video(video_path)
            if cap is None:
                return {"detected": False, "confidence": 0.0, "detected_timestamps": []}

            timestamps = []
            total_frames = 0
            detected_frames = 0
            frame_index = 0

            base_name = Path(video_path).stem
            output_folder = Path(video_path).parent / base_name

            if output_folder.exists() and output_folder.is_dir():
                shutil.rmtree(output_folder) 
                self.logger.log(f"Output folder cleaned: {output_folder}")

            output_folder.mkdir(exist_ok=True)
            self.logger.log(f"Output folder: {output_folder}")

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_index % self.frame_skip != 0:
                    frame_index += 1
                    continue

                total_frames += 1
                results = self.analyze_frame(frame, frame_index)
                if results is None:
                    frame_index += 1
                    continue

                people = [det for det in results.boxes.data if int(det[5]) == 0 and det[4] > self.confidence]
                total_people = len(people)

                if total_people > 1:
                    for det in people:
                        x1, y1, x2, y2 = map(int, det[:4])
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # green box

                    confidence = round(float(max(det[4] for det in people)), 2)
                    timestamp = self.to_timestamp(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0)
                    image_path = self.save_frame(frame, output_folder, timestamp)

                    self.logger.log(f"At [{timestamp}], detected [{total_people}] people. Confidence [{confidence}]")

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
            self.logger.log("Video analysis complete", start_time)

            if detected_frames == 0:
                self.logger.log("Not detected more than 1 person in the video")

            return {
                "detected": detected_frames > 0,
                "confidence": confidence_score,
                "detected_timestamps": timestamps
            }

        except Exception as e:
            self.logger.error("Unexpected error during video analysis.", e)
            return {"detected": False, "confidence": 0.0, "detected_timestamps": []}
