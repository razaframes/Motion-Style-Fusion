#!/usr/bin/env bash
# Package the skill into dist/motion-style-fusion.skill (zip with the skill folder at its root).
set -euo pipefail
cd "$(dirname "$0")/skills"
mkdir -p ../dist
rm -f ../dist/motion-style-fusion.skill
zip -qr ../dist/motion-style-fusion.skill motion-style-fusion -x "*/__pycache__/*" "*.pyc"
echo "Built dist/motion-style-fusion.skill"
