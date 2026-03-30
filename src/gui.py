"""
DrowsiGuard GUI Application
============================
Dark-themed tkinter dashboard with embedded OpenCV video feed,
live metrics, session statistics, and adjustable thresholds.
"""

import tkinter as tk
import cv2
import time
import numpy as np
from PIL import Image, ImageTk

from . import config
from .detector import FaceDetector
from .metrics import calculate_ear, calculate_mar, estimate_head_pose
from .alarm import AlarmManager
from .logger import EventLogger


class DrowsiGuardApp:
    """Main GUI application."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("DrowsiGuard \u2014 Real-Time Drowsiness Detection")
        self.root.configure(bg=config.GUI_BG_PRIMARY)
        self.root.resizable(False, False)

        # --- Core components ---
        self.detector = FaceDetector()
        self.alarm = AlarmManager()
        self.logger = EventLogger()

        # --- State ---
        self.running = False
        self.cap = None
        self.ear_counter = 0
        self.mar_counter = 0
        self.head_counter = 0
        self.current_ear = 0.0
        self.current_mar = 0.0
        self.current_pitch = 0.0
        self.current_yaw = 0.0
        self.status = "IDLE"
        self.fps = 0.0
        self.prev_time = time.time()
        self.drowsy_active = False
        self.yawn_active = False
        self.head_active = False

        # --- Tkinter variables (linked to sliders) ---
        self.ear_thresh_var = tk.DoubleVar(value=config.EAR_THRESHOLD)
        self.mar_thresh_var = tk.DoubleVar(value=config.MAR_THRESHOLD)

        self._build_ui()

    # ==========================================================
    # UI construction
    # ==========================================================
    def _build_ui(self):
        root = self.root

        # ---- Title bar ----
        hdr = tk.Frame(root, bg=config.GUI_BG_SECONDARY, height=50)
        hdr.pack(fill="x", padx=10, pady=(10, 5))
        hdr.pack_propagate(False)
        tk.Label(hdr, text="\U0001f6e1  DrowsiGuard",
                 font=("Segoe UI", 18, "bold"),
                 fg=config.GUI_ACCENT_BLUE,
                 bg=config.GUI_BG_SECONDARY).pack(side="left", padx=15)
        tk.Label(hdr, text="Real-Time Drowsiness Detection",
                 font=("Segoe UI", 10),
                 fg=config.GUI_TEXT_SECONDARY,
                 bg=config.GUI_BG_SECONDARY).pack(side="left")

        # ---- Content ----
        body = tk.Frame(root, bg=config.GUI_BG_PRIMARY)
        body.pack(fill="both", padx=10, pady=5)

        # -- Video panel (left) --
        vf = tk.Frame(body, bg=config.GUI_BG_CARD, bd=2)
        vf.pack(side="left", padx=(0, 10))
        self.video_label = tk.Label(vf, bg=config.GUI_BG_CARD)
        self.video_label.pack(padx=4, pady=4)
        self._show_placeholder()

        # -- Sidebar (right) --
        sb = tk.Frame(body, bg=config.GUI_BG_PRIMARY, width=280)
        sb.pack(side="right", fill="y")
        sb.pack_propagate(False)

        self._card_status(sb)
        self._card_controls(sb)   # controls near top — always visible
        self._card_metrics(sb)
        self._card_stats(sb)
        self._card_settings(sb)

    # ---------- helpers ----------
    def _show_placeholder(self):
        ph = np.zeros((config.FRAME_HEIGHT, config.FRAME_WIDTH, 3),
                       dtype=np.uint8)
        ph[:] = (26, 26, 46)
        cv2.putText(ph, "Press  Start  to begin", (140, 240),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        self._put_frame(ph)

    def _put_frame(self, bgr):
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        img = ImageTk.PhotoImage(Image.fromarray(rgb))
        self.video_label.configure(image=img)
        self.video_label.imgtk = img          # prevent GC

    def _card(self, parent, title):
        """Reusable styled card widget."""
        c = tk.Frame(parent, bg=config.GUI_BG_CARD,
                     highlightbackground=config.GUI_BORDER,
                     highlightthickness=1)
        c.pack(fill="x", pady=(0, 4))
        tk.Label(c, text=title, font=("Segoe UI", 9, "bold"),
                 fg=config.GUI_TEXT_SECONDARY,
                 bg=config.GUI_BG_CARD, anchor="w").pack(fill="x",
                                                          padx=10,
                                                          pady=(5, 1))
        inner = tk.Frame(c, bg=config.GUI_BG_CARD)
        inner.pack(fill="x", padx=10, pady=(0, 5))
        return inner

    # ---------- Status card ----------
    def _card_status(self, parent):
        inner = self._card(parent, "STATUS")
        self.status_canvas = tk.Canvas(inner, width=255, height=38,
                                       bg=config.GUI_BG_CARD,
                                       highlightthickness=0)
        self.status_canvas.pack()
        self._draw_status("IDLE", config.GUI_TEXT_SECONDARY)

    def _draw_status(self, text, color):
        c = self.status_canvas
        c.delete("all")
        c.create_oval(8, 6, 30, 28, fill=color, outline="")
        c.create_text(40, 19, text=text,
                      font=("Segoe UI", 14, "bold"),
                      fill=color, anchor="w")

    # ---------- Metrics card ----------
    def _card_metrics(self, parent):
        inner = self._card(parent, "LIVE METRICS")
        self._metric_labels = {}
        self._metric_bars = {}
        for key in ("EAR", "MAR", "Pitch", "Yaw", "FPS"):
            row = tk.Frame(inner, bg=config.GUI_BG_CARD)
            row.pack(fill="x", pady=1)
            tk.Label(row, text=f"{key}:", font=("Consolas", 9),
                     fg=config.GUI_TEXT_SECONDARY,
                     bg=config.GUI_BG_CARD, width=6,
                     anchor="w").pack(side="left")
            val = tk.Label(row, text="--", font=("Consolas", 9, "bold"),
                           fg=config.GUI_ACCENT_GREEN,
                           bg=config.GUI_BG_CARD, width=7,
                           anchor="w")
            val.pack(side="left")
            self._metric_labels[key] = val
            if key in ("EAR", "MAR"):
                bar = tk.Canvas(row, width=120, height=12,
                                bg=config.GUI_BG_SECONDARY,
                                highlightthickness=0)
                bar.pack(side="right", padx=(0, 2))
                self._metric_bars[key] = bar

    # ---------- Stats card ----------
    def _card_stats(self, parent):
        inner = self._card(parent, "SESSION STATISTICS")
        defs = [
            ("Drowsy Alerts:", "drowsy_lbl", config.GUI_ACCENT_RED),
            ("Yawn Alerts:",   "yawn_lbl",   config.GUI_ACCENT_YELLOW),
            ("Head Drops:",    "head_lbl",   config.GUI_ACCENT_YELLOW),
            ("Session Time:",  "time_lbl",   config.GUI_ACCENT_BLUE),
        ]
        for txt, attr, clr in defs:
            row = tk.Frame(inner, bg=config.GUI_BG_CARD)
            row.pack(fill="x", pady=1)
            tk.Label(row, text=txt, font=("Segoe UI", 9),
                     fg=config.GUI_TEXT_SECONDARY,
                     bg=config.GUI_BG_CARD).pack(side="left")
            lbl = tk.Label(row, text="0", font=("Segoe UI", 9, "bold"),
                           fg=clr, bg=config.GUI_BG_CARD)
            lbl.pack(side="right")
            setattr(self, attr, lbl)

    # ---------- Settings card ----------
    def _card_settings(self, parent):
        inner = self._card(parent, "\u2699  SETTINGS")
        for label, var, lo, hi, res in [
            ("EAR Threshold", self.ear_thresh_var, 0.10, 0.35, 0.01),
            ("MAR Threshold", self.mar_thresh_var, 0.30, 1.20, 0.05),
        ]:
            tk.Label(inner, text=label, font=("Segoe UI", 8),
                     fg=config.GUI_TEXT_SECONDARY,
                     bg=config.GUI_BG_CARD).pack(anchor="w")
            tk.Scale(inner, from_=lo, to=hi, resolution=res,
                     orient="horizontal", variable=var,
                     bg=config.GUI_BG_CARD, fg=config.GUI_TEXT_PRIMARY,
                     troughcolor=config.GUI_BG_SECONDARY,
                     highlightthickness=0, length=220,
                     font=("Consolas", 8)).pack(fill="x")

    # ---------- Controls ----------
    def _card_controls(self, parent):
        f = tk.Frame(parent, bg=config.GUI_BG_PRIMARY)
        f.pack(fill="x", pady=(0, 4))
        btn_kw = dict(font=("Segoe UI", 10, "bold"), bd=0,
                      relief="flat", cursor="hand2", pady=6)
        tk.Button(f, text="\u25b6  Start", bg="#1b5e20", fg="white",
                  activebackground="#2e7d32", activeforeground="white",
                  command=self._start, **btn_kw).pack(side="left", fill="x",
                                                       expand=True, padx=(0, 2))
        tk.Button(f, text="\u23f9  Stop", bg="#b71c1c", fg="white",
                  activebackground="#c62828", activeforeground="white",
                  command=self._stop, **btn_kw).pack(side="left", fill="x",
                                                      expand=True, padx=(2, 0))
        tk.Button(parent, text="\u21bb  Reset Stats",
                  bg=config.GUI_BG_CARD, fg=config.GUI_TEXT_PRIMARY,
                  activebackground=config.GUI_BG_SECONDARY,
                  activeforeground=config.GUI_TEXT_PRIMARY,
                  command=self._reset, font=("Segoe UI", 8),
                  bd=0, cursor="hand2", pady=3).pack(fill="x", pady=(0, 4))

    # ==========================================================
    # Detection loop
    # ==========================================================
    def _start(self):
        if self.running:
            return
        self.cap = cv2.VideoCapture(config.CAMERA_INDEX)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
        if not self.cap.isOpened():
            self._draw_status("CAM ERROR", config.GUI_ACCENT_RED)
            return
        self.running = True
        self.prev_time = time.time()
        self._tick()

    def _stop(self):
        self.running = False
        self.alarm.stop()
        if self.cap:
            self.cap.release()
            self.cap = None
        self._draw_status("STOPPED", config.GUI_TEXT_SECONDARY)

    def _reset(self):
        self.logger.reset()
        self.ear_counter = self.mar_counter = self.head_counter = 0
        self.drowsy_active = self.yawn_active = self.head_active = False
        self.alarm.stop()

    # ----------------------------------------------------------
    def _tick(self):
        """One iteration of the detection + render loop."""
        if not self.running:
            return

        ret, frame = self.cap.read()
        if not ret:
            self.root.after(10, self._tick)
            return

        frame = cv2.flip(frame, 1)

        # FPS
        now = time.time()
        self.fps = 1.0 / max(now - self.prev_time, 1e-6)
        self.prev_time = now

        data = self.detector.process_frame(frame)

        if data is not None:
            self._process_landmarks(data)
            frame = self.detector.draw_landmarks(frame, data)
            self._overlay_status(frame)
        else:
            self._draw_status("NO FACE", config.GUI_TEXT_SECONDARY)
            cv2.putText(frame, "No face detected", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (128, 128, 128), 2)

        self._put_frame(frame)
        self._update_sidebar()
        self.root.after(10, self._tick)

    # ----------------------------------------------------------
    def _process_landmarks(self, data):
        """Run EAR / MAR / head-pose logic and manage alarms."""
        ear_l = calculate_ear(data["left_eye"])
        ear_r = calculate_ear(data["right_eye"])
        self.current_ear = (ear_l + ear_r) / 2.0
        self.current_mar = calculate_mar(data["mouth"])

        hp = estimate_head_pose(data["head_pose"], data["frame_shape"])
        if hp:
            self.current_pitch, self.current_yaw, _ = hp

        et = self.ear_thresh_var.get()
        mt = self.mar_thresh_var.get()

        status, color = "ALERT", config.GUI_ACCENT_GREEN

        # --- Eye closure ---
        if self.current_ear < et:
            self.ear_counter += 1
            if self.ear_counter >= config.EAR_CONSEC_FRAMES:
                status, color = "DROWSY!", config.GUI_ACCENT_RED
                if not self.drowsy_active:
                    self.alarm.start()
                    self.logger.log_event("DROWSY", self.ear_counter,
                                          self.current_ear, self.current_mar,
                                          self.current_pitch, self.current_yaw)
                    self.drowsy_active = True
        else:
            if self.drowsy_active:
                self.alarm.stop()
            self.ear_counter = 0
            self.drowsy_active = False

        # --- Yawning ---
        if self.current_mar > mt:
            self.mar_counter += 1
            if self.mar_counter >= config.MAR_CONSEC_FRAMES:
                if status != "DROWSY!":
                    status, color = "YAWNING", config.GUI_ACCENT_YELLOW
                if not self.yawn_active:
                    self.logger.log_event("YAWN", self.mar_counter,
                                          self.current_ear, self.current_mar,
                                          self.current_pitch, self.current_yaw)
                    self.yawn_active = True
        else:
            self.mar_counter = 0
            self.yawn_active = False

        # --- Head drop ---
        if self.current_pitch < config.HEAD_PITCH_THRESHOLD:
            self.head_counter += 1
            if self.head_counter >= config.HEAD_CONSEC_FRAMES:
                if status == "ALERT":
                    status, color = "HEAD DROP!", config.GUI_ACCENT_RED
                if not self.head_active:
                    self.alarm.start()
                    self.logger.log_event("HEAD_DROP", self.head_counter,
                                          self.current_ear, self.current_mar,
                                          self.current_pitch, self.current_yaw)
                    self.head_active = True
        else:
            if self.head_active and not self.drowsy_active:
                self.alarm.stop()
            self.head_counter = 0
            self.head_active = False

        self.status = status
        self._draw_status(status, color)

    # ----------------------------------------------------------
    def _overlay_status(self, frame):
        """Draw status text on the OpenCV frame."""
        clr_map = {"ALERT": config.COLOR_GREEN,
                    "DROWSY!": config.COLOR_RED,
                    "YAWNING": config.COLOR_YELLOW,
                    "HEAD DROP!": config.COLOR_RED}
        clr = clr_map.get(self.status, config.COLOR_WHITE)
        cv2.putText(frame, self.status, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, clr, 2)
        cv2.putText(frame, f"EAR: {self.current_ear:.2f}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, config.COLOR_WHITE, 1)
        cv2.putText(frame, f"MAR: {self.current_mar:.2f}", (10, 85),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, config.COLOR_WHITE, 1)

    # ----------------------------------------------------------
    def _update_sidebar(self):
        """Refresh sidebar labels and bars."""
        ml = self._metric_labels
        ml["EAR"].config(text=f"{self.current_ear:.3f}")
        ml["MAR"].config(text=f"{self.current_mar:.3f}")
        ml["Pitch"].config(text=f"{self.current_pitch:.1f}\u00b0")
        ml["Yaw"].config(text=f"{self.current_yaw:.1f}\u00b0")
        ml["FPS"].config(text=f"{self.fps:.0f}")

        self._bar(self._metric_bars["EAR"], self.current_ear,
                  0.5, self.ear_thresh_var.get(), below=True)
        self._bar(self._metric_bars["MAR"], self.current_mar,
                  1.5, self.mar_thresh_var.get(), below=False)

        s = self.logger.stats
        self.drowsy_lbl.config(text=str(s["drowsy_count"]))
        self.yawn_lbl.config(text=str(s["yawn_count"]))
        self.head_lbl.config(text=str(s["head_drop_count"]))
        self.time_lbl.config(text=s["session_duration"])

    @staticmethod
    def _bar(canvas, value, max_v, thresh, below):
        canvas.delete("all")
        w, h = 120, 12
        ratio = min(value / max_v, 1.0)
        bw = int(ratio * w)
        danger = value < thresh if below else value > thresh
        clr = config.GUI_ACCENT_RED if danger else config.GUI_ACCENT_GREEN
        canvas.create_rectangle(0, 0, w, h,
                                fill=config.GUI_BG_SECONDARY, outline="")
        if bw > 0:
            canvas.create_rectangle(0, 0, bw, h, fill=clr, outline="")
        tx = int((thresh / max_v) * w)
        canvas.create_line(tx, 0, tx, h, fill="white", width=2)

    # ==========================================================
    # Lifecycle
    # ==========================================================
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.mainloop()

    def _on_close(self):
        self._stop()
        self.detector.release()
        self.alarm.cleanup()
        self.root.destroy()
