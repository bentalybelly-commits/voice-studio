import os
import edge_tts
from fastapi import FastAPI, Response, Form
from fastapi.responses import HTMLResponse

app = FastAPI()

# Studio Voices
VOICE_GROUPS = {
    "🇨🇦 CANADIAN": {
        "🇨🇦 Clara (Female)": "en-CA-ClaraNeural",
        "🇨🇦 Liam (Male)": "en-CA-LiamNeural",
    },
    "⚡ ENERGETIC": {
        "⚡ Sara (Upbeat Female)": "en-US-SaraNeural",
        "⚡ Jason (Friendly Male)": "en-US-JasonNeural",
    },
    "🧘 CALM": {
        "🧘 Ava (Soft Female)": "en-US-AvaNeural",
        "🎧 Brian (Meditation Male)": "en-US-BrianNeural",
    },
    "🎙️ DEEP/NARRATIVE": {
        "🎙️ Christopher (Deep Male)": "en-US-ChristopherNeural",
        "☕ Jenny (Warm Female)": "en-US-JennyNeural",
    }
}

def build_voice_options():
    options_html = ""
    for group, voices in VOICE_GROUPS.items():
        options_html += f'<optgroup label="{group}">'
        for name, code in voices.items():
            options_html += f'<option value="{code}">{name}</option>'
        options_html += '</optgroup>'
    return options_html

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Voice Studio</title>
    <style>
        body { background: #0f172a; color: #f8fafc; font-family: sans-serif; padding: 15px; max-width: 500px; margin: 0 auto; }
        .card { background: #1e293b; padding: 20px; border-radius: 12px; }
        textarea, select, button { width: 100%; margin-top: 10px; padding: 12px; border-radius: 8px; border: 1px solid #334155; background: #0f172a; color: white; box-sizing: border-box; }
        button { background: #6366f1; font-weight: bold; border: none; margin-top: 15px; cursor: pointer; }
        #loader { display: none; text-align: center; margin-top: 10px; color: #a5b4fc; }
        audio { width: 100%; margin-top: 15px; display: none; }
        .guide { margin-top: 20px; font-size: 0.8rem; color: #94a3b8; line-height: 1.4; border-top: 1px solid #334155; padding-top: 10px; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🎙️ AI Voice Studio</h2>
        <textarea id="text" rows="4" placeholder="Use ! and ? for more emotion..."></textarea>
        <label style="font-size:0.7rem; color:#94a3b8;">VOICE</label>
        <select id="voice">{% OPTIONS %}</select>
        <button id="btn" onclick="generate()">Generate Audio</button>
        <div id="loader">Generating...</div>
        <audio id="player" controls></audio>
        <div class="guide">
            <b>Tips:</b> Use <b>!</b> for energy, <b>?</b> for pitch, and <b>...</b> for pauses.
        </div>
    </div>
    <script>
        async function generate() {
            const text = document.getElementById('text').value.trim();
            if(!text) return alert("Enter text");
            document.getElementById('btn').disabled = true;
            document.getElementById('loader').style.display = 'block';
            document.getElementById('player').style.display = 'none';
            const body = new FormData();
            body.append('text', text);
            body.append('voice', document.getElementById('voice').value);
            try {
                const res = await fetch('/generate', { method: 'POST', body });
                const blob = await res.blob();
                const player = document.getElementById('player');
                player.src = URL.createObjectURL(blob);
                player.style.display = 'block';
                player.play();
            } catch(e) { alert("Error"); }
            document.getElementById('btn').disabled = false;
            document.getElementById('loader').style.display = 'none';
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def ui():
    return HTML_TEMPLATE.replace("{% OPTIONS %}", build_voice_options())

@app.post("/generate")
async def generate(text: str = Form(...), voice: str = Form(...)):
    comm = edge_tts.Communicate(text, voice)
    audio = bytearray()
    async for chunk in comm.stream():
        if chunk["type"] == "audio":
            audio.extend(chunk["data"])
    return Response(content=bytes(audio), media_type="audio/mpeg")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 