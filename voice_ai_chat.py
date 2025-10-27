#!/usr/bin/env python3
"""
Voice AI Chat (Python v2)
-------------------------
Rebuilt from n8n workflow:
"AI Voice Chat using Webhook, Memory Manager, OpenAI, Google Gemini & ElevenLabs"

Features:
- Accepts voice input (via file or webhook)
- Transcribes speech to text (OpenAI Whisper API)
- Maintains chat context between sessions
- Responds via Gemini or OpenAI GPT models
- Converts text response to speech using ElevenLabs API
- Mock mode enabled automatically if API keys are missing
"""

import os
import json
import logging
import tempfile
import requests
from datetime import datetime
from config import Config

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

log = logging.getLogger("voice_ai_chat")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
cfg = Config.load_from_env()

# ---------- CONTEXT / MEMORY ----------
CONTEXT_FILE = "chat_context.json"

def load_context() -> list:
    if not os.path.exists(CONTEXT_FILE):
        return []
    with open(CONTEXT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_context(context: list):
    with open(CONTEXT_FILE, "w", encoding="utf-8") as f:
        json.dump(context, f, ensure_ascii=False, indent=2)

def append_to_context(user_text, ai_reply):
    context = load_context()
    context.append({"timestamp": datetime.utcnow().isoformat(), "human": user_text, "ai": ai_reply})
    save_context(context)

# ---------- SPEECH TO TEXT ----------
def transcribe_audio(file_path: str) -> str:
    if cfg.mock or not cfg.OPENAI_API_KEY:
        log.info("[MOCK] Transcribing audio")
        return "Hello AI, how are you today?"
    client = OpenAI(api_key=cfg.OPENAI_API_KEY)
    with open(file_path, "rb") as f:
        transcript = client.audio.transcriptions.create(model="whisper-1", file=f)
    return transcript.text

# ---------- TEXT GENERATION ----------
def generate_response(user_text: str, context: list) -> str:
    if cfg.mock:
        log.info("[MOCK] Generating AI reply")
        return "I'm great! How can I assist you today?"

    # Combine context
    history = "\n".join([f"Human: {c['human']}\nAI: {c['ai']}" for c in context[-5:]])
    prompt = f"""The following is a conversation between a human and an AI assistant.
Previous conversation:
{history}

Human: {user_text}
AI:"""

    if cfg.GEMINI_API_KEY:
        log.info("Using Google Gemini API")
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {cfg.GEMINI_API_KEY}"}
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        r = requests.post("https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent", 
                          headers=headers, json=data)
        r.raise_for_status()
        content = r.json()
        return content["candidates"][0]["content"]["parts"][0]["text"]

    if cfg.OPENAI_API_KEY:
        log.info("Using OpenAI GPT model")
        client = OpenAI(api_key=cfg.OPENAI_API_KEY)
        completion = client.chat.completions.create(
            model=cfg.OPENAI_MODEL or "gpt-4o-mini",
            messages=[{"role": "system", "content": "You are a helpful voice AI assistant."},
                      {"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return completion.choices[0].message.content.strip()

    return "[Error] No language model API configured."

# ---------- TEXT TO SPEECH ----------
def synthesize_speech(text: str) -> bytes:
    if cfg.mock or not cfg.ELEVEN_API_KEY:
        log.info("[MOCK] Generating audio (TTS)")
        return b"FAKEAUDIOBYTES"

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{cfg.ELEVEN_VOICE_ID}"
    headers = {"Content-Type": "application/json", "xi-api-key": cfg.ELEVEN_API_KEY}
    body = {"text": text, "voice_settings": {"stability": 0.3, "similarity_boost": 0.7}}
    r = requests.post(url, headers=headers, json=body)
    r.raise_for_status()
    return r.content

# ---------- MAIN WORKFLOW ----------
def process_voice_message(audio_path: str):
    log.info(f"🎤 Processing voice message: {audio_path}")
    text_input = transcribe_audio(audio_path)
    log.info(f"🗣️ User said: {text_input}")
    context = load_context()
    ai_reply = generate_response(text_input, context)
    log.info(f"🤖 AI reply: {ai_reply}")
    append_to_context(text_input, ai_reply)
    audio_bytes = synthesize_speech(ai_reply)
    output_path = "ai_reply.mp3"
    with open(output_path, "wb") as f:
        f.write(audio_bytes)
    log.info(f"🔊 Saved synthesized speech to {output_path}")
    return {"text": ai_reply, "audio_path": output_path}


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Voice AI Chat Agent")
    parser.add_argument("--audio", type=str, help="Path to input audio file")
    args = parser.parse_args()

    if not args.audio or not os.path.exists(args.audio):
        log.error("Please provide a valid --audio path (e.g. a .wav or .mp3 file).")
        return

    result = process_voice_message(args.audio)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
