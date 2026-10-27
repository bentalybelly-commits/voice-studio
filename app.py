import os
import re
import edge_tts
from fastapi import FastAPI, Form, Response
from fastapi.responses import HTMLResponse

app = FastAPI()

def preprocess_for_tts(text: str) -> str:
    """Preprocesses text to ensure edge-tts pronounces Nigerian food words correctly."""
    text = re.sub(r'\beba\b', 'Eh-bah', text, flags=re.IGNORECASE)
    text = re.sub(r'\begusi\b', 'Eh-goo-see', text, flags=re.IGNORECASE)
    return text

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EBA Pro Calculator & Recipe</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800&display=swap');

        * { box-sizing: border-box; font-family: 'Outfit', sans-serif; }

        body {
            margin: 0; padding: 20px; min-height: 100vh;
            background: linear-gradient(135deg, #0B132B, #1C2541, #3A506B);
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
            color: #E0E1DD;
            display: flex; justify-content: center; align-items: flex-start;
        }

        @keyframes gradientBG {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        .container {
            background: rgba(28, 37, 65, 0.85);
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 30px;
            max-width: 600px;
            width: 100%;
            box-shadow: 0 25px 50px rgba(0,0,0,0.5);
            animation: dropIn 0.8s ease-out;
        }

        .gallery {
            display: flex; justify-content: center; gap: 15px; margin-bottom: 20px;
        }
        .gallery img {
            width: 130px; height: 130px; object-fit: cover;
            border-radius: 20px; border: 3px solid #F4A261;
            box-shadow: 0 10px 20px rgba(0,0,0,0.3);
            transition: transform 0.3s;
        }
        .gallery img:hover { transform: scale(1.1) rotate(5deg); }

        h1 { color: #F4A261; text-align: center; font-size: 2.2em; margin: 0 0 5px; text-transform: uppercase; letter-spacing: 1px;}
        p.subtitle { text-align: center; color: #9CA3AF; margin-bottom: 25px; }

        input {
            width: 100%; padding: 15px; font-size: 1.2em;
            background: rgba(255,255,255,0.05); color: white;
            border: 2px solid #3A506B; border-radius: 12px;
            text-align: center; outline: none; transition: 0.3s;
        }
        input:focus { border-color: #E76F51; box-shadow: 0 0 15px rgba(231, 111, 81, 0.3); }

        button.calc-btn {
            width: 100%; background: linear-gradient(135deg, #E76F51, #F4A261);
            color: white; border: none; padding: 16px; font-size: 1.2em; font-weight: 800;
            border-radius: 12px; cursor: pointer; margin-top: 15px; transition: 0.3s;
        }
        button.calc-btn:hover { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(231, 111, 81, 0.4); }

        #results { display: none; margin-top: 25px; animation: slideUp 0.5s ease-out forwards; }
        
        .box {
            background: rgba(255,255,255,0.05);
            border-left: 4px solid #F4A261;
            padding: 20px; border-radius: 12px; margin-bottom: 15px;
        }
        .box h3 { margin-top: 0; color: #F4A261; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px; }
        
        ul, ol { padding-left: 20px; line-height: 1.6; color: #E0E1DD; }
        li { margin-bottom: 10px; }
        
        .highlight { color: #E76F51; font-weight: bold; }

        button.play-btn {
            background: #2A9D8F; color: white; border: none; padding: 12px 20px;
            font-size: 1em; font-weight: bold; border-radius: 10px; cursor: pointer;
            display: flex; align-items: center; justify-content: center; width: 100%;
            margin-top: 15px; transition: 0.3s;
        }
        button.play-btn:hover { background: #21867a; }
        button.play-btn:disabled { opacity: 0.6; cursor: wait; }

        @keyframes dropIn { 0% { transform: translateY(-30px); opacity: 0; } 100% { transform: translateY(0); opacity: 1; } }
        @keyframes slideUp { 0% { transform: translateY(20px); opacity: 0; } 100% { transform: translateY(0); opacity: 1; } }
    </style>
</head>
<body>

    <div class="container">
        <div class="gallery">
            <img src="https://upload.wikimedia.org/wikipedia/commons/6/69/Eba_and_Efo_riro_soup.jpg" alt="Eba Dish">
            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/ca/Egusi_soup_and_eba.jpg/800px-Egusi_soup_and_eba.jpg" alt="Eba and Egusi">
        </div>

        <h1>Eba & Egusi Pro 🥣</h1>
        <p class="subtitle">The ultimate guide to authentic Nigerian Yoruba Eba</p>

        <input type="number" id="peopleInput" placeholder="How many people are eating?" min="1">
        <button class="calc-btn" onclick="calculateEba()">Calculate & Show Recipe</button>

        <div id="results">
            <div class="box">
                <h3>📊 Calculated Measurements</h3>
                <p>👨‍👩‍👧 For <span id="outPeople" class="highlight"></span> people, you need:</p>
                <ul>
                    <li><span id="outGarri" class="highlight"></span> Cups of Garri</li>
                    <li><span id="outWater" class="highlight"></span> Cups of Clean Water</li>
                    <li>Estimated Cost: <span class="highlight">₦</span><span id="outCost" class="highlight"></span></li>
                </ul>
            </div>

            <div class="box">
                <h3>🥘 Ingredients & Tools Needed</h3>
                <ul>
                    <li><b>Garri (Cassava Flakes):</b> White or Yellow/Bendel based on preference.</li>
                    <li><b>Clean Water:</b> Filtered and ready to boil.</li>
                    <li><b>Mixing Bowl / Pot:</b> Heat-proof plastic, ceramic bowl, or stainless pot.</li>
                    <li><b>Omorogun:</b> A wooden spatula or turning stick.</li>
                </ul>
            </div>

            <div class="box">
                <h3>📖 Step-by-Step Preparation</h3>
                <button class="play-btn" id="playBtn" onclick="playVoice()">
                    🔊 Play Audio Instructions (Female Voice)
                </button>
                <audio id="audioPlayer" style="width: 100%; margin-top: 15px; display: none;" controls></audio>

                <ol>
                    <li>Put your clean pot on the burner. Pour the required water into the pot and let it boil for about <b>5 to 7 minutes</b> until it is bubbling hot.</li>
                    <li>Turn off the heat or bring the pot down.</li>
                    <li>Gradually pour the Garri into the hot water, spreading it evenly across the surface.</li>
                    <li>Cover it for <b>1 minute</b> to allow the Garri to absorb the hot water and soften.</li>
                    <li>Use your wooden spatula to turn and stir the mixture vigorously against the edges of the pot until it becomes smooth, firm, and lump-free.</li>
                    <li>Mold it into your desired shape and <b>serve hot with delicious Egusi soup!</b></li>
                </ol>
            </div>
        </div>
    </div>

    <script>
        let recipeScript = "";

        function calculateEba() {
            let people = parseInt(document.getElementById('peopleInput').value);
            if (isNaN(people) || people <= 0) {
                alert("Please enter a valid number of people!");
                return;
            }

            let garri = people; 
            let water = (garri * 1.35).toFixed(1); 
            let cost = garri * 200;

            document.getElementById('outPeople').innerText = people;
            document.getElementById('outGarri').innerText = garri;
            document.getElementById('outWater').innerText = water;
            document.getElementById('outCost').innerText = cost;

            recipeScript = `Welcome to the eba calculation guide. You will need ${garri} cups of Garri, and ${water} cups of clean water. 
            Step 1. Put your pot on the burner, pour in the water, and let it boil for about 5 to 7 minutes until it is bubbling hot. 
            Step 2. Turn off the heat.
            Step 3. Gradually pour your Garri into the hot water, spreading it evenly. 
            Step 4. Cover it for 1 minute to allow the Garri to soften. 
            Step 5. Use your wooden spatula, to turn and stir vigorously until smooth and lump-free. 
            Finally, mold it into your desired shape and serve hot with delicious egusi soup!`;

            document.getElementById('results').style.display = 'block';
        }

        async function playVoice() {
            const btn = document.getElementById('playBtn');
            const player = document.getElementById('audioPlayer');
            
            btn.disabled = true;
            btn.innerText = "⏳ Generating AI Audio...";
            player.style.display = 'none';

            const formData = new FormData();
            formData.append('text', recipeScript);

            try {
                const response = await fetch('/generate', { method: 'POST', body: formData });
                if (!response.ok) throw new Error("Failed");
                
                const blob = await response.blob();
                player.src = URL.createObjectURL(blob);
                player.style.display = 'block';
                player.play();
                btn.innerText = "🔊 Audio Generated!";
                btn.disabled = false;
            } catch (e) {
                alert("Audio generation failed. Please try again.");
                btn.innerText = "🔊 Play Audio Instructions";
                btn.disabled = false;
            }
        }
    </script>
</body>
</html>"""

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML

@app.post("/generate")
async def generate(text: str = Form(...)):
    cleaned_text = preprocess_for_tts(text)

    # rate="-15%" slows down the speech tempo. Adjust to "-20%" if you want it even slower.
    communicate = edge_tts.Communicate(cleaned_text, "en-NG-EzinneNeural", rate="-15%", pitch="+0Hz")
    
    audio = bytearray()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio.extend(chunk["data"])
    return Response(content=bytes(audio), media_type="audio/mpeg")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
