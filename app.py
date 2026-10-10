import os
import edge_tts
from fastapi import FastAPI, Response, Form
from fastapi.responses import HTMLResponse

app = FastAPI()

VOICES = {
    "US - Christopher (Narrative Male)": "en-US-ChristopherNeural",
    "US - Guy (Casual Male)": "en-US-GuyNeural",
    "US - Jenny (Natural Female)": "en-US-JennyNeural",
    "US - Aria (Expressive Female)": "en-US-AriaNeural",
    "UK - Ryan (British Male)": "en-GB-RyanNeural",
    "UK - Sonia (British Female)": "en-GB-SoniaNeural",
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Voice Studio</title>
    <style>
        body { background: #0f172a; color: #f8fafc; font-family: sans-serif; padding: 20px; max-width: 500px; margin: 0 auto; }
        .card { background: #1e293b; padding: 20px; border-radius: 12px; }
        textarea, select, button { width: 100%; margin-top: 10px; padding: 12px; border-radius: 8px; border: 1px solid #334155; background: #0f172a; color: white; box-sizing: border-box; }
        button { background: #6366f1; font-weight: bold; border: none; margin-top: 15px; cursor: pointer; }
        #loader { display: none; text-align: center; margin-top: 10px; color: #94a3b8; }
        #player { width: 100%; margin-top: 15px; display: none; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🎙️ AI Voice Studio</h2>
        <textarea id="text" rows="5" placeholder="Paste your script here..."></textarea>
        <select id="voice">
            {% OPTIONS %}
        </select>
        <button id="btn" onclick="generate()">Generate Voiceover</button>
        <div id="loader">Generating audio...</div>
        <audio id="player" controls></audio>
    </div>
    <script>
        async function generate() {
            const text = document.getElementById('text').value.trim();
            if(!text) return alert("Please enter text");
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
            } catch(e) { alert("Error generating audio"); }
            
            document.getElementById('btn').disabled = false;
            document.getElementById('loader').style.display = 'none';
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def ui():
    opts = "".join([f'<option value="{c}">{n}</option>' for n, c in VOICES.items()])
    return HTML_TEMPLATE.replace("{% OPTIONS %}", opts)

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