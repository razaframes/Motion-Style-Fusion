#!/usr/bin/env python3
"""
Lint generated video prompts BEFORE giving them to the user.

Usage: python lint_prompts.py prompts.md        (every ``` fenced block is checked as one prompt)
       cat prompts.md | python lint_prompts.py -

Why: video models paint text they are given. Hex codes, pixel sizes, font names and tech specs
written into a prompt show up on screen as garbled text. Dense scenes and words like "morph" or
"liquid" produce wobbly, melting motion. Exit code 1 if any ERROR is found.
"""
import re, sys

ALLOWED_DURATIONS = {4, 6, 8, 10}
MAX_BEATS = {4: 2, 6: 2, 8: 3, 10: 3}
FONTS = r"playfair|bebas|helvetica|arial|roboto|montserrat|didot|futura|times new|georgia|garamond|impact font|oswald|poppins|\binter\b|font-family|typeface name"
RISKY = r"morph|liquid|melt|warp|shapeshift|metamorph|fluid shape|dissolves? into|transforms? into|turns? into|breaks? into (dots|particles|pieces)"
CROWD = r"\b(dozens?|hundreds?|countless|swarm|crowd of|grid of \d{2,}|\d{2,} (tiles|icons|coins|items|cards|objects))\b"

def blocks(text):
    return re.findall(r"```(?:[a-z]*)\n(.*?)```", text, re.S)

def strip_negated(line):
    return line

def lint(block, idx):
    errs, warns = [], []
    lines = [l.rstrip() for l in block.strip().splitlines()]
    body = "\n".join(lines)
    # lines where "avoid" words are allowed
    scan = "\n".join(l for l in lines if not re.match(r"\s*(AVOID|MOTION)\b", l, re.I))

    if re.search(r"#[0-9a-fA-F]{3,8}\b", body):
        errs.append("hex color code found (it will be painted on screen). Use plain color names.")
    if re.search(r"\b(rgb|rgba|hsl|hsla)\s*\(", body, re.I):
        errs.append("rgb()/hsl() color found. Use plain color names.")
    if re.search(r"\b\d+(\.\d+)?\s?(px|pt|em|rem|dpi|%)(?!\w)", body, re.I) or re.search(r"\d\s?%", body):
        errs.append("pixel/percent/point sizes found. Describe size in plain words (small, half the frame width).")
    if re.search(r"\b\d{3,4}\s?[x×]\s?\d{3,4}\b", body) or re.search(r"\b\d+\s?fps\b", body, re.I):
        errs.append("resolution/fps in prompt. Set these in the tool, not in the prompt.")
    if re.search(FONTS, body, re.I):
        errs.append("font name found. Describe letter shapes in plain words instead.")
    if re.search(r"\b(bpm|melody|soundtrack|lyrics|beat drop|chord)\b", body, re.I):
        errs.append("music words found. Prompts are SFX-only.")
    m = re.search(RISKY, scan, re.I)
    if m:
        errs.append(f'risky motion word "{m.group(0)}" (causes melting/wobble). Use slide, scale, wipe, cross-fade, or a clean cut.')
    m = re.search(CROWD, scan, re.I)
    if m:
        warns.append(f'dense scene wording "{m.group(0)}". Keep to 6 objects or fewer per shot.')

    dm = re.search(r"^DURATION:\s*(\d+)\s*seconds?", body, re.I | re.M)
    dur = int(dm.group(1)) if dm else None
    if dur is None:
        errs.append("missing 'DURATION: N seconds.' line")
    elif dur not in ALLOWED_DURATIONS:
        errs.append(f"duration {dur}s not allowed (use 4, 6, 8 or 10)")

    for key in ("STYLE", "START", "ACTION", "ON-SCREEN TEXT", "MOTION", "SOUND", "END"):
        if not re.search(rf"^{key}\b", body, re.M):
            errs.append(f"missing {key} line")

    st = re.search(r"^START:(.*)$", body, re.M)
    if st and re.search(r"last frame", st.group(1), re.I) and not re.search(r"exact last frame", st.group(1), re.I):
        errs.append("continuation START must say 'exact last frame'")

    sound = re.search(r"^SOUND:(.*?)(?=^\w[\w -]*:|\Z)", body, re.M | re.S)
    s_txt = sound.group(1) if sound else ""
    if not re.search(r"\bno music\b", body, re.I):
        errs.append("SOUND must state 'No music.'")
    if not re.search(r"no voice-?over", body, re.I) or not re.search(r"spoken word", body, re.I):
        errs.append("SOUND must state 'No voiceover ... not a single spoken word.'")
    if s_txt and not re.search(r"\d", s_txt):
        warns.append("SOUND has no timestamps; time each effect to a visual beat")

    ot = re.search(r"^ON-SCREEN TEXT:(.*?)(?=^[A-Z][A-Z -]*:|\Z)", body, re.M | re.S)
    if ot:
        t = ot.group(1)
        quoted = re.findall(r'"([^"]+)"', t)
        if quoted:
            wc = sum(len(q.split()) for q in quoted)
            if wc > 10:
                warns.append(f"{wc} words of on-screen text; models spell better with 8 or fewer per shot")
            if not re.search(r"no other (text|letters)", t, re.I):
                errs.append("ON-SCREEN TEXT must say 'No other text...'")
        elif not re.search(r"\bnone\b", t, re.I):
            errs.append("ON-SCREEN TEXT must list quoted words or say 'None.'")

    beats = re.findall(r"^\s*(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*s\s*:", body, re.M)
    if dur and beats:
        if len(beats) > MAX_BEATS.get(dur, 3):
            errs.append(f"{len(beats)} beats in {dur}s (max {MAX_BEATS.get(dur, 3)}). Fewer, calmer beats avoid morphing.")
        prev = 0.0
        for a, b in beats:
            a, b = float(a), float(b)
            if abs(a - prev) > 0.11 or b <= a:
                errs.append("ACTION time ranges must tile the shot with no gaps or overlaps")
                break
            prev = b
        if abs(prev - dur) > 0.11:
            errs.append(f"ACTION ends at {prev}s but DURATION is {dur}s")
    elif dur:
        errs.append("ACTION needs timed lines like '0-4s: ...'")

    wc = len(body.split())
    if wc > 330:
        warns.append(f"{wc} words; shorter prompts are followed more faithfully (aim under 300)")
    return errs, warns

def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "-"
    text = sys.stdin.read() if src == "-" else open(src, encoding="utf-8").read()
    bl = blocks(text)
    if not bl:
        print("No fenced prompt blocks found."); sys.exit(1)
    bad = 0
    for i, b in enumerate(bl, 1):
        e, w = lint(b, i)
        status = "FAIL" if e else "ok"
        print(f"Prompt {i}: {status}")
        for x in e: print("  ERROR:", x)
        for x in w: print("  warn: ", x)
        bad += bool(e)
    print(f"\n{len(bl)} prompt(s) checked, {bad} failing.")
    sys.exit(1 if bad else 0)

if __name__ == "__main__":
    main()
