#!/usr/bin/env python3
"""
Extract analysis material from a motion-graphics video.

Usage:
  python extract_frames.py VIDEO [--out DIR] [--max-frames 24] [--cols 4]

Outputs in DIR (default: ./frames_<videoname>):
  - meta.json          : duration, resolution, fps, aspect ratio, has_audio, codec
  - frame_XX_<t>s.jpg  : frames spread over the WHOLE duration + scene-change frames
  - contact_sheet.jpg  : numbered grid of all frames (view this first for a quick overview)
  - palette.json       : dominant colors overall and per frame, each with a PLAIN COLOR NAME.
                         Hex is for YOUR analysis only; prompts must use the names, never hex.
  - sfx_events.json    : heuristic SFX events (time, plain-language label, nearest scene cut) plus
                         music/voice likelihood so music and speech can be ignored
  - audio_profile.json : loudness / silence segments (only if audio exists)

Why this exists: sampling only the first seconds misses most of a motion video.
Frames are chosen as a union of (a) evenly spaced timestamps and (b) detected scene cuts,
so both slow-moving and fast-cutting videos get covered.
"""
import argparse, json, os, re, subprocess, sys
from pathlib import Path

def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)

def probe(video):
    r = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", video])
    if r.returncode != 0:
        sys.exit(f"ffprobe failed: {r.stderr}")
    info = json.loads(r.stdout)
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    if not v:
        sys.exit("No video stream found")
    num, den = (v.get("avg_frame_rate") or "0/1").split("/")
    fps = round(float(num) / float(den), 3) if float(den) else 0
    w, h = int(v["width"]), int(v["height"])
    from math import gcd
    g = gcd(w, h)
    dur = float(info["format"].get("duration") or v.get("duration") or 0)
    return {
        "duration_s": round(dur, 3), "width": w, "height": h,
        "aspect_ratio": f"{w//g}:{h//g}", "fps": fps,
        "video_codec": v.get("codec_name"), "has_audio": a is not None,
        "audio_codec": a.get("codec_name") if a else None,
        "bitrate_kbps": round(int(info["format"].get("bit_rate", 0)) / 1000),
    }

def scene_cuts(video, threshold=0.25):
    r = run(["ffmpeg", "-i", video, "-vf", f"select='gt(scene,{threshold})',showinfo", "-f", "null", "-"])
    return [float(m) for m in re.findall(r"pts_time:([\d.]+)", r.stderr)]

def pick_times(duration, n_even, cuts, max_frames):
    times = [duration * (i + 0.5) / n_even for i in range(n_even)]
    times += [max(0, t + 0.05) for t in cuts]
    times += [0.05, max(0, duration - 0.1)]  # always include first and last held frame
    times = sorted(set(round(t, 2) for t in times if 0 <= t < duration))
    # thin out near-duplicates (<0.2s apart), then cap
    thinned = []
    for t in times:
        if not thinned or t - thinned[-1] >= 0.2:
            thinned.append(t)
    if len(thinned) > max_frames:
        step = len(thinned) / max_frames
        thinned = [thinned[int(i * step)] for i in range(max_frames)]
        if thinned[-1] < duration - 0.3:
            thinned[-1] = round(max(0, duration - 0.1), 2)
    return thinned

def grab(video, t, path, width=960):
    run(["ffmpeg", "-y", "-ss", str(t), "-i", video, "-frames:v", "1", "-vf", f"scale={width}:-2", "-q:v", "3", path])

NAMED = {
    "pure white": (255, 255, 255), "warm cream": (245, 241, 229), "light grey": (215, 215, 215),
    "mid grey": (140, 140, 140), "charcoal": (55, 55, 60), "near-black": (10, 6, 24), "black": (0, 0, 0),
    "soft lilac": (222, 196, 233), "pale lavender": (232, 224, 245), "vivid royal purple": (112, 8, 163),
    "deep violet": (60, 20, 110), "electric violet": (140, 60, 230), "hot pink": (240, 60, 150),
    "soft rose pink": (240, 180, 190), "crimson red": (200, 30, 50), "bright red": (230, 40, 40),
    "burnt orange": (220, 110, 30), "golden yellow": (242, 195, 24), "pale butter yellow": (250, 235, 160),
    "lime green": (170, 230, 50), "emerald green": (20, 150, 90), "forest green": (20, 80, 50),
    "teal": (20, 150, 160), "sky blue": (120, 190, 240), "electric blue": (30, 110, 255),
    "royal blue": (40, 70, 200), "deep navy": (12, 20, 70), "chocolate brown": (95, 55, 35),
    "sand beige": (210, 190, 150), "silver": (190, 195, 200), "warm gold": (200, 160, 70),
}

def color_name(rgb):
    best, bd = None, 1e18
    for n, c in NAMED.items():
        d = sum(w * (a - b) ** 2 for w, a, b in zip((0.3, 0.59, 0.11), rgb, c))
        if d < bd:
            best, bd = n, d
    return best

def dominant_colors(img_path, k=5):
    from PIL import Image
    import numpy as np
    im = Image.open(img_path).convert("RGB").resize((96, 96))
    q = im.quantize(colors=k, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()[: k * 3]
    counts = sorted(q.getcolors(), reverse=True)
    out = []
    total = sum(c for c, _ in counts)
    for c, idx in counts:
        r, g, b = pal[idx * 3: idx * 3 + 3]
        out.append({"hex": f"#{r:02X}{g:02X}{b:02X}", "name": color_name((r, g, b)), "share": round(c / total, 3)})
    return out

def contact_sheet(frames, out, cols=4, thumb_w=360):
    from PIL import Image, ImageDraw
    thumbs = []
    for i, (t, p) in enumerate(frames):
        im = Image.open(p).convert("RGB")
        r = thumb_w / im.width
        im = im.resize((thumb_w, int(im.height * r)))
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, 110, 22], fill=(0, 0, 0))
        d.text((6, 4), f"#{i+1}  {t:.2f}s", fill=(255, 255, 255))
        thumbs.append(im)
    rows = (len(thumbs) + cols - 1) // cols
    th = max(t.height for t in thumbs)
    sheet = Image.new("RGB", (cols * thumb_w, rows * th), (20, 20, 20))
    for i, im in enumerate(thumbs):
        sheet.paste(im, ((i % cols) * thumb_w, (i // cols) * th))
    sheet.save(out, quality=85)

def audio_profile(video, out_json):
    r = run(["ffmpeg", "-i", video, "-af", "silencedetect=noise=-40dB:d=0.15", "-f", "null", "-"])
    silences = re.findall(r"silence_(start|end): ([\d.]+)", r.stderr)
    v = run(["ffmpeg", "-i", video, "-af", "volumedetect", "-f", "null", "-"])
    mean = re.search(r"mean_volume: ([-\d.]+) dB", v.stderr)
    mx = re.search(r"max_volume: ([-\d.]+) dB", v.stderr)
    prof = {"mean_volume_db": float(mean.group(1)) if mean else None,
            "max_volume_db": float(mx.group(1)) if mx else None,
            "silence_events": [{"type": k, "t": float(t)} for k, t in silences]}
    json.dump(prof, open(out_json, "w"), indent=2)
    return prof

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--out")
    ap.add_argument("--max-frames", type=int, default=24)
    ap.add_argument("--cols", type=int, default=4)
    a = ap.parse_args()

    name = Path(a.video).stem
    out = Path(a.out or f"frames_{name}")
    out.mkdir(parents=True, exist_ok=True)

    meta = probe(a.video)
    json.dump(meta, open(out / "meta.json", "w"), indent=2)
    dur = meta["duration_s"]

    n_even = min(a.max_frames, max(8, int(dur * 1.5)))  # ~1.5 frames/sec, at least 8
    cuts = scene_cuts(a.video)
    times = pick_times(dur, n_even, cuts, a.max_frames)

    frames, palettes = [], {}
    for i, t in enumerate(times):
        p = str(out / f"frame_{i+1:02d}_{t:.2f}s.jpg")
        grab(a.video, t, p)
        if os.path.exists(p):
            frames.append((t, p))
            palettes[os.path.basename(p)] = dominant_colors(p)

    contact_sheet(frames, str(out / "contact_sheet.jpg"), cols=a.cols)

    # overall palette = average of share-weighted per-frame colors (simple merge by hex)
    agg, names = {}, {}
    for cols in palettes.values():
        for c in cols:
            agg[c["hex"]] = agg.get(c["hex"], 0) + c["share"]
            names[c["hex"]] = c["name"]
    overall = sorted(agg.items(), key=lambda kv: -kv[1])[:8]
    json.dump({"overall_top": [{"hex": h, "name": names[h], "weight": round(w, 2)} for h, w in overall],
               "per_frame": palettes}, open(out / "palette.json", "w"), indent=2)

    if meta["has_audio"]:
        audio_profile(a.video, str(out / "audio_profile.json"))
        try:
            sys.path.insert(0, str(Path(__file__).parent))
            from analyze_audio import analyze
            sfx = analyze(a.video)
            for ev in sfx.get("events", []):
                near = min(cuts, key=lambda c: abs(c - ev["t"])) if cuts else None
                ev["on_cut"] = bool(near is not None and abs(near - ev["t"]) <= 0.15)
                ev["nearest_cut_s"] = round(near, 2) if near is not None else None
            sfx["scene_cuts_s"] = [round(c, 2) for c in cuts]
            json.dump(sfx, open(out / "sfx_events.json", "w"), indent=2)
        except Exception as e:  # audio analysis is best-effort
            print(f"[warn] sfx analysis skipped: {e}", file=sys.stderr)

    print(json.dumps({"out_dir": str(out), "frames": len(frames),
                      "scene_cuts_detected": len(cuts), **meta}, indent=2))

if __name__ == "__main__":
    main()
