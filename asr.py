"""
Ovozni matnga aylantirish. Uchta variant — narx va sifat bo'yicha tanlaysan.

  openai   — eng oson, 1 daqiqa ≈ 72 so'm. Test uchun shu.
  eleven   — o'zbekchada odatda aniqroq, ≈ 80 so'm/daqiqa.
  local    — faster-whisper, o'z serveringda. Hajm oshganda eng arzoni.

Uchalasi ham bir xil format qaytaradi:
  [{"word": "salom", "start": 0.0, "end": 0.42}, ...]
"""

import os
import json
import subprocess
import tempfile


def extract_audio(video_path: str) -> str:
    """Videodan 16kHz mono wav ajratadi (ASR uchun optimal, fayl kichik)."""
    out = tempfile.mktemp(suffix=".wav")
    subprocess.run(
        ["ffmpeg", "-y", "-i", video_path,
         "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", out],
        check=True, capture_output=True,
    )
    return out


# ---------------------------------------------------------------- OpenAI
def transcribe_openai(audio_path, language="uz"):
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    with open(audio_path, "rb") as f:
        r = client.audio.transcriptions.create(
            file=f,
            model="whisper-1",
            language=language,
            response_format="verbose_json",
            timestamp_granularities=["word"],
        )
    return [
        {"word": w.word, "start": w.start, "end": w.end}
        for w in r.words
    ]


# ------------------------------------------------------------ ElevenLabs
def transcribe_elevenlabs(audio_path, language="uzb"):
    import requests

    with open(audio_path, "rb") as f:
        r = requests.post(
            "https://api.elevenlabs.io/v1/speech-to-text",
            headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"]},
            files={"file": f},
            data={"model_id": "scribe_v1", "language_code": language},
            timeout=300,
        )
    r.raise_for_status()
    data = r.json()

    out = []
    for w in data.get("words", []):
        # Scribe jimlik/tinish bo'laklarini ham qaytaradi — ularni tashlaymiz
        if w.get("type") != "word":
            continue
        out.append({"word": w["text"], "start": w["start"], "end": w["end"]})
    return out


# ------------------------------------------------------------ Mahalliy
def transcribe_local(audio_path, language="uz", model_size="large-v3"):
    from faster_whisper import WhisperModel

    model = WhisperModel(model_size, device="auto", compute_type="int8")
    segments, _ = model.transcribe(
        audio_path, language=language, word_timestamps=True, vad_filter=True
    )

    out = []
    for seg in segments:
        for w in seg.words:
            out.append({"word": w.word.strip(), "start": w.start, "end": w.end})
    return out


PROVIDERS = {
    "openai": transcribe_openai,
    "eleven": transcribe_elevenlabs,
    "local": transcribe_local,
}


def transcribe(video_path, provider="openai", language="uz"):
    audio = extract_audio(video_path)
    try:
        words = PROVIDERS[provider](audio, language=language)
    finally:
        if os.path.exists(audio):
            os.remove(audio)

    # Vaqt belgilari ba'zan ustma-ust tushadi — tozalaymiz
    for i in range(len(words) - 1):
        if words[i]["end"] > words[i + 1]["start"]:
            words[i]["end"] = words[i + 1]["start"]
    return [w for w in words if w["word"] and w["end"] > w["start"]]


def save_words(words, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=1)


def load_words(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)
