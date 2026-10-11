import asyncio
import io
import re
import edge_tts

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.concurrency import run_in_threadpool

app = FastAPI(title="Mark AI Studio")

VOICES = {
    "Andrew": "en-US-AndrewMultilingualNeural",
    "Brian": "en-US-BrianMultilingualNeural",
    "Guy": "en-US-GuyNeural",
    "Jenny": "en-US-JennyNeural",
    "Aria": "en-US-AriaNeural",
    "Sonia": "en-GB-SoniaNeural",
}

EMOTIONS = {
    "Natural": {"rate": "+0%", "pitch": "+0Hz"},
    "Excited": {"rate": "+10%", "pitch": "+3Hz"},
    "Dramatic": {"rate": "-8%", "pitch": "-2Hz"},
    "Suspenseful": {"rate": "-15%", "pitch": "-2Hz"},
    "Calm": {"rate": "-8%", "pitch": "-1Hz"},
}

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mark AI Studio</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #101114;
    color: #ffffff;
}

.container {
    max-width: 700px;
    margin: auto;
    padding: 24px 16px 40px;
}

header {
    text-align: center;
    margin-bottom: 28px;
}

.logo {
    font-size: 28px;
    font-weight: bold;
    letter-spacing: -1px;
}

.logo span {
    color: #8b7cff;
}

.subtitle {
    color: #a4a5b0;
    font-size: 14px;
    margin-top: 8px;
}

.card {
    background: #191a20;
    border: 1px solid #2b2c35;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 16px;
}

label {
    display: block;
    font-size: 14px;
    font-weight: bold;
    margin-bottom: 10px;
}

textarea, select {
    width: 100%;
    background: #101114;
    color: white;
    border: 1px solid #363742;
    border-radius: 10px;
    padding: 13px;
    font-size: 15px;
    outline: none;
}

textarea {
    min-height: 190px;
    resize: vertical;
    line-height: 1.6;
}

textarea:focus, select:focus {
    border-color: #8b7cff;
}

.counter {
    color: #a4a5b0;
    text-align: right;
    font-size: 12px;
    margin-top: 8px;
}

.field {
    margin-bottom: 20px;
}

button {
    width: 100%;
    padding: 15px;
    border: none;
    border-radius: 10px;
    font-size: 16px;
    font-weight: bold;
    cursor: pointer;
}

.generate {
    background: #8b7cff;
    color: white;
}

.generate:disabled {
    opacity: 0.6;
    cursor: wait;
}

.status {
    margin-top: 14px;
    font-size: 14px;
    text-align: center;
    color: #c5c5d0;
    overflow-wrap: anywhere;
}

audio {
    width: 100%;
    margin: 15px 0;
}

.download {
    display: block;
    text-decoration: none;
    text-align: center;
    background: #292a34;
    color: white;
    padding: 14px;
    border-radius: 10px;
    font-weight: bold;
}

.hidden {
    display: none;
}

.footer {
    text-align: center;
    color: #777986;
    font-size: 12px;
    margin-top: 24px;
}
</style>
</head>

<body>
<div class="container">

<header>
    <div class="logo">Mark <span>AI Studio</span></div>
    <div class="subtitle">Turn your script into a voiceover.</div>
</header>

<div class="card">
    <div class="field">
        <label for="script">Your script</label>
        <textarea id="script"
        placeholder="Paste your narration here..."></textarea>
        <div class="counter"><span id="count">0</span> characters</div>
    </div>

    <div class="field">
        <label for="voice">Choose a voice</label>
        <select id="voice">
            <option value="Andrew">Andrew — US Male</option>
            <option value="Brian">Brian — US Male</option>
            <option value="Guy">Guy — US Male</option>
            <option value="Jenny">Jenny — US Female</option>
            <option value="Aria">Aria — US Female</option>
            <option value="Sonia">Sonia — UK Female</option>
        </select>
    </div>

    <div class="field">
        <label for="emotion">Voice style</label>
        <select id="emotion">
            <option>Natural</option>
            <option>Excited</option>
            <option>Dramatic</option>
            <option>Suspenseful</option>
            <option>Calm</option>
        </select>
    </div>

    <button class="generate" id="generate" onclick="generateVoice()">
        Generate Voice
    </button>

    <div class="status" id="status"></div>
</div>

<div class="card hidden" id="result">
    <label>Your voiceover is ready</label>
    <audio id="audio" controls></audio>
    <a class="download" id="download" download="mark-ai-voiceover.mp3">
        Download MP3
    </a>
</div>

<div class="footer">
    Mark AI Studio · Simple AI voiceovers
</div>

</div>

<script>
const scriptBox = document.getElementById("script");
const count = document.getElementById("count");
const button = document.getElementById("generate");
const statusBox = document.getElementById("status");
const result = document.getElementById("result");
const audio = document.getElementById("audio");
const download = document.getElementById("download");

let currentAudioUrl = null;

scriptBox.addEventListener("input", () => {
    count.textContent = scriptBox.value.length;
});

async function generateVoice() {
    const script = scriptBox.value.trim();

    if (!script) {
        statusBox.textContent = "Please enter your script first.";
        scriptBox.focus();
        return;
    }

    button.disabled = true;
    button.textContent = "Generating...";
    statusBox.textContent = "Creating your voiceover. Please wait.";
    result.classList.add("hidden");

    if (currentAudioUrl) {
        URL.revokeObjectURL(currentAudioUrl);
        currentAudioUrl = null;
    }

    try {
        const form = new FormData();
        form.append("text", script);
        form.append("voice", document.getElementById("voice").value);
        form.append("emotion", document.getElementById("emotion").value);

        const response = await fetch("/generate", {
            method: "POST",
            body: form
        });

        if (!response.ok) {
            let message = "Voice generation failed.";

            try {
                const data = await response.json();
                message = data.detail || message;
            } catch (_) {}

            throw new Error(message);
        }

        const blob = await response.blob();

        if (!blob.size) {
            throw new Error("The server returned an empty audio file.");
        }

        currentAudioUrl = URL.createObjectURL(blob);
        audio.src = currentAudioUrl;
        download.href = currentAudioUrl;

        result.classList.remove("hidden");
        statusBox.textContent = "Voiceover generated successfully!";

        result.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

    } catch (error) {
        statusBox.textContent = error.message || "Something went wrong.";
    } finally {
        button.disabled = false;
        button.textContent = "Generate Voice";
    }
}
</script>

</body>
</html>
"""


def clean_text(text: str) -> str:
    text = re.sub(r"<[^>]*>", "", text)
    text = re.sub(r"https?://\S+", "", text)
    text = text.replace("\x00", "")
    return text.strip()


async def create_audio(text: str, voice: str, emotion: str) -> bytes:
    settings = EMOTIONS[emotion]
    audio_data = io.BytesIO()

    # Generate in chunks to avoid sending one extremely long request.
    chunks = []
    remaining = text

    while remaining:
        if len(remaining) <= 2500:
            chunks.append(remaining)
            break

        split_at = remaining.rfind(" ", 0, 2500)

        if split_at < 1:
            split_at = 2500

        chunks.append(remaining[:split_at])
        remaining = remaining[split_at:].strip()

    for chunk in chunks:
        communicate = edge_tts.Communicate(
            text=chunk,
            voice=VOICES[voice],
            rate=settings["rate"],
            pitch=settings["pitch"],
        )

        async for item in communicate.stream():
            if item["type"] == "audio":
                audio_data.write(item["data"])

    return audio_data.getvalue()


@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/generate")
async def generate(
    text: str = Form(...),
    voice: str = Form("Andrew"),
    emotion: str = Form("Natural"),
):
    text = clean_text(text)

    if not text:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Enter some text first.")

    if len(text) > 20000:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=400,
            detail="Your script is too long. Please use 20,000 characters or fewer."
        )

    if voice not in VOICES:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Please select a valid voice.")

    if emotion not in EMOTIONS:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Please select a valid voice style.")

    try:
        audio_bytes = await asyncio.wait_for(
            create_audio(text, voice, emotion),
            timeout=240
        )

        if not audio_bytes:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=502,
                detail="No audio was returned. Please try again."
            )

        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition":
                    'attachment; filename="mark-ai-voiceover.mp3"'
            },
        )

    except asyncio.TimeoutError:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=504,
            detail="Generation took too long. Try a shorter script."
        )
    except HTTPException:
        raise
    except Exception:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=502,
            detail="Voice generation failed. Check your internet connection and try again."
        )