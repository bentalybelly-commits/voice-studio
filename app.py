import os
import re
import edge_tts
from fastapi import FastAPI, Form, Response
from fastapi.responses import HTMLResponse, FileResponse

app = FastAPI()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

VOICES = {
    "en-NG-EzinneNeural",
    "en-NG-AbeoNeural",
    "en-US-AndrewNeural",
    "en-US-AvaNeural",
    "en-GB-RyanNeural",
}
RATES = {"-25%", "-15%", "+0%", "+10%"}


def preprocess_for_tts(text: str) -> str:
    """Helps the voice say Nigerian food words correctly."""
    text = re.sub(r'\beba\b', 'Eh-bah', text, flags=re.IGNORECASE)
    text = re.sub(r'\begusi\b', 'Eh-goo-see', text, flags=re.IGNORECASE)
    text = re.sub(r'\bgarri\b', 'Gah-ree', text, flags=re.IGNORECASE)
    text = re.sub(r'\bmoi moi\b', 'Moy Moy', text, flags=re.IGNORECASE)
    return text


@app.get("/", response_class=HTMLResponse)
def home():
    with open(os.path.join(BASE_DIR, "index.html"), encoding="utf-8") as f:
        return f.read()


@app.get("/pfp.jpg")
def pfp():
    for name in ("pfp.jpg", "1000072279.jpg"):
        path = os.path.join(BASE_DIR, name)
        if os.path.exists(path):
            return FileResponse(path, media_type="image/jpeg")
    return Response(status_code=404)


@app.post("/generate")
async def generate(
    text: str = Form(...),
    voice: str = Form("en-NG-EzinneNeural"),
    rate: str = Form("-15%"),
):
    if voice not in VOICES:
        voice = "en-NG-EzinneNeural"
    if rate not in RATES:
        rate = "-15%"
    text = text.strip()[:3000]
    if not text:
        return Response(status_code=400)

    cleaned_text = preprocess_for_tts(text)
    communicate = edge_tts.Communicate(cleaned_text, voice, rate=rate, pitch="+0Hz")

    audio = bytearray()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio.extend(chunk["data"])
    return Response(content=bytes(audio), media_type="audio/mpeg")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)