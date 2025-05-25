import cv2
import mediapipe as mp
import numpy as np
import json
import os
from glob import glob

class MeetingVideoAnalyzer:
    def __init__(self, frame_skip=5, look_away_thresh=0.3):
        self.frame_skip = frame_skip
        self.look_away_thresh = look_away_thresh
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(static_image_mode=False)
        self.holistic = mp.solutions.holistic.Holistic(static_image_mode=False)

    def _is_looking_away(self, landmarks, img_width):
        left_eye_x = landmarks[33].x * img_width
        right_eye_x = landmarks[263].x * img_width
        eye_center = (left_eye_x + right_eye_x) / 2
        return abs(eye_center - img_width / 2) > (img_width * self.look_away_thresh)

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
                if self._is_looking_away(face_landmarks, width):
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

