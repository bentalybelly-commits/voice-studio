import os
import re
import html
import edge_tts
from fastapi import FastAPI, Response, Form
from fastapi.responses import HTMLResponse

app = FastAPI()

# ACOUSTIC TUNING: Mark Clone (Deeper, Energetic, Conversational)
VOICE_NAME = "en-US-AndrewNeural"
SPEED_RATE = "+8%"    # Brisk, energetic pacing
PITCH_DEPTH = "-4Hz"  # Deeper mid-low tone
VOLUME_BOOST = "+10%" # Stronger, confident projection

def sanitize_text(raw_text: str) -> str:
    """Strips code snippets, HTML tags, and markdown so AI never reads code aloud."""
    # 1. Remove markdown code blocks (```code```)
    text = re.sub(r'```[\s\S]*?```', '', raw_text)
    # 2. Remove inline code (`code`)
    text = re.sub(r'`[^`]*`', '', text)
    # 3. Remove HTML tags (<tag>)
    text = re.sub(r'<[^>]+>', '', text)
    # 4. Remove URLs
    text = re.sub(r'http[s]?://\S+', '', text)
    # 5. Unescape HTML entities (&amp; -> &)
    text = html.unescape(text)
    # 6. Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
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
        <textarea id="text" rows="6" placeholder="Paste your text here... Code snippets and tags will be cleaned out automatically so Mark reads smoothly."></textarea>
        
        <button id="btn" onclick="generate()">Generate Voiceover</button>
        <div id="status">⚡ Synthesizing Mark's voice...</div>
        
        <audio id="player" controls></audio>
    </div>

    <script>
        async function generate() {
            const text = document.getElementById('text').value.trim();
            if(!text) return alert("Please paste or type a script first!");
            
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
                if(!res.ok) throw new Error("Generation error");
                const blob = await res.blob();
                player.src = URL.createObjectURL(blob);
                player.style.display = 'block';
                player.play();
            } catch(e) {
                alert("Error generating voice. Please try again.");
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
    # Clean text to prevent code/tags from being read aloud
    clean_text = sanitize_text(text)
    
    if not clean_text:
        return Response(content=b"", status_code=400)
    
    # Generate speech natively using tuned parameters (NO manual XML wrapping)
    communicate = edge_tts.Communicate(
        text=clean_text, 
        voice=VOICE_NAME, 
        rate=SPEED_RATE, 
        pitch=PITCH_DEPTH,
        volume=VOLUME_BOOST
    )
    
    audio = bytearray()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio.extend(chunk["data"])
            
    return Response(content=bytes(audio), media_type="audio/mpeg")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)