"""
DrowsiGuard Configuration
=========================
All tunable parameters for the drowsiness detection system.
Centralizing settings here makes it easy to adjust thresholds
without touching any detection logic.
"""

import os

# ==============================================================
# Detection Thresholds
# ==============================================================

# Eye Aspect Ratio — below this value, eyes considered closed
EAR_THRESHOLD = 0.21

# Mouth Aspect Ratio — above this value, mouth considered open (yawning)
MAR_THRESHOLD = 0.75

# Head pitch below this (degrees) → head drooping / nodding off
HEAD_PITCH_THRESHOLD = -15.0

# Head yaw beyond this (degrees) → head turned away
HEAD_YAW_THRESHOLD = 30.0

# ==============================================================
# Consecutive Frame Thresholds
# ==============================================================

# Frames of low EAR to trigger drowsy alarm (~0.7s at 30fps)
EAR_CONSEC_FRAMES = 20

# Frames of high MAR to trigger yawn alert
MAR_CONSEC_FRAMES = 15

# Frames of head droop to trigger alert
HEAD_CONSEC_FRAMES = 15

# ==============================================================
# Camera Settings
# ==============================================================

CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# ==============================================================
# MediaPipe Face Mesh Settings
# ==============================================================

MIN_DETECTION_CONFIDENCE = 0.5
MIN_TRACKING_CONFIDENCE = 0.5
REFINE_LANDMARKS = True

# ==============================================================
# Landmark Indices (MediaPipe 468-point Face Mesh)
# ==============================================================

# Eye landmarks ordered as [p1, p2, p3, p4, p5, p6] for EAR formula
LEFT_EYE_INDICES = [362, 385, 387, 263, 373, 380]
RIGHT_EYE_INDICES = [33, 160, 158, 133, 153, 144]

# Inner lip landmarks for MAR calculation
# Order: [left_corner, upper_left, top_center, upper_right,
#          right_corner, lower_right, bottom_center, lower_left]
MOUTH_INDICES = [78, 81, 13, 311, 308, 402, 14, 178]

# Key landmarks for head pose estimation via solvePnP
# [nose_tip, chin, left_eye_corner, right_eye_corner,
#  left_mouth_corner, right_mouth_corner]
HEAD_POSE_INDICES = [1, 152, 33, 263, 61, 291]

# ==============================================================
# Paths
# ==============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
LOG_DIR = os.path.join(BASE_DIR, "logs")
ALARM_SOUND_PATH = os.path.join(ASSETS_DIR, "alarm.wav")

# ==============================================================
# Alarm Sound Generation
# ==============================================================

ALARM_FREQUENCY = 2500      # Hz
ALARM_DURATION = 0.5        # seconds per beep cycle
ALARM_SAMPLE_RATE = 44100   # samples per second

# ==============================================================
# OpenCV UI Colors (BGR)
# ==============================================================

COLOR_GREEN = (0, 255, 0)
COLOR_YELLOW = (0, 255, 255)
COLOR_RED = (0, 0, 255)
COLOR_WHITE = (255, 255, 255)
COLOR_CYAN = (255, 255, 0)
COLOR_ORANGE = (0, 165, 255)

# ==============================================================
# Tkinter GUI Theme (Hex)
# ==============================================================

GUI_BG_PRIMARY = "#0f0f1a"
GUI_BG_SECONDARY = "#1a1a2e"
GUI_BG_CARD = "#16213e"
GUI_ACCENT_GREEN = "#00e676"
GUI_ACCENT_YELLOW = "#ffea00"
GUI_ACCENT_RED = "#ff1744"
GUI_ACCENT_BLUE = "#448aff"
GUI_TEXT_PRIMARY = "#ffffff"
GUI_TEXT_SECONDARY = "#b0b0b0"
GUI_BORDER = "#2a2a4a"
