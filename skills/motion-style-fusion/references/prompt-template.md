# Prompt template (Google Omni Flash and similar video models)

One fenced code block per shot. Nothing but the prompt inside: no headings, questions or notes. Every line label is at the start of a line exactly as written (the linter checks them).

```
Vertical 9:16 motion graphics video.
DURATION: 6 seconds.
STYLE: <the locked plain-language style sentence, identical in every shot>
START: <fresh | continuation sentence, see SKILL.md>
ACTION:
0-3s: <one hero subject, one clear motion, plain words>
3-6s: <next beat; ranges must tile the full duration, no gaps>
ON-SCREEN TEXT: Only this text appears, spelled exactly: "<words>". No other text, letters, numbers, symbols, captions, labels, or watermarks anywhere in the frame.
MOTION: Smooth, continuous, physically natural movement. Every object is a solid, rigid shape that keeps its form; nothing melts, stretches or warps. Camera stays steady.
SOUND: Sound effects only: <time + effect>; <time + effect>. No music. No voiceover, narration, speech, or singing - not a single spoken word.
END: <still held last frame, nothing moving for the final half second>
AVOID: morphing shapes, liquid warping, flicker, extra or garbled text, logos, watermarks, music, voices.
```

No text in the shot? Write `ON-SCREEN TEXT: None. No text, letters, numbers or symbols appear in the frame.`

## Beat limits and size
4 s: 1-2 beats. 6 s: 2. 8 s: 2-3. 10 s: 3. Aim under 300 words. At most 6 objects in frame.

## Translate analysis into plain words (never paste the left column)
| In your notes | In the prompt |
|---|---|
| #7008A3 | vivid royal purple |
| #0A0418 | near-black |
| 12px stroke | thin line / thick line |
| headline 9% of frame | large headline in the upper third |
| 1080x1920, 30 fps | (omit; set in the tool) |
| Playfair/Didone font | elegant high-contrast serif letters |
| Bebas/condensed sans | tall narrow heavy sans-serif capitals |
| ease-out-expo | starts fast and settles gently |
| scale-pop with overshoot | grows quickly with one small soft bounce |
| ghost echo text | a very large, faint, cropped copy of the same word behind it (only if the reference has it, and counts as the same text) |
| starburst shards | sharp white triangular spikes at the corners |
| grid overlay | faint thin grid lines in the background |
| blur-to-sharp reveal | fades in from slightly blurred to sharp |

## Writing tips
- Describe what the camera sees, not how software made it.
- Specify the background color of the shot in words inside ACTION so shots alternate on purpose.
- Keep recurring subjects described identically across shots (same words) for continuity.
- Time SFX to the visual beat they belong to, and mention only effects (pop, whoosh, thud, click, coin clink, paper rustle...).
