# O.M.N.I.S. (Omni-Modal Neural Interface System)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![UI](https://img.shields.io/badge/Frontend-Futuristic%20Web%20HUD-cyan.svg)](Frontend/index.html)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#)

**O.M.N.I.S.** is an advanced AI assistant and desktop automation cognitive framework featuring a high-tech, futuristic Sci-Fi Web HUD with real-time holographic reactor visualization, voice input, telemetry monitoring, and multi-model decision routing.

---

## ⚡ Key Capabilities

- **Holographic Arc Reactor HUD**: Dynamic multi-ring gyro canvas visualizer reacting to listening, thinking, speaking, and standby states.
- **Audio Waveform Equalizer**: Symmetrical cyber frequency spectrum responding to microphone and vocal output.
- **Voice-First Input**: Instant speech recognition via browser Web Speech API (with push-to-talk `Spacebar` or continuous mode).
- **Decision-Making Layer (DMM)**: Classifies user directives across conversational LLM, real-time web search, PC automation, or image synthesis.
- **Real-Time Web Search**: Retrieves live prices, news, and factual information.
- **Desktop Automation**: Controls PC volume, opens applications/sites (YouTube, Google, Chrome, WhatsApp), and drafts notes in Notepad.
- **Neural Image Generation**: Automated text-to-image synthesis using Stable Diffusion with integrated gallery preview.
- **Cybernetic Audio Feedback**: Built-in procedural Web Audio API SFX (activation chirps, recording cues, response chimes).

---

## 🚀 Quick Start

### 1. Configure Environment Variables
Copy [.env.example](file:///c:/Users/navje/O.M.N.I.S/.env.example) to `.env` and fill in your API keys:
```env
Username=Sir
Assistantname=OMNIS
AssistantVoice=en-US-AriaNeural

# Free API Keys
CohereAPIKey=your_cohere_key_here     # https://dashboard.cohere.com/
GroqAPIKey=your_groq_key_here         # https://console.groq.com/
HuggingFaceAPIKey=your_hf_key_here    # https://huggingface.co/settings/tokens
```
*(Note: O.M.N.I.S includes smart heuristic fallbacks and offline simulation even before adding API keys!)*

### 2. Launch the Web HUD
Run the unified Flask backend:
```bash
python app.py
```
Then open your browser at:
👉 **[http://localhost:5000](http://localhost:5000)**

---

## 📂 Project Architecture

```
O.M.N.I.S/
├── Backend/
│   ├── Model.py               # FirstLayerDMM decision routing
│   ├── Chatbot.py             # Groq Llama-3 conversational engine
│   ├── RealtimeSearchEngine.py# DuckDuckGo search reasoning
│   ├── Automation.py          # App opener, volume, web automation
│   ├── ImageGeneration.py     # SDXL / Decohere image generator
│   ├── SpeechToText.py        # Background speech recognition
│   └── TextToSpeech.py        # Edge-TTS neural speech playback
├── Frontend/
│   ├── index.html             # Main Sci-Fi Cyber Deck layout
│   ├── css/
│   │   └── style.css          # Glassmorphism, neon HUD aesthetic
│   └── js/
│       ├── visualizer.js      # Arc Reactor & Audio Waveform canvas
│       ├── audio-sfx.js       # Real-time Web Audio API sound generator
│       └── app.js             # Speech controller, API bridge, UI logic
├── Data/
│   ├── ChatLog.json           # Interaction history
│   └── *.jpg                  # Synthesized neural renders
├── app.py                     # Flask backend API server & static host
├── Main.py                    # Terminal-only voice loop (legacy)
├── requirement.txt            # Python dependencies
└── .env.example               # Template for configuration
```

---

## ⌨️ Shortcuts & Controls

- **`Spacebar`**: Toggle voice speech recognition (Hold or tap to speak).
- **`Enter`**: Submit text prompt in the directive bar.
- **`🔊` Button**: Toggle futuristic sound effects on/off.
- **`🗣️` Button**: Toggle AI vocal audio synthesis.
- **`⚙️` Button**: Open system callsign & voice configuration modal.
