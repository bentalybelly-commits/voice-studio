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


HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Naija Kitchen Pro</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800&family=Fredoka:wght@600&family=Noto+Sans+Math&display=swap');

* { box-sizing: border-box; font-family: 'Outfit', sans-serif; }

body {
    margin: 0; padding: 20px; min-height: 100vh; color: #E0E1DD;
    background:
        radial-gradient(circle at 15% 10%, rgba(231,111,81,0.35), transparent 45%),
        radial-gradient(circle at 85% 90%, rgba(42,157,143,0.35), transparent 45%),
        linear-gradient(135deg, #0B132B, #1C2541);
    background-attachment: fixed;
    display: flex; justify-content: center; align-items: flex-start;
}

.container {
    background: rgba(28, 37, 65, 0.88);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 20px; padding: 26px;
    max-width: 640px; width: 100%;
    box-shadow: 0 25px 50px rgba(0,0,0,0.6);
    animation: dropIn 0.8s ease-out;
}

h1 {
    text-align: center; font-size: 2.1em; margin: 0 0 5px;
    text-transform: uppercase; letter-spacing: 1px;
    background: linear-gradient(135deg, #F4A261, #E76F51, #2A9D8F);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
p.subtitle { text-align: center; color: #9CA3AF; margin: 0 0 20px; }

.tabs { display: flex; gap: 10px; overflow-x: auto; padding: 6px 4px 12px; margin-bottom: 10px; }
.tab {
    flex: 0 0 auto; border: none; color: white; padding: 12px 16px;
    border-radius: 25px; font-weight: 800; font-size: 1em; cursor: pointer;
    opacity: 0.55; transition: 0.3s;
}
.tab.active { opacity: 1; transform: scale(1.06); box-shadow: 0 8px 18px rgba(0,0,0,0.4); }

.dish-head { text-align: center; margin-bottom: 15px; }
.dish-emoji { font-size: 3.5em; }
.dish-head h2 { margin: 5px 0; font-size: 1.8em; color: var(--accent); }
.dish-head p { margin: 0; color: #9CA3AF; }

input, textarea, select {
    width: 100%; padding: 14px; font-size: 1.1em;
    background: rgba(255,255,255,0.06); color: white;
    border: 2px solid #3A506B; border-radius: 12px; outline: none; transition: 0.3s;
}
input { text-align: center; }
textarea { min-height: 150px; resize: vertical; }
select option { color: black; }
input:focus, textarea:focus, select:focus { border-color: #E76F51; box-shadow: 0 0 15px rgba(231,111,81,0.3); }
label { display: block; margin: 12px 0 6px; color: #F4A261; font-weight: 600; }

.box {
    background: rgba(255,255,255,0.05);
    border-left: 4px solid var(--accent, #F4A261);
    padding: 18px; border-radius: 12px; margin-top: 15px;
}
.box h3 { margin-top: 0; color: var(--accent, #F4A261); border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px; }
ul, ol { padding-left: 20px; line-height: 1.6; }
li { margin-bottom: 10px; }
.hl { color: #E76F51; font-weight: 800; }

button.big {
    width: 100%; color: white; border: none; padding: 14px; font-size: 1.1em; font-weight: 800;
    border-radius: 12px; cursor: pointer; margin-top: 14px; transition: 0.3s;
    background: linear-gradient(135deg, #2A9D8F, #21867a);
}
button.big:hover { transform: translateY(-3px); }
button.big:disabled { opacity: 0.6; cursor: wait; }

audio { width: 100%; margin-top: 14px; display: none; }
a.download {
    display: none; text-align: center; margin-top: 12px; padding: 12px; border-radius: 12px;
    background: #E76F51; color: white; text-decoration: none; font-weight: 800;
}

.dev-card {
    margin-top: 30px; padding: 20px; text-align: center;
    background: rgba(231,111,81,0.15); border: 2px dashed #F4A261; border-radius: 18px;
}
.dev-pfp {
    width: 120px; height: 120px; border-radius: 50%;
    object-fit: cover; object-position: center 30%;
    border: 3px solid #F4A261;
    box-shadow: 0 0 25px rgba(244,162,97,0.7), 0 0 45px rgba(60,170,255,0.4);
}
.dev-fallback { display: none; font-size: 4em; }
.dev-label { margin: 12px 0 2px; color: #9CA3AF; font-size: 0.9em; letter-spacing: 2px; text-transform: uppercase; }
.dev-name {
    margin: 0; font-size: 2.2em;
    font-family: 'Noto Sans Math', 'Cambria Math', 'Segoe UI Symbol', serif;
    background: linear-gradient(135deg, #F4A261, #E76F51, #2A9D8F);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}

@keyframes dropIn { 0% { transform: translateY(-30px); opacity: 0; } 100% { transform: translateY(0); opacity: 1; } }
</style>
</head>
<body>
<div class="container">
    <h1>Naija Kitchen Pro 🍽️</h1>
    <p class="subtitle">Learn how to cook your favourite foods, and listen while you cook</p>

    <div class="tabs" id="tabs"></div>

    <div id="dishBox">
        <div class="dish-head">
            <div class="dish-emoji" id="dEmoji"></div>
            <h2 id="dName"></h2>
            <p id="dTag"></p>
        </div>

        <input type="number" id="people" min="1" max="100" value="4" placeholder="How many people are eating?" oninput="updateAmounts()">

        <div class="box">
            <h3>📊 What you need</h3>
            <p>For <span class="hl" id="outPeople"></span> people:</p>
            <ul id="ingList"></ul>
        </div>

        <div class="box">
            <h3>🧰 Extras</h3>
            <ul id="extraList"></ul>
        </div>

        <div class="box">
            <h3>📖 Step-by-step</h3>
            <button class="big" id="listenBtn" onclick="listenRecipe()">🔊 Listen to the recipe</button>
            <audio id="dishPlayer" controls></audio>
            <ol id="stepList"></ol>
        </div>
    </div>

    <div id="voiceBox" style="display:none;">
        <div class="dish-head">
            <div class="dish-emoji">🎙️</div>
            <h2 style="color:#2A9D8F;">Voice Generator</h2>
            <p>Type anything and hear it read out loud</p>
        </div>
        <label for="vText">Your text</label>
        <textarea id="vText">Welcome to Naija Kitchen. Type anything here and I will read it out loud for you.</textarea>
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

    <div class="dev-card">
        <img class="dev-pfp" src="/pfp.jpg" alt="Developer picture"
             onerror="this.style.display='none'; document.getElementById('devFallback').style.display='block';">
        <div class="dev-fallback" id="devFallback">👑</div>
        <p class="dev-label">Developer</p>
        <p class="dev-name">𝕴 𝖉𝖔𝖓'𝖙 𝖐𝖓𝖔𝖜</p>
    </div>
</div>

<script>
const DISHES = {
    eba: {
        tab: "🥣 Eba", name: "Eba", emoji: "🥣", color: "#F4A261",
        tagline: "Smooth, soft and lump free every time",
        ingredients: [
            {n: "Garri", per: 1, one: "cup", many: "cups"},
            {n: "Boiling water", per: 1.35, one: "cup", many: "cups"}
        ],
        extras: ["A clean pot", "A strong wooden spatula (omorogun)", "Egusi or any soup to eat it with"],
        steps: [
            "Pour the water into a clean pot and boil it for 5 to 7 minutes until it is bubbling hot.",
            "Turn off the heat, or take the pot off the fire.",
            "Pour the garri slowly into the hot water and spread it evenly. Do not stir yet.",
            "Cover the pot for 1 minute so the garri can soak and soften.",
            "Use the wooden spatula to turn and press the eba against the sides of the pot until it is smooth and lump free.",
            "Mold it into balls and serve hot with your favourite soup."
        ]
    },
    jollof: {
        tab: "🍛 Jollof Rice", name: "Jollof Rice", emoji: "🍛", color: "#E76F51",
        tagline: "Party style, smoky and full of flavour",
        ingredients: [
            {n: "Long grain parboiled rice", per: 0.75, one: "cup", many: "cups"},
            {n: "Blended tomato and pepper mix", per: 0.5, one: "cup", many: "cups"},
            {n: "Chicken stock or water", per: 0.75, one: "cup", many: "cups"},
            {n: "Vegetable oil", per: 1, one: "tablespoon", many: "tablespoons"},
            {n: "Tomato paste", per: 0.5, one: "tablespoon", many: "tablespoons"}
        ],
        extras: ["1 sliced onion for every 4 people", "Curry powder, thyme, salt and seasoning cubes to taste", "Aluminium foil", "Fried plantain to serve"],
        steps: [
            "Wash the rice in warm water 2 to 3 times until the water looks clearer, then drain it.",
            "Pour the blended tomato and pepper mix into a pot and boil on medium heat for 10 to 15 minutes until it becomes thick.",
            "In a big pot, heat the oil. Add the sliced onions and fry for 2 minutes.",
            "Add the tomato paste and fry for 3 to 5 minutes, stirring so it does not burn.",
            "Add the cooked pepper mix, curry, thyme, seasoning cubes and salt. Fry for 5 minutes.",
            "Add the stock and let it boil. Taste it and add salt if needed.",
            "Add the washed rice and stir once. The liquid should be just level with the rice. Cover with foil, then the lid, and cook on the lowest heat for 25 to 30 minutes.",
            "Stir gently from the bottom, cover again and cook 5 to 10 more minutes until the rice is soft. Serve hot with fried plantain."
        ]
    },
    egusi: {
        tab: "🍲 Egusi Soup", name: "Egusi Soup", emoji: "🍲", color: "#2A9D8F",
        tagline: "Rich melon seed soup that goes with eba",
        ingredients: [
            {n: "Ground egusi (melon seeds)", per: 0.25, one: "cup", many: "cups"},
            {n: "Palm oil", per: 2, one: "tablespoon", many: "tablespoons"},
            {n: "Meat or fish stock", per: 0.75, one: "cup", many: "cups"},
            {n: "Blended pepper and onion", per: 2, one: "tablespoon", many: "tablespoons"},
            {n: "Ground crayfish", per: 1, one: "tablespoon", many: "tablespoons"},
            {n: "Cooked meat or fish", per: 2, one: "piece", many: "pieces"},
            {n: "Washed and chopped spinach or ugu leaves", per: 1, one: "handful", many: "handfuls"}
        ],
        extras: ["Salt and seasoning cubes to taste", "A wooden spoon", "Eba, pounded yam or fufu to eat it with"],
        steps: [
            "Heat the palm oil in a pot on medium heat for 2 minutes. Do not let it smoke.",
            "Add the blended pepper and onion and fry for 5 minutes.",
            "Mix the ground egusi with a little water to make a thick paste.",
            "Scoop the egusi paste into the pot in small lumps. Leave it for 5 minutes without stirring so it forms curds.",
            "Add the stock, crayfish, seasoning cubes and salt. Cover and cook on low heat for 10 to 15 minutes, stirring gently once or twice.",
            "Add the cooked meat or fish and cook for 5 to 10 more minutes.",
            "Add the chopped leaves, stir, and cook for 3 minutes. Turn off the heat and serve hot with eba."
        ]
    },
    moimoi: {
        tab: "🫔 Moi Moi", name: "Moi Moi", emoji: "🫔", color: "#9B5DE5",
        tagline: "Soft steamed bean pudding",
        ingredients: [
            {n: "Peeled beans", per: 0.5, one: "cup", many: "cups"},
            {n: "Blended pepper and onion mix", per: 0.25, one: "cup", many: "cups"},
            {n: "Warm water for blending", per: 0.5, one: "cup", many: "cups"},
            {n: "Vegetable oil", per: 1, one: "tablespoon", many: "tablespoons"},
            {n: "Boiled egg", per: 1, one: "piece", many: "pieces"}
        ],
        extras: ["Salt, seasoning cubes and ground crayfish to taste", "Moi moi cups, small bowls or foil cups", "A pot with a lid", "Pap or jollof rice to serve"],
        steps: [
            "Soak the beans in water for 5 minutes. Rub them with your hands to remove the skins, then rinse until the skins float away and the beans look white.",
            "Blend the beans with the pepper and onion mix and the warm water until smooth. It should be thick, not watery.",
            "Pour the mixture into a bowl. Add the oil, salt, crayfish and seasoning cubes. Stir well.",
            "Pour into your moi moi cups. Add a slice of boiled egg to each one if you like. Cover them.",
            "Put 2 cups of water in a pot. Place a small rack or upside down plate inside, then arrange the cups on it. Cover the pot and steam on medium heat for 45 to 60 minutes. Add hot water if it dries out.",
            "Push a knife into the middle. If it comes out clean, it is ready. Let it cool for 5 minutes and serve."
        ]
    }
};

let current = "eba";

function fmt(x) { return parseFloat(x.toFixed(2)).toString(); }

function getPeople() {
    const p = parseInt(document.getElementById("people").value);
    return (isNaN(p) || p < 1) ? 0 : p;
}

function buildTabs() {
    const tabs = document.getElementById("tabs");
    let html = "";
    for (const key in DISHES) {
        html += '<button class="tab" id="tab-' + key + '" style="background:' + DISHES[key].color + '" onclick="showTab(\'' + key + '\')">' + DISHES[key].tab + '</button>';
    }
    html += '<button class="tab" id="tab-voice" style="background:#2A9D8F" onclick="showTab(\'voice\')">🎙️ Voice Generator</button>';
    tabs.innerHTML = html;
}

function showTab(key) {
    document.querySelectorAll(".tab").forEach(function (t) { t.classList.remove("active"); });
    document.getElementById("tab-" + key).classList.add("active");
    if (key === "voice") {
        document.getElementById("dishBox").style.display = "none";
        document.getElementById("voiceBox").style.display = "block";
        return;
    }
    document.getElementById("voiceBox").style.display = "none";
    document.getElementById("dishBox").style.display = "block";
    current = key;
    const d = DISHES[key];
    document.getElementById("dishBox").style.setProperty("--accent", d.color);
    document.getElementById("dEmoji").innerText = d.emoji;
    document.getElementById("dName").innerText = d.name;
    document.getElementById("dTag").innerText = d.tagline;
    document.getElementById("extraList").innerHTML = d.extras.map(function (e) { return "<li>" + e + "</li>"; }).join("");
    document.getElementById("stepList").innerHTML = d.steps.map(function (s) { return "<li>" + s + "</li>"; }).join("");
    document.getElementById("dishPlayer").style.display = "none";
    updateAmounts();
}

function amountText(i, people) {
    const q = i.per * people;
    return fmt(q) + " " + (q <= 1 ? i.one : i.many);
}

function updateAmounts() {
    const d = DISHES[current];
    const people = getPeople();
    const list = document.getElementById("ingList");
    if (people === 0) {
        document.getElementById("outPeople").innerText = "?";
        list.innerHTML = "<li>Type how many people are eating above.</li>";
        return;
    }
    document.getElementById("outPeople").innerText = people;
    list.innerHTML = d.ingredients.map(function (i) {
        return '<li><span class="hl">' + amountText(i, people) + '</span> of ' + i.n + '</li>';
    }).join("");
}

async function speak(text, voice, rate, btn, player) {
    const original = btn.innerText;
    btn.disabled = true;
    btn.innerText = "⏳ Making voice...";
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

function listenRecipe() {
    const d = DISHES[current];
    const people = getPeople();
    if (people === 0) { alert("Please type how many people are eating first."); return; }
    let script = "Here is how to make " + d.name + " for " + people + (people === 1 ? " person" : " people") + ". You will need: ";
    script += d.ingredients.map(function (i) { return amountText(i, people) + " of " + i.n; }).join(", ") + ". ";
    d.steps.forEach(function (s, idx) { script += "Step " + (idx + 1) + ". " + s + " "; });
    script += "Enjoy your " + d.name + "!";
    speak(script, "en-NG-EzinneNeural", "-15%", document.getElementById("listenBtn"), document.getElementById("dishPlayer"));
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

buildTabs();
showTab("eba");
</script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def home():
    return HTML


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