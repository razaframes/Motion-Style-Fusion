#!/usr/bin/env python3
"""
Heuristic sound-effect analysis for a reference video (numpy + ffmpeg only).

IMPORTANT: this does not "listen". It measures the signal (transients, spectrum, decay,
periodicity) and labels each event with a plain-language SFX guess. Treat labels as hints and
cross-check them against the visual cuts. Music and speech are DETECTED so they can be IGNORED:
the skill only carries SFX over into prompts.

Usage:  python analyze_audio.py VIDEO [--out sfx_events.json]
"""
import argparse, json, subprocess, sys
import numpy as np

SR = 22050
N_FFT = 1024
HOP = 256

def decode(video):
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", video, "-vn", "-ac", "1", "-ar", str(SR),
                        "-f", "s16le", "-"], capture_output=True)
    if p.returncode != 0 or not p.stdout:
        return None
    return np.frombuffer(p.stdout, dtype=np.int16).astype(np.float32) / 32768.0

def stft_mag(x):
    if len(x) < N_FFT * 2:
        x = np.pad(x, (0, N_FFT * 2 - len(x)))
    win = np.hanning(N_FFT).astype(np.float32)
    n = 1 + (len(x) - N_FFT) // HOP
    idx = np.arange(N_FFT)[None, :] + HOP * np.arange(n)[:, None]
    return np.abs(np.fft.rfft(x[idx] * win, axis=1)).astype(np.float32)

def onset_env(mag):
    logm = np.log1p(mag * 20)
    flux = np.maximum(logm[1:] - logm[:-1], 0).sum(axis=1)
    flux = np.concatenate([[0], flux])
    k = np.ones(3) / 3
    return np.convolve(flux, k, mode="same")

def pick_peaks(env, min_gap_s=0.12):
    med = np.median(env)
    mad = np.median(np.abs(env - med)) + 1e-9
    thr = med + 6 * mad
    gap = int(min_gap_s * SR / HOP)
    peaks = []
    for i in range(1, len(env) - 1):
        if env[i] > thr and env[i] >= env[i - 1] and env[i] >= env[i + 1]:
            if not peaks or i - peaks[-1] >= gap:
                peaks.append(i)
            elif env[i] > env[peaks[-1]]:
                peaks[-1] = i
    return peaks

def classify(mag, i, freqs):
    n = mag.shape[0]
    end = min(n, i + int(0.45 * SR / HOP))
    seg = mag[max(0, i - 1):end]
    if len(seg) < 3:
        return None
    power = seg ** 2
    energy = power.sum(axis=1) + 1e-12
    peak_db = float(10 * np.log10(energy.max()))
    pk = int(np.argmax(energy))
    below = np.where(energy[pk:] < energy[pk] * 0.01)[0]  # -20 dB
    decay_s = float((below[0] if len(below) else len(energy) - pk) * HOP / SR)
    first = power[: max(2, int(0.15 * SR / HOP))].sum(axis=0)
    centroid = float((freqs * first).sum() / (first.sum() + 1e-12))
    low = float(first[freqs < 250].sum() / (first.sum() + 1e-12))
    high = float(first[freqs > 4000].sum() / (first.sum() + 1e-12))
    flat = float(np.exp(np.mean(np.log(first + 1e-12))) / (np.mean(first) + 1e-12))
    half = max(2, len(power) // 2)
    c1 = float((freqs * power[:half].sum(axis=0)).sum() / (power[:half].sum() + 1e-12))
    c2 = float((freqs * power[half:].sum(axis=0)).sum() / (power[half:].sum() + 1e-12)) if len(power) > half else c1
    slope = "rising" if c2 > c1 * 1.25 else "falling" if c2 < c1 * 0.8 else "flat"

    if low > 0.5 and centroid < 900:
        label = "deep thud / bass hit" if decay_s < 0.5 else "deep boom with tail"
    elif decay_s >= 0.2 and (high > 0.15 or flat > 0.02):
        label = {"rising": "rising whoosh", "falling": "falling swish", "flat": "airy whoosh / swish"}[slope]
    elif decay_s < 0.12 and centroid > 2500:
        label = "short click / tick / snap"
    elif decay_s < 0.25:
        label = "soft pop / thump"
    else:
        label = "accent hit with short tail"
    return {"label": label, "peak_db": round(peak_db, 1), "decay_s": round(decay_s, 2),
            "centroid_hz": round(centroid), "low_ratio": round(low, 2), "high_ratio": round(high, 2)}

def music_voice_scores(x, mag, env, freqs):
    # periodicity of onsets -> tempo-like regularity
    e = env - env.mean()
    ac = np.correlate(e, e, mode="full")[len(e) - 1:]
    lo, hi = int(0.25 * SR / HOP), int(1.0 * SR / HOP)
    per = float(ac[lo:hi].max() / (ac[0] + 1e-9)) if hi < len(ac) else 0.0
    # tonal sustained content
    power = mag ** 2
    flat_t = np.exp(np.mean(np.log(power + 1e-12), axis=1)) / (np.mean(power, axis=1) + 1e-12)
    loud = power.sum(axis=1) > np.percentile(power.sum(axis=1), 40)
    tonal = float(np.mean(flat_t[loud] < 0.01)) if loud.any() else 0.0
    # speech-like: 300-3400 Hz energy envelope modulated at 3-8 Hz
    band = (freqs > 300) & (freqs < 3400)
    be = power[:, band].sum(axis=1)
    be = be / (be.max() + 1e-12)
    spec = np.abs(np.fft.rfft(be - be.mean()))
    mf = np.fft.rfftfreq(len(be), d=HOP / SR)
    syl = float(spec[(mf >= 3) & (mf <= 8)].sum() / (spec[(mf >= 0.5) & (mf <= 20)].sum() + 1e-9))
    activity = float(np.mean(be > 0.03))  # speech keeps the band busy; SFX leaves gaps
    music = round(min(1.0, 0.55 * min(per * 2.5, 1) + 0.45 * tonal), 2)
    voice = round(min(1.0, syl * 1.6 * activity), 2)
    return music, voice, round(per, 2), round(tonal, 2), round(syl, 2)

def analyze(video):
    x = decode(video)
    if x is None or len(x) < SR * 0.3:
        return {"has_audio": False, "events": [], "note": "No usable audio. Infer SFX from the visuals (see references/sfx-vocabulary.md)."}
    mag = stft_mag(x)
    freqs = np.fft.rfftfreq(N_FFT, d=1 / SR)
    env = onset_env(mag)
    peaks = pick_peaks(env)
    events = []
    for i in peaks:
        c = classify(mag, i, freqs)
        if c:
            c["t"] = round(i * HOP / SR, 2)
            events.append(c)
    music, voice, per, tonal, syl = music_voice_scores(x, mag, env, freqs)
    rms = np.sqrt((mag ** 2).sum(axis=1))
    bed_db = round(float(20 * np.log10(np.percentile(rms, 20) / (rms.max() + 1e-9) + 1e-9)), 1)
    notes = []
    if music > 0.55:
        notes.append("Music bed likely present: IGNORE it. Do not describe any music in prompts.")
    if voice > 0.6:
        notes.append("Speech-like content MAY be present (heuristic): IGNORE it. Prompts must contain no voiceover at all.")
    if not events:
        notes.append("No clear transients found: infer SFX from cuts and motion.")
    return {"has_audio": True, "duration_s": round(len(x) / SR, 2), "events": events,
            "music_likelihood": music, "voice_likelihood": voice,
            "debug": {"periodicity": per, "tonal_fraction": tonal, "syllabic_modulation": syl, "quiet_bed_db_vs_peak": bed_db},
            "notes": notes,
            "disclaimer": "Heuristic labels from signal features, not human listening. Cross-check against cuts."}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--out")
    a = ap.parse_args()
    res = analyze(a.video)
    if a.out:
        json.dump(res, open(a.out, "w"), indent=2)
    print(json.dumps(res, indent=2))
