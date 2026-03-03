from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import io, re
import torch
import numpy as np
import soundfile as sf

app = FastAPI()

from kokoro import KPipeline

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

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

pipelines = {
    "a": KPipeline(lang_code="a", device=device),
    "b": KPipeline(lang_code="b", device=device),
}

def split_sentences(text: str):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if len(s.strip()) > 2]

def text_to_wav_bytes(text, voice, speed):
    lang_code = "b" if voice.startswith("b") else "a"
    pipeline = pipelines[lang_code]
    chunks = []
    for _, _, audio in pipeline(text, voice=voice, speed=speed):
        chunks.append(audio)
    if not chunks:
        return b""
    combined = np.concatenate(chunks)
    buf = io.BytesIO()
    sf.write(buf, combined, 24000, format="WAV")
    buf.seek(0)
    return buf.read()

@app.get("/voices")
def get_voices():
    return VOICES

class TTSRequest(BaseModel):
    text: str
    voice: str = "af_heart"
    speed: float = 1.0

@app.post("/speak")
def speak(req: TTSRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text is empty")
    if req.voice not in VOICES:
        raise HTTPException(status_code=400, detail="Invalid voice")
    wav_bytes = text_to_wav_bytes(req.text, req.voice, req.speed)
    if not wav_bytes:
        raise HTTPException(status_code=500, detail="No audio generated")
    return StreamingResponse(io.BytesIO(wav_bytes), media_type="audio/wav")

class SplitRequest(BaseModel):
    text: str

@app.post("/split")
def split_text(req: SplitRequest):
    return {"sentences": split_sentences(req.text)}

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        import pdfminer.high_level
        contents = await file.read()
        buf = io.BytesIO(contents)
        text = pdfminer.high_level.extract_text(buf)
        if not text or not text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")
        sentences = split_sentences(text)
        return {"text": text, "sentences": sentences}
    except ImportError:
        raise HTTPException(status_code=500, detail="pdfminer not installed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app.mount("/", StaticFiles(directory="public", html=True), name="static")
