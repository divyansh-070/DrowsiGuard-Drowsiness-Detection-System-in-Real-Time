"""
DrowsiGuard — Real-Time Drowsiness Detection System
====================================================
Entry point.  Run with:  python run.py
"""

from src.gui import DrowsiGuardApp


def main():
    app = DrowsiGuardApp()
    app.run()


if __name__ == "__main__":
    main()
