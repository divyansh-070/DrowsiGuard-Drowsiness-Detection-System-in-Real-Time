# Project Report: DrowsiGuard — Real-Time Drowsiness Detection System

**Author:** Divyansh Kumar  
**Course:** Computer Vision  
**Date:** March 2026

---

## 1. Problem Identification

### 1.1 Real-World Problem

Drowsy driving is one of the most under-reported yet dangerous causes of road accidents globally. According to the National Highway Traffic Safety Administration (NHTSA), drowsy driving is responsible for approximately **100,000 crashes, 71,000 injuries, and 1,550 fatalities** every year in the United States alone. Similar patterns are documented worldwide.

The challenge with drowsiness is that it creeps up gradually — drivers often fail to recognize that they are impaired until after an incident occurs. Unlike alcohol intoxication, which has measurable thresholds, drowsiness has no single biological marker that is easy to test in real time. This makes **non-invasive, real-time, camera-based monitoring** an attractive and practical solution.

### 1.2 Why This Problem?

This problem was chosen for three reasons:

1. **Personal relevance**: Long study sessions and late-night driving are common experiences. A system that operates using just a laptop webcam — no special hardware — is genuinely useful.
2. **Strong CV applicability**: The problem directly requires facial landmark detection, geometric computations, temporal frame analysis, and camera calibration — all core topics of the Computer Vision course.
3. **Measurable outcomes**: The effectiveness of the system can be evaluated objectively by testing with real eye-closure vs. open-eye conditions.

---

## 2. Approach & Technical Architecture

### 2.1 Overview

The system processes a live webcam feed frame by frame. For each frame it:

1. Detects a face using **MediaPipe Face Mesh** (468 3D landmarks)
2. Computes three independent drowsiness indicators:
   - Eye Aspect Ratio (EAR) — eye closure
   - Mouth Aspect Ratio (MAR) — yawning
   - Head pitch angle — head drooping
3. Applies temporal filtering (consecutive frame counters) to avoid false positives
4. Triggers a looped audio alarm for sustained alerts
5. Logs every event to a session CSV file
6. Renders all metrics onto a dark-themed tkinter GUI dashboard

### 2.2 Technology Choices

| Choice | Rationale |
|--------|-----------|
| **MediaPipe Face Mesh** over dlib | No C++ toolchain needed on Windows; faster inference; 468 refined landmarks vs. 68; actively maintained by Google |
| **OpenCV** for video & drawing | Industry-standard CV library; excellent webcam support |
| **Tkinter** for GUI | Ships with Python stdlib; no extra GUI framework install needed; integrates cleanly with OpenCV via Pillow |
| **Pygame** for audio | Cross-platform; non-blocking `mixer.music.play(-1)` loop |
| **SciPy `distance.euclidean`** | Numerically stable; clear readable code |
| **Synthetic alarm sound** | No external file dependency; generated at runtime using pure Python `wave` + `struct` |

---

## 3. Core Algorithms

### 3.1 Eye Aspect Ratio (EAR)

Based on the seminal paper by **Soukupová & Čech (2016)**, *"Real-Time Eye Blink Detection using Facial Landmarks"*, EAR is defined as:

```
EAR = (||p2 - p6|| + ||p3 - p5||) / (2 × ||p1 - p4||)
```

Where p1–p6 are six facial landmarks around each eye. The numerator measures the vertical openness of the eye; the denominator normalises for face scale. When the eye is open, EAR remains roughly constant (~0.25–0.35). When it closes, EAR rapidly approaches zero.

**MediaPipe indices used:**
- Left eye: `[362, 385, 387, 263, 373, 380]`
- Right eye: `[33, 160, 158, 133, 153, 144]`

Both eyes are averaged for robustness. If EAR stays below `0.21` for **20 consecutive frames** (~0.67 seconds at 30 fps), a DROWSY alarm is triggered.

### 3.2 Mouth Aspect Ratio (MAR)

The MAR extends the same geometric idea to the mouth:

```
MAR = (||p2 - p8|| + ||p3 - p7|| + ||p4 - p6||) / (3 × ||p1 - p5||)
```

It measures three vertical distances across the inner lips normalised by the horizontal mouth width. A yawn produces a MAR significantly above the closed-mouth baseline. If MAR exceeds `0.75` for **15 consecutive frames**, a YAWN alert is raised.

### 3.3 Head Pose Estimation via solvePnP

The head pose is estimated using OpenCV's `solvePnP` function, which solves the **Perspective-n-Point (PnP)** problem — finding the rotation and translation that maps a set of 3D model points onto their 2D image projections.

**Six keypoints used:** nose tip, chin, left eye corner, right eye corner, left mouth corner, right mouth corner.

The camera intrinsic matrix is approximated from the frame dimensions (pinhole camera model). The rotation vector is converted to Euler angles via `cv2.RQDecomp3x3`. A **pitch angle below -15°** (head drooping forward) for 15 consecutive frames triggers a HEAD DROP alert.

---

## 4. Key Design Decisions

### 4.1 Temporal Filtering (Consecutive Frame Counters)

A naive approach would trigger an alarm on every frame where EAR < threshold. This produces excessive false alarms from camera jitter and normal blinks (~150–400 ms). The counters act as a **debounce mechanism**: only sustained anomalous readings trigger alerts.

### 4.2 Modular Architecture

The project is split into five focused modules (`config`, `metrics`, `detector`, `alarm`, `logger`) plus the GUI. This separation means:
- Individual components are unit-testable in isolation
- Thresholds can be changed in one place (`config.py`) without touching detection logic
- The alarm or logging backend can be swapped without touching the GUI

### 4.3 Thread Safety

All OpenCV processing and tkinter rendering happen on the **main thread** via `root.after(10, self._tick)`. This avoids thread-safety issues with tkinter while still feeling responsive. The pygame alarm plays in a **background thread** managed by its mixer engine.

### 4.4 Adjustable Thresholds

Because EAR/MAR optimal thresholds vary between users (different face shapes, glasses, facial hair), the GUI provides **real-time sliders** so users can calibrate without restarting the application.

---

## 5. Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| MediaPipe returns normalised (0–1) coords, not pixel coords | Multiplied by frame width/height before drawing and EAR/MAR calculation |
| pygame and tkinter both want the main thread | MediaPipe + tkinter on main thread via `after()`; pygame mixer runs in its own background thread — no conflict |
| `solvePnP` returns radians in a rotation vector, not Euler angles | Used `cv2.Rodrigues` to get rotation matrix, then `cv2.RQDecomp3x3` for Euler angles in degrees |
| Generating an alarm with no external audio file | Used Python's built-in `wave` + `struct` + `math.sin` to synthesize a 0.5-second dual-frequency WAV; saved to `assets/alarm.wav` on first run |
| Normal eye blinks triggering false alarms | Set `EAR_CONSEC_FRAMES = 20` (~0.67s) — longer than any normal blink (~150–400 ms) |

---

## 6. Results & Observations

Testing was conducted with a standard laptop webcam (30 fps, 640×480):

| Condition | System Response |
|-----------|----------------|
| Eyes fully open | Steady ALERT status; EAR ≈ 0.27–0.32 |
| Normal blink | EAR briefly drops but no alarm (< 20 frames) |
| Eyes held closed 1 second | DROWSY status + alarm triggered |
| Yawning (mouth wide) | MAR spikes to ~0.85+; YAWNING alert |
| Head tilted forward ~20° | HEAD DROP alert triggered |
| No face in frame | "NO FACE" status; all counters frozen |

**Average FPS:** 22–28 fps on a mid-range CPU (Intel Core i5, no GPU acceleration required — MediaPipe runs efficiently on CPU).

---

## 7. What I Learned

1. **Geometric methods are powerful.** The EAR formula, published in 2016, still works reliably in 2026. Classical geometry-based features can outperform ML approaches when the signal is well-defined and lighting conditions are controlled.

2. **Temporal context matters in video CV.** A single-frame threshold produces noisy output. Frame counters transform an unreliable per-frame classifier into a robust time-series detector.

3. **MediaPipe is production-quality.** It handles head rotation, partial occlusion, and varying lighting gracefully, far better than older Haar-cascade-based approaches I initially considered.

4. **solvePnP requires careful modelling.** Approximating camera intrinsics from frame dimensions works acceptably for pose estimation but would need full calibration for metric accuracy.

5. **Good software architecture pays off.** Separating concerns into `config / metrics / detector / alarm / logger / gui` made debugging much faster — each component could be tested and verified independently.

---

## 8. Future Improvements

- **CNN-based drowsiness classifier**: Train a lightweight model (MobileNetV3) on the NTHU-DDD or UTA-RLDD datasets for even more robust detection.
- **Multi-occupant monitoring**: Extend to detect multiple faces simultaneously (MediaPipe already supports `max_num_faces > 1`).
- **Attention heatmaps**: Visualise which facial regions contributed most to the alert decision.
- **Mobile deployment**: Export MediaPipe graph to TensorFlow Lite for smartphone-based dashboard cameras.
- **CAN bus integration**: Interface with vehicle OBD-II to automatically reduce speed or alert fleet managers when drowsiness is detected.

---

## 9. References

1. Soukupová, T. & Čech, J. (2016). *Real-Time Eye Blink Detection using Facial Landmarks*. 21st Computer Vision Winter Workshop.
2. Lugaresi, C. et al. (2019). *MediaPipe: A Framework for Building Perception Pipelines*. Google Research.
3. NHTSA (2023). *Drowsy Driving Research and Program*. National Highway Traffic Safety Administration.
4. OpenCV Developers (2024). *cv2.solvePnP Documentation*. opencv.org.
5. Bradski, G. (2000). *The OpenCV Library*. Dr. Dobb's Journal of Software Tools.
