#!/usr/bin/env bash
# Smoke + behaviour tests. Needs ffmpeg, python3, numpy, Pillow.
set -euo pipefail
cd "$(dirname "$0")/.."
S=skills/motion-style-fusion/scripts
T=$(mktemp -d)

echo "== synthetic video with SFX-like clicks =="
ffmpeg -y -v error -f lavfi -i "testsrc2=size=720x1280:rate=30:duration=6" \
  -f lavfi -i "aevalsrc='0.8*sin(2*PI*180*t)*exp(-12*mod(t,1.5))':s=22050:d=6" \
  -shortest -pix_fmt yuv420p "$T/t.mp4"

echo "== extract_frames (frames, palette names, sfx_events) =="
python3 $S/extract_frames.py "$T/t.mp4" --out "$T/out" > /dev/null
for f in contact_sheet.jpg palette.json meta.json sfx_events.json; do test -f "$T/out/$f"; done
python3 - "$T/out/palette.json" << 'PY'
import json, sys
p = json.load(open(sys.argv[1]))
assert all("name" in c for c in p["overall_top"]), "palette entries need color names"
PY

echo "== last_frame =="
python3 $S/last_frame.py "$T/t.mp4" "$T/last.png" && test -f "$T/last.png"

echo "== plan_shots =="
python3 $S/plan_shots.py examples/sample-script.txt > "$T/plan.txt"; grep -q "Shot  1" "$T/plan.txt"

echo "== lint: good example must pass =="
python3 $S/lint_prompts.py examples/example-output.md

echo "== lint: bad example must FAIL =="
if python3 $S/lint_prompts.py tests/bad_prompt.md > "$T/bad.txt"; then
  echo "linter accepted a bad prompt"; cat "$T/bad.txt"; exit 1
fi
for needle in "hex color" "pixel/percent" "font name" "risky motion" "music words" "not allowed"; do
  grep -qi "$needle" "$T/bad.txt" || { echo "linter did not report: $needle"; cat "$T/bad.txt"; exit 1; }
done
echo "ALL TESTS PASSED"
