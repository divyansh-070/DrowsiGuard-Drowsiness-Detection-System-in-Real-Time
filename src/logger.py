"""
Event Logger
============
Records drowsiness / yawn / head-drop events to a
timestamped CSV file and tracks session statistics.
"""

import os
import csv
import time
from datetime import datetime

from . import config


class EventLogger:
    """Append-only CSV logger with live session stats."""

    COLUMNS = [
        "timestamp", "event_type", "duration_frames",
        "ear_value", "mar_value", "pitch", "yaw",
    ]

    def __init__(self):
        os.makedirs(config.LOG_DIR, exist_ok=True)

        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_path = os.path.join(config.LOG_DIR,
                                     f"session_{stamp}.csv")

        self.session_start = time.time()
        self.drowsy_count = 0
        self.yawn_count = 0
        self.head_drop_count = 0

        with open(self.log_path, "w", newline="") as f:
            csv.writer(f).writerow(self.COLUMNS)

    # ----------------------------------------------------------
    def log_event(self, event_type, duration_frames=0,
                  ear=0.0, mar=0.0, pitch=0.0, yaw=0.0):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        if event_type == "DROWSY":
            self.drowsy_count += 1
        elif event_type == "YAWN":
            self.yawn_count += 1
        elif event_type == "HEAD_DROP":
            self.head_drop_count += 1

        try:
            with open(self.log_path, "a", newline="") as f:
                csv.writer(f).writerow([
                    ts, event_type, duration_frames,
                    f"{ear:.4f}", f"{mar:.4f}",
                    f"{pitch:.1f}", f"{yaw:.1f}",
                ])
        except Exception as exc:
            print(f"[Logger] write error: {exc}")

    # ----------------------------------------------------------
    @property
    def session_duration(self):
        return time.time() - self.session_start

    @property
    def session_duration_str(self):
        s = int(self.session_duration)
        return f"{s // 3600:02d}:{(s % 3600) // 60:02d}:{s % 60:02d}"

    @property
    def stats(self):
        return {
            "drowsy_count": self.drowsy_count,
            "yawn_count": self.yawn_count,
            "head_drop_count": self.head_drop_count,
            "session_duration": self.session_duration_str,
            "total_alerts": (self.drowsy_count
                             + self.yawn_count
                             + self.head_drop_count),
        }

    def reset(self):
        self.session_start = time.time()
        self.drowsy_count = 0
        self.yawn_count = 0
        self.head_drop_count = 0
