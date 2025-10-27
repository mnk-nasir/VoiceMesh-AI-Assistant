# VoiceMesh-AI-Assistant# 🎙️ Voice AI Chat (Python v2)

Rebuilt from your n8n workflow:
**“AI Voice Chat using Webhook, Memory Manager, OpenAI, Google Gemini & ElevenLabs”**

---

## 🧩 Features
- 🎤 Speech → Text via OpenAI Whisper
- 🧠 Context memory via JSON
- 💬 Response generation with Gemini or GPT
- 🔊 Voice reply via ElevenLabs Text-to-Speech
- 🧪 Mock mode (no API keys required)

---

## 🚀 Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
Then add your API keys to .env.

▶️ Run
bash
Copy code
python voice_ai_chat.py --audio path/to/input.wav
You’ll get:

AI text reply in console

Voice output saved to ai_reply.mp3

⚙️ Mock Mode
If no .env keys are found, all API calls are simulated — perfect for testing.

🧠 Extend
Replace file I/O with a Flask webhook for real-time requests

Add conversational persistence via SQLite or Redis

Stream audio replies for live chatbots
