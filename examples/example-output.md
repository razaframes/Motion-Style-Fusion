# Example output (v2 format, illustrative)

**Style summary:** clean editorial motion graphics; bright white, vivid royal purple, soft lilac and near-black; glossy 3D objects with flat layouts; elegant high-contrast serif letters. Mode: Fusion. SFX signature: hard cut = deep soft thud plus quick swish, text reveal = airy whoosh, object landing = soft pop.

| Shot | Seconds | Script | Type |
|---|---|---|---|
| 1 | 6 | Germany has more than 40 different types of taxes. | Fresh |
| 2 | 8 | Those taxes finance an entire country... almost 1 trillion euros. | Fresh |
| 3 | 6 | (same idea continues) | Continuation of Shot 2 |

## Shot 1 - 6 seconds
Attach: nothing.

```
Vertical 9:16 motion graphics video.
DURATION: 6 seconds.
STYLE: Clean editorial motion graphic with a flat 2D layout and glossy 3D objects, a bright pure white background with faint thin grid lines, vivid royal purple as the main color with soft lilac and near-black details, soft studio lighting with gentle shadows under objects, elegant high-contrast serif letters, razor-sharp finish with no film grain.
START: Begin on a fresh, clean frame.
ACTION:
0-3s: On the plain white background, a rounded purple rectangle slides up into the center of the frame and a short headline fades in inside it, from slightly blurred to sharp. A thin black dashed ring circles slowly behind it.
3-6s: A single glossy paper form drops in from above and lands in front of the rectangle with one small soft bounce. Everything then holds still.
ON-SCREEN TEXT: Only this text appears, spelled exactly: "40+ taxes". No other text, letters, numbers, symbols, captions, labels, or watermarks anywhere in the frame.
MOTION: Smooth, continuous, physically natural movement. Every object is a solid, rigid shape that keeps its form; nothing melts, stretches or warps. Camera stays steady.
SOUND: Sound effects only: 0.3s soft pop as the rectangle lands; 1.0s airy whoosh as the ring circles; 3.2s soft thump when the paper lands. No music. No voiceover, narration, speech, or singing - not a single spoken word.
END: The last half second is a perfectly still frame.
AVOID: morphing shapes, liquid warping, flicker, extra or garbled text, logos, watermarks, music, voices.
```

## Shot 2 - 8 seconds
Attach: nothing.

```
Vertical 9:16 motion graphics video.
DURATION: 8 seconds.
STYLE: Clean editorial motion graphic with a flat 2D layout and glossy 3D objects, a bright pure white background with faint thin grid lines, vivid royal purple as the main color with soft lilac and near-black details, soft studio lighting with gentle shadows under objects, elegant high-contrast serif letters, razor-sharp finish with no film grain.
START: Begin on a fresh, clean frame.
ACTION:
0-4s: The scene cuts to a solid vivid purple background with sharp white triangular spikes in two corners. A tall stack of glossy silver coins rises from the bottom of the frame one coin at a time and stops in the lower center.
4-8s: Large white serif words fade in above the stack from slightly blurred to sharp. The coins stay perfectly still.
ON-SCREEN TEXT: Only this text appears, spelled exactly: "Almost one trillion euros". No other text, letters, numbers, symbols, captions, labels, or watermarks anywhere in the frame.
MOTION: Smooth, continuous, physically natural movement. Every object is a solid, rigid shape that keeps its form; nothing melts, stretches or warps. Camera stays steady.
SOUND: Sound effects only: 0.0s deep soft thud on the cut; 0.5s to 3.5s soft coin clinks as each coin lands; 4.2s airy whoosh as the words appear. No music. No voiceover, narration, speech, or singing - not a single spoken word.
END: The last half second is a perfectly still frame with the coin stack and the words.
AVOID: morphing shapes, liquid warping, flicker, extra or garbled text, logos, watermarks, music, voices.
```

## Shot 3 - 6 seconds (continuation of Shot 2)
Attach: the last frame of Shot 2. Generate Shot 2 first, then run `python scripts/last_frame.py shot2.mp4` (or pause on its final frame and take a screenshot) and attach that image.

```
Vertical 9:16 motion graphics video.
DURATION: 6 seconds.
STYLE: Clean editorial motion graphic with a flat 2D layout and glossy 3D objects, a bright pure white background with faint thin grid lines, vivid royal purple as the main color with soft lilac and near-black details, soft studio lighting with gentle shadows under objects, elegant high-contrast serif letters, razor-sharp finish with no film grain.
START: Start with the exact last frame of the previous shot (the attached image), then continue the same motion without any cut.
ACTION:
0-3s: The camera slowly pushes in toward the top of the silver coin stack while the stack stays where it is.
3-6s: One more silver coin drops onto the top of the stack with one small soft bounce, then everything holds still.
ON-SCREEN TEXT: Only this text appears, spelled exactly: "Almost one trillion euros". No other text, letters, numbers, symbols, captions, labels, or watermarks anywhere in the frame.
MOTION: Smooth, continuous, physically natural movement. Every object is a solid, rigid shape that keeps its form; nothing melts, stretches or warps. Camera stays steady except for the slow push-in.
SOUND: Sound effects only: 0.0s to 3.0s a faint airy whoosh with the push-in; 3.3s soft coin clink as the coin lands. No music. No voiceover, narration, speech, or singing - not a single spoken word.
END: The last half second is a perfectly still frame.
AVOID: morphing shapes, liquid warping, flicker, extra or garbled text, logos, watermarks, music, voices.
```

Settings: choose aspect ratio 9:16 and the stated duration in the tool, not in the prompt. Generate shots in order.
