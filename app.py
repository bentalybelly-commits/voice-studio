import os
import html
import edge_tts
from fastapi import FastAPI, Response, Form
from fastapi.responses import HTMLResponse

app = FastAPI()

# THE MARK CLONE CONFIGURATION
# BrianNeural is the 'Twin' of ElevenLabs Mark. 
# We apply a +5% rate to match Mark's brisk conversational pace.
MARK_VOICE = "en-US-BrianNeural"
MARK_RATE = "+5%"
MARK_PITCH = "-1Hz"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mark AI Studio</title>
    <style>
        :root { --bg: #0b0f1a; --card: #161b2c; --accent: #4f46e5; --text: #f1f5f9; }
        body { background: var(--bg); color: var(--text); font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .card { background: var(--card); width: 90%; max-width: 450px; padding: 30px; border-radius: 20px; box-shadow: 0 20px 50px rgba(0,0,0,0.5); border: 1px solid #2d3748; }
        h1 { font-size: 1.5rem; margin-bottom: 5px; color: #818cf8; text-align: center; }
        p { text-align: center; color: #94a3b8; font-size: 0.8rem; margin-bottom: 25px; }
        textarea { width: 100%; background: #0b0f1a; border: 1px solid #2d3748; color: white; padding: 15px; border-radius: 12px; font-size: 1rem; resize: none; box-sizing: border-box; outline: none; }
        textarea:focus { border-color: var(--accent); }
        button { width: 100%; background: var(--accent); color: white; border: none; padding: 15px; border-radius: 12px; font-size: 1rem; font-weight: bold; margin-top: 20px; cursor: pointer; transition: 0.3s; }
        button:hover { background: #4338ca; }
        button:disabled { background: #312e81; color: #94a3b8; cursor: not-allowed; }
        #player { width: 100%; margin-top: 25px; display: none; }
        .status { text-align: center; font-size: 0.8rem; margin-top: 15px; color: #818cf8; display: none; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🎙️ Mark AI Studio</h1>
        <p>Conversational • Warm • Natural Pacing</p>
        
        <textarea id="text" rows="6" placeholder="Paste your script here... Mark handles the conversational flow and breathing automatically."></textarea>
        
        <button id="btn" onclick="generate()">Generate Mark's Voice</button>
        <div class="status" id="status">Mark is thinking...</div>
        
        <audio id="player" controls></audio>
    </div>

    <script>
        async function generate() {
            const text = document.getElementById('text').value.trim();
            if(!text) return;
            
            const btn = document.getElementById('btn');
            const status = document.getElementById('status');
            const player = document.getElementById('player');
            
            btn.disabled = true;
            status.style.display = 'block';
            player.style.display = 'none';
            
            const body = new FormData();
            body.append('text', text);
            
            try {
                const res = await fetch('/generate', { method: 'POST', body });
                const blob = await res.blob();
                player.src = URL.createObjectURL(blob);
                player.style.display = 'block';
                player.play();
            } catch(e) {
                alert("Connection error");
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
async def generate(text: str = Form(...)):
    # Clean text for XML safety
    clean_text = html.escape(text)
    
    # This SSML structure mimics ElevenLabs' 'Conversational' logic
    # It forces the engine to prioritize flow over robotic precision.
    ssml = f"""
    <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
        <voice name="{MARK_VOICE}">
            <prosody rate="{MARK_RATE}" pitch="{MARK_PITCH}">
                {clean_text}
            </prosody>
        </voice>
    </speak>
    """
    
    communicate = edge_tts.Communicate(ssml, MARK_VOICE)
    audio = bytearray()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio.extend(chunk["data"])
            
    return Response(content=bytes(audio), media_type="audio/mpeg")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)