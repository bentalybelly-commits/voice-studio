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
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800&family=Fredoka:wght@600&display=swap');

        * { box-sizing: border-box; font-family: 'Outfit', sans-serif; }

        body {
            margin: 0; padding: 20px; min-height: 100vh;
            /* Low opacity Eba background overlay */
            background: linear-gradient(rgba(11, 19, 43, 0.92), rgba(28, 37, 65, 0.92)), 
                        url('https://upload.wikimedia.org/wikipedia/commons/6/69/Eba_and_Efo_riro_soup.jpg');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            color: #E0E1DD;
            display: flex; flex-direction: column; justify-content: center; align-items: center;
        }

        .container {
            background: rgba(28, 37, 65, 0.88);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 20px;
            padding: 30px;
            max-width: 600px;
            width: 100%;
            box-shadow: 0 25px 50px rgba(0,0,0,0.6);
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
            background: rgba(255,255
