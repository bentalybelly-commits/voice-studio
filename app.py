import os
import re
import html
import httpx
from fastapi import FastAPI, Response, Form
from fastapi.responses import HTMLResponse

app = FastAPI()

ELEVEN_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "")
MODEL_ID = os.environ.get("ELEVENLABS_MODEL_ID", "eleven_v4")


def sanitize_text(raw_text: str) -> str:
    """Strips code, HTML tags, and URLs so they are never read aloud."""
    text = re.sub(r"```[\s\S]*?```", "", raw_text)
    text = re.sub(r"`[^`]*`", "", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"https?://\S+", "", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


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
        textarea { width: 100%; background: #0b0f1a; border: 1px solid #334155; color: white; padding: 14px; border-radius: 12px; font-size: 0.95rem; resize: none; box-sizing: border-box; outline: none; line-height: 1.5; }
        textarea:focus { border-color: var(--accent); }
        input[type=range] { width: 100%; margin-top: 4px; }
        .row { margin-top: 16px; }
        button { width: 100%; background: var(--accent); color: white; border: none; padding: 14px; border-radius: 12px; font-size: 1rem; font-weight: bold; margin-top: 18px; cursor: pointer; transition: background 0.2s; }
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
        <textarea id="text" rows="6" placeholder="Paste your text here... Code snippets and tags are cleaned out automatically."></textarea>

        <div class="row">
            <label>EXPRESSIVENESS (lower = more emotion): <span id="stabVal">0.40</span></label>
            <input type="range" id="stability" min="0" max="1" step="0.05" value="0.4"
                   oninput="document.getElementById('stabVal').textContent = Number(this.value).toFixed(2)">
        </div>

        <button id="btn" onclick="generate()">Generate Voiceover</button>
        <div id="status">⚡ Synthesizing voice...</div>

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
            body.append('stability', document.getElementById('stability').value);

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
    return HTML_TEMPLATE


@app.post("/generate")
async def generate(text: str = Form(...), stability: float = Form(0.4)):
    if not ELEVEN_KEY or not VOICE_ID:
        return Response(
            content="Server missing ELEVENLABS_API_KEY or ELEVENLABS_VOICE_ID.",
            status_code=500,
        )

    clean_text = sanitize_text(text)
    if not clean_text:
        return Response(content="Script is empty after cleaning.", status_code=400)

    stability = max(0.0, min(1.0, stability))

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
                params={"output_format": "mp3_44100_128"},
                headers={"xi-api-key": ELEVEN_KEY},
                json={
                    "text": clean_text,
                    "model_id": MODEL_ID,
                    "voice_settings": {
                        "stability": stability,
                        "similarity_boost": 0.8,
                        "style": 0.3,
                        "use_speaker_boost": True,
                    },
                },
            )
    except httpx.HTTPError as e:
        return Response(content=f"Could not reach ElevenLabs: {e}", status_code=502)

    if r.status_code != 200:
        return Response(content=f"ElevenLabs error: {r.text}", status_code=r.status_code)

    return Response(content=r.content, media_type="audio/mpeg")


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)