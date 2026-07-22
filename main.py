#!/usr/bin/env python3
"""
Subtitr prototip — video kiradi, subtitrli video chiqadi.

Ishlatish:
    # to'liq: ovozni tanish + render
    python3 main.py video.mp4 -s karaoke -o natija.mp4

    # tayyor so'z vaqtlaridan (ASR'ga qayta pul to'lamasdan stil sinash)
    python3 main.py video.mp4 -s pop --words sozlar.json -o natija.mp4

    # faqat .ass fayl (CapCut/Premiere'ga import qilish uchun)
    python3 main.py video.mp4 --ass-only -o subtitr.ass
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile

from ass_builder import build_ass
from styles import STYLES


def probe(video_path):
    """Video o'lchamini oladi — .ass PlayRes shunga mos bo'lishi shart."""
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "json", video_path],
        check=True, capture_output=True, text=True,
    )
    s = json.loads(r.stdout)["streams"][0]
    return int(s["width"]), int(s["height"])


def render(video_path, ass_path, out_path, crf=20, preset="medium"):
    """Subtitrni videoga kuydiradi (burn-in)."""
    # Windows'da yo'l ichidagi ':' va '\' ffmpeg filtrini buzadi
    safe = ass_path.replace("\\", "/").replace(":", "\\:")

    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vf", f"ass='{safe}'",
        "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
        "-pix_fmt", "yuv420p", "-profile:v", "high",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        out_path,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2500:], file=sys.stderr)
        raise RuntimeError("ffmpeg render xatosi")
    return out_path


def main():
    p = argparse.ArgumentParser(description="Video subtitr prototipi")
    p.add_argument("video", help="kirish video fayli")
    p.add_argument("-s", "--style", default="karaoke",
                   choices=list(STYLES), help="subtitr stili")
    p.add_argument("-o", "--out", default="natija.mp4", help="chiqish fayli")
    p.add_argument("-l", "--lang", default="uz", help="til kodi")
    p.add_argument("-p", "--provider", default="openai",
                   choices=["openai", "eleven", "local"], help="ASR xizmati")
    p.add_argument("--words", help="tayyor so'z vaqtlari (.json)")
    p.add_argument("--save-words", help="so'z vaqtlarini shu faylga saqlash")
    p.add_argument("--ass-only", action="store_true",
                   help="renderlamasdan faqat .ass chiqarish")
    args = p.parse_args()

    if not os.path.exists(args.video):
        sys.exit(f"Fayl topilmadi: {args.video}")

    # 1. So'z vaqtlari
    if args.words:
        with open(args.words, encoding="utf-8") as f:
            words = json.load(f)
        print(f"[1/3] {len(words)} ta so'z fayldan o'qildi")
    else:
        import asr
        print(f"[1/3] Ovoz tanilmoqda ({args.provider})...")
        words = asr.transcribe(args.video, provider=args.provider,
                               language=args.lang)
        print(f"      {len(words)} ta so'z topildi")
        if args.save_words:
            asr.save_words(words, args.save_words)

    if not words:
        sys.exit("Nutq topilmadi — ovoz yo'q yoki juda past")

    # 2. .ass yasash
    w, h = probe(args.video)
    ass_text = build_ass(words, style_name=args.style, width=w, height=h)
    print(f"[2/3] .ass tayyor — {args.style} stili, {w}x{h}")

    if args.ass_only:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(ass_text)
        print(f"[3/3] Saqlandi: {args.out}")
        return

    ass_path = tempfile.mktemp(suffix=".ass")
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass_text)

    # 3. Render
    print("[3/3] Render...")
    try:
        render(args.video, ass_path, args.out)
    finally:
        os.remove(ass_path)

    size = os.path.getsize(args.out) / 1024 / 1024
    print(f"Tayyor: {args.out} ({size:.1f} MB)")


if __name__ == "__main__":
    main()
