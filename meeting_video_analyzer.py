import cv2
import mediapipe as mp
import numpy as np
import json
import os
from glob import glob

class MeetingVideoAnalyzer:
    def __init__(self, frame_skip=0, look_away_thresh=0.1):
        self.frame_skip = frame_skip
        self.look_away_thresh = look_away_thresh
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(static_image_mode=False)
        self.holistic = mp.solutions.holistic.Holistic(static_image_mode=False)

    def _is_looking_away(self, frame_index, landmarks):
        # Nose, left eye, right eye, chin
        nose = landmarks[1]
        left_eye = landmarks[33]
        right_eye = landmarks[263]
        chin = landmarks[152]

        # Face direction vector approximation
        face_vector_x = right_eye.x - left_eye.x
        face_vector_y = chin.y - nose.y

        # Normalize the vector (optional, more precise)
        magnitude = np.sqrt(face_vector_x**2 + face_vector_y**2)
        if magnitude == 0:
            return False
        face_vector_x /= magnitude
        face_vector_y /= magnitude

        # If face_vector_x is large, person is likely looking sideways
        print(f"Frame {frame_index}: face_vector_x = {face_vector_x:.2f}")
        return abs(face_vector_x) > 0.35  # Tune this threshold

    def analyze_file(self, video_path):
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

        results = {
            "video_file": os.path.basename(video_path),
            "look_away_events": 0,
            "total_look_away_duration_sec": 0,
            "longest_look_away_sec": 0,
            "head_turn_detected": False,
            "multiple_people_detected": False
        }

        frame_index = 0
        look_start = None
        look_durations = []

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            if frame_index % self.frame_skip != 0:
                frame_index += 1
                continue

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mesh_result = self.face_mesh.process(rgb)
            pose_result = self.holistic.process(rgb)

            if mesh_result.multi_face_landmarks:
                if len(mesh_result.multi_face_landmarks) > 1:
                    results["multiple_people_detected"] = True

                face_landmarks = mesh_result.multi_face_landmarks[0].landmark
                if self._is_looking_away(frame_index, face_landmarks):
                    if look_start is None:
                        look_start = frame_index
                else:
                    if look_start is not None:
                        dur = (frame_index - look_start) / fps
                        look_durations.append(dur)
                        look_start = None
            else:
                look_start = None

            if pose_result.pose_landmarks:
                l = pose_result.pose_landmarks.landmark[11]
                r = pose_result.pose_landmarks.landmark[12]
                if abs(l.x - r.x) > 0.5:
                    results["head_turn_detected"] = True

            frame_index += 1

        cap.release()

        if look_durations:
            results["look_away_events"] = len(look_durations)
            results["total_look_away_duration_sec"] = round(sum(look_durations), 2)
            results["longest_look_away_sec"] = round(max(look_durations), 2)

        return results

    def analyze_folder(self, folder_path):
        reports = []
        for filepath in glob(os.path.join(folder_path, "*.mp4")):
            print(f"Analyzing: {filepath}")
            report = self.analyze_file(filepath)
            reports.append(report)
        return reports

