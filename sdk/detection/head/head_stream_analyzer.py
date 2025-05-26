import cv2
import mediapipe as mp

class HeadStreamAnalyzer:
    def __init__(self, look_away_thresh=0.3):
        self.look_away_thresh = look_away_thresh
        self.face_mesh = mp.solutions.face_mesh.FaceMesh()
        self.holistic = mp.solutions.holistic.Holistic()

    def _is_looking_away(self, landmarks, img_width):
        left_eye_x = landmarks[33].x * img_width
        right_eye_x = landmarks[263].x * img_width
        eye_center = (left_eye_x + right_eye_x) / 2
        return abs(eye_center - img_width / 2) > (img_width * self.look_away_thresh)

    def start(self):
        cap = cv2.VideoCapture(0)
        print("Starting live stream analysis... Press 'q' to quit.")
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mesh_result = self.face_mesh.process(rgb)
            pose_result = self.holistic.process(rgb)

            info = []

            if mesh_result.multi_face_landmarks:
                cv2.putText(frame, f"Faces: {len(mesh_result.multi_face_landmarks)}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                if len(mesh_result.multi_face_landmarks) > 1:
                    info.append("Multiple faces detected!")

                landmarks = mesh_result.multi_face_landmarks[0].landmark
                if self._is_looking_away(landmarks, frame.shape[1]):
                    info.append("Looking Away!")

            if pose_result.pose_landmarks:
                l = pose_result.pose_landmarks.landmark[11]
                r = pose_result.pose_landmarks.landmark[12]
                if abs(l.x - r.x) > 0.5:
                    info.append("Head Turn Detected!")

            for i, txt in enumerate(info):
                cv2.putText(frame, txt, (10, 60 + 30 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            cv2.imshow("Live Interview Monitor", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
