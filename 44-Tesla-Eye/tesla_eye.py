#!/usr/bin/env python3
import sys
from datetime import datetime
from PIL import ImageGrab

def capture_screen(output_path=None):
    """
    Captures the primary X11 display context.
    """
    if not output_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"/tmp/tesla_eye_capture_{timestamp}.png"
    
    try:
        screenshot = ImageGrab.grab()
        screenshot.save(output_path)
        print(f"SUCCESS: Visual capture acquired -> {output_path}")
        return output_path
    except Exception as e:
        print(f"ERROR: Visual capture failed -> {e}")
        sys.exit(1)

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else None
    capture_screen(out)
