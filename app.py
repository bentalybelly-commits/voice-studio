import os
import edge_tts
from fastapi import FastAPI, Response, Form
from fastapi.responses import HTMLResponse

app = FastAPI()

# Organized Studio-Quality Voices
VOICE_GROUPS = {
    "🇨🇦 CANADIAN ACCENTS": {
        "🇨🇦 Clara (Canadian Natural Female)": "en-CA-ClaraNeural",
        "🇨🇦 Liam (Canadian Studio Male)": "en-CA-LiamNeural",
    },
    "⚡ ENERGETIC & UPBEAT": {
        "⚡ Sara (Energetic & Cheerful Female)": "en-US-SaraNeural",
        "⚡ Ana (Youthful & Energetic Female)": "en-US-AnaNeural",
        "⚡ Jason (Upbeat & Friendly Male)": "en-US-JasonNeural",
        "⚡ Aria (Expressive News & Promo Female)": "en-US-AriaNeural",
    },
    "🧘 CALM & RELAXING": {
        "🧘 Ava (Soft & Meditation Female)": "en-US-AvaNeural",
        "📖 Emma (Gentle Storyteller Female)": "en-US-EmmaNeural",
        "🎧 Brian (Calm & Soothing Male)": "en-US-BrianNeural",
        "🌙 Steffan (Deep & Relaxing Male)": "en-US-SteffanNeural",
    },
    "🎙️ DEEP & DOCUMENTARY": {
        "🎙️ Christopher (Deep Narrative Male)": "en-US-ChristopherNeural",
        "🎙️ Andrew (Warm & Authoritative Male)": "en-US-AndrewNeural",
        "🎙️ Guy (Casual Professional Male)": "en-US-GuyNeural",
        "☕ Jenny (Warm & Natural Female)": "en-US-JennyNeural",
    },
    "🇬🇧 BRITISH ACCENTS": {
        "🇬🇧 Sonia (Soft British Female)": "en-GB-SoniaNeural",
        "🇬🇧 Ryan (Professional British Male)": "en-GB-RyanNeural",
        "🇬🇧 Thomas (Warm British Male)": "en-GB-ThomasNeural",
        "🇬🇧 Maisie (Upbeat British Youth)": "en-GB-MaisieNeural",
    },
    "🇦🇺 AUSTRALIAN ACCENTS": {
        "🇦🇺 Natasha (Australian Female)": "en-AU-NatashaNeural",
        "🇦🇺 William (Australian Male)": "en-AU-WilliamNeural",
    },
    "🇮🇳 INDIAN ENGLISH ACCENTS": {
        "🇮🇳 Neerja (Expressive Indian Female)": "en-IN-NeerjaNeural",
        "🇮🇳 Prabhat (Natural Indian Male)": "en-IN-PrabhatNeural",
    }
}

# Generate Dropdown HTML with categories
def build_voice_options():
    options_html = ""
    for group_name, voices in VOICE_GROUPS.items():
        options_html += f'<optgroup label="{group_name}">'
        for name, code in voices.items():
            options_html += f'<option value="{code}">{name}</option>'
        options_html += '</optgroup>'
    return options_html

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ultimate AI Voice Studio</title>
    <style>
        :root { --bg: #0f172a; --card: #1e293b; --accent: #6366f1; --text: #f8fafc; --muted: #94a3b8; }
        body { background: var(--bg); color: var(--text); font-family: -apple-system, sans-serif; padding: 16px; max-width: 520px; margin: 0 auto; box-sizing: border-box; }
        .card { background: var(--card); padding: 20px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.4); margin-bottom: 16px; }
        h2 { margin-top: 0; text-align: center; color: #a5b4fc; font-size: 1.4rem; }
        label { display: block; font-size: 0.8rem; font-weight: 700; margin-top: 14px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; }
        textarea, select, button { width: 100%; margin-top: 6px; padding: 12px; border-radius: 8px; border: 1px solid #334155; background: #0f172a; color: white; box-sizing: border-box; font-size: 0.95rem; }
        textarea:focus, select:focus { border-color: var(--accent); outline: none; }
        .row { display: flex; gap: 10px; }
        .row > div { flex: 1; }
        button { background: var(--accent); font-weight: bold; border: none; margin-top: 18px; padding: 14px; border-radius: 10px; cursor: pointer; font-size: 1rem; }
        button:disabled { opacity: 0.5; }
        #loader { display: none; text-align: center; margin-top: 14px; color: #a5b4fc; font-size: 0.9rem; }
        #player { width: 100%; margin-top: 18px; display: none; }
        
        /* Expression Guide Box */
        .guide { background: #0f172a; padding: 14px; border-radius: 10px; border-left: 4px solid var(--accent); font-size: 0.82rem; color: #cbd5e1; line-height: 1.5; }
        .guide h4 { margin: 0 0 6px 0; color: #a5b4fc; font-size: 0.9rem; }
        .guide code { background: #334155; padding: 2px 5px; border-radius: 4px; color: #f1f5f9; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🎙️ AI Voice Studio Pro</h2>
        
        <label>YOUR SCRIPT</label>
        <textarea id="text" rows="5" placeholder="Type or paste text... Use !, ?, and ... for emotion!"></textarea>
        
        <label>VOICE MODEL & ACCENT</label>
        <select id="voice">
            {% OPTIONS %}
        </select>

        <div class="row">
            <div>
                <label>SPEED</label>
                <select id="rate">
                    <option value="-20%">Slow (-20%)</option>
                    <option value="+0%" selected>Normal (1.0x)</option>
                    <option value="+10%">Upbeat (+10%)</option>
                    <option value="+25%">Fast (+25%)</option>
                </select>
            </div>
            <div>
                <label>PITCH / TONE</label>
                <select id="pitch">
                    <option value="-10Hz">Deeper (-10Hz)</option>
                    <option value="+0Hz" selected>Normal Pitch</option>
                    <option value="+10Hz">Higher (+10Hz)</option>
                </select>
            </div>
        </div>
        
        <button id="btn" onclick="generate()">Generate Human Voiceover</button>
        <div id="loader">⚡ Synthesizing natural audio...</div>
        <audio id="player" controls></audio>
    </div>

    <!-- Human Sounding Tricks Guide -->
    <div class="guide">
        <h4>✨ How to make AI sound 100% Human:</h4>
        • <b>Exclamation Points (<code>!</code>):</b> Adds excitement, energy, and loudness.<br>
        • <b>Question Marks (<code>?</code>):</b> Raises pitch naturally at sentence end.<br>
        • <b>Commas (<code>,</code>):</b> Adds brief, 