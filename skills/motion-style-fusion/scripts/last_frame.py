#!/usr/bin/env python3
"""
Save the exact last frame of a generated clip, to attach to the NEXT shot's generation.

Usage: python last_frame.py shot3.mp4 [shot3_last.png]
Needs ffmpeg. No ffmpeg? Pause the video on its final frame and take a screenshot instead.
"""
import subprocess, sys
from pathlib import Path

if len(sys.argv) < 2:
    sys.exit(__doc__)
src = sys.argv[1]
out = sys.argv[2] if len(sys.argv) > 2 else str(Path(src).with_suffix("")) + "_last.png"
r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-sseof", "-0.2", "-i", src, "-update", "1", "-q:v", "1", out],
                   capture_output=True, text=True)
if r.returncode != 0 or not Path(out).exists():
    sys.exit(f"ffmpeg failed: {r.stderr}")
print(f"Saved last frame: {out}")
