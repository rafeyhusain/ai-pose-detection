import cv2
import mediapipe as mp
import json
import os
from glob import glob

from sdk.app.logger import Logger
from sdk.detection.head.head_request import HeadRequest

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 2 = warning and info messages suppressed

class HeadFileAnalyzer:
    def __init__(self, request: HeadRequest):
        self.request = request
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(static_image_mode=False)
        self.holistic = mp.solutions.holistic.Holistic(static_image_mode=False)
        self.logger = Logger(__name__)

    def _is_looking_away(self, frame_index, landmarks):
        self.logger.info(f"Frame {frame_index}: Nose landmark: x={landmarks[1].x}, y={landmarks[1].y}")

        if self.look_mode == "gaze":
            # Advanced: use eye landmarks (horizontal deviation from face center)
            left_eye = landmarks[33]
            right_eye = landmarks[263]
            eye_center_x = (left_eye.x + right_eye.x) / 2
            deviation = abs(eye_center_x - 0.5)
            return deviation > self.look_away_thresh

        elif self.look_mode == "yaw":
            # Horizontal only: nose deviation from center
            nose_x = landmarks[1].x
            return abs(nose_x - 0.5) > self.look_away_thresh

        elif self.look_mode == "yaw_pitch":
            # Both horizontal and vertical deviation
            nose_x = landmarks[1].x
            nose_y = landmarks[1].y
            return (abs(nose_x - 0.5) > self.look_away_thresh or
                    abs(nose_y - 0.5) > self.look_away_thresh)

        return False

    def analyze(self):
        if os.path.isfile(self.request.input):
            result = self.analyze_file(self.request.input)
            self.save_result(result)

        elif os.path.isdir(self.request.input):
            result = self.analyze_folder(self.request.input)
            self.save_result(result)

        else:
            self.logger.error(f"Invalid input path in request {self.request}")

    def analyze_folder(self, folder_path):
        reports = []
        for filepath in glob(os.path.join(folder_path, "*.mp4")):
            self.logger.info(f"Analyzing: {filepath}")
            report = self.analyze_file(filepath)
            reports.append(report)
        
        output = {
            "results": reports
        }

        return output
    
    def analyze(self):
        cap = cv2.VideoCapture(self.request.input)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_index = 0

        look_away_frames = []
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame_index % self.frame_skip == 0:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mesh_result = self.face_mesh.process(rgb)

                if mesh_result.multi_face_landmarks:
                    face_landmarks = mesh_result.multi_face_landmarks[0].landmark
                    if self._is_looking_away(frame_index, face_landmarks):
                        time_sec = frame_index / fps
                        look_away_frames.append(round(time_sec, 2))  # save time in seconds, rounded

            frame_index += 1

        cap.release()

        return {
            "detected": len(look_away_frames) > 0,
            "confidence": float,
            "eye_tracking_flags": [
            {
                "confidence": float,
                "image": "base64 or path to frame image",
                "timestamp": float
            }
            ],
            "head_tracking_flags": look_away_frames
        }

