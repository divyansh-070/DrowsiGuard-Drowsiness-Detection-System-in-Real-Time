"""
Unit tests for EAR and MAR metric calculations.
Run with:  python -m pytest tests/ -v
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.metrics import calculate_ear, calculate_mar


# ==============================================================
# Eye Aspect Ratio
# ==============================================================
class TestEAR:

    def test_open_eye_above_threshold(self):
        """Wide-open eye → EAR clearly above the 0.21 drowsy threshold."""
        eye = [(0, 5), (2, 0), (4, 0), (6, 5), (4, 10), (2, 10)]
        assert calculate_ear(eye) > 0.21

    def test_closed_eye_near_zero(self):
        """Flat (closed) eye → EAR ≈ 0."""
        eye = [(0, 5), (2, 5), (4, 5), (6, 5), (4, 5), (2, 5)]
        assert calculate_ear(eye) < 0.05

    def test_half_open_eye(self):
        """Half-open eye → EAR between closed (0) and wide-open value."""
        eye_open  = [(0, 5), (2, 0), (4, 0), (6, 5), (4, 10), (2, 10)]
        eye_half  = [(0, 5), (2, 3), (4, 3), (6, 5), (4,  7), (2,  7)]
        ear_open  = calculate_ear(eye_open)
        ear_half  = calculate_ear(eye_half)
        ear_closed = calculate_ear([(0,5),(2,5),(4,5),(6,5),(4,5),(2,5)])
        # Half-open should be strictly between closed and fully open
        assert ear_closed < ear_half < ear_open

    def test_degenerate_returns_zero(self):
        """All points identical → 0 (no crash)."""
        assert calculate_ear([(5, 5)] * 6) == 0.0

    def test_symmetry(self):
        """Mirrored eyes should give same EAR."""
        left = [(0, 5), (2, 0), (4, 0), (6, 5), (4, 10), (2, 10)]
        right = [(6, 5), (4, 0), (2, 0), (0, 5), (2, 10), (4, 10)]
        assert abs(calculate_ear(left) - calculate_ear(right)) < 1e-9


# ==============================================================
# Mouth Aspect Ratio
# ==============================================================
class TestMAR:

    def test_closed_mouth_low(self):
        """Closed lips → MAR < 0.5."""
        mouth = [(0, 5), (2, 4), (3, 4), (4, 4),
                 (6, 5), (4, 6), (3, 6), (2, 6)]
        assert calculate_mar(mouth) < 0.5

    def test_open_mouth_high(self):
        """Wide-open mouth (yawn) → MAR > 0.5."""
        mouth = [(0, 5), (2, 0), (3, 0), (4, 0),
                 (6, 5), (4, 10), (3, 10), (2, 10)]
        assert calculate_mar(mouth) > 0.5

    def test_degenerate_returns_zero(self):
        assert calculate_mar([(5, 5)] * 8) == 0.0

    def test_slightly_open(self):
        """Slightly open mouth → moderate MAR."""
        mouth = [(0, 5), (2, 3), (3, 3), (4, 3),
                 (6, 5), (4, 7), (3, 7), (2, 7)]
        mar = calculate_mar(mouth)
        assert 0.2 < mar < 0.8
