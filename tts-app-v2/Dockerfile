# CUDA-enabled Python base image
FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04

# System deps
RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    espeak-ng \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python deps
RUN pip3 install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    kokoro \
    soundfile \
    numpy \
    torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

COPY main.py .
COPY public/ ./public/

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
