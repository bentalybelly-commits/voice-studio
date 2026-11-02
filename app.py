import os
import re
import edge_tts
from fastapi import FastAPI, Form, Response
from fastapi.responses import HTMLResponse

app = FastAPI()

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
    text = text.replace("H₂O", "water")
    text = re.sub(r'\beba\b', 'Eh-bah', text, flags=re.IGNORECASE)
    text = re.sub(r'\begusi\b', 'Eh-goo-see', text, flags=re.IGNORECASE)
    text = re.sub(r'\bgarri\b', 'Gah-ree', text, flags=re.IGNORECASE)
    text = re.sub(r'\bomorogun\b', 'Oh-moh-roh-goon', text, flags=re.IGNORECASE)
    text = re.sub(r'\bewedu\b', 'Eh-weh-doo', text, flags=re.IGNORECASE)
    text = re.sub(r'\bgbegiri\b', 'Beh-geh-ree', text, flags=re.IGNORECASE)
    return text


HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The Story of Eba</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800&family=Noto+Sans+Math&display=swap');

* { box-sizing: border-box; font-family: 'Outfit', sans-serif; }

body {
    margin: 0; padding: 18px; min-height: 100vh; color: #FFE066;
    background: linear-gradient(135deg, #0F0C29, #302B63, #4A00E0 70%, #8E2DE2);
    background-attachment: fixed;
    display: flex; justify-content: center; align-items: flex-start;
}

.gold {
    background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #FCF6BA, #AA771C);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}

.container {
    background: rgba(15, 12, 41, 0.72);
    backdrop-filter: blur(14px);
    border: 1px solid rgba(255, 215, 0, 0.35);
    border-radius: 22px; padding: 22px;
    max-width: 680px; width: 100%;
    box-shadow: 0 25px 60px rgba(0,0,0,0.6), 0 0 40px rgba(142,45,226,0.35);
}

h1 { text-align: center; font-size: 2.2em; margin: 0 0 4px; text-transform: uppercase; letter-spacing: 2px; }
p.subtitle { text-align: center; color: #FFE066; margin: 0 0 18px; }

.tabs { display: flex; gap: 10px; overflow-x: auto; padding: 4px 2px 12px; }
.tab {
    flex: 0 0 auto; padding: 12px 18px; border-radius: 25px; font-weight: 800; font-size: 1em;
    cursor: pointer; color: #FFD700; background: rgba(255,215,0,0.08);
    border: 2px solid #AA771C; transition: 0.3s;
}
.tab.active {
    color: #0F0C29; border-color: #FFD700;
    background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728);
    box-shadow: 0 0 18px rgba(255,215,0,0.5);
}

.gallery { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 14px; }
.gallery img {
    width: 100%; aspect-ratio: 1 / 1; object-fit: cover; border-radius: 16px; cursor: pointer;
    border: 2px solid #FFD700; box-shadow: 0 6px 16px rgba(0,0,0,0.5);
}
img.wide {
    width: 100%; height: 170px; object-fit: cover; border-radius: 16px; cursor: pointer;
    border: 2px solid #FFD700; box-shadow: 0 6px 16px rgba(0,0,0,0.5); margin-top: 14px; display: block;
}

.card {
    background: rgba(48, 43, 99, 0.55);
    border-left: 4px solid #FFD700; border-radius: 14px;
    padding: 16px 18px; margin-top: 14px;
}
.card h3 { margin: 0 0 10px; font-size: 1.25em; padding-bottom: 8px; border-bottom: 1px solid rgba(255,215,0,0.25); }
.card p { margin: 0 0 10px; line-height: 1.6; color: #FFE066; }
.card ol, .card ul { padding-left: 20px; line-height: 1.6; color: #FFE066; }
.card li { margin-bottom: 9px; }
.hl { color: #FFD700; font-weight: 800; }
.big-number { font-size: 1.4em; }

.chips { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.chip { background: rgba(255,215,0,0.08); border: 1px solid #AA771C; border-radius: 12px; padding: 10px; text-align: center; font-size: 0.95em; }
.chip b { display: block; color: #FFD700; margin-bottom: 3px; }

.tl { border-left: 3px solid #FFD700; margin-left: 8px; padding-left: 18px; }
.tl-item { margin-bottom: 16px; position: relative; line-height: 1.5; }
.tl-item::before { content: ""; position: absolute; left: -26px; top: 5px; width: 12px; height: 12px; border-radius: 50%; background: #FFD700; box-shadow: 0 0 8px #FFD700; }
.tl-item b { color: #FFD700; display: block; }

.scroll-x { overflow-x: auto; }
table.chart { width: 100%; border-collapse: collapse; color: #FFE066; text-align: center; }
table.chart th, table.chart td { padding: 9px 6px; border-bottom: 1px solid rgba(255,215,0,0.25); font-size: 0.95em; }
table.chart th { color: #FFD700; }

details { border-bottom: 1px solid rgba(255,215,0,0.25); padding: 10px 0; }
summary { cursor: pointer; color: #FFD700; font-weight: 800; line-height: 1.4; }
details p { margin: 8px 0 0; }

input[type=number], textarea, select {
    width: 100%; padding: 14px; font-size: 1.1em; color: #FFE066;
    background: rgba(255,255,255,0.07); border: 2px solid #AA771C;
    border-radius: 12px; outline: none;
}
input[type=number] { text-align: center; }
textarea { min-height: 150px; resize: vertical; }
select option { color: black; }
input:focus, textarea:focus, select:focus { border-color: #FFD700; box-shadow: 0 0 14px rgba(255,215,0,0.4); }
label { display: block; margin: 12px 0 6px; color: #FFD700; font-weight: 600; }

.toggle { display: flex; gap: 10px; margin-top: 12px; }
.toggle button {
    flex: 1; padding: 12px 8px; border-radius: 12px; font-weight: 800; font-size: 0.95em;
    color: #FFD700; background: rgba(255,215,0,0.08); border: 2px solid #AA771C; cursor: pointer;
}
.toggle button.on {
    color: #0F0C29; border-color: #FFD700;
    background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728);
}

button.big {
    width: 100%; padding: 14px; font-size: 1.1em; font-weight: 800; margin-top: 14px;
    border: none; border-radius: 12px; cursor: pointer; color: #0F0C29;
    background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728);
    box-shadow: 0 6px 18px rgba(255,215,0,0.3);
}
button.big:disabled { opacity: 0.6; cursor: wait; }

audio { width: 100%; margin-top: 14px; display: none; }
a.download {
    display: none; text-align: center; margin-top: 12px; padding: 12px; border-radius: 12px;
    background: #8E2DE2; color: #FFD700; text-decoration: none; font-weight: 800;
}

.dev-card { margin-top: 26px; padding: 18px 10px; text-align: center; border: 2px dashed #AA771C; border-radius: 20px; background: rgba(142,45,226,0.18); }
.frame { width: 270px; max-width: 80%; height: auto; display: block; margin: 0 auto; filter: drop-shadow(0 0 14px rgba(255,215,0,0.6)); }
.dev-label { margin: 4px 0 2px; font-size: 0.85em; letter-spacing: 3px; text-transform: uppercase; color: #FFE066; }
.dev-name { margin: 0; font-size: 2.2em; font-family: 'Noto Sans Math', 'Cambria Math', 'Segoe UI Symbol', serif; }
.tap-hint { font-size: 0.85em; margin: 6px 0 0; color: #FFE066; }
a.discord {
    display: inline-flex; align-items: center; gap: 10px; margin-top: 14px; padding: 8px 18px 8px 8px;
    border-radius: 40px; text-decoration: none; font-weight: 800; color: #FFD700;
    border: 2px solid #FFD700; background: rgba(15,12,41,0.7);
}
a.discord img { width: 38px; height: 38px; border-radius: 50%; object-fit: cover; }

#lightbox { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.92); align-items: center; justify-content: center; z-index: 99; }
#lightbox img { max-width: 95%; max-height: 88%; border-radius: 12px; border: 3px solid #FFD700; }
</style>
</head>
<body>
<div class="container">
    <h1 class="gold">The Story of Eba</h1>
    <p class="subtitle">Read the history, learn the science, then make it</p>

    <div class="tabs">
        <button class="tab active" id="tab-history" onclick="showTab('history')">📜 History</button>
        <button class="tab" id="tab-eba" onclick="showTab('eba')">🥣 How to Make Eba</button>
        <button class="tab" id="tab-soups" onclick="showTab('soups')">🍲 Soups & Garri</button>
        <button class="tab" id="tab-voice" onclick="showTab('voice')">🎙️ Voice</button>
    </div>

    <!-- HISTORY -->
    <div id="sec-history">
        <div class="gallery" id="gallery"></div>
        <button class="big" id="histBtn" onclick="listenHistory()">🔊 Listen to the history</button>
        <audio id="histPlayer" controls></audio>

        <div class="card">
            <h3 class="gold">⚡ Quick Facts</h3>
            <div class="chips">
                <div class="chip"><b>Main ingredient</b>Garri</div>
                <div class="chip"><b>Made from</b>Cassava root</div>
                <div class="chip"><b>Cassava came from</b>Brazil</div>
                <div class="chip"><b>Fermenting time</b>2 to 3 days</div>
                <div class="chip"><b>Steam time</b>60 seconds</div>
                <div class="chip"><b>Water ratio</b>1 : 1.35</div>
            </div>
        </div>

        <div id="historyCards"></div>

        <div class="card">
            <h3 class="gold">🕰️ Timeline</h3>
            <div class="tl" id="timeline"></div>
        </div>

        <div class="card">
            <h3 class="gold">📚 Words to Know</h3>
            <div id="glossary"></div>
        </div>
    </div>

    <!-- HOW TO MAKE EBA -->
    <div id="sec-eba" style="display:none;">
        <img class="wide" id="banner-eba" alt="Eba picture" onclick="zoom(this.src)" onerror="this.style.display='none'">

        <div class="card">
            <h3 class="gold">👥 How many people are eating?</h3>
            <input type="number" id="people" min="1" max="200" value="4" oninput="calc()">
            <div class="toggle">
                <button id="normalBtn" class="on" onclick="setMode(1)">🍽️ Normal appetite</button>
                <button id="bigBtn" onclick="setMode(8)">🍖 Big eaters (8x)</button>
            </div>
        </div>

        <div class="card">
            <h3 class="gold">📊 What you need</h3>
            <p id="servLine"></p>
            <ul>
                <li><span class="hl big-number" id="outGarri"></span> cups of garri</li>
                <li><span class="hl big-number" id="outWater"></span> cups of hot water <span id="outMl"></span></li>
            </ul>
            <p id="potTip"></p>
        </div>

        <div class="card">
            <h3 class="gold">📖 Step-by-step</h3>
            <button class="big" id="recipeBtn" onclick="listenRecipe()">🔊 Listen to the steps</button>
            <audio id="recipePlayer" controls></audio>
            <ol>
                <li>Pour the water into a clean pot and boil it for <b>5 to 7 minutes</b> until it is bubbling hot.</li>
                <li>Turn off the heat, or take the pot off the fire.</li>
                <li>Pour the garri slowly into the hot water and spread it evenly. Do not stir yet.</li>
                <li>Cover the pot for <b>1 minute</b> so the garri can soak and soften.</li>
                <li>Use a wooden spatula (omorogun) to turn and press the eba against the sides of the pot until it is smooth and lump free.</li>
                <li>Mold it into balls and serve hot with your favourite soup.</li>
            </ol>
        </div>

        <div class="card">
            <h3 class="gold">📋 Quick Serving Chart</h3>
            <div class="scroll-x" id="chart"></div>
        </div>

        <div class="card">
            <h3 class="gold">✅ Tips for Perfect Eba</h3>
            <ul id="tips"></ul>
        </div>

        <div class="card">
            <h3 class="gold">❓ Problems and Answers</h3>
            <div id="faq"></div>
        </div>
    </div>

    <!-- SOUPS AND GARRI -->
    <div id="sec-soups" style="display:none;">
        <img class="wide" id="banner-soups" alt="Soup picture" onclick="zoom(this.src)" onerror="this.style.display='none'">

        <div class="card">
            <h3 class="gold">🌾 White Garri or Yellow Garri?</h3>
            <p><span class="hl">White garri</span> is made only from cassava starch, with nothing added to it.</p>
            <p><span class="hl">Yellow garri</span> has red palm oil added, which gives it a yellow colour and extra flavour.</p>
        </div>

        <div class="card">
            <h3 class="gold">🍲 What to Eat Eba With</h3>
            <div id="soupList"></div>
        </div>

        <div class="card">
            <h3 class="gold">🤲 How to Eat Eba</h3>
            <ol>
                <li>Take a small piece of eba and roll it into a ball with your fingers.</li>
                <li>Press your thumb into the middle to make a small hole.</li>
                <li>Use the hole to scoop up the soup, with some meat or fish.</li>
                <li>Swallow it. Do not chew it.</li>
            </ol>
            <p>The eba works like an edible spoon.</p>
        </div>
    </div>

    <!-- VOICE -->
    <div id="sec-voice" style="display:none;">
        <div class="card">
            <h3 class="gold">🎙️ Voice Generator</h3>
            <label for="vText">Your text</label>
            <textarea id="vText">Welcome to the story of eba. Type anything here and I will read it out loud for you.</textarea>
            <label for="vVoice">Voice</label>
            <select id="vVoice">
                <option value="en-NG-EzinneNeural">Ezinne (Nigerian woman)</option>
                <option value="en-NG-AbeoNeural">Abeo (Nigerian man)</option>
                <option value="en-US-AndrewNeural">Andrew (American man)</option>
                <option value="en-US-AvaNeural">Ava (American woman)</option>
                <option value="en-GB-RyanNeural">Ryan (British man)</option>
            </select>
            <label for="vSpeed">Speed</label>
            <select id="vSpeed">
                <option value="-25%">Very slow</option>
                <option value="-15%" selected>Slow and clear</option>
                <option value="+0%">Normal</option>
                <option value="+10%">A bit fast</option>
            </select>
            <button class="big" id="vBtn" onclick="makeVoice()">🔊 Generate voice</button>
            <audio id="vPlayer" controls></audio>
            <a class="download" id="vDownload" download="voice.mp3">⬇️ Download audio</a>
        </div>
    </div>

    <!-- DEVELOPER CARD -->
    <div class="dev-card">
        <a href="https://discord.com/users/1565467595526643834" target="_blank" rel="noopener">
            <svg class="frame" viewBox="0 0 300 285" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <linearGradient id="goldG" x1="0" y1="0" x2="1" y2="1">
                        <stop offset="0%" stop-color="#FCF6BA"/>
                        <stop offset="45%" stop-color="#FFD700"/>
                        <stop offset="100%" stop-color="#AA771C"/>
                    </linearGradient>
                    <clipPath id="circ"><circle cx="150" cy="150" r="76"/></clipPath>
                </defs>
                <g id="leaves"></g>
                <circle cx="150" cy="150" r="80" fill="#0F0C29" stroke="url(#goldG)" stroke-width="6"/>
                <image href="https://i.postimg.cc/ydWjTWpD/Roblox-figure-wearing-gold-crown-4a68337d-2K.jpg"
                       x="74" y="74" width="152" height="152" clip-path="url(#circ)" preserveAspectRatio="xMidYMid slice"/>
                <path d="M112 62 L106 34 L126 48 L138 26 L150 44 L162 26 L174 48 L194 34 L188 62 Z" fill="url(#goldG)" stroke="#AA771C" stroke-width="1.5"/>
                <circle cx="106" cy="32" r="3.5" fill="#FCF6BA"/>
                <circle cx="138" cy="24" r="3.5" fill="#FCF6BA"/>
                <circle cx="162" cy="24" r="3.5" fill="#FCF6BA"/>
                <circle cx="194" cy="32" r="3.5" fill="#FCF6BA"/>
                <text x="118" y="270" text-anchor="middle" font-size="17" fill="url(#goldG)">★</text>
                <text x="150" y="274" text-anchor="middle" font-size="24" fill="url(#goldG)">★</text>
                <text x="182" y="270" text-anchor="middle" font-size="17" fill="url(#goldG)">★</text>
            </svg>
        </a>
        <p class="tap-hint">Tap the picture to open my Discord</p>
        <p class="dev-label">Developer</p>
        <p class="dev-name gold">𝕴 𝖉𝖔𝖓'𝖙 𝖐𝖓𝖔𝖜</p>
        <a class="discord" href="https://discord.com/users/1565467595526643834" target="_blank" rel="noopener">
            <img src="https://i.postimg.cc/qvwD4P9c/IMG-1c54020a-8bc0-4272-a7e6-d9e821f653f5.png" alt="Discord" onerror="this.style.display='none'">
            Find me on Discord
        </a>
    </div>
</div>

<div id="lightbox" onclick="this.style.display='none'"><img id="lbImg" alt="Big picture"></div>

<script>
const PICS = [
    "https://i.postimg.cc/mDSdDQFn/IMG-40e1048b-d00d-4094-b865-826da1e046f8.jpg",
    "https://i.postimg.cc/W1j7H5YQ/IMG-c0faf892-8342-4e24-9e2b-8d2fb7bed618.jpg",
    "https://i.postimg.cc/d17RypD3/IMG-866b9346-738d-4667-917b-61e830f9c373.jpg"
];

const HISTORY = [
    {
        title: "🌍 Where Eba Comes From",
        lines: [
            "Eba is one of the most prominent swallow staples across West Africa today.",
            "Its core ingredient is garri, a dry processed flour derived from cassava roots.",
            "The story of eba begins with cassava (Manihot esculenta), native to Brazil.",
            "South American tribes learned to detoxify cassava by grating and squeezing it.",
            "Portuguese traders brought cassava to West Africa during the 16th century.",
            "Cassava thrived in poor soils, surviving drought and insect invasions easily."
        ]
    },
    {
        title: "☠️ Making the Root Safe",
        lines: [
            "However, raw cassava contains cyanogenic glycosides that produce lethal hydrogen cyanide (HCN).",
            "West Africans had to master biochemical processing to render the root safe.",
            "Repatriated Afro-Brazilian slaves brought farinha de mandioca roasting techniques in the 19th century.",
            "Cassava was peeled, washed, and shredded into a soggy starch pulp.",
            "Microbial fermentation occurred in woven bags over two to three days.",
            "Lactic acid bacteria drove down the pH, giving garri its characteristic sour tang.",
            "Fermentation also activated endogenous enzymes that broke down the toxic cyanide.",
            "The mash was pressed dry and sieved into uniform starch granules."
        ]
    },
    {
        title: "🔥 Roasting Into Garri",
        lines: [
            "Roasting garri over open fires thermally gelatinized the cassava amylose and amylopectin.",
            "This thermal transformation created shelf-stable, dehydrated garri granules."
        ]
    },
    {
        title: "🧪 The Science of Eba",
        lines: [
            "To make eba, garri undergoes a rapid thermal rehydration reaction with boiling H₂O.",
            "Preparing eba is basically organic chemistry disguised as home cooking.",
            "Boiling H₂O breaks hydrogen bonds between starch polymer chains in the garri.",
            "Garri acts like a moisture-seeking polymer sponge, aggressively absorbing liquid.",
            "You must respect the stoichiometry—too much H₂O yields a sad, liquid slurry.",
            "Too little H₂O creates concrete-hard projectile ammo capable of breaking tiles.",
            "Pouring garri into hot water triggers exothermic hydration and rapid gelatinization.",
            "Dynamic mechanical agitation with a wooden spatula (Omorogun) prevents catastrophic lump formation.",
            "Aggressive stirring cross-links starch chains into a uniform, viscoelastic gel polymer.",
            "Allowing the pot to steam for 60 seconds lets heat complete the gel-network alignment.",
            "The result is a smooth, structural dough matrix engineered to hold heavy soup loads."
        ]
    },
    {
        title: "🍲 Garri Types and Soups",
        lines: [
            "Yellow garri includes red palm oil, adding lipophilic beta-carotene and extra flavor.",
            "White gar