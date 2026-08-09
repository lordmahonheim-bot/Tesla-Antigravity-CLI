#!/usr/bin/env python3
"""
Tesla Eye - Photographic Vision Capture
Takes a screenshot of the X11 Display and saves it to /tmp/tesla_vision.png
"""
import PIL.ImageGrab
import datetime
import sys

def capture():
    try:
        img = PIL.ImageGrab.grab()
        path = "/tmp/tesla_vision.png"
        img.save(path)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"SUCCESS: Screenshot captured at {timestamp} -> {path}")
    except Exception as e:
        print(f"ERROR: Failed to capture screenshot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    capture()
