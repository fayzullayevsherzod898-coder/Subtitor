# Subtitr — prototip (Faza 0)

Video kiradi → so'z-so'z animatsiyalangan subtitrli video chiqadi.
Sinovdan o'tkazilgan: ffmpeg 6.1, 5 ta stil, 1080x1920.

## O'rnatish (Windows)

```powershell
# 1. ffmpeg — libass bilan bo'lishi SHART
winget install Gyan.FFmpeg
# PowerShell'ni yopib qayta och, keyin tekshir:
ffmpeg -version
# chiqishda "--enable-libass" bo'lishi kerak

# 2. Kutubxonalar
pip install -r requirements.txt
```

Windows'da `python3` emas, **`python`** deb yozasan.

Mac uchun: `brew install ffmpeg`

## Ishlatish

```bash
# 1. ASR'siz sinash — stillarni tekin ko'rish
python3 demo.py
python3 main.py test.mp4 -s karaoke --words sozlar.json -o natija.mp4

# 2. Haqiqiy video
export OPENAI_API_KEY=sk-...
python3 main.py mening_videom.mp4 -s pop -o natija.mp4

# 3. So'zlarni saqlab qo'yish (stil sinaganda ASR'ga qayta to'lamaslik uchun)
python3 main.py video.mp4 --save-words w.json -o natija.mp4
python3 main.py video.mp4 --words w.json -s neon -o natija2.mp4

# 4. Faqat .ass — CapCut/Premiere/Resolve'ga import qilish uchun
python3 main.py video.mp4 --ass-only -o subtitr.ass
```

## Stillar

| Nom | Tavsif |
|---|---|
| `klassik` | Oq qalin matn, qora kontur. Universal |
| `karaoke` | Faol so'z sariq bo'lib yonadi |
| `pop` | Faol so'z kattalashib chiqadi, BOSH HARF. TikTok uslubi |
| `neon` | Qora fon qutisi + moviy. Shovqinli fonda o'qiladi |
| `markaz` | Ekran o'rtasida, 2 so'zdan. Dinamik kliplar uchun |

Yangi stil qo'shish: `styles.py` ichida lug'atga bitta yozuv qo'shasan.
Kod o'zgartirilmaydi.

## Fayllar

```
styles.py       stil presetlari (rang, shrift, joylashuv)
ass_builder.py  so'z vaqtlari -> .ass fayl (asosiy mantiq shu yerda)
asr.py          OpenAI / ElevenLabs / mahalliy Whisper
main.py         CLI va ffmpeg render
demo.py         sinov videosi generatsiyasi
```

## O'lchangan natijalar (1 yadroli server)

| Preset | 9.3s video | ~60s videoga |
|---|---|---|
| medium | 28.6s | ~185s |
| fast | 26.4s | ~170s |
| veryfast | 15.5s | ~100s |

`veryfast` + `crf 21` — sifat farqi Reels'da ko'rinmaydi, vaqt 2 barobar kam.

## Muhim: arxitektura bo'yicha ogohlantirish

Serverda to'liq video render qilish — eng qimmat va eng sekin yo'l.
Foydalanuvchi 100 sekund kutadi, sen 50 MB yuklab olib, 50 MB qaytarasan.

**To'g'ri yo'l (Faza 1 uchun):**

1. Telefon videodan faqat **audioni** ajratadi (~1 MB, 50 barobar kichik)
2. Server faqat ASR qiladi → `.ass` yoki JSON qaytaradi
3. Telefon o'z **apparat kodeki** bilan renderlaydi (iOS AVFoundation,
   Android MediaCodec) — bu bir necha sekund va senga 0 so'm turadi

Shunda server xarajating ~150 so'mdan ~75 so'mga tushadi, trafik
50 barobar kamayadi, kutish vaqti esa sezilarli qisqaradi.

Bu skript serverli variantni ko'rsatadi — Telegram bot uchun aynan shu
kerak. Mobil ilovaga o'tganda yuqoridagi sxemaga o'tasan.
