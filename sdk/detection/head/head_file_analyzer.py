import cv2
import mediapipe as mp
import json
import os
from glob import glob

from sdk.app.logger import Logger
from sdk.detection.core.core_analyzer import CoreAnalyzer
from sdk.detection.head.head_request import HeadRequest

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 2 = warning and info messages suppressed
os.environ['GLOG_minloglevel'] = '2'  # 0 = all, 1 = warning+, 2 = error+, 3 = fatal only

class HeadFileAnalyzer(CoreAnalyzer):
    def __init__(self, request: HeadRequest):
        self.logger = Logger(__name__)
        self.request = request
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(static_image_mode=False)
        #self.holistic = mp.solutions.holistic.Holistic(static_image_mode=False)

    @property
    def type(self):
        return "head"
    
    def _is_looking_away(self, frame_index, landmarks):
        result = False
        deviation = 0.0

        if self.request.look_mode == "gaze":
            left_eye = landmarks[33]
            right_eye = landmarks[263]
            eye_center_x = (left_eye.x + right_eye.x) / 2
            deviation = abs(eye_center_x - 0.5)
            result = deviation > self.request.look_away_threshold

        elif self.request.look_mode == "yaw":
            nose_x = landmarks[1].x
            deviation = abs(nose_x - 0.5)
            result = deviation > self.request.look_away_threshold

        elif self.request.look_mode == "yaw_pitch":
            nose_x = landmarks[1].x
            nose_y = landmarks[1].y
            dx = abs(nose_x - 0.5)
            dy = abs(nose_y - 0.5)
            deviation = max(dx, dy)
            result = (dx > self.request.look_away_threshold or dy > self.request.look_away_threshold)

        if result:
            self.logger.info(f"Looking away in frame {frame_index}: Deviation = {deviation:.3f}")

        confidence = min(1.0, deviation / self.request.look_away_threshold)

        return result, confidence

    def analyze(self):
        if os.path.isfile(self.request.input):
            result = self.analyze_file(self.request.input)
            self.save_result(result)

        elif os.path.isdir(self.request.input):
            result = self.analyze_folder(self.request.input)
            self.save_results(result)

        else:
            self.logger.error(f"Invalid input path in request {self.request}")

    def analyze_folder(self, folder_path):
        results = []
        for file_path in glob(os.path.join(folder_path, "*.mp4")):
            self.logger.info(f"Analyzing: {file_path}")
            result = self.analyze_file(file_path)
            self.save_result(result)
            results.append(result)
        
        output = {
            "results": results
        }

        return output
    
    def analyze_file(self, file_path: str):
        self.set_file(file_path)

        cap = cv2.VideoCapture(file_path)
        frame_index = 0

        head_tracking_flags = []
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            self.analyze_frame(cap, frame_index, head_tracking_flags, frame)

            frame_index += 1

        cap.release()

        result = self.get_result(head_tracking_flags)

        return result

    def analyze_frame(self, cap, frame_index, head_tracking_flags, frame):
        if frame_index % self.request.frame_skip == 0:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mesh_result = self.face_mesh.process(rgb)

            if not mesh_result.multi_face_landmarks:
                return  # Skip if no face detected

            face_landmarks = mesh_result.multi_face_landmarks[0].landmark

            is_detected, confidence = self._is_looking_away(frame_index, face_landmarks)

            if is_detected:
                timestamp = self.to_timestamp(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0)
                image_path = self.save_frame(frame, timestamp)

                head_tracking_flags.append({
                        "confidence": confidence, 
                        "timestamp": timestamp, 
                        "image": image_path
                        })
                    
    def get_result(self, head_tracking_flags):
        total_detections = len(head_tracking_flags)
        overall_confidence = 0.0

        if total_detections == 0:
            self.logger.info("No look away detected")
        else:
          overall_confidence = sum(flag["confidence"] for flag in head_tracking_flags) / total_detections

        result = {
            "detected": total_detections > 0,
            "confidence": overall_confidence,
            "eye_tracking_flags": [
                {
                    "confidence": "some float",
                    "image": "base64 or path to frame image",
                    "timestamp": "float"
                }
            ],
            "head_tracking_flags": head_tracking_flags
        }
        
        return result

