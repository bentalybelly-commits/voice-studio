import os
import edge_tts
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()

VOICES = {
    "🎙️ Mark - Natural Conversational": "en-US-AndrewMultilingualNeural",
    "🎙️ Mark (Warm Casual)": "en-US-BrianMultilingualNeural",
    "🎙️ Mark (Classic)": "en-US-AndrewNeural",
    "🎙️ Casual Guy": "en-US-GuyNeural",
    "👴 Deep Storyteller": "en-US-SteffanNeural",
    "☕ Jenny (Natural Warm Female)": "en-US-JennyNeural",
    "⚡ Sara (Energetic Female)": "en-US-SaraNeural",
    "🧘 Ava (Soft Female)": "en-US-AvaNeural",
    "🇨🇦 Liam (Canadian Male)": "en-CA-LiamNeural",
    "🇬🇧 Ryan (British Male)": "en-GB-RyanNeural",
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Voice Studio</title>
    <style>
        :root { --bg: #0f172a; --card: #1e293b; --accent: #6366f1; --text: #f8fafc; --muted: #94a3b8; }
        body { background: var(--bg); color: var(--text); font-family: -apple-system, system-ui, sans-serif; padding: 16px; max-width: 500px; margin: 0 auto; box-sizing: border-box; }
        .card { background: var(--card); padding: 22px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.4); }
        h2 { margin-top: 0; text-align: center; color: #a5b4fc; font-size: 1.4rem; }
        label { display: block; font-size: 0.75rem; font-weight: 700; margin-top: 14px; color: var(--muted); text-transform: uppercase; }
        textarea, select, button { width: 100%; margin-top: 6px; padding: 12px; border-radius: 8px; border: 1px solid #334155; background: #0f172a; color: white; box-sizing: border-box; font-size: 0.95rem; }
        .row { display: flex; gap: 10px; }
        .row > div { flex: 1; }
        button { background: var(--accent); font-weight: bold; border: none; margin-top: 18px; padding: 14px; border-radius: 10px; font-size: 1rem; }
        button:disabled { opacity: 0.5; }
        #loader { display: none; text-align: center; margin-top: 14px; color: #a5b4fc; }
        #player { width: 100%; margin-top: 18px; display: none; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🎙️ AI Voice Studio</h2>

        <label>Your script</label>
        <textarea id="text" rows="6" placeholder="Type script here... Use commas and ? ! for natural pauses."></textarea>

        <label>Voice</label>
        <select id="voice">__OPTIONS__</select>

        <div class="row">
            <div>
                <label>Speed</label>
                <select id="rate">
                    <option value="-10%">Slower (-10%)</option>
                    <option value="+0%">Natural</option>
                    <option value="+8%" selected>Brisk (+8%)</option>
                    <option value="+15%">Fast (+15%)</option>
                </select>
            </div>
            <div>
                <label>Pitch</label>
                <select id="pitch">
                    <option value="-6Hz">Deeper (-6Hz)</option>
                    <option value="-3Hz" selected>Warmer (-3Hz)</option>
                    <option value="+0Hz">Natural</option>
                    <option value="+3Hz">Higher (+3Hz)</option>
                </select>
            </div>
        </div>

        <button id="btn" onclick="generate()">Generate Voiceover</button>
        <div id="loader">⚡ Generating voice...</div>
        <audio id="player" controls></audio>
    </div>

    <script>
        async function generate() {
            const text = document.getElementById('text').value.trim();
            if (!text) return alert("Please enter your script!");

            const btn = document.getElementById('btn');
            const loader = document.getElementById('loader');
            const player = document.getElementById('player');
            btn.disabled = true;
            loader.style.display = 'block';
            player.style.display = 'none';

            try {
                const res = await fetch('/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        text: text,
                        voice: document.getElementById('voice').value,
                        rate: document.getElementById('rate').value,
                        pitch: document.getElementById('pitch').value
                    })
                });
                if (!res.ok) throw new Error(await res.text());
                const blob = await res.blob();
                player.src = URL.createObjectURL(blob);
                player.style.display = 'block';
                player.play();
            } catch (e) {
                alert("Error: " + e.message);
            }
            btn.disabled = false;
            loader.style.display = 'none';
        }
    </script>
</body>
</html>
"""


class SpeechRequest(BaseModel):
    text: str
    voice: str = "en-US-AndrewMultilingualNeural"
    rate: str = "+8%"
    pitch: str = "-3Hz"


@app.get("/", response_class=HTMLResponse)
async def ui():
    opts = "".join(
        f'<option value="{code}">{name}</option>' for name, code in VOICES.items()
    )
    return HTML_TEMPLATE.replace("__OPTIONS__", opts)


@app.post("/generate")
async def generate(req: SpeechRequest):
    voice = req.voice if req.voice in VOICES.values() else "en-US-AndrewNeural"
    try:
        communicate = edge_tts.Communicate(
            req.text, voice, rate=req.rate, pitch=req.pitch
        )
        audio = bytearray()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio.extend(chunk["data"])
    except Exception as e:
        return Response(content=f"Voice error: {e}", status_code=502)

    if not audio:
        return Response(content="No audio returned.", status_code=502)
    return Response(content=bytes(audio), media_type="audio/mpeg")


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)