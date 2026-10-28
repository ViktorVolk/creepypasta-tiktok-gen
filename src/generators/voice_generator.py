import asyncio
import edge_tts
from pathlib import Path
from ..config import VOICE_NAME, VOICE_RATE


class VoiceGenerator:
    def __init__(self):
        self.voice = VOICE_NAME
        self.rate = VOICE_RATE

    async def generate(self, text: str, output_path: str) -> str:
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Текст должен быть непустой строкой")
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        communicate = edge_tts.Communicate(text, self.voice, rate=self.rate)
        await communicate.save(str(output_path))
        
        return str(output_path)

    def generate_sync(self, text: str, output_path: str) -> str:
        return asyncio.run(self.generate(text, output_path))
