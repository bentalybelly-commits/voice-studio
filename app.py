import os
import edge_tts
from fastapi import FastAPI, Response, Form
from fastapi.responses import HTMLResponse

app = FastAPI()

# Primary Voice: Mark (ElevenLabs Match) + Other High-Quality Options
VOICES = {
    "🎙️ Mark - Natural Conversational (ElevenLabs)": "en-US-AndrewNeural",
    "🎙️ Mark (Alternative - Casual Guy)": "en-US-GuyNeural",
    "👴 Spuds Oxley (Deep Storyteller)": "en-US-SteffanNeural",
    "☕ Jenny (Natural Warm Female)": "en-US-JennyNeural",
    "⚡ Sara (Energetic & Upbeat Female)": "en-US-SaraNeural",
    "🧘 Ava (Soft Meditation Female)": "en-US-AvaNeural",
    "🇨🇦 Liam (Canadian Studio Male)": "en-CA-LiamNeural",
    "🇬🇧 Ryan (British Studio Male)": "en-GB-RyanNeural"
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Voice Studio - Mark ElevenLabs</title>
    <style>
        :root { --bg: #0f172a; --card: #1e293b; --accent: #6366f1; --text: #f8fafc; --muted: #94a3b8; }
        body { background: var(--bg); color: var(--text); font-family: -apple-system, system-ui, sans-serif; padding: 16px; max-width: 500px; margin: 0 auto; box-sizing: border-box; }
        .card { background: var(--card); padding: 22px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.4); }
        h2 { margin-top: 0; text-align: center; color: #a5b4fc; font-size: 1.4rem; }
        label { display: block; font-size: 0.75rem; font-weight: 700; margin-top: 14px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; }
        textarea, select, button { width: 100%; margin-top: 6px; padding: 12px; border-radius: 8px; border: 1px solid #334155; background: #0f172a; color: white; box-sizing: border-box; font-size: 0.95rem; }
        textarea:focus, select:focus { border-color: var(--accent); outline: none; }
        .row { display: flex; gap: 10px; }
        .row > div { flex: 1; }
        button { background: var(--accent); font-weight: bold; border: none; margin-top: 18px; padding: 14px; border-radius: 10px; cursor: pointer; font-size: 1rem; }
        button:disabled { opacity: 0.5; }
        #loader { display: none; text-align: center; margin-top: 14px; color: #a5b4fc; font-size: 0.9rem; }
        #player { width: 100%; margin-top: 18px; display: none; }
        .guide { margin-top: 18px; background: #0f172a; padding: 12px; border-radius: 10px; border-left: 3px solid var(--accent); font-size: 0.8rem; color: #cbd5e1; line-height: 1.4; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🎙️ AI Voice Studio</h2>
        
        <label>YOUR SCRIPT</label>
        <textarea id="text" rows="5" placeholder="Type script here... Use !, ?, and commas for natural conversational pauses!"></textarea>
        
        <label>SELECT VOICE</label>
        <select id="voice">
            {% OPTIONS %}
        </select>

        <div class="row">
            <div>
                <label>SPEED</label>
                <select id="rate">
                    <option value="-10%">Slightly Slower (-10%)</option>
                    <option value="+0%" selected>Natural (1.0x)</option>
                    <option value="+10%">Faster (+10%)</option>
                </select>
            </div>
            <div>
                <label>PITCH / TONE</label>
                <select id="pitch">
                    <option value="-3Hz">Warmer (-3Hz)</option>
                    <option value="+0Hz" selected>Natural Pitch</option>
                    <option value="+3Hz">Higher (+3Hz)</option>
                </select>
            </div>
        </div>
        
        <button id="btn" onclick="generate()">Generate Voiceover</button>
        <div id="loader">⚡ Generating Mark's voice...</div>
        <audio id="player" controls></audio>

        <div class="guide">
            <b>💡 How to make "Mark" sound 100% real:</b><br>
            • Add commas (<code>,</code>) for conversational breath pauses.<br>
            • Use question marks (<code>?</code>) to raise inflection naturally.<br>
            • Set pitch to <b>Warmer (-3Hz)</b> for a deeper conversational tone.
        </div>
    </div>

    <script>
        async function generate() {
            const text = document.getElementById('text').value.trim();
            if(!text) return alert("Please enter your script!");
            
            document.getElementById('btn').disabled = true;
            document.getElementById('loader').style.display = 'block';
            document.getElementById('player').style.display = 'none';
            
            const body = new FormData();
            body.append('text', text);
            body.append('voice', document.getElementById('voice').value);
            body.append('rate', document.getElementById('rate').value);
            body.append('pitch', document.getElementById('pitch').value);
            
            try {
                const res = await fetch('/generate', { method: 'POST', body });
                if(!res.ok) throw new Error("Failed");
                const blob = await res.blob();
                const player = document.getElementById('player');
                player.src = URL.createObjectURL(blob);
                player.style.display = 'block';
                player.play();
            } catch(e) { alert("Error generating speech."); }
            
            document.getElementById('btn').disabled = false;
            document.getElementById('loader').style.display = 'none';
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def ui():
    opts = "".join([f'<option value="{code}">{name}</option>' for name, code in VOICES.items()])
    return HTML_TEMPLATE.replace("{% OPTIONS %}", opts)

@app.post("/generate")
async def generate(
    text: str = Form(...), 
    voice: str = Form(...), 
    rate: str = Form("+0%"), 
    pitch: str = Form("+0Hz")
):
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    audio = bytearray()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio.extend(chunk["data"])
    return Response(content=bytes(audio), media_type="audio/mpeg")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)