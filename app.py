<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EBA Calculator App</title>
    <style>
        /* === COLORFUL THEME & LAYOUT === */
        :root {
            --garri-yellow: #FFB703;
            --garri-orange: #FB8500;
            --naija-green: #2A9D8F;
            --dark-text: #023047;
            --white: #FFFFFF;
        }

        body {
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, var(--garri-yellow), var(--garri-orange));
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            color: var(--dark-text);
        }

        .container {
            background: var(--white);
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 15px 30px rgba(0,0,0,0.2);
            max-width: 450px;
            width: 90%;
            text-align: center;
            animation: dropIn 0.8s ease-out;
        }

        h1 {
            color: var(--garri-orange);
            margin-bottom: 5px;
            font-size: 2.5em;
        }

        .subtitle {
            color: gray;
            margin-bottom: 25px;
            font-style: italic;
        }

        /* === INPUT SECTION === */
        .input-group {
            margin-bottom: 20px;
        }

        label {
            font-weight: bold;
            font-size: 1.1em;
            display: block;
            margin-bottom: 10px;
        }

        input {
            width: 80%;
            padding: 12px;
            font-size: 1.2em;
            border: 2px solid var(--garri-yellow);
            border-radius: 10px;
            text-align: center;
            outline: none;
            transition: all 0.3s ease;
        }

        input:focus {
            border-color: var(--naija-green);
            box-shadow: 0 0 10px rgba(42, 157, 143, 0.4);
        }

        button {
            margin-top: 15px;
            background: var(--naija-green);
            color: var(--white);
            border: none;
            padding: 15px 30px;
            font-size: 1.2em;
            font-weight: bold;
            border-radius: 10px;
            cursor: pointer;
            transition: transform 0.2s, background 0.3s;
            box-shadow: 0 5px 15px rgba(42, 157, 143, 0.4);
        }

        button:hover {
            background: #21867a;
            animation: pulse 1s infinite;
        }

        button:active {
            transform: scale(0.95);
        }

        /* === RESULTS SECTION === */
        #results {
            display: none; /* Hidden until calculated */
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
            font-size: 1.1em;
        }

        .result-item span {
            font-weight: bold;
            color: var(--garri-orange);
        }

        /* === RECIPE STEPS === */
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

        /* === ANIMATIONS === */
        @keyframes dropIn {
            0% { transform: translateY(-50px); opacity: 0; }
            100% { transform: translateY(0); opacity: 1; }
        }

        @keyframes slideUp {
            0% { transform: translateY(30px); opacity: 0; }
            100% { transform: translateY(0); opacity: 1; }
        }

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
    </style>
</head>
<body>

    <div class="container">
        <h1>=== EBA ===<br>CALCULATOR 🥣</h1>
        <p class="subtitle">Compute Garri and Water based on your Python assignment!</p>

        <div class="input-group">
            <label for="peopleInput">How many people are eating?</label>
            <input type="number" id="peopleInput" placeholder="Enter number of people" min="1" required>
            <button onclick="computeEba()">Compute EBA ( )</button>
        </div>

        <div id="results">
            <h2 style="text-align: center; margin-top: 0; color: var(--dark-text);">-- Result --</h2>
            <div class="result-item">👩‍👩‍👦 Estimated Wraps: <span id="outWraps"></span></div>
            <div class="result-item">🍚 Garri Needed: <span id="outGarri"></span> Cups</div>
            <div class="result-item">💧 Hot Water Needed: <span id="outWaterCups"></span> Cups (<span id="outWaterLitres"></span> Litres)</div>
            <div class="result-item">💵 Estimated Cost: <span id="outCost"></span> ₦</div>
            
            <div class="steps-box">
                <h3>Steps To Make It:</h3>
                <ol>
                    <li>Boil water</li>
                    <li>Pour Garri into the hot water</li>
                    <li>Turn/Stir the EBA to your desired texture</li>
                </ol>
            </div>
        </div>
    </div>

    <script>
        function computeEba() {
            // 1. Get input (Number of people)
            let people = document.getElementById('peopleInput').value;
            people = parseInt(people);

            if (isNaN(people) || people <= 0) {
                alert("Please enter a valid number of people! 😅");
                return;
            }

            // 2. The Math/Logic from your Python Homework
            let wraps = people; // 1 person = 1 wrap
            let garri_cups = people; // 1 person = 1 cup of garri
            let water_cups = garri_cups * 2; // 1 cup garri needs 2 cups hot water
            let water_litres = water_cups * 0.25; // 1 cup = 0.25 Litres
            
            // Cost calculation
            let price_per_cup = 200; // ₦200 per cup of garri
            let total_cost = garri_cups * price_per_cup;

            // 3. Output to HTML
            document.getElementById('outWraps').innerText = wraps;
            document.getElementById('outGarri').innerText = garri_cups;
            document.getElementById('outWaterCups').innerText = water_cups;
            document.getElementById('outWaterLitres').innerText = water_litres;
            document.getElementById('outCost').innerText = total_cost;

            // 4. Trigger Animation (Show the results box)
            let resultsDiv = document.getElementById('results');
            
            // Reset animation so it plays every time you click the button
            resultsDiv.style.display = 'none';
            setTimeout(() => {
                resultsDiv.style.display = 'block';
            }, 50);
        }
    </script>
</body>
</html>