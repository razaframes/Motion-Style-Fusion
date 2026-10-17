# Shot planning

## Allowed lengths: 4, 6, 8, 10 seconds
Fit the shot to its narration chunk: take the smallest allowed length that covers the narration plus about half a second of breathing room (narration is spoken separately by the user, so on-screen text and motion should land just before or with the matching words). A one-line idea can be 4 s; a two-sentence idea 6-8 s; a dense idea 10 s.

## Fresh shot vs continuation shot
Use a **continuation** only when one idea outlasts 10 s (or 8 s) and the same subject, camera and motion must carry on without a cut. Examples: a character slowly buried in paper over two shots, a counter that keeps rising, a camera push that keeps going.
Use **fresh shots** for new ideas, even if the topic is related; a hard cut is fine and safer than forcing continuity.

## Rules for continuation chains
- The lead shot ends on a still, well-composed held frame (half second hold) so its last frame is a clean starting image.
- Continuation shot: `START: Start with the exact last frame of the previous shot (the attached image), then continue the same motion without any cut.`
- Repeat the same STYLE sentence and the same subject wording; keep the same background unless the story demands a cut inside the shot.
- The user must generate in order and attach the last frame: tell them in the `Attach:` line.
- Chains longer than 3 shots drift; prefer breaking into a fresh shot with a deliberate cut.

## Splitting narration
Split at sentence ends. Keep numbers and lists (e.g. "Income. Property. Energy.") in one shot as a slow sequence of at most three beats, not nine rapid cuts; if the list is long, group items (three per shot) or show the first few and imply the rest.
Use `scripts/plan_shots.py` for a draft table, then edit. It estimates narration time at about 2.5 words per second unless the script has timecodes.
