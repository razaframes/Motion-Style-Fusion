# Per-reference analysis template

Do this for every reference (V1, V2, ...). Frames are sampled across the whole video; if the last third is not described you skipped it. Hex values are for your notes only; add the color name next to every hex because only names go into prompts.

## Top-line
Duration, aspect ratio, fps (meta.json) / overall style in ONE line / pacing (cuts per 10 s, hold lengths) / recurring motif / confidence (full, partial, screenshots).

## Per beat (timestamp range)
- **Composition and camera:** framing, camera movement, focal point
- **Subjects:** each object, illustration or icon: shape, style (flat, glossy 3D, halftone, line), position, relative size
- **Text:** exact wording, letter style in plain words (high-contrast serif / narrow heavy sans), emphasis, animation (blur-to-sharp, wipe, pop)
- **Palette:** background and accents with names (and hex for yourself)
- **Light and texture:** soft studio light, shadows, grain, glow
- **Motion and easing:** what moves, how fast, bounce or none
- **Transition into the next beat:** hard cut, wipe, slide, scale
- **Sound effects:** from `sfx_events.json` and the visuals (see below). Ignore music and speech entirely.

## SFX analysis
List each audible event: time, plain label, which visual event it lands on (`on_cut`). Then the **SFX signature**: the repeatable mapping (e.g. "every hard cut = deep soft thud + quick swish; text reveals = airy whoosh; small objects land = soft pop"). Note loudness character (sparse and punchy, or dense). Flag music/voice likelihood and ignore them.

## Style DNA card
```
Mood:            [3 adjectives]
Palette (names): [background(s), 2-3 accents]   (hex kept in notes)
Light/finish:    [soft studio, matte, glossy, grain...]
Lettering:       [plain-words description, case, animation habit]
Shapes/objects:  [flat vector / glossy 3D / halftone; icon style]
Camera:          [locked / slow push; framing habit]
Motion feel:     [fast start gentle settle, bounce or none]
Transitions:     [signature technique]
Pacing:          [cuts per 10 s, hold ratio]
SFX signature:   [event -> sound mapping]
Signature move:  [what makes it recognizable]
```
