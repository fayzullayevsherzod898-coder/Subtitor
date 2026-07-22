"""
Subtitr stillari (presetlar).

MUHIM: ASS formatida ranglar &HAABBGGRR& ko'rinishida — ya'ni TESKARI (BGR),
va AA = shaffoflik (00 = to'liq ko'rinadi, FF = ko'rinmas).
Masalan sariq = RGB(255,255,0) -> &H0000FFFF&
"""

# --- Yordamchi: RGB -> ASS rang ---
def rgb(r, g, b, alpha=0):
    return f"&H{alpha:02X}{b:02X}{g:02X}{r:02X}&"


WHITE = rgb(255, 255, 255)
BLACK = rgb(0, 0, 0)
YELLOW = rgb(255, 214, 0)
GREEN = rgb(0, 255, 128)
PINK = rgb(255, 45, 120)
CYAN = rgb(0, 229, 255)


STYLES = {
    # 1. Oddiy, ishonchli. Instagram/YouTube uchun universal.
    "klassik": {
        "label": "Klassik",
        "font": "DejaVu Sans",
        "fontsize": 78,
        "bold": -1,
        "primary": WHITE,
        "outline_colour": BLACK,
        "back_colour": rgb(0, 0, 0, 0x80),
        "border_style": 1,      # 1 = kontur, 3 = fon qutisi
        "outline": 5,
        "shadow": 2,
        "alignment": 2,          # 2 = past-markaz
        "margin_v": 260,
        "words_per_line": 4,
        "highlight": None,       # so'z-so'z rang o'zgarishi yo'q
        "pop": False,
        "uppercase": False,
    },

    # 2. Karaoke: faol so'z sariq bo'lib yonadi. Eng ko'p ishlatiladigan.
    "karaoke": {
        "label": "Karaoke",
        "font": "DejaVu Sans",
        "fontsize": 82,
        "bold": -1,
        "primary": WHITE,
        "outline_colour": BLACK,
        "back_colour": rgb(0, 0, 0, 0x80),
        "border_style": 1,
        "outline": 6,
        "shadow": 0,
        "alignment": 2,
        "margin_v": 280,
        "words_per_line": 4,
        "highlight": YELLOW,
        "pop": False,
        "uppercase": False,
    },

    # 3. Pop: faol so'z kattalashib chiqadi + rang. TikTok uslubi.
    "pop": {
        "label": "Pop",
        "font": "DejaVu Sans",
        "fontsize": 84,
        "bold": -1,
        "primary": WHITE,
        "outline_colour": BLACK,
        "back_colour": rgb(0, 0, 0, 0x80),
        "border_style": 1,
        "outline": 7,
        "shadow": 0,
        "alignment": 2,
        "margin_v": 300,
        "words_per_line": 3,
        "highlight": GREEN,
        "pop": True,             # \t() bilan masshtab animatsiyasi
        "uppercase": True,
    },

    # 4. Neon: qora fon qutisi + yorqin rang. Shovqinli fonda o'qiladi.
    "neon": {
        "label": "Neon",
        "font": "DejaVu Sans",
        "fontsize": 76,
        "bold": -1,
        "primary": WHITE,
        "outline_colour": rgb(0, 0, 0, 0x30),
        "back_colour": rgb(0, 0, 0, 0x30),
        "border_style": 3,       # to'liq fon qutisi
        "outline": 12,
        "shadow": 0,
        "alignment": 2,
        "margin_v": 300,
        "words_per_line": 4,
        "highlight": CYAN,
        "pop": False,
        "uppercase": False,
    },

    # 5. Markaz: ekran o'rtasida, bitta-ikkita so'z. Dinamik kliplar uchun.
    "markaz": {
        "label": "Markaz",
        "font": "DejaVu Sans",
        "fontsize": 96,
        "bold": -1,
        "primary": WHITE,
        "outline_colour": BLACK,
        "back_colour": rgb(0, 0, 0, 0x80),
        "border_style": 1,
        "outline": 8,
        "shadow": 3,
        "alignment": 5,          # 5 = markaz-markaz
        "margin_v": 40,
        "words_per_line": 2,
        "highlight": PINK,
        "pop": True,
        "uppercase": True,
    },
}


def get(name):
    if name not in STYLES:
        raise ValueError(
            f"'{name}' stili yo'q. Mavjudlari: {', '.join(STYLES)}"
        )
    return STYLES[name]
