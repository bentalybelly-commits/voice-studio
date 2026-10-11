import asyncio
import edge_tts
import gradio as gr
import tempfile

# High-quality neural voices
VOICES = {
    "US - Christopher (Narrative Male)": "en-US-ChristopherNeural",
    "US - Guy (Casual Male)": "en-US-GuyNeural",
    "US - Jenny (Natural Female)": "en-US-JennyNeural",
    "US - Aria (Expressive Female)": "en-US-AriaNeural",
    "UK - Ryan (British Male)": "en-GB-RyanNeural",
    "UK - Sonia (British Female)": "en-GB-SoniaNeural",
    "AU - William (Australian Male)": "en-AU-WilliamNeural",
}

async def generate_speech(text, voice_name, speed):
    if not text.strip():
        return None
    
    voice = VOICES[voice_name]
    speed_str = f"{speed:+d}%"
    
    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    communicate = edge_tts.Communicate(text, voice, rate=speed_str)
    await communicate.save(temp_audio.name)
    return temp_audio.name

def tts_interface(text, voice_name, speed):
    return asyncio.run(generate_speech(text, voice_name, speed))

# Mobile-Optimized Layout
with gr.Blocks(title="Voice Studio") as demo:
    gr.Markdown("### 🎙️ My AI Voice Generator")
    
    text_input = gr.Textbox(
        label="Script", 
        placeholder="Type or paste your text here...", 
        lines=5
    )
    voice_dropdown = gr.Dropdown(
        choices=list(VOICES.keys()), 
        value="US - Christopher (Narrative Male)", 
        label="Select Voice"
    )
    speed_slider = gr.Slider(minimum=-50, maximum=50, value=0, step=5, label="Speed adjustment (%)")
    generate_btn = gr.Button("Generate Voice", variant="primary")
    audio_output = gr.Audio(label="Play / Download MP3", type="filepath")

    generate_btn.click(
        fn=tts_interface,
        inputs=[text_input, voice_dropdown, speed_slider],
        outputs=audio_output
    )

if __name__ == "__main__":
    demo.launch()