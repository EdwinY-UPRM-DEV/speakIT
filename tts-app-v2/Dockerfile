FROM nvidia/cuda:12.8.1-cudnn-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    espeak-ng \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# PyTorch nightly — required for RTX 5080 (Blackwell sm_120)
RUN pip3 install --no-cache-dir --pre torch torchvision torchaudio \
    --index-url https://download.pytorch.org/whl/nightly/cu128

# App dependencies
RUN pip3 install --no-cache-dir fastapi uvicorn[standard] kokoro soundfile numpy pdfminer.six

COPY main.py .
COPY public/ ./public/

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
