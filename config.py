import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    OPENAI_API_KEY: str
    OPENAI_MODEL: str
    GEMINI_API_KEY: str
    ELEVEN_API_KEY: str
    ELEVEN_VOICE_ID: str
    mock: bool

    @staticmethod
    def load_from_env() -> "Config":
        o = os.getenv("OPENAI_API_KEY", "")
        g = os.getenv("GEMINI_API_KEY", "")
        e = os.getenv("ELEVEN_API_KEY", "")
        vid = os.getenv("ELEVEN_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        mock = not (o or g or e)
        return Config(o, model, g, e, vid, mock)
