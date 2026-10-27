import os
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EBA Calculator App</title>
    <style>
        :root {
            --garri-yellow: #FFB703;
            --garri-orange: #FB8500;
            --naija-green: #2A9D8F;
            --dark-text: #023047;
            --white: #FFFFFF;
        }

        body {
            margin: 0;
            padding: 16px;
            font-family: system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, var(--garri-yellow), var(--garri-orange));
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            color: var(--dark-text);
            box-sizing: border-box;
        }

        .container {
            background: var(--white);
            padding: 24px;
            border-radius: 20px;
            box-shadow: 0 15px 30px rgba(0,0,0,0.2);
            max-width: 450px;
            width: 100%;
            text-align: center;
            animation: dropIn 0.8s ease-out;
        }

        h1 {
            color: var(--garri-orange);
            margin-bottom: 5px;
            font-size: 2em;
        }

        .subtitle {
            color: gray;
            margin-bottom: 25px;
            font-style: italic;
            font-size: 0.9em;
        }

        .input-group {
            margin-bottom: 20px;
        }

        label {
            font-weight: bold;
            font-size: 1em;
            display: block;
            margin-bottom: 10px;
        }

        input {
            width: 100%;
            padding: 12px;
            font-size: 1.2em;
            border: 2px solid var(--garri-yellow);
            border-radius: 10px;
            text-align: center;
            outline: none;
            box-sizing: border-box;
        }

        input:focus {
            border-color: var(--naija-green);
        }

        button {
            margin-top: 15px;
            background: var(--naija-green);
            color: var(--white);
            border: none;
            padding: 15px 25px;
            font-size: 1.1em;
            font-weight: bold;
            border-radius: 10px;
            cursor: pointer;
            width: 100%;
            box-shadow: 0 5px 15px rgba(42, 157, 143, 0.4);
        }

        button:active {
            transform: scale(0.98);
        }

        #results {
            display: none;
            margin-top: 25px;
            background: #fdf6e3;
            padding: 20px;
            border-radius: 15px;
            border-left: 5px solid var(--garri-orange);
            text-align: left;
            animation: slideUp 0.5s ease-out forwards;
        }

        .result-item {
            margin: 10px 0;
            font-size: 1.05em;
        }

        .result-item span {
            font-weight: bold;
            color: var(--garri-orange);
        }

        .steps-box {
            margin-top: 20px;
            background: #e9f5f4;
            padding: 15px;
            border-radius: 10px;
            text-align: left;
            border-left: 5px solid var(--naija-green);
        }

        .steps-box h3 {
            margin-top: 0;
            color: var(--naija-green);
        }

        @keyframes dropIn {
            0% { transform: translateY(-30px); opacity: 0; }
            100% { transform: translateY(0); opacity: 1; }
        }

        @keyframes slideUp {
            0% { transform: translateY(20px); opacity: 0; }
            100% { transform: translateY(0); opacity: 1; }
        }
    </style>
</head>
<body>

    <div class="container">
        <h1>=== EBA ===<br>CALCULATOR 🥣</h1>
        <p class="subtitle">Compute Garri and Water for EBA</p>

        <div class="input-group">
            <label for="peopleInput">Number of people eating:</label>
            <input type="number" id="peopleInput" placeholder="Enter number of people" min="1">
            <button onclick="computeEba()">Compute EBA ( )</button>
        </div>

        <div id="results">
            <h3 style="text-align: center; margin-top: 0; color: var(--dark-text);">-- Output --</h3>
            <div class="result-item">👨‍👩‍👧 Estimated Wraps: <span id="outWraps"></span></div>
            <div class="result-item">🍚 Garri Needed: <span id="outGarri"></span> Cups</div>
            <div class="result-item">💧 Hot Water Needed: <span id="outWaterCups"></span> Cups (<span id="outWaterLitres"></span> Litres)</div>
            <div class="result-item">💵 Total Cost (₦200/cup): <span id="outCost"></span> ₦</div>
            
            <div class="steps-box">
                <h3>Steps To Make IT:</h3>
                <ol>
                    <li>Boil water</li>
                    <li>Pour Garri into cups</li>
                    <li>Stir/Turn EBA</li>
                </ol>
            </div>
        </div>
    </div>

    <script>
        function computeEba() {
            let people = document.getElementById('peopleInput').value;
            people = parseInt(people);

            if (isNaN(people) || people <= 0) {
                alert("Please enter a valid number of people!");
                return;
            }

            let wraps = people;
            let garri_cups = people;
            let water_cups = garri_cups * 2;
            let water_litres = water_cups * 0.25;
            let price_per_cup = 200;
            let total_cost = garri_cups * price_per_cup;

            document.getElementById('outWraps').innerText = wraps;
            document.getElementById('outGarri').innerText = garri_cups;
            document.getElementById('outWaterCups').innerText = water_cups;
            document.getElementById('outWaterLitres').innerText = water_litres;
            document.getElementById('outCost').innerText = total_cost;

            let resultsDiv = document.getElementById('results');
            resultsDiv.style.display = 'none';
            setTimeout(() => {
                resultsDiv.style.display = 'block';
            }, 50);
        }
    </script>
</body>
</html>"""

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)