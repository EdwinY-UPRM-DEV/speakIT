from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
import io
import os
import torch

app = FastAPI()

# --- Load Kokoro model ---
from kokoro import KPipeline

# Detect device
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Available voices (Kokoro built-in)
VOICES = {
    "af_heart":    "Heart (US Female)",
    "af_bella":    "Bella (US Female)",
    "af_nicole":   "Nicole (US Female)",
    "af_sarah":    "Sarah (US Female)",
    "af_sky":      "Sky (US Female)",
    "am_adam":     "Adam (US Male)",
    "am_michael":  "Michael (US Male)",
    "bf_emma":     "Emma (UK Female)",
    "bf_isabella": "Isabella (UK Female)",
    "bm_george":   "George (UK Male)",
    "bm_lewis":    "Lewis (UK Male)",
}

# Load pipeline (lang_code: 'a' = American English, 'b' = British English)
pipelines = {
    "a": KPipeline(lang_code="a", device=device),
    "b": KPipeline(lang_code="b", device=device),
}

class TTSRequest(BaseModel):
    text: str
    voice: str = "af_heart"
    speed: float = 1.0

@app.get("/voices")
def get_voices():
    return VOICES

@app.post("/speak")
def speak(req: TTSRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text is empty")

    if req.voice not in VOICES:
        raise HTTPException(status_code=400, detail="Invalid voice")

    # Choose pipeline based on voice prefix
    lang_code = "b" if req.voice.startswith("b") else "a"
    pipeline = pipelines[lang_code]

    # Generate audio
    audio_chunks = []
    generator = pipeline(req.text, voice=req.voice, speed=req.speed)
    for _, _, audio in generator:
        audio_chunks.append(audio)

    if not audio_chunks:
        raise HTTPException(status_code=500, detail="No audio generated")

    import numpy as np
    import soundfile as sf

    combined = np.concatenate(audio_chunks)
    buf = io.BytesIO()
    sf.write(buf, combined, 24000, format="WAV")
    buf.seek(0)

    return StreamingResponse(buf, media_type="audio/wav")

# Serve frontend
app.mount("/", StaticFiles(directory="public", html=True), name="static")
