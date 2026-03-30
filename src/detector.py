"""
Face Detection & Landmark Extraction
=====================================
Uses MediaPipe Face Mesh (468 landmarks) to detect faces
and extract eye, mouth, and head-pose keypoints in real time.
"""

import cv2
import numpy as np
import mediapipe as mp

from . import config


class FaceDetector:
    """Wraps MediaPipe Face Mesh for landmark extraction."""

    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=config.REFINE_LANDMARKS,
            min_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE,
        )

    # ----------------------------------------------------------
    def process_frame(self, frame):
        """
        Detect a face and return organised landmark groups.

        Returns:
            dict with keys 'left_eye', 'right_eye', 'mouth',
            'head_pose', 'all_landmarks', 'frame_shape'
            — or None if no face found.
        """
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = self.face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            return None

        lm = results.multi_face_landmarks[0].landmark

        def px(indices):
            return [(int(lm[i].x * w), int(lm[i].y * h)) for i in indices]

        return {
            "left_eye": px(config.LEFT_EYE_INDICES),
            "right_eye": px(config.RIGHT_EYE_INDICES),
            "mouth": px(config.MOUTH_INDICES),
            "head_pose": px(config.HEAD_POSE_INDICES),
            "all_landmarks": results.multi_face_landmarks[0],
            "frame_shape": (h, w),
        }

    # ----------------------------------------------------------
    def draw_landmarks(self, frame, data):
        """
        Draw eye contours, mouth contours, and head-pose
        keypoints onto the frame (returns a copy).
        """
        if data is None:
            return frame

        out = frame.copy()

        # Eyes
        for eye_pts in (data["left_eye"], data["right_eye"]):
            pts = np.array(eye_pts, np.int32)
            cv2.polylines(out, [pts], True, config.COLOR_CYAN, 1)
            for pt in eye_pts:
                cv2.circle(out, pt, 2, config.COLOR_GREEN, -1)

        # Mouth
        pts = np.array(data["mouth"], np.int32)
        cv2.polylines(out, [pts], True, config.COLOR_ORANGE, 1)
        for pt in data["mouth"]:
            cv2.circle(out, pt, 2, config.COLOR_YELLOW, -1)

        # Head-pose keypoints
        for pt in data["head_pose"]:
            cv2.circle(out, pt, 3, config.COLOR_WHITE, -1)

        return out

    # ----------------------------------------------------------
    def release(self):
        """Release MediaPipe resources."""
        self.face_mesh.close()
