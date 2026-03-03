# SpeakIt v2 — Local Neural TTS with Kokoro

High-quality, GPU-accelerated text-to-speech running entirely on your machine. No API keys. No internet required after setup.

## Requirements

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) with **WSL2 backend** enabled
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) for GPU support
- [ngrok](https://ngrok.com/download) to share publicly

---

## Setup NVIDIA Container Toolkit (one-time)

Docker needs this to pass your GPU into the container.

1. Open **WSL2** (search "wsl" in Start Menu)
2. Run:
```bash
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/libnvidia-container/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

---

## Run the App

```bash
cd tts-app-v2
docker compose up --build
```

> First run will download the Kokoro model (~500MB) and PyTorch — this takes a few minutes. Subsequent starts are fast.

App will be at: **http://localhost:8000**

---

## Share with ngrok

```bash
ngrok http 8000
```

---

## Voices included

| ID | Name |
|----|------|
| af_heart | Heart (US Female) — default, best quality |
| af_bella | Bella (US Female) |
| af_nicole | Nicole (US Female) |
| af_sarah | Sarah (US Female) |
| af_sky | Sky (US Female) |
| am_adam | Adam (US Male) |
| am_michael | Michael (US Male) |
| bf_emma | Emma (UK Female) |
| bf_isabella | Isabella (UK Female) |
| bm_george | George (UK Male) |
| bm_lewis | Lewis (UK Male) |

---

## Stop

```bash
docker compose down
```
