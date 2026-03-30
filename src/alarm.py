"""
Alarm Manager
=============
Uses winsound (Windows built-in stdlib) in a background thread
for a guaranteed-to-work, non-blocking looped alarm.

Falls back to playsound / pygame if not on Windows.
"""

import threading
import platform

from . import config


class AlarmManager:
    """
    Non-blocking alarm that runs in a daemon thread.

    On Windows: uses winsound.Beep() — zero dependencies, always works.
    On other OS: uses pygame.mixer as fallback.
    """

    def __init__(self):
        self._playing = False
        self._stop_event = threading.Event()
        self._thread = None
        self._is_windows = platform.system() == "Windows"

    # ----------------------------------------------------------
    def start(self):
        """Start the alarm loop (no-op if already playing)."""
        if self._playing:
            return
        self._stop_event.clear()
        self._playing = True
        self._thread = threading.Thread(
            target=self._loop, daemon=True, name="AlarmThread"
        )
        self._thread.start()

    # ----------------------------------------------------------
    def stop(self):
        """Stop the alarm loop."""
        if not self._playing:
            return
        self._stop_event.set()
        self._playing = False
        # Don't join — daemon thread will exit on its own

    # ----------------------------------------------------------
    def _loop(self):
        """Beep loop — runs entirely in the background thread."""
        if self._is_windows:
            self._windows_loop()
        else:
            self._pygame_loop()

    def _windows_loop(self):
        import winsound
        # Two-tone urgent alarm: high beep then lower beep
        pattern = [
            (2800, 200),   # high
            (2000, 200),   # low
            (2800, 200),
            (2000, 200),
            (0,    150),   # short silence between cycles
        ]
        while not self._stop_event.is_set():
            for freq, dur in pattern:
                if self._stop_event.is_set():
                    break
                if freq == 0:
                    self._stop_event.wait(dur / 1000.0)
                else:
                    winsound.Beep(freq, dur)

    def _pygame_loop(self):
        """Fallback for non-Windows systems using pygame."""
        try:
            import pygame
            import os, wave, math, struct

            # Generate WAV if needed
            os.makedirs(config.ASSETS_DIR, exist_ok=True)
            path = config.ALARM_SOUND_PATH
            if not os.path.exists(path):
                sr, dur = 44100, 0.5
                n = int(sr * dur)
                with wave.open(path, "w") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(sr)
                    for i in range(n):
                        t = i / sr
                        s = math.sin(2 * math.pi * 2500 * t)
                        wf.writeframes(struct.pack("<h", int(s * 22767)))

            pygame.mixer.init()
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(-1)
            # Wait until stopped
            while not self._stop_event.is_set():
                self._stop_event.wait(0.1)
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except Exception as exc:
            print(f"[Alarm] fallback failed: {exc}")

    # ----------------------------------------------------------
    @property
    def is_playing(self):
        return self._playing

    def cleanup(self):
        """Call on app exit."""
        self.stop()
