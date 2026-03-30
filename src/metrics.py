"""
Metrics Calculations for Drowsiness Detection
==============================================
Implements:
  - Eye Aspect Ratio (EAR)  — detects eye closure
  - Mouth Aspect Ratio (MAR) — detects yawning
  - Head Pose Estimation     — detects head drooping

Reference: Soukupová & Čech, "Real-Time Eye Blink Detection
using Facial Landmarks", 2016.
"""

import numpy as np
from scipy.spatial import distance as dist
import cv2


def calculate_ear(eye_landmarks):
    """
    Calculate Eye Aspect Ratio.

    EAR = (||p2 - p6|| + ||p3 - p5||) / (2 × ||p1 - p4||)

    When the eye is open, EAR ≈ 0.25–0.35.
    When the eye is closed, EAR drops toward 0.

    Args:
        eye_landmarks: list of 6 (x, y) tuples
            [left_corner, upper_left, upper_right,
             right_corner, lower_right, lower_left]

    Returns:
        float: Eye Aspect Ratio (0.0 if degenerate)
    """
    A = dist.euclidean(eye_landmarks[1], eye_landmarks[5])
    B = dist.euclidean(eye_landmarks[2], eye_landmarks[4])
    C = dist.euclidean(eye_landmarks[0], eye_landmarks[3])

    if C == 0:
        return 0.0

    return (A + B) / (2.0 * C)


def calculate_mar(mouth_landmarks):
    """
    Calculate Mouth Aspect Ratio.

    MAR = (||p2 - p8|| + ||p3 - p7|| + ||p4 - p6||) / (3 × ||p1 - p5||)

    A high MAR indicates an open mouth (yawning).

    Args:
        mouth_landmarks: list of 8 (x, y) tuples
            [left_corner, upper_left, top_center, upper_right,
             right_corner, lower_right, bottom_center, lower_left]

    Returns:
        float: Mouth Aspect Ratio (0.0 if degenerate)
    """
    A = dist.euclidean(mouth_landmarks[1], mouth_landmarks[7])
    B = dist.euclidean(mouth_landmarks[2], mouth_landmarks[6])
    C = dist.euclidean(mouth_landmarks[3], mouth_landmarks[5])
    D = dist.euclidean(mouth_landmarks[0], mouth_landmarks[4])

    if D == 0:
        return 0.0

    return (A + B + C) / (3.0 * D)


def estimate_head_pose(landmarks_2d, frame_shape):
    """
    Estimate head orientation (pitch, yaw, roll) using cv2.solvePnP.

    Uses a generic 3-D face model and the camera's intrinsic matrix
    (approximated from frame dimensions) to solve for the rotation
    that maps the model onto the detected 2-D landmarks.

    Args:
        landmarks_2d: list of 6 (x, y) pixel coordinates
            [nose_tip, chin, left_eye, right_eye,
             left_mouth, right_mouth]
        frame_shape: (height, width, ...) of the video frame

    Returns:
        (pitch, yaw, roll) in degrees, or None on failure
    """
    h, w = frame_shape[:2]

    # Canonical 3-D face model points (mm, arbitrary scale)
    model_points = np.array([
        (0.0, 0.0, 0.0),            # Nose tip
        (0.0, -330.0, -65.0),       # Chin
        (-225.0, 170.0, -135.0),    # Left eye left corner
        (225.0, 170.0, -135.0),     # Right eye right corner
        (-150.0, -150.0, -125.0),   # Left mouth corner
        (150.0, -150.0, -125.0),    # Right mouth corner
    ], dtype=np.float64)

    image_points = np.array(landmarks_2d, dtype=np.float64)

    # Approximate camera intrinsics
    focal_length = float(w)
    center = (w / 2.0, h / 2.0)
    camera_matrix = np.array([
        [focal_length, 0, center[0]],
        [0, focal_length, center[1]],
        [0, 0, 1],
    ], dtype=np.float64)

    dist_coeffs = np.zeros((4, 1))

    try:
        ok, rvec, tvec = cv2.solvePnP(
            model_points, image_points,
            camera_matrix, dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE,
        )
        if not ok:
            return None

        rmat, _ = cv2.Rodrigues(rvec)
        angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)

        return (angles[0], angles[1], angles[2])   # pitch, yaw, roll
    except Exception:
        return None
