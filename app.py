import os
import re
import html
import asyncio
import logging

from typing import Optional

import edge_tts

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, Response
from fastapi.concurrency import run_in_threadpool

app = FastAPI(title="Mark AI Studio")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mark_ai")

DEFAULT_VOICE = "en-US-AndrewMultilingualNeural"

VOICES = {
    "en-US-AndrewMultilingualNeural": "Andrew Multilingual",
    "en-US-BrianMultilingualNeural": "Brian Multilingual",
    "en-US-AndrewNeural": "Andrew",
    "en-US-BrianNeural": "Brian",
    "en-US-ChristopherNeural": "Christopher",
    "en-US-GuyNeural": "Guy",
    "en-US-EricNeural": "Eric",
    "en-US-RogerNeural": "Roger",
    "en-US-SteffanNeural": "Steffan",
}

# These presets adjust supported speech parameters.
# They do NOT guarantee genuine emotional acting.
EMOTION_PRESETS = {
    "natural": {
        "rate": 0,
        "pitch": 0,
        "volume": 0,
    },
    "suspense": {
        "rate": -8,
        "pitch": -2,
        "volume": 0,
    },
    "excited": {
        "rate": 8,
        "pitch": 2,
        "volume": 5,
    },
    "dramatic": {
        "rate": -4,
        "pitch": -3,
        "volume": 3,
    },
    "serious": {
        "rate": -3,
        "pitch": -4,
        "volume": 0,
    },
}

MAX_TEXT_LENGTH = 12000
MAX_CHUNK_LENGTH = 2000


def sanitize_text(raw_text: str) -> str:
    """Clean pasted text while preserving useful punctuation."""

    text = html.unescape(raw_text or "")

    # Remove fenced code blocks and inline code.
    text = re.sub(r"```[\s\S]*?```", " ", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)

    # Remove URLs.
    text = re.sub(r"https?://\S+", " ", text)

    # Remove HTML tags.
    text = re.sub(r"<[^>]*>", " ", text)

    # Normalize whitespace without flattening all paragraphs immediately.
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    lines = []

    for line in text.split("\n"):
        line = re.sub(r"[ \t]+", " ", line).strip()

        if not line:
            continue

        lines.append(line)

    return "\n".join(lines).strip()


def detect_emotion(text: str) -> str:
    """
    Basic rule-based classification.
    This is not a trained emotion-detection model.
    """

    text_lower = text.lower()

    suspense_patterns = [
        "nobody knew",
        "little did they know",
        "then he removed",
        "then she removed",
        "what happened next",
        "until suddenly",
        "but then",
    ]

    excited_patterns = [
        "unbelievable",
        "incredible",
        "shocked everyone",
        "you won't believe",
        "went crazy",
    ]

    dramatic_patterns = [
        "the truth",
        "the real one",
        "finally revealed",
        "the moment",
    ]

    if any(p in text_lower for p in suspense_patterns):
        return "suspense"

    if any(p in text_lower for p in excited_patterns):
        return "excited"

    if any(p in text_lower for p in dramatic_patterns):
        return "dramatic"

    return "natural"


def split_text(text: str, max_length: int = MAX_CHUNK_LENGTH):
    """Split text at sentence boundaries where possible."""

    sentences = re.split(r"(?<=[.!?])\s+", text.strip())

    chunks = []
    current = ""

    for sentence in sentences:
        if not sentence:
            continue

        while len(sentence) > max_length:
            if current:
                chunks.append(current)
                current = ""

            chunks.append(sentence[:max_length].strip())
            sentence = sentence[max_length:].strip()

        candidate = f"{current} {sentence}".strip()

        if len(candidate) <= max_length:
            current = candidate
        else:
            if current:
                chunks.append(current)

            current = sentence

    if current:
        chunks.append(current)

    return chunks


async def generate_audio(
    text: str,
    voice: str,
    rate: int,
    pitch: int,
    volume: int,
) -> bytes:
    """Generate audio with Edge TTS and combine returned audio chunks."""

    output = bytearray()

    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=f"{rate:+d}%",
        pitch=f"{pitch:+d}Hz",
        volume=f"{volume:+d}%",
    )

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            output.extend(chunk["data"])

    return bytes(output)


@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse(
        """
        <h1>Mark AI Studio API</h1>
        <p>The backend is running.</p>
        <p>Open <a href="/docs">/docs</a> to test the API.</p>
        """
    )


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/presets")
async def presets():
    return {
        "presets": EMOTION_PRESETS,
        "note": (
            "Presets adjust speed, pitch and volume. "
            "They do not guarantee emotional expression."
        ),
    }


@app.post("/generate")
async def generate(
    text: str = Form(...),
    voice: str = Form(DEFAULT_VOICE),
    emotion: str = Form("natural"),
    rate: Optional[int] = Form(None),
    pitch: Optional[int] = Form(None),
    volume: Optional[int] = Form(None),
):
    clean_text = sanitize_text(text)

    if not clean_text:
        return Response(
            content="Please enter a script containing readable text.",
            status_code=400,
        )

    if len(clean_text) > MAX_TEXT_LENGTH:
        return Response(
            content=(
                f"Your script is too long. "
                f"Maximum length: {MAX_TEXT_LENGTH} characters."
            ),
            status_code=413,
        )

    if voice not in VOICES:
        return Response(
            content="Unsupported voice. Please select a listed voice.",
            status_code=400,
        )

    if emotion not in EMOTION_PRESETS:
        return Response(
            content="Unsupported emotion preset.",
            status_code=400,
        )

    preset = EMOTION_PRESETS[emotion]

    # Explicit user settings override the preset.
    rate = preset["rate"] if rate is None else rate
    pitch = preset["pitch"] if pitch is None else pitch
    volume = preset["volume"] if volume is None else volume

    # Validate ranges.
    rate = max(-50, min(50, rate))
    pitch = max(-50, min(50, pitch))
    volume = max(-50, min(50, volume))

    chunks = split_text(clean_text)

    if not chunks:
        return Response(
            content="No usable text was found.",
            status_code=400,
        )

    try:
        audio_parts = []

        for chunk in chunks:
            audio = await asyncio.wait_for(
                generate_audio(
                    text=chunk,
                    voice=voice,
                    rate=rate,
                    pitch=pitch,
                    volume=volume,
                ),
                timeout=90,
            )

            if not audio:
                raise RuntimeError("The speech service returned empty audio.")

            audio_parts.append(audio)

        # MP3 streams are commonly concatenable, but this is not a
        # full audio-editing pipeline. Validate playback for your target
        # browser before using the result in production.
        combined_audio = b"".join(audio_parts)

        return Response(
            content=combined_audio,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": 'inline; filename="voiceover.mp3"'
            },
        )

    except asyncio.TimeoutError:
        logger.warning("Speech generation timed out.")

        return Response(
            content="Speech generation timed out. Try a shorter script.",
            status_code=504,
        )

    except Exception:
        logger.exception("Speech generation failed.")

        return Response(
            content=(
                "Voice generation failed. Check your internet connection, "
                "voice availability, and speech-service access, then retry."
            ),
            status_code=502,
        )


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "8000"))

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
    )