from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import uuid
from TTS.api import TTS

app = FastAPI(
    title="EchoClone 🗣️🔥",
    description="Clone your voice in 30 seconds. Scale your content.",
    version="1.0.0"
)

# Allow frontend origins later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
os.makedirs("refs", exist_ok=True)
os.makedirs("generated", exist_ok=True)
app.mount("/generated", StaticFiles(directory="generated"), name="generated")

# Load model once (XTTS v2 — god tier cloning)
print("Loading TTS model... (first run takes ~30s)")
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=True).to("cpu")

@app.get("/")
def root():
    return {"message": "EchoClone live 🚀 | Go to /docs for API"}

@app.post("/clone")
async def clone_voice(
    reference_audio: UploadFile = File(..., description="30s+ WAV of your voice"),
    text: str = Form(..., description="Text to speak in cloned voice"),
    language: str = Form("en", description="Language code (en, es, fr, etc)")
):
    if not reference_audio.filename.endswith(".wav"):
        raise HTTPException(400, detail="Upload .wav only")

    # Save reference
    ref_id = str(uuid.uuid4())
    ref_path = f"refs/{ref_id}.wav"
    with open(ref_path, "wb") as f:
        shutil.copyfileobj(reference_audio.file, f)

    # Generate
    out_id = str(uuid.uuid4())
    output_path = f"generated/{out_id}.wav"
    tts.tts_to_file(
        text=text,
        speaker_wav=ref_path,
        language=language,
        file_path=output_path
    )

    return JSONResponse({
        "cloned_audio_url": f"/generated/{out_id}.wav",
        "message": "Voice cloned 🔥 Say whatever, whenever."
    })
