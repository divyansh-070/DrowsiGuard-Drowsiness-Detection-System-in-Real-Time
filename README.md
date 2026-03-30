# DrowsiGuard — Drowsiness Detection System in Real Time.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8%2B-green?logo=opencv)](https://opencv.org)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-Face%20Mesh-orange?logo=google)](https://mediapipe.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**DrowsiGuard** is a real-time computer vision device that tracks on the face of a driver using a web camera and sends out an alarm whenever indicative signs of drowsiness are detected. It is equipped with eye-closure, yawn, and head drooping detection (Eye Aspect Ratio, Mouth Aspect Ratio and head pose estimation respectively) that are independent of each other and leads to strong drowsiness detection.

> **Why does this matter?**  
> In the United States alone, drowsy driving is estimated to have caused about 100,000 crashes, 71,000 injuries and 1550 deaths each year (NHTSA). An inexpensive, camera-based alertness system will be used to save lives.

---

## Features

| Feature | Description |
|---------|-------------|
| **Eye Closure Detection** | Calculates Eye Aspect Ratio from facial landmarks which then triggers alarm after maintained closure i.e alert |
| **Yawn Detection** | Monitors Mouth Aspect Ratio to identify yawning |
| **Head Pose Estimation** | Uses `cv2.solvePnP` to detect head drooping (nodding off) |
| **Audio Alarm** | Automatic dual-tone alarm sounds continuously until the user wakes up |
| **Dark-Themed GUI** | Tkinter dashboard with inbuilt video feed, live metric bars, and session statistics |
| **Adjustable Thresholds** | Real-time slider controls for EAR and MAR sensitivity |
| **Event Logging** | All drowsiness events are logged to CSV files that are timestamped |
| **Tested** | Unit tests for all metric calculations |

---

## How It Works

### Eye Aspect Ratio (EAR)

The EAR is a scalar value that tells how much open or closed an eye is:

```
EAR = (||p2 - p6|| + ||p3 - p5||) / (2 × ||p1 - p4||)
```

- **Open eyes**: EAR ≈ 0.25 – 0.35
- **Closed eyes**: EAR drops toward 0
- If EAR stays below threshold for **20 consecutive frames** (~0.7 s), the system will trigger a **DROWSY** alarm.

### Mouth Aspect Ratio (MAR)

```
MAR = (||p2 - p8|| + ||p3 - p7|| + ||p4 - p6||) / (3 × ||p1 - p5||)
```

Increased MAR is an indication of an open mouth (yawning). A **YAWN** alert is raised in case it is sustained over more than **15 frames**.

### Head Pose Estimation

The six keypoints of the face are matched with a canonical 3-D face model with the use of the feature of cv2.solvePnP.  The resulted **pitch** angle will detect head drooping which is a classic sign of micro-sleep.

---

## Project Structure

```
DrowsiGuard/
├── src/
│   ├── __init__.py        # Package marker
│   ├── config.py          # All tunable parameters & constants
│   ├── metrics.py         # EAR, MAR, head-pose calculations
│   ├── detector.py        # MediaPipe Face Mesh wrapper
│   ├── alarm.py           # Alarm sound generation & playback
│   ├── logger.py          # CSV event logging
│   └── gui.py             # Tkinter GUI application
├── tests/
│   └── test_metrics.py    # Unit tests for EAR & MAR
├── assets/                # Auto-generated alarm sound
├── logs/                  # Session CSV logs (auto-created)
├── docs/
│   └── report.md          # Detailed project report
├── run.py                 # Entry point
├── requirements.txt       # Python dependencies
├── .gitignore
├── LICENSE
└── README.md
```

---

## Getting Started

### Prerequisites

- **Python 3.10+**
- A working **webcam**
- **Windows / macOS / Linux**

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/divyansh-kumar/DrowsiGuard.git
   cd DrowsiGuard
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS / Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

```bash
python run.py
```

The GUI window will appear. Click **Start** button to detect.

### Running Tests

```bash
pip install pytest
python -m pytest tests/ -v
```

---

## Configuration

There are two ways of adjusting all thresholds:

1. **Live sliders** which are availaible in the GUI sidebar (EAR and MAR thresholds)
2. **`src/config.py`** for all given parameters:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `EAR_THRESHOLD` | 0.21 | Below that → eyes are considered closed |
| `MAR_THRESHOLD` | 0.75 | Above that → mouth is considered as yawning |
| `HEAD_PITCH_THRESHOLD` | -15.0° | Below this → head drooping |
| `EAR_CONSEC_FRAMES` | 20 | low EAR before alarm frames |
| `MAR_CONSEC_FRAMES` | 15 | high MAR before alert frames |
| `HEAD_CONSEC_FRAMES` | 15 | head droop before alert frames|
| `CAMERA_INDEX` | 0 | Webcam device index |

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| Face Detection | MediaPipe Face Mesh (468 landmarks) |
| Video Processing | OpenCV |
| GUI | Tkinter + Pillow |
| Audio | Pygame |
| Math | NumPy, SciPy |

---

## License

This project is licensed under the MIT License — check the (LICENSE) file.

---

## Author

**Divyansh Kumar**

---

## Future Improvements

- Add a less powerful CNN to achieve more powerful drowsiness classification
- Introduce multi-face support in passenger monitoring
- Mobile deployment through TFLite / ONNX
- CFleet driver monitoring cloud dashboard
- CAN bus integration allows for automatic speed reduction
