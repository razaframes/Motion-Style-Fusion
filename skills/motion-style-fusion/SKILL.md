---
name: motion-style-fusion
description: Turns a user's video script plus favourite reference styles (uploaded videos, screenshots, or Pinterest/YouTube/Vimeo/Instagram/X links) into numbered Google Omni Flash prompts for motion-graphics shots of 4, 6, 8 or 10 seconds. Analyzes the references' look, motion and sound effects, blends several styles into one or randomly picks per scene, keeps prompts SFX-only (no music, no voiceover), plans continuation shots that start from the exact last frame, and lints prompts so no hex codes, pixel sizes or font names leak onto the screen. Use when the user mentions this skill, motion-style-fusion, "reverse engineer this video", "is script ke prompts bana do", "ye style copy kro", "in videos ko mix kro", or wants Omni Flash/Veo/Sora/Kling prompts for a motion graphics or explainer video. If the user only names the skill without a script and style references, do NOT generate prompts; ask for them first.
---

# Motion Style Fusion v2

Input: a **script** + **style references** (video / link / screenshots, one or many).
Output: a numbered series of shot prompts (4 / 6 / 8 / 10 s) that recreate the references' look, motion and sound-effect feel for that script.

## Language
Talk to the user in their language (Roman Urdu if they write Roman Urdu). The prompt blocks are always English and contain zero commentary.

## Hard rules (each one exists because a past run failed without it)
1. **Plain language only inside prompts.** Never write hex codes, rgb/hsl, px/pt/em/%, resolution, fps, or font names. Video models paint whatever text they receive, so `#7008A3` or `12px` appears on screen as garbage text. Hex may exist in your analysis notes only; translate every color to a name ("vivid royal purple") and every size to words ("large", "half the frame width").
2. **Calm, simple shots.** One hero subject, at most 6 objects, rigid solid shapes. Beats per shot: 4 s and 6 s max 2, 8 s and 10 s max 3. Many cuts and crowded scenes make the model morph and melt. Never use morph/liquid/melt/warp/"turns into"/"breaks into particles". See `references/motion-vocabulary.md`.
3. **On-screen text is only the exact quoted words** (8 words or fewer per shot), followed by "No other text...". Everything else in the prompt is invisible description.
4. **Sound = sound effects only.** Every prompt states "No music. No voiceover, narration, speech, or singing - not a single spoken word." Ignore any music or speech in the references; carry over only their SFX character.
5. **Shot lengths are 4, 6, 8 or 10 seconds**, nothing else.
6. **Continuation shots** start from the exact last frame of the previous shot and the user is told to attach it (details below).
7. **Never output prompts before the intake gate is satisfied.**

## Step 0 - Intake gate
Decide what the user has given:
- Only mentioned the skill / has neither script nor references -> ask once, briefly: send (1) the video script and (2) the styles you like (upload videos or screenshots, or paste links; several allowed). Mention they may also add brand/palette/text changes, and whether they want styles blended or randomly picked. **Generate nothing yet, not even a sample prompt.**
- Script only -> ask for style references. Script missing -> ask for it.
- If they say "no references, you choose" -> proceed, pick a style yourself and say so in one line.
- Both present -> continue. Do not ask about anything that has a default (aspect ratio 9:16, shot lengths, SFX-only).

## Step 1 - Acquire references (be honest about what you can see)
- **Uploaded video:** `python scripts/extract_frames.py <video> --out <dir>`. View `contact_sheet.jpg` first, then key frames. Read `meta.json`, `palette.json` (has color names) and `sfx_events.json` (SFX hints). Frames cover the whole video plus scene cuts.
- **Direct .mp4 link:** try `curl -L`; blocked host -> say so, ask for an upload.
- **YouTube/Pinterest/Instagram/X/Vimeo page link:** the sandbox usually cannot download these. Use `web_fetch` / `web_search` for title, description, thumbnail only. Say clearly that the analysis of that link is partial (give confidence) and invite an upload or screenshots. Never invent shots, timings or text you could not see; mark guesses `(inferred)`.
- **Screenshots only:** treat as keyframes; motion and sound are inferred.

## Step 2 - Analyze each reference (V1, V2, ...)
Follow `references/analysis-template.md`: look, motion, transitions, text behavior, **and sound effects**. For SFX:
1. Read `sfx_events.json`. Labels are signal-based hints (thud, click, swish, pop...), not human listening; cross-check each event with `on_cut` and the visual beat it lands on.
2. If `music_likelihood` > 0.55 or `voice_likelihood` > 0.6, treat that layer as noise and ignore it.
3. Build an **SFX signature**: which visual events get which sound (e.g. hard cut = deep soft thud plus quick swish; text reveal = airy whoosh; object landing = soft pop). If audio is missing or unclear, infer from visuals with `references/sfx-vocabulary.md` and mark `(inferred)`.
End each analysis with its Style DNA card.

## Step 3 - Style lock
Write ONE plain-language STYLE sentence (look, named palette, lighting, material, lettering look, finish) and reuse it word for word in every prompt so the series matches. Mode (`references/fusion-rules.md`):
- **Fusion** (default for a script, keeps the series consistent): blend 2+ references into one new original style.
- **Assign:** user asked for random/variety -> pick the lead style per scene with real randomness (`python -c "import random;print(random.sample(range(N),N))"`). A continuation shot always keeps its previous shot's style.
Apply any user overrides (brand, palette, copy, tone, add/remove elements); everything else stays faithful to the references. Do not copy logos, characters or distinctive artwork from references; use generic stand-ins.

## Step 4 - Shot plan
Run `python scripts/plan_shots.py <script.txt>` for a draft, then refine by story logic using `references/shot-planning.md`. Each shot gets a length of 4, 6, 8 or 10 s that fits its narration. A long idea whose motion truly continues is split into a lead shot and **continuation shot(s)**; unrelated ideas get fresh shots.

## Step 5 - Write the prompts
Use the exact format in `references/prompt-template.md`. Key points: timed ACTION lines with one clear motion each, ON-SCREEN TEXT line, MOTION line, SOUND line with timed SFX only, END = a still held final frame (needed so the last frame is clean for the next shot).
- Fresh shot: `START: Begin on a fresh, clean frame.`
- Continuation shot: `START: Start with the exact last frame of the previous shot (the attached image), then continue the same motion without any cut.` Keep subject descriptions, style sentence and background identical to the previous shot.

## Step 6 - Lint (mandatory)
Save all prompts as fenced blocks in `/tmp/prompts.md`, run `python scripts/lint_prompts.py /tmp/prompts.md`, fix every ERROR, rerun until clean. Do not show lint output to the user.

## Step 7 - Deliver
Order: (1) one line of confidence note if any reference was partial; (2) short style summary in plain words, mode used, and the SFX signature found; (3) shot table: shot, seconds, script excerpt, fresh/continuation; (4) the prompts, each under a heading `Shot N - X seconds` with an **Attach:** line:
- fresh shot -> `Attach: nothing.`
- continuation -> `Attach: the last frame of Shot N-1. Generate Shot N-1 first, then run python scripts/last_frame.py shotN-1.mp4 (or pause on the final frame and screenshot it) and attach that image.`
(5) a settings reminder: set aspect ratio (9:16 default) and the shot duration in the tool, not in the prompt. If there are more than 5 shots also save `prompts.md` to outputs and present it.

## When the user reports bad output
Read `references/troubleshooting.md`, fix the cause in the prompt (fewer beats, plainer words, shorter text), re-lint, and resend only the affected shots.
