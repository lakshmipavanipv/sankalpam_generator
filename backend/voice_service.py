"""
voice_service.py
────────────────
Recites the sankalpam in a male priest-style voice (slow, low pitch) using
Microsoft neural voices via edge-tts. Audio is cached on disk by content hash,
so each unique sankalpam is synthesised only once.
"""
import asyncio, hashlib, os, re, tempfile, logging

logger = logging.getLogger(__name__)

# Which voice reads which tab. The Sanskrit text is read by the Hindi voice,
# whose Devanagari pronunciation suits Sanskrit best.
VOICES = {
    "sanskrit": "hi-IN-MadhurNeural",
    "english":  "hi-IN-MadhurNeural",   # recites the Devanagari original
    "hindi":    "hi-IN-MadhurNeural",
    "marathi":  "mr-IN-ManoharNeural",
    "telugu":   "te-IN-MohanNeural",
    "tamil":    "ta-IN-ValluvarNeural",
    "kannada":  "kn-IN-GaganNeural",
}
RATE, PITCH = "-18%", "-8Hz"

CACHE_DIR = os.environ.get("SANKALPAM_AUDIO_CACHE",
                           os.path.join(tempfile.gettempdir(), "sankalpam_audio"))
os.makedirs(CACHE_DIR, exist_ok=True)


def _prepare(text: str) -> str:
    """Strip the meaning and bracketed notes; turn dandas into pauses."""
    text = text.split("━")[0]
    text = re.sub(r"\([^)]*\)", "", text)
    text = text.replace("॥", ".").replace("।", ",")
    return re.sub(r"\s+", " ", text).strip()


async def _synthesise(text: str, voice: str, path: str):
    import edge_tts
    tmp = path + ".part"
    await edge_tts.Communicate(text, voice, rate=RATE, pitch=PITCH).save(tmp)
    os.replace(tmp, path)


def recite(text: str, language: str) -> str:
    """Return the path of an mp3 reciting `text`; raises on failure."""
    voice = VOICES.get(language, VOICES["sanskrit"])
    spoken = _prepare(text)
    key = hashlib.sha256(f"{voice}|{RATE}|{PITCH}|{spoken}".encode("utf-8")).hexdigest()[:32]
    path = os.path.join(CACHE_DIR, f"{key}.mp3")
    if not os.path.exists(path):
        for attempt in range(3):  # the speech service occasionally drops connections
            try:
                asyncio.run(_synthesise(spoken, voice, path))
                break
            except Exception as e:
                logger.warning(f"Voice attempt {attempt + 1} failed: {e}")
                if attempt == 2:
                    raise
    return path
