"""
So'z darajasidagi vaqt belgilaridan .ass subtitr fayli yasaydi.

Ishlash printsipi (muhim!):
Har bir so'z uchun ALOHIDA Dialogue qatori yoziladi. Har qatorda butun
guruh ko'rinadi, lekin faqat o'sha paytdagi faol so'z boshqa rangda /
kattaroq bo'ladi. Shuning uchun ekranda so'zlar "yonib" ketayotgandek
ko'rinadi. ASS'ning \k karaoke tegi qo'shiqlar uchun mo'ljallangan va
bu yerda kerak emas.
"""

from styles import get as get_style


def ts(seconds: float) -> str:
    """Sekundni ASS vaqt formatiga: 0:00:01.23"""
    if seconds < 0:
        seconds = 0
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def escape(text: str) -> str:
    """ASS uchun xavfli belgilarni tozalash."""
    return (
        text.replace("\\", "")
        .replace("{", "(")
        .replace("}", ")")
        .strip()
    )


def group_words(words, max_words=4, max_gap=0.7, max_dur=3.0):
    """
    So'zlarni qatorlarga bo'ladi.

    words: [{"word": "salom", "start": 0.0, "end": 0.4}, ...]

    Yangi qator boshlanadi agar:
      - so'zlar soni limitga yetsa
      - so'zlar orasida uzun jimlik bo'lsa (max_gap)
      - qator juda uzoq davom etsa (max_dur)
      - oldingi so'z tinish belgisi bilan tugasa
    """
    groups, cur = [], []
    for w in words:
        if cur:
            gap = w["start"] - cur[-1]["end"]
            dur = w["end"] - cur[0]["start"]
            ends_sentence = cur[-1]["word"].rstrip().endswith((".", "!", "?", "…"))
            if (
                len(cur) >= max_words
                or gap > max_gap
                or dur > max_dur
                or ends_sentence
            ):
                groups.append(cur)
                cur = []
        cur.append(w)
    if cur:
        groups.append(cur)
    return groups


def build_ass(words, style_name="karaoke", width=1080, height=1920):
    """So'z ro'yxatidan to'liq .ass fayl matnini qaytaradi."""
    st = get_style(style_name)

    header = f"""[Script Info]
Title: Subtitr prototip
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Main,{st['font']},{st['fontsize']},{st['primary']},{st['primary']},{st['outline_colour']},{st['back_colour']},{st['bold']},0,0,0,100,100,0,0,{st['border_style']},{st['outline']},{st['shadow']},{st['alignment']},80,80,{st['margin_v']},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    lines = []
    groups = group_words(words, max_words=st["words_per_line"])

    for g in groups:
        for i, active in enumerate(g):
            parts = []
            for j, w in enumerate(g):
                txt = escape(w["word"])
                if st["uppercase"]:
                    txt = txt.upper()

                if j == i and st["highlight"]:
                    tag = f"{{\\c{st['highlight']}"
                    if st["pop"]:
                        # 100% -> 118% -> 100% qisqa "sakrash"
                        tag += "\\t(0,80,\\fscx118\\fscy118)\\t(80,180,\\fscx100\\fscy100)"
                    tag += "}"
                    parts.append(f"{tag}{txt}{{\\c{st['primary']}\\fscx100\\fscy100}}")
                else:
                    parts.append(txt)

            text = " ".join(parts)

            # Guruhning birinchi so'zida yumshoq paydo bo'lish effekti
            prefix = "{\\fad(90,0)}" if i == 0 else ""

            start = active["start"]
            # Oxirgi so'z guruh oxirigacha ekranda qoladi
            end = active["end"] if i < len(g) - 1 else g[-1]["end"] + 0.12

            lines.append(
                f"Dialogue: 0,{ts(start)},{ts(end)},Main,,0,0,0,,{prefix}{text}"
            )

    return header + "\n".join(lines) + "\n"
