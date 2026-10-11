import io
import asyncio

import edge_tts
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse

app = FastAPI(title="Mark AI Studio")

VOICES = {
    "Andrew": "en-US-AndrewMultilingualNeural",
    "Brian": "en-US-BrianMultilingualNeural",
    "Guy": "en-US-GuyNeural",
    "Jenny": "en-US-JennyNeural",
    "Aria": "en-US-AriaNeural",
    "Sonia": "en-GB-SoniaNeural",
}

PAGE = """
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
    padding: 20px;
    background: #101114;
    color: white;
    font-family: Arial, sans-serif;
}

main {
    max-width: 560px;
    margin: 35px auto;
}

h1 {
    text-align: center;
    font-size: 30px;
    margin-bottom: 8px;
}

h1 span {
    color: #927bff;
}

.subtitle {
    text-align: center;
    color: #aaa;
    margin-bottom: 30px;
}

.card {
    background: #1b1c22;
    padding: 20px;
    border-radius: 15px;
    border: 1px solid #30313a;
}

label {
    display: block;
    margin: 18px 0 9px;
    font-size: 14px;
    font-weight: bold;
}

textarea, select {
    width: 100%;
    padding: 14px;
    border: 1px solid #393a45;
    border-radius: 9px;
    background: #111216;
    color: white;
    font-size: 15px;
}

textarea {
    height: 210px;
    resize: vertical;
    line-height: 1.5;
}

button {
    width: 100%;
    margin-top: 22px;
    padding: 15px;
    border: none;
    border-radius: 9px;
    background: #927bff;
    color: white;
    font-size: 16px;
    font-weight: bold;
    cursor: pointer;
}

button:disabled {
    opacity: 0.6;
}

#status {
    margin-top: 16px;
    font-size: 14px;
    text-align: center;
    overflow-wrap: anywhere;
}

#result {
    margin-top: 20px;
    display: none;
}

audio {
    width: 100%;
    margin-top: 12px;
}

#download {
    display: block;
    margin-top: 14px;
    padding: 14px;
    border-radius: 9px;
    background: #292a34;
    color: white;
    text-align: center;
    text-decoration: none;
}

.small {
    margin-top: 12px;
    color: #999;
    font-size: 12px;
    text-align: center;
}
</style>
</head>

<body>
<main>
    <h1>Mark <span>AI Studio</span></h1>
    <p class="subtitle">Turn your script into a voiceover.</p>

    <div class="card">
        <label for="script">Your script</label>
        <textarea id="script"
        placeholder="Paste your narration here..."></textarea>

        <label for="voice">Choose a voice</label>
        <select id="voice">
            <option value="Andrew">Andrew — US Male</option>
            <option value="Brian">Brian — US Male</option>
            <option value="Guy">Guy — US Male</option>
            <option value="Jenny">Jenny — US Female</option>
            <option value="Aria">Aria — US Female</option>
            <option value="Sonia">Sonia — UK Female</option>
        </select>

        <button id="generate" onclick="generateVoice()">
            Generate Voice
        </button>

        <div id="status"></div>

        <div id="result">
            <label>Your voiceover</label>
            <audio id="player" controls></audio>
            <a id="download" download="mark-voiceover.mp3">
                Download MP3
            </a>
        </div>
    </div>

    <p class="small">Mark AI Studio · Simple voice generation</p>
</main>

<script>
const button = document.getElementById("generate");
const status = document.getElementById("status");
const result = document.getElementById("result");
const player = document.getElementById("player");
const download = document.getElementById("download");

let audioUrl = null;

async function generateVoice() {
    const script = document.getElementById("script").value.trim();
    const voice = document.getElementById("voice").value;

    if (!script) {
        status.textContent = "Please paste your script first.";
        return;
    }

    if (script.length > 15000) {
        status.textContent =
            "Your script is too long. Please use fewer than 15,000 characters.";
        return;
    }

    button.disabled = true;
    button.textContent = "Generating...";
    status.textContent = "Please wait while your voiceover is created.";
    result.style.display = "none";

    try {
        const form = new FormData();
        form.append("text", script);
        form.append("voice", voice);

        const response = await fetch("/generate", {
            method: "POST",
            body: form
        });

        if (!response.ok) {
            let message = "Could not generate the voiceover.";

            try {
                const data = await response.json();
                message = data.detail || message;
            } catch (e) {}

            throw new Error(message);
        }

        const blob = await response.blob();

        if (!blob.size) {
            throw new Error("The audio file was empty. Please try again.");
        }

        if (audioUrl) {
            URL.revokeObjectURL(audioUrl);
        }

        audioUrl = URL.createObjectURL(blob);
        player.src = audioUrl;
        download.href = audioUrl;

        result.style.display = "block";
        status.textContent = "Your voiceover is ready!";

    } catch (error) {
        status.textContent = error.message || "Something went wrong.";
    } finally {
        button.disabled = false;
        button.textContent = "Generate Voice";
    }
}
</script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def home():
    return PAGE


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/generate")
async def generate(
    text: str = Form(...),
    voice: str = Form("Andrew"),
):
    text = text.strip()

    if not text:
        raise HTTPException(
            status_code=400,
            detail="Please enter your script."
        )

    if len(text) > 15000:
        raise HTTPException(
            status_code=400,
            detail="Your script exceeds the 15,000-character limit."
        )

    if voice not in VOICES:
        raise HTTPException(
            status_code=400,
            detail="Please select a valid voice."
        )

    try:
        audio_data = io.BytesIO()

        # Split long scripts into manageable chunks.
        chunks = []
        remaining = text

        while remaining:
            if len(remaining) <= 2500:
                chunks.append(remaining)
                break

            split_at = remaining.rfind(" ", 0, 2500)

            if split_at <= 0:
                split_at = 2500

            chunks.append(remaining[:split_at])
            remaining = remaining[split_at:].strip()

        for chunk in chunks:
            communicator = edge_tts.Communicate(
                chunk,
                VOICES[voice]
            )

            async for item in communicator.stream():
                if item["type"] == "audio":
                    audio_data.write(item["data"])

        if audio_data.tell() == 0:
            raise HTTPException(
                status_code=502,
                detail="No audio was generated. Please try again."
            )

        audio_data.seek(0)

        return StreamingResponse(
            audio_data,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition":
                    'attachment; filename="mark-voiceover.mp3"'
            }
        )

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=502,
            detail=(
                "Voice generation failed. Check your internet connection "
                "or try again later."
            )
        )