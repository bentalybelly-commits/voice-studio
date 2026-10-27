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
    <title>EBA Calculator Pro</title>
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
            /* Cool Moving Background Animation */
            background: linear-gradient(-45deg, #FFB703, #FB8500, #ff9e00, #ffc300);
            background-size: 400% 400%;
            animation: gradientBG 10s ease infinite;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            color: var(--dark-text);
            box-sizing: border-box;
        }

        @keyframes gradientBG {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        .container {
            background: var(--white);
            padding: 30px 24px;
            border-radius: 24px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            max-width: 480px;
            width: 100%;
            text-align: center;
            /* Entrance Animation */
            animation: bounceIn 1s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        }

        @keyframes bounceIn {
            0% { transform: scale(0.8) translateY(-50px); opacity: 0; }
            100% { transform: scale(1) translateY(0); opacity: 1; }
        }

        h1 {
            color: var(--garri-orange);
            margin-bottom: 5px;
            font-size: 2.2em;
            line-height: 1.1;
            text-shadow: 2px 2px 4px rgba(251, 133, 0, 0.2);
        }

        .subtitle {
            color: #6b7280;
            margin-bottom: 25px;
            font-style: italic;
            font-size: 0.95em;
        }

        label {
            font-weight: 800;
            font-size: 1.05em;
            display: block;
            margin-bottom: 12px;
            color: var(--dark-text);
        }

        input {
            width: 100%;
            padding: 14px;
            font-size: 1.2em;
            border: 2px solid #e5e7eb;
            border-radius: 12px;
            text-align: center;
            outline: none;
            box-sizing: border-box;
            transition: all 0.3s ease;
        }

        input:focus {
            border-color: var(--garri-orange);
            box-shadow: 0 0 15px 