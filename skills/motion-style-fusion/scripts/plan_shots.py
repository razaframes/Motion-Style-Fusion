#!/usr/bin/env python3
"""
Suggest a shot plan (4 / 6 / 8 / 10 second shots) for a script.

Usage: python plan_shots.py script.txt [--wps 2.5] [--json]

Reads plain text. If the script has editor timecodes (HH:MM:SS:FF - HH:MM:SS:FF) the block
durations are used; otherwise narration time is estimated at --wps words per second.
This is a STARTING POINT: the skill then adjusts for story logic (see references/shot-planning.md).
"""
import argparse, json, re, sys

ALLOWED = [4, 6, 8, 10]
TC = re.compile(r"(\d\d):(\d\d):(\d\d):(\d\d)\s*-\s*(\d\d):(\d\d):(\d\d):(\d\d)")

def tc_s(h, m, s, f, fps=30):
    return int(h) * 3600 + int(m) * 60 + int(s) + int(f) / fps

def sentences(text):
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]

def parse(path):
    raw = open(path, encoding="utf-8").read()
    lines = [l.rstrip() for l in raw.splitlines()]
    blocks, cur = [], None
    for l in lines:
        m = TC.search(l)
        if m:
            g = m.groups()
            cur = {"start": tc_s(*g[:4]), "end": tc_s(*g[4:]), "text": []}
            blocks.append(cur)
        elif cur is not None and l.strip() and l.strip().lower() != "unknown":
            cur["text"].append(l.strip())
    if blocks:
        return [(" ".join(b["text"]), max(b["end"] - b["start"], 0.1)) for b in blocks]
    return [(raw.strip(), None)]

def nearest_allowed(t):
    for a in ALLOWED:
        if t <= a:
            return a
    return ALLOWED[-1]

def plan(path, wps):
    units = []  # (sentence, seconds)
    for text, dur in parse(path):
        sents = sentences(text)
        words = [len(s.split()) for s in sents]
        total = sum(words) or 1
        for s, w in zip(sents, words):
            sec = (dur * w / total) if dur else w / wps
            units.append((s, sec))
    shots, cur, cur_t = [], [], 0.0
    for s, t in units:
        if cur and cur_t + t > 10.5:
            shots.append((cur, cur_t)); cur, cur_t = [], 0.0
        cur.append(s); cur_t += t
        if cur_t >= 7.5:
            shots.append((cur, cur_t)); cur, cur_t = [], 0.0
    if cur:
        shots.append((cur, cur_t))
    out = []
    for i, (ss, t) in enumerate(shots, 1):
        out.append({"shot": i, "narration_s": round(t, 1), "suggested_duration_s": nearest_allowed(t),
                    "words": sum(len(x.split()) for x in ss),
                    "needs_split_check": t > 10,
                    "script": " ".join(ss)})
    return out

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("script")
    ap.add_argument("--wps", type=float, default=2.5)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    p = plan(a.script, a.wps)
    if a.json:
        print(json.dumps(p, indent=2, ensure_ascii=False))
    else:
        for s in p:
            flag = "  [check: may need continuation shot]" if s["needs_split_check"] else ""
            print(f'Shot {s["shot"]:>2} | {s["suggested_duration_s"]:>2}s (narration ~{s["narration_s"]}s){flag}\n   {s["script"]}\n')
        print("Total planned:", sum(s["suggested_duration_s"] for s in p), "s")
