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
            "White garri relies purely on native cassava starch without added lipid molecules.",
            "Yoruba culinary traditions paired eba with Ewedu and Gbegiri to form Abula.",
            "Ewedu provides mucilaginous polysaccharide slip to lower friction during swallowing.",
            "Gbegiri offers emulsified protein density from slow-cooked, pureed cowpeas.",
            "Igbo traditions favor yellow garri (Utara Garri) paired with rich Egusi or Ogbono.",
            "Ogbono seeds release long-chain mucilage polymers that maximize soup elasticity and grip.",
            "Eba acts as a biodegradable, edible utensil engineered for optimal soup transport.",
            "Diners form a spherical mass, press a central indentation, and scoop up liquid.",
            "The indentation acts as a micro-reservoir for high-viscosity broth and protein chunks."
        ]
    },
    {
        title: "🏭 Eba Through Time",
        lines: [
            "Industrial mechanical graters and hydraulic presses scaled garri synthesis in the 20th century.",
            "During the Nigerian Civil War, garri’s stable shelf-life provided emergency caloric security.",
            "Today, biofortified cassava crops deliver built-in provitamin A directly to the starch.",
            "Modern chefs mold eba into sleek geometric forms for high-end culinary presentations.",
            "Water temperature control remains the supreme physical variable in eba synthesis.",
            "Sub-boiling water fails to initiate starch gelatinization, leaving gritty, raw particles behind.",
            "Boiling H₂O forces amylose molecules to expand and form a cohesive viscoelastic matrix.",
            "Whether in Lagos or London, eba remains the ultimate speed-of-light carbohydrate fuel.",
            "It combines historical agricultural resilience, structural polymer physics, and absolute comfort.",
            "Simple to prepare yet deeply scientific, eba remains West Africa’s most iconic edible gel."
        ]
    }
];

const TIMELINE = [
    {when: "Long ago, in South America", text: "Tribes learn to remove the poison from cassava by grating and squeezing it."},
    {when: "16th century", text: "Portuguese traders bring cassava to West Africa. It grows well even in poor soil."},
    {when: "19th century", text: "Afro-Brazilians who returned to Africa bring the roasting method for cassava flour."},
    {when: "20th century", text: "Machines for grating and pressing cassava make garri in much bigger amounts."},
    {when: "Nigerian Civil War", text: "Garri lasts a long time without spoiling, so it becomes an emergency food."},
    {when: "Today", text: "New cassava crops carry extra vitamin A, chefs mold eba into modern shapes, and people eat it from Lagos to London."}
];

const GLOSSARY = [
    ["Cassava", "A starchy root. It must be processed before eating because raw cassava has poison in it."],
    ["Garri", "Dry cassava flakes made by grating, fermenting, pressing and roasting cassava."],
    ["Fermentation", "Letting the cassava mash sit for 2 to 3 days so good bacteria make it sour and break down the poison."],
    ["Omorogun", "The strong wooden spatula used to stir and turn eba."],
    ["Ewedu", "A slippery green soup that helps eba slide down easily."],
    ["Gbegiri", "A smooth soup made from slow-cooked, mashed beans."],
    ["Abula", "Ewedu and Gbegiri served together, a Yoruba favourite."],
    ["Egusi", "A rich soup made from ground melon seeds."],
    ["Ogbono", "A soup made from ogbono seeds. It is thick and stretchy."]
];

const SOUPS = [
    ["Abula (Yoruba favourite)", "Eba with Ewedu and Gbegiri. The Ewedu is slippery so the eba slides down easily. The Gbegiri is a smooth, rich soup made from slow-cooked mashed beans."],
    ["Egusi soup (Igbo tradition)", "Igbo tradition pairs yellow garri with rich Egusi soup, which is made from ground melon seeds."],
    ["Ogbono soup (Igbo tradition)", "Ogbono seeds make the soup thick and stretchy, so it grips the eba well."]
];

const TIPS = [
    "Use water that is truly boiling. Water that is only warm will not cook the garri, and the eba will feel gritty.",
    "Pour the garri in slowly and spread it over the water. Do not dump it all in one spot.",
    "Let the pot sit covered for 1 minute before you stir. This lets the garri soak properly.",
    "Stir hard with a wooden spatula and press the eba against the sides of the pot to remove lumps.",
    "Get the water right. Too much water makes it watery, too little makes it hard.",
    "Eat it while it is hot, with plenty of soup."
];

const FAQ = [
    ["Why is my eba full of lumps?", "Most likely the garri was poured in too fast, or it was not stirred hard enough. Pour slowly, let it soak for 1 minute, then stir and press firmly."],
    ["Why is my eba too hard?", "There was too little water. Use about 1.35 cups of water for every 1 cup of garri."],
    ["Why is my eba watery and soft?", "There was too much water. Next time measure the water carefully, or add a little more garri and stir."],
    ["Why does my eba feel gritty or raw?", "The water was not hot enough. Warm water cannot cook the garri. Make sure it is bubbling hot."],
    ["Can I use cold water?", "No. Eba needs boiling water to make the garri swell and turn smooth."],
    ["White garri or yellow garri?", "Both work. White garri is plain. Yellow garri has palm oil added for colour and flavour. Choose the one you like."]
];

let mode = 1;

function fmt(x) { return parseFloat(x.toFixed(2)).toString(); }

function zoom(src) {
    document.getElementById("lbImg").src = src;
    document.getElementById("lightbox").style.display = "flex";
}

function buildGallery() {
    let h = "";
    PICS.forEach(function (p) {
        h += '<img src="' + p + '" alt="Picture" onclick="zoom(this.src)" onerror="this.style.display=\'none\'">';
    });
    document.getElementById("gallery").innerHTML = h;
    document.getElementById("banner-eba").src = PICS[1];
    document.getElementById("banner-soups").src = PICS[2];
}

function buildHistory() {
    let html = "";
    HISTORY.forEach(function (sec, idx) {
        html += '<div class="card"><h3 class="gold">' + sec.title + '</h3>';
        sec.lines.forEach(function (l) { html += "<p>" + l + "</p>"; });
        html += "</div>";
        if (idx === 1) { html += '<img class="wide" src="' + PICS[1] + '" alt="Picture" onclick="zoom(this.src)" onerror="this.style.display=\'none\'">'; }
        if (idx === 3) { html += '<img class="wide" src="' + PICS[2] + '" alt="Picture" onclick="zoom(this.src)" onerror="this.style.display=\'none\'">'; }
    });
    document.getElementById("historyCards").innerHTML = html;

    let t = "";
    TIMELINE.forEach(function (i) { t += '<div class="tl-item"><b>' + i.when + '</b>' + i.text + '</div>'; });
    document.getElementById("timeline").innerHTML = t;

    let g = "";
    GLOSSARY.forEach(function (i) { g += '<p><span class="hl">' + i[0] + ':</span> ' + i[1] + '</p>'; });
    document.getElementById("glossary").innerHTML = g;
}

function buildEbaExtras() {
    const rows = [1, 2, 4, 6, 10, 20];
    let h = '<table class="chart"><tr><th>People</th><th>Normal<br>garri / water</th><th>Big eaters 8x<br>garri / water</th></tr>';
    rows.forEach(function (n) {
        h += "<tr><td><b>" + n + "</b></td><td>" + fmt(n) + " / " + fmt(n * 1.35) + " cups</td><td>" + fmt(n * 8) + " / " + fmt(n * 8 * 1.35) + " cups</td></tr>";
    });
    h += "</table>";
    document.getElementById("chart").innerHTML = h;

    document.getElementById("tips").innerHTML = TIPS.map(function (t) { return "<li>" + t + "</li>"; }).join("");

    let f = "";
    FAQ.forEach(function (q) { f += "<details><summary>" + q[0] + "</summary><p>" + q[1] + "</p></details>"; });
    document.getElementById("faq").innerHTML = f;

    let s = "";
    SOUPS.forEach(function (q) { s += '<p><span class="hl">' + q[0] + ':</span> ' + q[1] + '</p>'; });
    document.getElementById("soupList").innerHTML = s;
}

function buildFrame() {
    const R = 108;
    let out = "";
    function pt(theta, r) {
        const t = theta * Math.PI / 180;
        return [150 + r * Math.cos(t), 150 - r * Math.sin(t)];
    }
    const s1 = pt(130, R), e1 = pt(236, R);
    const s2 = pt(50, R), e2 = pt(-56, R);
    out += '<path d="M' + s1[0] + ' ' + s1[1] + ' A' + R + ' ' + R + ' 0 0 0 ' + e1[0] + ' ' + e1[1] + '" fill="none" stroke="url(#goldG)" stroke-width="3"/>';
    out += '<path d="M' + s2[0] + ' ' + s2[1] + ' A' + R + ' ' + R + ' 0 0 1 ' + e2[0] + ' ' + e2[1] + '" fill="none" stroke="url(#goldG)" stroke-width="3"/>';
    for (let a = 130; a <= 236; a += 8) {
        const size = 13 - ((a - 130) / 106) * 4;
        [1, 2].forEach(function (side) {
            const theta = side === 1 ? a : 180 - a;
            const rotBase = -(theta + 90);
            const inner = pt(theta, R - 8);
            const outer = pt(theta, R + 8);
            out += '<ellipse cx="' + inner[0] + '" cy="' + inner[1] + '" rx="' + size + '" ry="4.6" fill="url(#goldG)" transform="rotate(' + (rotBase + 35) + ' ' + inner[0] + ' ' + inner[1] + ')"/>';
            out += '<ellipse cx="' + outer[0] + '" cy="' + outer[1] + '" rx="' + size + '" ry="4.6" fill="url(#goldG)" transform="rotate(' + (rotBase - 35) + ' ' + outer[0] + ' ' + outer[1] + ')"/>';
        });
    }
    document.getElementById("leaves").innerHTML = out;
}

function showTab(key) {
    ["history", "eba", "soups", "voice"].forEach(function (k) {
        document.getElementById("sec-" + k).style.display = (k === key) ? "block" : "none";
        document.getElementById("tab-" + k).classList.toggle("active", k === key);
    });
}

function setMode(m) {
    mode = m;
    document.getElementById("normalBtn").classList.toggle("on", m === 1);
    document.getElementById("bigBtn").classList.toggle("on", m === 8);
    calc();
}

function getPeople() {
    const p = parseInt(document.getElementById("people").value);
    return (isNaN(p) || p < 1) ? 0 : p;
}

function amounts() {
    const people = getPeople();
    const garri = people * mode;
    const water = garri * 1.35;
    return {people: people, garri: garri, water: water};
}

function calc() {
    const a = amounts();
    if (a.people === 0) {
        document.getElementById("servLine").innerText = "Type how many people are eating above.";
        document.getElementById("outGarri").innerText = "?";
        document.getElementById("outWater").innerText = "?";
        document.getElementById("outMl").innerText = "";
        document.getElementById("potTip").innerText = "";
        return;
    }
    let line = "For " + a.people + (a.people === 1 ? " person" : " people");
    if (mode === 8) {
        line += " (big eaters, 8x portions) that is " + (a.people * 8) + " normal servings.";
    } else {
        line += " that is " + a.people + (a.people === 1 ? " serving." : " servings.");
    }
    document.getElementById("servLine").innerText = line;
    document.getElementById("outGarri").innerText = fmt(a.garri);
    document.getElementById("outWater").innerText = fmt(a.water);
    document.getElementById("outMl").innerText = "(about " + Math.round(a.water * 240) + " ml)";
    let tip = "Tip: use a pot that can hold at least double the water.";
    if (a.garri > 10) { tip = "Tip: this is a lot. Use a very big pot, or cook it in 2 or 3 rounds so it does not form lumps."; }
    document.getElementById("potTip").innerText = tip;
}

async function speak(text, voice, rate, btn, player) {
    const original = btn.innerText;
    btn.disabled = true;
    btn.innerText = "⏳ Making voice... please wait";
    const fd = new FormData();
    fd.append("text", text);
    fd.append("voice", voice);
    fd.append("rate", rate);
    try {
        const r = await fetch("/generate", {method: "POST", body: fd});
        if (!r.ok) throw new Error("failed");
        const blob = await r.blob();
        const url = URL.createObjectURL(blob);
        player.src = url;
        player.style.display = "block";
        player.play().catch(function () {});
        btn.innerText = original;
        btn.disabled = false;
        return url;
    } catch (e) {
        alert("Voice failed. Please wait a few seconds and try again.");
        btn.innerText = original;
        btn.disabled = false;
        return null;
    }
}

function listenHistory() {
    let text = "The story of eba. ";
    HISTORY.forEach(function (sec) {
        sec.lines.forEach(function (l) { text += l + " "; });
    });
    speak(text, "en-NG-EzinneNeural", "-15%", document.getElementById("histBtn"), document.getElementById("histPlayer"));
}

function listenRecipe() {
    const a = amounts();
    if (a.people === 0) { alert("Please type how many people are eating first."); return; }
    let t = "Here is how to make eba for " + a.people + (a.people === 1 ? " person. " : " people. ");
    if (mode === 8) { t += "These are big eaters, so the portions are eight times bigger. "; }
    t += "You will need " + fmt(a.garri) + " cups of garri, and " + fmt(a.water) + " cups of hot water. ";
    t += "Step 1. Pour the water into a clean pot and boil it for 5 to 7 minutes until it is bubbling hot. ";
    t += "Step 2. Turn off the heat. ";
    t += "Step 3. Pour the garri slowly into the hot water and spread it evenly. Do not stir yet. ";
    t += "Step 4. Cover the pot for 1 minute so the garri can soak and soften. ";
    t += "Step 5. Use a wooden spatula to turn and press the eba against the sides of the pot until it is smooth and lump free. ";
    t += "Step 6. Mold it into balls and serve hot with your favourite soup. Enjoy!";
    speak(t, "en-NG-EzinneNeural", "-15%", document.getElementById("recipeBtn"), document.getElementById("recipePlayer"));
}

async function makeVoice() {
    const text = document.getElementById("vText").value.trim();
    if (!text) { alert("Please type some text first."); return; }
    const url = await speak(
        text,
        document.getElementById("vVoice").value,
        document.getElementById("vSpeed").value,
        document.getElementById("vBtn"),
        document.getElementById("vPlayer")
    );
    if (url) {
        const dl = document.getElementById("vDownload");
        dl.href = url;
        dl.style.display = "block";
    }
}

buildGallery();
buildHistory();
buildEbaExtras();
buildFrame();
calc();
</script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def home():
    return HTML


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
    text = text.strip()[:9000]
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