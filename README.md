# Motion Style Fusion (v2)

A Claude skill that turns **your script + your favourite reference styles** into a numbered series of **ready-to-paste Google Omni Flash prompts** for motion-graphics shots (4, 6, 8 or 10 seconds each).

You give it: a script, and references (uploaded videos, screenshots, or links from Pinterest / YouTube / Vimeo / Instagram / X). It studies the references' **look, motion and sound effects**, mixes several styles into one new style (or randomly picks one per scene), splits the script into shots, and hands you prompts that are **SFX-only: no music, no voiceover, not a single spoken word.**

## What is new in v2

| Problem in v1 | Fix in v2 |
|---|---|
| Color codes, px sizes, font names appeared on screen | Prompts are **plain language only**; hex stays in analysis. A **linter** blocks hex, px, %, fps, font names |
| Motion looked liquid / morphing, not smooth | Calm-shot rules: 1 hero subject, max 6 objects, max 2-3 beats, no morph/melt/warp words, still end frame |
| Skill produced prompts the moment it was mentioned | **Intake gate**: asks for script + style references first |
| Only one 10 s prompt size | **4 / 6 / 8 / 10 s** shot planner |
| Long ideas broke continuity | **Continuation shots** start from the *exact last frame* of the previous shot, with an `Attach:` instruction for you |
| Only visuals were analyzed | **SFX analysis** of the references (heuristic) feeds an SFX signature into the prompts; music and speech in references are ignored |
| Hard to know prompt quality | `lint_prompts.py` + test suite + CI |
| Long outputs | Style lock sentence reused in every shot so the series matches |

## How to use

1. Install the skill (below).
2. In Claude, type `/motion-style-fusion` (or just mention it). It will ask for your **script** and **style references**; it will not generate anything before that.
3. Send the script and your references (upload videos or paste links; several are fine). Optional: brand, palette, text changes, "blend the styles" or "pick randomly".
4. Claude replies with a style summary, a shot table, and one prompt per shot.
5. Generate shots in order. When a shot says **Attach: last frame of Shot N-1**, get that image with
   ```bash
   python skills/motion-style-fusion/scripts/last_frame.py shotN-1.mp4
   ```
   (or pause on the final frame and screenshot it) and attach it when generating the next shot.
6. In the video tool, set aspect ratio (9:16 default) and the shot duration; do not expect the prompt to set them.

## Install

**Claude.ai / app:** download `dist/motion-style-fusion.skill`, open it in Claude and click **Save skill**.

**Claude Code:**
```bash
git clone https://github.com/bhaialiraza/Motion-Style-Fusion.git
cp -r Motion-Style-Fusion/skills/motion-style-fusion ~/.claude/skills/
```

## Limits (honest)

- **Links:** Claude's sandbox usually cannot download YouTube/Pinterest/Instagram/X videos. For those links it uses title, description and thumbnail only, says the confidence is partial, and asks for an upload or screenshots. It never invents shots it could not see.
- **SFX analysis is heuristic.** It measures the audio signal (transients, spectrum, decay) and cross-checks with the cuts; it is not human listening. If audio is missing or unclear, SFX are inferred from the visuals and marked as inferred.
- Prompts reduce, but cannot guarantee away, model artifacts. See `skills/motion-style-fusion/references/troubleshooting.md`.

## Scripts (standalone)

Requires `ffmpeg`, Python 3.9+, `numpy`, `Pillow` (`pip install -r requirements.txt`).

| Script | Purpose |
|---|---|
| `extract_frames.py VIDEO` | frames across the whole video, contact sheet, palette with color names, SFX events, meta |
| `analyze_audio.py VIDEO` | SFX / music / speech heuristics only |
| `plan_shots.py SCRIPT.txt` | draft 4/6/8/10 s shot plan (uses timecodes if present) |
| `lint_prompts.py PROMPTS.md` | checks prompts for hex/px/fonts/morph words/format/duration/SFX-only |
| `last_frame.py CLIP.mp4` | saves the exact last frame for continuation shots |

## Repo layout

```
skills/motion-style-fusion/
  SKILL.md                    workflow and hard rules
  scripts/                    the five scripts above
  references/                 prompt-template, motion-vocabulary, sfx-vocabulary,
                              shot-planning, analysis-template, fusion-rules, troubleshooting
examples/                     sample script and v2-format example output
tests/                        run_tests.sh and a deliberately bad prompt
dist/motion-style-fusion.skill  packaged skill (rebuild with ./build.sh)
.github/workflows/validate.yml  CI
```

## Develop

```bash
./tests/run_tests.sh   # smoke tests + linter checks
./build.sh             # rebuild dist/motion-style-fusion.skill
```

## License
MIT. See [LICENSE](LICENSE).
