import os
import re
import html
import edge_tts
from fastapi import FastAPI, Response, Form
from fastapi.responses import HTMLResponse

app = FastAPI()

DEFAULT_VOICE = "en-US-AndrewMultilingualNeural"

VOICES = {
    "en-US-AndrewMultilingualNeural": "Andrew Multilingual (most natural)",
    "en-US-BrianMultilingualNeural": "Brian Multilingual (warm, casual)",
    "en-US-AndrewNeural": "Andrew",
    "en-US-BrianNeural": "Brian",
    "en-US-ChristopherNeural": "Christopher (deep)",
    "en-US-GuyNeural": "Guy",
    "en-US-EricNeural": "Eric",
    "en-US-RogerNeural": "Roger",
    "en-US-SteffanNeural": "Steffan",
}


def sanitize_text(raw_text: str) -> str:
    text = re.sub(r"```[\s\S]*?```", "", raw_text)
    text = re.sub(r"`[^`]*`", "", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"https?://\S+", "", text)
    text = html.unescape(text)
    lines = []
    for line in text.splitlines():
        line = re.sub(r"[ \t]+", " ", line).strip()
        if not line:
            continue
        if line[-1] not in ".!?:;,":
            line += "."
        lines.append(line)
    return " ".join(lines).strip()


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mark AI - Conversational Studio</title>
    <style>
        :root { --bg: #0b0f1a; --card: #161b2c; --accent: #6366f1; --text: #f1f5f9; --muted: #94a3b8; }
        body { background: var(--bg); color: var(--text); font-family: -apple-system, system-ui, sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 16px; box-sizing: border-box; }
        .card { background: var(--card); width: 100%; max-width: 480px; padding: 24px; border-radius: 20px; box-shadow: 0 20px 50px rgba(0,0,0,0.5); border: 1px solid #2d3748; }
        h1 { font-size: 1.4rem; margin-top: 0; margin-bottom: 4px; color: #a5b4fc; text-align: center; }
        p.sub { text-align: center; color: var(--muted); font-size: 0.82rem; margin-top: 0; margin-bottom: 20px; }
        label { display: block; font-size: 0.75rem; font-weight: 700; margin-bottom: 6px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; }
        textarea, select { width: 100%; background: #0b0f1a; border: 1px solid #334155; color: white; padding: 14px; border-radius: 12px; font-size: 0.95rem; box-sizing: border-box; outline: none; }
        textarea { resize: none; line-height: 1.5; }
        textarea:focus, select:focus { border-color: var(--accent); }
        input[type=range] { width: 100%; margin-top: 4px; }
        .row { margin-top: 16px; }
        button { width: 100%; background: var(--accent); color: white; border: none; padding: 14px; border-radius: 12px; font-size: 1rem; font-weight: bold; margin-top: 18px; cursor: pointer; }
        button:hover { background: #4f46e5; }
        button:disabled { opacity: 0.5; cursor: not-allowed; }
        #status { text-align: center; font-size: 0.85rem; margin-top: 14px; color: #a5b4fc; display: none; }
        #player { width: 100%; margin-top: 20px; display: none; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🎙️ Mark AI Studio</h1>
        <p class="sub">Deep • Energetic • Natural Conversational</p>

        <label>YOUR SCRIPT</label>
        <textarea id="text" rows="6" placeholder="Paste your text here... Each new line becomes a natural pause."></textarea>

        <div class="row">
            <label>VOICE</label>
            <select id="voice">__VOICE_OPTIONS__</select>
        </div>

        <div class="row">
            <label>SPEED: <span id="rateVal">+8</span>%</label>
            <input type="range" id="rate" min="-20" max="30" step="1" value="8"
                   oninput="document.getElementById('rateVal').textContent = this.value">
        </div>

        <div class="row">
            <label>PITCH (lower = deeper): <span id="pitchVal">-4</span> Hz</label>
            <input type="range" id="pitch" min="-20" max="10" step="1" value="-4"
                   oninput="document.getElementById('pitchVal').textContent = this.value">
        </div>

        <div class="row">
            <label>VOLUME: <span id="volVal">+10</span>%</label>
            <input type="range" id="volume" min="0" max="30" step="1" value="10"
                   oninput="document.getElementById('volVal').textContent = this.value">
        </div>

        <button id="btn" onclick="generate()">Generate Voiceover</button>
        <div id="status">⚡ Creating voice...</div>
        <audio id="player" controls></audio>
    </div>

    <script>
        async function generate() {
            const text = document.getElementById('text').value.trim();
            if (!text) return alert("Please paste or type a script first!");

            const btn = document.getElementById('btn');
            const status = document.getElementById('status');
            const player = document.getElementById('player');

            btn.disabled = true;
            status.style.display = 'block';
            player.style.display = 'none';

            const body = new FormData();
            body.append('text', text);
            body.append('voice', document.getElementById('voice').value);
            body.append('rate', document.getElementById('rate').value);
            body.append('pitch', document.getElementById('pitch').value);
            body.append('volume', document.getElementById('volume').value);

            try {
                const res = await fetch('/generate', { method: 'POST', body });
                if (!res.ok) {
                    const msg = await res.text();
                    throw new Error(msg || "Generation error");
                }
                const blob = await res.blob();
                player.src = URL.createObjectURL(blob);
                player.style.display = 'block';
                player.play();
            } catch (e) {
                alert("Error: " + e.message);
            } finally {
                btn.disabled = false;
                status.style.display = 'none';
            }
        }
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def ui():
    options = "".join(
        f'<option value="{vid}"{" selected" if vid == DEFAULT_VOICE else ""}>{name}</option>'
        for vid, name in VOICES.items()
    )
    return HTML_TEMPLATE.replace("__VOICE_OPTIONS__", options)


@app.post("/generate")
async def generate(
    text: str = Form(...),
    voice: str = Form(DEFAULT_VOICE),
    rate: int = Form(8),
    pitch: int = Form(-4),
    volume: int = Form(10),
):
    clean_text = sanitize_text(text)
    if not clean_text:
        return Response(content="Script is empty after cleaning.", status_code=400)

    if voice not in VOICES:
        voice = DEFAULT_VOICE
    rate = max(-50, min(50, rate))
    pitch = max(-50, min(50, pitch))
    volume = max(-50, min(50, volume))

    try:
        communicate = edge_tts.Communicate(
            text=clean_text,
            voice=voice,
            rate=f"{rate:+d}%",
            pitch=f"{pitch:+d}Hz",
            volume=f"{volume:+d}%",
        )
        audio = bytearray()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio.extend(chunk["data"])
    except Exception as e:
        return Response(content=f"Voice error: {e}", status_code=502)

    if not audio:
        return Response(content="No audio was returned. Please try again.", status_code=502)

    return Response(content=bytes(audio), media_type="audio/mpeg")


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)