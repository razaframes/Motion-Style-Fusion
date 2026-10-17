# Changelog

## 2.0.0
### Fixed
- Prompts no longer contain hex codes, px/% sizes, resolution, fps or font names (they were rendered on screen). Added `lint_prompts.py`.
- Choppy/liquid motion: calmer shots (one hero subject, max 6 objects, max 2-3 beats, no morph/melt/warp wording, still held end frame).
### Changed
- Skill no longer outputs prompts when merely mentioned; it asks for the script and style references first.
- Shots are 4, 6, 8 or 10 seconds (was fixed 10 s).
- Prompts are SFX-only with an explicit "no music, no voiceover, not a single spoken word" line.
### Added
- Reference SFX analysis (`analyze_audio.py`) and SFX signature in the style DNA.
- Continuation shots that start with the exact last frame plus `Attach:` instructions and `last_frame.py`.
- `plan_shots.py`, plain color names in `palette.json`, troubleshooting guide, motion and SFX vocabularies.
- Test suite and CI.

## 0.1.0
- Initial release.
