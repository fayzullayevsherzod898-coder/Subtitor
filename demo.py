#!/usr/bin/env python3
"""
Sinov uchun: soxta 1080x1920 video + qo'lda yozilgan so'z vaqtlari.
ASR'ga pul to'lamasdan stillarni ko'rish uchun.
"""
import json
import subprocess
import os

HERE = os.path.dirname(os.path.abspath(__file__))

MATN = (
    "Salom Bugun sizga kofe haqida gapiraman "
    "Caffelitoda yangi mavsumiy ichimlik paydo boldi "
    "Uni albatta sinab koring"
).split()

# Har bir so'zga taxminiy davomiylik (uzun so'z — uzunroq)
words, t = [], 0.35
for w in MATN:
    dur = 0.20 + len(w) * 0.042
    words.append({"word": w, "start": round(t, 2), "end": round(t + dur, 2)})
    t += dur + 0.07

TOTAL = round(t + 0.6, 1)


def make_video(path):
    """Gradient fon + harakatlanuvchi doira — subtitr o'qilishini tekshirish uchun."""
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i",
        f"gradients=s=1080x1920:c0=0x1a2b4a:c1=0x8a4b2a:d={TOTAL}:speed=0.08:r=30",
        "-f", "lavfi", "-i", f"sine=frequency=220:duration={TOTAL}",
        "-vf", "drawbox=x=0:y=0:w=1080:h=1920:color=black@0.15:t=fill",
        "-t", str(TOTAL),
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest",
        path,
    ], check=True, capture_output=True)


if __name__ == "__main__":
    with open(os.path.join(HERE, "sozlar.json"), "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=1)

    make_video(os.path.join(HERE, "test.mp4"))
    print(f"test.mp4 ({TOTAL}s) va sozlar.json ({len(words)} so'z) tayyor")
